"""Extract inspected supplementary source values and prepare the Excel reference view."""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
URL='https://ndownloader.figshare.com/files/42479975'
SHA='d86e41c1535b7d1241ebc94e5ed9be37e83ed5878296aa0614aeac739192197f'


def main():
    raw=ROOT/'tmp/pdfs/tcar_research_v2/ie3c02226_si_001.pdf'
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==SHA
    out=ROOT/'data/research_v2/tiggeloven_supplement';out.mkdir(parents=True,exist_ok=True)
    coproducts=[('C2_excluding_ethylene',.0496,918.7,'IEA2019'),
        ('C3_propylene',.1481,815.1,'Statista2019'),('methane',.1690,382.9,'Eurostat2019'),
        ('BTX',.0766,600.,'Spallina2017_estimate'),('C4',.0525,785.,'BoulamantiMoya2017_estimate'),
        ('pyrolysis_gas',.0438,745.,'BoulamantiMoya2017_estimate'),('fuel_oil',.1286,430.,'BoulamantiMoya2017_estimate')]
    rows=[dict(product=p,yield_t_per_t_naphtha=y,price_source_EUR_per_t=price,
        cited_price_reference=ref,source_url=URL,pdf_page=8,source_table='S6',
        meaning='allocation_input_not_observed_site_export_netback') for p,y,price,ref in coproducts]
    pd.DataFrame(rows).to_csv(out/'coproduct_observations.csv',index=False)
    meta=dict(source_url=URL,source_doi='10.1021/acs.iecr.3c02226.s001',source_sha256=SHA,
        public_metadata_url='https://api.figshare.com/v2/articles/24205025',
        license='CC BY-NC4.0',pages=9,visually_reviewed_pages=[2,8],numeric_coproduct_cells=14,
        source_formula='new_price = new_mean + (base_price-base_mean)*new_sd/base_sd',
        stochastic_sampling=False,profile_count=160,profile_count_is_independent_sample_size=False,
        price_unit_conflict='SI p2 states mean0to150EUR/kWh; FigS1 scale inconsistent. Do not silently adopt corrected units.',
        maintenance_resolved=False,plant_lifetime_annuity_resolved=False,
        hourly_numeric_results_received=False,
        cashflow_rule='CCAF is allocation share multiplying total costs including feedstock; do not also subtract coproduct revenue',
        price_year='Mixed cited2017/2019; not an asserted uniform2019realprice basket',
        cost_scope='Main optimization omits feedstock; SIeq2adds it for allocated reporting metric')
    (out/'source_review.json').write_text(json.dumps(meta,indent=2)+'\n')
    source=pd.read_csv(ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv').fillna('')
    reference=dict(source_main_url=source.source_url.iloc[0],source_si_url=URL,
        source_main_sha256=json.loads((ROOT/'data/research_v2/tiggeloven_reference/package.json').read_text())['source_sha256'],
        source_si_sha256=SHA,
        observations=source[['case','item','value','unit','pdf_page','interpretation']].values.tolist(),
        coproducts=[list(x) for x in coproducts],
        model_use='참조 검토 중. 현재 MC는 Layritz 부분 원장을 사용합니다.',
        outstanding='유지비 비율·플랜트 수명·개조비·메탄 및 증기 수지 확인 필요',
        derivation_values=[1/.303,.083/.303,1.942/.303,1.859/.303,994.49])
    (out/'workbook_reference.json').write_text(json.dumps(reference,ensure_ascii=False,indent=2)+'\n')
    files=[raw,Path(__file__),out/'coproduct_observations.csv',out/'source_review.json',out/'workbook_reference.json']
    manifest=dict(numeric_cells=14,source_visual_QA_complete=True,source_formula_reviewed=True,
        source_maintenance_hold_remains=True,model_inputs_changed=False,
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='sha256'}))


if __name__=='__main__':main()
