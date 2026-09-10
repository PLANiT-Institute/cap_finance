"""Conditional NCC cash reference with explicit engineering/accounting assumptions.

Steam grades are collapsed only under the caller's declared useful-recovery
factor. This bookkeeping abstraction is not an engineering validation of a site.
Both alternatives are new plants; the incumbent retrofit is not inferred.
"""
from dataclasses import dataclass
import math
import numpy as np
from .commodity_ledger import CommodityFlow
from .component_capital import CapitalComponent, component_capital_cashflows
from .plancost import PlanProfile


@dataclass(frozen=True)
class NCCConditions:
    useful_steam_recovery: float
    operating_hours: float
    plant_lifetime: int
    maintenance_fraction: float
    boiler_maintenance_fraction: float
    maintenance_annuity_rate: float
    methane_sale_fraction: float
    terminal_rule: str


def build_ncc_reference(observations, case, years, conditions, *, numerical_KRW_per_EUR):
    if case not in ('conventional','electric'):raise ValueError('Unknown source case')
    c=conditions
    for key in ('useful_steam_recovery','methane_sale_fraction'):
        v=getattr(c,key)
        if isinstance(v,bool) or not math.isfinite(v) or not 0<=v<=1:raise ValueError(key)
    for key in ('operating_hours','maintenance_fraction','boiler_maintenance_fraction','maintenance_annuity_rate'):
        v=getattr(c,key)
        if isinstance(v,bool) or not math.isfinite(v) or v<0:raise ValueError(key)
    if not 0<c.operating_hours<=8760:raise ValueError('Hours must be within one non-leap year')
    if not 0<=c.maintenance_fraction<=1 or not 0<=c.boiler_maintenance_fraction<=1:raise ValueError('Maintenance fraction outside0to1')
    if isinstance(c.plant_lifetime,bool) or not isinstance(c.plant_lifetime,int) or c.plant_lifetime<1:raise ValueError('Exact positive lifetime required')
    if isinstance(numerical_KRW_per_EUR,bool) or not math.isfinite(numerical_KRW_per_EUR) or numerical_KRW_per_EUR<=0:raise ValueError('Positive numerical conversion required')
    years=tuple(years)
    if years!=tuple(range(2027,2051)):raise ValueError('Reference construction2027to2029 and operation2030to2050 required')
    values={(x['case'],x['item']):float(x['value']) for x in observations}
    if len(values)!=len(observations):raise ValueError('Duplicate source key')
    units={(x['case'],x['item']):x['unit'] for x in observations}
    for key,unit in [((case,'ethylene_yield'),'kg_ethylene/kg_naphtha'),
                     ((case,'TOC_slope'),'EUR2019/(kg_ethylene/h)'),
                     (('both','reference_capacity'),'t_ethylene/h')]:
        if units.get(key)!=unit:raise ValueError('Source units changed: '+str(key))
    get=lambda k,which=case:values[which,k]
    y=get('ethylene_yield');capacity=get('reference_capacity','both')
    if not 0<y<=1 or capacity<=0:raise ValueError('Invalid source capacity or yield')
    # The subtractions below are a declared lumped service approximation.
    # No downstream compressor exhaust or pressure-level equivalence is inferred.
    if case=='conventional':
        recovered=max(0.,get('cracker_superheated_steam_production')-get('compression_superheated_steam_consumption'))*c.useful_steam_recovery
        cracker_fuel=get('cracker_methane_consumption')
        electricity=get('separation_electricity_consumption')
    else:
        recovered=get('cracker_saturated_steam_production')*c.useful_steam_recovery
        cracker_fuel=0.
        electricity=sum(get(k+'_electricity_consumption') for k in ('cracker','compression','separation'))
    steam_demand=get('separation_saturated_steam_consumption')
    boiler_heat=max(steam_demand-recovered,0.)
    unused_heat=max(recovered-steam_demand,0.)
    boiler_fuel=boiler_heat/(get('efficiency','gas_boiler')/100)
    generated=get('separation_methane_production')
    consumed=cracker_fuel+boiler_fuel
    purchased=max(consumed-generated,0.);surplus=max(generated-consumed,0.)
    # Unsold gas is transferred outside this boundary for no compensation.
    # It is not silently treated as zero-emission flaring.
    sold=surplus*c.methane_sale_fraction;transferred=surplus-sold
    assert math.isclose(generated+purchased,consumed+sold+transferred,abs_tol=1e-12)
    assert math.isclose(recovered+boiler_heat,steam_demand+unused_heat,abs_tol=1e-12)
    op=(np.array(years)>=2030).astype(float);output=op*capacity*c.operating_hours
    feedstock=output/y
    plant=get('TOC_slope')*capacity*1000+get('TOC_intercept')*1e6
    # Boiler production kW at nameplate feed rate, explicitly separate auxiliary.
    boiler=get('TOC_slope','gas_boiler')*boiler_heat*capacity/y*1000
    cash=component_capital_cashflows((CapitalComponent('plant',plant,c.plant_lifetime),
        CapitalComponent('auxiliary_boiler',boiler,int(get('lifetime','gas_boiler')))),
        1.,2027,3,years,unit_of_account='EUR2019_assumed_operating_price_basis',terminal_rule=c.terminal_rule)
    def annuity(rate,life):return 1/life if rate==0 else rate/(1-(1+rate)**-life)
    maintenance=op*(c.maintenance_fraction*plant*annuity(c.maintenance_annuity_rate,c.plant_lifetime)
        +c.boiler_maintenance_fraction*boiler*annuity(c.maintenance_annuity_rate,25))
    factor=numerical_KRW_per_EUR/1000;zero=np.zeros(len(years))
    flows=(CommodityFlow('naphtha','naphtha',feedstock,'t_naphtha','purchased','Table1 yield; fixed production'),
           CommodityFlow('methane_purchase','methane',feedstock*purchased,'MWh_source_methane','purchased','Conditional steam/gas closure'),
           CommodityFlow('methane_sale','methane',-feedstock*sold,'MWh_source_methane','export_netback','Explicit sales fraction and assumed net price'))
    p=PlanProfile(grid_mwh=feedstock*electricity,re_mwh=zero.copy(),h2_kg=zero.copy(),
        other_cost_k=maintenance*factor,capex_k=cash.cash_payments*factor,
        capex_by_tech={k:cash.construction[i]*factor for i,k in enumerate(cash.component_ids)},
        capex_unc={k:0. for k in cash.component_ids},emissions=zero.copy(),ppa=0.,epc=0,ccfd=0,
        maintenance_capex_k=cash.renewal.sum(axis=0)*factor,
        terminal_value_k=cash.terminal_receipt.sum(axis=0)*factor,
        additional_commodity_flows=flows,embedded_price_basis={},profile_years=years)
    return dict(profile=p,capital=cash,maintenance_EUR=maintenance,output_t=output,
        quantities_per_t_naphtha=dict(electricity_MWh=electricity,methane_generated_MWh=generated,
            cracker_methane_MWh=cracker_fuel,boiler_methane_MWh=boiler_fuel,
            methane_purchased_MWh=purchased,methane_sold_MWh=sold,methane_transferred_MWh=transferred,
            useful_steam_MWh=recovered,boiler_heat_MWh=boiler_heat,steam_demand_MWh=steam_demand,unused_heat_MWh=unused_heat),
        initial_plant_EUR=plant,initial_boiler_EUR=boiler,
        carbon_cost_included=False,corporate_full_cost=False,incumbent_retrofit=False)
