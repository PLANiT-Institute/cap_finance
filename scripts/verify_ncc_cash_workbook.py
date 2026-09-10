"""Independent saved-XLSX verification for the conditional cash extension."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.risk_metrics import loss_summary
from ncc_cash_workbook_control import read_input,FIELDS
from xlsx_table_reader import read_cells,WorkbookInputError

def main():
 d=ROOT/'tmp/ncc_joint_workbook/completion7';results=[];maxerror=0.
 for name in ('base','changed','zero'):
  file=d/'roundtrip'/f'{name}.xlsx';s=read_cells(file);c=read_input(file)
  draws=np.array([[s['NCC paths'][r,k]['value'] for k in (2,3)] for r in range(5,c['paths']+5)])
  m=loss_summary(draws[:,1]-draws[:,0],c['alpha'])
  expected=[m[k] for k in ('mean','p50','q_alpha','tcar','es_alpha')]
  actual=[s['NCC cash'][r,2]['value'] for r in range(5,10)]
  np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-8)
  p=json.loads((d/'roundtrip'/name/'payload.json').read_text())
  for k in ('mean','p50','q_alpha','tcar','es_alpha'):np.testing.assert_allclose(m[k],p['metrics'][k],rtol=1e-12,atol=1e-8)
  assert s['NCC cash'][31,2]['value']=='최신 계산'
  for row,(key,_,_) in enumerate(FIELDS,12):assert s['NCC cash'][row,6]['value']==c[key]
  # Rebuild all central-price annual cash NPVs from separate saved quantities/rates.
  annual=[]
  for row in range(5,53):
   v=[s['NCC annual'][row,col]['value'] for col in range(1,19)]
   cost=(v[3]-v[4]+v[5]+v[6]*v[10]+v[7]*v[11]+(v[8]+v[9])*v[12])*v[13]/1e6
   np.testing.assert_allclose(cost,v[17],rtol=1e-12,atol=1e-8);annual.append(cost)
  theory=sum(annual[24:])-sum(annual[:24]);np.testing.assert_allclose(theory,s['NCC cash'][10,2]['value'],rtol=1e-12,atol=1e-8)
  assert not any(cell['error'] for sheet in s.values() for cell in sheet.values())
  err=float(np.max(np.abs(np.array(actual)-expected)));maxerror=max(maxerror,err)
  results.append(dict(case=name,paths=c['paths'],tail_mass=(1-c['alpha'])*c['paths'],metrics_checked=5,annual_cash_rows_checked=48,max_metric_error=err,analytic_mean=theory))
 assert results[-1]['analytic_mean']!=0 # Zero commodity prices leave capital/maintenance costs.
 rejections=[]
 for name in ('blank','fractional','alpha','source_value','source_unit','source_blank'):
  try:read_input(d/'edits'/f'{name}.xlsx')
  except WorkbookInputError as e:rejections.append(dict(case=name,reason=str(e)))
  else:raise AssertionError('Invalid edit accepted '+name)
 old=read_cells(ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v2.xlsx')
 final=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v3.xlsx';new=read_cells(final)
 for name,cells in old.items():assert cells==new[name],name
 assert len(new)==10
 report=dict(roundtrips=results,max_metric_error=maxerror,rejections=rejections,old_sheets_values_formulas_preserved=7,
  new_input_controls=18,total_sheets=10,final_error_cells=sum(cell['error'] for sh in new.values() for cell in sh.values()),
  native_Excel_tested=False,company_calibrated=False,
  final_workbook_sha256=hashlib.sha256(final.read_bytes()).hexdigest())
 (d/'roundtrip_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
