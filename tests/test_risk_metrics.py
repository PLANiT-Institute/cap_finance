"""Analytical counterexamples, not comparisons to the implementation itself."""

import numpy as np
import pytest

from cap.risk_metrics import expected_shortfall, finite_candidate_gap, loss_summary


def test_es_includes_fractional_tail_mass():
    # Worst 1.5 of three equiprobable observations: (10 + 0.5*2) / 1.5.
    assert expected_shortfall([0, 2, 10], .5) == pytest.approx(22 / 3)


def test_es_handles_ties_and_negative_costs():
    assert expected_shortfall([0] * 95 + [100] * 5, .9) == pytest.approx(50)
    assert expected_shortfall([-10, -10, -10], .9) == pytest.approx(-10)
    assert expected_shortfall([1, 3, 8], 0) == pytest.approx(4)
    assert expected_shortfall([1, 3, 8], .999) == pytest.approx(8)


def test_tcar_misses_rare_tail_but_es_and_mean_respond():
    s = loss_summary([0] * 95 + [100] * 5)
    assert s["p50"] == s["tcar"] == 0
    assert s["mean"] == 5
    assert s["es_alpha"] == pytest.approx(50)


def test_tcar_is_shift_invariant_and_not_a_capital_level():
    x = np.arange(100, dtype=float)
    before, after = loss_summary(x), loss_summary(x + 700)
    assert after["tcar"] == pytest.approx(before["tcar"])
    for field in ["mean", "p50", "q_alpha", "es_alpha"]:
        assert after[field] - before[field] == pytest.approx(700)


def test_tcar_is_not_monotone_in_loss():
    x = np.r_[np.zeros(80), np.ones(20) * 100]
    y = np.ones(100) * 100
    assert np.all(x <= y)
    assert loss_summary(x)["tcar"] == 100
    assert loss_summary(y)["tcar"] == 0


def test_tcar_not_subadditive_for_disjoint_tail_events():
    x, y = np.zeros(100), np.zeros(100)
    x[:6], y[6:12] = 100, 100
    assert loss_summary(x)["tcar"] == loss_summary(y)["tcar"] == 0
    assert loss_summary(x + y)["tcar"] == 100
    assert expected_shortfall(x + y) <= expected_shortfall(x) + expected_shortfall(y)


def test_cost_plus_tcar_can_select_a_pathwise_worse_plan():
    # Y costs at least X in every state, and strictly more in 80% of states.
    # A spread objective can prefer Y despite this pathwise dominance.
    x = np.r_[np.zeros(80), np.ones(20) * 100]
    y = np.full(100, 100.)
    a, b = loss_summary(x), loss_summary(y)
    lam = 2
    assert b["p50"] + lam*b["tcar"] < a["p50"] + lam*a["tcar"]
    assert b["mean"] + lam*b["tcar"] < a["mean"] + lam*a["tcar"]
    assert a["mean"] + lam*a["es_alpha"] < b["mean"] + lam*b["es_alpha"]


def test_linear_frontier_segment_can_invent_attainable_savings():
    # A=(cost10,risk0), B=(cost0,risk10); disclosed=(cost7,risk5).
    # A line would suggest cost saving 2 and risk saving 2. Neither exists.
    assert finite_candidate_gap([10, 0], [0, 10], 7, 5) == (0, 0)


def test_finite_gap_thresholds_and_endpoints():
    assert finite_candidate_gap([10, 0], [0, 10], 12, 12) == (12, 12)
    c, r = finite_candidate_gap([10, 5], [2, 10], 7, 1)
    assert np.isnan(c) and r == 0
    assert all(np.isnan(v) for v in finite_candidate_gap([], [], 1, 1))


@pytest.mark.parametrize("x", [[], [1, np.nan], [np.inf], [[1, 2]]])
def test_invalid_draws_are_not_silently_removed(x):
    with pytest.raises(ValueError):
        loss_summary(x)


@pytest.mark.parametrize("alpha", [-1, 1, np.nan])
def test_invalid_es_probability_rejected(alpha):
    with pytest.raises(ValueError):
        expected_shortfall([1, 2], alpha)


def test_invalid_candidate_vectors_rejected():
    with pytest.raises(ValueError):
        finite_candidate_gap([1], [1, 2], 1, 1)
    with pytest.raises(ValueError):
        finite_candidate_gap([np.nan], [1], 1, 1)
