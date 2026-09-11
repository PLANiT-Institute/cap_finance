"""Financial adapter contracts, executed separately from the original test suite."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import numpy as np
import pytest

PLATFORM=Path(__file__).resolve().parents[1]
REPO=PLATFORM.parent
sys.path.insert(0,str(PLATFORM/'api'))
import simulate

@pytest.mark.parametrize('model',['joint','cash','timing'])
def test_web_matches_original_fin_with_fractional_tail(model):
    controls=dict(simulate.DEFAULTS[model],paths=103,alpha=.9327)
    payload=dict(model=model,controls=controls)
    actual=simulate.solve(payload)
    program='''
import sys,json
sys.path.insert(0,'scripts')
import ncc_joint_control as joint
import ncc_cash_workbook_control as cash
import timing_workbook_control as timing
p=json.loads(sys.argv[1]);m=p['model'];c=p['controls']
if m=='joint':
 r,_=joint.evaluate(c);v={'electric':r['metrics']}
elif m=='cash':
 r=cash.evaluate(c);v={'electric':r['metrics']}
else:
 r=timing.evaluate(c);v=r['metrics']
print(json.dumps(v))
'''
    expected=json.loads(subprocess.check_output([sys.executable,'-c',program,json.dumps(payload)],cwd=REPO))
    for summary in actual['summaries']:
        if not summary['eligible']:
            assert summary['id'] not in expected
            assert 'mean' not in summary
            continue
        for key in ['mean','p50','q_alpha','tcar','es_alpha']:
            assert summary[key]==expected[summary['id']][key]
        assert sum(row['count'] for row in actual['distributions'][summary['id']])==103
        assert summary['tcar']==summary['q_alpha']-summary['p50']
    if model!='timing':
        assert sum(r['incremental'] for r in actual['chart'])==pytest.approx(actual['summaries'][0]['analytic_mean'])

@pytest.mark.parametrize('constraint',['annual_linear','residual'])
def test_no_feasible_timing_does_not_invent_zero_cost(constraint):
    c=dict(simulate.DEFAULTS['timing'],paths=103)
    c.update(constraint='annual_linear') if constraint=='annual_linear' else c.update(residual=.1)
    r=simulate.solve(dict(model='timing',controls=c))
    assert not any(s['eligible'] for s in r['summaries'])
    assert not r['audit']['mc_executed']
    assert r['audit']['checks']==0
    assert not r['distributions']
    assert all('mean' not in s for s in r['summaries'])

def test_zero_production_is_valid_zero_cost_not_missing():
    r=simulate.solve(dict(model='joint',controls=dict(simulate.DEFAULTS['joint'],paths=103,production_t=0)))
    assert all(r['summaries'][0][k]==0 for k in ['mean','p50','q_alpha','tcar','es_alpha'])

@pytest.mark.parametrize('key,value',[('paths',10001),('paths',0),('paths',2.5),('paths',True),('discount',None),('discount',''),('alpha',1),('alpha',float('nan')),('seed',-1),('seed',2**32),('scenario','FAKE'),('constraint','no_budget')])
def test_invalid_inputs_fail_before_compute(key,value):
    c=dict(simulate.DEFAULTS['timing']);c[key]=value
    with pytest.raises(ValueError): simulate.validate_request(dict(model='timing',controls=c))

def test_unknown_and_missing_controls_are_not_silently_ignored():
    c=dict(simulate.DEFAULTS['cash']);c['extra']=1
    with pytest.raises(ValueError):simulate.validate_request(dict(model='cash',controls=c))
    del c['extra'];del c['power']
    with pytest.raises(ValueError):simulate.validate_request(dict(model='cash',controls=c))

def test_reproducibility_and_seed_change():
    p=dict(model='cash',controls=dict(simulate.DEFAULTS['cash'],paths=103))
    a=simulate.solve(p);b=simulate.solve(p)
    assert a['request_id']==b['request_id'] and a['summaries']==b['summaries']
    p['controls']['seed']+=1;c=simulate.solve(p)
    assert a['request_id']!=c['request_id'] and a['summaries']!=c['summaries']

def test_publication_has_no_facility_identifiers_or_private_inputs():
    frames=json.loads((PLATFORM/'public/data/frames.json').read_text())
    assert len(frames)==14
    for frame in frames:
        assert 'facility_id' not in frame['columns']
        assert hashlib.sha256((PLATFORM/'public/data'/frame['file']).read_bytes()).hexdigest()==frame['sha256']
    for p in (PLATFORM/'public').rglob('*'):
        if p.is_file():
            assert p.suffix not in ['.xlsx','.npz','.pdf','.py']
            if p.suffix in ['.csv','.json']:
                body=p.read_text()
                assert '/Users/' not in body
                assert 'POSCO_POH_BF2' not in body
    assert not (PLATFORM/'engine/data/research_v2').joinpath('company_boundary').exists()

def test_served_default_results_are_from_current_engine():
    for model in simulate.DEFAULTS:
        saved=json.loads((PLATFORM/f'public/data/default-{model}.json').read_text())
        live=simulate.solve(dict(model=model,controls=simulate.DEFAULTS[model]))
        assert saved['engine_version']==live['engine_version']
        assert saved['request_id']==live['request_id']
        assert saved['summaries']==live['summaries']

def test_historical_corporate_snapshot_preserves_risk_definitions():
    r=json.loads((PLATFORM/'src/lib/research.json').read_text())
    assert r['metadata']['candidate_count']==len(r['candidates'])==450
    assert len({x['base_plan_id'] for x in r['candidates']})==45
    assert all(x['tcar']==pytest.approx(x['p90']-x['p50']) for x in r['candidates'])
    assert all(not x['decision_eligible'] for x in r['candidates'] if x['sampled_statewise_dominated'])


# ---- L7 (2026-09-11): publication consistency contracts -------------------------
def _research():
    return json.loads((PLATFORM/'src/lib/research.json').read_text())

def _versions(r):
    out={'canonical':r}
    for k in ('v22','v21','v2','v1'):
        if k in r: out[k]=r[k]
    return out

def test_no_sampled_dominated_candidate_is_flagged_on_any_frontier():
    """B3: a candidate excluded by sampled statewise dominance can never carry a frontier flag
    (this was violated by LOTTE NZ15 P0001.c06 in the 2026-09-05 snapshot)."""
    for name,v in _versions(_research()).items():
        flags=[k for k in v['candidates'][0] if k.startswith('on_') and k.endswith('_frontier')]
        bad=[(c['plan_id'],f) for c in v['candidates'] if c.get('sampled_statewise_dominated') for f in flags if c.get(f)]
        assert not bad, f'{name}: dominated-but-frontier {bad[:5]}'

def test_public_csv_matches_canonical_snapshot():
    r=_research()
    import csv
    rows=list(csv.DictReader((PLATFORM/'public/data/company-candidates.csv').open()))
    assert len(rows)==len(r['candidates'])==r['metadata']['candidate_count']
    assert {x['plan_id'] for x in rows}=={c['plan_id'] for c in r['candidates']}

def test_catalog_hint_never_exceeds_api_cap():
    cat=json.loads((PLATFORM/'public/data/catalog.json').read_text())
    for model,spec in cat['models'].items():
        for field in spec['fields']:
            if field[0]=='paths':
                import re
                nums=[int(n.replace(',','')) for n in re.findall(r'\d[\d,]*',field[-1])]
                assert nums and max(n for n in nums if n>=2 and n<=100000)<=10000, f'{model}: paths hint {field[-1]} exceeds API cap 10,000'

def test_each_version_declares_its_convention():
    for name,v in _versions(_research()).items():
        m=v['metadata']
        for key in ('hedge_basis','frontier_axes','carbon_included','scenario_status','result_sha256'):
            assert key in m, f'{name} metadata lacks {key}'
