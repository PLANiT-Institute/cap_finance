"""Revalue frozen NCC timing prices through FIN's invoice replacement adapter.

No new Monte Carlo. The original EUR2019 assumed price basis, numerical constant
1000KRW/EUR and discounting are retained only for regression. Unit price indices
are explicit numerical conventions, not future inflation or FX forecasts.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from cap import config as C
from cap.fx_settlement import PathValues, FXQuotes, PricePath, PriceIndex
from cap.invoice_fin import InvoiceTerms, simulate_cost_with_invoices, paired_incremental_cost
from cap.plancost import simulate_cost
from cap.reference_timing import timing_menu
from cap.risk_metrics import loss_summary
from cap.scenario_prices import ScenarioPriceCurve, interpolate_curve

SOURCE = ROOT/'data/research_v2/ncc_timing_frontier'
OUT = ROOT/'data/research_v2/invoice_fin_bridge'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((SOURCE/'manifest.json').read_text())
    for name, expected in (manifest['input_sha256'] | manifest['artifact_sha256']).items():
        if sha(ROOT/name) != expected:
            raise ValueError(f'Frozen NCC evidence changed: {name}')
    observations = pd.read_csv(ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv').to_dict('records')
    menu = timing_menu(observations, [2030,2035,2040,2045], remaining_years=8,
                      replacement_cost_scale=1., numerical_KRW_per_EUR=1000.)
    years = tuple(menu['years']); dates = tuple(f'{y}-01-01' for y in years)
    cfg = C.load(discount_rate=.05, carbon_accounting_mode='gross_obligation_proxy')
    cfg['years'] = dict(start=2027, end=2050)
    curves = [ScenarioPriceCurve(**r) for r in json.loads((ROOT/'data/research_v2/iea_2025_scenarios/curves.json').read_text())]

    def ratio(commodity, region=None):
        c = next(c for c in curves if c.scenario=='STEPS' and c.commodity==commodity
                 and (region is None or c.region==region))
        return np.asarray(interpolate_curve(c, years, method='linear').values)/c.values[0]

    gas_ratio, oil_ratio = ratio('natural_gas','Japan'), ratio('crude_oil')
    cp, cg, cn = 100*(.5+.5*gas_ratio), 40*gas_ratio, 600*oil_ratio
    prices = {k: np.zeros(len(years)) for k in ['elec','re','h2','co2','coal','gas']}
    prices.update(elec=cp*1000, methane=cg*1000, naphtha=cn*1000)
    saved_prices = np.load(SOURCE/'annual_prices.npz')
    saved_costs = np.load(SOURCE/'cost_draws.npz')
    saved_metrics = pd.read_csv(SOURCE/'risk_metrics.csv')
    results, risk_rows = [], []
    max_old_error = max_saved_error = max_common_error = 0.
    cost_count = 0
    profiles = {'baseline': menu['baseline']} | {
        name: menu['candidates'][name]['profile'] for name in ['replace_2030','replace_2035','replace_2040']}
    for seed in [20260917,20260918]:
        n = 5000
        ids = tuple(f'path_{i}' for i in range(n))
        sample = f'frozen_ncc_timing_seed_{seed}'

        def paths(x):
            return PathValues(np.broadcast_to(x,(n,len(years))), ids, dates, sample)

        power = saved_prices[f'{seed}_power']
        methane = saved_prices[f'{seed}_methane']
        naphtha = saved_prices[f'{seed}_naphtha']
        shocks = {'elec': paths(power/cp), 'h2': paths(1.), 'capex': paths(1.)}
        old_shocks = {k: v.values for k,v in shocks.items()} | {'methane': methane/cg, 'naphtha': naphtha/cn}
        fx = FXQuotes('EUR', {'EUR':paths(1.), 'KRW':paths(1000.)})
        discounts = paths(1.05**-np.arange(len(years)))
        ppaths = {'methane': paths(methane), 'naphtha': paths(naphtha)}
        paired = {}
        for name, profile in profiles.items():
            terms = {f.flow_id: InvoiceTerms(PricePath('EUR', f.quantity_unit,
                ppaths[f.price_key], 2019), dates, dates,
                'Frozen research reference EUR2019 operating prices; annual same-date settlement')
                for f in profile.additional_commodity_flows}
            actual = simulate_cost_with_invoices(profile, prices, shocks, {'subsidy':{}}, cfg,
                terms=terms, fx=fx, discount_factors=discounts, real_base_year=2019,
                basis_evidence='Legacy NCC numerical KRW/EUR1000 and EUR2019 assumed real costs; not market prices',
                invoice_indices={('EUR',2019):PriceIndex('EUR',2019,paths(1.))},
                evaluation_index=PriceIndex('KRW',2019,paths(1.)), freeze='capex')
            legacy = simulate_cost(profile, prices, old_shocks, {'subsidy':{}}, cfg, freeze='capex')
            np.testing.assert_allclose(actual.npv_krw_billion, legacy, rtol=1e-12, atol=1e-7)
            old_error = float(np.max(abs(actual.npv_krw_billion-legacy)))
            max_old_error = max(max_old_error, old_error)
            paired[name] = actual
            compared = actual.npv_krw_billion if name=='baseline' else paired_incremental_cost(actual, paired['baseline'])
            expected = saved_costs[f'{seed}_{name}']
            np.testing.assert_allclose(compared, expected, rtol=1e-12, atol=1e-7)
            saved_error = float(np.max(abs(compared-expected)))
            max_saved_error = max(max_saved_error, saved_error)
            common_error = float(np.max(abs(actual.settlement.flow_cash_by_date['naphtha']
                           -paired['baseline'].settlement.flow_cash_by_date['naphtha'])))
            assert common_error == 0
            max_common_error = max(max_common_error, common_error)
            cost_count += n
            results.append(dict(seed=seed, candidate=name, paths=n,
                comparison='absolute baseline' if name=='baseline' else 'paired incremental',
                max_error_vs_original_FIN_KRW_billion=old_error,
                max_error_vs_frozen_cost_KRW_billion=saved_error,
                max_common_naphtha_cash_error_KRW=common_error))
            if name!='baseline':
                metrics = loss_summary(compared,.95)
                old = saved_metrics[(saved_metrics.seed==seed)&(saved_metrics.candidate==name)].iloc[0]
                for key in ['mean','p50','q_alpha','tcar','es_alpha']:
                    np.testing.assert_allclose(metrics[key], old[key], rtol=1e-12, atol=1e-7)
                risk_rows.append(dict(seed=seed, candidate=name, **metrics))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(OUT/'frozen_FIN_comparison.csv',index=False)
    pd.DataFrame(risk_rows).to_csv(OUT/'paired_risk_metrics.csv',index=False)
    report = dict(verification_passed=True, new_MC_draws=0,
        frozen_price_pools=2, paths_per_pool=5000, baseline_and_incremental_values_checked=cost_count,
        adapter_full_cost_values_compared_with_existing_FIN=cost_count,
        paired_summary_values_checked=len(risk_rows)*5,
        max_error_vs_original_FIN_KRW_billion=max_old_error,
        max_error_vs_frozen_cost_KRW_billion=max_saved_error,
        max_common_naphtha_cash_error_KRW=max_common_error,
        FIN_integration_scope='Opt-in wrapper replaces all additional commodity flows; retains other FIN channels',
        price_basis='EUR2019 and KRW2019 assumed research basis, numerical constant1000KRW/EUR, unit indices',
        future_FX_or_inflation_estimated=False, company_calibration=False, frontier_reoptimized=False,
        original_FIN_modified=False, Excel_updated=False,
        source_sha256={str((SOURCE/name).relative_to(ROOT)):sha(SOURCE/name) for name in
                       ['manifest.json','annual_prices.npz','cost_draws.npz','risk_metrics.csv']},
        artifact_sha256={str(p.relative_to(ROOT)):sha(p) for p in
            [ROOT/'src/cap/invoice_fin.py',ROOT/'src/cap/fx_settlement.py',
             ROOT/'tests/test_invoice_fin.py',Path(__file__),
             OUT/'frozen_FIN_comparison.csv',OUT/'paired_risk_metrics.csv']})
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if not k.endswith('sha256')},indent=2))


if __name__=='__main__':
    main()
