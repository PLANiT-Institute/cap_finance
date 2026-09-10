import numpy as np

from cap.risk_metrics import sampled_dominance_witnesses, pareto_mask, loss_summary


def test_lower_tcar_does_not_rescue_a_pathwise_dominated_loss():
    # X: 80% zero,20%100. Y: certain100. TCaR(Y)=0 but X<=Y in every state.
    x=np.array([0.]*8+[100.]*2);y=np.full(10,100.)
    assert loss_summary(y)['tcar'] < loss_summary(x)['tcar']
    assert sampled_dominance_witnesses({'X':x,'Y':y}) == {'Y':'X'}


def test_crossing_losses_and_identical_losses_have_no_strict_dominance():
    assert sampled_dominance_witnesses({'A':np.array([0,2]),'B':np.array([2,0]),
                                        'C':np.array([0,2])}) == {}
    np.testing.assert_equal(pareto_mask([1,2,3,1],[3,2,4,3]),[True,True,False,True])
