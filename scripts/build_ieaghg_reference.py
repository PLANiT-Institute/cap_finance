"""Transcribe same-boundary IEAGHG reference/MEA capture cash accounts.

The official PDF's web text was reviewed; local download and visual inspection
were unavailable. This is a provisional source transcription, not approval of
these idealised 2013 process cases as current corporate technology specifications.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://ieaghg.org/publications/2013-04%20Iron%20and%20Steel%20CCS%20Study%20(Techno-Economics%20Integrated%20Steel%20Mill).pdf'
CASES = ['REFERENCE', 'EOP_L1', 'EOP_L2']


def main():
    # PDF pages are one-based physical pages, not printed section page numbers.
    native = {
        'maintenance': [141996.10, 169902.80, 179996.35],
        'direct_labour': [204580.78, 208246.78, 208622.78],
        'indirect_labour': [76140., 76140., 76140.],
        'energy_reductant': [483937.74, 615480.92, 666361.92],
        'iron_ore': [492053.74, 492053.74, 492053.74],
        'scrap_alloys': [218228.11, 218228.11, 218228.11],
        'flux': [44649.89, 44649.89, 44649.89],
        'consumables_utilities': [49780.77, 67942.82, 71326.10],
        'miscellaneous': [62246.77, 62246.77, 62246.77],
        'other_opex': [8181.34, 11333.92, 12068.56],
        'coke_byproducts_credit': [21422.91]*3,
        'bf_slag_credit': [17780.03]*3,
        'ld_slag_credit': [449.81]*3,
        'argon_credit': [14017.68]*3,
        'reported_fixed_total': [422716.88, 454289.58, 464759.13],
        'reported_variable_total': [1359078.36, 1511936.17, 1566935.10],
    }
    rows=[]
    for item, values in native.items():
        for case, value in zip(CASES, values):
            rows.append(dict(case=case, item=item, value=value, unit='thousand_source_USD/year',
                pdf_page=304, location='Volume II D-27 Table D-15; operating years 4-25',
                status='web_text_transcribed_visual_review_pending', source_url=URL))
    extra = [
        ('initial_capex', [4124.,5038.,5321.], 'million_source_USD',289,'Volume II D-12 Table D-4'),
        ('reline_capex',[232.]*3,'million_source_USD',289,'Volume II D-12 Table D-4'),
        ('direct_co2',[2090.14,1041.73,827.42],'kg_CO2/t_HRC',305,'Volume II D-28 Table D-15 CO2 avoidance'),
        ('rounded_ng_bill',[33.20,164.75,215.63],'million_source_USD/year',294,'Volume II D-17 Table D-8'),
        ('output',[4e6]*3,'t_HRC/year',304,'Volume II D-27 Table D-15'),
    ]
    for item,values,unit,page,location in extra:
        for case,value in zip(CASES,values):
            rows.append(dict(case=case,item=item,value=value,unit=unit,pdf_page=page,
                location=location,status='web_text_transcribed_visual_review_pending',source_url=URL))
    bundle_quantities={'coal_hard':1257292.,'coal_soft':838194.,'coal_PCI':603251.,
        'ore_fines_Brazil':2923276.,'ore_fines_Australia':352202.,'ore_fines_Sweden':246541.,
        'ore_lump_Australia':497139.,'ore_pellet_Brazil':1417721.}
    for item,value in bundle_quantities.items():
        rows.append(dict(case='ALL',item=item,value=value,unit='source_reported_t/year',
            pdf_page=169 if item.startswith('coal') else 170,
            location='Volume I E-29 Table E-9' if item.startswith('coal') else 'Volume I E-30 Table E-10',
            status='web_text_transcribed_visual_review_pending',source_url=URL))
    for item,value,unit,page,loc in [
        ('reference_ng_quantity',3398486.,'GJ/year',191,'Volume I E-51 Table E-35'),
        ('ng_price',9.77,'source_USD/GJ',169,'Volume I E-29 section 5.2.2'),
        ('reference_ng_quantity_conflicting',2.9268e6,'GJ/year',169,'Volume I E-29 section 5.2.2; PJ converted to GJ'),
        ('reported_reference_ng_bill',33.203e6,'source_USD/year',191,'Volume I E-51 Table E-35'),
    ]:
        rows.append(dict(case='REFERENCE',item=item,value=value,unit=unit,pdf_page=page,
            location=loc,status='held_conflict' if 'conflicting' in item else 'web_text_transcribed_visual_review_pending',source_url=URL))
    ng_ref=3398486.; ng_price=9.77
    coal_bill=native['energy_reductant'][0]*1000-ng_ref*ng_price
    fixed_keys=['maintenance','direct_labour','indirect_labour']
    var_keys=['energy_reductant','iron_ore','scrap_alloys','flux','consumables_utilities','miscellaneous','other_opex']
    credit_keys=[k for k in native if k.endswith('_credit')]
    checks=[];cases={}
    for i,case in enumerate(CASES):
        for group,keys in [('fixed',fixed_keys),('variable',var_keys)]:
            computed=sum(native[k][i] for k in keys)*1000
            reported=native['reported_'+group+'_total'][i]*1000
            checks.append(dict(case=case,check=group+'_account_sum',computed=computed,reported=reported,
                tolerance_source_USD=50.,passed=bool(abs(computed-reported)<=50.)))
        gas=ng_ref+(native['energy_reductant'][i]-native['energy_reductant'][0])*1000/ng_price
        rounded=extra[3][1][i]*1e6
        checks.append(dict(case=case,check='gas_bill_vs_independent_rounded_D8',computed=gas*ng_price,
            reported=rounded,tolerance_source_USD=5000.,passed=bool(abs(gas*ng_price-rounded)<=5000.)))
        gross=sum(native[k][i] for k in fixed_keys+var_keys)*1000
        credit=sum(native[k][i] for k in credit_keys)*1000
        cases[case]=dict(initial_capex_source_USD=extra[0][1][i]*1e6,
            reline_source_USD=232e6,output_t_HRC=4e6,direct_co2_t_per_t_HRC=extra[2][1][i]/1000,
            ng_GJ=gas,ng_quantity_status='source_table_E35' if i==0 else 'cost_implied_from_D15_fuel_difference_at_9.77_USD_GJ',
            coal_bundle_source_USD=coal_bill,ore_bundle_source_USD=native['iron_ore'][i]*1000,
            gross_opex_source_USD=gross,byproduct_credit_source_USD=credit,
            residual_fixed_price_opex_source_USD=gross-credit-gas*ng_price-coal_bill-native['iron_ore'][i]*1000,
            source_components={k:native[k][i]*1000 for k in fixed_keys+var_keys+credit_keys})
    checks.append(dict(case='REFERENCE',check='conflicting_prose_ng_bill',computed=2.9268e6*ng_price,
        reported=33.203e6,tolerance_source_USD=1000.,passed=bool(abs(2.9268e6*ng_price-33.203e6)<=1000.)))
    assert all(c['passed'] for c in checks[:-1]) and not checks[-1]['passed']
    out=ROOT/'data/research_v2/ieaghg_reference';out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'source_observations.csv',index=False)
    pd.DataFrame(checks).to_csv(out/'account_checks.csv',index=False)
    package=dict(package_id='IEAGHG2013_04_HRC_REFERENCE_EOP', source=dict(url=URL,
        local_pdf_sha256=None,access='official PDF web text; screenshot attempts returned no inspectable image',
        visual_review_complete=False), unit_of_account='USD_source_report_basis',uniform_real_price_year_verified=False,
        capital_basis='equipment adjusted to 2010; +/-30% accuracy is not a probability distribution',
        operating_price_basis='source long-term trend price assumptions; not asserted to be uniformly USD2010',
        ng_price_source_USD_GJ=ng_price,cases=cases,bundle_quantities_source_t=bundle_quantities,
        bundles={'coal':'One annual source coal mix: hard1257292t,soft838194t,PCI603251t; source moisture8%; basket bill reconciled to D15 total less E35 NG. No dry/wet conversion inferred.',
                 'ore':'One annual source iron-ore mix for4MtHRC. Price-index exposure applies to the whole fixed basket, not a tonne of homogeneous iron ore.'},
        boundary={'output':'4Mt/year standard HRC; includes coke,sinter,BF,BOF,casting,rolling,lime,ASU,power,steam,capture/compression',
                  'grid_import_MWh':0,'grid_export_MWh':0,'internal_transfers_billed':False,
                  'direct_co2':'on-site boundary as defined by source; not lifetime/net lifecycle reduction',
                  'CO2_transport_storage_included':False,'carbon_price_included':False,
                  'greenfield_cost_not_retrofit_quote':True},
        limits=['Provisional web-text transcription; PDF visual QA unavailable',
                'Western Europe conceptual design; no Korea/Japan company calibration',
                'Unchanged core iron/steel operation and coproduct revenue across EOP cases are source assumptions',
                'Operating accounts are steady-state years4-25; construction/ramp/working capital must be specified separately',
                'Only BF reline every15th operating year is included as source recurring capital',
                'No backup natural gas, CO2 transport/storage, taxes, financing, working capital or end-of-life cashflow in this package',
                'Source E35 labels electricity intensity MWh/t instead of the dimensional kWh/t; this field is not used',
                'Source prose2.9268PJ conflicts with E35 gas and cost; conflicting field held, not averaged'])
    (out/'package.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
    manifest=dict(observations=len(rows),account_checks=len(checks),passed=sum(c['passed'] for c in checks),
        held=sum(not c['passed'] for c in checks),external_source_validation_complete=False,
        source_visual_review_complete=False,source_url=URL,
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'package.json',out/'source_observations.csv',out/'account_checks.csv',Path(__file__)]})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='sha256'}))


if __name__=='__main__':main()
