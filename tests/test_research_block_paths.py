"""Accounting identities and block-distribution invariants, not fit validation."""
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from research_block_price_paths import block_paths, expected_shortfall


def test_exact_anchor_against_exhaustive_independent_blocks():
    r = np.array([[.1, -.2], [.3, .1], [-.2, .4], [.05, -.1]])
    _, a, _ = block_paths(r, months=5, paths=2, block_length=2, seed=3)
    centered = r-r.mean(axis=0)
    # Three independently selected blocks, with a truncated final block.
    all_paths = []
    for starts in itertools.product(range(3), repeat=3):
        z = np.concatenate([centered[s:s+2] for s in starts])[:5].cumsum(axis=0)
        all_paths.append(np.exp(z-a))
    np.testing.assert_allclose(np.mean(all_paths, axis=0), 1., atol=1e-14)


def test_joint_same_starts_and_reproducibility():
    x = np.array([-.1, .2, -.05, .15])
    r = np.column_stack([x, x])
    first = block_paths(r, 7, 17, 3, 45)
    second = block_paths(r, 7, 17, 3, 45)
    for a,b in zip(first,second):
        np.testing.assert_array_equal(a,b)
    np.testing.assert_array_equal(first[0][:,:,0], first[0][:,:,1])


def test_constant_history_and_invalid_inputs():
    x, _, _ = block_paths(np.ones((7,2)), 24, 30, 6, 8)
    np.testing.assert_array_equal(x, np.ones_like(x))
    with pytest.raises(ValueError):
        block_paths(np.array([[np.nan]]), 1, 1, 1, 1)


def test_fractional_tail_mass():
    assert expected_shortfall([0.,10.,20.], .5) == pytest.approx(50/3)
