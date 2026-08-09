"""E2 — facility transition MILP + epsilon-constraint frontier tracing (REDESIGN_SPEC §3 E2).

Per company x scenario:
  decisions  x[f,k,ta] = facility f adopts tech k in year ta (≤1 adoption per facility)
             ppa ∈ [0,1] (company PPA share), epc ∈ {0,1}, ccfd ∈ {0,1}
  objective  NPV of capex + opex + energy + carbon cost + contract premiums
             + stranded-cost penalty for off-reinvestment-window adoption
             + soft carbon-budget violation penalty
  frontier   epsilon-constraint on a LINEAR risk proxy (unhedged elec+h2+capex+policy
             exposure x volatility). The proxy only orders candidate plans; the real
             TCaR of every plan is computed by simulation in E4 (documented in spec).

Timing is endogenous: adopting outside the reinvestment window burns remaining
asset life (penalty ∝ years from nearest window x adopted capex) — 설계서 §2.

Outputs: out/e2/plan_index.csv, out/e2/plans/plan_<id>.csv
"""

from __future__ import annotations

import itertools
import shutil
import time

import numpy as np
import pandas as pd
import pulp

from . import config as C
from .calibration import calibrate, hydrogen_price
from .e1_constraints import COMPANY_REGION
from .plancost import auction_share, salvage_fraction, stranded_cost_k
from .schemas import load_input

SCALE = 1e-6          # KRW thousands -> KRW billions (numerical scaling for CBC)
GJ_PER_T_COAL = 28.0
GJ_PER_T_GAS = 54.0
CARBON_POLICY_VOL = 0.3  # ponytail: proxy vol for policy axis so ccfd can buy risk; real ④ comes from E5


def _prep_company(cfg, ddir):
    """Load inputs once; return dict of per-company static data."""
    d1a = load_input(ddir, "D1a_facility_static")
    d1b = load_input(ddir, "D1b_facility_panel")
    d3 = load_input(ddir, "D3_tech_options")
    d4 = load_input(ddir, "D4_price_history")
    cal = calibrate(d4)

    recent = d1b[d1b.year >= d1b.year.max() - 2].groupby("facility_id").mean(numeric_only=True)
    fac = d1a.set_index("facility_id").join(recent[["production", "emissions_s1", "energy_coal",
                                                    "energy_gas", "energy_elec"]])
    fac["ef_inc"] = fac.emissions_s1 / fac.production
    fac["elec_int_inc"] = fac.energy_elec / fac.production           # MWh/t
    fac["coal_int_inc"] = fac.energy_coal / fac.production / GJ_PER_T_COAL   # t coal / t prod
    fac["gas_int_inc"] = fac.energy_gas / fac.production / GJ_PER_T_GAS
    return fac, d3, cal


def _central(prices, region, scen, var, years):
    g = prices[(prices.region == region) & (prices.scenario == scen) & (prices.variable == var)]
    s = g.set_index("year").value.reindex(years)
    if s.isna().any():
        raise RuntimeError(f"central price path missing: {var} {region} {scen}")
    return s.to_numpy()


def _year_cost_components(fac_row, tech, years, px, cfg):
    """Per-year (variable cost, emissions, elec_cost_k, h2_cost_k) for one facility
    under incumbent (tech=None) or a given tech row. Costs in KRW thousands/yr.
    v2.1: incumbent power at grid price, transition-tech power at renewable
    procurement price (px['re']); hydrogen externally procured at px['h2']."""
    prod = fac_row.production
    ones = np.ones(len(years))
    inc_elec_cost = fac_row.elec_int_inc * prod * px["elec"] / 1000.0   # KRW/MWh -> 천원
    inc_var = (inc_elec_cost
               + fac_row.coal_int_inc * prod * px["coal"] / 1000.0
               + fac_row.gas_int_inc * prod * px["gas"] / 1000.0)
    if tech is None:
        return inc_var, fac_row.ef_inc * prod * ones, inc_elec_cost, 0.0 * ones
    emis = tech.emission_factor * prod * ones
    re_cost = tech.elec_intensity * prod * px["re"] / 1000.0
    h2_cost = tech.h2_intensity * prod * px["h2"] / 1000.0
    add_cost = (re_cost + h2_cost
                + tech.opex_var * prod * ones                        # 천원/t x t
                + tech.opex_fixed * fac_row.capacity * ones)         # 천원/t능력 x t능력 (spec D3)
    if int(getattr(tech, "retrofit", 0) or 0):
        # retrofit keeps the incumbent process energy; tech intensities are add-ons
        return inc_var + add_cost, emis, inc_elec_cost + re_cost, h2_cost
    return add_cost, emis, re_cost, h2_cost   # replacement: process energy swapped out


def _solve_company(cfg, company, scen, fac, d3, cal, prices, constraints, avail,
                   eps=None, fixed=None, objective="cost"):
    """Build & solve one MILP. Returns dict(plan rows, npv_cost, risk, meta) or None."""
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc = (1 + cfg.discount_rate) ** -(years - years[0])
    region = COMPANY_REGION.get(company)
    if region is None:
        raise RuntimeError(f"unknown company '{company}' — add to COMPANY_REGION in e1_constraints.py")
    cf = fac[fac.company_id == company]
    sector = cf.sector.iloc[0]

    # fail fast on NaN model coefficients (panel gaps, missing static fields) —
    # CBC behaviour on NaN in the LP is undefined
    need = ["production", "ef_inc", "elec_int_inc", "coal_int_inc", "gas_int_inc",
            "capacity", "next_reinvest_year", "reinvest_cycle_yr"]
    bad = cf[need].isna()
    if bad.any().any():
        rows = cf.index[bad.any(axis=1)].tolist()
        raise RuntimeError(f"{company}: NaN in facility data {rows} "
                           f"(columns: {bad.any()[bad.any()].index.tolist()}) — "
                           "check D1a/D1b coverage for the last 3 panel years")

    px = {"elec": _central(prices, region, scen, "elec_price", years),
          "coal": _central(prices, region, scen, "coal_price", years),
          "gas": _central(prices, region, scen, "gas_price", years),
          "co2": _central(prices, region, scen, "co2_price", years)}
    # v2.1: hydrogen externally procured (D2b path); transition power at renewable
    # procurement price. Graceful fallbacks keep synthetic sample data runnable.
    try:
        px["h2"] = _central(prices, region, scen, "h2_price", years)
    except RuntimeError:
        px["h2"] = hydrogen_price(px["elec"], cal.ez_central(years), cfg.hydrogen)
        print(f"[e2] note: D2b h2_price missing for {region} {scen} — structural fallback used")
    try:
        px["re"] = _central(prices, region, scen, "re_price", years)
    except RuntimeError:
        px["re"] = px["elec"]
        print(f"[e2] note: D2b re_price missing for {region} {scen} — grid price used for 재생 조달")

    budget = (constraints[(constraints.company_id == company) & (constraints.scenario == scen)]
              .set_index("year").company_budget_tco2.reindex(years).to_numpy())
    if np.isnan(budget).any():
        raise RuntimeError(f"budget path incomplete for {company} {scen} — rerun e1")

    techs = d3[d3.sector == sector]
    av = avail[(avail.scenario == scen) & (avail.region == region)].set_index("tech_id").avail_year_scenario

    m = pulp.LpProblem(f"{company}_{scen}", pulp.LpMinimize)
    x = {}      # (fid, tech_id, ta) -> binary
    for fid, fr in cf.iterrows():
        for _, tk in techs[techs.applies_to_unit == fr.unit_type].iterrows():
            a0 = int(max(years[0], av.get(tk.tech_id, tk.avail_year), tk.avail_year))
            for ta in range(a0, int(years[-1]) - int(tk.build_years) + 1):
                x[fid, tk.tech_id, ta] = pulp.LpVariable(f"x_{fid}_{tk.tech_id}_{ta}", cat="Binary")
    ppa = pulp.LpVariable("ppa", 0, 1)
    epc = pulp.LpVariable("epc", cat="Binary")
    ccfd = pulp.LpVariable("ccfd", cat="Binary")
    slack = {t: pulp.LpVariable(f"slack_{t}", 0) for t in years}

    # retire option (v2.1): close the facility at ta — emissions/energy stop,
    # campaign book value written off, future margin forfeited. Only enabled when
    # margin data exists (free-abatement guard, 스펙 §5-1-6).
    rt: dict[tuple, pulp.LpVariable] = {}
    margin_ok = "margin_kthou_t" in cf.columns and cf.margin_kthou_t.notna().all() \
        and (cf.margin_kthou_t > 0).all()
    if margin_ok:
        for fid in cf.index:
            for ta in range(int(years[0]), int(years[-1]) + 1):
                rt[fid, ta] = pulp.LpVariable(f"r_{fid}_{ta}", cat="Binary")

    for fid in cf.index:
        m += (pulp.lpSum(v for (f2, _, _), v in x.items() if f2 == fid)
              + pulp.lpSum(rv for (f2, _), rv in rt.items() if f2 == fid)) <= 1

    if fixed:
        for (fid, tid, ta), val in fixed.get("x", {}).items():
            if (fid, tid, ta) in x:
                m += x[fid, tid, ta] == val
            else:
                print(f"[e2] warning: fixed commitment {(fid, tid, ta)} has no variable "
                      "— not enforced (check availability/applies_to_unit)")
        if "ppa" in fixed:
            m += ppa == fixed["ppa"]
        if "epc" in fixed:
            m += epc == fixed["epc"]
        if "ccfd" in fixed:
            m += ccfd == fixed["ccfd"]

    # accumulate per-year expressions
    auc = auction_share(years, cfg)
    cost_terms, risk_terms, salvage_terms, retire_terms = [], [], [], []
    for (fid, ta), rv in rt.items():
        fr = cf.loc[fid]
        # margin (영업이익/t) is net of energy costs — neutralize the model's own
        # energy-cost saving so closure isn't double-credited (see plancost)
        inc_var_f, _, _, _ = _year_cost_components(fr, None, years, px, cfg)
        mloss = sum(disc[j] * SCALE * (fr.margin_kthou_t * fr.production + inc_var_f[j])
                    for j, tt in enumerate(years) if tt >= ta)
        strd = disc[int(ta - years[0])] * SCALE * stranded_cost_k(fr, int(ta), cfg)
        retire_terms.append((mloss + strd) * rv)

    for i, t in enumerate(years):
        emis_t, var_t, elec_cost_t, h2_cost_t, capex_t = [], [], [], [], []
        for fid, fr in cf.iterrows():
            inc_var, inc_emis, inc_elec_cost, _ = _year_cost_components(fr, None, years, px, cfg)
            adopted = [(k, ta, v) for (f2, k, ta), v in x.items() if f2 == fid]
            # active indicators: adoption in operation / facility retired by t
            op = pulp.lpSum(v for k, ta, v in adopted
                            if ta + int(techs.set_index("tech_id").loc[k].build_years) <= t)
            ret = pulp.lpSum(rv for (f2, ta), rv in rt.items() if f2 == fid and ta <= t)
            emis_t.append(inc_emis[i] * (1 - op - ret))
            var_t.append(inc_var[i] * (1 - op - ret))
            elec_cost_t.append(inc_elec_cost[i] * (1 - op - ret))
            for k, ta, v in adopted:
                tk = techs.set_index("tech_id").loc[k]
                tv, te, tel_cost, th2_cost = _year_cost_components(fr, tk, years, px, cfg)
                if ta + int(tk.build_years) <= t:
                    emis_t.append(te[i] * v)
                    var_t.append(tv[i] * v)
                    elec_cost_t.append(tel_cost[i] * v)
                    h2_cost_t.append(th2_cost[i] * v)
                if ta == t:
                    capex_kb = tk.capex_unit * fr.capacity  # KRW thousands
                    # stranded = depreciated remaining book value of the incumbent
                    # campaign asset; salvage = horizon-end book value of the new one
                    capex_t.append((capex_kb + stranded_cost_k(fr, ta, cfg)) * v)
                    frac = salvage_fraction(tk, ta + int(tk.build_years), int(years[-1]))
                    salvage_terms.append(disc[-1] * SCALE * capex_kb * frac * v)

        emis_expr = pulp.lpSum(emis_t)
        m += emis_expr <= budget[i] + slack[t]
        if rt:
            # closure cap: retired production ≤ share of company output (수요·시장지위 프록시)
            m += pulp.lpSum(cf.loc[f2].production * rv for (f2, ta), rv in rt.items() if ta <= t) \
                 <= cfg.milp.get("retire_max_share", 0.2) * cf.production.sum()

        carbon = px["co2"][i] * auc[i] / 1000.0  # 천원/tCO2, 유상할당 반영
        viol = max(2.0 * carbon, cfg.milp.get("budget_violation_floor_thkrw", 300))
        cost_terms.append(disc[i] * SCALE * (
            pulp.lpSum(var_t)
            + pulp.lpSum(capex_t)
            + carbon * emis_expr
            + viol * slack[t]))

        # risk proxy: market exposure x annualized vol. Multiplying exposure by (1-ppa)
        # would be bilinear with x, so hedges enter as separate linear credits below
        # (plan-independent central magnitudes; conservative). Contract premiums likewise.
        risk_terms.append(disc[i] * SCALE * (
            cal.vol["elec"] * pulp.lpSum(elec_cost_t)
            + cal.vol.get("h2", 0.25) * pulp.lpSum(h2_cost_t)   # v2.1: 수소 독립 요인
            + cal.vol["capex"] * pulp.lpSum(capex_t)
            + CARBON_POLICY_VOL * carbon * emis_expr))

    # hedge credits (linear): ppa removes elec+h2 exposure share, epc removes capex vol,
    # ccfd removes policy-carbon exposure — credited against the whole-horizon proxy using
    # plan-independent central magnitudes (upper-bound conservative).
    tot_mkt_ub = float(sum(disc[i] * SCALE * (cf.elec_int_inc * cf.production).sum() * px["elec"][i] / 1000.0
                           for i in range(len(years))))
    tot_capex_ub = float(techs.capex_unit.max() * cf.capacity.sum() * SCALE)
    tot_carbon_ub = float(sum(disc[i] * SCALE * px["co2"][i] / 1000.0 * (cf.ef_inc * cf.production).sum() * 0.5
                              for i in range(len(years))))
    risk = (pulp.lpSum(risk_terms)
            - cal.vol["elec"] * tot_mkt_ub * ppa
            - cal.vol["capex"] * tot_capex_ub * 0.8 * epc
            - CARBON_POLICY_VOL * tot_carbon_ub * ccfd)
    risk_lb = pulp.LpVariable("risk_nonneg", 0)
    m += risk_lb >= risk

    cost = (pulp.lpSum(cost_terms)
            + pulp.lpSum(retire_terms)
            - pulp.lpSum(salvage_terms)
            + cfg.contracts.ppa_premium_pct * tot_mkt_ub * ppa
            + cfg.contracts.epc_premium_pct * tot_capex_ub * 0.3 * epc
            + cfg.contracts.ccfd_fee_pct * tot_carbon_ub * ccfd)

    if eps is not None:
        m += risk_lb <= eps
    m += cost if objective == "cost" else risk_lb

    # A relative MIP gap is not a shortcut here, it is the honest setting: this
    # objective is an ORDERING surrogate (linear risk proxy, linearized contracts)
    # and the authoritative cost of every plan is re-derived by simulation in E4.
    # Proving the last fraction of a percent of surrogate optimality buys nothing
    # and was costing tens of minutes per run.
    m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cfg.milp.solver_time_limit_s,
                              gapRel=float(cfg.milp.get("mip_gap_rel", 0.005)),
                              threads=int(cfg.milp.get("solver_threads", 0)) or None))
    status = pulp.LpStatus[m.status]
    if status != "Optimal":
        # A time-limited solve that found an incumbent is still a usable candidate
        # plan — E4 re-costs it from scratch anyway. Dropping it silently shrank the
        # frontier instead. Keep it, but carry the status into plan_index so the
        # quality of every point is visible in the artefact.
        has_incumbent = any(v.value() is not None for v in x.values()) if x else False
        if not has_incumbent:
            print(f"[e2] warning: {company} {scen} '{status}' with no incumbent "
                  f"(eps={eps}, fixed={'yes' if fixed else 'no'}) — 계획 없음", flush=True)
            return None
        print(f"[e2] note: {company} {scen} '{status}' — 시간상한에서 얻은 실행가능해 사용 "
              f"(eps={eps}). 대리목적함수이므로 정본 비용은 E4가 재산출.", flush=True)

    plan = [{"facility_id": fid, "tech_id": k, "adopt_year": ta,
             "op_year": ta + int(techs.set_index("tech_id").loc[k].build_years)}
            for (fid, k, ta), v in x.items() if v.value() and v.value() > 0.5]
    plan += [{"facility_id": fid, "tech_id": "retire", "adopt_year": ta, "op_year": ta}
             for (fid, ta), rv in rt.items() if rv.value() and rv.value() > 0.5]
    # report the plan's actual risk expression, not risk_lb (which is only
    # sandwiched max(risk,0) <= risk_lb <= eps and can sit anywhere in between
    # when the objective is cost)
    return {"plan": plan, "npv_cost": pulp.value(cost), "risk": max(0.0, pulp.value(risk)),
            "solve_status": status,
            "ppa": ppa.value(), "epc": round(epc.value() or 0), "ccfd": round(ccfd.value() or 0),
            "budget_slack": sum(s.value() or 0 for s in slack.values())}


def _disclosed_fixed(d7, cf, techs, years, av):
    """Fix decision variables to the disclosed plan. Adoption year is clamped into
    the feasible variable range [max(avail, start), end - build] so a commitment
    whose back-computed start predates tech availability is enforced at the
    earliest feasible year instead of silently vanishing."""
    fixed = {"x": {}}
    sub = d7[d7.company_id.isin(cf.company_id.unique())]
    for _, r in sub.iterrows():
        if r.item_type == "tech_commit" and r.facility_id in cf.index and pd.notna(r.year_stated):
            tk = techs[techs.tech_id == r.tech_id]
            if not len(tk):
                print(f"[e2] warning: disclosed tech {r.tech_id!r} not in D3 — commitment dropped")
                continue
            if tk.applies_to_unit.iloc[0] != cf.loc[r.facility_id].unit_type:
                print(f"[e2] note: disclosed {r.facility_id}({cf.loc[r.facility_id].unit_type})/"
                      f"{r.tech_id} not applicable (applies to {tk.applies_to_unit.iloc[0]}) "
                      "— commitment dropped")
                continue
            build = int(tk.build_years.iloc[0])
            a0 = int(max(years[0], av.get(r.tech_id, tk.avail_year.iloc[0]), tk.avail_year.iloc[0]))
            hi = int(years[-1]) - build
            if a0 > hi:
                print(f"[e2] warning: {r.tech_id} never available in this scenario — "
                      f"disclosed commitment for {r.facility_id} dropped")
                continue
            ta = int(np.clip(r.year_stated - build, a0, hi))
            if ta != r.year_stated - build:
                print(f"[e2] note: disclosed {r.facility_id}/{r.tech_id} start shifted "
                      f"{int(r.year_stated - build)} -> {ta} (availability/horizon clamp)")
            fixed["x"][(r.facility_id, r.tech_id, ta)] = 1
    ppa_rows = sub[sub.item_type == "ppa"].coverage_pct.dropna()
    fixed["ppa"] = float(ppa_rows.max()) / 100.0 if len(ppa_rows) else 0.0
    fixed["epc"] = 1 if len(sub[sub.item_type == "epc"]) else 0
    fixed["ccfd"] = 1 if len(sub[sub.item_type == "ccfd"]) else 0
    return fixed


def run(cfg: C.Config):
    ddir = C.data_dir(cfg)
    odir = C.out_dir(cfg, "e2")
    # plan ids restart at P0001 every run, so a shorter run leaves the previous
    # run's higher-numbered plans on disk. plan_index.csv keeps downstream stages
    # honest, but the stale files still look like current output — clear them.
    shutil.rmtree(odir / "plans", ignore_errors=True)
    (odir / "plans").mkdir(exist_ok=True)
    fac, d3, cal = _prep_company(cfg, ddir)
    d7 = load_input(ddir, "D7_disclosed_plan")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    constraints = pd.read_csv(C.out_dir(cfg, "e1") / "constraints.csv")
    avail = pd.read_csv(C.out_dir(cfg, "e1") / "tech_availability.csv")
    years = np.arange(cfg.years.start, cfg.years.end + 1)

    index_rows, pid = [], 0
    combos = list(itertools.product(sorted(fac.company_id.unique()), cfg.scenarios))
    # each combo is ~14 CBC solves and the stage runs for tens of minutes; without
    # a heartbeat there is no way to tell a slow solve from a hung one
    for n, (company, scen) in enumerate(combos, 1):
        t_co = time.time()
        print(f"[e2] {n}/{len(combos)} {company} {scen} — 경계 추적 "
              f"{cfg.milp.frontier_points}점 ...", flush=True)
        args = (cfg, company, scen, fac, d3, cal, prices, constraints, avail)
        lo = _solve_company(*args, objective="risk")
        hi = _solve_company(*args, objective="cost")
        if lo is None or hi is None:
            raise RuntimeError(f"MILP infeasible for {company} {scen}")
        grid = np.linspace(lo["risk"], max(hi["risk"], lo["risk"] * 1.001), cfg.milp.frontier_points)
        seen = set()
        sols = []
        for e in grid:
            s = _solve_company(*args, eps=float(e))
            if s is None:
                continue
            key = (tuple(sorted((p["facility_id"], p["tech_id"], p["adopt_year"]) for p in s["plan"])),
                   round(s["ppa"] or 0, 2), s["epc"], s["ccfd"])
            if key in seen:
                continue
            seen.add(key)
            sols.append(s)
        cf = fac[fac.company_id == company]
        av_cs = (avail[(avail.scenario == scen) & (avail.region == COMPANY_REGION[company])]
                 .set_index("tech_id").avail_year_scenario)
        disc_fixed = _disclosed_fixed(d7, cf, d3[d3.sector == cf.sector.iloc[0]], years, av_cs)
        if not disc_fixed["x"] and not disc_fixed["ppa"] and not disc_fixed["epc"] and not disc_fixed["ccfd"]:
            # no enforceable commitment survived — a "disclosed" solve would just be a
            # second unconstrained optimization whose surrogate near-optimum can differ
            # arbitrarily in E4 terms, fabricating a gap. 공시 해상도 부족 = gap 미식별 (§8-4).
            print(f"[e2] note: {company} {scen} disclosed plan has no enforceable commitments "
                  "— disclosed coordinate skipped (resolution too low to locate the plan)")
            s_disc = None
        else:
            s_disc = _solve_company(*args, fixed=disc_fixed)
        if s_disc is None:
            print(f"[e2] warning: disclosed plan for {company} {scen} infeasible/unsolved — "
                  "no gap row will be produced in E5")
        if s_disc is not None:
            s_disc["disclosed"] = True
            sols.append(s_disc)

        for s in sols:
            pid += 1
            plan_id = f"P{pid:04d}"
            pd.DataFrame(s["plan"] or [{"facility_id": None, "tech_id": None,
                                        "adopt_year": None, "op_year": None}]).assign(
                plan_id=plan_id, company_id=company, scenario=scen,
                ppa_share=s["ppa"], epc=s["epc"], ccfd=s["ccfd"],
            ).to_csv(odir / "plans" / f"plan_{plan_id}.csv", index=False)
            index_rows.append([plan_id, company, scen, s["npv_cost"], s["risk"],
                               s["ppa"], s["epc"], s["ccfd"], s["budget_slack"],
                               bool(s.get("disclosed", False)), s.get("solve_status", "Optimal")])
        print(f"[e2] {n}/{len(combos)} {company} {scen} — 고유 계획 {len(sols)}개, "
              f"{time.time() - t_co:.0f}s", flush=True)

    idx = pd.DataFrame(index_rows, columns=["plan_id", "company_id", "scenario", "npv_cost_bnkrw",
                                            "risk_proxy", "ppa_share", "epc", "ccfd",
                                            "budget_slack_tco2", "is_disclosed", "solve_status"])
    idx.to_csv(odir / "plan_index.csv", index=False)
    return idx


if __name__ == "__main__":
    print(run(C.load()).to_string())
