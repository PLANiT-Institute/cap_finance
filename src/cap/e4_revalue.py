"""E4 — revalue every plan across simulated price paths (REDESIGN_SPEC §3 E4).

For each plan x support scenario: NPV cost distribution over sims (fixed-plan mode).
Flexibility (⑤ input): plan-switching approximation — per sim, the company picks the
cheapest plan in its generated plan set. Lower bound of true re-optimization value
(true re-opt would re-solve the MILP per path; the plan set is the feasible menu we
already traced). ponytail: plan-switching lower bound; full per-sim re-MILP if ⑤ looks material.

Outputs: out/e4/cost_dist.parquet, out/e4/summary.csv, out/e4/flex_value.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .calibration import calibrate, hydrogen_price
from .e1_constraints import COMPANY_REGION
from .e2_milp import _prep_company
from .e3_prices import load_shocks
from .plancost import build_profile, simulate_cost, support_params
from .schemas import load_input


def _central_px(prices, region, scen, years, cfg=None, cal=None):
    out = {}
    for var, key in [("elec_price", "elec"), ("coal_price", "coal"), ("gas_price", "gas"),
                     ("co2_price", "co2")]:
        g = prices[(prices.region == region) & (prices.scenario == scen) & (prices.variable == var)]
        s = g.set_index("year").value.reindex(years)
        if s.isna().any():
            raise RuntimeError(f"central price path missing/incomplete: {var} {region} {scen} — check D2b")
        out[key] = s.to_numpy()
    # v2.1: externally procured hydrogen + renewable-procured transition power,
    # with graceful fallbacks (keeps synthetic sample data runnable)
    for var, key in [("h2_price", "h2"), ("re_price", "re")]:
        g = prices[(prices.region == region) & (prices.scenario == scen) & (prices.variable == var)]
        s = g.set_index("year").value.reindex(years)
        if s.isna().any() or s.empty:
            if key == "re":
                out["re"] = out["elec"]
            elif cal is not None and cfg is not None:
                out["h2"] = hydrogen_price(out["elec"], cal.ez_central(years), cfg.hydrogen)
            else:
                raise RuntimeError(f"h2_price missing for {region} {scen} and no fallback available")
        else:
            out[key] = s.to_numpy()
    return out


def run(cfg: C.Config):
    ddir = C.data_dir(cfg)
    odir = C.out_dir(cfg, "e4")
    e2dir = C.out_dir(cfg, "e2")
    fac, d3, cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    idx = pd.read_csv(e2dir / "plan_index.csv")
    shocks = load_shocks(cfg)
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    ones = {k: np.ones((1, len(years))) for k in shocks}

    dist_rows, summary_rows = [], []
    profiles = {}
    for _, pr in idx.iterrows():
        plan_df = pd.read_csv(e2dir / "plans" / f"plan_{pr.plan_id}.csv")
        region = COMPANY_REGION[pr.company_id]
        px = _central_px(prices, region, pr.scenario, years, cfg, cal)
        prof = build_profile(plan_df, fac, d3, px, years, cfg)
        profiles[pr.plan_id] = (prof, px)
        for supp in cfg.support_scenarios:
            sp = support_params(d5, supp, years)
            sims = simulate_cost(prof, px, shocks, sp, cfg)
            central = simulate_cost(prof, px, ones, sp, cfg)[0]
            dist_rows.append(pd.DataFrame({
                "plan_id": pr.plan_id, "company_id": pr.company_id, "scenario": pr.scenario,
                "support": supp, "sim": np.arange(len(sims)), "npv_cost_bnkrw": sims}))
            summary_rows.append([pr.plan_id, pr.company_id, pr.scenario, supp, central,
                                 float(np.median(sims)), float(np.percentile(sims, 90)),
                                 float(np.percentile(sims, 90) - np.median(sims))])

    dist = pd.concat(dist_rows, ignore_index=True)
    dist.to_parquet(odir / "cost_dist.parquet", index=False)
    summary = pd.DataFrame(summary_rows, columns=[
        "plan_id", "company_id", "scenario", "support", "central_cost",
        "p50", "p90", "tcar"])
    # surrogate wedge vs E2 objective — informational reconciliation (spec §3 E4 검증)
    summary = summary.merge(idx[["plan_id", "npv_cost_bnkrw"]].rename(
        columns={"npv_cost_bnkrw": "e2_surrogate_cost"}), on="plan_id", how="left")
    summary["surrogate_wedge"] = summary.central_cost - summary.e2_surrogate_cost
    summary.to_csv(odir / "summary.csv", index=False)

    # convergence check (spec §6-3): P50/TCaR on the first HALF of sims must be
    # within 1% of the full run — half-vs-full measures stability at the current
    # N (a fixed small subsample would never converge as N grows)
    nc = shocks["elec"].shape[0] // 2
    if 0 < nc < shocks["elec"].shape[0]:
        conv_rows = []
        for (pid, supp), g in dist.groupby(["plan_id", "support"]):
            full, part = g.npv_cost_bnkrw.to_numpy(), g.npv_cost_bnkrw.to_numpy()[:nc]
            denom = max(abs(np.median(full)), 1e-9)
            conv_rows.append([pid, supp,
                              abs(np.median(part) - np.median(full)) / denom,
                              abs((np.percentile(part, 90) - np.median(part))
                                  - (np.percentile(full, 90) - np.median(full))) / denom])
        conv = pd.DataFrame(conv_rows, columns=["plan_id", "support", "p50_reldiff", "tcar_reldiff"])
        conv.to_csv(odir / "convergence.csv", index=False)
        worst = conv[["p50_reldiff", "tcar_reldiff"]].max().max()
        if worst > 0.01:
            print(f"[e4] warning: convergence check failed (max rel diff {worst:.2%} > 1%) — "
                  "raise simulation.n_sims (spec: escalate to 10000)")

    # flexibility value (⑤): per company x scenario x support, on a sim subsample
    nf = min(cfg.simulation.n_sims_flex, shocks["elec"].shape[0])
    sub_shocks = {k: v[:nf] for k, v in shocks.items()}
    flex_rows = []
    for (company, scen, supp), g in summary.groupby(["company_id", "scenario", "support"]):
        plan_costs = []
        for plan_id in g.plan_id:
            prof, px = profiles[plan_id]
            sp = support_params(d5, supp, years)
            plan_costs.append(simulate_cost(prof, px, sub_shocks, sp, cfg))
        M = np.vstack(plan_costs)                       # (n_plans, nf)
        best_fixed = M[np.argmin(np.median(M, axis=1))]  # commit to ex-ante best plan
        switch = M.min(axis=0)                           # re-optimize (switch) per path
        flex_rows.append([company, scen, supp, float(np.median(best_fixed - switch)),
                          float((best_fixed - switch).mean())])
    flex = pd.DataFrame(flex_rows, columns=["company_id", "scenario", "support",
                                            "flex_value_p50", "flex_value_mean"])
    flex.to_csv(odir / "flex_value.csv", index=False)
    return summary, flex


if __name__ == "__main__":
    s, f = run(C.load())
    print(s.head().to_string(), "\n", f.to_string())
