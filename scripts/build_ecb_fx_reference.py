"""ECB nominal FX references and a calendar-aligned commodity/FX research panel.

USD-based quotes span the currencies; derived crosses are not independent factors.
No company contract, future FX forecast, inflation path or MC calibration is inferred.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'tmp/pdfs/tcar_research_v2/ecb_fx'
OUT=ROOT/'data/research_v2/ecb_fx_reference'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with ZipFile(RAW/'eurofxref-hist.zip') as z:
        assert z.read('eurofxref-hist.csv')==(RAW/'eurofxref-hist.csv').read_bytes()
    source=pd.read_csv(RAW/'eurofxref-hist.csv',usecols=['Date','USD','JPY','KRW'])
    assert not source.Date.duplicated().any()
    source=source.sort_values('Date')
    d=source.query("'2010-01-01' <= Date <= '2025-12-31'").copy()
    assert d[['USD','JPY','KRW']].notna().all().all()
    assert (d[['USD','JPY','KRW']]>0).all().all()
    d=d.rename(columns={'USD':'USD_per_EUR','JPY':'JPY_per_EUR','KRW':'KRW_per_EUR'})
    d['EUR_per_USD']=1/d.USD_per_EUR
    d['KRW_per_USD']=d.KRW_per_EUR/d.USD_per_EUR
    d['JPY_per_USD']=d.JPY_per_EUR/d.USD_per_EUR
    d['KRW_per_JPY']=d.KRW_per_EUR/d.JPY_per_EUR
    d['period']=d.Date.str[:4]+'M'+d.Date.str[5:7]
    d.to_csv(OUT/'selected_daily_rates.csv',index=False)
    basis=['EUR_per_USD','KRW_per_USD','JPY_per_USD']
    m=d.groupby('period')[basis].mean()
    m['observed_days']=d.groupby('period').size()
    assert len(m)==192
    m.to_csv(OUT/'monthly_USD_basis.csv')
    # The ratio of two monthly means need not equal the mean daily cross.
    cross=d.groupby('period')[['KRW_per_EUR','KRW_per_JPY']].mean()
    rows=[]
    for pair,denom in [('KRW_per_EUR','EUR_per_USD'),('KRW_per_JPY','JPY_per_USD')]:
        implied=m.KRW_per_USD/m[denom]
        for period in m.index:
            rows.append(dict(period=period,pair=pair,mean_daily_cross=cross.loc[period,pair],
                ratio_monthly_USD_basis=implied.loc[period],
                relative_difference=implied.loc[period]/cross.loc[period,pair]-1))
    pd.DataFrame(rows).to_csv(OUT/'aggregation_order_diagnostic.csv',index=False)
    r=np.log(m[basis]).diff().iloc[1:]
    r=r.rename(columns={c:'fx_'+c for c in basis})
    wbpath=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    wb=pd.read_csv(wbpath,index_col='period')
    assert r.index.equals(wb.index) and r.shape==(191,3)
    joined=wb.join(r,validate='one_to_one')
    assert joined.shape==(191,9) and np.isfinite(joined).all().all()
    joined.to_csv(OUT/'aligned_commodity_fx_returns.csv')
    joined.corr().to_csv(OUT/'historical_return_correlation.csv')
    annual=d.groupby(d.Date.str[:4])[['EUR_per_USD','KRW_per_USD','JPY_per_USD','KRW_per_EUR','KRW_per_JPY']].mean()
    annual.index.name='calendar_year'
    annual.to_csv(OUT/'annual_mean_daily_quotes.csv')
    meta=dict(source_url='https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip',
        framework_url='https://www.ecb.europa.eu/stats/pdf/exchange/Frameworkfortheeuroforeignexchangereferencerates.en.pdf',
        downloaded_on='2026-09-09',raw_latest_date=source.Date.max(),
        diagnostic_window=['2010-01-01','2025-12-31'],native_daily_rows=len(d),native_daily_cells=3*len(d),
        monthly_levels=192,monthly_returns=191,commodity_factors=6,spanning_FX_factors=3,
        quote_unit='nominal numerator currency units per one denominator currency',
        raw_basis='ECB USD, JPY, KRW units per EUR',
        monthly_basis='same observed days; arithmetic mean of daily USD-based cross rates; no weekend forward fill',
        within_month_commodity_FX_dependence_identified=False,
        company_purchase_or_settlement_rates=False,future_FX_or_inflation_scenarios=False,
        legacy_FIN_Excel_inputs_modified=False,
        limits=['ECB references are informational, not transaction quotes',
                'WB monthly benchmark and ECB fixing coverage differ; product of monthly averages is a proxy',
                'Derived monthly crosses preserve algebra but differ from average daily crosses',
                'Post2025 rates are preserved in raw source but excluded from diagnostic panel',
                'Use a spanning FX basis and derive inverses/crosses on each simulated date and path',
                'Nominal FX alone does not convert a foreign real-price path into domestic real prices',
                'Historical return dependence is not a forecast-error law or company invoice exposure'],
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [RAW/'eurofxref-hist.zip',RAW/'eurofxref-hist.csv',RAW/'framework.pdf',wbpath]},
        artifact_sha256={str((OUT/name).relative_to(ROOT)):sha(OUT/name) for name in [
            'selected_daily_rates.csv','monthly_USD_basis.csv','aggregation_order_diagnostic.csv',
            'aligned_commodity_fx_returns.csv','historical_return_correlation.csv','annual_mean_daily_quotes.csv']})
    meta['artifact_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    (OUT/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps({k:v for k,v in meta.items() if k not in ['limits','source_sha256','artifact_sha256']},indent=2))
    print(annual.tail(2).to_string())

if __name__=='__main__':main()
