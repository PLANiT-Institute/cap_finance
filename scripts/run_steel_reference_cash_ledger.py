"""Joint-price execution of Vogl's published cost components, with dated capital.

No incumbent comparator is fabricated. These are absolute reference process cost
sensitivities, not company transition TCaR or a frontier across output levels.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C
from cap.reference_steel import build_vogl_reference_profile
from cap.plancost import simulate_cost
from cap.risk_metrics import loss_summary
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from research_block_price_paths import block_paths


def main():
    package_path=ROOT/'data/research_v2/steel_cost_reference/vogl_main_text_package.json'
    package=json.loads(package_path.read_text())
    assert hashlib.sha256((ROOT/package['source']['local_path']).read_bytes()).hexdigest()==package['source']['sha256']
    history_path=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    hist=pd.read_csv(history_path).set_index('period')
    old=json.loads((ROOT/'data/research_v2/block_price_paths/manifest.json').read_text())
    assert hashlib.sha256(history_path.read_bytes()).hexdigest()==old['source_sha256']
    curve_path=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
    curves=[ScenarioPriceCurve(**c) for c in json.loads(curve_path.read_text())]
    gas=next(c for c in curves if c.scenario=='STEPS' and c.commodity=='natural_gas' and c.region=='Japan')
    years=tuple(range(2027,2051));T=len(years);N=10000;fx=1500.;discount=1.05**-np.arange(T)
    ratio=np.array(interpolate_curve(gas,years,method='linear').values)/gas.values[0]
    central_power=40.*(.5+.5*ratio)
    px={k:np.zeros(T) for k in ['elec','re','h2','co2','coal','gas']};px['elec']=central_power*fx
    for p in package['purchases']:px[p['flow_id']]=np.full(T,p['price_EUR']*fx)
    px['oxygen_netback']=np.full(T,60.8*fx)
    cfg=C.load(discount_rate=.05,carbon_accounting_mode='gross_obligation_proxy');cfg['years']={'start':2027,'end':2050}
    out=ROOT/'data/research_v2/steel_reference_ledger';out.mkdir(parents=True,exist_ok=True)
    rows=[];annual_rows=[];draws={};max_error=0.
    for length in [1,12]:
        for seed in [20260908,20260909]:
            monthly,_,_=block_paths(hist.to_numpy(),T*12,N,length,seed)
            annual=monthly.reshape(N,T,12,len(hist.columns)).mean(axis=2);del monthly
            gas_mult=annual[:,:,hist.columns.get_loc('japan_lng')]
            ore_mult=annual[:,:,hist.columns.get_loc('iron_ore')]
            power_native=40.*(.5+.5*ratio*gas_mult)
            sh={k:np.ones((N,T)) for k in ['elec','h2','capex','pellets','lime','alloys','graphite_electrodes','oxygen_netback']}
            sh['elec']=power_native/central_power;sh['pellets']=ore_mult
            for utilization in [.5,.75,1.]:
                for sale in [0.,.6]:
                    reference=build_vogl_reference_profile(package,years,capacity_t_per_year=1e6,
                        annual_utilization=np.full(T,utilization),adopt_year=2027,build_years=3,
                        numerical_KRW_per_source_EUR=fx,oxygen_sale_fraction=sale,direct_emission_factor_tco2_per_t=0.)
                    p=reference.profile;output=reference.output_t
                    costs=simulate_cost(p,px,sh,{'subsidy':{}},cfg,freeze='capex')*1000/fx
                    # Independent explicit native-unit formula; source maintenance
                    # remains capacity-based. No annualized capital is added.
                    cap=np.zeros(T);cap[:3]=574e6/3;cap[13]=160e6;cap[23]=574e6
                    deterministic=cap+output*(.05*100+.011*1777+.002*4000+53.2-.411*sale*60.8)
                    deterministic+=(np.array(years)>=2030)*1e6*574*.03
                    hand=((deterministic+output*(3.48*power_native+1.504*100*ore_mult))*discount).sum(axis=1)/1e6
                    np.testing.assert_allclose(costs,hand,rtol=2e-13,atol=1e-8)
                    max_error=max(max_error,float(np.max(np.abs(costs-hand))))
                    m=loss_summary(costs,.95)
                    theoretical=float(((deterministic+output*(3.48*central_power+1.504*100))*discount).sum()/1e6)
                    rows.append(dict(model=f'block_{length}',seed=seed,paths=N,utilization=utilization,oxygen_sale_fraction=sale,
                        mean_million_source_EUR=m['mean'],theoretical_mean_million_source_EUR=theoretical,
                        mc_mean_standard_error_million_source_EUR=float(costs.std(ddof=1)/np.sqrt(N)),p50_million_source_EUR=m['p50'],
                        q95_million_source_EUR=m['q_alpha'],absolute_cost_upper_gap95_million_source_EUR=m['tcar'],
                        ES95_million_source_EUR=m['es_alpha'],
                        mean_per_discounted_output_source_EUR_t=costs.mean()*1e6/(output@discount)))
                    if length==12 and seed==20260908:
                        draws[f'u{utilization}_sale{sale}']=costs
                        for i,y in enumerate(years):
                            annual_rows.append(dict(utilization=utilization,oxygen_sale_fraction=sale,year=y,output_t=output[i],
                                electricity_MWh=p.grid_mwh[i],pellets_t=output[i]*1.504,
                                labour_source_EUR=reference.operating_cost_components_k['labour'][i]*1000/fx,
                                fixed_maintenance_source_EUR=reference.operating_cost_components_k['fixed_maintenance'][i]*1000/fx,
                                gross_capital_source_EUR=p.capex_k[i]*1000/fx,
                                electricity_source_EUR_MWh=central_power[i],discount_factor=discount[i]))
    results=pd.DataFrame(rows);results.to_csv(out/'absolute_cost_sensitivity.csv',index=False)
    pd.DataFrame(annual_rows).to_csv(out/'annual_quantities_and_cash.csv',index=False)
    np.savez_compressed(out/'absolute_cost_draws.npz',**draws)
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':10,'axes.unicode_minus':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    view=results[(results.model=='block_12')&(results.seed==20260908)]
    for sale,color in [(0.,'#b35a26'),(.6,'#236997')]:
        v=view[view.oxygen_sale_fraction==sale]
        axes[0].plot(v.utilization*100,v.mean_per_discounted_output_source_EUR_t,marker='o',color=color,label=f'산소 판매비율 {sale:.0%}')
        for _,r in v.iterrows():
            x=r.utilization*100+(sale-.3)*2
            axes[1].plot([x,x],[r.p50_million_source_EUR,r.q95_million_source_EUR],color=color,lw=4)
    axes[0].set(xlabel='연간 설비 가동률 (%)',ylabel='평균 비용 NPV / 할인 생산량 (원문 EUR/t)',title='생산량이 줄어도 고정 투자·유지비는 남는다')
    axes[0].legend(fontsize=8)
    axes[1].set(xlabel='연간 설비 가동률 (%)',ylabel='절대 비용 NPV (백만 원문 EUR)',title='중앙값–95분위: 기준안 대비 증분 TCaR는 미산출')
    fig.suptitle('문헌 비용항목 참조: 같은 설비용량·다른 생산량의 민감도',fontsize=11)
    fig.savefig(out/'utilization_and_cost_distribution.png',dpi=180)
    fig.savefig(ROOT/'paper/methodology/figures/steel_utilization_and_cash.png',dpi=180)
    plt.close(fig)
    manifest=dict(scope='Vogl published material/electricity/labour/maintenance plus dated component capital; absolute reference cost only',
        company_transition_TCaR=False,frontier_comparison=False,incumbent_counterfactual_included=False,
        price_basis=package['price_basis'],uniform_real_price_year_verified=False,
        paired_FIN_paths_checked=len(rows)*N,max_independent_error_million_source_EUR=max_error,
        scenario='IEA2025 STEPS Japan LNG dimensionless ratio only; native USD2024 level NOT mixed into source EUR',
        assumptions={'capacity_t_annual':1e6,'years':years,'adoption':2027,'operation':2030,'discount_rate':.05,
            'electricity_anchor_source_EUR_MWh':40.,'gas_indexed_power_share':.5,
            'pellet_mean_native_source_EUR_t':100.,'pellet_shock_mapping':'World Bank iron ore joint multiplier; no pellet-grade/basis residual',
            'oxygen_native_price_EUR_t':60.8,'oxygen_conditioning_cost':0.,'oxygen_price_random':False,
            'capital_random':False,'carbon_price':0.,'other_material_prices_random':False,
            'numerical_KRW_per_source_EUR':fx,'unit_mapping_not_observed_FX':True},
        limits=package['limits']+['No future forecast probability validation','No corporate baseline or emission feasibility comparison',
            'Utilization sensitivity changes output, so these points cannot define a common-service frontier',
            'Zero oxygen conditioning is source-price reproduction, not a verified market netback'],
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [package_path,history_path,curve_path,
            ROOT/'src/cap/reference_steel.py',ROOT/'src/cap/component_capital.py',ROOT/'src/cap/plancost.py',Path(__file__)]})
    manifest['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='manifest.json'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'paths_verified':len(rows)*N,'max_error_million_source_EUR':max_error,
                     'example':view[view.oxygen_sale_fraction==.6].to_dict('records')},indent=2))

if __name__=='__main__':main()
