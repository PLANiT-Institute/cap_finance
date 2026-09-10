"""Source-specific steel material/energy/cost bundles with visible discrepancies.

Vogl2018: rounded main-text onsite H2-DR-EAF annualized cost reconstruction.
Radloff2023: structured SI tables for H2-DR-MU-BOF; unresolved cells retained.
Neither bundle is automatically a current Korean/Japanese company input.
"""
from pathlib import Path
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'tmp/pdfs/tcar_research_v2'
OUT=ROOT/'data/research_v2/steel_cost_reference'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def crf(rate,years):return rate/(1-(1+rate)**-years)


def read_si(path):
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    r=ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'))
    def text(e):return ''.join(x.text or '' for x in e.iter() if x.tag.endswith('}t'))
    return [[[text(cell) for cell in row.findall('w:tc',ns)]
             for row in table.findall('w:tr',ns)] for table in r.findall('.//w:tbl',ns)]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=RAW/'vogl_2018.pdf'
    assert sha(source)=='3b3654ceb0b9d332f0ac4676c56ff525544b6dda7633bfb30eb23943278684da'
    vp={'doi':'10.1016/j.jclepro.2018.08.279',
        'url':'https://www.p-plus.nl/resources/articlefiles/Staal-van-waterstof.pdf',
        'local_path':str(source.relative_to(ROOT)),'sha256':sha(source)}
    records=[]
    def obs(key,value,unit,page,role,description):
        records.append(dict(observation_id='VC_'+key,source_doi=vp['doi'],source_sha256=vp['sha256'],
            pdf_page=page,printed_page=735+page,value=value,unit=unit,role=role,
            native_value=value,native_unit=unit,conversion='identity',
            description=description,status='published_model_assumption_or_rounded_result'))
        return value
    flows=[]
    def purchase(key,q,qunit,price,pageq,pagep):
        obs(key+'_quantity',q,qunit, pageq,'purchased','0% scrap onsite H2 route')
        records[-1].update(native_value=q*1000,native_unit='kg/tLS',conversion='kg/1000 -> t')
        obs(key+'_price',price,'EUR/'+qunit.split('/')[0],pagep,'source_price_assumption','2015–2018 source price range; no common currency year verified')
        if key=='graphite_electrodes':
            records[-1].update(native_value=price/1000,native_unit='EUR/kg',conversion='EUR/kg *1000 -> EUR/t')
        flows.append(dict(flow_id=key,quantity=q,quantity_unit=qunit,role='purchased',
            source_quantity='VC_'+key+'_quantity',source_price='VC_'+key+'_price',price_EUR=price))
    purchase('pellets',1.504,'t/tLS',100,4,3)
    purchase('lime',.05,'t/tLS',100,3,4)
    purchase('alloys',.011,'t/tLS',1777,4,4)
    purchase('graphite_electrodes',.002,'t/tLS',4000,4,4)
    electricity=obs('electricity',3.48,'MWh/tLS',4,'purchased','Total onsite process, including electrolysis; excludes downstream casting/rolling and upstream pelletization')
    obs('hydrogen',51.,'kgH2/tLS',4,'internal_transfer','No H2 losses; do not additionally purchase this hydrogen')
    oxygen=obs('oxygen',.411,'tO2/tLS',6,'potential_export','Gross oxygen generation, rounded')
    records[-1].update(native_value=411,native_unit='kgO2/tLS',conversion='kg/1000 -> t')
    sale=obs('oxygen_sale_fraction',.6,'fraction_of_generation',4,'saleability_assumption','Assumes nearby oxygen market; not verified at target plants')
    po=obs('oxygen_price',60.8,'EUR/tO2',4,'source_price_assumption','Gross selling price, separate conditioning costs unresolved')
    labour=obs('labour',53.2,'EUR/tLS',4,'operating_cost','Source cost assumption')
    om=obs('OM_fraction',.03,'fraction_CAPEX_per_year',4,'operating_cost','Includes refractory lining; not capital renewal cash')
    rate=obs('interest_rate',.05,'fraction',4,'financing_assumption','Annualized source comparison, not a prescribed corporate discount rate')
    capital=[]
    for key,value,life in [('electrolyser',160.,10),('shaft',230.,20),('EAF',184.,20)]:
        obs(key+'_capex',value,'EUR/(tLS/year_capacity)',6,'capital','2030 technology assumption in source')
        obs(key+'_lifetime',life,'years',4,'capital','Annualization life')
        capital.append(dict(component=key,capex_EUR_per_t_annual_capacity=value,lifetime_years=life))
    totalcap=sum(c['capex_EUR_per_t_annual_capacity'] for c in capital)
    annualcap=sum(c['capex_EUR_per_t_annual_capacity']*crf(rate,c['lifetime_years']) for c in capital)
    material=sum(f['quantity']*f['price_EUR'] for f in flows)
    rows=[]
    for power_price in (20.,40.,60.,80.,100.):
        for oxygen_sale in (0.,sale):
            total=material+electricity*power_price+labour+om*totalcap+annualcap-oxygen*oxygen_sale*po
            rows.append(dict(power_price_EUR_MWh=power_price,oxygen_sale_fraction=oxygen_sale,
                materials_EUR_t=material,power_EUR_t=electricity*power_price,
                labour_EUR_t=labour,OM_EUR_t=om*totalcap,annualized_capital_EUR_t=annualcap,
                oxygen_credit_EUR_t=oxygen*oxygen_sale*po,total_EUR_t=total,
                electricity_cost_share=electricity*power_price/total,
                status='main_text_annualized_cost_reconstruction_not_project_cash_NPV'))
    base40=next(r for r in rows if r['power_price_EUR_MWh']==40 and r['oxygen_sale_fraction']==sale)
    base80=next(r for r in rows if r['power_price_EUR_MWh']==80 and r['oxygen_sale_fraction']==sale)
    assert totalcap==574 and abs(oxygen*sale*po-14.9)<.15
    # Published headline range361–640 reproduced only to rounded-input precision.
    lo=next(r['total_EUR_t'] for r in rows if r['power_price_EUR_MWh']==20 and r['oxygen_sale_fraction']==sale)
    hi=next(r['total_EUR_t'] for r in rows if r['power_price_EUR_MWh']==100 and r['oxygen_sale_fraction']==sale)
    assert abs(lo-361)<1.5 and abs(hi-640)<1.5
    bundle=dict(package_id='VOGL2018_MAIN_TEXT_ONSITE_COST',source=vp,
        functional_unit='1 t liquid steel; 0% scrap; continuous onsite electrolysis',
        electricity_MWh_t=electricity,hydrogen_purchase_kg_t=0.,purchases=flows,
        oxygen=dict(generated_t_t=oxygen,sale_fraction=sale,price_EUR_t=po),capital_components=capital,
        labour_EUR_t=labour,OM_fraction_CAPEX=om,source_interest_rate=rate,
        annualized_capital_EUR_t=annualcap,price_basis='Source2015–2018 commodity assumptions plus projected2030 equipment; no uniform price-year established',
        current_company_input_approved=False,full_engineering_balance_verified=False,
        limits=['Supplementary Vogl model not obtained; rounded main text reconstruction',
                'No purge/compression/HBI compaction losses added; source simplifications retained',
                'Carbon addition quantity/cost not resolved; oxygen conditioning costs unresolved',
                'Do not charge onsite H2 or upstream pelletizing power in addition to purchased pellets',
                'Annualized capital must be replaced by dated cash investment for TCaR; never add both',
                'Different component lives require electrolyser renewal separate from EAF/shaft'],
        audit=dict(capex_sum=totalcap,reported_oxygen_credit=14.9,reconstructed_oxygen_credit=oxygen*sale*po,
            reconstructed_range=[lo,hi],reported_range=[361,640],
            reported_energy_share_40=.32,reconstructed_energy_share_40=base40['electricity_cost_share'],
            reported_energy_share_80=.47,reconstructed_energy_share_80=base80['electricity_cost_share'],
            energy_share_80_status='unresolved_discrepancy; do not force fit inputs'))
    (OUT/'vogl_main_text_package.json').write_text(json.dumps(bundle,indent=2)+'\n')
    for name,data in [('vogl_observations.csv',records),('vogl_cost_reconstruction.csv',rows)]:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)

    # A distinct MU–BOF route, not an alternative EAF coefficient to average in.
    si=RAW/'radloff_2023_si.docx';meta=json.loads(si.with_suffix('.json').read_text())
    assert sha(si)==meta['sha256']=='7efe5843ad0e2c53b05a25664cc4a5f6c3f239db8a0e40150db6311fa91d8775'
    tables=read_si(si);assert len(tables)==6
    native=[]
    for table_no,table in enumerate(tables,start=2):
        for ri,row in enumerate(table[1:],start=2):
            for ci,cell in enumerate(row,start=1):
                native.append(dict(source_doi='10.1111/jiec.13387',source_sha256=sha(si),
                    table=f'S{table_no}',row=ri,column=ci,column_heading=table[0][ci-1],native_text=cell,
                    status='native_cell_not_automatically_adopted'))
    with (OUT/'radloff_si_native_cells.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(native[0]));w.writeheader();w.writerows(native)
    params={r[0]:dict(value=r[1],unit=r[2],note=r[3]) for r in tables[1][1:]}
    flow_rows=[];last=''
    for row in tables[3][1:]:
        last=row[0] or last
        flow_rows.append(dict(flow=last,process=row[1],input=float(row[2].replace(',','.')),
                              output=float(row[3].replace(',','.')),unit=row[4]))
    def number(v):return float(v.replace(',','.'))
    def flow(name,process=None,side='input'):
        selected=[r for r in flow_rows if r['flow']==name and (process is None or r['process']==process)]
        assert selected,(name,process)
        return sum(r[side] for r in selected)
    costs={r[0]:number(r[1]) for r in tables[2][1:]}
    categories={r[0]:number(r[1]) for r in tables[4][1:]}
    material_items={
        'pellets':flow('Pellets')*costs['Price of iron ore pellets'],
        'scrap':flow('Scrap')*costs['Price of scrap'],
        'quicklime':flow('Quicklime')*costs['Price of quicklime'],
        'carbon':flow('Carbon')*costs['Price of coal for MU'],
        'alloys':costs['Consumption of alloy elements']*costs['Price of alloy elements']}
    # Left sides derive from extracted cells; right-side main-text values are
    # independently transcribed rounded findings, not silently fitted targets.
    checks=[dict(name='power_sum',left=flow('Power'),right=3070,tolerance=5,status='rounding_compatible'),
        dict(name='BOF_quicklime_input',left=number(params['Quicklime feed to BOF']['value']),right=flow('Quicklime','BOF'),tolerance=.001,status='held_S3_vs_S5_conflict'),
        dict(name='slag_total',left=flow('Slag',side='output'),right=.220,tolerance=.002,status='held_S5_vs_main_text_conflict'),
        dict(name='oxygen_surplus',left=flow('O2','ELEC','output')-flow('O2','BOF'),right=flow('O2','O2EXCESS'),tolerance=.0001,status='rounding_compatible'),
        dict(name='pelletizing_emissions',left=flow('Pellets')*number(params['Emission intensity of pelletizing']['value'])/1000,right=flow('CO2','PELL','output'),tolerance=1e-9,status='matches'),
        dict(name='direct_CO2',left=flow('CO2','MU','output')+flow('CO2','BOF','output'),right=.201,tolerance=1e-9,status='matches'),
        dict(name='cost_categories',left=sum(v for k,v in categories.items() if k!='Total specific costs'),right=categories['Total specific costs'],tolerance=1e-9,status='matches'),
        dict(name='resource_cost_reconstruction',left=sum(material_items.values()),right=categories['Resource costs'],tolerance=1.,status='held_partial_reconstruction_vs_S6')]
    assert all(abs(c['left']-c['right'])<=c['tolerance'] for c in checks if c['status'] in ('matches','rounding_compatible'))
    r_bundle=dict(package_id='RADLOFF2023_H2_DR_MU_BOF',source=meta,doi='10.1111/jiec.13387',
        functional_unit='1 t liquid steel; onsite electrolysis; approximately20% BOF scrap charge',
        route='H2 direct reduction + hot melting unit + retained BOF, not DRI-EAF',
        source_parameters=params,source_flow_rows=flow_rows,checks=checks,
        costs_source_table_S4=tables[2],reported_costs_S6=tables[4],reported_sensitivity_S7=tables[5],
        resource_reconstruction_EUR_t=material_items,
        evidence_note='Structured SI cells, display text only; embedded citation-field codes excluded',
        price_basis='Mixed historical commodity assumptions and projected costs, uniform price-year not established',
        complete_company_cost_import_allowed=False,
        unresolved=['Quicklime input conflict; no silent decimal correction',
                    'Slag mass differs between S5 and main text',
                    'S4 prices times S5 material quantities plus S4 alloys give232.68 vs S6 resource cost237 EUR/t; composition or input discrepancy unresolved',
                    'Oxygen sale fraction denominator: gross generation vs surplus not unambiguously specified',
                    'S2 gas cycle denominator and S5 per-liquid-steel normalization must be reconciled',
                    'Carbon-rich MU-BOF emissions must not be substituted for EAF emissions',
                    'No H2 transport cost; no verified target-company mapping'])
    (OUT/'radloff_source_package.json').write_text(json.dumps(r_bundle,ensure_ascii=False,indent=2)+'\n')
    manifest=dict(source_files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in (source,si,RAW/'radloff_2023.pdf',Path(__file__))],
        vogl_observations=len(records),vogl_cost_cases=len(rows),radloff_native_cells=len(native),
        radloff_checks=len(checks),radloff_held_conflicts=sum(c['status'].startswith('held_') for c in checks),
        adopted_to_company_inputs=False,distribution_calibrated=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(**manifest,vogl_audit=bundle['audit']),indent=2))


if __name__=='__main__':main()
