"""Old identical results must not be described as a fresh-control partial rerun."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_tech_guide as guide


def test_drift_distinguishes_zero_from_unmeasured():
    values = {("POSCO", "NZ15", "none"): (100.0, 200.0)}
    count, cost, risk = guide._drift(values, values)
    assert count == 0 and "+0.00%" in cost and "+0.00%" in risk
    assert guide._drift({}, values) == (0, "—", "—")


def test_partial_rerun_requires_a_newer_control(tmp_path, monkeypatch):
    content = ("company_id,scenario,support,cost_per_tco2_thkrw,tcar_bnkrw\n"
               "POSCO,NZ15,none,100,200\n")
    files = [tmp_path / "out/e5/metrics_company.csv",
             tmp_path / "out/process/gbm/e5/metrics_company.csv",
             tmp_path / "out/process/ou/e5/metrics_company.csv"]
    for f, stamp in zip(files, [200, 100, 100]):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
        os.utime(f, (stamp, stamp))
    monkeypatch.setattr(guide, "ROOT", tmp_path)
    old = guide.gen_diagnostic_drift()
    assert "2 of 2" in old and "+0.00%" in old
    assert "is part re-run" not in old
    assert "Timestamps alone do not establish" in old
    os.utime(files[1], (300, 300))
    partial = guide.gen_diagnostic_drift()
    assert "1 of 2" in partial
    assert "is part re-run" in partial
