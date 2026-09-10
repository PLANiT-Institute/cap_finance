"""Exercise importer failures and export isolation against an actual saved workbook."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
from unittest.mock import patch

import research_control as control
from xlsx_table_reader import WorkbookInputError, read_cells


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workbook',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();original=read_cells(args.workbook);results=[]
    def rejects(name, change, text):
        cells=copy.deepcopy(original);change(cells)
        with patch.object(control,'read_cells',return_value=cells):
            try:control.validate(args.workbook)
            except WorkbookInputError as error:
                assert text in str(error),(name,str(error))
                results.append(dict(case=name,rejected=True,reason=str(error),test_surface='in_memory_cells_read_from_actual_workbook'))
            else:raise AssertionError(f'Invalid case accepted: {name}')
    rejects('missing_D3',lambda s:s.pop('D3'),'Missing required input sheet')
    rejects('duplicated_facility_ID',lambda s:s['D1a'][(7,1)].update(value=s['D1a'][(6,1)]['value']),'duplicated or altered record ID')
    rejects('missing_capex',lambda s:s['D3'][(7,4)].update(value=None),'required numeric value')
    rejects('nonnumeric_capex',lambda s:s['D3'][(7,4)].update(value='unknown'),'finite numeric cell')
    rejects('negative_capex',lambda s:s['D3'][(7,4)].update(value=-1),'invalid domain')
    rejects('fractional_construction_years',lambda s:s['D3'][(7,11)].update(value=2.5),'invalid domain')
    rejects('missing_setting',lambda s:s['Settings'][(6,1)].update(value=None),'required parameter is missing')
    rejects('reference_header',lambda s:s['D3'][(5,4)].update(value='capex_USD'),'header names or order')
    # Row sorting preserves record identity and cannot change the exported ordering.
    cells=copy.deepcopy(original)
    for col in range(1,18):
        a=cells['D1a'].get((6,col));b=cells['D1a'].get((7,col))
        if a is not None:cells['D1a'][(7,col)]=a
        if b is not None:cells['D1a'][(6,col)]=b
    with patch.object(control,'read_cells',return_value=cells):
        r=control.validate(args.workbook);assert not r['changes']
    results.append(dict(case='sorted_rows',accepted=True,changes=0,test_surface='in_memory_cells_read_from_actual_workbook'))
    record=dict(workbook_sha256=hashlib.sha256(args.workbook.read_bytes()).hexdigest(),cases=results)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(f'Checked {len(results)} importer edge cases')


if __name__=='__main__':main()
