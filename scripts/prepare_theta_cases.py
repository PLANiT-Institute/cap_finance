"""Prepare isolated theta-alternative cases (cycle 6, 2026-09-07).

Copies the verified reproduction input set (17 CSV, byte-identical to the v1.0
workbook inputs) into tmp/research_v2_theta/<case>/data, patches only the D3
rows named by the specification set from cycles 2-3, writes a config.yaml with
the research-case conventions (cash_v1, explicit_retention, strict) and a
reduced search (frontier 4, sims 4000) so six cases can run in parallel.
Canonical data/prepared and out/ are not touched.

Usage: .venv/bin/python scripts/prepare_theta_cases.py  -> prints run commands
"""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC_DATA = ROOT / "tmp/bundle_portability_v1/runs/reproduction/data"
BASE_CFG = ROOT / "tmp/bundle_portability_v1/runs/reproduction/expanded/config.yaml"
WORK = ROOT / "tmp/research_v2_theta"

# case -> {tech_id: {field: value}}; sources: steel_specifications.csv / petchem_specifications.csv
CASES = {
    "base_fin": {},
    "steel_vogl_hot": {"steel_h2dri": {"elec_intensity": 1.119}, "steel_hyrex": {"elec_intensity": 1.119}},
    "steel_vogl_cold": {"steel_h2dri": {"elec_intensity": 1.278}, "steel_hyrex": {"elec_intensity": 1.278}},
    "ncc_linde3": {"petchem_ecracker": {"elec_intensity": 3.25}, "petchem_ecracker_hybrid": {"elec_intensity": 1.3}},
    "ncc_layritz": {"petchem_ecracker": {"elec_intensity": 6.99}, "petchem_ecracker_hybrid": {"elec_intensity": 2.8}},
    "h2fuel_102": {"petchem_h2fuel": {"h2_intensity": 102.0}},
}
NOTE = {
    "base_fin": "unchanged v1.0 inputs; reduced search only",
    "steel_vogl_hot": "H2-DRI purchased-H2 electricity = Vogl residual, hot charge (VOGL_H2DRI_PURCHASEDH2_0SCRAP_HOT)",
    "steel_vogl_cold": "same + 0.159 cold-HBI penalty",
    "ncc_linde3": "e-cracker electricity = Linde approach 3 + base (lower bound); hybrid = 40% of that",
    "ncc_layritz": "e-cracker electricity = Layritz 1:1 furnace replacement (upper bound); hybrid 40%",
    "h2fuel_102": "H2 fuel switch quantity tied to 50% of Layritz furnace duty; purchased-gas retention left as-is (structural netback issue NOT fixed here)",
}


def main():
    cfg0 = yaml.safe_load(BASE_CFG.read_text())
    cmds = []
    for case, patch in CASES.items():
        d = WORK / case
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(SRC_DATA, d / "data")
        p = d / "data/D3_tech_options.csv"
        rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
        touched = 0
        for r in rows:
            for k, v in patch.get(r["tech_id"], {}).items():
                r[k] = str(v); touched += 1
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        assert touched == sum(len(v) for v in patch.values()), case
        cfg = dict(cfg0)
        cfg.update(data_dir=str(d / "data"), out_dir=str(d / "run"),
                   simulation={"n_sims": 4000, "n_sims_flex": 500, "convergence_check_n": 1000},
                   milp={**cfg0["milp"], "frontier_points": 4, "solver_time_limit_s": 20},
                   case_note=NOTE[case], theta_patch=patch, case_scope=cfg0["case_scope"] + "; theta alternative, reduced search")
        (d / "config.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
        cmds.append(f".venv/bin/python scripts/run_research_case.py --config {d / 'config.yaml'} > {d / 'run.log'} 2>&1")
    (WORK / "run_all.sh").write_text("\n".join(c + " &" for c in cmds) + "\nwait\n")
    print(f"{len(CASES)} cases prepared under {WORK}; run: sh {WORK / 'run_all.sh'}")


if __name__ == "__main__":
    main()
