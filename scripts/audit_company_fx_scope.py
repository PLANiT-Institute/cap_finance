"""Register disclosed financial-stock FX exposure without inferring procurement flows."""
from pathlib import Path
from fractions import Fraction
import csv,hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/company_fx_scope'
SOURCES={
 'lotte_2024':dict(path='tmp/pdfs/company_process_bridge/lotte_business_2024.pdf',url='https://www.lottechem.com/pdfRead.do?fileId=FILE_250319162135146&voNm=irdataVo',pages=[197,198,199,200,205,206]),
 'mci_2025':dict(path='tmp/pdfs/company_fx_scope/mci_fy2024.pdf',url='https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/release/2025/ms_250623e.pdf',pages=[56,59,60,61]),
 'mci_2026':dict(path='tmp/pdfs/company_fx_scope/mci_fy2025.pdf',url='https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/release/2026/ms_260622e.pdf',pages=[59,60])}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

# Read in visual table order: functional KRW, PKR, USD, CNY, TRY, disclosed total.
BALANCES={
 (2024,'assets','USD'):[1331197574,0,0,7475422,3728998,1342401994],
 (2024,'assets','EUR'):[168139105,0,0,0,2566982,170706087],
 (2024,'assets','MYR'):[676187,0,87876037,0,0,88552224],
 (2023,'assets','USD'):[1606502533,0,0,4700074,12372902,1623575509],
 (2023,'assets','EUR'):[137301796,0,4058012,0,2235814,143595622],
 (2023,'assets','MYR'):[3785283,0,82663448,0,0,86448731],
 (2024,'liabilities','USD'):[1340889082,50807030,0,1624931,0,1393321043],
 (2024,'liabilities','EUR'):[13556859,128076,1308851,0,37912504,52906290],
 (2024,'liabilities','MYR'):[314174,0,148946946,0,0,149261120],
 (2023,'liabilities','USD'):[1729370698,21342497,0,6179746,11232416,1768125357],
 (2023,'liabilities','EUR'):[7565425,104189,36775,0,35980952,43687341],
 (2023,'liabilities','MYR'):[766185,0,101787911,0,0,102554096]}
SCOPES=['KRW','PKR','USD','CNY','TRY','TOTAL']
SENSITIVITY={
 (2024,'USD'):{'KRW':-969151,'PKR':-5080703,'CNY':585050,'TRY':372900,'TOTAL':-5091904},
 (2024,'EUR'):{'KRW':15458225,'PKR':-12808,'USD':-130885,'TRY':-3534552,'TOTAL':11779980},
 (2024,'MYR'):{'KRW':36201,'USD':-6107091,'TOTAL':-6070890},
 (2023,'USD'):{'KRW':-12286817,'PKR':-2134250,'CNY':-147966,'TRY':114049,'TOTAL':-14454984},
 (2023,'EUR'):{'KRW':12973637,'PKR':-10419,'USD':402124,'TRY':-3374514,'TOTAL':9990828},
 (2023,'MYR'):{'KRW':301910,'USD':-1912446,'TOTAL':-1610536}}

def main():
 OUT.mkdir(exist_ok=True)
 obs=[]
 def add(source,company,period,measure,ccy,scope,value,unit,page,raw=None,admission='reference_only_not_procurement_input'):
  obs.append(dict(observation_id=f'FX{len(obs)+1:03}',source_id=source,company=company,period_end=period,measure=measure,instrument_currency=ccy,functional_currency_scope=scope,value=value,unit=unit,pdf_page=page,printed_page=page-(3 if company=='LOTTE' else 1),raw_token=raw if raw is not None else f'{value:,}',source_url=SOURCES[source]['url'],admission=admission))
 for (year,kind,ccy),values in BALANCES.items():
  page=197 if kind=='assets' and year==2024 else 198 if kind=='assets' else 199 if year==2024 else 200
  for scope,v in zip(SCOPES,values):
   cellpage=199 if year==2023 and kind=='liabilities' and ccy=='USD' and scope=='KRW' else page
   add('lotte_2024','LOTTE',f'{year}-12-31',f'foreign_financial_{kind}',ccy,scope,v,'KRW_thousand',cellpage)
 for (year,ccy),values in SENSITIVITY.items():
  for scope,v in values.items():
   add('lotte_2024','LOTTE',f'{year}-12-31','reported_10pct_FX_pretax_profit_effect',ccy,scope,v,'KRW_thousand',206,raw=f'({abs(v):,})' if v<0 else f'{v:,}')
 for src,years,vals in [('mci_2025',[2025,2024],[[-675,-44,-9],[-711,-26,-15]]),('mci_2026',[2026,2025],[[-665,-84,-14],[-675,-44,-9]])]:
  for year,values in zip(years,vals):
   for ccy,v in zip(['USD','EUR','CNY'],values):
    add(src,'MCI',f'{year}-03-31','reported_1pct_JPY_appreciation_pretax_profit_effect',ccy,'disclosed_group_financial_instruments',v,'JPY_million',59,raw=f'({abs(v)})')
 # 2025 comparative table in 2026 report has unambiguous contract/carrying headers.
 for src,year,nominal,asset,liability in [('mci_2025',2024,600,16,None),('mci_2026',2025,837,None,2)]:
  for measure,v in [('cashflow_hedge_contract_amount',nominal),('cashflow_hedge_carrying_asset',asset),('cashflow_hedge_carrying_liability',liability)]:
   add(src,'MCI',f'{year}-03-31',measure,'FX_unspecified','designated_cashflow_hedges_only','' if v is None else v,'JPY_million',60,raw='—' if v is None else str(v))
 for src,year,rate in [('mci_2025',2024,147),('mci_2025',2025,150),('mci_2026',2025,150),('mci_2026',2026,155)]:
  add(src,'MCI',f'{year}-03-31','reported_principal_forward_rate','USD','designated_cashflow_hedges_only',rate,'JPY_per_USD',60)
 save('observations.csv',obs)
 checks=[]
 for (year,kind,ccy),values in BALANCES.items():
  checks.append(dict(check='functional_parts_sum',year=year,instrument_currency=ccy,functional_scope=kind,computed=sum(values[:5]),reported=values[5],difference=sum(values[:5])-values[5],allowed_abs_difference=0))
 for (year,ccy),values in SENSITIVITY.items():
  for scope,value in values.items():
   i=SCOPES.index(scope);derived=Fraction(BALANCES[year,'assets',ccy][i]-BALANCES[year,'liabilities',ccy][i],10)
   # Printed balances and sensitivity are rounded to thousands; retain residuals.
   checks.append(dict(check='net_balance_times_10pct',year=year,instrument_currency=ccy,functional_scope=scope,computed=float(derived),reported=value,difference=float(derived-value),allowed_abs_difference=0.6))
 for r in checks:
  r['status']='reconciled' if abs(r['difference'])<=r['allowed_abs_difference'] else 'held_rounding_not_sufficient'
 assert sum(r['status']!='reconciled' for r in checks)==4
 save('arithmetic_checks.csv',checks)
 diagnostic=[]
 for year in [2023,2024]:
  for ccy in ['USD','EUR','MYR']:
   for scope in ['KRW','TOTAL']:
    i=SCOPES.index(scope);a=BALANCES[year,'assets',ccy][i];b=BALANCES[year,'liabilities',ccy][i]
    diagnostic.append(dict(year=year,instrument_currency=ccy,functional_scope=scope,assets_KRW_million=a/1000,liabilities_KRW_million=b/1000,net_KRW_million=(a-b)/1000,sensitivity10pct_KRW_million=(a-b)/10000,annual_purchase_flow_identified=False,facility_allocation_identified=False))
 save('stock_scope_diagnostic.csv',diagnostic)
 issues=[
 dict(issue_id='MCI_2025_CURRENT_HEADER',source_id='mci_2025',page=60,period='2025-03-31',status='resolved_for_2025_via_2026_comparative_table',raw_first_column=837,raw_second_column='—',raw_third_column=2,explanation='2025 current table puts Carrying amount over first column and Contract amount over Assets/Liabilities; 2026 comparative table labels same 837 as contract and 2 as carrying liability. Source not silently corrected.'),
 dict(issue_id='MCI_2026_CURRENT_HEADER',source_id='mci_2026',page=60,period='2026-03-31',status='held_header_ambiguity',raw_first_column=1983,raw_second_column=66,raw_third_column='—',explanation='Current-year header has same reversal. Store raw positions; do not admit current-year notional or carrying amount from this table alone.'),
 dict(issue_id='LOTTE_SHOCK_DIRECTION',source_id='lotte_2024',page=205,period='2024-12-31',status='signed_check_not_distribution',raw_first_column='',raw_second_column='',raw_third_column='',explanation='Source says FX changes10pct; signed cells match0.1*(assets-liabilities) with four USD residuals exceeding the0.6 KRW thousand nearest-rounding bound. Do not relabel this as a measured standard deviation, percentile, or daily FX quotation convention.')]
 save('source_issues.csv',issues)
 admission=[
 dict(observation_class='financial_balance',usable_for='reporting_date_financial_stock_reference',not_identified='annual_raw_material_purchases;facility_allocation;invoice_terms',engine_input_allowed=False),
 dict(observation_class='disclosed_sensitivity',usable_for='conditional_reported_stress_check',not_identified='shock_probability;volatility;TCaR;long_horizon_flow',engine_input_allowed=False),
 dict(observation_class='designated_cashflow_hedge',usable_for='historical_designated_instrument_reference',not_identified='all_economic_hedges;procurement_hedge_ratio;renewal_terms',engine_input_allowed=False),
 dict(observation_class='principal_forward_rate',usable_for='historical_contract_reference',not_identified='future_available_strike;premium;counterparty_terms;NCC_allocation',engine_input_allowed=False)]
 save('admission_register.csv',admission)
 manifest=dict(scope='Published financial stocks and conditional FX stress; not process cashflow calibration',company_calibration=False,new_MC_draws=0,source_pages_visually_reviewed=12,LOTTE_balance_cells=72,LOTTE_reported_sensitivity_cells=26,MCI_sensitivity_cells=12,MCI_contract_or_carrying_cells_including_dashes=6,MCI_forward_rate_cells=4,arithmetic_checks=len(checks),reconciled_arithmetic=34,held_arithmetic=4,source_issues=issues,
 source_files={k:{**v,'sha256':sha(ROOT/v['path'])} for k,v in SOURCES.items()},outputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.glob('*.csv'))},builder_sha256=sha(Path(__file__)))
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in manifest.items() if k not in ['source_files','source_issues','outputs_sha256']},ensure_ascii=False))

if __name__=='__main__':main()
