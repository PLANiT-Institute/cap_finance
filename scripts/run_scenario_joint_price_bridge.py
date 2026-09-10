"""Connect sourced IEA central paths and joint historical shocks through FIN.

Five-year NCC partial cashflow experiment. Procurement price anchors, indexing,
saleability and constant-currency conversion are explicit assumptions, not
observed firm contracts. No corporate total, optimized plan or PPA is claimed.
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
from cap.joint_prices import (DrawAxis,JointPricePaths,JointPriceBundle,
    FINPriceRequirement,prices_from_multipliers,indexed_procurement_price,
    paired_cost_difference)
from cap.commodity_ledger import CommodityFlow
from cap.plancost import PlanProfile,simulate_cost
from cap.risk_metrics import loss_summary


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    iea=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
    folder=ROOT/'data/research_v2/block_price_paths'
    meta_path=folder/'manifest.json'
    archive=folder/'annual_multipliers.npz'
    packages_path=ROOT/'data/research_v2/technology_packages/reference_process_packages.json'
    iea_manifest=ROOT/'data/research_v2/iea_2025_scenarios/manifest.json'
    curves=[ScenarioPriceCurve(**x) for x in json.loads(iea.read_text())]
    meta=json.loads(meta_path.read_text())
    assert sha(ROOT/meta['source'])==meta['source_sha256']
    packages=json.loads(packages_path.read_text())
    for item in packages['source_registers']:
        assert sha(ROOT/item['path'])==item['sha256']
    byid={p['package_id']:p for p in packages['packages']}
    base,post=[{f['flow_id']:f['quantity'] for f in byid[k]['flows']}
               for k in ('LAYRITZ2021_NCC_BASE','LAYRITZ2021_NCC_ELECTRIC')]
    assert base['naphtha']==post['naphtha']==3.58
    qe=post['electricity']-base['electricity']; qm=base['methane_fuel']
    pe,pn,pm=100.,600.,500.  # assumed EUR2024 reporting anchors, not observations
    fx=1500.  # assumed constant EUR2024 -> KRW2024 reporting conversion
    Q=1e6; rate=.05
    hedge_beta=qm*pm/(qe*pe)
    zips=np.load(archive)
    N,T,K=zips[meta['models'][0]].shape
    assert N==meta['paths'] and T*12==meta['months'] and K==len(meta['factors'])
    years=tuple(range(2027,2027+T))
    j_oil,j_gas=[meta['factors'].index(k) for k in ('brent','japan_lng')]
    draw_ids=tuple(f'draw:{i:05d}' for i in range(N))
    cfg=C.Config(dict(years=dict(start=years[0],end=years[-1]),discount_rate=rate,
        contracts=dict(ppa_premium_pct=0.,epc_premium_pct=0.,ccfd_fee_pct=0.),
        carbon_accounting_mode='gross_obligation_proxy'))
    z=np.zeros(T);disc=(1+rate)**-np.arange(T)
    naphtha=CommodityFlow('naphtha_purchase','naphtha',np.full(T,base['naphtha']*Q),
        't_naphtha','purchased','Layritz source package: unchanged3.58t/t ethylene')
    methane=CommodityFlow('freed_methane','methane_netback',np.full(T,-qm*Q),
        'tCH4','export_netback','Layritz internal fuel; full netback sale assumed')
    baseline=PlanProfile(np.full(T,base['electricity']*Q),z.copy(),z.copy(),z.copy(),
        z.copy(),{},{},z.copy(),0.,0,0,coal_t=z.copy(),gas_t=z.copy(),
        additional_commodity_flows=(naphtha,),embedded_price_basis={},profile_years=years)
    transition=replace(baseline,re_mwh=np.full(T,qe*Q),
                       additional_commodity_flows=(naphtha,methane))
    rows=[];central_rows=[];price_checks=[];saved={};maxerr=0.;maxcancel=0.
    source_archive_hash=sha(archive)
    for scenario in ('CPS','STEPS','NZE'):
        oil0=next(c for c in curves if c.scenario==scenario and c.commodity=='crude_oil')
        gas0=next(c for c in curves if c.scenario==scenario and c.commodity=='natural_gas' and c.region=='Japan')
        oil=interpolate_curve(oil0,years,method='linear')
        gas=interpolate_curve(gas0,years,method='linear')
        ro=np.asarray(oil.values)/oil0.values[0]
        rg=np.asarray(gas.values)/gas0.values[0]
        for model in meta['models']:
            # IDs index whole paths, never independent commodity permutations.
            axis=DrawAxis(years,draw_ids,f'{source_archive_hash}:{model}:seed{meta["seed"]}')
            raw_oil=prices_from_multipliers(oil,axis,zips[model][:,:,j_oil],
                evidence='Assumption: WB Brent historical multiplier applied to IEA import-average oil')
            raw_gas=prices_from_multipliers(gas,axis,zips[model][:,:,j_gas],
                evidence='Assumption: WB Japan LNG historical multiplier applied to IEA Japan LNG')
            for beta in (0.,hedge_beta,.5,1.):
                boundary='conditional_NCC_reference_procurement_not_company_contract'
                def target(commodity,unit,values):
                    return ScenarioPriceCurve(oil.model,scenario,'reference_NCC',commodity,
                        years,tuple(np.asarray(values)*fx),unit,'KRW',2024,boundary,
                        ('assumed_total_price',),
                        'Assumed EUR2024 anchors and1500KRW2024/EUR2024; IEA ratios, not currency/unit conversion')
                power_c=target('electricity','MWh',pe*(1-beta+beta*rg))
                power_b=beta*rg/(1-beta+beta*rg)
                power=indexed_procurement_price(raw_gas,power_c,indexed_share=power_b,
                    evidence=f'Assumed tariff P=100*((1-{beta})+{beta}*LNG_t/LNG_2024), fixed EUR2024')
                nap=indexed_procurement_price(raw_oil,target('naphtha','t_naphtha',pn*ro),
                    indexed_share=1.,evidence='Assumed naphtha=600EUR2024/t*IEA oil_t/oil_2024')
                met=indexed_procurement_price(raw_gas,target('methane_netback','tCH4',pm*rg),
                    indexed_share=1.,evidence='Assumed netback=500EUR2024/t*IEA LNG_t/LNG_2024; full sale')
                channel={'elec':power,'re':power,'naphtha':nap,'methane_netback':met}
                for key,unit in dict(h2='kg_H2',gas='t_gas',coal='t_coal',co2='tCO2').items():
                    channel[key]=JointPricePaths(target('excluded_'+key,unit,z),axis,np.zeros(axis.shape),
                        'Explicitly excluded from partial experiment; physical quantity zero')
                bundle=JointPriceBundle(channel)
                expected={'elec':('electricity','MWh'),'re':('electricity','MWh'),
                    'naphtha':('naphtha','t_naphtha'),'methane_netback':('methane_netback','tCH4'),
                    'h2':('excluded_h2','kg_H2'),'gas':('excluded_gas','t_gas'),
                    'coal':('excluded_coal','t_coal'),'co2':('excluded_co2','tCO2')}
                requirements={k:FINPriceRequirement(commodity,unit,'KRW',2024,boundary)
                              for k,(commodity,unit) in expected.items()}
                px,sh=bundle.fin_inputs_for_profile(transition,requirements,years=years)
                bundle.fin_inputs_for_profile(baseline,requirements,years=years)
                sh['capex']=np.ones(axis.shape) # no capital flows in this partial experiment
                cb=simulate_cost(baseline,px,sh,dict(subsidy={}),cfg)
                ct=simulate_cost(transition,px,sh,dict(subsidy={}),cfg)
                delta=paired_cost_difference(ct,cb,transition_axis=axis,baseline_axis=axis)
                hand=((qe*power.values-qm*met.values)*disc).sum(axis=1)*Q/1e9
                maxerr=max(maxerr,float(np.max(np.abs(delta-hand))))
                np.testing.assert_allclose(delta,hand,atol=1e-8,rtol=1e-11)
                expected=((qe*np.asarray(power_c.values)-qm*np.asarray(met.curve.values))*disc).sum()*Q/1e9
                if beta==hedge_beta:
                    fixed=pe*(1-beta)*fx*qe*disc.sum()*Q/1e9
                    maxcancel=max(maxcancel,float(np.max(np.abs(delta-fixed))))
                    np.testing.assert_allclose(delta,fixed,atol=1e-8,rtol=1e-11)
                stats=loss_summary(delta,.95)
                rows.append(dict(scenario=scenario,shock_model=model,power_base_indexed_share=beta,
                    **stats,theoretical_mean=expected,mean_mc_se=float(delta.std(ddof=1)/np.sqrt(N)),
                    baseline_mean=float(cb.mean()),transition_mean=float(ct.mean()),
                    unit='bnKRW2024_partial_incremental_NPV',
                    status='conditional_reference_experiment_not_corporate_TCaR'))
                key=f'{scenario}__{model}__beta_{beta:.12g}'
                saved[key]=delta
                if model==meta['models'][0]:
                    for key2,p in (('electricity',power),('naphtha',nap),('methane_netback',met)):
                        for t,y in enumerate(years):
                            central_rows.append(dict(scenario=scenario,beta_base=beta,year=y,
                                commodity=key2,central_price=p.curve.values[t],
                                price_unit=f'KRW2024/{p.curve.quantity_unit}',
                                power_indexed_share_at_t=power_b[t],
                                status='assumed_procurement_from_sourced_scenario_ratios'))
                if beta==.5:
                    for key2,p in (('IEA_oil',raw_oil),('IEA_LNG',raw_gas),('electricity',power),('naphtha',nap)):
                        for t,y in enumerate(years):
                            x=p.values[:,t]
                            price_checks.append(dict(scenario=scenario,model=model,channel=key2,year=y,
                                central=p.curve.values[t],sample_mean=float(x.mean()),
                                mean_mc_se=float(x.std(ddof=1)/np.sqrt(N)),
                                unit=f'{p.curve.currency}{p.curve.price_year}/{p.curve.quantity_unit}'))
    out=ROOT/'data/research_v2/scenario_joint_bridge';out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'conditional_risk_metrics.csv',index=False)
    pd.DataFrame(central_rows).to_csv(out/'procurement_central_assumptions.csv',index=False)
    pd.DataFrame(price_checks).to_csv(out/'price_mean_checks.csv',index=False)
    pd.DataFrame({'draw_id':draw_ids}).to_csv(out/'draw_ids.csv',index=False)
    np.savez_compressed(out/'incremental_cost_draws.npz',**saved)
    sources=[iea,iea_manifest,meta_path,archive,ROOT/meta['source'],packages_path,Path(__file__),
        ROOT/'src/cap/joint_prices.py',ROOT/'src/cap/scenario_prices.py',
        ROOT/'src/cap/plancost.py',ROOT/'src/cap/commodity_ledger.py']
    manifest=dict(paths=N,years=years,scenarios=['CPS','STEPS','NZE'],shock_models=meta['models'],
        rows=len(rows),reference_production_t_per_year=Q,discount_rate=rate,
        price_anchors_assumed_EUR2024=dict(electricity_per_MWh=pe,naphtha_per_t=pn,methane_netback_per_t=pm),
        fixed_reporting_KRW2024_per_EUR2024=fx,currency_conversion_empirically_verified=False,
        electricity_equation='100EUR2024/MWh*(1-beta+beta*(IEA_LNG_s,t/IEA_LNG_2024)*M_LNG)',
        naphtha_equation='600EUR2024/t*(IEA_oil_s,t/IEA_oil_2024)*M_Brent',
        methane_equation='500EUR2024/t*(IEA_LNG_s,t/IEA_LNG_2024)*M_LNG',
        beta_at_t='beta*R_gas/(1-beta+beta*R_gas); keeping beta constant after reanchoring changes the tariff',
        maximum_independent_formula_error_bnKRW=maxerr,maximum_exact_index_cancellation_error_bnKRW=maxcancel,
        exact_cancellation_beta_base=hedge_beta,FIN_simulate_cost_used=True,legacy_inputs_changed=False,
        E2_reoptimized=False,full_company_cost=False,procurement_mapping_estimated=False,
        distribution_interpretation='Scenario-conditional model sensitivity; no scenario probabilities or identified forecast-error distribution',
        independent_selection_validation=False,draw_id_policy='Whole path identity; source archive hash, shock model, seed; shared across commodities',
        excluded=['Capital','Other operating changes','Carbon','Steam/compression and other coproduct changes',
            'Company contracts and netback saleability','FX and basis residuals','Price/technology parameter estimation uncertainty',
            'Unobserved crises and long-run mean reversion','PPA or operating flexibility valuation'],
        limitations=['IEA import-average oil is not Brent or naphtha; using benchmark multipliers is an assumption',
            'Japan LNG border HHV prices are not plant electricity or methane netbacks',
            'EUR2024 anchors and reporting FX are explicit illustrative assumptions, not sourced market prices',
            'Same annual quantity and unchanged naphtha prices/contracts in both strategies',
            'The exact cancellation beta is an algebraic diagnostic under assumed shared indexing; not an available tariff or recommendation',
            '10k Monte Carlo paths and five years do not validate the2050tail'],
        sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'max_formula_error':maxerr,'max_cancellation_error':maxcancel,
                      'out':str(out.relative_to(ROOT))},indent=2))


if __name__=='__main__':main()
