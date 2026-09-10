"""Audit official nominal monthly prices before any conditional shock calibration.

Read-only XLSX input. Selected international benchmarks are not company tariffs.
Full history is preserved; diagnostic returns use 2010-2025, excluding estimates.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import numpy as np
from xlsx_table_reader import read_cells

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'tmp/pdfs/tcar_research_v2'
OUT = ROOT / 'data/research_v2/price_history'
SERIES = {
    'Crude oil, Brent': ('brent', 'oil_benchmark_not_naphtha_price'),
    'Coal, Australian': ('thermal_coal_au', 'thermal_coal_not_coking_coal;definition_switch_Feb2022'),
    'Natural gas, US': ('henry_hub', 'US_spot_not_Korea_or_Japan_delivered_gas'),
    'Natural gas, Europe': ('europe_gas', 'TTF_from_Apr2015_prior_definition_differs'),
    'Liquefied natural gas, Japan': ('japan_lng', 'CIF_import_price_recent_two_months_estimated;not_Korea_contract'),
    'Iron ore, cfr spot': ('iron_ore', 'ore_benchmark_not_DRI_grade_pellet_price'),
}


def save(name, rows):
    with (OUT/name).open('w', newline='', encoding='utf-8-sig') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = next(r for r in json.loads((RAW/'wb_download_manifest.json').read_text()) if r['file'].endswith('xlsx'))
    path = RAW/meta['file']; assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']
    sheets=read_cells(path); cells=sheets['Monthly Prices']
    headers={v['value']:c for (r,c),v in cells.items() if r==5 and v['value'] in SERIES}
    assert set(headers)==set(SERIES)
    rows=[]
    for r in range(7, max(r for r,c in cells)+1):
        period=cells.get((r,1),{}).get('value')
        if not isinstance(period,str) or not re.fullmatch(r'\d{4}M\d{2}',period):continue
        assert 1<=int(period[-2:])<=12
        for name,(sid,scope) in SERIES.items():
            c=headers[name]; cell=cells[(r,c)]; v=cell['value']
            assert not cell['error'] and cell['formula'] is None,(period,name)
            missing=v is None or v in ('…','...','')
            assert missing or isinstance(v,(float,int)) and np.isfinite(v) and v>0,(period,name,v)
            rows.append(dict(period=period,series_id=sid,source_name=name,
                value='' if missing else v,unit=cells[(6,c)]['value'],nominal_or_real='nominal_USD',
                is_missing=missing,recent_estimate=sid=='japan_lng' and period>='2026M07',
                scope=scope,sheet='Monthly Prices',source_row=r,source_column=c,
                source_url=meta['url'],source_sha256=meta['sha256'],
                extraction='native_cell_value_no_currency_or_energy_conversion'))
    save('native_monthly_prices.csv',rows)
    # Calendar-aligned vector: no missing values or unequal observation frequencies.
    panel={}
    for r in rows:
        if '2010M01'<=r['period']<='2025M12':
            assert not r['is_missing'],r
            panel.setdefault(r['period'],{})[r['series_id']]=r['value']
    keys=[s[0] for s in SERIES.values()];dates=sorted(panel)
    assert len(dates)==192 and all(len(panel[d])==len(keys) for d in dates)
    assert all(int(d[:4])*12+int(d[-2:])==int(dates[0][:4])*12+1+i for i,d in enumerate(dates))
    values=np.array([[panel[d][k] for k in keys] for d in dates])
    returns=np.diff(np.log(values),axis=0)
    stats=[]
    for j,k in enumerate(keys):
        x=returns[:,j];mean=x.mean();sd=x.std(ddof=1)
        stats.append(dict(series_id=k,n_monthly_returns=len(x),start=dates[1],end=dates[-1],
            mean_monthly_log_return=mean,sd_monthly_log_return=sd,
            q01=float(np.quantile(x,.01)),q05=float(np.quantile(x,.05)),
            q95=float(np.quantile(x,.95)),q99=float(np.quantile(x,.99)),
            skew_moment=float(np.mean(((x-mean)/x.std())**3)),
            excess_kurtosis_moment=float(np.mean(((x-mean)/x.std())**4)-3),
            acf1=float(np.corrcoef(x[:-1],x[1:])[0,1]),
            squared_return_acf1=float(np.corrcoef(x[:-1]**2,x[1:]**2)[0,1]),
            note='descriptive_only;not_forecast_error_distribution;no_sqrt12_annualization_assumed'))
    save('monthly_log_return_diagnostics.csv',stats)
    corr=np.corrcoef(returns,rowvar=False)
    save('monthly_log_return_correlation.csv',[dict(series_id=k,**dict(zip(keys,corr[i]))) for i,k in enumerate(keys)])
    save('aligned_monthly_log_returns.csv',[dict(period=d,**dict(zip(keys,x))) for d,x in zip(dates[1:],returns)])
    desc=[dict(source_row=r,text=v['value']) for (r,c),v in sheets['Description'].items()
          if c==2 and isinstance(v['value'],str) and v['value'].strip()]
    save('source_series_descriptions.csv',desc)
    # Preserve unexpected comparison notes; do not silently use them to overwrite prices.
    comparisons=[]
    if 'Mismatch Details' in sheets:
        m=sheets['Mismatch Details']
        comparisons=[{str(c):m.get((r,c),{}).get('value') for c in range(1,8)}
                     for r in range(5,max(rr for rr,c in m)+1)]
        (OUT/'source_comparison_notes.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2)+'\n')
    manifest=dict(source=meta,source_update_cell=cells[(4,1)]['value'],
        native_rows=len(rows),series=len(keys),last_period=max(r['period'] for r in rows),
        diagnostic_window=['2010M01','2025M12'],monthly_returns=len(returns),
        missing_in_diagnostic_window=0,unexpected_comparison_sheet_present=bool(comparisons),
        comparison_note_warning='Source workbook contains Mismatch Details including July2026 LNG and date/cell discrepancies; preserved; outside diagnostic window',
        basis_risk='No electricity, hydrogen, carbon allowance or company procurement series in this six-series extract',
        statistics_status='descriptive;historical_returns_are_not_GCAM_forecast_errors',
        mean_reversion_estimated=False,tail_model_validated=False,FIN_engine_modified=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='source'},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
