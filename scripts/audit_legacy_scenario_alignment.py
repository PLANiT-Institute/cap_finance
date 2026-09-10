"""Compare old FIN price labels with newly verified IEA2025 native tables.

Numeric reproduction with legacy1350FX and52millionBtu/t does not endorse
their currency basis, geographic delivery boundary or carbon-sector transfer.
"""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pandas as pd
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]


def main():
    ref=ROOT/'data/research_v2/iea_2025_scenarios'
    manifest=json.loads((ref/'manifest.json').read_text())
    pdf=ROOT/'tmp/pdfs/tcar_research_v2/iea_gecm_2025_current.pdf'
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==manifest['source']['sha256']
    text=PdfReader(pdf).pages[21].extract_text(extraction_mode='layout')
    steps=text.split('Stated Policies Scenario')[1].split('Announced Pledges Scenario')[0]
    nze=text.split('Net Zero Emissions by 2050 Scenario')[1].split('1 Includes')[0]
    carbon={}
    for region in ('Korea','Japan'):
        m=re.search(r'^\s*'+region+r'\s+(\d+)\s+(\d+)\s+(\d+)\s*$',steps,re.M)
        assert m
        carbon['STEPS',region]=[float(x) for x in m.groups()]
        m=re.search(r'Advanced economies with net zero emissions pledges\s+(\d+)\s+(\d+)\s+(\d+)',nze)
        assert m
        carbon['NZE',region]=[float(x) for x in m.groups()]
    assert carbon['STEPS','Korea']==[52,62,75]
    assert carbon['STEPS','Japan']==[39,61,105]
    assert carbon['NZE','Korea']==[180,205,250]
    native=pd.read_csv(ref/'native_observations.csv')
    prepared=ROOT/'data/prepared/D2b_scenario_prices.csv'
    legacy=pd.read_csv(prepared)
    selected=legacy[legacy.variable.isin(['gas_price','coal_price','co2_price']) & legacy.year.isin([2035,2040,2050])]
    rows=[]
    for r in selected.itertuples(index=False):
        scenario={'NZ15':'NZE','B20':'STEPS'}[r.scenario]
        if r.variable=='co2_price':
            raw=carbon[scenario,r.region][[2035,2040,2050].index(r.year)]
            factor=1350.;boundary='electricity carbon assumption; industrial applicability not established'
            source_region=r.region if scenario=='STEPS' else 'advanced_economies_with_net_zero_pledges'
            table='2.4';node=True
        else:
            commodity={'gas_price':'natural_gas','coal_price':'steam_coal'}[r.variable]
            d=native[(native.commodity==commodity)&(native.region=='Japan')&(native.scenario==scenario)].sort_values('year')
            raw=float(np.interp(r.year,d.year,d.value));node=r.year in d.year.values
            factor=1350.*(52. if r.variable=='gas_price' else 1.)
            boundary='Japan LNG border HHV,52millionBtu/t assumed' if r.variable=='gas_price' else 'Japan imported steam coal6000kcal/kg, not coking coal'
            source_region='Japan';table='2.3'
        reconstructed=raw*factor
        rows.append(dict(local_scenario=r.scenario,matched_source_scenario=scenario,region=r.region,
            variable=r.variable,year=r.year,legacy_value=r.value,legacy_source_id=r.source_id,
            source_region=source_region,source_table=table,source_node=node,
            source_or_linear_value=raw,legacy_conversion_factor=factor,reconstructed_value=reconstructed,
            difference=r.value-reconstructed,numeric_match=abs(r.value-reconstructed)<1e-6,
            boundary_limit=boundary,company_scenario_alignment_verified=False))
    out=pd.DataFrame(rows);assert len(out)==36
    # All actual checked source nodes reproduce; interpolated old values may not.
    assert out[out.source_node].numeric_match.all()
    out.to_csv(ref/'legacy_alignment_audit.csv',index=False)
    audit=dict(rows=len(out),source_node_rows=int(out.source_node.sum()),
        numeric_matches=int(out.numeric_match.sum()),interpolation_differences=int((~out.numeric_match).sum()),
        B20_source_prices='Checked anchors match STEPS, not an independently verified below2C scenario',
        NZ15_source_prices='Checked anchors match NZE; source NZE2025 has overshoot, not a generic no-overshoot1.5C scenario',
        source_boundary_verified=False,legacy_inputs_changed=False,
        source_files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                      for p in (prepared,pdf,Path(__file__))])
    (ref/'legacy_alignment_manifest.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
