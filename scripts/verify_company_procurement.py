"""Independent reconciliation and selected manuscript claims from source register."""
from pathlib import Path
import csv
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'data/research_v2/company_procurement'
 manifest=json.loads((out/'manifest.json').read_text())
 for group in ['source_sha256','implementation_sha256','artifact_sha256']:
  for p,h in manifest[group].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 rows=list(csv.DictReader((out/'source_observations.csv').open()));assert len(rows)==30
 d={r['id']:r for r in rows};assert len(d)==30
 assert all(r['FIN_adopted']=='False' for r in rows)
 for year,delta in [(2023,0),(2024,5),(2025,4)]:
  v=lambda item:float(d[f'lotte_{year}_{item}']['value'])
  gap=sum(v(s) for s in ['nonrenewable_fuel','nonrenewable_electricity','nonrenewable_steam'])-v('nonrenewable_total')
  assert gap==delta
  assert v('nonrenewable_total')+v('renewable_REC_reported_energy')==v('energy_total')
  # Four independently rounded numbers imply an absolute gap no larger than2TJ.
  saved=next(r for r in json.loads((out/'reconciliation.json').read_text()) if r['year']==year)
  assert saved['nearest_integer_rounding_can_reconcile']==(abs(gap)<=2)
 assert d['lotte_2025_PPA_solar']['entity']=='LOTTE Fine Chemical'
 assert d['lotte_2025_PPA_wind']['entity']=='LOTTE Fine Chemical'
 assert d['lotte_2025_REC_solar']['entity']=='LOTTE Chemical parent'
 assert 'market-based' in d['mci_2024_scope2_total']['method']
 assert d['mci_2024_scope2_total']['period']=='2024-04-01/2025-03-31'
 paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
 for s in ['Scope 2는486kt-CO2','비재생 전력21,822TJ·스팀16,334TJ와 자가발전12,787TJ','합은113,075TJ이나 비재생 총계는113,070TJ','차이는5TJ이고2025년에는4TJ','REC 약6,384MWh','약10,161MWh·풍력 약9,301MWh','평균과 ES는 그 할인액만큼 이동하지만 TCaR는 불변']:
  assert s in paper,s
 report=dict(source_numeric_observations=30,new_selected_manuscript_values=11,
   annual_reconciliations=3,nearest_integer_rounding_failures=2,
   procurement_mapping_entries=4,actual_hedge_parameters_identified=False,
   new_MC=False,core_engine_changed=False,
   sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
 version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
 (ROOT/f'docs/research_cycles/2026-09-07-hourly/company_procurement_{version}_verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print({k:v for k,v in report.items() if k!='sha256'})

if __name__=='__main__':main()
