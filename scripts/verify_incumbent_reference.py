"""Saved-risk and counterfactual-date checks independent of the FIN evaluator."""
from pathlib import Path
import json,hashlib,re
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'data/research_v2/incumbent_ncc';m=json.loads((out/'manifest.json').read_text())
 for group in ['input_sha256','artifact_sha256']:
  for p,h in m[group].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 data=pd.read_csv(out/'conditional_metrics.csv');annual=pd.read_csv(out/'annual_cash.csv');saved=np.load(out/'incremental_draws.npz')
 for r in data.itertuples():
  x=np.sort(saved[f'life{r.remaining_years}_scale{r.replacement_cost_scale}']);median,q=np.quantile(x,[.5,.95])
  es=x[-250:].mean()
  np.testing.assert_allclose([r.mean,r.p50,r.q_alpha,r.tcar,r.es_alpha],[x.mean(),median,q,q-median,es],rtol=1e-12,atol=1e-8)
  a=annual[(annual.remaining_years==r.remaining_years)&(annual.replacement_cost_scale==r.replacement_cost_scale)]
  b=a[a['case']=='continue_existing'];e=a[a['case']=='replace_2030']
  assert list(b[b.incumbent_renewal_EUR>0].year)==[2027+r.remaining_years]
  assert b.construction_EUR.sum()==0 and e.incumbent_renewal_EUR.sum()==0
  assert (b.output_t==920000).all() and (e.output_t==920000).all()
  # The net cash identity excludes the separately reported noncash writeoff.
  np.testing.assert_allclose(a.net_fixed_cash_EUR,a.construction_EUR+a.incumbent_renewal_EUR+a.new_renewal_EUR+a.maintenance_EUR+a.closure_net_cash_EUR-a.terminal_receipt_EUR,rtol=1e-12,atol=1e-7)
 assert data.mean_shift.min()<0<data.mean_shift.max()
 paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
 n=0
 for r in data.query('replacement_cost_scale==1').itertuples():
  for v in [r.mean,r.es_alpha,r.tcar,r.mean_shift]:assert f'| {v:.3f}' in paper;n+=1
 assert n==12
 for s in ['비용값 90,000개','연간 원장 432행','관련 검사 19개 중 13개']:assert s in paper
 version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
 report=dict(new_printed_numeric_values=12,saved_risk_metrics_checked=45,annual_cash_identity_rows=432,renewal_dates_checked=9,mean_shift_has_both_signs=True,independent_draw_pools=1,new_execution_claims_checked=3,corporate_calibration=False,frontier_selection=False,
 sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
 (ROOT/f'docs/research_cycles/2026-09-07-hourly/incumbent_ncc_{version}_verification.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='sha256'})
if __name__=='__main__':main()
