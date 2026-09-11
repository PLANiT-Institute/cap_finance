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
import pathlib
import shutil
import time

import numpy as np
import pandas as pd
import pulp

from . import config as C
from .calibration import calibrate, hydrogen_price, calibrate_for
from .e1_constraints import COMPANY_REGION
from .plancost import auction_share, salvage_fraction, stranded_cost_k, uses_cash_capital, capital_ledger_for
from .schemas import load_input
from .energy_balance import retained_energy
from .carbon_accounting import carbon_mode, free_allowance_path
from .solver_validation import validate_mip_solution

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
    cal = calibrate_for(cfg, d4)

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
    coal_keep, gas_keep, grid_keep = retained_energy(tech, cfg)
    retained_cost = (grid_keep * inc_elec_cost
                     + coal_keep * fac_row.coal_int_inc * prod * px["coal"] / 1000.0
                     + gas_keep * fac_row.gas_int_inc * prod * px["gas"] / 1000.0)
    return retained_cost + add_cost, emis, grid_keep * inc_elec_cost + re_cost, h2_cost


def _solve_company(cfg, company, scen, fac, d3, cal, prices, constraints, avail,
                   eps=None, fixed=None, objective="cost", emis_cap=None):
    """Build & solve one MILP. Returns dict(plan rows, npv_cost, risk, meta) or None.

    emis_cap (tCO2, cumulative over the horizon) is a SECOND epsilon axis, on the
    technology schedule rather than the risk proxy — contracts cannot buy it, so it
    is the axis that tells a thin candidate set apart from a genuinely unique
    cost-minimal schedule (M8). None = untouched behaviour, headline pipeline never
    passes it."""
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc = (1.0 + cfg.discount_rate) ** -(years - years[0])
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
    if cfg.get("candidate_contracts", "legacy_surrogate") == "unhedged":
        m += ppa == 0
        m += epc == 0
    if carbon_mode(cfg) != "legacy_auction_discount":
        m += ccfd == 0  # no reviewed payoff contract is supplied in the research case
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
                raise ValueError(f"Fixed commitment {(fid, tid, ta)} has no decision variable; cannot silently omit it")
        if "ppa" in fixed:
            m += ppa == fixed["ppa"]
        if "epc" in fixed:
            m += epc == fixed["epc"]
        if "ccfd" in fixed:
            m += ccfd == fixed["ccfd"]

    # Reuse the same annual capital ledger as E4, including avoided baseline renewals.
    cash_basis = uses_cash_capital(cfg)
    capital_base, capital_choices, capital_retire = {}, {}, {}
    if cash_basis:
        tech_index = techs.set_index("tech_id")
        for fid, fr in cf.iterrows():
            capital_base[fid] = capital_ledger_for(fr, None, None, years, cfg)
        for fid, tid, ta in x:
            capital_choices[fid, tid, ta] = capital_ledger_for(cf.loc[fid], tech_index.loc[tid], ta, years, cfg)
        for fid, ta in rt:
            capital_retire[fid, ta] = capital_ledger_for(cf.loc[fid], None, ta, years, cfg, retire=True)

    # accumulate per-year expressions
    budget_mode = cfg.get("budget_mode", "legacy_relative_slack")
    if budget_mode not in ("legacy_relative_slack", "cumulative_hard", "annual_hard"):
        raise ValueError(f"Unknown budget mode: {budget_mode}")
    auc = auction_share(years, cfg)
    carbon_basis = carbon_mode(cfg)
    free_allocation = free_allowance_path(cfg, company, years, scenario=scen)
    cost_terms, risk_terms, salvage_terms, retire_terms, emis_exprs = [], [], [], [], []
    for (fid, ta), rv in rt.items():
        fr = cf.loc[fid]
        # margin (영업이익/t) is net of energy costs — neutralize the model's own
        # energy-cost saving so closure isn't double-credited (see plancost)
        inc_var_f, _, _, _ = _year_cost_components(fr, None, years, px, cfg)
        mloss = sum(disc[j] * SCALE * (fr.margin_kthou_t * fr.production + inc_var_f[j])
                    for j, tt in enumerate(years) if tt >= ta)
        strd = 0.0 if cash_basis else disc[int(ta - years[0])] * SCALE * stranded_cost_k(fr, int(ta), cfg)
        retire_terms.append((mloss + strd) * rv)

    for i, t in enumerate(years):
        emis_t, var_t, elec_cost_t, h2_cost_t, capex_t = [], [], [], [], []
        for fid, fr in cf.iterrows():
            inc_var, inc_emis, inc_elec_cost, _ = _year_cost_components(fr, None, years, px, cfg)
            adopted = [(k, ta, v) for (f2, k, ta), v in x.items() if f2 == fid]
            if cash_basis:
                baseline_capital = capital_base[fid]
                capex_t.append(baseline_capital.cash_capex_k[i])
                for k, ta, v in adopted:
                    capex_t.append((capital_choices[fid, k, ta].cash_capex_k[i]
                                    - baseline_capital.cash_capex_k[i]) * v)
                for (f2, ta), rv in rt.items():
                    if f2 == fid:
                        capex_t.append((capital_retire[fid, ta].cash_capex_k[i]
                                        - baseline_capital.cash_capex_k[i]) * rv)
                if i == len(years) - 1:
                    terminal_expr = baseline_capital.terminal_value_k[-1]
                    terminal_expr += pulp.lpSum((capital_choices[fid, k, ta].terminal_value_k[-1]
                                      - baseline_capital.terminal_value_k[-1]) * v for k, ta, v in adopted)
                    terminal_expr += pulp.lpSum((capital_retire[fid, ta].terminal_value_k[-1]
                                      - baseline_capital.terminal_value_k[-1]) * rv
                                      for (f2, ta), rv in rt.items() if f2 == fid)
                    salvage_terms.append(disc[-1] * SCALE * terminal_expr)
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
                if ta == t and not cash_basis:
                    capex_kb = tk.capex_unit * fr.capacity  # KRW thousands
                    # stranded = depreciated remaining book value of the incumbent
                    # campaign asset; salvage = horizon-end book value of the new one
                    capex_t.append((capex_kb + stranded_cost_k(fr, ta, cfg)) * v)
                    frac = salvage_fraction(tk, ta + int(tk.build_years), int(years[-1]))
                    salvage_terms.append(disc[-1] * SCALE * capex_kb * frac * v)

        emis_expr = pulp.lpSum(emis_t)
        emis_exprs.append(emis_expr)
        m += emis_expr <= budget[i] + slack[t]
        if budget_mode == "annual_hard":
            m += slack[t] == 0
        if rt:
            # closure cap: retired production ≤ share of company output (수요·시장지위 프록시)
            m += pulp.lpSum(cf.loc[f2].production * rv for (f2, ta), rv in rt.items() if ta <= t) \
                 <= cfg.milp.get("retire_max_share", 0.2) * cf.production.sum()

        carbon = px["co2"][i] * auc[i] / 1000.0  # 천원/tCO2, 유상할당 반영
        obligation = emis_expr - free_allocation[i]
        if carbon_basis == "purchase_only":
            uncovered = pulp.LpVariable(f"uncovered_allowances_{t}", 0)
            m += uncovered >= obligation
            obligation = uncovered
        viol = (max(2.0 * carbon, cfg.milp.get("budget_violation_floor_thkrw", 300))
                if budget_mode == "legacy_relative_slack" else 0.0)
        cost_terms.append(disc[i] * SCALE * (
            pulp.lpSum(var_t)
            + pulp.lpSum(capex_t)
            + carbon * obligation
            + viol * slack[t]))

        # risk proxy: market exposure x annualized vol. Multiplying exposure by (1-ppa)
        # would be bilinear with x, so hedges enter as separate linear credits below
        # (plan-independent central magnitudes; conservative). Contract premiums likewise.
        # v2 (L6): hydrogen vol is structural (≤ electricity vol; E3 sets w·σ_e, here the
        # upper bound σ_e is used), capex vol is 0 when no verified series exists, and the
        # carbon term uses the ESTIMATED KAU vol on the NET obligation (E−A) so the
        # generator's notion of risk matches the evaluator's (both credit abatement).
        _h2_vol = cal.vol.get("h2", 0.25)
        if _h2_vol is None or not np.isfinite(_h2_vol):
            _h2_vol = cal.vol["elec"]
        _co2_vol = cal.vol.get("co2", CARBON_POLICY_VOL)
        risk_terms.append(disc[i] * SCALE * (
            cal.vol["elec"] * pulp.lpSum(elec_cost_t)
            + _h2_vol * pulp.lpSum(h2_cost_t)
            + cal.vol["capex"] * pulp.lpSum(capex_t)
            + _co2_vol * carbon * (obligation if "co2" in cal.vol else emis_expr)))

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
            - cal.vol.get("co2", CARBON_POLICY_VOL) * tot_carbon_ub * ccfd)
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
    cum_emis = pulp.lpSum(emis_exprs)
    if budget_mode == "cumulative_hard":
        m += cum_emis <= float(budget.sum())
    if emis_cap is not None:
        m += cum_emis <= float(emis_cap)
    m += {"cost": cost, "risk": risk_lb, "emissions": cum_emis}[objective]

    # A relative MIP gap is not a shortcut here, it is the honest setting: this
    # objective is an ORDERING surrogate (linear risk proxy, linearized contracts)
    # and the authoritative cost of every plan is re-derived by simulation in E4.
    # Proving the last fraction of a percent of surrogate optimality buys nothing
    # and was costing tens of minutes per run.
    # L6 (2026-09-11): keep the CBC log so the ACTUAL relative gap and best bound of
    # every solve are recorded in plan_index (the audit found "Optimal" printed for
    # solves that stopped on the 2% gap, with no record of how large the gap was).
    import tempfile, re as _re
    _log = tempfile.NamedTemporaryFile(prefix="cbc_", suffix=".log", delete=False).name
    m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cfg.milp.solver_time_limit_s,
                              gapRel=float(cfg.milp.get("mip_gap_rel", 0.005)),
                              threads=int(cfg.milp.get("solver_threads", 0)) or None,
                              logPath=_log))
    mip_gap_actual, mip_lower_bound = float("nan"), float("nan")
    try:
        txt = pathlib.Path(_log).read_text(errors="ignore")
        mo = _re.search(r"Objective value:\s*([-\d.eE+]+)", txt)
        ml = _re.search(r"Lower bound:\s*([-\d.eE+]+)", txt)
        mg = _re.search(r"Gap:\s*([-\d.eE+]+)", txt)
        if ml: mip_lower_bound = float(ml.group(1))
        if mg: mip_gap_actual = float(mg.group(1))
        elif mo and ml and abs(float(mo.group(1))) > 0:
            mip_gap_actual = (float(mo.group(1)) - float(ml.group(1))) / abs(float(mo.group(1)))
        pathlib.Path(_log).unlink(missing_ok=True)
    except Exception:
        pass
    # CBC's text solution rounds continuous auxiliary values. Reconstruct their
    # exact minimal values from the returned primary decisions before checking
    # every original constraint. This cannot rescue an infeasible primary plan.
    if (m.status not in (pulp.LpStatusInfeasible, pulp.LpStatusUnbounded, pulp.LpStatusUndefined)
            and m.sol_status in (pulp.LpSolutionOptimal, pulp.LpSolutionIntegerFeasible)):
        for variable in m.variables():
            value = variable.value()
            if variable.cat == pulp.LpInteger and value is not None and abs(value-round(value)) <= 1e-7:
                variable.varValue = float(round(value))
        for i,t in enumerate(years):
            emission = pulp.value(emis_exprs[i])
            if emission is not None:
                slack[t].varValue = max(0.0, float(emission)-float(budget[i]))
                uncovered = m.variablesDict().get(f"uncovered_allowances_{t}")
                if uncovered is not None:
                    uncovered.varValue = max(0.0, float(emission)-float(free_allocation[i]))
        risk_value = pulp.value(risk)
        if risk_value is not None:
            risk_lb.varValue = max(0.0, float(risk_value))
    feasibility = validate_mip_solution(m)
    status = feasibility["solver_status"]
    if not feasibility["valid"]:
        print(f"[e2] rejected {company} {scen} {status}: "
              + "; ".join(feasibility["problems"][:3]), flush=True)
        return None
    if status != "Optimal" or m.sol_status != pulp.LpSolutionOptimal:
        print(f"[e2] {company} {scen}: verified feasible incumbent; "
              f"optimality not established ({status}/{feasibility['solution_status']})", flush=True)

    plan = [{"facility_id": fid, "tech_id": k, "adopt_year": ta,
             "op_year": ta + int(techs.set_index("tech_id").loc[k].build_years)}
            for (fid, k, ta), v in x.items() if v.value() and v.value() > 0.5]
    plan += [{"facility_id": fid, "tech_id": "retire", "adopt_year": ta, "op_year": ta}
             for (fid, ta), rv in rt.items() if rv.value() and rv.value() > 0.5]
    # report the plan's actual risk expression, not risk_lb (which is only
    # sandwiched max(risk,0) <= risk_lb <= eps and can sit anywhere in between
    # when the objective is cost)
    return {"plan": plan, "npv_cost": pulp.value(cost), "risk": max(0.0, pulp.value(risk)),
            "solve_status": status, "mip_gap_actual": mip_gap_actual, "mip_lower_bound": mip_lower_bound, "cum_emis_tco2": pulp.value(cum_emis),
            "ppa": ppa.value(), "epc": round(epc.value() or 0), "ccfd": round(ccfd.value() or 0),
            "budget_slack": sum(max(0.0, float(pulp.value(e)) - float(budget[i])) for i,e in enumerate(emis_exprs)),
            "cumulative_budget_tco2": float(budget.sum()),
            "budget_mode": budget_mode, "primal_feasibility": feasibility}


def _disclosed_fixed(d7, cf, techs, years, av):
    """Represent reviewed commitments exactly, with no date/technology substitution.

    The solve remains a model completion conditional on commitments, not the
    firm's full disclosed plan. Any unrepresented commitment invalidates it.
    """
    fixed = {"x": {}, "dropped": [], "valid": True,
             "comparison_basis": "commitment_constrained_model_completion"}
    sub = d7[d7.company_id.isin(cf.company_id.unique())]
    for _, r in sub.iterrows():
        if r.item_type in ("tech_commit", "ppa", "epc", "ccfd"):
            status = r.get("mapping_status", "")
            if status != "validated_exact" and r.source_id != "SAMPLE_SYNTH":
                fixed["dropped"].append(f"{r.facility_id}/{r.tech_id}: exact source-to-model mapping is unverified ({status})")
                continue
        if r.item_type == "tech_commit":
            if r.facility_id not in cf.index or pd.isna(r.year_stated):
                fixed["dropped"].append(f"{r.facility_id}/{r.tech_id}: facility or exact operation date unavailable")
                continue
            if pd.notna(r.coverage_pct) and float(r.coverage_pct) != 100:
                fixed["dropped"].append(f"{r.facility_id}/{r.tech_id}: partial coverage cannot be represented as full-facility conversion")
                continue
            tk = techs[techs.tech_id == r.tech_id]
            if not len(tk):
                print(f"[e2] warning: disclosed tech {r.tech_id!r} not in D3 — commitment dropped")
                fixed["dropped"].append(
                    f"{r.facility_id}/{r.tech_id}: 기술이 D3에 없음(모형 밖 수단)")
                continue
            if tk.applies_to_unit.iloc[0] != cf.loc[r.facility_id].unit_type:
                print(f"[e2] note: disclosed {r.facility_id}({cf.loc[r.facility_id].unit_type})/"
                      f"{r.tech_id} not applicable (applies to {tk.applies_to_unit.iloc[0]}) "
                      "— commitment dropped")
                fixed["dropped"].append(
                    f"{r.facility_id}/{r.tech_id}: 모형 규칙상 이 설비 유형에 적용 불가"
                    f"(A-10, {r.tech_id}는 {tk.applies_to_unit.iloc[0]}에만) — "
                    "공시 해상도 문제가 아니라 모형 경계 문제")
                continue
            build = int(tk.build_years.iloc[0])
            a0 = int(max(years[0], av.get(r.tech_id, tk.avail_year.iloc[0]), tk.avail_year.iloc[0]))
            hi = int(years[-1]) - build
            if a0 > hi:
                fixed["dropped"].append(f"{r.facility_id}/{r.tech_id}: technology unavailable within this horizon")
                continue
            ta = int(r.year_stated - build)
            if not a0 <= ta <= hi:
                fixed["dropped"].append(f"{r.facility_id}/{r.tech_id}: stated operation {r.year_stated} cannot be represented without shifting dates")
                continue
            fixed["x"][(r.facility_id, r.tech_id, ta)] = 1
        elif r.item_type in ("ppa", "epc", "ccfd") and pd.notna(r.year_stated) and r.year_stated > years[0]:
            fixed["dropped"].append(f"{r.item_type}: future contract start cannot be represented by a horizon-wide contract")
    ppa_rows = sub[sub.item_type == "ppa"].coverage_pct.dropna()
    fixed["ppa"] = float(ppa_rows.max()) / 100.0 if len(ppa_rows) else 0.0
    fixed["epc"] = 1 if len(sub[sub.item_type == "epc"]) else 0
    fixed["ccfd"] = 1 if len(sub[sub.item_type == "ccfd"]) else 0
    fixed["valid"] = not fixed["dropped"]
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

    index_rows, pid, skipped_rows = [], 0, []
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
            raise RuntimeError(f"No verified feasible endpoint for {company} {scen}; inspect solver/rejection reasons before claiming infeasibility")
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
        if (not disc_fixed["valid"] or
                (not disc_fixed["x"] and not disc_fixed["ppa"] and not disc_fixed["epc"] and not disc_fixed["ccfd"])):
            # no enforceable commitment survived — a "disclosed" solve would just be a
            # second unconstrained optimization whose surrogate near-optimum can differ
            # arbitrarily in E4 terms, fabricating a gap. 공시 해상도 부족 = gap 미식별 (§8-4).
            why = disc_fixed.get("dropped") or ["공시에 시설·기술이 특정된 커밋 자체가 없음"]
            print(f"[e2] note: {company} {scen} 공시 좌표 미산출 — 강제 가능한 커밋 없음. "
                  f"사유: {'; '.join(why)}", flush=True)
            skipped_rows.append([company, scen, "; ".join(why)])
            s_disc = None
        else:
            s_disc = _solve_company(*args, fixed=disc_fixed)
        if s_disc is None:
            print(f"[e2] warning: disclosed plan for {company} {scen} infeasible/unsolved — "
                  "no gap row will be produced in E5")
        if s_disc is not None:
            s_disc["disclosed"] = True
            s_disc["comparison_basis"] = disc_fixed["comparison_basis"]
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
                               bool(s.get("disclosed", False)), s.get("solve_status", "Optimal"),
                               s.get("comparison_basis", "optimized_candidate"),
                               s["cum_emis_tco2"], s["cumulative_budget_tco2"], s["budget_mode"],
                               s["primal_feasibility"]["valid"], s["primal_feasibility"]["solution_status"],
                               s["primal_feasibility"]["max_scaled_constraint_violation"],
                               s.get("mip_gap_actual", float("nan")), s.get("mip_lower_bound", float("nan"))])
        print(f"[e2] {n}/{len(combos)} {company} {scen} — 고유 계획 {len(sols)}개, "
              f"{time.time() - t_co:.0f}s", flush=True)

    pd.DataFrame(skipped_rows, columns=["company_id", "scenario", "reason"]).to_csv(
        odir / "disclosed_skipped.csv", index=False)
    idx = pd.DataFrame(index_rows, columns=["plan_id", "company_id", "scenario", "npv_cost_bnkrw",
                                            "risk_proxy", "ppa_share", "epc", "ccfd",
                               "budget_slack_tco2", "is_disclosed", "solve_status", "comparison_basis", "cum_emis_tco2", "cumulative_budget_tco2", "budget_mode", "primal_feasible", "solution_status", "max_scaled_constraint_violation", "mip_gap_actual", "mip_lower_bound"])
    idx.to_csv(odir / "plan_index.csv", index=False)
    return idx


if __name__ == "__main__":
    print(run(C.load()).to_string())
