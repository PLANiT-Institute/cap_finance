from __future__ import annotations

import hashlib
import itertools
from collections.abc import Mapping, Sequence

from .costing import base_market_states, evaluate_cost
from .models import (
    DataBundle,
    Facility,
    Plan,
    ScenarioPoint,
    Schedule,
    Technology,
    TransitionAction,
)


TRANSITION_TECHNOLOGIES = {
    "BF_BOF": ("BF_RELINE", "SCRAP_EAF", "H2_DRI_EAF"),
    "EAF_BASELINE": ("EAF_RENEWABLE",),
}


def _action_for(
    facility: Facility,
    technology: Technology,
    plan: Plan,
    first_year: int,
    last_year: int,
) -> TransitionAction:
    preferred_year = facility.reinvestment_year + plan.schedule_shift_years
    transition_year = min(last_year, max(first_year, technology.available_year, preferred_year))
    return TransitionAction(
        facility_id=facility.facility_id,
        technology_id=technology.technology_id,
        transition_year=transition_year,
    )


def _meets_carbon_budget(
    actions: Sequence[TransitionAction],
    facilities: Mapping[str, Facility],
    technologies: Mapping[str, Technology],
    scenario: Sequence[ScenarioPoint],
) -> bool:
    action_map = {action.facility_id: action for action in actions}
    for point in scenario:
        emissions = 0.0
        for facility in facilities.values():
            action = action_map[facility.facility_id]
            intensity = facility.baseline_emissions_tco2_per_t
            if point.year >= action.transition_year:
                intensity = technologies[action.technology_id].emissions_tco2_per_t
            emissions += intensity * facility.output_mt
        if emissions > point.company_carbon_budget_mtco2 + 1e-9:
            return False
    return True


def optimize_schedule(
    bundle: DataBundle,
    company_id: str,
    scenario_id: str,
    plan_id: str,
) -> Schedule:
    scenario = bundle.scenarios[(company_id, scenario_id)]
    plan = bundle.plans[(company_id, plan_id)]
    facilities = {
        facility_id: facility
        for facility_id, facility in bundle.facilities.items()
        if facility.company_id == company_id
    }
    technologies = bundle.technologies
    company = bundle.companies[company_id]
    first_year, last_year = scenario[0].year, scenario[-1].year
    candidates_by_facility: list[list[TransitionAction]] = []
    for facility in facilities.values():
        technology_ids = TRANSITION_TECHNOLOGIES.get(facility.baseline_technology_id)
        if technology_ids is None:
            raise ValueError(f"No transition set for {facility.baseline_technology_id}")
        candidates_by_facility.append([
            _action_for(facility, technologies[technology_id], plan, first_year, last_year)
            for technology_id in technology_ids
        ])

    bf_capacity = sum(
        facility.capacity_mtpa
        for facility in facilities.values()
        if facility.baseline_technology_id == "BF_BOF"
    )
    base_markets = base_market_states(scenario, bundle.price_process)
    discount_rate = float(bundle.price_process["discount_rate"])
    recognized_carbon_cost_share = float(
        bundle.price_process["recognized_carbon_cost_share"]
    )
    best: Schedule | None = None
    evaluated = 0
    for actions in itertools.product(*candidates_by_facility):
        h2_capacity = sum(
            facilities[action.facility_id].capacity_mtpa
            for action in actions
            if action.technology_id == "H2_DRI_EAF"
        )
        if h2_capacity / bf_capacity + 1e-9 < plan.min_h2_capacity_share:
            continue
        if not _meets_carbon_budget(actions, facilities, technologies, scenario):
            continue
        provisional = (company_id, scenario_id, plan_id, tuple(actions))
        cost = evaluate_cost(
            provisional,
            facilities,
            technologies,
            scenario,
            bundle.policies,
            plan,
            base_markets,
            base_markets,
            discount_rate,
            recognized_carbon_cost_share,
            company.country_code,
            company.capex_cost_index,
        )
        evaluated += 1
        candidate = Schedule(
            company_id=company_id,
            scenario_id=scenario_id,
            plan_id=plan_id,
            actions=tuple(actions),
            deterministic_net_cost_bn_krw=cost.net_cost_bn_krw,
            cumulative_avoided_emissions_mtco2=cost.avoided_emissions_mtco2,
        )
        if best is None or candidate.deterministic_net_cost_bn_krw < best.deterministic_net_cost_bn_krw:
            best = candidate

    if best is None:
        raise ValueError(
            f"No feasible schedule for company={company_id}, scenario={scenario_id}, plan={plan_id}; "
            "review carbon budgets, availability years, and H2 share constraints"
        )
    if evaluated == 0:
        raise RuntimeError("Optimizer did not evaluate any feasible candidate")
    return best


def portfolio_signature(schedule: Schedule) -> str:
    return "|".join(
        f"{action.facility_id}:{action.technology_id}:{action.transition_year}"
        for action in sorted(schedule.actions, key=lambda item: item.facility_id)
    )


def portfolio_id(schedule: Schedule) -> str:
    digest = hashlib.sha256(portfolio_signature(schedule).encode("utf-8")).hexdigest()
    return f"PORT-{digest[:12].upper()}"


def rebase_fixed_schedule(
    bundle: DataBundle,
    source_schedule: Schedule,
    target_scenario_id: str,
) -> Schedule:
    """Price and test the same physical actions under another scenario."""
    company_id = source_schedule.company_id
    plan_id = source_schedule.plan_id
    scenario = bundle.scenarios[(company_id, target_scenario_id)]
    company = bundle.companies[company_id]
    facilities = {
        facility_id: facility
        for facility_id, facility in bundle.facilities.items()
        if facility.company_id == company_id
    }
    plan = bundle.plans[(company_id, plan_id)]
    base_markets = base_market_states(scenario, bundle.price_process)
    provisional = Schedule(
        company_id=company_id,
        scenario_id=target_scenario_id,
        plan_id=plan_id,
        actions=source_schedule.actions,
        deterministic_net_cost_bn_krw=0.0,
        cumulative_avoided_emissions_mtco2=0.0,
    )
    cost = evaluate_cost(
        provisional,
        facilities,
        bundle.technologies,
        scenario,
        bundle.policies,
        plan,
        base_markets,
        base_markets,
        float(bundle.price_process["discount_rate"]),
        float(bundle.price_process["recognized_carbon_cost_share"]),
        company.country_code,
        company.capex_cost_index,
    )
    return Schedule(
        company_id=company_id,
        scenario_id=target_scenario_id,
        plan_id=plan_id,
        actions=source_schedule.actions,
        deterministic_net_cost_bn_krw=cost.net_cost_bn_krw,
        cumulative_avoided_emissions_mtco2=cost.avoided_emissions_mtco2,
    )


def schedule_budget_diagnostics(
    bundle: DataBundle,
    schedule: Schedule,
) -> dict[str, float | int | bool | None]:
    scenario = bundle.scenarios[(schedule.company_id, schedule.scenario_id)]
    facilities = {
        facility_id: facility
        for facility_id, facility in bundle.facilities.items()
        if facility.company_id == schedule.company_id
    }
    action_map = {action.facility_id: action for action in schedule.actions}
    breaches: list[tuple[int, float]] = []
    maximum_excess = 0.0
    minimum_margin = float("inf")
    for point in scenario:
        emissions = 0.0
        for facility in facilities.values():
            action = action_map[facility.facility_id]
            intensity = facility.baseline_emissions_tco2_per_t
            if point.year >= action.transition_year:
                intensity = bundle.technologies[action.technology_id].emissions_tco2_per_t
            emissions += intensity * facility.output_mt
        excess = emissions - point.company_carbon_budget_mtco2
        maximum_excess = max(maximum_excess, excess)
        minimum_margin = min(minimum_margin, -excess)
        if excess > 1e-9:
            breaches.append((point.year, excess))
    return {
        "carbon_budget_feasible": not breaches,
        "scenario_feasible": not breaches,
        "first_budget_breach_year": breaches[0][0] if breaches else None,
        "max_annual_budget_excess_mtco2": maximum_excess,
        "minimum_annual_budget_margin_mtco2": minimum_margin,
    }


def physical_constraint_diagnostics(
    bundle: DataBundle,
    schedule: Schedule,
) -> dict[str, float | int | bool | None]:
    facilities = {
        facility_id: facility
        for facility_id, facility in bundle.facilities.items()
        if facility.company_id == schedule.company_id
    }
    limits = bundle.resource_constraints[(schedule.company_id, schedule.scenario_id)]
    company_limit = bundle.company_constraints[schedule.company_id]
    action_map = {action.facility_id: action for action in schedule.actions}
    first_resource_breach_year: int | None = None
    max_scrap_excess = 0.0
    max_hydrogen_excess = 0.0
    max_grid_excess = 0.0
    for limit in limits:
        scrap = 0.0
        hydrogen = 0.0
        incremental_grid = 0.0
        for facility in facilities.values():
            action = action_map[facility.facility_id]
            if limit.year < action.transition_year:
                continue
            technology = bundle.technologies[action.technology_id]
            tech_constraint = bundle.technology_constraints[action.technology_id]
            scrap += tech_constraint.scrap_input_t_per_t * facility.output_mt
            hydrogen += technology.hydrogen_t_per_t * facility.output_mt
            incremental_grid += max(
                0.0,
                technology.electricity_mwh_per_t
                - facility.baseline_electricity_mwh_per_t,
            ) * facility.output_mt
        scrap_excess = scrap - limit.max_scrap_supply_mt
        hydrogen_excess = hydrogen - limit.max_hydrogen_supply_mt
        grid_excess = incremental_grid - limit.max_incremental_grid_twh
        max_scrap_excess = max(max_scrap_excess, scrap_excess)
        max_hydrogen_excess = max(max_hydrogen_excess, hydrogen_excess)
        max_grid_excess = max(max_grid_excess, grid_excess)
        if (
            first_resource_breach_year is None
            and max(scrap_excess, hydrogen_excess, grid_excess) > 1e-9
        ):
            first_resource_breach_year = limit.year

    scenario_years = range(limits[0].year, limits[-1].year + 1)
    max_concurrent = 0
    for year in scenario_years:
        active_projects = sum(
            action.transition_year
            - bundle.technologies[action.technology_id].construction_years
            <= year
            < action.transition_year
            for action in schedule.actions
        )
        max_concurrent = max(max_concurrent, active_projects)

    survival_probability = 1.0
    expected_failure_delay = 0.0
    for action in schedule.actions:
        constraint = bundle.technology_constraints[action.technology_id]
        survival_probability *= 1.0 - constraint.failure_probability
        expected_failure_delay += (
            constraint.failure_probability * constraint.max_failure_delay_years
        )
    portfolio_failure_probability = 1.0 - survival_probability
    resource_feasible = first_resource_breach_year is None
    concurrency_feasible = (
        max_concurrent <= company_limit.max_concurrent_construction_projects
    )
    failure_feasible = (
        portfolio_failure_probability
        <= company_limit.max_portfolio_failure_probability + 1e-9
    )
    return {
        "physical_constraints_feasible": (
            resource_feasible and concurrency_feasible and failure_feasible
        ),
        "resource_constraints_feasible": resource_feasible,
        "construction_concurrency_feasible": concurrency_feasible,
        "failure_risk_constraint_feasible": failure_feasible,
        "first_resource_breach_year": first_resource_breach_year,
        "max_scrap_supply_excess_mt": max_scrap_excess,
        "max_hydrogen_supply_excess_mt": max_hydrogen_excess,
        "max_incremental_grid_excess_twh": max_grid_excess,
        "max_concurrent_construction_projects": max_concurrent,
        "concurrent_construction_limit": company_limit.max_concurrent_construction_projects,
        "portfolio_failure_probability": portfolio_failure_probability,
        "portfolio_failure_probability_limit": company_limit.max_portfolio_failure_probability,
        "expected_failure_delay_years": expected_failure_delay,
    }


def resource_profile_rows(
    bundle: DataBundle,
    schedule: Schedule,
) -> list[dict[str, object]]:
    """Return annual demand, supply and headroom for auditable resource checks."""
    facilities = {
        facility_id: facility
        for facility_id, facility in bundle.facilities.items()
        if facility.company_id == schedule.company_id
    }
    action_map = {action.facility_id: action for action in schedule.actions}
    rows: list[dict[str, object]] = []
    for limit in bundle.resource_constraints[
        (schedule.company_id, schedule.scenario_id)
    ]:
        scrap = 0.0
        hydrogen = 0.0
        incremental_grid = 0.0
        active_actions = 0
        for facility in facilities.values():
            action = action_map[facility.facility_id]
            if limit.year < action.transition_year:
                continue
            active_actions += 1
            technology = bundle.technologies[action.technology_id]
            constraint = bundle.technology_constraints[action.technology_id]
            scrap += constraint.scrap_input_t_per_t * facility.output_mt
            hydrogen += technology.hydrogen_t_per_t * facility.output_mt
            incremental_grid += max(
                0.0,
                technology.electricity_mwh_per_t
                - facility.baseline_electricity_mwh_per_t,
            ) * facility.output_mt
        rows.append({
            "company_id": schedule.company_id,
            "company_name": bundle.companies[schedule.company_id].company_name,
            "scenario_id": schedule.scenario_id,
            "plan_id": schedule.plan_id,
            "year": limit.year,
            "active_transitioned_facilities": active_actions,
            "scrap_demand_mt": round(scrap, 6),
            "scrap_supply_mt": limit.max_scrap_supply_mt,
            "scrap_headroom_mt": round(limit.max_scrap_supply_mt - scrap, 6),
            "scrap_utilization_pct": round(
                100.0 * scrap / limit.max_scrap_supply_mt
                if limit.max_scrap_supply_mt > 0 else 0.0,
                3,
            ),
            "hydrogen_demand_mt": round(hydrogen, 6),
            "hydrogen_supply_mt": limit.max_hydrogen_supply_mt,
            "hydrogen_headroom_mt": round(limit.max_hydrogen_supply_mt - hydrogen, 6),
            "hydrogen_utilization_pct": round(
                100.0 * hydrogen / limit.max_hydrogen_supply_mt
                if limit.max_hydrogen_supply_mt > 0 else 0.0,
                3,
            ),
            "incremental_grid_demand_twh": round(incremental_grid, 6),
            "incremental_grid_supply_twh": limit.max_incremental_grid_twh,
            "incremental_grid_headroom_twh": round(
                limit.max_incremental_grid_twh - incremental_grid, 6
            ),
            "incremental_grid_utilization_pct": round(
                100.0 * incremental_grid / limit.max_incremental_grid_twh
                if limit.max_incremental_grid_twh > 0 else 0.0,
                3,
            ),
            "resource_feasible": (
                scrap <= limit.max_scrap_supply_mt + 1e-9
                and hydrogen <= limit.max_hydrogen_supply_mt + 1e-9
                and incremental_grid <= limit.max_incremental_grid_twh + 1e-9
            ),
            "data_status": limit.data_status,
            "source_note": limit.source_note,
        })
    return rows


def capex_schedule_rows(bundle: DataBundle, schedule: Schedule) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    scenario = bundle.scenarios[(schedule.company_id, schedule.scenario_id)]
    plan = bundle.plans[(schedule.company_id, schedule.plan_id)]
    company = bundle.companies[schedule.company_id]
    base_markets = base_market_states(scenario, bundle.price_process)
    discount_rate = float(bundle.price_process["discount_rate"])
    recognized_carbon_cost_share = float(
        bundle.price_process["recognized_carbon_cost_share"]
    )
    last_year = scenario[-1].year
    for action in schedule.actions:
        facility = bundle.facilities[action.facility_id]
        technology = bundle.technologies[action.technology_id]
        baseline_technology = bundle.technologies[facility.baseline_technology_id]
        facility_cost = evaluate_cost(
            (
                schedule.company_id,
                schedule.scenario_id,
                schedule.plan_id,
                (action,),
            ),
            {facility.facility_id: facility},
            bundle.technologies,
            scenario,
            bundle.policies,
            plan,
            base_markets,
            base_markets,
            discount_rate,
            recognized_carbon_cost_share,
            company.country_code,
            company.capex_cost_index,
        )
        output_mt = facility.output_mt
        baseline_emissions = facility.baseline_emissions_tco2_per_t * output_mt
        residual_emissions = technology.emissions_tco2_per_t * output_mt
        annual_avoided = max(0.0, baseline_emissions - residual_emissions)
        incremental_capex = max(
            0.0,
            technology.capex_bn_krw_per_mtpa
            - baseline_technology.capex_bn_krw_per_mtpa,
        ) * facility.capacity_mtpa * company.capex_cost_index

        def emissions_in(year: int) -> float:
            return residual_emissions if year >= action.transition_year else baseline_emissions

        rows.append({
            "company_id": schedule.company_id,
            "company_name": company.company_name,
            "scenario_id": schedule.scenario_id,
            "plan_id": schedule.plan_id,
            "facility_id": facility.facility_id,
            "facility_name": facility.facility_name,
            "region": facility.region,
            "transition_year": action.transition_year,
            "baseline_technology_id": facility.baseline_technology_id,
            "baseline_technology_name": baseline_technology.technology_name,
            "technology_id": technology.technology_id,
            "technology_name": technology.technology_name,
            "aligned_capex_bn_krw": round(
                technology.capex_bn_krw_per_mtpa
                * facility.capacity_mtpa
                * company.capex_cost_index,
                3,
            ),
            "incremental_capex_bn_krw": round(incremental_capex, 3),
            "capacity_mtpa": facility.capacity_mtpa,
            "output_mt": round(output_mt, 6),
            "baseline_emissions_mtco2": round(baseline_emissions, 6),
            "emissions_2030_mtco2": round(emissions_in(2030), 6),
            "emissions_2040_mtco2": round(emissions_in(2040), 6),
            "residual_emissions_mtco2": round(residual_emissions, 6),
            "annual_avoided_emissions_mtco2": round(annual_avoided, 6),
            "cumulative_avoided_emissions_mtco2": round(
                annual_avoided * max(0, last_year - action.transition_year + 1),
                6,
            ),
            "base_case_gross_cost_bn_krw": round(facility_cost.gross_cost_bn_krw, 3),
            "base_case_policy_support_bn_krw": round(
                facility_cost.policy_support_bn_krw, 3
            ),
            "base_case_cash_cost_before_support_bn_krw": round(
                facility_cost.cash_cost_before_support_bn_krw, 3
            ),
            "base_case_net_cash_cost_after_support_bn_krw": round(
                facility_cost.net_cash_cost_after_support_bn_krw, 3
            ),
            "base_case_avoided_carbon_cost_value_bn_krw": round(
                facility_cost.avoided_carbon_cost_value_bn_krw, 3
            ),
            "base_case_net_cost_bn_krw": round(facility_cost.net_cost_bn_krw, 3),
            "base_case_capex_cost_bn_krw": round(facility_cost.capex_cost_bn_krw, 3),
            "base_case_fixed_opex_cost_bn_krw": round(
                facility_cost.fixed_opex_cost_bn_krw, 3
            ),
            "base_case_electricity_cost_bn_krw": round(
                facility_cost.electricity_cost_bn_krw, 3
            ),
            "base_case_hydrogen_cost_bn_krw": round(
                facility_cost.hydrogen_cost_bn_krw, 3
            ),
            "base_case_contract_premium_bn_krw": round(
                facility_cost.contract_premium_bn_krw, 3
            ),
            "base_case_carbon_value_bn_krw": round(
                facility_cost.carbon_value_bn_krw, 3
            ),
            "data_status": facility.data_status,
            "source_note": facility.source_note,
        })
    return rows
