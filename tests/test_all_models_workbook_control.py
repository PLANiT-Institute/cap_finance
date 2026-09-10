"""A failed third model must not publish a partially refreshed workbook."""
from pathlib import Path
import json
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import all_models_workbook_control as all_models


@pytest.fixture
def run(tmp_path, monkeypatch):
    source = tmp_path / 'input.xlsx'
    source.write_bytes(b'saved input')
    target, scratch = tmp_path / 'output.xlsx', tmp_path / 'run'
    events = []
    controls = dict(joint={'paths': 103}, cash={'paths': 107}, timing={'paths': 109})

    def read(path):
        events.append('validate')
        return controls.copy()

    def paired(source, target, scratch, **kwargs):
        events.append('paired')
        Path(target).write_bytes(b'first two complete')
        return {'both_models_refreshed': True}

    def timing(source, target, scratch, **kwargs):
        assert kwargs['integrated_refresh'] is True
        assert Path(source).read_bytes() == b'first two complete'
        events.append('timing')
        Path(target).write_bytes(b'all three complete')
        return {'candidates_checked': 4}

    monkeypatch.setattr(all_models, 'read_all', read)
    monkeypatch.setattr(all_models.paired, 'refresh', paired)
    monkeypatch.setattr(all_models.timing, 'refresh', timing)
    return source, target, scratch, events


def test_all_input_validation_precedes_any_model(run, monkeypatch):
    source, target, scratch, events = run
    def fail(path):
        raise all_models.WorkbookInputError('invalid Timing control')
    monkeypatch.setattr(all_models, 'read_all', fail)
    with pytest.raises(all_models.WorkbookInputError):
        all_models.refresh(source, target, scratch)
    assert events == [] and not target.exists()


@pytest.mark.parametrize('stage', ['paired', 'timing'])
def test_stage_failure_never_publishes_partial_result(run, monkeypatch, stage):
    source, target, scratch, events = run
    def fail(*args, **kwargs):
        raise AssertionError('saved formula mismatch')
    monkeypatch.setattr(getattr(all_models, stage), 'refresh', fail)
    with pytest.raises(AssertionError, match='formula'):
        all_models.refresh(source, target, scratch)
    assert not target.exists() and source.read_bytes() == b'saved input'
    assert not list(target.parent.glob('.all-models-*'))
    assert not (scratch / 'verification.json').exists()


def test_final_control_mismatch_prevents_publication(run, monkeypatch):
    source, target, scratch, events = run
    read = all_models.read_all
    def mismatch(path):
        result = read(path)
        if Path(path).name == 'all.xlsx':
            result['timing'] = {'paths': 999}
        return result
    monkeypatch.setattr(all_models, 'read_all', mismatch)
    with pytest.raises(all_models.WorkbookInputError, match='Final controls'):
        all_models.refresh(source, target, scratch)
    assert not target.exists()


def test_concurrent_user_input_preserved(run, monkeypatch):
    source, target, scratch, events = run
    third = all_models.timing.refresh
    def edit(*args, **kwargs):
        result = third(*args, **kwargs)
        source.write_bytes(b'user edit')
        return result
    monkeypatch.setattr(all_models.timing, 'refresh', edit)
    with pytest.raises(all_models.WorkbookInputError, match='edited during'):
        all_models.refresh(source, target, scratch)
    assert source.read_bytes() == b'user edit' and not target.exists()


def test_competing_output_preserved_without_false_success_record(run, monkeypatch):
    source, target, scratch, events = run
    third = all_models.timing.refresh
    def compete(*args, **kwargs):
        result = third(*args, **kwargs)
        target.write_bytes(b'other output')
        return result
    monkeypatch.setattr(all_models.timing, 'refresh', compete)
    with pytest.raises(FileExistsError):
        all_models.refresh(source, target, scratch)
    assert target.read_bytes() == b'other output'
    assert not (scratch / 'verification.json').exists()
    assert not json.loads((scratch / 'validated_result.json').read_text()).get('published')


@pytest.mark.parametrize('occupied', ['output', 'scratch', 'same_path'])
def test_existing_files_and_evidence_preserved(run, occupied):
    source, target, scratch, events = run
    if occupied == 'output': target.write_bytes(b'existing output')
    elif occupied == 'scratch':
        scratch.mkdir(); (scratch / 'keep.txt').write_text('existing evidence')
    else: target = source
    with pytest.raises(all_models.WorkbookInputError):
        all_models.refresh(source, target, scratch)
    assert events == [] and source.read_bytes() == b'saved input'
    if occupied == 'output': assert target.read_bytes() == b'existing output'
    elif occupied == 'scratch': assert (scratch / 'keep.txt').read_text() == 'existing evidence'


def test_success_publishes_only_after_three_models_and_final_validation(run):
    source, target, scratch, events = run
    report = all_models.refresh(source, target, scratch)
    assert events == ['validate', 'paired', 'timing', 'validate']
    assert target.read_bytes() == b'all three complete'
    assert source.read_bytes() == b'saved input'
    assert report['published'] and report['all_models_refreshed']
    assert report['output_sha256'] == all_models.sha(target)
    assert json.loads((scratch / 'verification.json').read_text()) == report


def test_missing_timing_sheets_rejected_before_defaults(monkeypatch):
    monkeypatch.setattr(all_models, 'read_cells', lambda p: {'Timing': {}})
    with pytest.raises(all_models.WorkbookInputError, match='complete Timing'):
        all_models.read_all('partial.xlsx')


def test_changed_engine_during_run_prevents_publication(run, monkeypatch):
    source, target, scratch, events = run
    hashes = iter([{'engine.py': 'before'}, {'engine.py': 'after'}])
    monkeypatch.setattr(all_models, 'execution_fingerprint', lambda: next(hashes))
    with pytest.raises(all_models.WorkbookInputError, match='data or code changed'):
        all_models.refresh(source, target, scratch)
    assert not target.exists()


def test_bad_reviewed_source_prevents_any_simulation(run, monkeypatch):
    source, target, scratch, events = run
    def fail():
        raise all_models.WorkbookInputError('Reviewed source hash changed')
    monkeypatch.setattr(all_models, 'execution_fingerprint', fail)
    with pytest.raises(all_models.WorkbookInputError, match='Reviewed source'):
        all_models.refresh(source, target, scratch)
    assert events == [] and not target.exists()
