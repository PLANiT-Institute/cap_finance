"""시나리오 묶음이 실제로 무언가를 흔들었는가 (M5, D14).

`scripts/run_scenarios.py`는 E1·E2를 심볼릭 링크로 공유하고 E3–E5만 다시 돈다. 그래서
**E2에서만 읽히는 축**(유상할당 비중, PPA 프리미엄, 폐쇄 상한, 예산위반 벌칙)을 `--replan`
없이 돌리면 base와 소수점까지 같은 수가 나오고, 그것이 요약표에 "검증됨"으로 남는다.
D14 전까지 넷이 그 상태였다 — 읽는 사람에게는 "흔들었는데 안 변했다"로 보이지만 흔든 적이
없다. §5.4의 빈 지원 축과 같은 종류의 결함이다.

여기서 거는 것은 **값이 아니라 그 대응**이다.

  (1) base와 구분 불가한 묶음은 전부 `REPLAN_REQUIRED`에 있어야 한다 — 설명되지 않은
      평평함이 새로 생기면 깨진다.
  (2) `--replan`으로 돈 E2 전용 묶음은 base와 달라야 한다 — 재계획이 실제로 계획 메뉴를
      바꿨는지 확인한다. 안 바뀌면 그 축은 E2에서도 무력하다는 뜻이고 §6.2를 고쳐야 한다.

Run: .venv/bin/pytest tests/test_scenario_bundles.py -q
"""

import importlib.util
import pathlib

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out" / "scenarios" / "summary.csv"
# p50_incl_carbon 포함 — 빼면 유상할당 램프처럼 "헤드라인에만 안 닿는" 축이
# "무력한" 축으로 잘못 잡힌다 (§6.2)
KEYS = ["p50_bnkrw", "cost_per_tco2_thkrw", "tcar_bnkrw", "capex_total_bnkrw",
        "p50_incl_carbon_bnkrw"]
TOL = 1e-6      # 부동소수 잡음(1e-9 수준)은 변화가 아니다


def _run_scenarios():
    spec = importlib.util.spec_from_file_location(
        "run_scenarios", ROOT / "scripts" / "run_scenarios.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _deltas() -> dict[str, float]:
    if not SUMMARY.exists():
        pytest.skip(f"{SUMMARY.relative_to(ROOT)} 없음 — run_scenarios.py 먼저 실행")
    s = pd.read_csv(SUMMARY)
    idx = ["company_id", "scenario", "support"]
    base = s[s.bundle == "base"].set_index(idx)[KEYS]
    assert not base.empty, "base 묶음이 요약표에 없다"
    return {n: float((d.set_index(idx)[KEYS] - base).abs().max().max())
            for n, d in s[s.bundle != "base"].groupby("bundle")}


def test_replan_required_covers_every_e2_only_override():
    """BUNDLES에 milp/contracts/유상할당 축을 새로 넣고 REPLAN_REQUIRED에 안 넣으면 깨진다."""
    m = _run_scenarios()
    e2_only = {n for n, (_, over) in m.BUNDLES.items()
               if set(over) & {"milp", "contracts", "carbon_auction_share"}}
    assert e2_only <= m.REPLAN_REQUIRED, (
        f"E2에서만 읽히는 축인데 REPLAN_REQUIRED에 없다: {sorted(e2_only - m.REPLAN_REQUIRED)}. "
        "이대로 두면 --replan 없이 돌아 base와 같은 수가 요약표에 실린다.")


def test_flat_bundles_are_exactly_the_ones_we_know_are_flat():
    """설명되지 않은 '변화 0'이 새로 생기면 알린다."""
    m, d = _run_scenarios(), _deltas()
    flat = {n for n, v in d.items() if v <= TOL}
    unexplained = flat - m.REPLAN_REQUIRED
    assert not unexplained, (
        f"base와 구분되지 않는데 이유가 등록되지 않은 묶음: {sorted(unexplained)}. "
        "그 축이 E3–E5에 등장하지 않는지 확인하고, 맞으면 REPLAN_REQUIRED에 넣어라.")


def test_replanned_e2_bundles_actually_moved():
    """재계획한 E2 전용 묶음은 base와 달라야 한다 — 같으면 그 축은 E2에서도 무력하다."""
    if not SUMMARY.exists():
        pytest.skip("요약표 없음")
    m, d = _run_scenarios(), _deltas()
    s = pd.read_csv(SUMMARY)
    replanned = set(s[s.replanned & (s.bundle != "base")].bundle) & m.REPLAN_REQUIRED
    if not replanned:
        pytest.skip("재계획된 E2 전용 묶음이 아직 없다 — run_scenarios.py <묶음> --replan")
    dead = {n for n in replanned if d[n] <= TOL}
    assert not dead, (f"--replan으로 돌았는데도 base와 같다: {sorted(dead)}. "
                      "그 축은 계획 선택도 바꾸지 못한다는 뜻이고 §6.2가 그렇게 적어야 한다.")
