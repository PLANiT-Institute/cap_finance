"""E5 — metrics ①–⑤, frontier, gap (REDESIGN_SPEC §3 E5).

Transition cost is INCREMENTAL: plan cost minus the no-transition baseline
(incumbent forever, market carbon price on full emissions), computed per sim so
the distribution is of the increment. ② divides P50 increment by cumulative
abatement (천원/tCO2). TCaR = P90 − P50 of the increment.

Variance decomposition (③): freeze one shock factor at central and measure the
variance drop. 'elec' freezes grid and renewable-procured electricity; 'h2'
freezes the separately procured hydrogen price; 'capex' freezes the capex index.

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
from .financial_reference import comparable_funding_ratios
from .risk_metrics import finite_candidate_gap, loss_summary, sampled_dominance_witnesses, pareto_mask


def evaluation_contract_grid(cfg):
    """Contract menu for final evaluation, separate from E2 candidate generation.

    Preserve the historical menu when unspecified. New research runs can
    explicitly exclude assumed contracts or declare a reviewed comparison menu.
    These settings describe idealised price fixation, not executable quotes.
    """
    policy=cfg.get('evaluation_contracts','legacy_grid')
    if policy=='unhedged':
        return [(0.,0)]
    if policy=='legacy_grid':
        return [(ppa,epc) for ppa in (0.,.25,.5,.75,1.) for epc in (0,1)]
    if policy!='explicit_grid':
        raise ValueError('evaluation_contracts must be unhedged, legacy_grid or explicit_grid')
    entries=cfg.get('evaluation_contract_grid')
    if not isinstance(entries,list) or not entries:
        raise ValueError('An explicit evaluation contract grid must be a nonempty list')
    result=[]
    for row in entries:
        if not isinstance(row,dict) or set(row)!={'ppa_share','epc'}:
            raise ValueError('Each contract row must specify exactly ppa_share and epc')
        ppa,epc=row['ppa_share'],row['epc']
        if isinstance(ppa,bool) or not isinstance(ppa,(int,float)) or not np.isfinite(ppa) or not 0<=ppa<=1:
            raise ValueError('PPA share must be finite and between0and1')
        if isinstance(epc,bool) or not isinstance(epc,int) or epc not in (0,1):
            raise ValueError('EPC must be integer0or1')
        item=(float(ppa),epc)
        if item in result:
            raise ValueError('Duplicate evaluation contract variant')
        result.append(item)
    return result


def _carbon_npv(prof, px, disc, auc) -> float:
    """Deterministic NPV of carbon expenditure (bn KRW) — carbon price is a
    scenario path, not a simulated factor, so this is a per-plan constant.
    Must mirror simulate_cost's auction-share treatment or the resource-basis
    subtraction leaves a residue."""
    allocation = prof.free_allowances_tco2 if prof.free_allowances_tco2 is not None else 0.0
    # Resource-basis subtraction uses the profile's explicit net allocation.
    obligation = prof.emissions - allocation
    if prof.carbon_accounting_basis == "purchase_only":
        obligation = np.maximum(obligation, 0)
    return float((obligation * px["co2"] * auc / 1000.0 * disc).sum() * SCALE)


def _empty_plan(company, scenario="-"):
    return pd.DataFrame([{"facility_id": None, "tech_id": None, "adopt_year": None,
                          "op_year": None, "company_id": company, "scenario": scenario,
                          "ppa_share": 0.0, "epc": 0, "ccfd": 0}])


def frontier_axes(cfg) -> tuple[str, str]:
    """(cost axis, risk axis) of the canonical frontier.

    v1 historical: (p50, tcar) — the rule Proposition 6 warns against.
    v2 (finding A1/B3): (mean, es_abs) — expected incremental cost against the
    Expected Shortfall of the plan's OWN absolute cost distribution, so that a
    plan which removes exposure (e.g. to a stochastic carbon price) is credited
    with lower risk instead of being charged tracking error against a baseline
    that violates the target.
    """
    axes = cfg.get("frontier_axes", ["p50", "tcar"])
    if not (isinstance(axes, (list, tuple)) and len(axes) == 2):
        raise ValueError("frontier_axes must be a two-item list [cost, risk]")
    return str(axes[0]), str(axes[1])


def _frontier(pts: pd.DataFrame, cost: str = "p50", risk: str = "tcar") -> pd.DataFrame:
    """Lower-left envelope on (risk, cost): sort by risk, keep points with decreasing cost."""
    g = pts.sort_values([risk, cost]).drop_duplicates()
    keep, best = [], np.inf
    for r in g.itertuples():
        if getattr(r, cost) < best - 1e-9:
            keep.append(r.Index)
            best = getattr(r, cost)
    return g.loc[keep]


def _gap(frontier: pd.DataFrame, point) -> tuple[float, float]:
    """Attainable savings from actual candidates, with no increase in the other axis.

    The two comparisons can select different plans. Zero means no improvement;
    NaN means no candidate reaches the corresponding threshold. Connecting
    discrete frontier coordinates does not create an attainable investment plan.
    """
    return finite_candidate_gap(frontier.p50, frontier.tcar, point.p50, point.tcar)


def _gap_witnesses(frontier: pd.DataFrame, point) -> tuple[str | None, str | None]:
    """IDs attaining positive cost/risk savings; no witness is claimed for zero/NaN."""
    dcost, drisk = _gap(frontier, point)
    cost = frontier[frontier.tcar <= point.tcar + 1e-9].sort_values(["p50", "tcar", "plan_id"])
    risk = frontier[frontier.p50 <= point.p50 + 1e-9].sort_values(["tcar", "p50", "plan_id"])
    return (str(cost.iloc[0].plan_id) if dcost > 0 else None,
            str(risk.iloc[0].plan_id) if drisk > 0 else None)


def _affordability(metrics: pd.DataFrame, d6: pd.DataFrame, cfg=None) -> pd.DataFrame:
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
    if cfg is None or cfg.get("financial_boundary_mode", "strict") == "strict":
        return comparable_funding_ratios(metrics, d6)
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
    budget_mode = cfg.get("budget_mode", "legacy_relative_slack")
    if budget_mode == "cumulative_hard":
        idx["budget_ok"] = idx.cum_emis_tco2 <= idx.cumulative_budget_tco2 + 1e-6 * np.maximum(1.0,idx.cumulative_budget_tco2)
    elif budget_mode == "annual_hard":
        idx["budget_ok"] = idx.budget_slack_tco2 <= 1e-3
    elif budget_mode == "legacy_relative_slack":
        idx["budget_ok"] = idx.budget_slack_tco2 <= idx.min_slack * 1.25 + 1e6
    else:
        raise ValueError(f"Unknown budget mode: {budget_mode}")
    loss_basis = cfg.get("transition_loss_basis", "incremental_cash")
    if loss_basis not in ("incremental_cash", "incremental_ex_carbon"):
        raise ValueError(f"Unknown transition loss basis: {loss_basis}")
    flex = pd.read_csv(C.out_dir(cfg, "e4") / "flex_value.csv")
    shocks = load_shocks(cfg)
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc_v = (1.0 + cfg.discount_rate) ** -(years - years[0])
    auc_v = auction_share(years, cfg)

    selection = cfg.get("plan_selection_criterion", "mean")
    if selection not in ("p50", "mean"):
        raise ValueError("plan_selection_criterion must be p50 or mean")
    cost_axis, risk_axis = frontier_axes(cfg)
    hedge_basis = cfg.get("hedge_basis", "total_purchase")
    if hedge_basis not in ("total_purchase", "incremental"):
        raise ValueError("hedge_basis must be total_purchase (v1) or incremental (v2)")
    # decomposition channels: every simulated factor that actually varies
    channels = [k for k in shocks if k != "electrolyzer" and float(np.var(shocks[k])) > 0]
    if str(cfg.get("price_factor_set", "v1")).lower() == "v2" and "h2" in channels:
        # v2: h2 shock is a deterministic function of the elec shock (E3); it is
        # not a separate source of variance, so it is folded into 'elec'.
        channels.remove("h2")
    frontier_rows, gap_rows, decomp_rows, metric_rows, path_rows, dist_rows, lam_rows = \
        [], [], [], [], [], [], []
    wedge_store: dict[str, list] = {}  # company -> [(vid, scen_origin, sched_df, ppa, epc)], every scenario's frontier
    # contract grid: contracts don't affect budget feasibility, so each distinct
    # tech schedule from E2 is expanded into PPA x EPC variants and revalued —
    # this traces the 설계서 P1(지연·스팟) → P6(조기·계약화) journey the MILP's
    # linearized contract terms collapse into corner solutions. CCfD stays 0
    # (no confirmed instrument in D5).
    CONTRACT_GRID = evaluation_contract_grid(cfg)

    for (company, scen, supp) in [(c, s, u) for c in sorted(idx.company_id.unique())
                                  for s in cfg.scenarios for u in cfg.support_scenarios]:
        region = COMPANY_REGION[company]
        px = _central_px(prices, region, scen, years, cfg, cal)
        sp = support_params(d5, supp, years)
        base_prof = build_profile(_empty_plan(company, scen), fac, d3, px, years, cfg)
        base_sims = simulate_cost(base_prof, px, shocks, sp, cfg)
        base_stats = loss_summary(base_sims)
        base_f_ch = {ch: simulate_cost(base_prof, px, shocks, sp, cfg, freeze=ch)
                     for ch in channels}
        hedge_ref = (base_prof.grid_mwh + base_prof.re_mwh) if hedge_basis == "incremental" else None

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
                                 replace(prof0, ppa=ppa_v, epc=epc_v, ccfd=0, hedge_reference_mwh=hedge_ref),
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
            evaluated = inc - dcarb if loss_basis == "incremental_ex_carbon" else inc
            statistics = loss_summary(evaluated)
            absolute = loss_summary(sims)          # the plan's own cost distribution (v2 risk axis)
            p50, p90 = statistics["p50"], statistics["q_alpha"]
            inc_store[vid] = evaluated
            prof_store[vid] = prof
            abated = float(((base_prof.emissions - prof.emissions) * disc_v).sum())
            rows.append(dict(plan_id=vid, base_plan_id=bid, company_id=company, scenario=scen,
                             support=supp, p50=p50, p90=p90, tcar=p90 - p50,
                             mean=statistics["mean"], es_alpha=statistics["es_alpha"],
                             alpha=statistics["alpha"], n_draws=statistics["n_draws"],
                             p50_abs=absolute["p50"], mean_abs=absolute["mean"],
                             tcar_abs=absolute["q_alpha"] - absolute["p50"], es_abs=absolute["es_alpha"],
                             es_abs_vs_baseline=absolute["es_alpha"] - base_stats["es_alpha"],
                             tcar_abs_vs_baseline=(absolute["q_alpha"] - absolute["p50"])
                                                  - (base_stats["q_alpha"] - base_stats["p50"]),
                             hedge_basis=hedge_basis,
                             loss_basis=loss_basis, budget_mode=budget_mode,
                             capital_accounting=cfg.get("capital_accounting", "cash_v1"),
                             carbon_accounting=cfg.get("carbon_accounting_mode", "gross_obligation_proxy"),
                             p50_incl_carbon=p50_tot, carbon_delta=dcarb,
                             ppa_share=float(prof.ppa), epc=int(prof.epc), ccfd=int(prof.ccfd),
                             budget_ok=ok or isd, budget_slack_tco2=slack,
                             abated_tco2_disc=abated, is_disclosed=isd,
                             capex_total=float(prof.capex_k.sum() * 1e-6),
                             capex_peak=float(prof.capex_k.max() * 1e-6),
                             capex_peak_year=int(years[prof.capex_k.argmax()]) if prof.capex_k.any() else None))

        pts = pd.DataFrame(rows)
        eligible = pts[~pts.is_disclosed & pts.budget_ok]
        witnesses = sampled_dominance_witnesses({pid:inc_store[pid] for pid in eligible.plan_id})
        pts["sampled_dominance_witness"] = pts.plan_id.map(witnesses).fillna("")
        pts["sampled_statewise_dominated"] = pts.plan_id.isin(witnesses)
        pts["decision_eligible"] = (~pts.is_disclosed & pts.budget_ok & ~pts.sampled_statewise_dominated)
        # frontier flags are computed on the DECISION-ELIGIBLE set (B3: a sampled-
        # dominated candidate can no longer be flagged non-dominated)
        elig = pts[pts.decision_eligible]
        for cost,risk,label in [("mean","tcar","on_mean_tcar_frontier"),("mean","es_alpha","on_mean_es_frontier"),
                                ("mean","es_abs","on_mean_esabs_frontier"),("mean","tcar_abs","on_mean_tcarabs_frontier")]:
            pts[label] = False
            if len(elig):
                pts.loc[elig.index,label] = pareto_mask(elig[cost],elig[risk])
        fr = _frontier(elig if len(elig) else pts[~pts.is_disclosed & pts.budget_ok], cost_axis, risk_axis)
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
            for channel in channels:
                sims_f = simulate_cost(prof, px, shocks, sp, cfg, freeze=channel)
                contrib = 1 - np.var(sims_f - base_f_ch[channel]) / var_full if var_full > 0 else 0.0
                decomp_rows.append([vid, company, scen, supp, channel, float(contrib)])  # signed: under correlated factors freezing one channel can RAISE incremental variance (coal vs elec, corr 0.84)

        # λ tangency (설계서 그림 5): optimal plan = argmin(cost + λ·risk) over the
        # canonical axes. λ is exogenous — we report the tangent plan per λ. v1 used
        # (p50, tcar); Proposition 6 shows that rule can pick a statewise-dominated
        # plan, so v2 runs it on (mean, es_abs) over decision-eligible plans only.
        if supp == cfg.support_scenarios[0]:
            el = pts[pts.decision_eligible] if len(pts[pts.decision_eligible]) else pts[~pts.is_disclosed & pts.budget_ok]
            if len(el):
                for lam in [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]:
                    w = el[cost_axis] + lam * el[risk_axis]
                    b = el.loc[w.idxmin()]
                    lam_rows.append([company, scen, lam, b.plan_id, b.base_plan_id,
                                     round(float(b[cost_axis]), 1), round(float(b[risk_axis]), 1),
                                     round(b.ppa_share, 2), int(b.epc), cost_axis, risk_axis])

        # cost distribution (그림 2 유형): cost-min & disclosed plans, first support only
        if supp == cfg.support_scenarios[0]:
            picks = {}
            el = pts[~pts.is_disclosed & pts.budget_ok]
            if len(el):
                candidates = el[el.decision_eligible] if selection == "mean" else el
                picks["cost_min"] = candidates.sort_values([selection,"es_alpha","plan_id"]).iloc[0].plan_id
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
                candidates = gm0[gm0.decision_eligible] if selection == "mean" else gm0
                sel["cost_min"] = prof_store[candidates.sort_values([selection,"es_alpha","plan_id"]).iloc[0].plan_id]
            dp_ = pts[pts.is_disclosed]
            if len(dp_):
                sel["disclosed"] = prof_store[dp_.plan_id.iloc[0]]
            for label, prof_ in sel.items():
                for y, e in zip(years, prof_.emissions):
                    path_rows.append([company, scen, label, int(y), float(e), float(budget[y])])

        disc = pts[pts.is_disclosed]
        if len(disc) and len(fr) >= 1:
            dcost, drisk = _gap(fr, disc.iloc[0])
            wc, wr = _gap_witnesses(fr, disc.iloc[0])
            gap_rows.append([company, scen, supp, disc.plan_id.iloc[0],
                             disc.p50.iloc[0], disc.tcar.iloc[0], dcost, drisk,
                             wc, wr, "attainable_discrete_candidates",
                             disc_entry[0].get("comparison_basis", "historical_unverified_proxy")])

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
            base_prof = build_profile(_empty_plan(company, scen), fac, d3, px, years, cfg)
            base_sims = simulate_cost(base_prof, px, shocks, sp0, cfg)
            carb_base = _carbon_npv(base_prof, px, disc_v, auc_v)
            bud = (budgets.query("company_id == @company and scenario == @scen")
                   .set_index("year").company_budget_tco2.reindex(years).to_numpy())
            hedge_ref_w = (base_prof.grid_mwh + base_prof.re_mwh) if hedge_basis == "incremental" else None
            for vid, scen_origin, sched_df, ppa_v, epc_v in ref:
                # The plan is revalued under the EVALUATING scenario: prices, baseline
                # AND free allocation (company_budget_path follows `scenario`), and the
                # same incremental hedge reference as the main loop. Using the origin
                # scenario's allocation understated cross-scenario regret (re-audit N1/N2).
                prof = replace(build_profile(sched_df.assign(scenario=scen), fac, d3, px, years, cfg),
                               ppa=ppa_v, epc=epc_v, ccfd=0, hedge_reference_mwh=hedge_ref_w)
                sims = simulate_cost(prof, px, shocks, sp0, cfg)
                inc_tot = sims - base_sims
                inc = (inc_tot - (_carbon_npv(prof, px, disc_v, auc_v) - carb_base)
                       if loss_basis == "incremental_ex_carbon" else inc_tot)
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
                                    "cost", "risk", "ppa_share", "epc", "cost_axis", "risk_axis"]
                 ).to_csv(odir / "lambda_tangency.csv", index=False)
    gap = pd.DataFrame(gap_rows, columns=["company_id", "scenario", "support", "plan_id",
                                          "p50", "tcar", "gap_cost_bnkrw", "gap_risk_bnkrw",
                                          "cost_witness_plan_id", "risk_witness_plan_id", "gap_method", "comparison_basis"])
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
        candidates = gm[gm.decision_eligible] if selection == "mean" else gm
        best = candidates.sort_values([selection,risk_axis,"plan_id"]).iloc[0]
        risk_min = candidates.sort_values([risk_axis,selection,"plan_id"]).iloc[0]
        m2 = best.p50 * 1e6 / best.abated_tco2_disc if best.abated_tco2_disc > 0 else np.nan
        f5 = flex[(flex.company_id == company) & (flex.scenario == scen) & (flex.support == supp)]
        metric_rows.append([company, scen, supp,
                            best.capex_total, best.capex_peak, best.capex_peak_year,   # ①
                            best.p50, m2,                                  # ② (자원비용 bn KRW, 천원/tCO2 disc)
                            best.tcar,                                     # ③
                            f5.flex_value_mean.iloc[0] if len(f5) else np.nan,  # ⑤ (mean; p50 degenerates to 0)
                            best.p50_incl_carbon, best.carbon_delta,
                            best["mean"], best.es_alpha, best.plan_id, selection, loss_basis,
                            budget_mode, best.capital_accounting, best.carbon_accounting,
                            best.es_abs, best.tcar_abs, best.es_abs_vs_baseline,
                            risk_axis, risk_min.plan_id, float(risk_min["mean"]), float(risk_min[risk_axis]),
                            float(risk_min.ppa_share), int(risk_min.epc), best.hedge_basis])
    metrics = pd.DataFrame(metric_rows, columns=[
        "company_id", "scenario", "support", "capex_total_bnkrw", "capex_peak_bnkrw", "capex_peak_year",
        "p50_bnkrw", "cost_per_tco2_thkrw", "tcar_bnkrw", "flex_value_bnkrw",
        "p50_incl_carbon_bnkrw", "carbon_delta_bnkrw", "mean_bnkrw", "es_alpha_bnkrw",
        "selected_plan_id", "selection_criterion", "loss_basis", "budget_mode",
        "capital_accounting", "carbon_accounting",
        "es_abs_bnkrw", "tcar_abs_bnkrw", "es_abs_vs_baseline_bnkrw",
        "risk_axis", "risk_min_plan_id", "risk_min_mean_bnkrw", "risk_min_risk_bnkrw",
        "risk_min_ppa_share", "risk_min_epc", "hedge_basis"])
    # ④ policy exposure: scenarios[0] − scenarios[1] within support (config-driven)
    piv = metrics.pivot_table(index=["company_id", "support"], columns="scenario", values="p50_bnkrw")
    s_hi, s_lo = (cfg.scenarios + [None, None])[:2]
    if s_lo is not None and {s_hi, s_lo} <= set(piv.columns):
        piv["policy_exposure_bnkrw"] = piv[s_hi] - piv[s_lo]
        metrics = metrics.merge(piv[["policy_exposure_bnkrw"]].reset_index(),
                                on=["company_id", "support"], how="left")
    metrics.to_csv(odir / "metrics_company.csv", index=False)
    _affordability(metrics, load_input(ddir, "D6_company_financials"), cfg).to_csv(
        odir / "affordability.csv", index=False)

    # spec checks: frontier monotone, gaps non-negative (NaN = point outside frontier range, allowed)
    for _, fgrp in frontier[frontier.on_frontier].groupby(["company_id", "scenario", "support"]):
        f = fgrp.sort_values(risk_axis)
        assert (f[cost_axis].diff().dropna() <= 1e-6).all(), "frontier not monotone"
    gv = gap[["gap_cost_bnkrw", "gap_risk_bnkrw"]]
    assert ((gv >= 0) | gv.isna()).all().all()
    return metrics, frontier, gap, decomp


if __name__ == "__main__":
    m, *_ = run(C.load())
    print(m.to_string())
