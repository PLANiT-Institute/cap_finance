"""Refresh both research models from one immutable workbook snapshot.

Publish a distinct output only after both FIN models and saved Excel results pass.
No model inputs are merged across their different price/cost boundaries.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

import numpy as np
import joint_workbook_control as joint
import ncc_cash_workbook_control as cash
from cap.risk_metrics import loss_summary
from xlsx_table_reader import read_cells, literal, WorkbookInputError

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'Control', 'Annual cost', 'Scenario source', 'Technology DB',
            'MC summary', 'Cost paths', 'NCC reference', 'NCC cash', 'NCC annual', 'NCC paths'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_both(path):
    sheets = read_cells(path)
    if not REQUIRED <= set(sheets):
        raise WorkbookInputError('Unified refresh requires the complete ten-sheet workbook')
    original, capital = joint.read_controls(path), cash.read_input(path)
    # Source labels/units are part of the contract, not cosmetic annotations.
    for row, values in enumerate(joint.sources(), 5):
        for col, expected in enumerate(values, 1):
            if literal(sheets['Scenario source'], row, col, 'Scenario source') != expected:
                raise WorkbookInputError('Scenario source value, label or provenance changed')
    for row, unit in enumerate(('MWh/t 에틸렌', 'MWh/t 에틸렌', 't 나프타/t 에틸렌', 't CH4/t 에틸렌'), 5):
        if literal(sheets['Technology DB'], row, 3, 'Technology DB unit') != unit:
            raise WorkbookInputError('Technology unit changed')
    for row, (_, _, unit, note) in enumerate(joint.FIELDS, 12):
        if literal(sheets['Control'], row, 3, 'Control unit') != unit or literal(sheets['Control'], row, 4, 'Control interpretation') != note:
            raise WorkbookInputError('Control unit or interpretation changed')
    for row, (_, _, unit) in enumerate(cash.FIELDS, 12):
        if literal(sheets['NCC cash'], row, 3, 'NCC cash interpretation') != unit:
            raise WorkbookInputError('NCC cash unit or interpretation changed')
    return original, capital


def verify_saved(path, p):
    """Independent saved-cell arithmetic; cached PASS alone is not evidence."""
    original, capital = read_both(path)
    s = read_cells(path)
    if original != p['joint']['result']['controls'] or capital != p['cash']['controls']:
        raise WorkbookInputError('Saved controls differ from the executed inputs')
    errors = [(name, key) for name, cells in s.items() for key, value in cells.items() if value['error']]
    if errors:
        raise WorkbookInputError(f'Excel error cells: {errors[:5]}')
    reports = []
    for name, summary, inputs, record, lastcol in [
        ('Cost paths', 'Control', original, p['joint']['result'], 2),
        ('NCC paths', 'NCC cash', capital, p['cash'], 2),
    ]:
        rows = range(5, inputs['paths'] + 5)
        draws = np.array([[s[name][r, c]['value'] for c in (2, 3)] for r in rows])
        metrics = loss_summary(draws[:, 1] - draws[:, 0], inputs['alpha'])
        expected = [metrics[k] for k in ('mean', 'p50', 'q_alpha', 'tcar', 'es_alpha')]
        backend = [record['metrics'][k] for k in ('mean', 'p50', 'q_alpha', 'tcar', 'es_alpha')]
        actual = [s[summary][r, lastcol]['value'] for r in range(5, 10)]
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-7)
        np.testing.assert_allclose(actual, backend, rtol=1e-12, atol=1e-7)
        stale_row = 29 if summary == 'Control' else 31
        assert s[summary][stale_row, 2]['value'] == '최신 계산'
        assert all(v['value'] is None and v['formula'] is None for (r, c), v in s[name].items()
                   if r >= inputs['paths'] + 5 and c <= 5), 'Old draw rows remain'
        reports.append(dict(model=summary, paths=inputs['paths'], metrics=actual,
                            max_metric_error=float(np.max(np.abs(np.array(actual) - expected)))))
    np.testing.assert_allclose(s['Annual cost'][29, 2]['value'], p['joint']['result']['theoretical_mean_bnKRW2024'], rtol=1e-12, atol=1e-7)
    annual = []
    for row in range(5, 53):
        v = [s['NCC annual'][row, col]['value'] for col in range(1, 19)]
        value = (v[3]-v[4]+v[5]+v[6]*v[10]+v[7]*v[11]+(v[8]+v[9])*v[12])*v[13]/1e6
        np.testing.assert_allclose(value, v[17], rtol=1e-12, atol=1e-8)
        annual.append(value)
    theory = sum(annual[24:])-sum(annual[:24])
    np.testing.assert_allclose(theory, s['NCC cash'][10, 2]['value'], rtol=1e-12, atol=1e-7)
    np.testing.assert_allclose(theory, p['cash']['analytic_mean'], rtol=1e-12, atol=1e-7)
    before = read_cells(p['input_workbook'])
    assert list(before) == list(s), 'Worksheet order changed'
    for name in ('Scenario source', 'Technology DB', 'NCC reference'):
        for key, cell in before[name].items():
            permitted_guard = (name == 'Technology DB' and key == (11, 2)) or (name == 'Scenario source' and key[1] == 8 and 5 <= key[0] <= 85)
            if permitted_guard:
                assert s[name][key]['value'] == '일치' and s[name][key]['formula']
            else:
                assert cell == s[name].get(key), f'Source cell changed: {name} {key}'
    for name in set(before) - REQUIRED:
        assert before[name] == s[name], f'Unrelated sheet changed: {name}'
    return dict(models=reports, annual_cash_rows_checked=48, source_sheets_preserved=3,
                sheets=len(s), native_Excel_tested=False, company_calibrated=False)


def refresh(input_path, output_path, scratch, *, preview=True):
    input_path, output_path, scratch = map(lambda x: Path(x).resolve(), (input_path, output_path, scratch))
    if input_path == output_path or output_path.exists():
        raise WorkbookInputError('Use a distinct, unused output path; existing files are preserved')
    if scratch.exists() and any(scratch.iterdir()):
        raise WorkbookInputError('Use an empty run folder to preserve previous evidence')
    scratch.mkdir(parents=True, exist_ok=True)
    original_hash = sha(input_path)
    snapshot = scratch/'input.xlsx'
    shutil.copyfile(input_path, snapshot)
    if sha(snapshot) != original_hash:
        raise WorkbookInputError('Input changed during snapshot; retry from the saved file')
    original, capital = read_both(snapshot)  # Validate both before either simulation.
    jp = joint.payload(original, scratch/'joint')
    cp = cash.evaluate(capital)
    p = dict(input_workbook=str(snapshot), joint=json.loads(jp.read_text()), cash=cp)
    payload = scratch/'payload.json'
    payload.write_text(json.dumps(p, ensure_ascii=False)+'\n')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.tcar-refresh-', dir=output_path.parent) as stage:
        candidate = Path(stage)/'result.xlsx'
        cmd = [str(joint.NODE), str(ROOT/'scripts/refresh_joint_workbook.mjs'), str(payload), str(candidate)]
        if not preview:
            cmd.append('--no-preview')
        subprocess.run(cmd, check=True, cwd=ROOT)
        report = verify_saved(candidate, p)
        if sha(input_path) != original_hash:
            raise WorkbookInputError('Input edited during execution; result not published')
        report.update(input_sha256=original_hash, output_sha256=sha(candidate),
                      output=str(output_path), both_models_refreshed=True,
                      input_preserved=True, atomic_new_output=True,
                      orchestrator_sha256=sha(__file__), builder_sha256=sha(ROOT/'scripts/refresh_joint_workbook.mjs'))
        (scratch/'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        # Same-filesystem link is atomic and refuses an existing target (including a race).
        os.link(candidate, output_path)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--scratch', type=Path, required=True)
    ap.add_argument('--no-preview', action='store_true')
    a = ap.parse_args()
    print(json.dumps(refresh(a.input, a.output, a.scratch, preview=not a.no_preview), ensure_ascii=False))


if __name__ == '__main__':
    main()
