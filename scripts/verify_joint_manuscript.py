"""Independently reconcile new joint-price and disclosed tables in the paper."""
from pathlib import Path
import json
import hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def verify():
    path=ROOT/'paper/methodology/TCaR_METHOD_KO.md';text=path.read_text()
    tables=[[v.strip() for v in l.strip().strip('|').split('|')] for l in text.splitlines() if l.startswith('|')]
    tail_file=ROOT/'data/research_v2/joint_tail_precision/conditional_bootstrap_intervals.csv'
    bound_file=ROOT/'data/research_v2/disclosed_feasibility/case_summary.csv'
    result_file=ROOT/'data/research_v2/joint_workbook_control/roundtrip_verification.json'
    checked=[]
    labels={'iid_gaussian':'독립 정규','empirical_block_1':'블록 1개월','empirical_block_6':'블록 6개월','empirical_block_12':'블록 12개월','empirical_block_24':'블록 24개월'}
    for r in pd.read_csv(tail_file).query('horizon_years == 24').itertuples():
        printed=[x for x in tables if len(x)==5 and x[0]==labels[r.model]]
        assert len(printed)==1
        for i,key in enumerate(('tcar95','tcar95_low','tcar95_high','es95'),1):
            expected=f'{getattr(r,key)/1000:.3f}';assert printed[0][i]==expected
            checked.append(dict(table='tail',row=r.model,metric=key,printed=expected))
    bounds=pd.read_csv(bound_file)
    assert len(bounds)==16 and bounds.linear_path_accepted.all() and bounds.conditional_gross_path_infeasible.all()
    assert not bounds.cost_evaluated.any() and not bounds.corporate_scope_harmonized.any()
    for cid in ('POSCO','NSC','LOTTE','MCI'):
        early=bounds.query('company_id == @cid and scenario == "NZ15" and earliest_start_year == 2024').iloc[0]
        late=bounds.query('company_id == @cid and scenario == "NZ15" and earliest_start_year == 2027').iloc[0]
        printed=[x for x in tables if len(x)==5 and x[0]==cid and x[2].endswith('%')]
        assert len(printed)==1
        expected=[str(early.covered_facilities),f'{early.terminal_floor_percent_of_proxy_baseline:.2f}%',str(early.first_bound_violation_year),str(late.first_bound_violation_year)]
        assert printed[0][1:]==expected
        checked.extend(dict(table='disclosed',row=cid,column=i+1,printed=v) for i,v in enumerate(expected))
    report=json.loads(result_file.read_text());assert len(report['valid_executions'])==3 and len(report['rejected'])==3
    assert all(r['excel_error_cells']==0 for r in report['valid_executions'])
    assert all(r['max_metric_error']<2.19e-11 for r in report['valid_executions'])
    for heading in ('5.11','5.12','6.9','6.10','7.4'):
        assert text.count('### '+heading+' ')==1
    assert '구조적으로 **LNG 한 요인의 가중합**' in text
    assert 'HHV로' not in text
    files=[path,tail_file,bound_file,result_file]
    return dict(checked_cells=checked,disclosed_cases=16,workbook_executions=3,
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},external_validity_claimed=False)


if __name__=='__main__':
    r=verify();out=ROOT/'docs/research_cycles/2026-09-07-hourly/joint_manuscript_v24_verification.json'
    out.write_text(json.dumps(r,indent=2)+'\n');print(f'Verified {len(r["checked_cells"])} new printed cells,16disclosed conditions,3workbook executions')
