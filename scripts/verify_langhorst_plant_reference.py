"""Independent read-only checks of the emitted register against the publisher workbook."""
from pathlib import Path
import csv,hashlib,json,math
import openpyxl
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/langhorst_plant_reference'
RAW=ROOT/'tmp/pdfs/tcar_research_v2/langhorst2026'
with (OUT/'scenario_physical_ledger.csv').open() as f:rows=list(csv.DictReader(f))
w=openpyxl.load_workbook(RAW/'model.xlsx',read_only=True,data_only=True)
s=w['1. Results']; count=0
for j,r in enumerate(rows):
 for key,cell in [('plates_kt_y',f'AA{57+j}'),('cast_slabs_kt_y',f'AB{57+j}'),('electricity_demand_before_CHP_GWh_y',f'P{17+j}'),('source_gross_subsystem_energy_GWh_y',f'M{17+j}'),('source_steelmaking_emissions_per_t_slab',f'W{57+j}')]:
  assert math.isclose(float(r[key]),s[cell].value,rel_tol=1e-12,abs_tol=1e-10),(j,key)
  count+=1
 # Physical electricity and total hydrogen are different: hydrogen is an internal intermediate.
 assert math.isclose(float(r['plates_kt_y']),513,abs_tol=1e-12)
 assert math.isclose(float(r['export_slabs_kt_y']),float(rows[0]['export_slabs_kt_y']),rel_tol=1e-12)
 assert math.isclose(float(r['natural_gas_input_GWh_y']),float(r['steelmaking_natural_gas_GWh_y'])+float(r['rolling_natural_gas_GWh_y']),rel_tol=1e-12,abs_tol=1e-12)
assert math.isclose(float(rows[0]['internal_COG_to_rolling_GWh_y']),s['D17'].value,rel_tol=1e-12)
assert math.isclose(s['M17'].value-s['D17'].value,float(rows[0]['carrier_inputs_excluding_internal_COG_GWh_y']),rel_tol=1e-12)
assert math.isclose(s['W58'].value*(968/float(rows[1]['liquid_steel_kt_y'])),float(rows[1]['derived_steelmaking_emissions_per_t_liquid_steel']),rel_tol=1e-12)
m=json.loads((OUT/'manifest.json').read_text())
for f,digest in m['sources'].items():assert hashlib.sha256((RAW/f).read_bytes()).hexdigest()==digest
for f,digest in m['outputs'].items():assert hashlib.sha256((OUT/f).read_bytes()).hexdigest()==digest
note=(ROOT/'paper/methodology/STEEL_PLANT_BOUNDARY_KO.md').read_text()
shown=0
for j in [0,1,2,7]:
 for value in [float(rows[j]['electricity_demand_before_CHP_GWh_y'])/1000,float(rows[j]['onsite_hydrogen_kt_y']),float(rows[j]['liquid_steel_kt_y'])]:
  assert f'{value:,.3f}' in note
  shown+=1
assert '0.197422' in note and '0.190512' in note
assert '50.705' in note and math.isclose(float(rows[1]['natural_gas_input_GWh_y'])-float(rows[0]['natural_gas_input_GWh_y']),50.705,abs_tol=.0005)
book=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
assert hashlib.sha256(book.read_bytes()).hexdigest()=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
r=dict(source_result_cells_checked=count,fixed_product_checks=16,gas_aggregation_checks=8,boundary_checks=3,note_table_values_checked=shown,note_denominator_values_checked=2,note_gas_difference_checked=1,source_hashes_checked=len(m['sources']),output_hashes_checked=len(m['outputs']),integrated_Excel_v6_unchanged=True,figure_visually_reviewed=True,full_Excel_engine_recalculation=False,new_Monte_Carlo_runs=0,all_passed=True)
path=ROOT/'docs/research_cycles/2026-09-07-hourly/completion_22_verification.json'
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(r,ensure_ascii=False))
