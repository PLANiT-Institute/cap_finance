from __future__ import annotations

from dataclasses import asdict
from itertools import combinations
from math import factorial
from pathlib import Path
from typing import Any

from .candidates import (
    active_scenario_ids,
    build_candidate_scenario_comparisons,
    build_robust_summary,
    candidate_catalog_row,
    enumerate_candidate_portfolios,
    screen_candidate,
    select_refinement_candidates,
    select_stochastic_candidates,
)
from .loader import load_data
from .gcam_manifest import validate_gcam_manifests
from .math_utils import pareto_frontier, quantile, sample_variance
from .report import write_csv, write_frontier_svg, write_json, write_markdown_report
from .schedule import (
    capex_schedule_rows,
    optimize_schedule,
    portfolio_id,
    physical_constraint_diagnostics,
    rebase_fixed_schedule,
    resource_profile_rows,
    schedule_budget_diagnostics,
)
from .simulation import simulate_schedule


FACTOR_LABELS = {
    "electricity": "electricity_variance_share",
    "hydrogen_input": "hydrogen_variance_share",
    "construction_capex": "capex_variance_share",
}

SHAPLEY_LABELS = {
    "electricity": "electricity_shapley_variance_share",
    "hydrogen_input": "hydrogen_shapley_variance_share",
    "construction_capex": "capex_shapley_variance_share",
}


def _shapley_variance_allocation(
    subset_variances: dict[frozenset[str], float],
) -> tuple[dict[str, float], dict[str, float], float]:
    """Allocate full-model variance across factors using the exact Shapley game.

    The caller supplies every subset of the three uncertainty factors.  Negative
    contributions are retained because correlation and non-linear cost mechanics
    can make a factor reduce incremental variance in a coalition.
    """
    factors = tuple(FACTOR_LABELS)
    expected = {
        frozenset(subset)
        for size in range(len(factors) + 1)
        for subset in combinations(factors, size)
    }
    if set(subset_variances) != expected:
        missing = sorted(expected - set(subset_variances), key=lambda item: (len(item), sorted(item)))
        raise ValueError(f"Shapley variance game is incomplete: missing={missing}")
    denominator = factorial(len(factors))
    contributions: dict[str, float] = {}
    for factor in factors:
        contribution = 0.0
        others = tuple(item for item in factors if item != factor)
        for size in range(len(others) + 1):
            weight = factorial(size) * factorial(len(factors) - size - 1) / denominator
            for subset in combinations(others, size):
                coalition = frozenset(subset)
                contribution += weight * (
                    subset_variances[coalition | {factor}]
                    - subset_variances[coalition]
                )
        contributions[factor] = contribution
    full_variance = subset_variances[frozenset(factors)]
    shares = {
        factor: (value / full_variance if full_variance > 0.0 else 0.0)
        for factor, value in contributions.items()
    }
    reconciliation_delta = sum(contributions.values()) - full_variance
    return contributions, shares, reconciliation_delta


def _scenario_ids(bundle, company_id: str) -> list[str]:
    return [
        scenario_id
        for scenario_id, definition in bundle.scenario_definitions.items()
        if definition.is_active and (company_id, scenario_id) in bundle.scenarios
    ]


def _plan_ids(bundle, company_id: str) -> list[str]:
    return [
        plan_id
        for candidate_company_id, plan_id in bundle.plans
        if candidate_company_id == company_id
    ]


def _metric_row(
    bundle,
    schedule,
    simulation,
    factor_variances,
    *,
    origin_scenario_id,
    fixed_portfolio_id,
    common_avoided_emissions_mtco2,
    budget_diagnostics,
):
    plan = bundle.plans[(schedule.company_id, schedule.plan_id)]
    company = bundle.companies[schedule.company_id]
    financials = bundle.financials[schedule.company_id]
    avoided = simulation.avoided_emissions_mtco2
    if avoided <= 0.0:
        raise ValueError(f"Schedule {schedule.company_id}/{schedule.plan_id} has no avoided emissions")
    if common_avoided_emissions_mtco2 <= 0.0:
        raise ValueError(
            f"Fixed portfolio {fixed_portfolio_id} has no common avoided-emissions denominator"
        )
    gross_intensity = [value / avoided for value in simulation.gross_costs_bn_krw]
    net_intensity = [value / avoided for value in simulation.net_costs_bn_krw]
    net_common_intensity = [
        value / common_avoided_emissions_mtco2
        for value in simulation.net_costs_bn_krw
    ]
    cash_common_intensity = [
        value / common_avoided_emissions_mtco2
        for value in simulation.net_cash_costs_after_support_bn_krw
    ]
    gross_p50 = quantile(gross_intensity, 0.5)
    net_p50 = quantile(net_intensity, 0.5)
    net_p90 = quantile(net_intensity, 0.9)
    net_p50_bn = quantile(simulation.net_costs_bn_krw, 0.5)
    p90_cost_bn = quantile(simulation.net_costs_bn_krw, 0.9)
    cash_before_support_p50_bn = quantile(
        simulation.cash_costs_before_support_bn_krw, 0.5
    )
    net_cash_p50_bn = quantile(
        simulation.net_cash_costs_after_support_bn_krw, 0.5
    )
    net_cash_p90_bn = quantile(
        simulation.net_cash_costs_after_support_bn_krw, 0.9
    )
    avoided_carbon_value_p50_bn = quantile(
        simulation.avoided_carbon_cost_values_bn_krw, 0.5
    )
    policy_support_value_p50_bn = quantile(
        simulation.policy_support_bn_krw, 0.5
    )
    cash_policy_p50_nonadditivity_bn = net_cash_p50_bn - (
        cash_before_support_p50_bn - policy_support_value_p50_bn
    )
    economic_cost_p50_identity_delta_bn = net_p50_bn - (
        net_cash_p50_bn - avoided_carbon_value_p50_bn
    )
    central_index = min(
        range(len(simulation.net_costs_bn_krw)),
        key=lambda index: abs(simulation.net_costs_bn_krw[index] - net_p50_bn),
    )
    central_components = {
        "capex_cost_p50_bn_krw": simulation.capex_costs_bn_krw[central_index],
        "fixed_opex_cost_p50_bn_krw": simulation.fixed_opex_costs_bn_krw[central_index],
        "electricity_cost_p50_bn_krw": simulation.electricity_costs_bn_krw[central_index],
        "hydrogen_cost_p50_bn_krw": simulation.hydrogen_costs_bn_krw[central_index],
        "contract_premium_p50_bn_krw": simulation.contract_premiums_bn_krw[central_index],
        "carbon_value_p50_bn_krw": simulation.carbon_values_bn_krw[central_index],
        "policy_support_p50_bn_krw": -simulation.policy_support_bn_krw[central_index],
    }
    component_total = sum(central_components.values())
    capex_rows = capex_schedule_rows(bundle, schedule)
    total_capex = sum(float(row["aligned_capex_bn_krw"]) for row in capex_rows)
    annual_capex: dict[int, float] = {}
    for row in capex_rows:
        year = int(row["transition_year"])
        annual_capex[year] = annual_capex.get(year, 0.0) + float(row["aligned_capex_bn_krw"])
    peak_year, peak_capex = max(annual_capex.items(), key=lambda item: item[1])
    variance_total = sum(factor_variances.values())
    shares = {
        FACTOR_LABELS[factor]: (variance / variance_total if variance_total > 0 else 0.0)
        for factor, variance in factor_variances.items()
    }
    return {
        "company_id": schedule.company_id,
        "company_name": company.company_name,
        "country_code": company.country_code,
        "reported_production_mt": company.production_mt,
        "reported_scope12_emissions_mtco2": company.scope12_emissions_mtco2,
        "scenario_id": schedule.scenario_id,
        "portfolio_origin_scenario_id": origin_scenario_id,
        "portfolio_id": fixed_portfolio_id,
        **budget_diagnostics,
        "plan_id": schedule.plan_id,
        "plan_name": plan.plan_name,
        "is_disclosed_plan": plan.is_disclosed_plan,
        "aligned_capex_bn_krw": round(total_capex, 3),
        "peak_capex_year": peak_year,
        "peak_capex_bn_krw": round(peak_capex, 3),
        "expected_cost_p50_kkrw_per_tco2": round(net_p50, 6),
        "expected_cost_p50_bn_krw": round(net_p50_bn, 3),
        "absolute_npv_p50_bn_krw": round(net_p50_bn, 3),
        "absolute_npv_p90_bn_krw": round(p90_cost_bn, 3),
        "scenario_avoided_emissions_mtco2": round(avoided, 6),
        "common_avoided_emissions_mtco2": round(
            common_avoided_emissions_mtco2, 6
        ),
        "net_economic_cost_p50_kkrw_per_tco2_common_denominator": round(
            quantile(net_common_intensity, 0.5), 6
        ),
        "net_cash_cost_after_support_p50_kkrw_per_tco2_common_denominator": round(
            quantile(cash_common_intensity, 0.5), 6
        ),
        "cash_cost_before_support_p50_bn_krw": round(
            cash_before_support_p50_bn, 3
        ),
        "net_cash_cost_after_support_p50_bn_krw": round(net_cash_p50_bn, 3),
        "net_cash_cost_after_support_p90_bn_krw": round(net_cash_p90_bn, 3),
        "avoided_carbon_cost_value_p50_bn_krw": round(
            avoided_carbon_value_p50_bn, 3
        ),
        "policy_support_value_p50_bn_krw": round(
            policy_support_value_p50_bn, 3
        ),
        "cash_policy_p50_nonadditivity_bn_krw": round(
            cash_policy_p50_nonadditivity_bn, 3
        ),
        "economic_cost_p50_identity_delta_bn_krw": round(
            economic_cost_p50_identity_delta_bn, 3
        ),
        "p90_cost_kkrw_per_tco2": round(net_p90, 6),
        "tcar_kkrw_per_tco2": round(net_p90 - net_p50, 6),
        "gross_cost_p50_kkrw_per_tco2": round(gross_p50, 6),
        "policy_support_dependence_kkrw_per_tco2": round(gross_p50 - net_p50, 6),
        "electricity_variance_share": round(shares["electricity_variance_share"], 6),
        "hydrogen_variance_share": round(shares["hydrogen_variance_share"], 6),
        "capex_variance_share": round(shares["capex_variance_share"], 6),
        "policy_uncertainty_exposure_kkrw_per_tco2": 0.0,
        "flexibility_value_kkrw_per_tco2": 0.0,
        "avoided_emissions_mtco2": round(avoided, 6),
        "p90_net_cost_bn_krw": round(p90_cost_bn, 3),
        "p90_cost_to_ebitda_x": round(p90_cost_bn / financials.ebitda_bn_krw, 6),
        "p90_cost_to_annual_capex_x": round(p90_cost_bn / financials.annual_capex_bn_krw, 6),
        **{key: round(value, 3) for key, value in central_components.items()},
        "component_reconciliation_p50_bn_krw": round(
            net_p50_bn - component_total, 3
        ),
    }, net_intensity


def _gap(current: dict[str, object], frontier: list[dict[str, float | str]]) -> dict[str, float]:
    current_cost = float(current["expected_cost_p50_kkrw_per_tco2"])
    current_risk = float(current["tcar_kkrw_per_tco2"])
    cost_comparables = [float(row["p50"]) for row in frontier if float(row["tcar"]) <= current_risk]
    risk_comparables = [float(row["tcar"]) for row in frontier if float(row["p50"]) <= current_cost]
    return {
        "cost_gap_same_or_lower_risk": max(0.0, current_cost - min(cost_comparables)) if cost_comparables else 0.0,
        "risk_gap_same_or_lower_cost": max(0.0, current_risk - min(risk_comparables)) if risk_comparables else 0.0,
    }


def _scenario_comparison_rows(bundle, by_key) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for company_id, company in bundle.companies.items():
        scenario_ids = _scenario_ids(bundle, company_id)
        for from_scenario_id, to_scenario_id in combinations(scenario_ids, 2):
            for plan_id in _plan_ids(bundle, company_id):
                origin = by_key[(company_id, from_scenario_id, plan_id)]
                target = by_key[(company_id, to_scenario_id, plan_id)]
                if origin["portfolio_id"] != target["portfolio_id"]:
                    raise ValueError(
                        f"Physical portfolio drift for {company_id}/{plan_id}: "
                        f"{origin['portfolio_id']} vs {target['portfolio_id']}"
                    )
                rows.append({
                    "company_id": company_id,
                    "company_name": company.company_name,
                    "plan_id": plan_id,
                    "plan_name": origin["plan_name"],
                    "portfolio_id": origin["portfolio_id"],
                    "portfolio_origin_scenario_id": origin[
                        "portfolio_origin_scenario_id"
                    ],
                    "from_scenario_id": from_scenario_id,
                    "to_scenario_id": to_scenario_id,
                    "from_scenario_feasible": origin["scenario_feasible"],
                    "to_scenario_feasible": target["scenario_feasible"],
                    "same_physical_portfolio": True,
                    "common_avoided_emissions_mtco2": origin[
                        "common_avoided_emissions_mtco2"
                    ],
                    "delta_p50_common_kkrw_per_tco2": round(
                        float(target[
                            "net_economic_cost_p50_kkrw_per_tco2_common_denominator"
                        ])
                        - float(origin[
                            "net_economic_cost_p50_kkrw_per_tco2_common_denominator"
                        ]),
                        6,
                    ),
                    "delta_tcar_kkrw_per_tco2": round(
                        float(target["tcar_kkrw_per_tco2"])
                        - float(origin["tcar_kkrw_per_tco2"]),
                        6,
                    ),
                    "delta_absolute_npv_p50_bn_krw": round(
                        float(target["absolute_npv_p50_bn_krw"])
                        - float(origin["absolute_npv_p50_bn_krw"]),
                        3,
                    ),
                    "delta_absolute_npv_p90_bn_krw": round(
                        float(target["absolute_npv_p90_bn_krw"])
                        - float(origin["absolute_npv_p90_bn_krw"]),
                        3,
                    ),
                    "delta_aligned_capex_bn_krw": round(
                        float(target["aligned_capex_bn_krw"])
                        - float(origin["aligned_capex_bn_krw"]),
                        3,
                    ),
                    "delta_net_cash_cost_p50_bn_krw": round(
                        float(target["net_cash_cost_after_support_p50_bn_krw"])
                        - float(origin["net_cash_cost_after_support_p50_bn_krw"]),
                        3,
                    ),
                    "delta_avoided_carbon_value_p50_bn_krw": round(
                        float(target["avoided_carbon_cost_value_p50_bn_krw"])
                        - float(origin["avoided_carbon_cost_value_p50_bn_krw"]),
                        3,
                    ),
                    "delta_policy_support_value_p50_bn_krw": round(
                        float(target["policy_support_value_p50_bn_krw"])
                        - float(origin["policy_support_value_p50_bn_krw"]),
                        3,
                    ),
                })
    return rows


def run_pipeline(
    data_dir: Path | str = Path("data"),
    output_dir: Path | str = Path("outputs"),
    path_count: int | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    bundle = load_data(data_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    paths = path_count or int(bundle.price_process["default_paths"])
    run_seed = seed if seed is not None else int(bundle.price_process["seed"])

    metrics: list[dict[str, object]] = []
    distributions: dict[tuple[str, str, str], list[float]] = {}
    facility_rows: list[dict[str, object]] = []
    origin_schedules = {}
    origin_scenario_by_company: dict[str, str] = {}

    for company_id in bundle.companies:
        scenario_ids = _scenario_ids(bundle, company_id)
        origin_scenario_id = (
            "DISCLOSED_PATH"
            if "DISCLOSED_PATH" in scenario_ids
            else scenario_ids[0]
        )
        origin_scenario_by_company[company_id] = origin_scenario_id
        for plan_id in _plan_ids(bundle, company_id):
            origin_schedules[(company_id, plan_id)] = optimize_schedule(
                bundle, company_id, origin_scenario_id, plan_id
            )

    for company_id in bundle.companies:
        for scenario_id in _scenario_ids(bundle, company_id):
            for plan_id in _plan_ids(bundle, company_id):
                origin_schedule = origin_schedules[(company_id, plan_id)]
                schedule = rebase_fixed_schedule(
                    bundle, origin_schedule, scenario_id
                )
                fixed_portfolio_id = portfolio_id(origin_schedule)
                diagnostics = schedule_budget_diagnostics(bundle, schedule)
                diagnostics.update(physical_constraint_diagnostics(bundle, schedule))
                diagnostics["scenario_feasible"] = bool(
                    diagnostics["carbon_budget_feasible"]
                    and diagnostics["physical_constraints_feasible"]
                )
                rows = capex_schedule_rows(bundle, schedule)
                for facility_row in rows:
                    facility_row.update({
                        "portfolio_origin_scenario_id": origin_scenario_by_company[
                            company_id
                        ],
                        "portfolio_id": fixed_portfolio_id,
                        **diagnostics,
                    })
                facility_rows.extend(rows)
                simulation = simulate_schedule(bundle, schedule, paths, run_seed)
                factor_variances: dict[str, float] = {}
                for factor in FACTOR_LABELS:
                    isolated = simulate_schedule(
                        bundle,
                        schedule,
                        paths,
                        run_seed,
                        active_factors={factor},
                    )
                    factor_intensity = [
                        value / origin_schedule.cumulative_avoided_emissions_mtco2
                        for value in isolated.net_costs_bn_krw
                    ]
                    factor_variances[factor] = sample_variance(factor_intensity)
                row, net_intensity = _metric_row(
                    bundle,
                    schedule,
                    simulation,
                    factor_variances,
                    origin_scenario_id=origin_scenario_by_company[company_id],
                    fixed_portfolio_id=fixed_portfolio_id,
                    common_avoided_emissions_mtco2=(
                        origin_schedule.cumulative_avoided_emissions_mtco2
                    ),
                    budget_diagnostics=diagnostics,
                )
                metrics.append(row)
                distributions[(company_id, scenario_id, plan_id)] = net_intensity

    by_key = {
        (str(row["company_id"]), str(row["scenario_id"]), str(row["plan_id"])): row
        for row in metrics
    }
    for company_id in bundle.companies:
        scenario_ids = _scenario_ids(bundle, company_id)
        if {"ACCELERATED_15C", "DISCLOSED_PATH"}.issubset(scenario_ids):
            for plan_id in _plan_ids(bundle, company_id):
                strict = by_key[(company_id, "ACCELERATED_15C", plan_id)]
                disclosed = by_key[(company_id, "DISCLOSED_PATH", plan_id)]
                exposure = abs(
                    float(strict[
                        "net_economic_cost_p50_kkrw_per_tco2_common_denominator"
                    ])
                    - float(disclosed[
                        "net_economic_cost_p50_kkrw_per_tco2_common_denominator"
                    ])
                )
                strict["policy_uncertainty_exposure_kkrw_per_tco2"] = round(exposure, 6)
                disclosed["policy_uncertainty_exposure_kkrw_per_tco2"] = round(exposure, 6)

    candidate_catalog: list[dict[str, object]] = []
    candidate_screening: list[dict[str, object]] = []
    candidate_scenario_metrics: list[dict[str, object]] = []
    selected_candidate_counts: dict[str, int] = {}
    candidate_objects_by_company: dict[str, list[object]] = {}
    screening_rows_by_company: dict[str, list[dict[str, object]]] = {}
    scenario_ids_by_company = {
        company_id: active_scenario_ids(bundle, company_id)
        for company_id in bundle.companies
    }
    for company_id in bundle.companies:
        candidates = enumerate_candidate_portfolios(bundle, company_id)
        candidate_objects_by_company[company_id] = candidates
        catalog_rows = [
            candidate_catalog_row(bundle, candidate) for candidate in candidates
        ]
        candidate_catalog.extend(catalog_rows)
        screening_rows: list[dict[str, object]] = []
        for candidate in candidates:
            for scenario_id in scenario_ids_by_company[company_id]:
                _, screening_row = screen_candidate(bundle, candidate, scenario_id)
                screening_rows.append(screening_row)
        candidate_screening.extend(screening_rows)
        screening_rows_by_company[company_id] = screening_rows
        selected_candidates = select_stochastic_candidates(
            candidates,
            screening_rows,
            scenario_ids_by_company[company_id],
            maximum=64,
        )
        selected_candidate_counts[company_id] = len(selected_candidates)
        for candidate in selected_candidates:
            for scenario_id in scenario_ids_by_company[company_id]:
                schedule, screening_row = screen_candidate(
                    bundle, candidate, scenario_id
                )
                simulation = simulate_schedule(
                    bundle,
                    schedule,
                    min(paths, 100),
                    run_seed,
                )
                row, _ = _metric_row(
                    bundle,
                    schedule,
                    simulation,
                    {factor: 0.0 for factor in FACTOR_LABELS},
                    origin_scenario_id=candidate.origin_scenario_id,
                    fixed_portfolio_id=portfolio_id(candidate.schedule),
                    common_avoided_emissions_mtco2=(
                        candidate.schedule.cumulative_avoided_emissions_mtco2
                    ),
                    budget_diagnostics=screening_row,
                )
                row.update({
                    "candidate_id": candidate.candidate_id,
                    "template_plan_id": candidate.template_plan_id,
                    "physical_portfolio_id": portfolio_id(candidate.schedule),
                    "candidate_path_count": min(paths, 100),
                    "is_generated_candidate": True,
                })
                candidate_scenario_metrics.append(row)
    candidate_robust_summary = build_robust_summary(
        candidate_scenario_metrics,
        scenario_ids_by_company,
    )
    candidate_scenario_comparisons = build_candidate_scenario_comparisons(
        candidate_scenario_metrics
    )

    refined_candidate_metrics: list[dict[str, object]] = []
    refined_candidate_counts: dict[str, int] = {}
    refined_candidates_by_id = {}
    for company_id in bundle.companies:
        refined_candidates = select_refinement_candidates(
            candidate_objects_by_company[company_id],
            screening_rows_by_company[company_id],
            scenario_ids_by_company[company_id],
        )
        refined_candidate_counts[company_id] = len(refined_candidates)
        refined_candidates_by_id.update(
            {candidate.candidate_id: candidate for candidate in refined_candidates}
        )
        for shortlist_rank, candidate in enumerate(refined_candidates, start=1):
            for scenario_id in scenario_ids_by_company[company_id]:
                schedule, screening_row = screen_candidate(
                    bundle, candidate, scenario_id
                )
                simulation = simulate_schedule(
                    bundle,
                    schedule,
                    paths,
                    run_seed,
                )
                common_avoided = candidate.schedule.cumulative_avoided_emissions_mtco2
                subset_variances: dict[frozenset[str], float] = {
                    frozenset(): 0.0,
                    frozenset(FACTOR_LABELS): sample_variance([
                        value / common_avoided
                        for value in simulation.net_costs_bn_krw
                    ]),
                }
                for size in (1, 2):
                    for subset in combinations(tuple(FACTOR_LABELS), size):
                        isolated = simulate_schedule(
                            bundle,
                            schedule,
                            paths,
                            run_seed,
                            active_factors=set(subset),
                        )
                        factor_intensity = [
                            value / common_avoided
                            for value in isolated.net_costs_bn_krw
                        ]
                        subset_variances[frozenset(subset)] = sample_variance(
                            factor_intensity
                        )
                factor_variances = {
                    factor: subset_variances[frozenset({factor})]
                    for factor in FACTOR_LABELS
                }
                shapley_contributions, shapley_shares, reconciliation_delta = (
                    _shapley_variance_allocation(subset_variances)
                )
                row, _ = _metric_row(
                    bundle,
                    schedule,
                    simulation,
                    factor_variances,
                    origin_scenario_id=candidate.origin_scenario_id,
                    fixed_portfolio_id=portfolio_id(candidate.schedule),
                    common_avoided_emissions_mtco2=(
                        candidate.schedule.cumulative_avoided_emissions_mtco2
                    ),
                    budget_diagnostics=screening_row,
                )
                row.update({
                    "candidate_id": candidate.candidate_id,
                    "template_plan_id": candidate.template_plan_id,
                    "physical_portfolio_id": portfolio_id(candidate.schedule),
                    "candidate_path_count": paths,
                    "refinement_shortlist_rank": shortlist_rank,
                    "refinement_tier": "deterministic_robust_shortlist_full_paths",
                    "is_generated_candidate": True,
                    "risk_decomposition_method": "variance_game_shapley_common_random_numbers",
                    "shapley_full_variance": round(
                        subset_variances[frozenset(FACTOR_LABELS)], 12
                    ),
                    "shapley_reconciliation_delta": round(
                        reconciliation_delta, 12
                    ),
                    **{
                        SHAPLEY_LABELS[factor]: round(shapley_shares[factor], 9)
                        for factor in FACTOR_LABELS
                    },
                    **{
                        f"{factor}_shapley_variance_contribution": round(
                            shapley_contributions[factor], 12
                        )
                        for factor in FACTOR_LABELS
                    },
                })
                refined_candidate_metrics.append(row)
    refined_candidate_robust_summary = build_robust_summary(
        refined_candidate_metrics,
        scenario_ids_by_company,
    )
    refined_candidate_scenario_comparisons = build_candidate_scenario_comparisons(
        refined_candidate_metrics
    )
    refined_metric_by_key = {
        (
            str(row["company_id"]),
            str(row["candidate_id"]),
            str(row["scenario_id"]),
        ): row
        for row in refined_candidate_metrics
    }
    refined_candidate_facility_rows: list[dict[str, object]] = []
    refined_candidate_resource_rows: list[dict[str, object]] = []
    for candidate_id, candidate in sorted(refined_candidates_by_id.items()):
        for scenario_id in scenario_ids_by_company[candidate.company_id]:
            schedule, screening_row = screen_candidate(
                bundle, candidate, scenario_id
            )
            metric = refined_metric_by_key[
                (candidate.company_id, candidate_id, scenario_id)
            ]
            common_fields = {
                "candidate_id": candidate_id,
                "template_plan_id": candidate.template_plan_id,
                "physical_portfolio_id": portfolio_id(candidate.schedule),
                "candidate_path_count": paths,
                "candidate_p50_kkrw_per_tco2": metric[
                    "expected_cost_p50_kkrw_per_tco2"
                ],
                "candidate_tcar_kkrw_per_tco2": metric["tcar_kkrw_per_tco2"],
                **screening_row,
            }
            for row in capex_schedule_rows(bundle, schedule):
                row.update(common_fields)
                refined_candidate_facility_rows.append(row)
            for row in resource_profile_rows(bundle, schedule):
                row.update(common_fields)
                refined_candidate_resource_rows.append(row)

    summary: dict[str, Any] = {
        "model_version": "0.8.0",
        "data_status": "official_company_totals_plus_explicit_model_estimates",
        "path_count": paths,
        "seed": run_seed,
        "active_scenario_ids": sorted(
            scenario_id
            for scenario_id, definition in bundle.scenario_definitions.items()
            if definition.is_active
        ),
        "pending_scenario_ids": sorted(
            scenario_id
            for scenario_id, definition in bundle.scenario_definitions.items()
            if not definition.is_active
        ),
        "generated_candidate_count": len(candidate_catalog),
        "candidate_screening_row_count": len(candidate_screening),
        "stochastic_candidate_count": sum(selected_candidate_counts.values()),
        "candidate_path_count": min(paths, 100),
        "selected_candidate_counts": selected_candidate_counts,
        "refined_candidate_count": sum(refined_candidate_counts.values()),
        "refined_candidate_path_count": paths,
        "refined_candidate_counts": refined_candidate_counts,
        "companies": {},
    }
    frontier_membership: list[dict[str, object]] = []
    for company_id, company in bundle.companies.items():
        company_summary: dict[str, Any] = {
            "company_name": company.company_name,
            "country_code": company.country_code,
            "scenarios": {},
        }
        for scenario_id in _scenario_ids(bundle, company_id):
            candidate_rows = [
                {
                    "plan_id": str(row["plan_id"]),
                    "p50": float(row["expected_cost_p50_kkrw_per_tco2"]),
                    "tcar": float(row["tcar_kkrw_per_tco2"]),
                }
                for row in metrics
                if row["company_id"] == company_id
                and row["scenario_id"] == scenario_id
                and not bool(row["is_disclosed_plan"])
                and bool(row["scenario_feasible"])
            ]
            if not candidate_rows:
                raise ValueError(
                    f"No scenario-feasible candidate portfolios for {company_id}/{scenario_id}"
                )
            frontier = pareto_frontier(candidate_rows)
            frontier_ids = {str(row["plan_id"]) for row in frontier}
            current = next(
                row
                for row in metrics
                if row["company_id"] == company_id
                and row["scenario_id"] == scenario_id
                and bool(row["is_disclosed_plan"])
            )
            candidate_plan_ids = [
                plan_id
                for plan_id in _plan_ids(bundle, company_id)
                if not bundle.plans[(company_id, plan_id)].is_disclosed_plan
                and bool(by_key[(company_id, scenario_id, plan_id)]["scenario_feasible"])
            ]
            pathwise_min = [
                min(
                    distributions[(company_id, scenario_id, plan_id)][index]
                    for plan_id in candidate_plan_ids
                )
                for index in range(paths)
            ]
            for plan_id in _plan_ids(bundle, company_id):
                values = distributions[(company_id, scenario_id, plan_id)]
                flexibility = quantile(
                    [
                        max(0.0, value - pathwise_min[index])
                        for index, value in enumerate(values)
                    ],
                    0.5,
                )
                by_key[(company_id, scenario_id, plan_id)][
                    "flexibility_value_kkrw_per_tco2"
                ] = round(flexibility, 6)
                frontier_membership.append({
                    "company_id": company_id,
                    "company_name": company.company_name,
                    "scenario_id": scenario_id,
                    "plan_id": plan_id,
                    "portfolio_id": by_key[(company_id, scenario_id, plan_id)][
                        "portfolio_id"
                    ],
                    "is_scenario_feasible": by_key[
                        (company_id, scenario_id, plan_id)
                    ]["scenario_feasible"],
                    "is_frontier_eligible": (
                        not bundle.plans[(company_id, plan_id)].is_disclosed_plan
                        and bool(by_key[(company_id, scenario_id, plan_id)][
                            "scenario_feasible"
                        ])
                    ),
                    "is_frontier": plan_id in frontier_ids,
                    "expected_cost_p50_kkrw_per_tco2": by_key[
                        (company_id, scenario_id, plan_id)
                    ]["expected_cost_p50_kkrw_per_tco2"],
                    "tcar_kkrw_per_tco2": by_key[(company_id, scenario_id, plan_id)][
                        "tcar_kkrw_per_tco2"
                    ],
                })
            lambda_choices = {}
            for risk_aversion in (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0):
                choice = min(
                    frontier,
                    key=lambda row: float(row["p50"])
                    + risk_aversion * float(row["tcar"]),
                )
                lambda_choices[str(risk_aversion)] = {
                    "plan_id": choice["plan_id"],
                    "objective": round(
                        float(choice["p50"])
                        + risk_aversion * float(choice["tcar"]),
                        6,
                    ),
                }
            company_summary["scenarios"][scenario_id] = {
                "frontier_plan_ids": sorted(frontier_ids),
                "current_plan_gap": _gap(current, frontier),
                "current_plan_scenario_feasible": current["scenario_feasible"],
                "current_plan_first_budget_breach_year": current[
                    "first_budget_breach_year"
                ],
                "current_plan_max_annual_budget_excess_mtco2": current[
                    "max_annual_budget_excess_mtco2"
                ],
                "lambda_optimal_plans": lambda_choices,
            }
            scenario_metrics = [
                row
                for row in metrics
                if row["company_id"] == company_id and row["scenario_id"] == scenario_id
            ]
            write_frontier_svg(
                output_root / f"frontier_{company_id}_{scenario_id}.svg",
                f"{company.company_name} · {scenario_id}",
                scenario_metrics,
                frontier_ids,
            )
        summary["companies"][company_id] = company_summary

    scenario_comparisons = _scenario_comparison_rows(bundle, by_key)

    write_csv(output_root / "plan_metrics.csv", metrics)
    write_csv(output_root / "facility_schedule.csv", facility_rows)
    write_csv(output_root / "frontier_membership.csv", frontier_membership)
    write_csv(output_root / "scenario_comparison.csv", scenario_comparisons)
    write_csv(output_root / "candidate_portfolios.csv", candidate_catalog)
    write_csv(output_root / "candidate_screening.csv", candidate_screening)
    write_csv(
        output_root / "candidate_scenario_metrics.csv",
        candidate_scenario_metrics,
    )
    write_csv(
        output_root / "candidate_robust_summary.csv",
        candidate_robust_summary,
    )
    write_csv(
        output_root / "candidate_scenario_comparison.csv",
        candidate_scenario_comparisons,
    )
    write_csv(
        output_root / "refined_candidate_scenario_metrics.csv",
        refined_candidate_metrics,
    )
    write_csv(
        output_root / "refined_candidate_robust_summary.csv",
        refined_candidate_robust_summary,
    )
    write_csv(
        output_root / "refined_candidate_scenario_comparison.csv",
        refined_candidate_scenario_comparisons,
    )
    write_csv(
        output_root / "refined_candidate_facility_schedule.csv",
        refined_candidate_facility_rows,
    )
    write_csv(
        output_root / "refined_candidate_resource_profile.csv",
        refined_candidate_resource_rows,
    )
    write_json(
        output_root / "scenario_registry.json",
        {
            "model_version": "0.8.0",
            "definitions": [
                asdict(bundle.scenario_definitions[scenario_id])
                for scenario_id in sorted(bundle.scenario_definitions)
            ],
        },
    )
    write_json(
        output_root / "gcam_manifest_validation.json",
        validate_gcam_manifests(bundle.root),
    )
    write_json(output_root / "run_summary.json", summary)
    report_path = output_root / "report.md"
    write_markdown_report(
        report_path,
        paths,
        metrics,
        summary,
        candidate_robust_summary,
        refined_candidate_robust_summary,
        refined_candidate_metrics,
        refined_candidate_facility_rows,
        refined_candidate_resource_rows,
        [asdict(item) for item in bundle.resource_benchmarks],
        [asdict(item) for item in bundle.transition_projects],
        [asdict(item) for item in bundle.technology_cost_evidence],
    )
    return {
        "report_path": str(report_path.resolve()),
        "company_count": len(bundle.companies),
        "plan_count": len(bundle.plans),
        "scenario_count": len(bundle.scenarios),
        "scenario_definition_count": len(bundle.scenario_definitions),
        "path_count": paths,
        "summary": summary,
        "metrics": metrics,
        "facility_rows": facility_rows,
        "frontier_membership": frontier_membership,
        "scenario_comparisons": scenario_comparisons,
        "candidate_catalog": candidate_catalog,
        "candidate_screening": candidate_screening,
        "candidate_scenario_metrics": candidate_scenario_metrics,
        "candidate_robust_summary": candidate_robust_summary,
        "candidate_scenario_comparisons": candidate_scenario_comparisons,
        "refined_candidate_metrics": refined_candidate_metrics,
        "refined_candidate_robust_summary": refined_candidate_robust_summary,
        "refined_candidate_scenario_comparisons": (
            refined_candidate_scenario_comparisons
        ),
        "refined_candidate_facility_rows": refined_candidate_facility_rows,
        "refined_candidate_resource_rows": refined_candidate_resource_rows,
    }
