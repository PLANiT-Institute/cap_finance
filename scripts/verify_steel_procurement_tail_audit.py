"""Independently rebuild saved price paths, cash costs and tail accounting.

No imports of the production price, FIN, or risk routines. The sorted worst-250
observations suffice for this experiment's integer tail mass; generic fractional
and tied boundaries are checked separately in test_tail_attribution.py.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/research_v2/steel_procurement_tail'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
close = lambda a,b: np.testing.assert_allclose(a,b,rtol=2e-12,atol=1e-8)


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    for group in ['input_sha256','artifact_sha256']:
        for path,digest in manifest[group].items(): assert sha(ROOT/path)==digest,path
    history=pd.read_csv(ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv').set_index('period')
    raw=history.to_numpy(); centered=raw-raw.mean(axis=0)
    curves=json.loads((ROOT/'data/research_v2/iea_2025_scenarios/curves.json').read_text())
    curve=next(c for c in curves if c['commodity']=='natural_gas' and c['region']=='Japan' and c['scenario']=='STEPS')
    years=np.arange(2027,2051);disc=1.05**-np.arange(24)
    ratio=np.interp(years,curve['years'],curve['values'])/curve['values'][0]
    output=np.where(years<2030,0.,750000.)
    cap=np.array([574e6/3 if y<2030 else 160e6 if y==2040 else 574e6 if y==2050 else 0. for y in years])
    fixed=cap+output*(5+19.547+8+53.2-14.99328)+(years>=2030)*17220000
    central_power=40*(.5+.5*ratio)
    ledger=pd.read_csv(OUT/'annual_ledger.csv')
    for k,v in dict(year=years,output_t=output,fixed_cash_EUR=fixed,central_power=central_power,
                    pellet_t=output*1.504,grid_MWh=output*3.48,discount=disc).items(): close(ledger[k],v)
    fixed_npv=fixed@disc/1e6; central_ore=output@disc*150.4/1e6
    theoretical=fixed_npv+(output*3.48*central_power)@disc/1e6+central_ore
    draws=np.load(OUT/'paths.npz');risk=pd.read_csv(OUT/'conditional_risk.csv')
    allocations=pd.read_csv(OUT/'tail_allocation.csv');randomized=pd.read_csv(OUT/'pairing_randomization.csv')
    correlations=pd.read_csv(OUT/'dependence.csv')
    cost_checks=0; metric_checks=0; allocation_checks=0; randomized_checks=0
    for seed in manifest['seeds']:
        starts=draws[f'block_starts_{seed}'];assert starts.shape==(5000,24)
        np.testing.assert_array_equal(starts,np.random.default_rng(seed).integers(0,180,(5000,24)))
        reconstructed={}
        # Explicit finite-support expectation: each new block multiplies the
        # full-block expectation and the current within-block partial moment.
        for factor in ['japan_lng','iron_ore']:
            j=history.columns.get_loc(factor)
            windows=np.stack([centered[i:i+12,j] for i in range(180)])
            moments=np.exp(windows.cumsum(axis=1)).mean(axis=0)
            log_anchor=np.array([h//12*np.log(moments[-1])+np.log(moments[h%12]) for h in range(288)])
            close(log_anchor,draws[f'log_anchors_{seed}'][:,j])
            levels=np.exp(windows[starts].reshape(5000,288).cumsum(axis=1)-log_anchor)
            reconstructed[factor]=levels.reshape(5000,24,12).mean(axis=2)
        power=40*(.5+.5*ratio*reconstructed['japan_lng']);ore=reconstructed['iron_ore']
        close(power,draws[f'power_{seed}']);close(ore,draws[f'ore_{seed}'])
        power_npv=(output*3.48*power)@disc/1e6;ore_npv=(output*150.4*ore)@disc/1e6
        rng=np.random.default_rng(seed+1000);first=rng.permutation(5000)
        np.testing.assert_array_equal(first,draws[f'permutation_{seed}'])
        for pairing,ix in [('joint',np.arange(5000)),('permuted',first)]:
            # Invert the permutation: every entire 24-year trajectory retained.
            np.testing.assert_array_equal(ore[ix][np.argsort(ix)],ore)
            corr=correlations.query('seed==@seed and pairing==@pairing').iloc[0]
            close(corr.discounted_power_ore_correlation,np.corrcoef(power_npv,ore_npv[ix])[0,1])
            for beta in [0.,.5,1.]:
                components=np.column_stack([np.full(5000,fixed_npv),power_npv,(1-beta)*central_ore+beta*ore_npv[ix]])
                costs=components.sum(axis=1);saved=draws[f'cost_{seed}_{pairing}_{beta}']
                close(costs,saved);cost_checks+=len(costs)
                row=risk.query('seed==@seed and pairing==@pairing and beta==@beta').iloc[0]
                tail=np.argsort(costs)[-250:];es=costs[tail].mean()
                stats=dict(mean=costs.mean(),p50=np.median(costs),q_alpha=np.quantile(costs,.95),
                           tcar=np.quantile(costs,.95)-np.median(costs),es_alpha=es,
                           excess_ES=es-costs.mean(),theoretical_mean=theoretical)
                for key,value in stats.items():close(row[key],value);metric_checks+=1
                selected=allocations.query('seed==@seed and pairing==@pairing and beta==@beta')
                for i,name in enumerate(['fixed_other_cash','electricity','pellets']):
                    a=selected[selected.component==name].iloc[0]
                    for key,value in dict(mean=components[:,i].mean(),ES_contribution=components[tail,i].mean(),
                                         excess_ES_contribution=components[tail,i].mean()-components[:,i].mean()).items():
                        close(a[key],value);allocation_checks+=1
                close(selected.ES_contribution.sum(),es)
                close(selected.excess_ES_contribution.sum(),es-costs.mean())
        for rep in range(200):
            ix=rng.permutation(5000)
            for beta in [.5,1.]:
                costs=fixed_npv+power_npv+(1-beta)*central_ore+beta*ore_npv[ix]
                row=randomized.query('seed==@seed and beta==@beta and permutation==@rep').iloc[0]
                for key,value in dict(mean=costs.mean(),es_alpha=np.sort(costs)[-250:].mean(),
                                      tcar=np.quantile(costs,.95)-np.median(costs)).items():
                    close(row[key],value);randomized_checks+=1
    result=dict(passed=True,FIN_path_values_reconstructed=cost_checks,risk_statistics_checked=metric_checks,
                tail_allocation_values_checked=allocation_checks,randomization_values_checked=randomized_checks,
                annual_ledger_values_checked=24*7,annual_price_values_reconstructed=2*2*5000*24,
                generic_fractional_ties_tested_separately=True,predictive_interval=False,
                corporate_calibration=False,frontier_estimated=False,
                manifest_sha256=sha(OUT/'manifest.json'),verifier_sha256=sha(__file__))
    (OUT/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
