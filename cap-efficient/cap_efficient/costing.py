from __future__ import annotations

from collections.abc import Mapping, Sequence

from .models import (
    CostResult,
    Facility,
    MarketState,
    Plan,
    PolicySupport,
    ScenarioPoint,
    Schedule,
    Technology,
)


def base_hydrogen_price(
    point: ScenarioPoint,
    price_process: Mapping[str, object],
) -> float:
    hydrogen = price_process["hydrogen"]
    assert isinstance(hydrogen, dict)
    return (
        float(hydrogen["non_electricity_krw_per_kg"])
        + float(hydrogen["electricity_kwh_per_kg"])
        * point.electricity_price_krw_per_kwh
        + float(hydrogen["electrolyzer_component_krw_per_kg"])
        * point.electrolyzer_capex_index
    )


def base_market_states(
    scenario: Sequence[ScenarioPoint],
    price_process: Mapping[str, object],
) -> dict[int, MarketState]:
    return {
        point.year: MarketState(
            electricity_price_krw_per_kwh=point.electricity_price_krw_per_kwh,
            hydrogen_price_krw_per_kg=base_hydrogen_price(point, price_process),
            construction_capex_multiplier=1.0,
        )
        for point in scenario
    }


def evaluate_cost(
    schedule: Schedule | tuple[str, str, str, tuple],
    facilities: Mapping[str, Facility],
    technologies: Mapping[str, Technology],
    scenario: Sequence[ScenarioPoint],
    policies: Mapping[tuple[str, str], PolicySupport],
    plan: Plan,
    markets: Mapping[int, MarketState],
    reference_markets: Mapping[int, MarketState],
    discount_rate: float,
    recognized_carbon_cost_share: float,
    country_code: str,
    capex_cost_index: float,
) -> CostResult:
    if isinstance(schedule, Schedule):
        scenario_id = schedule.scenario_id
        actions = schedule.actions
    else:
        _, scenario_id, _, actions = schedule
    action_map = {action.facility_id: action for action in actions}
    base_year = scenario[0].year - 1
    gross_cost = 0.0
    policy_support = 0.0
    avoided_emissions = 0.0
    capex_cost = 0.0
    fixed_opex_cost = 0.0
    electricity_cost = 0.0
    hydrogen_cost = 0.0
    contract_premium = 0.0
    carbon_value = 0.0

    for point in scenario:
        market = markets[point.year]
        discount_factor = 1.0 / ((1.0 + discount_rate) ** (point.year - base_year))
        for facility in facilities.values():
            action = action_map[facility.facility_id]
            technology = technologies[action.technology_id]
            if point.year < action.transition_year:
                continue

            output = facility.output_mt
            effective_electricity = (
                (1.0 - plan.ppa_share) * market.electricity_price_krw_per_kwh
                + plan.ppa_share
                * point.electricity_price_krw_per_kwh
                * (1.0 + plan.contract_premium_pct)
            )
            base_electricity = (
                (1.0 - plan.ppa_share) * market.electricity_price_krw_per_kwh
                + plan.ppa_share * point.electricity_price_krw_per_kwh
            )
            effective_hydrogen = (
                (1.0 - plan.hydrogen_contract_share) * market.hydrogen_price_krw_per_kg
                + plan.hydrogen_contract_share
                * reference_markets[point.year].hydrogen_price_krw_per_kg
                * (1.0 + plan.contract_premium_pct)
            )
            base_hydrogen = (
                (1.0 - plan.hydrogen_contract_share) * market.hydrogen_price_krw_per_kg
                + plan.hydrogen_contract_share
                * reference_markets[point.year].hydrogen_price_krw_per_kg
            )
            incremental_fixed = (
                technology.fixed_opex_kkrw_per_t - facility.baseline_fixed_opex_kkrw_per_t
            ) * output
            incremental_electricity = (
                technology.electricity_mwh_per_t - facility.baseline_electricity_mwh_per_t
            ) * base_electricity * output
            incremental_hydrogen = (
                technology.hydrogen_t_per_t * base_hydrogen * output
            )
            energy_contract_premium = (
                (technology.electricity_mwh_per_t - facility.baseline_electricity_mwh_per_t)
                * (effective_electricity - base_electricity)
                * output
                + technology.hydrogen_t_per_t
                * (effective_hydrogen - base_hydrogen)
                * output
            )
            carbon_delta = (
                technology.emissions_tco2_per_t - facility.baseline_emissions_tco2_per_t
            ) * output * (point.carbon_price_krw_per_tco2 / 1_000.0) * recognized_carbon_cost_share
            annual_incremental = (
                incremental_fixed
                + incremental_electricity
                + incremental_hydrogen
                + energy_contract_premium
                + carbon_delta
            )
            gross_cost += annual_incremental * discount_factor
            fixed_opex_cost += incremental_fixed * discount_factor
            electricity_cost += incremental_electricity * discount_factor
            hydrogen_cost += incremental_hydrogen * discount_factor
            contract_premium += energy_contract_premium * discount_factor
            carbon_value += carbon_delta * discount_factor
            avoided_emissions += max(
                0.0,
                (facility.baseline_emissions_tco2_per_t - technology.emissions_tco2_per_t)
                * output,
            )

            policy = policies[(country_code, scenario_id, technology.technology_id)]
            ccfd_support = (
                max(0.0, annual_incremental)
                * policy.ccfd_opex_support_pct
                * plan.ccfd_share
            )
            policy_support += ccfd_support * discount_factor

            if point.year == action.transition_year:
                baseline_technology = technologies[facility.baseline_technology_id]
                eligible_incremental_capex = max(
                    0.0,
                    technology.capex_bn_krw_per_mtpa
                    - baseline_technology.capex_bn_krw_per_mtpa,
                ) * facility.capacity_mtpa * capex_cost_index
                effective_capex_multiplier = (
                    (1.0 - plan.fixed_epc_share) * market.construction_capex_multiplier
                    + plan.fixed_epc_share
                )
                incremental_capex = eligible_incremental_capex * effective_capex_multiplier
                capex_contract_premium = (
                    eligible_incremental_capex
                    * plan.fixed_epc_share
                    * plan.contract_premium_pct
                )
                gross_cost += (
                    incremental_capex + capex_contract_premium
                ) * discount_factor
                capex_cost += incremental_capex * discount_factor
                contract_premium += capex_contract_premium * discount_factor
                policy_support += (
                    (incremental_capex + capex_contract_premium)
                    * policy.capex_subsidy_pct
                    * discount_factor
                )

    cash_cost_before_support = (
        capex_cost
        + fixed_opex_cost
        + electricity_cost
        + hydrogen_cost
        + contract_premium
    )
    avoided_carbon_cost_value = -carbon_value
    return CostResult(
        gross_cost_bn_krw=gross_cost,
        net_cost_bn_krw=gross_cost - policy_support,
        cash_cost_before_support_bn_krw=cash_cost_before_support,
        net_cash_cost_after_support_bn_krw=(
            cash_cost_before_support - policy_support
        ),
        avoided_carbon_cost_value_bn_krw=avoided_carbon_cost_value,
        policy_support_bn_krw=policy_support,
        avoided_emissions_mtco2=avoided_emissions,
        capex_cost_bn_krw=capex_cost,
        fixed_opex_cost_bn_krw=fixed_opex_cost,
        electricity_cost_bn_krw=electricity_cost,
        hydrogen_cost_bn_krw=hydrogen_cost,
        contract_premium_bn_krw=contract_premium,
        carbon_value_bn_krw=carbon_value,
    )
