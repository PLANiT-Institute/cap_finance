"""Visually reviewed company energy/contract observations; no inferred FIN inputs."""
from pathlib import Path
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/company_procurement'
SOURCES={
 'lotte':dict(path='tmp/pdfs/tcar_petchem_sources/lotte_esg_2025.pdf',url='https://www.lottechem.com/pdfRead.do?fileId=FILE_260803112356995',pages=[51,52,117,118]),
 'mci':dict(path='tmp/pdfs/tcar_petchem_sources/mci_esg_2025_part6.pdf',url='https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/sustainability/report/esg2025web_e_part06.pdf.coredownload.pdf',pages=[42])}
# Page118 columns read in source order: 2025,2024,2023.
ENERGY={2025:[70559,18313,13706,102574,102635,61,9576,1776107],
        2024:[74919,21822,16334,113070,113133,63,12787,2094447],
        2023:[78697,24960,15102,118759,118765,6,10982,2159203]}
ITEMS=['nonrenewable_fuel','nonrenewable_electricity','nonrenewable_steam',
       'nonrenewable_total','energy_total','renewable_REC_reported_energy',
       'self_generation','scope2_total']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=[]
 def add(source,page,entity,year,item,value,unit,status,method,period=None):
  text=(ROOT/SOURCES[source]['path']).with_suffix('.txt').read_text().split('\f')[page-1]
  assert f'{value:,}' in text or str(value) in text,(item,value,page)
  rows.append(dict(id=f'{source}_{year}_{item}',source_url=SOURCES[source]['url'],source_sha256=sha(ROOT/SOURCES[source]['path']),pdf_page=page,entity=entity,year=year,period=period or f'CY{year}',item=item,value=value,unit=unit,status=status,method=method,FIN_adopted=False))
 for year,values in ENERGY.items():
  for item,value in zip(ITEMS,values):
   add('lotte',117 if item=='scope2_total' else 118,'LOTTE Chemical parent',year,item,value,'tCO2eq' if item=='scope2_total' else 'reported_TJ','reported_first_submission' if item=='scope2_total' and year==2025 else 'reported_observation',
       'No electricity/steam Scope2 split' if item=='scope2_total' else 'Report accounting energy; physical procurement and conversion coefficient unresolved')
 for item,value,entity,method in [
  ('REC_solar',6384,'LOTTE Chemical parent','Long-term certificate purchase; no power price settlement disclosed'),
  ('PPA_solar',10161,'LOTTE Fine Chemical','Direct PPA (LOTTE Chemical); price settlement not disclosed'),
  ('PPA_wind',9301,'LOTTE Fine Chemical','Direct PPA (SK Innovation); price settlement not disclosed')]:
  add('lotte',52,entity,2025,item,value,'MWh','reported_approximate',method)
 for item,value,unit,method in [
  ('scope1_total',3383,'ktCO2_native_label','GHG Protocol; off-site vehicle fuels excluded'),
  ('scope2_total',486,'ktCO2_native_label','GHG Protocol market-based; some electricity sold to other companies excluded'),
  ('energy_total',64.6,'PJ','Company statutory accounting; regional partnership methodology applies at relevant sites')]:
  add('mci',42,'Mitsui Chemicals Inc.',2024,item,value,unit,'reported_assured_statement',method,'2024-04-01/2025-03-31')
 with (OUT/'source_observations.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 audits=[]
 for year,v in ENERGY.items():
  component=sum(v[:3]);total=v[3]
  # Explicit alternative diagnostic: independent nearest-integer TJ rounding.
  lo=component-1.5;hi=component+1.5;tlo=total-.5;thi=total+.5
  audits.append(dict(year=year,component_sum_TJ=component,reported_nonrenewable_TJ=total,
    components_minus_total_TJ=component-total,component_rounding_interval=[lo,hi],
    total_rounding_interval=[tlo,thi],nearest_integer_rounding_can_reconcile=max(lo,tlo)<=min(hi,thi),
    reported_nonrenewable_plus_REC_minus_energy_total_TJ=total+v[5]-v[4],
    decision='retain_literals_no_component_repair'))
 (OUT/'reconciliation.json').write_text(json.dumps(audits,indent=2)+'\n')
 mapping={
  'LOTTE_2024_electricity':dict(observation='lotte_2024_nonrenewable_electricity',native_value=21822,native_unit='reported_TJ',procured_MWh=None,required=['report conversion coefficient','purchased versus own-generation boundary','site allocation']),
  'LOTTE_2024_steam':dict(observation='lotte_2024_nonrenewable_steam',native_value=16334,native_unit='reported_TJ',procured_GJ=None,required=['purchased versus internally generated boundary','pressure enthalpy and conversion','site allocation']),
  'LOTTE_2025_REC':dict(observation='lotte_2025_REC_solar',native_value=6384,native_unit='MWh approximate',certificate_quantity_observed=True,price_hedge_quantity=None,required=['certificate price and payment schedule','ownership retirement vintage','any power price settlement']),
  'MCI_FY2024_scope2':dict(observation='mci_2024_scope2_total',native_value=486,native_unit='ktCO2 native label',accounting_basis='market_based',procured_MWh=None,required=['electricity and external heat quantities separately','supplier/menu factors','sold electricity exclusions','gas and GWP basis'])}
 (OUT/'procurement_mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
 manifest=dict(source_observations=len(rows),source_PDFs=2,source_PDF_pages=5,
   source_sha256={s['path']:sha(ROOT/s['path']) for s in SOURCES.values()},
   sources=SOURCES,implementation_sha256={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},
   artifact_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.name!='manifest.json'},
   company_procurement_calibrated=False,new_MC=False,FIN_mutated=False,
   rounding_assumption='nearest integer TJ diagnostic, not an issuer rounding-policy claim',
   native_MCI_ktCO2_label_not_GWP_normalized=True)
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(dict(observations=len(rows),reconciliation=audits))

if __name__=='__main__':main()
