"""Audit the institutional author manuscript before admitting BF comparison data."""
import hashlib
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]


def main():
    pdf=ROOT/'tmp/pdfs/tcar_research_v2/fischedick_2014.pdf'
    assert pdf.read_bytes().startswith(b'%PDF')
    txt=(pdf.with_suffix('.txt')).read_text()
    for token in ['All monetary values are real values to the base year 2010','10603 MJ','1967 kg','442']:
        assert token in txt,token
    out=ROOT/'data/research_v2/fischedick_reference';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    def obs(route,field,value,unit,page,location,status='source_model_assumption'):
        rows.append(dict(observation_id=f'F2014_{route}_{field}',route=route,field=field,value=value,unit=unit,
            pdf_page=page,printed_page=page-3,location=location,status=status))
    for route,values in {'BF_BOF':(44,0,162,390,596,1254,523,190,1967,712,642,124,165,930,2,498,1051,167,1718),
        'BF_CCS':(34,140,1057,520,2117,1254,523,190,1967,552,582,124,182,182,1,345,224,193,763),
        'H_DR':(10603,0,439,2028,13070,0,1453,325,1778,0,707,0,114,821,107,0,22,280,339),
        'EW':(0,0,7235,2028,9263,0,1658,325,1983,0,545,0,114,709,0,0,275,280,555)}.items():
        fields=['energy_reductant','energy_preparation','energy_ironmaking','energy_steelmaking','energy_total',
            'ore_preparation','ore_ironmaking','scrap_steelmaking','source_label_ore_total','coal_reductant',
            'other_first_reported_stage','other_ironmaking','other_steelmaking','other_total',
            'co2_reductant','co2_preparation','co2_ironmaking','co2_steelmaking','co2_total']
        for key,value in zip(fields,values):
            obs(route,key,value,'MJ/tCS' if key.startswith('energy') else 'kg/tCS',37,'Figure A1',
                'source_model_output_moderate2050_CO2' if key.startswith('co2') else 'source_model_output; dash treated as zero for sum check only')
    for route,capex in [('BF_BOF',442),('BF_CCS',566),('H_DR',874),('EW',639)]:
        obs(route,'capex',capex,'EUR2010/(t annual capacity)',36 if route!='EW' else 37,'Tables A2–A5')
    for field,value,unit,page in [('discount_rate',.10,'fraction',35),('inflation',.03,'fraction',35),
        ('investment_period',20,'year',35),('labour',38,'EUR2010/tCS',35),('maintenance',.03,'fraction CAPEX/year',36),
        ('overhead',.10,'fraction revenue',36),('tax',.25,'fraction EBIT',36),('HRC_mass_loss',.09,'fraction',36)]:
        obs('common',field,value,unit,page,'Table A1')
    for field,value,unit in [('electrolyser_capex',450,'EUR2010/(t annual capacity)'),('DRI_EAF_capex',414,'EUR2010/(t annual capacity)'),
        ('storage_capex_approx',10,'EUR2010/(t annual capacity)'),('peak_power_share_electrolyser',.8,'fraction'),
        ('peak_power_transport_surcharge',.12,'fraction'),('oxygen_sale_price_fraction',.6,'fraction purchase price'),
        ('labour_increase',.4,'fraction above BF_BOF'),('high_grade_ore_premium',.1,'fraction')]:
        obs('H_DR',field,value,unit,36,'Table A4')
    frame=pd.DataFrame(rows);frame.to_csv(out/'source_observations.csv',index=False)
    checks=[]
    def value(route,field):return float(frame[(frame.route==route)&(frame.field==field)].value.iloc[0])
    for route in ['BF_BOF','BF_CCS','H_DR','EW']:
        for group,parts,total in [
            ('energy_sum',['energy_reductant','energy_preparation','energy_ironmaking','energy_steelmaking'],'energy_total'),
            ('CO2_sum',['co2_reductant','co2_preparation','co2_ironmaking','co2_steelmaking'],'co2_total'),
            ('ore_label_is_ore_plus_scrap',['ore_preparation','ore_ironmaking','scrap_steelmaking'],'source_label_ore_total'),
            ('other_sum',['other_first_reported_stage','other_ironmaking','other_steelmaking'],'other_total')]:
            summed=sum(value(route,k) for k in parts);reported=value(route,total)
            checks.append(dict(route=route,check=group,sum=summed,reported=reported,difference=summed-reported,
                status=('label_requires_ore_scrap_split' if group.startswith('ore_label') else 'matches') if summed==reported else 'held_unresolved'))
    pd.DataFrame(checks).to_csv(out/'internal_consistency.csv',index=False)
    manifest=dict(doi='10.1016/j.jclepro.2014.05.063',source_url='https://d-nb.info/1104202093/34',
        source_version='institutional author manuscript, not definitive publisher layout',source_local_path=str(pdf.relative_to(ROOT)),
        source_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),observations=len(rows),checks=checks,
        price_basis='All monetary values real EUR2010 per section3.2, printed p13 / PDF p16',
        heat_basis='LHV per section3.2',visual_checked_pdf_pages=[16,35,36,37],
        boundaries=['Includes reducing-agent production/transport and feed preparation',
            'Liquid/crude steel exits process; rolling excluded though HRC-linked revenue uses9% mass loss',
            'CO2 includes selected indirect burdens and coproduct credits; not direct corporate Scope1',
            'Investment period20years is not evidence every component has20year physical life'],
        full_company_cost_import_allowed=False,
        held=['H_DR CO2 stage sum409 versus printed total339 kg/tCS',
            'BF_CCS other stage sum888 versus printed total182 kg/tCS',
            'BF_BOF other stage sum931 versus printed930 kg/tCS may be rounding',
            'Source Ore total combines ore and scrap; different input prices required',
            '596MJ BF energy is not total fuel demand nor automatically purchased electricity',
            'Coal quantity and metallurgical coke price cannot be equated without coking yield/procurement mapping',
            'Other materials and exported process gases/slag lack a complete independently priced quantity split'],
        source_access_note='Wuppertal endpoint returned bot-protection HTML; used German National Library deposited author manuscript without bypassing protection')
    manifest['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'source_observations.csv',out/'internal_consistency.csv']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'observations':len(rows),'checks':len(checks),'held_checks':sum(x['status']=='held_unresolved' for x in checks)}))

if __name__=='__main__':main()
