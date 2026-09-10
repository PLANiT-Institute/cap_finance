"""Independent saved-path reconstruction using source arithmetic and calendar dates."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'data/research_v2/ncc_timing_frontier';m=json.loads((out/'manifest.json').read_text())
 for group in ['input_sha256','artifact_sha256']:
  for p,h in m[group].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=pd.read_csv(ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv');v={(r.case,r.item):r.value for r in source.itertuples()}
 yy=np.arange(2027,2051);feed=920000/.303;disc=1.05**-np.arange(24)
 assert v['conventional','ethylene_yield']==v['electric','ethylene_yield']==.303
 plant=v['electric','TOC_slope']*115000+v['electric','TOC_intercept']*1e6
 assert plant==994490000
 old_boiler=72.1*(.492-(.841-.431))*115/.303*1000
 old_o=.04*plant*(.05/(1-1.05**-30))+.04*old_boiler*(.05/(1-1.05**-25))
 new_o=.02*plant*(.05/(1-1.05**-20))
 old_fixed=np.full(24,old_o);old_fixed[yy==2035]+=plant+old_boiler
 old_grid=np.full(24,feed*.083);old_netgas=np.full(24,-feed*(2.349-1.868-.082/.92))
 cash=pd.read_csv(out/'annual_cash.csv');assert len(cash)==96
 reconstructed={}
 for date in [2030,2035,2040,2045]:
  active=yy>=date;construction=np.where((yy>=date-3)&(yy<date),plant/3,0.)
  renewal=np.where(yy==date+20,plant,0.);oldrenewal=np.where((yy==2035)&(yy<date),plant+old_boiler,0.)
  fixed=np.where(active,new_o,old_o)+construction+renewal+oldrenewal
  grid=feed*np.where(active,1.942,.083);netgas=np.where(active,-feed*2.349,old_netgas)
  r=cash[cash.candidate==f'replace_{date}'];assert list(r.year)==list(yy)
  for col,value in [('construction_EUR',construction),('new_renewal_EUR',renewal),('incumbent_renewal_EUR',oldrenewal),('fixed_cash_EUR',fixed),('grid_mwh',grid),('net_methane_MWh',netgas)]:np.testing.assert_allclose(r[col],value,rtol=1e-12,atol=1e-7)
  reconstructed[f'replace_{date}']=(fixed,grid,netgas)
 emissions=pd.read_csv(out/'annual_emissions.csv');assert len(emissions)==384
 q=pd.read_csv(out/'qualification.csv');assert len(q)==16
 for r in q.itertuples():
  grid=r.grid_initial*(2050-yy)/23;active=yy>=r.commission_year;res=r.residual_per_t_naphtha
  expected=feed*(np.where(active,0.,.397)+np.where(active,1.942,.083)*grid+res)
  base=feed*(.397+.083*grid+res)
  a=emissions[(emissions.condition==r.condition)&(emissions.candidate==r.candidate)]
  np.testing.assert_allclose(a.total_emissions,expected,rtol=1e-12,atol=1e-7)
  assert r.cumulative_feasible==bool(expected.sum()<=.75*base.sum()+1e-7)
  assert r.terminal_feasible==bool(expected[-1]<=1e-7)
  assert not r.annual_feasible
  assert r.eligible_for_cumulative_terminal_menu==(r.cumulative_feasible and r.terminal_feasible)
 paths=np.load(out/'annual_prices.npz');draws=np.load(out/'cost_draws.npz');metrics=pd.read_csv(out/'risk_metrics.csv');checks=0;maxerror=0.
 for seed in m['seeds']:
  pe=paths[f'{seed}_power'];pg=paths[f'{seed}_methane'];pn=paths[f'{seed}_naphtha']
  base=((old_fixed+old_grid*pe+old_netgas*pg+feed*pn)*disc).sum(axis=1)/1e6
  np.testing.assert_allclose(base,draws[f'{seed}_baseline'],rtol=1e-12,atol=1e-7);checks+=len(base)
  for name in ['replace_2030','replace_2035','replace_2040']:
   fixed,grid,gas=reconstructed[name];total=((fixed+grid*pe+gas*pg+feed*pn)*disc).sum(axis=1)/1e6
   delta=total-base;stored=draws[f'{seed}_{name}'];np.testing.assert_allclose(delta,stored,rtol=1e-12,atol=1e-7);checks+=len(total);maxerror=max(maxerror,float(np.max(abs(delta-stored))))
   row=metrics[(metrics.seed==seed)&(metrics.candidate==name)].iloc[0]
   np.testing.assert_allclose([row['mean'],row.es_alpha,row.tcar],[stored.mean(),np.sort(stored)[-250:].mean(),np.quantile(stored,.95)-np.median(stored)],rtol=1e-12,atol=1e-7)
   # Cancellation of common feedstock before aggregation, path by path.
   no_feed_delta=((fixed-old_fixed+(grid-old_grid)*pe+(gas-old_netgas)*pg)*disc).sum(axis=1)/1e6
   np.testing.assert_allclose(delta,no_feed_delta,rtol=1e-12,atol=1e-7)
 curves=json.loads((ROOT/'data/research_v2/iea_2025_scenarios/curves.json').read_text())
 def central_ratio(commodity,region=None):
  c=next(c for c in curves if c['scenario']=='STEPS' and c['commodity']==commodity and (region is None or c['region']==region))
  return np.interp(yy,c['years'],c['values'])/c['values'][0]
 gr=central_ratio('natural_gas','Japan');cp=100*(.5+.5*gr);cg=40*gr
 for name in ['replace_2030','replace_2035','replace_2040']:
  fixed,grid,gas=reconstructed[name]
  expected=float(((fixed-old_fixed+(grid-old_grid)*cp+(gas-old_netgas)*cg)*disc).sum()/1e6)
  np.testing.assert_allclose(metrics[metrics.candidate==name].analytic_mean,expected,rtol=1e-12,atol=1e-7)
 f=pd.read_csv(out/'frontier_membership.csv')
 for row in f.itertuples():
  selected=q[(q.condition==row.condition)&q.eligible_for_cumulative_terminal_menu].candidate
  rr=metrics[(metrics.seed==row.seed)&metrics.candidate.isin(selected)];target=rr[rr.candidate==row.candidate].iloc[0]
  dominated=((rr[row.mean_axis]<=target[row.mean_axis])&(rr.es_alpha<=target.es_alpha)&((rr[row.mean_axis]<target[row.mean_axis])|(rr.es_alpha<target.es_alpha))).any()
  assert row.non_dominated==(not bool(dominated))
 assert set(f[f.non_dominated].candidate)=={'replace_2040'}
 precision=pd.read_csv(out/'bootstrap_precision.csv');membership=pd.read_csv(out/'paired_bootstrap_membership.csv')
 for seed in m['seeds']:
  names=['replace_2030','replace_2035','replace_2040'];rng=np.random.default_rng(seed+100)
  boot_es=[];boot_tcar=[];keep_counts=np.zeros(3,dtype=int)
  analytic=metrics[metrics.seed==seed].set_index('candidate').loc[names,'analytic_mean'].to_numpy()
  for b in range(500):
   ix=rng.integers(0,5000,5000);a=np.array([draws[f'{seed}_{name}'][ix] for name in names])
   es=np.sort(a,axis=1)[:,-250:].mean(axis=1);qs=np.quantile(a,[.5,.95],axis=1)
   boot_es.append(es);boot_tcar.append(qs[1]-qs[0])
   for j in range(3):
    keep_counts[j]+=not np.any((analytic<=analytic[j])&(es<=es[j])&((analytic<analytic[j])|(es<es[j])))
  es_bounds=np.quantile(boot_es,[.025,.975],axis=0);tc_bounds=np.quantile(boot_tcar,[.025,.975],axis=0)
  for j,name in enumerate(names):
   r=precision[(precision.seed==seed)&(precision.candidate==name)&(precision.condition=='g0.2_r0.0')].iloc[0]
   np.testing.assert_allclose([r.es_p025,r.es_p975,r.tcar_p025,r.tcar_p975],[es_bounds[0,j],es_bounds[1,j],tc_bounds[0,j],tc_bounds[1,j]],rtol=1e-12)
   r=membership[(membership.seed==seed)&(membership.candidate==name)&(membership.condition=='g0.2_r0.0')].iloc[0]
   assert r.frontier_count==keep_counts[j]
 note=(ROOT/'paper/methodology/NCC_TIMING_FRONTIER_KO.md').read_text()
 for y in [2030,2035,2040,2045]:
  rows=q[(q.commission_year==y)&(q.residual_per_t_naphtha==0)].set_index('grid_initial')
  assert f'| {y} | {rows.loc[.2,"cumulative_ratio"]*100:.2f}% | {rows.loc[.4,"cumulative_ratio"]*100:.2f}% |' in note
 for name in ['replace_2030','replace_2035','replace_2040']:
  a=metrics[(metrics.candidate==name)&(metrics.seed==20260917)].iloc[0];b=metrics[(metrics.candidate==name)&(metrics.seed==20260918)].iloc[0]
  assert f'| {name[-4:]} | {a.analytic_mean:,.2f} | {a.es_alpha:,.2f} | {b.es_alpha:,.2f} | {a.tcar:,.2f} | {b.tcar:,.2f} |' in note
 for literal in ['419.8과476.4','383.0–451.0과433.3–510.6','모두 연도별 선형 상한을 위반']:
  assert literal in note
 report=dict(independent_cost_values_checked=checks,max_incremental_cost_error=maxerror,independent_cash_rows=96,independent_emission_rows=384,qualification_cases=16,risk_values_checked=18,analytic_means_checked=3,bootstrap_interval_endpoints_checked=24,bootstrap_selection_counts_checked=6,standalone_numeric_values_checked=29,frontier_memberships_checked=len(f),feedstock_cancellation_paths=30000,annual_linear_feasible_candidates=0,empirical_frontier_singleton='replace_2040',corporate_calibration=False,sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/NCC_TIMING_FRONTIER_KO.md']})
 (ROOT/'docs/research_cycles/2026-09-07-hourly/timing_frontier_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':main()
