"""Independent raw CSV, FX algebra, block enumeration and cost-metric verification."""
from pathlib import Path
from fractions import Fraction as F
import csv,hashlib,json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/ecb_fx_reference'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    for name in ['manifest.json','experiment_manifest.json']:
        manifest=json.loads((OUT/name).read_text())
        for group in ['source_sha256','artifact_sha256']:
            for path,h in manifest[group].items():assert sha(ROOT/path)==h,path
    with (ROOT/'tmp/pdfs/tcar_research_v2/ecb_fx/eurofxref-hist.csv').open() as f:
        raw={r['Date']:r for r in csv.DictReader(f) if '2010-01-01'<=r['Date']<='2025-12-31'}
    d=pd.read_csv(OUT/'selected_daily_rates.csv')
    assert len(d)==len(raw)==4097
    for r in d.itertuples():
        x=raw[r.Date]
        for currency in ['USD','JPY','KRW']:assert getattr(r,currency+'_per_EUR')==float(x[currency])
        usd,jpy,krw=[F(x[c]) for c in ['USD','JPY','KRW']]
        for name,expected in [('EUR_per_USD',1/usd),('KRW_per_USD',krw/usd),('JPY_per_USD',jpy/usd),('KRW_per_JPY',krw/jpy)]:
            assert abs(getattr(r,name)-float(expected))<1e-9
    columns=['EUR_per_USD','KRW_per_USD','JPY_per_USD']
    monthly=pd.read_csv(OUT/'monthly_USD_basis.csv',index_col='period')
    for period,r in monthly.iterrows():
        days=d[d.period==period];assert len(days)==r.observed_days
        for c in columns:assert abs(sum(days[c])/len(days)-r[c])<1e-9
    joined=pd.read_csv(OUT/'aligned_commodity_fx_returns.csv',index_col='period')
    wb=pd.read_csv(ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv',index_col='period')
    np.testing.assert_allclose(joined[wb.columns],wb,rtol=0,atol=0)
    expected=np.log(monthly[columns].to_numpy()[1:]/monthly[columns].to_numpy()[:-1])
    np.testing.assert_allclose(joined[['fx_'+c for c in columns]],expected,atol=3e-15)
    # Build windows independently with sequential accumulation; no sampler import.
    data=joined.to_numpy();means=data.mean(axis=0);rawlevels=np.zeros((180,12,9))
    for start in range(180):
        acc=np.zeros(9)
        for month in range(12):
            acc+=data[start+month]-means;rawlevels[start,month]=np.exp(acc)
    levels=rawlevels/(sum(rawlevels)/180)
    metrics=pd.read_csv(OUT/'exact_block_conversion_metrics.csv')
    with np.load(OUT/'exact_block_arrays.npz') as saved:
        np.testing.assert_allclose(saved['multipliers'],levels,rtol=1e-13,atol=1e-13)
        cellcount=0
        for commodity in ['brent','japan_lng','iron_ore']:
            p=levels[:,:,joined.columns.get_loc(commodity)]
            for currency in ['KRW','JPY']:
                f=levels[:,:,joined.columns.get_loc(f'fx_{currency}_per_USD')]
                for mode in ['same_historical_block','independent_block_pairs']:
                    if mode=='same_historical_block':x=sum((p*f).T)/12
                    else:x=np.concatenate([sum((pi*f).T)/12 for pi in p])
                    np.testing.assert_allclose(saved[f'{commodity}_{currency}_{mode}'],x,rtol=1e-13)
                    cellcount+=len(x)
                    sx=sorted(x);n=len(sx);q50=sx[(n+1)//2-1];q95=sx[int(np.ceil(.95*n))-1]
                    # Both support sizes are divisible by 20; exact upper5% mean.
                    es=sum(sx[-(n//20):])/(n//20)
                    row=metrics.query('commodity==@commodity and currency==@currency and method==@mode').iloc[0]
                    np.testing.assert_allclose([row['mean'],row.p50,row.p95,row.upper_gap95,row.es95],
                        [sum(x)/n,q50,q95,q95-q50,es],rtol=1e-12)
                    assert abs(row.theoretical_mean-sum(x)/n)<1e-12
    # A non-degenerate FX quote and its inverse cannot both have mean multiplier1.
    f=[F(1,2),F(3,2)];inverse=[1/x for x in f];meaninv=sum(inverse)/2
    assert sum(f)/2==1 and meaninv==F(4,3)
    normalized_inverse=[x/meaninv for x in inverse]
    assert [a*b for a,b in zip(f,normalized_inverse)]==[F(3,4)]*2
    note=(ROOT/'paper/methodology/FX_JOINT_CONVERSION_KO.md').read_text()
    printed=0
    for commodity in ['brent','japan_lng','iron_ore']:
        for currency in ['KRW','JPY']:
            sub=metrics.query('commodity==@commodity and currency==@currency').set_index('method')
            values=[sub.loc['same_historical_block','mean'],sub.loc['independent_block_pairs','mean'],
                    sub.loc['same_historical_block','es95'],sub.loc['independent_block_pairs','es95']]
            assert ' | '.join(f'{v:.6f}' for v in values) in note
            printed+=4
    year=d[d.Date.str.startswith('2025')]
    for c in ['KRW_per_USD','JPY_per_USD','KRW_per_EUR']:
        assert f'{year[c].mean():,.6f}' in note;printed+=1
    wb=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
    assert sha(wb)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
    report=dict(all_passed=True,native_FX_cells_checked=12291,daily_cross_values_checked=16388,
        monthly_basis_values_checked=576,FX_return_values_checked=573,legacy_commodity_returns_preserved=1146,
        enumerated_multiplier_values_checked=19440,enumerated_cost_values_checked=cellcount,
        cost_metrics_checked=72,printed_values_checked=printed,
        mean_inverse_counterexample=str(meaninv),renormalized_reciprocal_product='3/4',
        new_MC_draws=0,Excel_v6_unchanged=True,company_calibration=False)
    report['artifact_sha256']={str(p.relative_to(ROOT)):sha(p) for p in [OUT/'manifest.json',OUT/'experiment_manifest.json',
        OUT/'fx_joint_conversion.png',ROOT/'paper/methodology/FX_JOINT_CONVERSION_KO.md',
        ROOT/'scripts/plot_fx_joint_conversion.py',Path(__file__)]}
    (ROOT/'docs/research_cycles/2026-09-07-hourly/completion_26_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='artifact_sha256'}))

if __name__=='__main__':main()
