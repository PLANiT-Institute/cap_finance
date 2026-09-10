"""Isolate pellet benchmark loading and dependence at identical steel output.

This extends a published reference cost ledger; beta is an uncalibrated mapping
assumption, not a hedge decision. Whole-path permutations preserve every sampled
ore trajectory and its marginal distribution, while changing energy/ore pairing.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cap import config as C
from cap.reference_steel import build_vogl_reference_profile
from cap.plancost import simulate_cost
from cap.risk_metrics import loss_summary
from cap.tail_attribution import tail_decomposition
from cap.scenario_prices import ScenarioPriceCurve, interpolate_curve
from research_block_price_paths import block_paths, expected_shortfall

OUT = ROOT / 'data/research_v2/steel_procurement_tail'
SEEDS = [20260923, 20260924]
N, PERMUTATIONS, ALPHA = 5000, 200, .95
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    package_file = ROOT / 'data/research_v2/steel_cost_reference/vogl_main_text_package.json'
    history_file = ROOT / 'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    curve_file = ROOT / 'data/research_v2/iea_2025_scenarios/curves.json'
    evidence_file = OUT/'source_register.json'
    evidence = json.loads(evidence_file.read_text())
    assert sha(ROOT/evidence['midrex']['local_path']) == evidence['midrex']['sha256']
    package = json.loads(package_file.read_text())
    assert sha(ROOT / package['source']['local_path']) == package['source']['sha256']
    assert sha(history_file) == json.loads((ROOT / 'data/research_v2/block_price_paths/manifest.json').read_text())['source_sha256']
    hist = pd.read_csv(history_file).set_index('period')
    assert hist.shape == (191, 6)
    years = tuple(range(2027, 2051));T = len(years);fx = 1500.;disc = 1.05**-np.arange(T)
    curves = [ScenarioPriceCurve(**r) for r in json.loads(curve_file.read_text())]
    gas = next(c for c in curves if c.scenario == 'STEPS' and c.commodity == 'natural_gas' and c.region == 'Japan')
    ratio = np.array(interpolate_curve(gas, years, method='linear').values) / gas.values[0]
    central_power = 40*(.5+.5*ratio)
    reference = build_vogl_reference_profile(package, years, capacity_t_per_year=1e6,
        annual_utilization=np.full(T, .75), adopt_year=2027, build_years=3,
        numerical_KRW_per_source_EUR=fx, oxygen_sale_fraction=.6, direct_emission_factor_tco2_per_t=0.)
    profile = reference.profile;output = reference.output_t
    np.testing.assert_array_equal(output, np.r_[np.zeros(3),np.full(21,750000.)])
    # Independent native-unit cash schedule, not copied from the profile arrays.
    cap = np.zeros(T);cap[:3] = 574e6/3;cap[13] = 160e6;cap[23] = 574e6
    fixed = cap + output*(.05*100+.011*1777+.002*4000+53.2-.411*.6*60.8)
    fixed += (np.array(years)>=2030)*1e6*574*.03
    fixed_npv = float(fixed @ disc / 1e6)
    theory = float((fixed+output*(3.48*central_power+1.504*100)) @ disc / 1e6)
    prices = {k:np.zeros(T) for k in ['elec','re','h2','co2','coal','gas']}
    prices['elec'] = central_power*fx
    for item in package['purchases']: prices[item['flow_id']] = np.full(T,item['price_EUR']*fx)
    prices['oxygen_netback'] = np.full(T,60.8*fx)
    cfg = C.load(discount_rate=.05,carbon_accounting_mode='gross_obligation_proxy')
    cfg['years'] = {'start':2027,'end':2050}
    risk, allocated, permutations, dependence, arrays = [], [], [], [], {}
    max_error = 0.
    for seed in SEEDS:
        monthly, anchors, starts = block_paths(hist.to_numpy(),T*12,N,12,seed)
        annual = monthly.reshape(N,T,12,6).mean(axis=2);del monthly
        g = annual[:,:,hist.columns.get_loc('japan_lng')]
        ore = annual[:,:,hist.columns.get_loc('iron_ore')]
        power = 40*(.5+.5*ratio*g)
        power_npv = (output*3.48*power*disc).sum(axis=1)/1e6
        ore_npv = (output*1.504*100*ore*disc).sum(axis=1)/1e6
        central_ore_npv = float(output @ disc * 1.504*100/1e6)
        rng = np.random.default_rng(seed+1000)
        perm = rng.permutation(N)
        arrays.update({f'power_{seed}':power,f'ore_{seed}':ore,f'permutation_{seed}':perm,
                       f'block_starts_{seed}':starts,f'log_anchors_{seed}':anchors})
        for pairing,ix in [('joint',np.arange(N)),('permuted',perm)]:
            assert np.array_equal(np.sort(ix),np.arange(N))
            dependence.append(dict(seed=seed,pairing=pairing,
                discounted_power_ore_correlation=float(np.corrcoef(power_npv,ore_npv[ix])[0,1])))
            for beta in [0.,.5,1.]:
                ore_mult = (1-beta)+beta*ore[ix]
                shocks = {k:np.ones((N,T)) for k in ['elec','h2','capex','pellets','lime','alloys','graphite_electrodes','oxygen_netback']}
                shocks['elec'] = power/central_power;shocks['pellets'] = ore_mult
                cost = simulate_cost(profile,prices,shocks,{'subsidy':{}},cfg,freeze='capex')*1000/fx
                components = np.column_stack([np.full(N,fixed_npv),power_npv,
                    (1-beta)*central_ore_npv+beta*ore_npv[ix]])
                hand = components.sum(axis=1)
                np.testing.assert_allclose(cost,hand,rtol=2e-13,atol=1e-8)
                max_error = max(max_error,float(np.max(abs(cost-hand))))
                summary = loss_summary(cost,ALPHA)
                risk.append(dict(seed=seed,pairing=pairing,beta=beta,paths=N,
                    theoretical_mean=theory,**summary,excess_ES=summary['es_alpha']-summary['mean']))
                dec = tail_decomposition(components,ALPHA)
                np.testing.assert_allclose(dec['es'],summary['es_alpha'],rtol=1e-12,atol=1e-8)
                for i,name in enumerate(['fixed_other_cash','electricity','pellets']):
                    allocated.append(dict(seed=seed,pairing=pairing,beta=beta,component=name,
                        mean=dec['component_means'][i],ES_contribution=dec['es_contributions'][i],
                        excess_ES_contribution=dec['excess_contributions'][i]))
                arrays[f'cost_{seed}_{pairing}_{beta}'] = cost
        # Paired-trajectory randomization distribution, NOT a predictive CI.
        for rep in range(PERMUTATIONS):
            ix = rng.permutation(N)
            for beta in [.5,1.]:
                v = fixed_npv+power_npv+(1-beta)*central_ore_npv+beta*ore_npv[ix]
                permutations.append(dict(seed=seed,beta=beta,permutation=rep,
                    mean=float(v.mean()),es_alpha=expected_shortfall(v,ALPHA),
                    tcar=float(np.quantile(v,ALPHA)-np.median(v))))
    risk = pd.DataFrame(risk);alloc = pd.DataFrame(allocated);perms = pd.DataFrame(permutations)
    risk.to_csv(OUT/'conditional_risk.csv',index=False)
    alloc.to_csv(OUT/'tail_allocation.csv',index=False)
    perms.to_csv(OUT/'pairing_randomization.csv',index=False)
    pd.DataFrame(dependence).to_csv(OUT/'dependence.csv',index=False)
    pd.DataFrame(dict(year=years,output_t=output,fixed_cash_EUR=fixed,central_power=central_power,
        pellet_t=output*1.504,grid_MWh=output*3.48,discount=disc)).to_csv(OUT/'annual_ledger.csv',index=False)
    np.savez_compressed(OUT/'paths.npz',**arrays)
    font = ROOT/'tmp/pdfs/methodology/Heading.ttf';font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':10,'axes.unicode_minus':False})
    fig,axes = plt.subplots(1,3,figsize=(13,4.3),layout='constrained')
    for seed,color in zip(SEEDS,['#236997','#b35a26']):
        q=risk[(risk.seed==seed)&(risk.pairing=='joint')]
        axes[0].plot(q.beta,q.es_alpha,marker='o',color=color,label=f'표본 {SEEDS.index(seed)+1}: ES95')
        axes[0].plot(q.beta,q['mean'],ls=':',color=color)
    axes[0].set(xlabel='펠릿 가격의 철광석 지수 연동 비중 β (가정)',ylabel='절대 비용 NPV (백만 원문 EUR)',title='같은 기대가격, 다른 꼬리 비용',xticks=[0,.5,1]);axes[0].legend(fontsize=8)
    view=alloc[(alloc.seed==SEEDS[0])&(alloc.pairing=='joint')]
    x=np.arange(3);bottom=np.zeros(3)
    for component,color,label in [('electricity','#236997','전력'),('pellets','#59a398','펠릿')]:
        v=view[view.component==component].sort_values('beta').excess_ES_contribution.to_numpy()
        axes[1].bar(x,v,bottom=bottom,color=color,label=label);bottom+=v
    axes[1].set(xticks=x,xticklabels=['0','0.5','1'],xlabel='β (표본 1)',ylabel='ES95 - 표본 평균 기여 (백만 원문 EUR)',title='같은 비용 꼬리에서 항목별 분해');axes[1].legend(fontsize=8)
    for i,seed in enumerate(SEEDS):
        sub=perms[(perms.seed==seed)&(perms.beta==1)]
        lo,mid,hi=np.quantile(sub.es_alpha,[.025,.5,.975])
        actual=float(risk[(risk.seed==seed)&(risk.beta==1)&(risk.pairing=='joint')].es_alpha.iloc[0])
        axes[2].plot([i,i],[lo,hi],lw=5,color='#abb6be');axes[2].scatter(i,mid,c='#526471',marker='_',s=90)
        axes[2].scatter(i,actual,c='#b35a26',s=55,zorder=3)
    axes[2].set(xticks=[0,1],xticklabels=['표본 1','표본 2'],ylabel='ES95 (백만 원문 EUR)',title='β=1: 원래 공동 연결과 경로 재배열')
    fig.suptitle('철강 참조: 원료 구매가격 연결을 식별해야 위험 기여도도 해석할 수 있다',fontsize=12)
    fig.supxlabel('점선: 표본 평균 · 회색: 200회 경로 순열의 2.5-97.5% 구간 · 주황점: 원래 공동 연결\n동일 생산·물량의 가정 민감도. 기업 증분 TCaR·효율경계·미래 예측구간이 아님.',fontsize=8)
    fig.savefig(OUT/'pellet_basis_and_tail.png',dpi=180);plt.close(fig)
    sources=[package_file,history_file,curve_file,evidence_file,ROOT/evidence['midrex']['local_path'],
             ROOT/'data/research_v2/price_history/source_series_descriptions.csv',Path(__file__),
             ROOT/'src/cap/tail_attribution.py',ROOT/'src/cap/reference_steel.py',ROOT/'src/cap/plancost.py',
             ROOT/'scripts/research_block_price_paths.py']
    manifest=dict(reference='Vogl2018 source-native cost ledger',scope='absolute process cash cost; no incumbent comparator or emissions feasibility',
        paths_per_seed=N,seeds=SEEDS,block_length=12,years=years,alpha=ALPHA,betas=[0,.5,1],
        FIN_cost_checks=len(risk)*N,max_independent_FIN_error=max_error,
        risk_rows=len(risk),allocation_rows=len(alloc),randomization_rows=len(perms),
        pellet_mapping='100*((1-beta)+beta*iron_ore_multiplier); beta is unestimated, premium residual held fixed',
        energy_mapping='40*(0.5+0.5*IEA2025_STEPS_Japan_LNG_ratio*LNG_multiplier)',
        historical_monthly_ore_LNG_correlation=float(hist[['iron_ore','japan_lng']].corr().iloc[0,1]),
        pairing_diagnostic='200 whole-trajectory permutations per seed; exact sampled marginals preserved; not a predictive or parameter confidence interval',
        limitations=['No company procurement or pellet basis calibration','No independent pellet-premium volatility','Uniform real price year unresolved in source package','No coking coal or scrap mapping','No annual emissions qualification','beta changes are assumptions, not selectable contracts','No full corporate transition TCaR or frontier'],
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
    generated=['conditional_risk.csv','tail_allocation.csv','pairing_randomization.csv',
               'dependence.csv','annual_ledger.csv','paths.npz','pellet_basis_and_tail.png']
    manifest['artifact_sha256']={str((OUT/name).relative_to(ROOT)):sha(OUT/name) for name in generated}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(risk[['seed','pairing','beta','mean','es_alpha','tcar']].to_string(index=False))
    print('FIN checks',manifest['FIN_cost_checks'],'max error',max_error)


if __name__=='__main__':main()
