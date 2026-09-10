"""Freeze primary historical factors and their conflicting republications."""
from pathlib import Path
import hashlib
import json
import re
import sys

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap.grid_factors import CONTEXT_FIELDS,select_grid_factor


def main():
    raw=ROOT/'tmp/pdfs/grid_factors';out=ROOT/'data/research_v2/grid_factors'
    out.mkdir(parents=True,exist_ok=True)
    access=json.loads((raw/'access.json').read_text())
    for r in access:
        assert hashlib.sha256((raw/r['file']).read_bytes()).hexdigest()==r['sha256']
    urls={r['file']:r['url'] for r in access}
    observations=[];registry=[]
    # Values and their row/column positions were visually checked against PDF.
    groups=[('gir2024.pdf',2024,2020,2022,'period_average',[.4172,.4150,.0044,.0077,.4541,.4517,.0048,.0084]),
            ('gir2025.pdf',2025,2023,2023,'single_year',[.3844,.3822,.0069,.0075,.4173,.4149,.0075,.0081]),
            ('gir2025.pdf',2025,2021,2023,'period_average',[.3986,.3964,.0053,.0075,.4330,.4307,.0057,.0082])]
    for file,approval,start,end,statistic,vals in groups:
        text=(raw/file.replace('.pdf','.txt')).read_text().split('\f')[0]
        for i,value in enumerate(vals):
            assert f'{value:.4f}' in text
            gas=['CO2e','CO2','CH4','N2O'][i%4]
            boundary='generation' if i<4 else 'consumption'
            identifier=f'KOR_GIR{approval}_{start}_{end}_{boundary}_{gas}'
            r=dict(identifier=identifier,country='KOR',gas=gas,
                   gwp_basis=('AR5' if approval==2025 else 'unspecified') if gas=='CO2e' else 'not_applicable',
                   energy_boundary=boundary,accounting_basis='national_inventory_2006IPCC',
                   period_start=start,period_end=end,statistic=statistic,allowed_use='regional_reference',
                   status='verified_primary',unit=f'{"t" if i%4<2 else "kg"}{gas}/MWh',value=value,
                   source_url=urls[file],source_file=str((raw/file).relative_to(ROOT)),pdf_page=1,
                   source_label=f'{approval} approval; {start}-{end}; {boundary}; {gas}',
                   approval_year=approval,publication_date='2025-12-18' if approval==2025 else '2025-03-31',
                   corporate_application_verified=False)
            observations.append(r);registry.append(r)
        # Positive non-CO2 gases cannot reduce the CO2-equivalent total.
        assert vals[0]>=vals[1] and vals[4]>=vals[5]
    # Official republisher differs from the approving authority.
    kea=(raw/'kea.html').read_text()
    assert '<td>0.3896</td>' in kea
    assert '.3986' in (raw/'gir2025.txt').read_text()
    observations.append(dict(identifier='KOR_KEA_republished_2021_2023_generation_CO2e',country='KOR',
                             value=.3896,unit='tCO2e/MWh',status='held_conflict',
                             source_url=urls['kea.html'],source_file=str((raw/'kea.html').relative_to(ROOT)),
                             source_label='2021-2023 generation CO2e; conflicts with GIR .3986'))
    for year,status,emissions,factor,file in [(2024,'verified_primary',3.14,.422,'elcs_final.html'),
                                            (2023,'verified_primary',3.12,.422,'elcs_final.html'),
                                            (2024,'superseded',3.09,.416,'elcs_provisional.html')]:
        html=(raw/file).read_text()
        assert str(emissions) in html and str(factor) in html
        r=dict(identifier=f'JPN_ELCS_FY{year}_{status}_CO2',country='JPN',gas='CO2',gwp_basis='not_applicable',
               energy_boundary='consumption',accounting_basis='ELCS_adjusted_member_aggregate',
               period_start=year,period_end=year,statistic='fiscal_year',allowed_use='regional_reference',
               status=status,unit='kgCO2/kWh',value=factor,source_url=urls[file],
               source_file=str((raw/file).relative_to(ROOT)),source_label=f'ELCS FY{year} adjusted member aggregate',
               publication_date='2026-03-12' if file=='elcs_final.html' else '2025-09-12',
               corporate_application_verified=False)
        registry.append(r);observations.append(r)
        observations.append(dict(identifier=r['identifier']+'_emissions',country='JPN',value=emissions,
                                 unit='100million_tCO2',status=status,source_url=urls[file],
                                 source_file=r['source_file'],source_label=r['source_label']))
    fepc=(raw/'fepc2025.txt').read_text().split('\f')[101]
    for key,value,unit,token in [('displayed_emissions',3.14,'100million_tCO2','3.14'),
                                ('bracketed_emissions',3.09,'100million_tCO2','3.09'),
                                ('consumption',7430,'100million_kWh','7,430'),
                                ('displayed_factor',.416,'kgCO2/kWh','0.416'),
                                ('bracketed_factor',.423,'kgCO2/kWh','0.423')]:
        assert token in fepc
        observations.append(dict(identifier='JPN_FEPC2025_FY2024_'+key,country='JPN',value=value,unit=unit,
                                 status='held_conflict',source_url=urls['fepc2025.pdf'],
                                 source_file=str((raw/'fepc2025.pdf').relative_to(ROOT)),pdf_page=102,
                                 source_label='printed98;FY2024 column; literal value retained, no automatic repair'))
    jp=(raw/'jp_r08_rev4.txt').read_text().split('\f')[17]
    for key,value in [('substitute',.000416),('certificate_national_average',.000423)]:
        assert f'{value:.6f}' in jp
        observations.append(dict(identifier='JPN_R8_rev4_'+key,country='JPN',value=value,unit='tCO2/kWh',
                                 status='verified_reporting_parameter_not_grid_proxy',source_url=urls['jp_r08_rev4.pdf'],
                                 source_file=str((raw/'jp_r08_rev4.pdf').relative_to(ROOT)),pdf_page=18,
                                 source_label='FY2025 emissions reporting inFY2026; table dated2026-08-03; '+key))
    pd.DataFrame(observations).to_csv(out/'source_observations.csv',index=False)
    (out/'factor_registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    selected=[];rejected=[]
    for r in registry:
        try:selected.append(select_grid_factor(registry,r['identifier'],context={k:r[k] for k in CONTEXT_FIELDS}))
        except ValueError as e:rejected.append(dict(identifier=r['identifier'],reason=str(e)))
    (out/'normalized_reference_factors.json').write_text(json.dumps(selected,indent=2)+'\n')
    conflicts=[dict(issue='KEA_republication',reported=.3896,primary=.3986,decision='use_GIR; preserve_republication_conflict'),
               dict(issue='ELCS_provisional_to_final_FY2024',reported=.416,primary=.422,decision='final_for_latest_adjusted_ELCS_reference;not_location_grid'),
               dict(issue='FEPC_displayed_pair',reported_factor=.416,emission_div_consumption=3.14/7430*1000,decision='held;displayed_pair_not_arithmetically_coherent'),
               dict(issue='FEPC_bracketed_pair',reported_factor=.423,emission_div_consumption=3.09/7430*1000,decision='held;do_not_infer_correction_or_mix_vintages'),
               dict(issue='Japan_reporting_table',decision='nominalFY2024;menuFY2025;reportFY2026;not_one_uniform_observation_year;administrativefactorsnotlocationgrid')]
    (out/'source_decisions.json').write_text(json.dumps(dict(conflicts=conflicts,rejected_for_selection=rejected,
        no_national_rank=True,no_regional_MC=True,no_future_grid_extrapolation=True,
        Korea_source2024_CO2e_GWP_not_identified_on_extracted_page=True,
        Japan_adjusted_ELCS_cannot_replace_location_based_grid=True),indent=2)+'\n')
    report=dict(source_numeric_observations=len(observations),registry_records=len(registry),
                normalized_reference_records=len(selected),selection_rejections=len(rejected),
                primary_PDFs_visually_reviewed=4,primary_PDF_pages_visually_reviewed=6,
                corporate_calibration=False,existing_workbook_modified=False,
                source_sha256={str((raw/r['file']).relative_to(ROOT)):r['sha256'] for r in access},
                implementation_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'src/cap/grid_factors.py']},
                artifact_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='manifest.json'})
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if not k.endswith('sha256')})


if __name__=='__main__':main()
