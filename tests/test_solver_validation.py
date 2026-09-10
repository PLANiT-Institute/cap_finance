import pulp

from cap.solver_validation import validate_mip_solution


def point(value,status=pulp.LpStatusOptimal,solution=pulp.LpSolutionOptimal):
    model=pulp.LpProblem('probe',pulp.LpMinimize)
    x=pulp.LpVariable('x',0,1,cat='Binary')
    model+=x>=1
    model+=x
    x.varValue=value;model.status=status;model.sol_status=solution
    return model


def test_infeasible_solver_status_is_never_rescued_by_numeric_variable_values():
    result=validate_mip_solution(point(1,pulp.LpStatusInfeasible,pulp.LpSolutionNoSolutionFound))
    assert not result['valid']


def test_fractional_or_constraint_violating_points_are_not_incumbents():
    for value in [None,.5,0.,2.]:
        assert not validate_mip_solution(point(value))['valid']


def test_time_limited_integer_incumbent_requires_primal_feasibility():
    valid=validate_mip_solution(point(1,pulp.LpStatusNotSolved,pulp.LpSolutionIntegerFeasible))
    assert valid['valid'] and valid['solver_status']=='Not Solved'
    assert not validate_mip_solution(point(0,pulp.LpStatusNotSolved,pulp.LpSolutionIntegerFeasible))['valid']
