"""Declaration-derived linear emissions comparator, separately from asset plans.

A carbon-neutrality declaration is sufficient to define this reference path.
Its interpolation, baseline and gross/net accounting bridge remain explicit
analyst assumptions; the declaration does not identify investment cashflows.
"""
import numpy as np
import pandas as pd


def linear_disclosed_path(*, company_id, base_year, target_year, base_emissions,
                          years, declaration_source, baseline_source,
                          scope, accounting_basis, unit, target_emissions=0.):
    for name,value in dict(company_id=company_id,declaration_source=declaration_source,
        baseline_source=baseline_source,scope=scope,unit=unit).items():
        if not isinstance(value,str) or not value.strip():
            raise ValueError(f'Explicit {name} is required')
    for value in (base_year,target_year):
        if isinstance(value,bool) or not isinstance(value,(int,np.integer)):
            raise ValueError('Base and target years must be integers')
    if target_year<=base_year:
        raise ValueError('Target year must follow base year')
    if accounting_basis not in ('net','gross_zero_offset_assumption','normalized_declaration_index'):
        raise ValueError('Declare net, explicit gross/offset assumption, or normalized index basis')
    values=np.asarray([base_emissions,target_emissions],float)
    if not np.isfinite(values).all() or base_emissions<=0 or not 0<=target_emissions<=base_emissions:
        raise ValueError('Linear reduction needs positive baseline and nonnegative smaller target')
    y=np.asarray(years)
    if y.ndim!=1 or not len(y) or y.dtype.kind not in 'iu' or (y[1:]<=y[:-1]).any():
        raise ValueError('Years must be nonempty increasing integers')
    if (y<base_year).any():
        raise ValueError('Do not infer historical emissions before the baseline')
    progress=np.clip((y-base_year)/(target_year-base_year),0,1)
    e=base_emissions+(target_emissions-base_emissions)*progress
    return pd.DataFrame(dict(company_id=company_id,year=y,emissions=e,
        relative_to_baseline=e/base_emissions,unit=unit,scope=scope,
        accounting_basis=accounting_basis,base_year=base_year,target_year=target_year,
        comparison_basis='declaration_derived_linear_path',
        interpolation='linear_to_target_then_constant',
        declaration_source=declaration_source,baseline_source=baseline_source,
        technology_schedule_inferred=False,cost_evaluated=False))
