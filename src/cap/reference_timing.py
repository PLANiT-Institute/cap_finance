"""Dated replacement candidates within the fixed Tiggeloven reference experiment.

Not a corporate retrofit quote. Source operating quantities, constant full output,
zero downtime, 3-year construction, 20-year new plant life and no terminal receipts
are explicit conditions. Carbon quantities are evaluated separately from cash.
"""
from dataclasses import replace
import numpy as np
from .reference_ncc import NCCConditions, build_ncc_reference
from .reference_incumbent import existing_ncc_pair
from .capital_ledger import facility_capital_ledger
from .component_capital import CapitalComponent,component_capital_cashflows


def timing_menu(observations,commission_years,*,remaining_years,replacement_cost_scale,numerical_KRW_per_EUR):
    years=tuple(range(2027,2051));yy=np.asarray(years);T=len(years)
    dates=tuple(commission_years)
    if not dates or len(set(dates))!=len(dates) or any(isinstance(y,bool) or not isinstance(y,int) or not 2030<=y<=2050 for y in dates):
        raise ValueError('Unique exact commissioning years2030to2050 required')
    refs=[build_ncc_reference(observations,c,years,NCCConditions(1.,8000,life,psi,.04,.05,1.,'none'),numerical_KRW_per_EUR=numerical_KRW_per_EUR) for c,life,psi in [('conventional',30,.04),('electric',20,.02)]]
    v={(r['case'],r['item']):float(r['value']) for r in observations};yield_=v['conventional','ethylene_yield']
    pair=existing_ncc_pair(*refs,years=years,remaining_years=remaining_years,replacement_cost_scale=replacement_cost_scale,retirement_cash_EUR=0.,salvage_receipt_EUR=0.,terminal_rule='none',ethylene_yield=yield_,numerical_KRW_per_EUR=numerical_KRW_per_EUR)
    old,new=refs;factor=numerical_KRW_per_EUR/1000.;result={}
    for date in dates:
        operated=yy>=date
        def quantity(field):return np.where(operated,np.asarray(getattr(new['profile'],field))[3],np.asarray(getattr(old['profile'],field))[3])
        flows=tuple(replace(f,quantity=np.where(operated,f.quantity[3],o.quantity[3])) for f,o in zip(new['profile'].additional_commodity_flows,old['profile'].additional_commodity_flows))
        cap=component_capital_cashflows((CapitalComponent('plant',new['initial_plant_EUR'],20),CapitalComponent('boiler',new['initial_boiler_EUR'],25)),1.,date-3,3,years,unit_of_account='EUR2019_assumed_operating_price_basis',terminal_rule='none')
        old_renewal=np.zeros(T)
        for component,cost,life in [('plant',old['initial_plant_EUR'],30),('boiler',old['initial_boiler_EUR'],25)]:
            f=dict(capacity=1.,incumbent_capex_unit=cost*replacement_cost_scale,reinvest_cycle_yr=life,last_reline_year=2027+remaining_years-life)
            old_renewal+=facility_capital_ledger(f,None,date,years,retire=True,terminal_rule='none').incumbent_renewal_k
        maintenance=np.where(operated,new['maintenance_EUR'][3],old['maintenance_EUR'][3])
        construction=cap.construction.sum(axis=0);renewal=cap.renewal.sum(axis=0)
        p=replace(new['profile'],grid_mwh=quantity('grid_mwh'),additional_commodity_flows=flows,other_cost_k=maintenance*factor,
          capex_k=(construction+renewal+old_renewal)*factor,capex_by_tech={'construction':construction*factor},capex_unc={'construction':0.},
          maintenance_capex_k=(renewal+old_renewal)*factor,terminal_value_k=np.zeros(T))
        output=np.full(T,old['output_t'][3]);np.testing.assert_allclose(flows[0].quantity*yield_,output,rtol=0,atol=1e-7)
        result[f'replace_{date}']=dict(profile=p,output_t=output,commission_year=date,electric_active=operated,
           fixed_cash_EUR=maintenance+construction+renewal+old_renewal,construction_EUR=construction,new_renewal_EUR=renewal,incumbent_renewal_EUR=old_renewal)
    return dict(years=years,candidates=result,baseline=pair['profiles']['continue_existing'],baseline_fixed_cash_EUR=pair['annual']['continue_existing']['net_fixed_cash_EUR'],source_yield=yield_,references=refs)


def emission_qualification(emissions,*,annual_caps,cumulative_cap,terminal_cap):
    """Three distinct tests. No mixing of annual/total constraints or missing data."""
    e=np.asarray(emissions,dtype=float);a=np.asarray(annual_caps,dtype=float)
    if e.ndim!=1 or not len(e) or a.shape!=e.shape or not np.isfinite(e).all() or not np.isfinite(a).all() or np.any(e<0) or np.any(a<0):raise ValueError('Aligned finite nonnegative annual quantities required')
    for x in [cumulative_cap,terminal_cap]:
        if isinstance(x,bool) or not isinstance(x,(int,float)) or not np.isfinite(x) or x<0:raise ValueError('Finite nonnegative budget required')
    return dict(annual_feasible=bool(np.all(e<=a+1e-7)),cumulative_feasible=bool(e.sum()<=cumulative_cap+1e-7),terminal_feasible=bool(e[-1]<=terminal_cap+1e-7))
