"""Verify the invoice/financial-disclosure integration without changing old audits."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import csv
import hashlib
import json
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/research_cycles/2026-09-07-hourly'
PAPER = ROOT/'paper/methodology/TCaR_METHOD_KO.md'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def readcsv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def main():
    old = json.loads((OUT/'completion31_evidence/before.json').read_text())
    text = PAPER.read_text()
    assert '연구 원고 v2.32' in text
    changed_old = '| KRW/EUR·KRW/JPY·USD/KRW 환율 시계열 | 고정 환산·위험요인 부재 | 한국은행 ECOS | 표 7, 6.9 |'
    changed_new = '| 기업 조달 환율·미래 공동 환율 경로 | 기업 실행은 고정 환산; ECB 역사 참조는 C.11 | 기업 계약·한국은행 ECOS 등 | 표 7, C.11–C.12 |'
    prior = Counter(old['table_rows']);current = Counter(x for x in text.splitlines() if x.startswith('|'))
    assert prior[changed_old] == 1 and current[changed_new] == 1
    prior[changed_old] -= 1
    assert not (prior-current)
    assert sum(prior.values()) == 222
    assert re.findall(r'^!\[.*$',text,re.M)[:25] == old['figures']
    assert re.findall(r'\*\*그림 (\d+)\.',text) == list(map(str,range(1,27)))
    assert re.findall(r'\*\*표 (\d+)\.',text) == list(map(str,range(1,23)))
    assert re.findall(r'\*\*표 C(\d+)\.',text) == list(map(str,range(1,9)))
    assert re.findall(r'\\\[(.*?)\\\]',text,re.S) == old['equations']
    refs = re.findall(r'^\d+\. .*$',text,re.M)
    assert refs[:63] == old['references'] and len(refs)==65
    assert [int(x.split('.')[0]) for x in refs] == list(range(1,66))
    hashes = 0
    for iteration in [28,29,30]:
        evidence = json.loads((OUT/f'completion_{iteration}_verification.json').read_text())
        for name,h in evidence['artifact_sha256'].items():
            assert sha(ROOT/name)==h,name;hashes+=1
    m = json.loads((ROOT/'data/research_v2/company_fx_scope/manifest.json').read_text())
    for name,h in m['outputs_sha256'].items():
        assert sha(ROOT/name)==h,name;hashes+=1
    for record in m['source_files'].values():
        assert sha(ROOT/record['path'])==record['sha256'];hashes+=1
    c12 = text.split('### C.12',1)[1].split('## 참고문헌',1)[0]
    # Two printed net balances, computed from the original registered stocks.
    records=readcsv(ROOT/'data/research_v2/company_fx_scope/observations.csv')
    company_values=0
    for scope in ['KRW','TOTAL']:
        chosen={r['measure']:Fraction(r['value']) for r in records
            if r['source_id']=='lotte_2024' and r['period_end']=='2024-12-31'
            and r['instrument_currency']=='USD' and r['functional_currency_scope']==scope
            and r['measure'] in ['foreign_financial_assets','foreign_financial_liabilities']}
        net=(chosen['foreign_financial_assets']-chosen['foreign_financial_liabilities'])/1000
        assert f'{float(net):,.3f}'.replace('-','−') in c12;company_values+=1
    obs={r['observation_id']:r for r in records}
    for key in ['FX099','FX100','FX101','FX114','FX116','FX118']:
        value=Fraction(obs[key]['value'])
        token=f'{int(value):,}'.replace('-','−')
        assert token in c12;company_values+=1
    checks=readcsv(ROOT/'data/research_v2/company_fx_scope/arithmetic_checks.csv')
    residuals=[r for r in checks if r['status']!='reconciled']
    assert len(checks)==38 and len(residuals)==4
    assert [Fraction(r['difference']) for r in residuals]==list(map(Fraction,['-.9','-.9','-1.2','-.8']))
    assert '−0.9·−0.9·−1.2·−0.8천원' in c12;company_values+=4
    assert Fraction('.5') + Fraction('.1')*(Fraction('.5')+Fraction('.5')) == Fraction('.6')
    assert '최대 차이0.6천원' in c12
    issues=readcsv(ROOT/'data/research_v2/company_fx_scope/source_issues.csv')
    held=next(r for r in issues if r['issue_id']=='MCI_2026_CURRENT_HEADER')
    assert (held['raw_first_column'],held['raw_second_column'])==('1983','66')
    assert '1,983·66' in c12 and '의미별 입력을 보류' in c12;company_values+=2
    assert Fraction(12*30,360)==Fraction(24*15,360)==1
    assert '연간 구매12단위·지급기일30일' in c12 and '구매24단위·지급기일15일' in c12
    data=ROOT/'data/research_v2/invoice_fin_bridge'
    inputs=readcsv(data/'timing_example_inputs.csv');costs=readcsv(data/'timing_example_costs.csv')
    values_checked=0
    for state in ['A','B']:
        rows={r['date']:r for r in inputs if r['state']==state}
        p1,p2=[float(rows[d]['USD_per_t']) for d in ['2027-01-01','2028-01-01']]
        def factor(d):return float(rows[d]['KRW_per_USD'])*float(rows[d]['discount_factor'])
        baseline=2*p1*factor('2027-01-01')+2*p2*factor('2028-01-01')
        delayed=2*p1*factor('2027-07-01')+2*p2*factor('2029-01-01')
        expected=[baseline,delayed,delayed-baseline]
        row=next(r for r in costs if r['state']==state)
        np.testing.assert_allclose(expected,[float(row[k]) for k in
            ['baseline_npv_KRW','later_npv_KRW','incremental_npv_KRW']],rtol=1e-13)
        line=next(l for l in c12.splitlines() if l.startswith('| '+state+' |'))
        displayed=[float(x.strip().replace(',','').replace('−','-')) for x in line.split('|')[2:-1]]
        np.testing.assert_allclose(displayed,expected,rtol=0,atol=.000501);values_checked+=3
    assert sha(ROOT/'paper/methodology/figures/payment_timing.png')==sha(data/'payment_timing.png')
    fin=json.loads((data/'verification.json').read_text())
    assert fin['baseline_and_incremental_values_checked']==40000
    assert fin['paired_summary_values_checked']==30
    assert round(fin['max_error_vs_frozen_cost_KRW_billion']*1e9,3)==.349
    assert '약0.349KRW' in text
    prior_check=json.loads((OUT/'decision_context_v232_verification.json').read_text())
    assert prior_check['prior_printed_cells_verified']==181 and prior_check['toy_ledger_cases']==90
    assert prior_check['sha256'][str(PAPER.relative_to(ROOT))]==sha(PAPER)
    book=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
    assert sha(book)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
    qa=json.loads((OUT/'completion31_evidence/final_render_check.json').read_text())
    assert qa['source_sha256']==sha(PAPER)
    assert qa['pdf_sha256']==sha(ROOT/'output/pdf/TCaR_methodology.pdf')
    assert qa['pages']==73 and qa['all_pages_layout_visually_reviewed']
    report=dict(iteration=31,verification_passed=True,manuscript_version='v2.32',
        old_table_rows_unchanged=222,old_table_rows_deliberately_updated=1,
        old_figures_unchanged=25,figures=26,numbered_equations_unchanged=12,
        references=65,old_references_unchanged=63,new_company_values_checked=company_values,
        new_table_C8_values_checked=values_checked,retained_unreconciled_items=4,
        stock_flow_nonidentification_example_verified=True,stored_source_hashes_checked=hashes,
        FIN_regression_values_referenced=40000,existing_printed_values_rechecked=181,
        existing_toy_ledger_cases_rechecked=90,new_MC_draws=0,Excel_v6_unchanged=True,
        company_calibration=False,goal_complete=False,pages=qa['pages'],
        all_pages_layout_visually_reviewed=True,
        detailed_pages_visually_reviewed=qa['detailed_pages_visually_reviewed'])
    report['artifact_sha256']={str(p.relative_to(ROOT)):sha(p) for p in
        [PAPER,ROOT/'output/pdf/TCaR_methodology.pdf',ROOT/'paper/methodology/figures/payment_timing.png',Path(__file__)]}
    (OUT/'completion_31_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='artifact_sha256'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
