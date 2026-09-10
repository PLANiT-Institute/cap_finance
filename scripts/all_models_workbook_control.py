"""Refresh all three research models from one saved workbook, then publish once.

Model controls and accounting boundaries remain separate. Validation of every
input precedes simulation. The two existing refreshers verify disjoint edits;
their staged outputs are never exposed as the requested final file.
"""
from pathlib import Path
import argparse
import json
import os
import shutil
import tempfile

import unified_workbook_control as paired
import timing_workbook_control as timing
from xlsx_table_reader import WorkbookInputError, read_cells

ROOT = Path(__file__).resolve().parents[1]
sha = timing.sha


def execution_fingerprint():
    """Check reviewed numeric sources and detect mid-run data/code changes."""
    observed = ROOT / 'data/research_v2/tiggeloven_reference/source_observations.csv'
    history = ROOT / 'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    direct = ROOT / 'data/research_v2/ncc_emissions_context/direct_emissions_observations.csv'
    checks = [
        (observed, observed.parent / 'manifest.json', 'sha256', str(observed.relative_to(ROOT))),
        (history, ROOT / 'data/research_v2/block_price_paths/manifest.json', 'source_sha256', None),
        (direct, direct.parent / 'manifest.json', 'artifact_sha256', str(direct.relative_to(ROOT))),
    ]
    sources = []
    for path, manifest, key, item in checks:
        expected = json.loads(manifest.read_text())[key]
        if item is not None:
            expected = expected[item]
        if sha(path) != expected:
            raise WorkbookInputError('Reviewed source hash changed: ' + str(path.relative_to(ROOT)))
        sources.extend([path, manifest])
    sources.extend(ROOT / p for p in [
        'config.yaml', 'data/research_v2/iea_2025_scenarios/curves.json',
        'data/research_v2/technology_packages/reference_process_packages.json',
        'data/research_v2/tiggeloven_supplement/workbook_reference.json',
        'data/research_v2/tiggeloven_supplement/manifest.json',
        'scripts/ncc_joint_control.py', 'scripts/research_block_price_paths.py',
        'scripts/joint_workbook_control.py', 'scripts/ncc_cash_workbook_control.py',
        'scripts/unified_workbook_control.py', 'scripts/timing_workbook_control.py',
        'scripts/xlsx_table_reader.py', 'scripts/all_models_workbook_control.py',
        'scripts/refresh_joint_workbook.mjs', 'scripts/build_timing_workbook.mjs',
    ])
    sources.extend((ROOT / 'src/cap').glob('*.py'))
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(sources))}


def read_all(path):
    sheets = read_cells(path)
    if not timing.NEW_SHEETS.issubset(sheets):
        raise WorkbookInputError('All-model refresh requires the complete Timing extension')
    joint, cash = paired.read_both(path)
    return dict(joint=joint, cash=cash, timing=timing.read_input(path))


def refresh(input_path, output_path, scratch, *, preview=True):
    input_path, output_path, scratch = (
        Path(p).resolve() for p in (input_path, output_path, scratch)
    )
    if input_path == output_path or output_path.exists():
        raise WorkbookInputError('Use a distinct unused output path')
    if scratch.exists() and any(scratch.iterdir()):
        raise WorkbookInputError('Use an empty run folder')
    scratch.mkdir(parents=True, exist_ok=True)
    input_hash = sha(input_path)
    snapshot = scratch / 'input.xlsx'
    shutil.copyfile(input_path, snapshot)
    if sha(snapshot) != input_hash:
        raise WorkbookInputError('Input changed during snapshot')
    execution_hashes = execution_fingerprint()
    controls = read_all(snapshot)  # Every control/source gate before any MC.
    (scratch / 'validated_controls.json').write_text(
        json.dumps(controls, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.all-models-', dir=output_path.parent) as stage:
        paired_output = Path(stage) / 'paired.xlsx'
        candidate = Path(stage) / 'all.xlsx'
        first = paired.refresh(snapshot, paired_output, scratch / 'paired', preview=preview)
        # First verification checks both old models and preserves every extra sheet.
        second = timing.refresh(
            paired_output, candidate, scratch / 'timing', preview=preview,
            integrated_refresh=True,
        )
        # Second verification checks timing results and preserves ALL other cells.
        # Together these establish the three-model result without disabling either
        # verifier's scope checks or comparing a workbook to itself.
        if read_all(candidate) != controls:
            raise WorkbookInputError('Final controls differ from the validated inputs')
        if execution_fingerprint() != execution_hashes:
            raise WorkbookInputError('Model data or code changed during execution; result not published')
        if sha(input_path) != input_hash:
            raise WorkbookInputError('Input edited during execution; result not published')
        report = dict(
            all_models_refreshed=True, models=['joint', 'cash', 'timing'],
            all_controls_validated_before_simulation=True,
            controls=controls, paired=first, timing=second,
            verification_composition='paired preserves extras; timing preserves paired cells',
            output=str(output_path), input_sha256=input_hash, output_sha256=sha(candidate),
            input_preserved=True, atomic_new_output=True,
            native_Excel_tested=False, company_calibrated=False,
            orchestrator_sha256=sha(__file__),
            execution_sha256=execution_hashes,
        )
        # Only this link publishes the requested result; a competing file wins.
        # Save a validation record before publication, not a false success record.
        (scratch / 'validated_result.json').write_text(
            json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
        )
        os.link(candidate, output_path)
        report['published'] = True
        (scratch / 'verification.json').write_text(
            json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
        )
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--scratch', type=Path, required=True)
    ap.add_argument('--no-preview', action='store_true')
    args = ap.parse_args()
    print(json.dumps(refresh(args.input, args.output, args.scratch,
                             preview=not args.no_preview), ensure_ascii=False))
