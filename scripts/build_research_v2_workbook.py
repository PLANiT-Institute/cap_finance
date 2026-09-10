"""Bundle the research_v2 registers into one Excel workbook (cycle 7, 2026-09-07).

Reference registers plus an editable, formula-based NCC partial cost ledger.
It is not the control workbook (outputs/.../TCaR_research_control.xlsx) and
does not drive the engine.

Output: outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_research_v2_registers.xlsx
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/research_v2/TCaR_research_v2_registers.xlsx"
SHEETS = {
    "tech_energy_register": "data/research_v2/technology_packages/tech_energy_demand_register.csv",
    "steel_specifications": "data/research_v2/technology_packages/steel_specifications.csv",
    "petchem_specifications": "data/research_v2/technology_packages/petchem_specifications.csv",
    "company_energy_obs": "data/research_v2/evidence/company_energy_observations.csv",
    "company_energy_intensity": "data/research_v2/evidence/company_energy_intensities.csv",
    "scenario_crosswalk": "data/research_v2/gcam_reference/scenario_crosswalk.csv",
    "horizon_tail_audit": "data/research_v2/price_model_audit/horizon_tail_audit.csv",
    "theta_price_exposure": "data/research_v2/price_model_audit/theta_price_exposure.csv",
    "theta_case_comparison": "data/research_v2/technology_packages/theta_case_comparison.csv",
    "primary_observations": "data/research_v2/evidence/primary_process_observations.csv",
}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    readme = pd.DataFrame({"sheet": list(SHEETS), "source_csv": list(SHEETS.values()),
                           "note": ["reference register; automatically_adopted=False everywhere; not an engine input"] * len(SHEETS)})
    import hashlib
    import json
    import subprocess
    sources = dict(SHEETS)
    sources['price_model_coverage'] = 'data/research_v2/price_model_audit/marginal_validation.csv'
    sources['block_price_metrics'] = 'data/research_v2/block_price_paths/annual_multiplier_metrics.csv'
    sources['tail_mc_intervals'] = 'data/research_v2/block_price_paths/displayed_tail_mc_intervals.csv'
    sheets=[]
    for name,rel in sources.items():
        p=ROOT/rel
        df=pd.read_csv(p)
        sheets.append(dict(name=name,source=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                           columns=list(df.columns),rows=json.loads(df.to_json(orient='values', double_precision=15))))
    payload=dict(sheets=sheets,ledger=json.loads((ROOT/'data/research_v2/technology_packages/ledger_exercise.json').read_text()))
    scratch=ROOT/'tmp/tcar_workbook'
    scratch.mkdir(parents=True,exist_ok=True)
    (scratch/'research_v2_register_payload.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    node='/Users/jinsu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
    subprocess.run([node,str(ROOT/'scripts/build_research_v2_registers.mjs')],check=True,cwd=ROOT)


if __name__ == "__main__":
    main()
