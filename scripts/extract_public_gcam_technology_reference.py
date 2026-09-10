"""Read pinned official GCAM inputs into native-key reference tables.

This is not a GCAM model run, a KAIST data import, or NGFS6.0 calibration.
Keep raw default coefficients distinct from regional overrides and solved outputs.
"""
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"tmp/pdfs/tcar_research_v2/gcam_public"
OUT=ROOT/"data/research_v2/gcam_reference"


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    access={Path(r['path']).name:r for r in json.loads((RAW/'download_manifest.json').read_text())}

    def read(name):
        b=(RAW/name).read_bytes()
        assert hashlib.sha256(b).hexdigest()==access[name]['sha256'],name
        lines=b.decode('utf-8-sig').splitlines()
        return list(csv.DictReader(io.StringIO('\n'.join(l for l in lines if not l.startswith('#')))))

    def save(name,rows):
        with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

    name='A323.globaltech_coef.csv';coef=read(name);rows=[]
    for r in coef:
        for year in [2025,2100]:
            v=float(r[str(year)]);carrier=r['minicam.energy.input']
            assert v>=0,(r,year)
            unit='t_scrap/t_GCAM_steel' if carrier=='scrap' else 'GJ/t_GCAM_steel'
            display_value=v;display_unit=unit;conversion='identity'
            if carrier=='elect_td_ind':
                display_value=v/3.6;display_unit='MWh/t_GCAM_steel';conversion='GJ/3.6=MWh'
            elif carrier=='H2 industrial':
                display_value=v/.12;display_unit='kgH2/t_GCAM_steel';conversion='GJ/0.12; LHV120GJ/tH2 per CMP415; verify against delivered commodity metadata'
            rows.append(dict(steel_region=r['steel_region'],supplysector=r['supplysector'],subsector=r['subsector'],
                technology=r['technology'],native_input=carrier,year=year,native_value=v,native_unit=unit,
                display_value=display_value,display_unit=display_unit,conversion=conversion,
                source_url=access[name]['url'],source_sha256=access[name]['sha256'],repository_commit=access[name]['repository_commit'],
                evidence_scope='public_default_input_not_solved_regional_scenario',KAIST_version_match_verified=False,
                use_status='reference_only_not_FIN_import'))
    save('steel_default_energy_coefficients.csv',rows)
    region_rows=[]
    for r in read('A_regions.csv'):
        if r['region'] not in ('South Korea','Japan'):continue
        region_rows.append(dict(FIN_region='Korea' if r['region']=='South Korea' else 'Japan',
            public_GCAM_region=r['region'],public_GCAM_region_ID=r['GCAM_region_ID'],steel_region=r['steel_region'],
            source_url=access['A_regions.csv']['url'],source_sha256=access['A_regions.csv']['sha256'],
            KAIST_region_match_verified=False))
    assert len(region_rows)==2
    save('region_crosswalk.csv',region_rows)
    chemistry=[]
    for r in read('A325.globaltech_coef.csv'):
        chemistry.append(dict(**r,native_unit='EJ/EJ',source_url=access['A325.globaltech_coef.csv']['url'],
            source_sha256=access['A325.globaltech_coef.csv']['sha256'],
            interpretation='aggregate_energy_service_and_feedstock_weights_not_ethylene_mass_yield_or_process_energy_intensity',
            FIN_per_tonne_import_allowed=False))
    save('chemical_aggregate_coefficients.csv',chemistry)
    crosswalk=[]
    mappings=[
        ('steel_h2dri','iron and steel','EAF with DRI','Hydrogen-based DRI','partial_process_specification',
         'CMP415 cites Zang2023 75%DRI feed to EAF with83%H2/17%NG reductant energy; native2025 inputs7.3GJ_H2,4.2GJ_electricity,1.1GJ_liquids,3.6GJ_gas; differs from FIN pureH2 assumptions'),
        ('steel_eaf','iron and steel','EAF with scrap','EAF with scrap','partial_process_specification','Full GCAM steel boundary is broader than an EAF component coefficient'),
        ('steel_h2inj','iron and steel','BLASTFUR','BLASTFUR with hydrogen','partial_process_specification','H2 injection rate and displaced incumbent fuels differ'),
        ('steel_hyrex','','','','unmapped','Fluidized reduction and melting route not verified as an exact native technology'),
        ('petchem_ecracker','chemical energy use','electricity','electricity','aggregate_only','Requires external NCC process DB; no per-ethylene functional unit in native sector'),
        ('petchem_h2fuel','chemical energy use','hydrogen','hydrogen','aggregate_only','Aggregate hydrogen energy service does not identify a cracker furnace'),
    ]
    with (ROOT/'tmp/research_case_v3/data/D3_tech_options.csv').open(encoding='utf-8-sig') as f:
        known_FIN_ids={r['tech_id'] for r in csv.DictReader(f)}
    for fin,sector,sub,tech,kind,reason in mappings:
        assert fin in known_FIN_ids,fin
        if sector=='iron and steel':
            assert any(r['supplysector']==sector and r['subsector']==sub and r['technology']==tech for r in coef)
        elif sector=='chemical energy use':
            assert any(r['supplysector']==sector and r['subsector']==sub and r['technology']==tech for r in read('A325.globaltech_eff.csv'))
        crosswalk.append(dict(FIN_tech_id=fin,public_GCAM_supplysector=sector,public_GCAM_subsector=sub,
            public_GCAM_technology=tech,mapping_kind=kind,reason=reason,KAIST_mapping_confirmed=False,
            automatic_parameter_replacement_allowed=False,repository_commit=access[name]['repository_commit']))
    save('technology_crosswalk.csv',crosswalk)
    h2=[r for r in rows if r['technology']=='Hydrogen-based DRI' and r['year']==2025]
    assert len(h2)==4
    total=sum(r['native_value'] for r in h2)
    assert abs(total-16.2)<1e-10
    # Published R processing divides non-scrap GJ/t coefficients by1000 for GJ/kg.
    code=(RAW/'zenergy_L2323.iron_steel.R').read_text()
    assert 'round(coefficient/1000, energy.DIGITS_COEFFICIENT)' in code
    assert 'L1323.IO_GJkg_R_iron_steel_F_Yh' in code
    result=dict(repository_commit=access[name]['repository_commit'],native_steel_energy_rows=len(rows),
        distinct_steel_technologies=len(set(r['technology'] for r in rows)),
        selected_regions=len(region_rows),crosswalk_rows=len(crosswalk),
        h2_DRI_2025_total_energy_GJ_per_t=total,
        hydrogen_2025_kg_per_t_with_LHV120=7.3/.12,electricity_2025_MWh_per_t=4.2/3.6,
        chemical_unit='EJ/EJ; no t_ethylene functional unit',
        steel_XML_unit='GJ/kg = EJ/Mt; input CSV GJ/t must divide by1000',
        native_steel_price_unit='1975$/kg',
        unresolved=['KAIST model version, configuration and overrides unavailable',
                    'Default CSV is not solved regional scenario output',
                    'Zang2023 Table1 and section3.2 confirm75%DRI feed and83%H2 energy; complete numeric original-source-to-GCAM reconciliation still needed',
                    'Non-energy price includes costs beyond investment and must not be treated as CAPEX',
                    'GCAM chemical energy/feedstock sectors do not identify a specific ethylene cracker'],
        GCAM_executed=False,KAIST_values_received=False,FIN_inputs_changed=False)
    (OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
