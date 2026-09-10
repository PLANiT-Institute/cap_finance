"""Visually checked NCC source observations; no automatic corporate calibration."""
from pathlib import Path
import hashlib
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, font_manager

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://publications.tno.nl/publication/34641733/2nm91Z/tiggeloven-2023-optimization.pdf'
SOURCE_SHA = '000e24d881ef43eba7fd9ec986434dbb5e6444e536822edeafba1303367c9b5c'


def main():
    source = ROOT/'tmp/pdfs/tcar_research_v2/tiggeloven_2023.pdf'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA
    out = ROOT/'data/research_v2/tiggeloven_reference'
    out.mkdir(parents=True, exist_ok=True)
    rows = []

    def add(case, item, value, unit, page, location, interpretation='source_observation'):
        rows.append(dict(case=case,item=item,value=value,unit=unit,pdf_page=page,
                         location=location,interpretation=interpretation,
                         transcription='visually_checked_publisher_PDF',source_url=URL))

    # Preserve steam grades and internal production. These are not purchase bills.
    for case, items in {
        'conventional': [('cracker_methane_consumption',1.868),('cracker_superheated_steam_production',.841),
                         ('compression_superheated_steam_consumption',.431)],
        'electric': [('cracker_electricity_consumption',1.476),('cracker_saturated_steam_production',.542),
                     ('compression_electricity_consumption',.383)],
    }.items():
        for item, value in items:
            add(case,item,value,'kWh/kg_naphtha',4,'Table 1; printed16363')
        for item,value in [('separation_saturated_steam_consumption',.492),
                           ('separation_electricity_consumption',.083),('separation_methane_production',2.349)]:
            add(case,item,value,'kWh/kg_naphtha',4,'Table 1; printed16363')
        add(case,'ethylene_yield',.303,'kg_ethylene/kg_naphtha',4,'Table 1; printed16363')
    costs = [('conventional',5126.,405.,.04,'kg_ethylene/h'),
             ('electric',5126.,405.,.02,'kg_ethylene/h'),
             ('gas_boiler',72.1,None,.04,'kW_steam'),('ethylene_tank',19.5,None,.02,'kg_ethylene'),
             ('Li_ion',168.9,None,.01,'kWh'),('wind_8_4MW',23.8e6,None,.02,'turbine'),
             ('PV',188.2,None,.01,'m2')]
    for case,slope,intercept,psi,unit in costs:
        add(case,'TOC_slope',slope,'EUR2019/('+unit+')',10,'Table 3; printed16369')
        if intercept is not None:
            add(case,'TOC_intercept',intercept,'million_EUR2019',10,'Table 3; printed16369')
        add(case,'maintenance_fraction_printed',psi,'table_header_percent',10,
            'Table 3 and equation3 p7', 'held_percent_header_vs_decimal; annualized_capital_base')
    for case,life in [('gas_boiler',25),('PV',25),('wind_8_4MW',25),('ethylene_tank',15),('Li_ion',15)]:
        add(case,'lifetime',life,'years',11,'Table 4; printed16370')
    add('gas_boiler','efficiency',92.,'percent',11,'Table 4; printed16370')
    for case,sec,page in [('conventional',2.44,4),('electric',2.05,6)]:
        add(case,'reported_pyrolysis_separation_SEC',sec,'kWh/kg_naphtha',page,'Body SEC statement',
            'gross_section_energy_not_net_plant_purchase')
    add('both','reference_capacity',115.,'t_ethylene/h',6,'Body reference115t/h')
    obs = pd.DataFrame(rows)
    obs.to_csv(out/'source_observations.csv',index=False)
    values = {(r.case,r.item):r.value for r in obs.itertuples()}
    get = lambda case,item: float(values[case,item])
    derived=[]; checks=[]
    for case in ['conventional','electric']:
        y=get(case,'ethylene_yield')
        electricity = get(case,'separation_electricity_consumption')
        if case=='electric':
            electricity += get(case,'cracker_electricity_consumption')+get(case,'compression_electricity_consumption')
        sec=get(case,'separation_electricity_consumption')+get(case,'separation_saturated_steam_consumption')
        sec+=get(case,'cracker_methane_consumption' if case=='conventional' else 'cracker_electricity_consumption')
        checks.append(dict(check=case+'_SEC_section_boundary',computed=sec,
            source=get(case,'reported_pyrolysis_separation_SEC'),tolerance=.005,
            passed=abs(sec-get(case,'reported_pyrolysis_separation_SEC'))<=.005,
            meaning='pyrolysis_plus_separation_gross_energy_excludes_compression_not_purchase'))
        derived.append(dict(case=case,naphtha_t_per_t_ethylene=1/y,
                            electricity_MWh_per_t_ethylene=electricity/y,
                            total_plant_TOC_at_115t_h_million_EUR2019=(get(case,'TOC_slope')*115000+get(case,'TOC_intercept')*1e6)/1e6,
                            section_SEC_kWh_per_kg_naphtha=sec))
    d=pd.DataFrame(derived);d.to_csv(out/'derived_quantities.csv',index=False)
    # Independent identities in native and converted units, including the omitted compressor.
    np.testing.assert_allclose(d.electricity_MWh_per_t_ethylene,[.083/.303,1.942/.303])
    np.testing.assert_allclose(d.naphtha_t_per_t_ethylene,[1000/303,1000/303])
    delta=float(d.electricity_MWh_per_t_ethylene.iloc[1]-d.electricity_MWh_per_t_ethylene.iloc[0])
    np.testing.assert_allclose(delta,1.859/.303)
    np.testing.assert_allclose(d.total_plant_TOC_at_115t_h_million_EUR2019,[994.49,994.49])
    assert all(c['passed'] for c in checks)
    (out/'boundary_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    package=dict(source_id='TIGGELOVEN2023_NCC',source_url=URL,source_sha256=SOURCE_SHA,
        reference_doi='10.1021/acs.iecr.3c02226',currency='EUR',price_year=2019,
        source_pdf_pages_reviewed=[4,6,7,10,11],source_edition='publisher_version',
        source_basis='naphtha cracker with electric compressor replacement; same0.303yield',
        conversion='1kWh/kg_naphtha equals1MWh/t_naphtha; divide by Table1yield for perethylene',
        delta_electricity_MWh_per_t_ethylene=delta,
        automatic_FIN_adoption=False,full_corporate_cost_ready=False,
        maintenance_formula='psi * TOC * annuity_factor (equation3), not psi * TOC',
        capital_basis='same_total_plant_curve_nth_of_kind_assumption_not_zero_retrofit_CAPEX',
        unresolved=['Table3percent_header_vs_decimal_psi; retain literal values without rescaling',
            'plant_annuity_factor_and_lifetime_not_identified_in_reviewed_main_text',
            'net_methane_disposition_and_steam_grade_conversion_require_explicit_boundary',
            'retrofit_CAPEX_construction_schedule_and_site_specific_costs_not_observed'],
        excluded_by_source=['naphtha_import_cost_in_optimization','decoking_emissions','scope3',
            'ethylene_tank_cooling_energy','direct_renewable_transmission_cost'],
        scenario_note='future_power_price_and_future_grid_CO2_profiles_are_independent_analyses_not_joint_sample',
        uncertainty_note='flexibility_ranges_are_design_sensitivities_not_probability_distributions')
    (out/'package.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
                        'font.size':10,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(9.4,3.7))
    components=[('분해로',1.476/.303),('압축기',.383/.303),('분리계통',.083/.303)]
    left=0
    for (label,val),color in zip(components,['#2d5a7b','#51a29d','#b9c7d2']):
        axes[0].barh(0,val,left=left,label=f'{label} {val:.3f}',color=color,height=.45)
        left+=val
    axes[0].barh(1,.083/.303,color='#b9c7d2',height=.45)
    axes[0].set(yticks=[0,1],yticklabels=['전기화','기존'],xlabel='전력 소비 (MWh/t 에틸렌)',xlim=(0,7.3),title='전기화는 압축기 교체까지 포함')
    axes[0].text(6.5,0,f'{left:.3f}',va='center',fontsize=9)
    axes[0].legend(loc='lower right',fontsize=8,frameon=False)
    axes[0].invert_yaxis()
    axes[1].bar(['원문 SEC\n분해·분리','전력 소비\n세 계통 합'],[2.05,1.942],color=['#b8a783','#2d5a7b'],width=.52)
    for i,val in enumerate([2.05,1.942]):axes[1].text(i,val+.035,f'{val:.3f}',ha='center')
    axes[1].set(ylim=(0,2.65),ylabel='kWh/kg 나프타',title='총에너지 지표와 전력 구매량의 구분')
    axes[1].text(.5,2.5,'SEC: 내부 증기 포함·압축기 제외',ha='center',fontsize=8.5)
    fig.subplots_adjust(left=.085,right=.975,top=.86,bottom=.25,wspace=.37)
    fig.text(.085,.055,'Tiggeloven et al. (2023), Table1 및 본문. 나프타 수율0.303 고정.\n문헌 공정 사양이며 기업 보정값·불확실성 분포가 아님. 증기와 메탄의 내부 흐름은 구매비와 구분한다.',fontsize=9,color='#555')
    figure=ROOT/'paper/methodology/figures/ncc_source_energy_boundaries.png'
    fig.savefig(figure,dpi=200);plt.close(fig)
    manifest=dict(observations=len(rows),source_visual_QA_complete=True,SEC_boundary_checks_passed=len(checks),
        derived_numeric_identities_checked=7,full_corporate_cost=False,figure=str(figure.relative_to(ROOT)))
    manifest['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [source,Path(__file__),figure,*sorted(out.glob('*.csv')),out/'package.json',out/'boundary_checks.json']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='sha256'}))


if __name__=='__main__':main()
