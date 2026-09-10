"""Gate source-reference timing choices by emissions, then evaluate paired FIN costs.

Two independent price pools; no fitted corporate inputs or scenario probabilities.
Grid/residual conditions are explicit sensitivity assumptions, not national paths.
"""
from pathlib import Path
import sys,json,hashlib,itertools
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.reference_timing import timing_menu,emission_qualification
from cap.risk_metrics import loss_summary,pareto_mask,sampled_dominance_witnesses
from cap.plancost import simulate_cost
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from cap import config as C
from research_block_price_paths import block_paths


def main():
 out=ROOT/'data/research_v2/ncc_timing_frontier';out.mkdir(parents=True,exist_ok=True)
 obsfile=ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv';histfile=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv';curvefile=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
 assert hashlib.sha256(obsfile.read_bytes()).hexdigest()==json.loads((obsfile.parent/'manifest.json').read_text())['sha256'][str(obsfile.relative_to(ROOT))]
 assert hashlib.sha256(histfile.read_bytes()).hexdigest()==json.loads((ROOT/'data/research_v2/block_price_paths/manifest.json').read_text())['source_sha256']
 obs=pd.read_csv(obsfile).to_dict('records');hist=pd.read_csv(histfile).set_index('period');curves=[ScenarioPriceCurve(**r) for r in json.loads(curvefile.read_text())]
 menu=timing_menu(obs,[2030,2035,2040,2045],remaining_years=8,replacement_cost_scale=1.,numerical_KRW_per_EUR=1000.)
 years=menu['years'];yy=np.asarray(years);T=len(years);N=5000;disc=1.05**-np.arange(T)
 # Separate emission ledger: never use cash profile zero placeholders.
 annual=[];qualification=[];eligible_by_condition={}
 for g0,residual in itertools.product([.2,.4],[0.,.05]):
  condition=f'g{g0}_r{residual}';grid=g0*(2050-yy)/23
  feed=menu['baseline'].additional_commodity_flows[0].quantity
  baseline_emissions=.397*feed+menu['baseline'].grid_mwh*grid+residual*feed
  annual_caps=baseline_emissions[0]*(2050-yy)/23;cumulative_cap=float(.75*baseline_emissions.sum());terminal_cap=0.
  eligible=[]
  for name,r in menu['candidates'].items():
   direct=np.where(r['electric_active'],0.,.397)*feed;power=r['profile'].grid_mwh*grid;rest=residual*feed;e=direct+power+rest
   q=emission_qualification(e,annual_caps=annual_caps,cumulative_cap=cumulative_cap,terminal_cap=terminal_cap)
   qualified=q['cumulative_feasible'] and q['terminal_feasible']
   if qualified:eligible.append(name)
   qualification.append(dict(condition=condition,candidate=name,commission_year=r['commission_year'],grid_initial=g0,residual_per_t_naphtha=residual,cumulative_emissions=float(e.sum()),baseline_cumulative=float(baseline_emissions.sum()),cumulative_ratio=float(e.sum()/baseline_emissions.sum()),cumulative_cap=cumulative_cap,terminal_emissions=float(e[-1]),terminal_cap=0.,**q,eligible_for_cumulative_terminal_menu=qualified))
   for i,y in enumerate(years):annual.append(dict(condition=condition,candidate=name,year=y,output_t=r['output_t'][i],grid_factor=grid[i],direct_emissions=direct[i],power_emissions=power[i],residual_emissions=rest[i],total_emissions=e[i],baseline_emissions=baseline_emissions[i],annual_linear_cap=annual_caps[i]))
  eligible_by_condition[condition]=eligible
 eligible_union=sorted(set().union(*map(set,eligible_by_condition.values())))
 assert eligible_union==['replace_2030','replace_2035','replace_2040']
 pd.DataFrame(qualification).to_csv(out/'qualification.csv',index=False);pd.DataFrame(annual).to_csv(out/'annual_emissions.csv',index=False)
 def ratio(commodity,region=None):
  c=next(c for c in curves if c.scenario=='STEPS' and c.commodity==commodity and (region is None or c.region==region))
  return np.asarray(interpolate_curve(c,years,method='linear').values)/c.values[0]
 gr=ratio('natural_gas','Japan');orr=ratio('crude_oil');cp=100*(.5+.5*gr);cg=40*gr;cn=600*orr
 cfg=C.load(discount_rate=.05,carbon_accounting_mode='gross_obligation_proxy');cfg['years']={'start':2027,'end':2050}
 prices={k:np.zeros(T) for k in ['elec','re','h2','co2','coal','gas']};prices.update(elec=cp*1000,methane=cg*1000,naphtha=cn*1000)
 rows=[];saved={};pools={};errors=[];dominance={};bootstrap=[];precision=[]
 def direct_cost(profile,fixed,power,methane,naphtha):
  flows=profile.additional_commodity_flows
  return ((fixed+profile.grid_mwh*power+flows[0].quantity*naphtha+(flows[1].quantity+flows[2].quantity)*methane)*disc).sum(axis=-1)/1e6
 analytic_base=float(direct_cost(menu['baseline'],menu['baseline_fixed_cash_EUR'],cp,cg,cn))
 analytic={name:float(direct_cost(menu['candidates'][name]['profile'],menu['candidates'][name]['fixed_cash_EUR'],cp,cg,cn))-analytic_base for name in eligible_union}
 for seed in [20260917,20260918]:
  monthly,_,_=block_paths(hist.to_numpy(),T*12,N,12,seed)
  mult=monthly.reshape(N,T,12,len(hist.columns)).mean(axis=2);del monthly
  gas=mult[:,:,hist.columns.get_loc('japan_lng')];oil=mult[:,:,hist.columns.get_loc('brent')]
  power=100*(.5+.5*gr*gas);methane=cg*gas;naphtha=cn*oil
  pools[f'{seed}_power']=power;pools[f'{seed}_methane']=methane;pools[f'{seed}_naphtha']=naphtha
  shocks={k:np.ones((N,T)) for k in ['elec','h2','capex']};shocks.update(elec=power/cp,methane=gas,naphtha=oil)
  base=simulate_cost(menu['baseline'],prices,shocks,{'subsidy':{}},cfg,freeze='capex')
  expected=direct_cost(menu['baseline'],menu['baseline_fixed_cash_EUR'],power,methane,naphtha);np.testing.assert_allclose(base,expected,rtol=1e-12,atol=1e-7);errors.append(float(np.max(abs(base-expected))));saved[f'{seed}_baseline']=base
  draws={}
  for name in eligible_union:
   r=menu['candidates'][name];actual=simulate_cost(r['profile'],prices,shocks,{'subsidy':{}},cfg,freeze='capex')
   expected=direct_cost(r['profile'],r['fixed_cash_EUR'],power,methane,naphtha);np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-7);errors.append(float(np.max(abs(actual-expected))))
   delta=actual-base;draws[name]=delta;saved[f'{seed}_{name}']=delta
   rows.append(dict(seed=seed,candidate=name,analytic_mean=analytic[name],**loss_summary(delta,.95)))
  dominance[str(seed)]=sampled_dominance_witnesses(draws)
  for condition,names in eligible_by_condition.items():
   if not names:continue
   rng=np.random.default_rng(seed+100);counts={n:0 for n in names};boot_es={n:[] for n in names};boot_tcar={n:[] for n in names}
   for b in range(500):
    ix=rng.integers(0,N,N);es=[np.sort(draws[n][ix])[-250:].mean() for n in names]
    mask=pareto_mask([analytic[n] for n in names],es)
    for j,(name,keep) in enumerate(zip(names,mask)):
     counts[name]+=int(keep);boot_es[name].append(es[j]);qs=np.quantile(draws[name][ix],[.5,.95]);boot_tcar[name].append(qs[1]-qs[0])
   for name in names:
    bounds_es=np.quantile(boot_es[name],[.025,.975]);bounds_tc=np.quantile(boot_tcar[name],[.025,.975])
    precision.append(dict(seed=seed,condition=condition,candidate=name,es_p025=bounds_es[0],es_p975=bounds_es[1],tcar_p025=bounds_tc[0],tcar_p975=bounds_tc[1],bootstrap_replicates=500,scope='conditional empirical percentile intervals; no model or parameter uncertainty'))
   for name,count in counts.items():bootstrap.append(dict(seed=seed,condition=condition,candidate=name,frontier_count=count,bootstrap_replicates=500,frequency=count/500,interpretation='paired empirical resampling selection frequency; not probability of true efficiency'))
 metrics=pd.DataFrame(rows);frontiers=[]
 for seed,g in metrics.groupby('seed'):
  for condition,names in eligible_by_condition.items():
   if not names:continue
   r=g.set_index('candidate').loc[names]
   for mean_col in ['mean','analytic_mean']:
    mask=pareto_mask(r[mean_col],r.es_alpha)
    for name,keep in zip(names,mask):frontiers.append(dict(seed=int(seed),condition=condition,candidate=name,mean_axis=mean_col,non_dominated=bool(keep)))
 metrics.to_csv(out/'risk_metrics.csv',index=False);pd.DataFrame(frontiers).to_csv(out/'frontier_membership.csv',index=False);pd.DataFrame(bootstrap).to_csv(out/'paired_bootstrap_membership.csv',index=False)
 pd.DataFrame(precision).to_csv(out/'bootstrap_precision.csv',index=False)
 np.savez_compressed(out/'cost_draws.npz',**saved);np.savez_compressed(out/'annual_prices.npz',**pools)
 cash=[]
 for name,r in menu['candidates'].items():
  for i,y in enumerate(years):cash.append(dict(candidate=name,year=y,output_t=r['output_t'][i],grid_mwh=r['profile'].grid_mwh[i],feedstock_t=r['profile'].additional_commodity_flows[0].quantity[i],net_methane_MWh=sum(f.quantity[i] for f in r['profile'].additional_commodity_flows[1:]),**{k:r[k][i] for k in ['fixed_cash_EUR','construction_EUR','new_renewal_EUR','incumbent_renewal_EUR']}))
 pd.DataFrame(cash).to_csv(out/'annual_cash.csv',index=False)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib import font_manager
 font=ROOT/'tmp/pdfs/methodology/Heading.ttf';font_manager.fontManager.addfont(str(font));plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'axes.unicode_minus':False})
 fig,axes=plt.subplots(1,2,figsize=(10,4.4))
 qual=pd.DataFrame(qualification)
 for g0,color in [(.2,'#188b91'),(.4,'#ad593d')]:
  d=qual[(qual.grid_initial==g0)&(qual.residual_per_t_naphtha==0)]
  axes[0].plot(d.commission_year,d.cumulative_ratio*100,'o-',label=f'전력계수 {g0}에서 0으로 감소',color=color)
 axes[0].axhline(75,ls='--',color='#566979',label='가정한 누적 예산 75%')
 axes[0].set(xlabel='전기화 공정 가동 시작',ylabel='기존 유지 대비 누적 배출 (%)',title='감축 자격을 먼저 검사한다',xticks=[2030,2035,2040,2045]);axes[0].legend(fontsize=8,frameon=False)
 for seed,marker,color in [(20260917,'o','#188b91'),(20260918,'x','#ad593d')]:
  d=metrics[metrics.seed==seed];axes[1].scatter(d.analytic_mean,d.es_alpha,marker=marker,s=45,color=color,label=f'독립 표본 {1 if seed==20260917 else 2}')
  for r in (d.itertuples() if seed==20260917 else []):axes[1].annotate(r.candidate[-4:],(r.analytic_mean,r.es_alpha),xytext=(5,4),textcoords='offset points',fontsize=8)
 axes[1].set(xlabel='해석적 평균 증분비용 (백만 EUR)',ylabel='표본 ES95 (백만 EUR)',title='전력 0.2→0 조건: 평균과 꼬리 비교');axes[1].legend(fontsize=8,frameon=False)
 for ax in axes:ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.15);ax.set_axisbelow(True)
 fig.text(.5,.018,'전력계수 단위 tCO2/MWh | 잔여배출 0의 조건부 문헌 공정 | 실제 기업·국가 경로 아님',ha='center',fontsize=9)
 fig.tight_layout(rect=(0,.05,1,1))
 for ext in ['png','pdf']:fig.savefig(out/f'timing_frontier.{ext}',dpi=190)
 plt.close(fig)
 report=dict(eligible_by_condition=eligible_by_condition,qualification_before_MC=True,all_annual_linear_qualifications=sum(r['annual_feasible'] for r in qualification),FIN_cost_values_checked=40000,max_FIN_error=max(errors),seeds=[20260917,20260918],paths_per_pool=N,bootstrap_replicates_per_nonempty_condition_pool=500,sampled_dominance=dominance,
   assumptions=dict(scenario='IEA2025 STEPS ratios',historical_source='WB6monthly2010-2025demeanedlogreturns',shock='common overlapping noncircular block12; exact expected multiplier1',price_basis='EUR2019 assumed real operating-price basis; not market quotations',electricity_central='100*(0.5+0.5*JapanLNGscenarioRatio)',methane_central='40*JapanLNGscenarioRatio',naphtha_central='600*BrentscenarioRatio',discount=.05,carbon_cost_excluded=True,emissions_ledger='reported direct0.397/assumed0 tCO2 per t naphtha + modeled purchased power + explicit common residual',grid_conditions='linear2027initial0.2or0.4 to2050zero; not national pathways; same price conditions held fixed',residual_per_t_naphtha=[0,.05],cumulative_cap='75% of same-condition continue-existing cumulative emissions',terminal_cap=0,annual_comparator='linear2027baseline to2050zero; separately tested, not implied by cumulative cap',commission_dates=[2030,2035,2040,2045],old_remaining_life=8,replacement_cost_scale=1,zero_downtime=True,common_output_t_per_year=920000,newplant_life=20,construction_years=3,terminal_cash_receipt=0,adaptation_to_observed_prices=False,excluded_other_costs=['labour','working capital','tax','financing','other coproduct revenues','closure salvage'],grid_residual_probabilities_assigned=False),corporate_calibration=False,full_GHG=False,workbook_updated=False,
   input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [obsfile,histfile,curvefile,Path(__file__),ROOT/'src/cap/reference_timing.py',ROOT/'src/cap/reference_ncc.py',ROOT/'src/cap/reference_incumbent.py',ROOT/'src/cap/plancost.py']},artifact_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.name!='manifest.json'})
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(metrics[['seed','candidate','analytic_mean','mean','es_alpha','tcar']].to_string(index=False));print(eligible_by_condition);print(pd.DataFrame(frontiers).to_string(index=False));print('max FIN error',max(errors))

if __name__=='__main__':main()
