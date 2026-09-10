"""Independent simulation, horizon and selection checks for the NCC diagnostic.

The unchanged naphtha term cancels in the paired difference. The remaining
linear LNG index permits exact mean/variance checks. This is simulation
validation under assumed procurement, not historical forecast validation.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap.block_moments import block_level_covariance,gaussian_level_covariance,weighted_sum_variance
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from cap.risk_metrics import loss_summary
from cap import config as C
from cap.commodity_ledger import CommodityFlow
from cap.plancost import PlanProfile,simulate_cost
from research_block_price_paths import block_paths


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def bootstrap_intervals(x,seed,repeats=200):
    """Resample entire independent path NPVs, conditional on fitted inputs."""
    x=np.asarray(x,dtype=float)
    rng=np.random.default_rng(seed)
    draws=np.sort(x[rng.integers(0,len(x),size=(repeats,len(x)))],axis=1)
    med,q=np.quantile(draws,[.5,.95],axis=1)
    # Here len(x)=10000, so the empirical upper5% has exactly500 draws.
    assert len(x)==10000
    values={'p50':med,'q95':q,'tcar95':q-med,'es95':draws[:,-500:].mean(axis=1)}
    return {f'{k}_{tail}':float(np.quantile(v,a)) for k,v in values.items()
            for tail,a in [('low',.025),('high',.975)]}


def fin_long_horizon_check(annual,ratio,expected):
    n,t=annual.shape;years=tuple(range(2027,2027+t));z=np.zeros(t)
    cfg=C.Config(dict(years=dict(start=years[0],end=years[-1]),discount_rate=.05,
        contracts=dict(ppa_premium_pct=0.,epc_premium_pct=0.,ccfd_fee_pct=0.),
        carbon_accounting_mode='gross_obligation_proxy'))
    flow=CommodityFlow('incremental_methane','netback',np.full(t,-.488e6),
                      'tCH4','export_netback','same conditional NCC full-sale assumption')
    profile=PlanProfile(z.copy(),np.full(t,6.78e6),z.copy(),z.copy(),z.copy(),
        {},{},z.copy(),0.,0,0,coal_t=z.copy(),gas_t=z.copy(),additional_commodity_flows=(flow,),
        embedded_price_basis={},profile_years=years)
    px={k:np.zeros(t) for k in ('elec','re','h2','gas','coal','co2')}
    px['re']=100*1500*(.5+.5*ratio)
    px['netback']=500*1500*ratio
    sh=dict(elec=(.5+.5*ratio*annual)/(.5+.5*ratio),
            h2=np.ones((n,t)),capex=np.ones((n,t)),netback=annual)
    got=simulate_cost(profile,px,sh,dict(subsidy={}),cfg)
    np.testing.assert_allclose(got,expected,atol=1e-8,rtol=1e-12)
    return float(np.max(np.abs(got-expected)))


def main():
    history=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    iea=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
    bridge=ROOT/'data/research_v2/scenario_joint_bridge/manifest.json'
    bridge_meta=json.loads(bridge.read_text())
    for a in bridge_meta['sources']:
        assert sha(ROOT/a['path'])==a['sha256'],a['path']
    r=pd.read_csv(history).japan_lng.to_numpy()
    native=[ScenarioPriceCurve(**c) for c in json.loads(iea.read_text())]
    horizons=(5,10,24);max_years=max(horizons);months=max_years*12
    years=tuple(range(2027,2027+max_years))
    ratios={}
    for s in ('CPS','STEPS','NZE'):
        c=next(c for c in native if c.scenario==s and c.region=='Japan' and c.commodity=='natural_gas')
        ratios[s]=np.asarray(interpolate_curve(c,years,method='linear').values)/c.values[0]
    # Same declared quantities and reporting convention as the FIN-checked60cases.
    qe=6.78;qm=.488;pe=100.;pm=500.;scale=1e6*1500/1e9;rate=.05
    betas=(0.,.5,1.)
    seeds=(20260908,20260909,20260910)
    sizes=(1000,10000,50000)
    disc=(1+rate)**-np.arange(max_years)
    rows=[];cis=[];selected_costs={};moment_rows=[];fin_errors=[]
    for length in (0,1,6,12,24):
        model='iid_gaussian' if length==0 else f'empirical_block_{length}'
        cov=(gaussian_level_covariance(r,months) if length==0
             else block_level_covariance(r,months,length))
        for h in horizons:
            for s,ratio in ratios.items():
                w=np.repeat(ratio[:h]*disc[:h]/12,12)
                variance=weighted_sum_variance(w,cov[:h*12,:h*12])
                moment_rows.append(dict(model=model,scenario=s,horizon_years=h,
                    index_mean=float(w.sum()),index_variance=variance,
                    note='exact conditional moments under specified block/Gaussian law'))
        for seed in seeds:
            print(f'{model} seed{seed}',flush=True)
            if length:
                monthly=block_paths(r[:,None],months,max(sizes),length,seed)[0][:,:,0]
            else:
                var=np.var(r,ddof=1)
                innovation=np.random.default_rng(seed).normal(0,np.sqrt(var),size=(max(sizes),months))
                monthly=np.exp(innovation.cumsum(axis=1)-np.arange(1,months+1)*var/2)
                del innovation
            annual=monthly.reshape(max(sizes),max_years,12).mean(axis=2)
            del monthly
            for s,ratio in ratios.items():
                for h in horizons:
                    weighted_index=annual[:,:h]@(ratio[:h]*disc[:h])
                    mean_index=float((ratio[:h]*disc[:h]).sum())
                    var_index=next(x['index_variance'] for x in moment_rows
                        if x['model']==model and x['scenario']==s and x['horizon_years']==h)
                    top=max(1,int(.01*len(weighted_index)))
                    concentration=float(np.sort(weighted_index)[-top:].sum()/weighted_index.sum())
                    for beta in betas:
                        constant=qe*pe*(1-beta)*disc[:h].sum()*scale
                        loading=(qe*pe*beta-qm*pm)*scale
                        cost=constant+loading*weighted_index
                        if seed==seeds[0] and beta==.5 and s=='STEPS' and h==24:
                            fin_errors.append(fin_long_horizon_check(annual,ratio,cost))
                        true_mean=constant+loading*mean_index
                        true_sd=abs(loading)*np.sqrt(var_index)
                        for n in sizes:
                            x=cost[:n];stats=loss_summary(x,.95)
                            empirical_se=float(x.std(ddof=1)/np.sqrt(n))
                            exact_se=true_sd/np.sqrt(n)
                            rows.append(dict(model=model,seed=seed,scenario=s,horizon_years=h,
                                beta_base=beta,n_paths=n,**stats,theoretical_mean=true_mean,
                                exact_mean_mc_se=exact_se,empirical_mean_mc_se=empirical_se,
                                mean_error_in_exact_se=(stats['mean']-true_mean)/exact_se,
                                empirical_to_exact_sd=float(x.std(ddof=1)/true_sd),
                                top1pct_index_share_50k=concentration,
                                unit='bnKRW2024_partial_incremental_NPV'))
                        # CI: representative exposure, one scenario, short/long horizons.
                        if seed==seeds[0] and beta==.5 and s=='STEPS' and h in (5,24):
                            stats=loss_summary(cost[:10000],.95)
                            cis.append(dict(model=model,scenario=s,horizon_years=h,beta_base=beta,
                                seed=seed,n_paths=10000,bootstrap_repeats=200,
                                tcar95=stats['tcar'],es95=stats['es_alpha'],
                                **bootstrap_intervals(cost[:10000],seed+length+h),
                                interpretation='conditional Monte Carlo uncertainty only; not parameter/model uncertainty'))
                        # Retain representative long-horizon evaluation arrays;
                        # all other arrays are reproducible from sources+seeds.
                        if seed!=seeds[0] and s=='STEPS' and h==24 and beta==.5:
                            selected_costs[f'{model}__{s}__h{h}__seed{seed}__beta{beta}']=cost
            del annual
    d=pd.DataFrame(rows)
    selections=[]
    for (model,s,h),g in d.groupby(['model','scenario','horizon_years']):
        for ntrain in (1000,10000):
            training=g[(g.seed==seeds[0])&(g.n_paths==ntrain)].sort_values('beta_base')
            for risk_weight in (0.,.25,.5,1.):
                obj=(1-risk_weight)*training['mean']+risk_weight*training.es_alpha
                choice=training.loc[obj.idxmin()]
                for validation_seed in seeds[1:]:
                    validation=g[(g.seed==validation_seed)&(g.n_paths==50000)].sort_values('beta_base')
                    val_obj=(1-risk_weight)*validation['mean']+risk_weight*validation.es_alpha
                    picked=validation[validation.beta_base==choice.beta_base].iloc[0]
                    actual=(1-risk_weight)*picked['mean']+risk_weight*picked.es_alpha
                    best=validation.loc[val_obj.idxmin()]
                    selections.append(dict(model=model,scenario=s,horizon_years=h,
                        training_seed=seeds[0],training_paths=ntrain,validation_seed=validation_seed,
                        validation_paths=50000,risk_weight=risk_weight,selected_beta=choice.beta_base,
                        training_objective=float(obj.min()),validation_objective=float(actual),
                        validation_best_beta=best.beta_base,
                        validation_menu_regret=float(actual-val_obj.min()),
                        selection_agrees=bool(choice.beta_base==best.beta_base),
                        caveat='numerical assumed tariff menu; no optimal company investment claim'))
    out=ROOT/'data/research_v2/joint_tail_precision';out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/'precision_metrics.csv',index=False)
    pd.DataFrame(moment_rows).to_csv(out/'exact_index_moments.csv',index=False)
    pd.DataFrame(cis).to_csv(out/'conditional_bootstrap_intervals.csv',index=False)
    pd.DataFrame(selections).to_csv(out/'independent_selection.csv',index=False)
    np.savez_compressed(out/'validation_cost_draws.npz',**selected_costs)
    sources=[history,iea,bridge,Path(__file__),ROOT/'scripts/research_block_price_paths.py',
             ROOT/'src/cap/block_moments.py',ROOT/'src/cap/risk_metrics.py',
             ROOT/'src/cap/plancost.py',ROOT/'src/cap/commodity_ledger.py']
    manifest=dict(sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources],
        seed_roles={'training':seeds[0],'independent_simulation_validation':list(seeds[1:])},
        sizes=sizes,horizons_years=horizons,rows=len(rows),moment_rows=len(moment_rows),
        bootstrap_rows=len(cis),selection_rows=len(selections),saved_arrays=len(selected_costs),
        saved_array_scope='STEPS,24years,beta0.5;five models andtwo validation seeds;others regenerate from script',
        scenario_probabilities_assigned=False,prices_recentered_by_sample_mean=False,
        calibrated_history='2010M02–2025M12 Japan LNG monthly returns',
        same_model_new_random_draws=True,chronological_forecast_holdout=False,
        independent_of_cycle4_seeds=True,full_company_cost=False,FIN_reoptimized=False,
        long_horizon_FIN_check=dict(conditions=len(fin_errors),paths_per_condition=50000,
            scenario='STEPS',years=24,beta=.5,maximum_error_bnKRW=max(fin_errors)),
        dependence_of_comparisons='Sample sizes are nested prefixes; scenarios and tariffs share draws; rows are not independent replications',
        exact_moment_tests='exhaustive enumeration of small independent overlapping block supports',
        mathematical_reduction='Unchanged naphtha cancels; partial incremental cost is constant plus weighted LNG index',
        menu={'beta_base':betas,'available_contracts_verified':False,
              'excluded_exact_cancellation_beta':'Algebraic diagnostic excluded from selection menu',
              'objective':'(1-lambda)*mean + lambda*ES95; lambda is an assumed preference, not estimated'},
        price_assumptions=bridge_meta['price_anchors_assumed_EUR2024'],
        mean_se='Exact conditional second moments and empirical sample SD are both reported',
        confidence_intervals='200percentile bootstrap samples of entire10k cost paths; conditional simulation error only',
        limits=['New simulation seeds are not new empirical data or independently validated forecast models',
            'Horizon24 means2027–2050; source history is shorter and long-run mean reversion is not identified',
            'Block start support is finite; unobserved crises and parameter uncertainty are excluded',
            'Bootstrap intervals do not guarantee nominal coverage in heavy tails; no model-validity claim',
            'Validation menu regret is an independent-sample comparison, not the exact population optimality gap',
            'Price indexing, full methane saleability, production and reporting FX remain assumptions',
            'Gaussian draws reproduce the LNG marginal, not the exact multi-factor random array from cycle4'])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(rows=len(rows),cis=len(cis),selections=len(selections),
        agreement=float(pd.DataFrame(selections).selection_agrees.mean()),out=str(out.relative_to(ROOT))),indent=2))


if __name__=='__main__':main()
