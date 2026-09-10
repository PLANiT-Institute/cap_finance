"""Paired same-output greenfield capture-boundary FIN research experiment.

All conditions are explicit below. Source transcription is provisional. This
does not calibrate a Korean/Japanese company or price permanent CO2 storage.
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
from cap.commodity_ledger import CommodityFlow
from cap.plancost import PlanProfile,simulate_cost
from cap.risk_metrics import loss_summary,pareto_mask,sampled_dominance_witnesses
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from research_block_price_paths import block_paths


def profile(package,case,years,central_gas,hedge,premium,fx):
    if not np.isfinite([hedge,premium,fx]).all() or not 0<=hedge<=1 or premium<0 or fx<=0:
        raise ValueError('Invalid explicit contract or numerical unit mapping')
    if tuple(years)!=tuple(range(2027,2051)):
        raise ValueError('This experiment fixes its research timing and production service')
    r=package['cases'][case];base=package['cases']['REFERENCE']
    op=(np.array(years)>=2030).astype(float);zero=np.zeros(len(years))
    delta_gas=r['ng_GJ']-base['ng_GJ'];hedged=delta_gas*hedge
    if case=='REFERENCE' and hedge!=0:raise ValueError('Baseline contract is explicitly unhedged')
    cap=zero.copy();cap[:3]=r['initial_capex_source_USD']/3
    renewal=zero.copy();renewal[list(years).index(2044)]=r['reline_source_USD']
    flows=(CommodityFlow('ng_market','ng_GJ',op*(r['ng_GJ']-hedged),'GJ','purchased',
               'IEAGHG package gas quantity; incremental gas block alone may be contracted'),
           CommodityFlow('ore_bundle','ore_bundle',op.copy(),'annual_source_ore_bundle','purchased',
               'IEAGHG Volume II D15 fixed composition basket at4MtHRC; price index mapping is a research assumption'))
    fixed=op*(r['residual_fixed_price_opex_source_USD']+r['coal_bundle_source_USD']+hedged*central_gas*(1+premium))
    p=PlanProfile(grid_mwh=zero.copy(),re_mwh=zero.copy(),h2_kg=zero.copy(),other_cost_k=fixed*fx/1000,
        capex_k=(cap+renewal)*fx/1000,capex_by_tech={case:cap*fx/1000},capex_unc={case:0.},
        emissions=op*r['output_t_HRC']*r['direct_co2_t_per_t_HRC'],ppa=0.,epc=0,ccfd=0,
        maintenance_capex_k=renewal*fx/1000,terminal_value_k=zero.copy(),
        additional_commodity_flows=flows,embedded_price_basis={},profile_years=tuple(years))
    return p,cap,renewal,fixed,op


def main():
    source_dir=ROOT/'data/research_v2/ieaghg_reference'
    package_path=source_dir/'package.json';pkg=json.loads(package_path.read_text())
    for name,want in json.loads((source_dir/'manifest.json').read_text())['sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want,name
    history_path=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    history=pd.read_csv(history_path).set_index('period')
    assert hashlib.sha256(history_path.read_bytes()).hexdigest()==json.loads((ROOT/'data/research_v2/block_price_paths/manifest.json').read_text())['source_sha256']
    curve_path=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
    curves=[ScenarioPriceCurve(**x) for x in json.loads(curve_path.read_text())]
    years=tuple(range(2027,2051));T=len(years);disc=1.05**-np.arange(T);fx=1000.;premium=.03
    cfg=C.load(discount_rate=.05,carbon_accounting_mode='gross_obligation_proxy')
    cfg['years']={'start':2027,'end':2050}
    out=ROOT/'data/research_v2/ieaghg_paired';out.mkdir(parents=True,exist_ok=True)
    results=[];selections=[];cash_rows=[];saved={};absolute_saved={};max_error=0.;max_cancellation=0.;fin_values=0
    for length in [1,12]:
        for role,N,seed in [('selection',2500,20260910),('validation',10000,20260911)]:
            monthly,_,_=block_paths(history.to_numpy(),T*12,N,length,seed)
            annual=monthly.reshape(N,T,12,len(history.columns)).mean(axis=2);del monthly
            gas_mult=annual[:,:,history.columns.get_loc('europe_gas')]
            ore_mult=annual[:,:,history.columns.get_loc('iron_ore')]
            for scenario in ['CPS','STEPS','NZE']:
                curve=next(c for c in curves if c.scenario==scenario and c.commodity=='natural_gas' and c.region=='European Union')
                central_gas=pkg['ng_price_source_USD_GJ']*np.asarray(interpolate_curve(curve,years,method='linear').values)/curve.values[0]
                gas_price=central_gas*gas_mult
                ore_bill=pkg['cases']['REFERENCE']['ore_bundle_source_USD']
                px={k:np.zeros(T) for k in ['elec','re','h2','co2','coal','gas']}
                px.update(ng_GJ=central_gas*fx,ore_bundle=np.full(T,ore_bill*fx))
                sh={k:np.ones((N,T)) for k in ['elec','h2','capex']}
                sh.update(ng_GJ=gas_mult,ore_bundle=ore_mult)
                base_cost=None;group=[];losses={}
                for case,h in [('REFERENCE',0.)]+[(c,h) for c in ['EOP_L1','EOP_L2'] for h in [0.,.25,.5,.75,1.]]:
                    p,cap,renewal,fixed,op=profile(pkg,case,years,central_gas,h,premium,fx)
                    r=pkg['cases'][case];b=pkg['cases']['REFERENCE'];dg=r['ng_GJ']-b['ng_GJ']
                    costs=simulate_cost(p,px,sh,{'subsidy':{}},cfg,freeze='capex')*1000/fx
                    hand=((cap+renewal+fixed+op*((r['ng_GJ']-h*dg)*gas_price+ore_bill*ore_mult))*disc).sum(axis=1)/1e6
                    np.testing.assert_allclose(costs,hand,rtol=2e-13,atol=1e-7)
                    max_error=max(max_error,float(abs(costs-hand).max()));fin_values+=N
                    if case=='REFERENCE':
                        base_cost=costs
                        if length==12 and role=='validation' and scenario=='STEPS':absolute_saved['REFERENCE']=costs
                        continue
                    delta=costs-base_cost
                    # Derive the difference without common ore, coal, byproducts,
                    # reline or baseline gas. It must match subtracting full bills.
                    dc=cap.copy();dc[:3]-=b['initial_capex_source_USD']/3
                    deterministic=op*(r['residual_fixed_price_opex_source_USD']-b['residual_fixed_price_opex_source_USD']+h*dg*central_gas*(1+premium))
                    direct=((dc+deterministic+op*(1-h)*dg*gas_price)*disc).sum(axis=1)/1e6
                    np.testing.assert_allclose(delta,direct,rtol=2e-12,atol=2e-7)
                    max_cancellation=max(max_cancellation,float(abs(delta-direct).max()))
                    # Use the algebraically equivalent difference to prevent
                    # roundoff in enormous shared bills from creating false tails.
                    delta=direct
                    if h==1:np.testing.assert_allclose(delta,delta[0],atol=1e-9)
                    metrics=loss_summary(delta,.95);absolute=loss_summary(costs,.95)
                    theoretical=float(((dc+deterministic+op*(1-h)*dg*central_gas)*disc).sum()/1e6)
                    pid=f'{case}_h{h:.2f}';losses[pid]=delta
                    row=dict(model=f'block_{length}',role=role,seed=seed,paths=N,scenario=scenario,plan_id=pid,case=case,
                        incremental_gas_contract_fraction=h,reported_direct_reduction=1-r['direct_co2_t_per_t_HRC']/b['direct_co2_t_per_t_HRC'],
                        mean=metrics['mean'],p50=metrics['p50'],q95=metrics['q_alpha'],tcar95=metrics['tcar'],es95=metrics['es_alpha'],
                        analytic_mean=theoretical,mean_mc_se=float(delta.std(ddof=1)/np.sqrt(N)),
                        absolute_mean=absolute['mean'],absolute_es95=absolute['es_alpha'])
                    results.append(row);group.append(row)
                    if length==12 and role=='validation' and scenario=='STEPS':
                        saved[pid]=delta
                        absolute_saved[pid]=costs
                        for i,year in enumerate(years):
                            cash_rows.append(dict(plan_id=pid,year=year,output_t_HRC=op[i]*4e6,
                                capex_source_USD=cap[i],reline_source_USD=renewal[i],
                                market_ng_GJ=p.additional_commodity_flows[0].quantity[i],contracted_ng_GJ=op[i]*h*dg,
                                ore_bundle_count=op[i],central_gas_source_USD_GJ=central_gas[i],
                                fixed_price_cash_source_USD=fixed[i],direct_co2=p.emissions[i]))
                for target in [.5,.6]:
                    admissible=[r for r in group if r['reported_direct_reduction']>=target]
                    witnesses=sampled_dominance_witnesses({r['plan_id']:losses[r['plan_id']] for r in admissible},atol=1e-8)
                    mask=pareto_mask([r['mean'] for r in admissible],[r['es95'] for r in admissible])
                    analytic_mask=pareto_mask([r['analytic_mean'] for r in admissible],[r['es95'] for r in admissible])
                    for r,on_frontier,on_analytic_frontier in zip(admissible,mask,analytic_mask):
                        selections.append(dict(model=r['model'],role=role,scenario=scenario,target_onsite_reduction=target,
                            plan_id=r['plan_id'],on_sampled_mean_ES_frontier=bool(on_frontier),
                            on_analytic_mean_sample_ES_frontier=bool(on_analytic_frontier),
                            pathwise_dominance_witness=witnesses.get(r['plan_id'],'')))
    df=pd.DataFrame(results);selection=pd.DataFrame(selections)
    df.to_csv(out/'conditional_cost_metrics.csv',index=False)
    selection.to_csv(out/'finite_frontier.csv',index=False)
    pd.DataFrame(cash_rows).to_csv(out/'annual_cash_quantities.csv',index=False)
    np.savez_compressed(out/'STEPS_validation_incremental_costs.npz',**saved)
    np.savez_compressed(out/'STEPS_validation_absolute_costs.npz',**absolute_saved)
    comparisons=[]
    for (model,scenario,target),g in selection.groupby(['model','scenario','target_onsite_reduction']):
        a=set(g[(g.role=='selection')&g.on_sampled_mean_ES_frontier].plan_id)
        b=set(g[(g.role=='validation')&g.on_sampled_mean_ES_frontier].plan_id)
        aa=set(g[(g.role=='selection')&g.on_analytic_mean_sample_ES_frontier].plan_id)
        bb=set(g[(g.role=='validation')&g.on_analytic_mean_sample_ES_frontier].plan_id)
        comparisons.append(dict(model=model,scenario=scenario,target=target,selection_frontier=sorted(a),validation_frontier=sorted(b),same_frontier=a==b,
            analytic_mean_selection_frontier=sorted(aa),analytic_mean_validation_frontier=sorted(bb),same_analytic_mean_frontier=aa==bb))
    (out/'independent_selection.json').write_text(json.dumps(comparisons,indent=2)+'\n')
    font_manager.fontManager.addfont(str(ROOT/'tmp/pdfs/methodology/Heading.ttf'))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=str(ROOT/'tmp/pdfs/methodology/Heading.ttf')).get_name(),'axes.unicode_minus':False,'font.size':9})
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    source=pd.DataFrame(pkg['cases']).T
    axes[0].bar(source.index,source.ng_GJ.astype(float)/4e6,color=['#8a959b','#397b94','#b8683b'])
    axes[0].set(ylabel='천연가스 (GJ/t HRC)',title='같은 HRC 생산에서 늘어나는 외부 가스')
    axes[0].text(.02,.97,'기준안: 원문 물량 / L1·L2: 비용차에서 역산\n전력 수입 0은 원문의 자체 발전 가정',transform=axes[0].transAxes,va='top',fontsize=8)
    for case,color in [('EOP_L1','#397b94'),('EOP_L2','#b8683b')]:
        v=df[(df.model=='block_12')&(df.role=='validation')&(df.scenario=='STEPS')&(df.case==case)]
        axes[1].scatter(v['mean'],v.es95,color=color,label=case)
        for r in v.itertuples():axes[1].annotate(f'{r.incremental_gas_contract_fraction:.0%}',(r.mean,r.es95),xytext=(4,3),textcoords='offset points',fontsize=7)
    axes[1].set(xlabel='평균 증분비용 (백만 원문 USD)',ylabel='ES95 (백만 원문 USD)',title='추가 가스 물량의 계약 비율별 후보')
    axes[1].legend(fontsize=8)
    axes[1].margins(x=.12)
    fig.suptitle('조건부 참조 실험: 신설 공정·포집 경계 / 수송·저장 비용 제외',fontsize=11)
    fig.savefig(out/'paired_capture_reference.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    view=df[(df.model=='block_12')&(df.scenario=='STEPS')&(df.case=='EOP_L1')]
    for role,color,label in [('selection','#b8683b','선택 표본 2,500경로'),('validation','#397b94','독립 평가 10,000경로')]:
        v=view[view.role==role]
        axes[0].plot(v.incremental_gas_contract_fraction*100,v['mean'],marker='o',color=color,label=label)
        axes[1].plot(v.incremental_gas_contract_fraction*100,v.es95,marker='o',color=color,label=label)
    v=view[view.role=='validation']
    axes[0].plot(v.incremental_gas_contract_fraction*100,v.analytic_mean,color='#333333',linestyle='--',label='주어진 모형의 해석적 기대값')
    axes[0].set(title='표본평균의 기울기가 반대로 나타난다',ylabel='평균 증분비용 (백만 원문 USD)')
    axes[1].set(title='평균 오차를 없애도 ES의 표본 차이는 남는다',ylabel='ES95 (백만 원문 USD)')
    for ax in axes:ax.set_xlabel('추가 가스 물량의 계약 비율 (%)');ax.legend(fontsize=8)
    fig.suptitle('같은 모형·후보, 다른 난수: EOP-L1 / STEPS / 블록12개월',fontsize=11)
    fig.savefig(out/'mean_and_tail_selection_instability.png',dpi=180);plt.close(fig)
    manifest=dict(source_visual_review_pending=True,company_calibration=False,full_CCS_cost=False,
        unit='million_USD_source_report_basis',cashflow_years=years,operation_start=2030,
        construction='equal thirds2027-29; research timing, not source ramp',reline='2044:15th operating year counting2030as1; zero downtime source assumption',
        discount=.05,numerical_KRW_per_source_USD=fx,unit_mapping_is_observed_FX=False,
        capital_deterministic=True,carbon_cost=0.,transport_storage_cost_excluded=True,
        working_capital_financing_end_of_life_excluded=True,incremental_gas_contract_premium=premium,
        contract='fixed annual central-price schedule plus3%; incremental NG volume only; baseline/common gas remains unhedged; no default/basis/volume risk',
        price_mapping='IEA2025 EU gas scenario/2024 ratio times9.77 source USD/GJ; WB Europe gas joint block multiplier; not observed firm contract or reconstructed2010prices',
        ore_mapping='source fixed ore-basket bill times WB iron-ore multiplier; no grade/freight/basis residual',
        coal_and_remaining_prices='source prices deterministic; not assigned a thermal-coal proxy',
        source_support='provisional web-text transcription,9arithmetic crosschecks passed,1source conflict held; not visual/source validation completion',
        model_scope='gas and ore conditional shocks only; complete listed source capital/O&M cash accounts, not all corporate costs or risks',
        candidate_scope='2source capture routes x5incremental gas contracts; annual on-site reduction50%or60%; no declaration-to-net-zero feasibility claim',
        FIN_cost_values_checked=fin_values,max_FIN_vs_independent_error=max_error,max_common_cost_cancellation_error=max_cancellation,
        conditional_rows=len(df),frontier_comparisons=len(comparisons),independent_frontier_disagreements=sum(not x['same_frontier'] for x in comparisons),
        analytic_mean_frontier_disagreements=sum(not x['same_analytic_mean_frontier'] for x in comparisons),
        independent_draw_pools=4,scenario_and_target_comparisons_share_draws=True,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [package_path,history_path,curve_path,Path(__file__),ROOT/'src/cap/plancost.py',ROOT/'scripts/research_block_price_paths.py']})
    manifest['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='manifest.json'}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['FIN_cost_values_checked','max_FIN_vs_independent_error','max_common_cost_cancellation_error','conditional_rows','frontier_comparisons','independent_frontier_disagreements']}))


if __name__=='__main__':main()
