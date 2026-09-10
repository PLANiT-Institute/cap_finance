"""Enumerate one-block commodity/FX costs; no Monte Carlo sampling.

Uniform historical-block support is a declared research distribution, not an
estimated probability of future scenarios. Unit monthly foreign purchases only.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from research_block_price_paths import log_mean_exp,expected_shortfall

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/ecb_fx_reference'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def summary(x):
    q=np.quantile(x,[.5,.95],method='inverted_cdf')
    return dict(mean=float(np.mean(x)),p50=float(q[0]),p95=float(q[1]),
                upper_gap95=float(q[1]-q[0]),es95=expected_shortfall(x))

def main():
    inp=OUT/'aligned_commodity_fx_returns.csv'
    h=pd.read_csv(inp,index_col='period');r=h.to_numpy();r-=r.mean(axis=0)
    length=12;n=len(r)-length+1
    ix=np.arange(n)[:,None]+np.arange(length)
    logs=r[ix].cumsum(axis=1)
    mult=np.exp(logs-log_mean_exp(logs,axis=0))
    np.testing.assert_allclose(mult.mean(axis=0),1.,atol=2e-15)
    rows=[];moments=[];arrays={'multipliers':mult,'window_indices':ix}
    for commodity in ['brent','japan_lng','iron_ore']:
        p=mult[:,:,h.columns.get_loc(commodity)]
        for currency in ['KRW','JPY']:
            f=mult[:,:,h.columns.get_loc(f'fx_{currency}_per_USD')]
            joint=(p*f).mean(axis=1)
            independent=(p[:,None,:]*f[None,:,:]).mean(axis=2).reshape(-1)
            shortcut=p.mean(axis=1)*f.mean(axis=1)
            cov=((p-1)*(f-1)).mean(axis=0)
            np.testing.assert_allclose(joint.mean(),1+cov.mean(),atol=1e-14)
            np.testing.assert_allclose(independent.mean(),1.,atol=1e-14)
            for method,cost in [('same_historical_block',joint),('independent_block_pairs',independent)]:
                rows.append(dict(commodity=commodity,currency=currency,method=method,
                    exact_support_size=len(cost),**summary(cost),
                    theoretical_mean=1+cov.mean() if method=='same_historical_block' else 1.))
                arrays[f'{commodity}_{currency}_{method}']=cost
            moments.append(dict(commodity=commodity,currency=currency,
                historical_return_correlation=float(h[[commodity,f'fx_{currency}_per_USD']].corr().iloc[0,1]),
                correct_monthly_product_mean=float(joint.mean()),
                wrong_product_of_annual_means=float(shortcut.mean()),
                average_within_path_monthly_covariance=float((joint-shortcut).mean()),
                largest_path_aggregation_error=float(np.max(abs(joint-shortcut))),
                average_cross_state_monthly_covariance=float(cov.mean())))
    pd.DataFrame(rows).to_csv(OUT/'exact_block_conversion_metrics.csv',index=False)
    pd.DataFrame(moments).to_csv(OUT/'conversion_moment_checks.csv',index=False)
    eur=mult[:,:,h.columns.get_loc('fx_EUR_per_USD')]
    krw=mult[:,:,h.columns.get_loc('fx_KRW_per_USD')]
    jpy=mult[:,:,h.columns.get_loc('fx_JPY_per_USD')]
    k_e=krw/eur;k_j=krw/jpy;j_e=jpy/eur
    np.testing.assert_allclose(k_j*j_e,k_e,rtol=1e-14)
    crosses=[]
    for name,x in [('USD_per_KRW',1/krw),('USD_per_JPY',1/jpy),('KRW_per_EUR',k_e),('KRW_per_JPY',k_j)]:
        for month in [1,12]:crosses.append(dict(derived_quote_multiplier=name,month=month,exact_mean=float(x[:,month-1].mean()),
            renormalized=False,scope='cross of normalized USD-basis quotes; central crosses derived from the same basis'))
    pd.DataFrame(crosses).to_csv(OUT/'derived_cross_moments.csv',index=False)
    np.savez_compressed(OUT/'exact_block_arrays.npz',**arrays)
    meta=dict(analysis='exact one-year block enumeration; not company TCaR',
        block_length=12,support_size=n,joint_states=n,independent_states=n*n,
        months=12,source_return_rows=191,MC_draws=0,random_seed=None,
        monthly_quantity='one normalized purchased unit each month; arithmetic annual average',
        marginal_anchor='each USD-basis FX and USD commodity multiplier has exact mean one each month',
        converted_cost_anchor='product expectation retained; no ex-post mean recentering',
        quantile_method='empirical inverse CDF',ES='integrated quantile with fractional boundary mass',
        real_currency_conversion=False,scenario_forecast=False,corporate_calibration=False,
        FIN_or_Excel_changed=False,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [inp,OUT/'manifest.json',ROOT/'scripts/research_block_price_paths.py']},
        artifact_sha256={str(p.relative_to(ROOT)):sha(p) for p in [OUT/'exact_block_conversion_metrics.csv',OUT/'conversion_moment_checks.csv',OUT/'derived_cross_moments.csv',OUT/'exact_block_arrays.npz',Path(__file__)]})
    (OUT/'experiment_manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(pd.DataFrame(rows)[['commodity','currency','method','mean','es95']].to_string(index=False))
    print(pd.DataFrame(moments).to_string(index=False))

if __name__=='__main__':main()
