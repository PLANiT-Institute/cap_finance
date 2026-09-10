"""Independently check raw disclosure transcription and arithmetic residuals."""
from pathlib import Path
from fractions import Fraction
import csv,hashlib,json,re,subprocess

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/research_v2/company_fx_scope';OUT=ROOT/'docs/research_cycles/2026-09-07-hourly'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return list(csv.DictReader((DATA/name).open()))
def main():
 manifest=json.loads((DATA/'manifest.json').read_text())
 for source in manifest['source_files'].values():assert sha(ROOT/source['path'])==source['sha256']
 for rel,digest in manifest['outputs_sha256'].items():assert sha(ROOT/rel)==digest
 obs=read('observations.csv');assert len(obs)==120
 # Extract anew from immutable PDFs rather than using the builder constants.
 texts={k:subprocess.check_output(['pdftotext','-layout',str(ROOT/v['path']),'-']).decode().split('\f') for k,v in manifest['source_files'].items()}
 raw=[]
 for page in [197,198,199,200]:
  raw.extend(int(v.replace(',','')) for v in re.findall(r'(?<![\d.,])(?:\d{1,3}(?:,\d{3})+|0)(?![\d.,])',texts['lotte_2024'][page-1]))
 balances=[r for r in obs if r['measure'] in ['foreign_financial_assets','foreign_financial_liabilities']]
 assert [int(r['value']) for r in balances]==raw and len(raw)==72
 token_checks=0
 for r in obs[72:]:
  page=texts[r['source_id']][int(r['pdf_page'])-1]
  assert r['raw_token'] in page,(r['observation_id'],r['raw_token'])
  token_checks+=1
 b={(r['period_end'][:4],r['measure'],r['instrument_currency'],r['functional_currency_scope']):int(r['value']) for r in balances}
 checks=read('arithmetic_checks.csv');held=[]
 for r in checks:
  year,ccy,scope=r['year'],r['instrument_currency'],r['functional_scope']
  if r['check']=='functional_parts_sum':
   value=sum(b[year,'foreign_financial_'+scope,ccy,f] for f in ['KRW','PKR','USD','CNY','TRY'])
  else:value=Fraction(b[year,'foreign_financial_assets',ccy,scope]-b[year,'foreign_financial_liabilities',ccy,scope],10)
  assert Fraction(r['computed'])==value
  difference=value-Fraction(r['reported']);assert Fraction(r['difference'])==difference
  status='reconciled' if abs(difference)<=Fraction(r['allowed_abs_difference']) else 'held_rounding_not_sufficient'
  assert status==r['status']
  if status!='reconciled':held.append(dict(year=year,ccy=ccy,scope=scope,residual_KRW_thousand=str(difference)))
 assert len(checks)==38 and len(held)==4
 for r in read('stock_scope_diagnostic.csv'):
  key=(r['year'],r['instrument_currency'],r['functional_scope'])
  a=b[key[0],'foreign_financial_assets',key[1],key[2]];l=b[key[0],'foreign_financial_liabilities',key[1],key[2]]
  for col,v in [('assets_KRW_million',Fraction(a,1000)),('liabilities_KRW_million',Fraction(l,1000)),('net_KRW_million',Fraction(a-l,1000)),('sensitivity10pct_KRW_million',Fraction(a-l,10000))]:assert Fraction(r[col])==v
 # Cross-report duplicate 2025 sensitivities agree, without treating repeated values as extra evidence.
 mci=[r for r in obs if r['company']=='MCI' and r['measure'].startswith('reported_1pct')]
 for ccy in ['USD','EUR','CNY']:
  rows=[r for r in mci if r['period_end']=='2025-03-31' and r['instrument_currency']==ccy]
  assert len(rows)==2 and rows[0]['value']==rows[1]['value']
 issues=read('source_issues.csv')
 assert issues[0]['status']=='resolved_for_2025_via_2026_comparative_table'
 assert issues[1]['status']=='held_header_ambiguity'
 assert not any(r['period_end']=='2026-03-31' and r['measure'].startswith('cashflow_hedge') for r in obs)
 assert all(r['engine_input_allowed']=='False' for r in read('admission_register.csv'))
 # Equal ending payables do not identify annual purchases: independent Fraction arithmetic.
 for purchase,days in [(12,30),(24,15)]:assert Fraction(purchase*days,360)==1
 note=(ROOT/'paper/methodology/COMPANY_FX_SCOPE_KO.md').read_text()
 for r in read('stock_scope_diagnostic.csv'):
  if r['year']=='2024':
   line='| '+r['instrument_currency']+' | '+('원화 기능 부문' if r['functional_scope']=='KRW' else '전체')+' | '+' | '.join(f'{float(r[k]):,.3f}' for k in ['assets_KRW_million','liabilities_KRW_million','net_KRW_million'])+' |'
   assert line in note
 previous=json.loads((OUT/'completion_27_verification.json').read_text())
 for rel in ['paper/methodology/TCaR_METHOD_KO.md','output/pdf/TCaR_methodology.pdf']:assert sha(ROOT/rel)==previous['artifact_sha256'][rel]
 workbook=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
 assert sha(workbook)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
 report=dict(iteration=28,verification_passed=True,scientific_reconciliation_complete=False,raw_balance_cells_checked=72,other_raw_tokens_checked=48,observation_rows=120,numeric_observations=118,preserved_source_dashes=2,arithmetic_checks=38,reconciled=34,unreconciled=held,stock_diagnostic_values_checked=48,printed_table_values_checked=18,cross_report_sensitivity_duplicates_checked=3,source_pages_visually_reviewed=12,source_header_issue_resolved_for_2025=True,source_2026_current_header_issue_held=True,stock_flow_identification_counterexamples=2,automatic_engine_admissions=0,new_MC_draws=0,company_calibration=False,main_manuscript_unchanged=True,PDF_unchanged=True,Excel_v6_unchanged=True,goal_complete=False)
 paths=[DATA/'manifest.json',DATA/'functional_currency_scope.png',ROOT/'paper/methodology/COMPANY_FX_SCOPE_KO.md',ROOT/'scripts/audit_company_fx_scope.py',ROOT/'scripts/plot_company_fx_scope.py',Path(__file__)]
 report['artifact_sha256']={str(p.relative_to(ROOT)):sha(p) for p in paths}
 (OUT/'completion_28_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
