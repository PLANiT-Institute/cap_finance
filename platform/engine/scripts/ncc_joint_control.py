"""Parameterized FIN execution behind the joint-price workbook.

This controls the sourced NCC energy/feedstock partial experiment, not total
corporate transition cost. Frozen legacy portfolio workflows remain separate.
"""
from dataclasses import replace
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from cap.joint_prices import (DrawAxis,JointPricePaths,JointPriceBundle,FINPriceRequirement,
    prices_from_multipliers,indexed_procurement_price,paired_cost_difference)
from cap.commodity_ledger import CommodityFlow
from cap.plancost import PlanProfile,simulate_cost
from cap.risk_metrics import loss_summary
from research_block_price_paths import block_paths,gaussian_paths

DEFAULTS=dict(scenario='STEPS',shock_model='empirical_block_12',seed=20260908,
    paths=10000,start_year=2027,end_year=2050,production_t=1e6,discount_rate=.05,alpha=.95,
    power_EUR2024_MWh=100.,methane_EUR2024_t=500.,naphtha_EUR2024_t=600.,
    power_indexed_share=.5,methane_sale_fraction=1.,KRW2024_per_EUR2024=1500.)
MODELS=('iid_gaussian','empirical_block_1','empirical_block_6','empirical_block_12','empirical_block_24')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_controls(controls):
    if set(controls)!=set(DEFAULTS):raise ValueError('Control keys must exactly match the documented schema')
    c=dict(controls)
    if c['scenario'] not in ('CPS','STEPS','NZE') or c['shock_model'] not in MODELS:
        raise ValueError('Unknown scenario or shock model')
    for key in set(c)-{'scenario','shock_model'}:
        v=c[key]
        if isinstance(v,bool) or not isinstance(v,(int,float,np.number)) or not np.isfinite(v):
            raise ValueError(f'{key}: finite numeric input required; blank is not zero')
    for key in ('seed','paths','start_year','end_year'):
        if c[key]!=int(c[key]):raise ValueError(f'{key}: exact integer required')
        c[key]=int(c[key])
    if c['seed']<0 or not 2<=c['paths']<=50000:raise ValueError('Seed nonnegative; this workflow supports2–50000paths')
    if not 2024<=c['start_year']<=c['end_year']<=2050:raise ValueError('Years outside the source scenario coverage')
    if c['production_t']<0 or c['discount_rate']<=-1:raise ValueError('Invalid output or discount rate')
    if not .5<c['alpha']<1:raise ValueError('Alpha must lie strictly between0.5and1')
    if min(c['power_EUR2024_MWh'],c['naphtha_EUR2024_t'])<0 or c['KRW2024_per_EUR2024']<=0:
        raise ValueError('Power/naphtha anchors nonnegative; reporting conversion positive')
    for key in ('power_indexed_share','methane_sale_fraction'):
        if not 0<=c[key]<=1:raise ValueError(f'{key} must lie between0and1')
    return c


def evaluate(controls):
    c=validate_controls(controls)
    history=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    historical_meta=ROOT/'data/research_v2/block_price_paths/manifest.json'
    old=json.loads(historical_meta.read_text());assert sha(history)==old['source_sha256']
    curve_file=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
    package_file=ROOT/'data/research_v2/technology_packages/reference_process_packages.json'
    packages=json.loads(package_file.read_text())
    for item in packages['source_registers']:
        assert sha(ROOT/item['path'])==item['sha256'],item['path']
    p={x['package_id']:x for x in packages['packages']}
    base,after=[{f['flow_id']:f['quantity'] for f in p[k]['flows']}
        for k in ('LAYRITZ2021_NCC_BASE','LAYRITZ2021_NCC_ELECTRIC')]
    assert base['naphtha']==after['naphtha']==3.58
    qe=after['electricity']-base['electricity'];qm=base['methane_fuel']*c['methane_sale_fraction']
    years=tuple(range(c['start_year'],c['end_year']+1));T=len(years);N=c['paths']
    returns=pd.read_csv(history).set_index('period');raw=returns.to_numpy()
    if c['shock_model']=='iid_gaussian':monthly=gaussian_paths(raw,T*12,N,c['seed'])
    else:monthly,_,_=block_paths(raw,T*12,N,int(c['shock_model'].split('_')[-1]),c['seed'])
    if not np.isfinite(monthly).all() or (monthly<=0).any():raise ValueError('Numerically invalid price paths')
    annual=monthly.reshape(N,T,12,len(returns.columns)).mean(axis=2);del monthly
    # Same IDs cover the full joint path and are shared by both cost profiles.
    signature=hashlib.sha256(json.dumps({k:c[k] for k in ('shock_model','seed','paths','start_year','end_year')},sort_keys=True).encode()).hexdigest()
    axis=DrawAxis(years,tuple(f'draw:{i:05d}' for i in range(N)),f'{sha(history)}:{signature}')
    curves=[ScenarioPriceCurve(**x) for x in json.loads(curve_file.read_text())]
    oil0=next(x for x in curves if x.scenario==c['scenario'] and x.commodity=='crude_oil')
    gas0=next(x for x in curves if x.scenario==c['scenario'] and x.commodity=='natural_gas' and x.region=='Japan')
    oil=interpolate_curve(oil0,years,method='linear');gas=interpolate_curve(gas0,years,method='linear')
    ro=np.asarray(oil.values)/oil0.values[0];rg=np.asarray(gas.values)/gas0.values[0]
    oil_path=prices_from_multipliers(oil,axis,annual[:,:,returns.columns.get_loc('brent')],evidence='WB Brent multiplier on IEA import-average oil: mapping assumption')
    gas_path=prices_from_multipliers(gas,axis,annual[:,:,returns.columns.get_loc('japan_lng')],evidence='WB Japan LNG multiplier on IEA Japan LNG')
    z=np.zeros(T);fx=c['KRW2024_per_EUR2024'];Q=c['production_t'];beta=c['power_indexed_share']
    boundary='conditional_NCC_reference_procurement_not_company_contract'
    def target(commodity,unit,values):
        return ScenarioPriceCurve(oil.model,c['scenario'],'reference_NCC',commodity,years,
            tuple(np.asarray(values)*fx),unit,'KRW',2024,boundary,('assumed_total_price',),
            source='Explicit control assumptions applied to IEA scenario ratios')
    def mapped(source,curve,indexed_share,evidence):
        if (np.asarray(curve.values)<=0).any():
            # Signed disposal netbacks and zero marginal prices are level maps.
            # Do not bypass the positive-target contract of the index helper.
            b=np.asarray(indexed_share)
            levels=np.asarray(curve.values)*(1-b+b*source.values/np.asarray(source.curve.values))
            return JointPricePaths(curve,axis,levels,evidence+'; explicit signed/zero price-level mapping')
        return indexed_procurement_price(source,curve,indexed_share=indexed_share,evidence=evidence)
    power_c=target('electricity','MWh',c['power_EUR2024_MWh']*(1-beta+beta*rg))
    power=mapped(gas_path,power_c,beta*rg/(1-beta+beta*rg),'Base-year fixed plus LNG-indexed tariff; not a PPA')
    nap=mapped(oil_path,target('naphtha','t_naphtha',c['naphtha_EUR2024_t']*ro),1.,'Assumed naphtha-to-oil mapping')
    met=mapped(gas_path,target('methane_netback','tCH4',c['methane_EUR2024_t']*rg),1.,'Assumed methane-to-LNG netback mapping')
    channel={'elec':power,'re':power,'naphtha':nap,'methane_netback':met}
    for key,unit in dict(h2='kg_H2',gas='t_gas',coal='t_coal',co2='tCO2').items():
        channel[key]=JointPricePaths(target('excluded_'+key,unit,z),axis,np.zeros(axis.shape),'Excluded partial-cost channel; quantity zero')
    flows=(CommodityFlow('naphtha_purchase','naphtha',np.full(T,base['naphtha']*Q),'t_naphtha','purchased','Sourced unchanged feedstock'),)
    baseline=PlanProfile(np.full(T,base['electricity']*Q),z.copy(),z.copy(),z.copy(),z.copy(),{},{},z.copy(),0.,0,0,
        coal_t=z.copy(),gas_t=z.copy(),additional_commodity_flows=flows,embedded_price_basis={},profile_years=years)
    transition=replace(baseline,re_mwh=np.full(T,qe*Q),additional_commodity_flows=flows+(
        CommodityFlow('freed_methane','methane_netback',np.full(T,-qm*Q),'tCH4','export_netback','Sourced internal methane times assumed sale fraction'),))
    bundle=JointPriceBundle(channel)
    requirements={k:FINPriceRequirement(v.curve.commodity,v.curve.quantity_unit,'KRW',2024,boundary) for k,v in channel.items()}
    px,sh=bundle.fin_inputs_for_profile(transition,requirements,years=years)
    bundle.fin_inputs_for_profile(baseline,requirements,years=years);sh['capex']=np.ones(axis.shape)
    cfg=C.Config(dict(years=dict(start=years[0],end=years[-1]),discount_rate=c['discount_rate'],
        contracts=dict(ppa_premium_pct=0.,epc_premium_pct=0.,ccfd_fee_pct=0.),carbon_accounting_mode='gross_obligation_proxy'))
    cb=simulate_cost(baseline,px,sh,dict(subsidy={}),cfg);ct=simulate_cost(transition,px,sh,dict(subsidy={}),cfg)
    delta=paired_cost_difference(ct,cb,transition_axis=axis,baseline_axis=axis)
    disc=(1+c['discount_rate'])**-np.arange(T)
    hand=((qe*power.values-qm*met.values)*disc).sum(axis=1)*Q/1e9
    np.testing.assert_allclose(delta,hand,rtol=1e-11,atol=1e-6)
    central=(qe*np.asarray(power.curve.values)-qm*np.asarray(met.curve.values))*Q/1e9
    annual_rows=[dict(year=y,oil_ratio=ro[i],lng_ratio=rg[i],
        power_EUR2024_MWh=power.curve.values[i]/fx,naphtha_EUR2024_t=nap.curve.values[i]/fx,
        methane_EUR2024_t=met.curve.values[i]/fx,discount_factor=disc[i],
        central_incremental_bnKRW2024=central[i],discounted_incremental_bnKRW2024=central[i]*disc[i]) for i,y in enumerate(years)]
    inputs=[history,historical_meta,curve_file,package_file,Path(__file__),ROOT/'scripts/research_block_price_paths.py',
        ROOT/'src/cap/joint_prices.py',ROOT/'src/cap/plancost.py',ROOT/'src/cap/commodity_ledger.py',
        ROOT/'src/cap/risk_metrics.py',ROOT/'src/cap/scenario_prices.py',ROOT/'src/cap/config.py']
    result=dict(controls=c,metrics=loss_summary(delta,c['alpha']),baseline_mean_bnKRW2024=float(cb.mean()),
        transition_mean_bnKRW2024=float(ct.mean()),theoretical_mean_bnKRW2024=float(central@disc),
        mc_mean_standard_error_bnKRW2024=float(delta.std(ddof=1)/np.sqrt(N)),
        max_independent_formula_error_bnKRW2024=float(np.max(np.abs(delta-hand))),annual=annual_rows,
        scope='NCC energy,unchanged naphtha,and methane sales partial costs; no capital,carbon,other operating costs or product revenue',
        price_anchors_status='Assumed EUR2024 values; not observed corporate procurement',
        quantities=dict(base_electricity_MWh_t=base['electricity'],added_electricity_MWh_t=qe,
            naphtha_t_t=base['naphtha'],generated_methane_t_t=base['methane_fuel']),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},sample_id=axis.sample_id,
        runtime=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__))
    return result,{'baseline':cb,'transition':ct,'incremental':delta}


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--controls',type=Path);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();result,draws=evaluate(json.loads(args.controls.read_text()) if args.controls else DEFAULTS)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    np.savez_compressed(args.out/'cost_draws.npz',**draws)
    print(json.dumps(result['metrics']))
