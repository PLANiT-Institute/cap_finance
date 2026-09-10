"""Conditional Monte Carlo error for the displayed Japan-LNG tail experiment.

Bootstrap entire simulated paths, not months or historical calibration rows.
This measures finite-simulation error conditional on the fitted mechanism only.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/block_price_paths'


def main():
    meta=json.loads((OUT/'manifest.json').read_text())
    index=meta['factors'].index('japan_lng')
    rng=np.random.default_rng(20260908)
    rows=[]
    with np.load(OUT/'annual_multipliers.npz') as data:
        for model in meta['models']:
            x=data[model][:,4,index]
            n=len(x); mass=.05*n; k=int(mass)
            point=np.quantile(x,[.5,.9,.95]);sx=np.sort(x)
            es=(sx[-k:].sum()+(mass-k)*sx[-k-1])/mass
            stats=[]
            for _ in range(400):
                sample=np.sort(x[rng.integers(0,n,size=n)])
                q=np.quantile(sample,[.5,.9,.95])
                tail=(sample[-k:].sum()+(mass-k)*sample[-k-1])/mass
                stats.append([q[0],q[2],q[1]-q[0],tail])
            lo,hi=np.quantile(stats,[.025,.975],axis=0)
            for j,(name,value) in enumerate(zip(['p50','p95','upper_gap90','es95'],[point[0],point[2],point[1]-point[0],es])):
                rows.append(dict(model=model,series='japan_lng',year_index=5,metric=name,value=value,
                                 mc_percentile_lower95=lo[j],mc_percentile_upper95=hi[j],
                                 bootstrap_replicates=400,seed=20260908,
                                 scope='simulation path resampling only; no historical calibration or model uncertainty'))
    pd.DataFrame(rows).to_csv(OUT/'displayed_tail_mc_intervals.csv',index=False)
    print(pd.DataFrame(rows).query('metric == "es95"')[['model','value','mc_percentile_lower95','mc_percentile_upper95']].to_string(index=False))


if __name__=='__main__':main()
