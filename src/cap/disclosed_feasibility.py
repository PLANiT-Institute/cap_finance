"""Optimistic emissions lower bound for a declared linear reference path.

Fixed output, no retirement, no unlisted technology or removals. Each facility
may pick its lowest-emission available route independently in every year. This
relaxes one-investment, financing and resource constraints, so exceeding a cap
certifies infeasibility under the tighter menu; meeting it proves no feasible
investment schedule. Corporate net-zero scope is not inferred here.
"""
import numpy as np
import pandas as pd


def emission_floor(facilities,technologies,years,*,earliest_start_year,availability):
    y=np.asarray(years)
    if y.ndim!=1 or not len(y) or y.dtype.kind not in 'iu' or (y[1:]<=y[:-1]).any():
        raise ValueError('Nonempty strictly increasing integer years required')
    if isinstance(earliest_start_year,bool) or not isinstance(earliest_start_year,(int,np.integer)):
        raise ValueError('Explicit integer earliest investment year required')
    if facilities.empty or not facilities.index.is_unique or not technologies.tech_id.is_unique:
        raise ValueError('Nonempty unique facilities and unique technologies required')
    fcols=['production','ef_inc'];tcols=['emission_factor','avail_year','build_years']
    f=facilities[fcols].to_numpy(float);t=technologies[tcols].to_numpy(float)
    if not np.isfinite(f).all() or not np.isfinite(t).all() or (f<0).any() or (t[:,[0,2]]<0).any():
        raise ValueError('Nonnegative finite output/emission factors/build durations required')
    if (t[:,1:]!=np.floor(t[:,1:])).any():
        raise ValueError('Availability and construction duration must be integer years')
    rows=[]
    for fid,fr in facilities.iterrows():
        options=technologies[(technologies.sector==fr.sector)&(technologies.applies_to_unit==fr.unit_type)]
        for year in y:
            candidates=[('incumbent',float(fr.ef_inc),None)]
            for tk in options.itertuples():
                a=availability.get(tk.tech_id,tk.avail_year)
                if isinstance(a,bool) or not np.isfinite(a) or a!=int(a):
                    raise ValueError('Scenario availability must be an integer year')
                operation=max(earliest_start_year,int(a),int(tk.avail_year))+int(tk.build_years)
                if operation<=year:
                    candidates.append((tk.tech_id,float(tk.emission_factor),operation))
            tech,ef,operation=min(candidates,key=lambda c:(c[1],c[0]))
            rows.append(dict(facility_id=fid,company_id=fr.company_id,year=int(year),
                floor_tech_id=tech,earliest_operation_year=operation,
                production_t=float(fr.production),emission_factor=ef,
                floor_emissions_tco2=float(fr.production)*ef,
                bound_type='optimistic_independent_year_route_choice_no_retirement_or_removals'))
    detail=pd.DataFrame(rows)
    aggregate=detail.groupby(['company_id','year'],as_index=False).floor_emissions_tco2.sum()
    return aggregate,detail
