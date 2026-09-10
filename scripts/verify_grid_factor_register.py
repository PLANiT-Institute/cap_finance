"""Independent source-register and manuscript checks, without selecting inputs."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'data/research_v2/grid_factors'
    m=json.loads((out/'manifest.json').read_text())
    for group in ['source_sha256','implementation_sha256','artifact_sha256']:
        for p,h in m[group].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    registry=json.loads((out/'factor_registry.json').read_text())
    ids={r['identifier']:r for r in registry}
    assert len(ids)==27
    selected=json.loads((out/'normalized_reference_factors.json').read_text())
    assert len(selected)==24
    for r in selected:
        source=ids[r['identifier']]
        unit=source['unit'];multiplier=.001 if unit.startswith('kg') and unit.endswith('/MWh') else 1.
        np.testing.assert_allclose(r['value'],source['value']*multiplier,rtol=0,atol=1e-15)
        assert r['context']['gas']==source['gas']
        assert not r['corporate_calibration'] and not r['future_scenario']
        assert source['status']=='verified_primary'
    decisions=json.loads((out/'source_decisions.json').read_text())
    assert len(decisions['rejected_for_selection'])==3
    data=pd.read_csv(out/'source_observations.csv').set_index('identifier')
    assert len(data)==38
    assert data.loc['KOR_KEA_republished_2021_2023_generation_CO2e','value']==.3896
    assert data.loc['KOR_GIR2025_2021_2023_generation_CO2e','value']==.3986
    assert data.loc['JPN_ELCS_FY2024_superseded_CO2','value']==.416
    assert data.loc['JPN_ELCS_FY2024_verified_primary_CO2','value']==.422
    # The FEPC displayed emissions/intensity pair fails even after allowing
    # half a last-displayed digit of rounding in all three values.
    ratio_low=(3.14-.005)/(7430+.5)*1000
    ratio_high=(3.14+.005)/(7430-.5)*1000
    assert ratio_low>.416+.0005
    bracket_low=(3.09-.005)/(7430+.5)*1000
    bracket_high=(3.09+.005)/(7430-.5)*1000
    assert bracket_high<.423-.0005
    paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
    expected_rows=[('GIR 2024 승인·2020–2022 평균',.4517,.4541),
                   ('GIR 2025 승인·2023 단년',.4149,.4173),
                   ('GIR 2025 승인·2021–2023 평균',.4307,.4330)]
    for label,co2,co2e in expected_rows:assert f'| {label} | {co2:.4f} | {co2e:.4f} |' in paper
    assert '| ELCS 2026 확정 공표·FY2024 | 0.422 | 해당 표 미제시 |' in paper
    for v in ['0.3896','0.3986','잠정 공표의 0.416','확정 공표의 0.422','각각 0.416·0.423tCO2/MWh']:
        assert v in paper
    assert '선택 원문 수치38개' in paper and '신규 검사25개와 기존 가격 단위 검사20개' in paper
    report=dict(new_selected_numeric_values=13,source_observations=38,normalized_values_checked=24,
                selection_holds=3,FEPC_rounding_intervals_disjoint=True,
                FEPC_displayed_ratio_interval=[ratio_low,ratio_high],
                FEPC_bracketed_ratio_interval=[bracket_low,bracket_high],
                new_execution_claims_checked=2,corporate_calibration=False,
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
    version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
    (ROOT/f'docs/research_cycles/2026-09-07-hourly/grid_factors_{version}_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if k!='sha256'})


if __name__=='__main__':main()
