import itertools
import math
import pytest
from cap.production_bounds import additive_output_bounds


def test_bounds_equal_exhaustive_feasible_lattice():
    caps={'A':2,'B':3,'C':4}
    for total in range(10):
        feasible=[x for x in itertools.product(range(3),range(4),range(5)) if sum(x)==total]
        result=additive_output_bounds(total,caps)
        for i,k in enumerate(caps):
            assert result[k]==(min(x[i] for x in feasible),max(x[i] for x in feasible))


def test_single_component_and_zero_output():
    assert additive_output_bounds(2,{'only':3})=={'only':(2,2)}
    assert additive_output_bounds(0,{'A':0,'B':3})=={'A':(0,0),'B':(0,0)}


def test_lotte_hypothesis_endpoints_are_attainable():
    for gamma in (1,1.05,1.1):
        caps={'ethylene':2330000*gamma,'propylene':1191000*gamma}
        r=additive_output_bounds(2848129,caps)
        for q in r['ethylene']:
            other=2848129-q
            assert 0<=q<=caps['ethylene'] and 0<=other<=caps['propylene']+1e-8
    assert additive_output_bounds(2848129,{'ethylene':2330000,'propylene':1191000})['ethylene']==(1657129,2330000)


@pytest.mark.parametrize('total,caps',[(4,{'A':3}),(-1,{'A':3}),(math.nan,{'A':3}),
    (1,{'A':None}),(1,{'A':math.inf}),(True,{'A':3}),(1,{}),(0,{'':1})])
def test_invalid_or_infeasible_identity_rejected(total,caps):
    with pytest.raises(ValueError):additive_output_bounds(total,caps)
