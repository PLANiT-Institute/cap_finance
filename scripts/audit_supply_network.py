"""Source attribution and deterministic accounting checks; no corporate simulation."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.supply_network import Transfer,consolidate_cash
OUT=ROOT/'data/research_v2/supply_continuity'

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 access=json.loads((ROOT/'tmp/pdfs/supply_continuity/access.json').read_text())
 assert hashlib.sha256((ROOT/access['file']).read_bytes()).hexdigest()==access['sha256']
 page=(ROOT/'tmp/pdfs/supply_continuity/mci_q3_fy2024_qa.txt').read_text().split('\f')[3]
 assert all(x in page for x in ['8.5 billion','2 billion','4 billion','2.5','procurement costs','fixed costs'])
 rows=[]
 for item,value,meaning in [('total_impact',8.5,'Issuer retrospective rough impact; not audited stand-alone cash expenditure'),('sales_volume_effect',2.,'Profit effect of lower sales volume, not gross revenue'),('terms_of_trade_effect',4.,'Includes procurement cost increases, not pure procurement premium'),('fixed_other_effect',2.5,'Includes repair/maintenance and steam losses; not a fixed-cost-only item')]:
  rows.append(dict(company='MCI',period='FY2024_Q1_Q3_April_December',item=item,value=value,unit='billion_JPY',meaning=meaning,pdf_page=4,question='Q10/A10',source_url=access['url'],source_file=access['file'],source_sha256=access['sha256'],visually_reviewed=True,automatic_FIN_adoption=False))
 pd.DataFrame(rows).to_csv(OUT/'mci_impact_observations.csv',index=False)
 assert sum(x['value'] for x in rows[1:])==rows[0]['value']
 t=Transfer('AB','A','B',[3,3],[3,3]);a=np.array([[1.,2.],[3.,4.]]);b=2*a;freight=np.full((2,2),.5)
 records=[]
 for markup in [0.,2.,1e20,-3.]:
  r=consolidate_cash({'A':a,'B':b},[t],{'AB':np.full((2,2),markup)},{'AB':freight},shape=(2,2))
  np.testing.assert_array_equal(r['consolidated_cash'],[[3.5,6.5],[9.5,12.5]])
  for i in range(2):
   for j in range(2):records.append(dict(internal_settlement=markup,draw=i,period=j,group_external_cash=r['consolidated_cash'][i,j],status='synthetic_accounting_test_not_company_or_MC'))
 pd.DataFrame(records).to_csv(OUT/'internal_settlement_invariance.csv',index=False)
 source_search=[dict(url='https://kind.krx.co.kr/external/2023/05/15/002729/20230515006150/11013.htm',result='LOTTE Holdings Q12023 filing; search suggests ethylene-basis production tables, but target CY2024 scope/values not verified. Not adopted as CY2024 output.'),dict(url=access['url'],result='Source title dates briefing February4,2025; filename250219 is not substituted for event date. Reviewed PDF4 Q10/Q11. Q4 forecasts not treated as retrospective values.')]
 (OUT/'source_decisions.json').write_text(json.dumps(source_search,ensure_ascii=False,indent=2)+'\n')
 files=list(OUT.glob('*.csv'))+[OUT/'source_decisions.json']
 manifest=dict(native_observations=4,source_PDFs=1,source_pages_visually_reviewed=1,component_sum_check=True,synthetic_internal_settlement_cells=16,corporate_MC=False,adaptive_policy_implemented=False,source_sha256={access['file']:access['sha256']},artifact_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'src/cap/supply_network.py',ROOT/'tests/test_supply_network.py']})
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print({k:v for k,v in manifest.items() if not k.endswith('sha256')})
if __name__=='__main__':main()
