"""Check source hashes, unit conversion and the new manuscript's displayed values."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'data/research_v2/tiggeloven_reference'
    manifest=json.loads((out/'manifest.json').read_text())
    for path,sha in manifest['sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
    o=pd.read_csv(out/'source_observations.csv').set_index(['case','item'])
    q=lambda case,item:float(o.loc[(case,item),'value'])
    paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
    section=paper.split('### C.2 ')[1].split('## 참고문헌')[0]
    y=q('electric','ethylene_yield')
    eb=q('conventional','separation_electricity_consumption')
    et=sum(q('electric',i+'_electricity_consumption') for i in ['cracker','compression','separation'])
    values=[1/y,eb/y,et/y,(et-eb)/y,
            (q('electric','TOC_slope')*q('both','reference_capacity')*1000+q('electric','TOC_intercept')*1e6)/1e6,
            q('conventional','cracker_methane_consumption')+q('conventional','separation_saturated_steam_consumption')+eb,
            q('electric','cracker_electricity_consumption')+q('electric','separation_saturated_steam_consumption')+eb,
            et,q('electric','reported_pyrolysis_separation_SEC')]
    for value in values:assert f'{value:.3f}' in section,f'{value:.3f}'
    d=pd.read_csv(out/'derived_quantities.csv').set_index('case')
    np.testing.assert_allclose(d.electricity_MWh_per_t_ethylene,[eb/y,et/y])
    p=json.loads((out/'package.json').read_text())
    assert not p['automatic_FIN_adoption'] and not p['full_corporate_cost_ready']
    assert p['price_year']==2019 and 'annuity_factor' in p['maintenance_formula']
    assert '자동 FIN 채택을 보류한다' in section
    captions=re.findall(r'\*\*그림 (\d+)\.',paper)
    assert captions==[str(i) for i in range(1,len(captions)+1)]
    references=[int(x) for x in re.findall(r'^(\d+)\. ',paper,re.M)]
    assert references==list(range(1,len(references)+1)) and len(references)>=38
    report=dict(source_observations=len(o),new_displayed_values_checked=len(values),
        source_hashes_checked=len(manifest['sha256']),figures=len(captions),references=len(references),
        automatic_FIN_adoption=False,corporate_costs_reestimated=False,
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',
             ROOT/'output/pdf/TCaR_methodology.pdf']})
    version=re.search(r'연구 원고 (v[0-9.]+)',paper).group(1)
    target=ROOT/f'docs/research_cycles/2026-09-07-hourly/tiggeloven_{version.replace(".","")}_verification.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='sha256'}))


if __name__=='__main__':main()
