"""Bind the conditional NCC FIN ledger to an explicit shared delivery contract."""
import numpy as np
from .supply_network import SiteSupply,delivery_balance


def validate_ncc_delivery_pair(cases, *, years, required_output_t, capacity_t, ethylene_yields):
    """Validate before price sampling or FIN evaluation, with no corrective scaling.

    Both source cases deliver the same ethylene service, with zero external
    ethylene purchases and initial/terminal stocks. This gate does not validate
    coproduct substitution, emissions, downtime or a company's actual demand.
    Required output/capacity come from the explicit comparison contract, not
    whichever candidate happens to have been generated first.
    """
    if set(cases)!={'conventional','electric'} or set(ethylene_yields)!=set(cases):
        raise ValueError('Exactly both NCC reference cases and their source yields required')
    shape=(len(years),);zero=np.zeros(shape);reports={}
    for name,r in cases.items():
        p=r['profile']
        if tuple(p.profile_years)!=tuple(years):raise ValueError('FIN and delivery periods differ')
        q=np.asarray(r['output_t'],dtype=float)
        site=SiteSupply(q,zero,q,zero,0.,capacity_t,zero,zero)
        balance=delivery_balance({'plant':site},[],years=years,product_specification='Source reference ethylene; common grade assumed',
          required_delivery={'plant':required_output_t},inventory_boundary={'plant':[0.,0.]})
        yield_=ethylene_yields[name]
        if isinstance(yield_,bool) or not np.isfinite(yield_) or not 0<yield_<=1:raise ValueError('Explicit physical ethylene yield required')
        flows={f.flow_id:f for f in p.additional_commodity_flows}
        expected={'naphtha':('naphtha','t_naphtha','purchased'),
                  'methane_purchase':('methane','MWh_source_methane','purchased'),
                  'methane_sale':('methane','MWh_source_methane','export_netback')}
        if len(flows)!=len(p.additional_commodity_flows) or set(flows)!=set(expected):raise ValueError('NCC external commodity menu differs')
        for key,meta in expected.items():
            f=flows[key]
            if (f.price_key,f.quantity_unit,f.role)!=meta:raise ValueError('NCC commodity unit or cash role differs')
        feed=np.asarray(flows['naphtha'].quantity,dtype=float)
        quantities=r['quantities_per_t_naphtha']
        pairs=[('ethylene material yield',q,feed*yield_),
               ('electricity',p.grid_mwh,feed*quantities['electricity_MWh']),
               ('methane purchase',flows['methane_purchase'].quantity,feed*quantities['methane_purchased_MWh']),
               ('methane sale',flows['methane_sale'].quantity,-feed*quantities['methane_sold_MWh'])]
        errors={}
        for label,actual,expected_quantity in pairs:
            a=np.asarray(actual,dtype=float);b=np.asarray(expected_quantity,dtype=float)
            if a.shape!=shape or b.shape!=shape or not np.isfinite(a).all() or not np.isfinite(b).all():
                raise ValueError('Aligned finite physical/FIN quantities required: '+label)
            # Absolute physical-unit tolerance, never a percentage of output.
            error=float(np.max(np.abs(a-b)))
            if error>1e-7:raise ValueError('FIN quantity is inconsistent with delivery: '+label)
            errors[label]=error
        reports[name]=dict(delivery_total_t=float(balance['delivery'].sum()),
            maximum_local_balance_error_t=float(np.abs(balance['local_residuals']['plant']).max()),
            quantity_link_errors=errors)
    return dict(years=list(years),required_output_t=np.asarray(required_output_t).tolist(),
                capacity_t=np.asarray(capacity_t).tolist(),cases=reports,external_ethylene_purchase=False,
                initial_terminal_inventory_t=0.,corporate_calibration=False,abatement_feasibility_verified=False)
