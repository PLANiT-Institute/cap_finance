"""E5 — metrics ①–⑤, frontier, gap (REDESIGN_SPEC §3 E5).

Transition cost is INCREMENTAL: plan cost minus the no-transition baseline
(incumbent forever, market carbon price on full emissions), computed per sim so
the distribution is of the increment. ② divides P50 increment by cumulative
abatement (천원/tCO2). TCaR = P90 − P50 of the increment.

Variance decomposition (③): freeze one shock factor at central and measure the
variance drop. 'elec' freezes electricity (which also stabilizes the power part
of hydrogen — hydrogen is structurally derived); 'h2' freezes the electrolyzer
residual; 'capex' freezes the capex index.

④ = same-support P50 difference NZ15 − B20 per company (cost-min plans).
⑤ = from E4 flex_value.csv.

Outputs: out/e5/metrics_company.csv, frontier_points.csv, gap.csv, variance_decomp.csv
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from . import config as C
from .calibration import hydrogen_price
from .e1_constraints import COMPANY_REGION
from .e2_milp import _prep_company
from .e3_prices import load_shocks
from .e4_revalue import _central_px
from .plancost import SCALE, auction_share, build_profile, simulate_cost, support_params
from .schemas import load_input


def _carbon_npv(prof, px, disc, auc) -> float:
    """Deterministic NPV of carbon expenditure (bn KRW) — carbon price is a
    scenario path, not a simulated factor, so this is a per-plan constant.
    Must mirror simulate_cost's auction-share treatment or the resource-basis
    subtraction leaves a residue."""
    return float((prof.emissions * px["co2"] * auc / 1000.0 * disc).sum() * SCALE)


def _empty_plan(company):
    return pd.DataFrame([{"facility_id": None, "tech_id": None, "adopt_year": None,
                          "op_year": None, "company_id": company, "scenario": "-",
                          "ppa_share": 0.0, "epc": 0, "ccfd": 0}])


def _frontier(pts: pd.DataFrame) -> pd.DataFrame:
    """Lower-left envelope on (tcar, p50): sort by tcar, keep points with decreasing p50."""
    g = pts.sort_values(["tcar", "p50"]).drop_duplicates()
    keep, best = [], np.inf
    for r in g.itertuples():
        if r.p50 < best - 1e-9:
            keep.append(r.Index)
            best = r.p50
    return g.loc[keep]


def _gap(frontier: pd.DataFrame, point) -> tuple[float, float]:
    """(cost saving at same risk, risk reduction at same cost) — both >= 0.

    Point beyond the frontier's high end on an axis (dominated by an endpoint,
    the 설계서 그림 4 case) → measure against that endpoint: a conservative lower
    bound, since the endpoint achieves the saving with even less risk/cost.
    Point BELOW the frontier's low end (frontier cannot reach that risk/cost
    level) → NaN, np.interp clamping would fabricate a gap there."""
    f = frontier.sort_values("tcar")                            # p50 decreasing along f
    if point.tcar < f.tcar.min():
        dcost = float("nan")
    else:
        t = min(float(point.tcar), float(f.tcar.max()))
        dcost = max(0.0, float(point.p50 - np.interp(t, f.tcar, f.p50)))
    fi = f.sort_values("p50")
    if point.p50 < fi.p50.min():
        drisk = float("nan")
    else:
        c = min(float(point.p50), float(fi.p50.max()))
        drisk = max(0.0, float(point.tcar - np.interp(c, fi.p50, fi.tcar)))
    return dcost, drisk


def _affordability(metrics: pd.DataFrame, d6: pd.DataFrame) -> pd.DataFrame:
    """지표 ⑥ 조달 부담 — 전환 CAPEX를 기업 재무능력에 견준다 (D6 실적 소비).

    The frontier says what the transition costs; this says whether the balance
    sheet can carry it. Reference earnings = mean EBITDA of the last 3 reported
    years (cycle-smoothing; petrochemicals are mid-trough so a single year would
    read as either impossible or free). Negative reference EBITDA is reported as
    such rather than as an infinite ratio — it is the finding, not an error.
    `netdebt_to_ebitda_post` is the debt-financed upper bound (전액 차입 가정):
    it is a ceiling on leverage impact, not a forecast of the funding mix.

    POSCO and LOTTE carry no leverage figures. That is an ENTITY BOUNDARY problem,
    not a disclosure gap: D6's POSCO rows are the steel operating company (revenue
    37.6조) while the balance sheet that is readily available is the holding
    company's, consolidated or separate. Pairing group debt with operating-company
    EBITDA would produce a ratio that means nothing, so the field stays empty.
    """
    d6 = d6.sort_values("year")
    fin = []
    for cid, g in d6.groupby("company_id"):
        ebitda = g.ebitda.dropna()
        nd = g.dropna(subset=["net_debt"])
        rev = g.revenue.dropna()
        fin.append(dict(
            company_id=cid,
            ebitda_ref_bnkrw=float(ebitda.tail(3).mean()) if len(ebitda) else np.nan,
            ebitda_years=";".join(str(int(y)) for y in g.year[g.ebitda.notna()].tail(3)),
            revenue_latest_bnkrw=float(rev.iloc[-1]) if len(rev) else np.nan,
            net_debt_bnkrw=float(nd.net_debt.iloc[-1]) if len(nd) else np.nan,
        ))
    m = metrics.merge(pd.DataFrame(fin), on="company_id", how="left")

    e = m.ebitda_ref_bnkrw
    pos = e > 0                                    # ratios are meaningless on a loss
    m["capex_peak_to_ebitda"] = np.where(pos, m.capex_peak_bnkrw / e, np.nan)
    m["capex_total_to_ebitda"] = np.where(pos, m.capex_total_bnkrw / e, np.nan)
    m["capex_total_to_revenue_pct"] = 100 * m.capex_total_bnkrw / m.revenue_latest_bnkrw
    m["netdebt_to_ebitda_now"] = np.where(pos, m.net_debt_bnkrw / e, np.nan)
    m["netdebt_to_ebitda_post"] = np.where(pos, (m.net_debt_bnkrw + m.capex_total_bnkrw) / e, np.nan)
    m["funding_verdict"] = np.select(
        [~pos, m.capex_peak_to_ebitda <= 0.5, m.capex_peak_to_ebitda <= 1.0],
        ["EBITDA 음수 — 자체 조달 불가", "피크연도 EBITDA 절반 이내", "피크연도 EBITDA 1배 이내"],
        default="피크연도 EBITDA 초과 — 외부조달 필수")
    return m[["company_id", "scenario", "support", "capex_total_bnkrw", "capex_peak_bnkrw",
              "capex_peak_year", "ebitda_ref_bnkrw", "ebitda_years", "revenue_latest_bnkrw",
              "net_debt_bnkrw", "capex_peak_to_ebitda", "capex_total_to_ebitda",
              "capex_total_to_revenue_pct", "netdebt_to_ebitda_now", "netdebt_to_ebitda_post",
              "funding_verdict"]]


def run(cfg: C.Config):
    ddir = C.data_dir(cfg)
    odir = C.out_dir(cfg, "e5")
    e2dir = C.out_dir(cfg, "e2")
    fac, d3, cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    idx = pd.read_csv(e2dir / "plan_index.csv")
    # budget eligibility: E4 costs deliberately exclude the E2 budget-violation
    # penalty (a search device), so an eff-only plan that massively violates the
    # budget would otherwise win the frontier. A plan is 예산 정합 if its slack is
    # within 25% (+1Mt) of the least-violating plan of its company x scenario —
    # some slack is structural (residual EFs exceed late budgets).
    min_slack = (idx[~idx.is_disclosed].groupby(["company_id", "scenario"])
                 .budget_slack_tco2.min().rename("min_slack"))
    idx = idx.merge(min_slack, on=["company_id", "scenario"], how="left")
    idx["budget_ok"] = idx.budget_slack_tco2 <= idx.min_slack * 1.25 + 1e6
    flex = pd.read_csv(C.out_dir(cfg, "e4") / "flex_value.csv")
    shocks = load_shocks(cfg)
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc_v = (1 + cfg.discount_rate) ** -(years - years[0])
    auc_v = auction_share(years, cfg)

    frontier_rows, gap_rows, decomp_rows, metric_rows, path_rows, dist_rows, lam_rows = \
        [], [], [], [], [], [], []
    wedge_store: dict[str, list] = {}  # company -> [(vid, scen_origin, sched_df, ppa, epc)], every scenario's frontier
    # contract grid: contracts don't affect budget feasibility, so each distinct
    # tech schedule from E2 is expanded into PPA x EPC variants and revalued —
    # this traces the 설계서 P1(지연·스팟) → P6(조기·계약화) journey the MILP's
    # linearized contract terms collapse into corner solutions. CCfD stays 0
    # (no confirmed instrument in D5).
    CONTRACT_GRID = [(ppa, epc) for ppa in (0.0, 0.25, 0.5, 0.75, 1.0) for epc in (0, 1)]

    for (company, scen, supp) in [(c, s, u) for c in sorted(idx.company_id.unique())
                                  for s in cfg.scenarios for u in cfg.support_scenarios]:
        region = COMPANY_REGION[company]
        px = _central_px(prices, region, scen, years, cfg, cal)
        sp = support_params(d5, supp, years)
        base_prof = build_profile(_empty_plan(company), fac, d3, px, years, cfg)
        base_sims = simulate_cost(base_prof, px, shocks, sp, cfg)
        base_f_ch = {ch: simulate_cost(base_prof, px, shocks, sp, cfg, freeze=ch)
                     for ch in ["elec", "h2", "capex"]}

        g = idx[(idx.company_id == company) & (idx.scenario == scen)]
        if g.empty:
            print(f"[e5] warning: no plans for {company} {scen} — skipped")
            continue
        carb_base = _carbon_npv(base_prof, px, disc_v, auc_v)

        # unique tech schedules (disclosed kept as-is with its own contracts)
        scheds, disc_entry = {}, None
        for _, pr in g.iterrows():
            plan_df = pd.read_csv(e2dir / "plans" / f"plan_{pr.plan_id}.csv")
            key = tuple(sorted((r.facility_id, r.tech_id, int(r.adopt_year))
                               for r in plan_df.itertuples() if pd.notna(r.tech_id)))
            if pr.is_disclosed:
                disc_entry = (pr, plan_df)
                continue
            if key not in scheds or (bool(pr.budget_ok) and not scheds[key]["ok"]):
                scheds[key] = dict(pid=pr.plan_id, df=plan_df, ok=bool(pr.budget_ok),
                                   slack=float(pr.budget_slack_tco2))

        variants = []  # (vid, base_id, prof, ok, slack, is_disclosed)
        for sc_ in scheds.values():
            prof0 = build_profile(sc_["df"], fac, d3, px, years, cfg)
            for k, (ppa_v, epc_v) in enumerate(CONTRACT_GRID):
                variants.append((f"{sc_['pid']}.c{k:02d}", sc_["pid"],
                                 replace(prof0, ppa=ppa_v, epc=epc_v, ccfd=0),
                                 sc_["ok"], sc_["slack"], False))
        if disc_entry is not None:
            pr_d, df_d = disc_entry
            variants.append((pr_d.plan_id, pr_d.plan_id,
                             build_profile(df_d, fac, d3, px, years, cfg),
                             True, float(pr_d.budget_slack_tco2), True))

        rows, inc_store, prof_store = [], {}, {}
        for vid, bid, prof, ok, slack, isd in variants:
            sims = simulate_cost(prof, px, shocks, sp, cfg)
            inc = sims - base_sims
            p50_tot, p90_tot = float(np.median(inc)), float(np.percentile(inc, 90))
            # RESOURCE-cost basis: strip the deterministic carbon-expenditure delta
            # (carbon avoidance otherwise dominates; TCaR unaffected — 설계서 §4)
            dcarb = _carbon_npv(prof, px, disc_v, auc_v) - carb_base
            p50, p90 = p50_tot - dcarb, p90_tot - dcarb
            inc_store[vid] = inc - dcarb
            prof_store[vid] = prof
            abated = float(((base_prof.emissions - prof.emissions) * disc_v).sum())
            rows.append(dict(plan_id=vid, base_plan_id=bid, company_id=company, scenario=scen,
                             support=supp, p50=p50, p90=p90, tcar=p90 - p50,
                             p50_incl_carbon=p50_tot, carbon_delta=dcarb,
                             ppa_share=float(prof.ppa), epc=int(prof.epc), ccfd=int(prof.ccfd),
                             budget_ok=ok or isd, budget_slack_tco2=slack,
                             abated_tco2_disc=abated, is_disclosed=isd,
                             capex_total=float(prof.capex_k.sum() * 1e-6),
                             capex_peak=float(prof.capex_k.max() * 1e-6),
                             capex_peak_year=int(years[prof.capex_k.argmax()]) if prof.capex_k.any() else None))

        pts = pd.DataFrame(rows)
        fr = _frontier(pts[~pts.is_disclosed & pts.budget_ok])
        frontier_rows.append(pts.assign(on_frontier=pts.plan_id.isin(fr.plan_id)))

        # reference plan set for the policy wedge (그림 6): EVERY scenario's frontier.
        # Only the 1st scenario's was kept until D13, which made the regret table
        # one-directional — "hold the NZ15 plan and B20 happens" was priced, the
        # reverse was not, and an asymmetry you can't see reads as "delay is free".
        if supp == cfg.support_scenarios[0]:
            ref = []
            df_by_pid = {sc_["pid"]: sc_["df"] for sc_ in scheds.values()}
            for vid in fr.plan_id:
                bid, ck = vid.split(".c")
                ppa_v, epc_v = CONTRACT_GRID[int(ck)]
                ref.append((vid, scen, df_by_pid[bid], ppa_v, epc_v))
            wedge_store.setdefault(company, []).extend(ref)

        # decomposition by COST CHANNEL — frontier & disclosed plans only
        for vid in pts[pts.plan_id.isin(fr.plan_id) | pts.is_disclosed].plan_id:
            prof, inc = prof_store[vid], inc_store[vid]
            var_full = float(np.var(inc))
            for channel in ["elec", "h2", "capex"]:
                sims_f = simulate_cost(prof, px, shocks, sp, cfg, freeze=channel)
                contrib = 1 - np.var(sims_f - base_f_ch[channel]) / var_full if var_full > 0 else 0.0
                decomp_rows.append([vid, company, scen, supp, channel, max(0.0, float(contrib))])

        # λ tangency (설계서 그림 5): optimal plan = argmin(p50 + λ·TCaR) over
        # eligible plans. λ is exogenous — we report the tangent plan per λ.
        if supp == cfg.support_scenarios[0]:
            el = pts[~pts.is_disclosed & pts.budget_ok]
            if len(el):
                for lam in [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]:
                    w = el.p50 + lam * el.tcar
                    b = el.loc[w.idxmin()]
                    lam_rows.append([company, scen, lam, b.plan_id, b.base_plan_id,
                                     round(b.p50, 1), round(b.tcar, 1),
                                     round(b.ppa_share, 2), int(b.epc)])

        # cost distribution (그림 2 유형): cost-min & disclosed plans, first support only
        if supp == cfg.support_scenarios[0]:
            picks = {}
            el = pts[~pts.is_disclosed & pts.budget_ok]
            if len(el):
                picks["cost_min"] = el.loc[el.p50.idxmin()].plan_id
            dl = pts[pts.is_disclosed]
            if len(dl):
                picks["disclosed"] = dl.plan_id.iloc[0]
            for kind, pid in picks.items():
                arr = inc_store[pid]
                # clip at P99 so the display range isn't dominated by the extreme tail
                counts, edges = np.histogram(arr, bins=40,
                                             range=(float(arr.min()), float(np.percentile(arr, 99))))
                for c, lo, hi in zip(counts, edges[:-1], edges[1:]):
                    dist_rows.append([company, scen, kind, pid, float(lo), float(hi), int(c),
                                      float(np.median(arr)), float(np.percentile(arr, 90))])

        # emissions pathway: baseline / cost-min / disclosed vs company budget
        # (facility-level tech switches make these stepwise)
        if supp == cfg.support_scenarios[0]:
            budget = (pd.read_csv(C.out_dir(cfg, "e1") / "constraints.csv")
                      .query("company_id == @company and scenario == @scen")
                      .set_index("year").company_budget_tco2.reindex(years))
            sel = {"baseline": base_prof}
            gm0 = pts[~pts.is_disclosed & pts.budget_ok]
            if len(gm0):
                sel["cost_min"] = prof_store[gm0.loc[gm0.p50.idxmin()].plan_id]
            dp_ = pts[pts.is_disclosed]
            if len(dp_):
                sel["disclosed"] = prof_store[dp_.plan_id.iloc[0]]
            for label, prof_ in sel.items():
                for y, e in zip(years, prof_.emissions):
                    path_rows.append([company, scen, label, int(y), float(e), float(budget[y])])

        disc = pts[pts.is_disclosed]
        if len(disc) and len(fr) >= 1:
            dcost, drisk = _gap(fr, disc.iloc[0])
            gap_rows.append([company, scen, supp, disc.plan_id.iloc[0],
                             disc.p50.iloc[0], disc.tcar.iloc[0], dcost, drisk])

    # policy stringency wedge (설계서 그림 6): the SAME plans (1st-scenario frontier,
    # schedule+contracts fixed) revalued under every scenario's prices and baseline —
    # the per-plan gap between the two evaluations is exposure to policy STRINGENCY,
    # not stochastic price risk (metric ④ at plan level).
    # `p50` keeps the resource-cost basis used everywhere else (carbon expenditure
    # stripped) so 그림 6 stays comparable with the frontier. That basis is NOT
    # comparable ACROSS scenarios, though: a plan that abates less looks cheaper
    # precisely because the carbon bill it pays has been removed. Regret in either
    # direction therefore reads off `p50_incl_carbon`, and `budget_gap_tco2` says
    # whether the plan even meets the evaluating scenario's budget (a B20 plan under
    # NZ15 usually does not — that overshoot is the thing money can't buy back).
    wedge_rows = []
    supp0 = cfg.support_scenarios[0]
    sp0 = support_params(d5, supp0, years)
    budgets = pd.read_csv(C.out_dir(cfg, "e1") / "constraints.csv")
    for company, ref in wedge_store.items():
        region = COMPANY_REGION[company]
        for scen in cfg.scenarios:
            px = _central_px(prices, region, scen, years, cfg, cal)
            base_prof = build_profile(_empty_plan(company), fac, d3, px, years, cfg)
            base_sims = simulate_cost(base_prof, px, shocks, sp0, cfg)
            carb_base = _carbon_npv(base_prof, px, disc_v, auc_v)
            bud = (budgets.query("company_id == @company and scenario == @scen")
                   .set_index("year").company_budget_tco2.reindex(years).to_numpy())
            for vid, scen_origin, sched_df, ppa_v, epc_v in ref:
                prof = replace(build_profile(sched_df, fac, d3, px, years, cfg),
                               ppa=ppa_v, epc=epc_v, ccfd=0)
                sims = simulate_cost(prof, px, shocks, sp0, cfg)
                inc_tot = sims - base_sims
                inc = inc_tot - (_carbon_npv(prof, px, disc_v, auc_v) - carb_base)
                p50w, p90w = float(np.median(inc)), float(np.percentile(inc, 90))
                over = float(np.maximum(prof.emissions - bud, 0.0).sum())
                wedge_rows.append([company, vid, scen_origin, scen,
                                   round(p50w, 1), round(p90w - p50w, 1),
                                   round(float(np.median(inc_tot)), 1), round(over, 1)])
    pd.DataFrame(wedge_rows, columns=["company_id", "plan_id", "scen_origin", "scen_eval",
                                      "p50", "tcar", "p50_incl_carbon", "budget_gap_tco2"]
                 ).to_csv(odir / "policy_wedge.csv", index=False)

    frontier = pd.concat(frontier_rows, ignore_index=True)
    frontier.to_csv(odir / "frontier_points.csv", index=False)
    pd.DataFrame(path_rows, columns=["company_id", "scenario", "plan", "year",
                                     "emissions_tco2", "budget_tco2"]
                 ).to_csv(odir / "emissions_pathway.csv", index=False)
    pd.DataFrame(dist_rows, columns=["company_id", "scenario", "plan_kind", "plan_id",
                                     "bin_lo", "bin_hi", "count", "p50", "p90"]
                 ).to_csv(odir / "cost_distribution.csv", index=False)
    pd.DataFrame(lam_rows, columns=["company_id", "scenario", "lam", "plan_id", "base_plan_id",
                                    "p50", "tcar", "ppa_share", "epc"]
                 ).to_csv(odir / "lambda_tangency.csv", index=False)
    gap = pd.DataFrame(gap_rows, columns=["company_id", "scenario", "support", "plan_id",
                                          "p50", "tcar", "gap_cost_bnkrw", "gap_risk_bnkrw"])
    gap.to_csv(odir / "gap.csv", index=False)
    decomp = pd.DataFrame(decomp_rows, columns=["plan_id", "company_id", "scenario", "support",
                                                "factor", "variance_share"])
    decomp.to_csv(odir / "variance_decomp.csv", index=False)

    # company metrics ①–⑤ (cost-min plan of each company x scenario x support)
    for (company, scen, supp), g in frontier.groupby(["company_id", "scenario", "support"]):
        gm = g[~g.is_disclosed & g.budget_ok]
        if gm.empty:
            print(f"[e5] warning: only disclosed plan exists for {company} {scen} {supp} — metrics skipped")
            continue
        best = gm.loc[gm.p50.idxmin()]
        m2 = best.p50 * 1e6 / best.abated_tco2_disc if best.abated_tco2_disc > 0 else np.nan
        f5 = flex[(flex.company_id == company) & (flex.scenario == scen) & (flex.support == supp)]
        metric_rows.append([company, scen, supp,
                            best.capex_total, best.capex_peak, best.capex_peak_year,   # ①
                            best.p50, m2,                                  # ② (자원비용 bn KRW, 천원/tCO2 disc)
                            best.tcar,                                     # ③
                            f5.flex_value_mean.iloc[0] if len(f5) else np.nan,  # ⑤ (mean; p50 degenerates to 0)
                            best.p50_incl_carbon, best.carbon_delta])
    metrics = pd.DataFrame(metric_rows, columns=[
        "company_id", "scenario", "support", "capex_total_bnkrw", "capex_peak_bnkrw", "capex_peak_year",
        "p50_bnkrw", "cost_per_tco2_thkrw", "tcar_bnkrw", "flex_value_bnkrw",
        "p50_incl_carbon_bnkrw", "carbon_delta_bnkrw"])
    # ④ policy exposure: scenarios[0] − scenarios[1] within support (config-driven)
    piv = metrics.pivot_table(index=["company_id", "support"], columns="scenario", values="p50_bnkrw")
    s_hi, s_lo = (cfg.scenarios + [None, None])[:2]
    if s_lo is not None and {s_hi, s_lo} <= set(piv.columns):
        piv["policy_exposure_bnkrw"] = piv[s_hi] - piv[s_lo]
        metrics = metrics.merge(piv[["policy_exposure_bnkrw"]].reset_index(),
                                on=["company_id", "support"], how="left")
    metrics.to_csv(odir / "metrics_company.csv", index=False)
    _affordability(metrics, load_input(ddir, "D6_company_financials")).to_csv(
        odir / "affordability.csv", index=False)

    # spec checks: frontier monotone, gaps non-negative (NaN = point outside frontier range, allowed)
    for _, fgrp in frontier[frontier.on_frontier].groupby(["company_id", "scenario", "support"]):
        f = fgrp.sort_values("tcar")
        assert (f.p50.diff().dropna() <= 1e-6).all(), "frontier not monotone"
    gv = gap[["gap_cost_bnkrw", "gap_risk_bnkrw"]]
    assert ((gv >= 0) | gv.isna()).all().all()
    return metrics, frontier, gap, decomp


if __name__ == "__main__":
    m, *_ = run(C.load())
    print(m.to_string())
