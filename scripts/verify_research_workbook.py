"""Compare the saved integrated workbook against its typed tables and computed summaries."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math

from research_control import validate
from xlsx_table_reader import read_cells


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workbook',type=Path,required=True)
    ap.add_argument('--payload',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();payload=json.loads(args.payload.read_text());sheets=read_cells(args.workbook)
    assert set(sheets)=={'Overview','Input checks'}|{s['name'] for s in payload['sheets']}
    checked=0
    for definition in payload['sheets']:
        cells=sheets[definition['name']]
        for r, row in enumerate([definition['columns']]+definition['rows'],5):
            for c, expected in enumerate(row,1):
                actual=cells.get((r,c),{}).get('value')
                if isinstance(expected,(int,float)) and not isinstance(expected,bool):
                    assert isinstance(actual,(int,float)) and math.isclose(actual,expected,rel_tol=1e-13,abs_tol=1e-10),(definition['name'],r,c,actual,expected)
                else:
                    assert actual==expected,(definition['name'],r,c,actual,expected)
                checked+=1
    errors=[(name,r,c) for name,cells in sheets.items() for (r,c),cell in cells.items() if cell.get('error')]
    assert not errors,errors
    check_values=[cell['value'] for (r,c),cell in sheets['Input checks'].items() if r>=6 and c==3]
    assert check_values and all(v==0 for v in check_values)
    cases=next(s for s in payload['sheets'] if s['name']=='Case results')
    for i,row in enumerate(cases['rows'],14):
        for c,j in enumerate([0,1,3,4,5,6,2],1):
            assert sheets['Overview'][(i,c)]['value']==row[j]
    assert sheets['Overview'][(5,2)]['value']=='마지막 실행의 입력과 동일'
    assert sheets['Overview'][(8,2)]['value']==len(next(s for s in payload['sheets'] if s['name']=='Risk measures')['rows'])
    assert sheets['Overview'][(9,2)]['value']==len(next(s for s in payload['sheets'] if s['name']=='Primary observations')['rows'])
    parameters=next(s for s in payload['sheets'] if s['name']=='Parameters')
    assert sheets['Overview'][(10,2)]['value']==len(parameters['rows'])
    pcols=parameters['columns'];tier=pcols.index('evidence_tier');low=pcols.index('value_low');high=pcols.index('value_high')
    missing=sum(row[tier]=='T5' and (row[low] is None or row[high] is None) for row in parameters['rows'])
    assert sheets['Overview'][(11,2)]['value']==missing
    validation=validate(args.workbook);assert not validation['changes']
    schedules=next((s for s in payload['sheets'] if s['name']=='Selected schedules'),None)
    annual=next((s for s in payload['sheets'] if s['name']=='Annual capital'),None)
    if annual:
        for values in annual['rows']:
            row=dict(zip(annual['columns'],values))
            assert math.isclose(row['plan_gross_bnkrw'],row['construction_bnkrw']+row['renewal_bnkrw'],abs_tol=1e-8)
            assert math.isclose(row['incremental_gross_bnkrw'],row['plan_gross_bnkrw']-row['baseline_gross_bnkrw'],abs_tol=1e-8)
    record=dict(workbook_sha256=hashlib.sha256(args.workbook.read_bytes()).hexdigest(),
                payload_sha256=hashlib.sha256(args.payload.read_bytes()).hexdigest(),
                checked_table_cells=checked,sheet_count=len(sheets),input_check_rows=len(check_values),
                formula_errors=len(errors),input_changes=0,selected_case_rows_verified=len(cases['rows']),
                selected_facility_rows_verified=len(schedules['rows']) if schedules else 0,
                selected_annual_capital_rows_verified=len(annual['rows']) if annual else 0,
                checked_at_utc=datetime.now(timezone.utc).isoformat(),
                scope='Typed source tables, executable-input contract, cached formulas and summary cells; visual inspection is recorded separately.')
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
