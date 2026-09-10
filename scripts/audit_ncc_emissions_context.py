"""Source-boundary emissions diagnostic; no calibrated national grid or new MC.

The publication's direct intensity is used as reported. An unresolved source
fuel heat basis is not converted with a generic natural-gas emissions factor.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cap.reference_ncc import NCCConditions, build_ncc_reference
from cap.reference_incumbent import existing_ncc_pair


def main():
    out = ROOT / 'data/research_v2/ncc_emissions_context'
    out.mkdir(parents=True, exist_ok=True)
    obsfile = ROOT / 'data/research_v2/tiggeloven_reference/source_observations.csv'
    pdf = ROOT / 'tmp/pdfs/tcar_research_v2/tiggeloven_2023.pdf'
    source_manifest = json.loads((obsfile.parent / 'manifest.json').read_text())
    for p in [obsfile, pdf]:
        assert hashlib.sha256(p.read_bytes()).hexdigest() == source_manifest['sha256'][str(p.relative_to(ROOT))]
    observations = pd.read_csv(obsfile).to_dict('records')
    values = {(r['case'], r['item']): float(r['value']) for r in observations}
    yield_ = values['conventional', 'ethylene_yield']
    assert yield_ == values['electric', 'ethylene_yield'] == .303
    q_c = values['conventional', 'separation_electricity_consumption']
    q_e = sum(values['electric', p + '_electricity_consumption'] for p in ['cracker', 'compression', 'separation'])
    direct_c, direct_e = .397, 0.
    source_url = 'https://publications.tno.nl/publication/34641733/2nm91Z/tiggeloven-2023-optimization.pdf'
    pd.DataFrame([
        dict(case='conventional', value=direct_c, unit='kgCO2/kg_naphtha', pdf_page=5, printed_page=16364,
             status='reported_model_result', boundary='furnace_and_boiler; excludes_decoking_and_scope3', source_url=source_url),
        dict(case='electric', value=direct_e, unit='kgCO2/kg_naphtha', pdf_page=6, printed_page=16365,
             status='source_model_assumption_not_measurement', boundary='direct_emissions; excludes_decoking_and_scope3', source_url=source_url),
    ]).to_csv(out / 'direct_emissions_observations.csv', index=False)
    threshold = (direct_c-direct_e)/(q_e-q_c)
    rows = []
    for g, residual in itertools.product(np.linspace(0, 1, 21), [0., .05]):
        for case, direct, power in [('conventional', direct_c, q_c), ('electric', direct_e, q_e)]:
            rows.append(dict(case=case, grid_tCO2_MWh=g, common_residual_tCO2_t_naphtha=residual,
                             direct_tCO2_t_ethylene=direct/yield_, grid_tCO2_t_ethylene=power*g/yield_,
                             residual_tCO2_t_ethylene=residual/yield_, total_tCO2_t_ethylene=(direct+power*g+residual)/yield_))
    pd.DataFrame(rows).to_csv(out / 'intensity_sensitivity.csv', index=False)
    selected = []
    for g in [0., .2, .4]:
        c = (direct_c+q_c*g)/yield_
        e = (direct_e+q_e*g)/yield_
        selected.append(dict(grid_tCO2_MWh=g, conventional=c, electric=e, incremental=e-c))
    pd.DataFrame(selected).to_csv(out / 'illustrative_table.csv', index=False)

    # Same-service actual reference profiles, independent of their zero carbon
    # placeholders in the cash-only FIN calculation. Do not overwrite profiles.
    years = tuple(range(2027, 2051))
    refs = [build_ncc_reference(observations, case, years, NCCConditions(1.,8000,life,psi,.04,.05,1.,'none'),
                               numerical_KRW_per_EUR=1000.)
            for case,life,psi in [('conventional',30,.04),('electric',20,.02)]]
    assert refs[1]['quantities_per_t_naphtha']['boiler_heat_MWh'] == 0.
    pair = existing_ncc_pair(*refs, years=years, remaining_years=8, replacement_cost_scale=1.,
                            retirement_cash_EUR=0., salvage_receipt_EUR=0., terminal_rule='none',
                            ethylene_yield=yield_, numerical_KRW_per_EUR=1000.)
    annual, feasibility = [], []
    for g, residual in itertools.product([0., .2, .4], [0., .05]):
        baseline_start = 920000*(direct_c+q_c*g+residual)/yield_
        budget = baseline_start*(2050-np.asarray(years))/23
        for case, profile in pair['profiles'].items():
            output = pair['annual'][case]['output_t']
            feedstock = profile.additional_commodity_flows[0].quantity
            assert np.all(output == 920000)
            np.testing.assert_allclose(feedstock*yield_, output, rtol=0, atol=1e-7)
            is_electric = (np.asarray(years)>=2030) & (case=='replace_2030')
            expected_power = np.where(is_electric, q_e, q_c)*feedstock
            np.testing.assert_allclose(profile.grid_mwh, expected_power, rtol=0, atol=1e-7)
            direct = np.where(is_electric, direct_e, direct_c)*feedstock
            grid = g*profile.grid_mwh
            residual_emissions = residual*feedstock
            total = direct+grid+residual_emissions
            feasible = total <= budget+1e-7
            for i, year in enumerate(years):
                annual.append(dict(case=case, grid_tCO2_MWh=g, common_residual_tCO2_t_naphtha=residual,
                                   year=year, output_t=output[i], direct_tCO2=direct[i], grid_tCO2=grid[i],
                                   residual_tCO2=residual_emissions[i], total_tCO2=total[i],
                                   budget_tCO2=budget[i], feasible=bool(feasible[i])))
            feasibility.append(dict(case=case, grid_tCO2_MWh=g, common_residual_tCO2_t_naphtha=residual,
                                    first_violation_year=next((y for y, ok in zip(years,feasible) if not ok),None),
                                    all_years_feasible=bool(feasible.all()), terminal_feasible=bool(feasible[-1]),
                                    post_2030_feasible=bool(feasible[3:].all())))
    pd.DataFrame(annual).to_csv(out / 'annual_boundary_diagnostic.csv', index=False)
    pd.DataFrame(feasibility).to_csv(out / 'feasibility_diagnostic.csv', index=False)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font = ROOT / 'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'axes.unicode_minus':False})
    fig, axes = plt.subplots(1,2,figsize=(10,4))
    g = np.linspace(0,.6,301)
    axes[0].plot(g,(direct_c+q_c*g)/yield_,label='재래식: 직접 + 전력',color='#465b70',lw=2.3)
    axes[0].plot(g,(direct_e+q_e*g)/yield_,label='전기화: 원문 직접 0 가정 + 전력',color='#188b91',lw=2.3)
    axes[0].axvline(threshold,color='#b45c3c',ls='--')
    axes[0].text(threshold+.014,.2,f'교차점 {threshold:.4f}',color='#994826')
    axes[0].set(xlabel='가정한 전력 배출계수 (tCO2/MWh)',ylabel='공정 배출 / 에틸렌 생산 (tCO2/t)',title='전기화의 감축 여부는 전력에 달린다',xlim=(0,.6),ylim=(0,4.1))
    axes[0].legend(loc='upper left',fontsize=8,frameon=False)
    # Equal residuals cancel in the difference but stay in absolute emissions.
    residuals = [0.,.05,.10]
    pd.DataFrame({'residual_tCO2_t_naphtha':residuals,'zero_grid_electric_tCO2_t_ethylene':np.asarray(residuals)/yield_}).to_csv(out/'residual_plot_values.csv',index=False)
    axes[1].bar(range(3),np.asarray(residuals)/yield_,color=['#d6e0e6','#84b3b5','#188b91'])
    for i,r in enumerate(residuals):axes[1].text(i,r/yield_+.012,f'{r/yield_:.3f}',ha='center')
    axes[1].set(xticks=range(3),xticklabels=['0','0.05','0.10'],xlabel='가정한 잔여배출 (tCO2/t 나프타)',ylabel='전기화 후 잔여배출 (tCO2/t 에틸렌)',title='무배출 전력이어도 잔여배출은 남는다',ylim=(0,.40))
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.18)
        ax.set_axisbelow(True)
    fig.text(.5,.015,'원문 경계의 조건부 산술 · 한국/일본 실측 계수 아님 · 전 과정 배출 및 실제 감축 가능성 미검증',ha='center',fontsize=9,color='#465b70')
    fig.tight_layout(rect=(0,.055,1,1))
    for suffix in ['png','pdf']:fig.savefig(out/f'grid_and_residual_boundary.{suffix}',dpi=190)
    plt.close(fig)
    report = dict(source_observations=2,source_pages_visually_reviewed=[4,5,6],
                  threshold_tCO2_MWh=threshold, common_residual_example_tCO2_t_ethylene=.05/yield_,
                  intensity_rows=len(rows),annual_rows=len(annual),feasibility_cases=len(feasibility),
                  all_years_feasible_cases=sum(r['all_years_feasible'] for r in feasibility),
                  terminal_feasible_cases=sum(r['terminal_feasible'] for r in feasibility),
                  source_direct_factor_used_without_fuel_heat_conversion=True,
                  useful_steam_recovery=1.,other_recovery_values_supported=False,
                  co2_not_full_GHG=True,no_scope3_or_export_credit=True,
                  grid_and_residual_are_unweighted_assumptions=True,
                  residual_values_are_not_empirical_bounds=True,
                  linear_2027_2050_budget_is_illustrative_not_corporate_disclosure=True,
                  corporate_calibration=False, new_MC=False, new_cost_evaluation=False,
                  FIN_carbon_profiles_modified=False, new_frontier_selection=False,
                  input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                [pdf,obsfile,Path(__file__),ROOT/'src/cap/reference_ncc.py',ROOT/'src/cap/reference_incumbent.py']},
                  artifact_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='manifest.json'})
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if k not in ['input_sha256','artifact_sha256']})


if __name__ == '__main__':
    main()
