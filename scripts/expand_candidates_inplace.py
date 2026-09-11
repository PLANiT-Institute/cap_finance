"""Add emission-direction candidates to an existing E2 menu, in place (L6, 2026-09-11).

Same construction as expand_research_candidates.py (minimum-emissions plan plus
cost minimisers at emission caps between that minimum and the budget) without
the parent-run bookkeeping, so a freshly regenerated E2 menu can be widened
before E3–E5. Existing plans are preserved; duplicates by schedule signature
are skipped; every attempt is logged to e2/expansion_attempts.csv.

Usage: python scripts/expand_candidates_inplace.py --config <run config> [--emissions-points 4]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.e2_milp import _prep_company, _solve_company  # noqa: E402


def signature(plan):
    return tuple(sorted((r.facility_id, r.tech_id, int(r.adopt_year))
                        for r in plan.itertuples() if pd.notna(r.tech_id)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--emissions-points", type=int, default=4)
    a = ap.parse_args(argv)
    cfg = C.load(a.config)
    out = Path(C.out_dir(cfg, "e2")).parent
    fac, tech, cal = _prep_company(cfg, C.data_dir(cfg))
    prices = pd.read_csv(out / "e1/price_paths_central.csv")
    constraints = pd.read_csv(out / "e1/constraints.csv")
    availability = pd.read_csv(out / "e1/tech_availability.csv")
    idx = pd.read_csv(out / "e2/plan_index.csv")
    next_id = max(int(x[1:]) for x in idx.plan_id) + 1
    additions, attempts = [], []
    for (company, scenario), group in idx.groupby(["company_id", "scenario"]):
        print("EXPAND", company, scenario, flush=True)
        sigs = {signature(pd.read_csv(out / "e2/plans" / f"plan_{pid}.csv")) for pid in group.plan_id}
        args = (cfg, company, scenario, fac, tech, cal, prices, constraints, availability)
        minimum = _solve_company(*args, objective="emissions")
        sols = []
        if minimum is not None:
            sols.append(("minimum_emissions", None, minimum))
            low, high = minimum["cum_emis_tco2"], minimum["cumulative_budget_tco2"]
            for cap in np.linspace(low, high, a.emissions_points):
                bound = min(high, float(cap) + max(1.0, abs(cap)) * 1e-9)
                sols.append(("cost_at_emissions_cap", bound, _solve_company(*args, objective="cost", emis_cap=bound)))
        for objective, cap, result in sols:
            if result is None:
                attempts.append(dict(company_id=company, scenario=scenario, objective=objective, emissions_cap=cap, status="no_verified_solution"))
                continue
            plan = pd.DataFrame(result["plan"] or [dict(facility_id=None, tech_id=None, adopt_year=None, op_year=None)])
            key = signature(plan)
            dup = key in sigs
            attempts.append(dict(company_id=company, scenario=scenario, objective=objective, emissions_cap=cap,
                                 status="duplicate" if dup else "new_schedule", cum_emissions=result["cum_emis_tco2"]))
            if dup:
                continue
            sigs.add(key)
            pid = f"P{next_id:04d}"; next_id += 1
            plan.assign(plan_id=pid, company_id=company, scenario=scenario, ppa_share=result["ppa"],
                        epc=result["epc"], ccfd=result["ccfd"]).to_csv(out / "e2/plans" / f"plan_{pid}.csv", index=False)
            f = result["primal_feasibility"]
            additions.append(dict(plan_id=pid, company_id=company, scenario=scenario,
                npv_cost_bnkrw=result["npv_cost"], risk_proxy=result["risk"], ppa_share=result["ppa"],
                epc=result["epc"], ccfd=result["ccfd"], budget_slack_tco2=result["budget_slack"],
                is_disclosed=False, solve_status=result["solve_status"], comparison_basis="optimized_candidate",
                cum_emis_tco2=result["cum_emis_tco2"], cumulative_budget_tco2=result["cumulative_budget_tco2"],
                budget_mode=result["budget_mode"], primal_feasible=f["valid"], solution_status=f["solution_status"],
                max_scaled_constraint_violation=f["max_scaled_constraint_violation"],
                mip_gap_actual=result.get("mip_gap_actual", float("nan")), mip_lower_bound=result.get("mip_lower_bound", float("nan"))))
    pd.concat([idx, pd.DataFrame(additions)], ignore_index=True).to_csv(out / "e2/plan_index.csv", index=False)
    pd.DataFrame(attempts).to_csv(out / "e2/expansion_attempts.csv", index=False)
    print(f"preserved {len(idx)} schedules, added {len(additions)}")


if __name__ == "__main__":
    main()
