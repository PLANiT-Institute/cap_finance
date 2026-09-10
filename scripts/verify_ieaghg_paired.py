"""Independent saved-draw, ledger-boundary and manuscript transcription checks."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

from run_ieaghg_paired_reference import profile

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'data/research_v2/ieaghg_paired'
    package=json.loads((ROOT/'data/research_v2/ieaghg_reference/package.json').read_text())
    results=pd.read_csv(out/'conditional_cost_metrics.csv')
    manifest=json.loads((out/'manifest.json').read_text())
    for field in ['input_sha256','artifact_sha256']:
        for name,want in manifest[field].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want,name
    draws=np.load(out/'STEPS_validation_incremental_costs.npz')
    absolute=np.load(out/'STEPS_validation_absolute_costs.npz')
    checks=0
    for name in draws.files:
        a=draws[name];r=results[(results.model=='block_12')&(results.role=='validation')&(results.scenario=='STEPS')&(results.plan_id==name)].iloc[0]
        np.testing.assert_allclose(absolute[name]-absolute['REFERENCE'],a,atol=2e-7,rtol=2e-12)
        # Independent equally weighted worst500 observations, no ES helper.
        vals=[a.mean(),np.median(a),np.quantile(a,.95),np.sort(a)[-500:].mean()]
        np.testing.assert_allclose(vals,[r['mean'],r.p50,r.q95,r.es95],atol=1e-8)
        checks+=4
    years=tuple(range(2027,2051));central=np.linspace(9.,6.,len(years))
    bills=[]
    for case in ['REFERENCE','EOP_L1','EOP_L2']:
        p,cap,renewal,fixed,operating=profile(package,case,years,central,0.,.03,1000.)
        assert not p.grid_mwh.any() and not p.re_mwh.any()
        np.testing.assert_allclose(cap.sum(),package['cases'][case]['initial_capex_source_USD'])
        assert np.count_nonzero(cap)==3 and np.count_nonzero(renewal)==1
        assert renewal[years.index(2044)]==232e6
        assert not p.emissions[:3].any() and not fixed[:3].any()
        assert p.additional_commodity_flows[1].quantity_unit=='annual_source_ore_bundle'
        bills.append(fixed + operating*(package['cases'][case]['ng_GJ']*central+package['cases'][case]['ore_bundle_source_USD']))
    # Contract premiums must be a nonnegative deterministic increment in the
    # central-price account; all new-plant gas must not be hedged by accident.
    base_ng=package['cases']['REFERENCE']['ng_GJ']
    for case in ['EOP_L1','EOP_L2']:
        p,_,_,fixed,op=profile(package,case,years,central,1.,.03,1000.)
        np.testing.assert_allclose(p.additional_commodity_flows[0].quantity,op*base_ng)
        new_bill=fixed+op*(base_ng*central+package['cases'][case]['ore_bundle_source_USD'])
        original=bills[['REFERENCE','EOP_L1','EOP_L2'].index(case)]
        np.testing.assert_allclose(new_bill-original,op*.03*(package['cases'][case]['ng_GJ']-base_ng)*central,atol=1e-6)
    paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
    printed=[[v.strip() for v in l.strip('|').split('|')] for l in paper.splitlines() if l.startswith('|')]
    table_cells=0
    for h in [0.,.5,1.]:
        r=results[(results.model=='block_12')&(results.scenario=='STEPS')&(results.case=='EOP_L1')&(results.incremental_gas_contract_fraction==h)]
        a=r[r.role=='selection'].iloc[0];b=r[r.role=='validation'].iloc[0]
        want=[f'추가 가스 {h:.0%}',*[f'{x:.3f}' for x in [a['mean'],b['mean'],b.analytic_mean,b.es95]]]
        assert want in printed;table_cells+=4
    selection=json.loads((out/'independent_selection.json').read_text())
    assert sum(not r['same_frontier'] for r in selection)==12
    assert sum(not r['same_analytic_mean_frontier'] for r in selection)==0
    assert not package['source']['visual_review_complete']
    assert not package['boundary']['CO2_transport_storage_included']
    assert not manifest['company_calibration'] and manifest['independent_draw_pools']==4
    assert '75개 수치' in paper and '12개의 독립 실증시험은 아니다' in paper
    report=dict(saved_draw_metrics_checked=checks,new_printed_cells_checked=table_cells,
        source_cases_checked=3,incremental_contract_boundary_checks=2,
        mean_ES_frontier_disagreements=12,analytic_mean_sample_ES_disagreements=0,
        source_visual_review_complete=False,company_calibration=False,
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf',
            out/'manifest.json',ROOT/'data/research_v2/ieaghg_reference/manifest.json',Path(__file__)]})
    import re
    version=re.search(r'연구 원고 (v[0-9.]+)',paper).group(1)
    target=ROOT/f'docs/research_cycles/2026-09-07-hourly/ieaghg_paired_{version.replace(".","")}_verification.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='sha256'}))


if __name__=='__main__':main()
