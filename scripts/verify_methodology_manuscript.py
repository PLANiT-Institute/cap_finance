"""Reconcile the revised methodology manuscript's case tables with audit outputs.

This is a numeric/source-snapshot check, not a scientific-validity certificate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/methodology/TCaR_METHOD_KO.md"
AUDIT = ROOT / "docs/research_cycles/2026-09-05/gap_engine_v2"
COMPANIES = {"POSCO": "POSCO", "Nippon Steel": "NSC",
             "Mitsui Chemicals": "MCI", "LOTTE Chemical": "LOTTE"}


def verify() -> dict:
    text = PAPER.read_text()
    risk_path, choice_path = AUDIT / "risk_measure_comparison.csv", AUDIT / "criterion_choices.csv"
    gap_path = ROOT / "out/e5/gap.csv"
    budget_path = ROOT / "docs/research_cycles/2026-09-05/budget_definition_comparison.csv"
    risk, choices, gaps = (pd.read_csv(p) for p in (risk_path, choice_path, gap_path))
    budgets = pd.read_csv(budget_path)
    selected = choices.query("scenario == 'NZ15' and support == 'none' and criterion == 'p50'")
    tables = [[v.strip() for v in line.strip().strip("|").split("|")]
              for line in text.splitlines() if line.startswith("|")]
    checked = []
    for label, cid in COMPANIES.items():
        printed = [r for r in tables if r[0] == label and len(r) == 6]
        assert len(printed) == 1, f"Missing or duplicated risk row: {label}"
        pick = selected.query("company_id == @cid")
        assert len(pick) == 1
        pid = pick.iloc[0].plan_id
        row = risk.query("company_id == @cid and scenario == 'NZ15' and support == 'none' and plan_id == @pid")
        assert len(row) == 1
        row = row.iloc[0]
        assert row.n_draws == 10000 and row.alpha == 0.9
        for i, key in enumerate(["p50", "mean", "q_alpha", "tcar", "es_alpha"], 1):
            expected = f"{row[key]:,.2f}"
            assert printed[0][i] == expected, (label, key, printed[0][i], expected)
            checked.append({"company_id": cid, "plan_id": pid, "metric": key, "value": expected})
    for label in ["Nippon Steel", "Mitsui Chemicals"]:
        cid = COMPANIES[label]
        printed = [r for r in tables if r[0] == f"{label} · NZ15 · none"]
        assert len(printed) == 1
        row = gaps.query("company_id == @cid and scenario == 'NZ15' and support == 'none'")
        assert len(row) == 1
        row = row.iloc[0]
        assert row.gap_method == "attainable_discrete_candidates"
        for i, key in enumerate(["gap_cost_bnkrw", "gap_risk_bnkrw", "cost_witness_plan_id", "risk_witness_plan_id"], 1):
            expected = f"{row[key]:,.2f}" if i <= 2 else row[key]
            assert printed[0][i] == expected, (label, key, printed[0][i], expected)
            checked.append({"company_id": cid, "metric": key, "value": expected})
    for label, scenario in [("Nippon Steel", "B20"), ("Mitsui Chemicals", "NZ15")]:
        cid = COMPANIES[label]
        for caption, rule in [("현행 소프트", "current_soft"), ("연간 엄격", "annual_hard"),
                              ("기간 누적 엄격", "horizon_cumulative_hard")]:
            printed = [r for r in tables if r[:2] == [f"{label} · {scenario}", caption]]
            assert len(printed) == 1
            row = budgets.query("company_id == @cid and scenario == @scenario and budget_rule == @rule")
            assert len(row) == 1
            row = row.iloc[0]
            for i, key in enumerate(["candidate_count", "cost_gap", "risk_gap"], 2):
                value = row[key]
                expected = str(int(value)) if i == 2 else ("NA" if pd.isna(value) else f"{value:,.2f}")
                assert printed[0][i] == expected, (label, rule, key, printed[0][i], expected)
                checked.append({"company_id": cid, "scenario": scenario, "budget_rule": rule,
                                "metric": key, "value": expected})
    current_path = ROOT / 'tmp/research_case_expanded/run/e5/metrics_company.csv'
    current = pd.read_csv(current_path)
    for row in current.itertuples():
        printed = [r for r in tables if len(r) == 7 and r[:2] == [row.company_id, row.scenario]]
        assert len(printed) == 1
        assert printed[0][2] == row.selected_plan_id
        checked.append(dict(company_id=row.company_id, scenario=row.scenario,
                            metric='selected_plan_id', value=row.selected_plan_id))
        for i, key in enumerate(['p50_bnkrw', 'mean_bnkrw', 'tcar_bnkrw', 'es_alpha_bnkrw'], 3):
            expected = f'{getattr(row, key):,.2f}'
            assert printed[0][i] == expected
            checked.append(dict(company_id=row.company_id, scenario=row.scenario, metric=key, value=expected))
    edit_path=ROOT/'docs/research_cycles/2026-09-05/excel_control/gas_retention_result_comparison.csv'
    edited=pd.read_csv(edit_path)
    for row in edited[edited.company_id.isin(['LOTTE','MCI'])].itertuples():
        printed=[r for r in tables if len(r)==5 and r[:2]==[row.company_id,row.scenario]]
        assert len(printed)==1
        for i,key in enumerate(['delta_mean_bnkrw','delta_tcar_bnkrw','delta_es_alpha_bnkrw'],2):
            value=getattr(row,key);value=0. if abs(value)<1e-8 else value
            expected=f'{value:,.2f}';assert printed[0][i]==expected
            checked.append(dict(company_id=row.company_id,scenario=row.scenario,metric=key,value=expected))
    analytic_path=ROOT/'docs/research_cycles/2026-09-05/robustness_verified/selected_analytic_means.csv'
    for row in pd.read_csv(analytic_path).itertuples():
        printed=[r for r in tables if len(r)==5 and r[0]==f'{row.company_id} · {row.scenario}']
        assert len(printed)==1
        for i,key in enumerate(['analytic_mean','monte_carlo_mean','bootstrap_low_95','bootstrap_high_95'],1):
            expected=f'{getattr(row,key):,.2f}';assert printed[0][i]==expected
            checked.append(dict(company_id=row.company_id,scenario=row.scenario,metric=key,value=expected))
    # Basic equation numbering guards missing/duplicated definitions during editing.
    assert re.findall(r"\\tag\{(\d+)\}", text) == [str(i) for i in range(1, 13)]
    assert text.count(r"\[") == text.count(r"\]") == 12
    paths = [PAPER, risk_path, choice_path, gap_path, budget_path, current_path, edit_path, analytic_path]
    return {"scope": "Printed metric/witness/budget cells and twelve equation labels; not external validation",
            "checked_cells": checked,
            "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


if __name__ == "__main__":
    result = verify()
    dest = ROOT / "docs/research_cycles/2026-09-05/manuscript_validation.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"Verified {len(result['checked_cells'])} metric/witness cells and 12 equation labels.")
