"""Failure containment for a two-model refresh; actual XLSX roundtrips are separate."""
from pathlib import Path
import json
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import unified_workbook_control as u


@pytest.fixture
def fake_run(tmp_path, monkeypatch):
    source = tmp_path/'input.bin'; source.write_bytes(b'original saved input')
    target = tmp_path/'output.xlsx'; scratch = tmp_path/'run'
    events = []
    monkeypatch.setattr(u, 'read_both', lambda p: ({'mode': 'joint'}, {'mode': 'cash'}))
    def joint_payload(c, folder):
        events.append('joint'); folder.mkdir(parents=True)
        p=folder/'payload.json'; p.write_text('{}'); return p
    def cash_evaluate(c):
        events.append('cash'); return {}
    def builder(cmd, **kw):
        events.append('builder'); Path(cmd[3]).write_bytes(b'candidate output')
    monkeypatch.setattr(u.joint, 'payload', joint_payload)
    monkeypatch.setattr(u.cash, 'evaluate', cash_evaluate)
    monkeypatch.setattr(u.subprocess, 'run', builder)
    monkeypatch.setattr(u, 'verify_saved', lambda p, data: {'verified': True})
    return source, target, scratch, events


def test_second_model_failure_does_not_publish(fake_run, monkeypatch):
    source,target,scratch,events=fake_run
    def fail(c): raise RuntimeError('capital model failed')
    monkeypatch.setattr(u.cash,'evaluate',fail)
    with pytest.raises(RuntimeError, match='capital'):u.refresh(source,target,scratch)
    assert events==['joint'] and not target.exists()
    assert source.read_bytes()==b'original saved input'


def test_validate_both_before_running_either(fake_run, monkeypatch):
    source,target,scratch,events=fake_run
    def fail(p): raise u.WorkbookInputError('invalid second control')
    monkeypatch.setattr(u,'read_both',fail)
    with pytest.raises(u.WorkbookInputError):u.refresh(source,target,scratch)
    assert events==[] and not target.exists()


def test_saved_formula_failure_does_not_publish(fake_run, monkeypatch):
    source,target,scratch,events=fake_run
    def fail(p,data):raise AssertionError('saved formula mismatch')
    monkeypatch.setattr(u,'verify_saved',fail)
    with pytest.raises(AssertionError):u.refresh(source,target,scratch)
    assert not target.exists() and source.read_bytes()==b'original saved input'
    assert not list(target.parent.glob('.tcar-refresh-*'))


def test_input_edit_during_run_prevents_publication(fake_run, monkeypatch):
    source,target,scratch,events=fake_run
    def verify(p,data):source.write_bytes(b'new user edit');return {}
    monkeypatch.setattr(u,'verify_saved',verify)
    with pytest.raises(u.WorkbookInputError,match='edited during'):u.refresh(source,target,scratch)
    assert source.read_bytes()==b'new user edit' and not target.exists()


def test_existing_output_is_not_overwritten(fake_run):
    source,target,scratch,events=fake_run;target.write_bytes(b'previous result')
    with pytest.raises(u.WorkbookInputError):u.refresh(source,target,scratch)
    assert target.read_bytes()==b'previous result' and events==[]


def test_competing_output_created_before_publish_is_preserved(fake_run, monkeypatch):
    source,target,scratch,events=fake_run
    def verify(p,data):target.write_bytes(b'competing result');return {}
    monkeypatch.setattr(u,'verify_saved',verify)
    with pytest.raises(FileExistsError):u.refresh(source,target,scratch)
    assert target.read_bytes()==b'competing result'


def test_success_publishes_after_both_models(fake_run):
    source,target,scratch,events=fake_run
    r=u.refresh(source,target,scratch)
    assert events==['joint','cash','builder']
    assert target.read_bytes()==b'candidate output' and source.read_bytes()==b'original saved input'
    assert r['output_sha256']==u.sha(target) and r['both_models_refreshed']
    assert json.loads((scratch/'verification.json').read_text())==r


def test_nonempty_run_folder_preserved(fake_run):
    source,target,scratch,events=fake_run;scratch.mkdir();(scratch/'evidence.txt').write_text('keep')
    with pytest.raises(u.WorkbookInputError,match='empty'):u.refresh(source,target,scratch)
    assert (scratch/'evidence.txt').read_text()=='keep' and events==[]
