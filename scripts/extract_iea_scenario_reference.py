"""Verified GEC2025 Table2.3 native nodes and explicitly derived annual curves.

This is a benchmark scenario register, not a Korea industrial tariff or a
probabilistic scenario ensemble. Original source stays in the local raw folder.
"""
from pathlib import Path
from dataclasses import asdict
import csv
import hashlib
import json
import re
import sys
import numpy as np
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap.scenario_prices import ScenarioPriceCurve,interpolate_curve

SOURCE=ROOT/'tmp/pdfs/tcar_research_v2/iea_gecm_2025_current.pdf'
OUT=ROOT/'data/research_v2/iea_2025_scenarios'
URL='https://iea.blob.core.windows.net/assets/9155992e-962c-45f4-97c1-78fd43a94178/GlobalEnergyandClimateModelDocumentation2025.pdf'
EXPECTED_SHA='803ddc49bb41fd3e6f49cb396cf749549372488900d7aa4f0057de5b4e61be8e'
SCENARIOS=('CPS','STEPS','NZE')
# Independent transcription checked against the rendered page, then compared
# with every numeric source row by the parser below.
ROWS=[
 ('crude_oil','IEA_import_average','barrel',None,[79,89,106,80,76,33,25]),
 ('natural_gas','United States','MMBtu_unspecified','HHV',[2.2,4.5,5.0,3.9,4.6,2.1,2.2]),
 ('natural_gas','European Union','MMBtu_unspecified','HHV',[10.3,9.1,10.6,6.5,8.4,4.2,4.0]),
 ('natural_gas','China','MMBtu_unspecified','HHV',[10.3,9.9,11.2,7.5,9.1,4.9,4.8]),
 ('natural_gas','Japan','MMBtu_unspecified','HHV',[13.5,11.2,12.9,8.4,9.7,4.9,4.9]),
 ('steam_coal','United States','t_steam_coal_6000kcal_kg',None,[56,56,53,41,41,25,23]),
 ('steam_coal','European Union','t_steam_coal_6000kcal_kg',None,[112,92,82,78,66,47,39]),
 ('steam_coal','Japan','t_steam_coal_6000kcal_kg',None,[151,112,105,100,84,57,49]),
 ('steam_coal','Coastal China','t_steam_coal_6000kcal_kg',None,[131,115,105,99,84,59,49])]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def write_csv(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    assert sha(SOURCE)==EXPECTED_SHA
    OUT.mkdir(parents=True,exist_ok=True)
    text=PdfReader(SOURCE).pages[20].extract_text(extraction_mode='layout')
    table=text.split('Notes:')[0]
    labels=r'IEA crude oil \(USD/barrel\)|United States|European Union|China|Japan|Coastal China'
    parsed=re.findall(r'^\s*('+labels+r')\s+((?:\d+(?:\.\d+)?\s+){6}\d+(?:\.\d+)?)\s*$',table,re.M)
    assert len(parsed)==len(ROWS)==9
    native=[];nodes=[];annual=[];curves=[]
    for ri,((label,numbers),(commodity,region,unit,heat,values)) in enumerate(zip(parsed,ROWS),1):
        assert label==('IEA crude oil (USD/barrel)' if ri==1 else region)
        np.testing.assert_array_equal([float(x) for x in numbers.split()],values)
        if commodity=='crude_oil':boundary='IEA_weighted_import_price'
        elif commodity=='natural_gas':
            boundary={'Japan':'LNG_customs_before_regasification','United States':'domestic_wholesale',
                      'European Union':'pipeline_LNG_import_mix','China':'pipeline_LNG_import_mix'}[region]
        else:
            boundary={'United States':'mine_mouth_plus_transport_handling','Coastal China':'domestic_import_mix',
                      'Japan':'import_price','European Union':'import_price'}[region]
        for ci,value in enumerate(values):
            native.append(dict(observation_id=f'IEA25_T23_R{ri}_C{ci+1}',commodity=commodity,region=region,
                scenario='shared_historical_anchor' if ci==0 else SCENARIOS[(ci-1)//2],
                year=2024 if ci==0 else (2035 if ci%2 else 2050),value=value,currency='USD',
                price_year=2024,exchange_basis='MER',quantity_unit=unit,heat_basis=heat or '',
                boundary=boundary,source_url=URL,source_sha256=EXPECTED_SHA,pdf_page=21,table='2.3'))
        for si,scenario in enumerate(SCENARIOS):
            curve=ScenarioPriceCurve(model='IEA_GEC_2025',scenario=scenario,region=region,
                commodity=commodity,years=(2024,2035,2050),values=(values[0],values[1+2*si],values[2+2*si]),
                quantity_unit=unit,currency='USD',price_year=2024,boundary=boundary,
                components=('benchmark_commodity',),source=URL+'#page=21',heat_basis=heat)
            curves.append(asdict(curve))
            for year,value in zip(curve.years,curve.values):
                native_column=1 if year==2024 else 2+2*si+(year==2050)
                nodes.append(dict(model=curve.model,scenario=scenario,region=region,commodity=commodity,
                    year=year,value=value,quantity_unit=unit,currency='USD',price_year=2024,
                    observation_id=f'IEA25_T23_R{ri}_C{native_column}',shared_anchor=year==2024))
            result=interpolate_curve(curve,tuple(range(2024,2051)),method='linear')
            for year,value in zip(result.years,result.values):
                annual.append(dict(model=curve.model,scenario=scenario,region=region,commodity=commodity,
                    year=year,value=value,quantity_unit=unit,currency='USD',price_year=2024,
                    boundary=boundary,heat_basis=heat or '',
                    status='source_node' if year in curve.years else 'derived_linear_interpolation',
                    company_delivered_input=False))
    write_csv('native_observations.csv',native);write_csv('scenario_nodes.csv',nodes)
    write_csv('annual_reference_curves.csv',annual)
    (OUT/'curves.json').write_text(json.dumps(curves,indent=2)+'\n')
    manifest=dict(source=dict(url=URL,sha256=EXPECTED_SHA,pdf_page=21,table='2.3',licence='IEA CC BY4.0'),
        native_observations=len(native),scenario_nodes_with_repeated_anchor=len(nodes),curves=len(curves),annual_rows=len(annual),
        source_page_visually_verified=True,all63_numeric_cells_match_independent_transcription=True,
        interpolation='linear2024–2035–2050; no extra source nodes or extrapolation',
        probabilities_assigned=False,kaist_data_received=False,company_delivered_prices=False,
        limitations=['Oil is IEA weighted import average, not Brent or naphtha',
          'Japan gas is LNG border before regasification, HHV; no Korea contract basis supplied',
          'MBtu means million Btu here; IT versus thermochemical convention not specified, retained native',
          'Steam coal6000kcal/kg is not coking coal or coke',
          'No electricity tariff, H2 price, pellet/scrap/naphtha premium or plant netback in this table',
          'Scenarios contain no calibrated commodity cycle fluctuations or scenario occurrence probabilities',
          'WEO2025 does not include APS; old local B20/APS labels not silently equated to STEPS',
          'Annual interpolations are analyst-derived reference levels, not IEA annual model outputs'],
        code_sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in (Path(__file__),ROOT/'src/cap/scenario_prices.py')])
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='limitations'},indent=2))


if __name__=='__main__':main()
