"""Recompute annual budget excess from actual saved schedules, independent of MILP slack."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cap import config as C
from cap.e1_constraints import COMPANY_REGION
from cap.e2_milp import _prep_company
from cap.e4_revalue import _central_px
from cap.plancost import build_profile
from cap.risk_metrics import finite_candidate_gap


def compare_definitions(points, schedules):
    points = points.query("support == 'none'").merge(
        schedules[["company_id", "scenario", "base_plan_id", "annual_budget_feasible",
                   "signed_cumulative_excess_tco2"]],
        on=["company_id", "scenario", "base_plan_id"], validate="many_to_one")
    rows = []
    for (co, sc), g in points.groupby(["company_id", "scenario"]):
        candidates, disclosed = g[~g.is_disclosed], g[g.is_disclosed]
        masks = {"current_soft": candidates.budget_ok,
                 "annual_hard": candidates.annual_budget_feasible,
                 "horizon_cumulative_hard": candidates.signed_cumulative_excess_tco2 <= 1e-6}
        for rule, mask in masks.items():
            c = candidates[mask]
            row = dict(company_id=co, scenario=sc, budget_rule=rule, candidate_count=len(c),
                       minimum_median_cost=float(c.p50.min()) if len(c) else np.nan,
                       cost_gap=np.nan, risk_gap=np.nan,
                       disclosed_coordinate_available=bool(len(disclosed)))
            if len(disclosed):
                d = disclosed.iloc[0]
                row["cost_gap"], row["risk_gap"] = finite_candidate_gap(c.p50, c.tcar, d.p50, d.tcar)
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    cfg = C.load()
    fac, tech, cal = _prep_company(cfg, C.data_dir(cfg))
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    fp = C.out_dir(cfg, "e5") / "frontier_points.csv"
    bp = C.out_dir(cfg, "e1") / "constraints.csv"
    pp = C.out_dir(cfg, "e1") / "price_paths_central.csv"
    points, budgets, prices = (pd.read_csv(p) for p in (fp, bp, pp))
    paths = [fp, bp, pp, Path(__file__), ROOT / "config.yaml"]
    paths.extend(C.data_dir(cfg).glob("*.csv"))
    paths.extend((ROOT / "src/cap").glob("*.py"))
    rows = []
    for (co, sc, pid), g in points.groupby(["company_id", "scenario", "base_plan_id"]):
        plan_path = C.out_dir(cfg, "e2") / "plans" / f"plan_{pid}.csv"
        paths.append(plan_path)
        plan = pd.read_csv(plan_path)
        px = _central_px(prices, COMPANY_REGION[co], sc, years, cfg, cal)
        profile = build_profile(plan, fac, tech, px, years, cfg)
        budget = budgets.query("company_id == @co and scenario == @sc").set_index("year").company_budget_tco2.reindex(years).to_numpy()
        assert np.isfinite(budget).all()
        excess = np.maximum(profile.emissions - budget, 0)
        breaches = years[excess > 1e-6]
        actual = float(excess.sum())
        rows.append(dict(company_id=co, scenario=sc, base_plan_id=pid,
                         is_disclosed=bool(g.is_disclosed.iloc[0]),
                         eligible_in_current_menu=bool(g.budget_ok.any()),
                         candidate_variant_rows=len(g),
                         annual_budget_feasible=not len(breaches),
                         first_breach_year=int(breaches[0]) if len(breaches) else None,
                         breach_years=len(breaches),
                         sum_annual_excess_tco2=actual,
                         max_annual_excess_tco2=float(excess.max()),
                         signed_cumulative_excess_tco2=float((profile.emissions-budget).sum()),
                         saved_milp_slack_tco2=float(g.budget_slack_tco2.iloc[0]),
                         actual_minus_saved_slack_tco2=actual-float(g.budget_slack_tco2.iloc[0])))
    result = pd.DataFrame(rows)
    out = ROOT / "docs/research_cycles/2026-09-05"
    result.to_csv(out / "candidate_budget_audit.csv", index=False)
    compare_definitions(points, result).to_csv(out / "budget_definition_comparison.csv", index=False)
    manifest = {"scope": "Actual schedule quantity profiles vs annual E1 budgets; no use of MILP slack to decide compliance",
                "tolerance_tco2": 1e-6,
                "unique_schedules": len(result),
                "hard_feasible_schedules": int(result.annual_budget_feasible.sum()),
                "horizon_cumulative_feasible_schedules": int((result.signed_cumulative_excess_tco2 <= 1e-6).sum()),
                "candidate_rows": int(result.candidate_variant_rows.sum()),
                "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}}
    (out / "candidate_budget_audit_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(result.to_string(index=False))
    print(json.dumps({k:v for k,v in manifest.items() if k!='sha256'}))


if __name__ == "__main__":
    main()
