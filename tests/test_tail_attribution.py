import numpy as np
import pytest
from cap.tail_attribution import empirical_tail_weights, tail_decomposition


def test_fractional_tail_of_three_observations():
    w = empirical_tail_weights([0, 2, 10], .5)
    np.testing.assert_allclose(w, [0, 1/3, 2/3])
    assert w @ [0, 2, 10] == pytest.approx(22/3)


def test_ties_share_boundary_mass_without_arbitrary_component_order():
    a = np.array([[0, 0], [9, 1], [1, 9], [10, 10]])
    d = tail_decomposition(a, .625)  # Worst 1.5 paths:20 plus half of tied10.
    np.testing.assert_allclose(d['weights'], [0, 1/6, 1/6, 2/3])
    np.testing.assert_allclose(d['es_contributions'], [25/3, 25/3])
    perm = tail_decomposition(a[[3, 2, 0, 1]], .625)
    np.testing.assert_allclose(perm['es_contributions'], d['es_contributions'])


def test_tail_below_one_observation_and_all_equal_losses():
    np.testing.assert_allclose(empirical_tail_weights([2, 2, 2], .999), [1/3]*3)
    np.testing.assert_allclose(empirical_tail_weights([-9, -2, -2], .99), [0, .5, .5])


def test_zero_alpha_allocates_the_full_mean():
    d = tail_decomposition([[-2, 5], [8, -6], [7, 9]], 0)
    np.testing.assert_allclose(d['excess_contributions'], 0, atol=1e-14)


def test_signed_hedge_can_have_negative_excess_contribution():
    d = tail_decomposition([[0, 0], [100, -90], [0, 30]], .8)
    np.testing.assert_allclose(d['es_contributions'], [0, 30])
    np.testing.assert_allclose(d['excess_contributions'], [-100/3, 50])
    assert sum(d['excess_contributions']) == pytest.approx(d['es']-d['mean'])


def test_adding_fixed_cash_changes_es_but_not_excess_allocation():
    a = np.array([[0, 2], [10, 5], [4, 7]], float)
    before = tail_decomposition(a, .5)
    after = tail_decomposition(np.column_stack([a, np.full(3, 123)]), .5)
    np.testing.assert_allclose(after['excess_contributions'][:2], before['excess_contributions'])
    assert after['es_contributions'][2] == pytest.approx(123)
    assert after['excess_contributions'][2] == pytest.approx(0)


@pytest.mark.parametrize('a', [[], [1, 2], [[1, np.nan]], [[np.inf]], np.empty((3, 0))])
def test_invalid_component_matrix(a):
    with pytest.raises(ValueError): tail_decomposition(a)


@pytest.mark.parametrize('alpha', [-.1, 1, np.nan, True])
def test_invalid_alpha(alpha):
    with pytest.raises(ValueError): empirical_tail_weights([1, 2], alpha)
