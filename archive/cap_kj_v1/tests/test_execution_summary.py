from pathlib import Path

from cap_kj.execution_summary import build_summary


ROOT = Path(__file__).resolve().parents[1]


def test_summary_contains_current_decision_outputs() -> None:
    report = build_summary(ROOT)
    assert "Run 0–13, 총 14회" in report
    assert "18.153" in report
    assert "6.017" in report
    assert "13.15%" in report
    assert "7.61배" in report
    assert "22 PASS, 7 WARN, 0 FAIL" in report
    assert "59/59 통과" in report


def test_summary_preserves_release_boundaries() -> None:
    report = build_summary(ROOT)
    assert "Mitsui 비용 경계 97.46%와 지원실험 경계 85.00%" in report
    assert "verified incentive-adjusted gap은 전 회사 `NA`" in report
    assert "operational abatement를 system abatement로 부를 수 없다" in report
    assert "확정 투자·실현 보조금·system abatement·기업가치 판단에는 사용할 수 없다" in report
