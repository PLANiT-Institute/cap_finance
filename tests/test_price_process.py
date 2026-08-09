"""G5 평균회귀 검정기가 방향을 맞추는가.

작은 표본에서 '기각 못함'이 나오는 것은 정상이므로, 검정 자체가 **부호와 순서를**
맞추는지만 본다: 강한 평균회귀는 큰 음수 τ, 랜덤워크는 0 근처.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from price_process_test import adf_stat, hurst_rs, null_and_power  # noqa: E402


def test_adf_separates_random_walk_from_strong_mean_reversion():
    rng = np.random.default_rng(7)
    n = 200
    rw = np.cumsum(rng.normal(0, 0.05, n))
    ar = np.zeros(n)
    for t in range(1, n):
        ar[t] = 0.5 * ar[t - 1] + rng.normal(0, 0.05)
    assert adf_stat(rw) > -2.86      # 단위근 기각 실패
    assert adf_stat(ar) < -5.0       # 강한 회귀는 확실히 기각


def test_hurst_of_random_walk_returns_is_near_half():
    rng = np.random.default_rng(11)
    level = np.cumsum(rng.normal(0, 0.05, 4000))
    assert 0.4 < hurst_rs(level) < 0.65


def test_finite_sample_critical_value_is_stricter_than_asymptotic():
    """n=19의 5% 임계값은 점근값(-2.86)보다 낮아야 한다 — 표를 쓰면 과대기각한다."""
    crit, power, _ = null_and_power(19, 0.07, np.log(2) / 120.0,
                                    np.random.default_rng(3), nsim=2000)
    assert crit < -2.86
    assert power < 0.15              # 반감기 10년은 n=19에서 사실상 검출 불가


def test_adf_returns_nan_when_too_few_observations():
    assert np.isnan(adf_stat(np.array([1.0, 1.1, 1.2])))
