"""Validate the returned primal point before treating it as an executable plan."""
import math

import pulp


def validate_mip_solution(model, *, absolute_tolerance=1e-7, relative_tolerance=1e-8):
    """Reject terminal failure, fractional relaxations, missing and infeasible values.

    A time limit with a solver-reported integer feasible incumbent can pass, but
    does not become an optimality proof. Constraint tolerance scales with the
    evaluated row magnitude; the caller must retain this numerical convention.
    """
    problems=[]
    status=pulp.LpStatus[model.status]
    solution_status=pulp.LpSolution.get(model.sol_status,str(model.sol_status))
    if model.status in (pulp.LpStatusInfeasible,pulp.LpStatusUnbounded,pulp.LpStatusUndefined):
        problems.append(f'terminal solver status {status}')
    if model.sol_status not in (pulp.LpSolutionOptimal,pulp.LpSolutionIntegerFeasible):
        problems.append(f'no reported integer feasible solution: {solution_status}')
    for variable in model.variables():
        value=variable.value()
        if variable.name=='__dummy' and value is None:
            continue
        if value is None or not math.isfinite(value):
            problems.append(f'{variable.name}: missing/nonfinite value')
            continue
        if variable.cat==pulp.LpInteger and abs(value-round(value))>absolute_tolerance:
            problems.append(f'{variable.name}: fractional integer decision')
        if variable.lowBound is not None and value<variable.lowBound-absolute_tolerance:
            problems.append(f'{variable.name}: below lower bound')
        if variable.upBound is not None and value>variable.upBound+absolute_tolerance:
            problems.append(f'{variable.name}: above upper bound')
    max_scaled_violation=0.
    for name,constraint in model.constraints.items():
        value=constraint.value()
        if value is None or not math.isfinite(value):
            problems.append(f'{name}: missing/nonfinite constraint value')
            continue
        violation=(abs(value) if constraint.sense==pulp.LpConstraintEQ else
                   max(value,0.) if constraint.sense==pulp.LpConstraintLE else max(-value,0.))
        scale=max(1.,abs(constraint.constant),sum(abs(coefficient*variable.value())
                  for variable,coefficient in constraint.items() if variable.value() is not None))
        max_scaled_violation=max(max_scaled_violation,violation/scale)
        if violation>absolute_tolerance+relative_tolerance*scale:
            problems.append(f'{name}: primal constraint violation {violation:g}')
    return dict(valid=not problems,solver_status=status,solution_status=solution_status,
                max_scaled_constraint_violation=max_scaled_violation,
                absolute_tolerance=absolute_tolerance,relative_tolerance=relative_tolerance,
                problems=problems)
