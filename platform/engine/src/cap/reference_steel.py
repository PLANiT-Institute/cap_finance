"""Vogl published cost components connected to the dated FIN cash ledger.

This is a source-native reference calculation, not a company-approved process.
The source's mixed price basis is preserved. Omitted carbon additions, oxygen
conditioning and incumbent costs are not silently supplied from another route.
"""
from dataclasses import dataclass

import numpy as np

from .component_capital import CapitalComponent, component_capital_cashflows
from .commodity_ledger import CommodityFlow
from .plancost import PlanProfile


@dataclass(frozen=True)
class SteelReferenceProfile:
    profile: PlanProfile
    output_t: np.ndarray
    operating_cost_components_k: dict
    metadata: dict


def build_vogl_reference_profile(package, years, *, capacity_t_per_year,
        annual_utilization, adopt_year, build_years, numerical_KRW_per_source_EUR,
        oxygen_sale_fraction, direct_emission_factor_tco2_per_t,
        terminal_rule='none'):
    """No default FX, emissions, utilization, saleability or project timing.

    FIN price keys for material purchases are the package flow_ids; the oxygen
    export key is oxygen_netback. The caller must provide all external prices
    and paired shocks to simulate_cost. Labour varies with output; the source
    3%-of-CAPEX maintenance charge is held fixed by installed capacity while
    operating. The latter extension away from full utilization is an assumption.
    """
    if package.get('package_id') != 'VOGL2018_MAIN_TEXT_ONSITE_COST':
        raise ValueError('This builder accepts the reviewed Vogl package only')
    if package.get('hydrogen_purchase_kg_t') != 0:
        raise ValueError('Onsite electrolyser power already includes hydrogen production')
    if not package.get('price_basis') or not package.get('source',{}).get('sha256'):
        raise ValueError('Source provenance and price basis are required')
    for value,name,lo,hi in [
            (capacity_t_per_year,'capacity',0,np.inf),
            (numerical_KRW_per_source_EUR,'unit mapping',0,np.inf),
            (oxygen_sale_fraction,'oxygen sale fraction',0,1),
            (direct_emission_factor_tco2_per_t,'direct emission factor',0,np.inf)]:
        if isinstance(value,(bool,np.bool_)) or not np.isscalar(value) or not np.isfinite(value) or value<lo or value>hi:
            raise ValueError(f'Invalid {name}')
    if numerical_KRW_per_source_EUR==0:raise ValueError('Unit mapping must be strictly positive')
    years=tuple(years)
    utilization=np.asarray(annual_utilization,dtype=float)
    if utilization.shape != (len(years),) or not np.isfinite(utilization).all() or (utilization<0).any() or (utilization>1).any():
        raise ValueError('Utilization must give one fraction in [0,1] for every year')
    components=tuple(CapitalComponent(c['component'],c['capex_EUR_per_t_annual_capacity'],c['lifetime_years'])
                     for c in package['capital_components'])
    cash=component_capital_cashflows(components,capacity_t_per_year,adopt_year,build_years,
                years,unit_of_account='EUR_source_composite',terminal_rule=terminal_rule)
    operating=np.array(years)>=adopt_year+build_years
    output=capacity_t_per_year*utilization*operating
    scale=numerical_KRW_per_source_EUR/1000
    zero=np.zeros(len(years))
    capital_unit=sum(c.cost_per_capacity for c in components)
    labour=output*package['labour_EUR_t']*scale
    maintenance=operating*capacity_t_per_year*capital_unit*package['OM_fraction_CAPEX']*scale
    flows=[]
    for row in package['purchases']:
        if row['role']!='purchased' or row['quantity_unit']!='t/tLS':
            raise ValueError('The reviewed material bill requires purchased tonnes per liquid-steel tonne')
        flows.append(CommodityFlow(row['flow_id'],row['flow_id'],output*row['quantity'],'t','purchased',
                    package['package_id']+':'+row['source_quantity']))
    flows.append(CommodityFlow('oxygen_export','oxygen_netback',
        -output*package['oxygen']['generated_t_t']*oxygen_sale_fraction,'t','export_netback',
        package['package_id']+':oxygen; sale fraction explicitly supplied'))
    p=PlanProfile(grid_mwh=output*package['electricity_MWh_t'],re_mwh=zero.copy(),h2_kg=zero.copy(),
        other_cost_k=labour+maintenance,capex_k=cash.cash_payments*scale,
        capex_by_tech={c:cash.construction[i]*scale for i,c in enumerate(cash.component_ids)},
        capex_unc={c:40. for c in cash.component_ids},
        emissions=output*direct_emission_factor_tco2_per_t,ppa=0.,epc=0,ccfd=0,
        maintenance_capex_k=cash.renewal.sum(axis=0)*scale,
        terminal_value_k=cash.terminal_receipt.sum(axis=0)*scale,
        additional_commodity_flows=tuple(flows),embedded_price_basis={},profile_years=cash.years)
    return SteelReferenceProfile(p,output,{'labour':labour,'fixed_maintenance':maintenance},dict(
        package_id=package['package_id'],source_sha256=package['source']['sha256'],
        source_price_basis=package['price_basis'],numerical_KRW_per_source_EUR=numerical_KRW_per_source_EUR,
        scope='published source components with dated capital; not complete company transition cost',
        annualized_capital_added=False,onsite_hydrogen_billed=False,incumbent_counterfactual_included=False,
        current_company_input_approved=False,uniform_real_price_year_verified=False,
        source_oxygen_price_is_gross_not_conditioning_netback=True,
        operating_assumptions=['Labour proportional to output','Maintenance fraction of initial capital at installed capacity while operating',
                               'Zero output does not retire an operating plant','Replacement costs constant in source unit; zero renewal downtime'],
        direct_emission_factor_status='explicit caller assumption; not validated by this cost package',
        limits=package['limits']))
