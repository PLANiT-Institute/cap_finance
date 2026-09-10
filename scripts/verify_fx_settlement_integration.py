"""Compare the settlement kernel with frozen exact FX cost enumeration.

Uses normalized diagnostic prices/quotes, not currency price forecasts. Twelve
synthetic calendar labels only route the twelve saved months. No Monte Carlo,
new distribution fit, corporate exposure or original artifact overwrite.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cap.fx_settlement import PathValues, FXQuotes, PricePath, InvoiceFlow, settle_invoices

SOURCE = ROOT / 'data/research_v2/ecb_fx_reference'
OUT = ROOT / 'data/research_v2/fx_settlement_validation'
EXPECTED = {
    'exact_block_arrays.npz': '0218b7f4f4af5fc2c4371e62a14af8989405d6acd1eda21b885e302a37a72b24',
    'aligned_commodity_fx_returns.csv': '9b8d3b05a5c5a5c0a2aafdb9b757be5cfb5fbaa4bb277117402bf3cf58e95e41',
    'experiment_manifest.json': 'c2b24f6c47642237098be463743a027d8e3ca527961488b90ff6791f20e71698',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for filename, expected in EXPECTED.items():
        if sha(SOURCE / filename) != expected:
            raise ValueError(f'Frozen evidence changed: {filename}')
    manifest = json.loads((SOURCE / 'experiment_manifest.json').read_text())
    for path, expected in manifest['artifact_sha256'].items():
        if sha(ROOT / path) != expected:
            raise ValueError(f'Frozen experiment artifact changed: {path}')
    panel = pd.read_csv(SOURCE / 'aligned_commodity_fx_returns.csv', index_col='period')
    old_metrics = pd.read_csv(SOURCE / 'exact_block_conversion_metrics.csv')
    frozen = np.load(SOURCE / 'exact_block_arrays.npz')
    mult = frozen['multipliers']
    assert mult.shape == (180, 12, 9)
    dates = tuple(f'2000-{month:02d}-01' for month in range(1, 13))
    rows = []
    for method in ['same_historical_block', 'independent_block_pairs']:
        if method == 'same_historical_block':
            price_ix = fx_ix = np.arange(180)
        else:
            price_ix = np.repeat(np.arange(180), 180)
            fx_ix = np.tile(np.arange(180), 180)
        ids = tuple(f'price_block_{p}|fx_block_{f}' for p, f in zip(price_ix, fx_ix))
        sample = f'frozen_exact_normalized_diagnostic:{method}'

        def paths(x):
            return PathValues(x, ids, dates, sample)

        one = paths(np.ones((len(ids), 12)))
        quotes = {'USD': one}
        for currency in ['EUR', 'KRW', 'JPY']:
            quotes[currency] = paths(mult[fx_ix, :, panel.columns.get_loc(f'fx_{currency}_per_USD')])
        fx = FXQuotes('USD', quotes)
        for commodity in ['brent', 'japan_lng', 'iron_ore']:
            price = PricePath('USD', 'normalized_unit',
                paths(mult[price_ix, :, panel.columns.get_loc(commodity)]), None)
            flow = InvoiceFlow(commodity, 'purchase', (1.,)*12, 'normalized_unit',
                dates, dates, price,
                'Frozen completion26 normalized arithmetic diagnostic; not a corporate invoice')
            for currency in ['KRW', 'JPY']:
                result = settle_invoices([flow], fx, currency, one)
                # Frozen diagnostic reports mean monthly unit cost, not annual total.
                computed = result.npv_by_path / 12
                expected = frozen[f'{commodity}_{currency}_{method}']
                np.testing.assert_allclose(computed, expected, rtol=2e-14, atol=2e-14)
                q50, q95 = np.quantile(computed, [.5, .95], method='inverted_cdf')
                tail_count = len(computed) // 20  # 180 and 32400 both divisible by 20.
                metrics = dict(mean=float(computed.mean()), p50=float(q50), p95=float(q95),
                    upper_gap95=float(q95-q50), es95=float(np.sort(computed)[-tail_count:].mean()))
                reference = old_metrics[(old_metrics.commodity == commodity) &
                    (old_metrics.currency == currency) & (old_metrics.method == method)].iloc[0]
                for name, value in metrics.items():
                    np.testing.assert_allclose(value, reference[name], rtol=2e-14, atol=2e-14)
                rows.append(dict(commodity=commodity, currency=currency, method=method,
                    paths_checked=len(computed), monthly_cashflows_checked=int(result.cash_by_date.size),
                    max_absolute_cost_error=float(np.max(np.abs(computed-expected))), **metrics))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / 'frozen_cost_comparison.csv', index=False)
    result = dict(verification_passed=True,
        scope='Fixed monthly nominal normalized purchases; no settlement delay in frozen integration example',
        calendar='Synthetic year 2000 routes saved month positions only, not observations or forecasts',
        scenarios_checked=len(rows), annual_cost_values_checked=sum(r['paths_checked'] for r in rows),
        monthly_cashflow_values_checked=sum(r['monthly_cashflows_checked'] for r in rows),
        summary_statistics_checked=len(rows)*5,
        maximum_absolute_cost_error=max(r['max_absolute_cost_error'] for r in rows),
        source_probabilities='Equal mass on frozen finite diagnostic supports; not future scenario likelihood',
        new_MC_draws=0, company_calibration=False, FIN_integrated=False, Excel_integrated=False,
        source_sha256={str((SOURCE / p).relative_to(ROOT)): h for p, h in EXPECTED.items()},
        artifact_sha256={str(p.relative_to(ROOT)): sha(p) for p in
            [ROOT / 'src/cap/fx_settlement.py', ROOT / 'tests/test_fx_settlement.py',
             Path(__file__), OUT / 'frozen_cost_comparison.csv']})
    (OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if not k.endswith('sha256')}, indent=2))


if __name__ == '__main__':
    main()
