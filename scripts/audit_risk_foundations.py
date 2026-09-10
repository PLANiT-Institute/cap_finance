"""Revalue saved FIN candidates to audit risk definitions without overwriting E5.

Usage: .venv/bin/python scripts/audit_risk_foundations.py
Output: docs/research_cycles/2026-09-05/ (override with --out).
This audits the saved search set, not global optimisation or empirical validity.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
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
from cap.e3_prices import load_shocks
from cap.e4_revalue import _central_px
from cap.e5_metrics import _carbon_npv, _empty_plan, _frontier
from cap.plancost import auction_share, build_profile, simulate_cost, support_params
from cap.risk_metrics import finite_candidate_gap, loss_summary
from cap.schemas import load_input


def _legacy_interpolated_gap(frontier, point):
    """Frozen pre-2026-09-05 diagnostic; never used to recommend a candidate."""
    f = frontier.sort_values("tcar")
    cost = (max(0.0, float(point.p50 - np.interp(min(point.tcar, f.tcar.max()), f.tcar, f.p50)))
            if len(f) and point.tcar >= f.tcar.min() else np.nan)
    f = f.sort_values("p50")
    risk = (max(0.0, float(point.tcar - np.interp(min(point.p50, f.p50.max()), f.p50, f.tcar)))
            if len(f) and point.p50 >= f.p50.min() else np.nan)
    return cost, risk


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "docs/research_cycles/2026-09-05")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    cfg = C.load(capex_shock_scaling="legacy_linear", allow_legacy_price_paths=True, capital_accounting="legacy_mixed", energy_balance_mode="legacy_retrofit_all", carbon_accounting_mode="legacy_auction_discount", transition_loss_basis="incremental_ex_carbon", plan_selection_criterion="p50")
    ddir, e2 = C.data_dir(cfg), C.out_dir(cfg, "e2")
    saved_path = C.out_dir(cfg, "e5") / "frontier_points.csv"
    saved = pd.read_csv(saved_path)
    keys = ["company_id", "scenario", "support"]
    fac, tech, cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    price_path = C.out_dir(cfg, "e1") / "price_paths_central.csv"
    prices = pd.read_csv(price_path)
    shocks = load_shocks(cfg)
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    discount = (1 + cfg.discount_rate) ** -(years - years[0])
    auction = auction_share(years, cfg)
    rows, gaps, choices = [], [], []
    files = {ROOT / "config.yaml", saved_path, price_path,
             C.out_dir(cfg, "e3") / "price_sims.parquet"}
    files.update(ddir.glob("*.csv"))
    files.update((ROOT / "src/cap").glob("*.py"))
    files.add(Path(__file__))

    for (company, scenario, support), g in saved.groupby(keys, sort=True):
        px = _central_px(prices, COMPANY_REGION[company], scenario, years, cfg, cal)
        sp = support_params(d5, support, years)
        base = build_profile(_empty_plan(company), fac, tech, px, years, cfg)
        base_draws = simulate_cost(base, px, shocks, sp, cfg)
        base_carbon = _carbon_npv(base, px, discount, auction)
        group_rows = []
        for r in g.itertuples():
            plan_path = e2 / "plans" / f"plan_{r.base_plan_id}.csv"
            files.add(plan_path)
            prof = build_profile(pd.read_csv(plan_path), fac, tech, px, years, cfg)
            prof = replace(prof, ppa=float(r.ppa_share), epc=int(r.epc), ccfd=int(r.ccfd))
            dcarbon = _carbon_npv(prof, px, discount, auction) - base_carbon
            losses = simulate_cost(prof, px, shocks, sp, cfg) - base_draws - dcarbon
            summary = loss_summary(losses)
            row = dict(company_id=company, scenario=scenario, support=support,
                       plan_id=r.plan_id, base_plan_id=r.base_plan_id,
                       is_disclosed=bool(r.is_disclosed), budget_ok=bool(r.budget_ok),
                       ppa_share=float(r.ppa_share), epc=int(r.epc),
                       saved_p50=float(r.p50), saved_tcar=float(r.tcar), **summary)
            row["p50_reproduction_error"] = summary["p50"] - r.p50
            row["tcar_reproduction_error"] = summary["tcar"] - r.tcar
            group_rows.append(row)
        cur = pd.DataFrame(group_rows)
        eligible = cur[~cur.is_disclosed & cur.budget_ok]
        # Alternative frontier within precisely the SAME saved candidate universe.
        es_fr = _frontier(eligible.assign(p50=eligible["mean"], tcar=eligible.es_alpha))
        median_fr = _frontier(eligible)
        cur["on_mean_es_frontier"] = cur.plan_id.isin(es_fr.plan_id)
        cur["on_median_tcar_frontier"] = cur.plan_id.isin(median_fr.plan_id)
        rows.extend(cur.to_dict("records"))
        if len(eligible):
            for criterion in ["p50", "mean", "q_alpha", "tcar", "es_alpha"]:
                chosen = eligible.sort_values([criterion, "plan_id"]).iloc[0]
                choices.append(dict(company_id=company, scenario=scenario, support=support,
                                    criterion=criterion, plan_id=chosen.plan_id,
                                    ppa_share=chosen.ppa_share, epc=chosen.epc,
                                    p50=chosen.p50, mean=chosen["mean"],
                                    tcar=chosen.tcar, es_alpha=chosen.es_alpha))
        for d in cur[cur.is_disclosed].itertuples():
            old = _legacy_interpolated_gap(median_fr, d)
            new = finite_candidate_gap(eligible.p50, eligible.tcar, d.p50, d.tcar)
            cset = eligible[eligible.tcar <= d.tcar + 1e-9]
            rset = eligible[eligible.p50 <= d.p50 + 1e-9]
            gaps.append(dict(company_id=company, scenario=scenario, support=support,
                             plan_id=d.plan_id, interpolated_cost_gap=old[0],
                             attainable_cost_gap=new[0], interpolated_risk_gap=old[1],
                             attainable_risk_gap=new[1],
                             cost_witness=cset.sort_values(["p50", "plan_id"]).plan_id.iloc[0]
                             if len(cset) and new[0] > 0 else "",
                             risk_witness=rset.sort_values(["tcar", "plan_id"]).plan_id.iloc[0]
                             if len(rset) and new[1] > 0 else ""))
        print(f"{company} {scenario} {support}: {len(cur)} candidates", flush=True)

    all_rows = pd.DataFrame(rows)
    all_rows.to_csv(a.out / "risk_measure_comparison.csv", index=False)
    pd.DataFrame(gaps).to_csv(a.out / "attainable_gap_comparison.csv", index=False)
    pd.DataFrame(choices).to_csv(a.out / "criterion_choices.csv", index=False)
    inv = pd.read_csv(ROOT / "docs/parameter_inventory.csv")
    evidence = {
        "parameter_rows": len(inv),
        "tier_counts": inv.evidence_tier.value_counts().to_dict(),
        "rows_with_both_bounds": int((inv.value_low.notna() & inv.value_high.notna()).sum()),
        "t5_without_both_bounds": int((inv.evidence_tier.astype(str).str.startswith("T5") &
            ~(inv.value_low.notna() & inv.value_high.notna())).sum()),
    }
    manifest = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
                    scope="Saved FIN candidates only; conditional on configured scenario/model",
                    units="billion KRW (existing engine convention; FX audit pending)",
                    quantile_method="numpy linear; ES empirical inverse-CDF integral",
                    n_candidates=len(all_rows),
                    max_abs_p50_error=float(all_rows.p50_reproduction_error.abs().max()),
                    max_abs_tcar_error=float(all_rows.tcar_reproduction_error.abs().max()),
                    evidence_inventory=evidence,
                    source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(files)})
    (a.out / "risk_audit_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Refuse to silently discuss different runs as if they were the saved baseline.
    if max(manifest["max_abs_p50_error"], manifest["max_abs_tcar_error"]) > 1e-6:
        raise SystemExit("Saved results do not reproduce: inspect reproduction_error columns")
    print(json.dumps({k: v for k, v in manifest.items() if k != "source_sha256"}, indent=2))


if __name__ == "__main__":
    main()
