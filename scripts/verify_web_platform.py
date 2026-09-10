"""Verify published HTTP artifacts and original FIN parity without browser UI QA."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'platform/api'))
from simulate import solve,DEFAULTS,VERSION

def verify(url):
    url=url.rstrip('/')
    checks=[]
    def fetch(path,payload=None):
        req=Request(url+path,data=None if payload is None else json.dumps(payload).encode(),
            headers={'Content-Type':'application/json'} if payload is not None else {})
        with urlopen(req,timeout=65) as response:
            return response.read(),dict(response.headers)
    body,headers=fetch('/')
    assert b'TCaR' in body and b'/_next/' in body
    assert any(k.lower()=='x-robots-tag' and 'noindex' in v for k,v in headers.items())
    checks.append('production_html_and_noindex')
    catalog=json.loads(fetch('/api/simulate')[0])
    assert catalog['engine_version']==VERSION
    assert set(catalog['models'])==set(DEFAULTS)
    checks.append('production_engine_release')
    frames=json.loads(fetch('/data/frames.json')[0])
    assert len(frames)==14
    for frame in frames:
        downloaded=fetch('/data/'+frame['file'])[0]
        assert hashlib.sha256(downloaded).hexdigest()==frame['sha256'],frame['id']
    checks.append('14_downloads_sha256')
    for path in ['/engine/config.yaml','/data/D1a_facility_static.csv','/tmp/research_case_expanded/config.yaml']:
        try:fetch(path)
        except HTTPError as error:assert error.code==404
        else:raise AssertionError('Private path exposed: '+path)
    checks.append('private_paths_404')
    runtime={}
    for model in DEFAULTS:
        payload=dict(model=model,controls=dict(DEFAULTS[model],paths=103,alpha=.9327))
        live=json.loads(fetch('/api/simulate',payload)[0]);expected=solve(payload)
        assert live['request_id']==expected['request_id']
        for key in ['numpy','pandas','pyyaml']:
            assert live['runtime'][key]==expected['runtime'][key]
        for a,b in zip(live['summaries'],expected['summaries']):
            assert a['id']==b['id'] and a['eligible']==b['eligible']
            if a['eligible']:
                keys=['mean','p50','q_alpha','tcar','es_alpha']
                np.testing.assert_allclose([a[k] for k in keys],[b[k] for k in keys],rtol=1e-11,atol=1e-7)
        runtime=live['runtime'];checks.append(model+'_original_fin_parity')
    no_candidate=dict(model='timing',controls=dict(DEFAULTS['timing'],constraint='annual_linear',paths=103))
    live=json.loads(fetch('/api/simulate',no_candidate)[0])
    assert not live['audit']['mc_executed'] and all(not x['eligible'] and 'mean' not in x for x in live['summaries'])
    checks.append('infeasible_no_cost_or_MC')
    invalid=dict(model='timing',controls=dict(DEFAULTS['timing'],paths=10001))
    try:fetch('/api/simulate',invalid)
    except HTTPError as e:
        assert e.code==400
        assert 'error' in json.loads(e.read())
    else:raise AssertionError('Invalid request accepted')
    checks.append('invalid_request_400')
    full=dict(model='joint',controls=DEFAULTS['joint'])
    live=json.loads(fetch('/api/simulate',full)[0])
    np.testing.assert_allclose(live['summaries'][0]['mean'],solve(full)['summaries'][0]['mean'],rtol=1e-11,atol=1e-7)
    checks.append('10000_path_production_execution')
    return dict(url=url,checks=checks,count=len(checks),runtime=runtime,engine_version=VERSION,browser_ui_tested=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='https://tcar-transition-finance.vercel.app');args=parser.parse_args()
    result=verify(args.url)
    out=ROOT/'tmp/web-platform-verification.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
