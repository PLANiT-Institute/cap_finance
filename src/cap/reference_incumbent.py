"""Conditional existing-asset NCC counterfactual using the existing capital ledger.

New-build source costs are explicit replacement proxies, never observed asset
book values or retrofit quotations. Historical payments are sunk; future cash
receipts/costs are separately specified. Zero replacement downtime is assumed.
"""
from dataclasses import replace
import numpy as np
from .capital_ledger import facility_capital_ledger
from .supply_network import SiteSupply,delivery_balance


def existing_ncc_pair(conventional,electric,*,years,remaining_years,replacement_cost_scale,
                      retirement_cash_EUR,salvage_receipt_EUR,terminal_rule,ethylene_yield,numerical_KRW_per_EUR):
    years=tuple(years)
    if years!=tuple(range(2027,2051)):raise ValueError('Reference calendar2027to2050 required')
    if isinstance(remaining_years,bool) or not isinstance(remaining_years,int) or not 1<=remaining_years<=25:
        raise ValueError('Explicit common remaining life from1to25years required')
    for name,v in [('replacement cost',replacement_cost_scale),('retirement cash',retirement_cash_EUR),('salvage receipt',salvage_receipt_EUR),('unit mapping',numerical_KRW_per_EUR)]:
        if isinstance(v,bool) or not np.isfinite(v) or v<0 or (name=='unit mapping' and v==0):raise ValueError(name)
    if terminal_rule!='none':raise ValueError('This incumbent bridge currently requires terminal_rule=none')
    if isinstance(ethylene_yield,bool) or not np.isfinite(ethylene_yield) or not 0<ethylene_yield<=1:raise ValueError('Source yield required')
    scale=numerical_KRW_per_EUR/1000;T=len(years);op=np.array(years)>=2030
    if any(tuple(r['profile'].profile_years)!=years for r in [conventional,electric]):raise ValueError('Source years differ')
    q=np.asarray(conventional['output_t'],dtype=float)
    if not np.array_equal(q,electric['output_t']) or not np.all(q[:3]==0) or not np.all(q[3:]==q[3]):
        raise ValueError('Equal, constant post2030 source production required')
    required=np.full(T,q[3]);zero=np.zeros(T);
    profiles={};annual={}
    components=[('plant',conventional['initial_plant_EUR'],30),('boiler',conventional['initial_boiler_EUR'],25)]
    for scenario in ['continue_existing','replace_2030']:
        old_cash=np.zeros(T);old_terminal=np.zeros(T);writeoff=np.zeros(T)
        for name,cost,life in components:
            f=dict(capacity=1.,incumbent_capex_unit=cost*replacement_cost_scale,reinvest_cycle_yr=life,last_reline_year=2027+remaining_years-life)
            c=facility_capital_ledger(f,None,2030 if scenario=='replace_2030' else None,years,retire=scenario=='replace_2030',terminal_rule=terminal_rule)
            old_cash+=c.incumbent_renewal_k;old_terminal+=c.terminal_value_k;writeoff+=c.noncash_writeoff_k
        new=scenario=='replace_2030';r=electric if new else conventional;p=r['profile']
        def full_quantity(new_quantity,old_quantity):
            return np.where(op,np.asarray(new_quantity),np.asarray(old_quantity)[3])
        grid=full_quantity(p.grid_mwh,conventional['profile'].grid_mwh)
        flows=[]
        for f,old in zip(p.additional_commodity_flows,conventional['profile'].additional_commodity_flows):
            if f.flow_id!=old.flow_id:raise ValueError('Source commodity order differs')
            flows.append(replace(f,quantity=full_quantity(f.quantity,old.quantity)))
        maintenance=full_quantity(r['maintenance_EUR'],conventional['maintenance_EUR'])
        construction=electric['capital'].construction.sum(axis=0) if new else zero.copy()
        new_renewal=electric['capital'].renewal.sum(axis=0) if new else zero.copy()
        new_terminal=electric['capital'].terminal_receipt.sum(axis=0) if new else zero.copy()
        # Terminal conventions must match the supplied new-source profile.
        if new and terminal_rule=='none' and np.any(new_terminal):raise ValueError('New and incumbent terminal conventions differ')
        closure=np.where(np.array(years)==2030,retirement_cash_EUR-salvage_receipt_EUR,0.) if new else zero.copy()
        total_cash=construction+old_cash+new_renewal
        terminal=old_terminal+new_terminal
        cash_profile=replace(p,grid_mwh=grid,additional_commodity_flows=tuple(flows),other_cost_k=(maintenance+closure)*scale,
            capex_k=total_cash*scale,capex_by_tech={'replacement_construction':construction*scale},capex_unc={'replacement_construction':0.},
            maintenance_capex_k=(old_cash+new_renewal)*scale,terminal_value_k=terminal*scale)
        site=SiteSupply(required,zero,required,zero,0.,required,zero,zero)
        balance=delivery_balance({'reference_plant':site},[],years=years,product_specification='Same source ethylene; same grade assumed',required_delivery={'reference_plant':required},inventory_boundary={'reference_plant':[0.,0.]})
        if not np.allclose(flows[0].quantity*ethylene_yield,required,rtol=0,atol=1e-7):raise ValueError('Source ethylene yield/delivery mismatch')
        profiles[scenario]=cash_profile
        annual[scenario]=dict(output_t=required,construction_EUR=construction,incumbent_renewal_EUR=old_cash,new_renewal_EUR=new_renewal,
           maintenance_EUR=maintenance,closure_net_cash_EUR=closure,terminal_receipt_EUR=terminal,
           noncash_writeoff_proxy_EUR=writeoff,net_fixed_cash_EUR=total_cash+maintenance+closure-terminal)
    return dict(profiles=profiles,annual=annual,assumptions=dict(remaining_life=remaining_years,replacement_cost_scale=replacement_cost_scale,
        historical_capital_recharged=False,writeoff_is_replacement_cost_based_proxy=True,zero_replacement_downtime=True,
        retirement_cash_EUR=retirement_cash_EUR,salvage_receipt_EUR=salvage_receipt_EUR,terminal_rule=terminal_rule,
        incumbent_operating_specification='conventional new-plant source proxy, not company observed',
        incumbent_maintenance='same source annualized-capital proxy; constant while operating',
        old_plant_lifetime=30,old_boiler_lifetime=25),company_calibration=False,retrofit_quote=False,emissions_feasibility=False)
