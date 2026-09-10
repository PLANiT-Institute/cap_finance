from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'data/research_v2/ncc_delivery_integration';m=json.loads((out/'manifest.json').read_text())
 for group in ['input_sha256','code_sha256','artifact_sha256']:
  for p,h in m[group].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 r=json.loads((out/'replays.json').read_text());assert len(r)==3
 assert sum(x['FIN_cost_values_checked'] for x in r)==10620
 assert sum(x['annual_rows'] for x in r)==144 and sum(x['risk_metrics_unchanged'] for x in r)==15
 assert all(x['maximum_cost_change']==0 for x in r)
 for x in r:
  d=x['delivery_contract']
  assert not d['corporate_calibration'] and not d['abatement_feasibility_verified']
  assert d['cases']['conventional']['delivery_total_t']==d['cases']['electric']['delivery_total_t']
  assert max(v for c in d['cases'].values() for v in c['quantity_link_errors'].values())<1e-7
  for p,h in d['implementation_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
 for term in ['기존 저장 Excel 입력 3건','비용값 10,620개','연간 원장 144행','위험 요약 15개','새 검사 8개']:assert term in paper,term
 version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
 result=dict(new_execution_claims_checked=5,FIN_cost_values_checked=10620,annual_rows_unchanged=144,risk_metrics_unchanged=15,maximum_cost_change=0,new_corporate_results=False,new_workbook_written=False,
 sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
 (ROOT/f'docs/research_cycles/2026-09-07-hourly/ncc_delivery_{version}_verification.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='sha256'})
if __name__=='__main__':main()
