"""Reproduce isolated input repair and strict disclosure mapping assessment.

Canonical inputs and historical E1-E5 results are not replaced. Observed company
Scope 2 totals do not make the allocated cracker estimates facility measurements.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C
from cap.e2_milp import COMPANY_REGION, _disclosed_fixed, _prep_company
from cap.schemas import load_input


def main():
    destination = ROOT / "tmp/petchem_boundary_v2/prepared"
    audit = ROOT / "docs/research_cycles/2026-09-05/petchem_data"
    audit.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts/prepare_raw.py"),
         "--out-dir", str(destination)], cwd=ROOT, capture_output=True, text=True,
        check=True)
    (audit / "isolated_preparation.log").write_text(run.stdout + run.stderr)
    changes, metadata = [], []
    for file in sorted((ROOT / "data/prepared").glob("D*.csv")):
        before, after = pd.read_csv(file), pd.read_csv(destination / file.name)
        assert len(before) == len(after), file.name
        assert set(before) <= set(after), file.name
        new_columns = sorted(set(after) - set(before))
        if new_columns:
            assert file.name == "D7_disclosed_plan.csv" and new_columns == ["mapping_status"]
            assert after.mapping_status.eq("unreviewed").all()
            metadata.append(dict(file=file.name, added_column="mapping_status",
                                 rows=len(after), default="unreviewed"))
        for column in before:
            equal = before[column].eq(after[column]) | (before[column].isna() & after[column].isna())
            for i in before.index[~equal]:
                assert file.name == "D1b_facility_panel.csv"
                assert column == "emissions_s2" and before.loc[i, "facility_id"].startswith("LOTTE_")
                assert before.loc[i, column] == 0 and after.loc[i, column] > 0
                changes.append(dict(facility_id=before.loc[i, "facility_id"],
                                    year=int(before.loc[i, "year"]), field=column,
                                    old=before.loc[i, column], new=after.loc[i, column]))
    assert len(changes) == 6
    pd.DataFrame(changes).to_csv(audit / "isolated_preparation_changed_cells.csv", index=False)
    observations = pd.read_csv(destination / "company_observation_reconciliation.csv")
    observations.to_csv(audit / "company_observation_reconciliation.csv", index=False)
    cfg = C.load()
    facilities, technologies, _ = _prep_company(cfg, destination)
    disclosures = load_input(destination, "D7_disclosed_plan")
    availability = pd.read_csv(C.out_dir(cfg, "e1") / "tech_availability.csv")
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    rows = []
    for company in sorted(facilities.company_id.unique()):
        cf = facilities[facilities.company_id == company]
        for scenario in cfg.scenarios:
            av = availability[(availability.scenario == scenario) &
                              (availability.region == COMPANY_REGION[company])]
            fixed = _disclosed_fixed(disclosures, cf,
                technologies[technologies.sector == cf.sector.iloc[0]], years,
                av.set_index("tech_id").avail_year_scenario)
            eligible = fixed["valid"] and bool(fixed["x"] or fixed["ppa"] or fixed["epc"] or fixed["ccfd"])
            rows.append(dict(company_id=company, scenario=scenario,
                             mapping_valid=fixed["valid"], comparator_eligible=eligible,
                             fixed_technology_count=len(fixed["x"]),
                             rejected_commitments=len(fixed["dropped"]),
                             reasons=" | ".join(fixed["dropped"]),
                             comparison_basis=fixed["comparison_basis"]))
    assert len(rows) == 8 and not any(r["comparator_eligible"] for r in rows)
    pd.DataFrame(rows).to_csv(audit / "current_disclosed_mapping_gate.csv", index=False)
    files = [ROOT / "scripts/prepare_raw.py", ROOT / "src/cap/input_boundaries.py",
             ROOT / "src/cap/e2_milp.py", Path(__file__).resolve(),
             destination / "D1b_facility_panel.csv", destination / "D7_disclosed_plan.csv"]
    manifest = dict(changed_input_cells=len(changes),
                    changed_field="LOTTE2022–2024 estimated emissions_s2",
                    company_observation_rows=len(observations),
                    added_review_metadata=metadata,
                    all_other_existing_prepared_cells_identical=True,
                    canonical_prepared_inputs_replaced=False,
                    scope2_allocation_is_verified_cracker_measurement=False,
                    current_mapping_gate_company_scenarios=len(rows),
                    eligible_disclosed_comparators=sum(r["comparator_eligible"] for r in rows),
                    source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in files})
    (audit / "isolated_preparation_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
