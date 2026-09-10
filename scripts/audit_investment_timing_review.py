"""Independent accounting/eligibility audit of the saved NCC timing experiment.

Reuses saved price paths, does not recalibrate firms or change frozen results.
Terminal credits are sensitivity proxies, not receipts or continuation values.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/research_cycles/2026-09-10-investment-review/cycle1'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'data/research_v2/ncc_timing_frontier'
    manifest = json.loads((source / 'manifest.json').read_text())
    names = ['annual_cash.csv', 'annual_prices.npz', 'cost_draws.npz',
             'risk_metrics.csv', 'qualification.csv']
    for name in names:
        file = source / name
        assert hashlib.sha256(file.read_bytes()).hexdigest() == manifest['artifact_sha256'][str(file.relative_to(ROOT))]
    cash = pd.read_csv(source / 'annual_cash.csv')
    metrics = pd.read_csv(source / 'risk_metrics.csv')
    qual = pd.read_csv(source / 'qualification.csv')
    prices = np.load(source / 'annual_prices.npz')
    saved = np.load(source / 'cost_draws.npz')
    yy = np.arange(2027, 2051)
    disc = 1.05 ** -(yy - 2027)
    feed = 920000 / .303
    plant = 994490000.
    boiler = 72.1 * (.492 - (.841 - .431)) * 115 / .303 * 1000
    old_maintenance = .04 * plant * (.05 / (1 - 1.05**-30)) + .04 * boiler * (.05 / (1 - 1.05**-25))
    old_renewal = np.where(yy == 2035, plant + boiler, 0.)
    old_gas = -feed * (2.349 - 1.868 - .082/.92)
    curves = json.loads((ROOT / 'data/research_v2/iea_2025_scenarios/curves.json').read_text())
    curve = next(c for c in curves if c['scenario'] == 'STEPS' and c['commodity'] == 'natural_gas' and c['region'] == 'Japan')
    gas_ratio = np.interp(yy, curve['years'], curve['values']) / curve['values'][0]
    central_power = 100 * (.5 + .5 * gas_ratio)
    central_gas = 40 * gas_ratio
    # Baseline's surviving 2035 investment is treated under the same proxy rule.
    baseline_terminal_proxy = plant * (1 - 16/30) + boiler * (1 - 16/25)
    decompositions, summaries, budgets = [], [], []
    all_draws, analytic = {}, {}
    max_error = 0.
    for date in [2030, 2035, 2040, 2045]:
        name = f'replace_{date}'
        r = cash[cash.candidate == name].sort_values('year')
        assert list(r.year) == list(yy)
        np.testing.assert_allclose(r.output_t, 920000, atol=0)
        np.testing.assert_allclose(r.feedstock_t, feed)
        maintenance = r.fixed_cash_EUR.to_numpy() - r[['construction_EUR', 'new_renewal_EUR', 'incumbent_renewal_EUR']].sum(axis=1).to_numpy()
        components = {
            'construction': r.construction_EUR.to_numpy(),
            'electric_renewal': r.new_renewal_EUR.to_numpy(),
            'incumbent_renewal_difference': r.incumbent_renewal_EUR.to_numpy() - old_renewal,
            'maintenance_difference': maintenance - old_maintenance,
            'electricity_difference': (r.grid_mwh.to_numpy() - feed*.083) * central_power,
            'methane_net_sales_difference': (r.net_methane_MWh.to_numpy() - old_gas) * central_gas,
        }
        vals = {k: float(np.dot(v, disc)/1e6) for k, v in components.items()}
        mean = sum(vals.values())
        analytic[name] = mean
        for k, v in vals.items():
            decompositions.append(dict(candidate=name, component=k, mean_million_EUR=v))
        if date < 2045:
            np.testing.assert_allclose(metrics[metrics.candidate == name].analytic_mean, mean, atol=1e-7)
        origin = date + 20 if date+20 <= 2050 else date
        proxy = plant * (1 - (2051-origin)/20)
        shift = -(proxy-baseline_terminal_proxy)*disc[-1]/1e6
        for seed in [20260917, 20260918]:
            power = prices[f'{seed}_power']
            gas = prices[f'{seed}_methane']
            total = ((r.fixed_cash_EUR.to_numpy()-old_maintenance-old_renewal
                      +(r.grid_mwh.to_numpy()-feed*.083)*power
                      +(r.net_methane_MWh.to_numpy()-old_gas)*gas)*disc).sum(axis=1)/1e6
            if date < 2045:
                max_error = max(max_error, float(np.max(abs(total-saved[f'{seed}_{name}']))))
                np.testing.assert_allclose(total, saved[f'{seed}_{name}'], rtol=1e-12, atol=1e-7)
            all_draws[seed, name] = total
            for rule, correction in [('zero_terminal_cash', 0.), ('symmetric_straight_line_proxy', shift)]:
                draw = total+correction
                p50, p95 = np.quantile(draw, [.5, .95])
                es = np.sort(draw)[-250:].mean()
                np.testing.assert_allclose(p95-p50, np.quantile(total, .95)-np.median(total), atol=1e-9)
                summaries.append(dict(seed=seed, candidate=name, terminal_rule=rule,
                    analytic_mean=mean+correction, p50=p50, p95=p95, tcar95=p95-p50,
                    es95=es, terminal_proxy_shift=correction,
                    electric_operating_years=int((yy>=date).sum())))
    # Budget changes only requalify the same evaluated plans; no new price paths.
    for grid in [.2, .4]:
        q = qual[(qual.grid_initial == grid) & (qual.residual_per_t_naphtha == 0)]
        for cap in [.45, .50, .55, .60, .65, .70, .75, .80, .85]:
            eligible = list(q[(q.cumulative_ratio <= cap+1e-12) & q.terminal_feasible].candidate)
            for seed in [20260917, 20260918]:
                es = {n: float(np.sort(all_draws[seed, n])[-250:].mean()) for n in eligible}
                frontier = [n for n in eligible if not any(analytic[m] <= analytic[n] and es[m] <= es[n]
                    and (analytic[m] < analytic[n] or es[m] < es[n]) for m in eligible)]
                budgets.append(dict(grid_initial=grid, maximum_baseline_emissions_ratio=cap,
                    seed=seed, eligible=';'.join(eligible), mean_ES_frontier=';'.join(frontier),
                    annual_linear_cap_enforced=False))
    summary_frame = pd.DataFrame(summaries)
    budget_frame = pd.DataFrame(budgets)
    expected_order = [f'replace_{d}' for d in [2045, 2040, 2035, 2030]]
    for seed in [20260917, 20260918]:
        for rule in ['zero_terminal_cash', 'symmetric_straight_line_proxy']:
            rows = summary_frame[(summary_frame.seed == seed) & (summary_frame.terminal_rule == rule)]
            for score in ['analytic_mean', 'es95']:
                assert list(rows.sort_values(score).candidate) == expected_order
        for cap, chosen in [(.45, ''), (.50, 'replace_2030'), (.55, 'replace_2035'),
                            (.65, 'replace_2040'), (.80, 'replace_2045')]:
            row = budget_frame[(budget_frame.seed == seed) & (budget_frame.grid_initial == .2)
                               & (budget_frame.maximum_baseline_emissions_ratio == cap)].iloc[0]
            assert row.mean_ES_frontier == chosen
    pd.DataFrame(decompositions).to_csv(OUT/'cost_decomposition.csv', index=False)
    summary_frame.to_csv(OUT/'terminal_sensitivity.csv', index=False)
    budget_frame.to_csv(OUT/'emissions_budget_sweep.csv', index=False)
    pv2050 = plant*disc[-1]/1e6
    gap = analytic['replace_2030']-analytic['replace_2040']
    report = dict(saved_incremental_draws_reconstructed=30000, maximum_absolute_error=max_error,
        additional_2045_draws_evaluated=10000, analytic_means_matched=3,
        terminal_translation_checks=8, terminal_order_checks=8,
        main_budget_choice_checks=10, budget_evaluations=len(budgets),
        mean_gap_2030_minus_2040=gap, terminal_year_2030_renewal_present_value=pv2050,
        renewal_share_of_mean_gap=pv2050/gap,
        remaining_gap_if_only_2050_renewal_removed=gap-pv2050,
        interpretation='Removing renewal is a diagnostic, not a feasible replacement policy. Straight-line credits are sensitivity proxies, not realised cash or a validated continuation value. Requalification is conditional; budgets and grid paths have no probabilities.',
        new_corporate_simulation=False, new_price_paths=False,
        inputs={str((source/n).relative_to(ROOT)):hashlib.sha256((source/n).read_bytes()).hexdigest() for n in names})
    curve_path = ROOT / 'data/research_v2/iea_2025_scenarios/curves.json'
    report['inputs'][str(curve_path.relative_to(ROOT))] = hashlib.sha256(curve_path.read_bytes()).hexdigest()
    report['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (OUT/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    print(pd.DataFrame(decompositions).pivot(index='component', columns='candidate', values='mean_million_EUR').round(3).to_string())


if __name__ == '__main__':
    main()
