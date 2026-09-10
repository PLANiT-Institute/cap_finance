"""Bounded investment comparisons, not corporate calibration or full CCS appraisal.

Reuses frozen independent price-pool statistics and costs. No resampling occurs.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parents[1]
O = R/'docs/research_cycles/2026-09-10-investment-review/cycle2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    O.mkdir(parents=True, exist_ok=True)
    paired = R/'data/research_v2/ieaghg_paired'
    phys = R/'data/research_v2/ieaghg_physical_reference'
    pm = json.loads((paired/'manifest.json').read_text())
    sm = json.loads((phys/'manifest.json').read_text())
    assert sha(R/sm['source_pdf']) == sm['source_pdf_sha256']
    for group in [pm['artifact_sha256'], sm['artifact_sha256'], sm['frozen_inputs_sha256']]:
        for p, expected in group.items():
            assert sha(R/p) == expected, p
    pkg = json.loads((R/'data/research_v2/ieaghg_reference/package.json').read_text())
    physical = pd.read_csv(phys/'same_product_ledger.csv').set_index('case')
    metrics = pd.read_csv(paired/'conditional_cost_metrics.csv')
    draws = np.load(paired/'STEPS_validation_incremental_costs.npz')
    # Check frozen saved statistics directly in the independent evaluation pool.
    check_values = 0
    view = metrics[(metrics.model == 'block_12') & (metrics.role == 'validation') & (metrics.scenario == 'STEPS')]
    for row in view.itertuples():
        a = draws[row.plan_id]
        expected = [np.mean(a), np.median(a), np.quantile(a, .95), np.sort(a)[-500:].mean()]
        np.testing.assert_allclose([row.mean, row.p50, row.q95, row.es95], expected, atol=1e-7, rtol=1e-12)
        check_values += 4
    years = np.arange(2027, 2051)
    discount = 1.05**-(years-2027)
    annuity = float(discount[years >= 2030].sum())
    l1, l2 = pkg['cases']['EOP_L1'], pkg['cases']['EOP_L2']
    delta_gas = l2['ng_GJ'] - l1['ng_GJ']
    delta_fixed = l2['residual_fixed_price_opex_source_USD'] - l1['residual_fixed_price_opex_source_USD']
    delta_cap = l2['initial_capex_source_USD'] - l1['initial_capex_source_USD']
    fixed_pv = delta_cap*discount[:3].mean()/1e6 + delta_fixed*annuity/1e6
    assert delta_gas > 0 and delta_fixed > 0 and delta_cap > 0
    # Therefore same-h L2 is strictly costlier on every admissible positive gas path
    # at zero carbon charge, with equal nonnegative downstream fee. Not just MC evidence.
    delta_avoid = physical.loc['EOP_L2','avoided_t_CO2_y']-physical.loc['EOP_L1','avoided_t_CO2_y']
    delta_capture = physical.loc['EOP_L2','captured_t_CO2_y']-physical.loc['EOP_L1','captured_t_CO2_y']
    selections, thresholds, margins, policy_choices = [], [], [], []
    for key, group in metrics.groupby(['model','role','scenario']):
        for target in [.50, .60, .604]:
            cases = [c for c in ['EOP_L1','EOP_L2'] if physical.loc[c,'C7_avoided_fraction'] >= target]
            for mode in ['common_unhedged', 'priced_contract_menu']:
                g = group[group.case.isin(cases)]
                if mode == 'common_unhedged':
                    g = g[g.incremental_gas_contract_fraction == 0]
                for weight in [0., .01, .1, 1.]:
                    if len(g):
                        scores = g.analytic_mean + weight*g.es95
                        selected = g.loc[np.isclose(scores, scores.min(), rtol=0, atol=1e-7)]
                        selected_cases = ';'.join(sorted(set(selected.case)))
                        selected_plans = ';'.join(sorted(selected.plan_id))
                    else:
                        selected_cases = selected_plans = ''
                    assert selected_cases == ({.50:'EOP_L1', .60:'EOP_L2', .604:''}[target])
                    selections.append(dict(model=key[0], role=key[1], scenario=key[2], target=target,
                        procurement_mode=mode, sensitivity_weight=weight,
                        selected_physical_cases=selected_cases, selected_plans=selected_plans))
        # Fixed-contract physical comparison first. Carbon charge is hypothetical,
        # uniform on the reported boundary; fee is per captured tonne, not avoided tonne.
        for h in [0., 1.]:
            a = group[(group.case == 'EOP_L1') & (group.incremental_gas_contract_fraction == h)].iloc[0]
            b = group[(group.case == 'EOP_L2') & (group.incremental_gas_contract_fraction == h)].iloc[0]
            for fee in [0., 20., 50., 100.]:
                for criterion, basegap in [('mean', b.analytic_mean-a.analytic_mean), ('ES95', b.es95-a.es95)]:
                    threshold = (basegap*1e6/annuity + fee*delta_capture)/delta_avoid
                    # Algebraic threshold tested against separately shifted full summaries.
                    for c in [threshold-.01, threshold, threshold+.01]:
                        shift1 = annuity*(fee*physical.loc['EOP_L1','captured_t_CO2_y']-c*physical.loc['EOP_L1','avoided_t_CO2_y'])/1e6
                        shift2 = annuity*(fee*physical.loc['EOP_L2','captured_t_CO2_y']-c*physical.loc['EOP_L2','avoided_t_CO2_y'])/1e6
                        av = (a.analytic_mean if criterion == 'mean' else a.es95)+shift1
                        bv = (b.analytic_mean if criterion == 'mean' else b.es95)+shift2
                        np.testing.assert_allclose(bv-av, (threshold-c)*delta_avoid*annuity/1e6, atol=1e-9)
                    thresholds.append(dict(model=key[0],role=key[1],scenario=key[2],common_contract_fraction=h,
                        criterion=criterion,downstream_fee_per_captured_t=fee,
                        switching_carbon_charge_per_avoided_t=threshold,
                        fee_slope=delta_capture/delta_avoid,unit='source USD per tCO2; hypothetical constant real schedule'))
        if key[0] == 'block_12' and key[2] == 'STEPS':
            for charge in [0., 50., 100., 200., 500., 1000.]:
                for fee in [0., 20., 50.]:
                    for target in [.50, .60]:
                        cases = [c for c in ['EOP_L1','EOP_L2'] if physical.loc[c,'C7_avoided_fraction'] >= target]
                        for mode in ['common_unhedged', 'priced_contract_menu']:
                            g = group[group.case.isin(cases)].copy()
                            if mode == 'common_unhedged':
                                g = g[g.incremental_gas_contract_fraction == 0]
                            shift = np.array([annuity*(fee*physical.loc[c,'captured_t_CO2_y']
                                -charge*physical.loc[c,'avoided_t_CO2_y'])/1e6 for c in g.case])
                            for weight in [0., .01, .1, 1.]:
                                scores = g.analytic_mean+shift+weight*(g.es95+shift)
                                selected = g.loc[np.isclose(scores, scores.min(), rtol=0, atol=1e-7)]
                                policy_choices.append(dict(role=key[1],carbon_charge=charge,downstream_fee=fee,
                                    target=target,procurement_mode=mode,sensitivity_weight=weight,
                                    selected_physical_cases=';'.join(sorted(set(selected.case))),
                                    selected_plans=';'.join(sorted(selected.plan_id))))
    for case, target in [('EOP_L1', .50), ('EOP_L2', .60)]:
        a = physical.loc[case,'avoided_t_CO2_y']
        q = physical.loc[case,'captured_t_CO2_y']
        e0 = physical.loc['REFERENCE','C7_emitted_t_CO2_y']
        margin = a-target*e0
        u = margin/q
        assert 0 < u < .005
        for stress in [0., u, .005, .01]:
            net = (a-stress*q)/e0
            eligible = net+1e-12 >= target
            assert eligible == (stress <= u+1e-12)
            margins.append(dict(case=case, target=target, net_additional_downstream_fraction_of_capture=stress,
                net_reduction=net, eligible=eligible,maximum_fraction=u,
                annual_net_emissions_margin=margin,
                interpretation='Accounting stress only: net extra downstream emissions relative to baseline, not estimated leakage'))
    # Exact continuation of the SAME electric technology, output and physical inputs
    # beyond 2050. Common future operating costs cancel pathwise; replacement dates do not.
    ncc = pd.read_csv(R/'docs/research_cycles/2026-09-10-investment-review/cycle1/terminal_sensitivity.csv')
    ncc = ncc[ncc.terminal_rule == 'zero_terminal_cash']
    continuations = []
    cap = 994.49  # million assumed source EUR; constant real replacements
    for seed, group in ncc.groupby('seed'):
        anchor = group[group.candidate == 'replace_2040'].iloc[0]
        for row in group.itertuples():
            date = int(row.candidate[-4:])
            next_due = date+20
            while next_due <= 2050:
                next_due += 20
            tail = cap*1.05**-(next_due-2027)/(1-1.05**-20)
            explicit = sum(cap*1.05**-(y-2027) for y in range(next_due, 3051, 20))
            np.testing.assert_allclose(tail, explicit, rtol=1e-12, atol=1e-10)
            tail2040 = cap*1.05**-(2060-2027)/(1-1.05**-20)
            difference = tail-tail2040
            continuations.append(dict(seed=seed,candidate=row.candidate,
                continuation_capex_PV=tail, continuation_difference_vs2040=difference,
                continued_mean_difference_vs2040=row.analytic_mean-anchor.analytic_mean+difference,
                window_ES_difference_with_capital_extension=row.es95-anchor.es95+difference,
                window_TCaR_with_capital_extension=row.tcar95))
    cf = pd.DataFrame(continuations)
    for seed, rows in cf.groupby('seed'):
        for col in ['continued_mean_difference_vs2040', 'window_ES_difference_with_capital_extension']:
            assert list(rows.sort_values(col).candidate) == ['replace_2045','replace_2040','replace_2035','replace_2030']
    # Common future random cash cannot simply be dropped from each plan's ES.
    # Instead prove ordering from pathwise cost differences under the frozen
    # within-window identity P_electricity = 50 + 1.25 P_methane (prices nonnegative).
    ncc_cash = pd.read_csv(R/'data/research_v2/ncc_timing_frontier/annual_cash.csv')
    ncc_prices = np.load(R/'data/research_v2/ncc_timing_frontier/annual_prices.npz')
    for seed in [20260917,20260918]:
        np.testing.assert_allclose(ncc_prices[f'{seed}_power'],50+1.25*ncc_prices[f'{seed}_methane'],rtol=1e-12)
    tails = cf[cf.seed==20260917].set_index('candidate').continuation_capex_PV
    bounds = []
    for early, late in [(2030,2035),(2035,2040),(2040,2045)]:
        e = ncc_cash[ncc_cash.candidate==f'replace_{early}'].sort_values('year')
        l = ncc_cash[ncc_cash.candidate==f'replace_{late}'].sort_values('year')
        dg = e.grid_mwh.to_numpy()-l.grid_mwh.to_numpy()
        dm = e.net_methane_MWh.to_numpy()-l.net_methane_MWh.to_numpy()
        coefficients = 1.25*dg+dm
        lower = np.dot(e.fixed_cash_EUR.to_numpy()-l.fixed_cash_EUR.to_numpy()+50*dg,discount)/1e6
        lower += tails[f'replace_{early}']-tails[f'replace_{late}']
        assert coefficients.min() >= 0 and lower > 0
        bounds.append(dict(earlier=early,later=late,minimum_pathwise_difference_million_EUR=lower,
            minimum_gas_coefficient=coefficients.min(),
            scope='Frozen affine energy-price mapping; identical common post2050 operating cash; stationary deterministic renewal; not general price coupling'))
    pd.DataFrame(bounds).to_csv(O/'ncc_continuation_dominance_bounds.csv',index=False)
    pd.DataFrame(selections).to_csv(O/'physical_and_contract_choices.csv', index=False)
    pd.DataFrame(thresholds).to_csv(O/'carbon_charge_switching_thresholds.csv', index=False)
    pd.DataFrame(margins).to_csv(O/'downstream_emissions_margins.csv', index=False)
    policy_frame = pd.DataFrame(policy_choices)
    # A declared sensitivity example, not an inferred company preference or carbon price.
    example = policy_frame[(policy_frame.carbon_charge==100) & (policy_frame.downstream_fee==0)
                           & (policy_frame.target==.5) & policy_frame.sensitivity_weight.isin([0.,.1])]
    for row in example.itertuples():
        expected = 'EOP_L1' if row.procurement_mode=='common_unhedged' and row.sensitivity_weight==.1 else 'EOP_L2'
        assert row.selected_physical_cases == expected
    policy_frame.to_csv(O/'policy_and_procurement_choices.csv',index=False)
    cf.to_csv(O/'ncc_matched_continuation.csv', index=False)
    view[['case','incremental_gas_contract_fraction','analytic_mean','p50','q95','tcar95','es95']].to_csv(O/'reference_risk_comparison.csv',index=False)
    report = dict(frozen_statistic_checks=check_values,choice_comparisons=len(selections),
        physical_choice_changed_by_risk_or_contract_at_zero_carbon_charge=False,
        analytic_same_contract_dominance=dict(delta_initial_capex_USD=delta_cap,
            delta_residual_fixed_opex_USD_y=delta_fixed,delta_ng_GJ_y=delta_gas,
            deterministic_PV_gap_million_USD=fixed_pv,scope='Positive gas prices; same h; nonnegative fee; no carbon charge'),
        switching_threshold_rows=len(thresholds), threshold_identity_checks=3*len(thresholds),
        policy_sensitivity_choices=len(policy_choices),declared_mechanism_example_checks=len(example),
        downstream_stress_rows=len(margins),continuation_rows=len(cf),
        source_status='Frozen text-based package retained; later selected-page physical audit bound by hashes; pages275 and305 visually rechecked this cycle. C7 column identity remains an inferred reconciliation, not an official erratum.',
        input_sha256={str(p.relative_to(R)):sha(p) for p in [paired/'manifest.json',phys/'manifest.json',
            paired/'conditional_cost_metrics.csv',phys/'same_product_ledger.csv',
            R/'docs/research_cycles/2026-09-10-investment-review/cycle1/terminal_sensitivity.csv']},
        script_sha256=sha(Path(__file__)),new_price_paths=False,new_corporate_calibration=False,
        transport_storage_tariff_calibrated=False,full_chain_emissions_verified=False,
        finite_horizon_resolved_generally=False,ncc_continuation_pathwise_bounds=len(bounds),
        full_horizon_ES_or_TCaR_levels_computed=False,
        risk_note='Capital-only ES/TCaR columns are diagnostics. Common future random operating cash preserves the proven pathwise ordering but can change ES/TCaR levels; those levels were not evaluated.')
    (O/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    t=pd.DataFrame(thresholds)
    print(t[(t.model=='block_12') & (t.scenario=='STEPS') & (t.downstream_fee_per_captured_t==0)].to_string(index=False))
    print(pd.DataFrame(margins).iloc[[0,4]].to_string(index=False))
    print(cf[cf.seed==20260917].to_string(index=False))


if __name__ == '__main__':
    main()
