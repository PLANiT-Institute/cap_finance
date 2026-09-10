"""Audit cached Excel metrics against executed FIN and inspect actual roundtrip."""
from pathlib import Path
import json
import subprocess
import numpy as np
from joint_workbook_control import ROOT, SCRATCH, NODE, read_controls
from xlsx_table_reader import read_cells, WorkbookInputError


def verify(path,result_path):
    s=read_cells(path);r=json.loads(result_path.read_text());errors=[]
    for name,cells in s.items():
        errors += [(name,k,v['value']) for k,v in cells.items() if v['error']]
    assert not errors,errors
    expected=[r['metrics'][k] for k in ('mean','p50','q_alpha','tcar','es_alpha')]
    actual=[s['Control'][(row,2)]['value'] for row in range(5,10)]
    np.testing.assert_allclose(actual,expected,rtol=1e-10,atol=1e-7)
    assert s['Control'][(29,2)]['value']=='최신 계산'
    assert read_controls(path)==r['controls']
    np.testing.assert_allclose(s['Annual cost'][(29,2)]['value'],r['theoretical_mean_bnKRW2024'],rtol=1e-11,atol=1e-7)
    return dict(file=str(path.relative_to(ROOT)),paths=r['controls']['paths'],metrics=actual,
                max_metric_error=float(np.max(np.abs(np.asarray(actual)-expected))),excel_error_cells=0)


def main():
    p=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control.xlsx'
    checks=[verify(p,SCRATCH/'default/result.json')]
    subprocess.run([str(NODE),str(ROOT/'scripts/exercise_joint_control_workbook.mjs'),str(p)],check=True)
    ex=SCRATCH/'exercises';rejected=[]
    for name in ('blank_production','changed_source','changed_technology'):
        try:read_controls(ex/(name+'.xlsx'))
        except (WorkbookInputError,ValueError) as e:rejected.append(dict(name=name,reason=str(e)))
        else:raise AssertionError(f'{name} was silently accepted')
    for name in ('changed_scenario_and_fractional_tail','zero_production'):
        output=ex/(name+'_recomputed.xlsx');d=ex/(name+'_run')
        subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/joint_workbook_control.py'),
                        '--input',str(ex/(name+'.xlsx')),'--output',str(output),'--scratch',str(d),'--no-preview'],check=True)
        checks.append(verify(output,d/'result.json'))
    assert checks[-1]['metrics']==[0.]*5
    report=dict(valid_executions=checks,rejected=rejected,native_Excel_tested=False,
                verification='Artifact Tool import/edit/recalculate/export, read-only XLSX XML import, actual FIN rerun and independent Excel tail formulas')
    (ex/'roundtrip_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
