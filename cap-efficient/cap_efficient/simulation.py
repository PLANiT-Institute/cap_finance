from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass

from .costing import base_market_states, evaluate_cost
from .math_utils import cholesky, matrix_vector_product
from .models import (
    DataBundle,
    MarketState,
    ScenarioPoint,
    Schedule,
)


@dataclass(frozen=True)
class SimulationResult:
    gross_costs_bn_krw: tuple[float, ...]
    net_costs_bn_krw: tuple[float, ...]
    cash_costs_before_support_bn_krw: tuple[float, ...]
    net_cash_costs_after_support_bn_krw: tuple[float, ...]
    avoided_carbon_cost_values_bn_krw: tuple[float, ...]
    policy_support_bn_krw: tuple[float, ...]
    avoided_emissions_mtco2: float
    capex_costs_bn_krw: tuple[float, ...]
    fixed_opex_costs_bn_krw: tuple[float, ...]
    electricity_costs_bn_krw: tuple[float, ...]
    hydrogen_costs_bn_krw: tuple[float, ...]
    contract_premiums_bn_krw: tuple[float, ...]
    carbon_values_bn_krw: tuple[float, ...]


def _market_path(
    rng: random.Random,
    scenario: Sequence[ScenarioPoint],
    config: Mapping[str, object],
    active_factors: Set[str] | None,
) -> dict[int, MarketState]:
    factors = [str(value) for value in config["factors"]]
    correlation = [[float(value) for value in row] for row in config["correlation"]]
    lower = cholesky(correlation)
    volatility_config = config["annual_volatility"]
    reversion_config = config["mean_reversion"]
    assert isinstance(volatility_config, dict)
    assert isinstance(reversion_config, dict)
    volatilities = [float(volatility_config[factor]) for factor in factors]
    persistence = [1.0 - float(reversion_config[factor]) for factor in factors]
    hydrogen = config["hydrogen"]
    assert isinstance(hydrogen, dict)
    state = [0.0] * len(factors)
    path: dict[int, MarketState] = {}

    for point in scenario:
        independent = [rng.gauss(0.0, 1.0) for _ in factors]
        correlated = matrix_vector_product(lower, independent)
        for index, factor in enumerate(factors):
            innovation = correlated[index] if active_factors is None or factor in active_factors else 0.0
            state[index] = persistence[index] * state[index] + volatilities[index] * innovation
        factor_state = dict(zip(factors, state, strict=True))
        electricity = point.electricity_price_krw_per_kwh * math.exp(
            factor_state["electricity"]
        )
        hydrogen_price = (
            float(hydrogen["non_electricity_krw_per_kg"])
            + float(hydrogen["electricity_kwh_per_kg"]) * electricity
            + float(hydrogen["electrolyzer_component_krw_per_kg"])
            * point.electrolyzer_capex_index
            * math.exp(factor_state["hydrogen_input"])
        )
        capex_multiplier = math.exp(factor_state["construction_capex"])
        path[point.year] = MarketState(
            electricity_price_krw_per_kwh=electricity,
            hydrogen_price_krw_per_kg=hydrogen_price,
            construction_capex_multiplier=capex_multiplier,
        )
    return path


def simulate_schedule(
    bundle: DataBundle,
    schedule: Schedule,
    path_count: int,
    seed: int,
    active_factors: Set[str] | None = None,
) -> SimulationResult:
    if path_count < 1:
        raise ValueError("path_count must be positive")
    scenario = bundle.scenarios[(schedule.company_id, schedule.scenario_id)]
    plan = bundle.plans[(schedule.company_id, schedule.plan_id)]
    company = bundle.companies[schedule.company_id]
    facilities = {
        facility_id: facility
        for facility_id, facility in bundle.facilities.items()
        if facility.company_id == schedule.company_id
    }
    discount_rate = float(bundle.price_process["discount_rate"])
    recognized_carbon_cost_share = float(
        bundle.price_process["recognized_carbon_cost_share"]
    )
    reference_markets = base_market_states(scenario, bundle.price_process)
    rng = random.Random(seed)
    gross_costs: list[float] = []
    net_costs: list[float] = []
    cash_costs_before_support: list[float] = []
    net_cash_costs_after_support: list[float] = []
    avoided_carbon_cost_values: list[float] = []
    supports: list[float] = []
    capex_costs: list[float] = []
    fixed_opex_costs: list[float] = []
    electricity_costs: list[float] = []
    hydrogen_costs: list[float] = []
    contract_premiums: list[float] = []
    carbon_values: list[float] = []
    avoided_emissions = schedule.cumulative_avoided_emissions_mtco2

    for _ in range(path_count):
        markets = _market_path(rng, scenario, bundle.price_process, active_factors)
        result = evaluate_cost(
            schedule,
            facilities,
            bundle.technologies,
            scenario,
            bundle.policies,
            plan,
            markets,
            reference_markets,
            discount_rate,
            recognized_carbon_cost_share,
            company.country_code,
            company.capex_cost_index,
        )
        gross_costs.append(result.gross_cost_bn_krw)
        net_costs.append(result.net_cost_bn_krw)
        cash_costs_before_support.append(result.cash_cost_before_support_bn_krw)
        net_cash_costs_after_support.append(result.net_cash_cost_after_support_bn_krw)
        avoided_carbon_cost_values.append(result.avoided_carbon_cost_value_bn_krw)
        supports.append(result.policy_support_bn_krw)
        capex_costs.append(result.capex_cost_bn_krw)
        fixed_opex_costs.append(result.fixed_opex_cost_bn_krw)
        electricity_costs.append(result.electricity_cost_bn_krw)
        hydrogen_costs.append(result.hydrogen_cost_bn_krw)
        contract_premiums.append(result.contract_premium_bn_krw)
        carbon_values.append(result.carbon_value_bn_krw)
        avoided_emissions = result.avoided_emissions_mtco2

    return SimulationResult(
        gross_costs_bn_krw=tuple(gross_costs),
        net_costs_bn_krw=tuple(net_costs),
        cash_costs_before_support_bn_krw=tuple(cash_costs_before_support),
        net_cash_costs_after_support_bn_krw=tuple(net_cash_costs_after_support),
        avoided_carbon_cost_values_bn_krw=tuple(avoided_carbon_cost_values),
        policy_support_bn_krw=tuple(supports),
        avoided_emissions_mtco2=avoided_emissions,
        capex_costs_bn_krw=tuple(capex_costs),
        fixed_opex_costs_bn_krw=tuple(fixed_opex_costs),
        electricity_costs_bn_krw=tuple(electricity_costs),
        hydrogen_costs_bn_krw=tuple(hydrogen_costs),
        contract_premiums_bn_krw=tuple(contract_premiums),
        carbon_values_bn_krw=tuple(carbon_values),
    )
