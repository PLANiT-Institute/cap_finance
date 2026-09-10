"""Recheck saved outputs, model-preservation composition and refresh metadata."""
from pathlib import Path
import argparse
import json
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import numpy as np

import all_models_workbook_control as all_models
from xlsx_table_reader import read_cells


def timing_status_rules(path):
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    rid = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
    with ZipFile(path) as z:
        links = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheet = next(s for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', ns) if s.attrib['name'] == 'Timing')
        target = links[sheet.attrib[rid]]
        target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        xml = ET.fromstring(z.read(target))
        return [r.attrib for cf in xml.findall('m:conditionalFormatting', ns)
                if cf.attrib['sqref'] in ('B30', 'B30:B30') for r in cf]


def verify(path, run, *, compare=None):
    path, run = Path(path), Path(run)
    report = json.loads((run / 'verification.json').read_text())
    assert all_models.sha(path) == report['output_sha256']
    assert all_models.read_all(path) == report['controls']
    paired_payload = json.loads((run / 'paired/payload.json').read_text())
    timing_payload = json.loads((run / 'timing/payload.json').read_text())
    paired_snapshot = Path(timing_payload['input_workbook'])
    assert all_models.sha(paired_snapshot) == report['paired']['output_sha256']
    paired = all_models.paired.verify_saved(paired_snapshot, paired_payload)
    timing = all_models.timing.verify_saved(path, timing_payload)
    # The saved timing output must retain all first-stage model results unchanged.
    rules = timing_status_rules(path)
    assert len(rules) == 1 and rules[0]['text'] == '재계산', rules
    cells = read_cells(path)
    assert len(cells) == 13
    values = {}
    for name in ['Control', 'NCC cash']:
        values[name] = [cells[name][r, 2]['value'] for r in range(5, 10)]
    values['Timing'] = [cells['Timing'][r, c]['value'] for r in range(6, 10) for c in range(5, 9)
                        if isinstance(cells['Timing'][r, c]['value'], (int, float))]
    comparison_count = 0
    if compare is not None:
        before = read_cells(compare)
        for name in ['Control', 'NCC cash']:
            for row in range(5, 10):
                np.testing.assert_allclose(cells[name][row, 2]['value'], before[name][row, 2]['value'], rtol=1e-12, atol=1e-7)
                comparison_count += 1
        for row in range(6, 10):
            for col in range(2, 10):
                actual, expected = cells['Timing'][row, col]['value'], before['Timing'][row, col]['value']
                if isinstance(expected, (int, float)):
                    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-7)
                else:
                    assert actual == expected
                comparison_count += 1
    return dict(paired=paired, timing=timing, status_rules=1, sheets=13,
                headline_metrics=values, compared_prior_cells=comparison_count,
                execution_fingerprint_files=len(report['execution_sha256']),
                output_sha256=all_models.sha(path), native_Excel_tested=False)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workbook', required=True)
    ap.add_argument('--run', required=True)
    ap.add_argument('--compare')
    ap.add_argument('--report', required=True)
    a = ap.parse_args()
    result = verify(a.workbook, a.run, compare=a.compare)
    Path(a.report).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print({k: result[k] for k in ['sheets', 'status_rules', 'compared_prior_cells', 'execution_fingerprint_files']})
