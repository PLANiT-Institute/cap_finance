"""Conditional same-output new-plant NCC cash comparison, not a company frontier."""
from pathlib import Path
import hashlib,json,sys,itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,font_manager
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.reference_ncc import NCCConditions,build_ncc_reference
from cap.plancost import simulate_cost
from cap.risk_metrics import loss_summary
from cap import config as C
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve
from research_block_price_paths import block_paths


def main():
    source=ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv'
    manifest=json.loads((source.parent/'manifest.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['sha256'][str(source.relative_to(ROOT))]
    obs=pd.read_csv(source).to_dict('records')
    histfile=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    hist=pd.read_csv(histfile).set_index('period')
    assert hashlib.sha256(histfile.read_bytes()).hexdigest()==json.loads((ROOT/'data/research_v2/block_price_paths/manifest.json').read_text())['source_sha256']
    curvefile=ROOT/'data/research_v2/iea_2025_scenarios/curves.json'
    curves=[ScenarioPriceCurve(**x) for x in json.loads(curvefile.read_text())]
    years=tuple(range(2027,2051));T=len(years);N=5000;fx=1000.;disc=1.05**-np.arange(T)
    def ratio(commodity,region=None):
        c=next(x for x in curves if x.scenario=='STEPS' and x.commodity==commodity and (region is None or x.region==region))
        return np.array(interpolate_curve(c,years,method='linear').values)/c.values[0]
    gas_ratio=ratio('natural_gas','Japan');oil_ratio=ratio('crude_oil')
    central_power=100*(.5+.5*gas_ratio);central_gas=40*gas_ratio;central_naphtha=600*oil_ratio
    px={k:np.zeros(T) for k in ['elec','re','h2','co2','coal','gas']}
    px.update(elec=central_power*fx,methane=central_gas*fx,naphtha=central_naphtha*fx)
    cfg=C.load(discount_rate=.05,carbon_accounting_mode='gross_obligation_proxy');cfg['years']={'start':2027,'end':2050}
    out=ROOT/'data/research_v2/ncc_reference_cash';out.mkdir(parents=True,exist_ok=True)
    results=[];annual_rows=[];saved={};max_error=0.;max_pair_error=0.;values_checked=0
    for block,seed in itertools.product([1,12],[20260912,20260913]):
        monthly,_,_=block_paths(hist.to_numpy(),T*12,N,block,seed)
        annual=monthly.reshape(N,T,12,len(hist.columns)).mean(axis=2);del monthly
        gas=annual[:,:,hist.columns.get_loc('japan_lng')];oil=annual[:,:,hist.columns.get_loc('brent')]
        power=100*(.5+.5*gas_ratio*gas);methane=central_gas*gas;naphtha=central_naphtha*oil
        sh={k:np.ones((N,T)) for k in ['elec','h2','capex']};sh.update(elec=power/central_power,methane=gas,naphtha=oil)
        for recovery,life,scale,terminal in itertools.product([.8,1.],[20,30],[.01,1.],['none','straight_line_proxy']):
            profiles=[];costs=[];det=[]
            for case,years_life,psi in [('conventional',30,.04),('electric',life,.02)]:
                c=NCCConditions(recovery,8000.,years_life,psi*scale,.04*scale,.05,1.,terminal)
                r=build_ncc_reference(obs,case,years,c,numerical_KRW_per_EUR=fx);p=r['profile'];profiles.append(r)
                fixed=r['capital'].net_cash_payments+r['maintenance_EUR'];det.append(fixed)
                cost=simulate_cost(p,px,sh,{'subsidy':{}},cfg,freeze='capex')*1000/fx
                feed=p.additional_commodity_flows[0].quantity
                netgas=p.additional_commodity_flows[1].quantity+p.additional_commodity_flows[2].quantity
                hand=((fixed+p.grid_mwh*power+feed*naphtha+netgas*methane)*disc).sum(axis=1)/1e6
                np.testing.assert_allclose(cost,hand,rtol=3e-13,atol=1e-7)
                max_error=max(max_error,float(abs(cost-hand).max()));values_checked+=N;costs.append(cost)
            b,e=[r['profile'] for r in profiles]
            np.testing.assert_array_equal(profiles[0]['output_t'],profiles[1]['output_t'])
            np.testing.assert_array_equal(b.additional_commodity_flows[0].quantity,e.additional_commodity_flows[0].quantity)
            dgrid=e.grid_mwh-b.grid_mwh
            dgas=sum(f.quantity for f in e.additional_commodity_flows[1:])-sum(f.quantity for f in b.additional_commodity_flows[1:])
            fixed=det[1]-det[0]
            # Common naphtha cash cancels, even when its price is correlated.
            delta=((fixed+dgrid*power+dgas*methane)*disc).sum(axis=1)/1e6
            np.testing.assert_allclose(costs[1]-costs[0],delta,rtol=3e-12,atol=1e-7)
            max_pair_error=max(max_pair_error,float(abs(costs[1]-costs[0]-delta).max()))
            m=loss_summary(delta,.95)
            theory=((fixed+dgrid*central_power+dgas*central_gas)*disc).sum()/1e6
            pid=f'r{recovery}_life{life}_psi{scale}_{terminal}'
            results.append(dict(block=block,seed=seed,paths=N,recovery=recovery,electric_life=life,
                maintenance_scale=scale,terminal=terminal,condition_id=pid,mean=m['mean'],p50=m['p50'],q95=m['q_alpha'],
                tcar95=m['tcar'],es95=m['es_alpha'],analytic_mean=theory,
                baseline_mean=costs[0].mean(),electric_mean=costs[1].mean(),
                capital_delta_npv=((profiles[1]['capital'].net_cash_payments-profiles[0]['capital'].net_cash_payments)*disc).sum()/1e6,
                maintenance_delta_npv=((profiles[1]['maintenance_EUR']-profiles[0]['maintenance_EUR'])*disc).sum()/1e6))
            if block==12 and seed==20260913:
                saved[pid]=delta
                for case,r in zip(['conventional','electric'],profiles):
                    p=r['profile']
                    for i,y in enumerate(years):
                        annual_rows.append(dict(condition_id=pid,case=case,year=y,output_t=r['output_t'][i],
                            capex_EUR=r['capital'].cash_payments[i],terminal_EUR=r['capital'].terminal_receipt.sum(axis=0)[i],
                            maintenance_EUR=r['maintenance_EUR'][i],power_MWh=p.grid_mwh[i],
                            naphtha_t=p.additional_commodity_flows[0].quantity[i],
                            methane_purchased_MWh=p.additional_commodity_flows[1].quantity[i],methane_export_signed_MWh=p.additional_commodity_flows[2].quantity[i]))
    df=pd.DataFrame(results);df.to_csv(out/'conditional_metrics.csv',index=False)
    pd.DataFrame(annual_rows).to_csv(out/'annual_cash.csv',index=False);np.savez_compressed(out/'incremental_cost_draws.npz',**saved)
    invariance=[]
    for keys,g in df.groupby(['block','seed','recovery']):
        spread=float(g.tcar95.max()-g.tcar95.min());assert spread<1e-8
        invariance.append(dict(block=int(keys[0]),seed=int(keys[1]),recovery=float(keys[2]),TCaR_spread=spread,ES_range=float(g.es95.max()-g.es95.min())))
    (out/'translation_checks.json').write_text(json.dumps(invariance,indent=2)+'\n')
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf';font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':10,'axes.unicode_minus':False})
    v=df.query('block==12 and seed==20260913 and recovery==1 and maintenance_scale==1')
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    for terminal,color,label in [('none','#b36538','잔존가치 없음'),('straight_line_proxy','#24698d','직선 잔존가치 대용치')]:
        a=v[v.terminal==terminal].sort_values('electric_life')
        axes[0].plot(a.electric_life,a.es95,'o-',color=color,label=label)
        axes[1].plot(a.electric_life,a.tcar95,'o-',color=color,label=label)
    axes[0].set(title='수명·잔존가치는 꼬리 비용 수준을 바꾼다',ylabel='증분 비용 ES95 (백만 EUR2019 가정)',xlabel='전기화 플랜트 수명 가정 (년)',xticks=[20,30]);axes[0].legend(fontsize=8)
    axes[1].set(title='동일한 확정 비용 이동에는 TCaR가 불변',ylabel='TCaR95 (백만 EUR2019 가정)',xlabel='전기화 플랜트 수명 가정 (년)',xticks=[20,30])
    axes[1].set_ylim(0,float(v.tcar95.max())*1.2)
    axes[1].ticklabel_format(axis='y',style='plain',useOffset=False)
    axes[1].text(25,float(v.tcar95.max())+35,f'{v.tcar95.iloc[0]:,.3f}',ha='center',fontsize=10)
    fig.suptitle('같은 생산량·가격 표본의 조건부 비교: 기업 관측·최적 frontier가 아님',fontsize=10)
    fig.savefig(out/'capital_and_tail_level.png',dpi=180);plt.close(fig)
    report=dict(conditions=len(df),FIN_cost_values_checked=values_checked,max_FIN_error_million_EUR=max_error,
        max_paired_error_million_EUR=max_pair_error,translation_groups=len(invariance),independent_draw_pools=4,
        assumptions=dict(years=years,scenario='IEA2025STEPS ratios only',hours=8000,capacity_t_hour=115,
            power_anchor_EUR2019_MWh=100,methane_netback_EUR2019_sourceMWh=40,naphtha_EUR2019_t=600,
            power_gas_index_share=.5,discount=.05,base_life=30,electric_life=[20,30],steam_usable_fraction=[.8,1],
            maintenance='source annualized-capital formula; decimal and literal-percent interpretations separate',
            zero_renewal_downtime=True,prices_are_research_assumptions=True,numerical_KRW_per_EUR=fx),
        limits=['Lumped steam-grade closure is assumption, not verified engineering','New plants, not incumbent retrofit',
            'Carbon,labour,working capital,tax,financing and nonmethane coproduct sales omitted',
            'Auxiliary boiler treated additional to plant curve; boundary needs site reconciliation',
            'No company calibration,no abatement feasibility or frontier claim','No future probability validation'],
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,histfile,curvefile,ROOT/'src/cap/reference_ncc.py',Path(__file__)]})
    report['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='manifest.json'}
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['conditions','FIN_cost_values_checked','max_FIN_error_million_EUR','max_paired_error_million_EUR']}))
    print(v[['electric_life','terminal','mean','es95','tcar95']].to_string(index=False))


if __name__=='__main__':main()
