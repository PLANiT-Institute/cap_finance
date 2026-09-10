"""Nine explicit incumbent-age/replacement-cost assumptions, one shared draw pool."""
from pathlib import Path
import sys,json,hashlib,itertools
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.reference_ncc import NCCConditions,build_ncc_reference
from cap.reference_incumbent import existing_ncc_pair
from cap.plancost import simulate_cost
from cap.risk_metrics import loss_summary
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from cap import config as C
from research_block_price_paths import block_paths


def main():
 out=ROOT/'data/research_v2/incumbent_ncc';out.mkdir(parents=True,exist_ok=True)
 src=ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv';histfile=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv';curvefile=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
 assert hashlib.sha256(src.read_bytes()).hexdigest()==json.loads((src.parent/'manifest.json').read_text())['sha256'][str(src.relative_to(ROOT))]
 assert hashlib.sha256(histfile.read_bytes()).hexdigest()==json.loads((ROOT/'data/research_v2/block_price_paths/manifest.json').read_text())['source_sha256']
 obs=pd.read_csv(src).to_dict('records');hist=pd.read_csv(histfile).set_index('period');curves=[ScenarioPriceCurve(**r) for r in json.loads(curvefile.read_text())]
 years=tuple(range(2027,2051));T=len(years);N=5000;fx=1000.;disc=1.05**-np.arange(T)
 ref=[build_ncc_reference(obs,c,years,NCCConditions(1,8000,life,psi,.04,.05,1,'none'),numerical_KRW_per_EUR=fx) for c,life,psi in [('conventional',30,.04),('electric',20,.02)]]
 def ratio(commodity,region=None):
  c=next(c for c in curves if c.scenario=='STEPS' and c.commodity==commodity and (region is None or c.region==region))
  return np.array(interpolate_curve(c,years,method='linear').values)/c.values[0]
 gr=ratio('natural_gas','Japan');orr=ratio('crude_oil')
 monthly,_,_=block_paths(hist.to_numpy(),T*12,N,12,20260913)
 annual=monthly.reshape(N,T,12,len(hist.columns)).mean(axis=2);del monthly
 gas=annual[:,:,hist.columns.get_loc('japan_lng')];oil=annual[:,:,hist.columns.get_loc('brent')]
 cp=100*(.5+.5*gr);cg=40*gr;cn=600*orr
 power=100*(.5+.5*gr*gas);methane=cg*gas;naphtha=cn*oil
 shocks={k:np.ones((N,T)) for k in ('elec','h2','capex')};shocks.update(elec=power/cp,methane=gas,naphtha=oil)
 prices={k:np.zeros(T) for k in ('elec','re','h2','co2','coal','gas')};prices.update(elec=cp*fx,methane=cg*fx,naphtha=cn*fx)
 cfg=C.load(discount_rate=.05,carbon_accounting_mode='gross_obligation_proxy');cfg['years']={'start':2027,'end':2050}
 original=[simulate_cost(r['profile'],prices,shocks,{'subsidy':{}},cfg,freeze='capex') for r in ref];original_delta=original[1]-original[0]
 rows=[];annual_rows=[];saved={};errors=[];shift_errors=[]
 for remaining,cost_scale in itertools.product([3,8,18],[.5,1.,1.5]):
  r=existing_ncc_pair(*ref,years=years,remaining_years=remaining,replacement_cost_scale=cost_scale,retirement_cash_EUR=0.,salvage_receipt_EUR=0.,terminal_rule='none',ethylene_yield=.303,numerical_KRW_per_EUR=fx)
  costs=[]
  for name,p in r['profiles'].items():
   a=r['annual'][name];f=p.additional_commodity_flows
   expected=((a['net_fixed_cash_EUR']+p.grid_mwh*power+f[0].quantity*naphtha+(f[1].quantity+f[2].quantity)*methane)*disc).sum(axis=1)/1e6
   actual=simulate_cost(p,prices,shocks,{'subsidy':{}},cfg,freeze='capex')
   np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-7);errors.append(float(np.max(abs(actual-expected))));costs.append(actual)
   for i,y in enumerate(years):annual_rows.append(dict(remaining_years=remaining,replacement_cost_scale=cost_scale,case=name,year=y,**{k:float(v[i]) for k,v in a.items()}))
  delta=costs[1]-costs[0];b=r['annual']['continue_existing'];e=r['annual']['replace_2030']
  shift=(disc*(ref[0]['capital'].net_cash_payments-b['incumbent_renewal_EUR']+e['incumbent_renewal_EUR'])).sum()/1e6
  np.testing.assert_allclose(delta-original_delta,shift,rtol=1e-10,atol=1e-7);shift_errors.append(float(np.max(abs(delta-original_delta-shift))))
  m=loss_summary(delta,.95);rows.append(dict(remaining_years=remaining,replacement_cost_scale=cost_scale,**m,new_vs_new_mean=float(original_delta.mean()),mean_shift=shift,baseline_renewal_NPV_million_EUR=float(b['incumbent_renewal_EUR']@disc/1e6),noncash_writeoff_proxy_million_EUR=float(e['noncash_writeoff_proxy_EUR'].sum()/1e6)))
  saved[f'life{remaining}_scale{cost_scale}']=delta
 pd.DataFrame(rows).to_csv(out/'conditional_metrics.csv',index=False);pd.DataFrame(annual_rows).to_csv(out/'annual_cash.csv',index=False);np.savez_compressed(out/'incremental_draws.npz',**saved)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib import font_manager
 font=ROOT/'tmp/pdfs/methodology/Heading.ttf';font_manager.fontManager.addfont(str(font));plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'axes.unicode_minus':False})
 matrix=pd.DataFrame(rows).pivot(index='replacement_cost_scale',columns='remaining_years',values='mean_shift').sort_index()
 fig,ax=plt.subplots(figsize=(7,3.8));limit=float(abs(matrix.to_numpy()).max());im=ax.imshow(matrix,cmap='RdBu_r',vmin=-limit,vmax=limit,aspect='auto')
 for i in range(3):
  for j in range(3):ax.text(j,i,f'{matrix.iloc[i,j]:+.1f}',ha='center',va='center',color='white' if abs(matrix.iloc[i,j])>limit*.62 else '#182c3d',fontsize=12)
 ax.set_xticks(range(3),['3년','8년','18년']);ax.set_yticks(range(3),['0.5배','1.0배','1.5배']);ax.set_xlabel('가정한 기존 설비의 남은 수명');ax.set_ylabel('가정한 교체비 / 신규공장 참조비');ax.set_title('기존 설비 기준선으로 바꿀 때 평균 증분비용의 변화')
 fig.colorbar(im,ax=ax,label='백만 EUR2019 가정');fig.tight_layout();fig.savefig(out/'incumbent_assumption_grid.png',dpi=180);plt.close(fig)
 report=dict(conditions=9,paths_per_condition=N,independent_draw_pools=1,FIN_cost_values_checked=90000,max_FIN_error=max(errors),max_counterfactual_shift_error=max(shift_errors),TCaR_range=float(np.ptp([r['tcar'] for r in rows])),annual_rows=len(annual_rows),corporate_calibration=False,emissions_feasibility=False,frontier_selection=False,
 assumptions=dict(remaining_years=[3,8,18],replacement_cost_scale=[.5,1,1.5],incumbent_cost_is_newbuild_proxy=True,historical_capital_recharged=False,retirement_cash=0,salvage_cash=0,terminal_rule='none',zero_replacement_downtime=True,old_specification_equals_new_conventional_reference=True,initial_incumbent_operates_2027_2029=True,one_common_price_pool=True,prices='same prior conditional STEPS/block12/seed20260913 assumptions',carbon_labour_working_capital_tax_financing_other_coproducts_excluded=True),
 input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,histfile,curvefile,ROOT/'src/cap/reference_ncc.py',ROOT/'src/cap/capital_ledger.py',ROOT/'src/cap/reference_incumbent.py',Path(__file__)]},artifact_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='manifest.json'})
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ('input_sha256','artifact_sha256','assumptions')});print(pd.DataFrame(rows).query('replacement_cost_scale==1')[['remaining_years','mean','es_alpha','tcar','mean_shift','noncash_writeoff_proxy_million_EUR']].to_string(index=False))
if __name__=='__main__':main()
