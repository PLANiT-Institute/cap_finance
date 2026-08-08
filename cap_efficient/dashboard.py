from __future__ import annotations

from dataclasses import asdict
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .dashboard_localization import localize_dashboard_html
from .dashboard_template import HTML_TEMPLATE as PROFESSIONAL_HTML_TEMPLATE
from .loader import load_data
from .pipeline import run_pipeline
from .report import write_csv, write_json


AGGREGATE_FIELDS = (
    "expected_cost_p50_kkrw_per_tco2",
    "expected_cost_p50_bn_krw",
    "absolute_npv_p50_bn_krw",
    "absolute_npv_p90_bn_krw",
    "net_economic_cost_p50_kkrw_per_tco2_common_denominator",
    "net_cash_cost_after_support_p50_kkrw_per_tco2_common_denominator",
    "cash_cost_before_support_p50_bn_krw",
    "net_cash_cost_after_support_p50_bn_krw",
    "net_cash_cost_after_support_p90_bn_krw",
    "avoided_carbon_cost_value_p50_bn_krw",
    "policy_support_value_p50_bn_krw",
    "cash_policy_p50_nonadditivity_bn_krw",
    "economic_cost_p50_identity_delta_bn_krw",
    "tcar_kkrw_per_tco2",
    "gross_cost_p50_kkrw_per_tco2",
    "policy_support_dependence_kkrw_per_tco2",
    "policy_uncertainty_exposure_kkrw_per_tco2",
    "flexibility_value_kkrw_per_tco2",
    "electricity_variance_share",
    "hydrogen_variance_share",
    "capex_variance_share",
    "p90_net_cost_bn_krw",
    "p90_cost_to_ebitda_x",
    "p90_cost_to_annual_capex_x",
    "capex_cost_p50_bn_krw",
    "fixed_opex_cost_p50_bn_krw",
    "electricity_cost_p50_bn_krw",
    "hydrogen_cost_p50_bn_krw",
    "contract_premium_p50_bn_krw",
    "carbon_value_p50_bn_krw",
    "policy_support_p50_bn_krw",
    "component_reconciliation_p50_bn_krw",
)


def _mean(values: Iterable[float]) -> float:
    return statistics.fmean(list(values))


def _stdev(values: Iterable[float]) -> float:
    items = list(values)
    return statistics.stdev(items) if len(items) > 1 else 0.0


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


def _aggregate_runs(bundle, run_results, seeds):
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for result in run_results:
        for row in result["metrics"]:
            grouped[(str(row["company_id"]), str(row["scenario_id"]), str(row["plan_id"]))].append(row)

    aggregates: list[dict[str, object]] = []
    for company_id, company in bundle.companies.items():
        for scenario_id in _scenario_ids(bundle, company_id):
            for order, plan_id in enumerate(_plan_ids(bundle, company_id)):
                plan = bundle.plans[(company_id, plan_id)]
                rows = grouped[(company_id, scenario_id, plan_id)]
                if len(rows) != len(run_results):
                    raise ValueError(f"Incomplete repeated metrics for {company_id}/{scenario_id}/{plan_id}")
                aggregate: dict[str, object] = {
                    "company_id": company_id,
                    "company_name": company.company_name,
                    "country_code": company.country_code,
                    "scenario_id": scenario_id,
                    "portfolio_origin_scenario_id": rows[0][
                        "portfolio_origin_scenario_id"
                    ],
                    "portfolio_id": rows[0]["portfolio_id"],
                    "scenario_feasible": rows[0]["scenario_feasible"],
                    "carbon_budget_feasible": rows[0]["carbon_budget_feasible"],
                    "physical_constraints_feasible": rows[0]["physical_constraints_feasible"],
                    "resource_constraints_feasible": rows[0]["resource_constraints_feasible"],
                    "construction_concurrency_feasible": rows[0]["construction_concurrency_feasible"],
                    "failure_risk_constraint_feasible": rows[0]["failure_risk_constraint_feasible"],
                    "first_resource_breach_year": rows[0]["first_resource_breach_year"],
                    "max_scrap_supply_excess_mt": rows[0]["max_scrap_supply_excess_mt"],
                    "max_hydrogen_supply_excess_mt": rows[0]["max_hydrogen_supply_excess_mt"],
                    "max_incremental_grid_excess_twh": rows[0]["max_incremental_grid_excess_twh"],
                    "max_concurrent_construction_projects": rows[0]["max_concurrent_construction_projects"],
                    "concurrent_construction_limit": rows[0]["concurrent_construction_limit"],
                    "portfolio_failure_probability": rows[0]["portfolio_failure_probability"],
                    "portfolio_failure_probability_limit": rows[0]["portfolio_failure_probability_limit"],
                    "expected_failure_delay_years": rows[0]["expected_failure_delay_years"],
                    "first_budget_breach_year": rows[0][
                        "first_budget_breach_year"
                    ],
                    "max_annual_budget_excess_mtco2": rows[0][
                        "max_annual_budget_excess_mtco2"
                    ],
                    "minimum_annual_budget_margin_mtco2": rows[0][
                        "minimum_annual_budget_margin_mtco2"
                    ],
                    "scenario_avoided_emissions_mtco2": rows[0][
                        "scenario_avoided_emissions_mtco2"
                    ],
                    "common_avoided_emissions_mtco2": rows[0][
                        "common_avoided_emissions_mtco2"
                    ],
                    "plan_id": plan_id,
                    "plan_name": plan.plan_name,
                    "is_disclosed_plan": plan.is_disclosed_plan,
                    "aligned_capex_bn_krw": rows[0]["aligned_capex_bn_krw"],
                    "peak_capex_year": rows[0]["peak_capex_year"],
                    "peak_capex_bn_krw": rows[0]["peak_capex_bn_krw"],
                    "avoided_emissions_mtco2": rows[0]["avoided_emissions_mtco2"],
                    "plan_order": order,
                }
                for field in AGGREGATE_FIELDS:
                    values = [float(row[field]) for row in rows]
                    aggregate[f"{field}_mean"] = round(_mean(values), 6)
                    aggregate[f"{field}_std"] = round(_stdev(values), 6)
                    aggregate[f"{field}_min"] = round(min(values), 6)
                    aggregate[f"{field}_max"] = round(max(values), 6)
                frontier_count = sum(
                    plan_id
                    in result["summary"]["companies"][company_id]["scenarios"][scenario_id][
                        "frontier_plan_ids"
                    ]
                    for result in run_results
                )
                aggregate["frontier_frequency_pct"] = round(
                    100.0 * frontier_count / len(run_results), 1
                )
                aggregates.append(aggregate)

    seed_rows: list[dict[str, object]] = []
    current_summary: dict[str, dict[str, object]] = {}
    for company_id in bundle.companies:
        current_summary[company_id] = {}
        for scenario_id in _scenario_ids(bundle, company_id):
            scenario_seed_rows = []
            for seed, result in zip(seeds, run_results, strict=True):
                current = next(
                    row
                    for row in result["metrics"]
                    if row["company_id"] == company_id
                    and row["scenario_id"] == scenario_id
                    and bool(row["is_disclosed_plan"])
                )
                gap = result["summary"]["companies"][company_id]["scenarios"][scenario_id][
                    "current_plan_gap"
                ]
                row = {
                    "company_id": company_id,
                    "scenario_id": scenario_id,
                    "seed": seed,
                    "current_p50_kkrw_per_tco2": float(current["expected_cost_p50_kkrw_per_tco2"]),
                    "current_tcar_kkrw_per_tco2": float(current["tcar_kkrw_per_tco2"]),
                    "cost_gap_kkrw_per_tco2": float(gap["cost_gap_same_or_lower_risk"]),
                    "risk_gap_kkrw_per_tco2": float(gap["risk_gap_same_or_lower_cost"]),
                }
                seed_rows.append(row)
                scenario_seed_rows.append(row)
            current_summary[company_id][scenario_id] = {
                "p50_mean": round(_mean(row["current_p50_kkrw_per_tco2"] for row in scenario_seed_rows), 3),
                "p50_std": round(_stdev(row["current_p50_kkrw_per_tco2"] for row in scenario_seed_rows), 3),
                "tcar_mean": round(_mean(row["current_tcar_kkrw_per_tco2"] for row in scenario_seed_rows), 3),
                "tcar_std": round(_stdev(row["current_tcar_kkrw_per_tco2"] for row in scenario_seed_rows), 3),
                "cost_gap_mean": round(_mean(row["cost_gap_kkrw_per_tco2"] for row in scenario_seed_rows), 3),
                "risk_gap_mean": round(_mean(row["risk_gap_kkrw_per_tco2"] for row in scenario_seed_rows), 3),
            }
    return aggregates, seed_rows, current_summary


def _aggregate_scenario_comparisons(run_results):
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for result in run_results:
        for row in result["scenario_comparisons"]:
            grouped[(
                str(row["company_id"]),
                str(row["plan_id"]),
                str(row["from_scenario_id"]),
                str(row["to_scenario_id"]),
            )].append(row)
    delta_fields = (
        "delta_p50_common_kkrw_per_tco2",
        "delta_tcar_kkrw_per_tco2",
        "delta_absolute_npv_p50_bn_krw",
        "delta_absolute_npv_p90_bn_krw",
        "delta_aligned_capex_bn_krw",
        "delta_net_cash_cost_p50_bn_krw",
        "delta_avoided_carbon_value_p50_bn_krw",
        "delta_policy_support_value_p50_bn_krw",
    )
    aggregates: list[dict[str, object]] = []
    for rows in grouped.values():
        first = rows[0]
        aggregate = {
            key: first[key]
            for key in (
                "company_id",
                "company_name",
                "plan_id",
                "plan_name",
                "portfolio_id",
                "portfolio_origin_scenario_id",
                "from_scenario_id",
                "to_scenario_id",
                "from_scenario_feasible",
                "to_scenario_feasible",
                "same_physical_portfolio",
                "common_avoided_emissions_mtco2",
            )
        }
        for field in delta_fields:
            values = [float(row[field]) for row in rows]
            aggregate[f"{field}_mean"] = round(_mean(values), 6)
            aggregate[f"{field}_std"] = round(_stdev(values), 6)
            aggregate[f"{field}_min"] = round(min(values), 6)
            aggregate[f"{field}_max"] = round(max(values), 6)
        aggregates.append(aggregate)
    return aggregates


def _aggregate_candidate_analysis(
    run_results,
    *,
    scenario_result_key="candidate_scenario_metrics",
    robust_result_key="candidate_robust_summary",
    comparison_result_key="candidate_scenario_comparisons",
):
    scenario_fields = (
        "expected_cost_p50_kkrw_per_tco2",
        "net_economic_cost_p50_kkrw_per_tco2_common_denominator",
        "tcar_kkrw_per_tco2",
        "absolute_npv_p50_bn_krw",
        "absolute_npv_p90_bn_krw",
        "aligned_capex_bn_krw",
        "net_cash_cost_after_support_p50_bn_krw",
        "avoided_carbon_cost_value_p50_bn_krw",
        "policy_support_value_p50_bn_krw",
        "scenario_regret_p50_kkrw_per_tco2",
        "electricity_variance_share",
        "hydrogen_variance_share",
        "capex_variance_share",
    )
    optional_scenario_fields = (
        "electricity_shapley_variance_share",
        "hydrogen_shapley_variance_share",
        "capex_shapley_variance_share",
        "shapley_full_variance",
        "shapley_reconciliation_delta",
    )
    scenario_grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    robust_grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    comparison_grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for result in run_results:
        for row in result[scenario_result_key]:
            scenario_grouped[(
                str(row["company_id"]),
                str(row["candidate_id"]),
                str(row["scenario_id"]),
            )].append(row)
        for row in result[robust_result_key]:
            robust_grouped[(
                str(row["company_id"]), str(row["candidate_id"])
            )].append(row)
        for row in result[comparison_result_key]:
            comparison_grouped[(
                str(row["company_id"]),
                str(row["candidate_id"]),
                str(row["from_scenario_id"]),
                str(row["to_scenario_id"]),
            )].append(row)

    scenario_aggregates: list[dict[str, object]] = []
    for rows in scenario_grouped.values():
        first = rows[0]
        aggregate = {
            key: first[key]
            for key in (
                "company_id",
                "company_name",
                "candidate_id",
                "template_plan_id",
                "physical_portfolio_id",
                "scenario_id",
                "scenario_feasible",
                "carbon_budget_feasible",
                "physical_constraints_feasible",
                "common_avoided_emissions_mtco2",
                "candidate_path_count",
            )
        }
        for field in scenario_fields:
            values = [float(row[field]) for row in rows]
            aggregate[f"{field}_mean"] = round(_mean(values), 6)
            aggregate[f"{field}_std"] = round(_stdev(values), 6)
        for field in optional_scenario_fields:
            if field not in first:
                continue
            values = [float(row[field]) for row in rows]
            aggregate[f"{field}_mean"] = round(_mean(values), 9)
            aggregate[f"{field}_std"] = round(_stdev(values), 9)
        if "risk_decomposition_method" in first:
            aggregate["risk_decomposition_method"] = first[
                "risk_decomposition_method"
            ]
        scenario_aggregates.append(aggregate)

    robust_aggregates: list[dict[str, object]] = []
    robust_fields = (
        "worst_case_p50_kkrw_per_tco2",
        "worst_case_tcar_kkrw_per_tco2",
        "maximum_regret_p50_kkrw_per_tco2",
        "mean_regret_p50_kkrw_per_tco2",
    )
    for rows in robust_grouped.values():
        first = rows[0]
        aggregate = {
            key: first[key]
            for key in (
                "company_id",
                "company_name",
                "candidate_id",
                "template_plan_id",
                "physical_portfolio_id",
                "scenario_count",
                "feasible_scenario_count",
                "robust_feasible",
            )
        }
        for field in robust_fields:
            values = [float(row[field]) for row in rows]
            aggregate[f"{field}_mean"] = round(_mean(values), 6)
            aggregate[f"{field}_std"] = round(_stdev(values), 6)
        aggregate["robust_frontier_frequency_pct"] = round(
            100.0 * sum(bool(row["robust_frontier"]) for row in rows) / len(rows),
            1,
        )
        for field in ("lambda_0_optimal", "lambda_1_optimal", "lambda_4_optimal"):
            aggregate[f"{field}_frequency_pct"] = round(
                100.0 * sum(bool(row[field]) for row in rows) / len(rows), 1
            )
        robust_aggregates.append(aggregate)

    delta_fields = (
        "delta_p50_common_kkrw_per_tco2",
        "delta_tcar_kkrw_per_tco2",
        "delta_absolute_npv_p50_bn_krw",
        "delta_absolute_npv_p90_bn_krw",
        "delta_aligned_capex_bn_krw",
        "delta_net_cash_cost_p50_bn_krw",
        "delta_avoided_carbon_value_p50_bn_krw",
        "delta_policy_support_value_p50_bn_krw",
    )
    comparison_aggregates: list[dict[str, object]] = []
    for rows in comparison_grouped.values():
        first = rows[0]
        aggregate = {
            key: first[key]
            for key in (
                "company_id",
                "company_name",
                "candidate_id",
                "template_plan_id",
                "physical_portfolio_id",
                "from_scenario_id",
                "to_scenario_id",
                "from_scenario_feasible",
                "to_scenario_feasible",
                "same_physical_portfolio",
                "common_avoided_emissions_mtco2",
            )
        }
        for field in delta_fields:
            values = [float(row[field]) for row in rows]
            aggregate[f"{field}_mean"] = round(_mean(values), 6)
            aggregate[f"{field}_std"] = round(_stdev(values), 6)
        comparison_aggregates.append(aggregate)
    return scenario_aggregates, robust_aggregates, comparison_aggregates


def _html_document(payload: dict[str, object]) -> str:
    import json

    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return PROFESSIONAL_HTML_TEMPLATE.replace(
        "__DASHBOARD_DATA__", data_json.replace("</", "<\\/")
    )


def run_repeated_analysis(
    data_dir: Path | str = Path("data"),
    output_dir: Path | str = Path("outputs"),
    path_count: int = 1000,
    seeds: list[int] | tuple[int, ...] = (40, 41, 42),
) -> dict[str, Any]:
    if path_count < 1:
        raise ValueError("path_count must be positive")
    seed_list = list(seeds)
    if len(seed_list) < 2 or len(seed_list) != len(set(seed_list)):
        raise ValueError("At least two unique seeds are required")
    bundle = load_data(data_dir)
    output_root = Path(output_dir)
    runs_root = output_root / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    run_results = [
        run_pipeline(data_dir, runs_root / f"seed_{seed}", path_count, seed)
        for seed in seed_list
    ]
    aggregates, seed_rows, current_summary = _aggregate_runs(bundle, run_results, seed_list)
    scenario_comparisons = _aggregate_scenario_comparisons(run_results)
    (
        candidate_scenario_metrics,
        candidate_robust_summary,
        candidate_scenario_comparisons,
    ) = _aggregate_candidate_analysis(run_results)
    (
        refined_candidate_metrics,
        refined_candidate_robust_summary,
        refined_candidate_scenario_comparisons,
    ) = _aggregate_candidate_analysis(
        run_results,
        scenario_result_key="refined_candidate_metrics",
        robust_result_key="refined_candidate_robust_summary",
        comparison_result_key="refined_candidate_scenario_comparisons",
    )
    representative_index = seed_list.index(42) if 42 in seed_list else 0
    representative = run_results[representative_index]
    first_company_id = next(iter(bundle.companies))
    scenario_ids = _scenario_ids(bundle, first_company_id)
    scenario_labels = {
        scenario_id: bundle.scenario_definitions[scenario_id].scenario_name
        for scenario_id in scenario_ids
    }
    companies = []
    for company_id, company in bundle.companies.items():
        financials = bundle.financials[company_id]
        companies.append({
            "company_id": company_id,
            "company_name": company.company_name,
            "country_code": company.country_code,
            "country_name": company.country_name,
            "base_year": company.base_year,
            "reporting_boundary": company.reporting_boundary,
            "production_mt": company.production_mt,
            "scope12_emissions_mtco2": company.scope12_emissions_mtco2,
            "reported_intensity_tco2_per_t": company.reported_intensity_tco2_per_t,
            "capacity_mtpa": company.capacity_mtpa,
            "target_2030_mtco2": company.target_2030_mtco2,
            "target_2040_mtco2": company.target_2040_mtco2,
            "source_name": company.source_name,
            "source_url": company.source_url,
            "source_note": company.source_note,
            "revenue_bn_krw": financials.revenue_bn_krw,
            "ebitda_bn_krw": financials.ebitda_bn_krw,
            "annual_capex_bn_krw": financials.annual_capex_bn_krw,
            "fx_to_krw": financials.fx_to_krw,
        })
    all_points = [point for points in bundle.scenarios.values() for point in points]
    payload: dict[str, object] = {
        "meta": {
            "model_version": "0.8.0",
            "data_status": "공식 기업 총량 + 명시적 모델 추정",
            "path_count": path_count,
            "seeds": seed_list,
            "run_count": len(seed_list),
            "effective_paths_per_plan": path_count * len(seed_list),
            "representative_seed": seed_list[representative_index],
            "generated_candidate_count": representative["summary"][
                "generated_candidate_count"
            ],
            "stochastic_candidate_count": representative["summary"][
                "stochastic_candidate_count"
            ],
            "candidate_path_count": representative["summary"][
                "candidate_path_count"
            ],
            "effective_candidate_paths": representative["summary"][
                "candidate_path_count"
            ] * len(seed_list),
            "refined_candidate_count": representative["summary"][
                "refined_candidate_count"
            ],
            "refined_candidate_path_count": representative["summary"][
                "refined_candidate_path_count"
            ],
            "effective_refined_candidate_paths": representative["summary"][
                "refined_candidate_path_count"
            ] * len(seed_list),
            "year_start": min(point.year for point in all_points),
            "year_end": max(point.year for point in all_points),
            "transition_project_count": len(bundle.transition_projects),
            "technology_cost_evidence_count": len(
                bundle.technology_cost_evidence
            ),
            "evidence_extraction_date": max(
                project.extraction_date for project in bundle.transition_projects
            ),
        },
        "companies": companies,
        "technologies": [
            asdict(technology)
            for technology in bundle.technologies.values()
        ],
        "scenarios": [
            {
                "scenario_id": scenario_id,
                "label": scenario_labels[scenario_id],
                "family": bundle.scenario_definitions[scenario_id].scenario_family,
                "data_status": bundle.scenario_definitions[scenario_id].data_status,
                "source_url": bundle.scenario_definitions[scenario_id].source_url,
                "source_note": bundle.scenario_definitions[scenario_id].source_note,
            }
            for scenario_id in scenario_ids
        ],
        "scenario_registry": [
            asdict(bundle.scenario_definitions[scenario_id])
            for scenario_id in sorted(bundle.scenario_definitions)
        ],
        "resource_benchmarks": [
            asdict(item) for item in bundle.resource_benchmarks
        ],
        "transition_projects": [
            asdict(item) for item in bundle.transition_projects
        ],
        "technology_cost_evidence": [
            asdict(item) for item in bundle.technology_cost_evidence
        ],
        "scenario_paths": {
            company_id: {
                scenario_id: [
                    {
                        "year": point.year,
                        "carbon_budget_mtco2": point.company_carbon_budget_mtco2,
                        "electricity_price_krw_per_kwh": point.electricity_price_krw_per_kwh,
                        "carbon_price_krw_per_tco2": point.carbon_price_krw_per_tco2,
                    }
                    for point in bundle.scenarios[(company_id, scenario_id)]
                ]
                for scenario_id in _scenario_ids(bundle, company_id)
            }
            for company_id in bundle.companies
        },
        "plans": [
            {
                "company_id": company_id,
                "plan_id": plan_id,
                "plan_name": plan.plan_name,
                "schedule_shift_years": plan.schedule_shift_years,
                "min_h2_capacity_share": plan.min_h2_capacity_share,
                "ppa_share": plan.ppa_share,
                "hydrogen_contract_share": plan.hydrogen_contract_share,
                "fixed_epc_share": plan.fixed_epc_share,
                "ccfd_share": plan.ccfd_share,
                "contract_premium_pct": plan.contract_premium_pct,
                "is_disclosed_plan": plan.is_disclosed_plan,
                "source_note": plan.source_note,
            }
            for (company_id, plan_id), plan in bundle.plans.items()
        ],
        "aggregates": aggregates,
        "seed_rows": seed_rows,
        "current_summary": current_summary,
        "scenario_comparisons": scenario_comparisons,
        "candidate_scenario_metrics": candidate_scenario_metrics,
        "candidate_robust_summary": candidate_robust_summary,
        "candidate_scenario_comparisons": candidate_scenario_comparisons,
        "refined_candidate_metrics": refined_candidate_metrics,
        "refined_candidate_robust_summary": refined_candidate_robust_summary,
        "refined_candidate_scenario_comparisons": (
            refined_candidate_scenario_comparisons
        ),
        "refined_candidate_facility_rows": representative[
            "refined_candidate_facility_rows"
        ],
        "refined_candidate_resource_rows": representative[
            "refined_candidate_resource_rows"
        ],
        "candidate_catalog": representative["candidate_catalog"],
        "facility_rows": representative["facility_rows"],
    }
    write_csv(output_root / "repeat_plan_summary.csv", aggregates)
    write_csv(output_root / "repeat_seed_results.csv", seed_rows)
    write_csv(output_root / "repeat_scenario_comparison.csv", scenario_comparisons)
    write_csv(
        output_root / "repeat_candidate_scenario_metrics.csv",
        candidate_scenario_metrics,
    )
    write_csv(
        output_root / "repeat_candidate_robust_summary.csv",
        candidate_robust_summary,
    )
    write_csv(
        output_root / "repeat_candidate_scenario_comparison.csv",
        candidate_scenario_comparisons,
    )
    write_csv(
        output_root / "repeat_refined_candidate_scenario_metrics.csv",
        refined_candidate_metrics,
    )
    write_csv(
        output_root / "repeat_refined_candidate_robust_summary.csv",
        refined_candidate_robust_summary,
    )
    write_csv(
        output_root / "repeat_refined_candidate_scenario_comparison.csv",
        refined_candidate_scenario_comparisons,
    )
    write_csv(
        output_root / "refined_candidate_facility_schedule.csv",
        representative["refined_candidate_facility_rows"],
    )
    write_csv(
        output_root / "refined_candidate_resource_profile.csv",
        representative["refined_candidate_resource_rows"],
    )
    write_csv(
        output_root / "candidate_portfolios.csv",
        representative["candidate_catalog"],
    )
    write_csv(
        output_root / "candidate_screening.csv",
        representative["candidate_screening"],
    )
    write_csv(output_root / "facility_schedule.csv", representative["facility_rows"])
    write_json(output_root / "repeat_summary.json", payload)
    dashboard_path = output_root / "dashboard.html"
    dashboard_html = _html_document(payload)
    dashboard_path.write_text(dashboard_html, encoding="utf-8")
    english_dashboard_path = output_root / "dashboard_en.html"
    english_dashboard_path.write_text(
        localize_dashboard_html(dashboard_html), encoding="utf-8"
    )
    return {
        "dashboard_path": str(dashboard_path.resolve()),
        "english_dashboard_path": str(english_dashboard_path.resolve()),
        "run_count": len(seed_list),
        "path_count": path_count,
        "effective_paths_per_plan": path_count * len(seed_list),
        "aggregates": aggregates,
        "current_summary": current_summary,
        "scenario_comparisons": scenario_comparisons,
        "candidate_scenario_metrics": candidate_scenario_metrics,
        "candidate_robust_summary": candidate_robust_summary,
        "candidate_scenario_comparisons": candidate_scenario_comparisons,
        "refined_candidate_metrics": refined_candidate_metrics,
        "refined_candidate_robust_summary": refined_candidate_robust_summary,
        "refined_candidate_scenario_comparisons": (
            refined_candidate_scenario_comparisons
        ),
    }


HTML_TEMPLATE = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>한·일 철강 Capital Allocation Pathway</title>
<style>
:root{--ink:#10243d;--muted:#657286;--line:#d9e1ea;--panel:#fff;--navy:#123c69;--blue:#1b6ea8;--teal:#16818a;--red:#a33b31;--gold:#b97a17;--soft:#f2f5f8;--shadow:0 10px 28px rgba(16,36,61,.07)}*{box-sizing:border-box}body{margin:0;background:#edf2f6;color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.5}.shell{max-width:1280px;margin:auto;padding:24px 20px 52px}.hero{padding:34px 38px;border-radius:22px;background:linear-gradient(125deg,#0d2d50,#164b75 62%,#18777e);color:#fff;box-shadow:var(--shadow)}.eyebrow{margin:0 0 9px;color:#b9dbe4;font-size:12px;font-weight:750;letter-spacing:.13em;text-transform:uppercase}.hero h1{margin:0;font-size:clamp(29px,4vw,48px);line-height:1.08;letter-spacing:-.03em}.hero p{max-width:880px;margin:13px 0 0;color:#dce9f1}.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}.chip{padding:5px 11px;border:1px solid rgba(255,255,255,.25);border-radius:999px;background:rgba(255,255,255,.08);font-size:12px}.control{display:flex;justify-content:space-between;align-items:center;gap:14px;margin:24px 2px 14px}.control-group{display:flex;flex-wrap:wrap;gap:6px}.btn{border:1px solid var(--line);border-radius:10px;padding:9px 13px;background:#fff;color:var(--muted);font-weight:700;cursor:pointer}.btn.on{border-color:var(--navy);background:var(--navy);color:#fff}.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.fact,.panel{border:1px solid var(--line);border-radius:16px;background:var(--panel);box-shadow:0 6px 18px rgba(16,36,61,.04)}.fact{padding:16px 18px}.label{font-size:11px;font-weight:750;color:var(--muted)}.value{margin-top:3px;font-size:25px;font-weight:780;letter-spacing:-.02em;font-variant-numeric:tabular-nums}.sub{font-size:11px;color:var(--muted)}.grid{display:grid;grid-template-columns:1.45fr 1fr;gap:14px;margin-top:14px}.panel{padding:20px;overflow:hidden}.wide{grid-column:1/-1}.head{display:flex;justify-content:space-between;gap:16px;margin-bottom:13px}.head h2{margin:0;font-size:17px}.head p{margin:4px 0 0;color:var(--muted);font-size:12px}.chart{width:100%;height:auto;min-height:370px}.compare{display:grid;gap:11px}.compare-row{display:grid;grid-template-columns:110px 1fr 76px;align-items:center;gap:9px;font-size:12px}.track{height:24px;border-radius:7px;background:var(--soft);overflow:hidden}.bar{height:100%;display:flex;align-items:center;padding-left:8px;background:linear-gradient(90deg,var(--blue),var(--teal));color:#fff;font-size:10px;font-weight:750}.num{text-align:right;font-variant-numeric:tabular-nums}.factors{display:grid;gap:10px}.factor-row{display:grid;grid-template-columns:48px 1fr;gap:8px;align-items:center;font-size:11px}.stack{display:flex;height:23px;border-radius:6px;overflow:hidden;background:var(--soft)}.seg{display:flex;justify-content:center;align-items:center;color:#fff;font-size:9px;font-weight:700}.elec{background:#16818a}.hyd{background:#7252a4}.cap{background:#7b8fa3}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:9px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}th{color:var(--muted);font-size:11px}th:first-child,td:first-child{text-align:left}tr.current{background:#fff3ef}.pill{display:inline-block;padding:2px 7px;border-radius:99px;background:#e5f1f2;color:#0d6970;font-weight:700}.source-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.source{padding:15px;border:1px solid var(--line);border-radius:12px;background:#fafbfd}.source h3{margin:0 0 4px;font-size:14px}.source p{margin:4px 0;color:var(--muted);font-size:11px}.source a{color:var(--blue);font-size:11px}.warning{margin-top:14px;padding:14px 16px;border-left:4px solid var(--gold);background:#fff8e9;color:#5d4a28;font-size:12px}footer{margin-top:18px;text-align:center;color:var(--muted);font-size:11px}@media(max-width:900px){.facts{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.wide{grid-column:auto}.source-grid{grid-template-columns:1fr}}@media(max-width:560px){.shell{padding:12px 9px 36px}.hero{padding:25px 20px}.facts{grid-template-columns:1fr}.control{align-items:flex-start;flex-direction:column}.panel{padding:15px 11px}.compare-row{grid-template-columns:90px 1fr 68px}}
</style></head><body><main class="shell">
<header class="hero"><p class="eyebrow">KOREA × JAPAN STEEL · CAPITAL ALLOCATION</p><h1>POSCO와 일본 3사의 탈탄소 전환비용·위험 비교</h1><p>공식 생산·Scope 1+2·재무 총량을 기준점으로 고정하고, 설비 블록·전환시점·기술비용·계약·정책지원은 명시적 추정치로 분리했다.</p><div class="chips"><span class="chip" id="runs"></span><span class="chip" id="paths"></span><span class="chip" id="years"></span><span class="chip">공통 단위: KRW bn / 천원·tCO₂</span></div></header>
<div class="control"><div class="control-group" id="company-buttons"></div><div class="control-group" id="scenario-buttons"></div></div>
<section class="facts"><article class="fact"><div class="label">공식 조강 생산</div><div class="value" id="production"></div><div class="sub" id="production-note"></div></article><article class="fact"><div class="label">Scope 1+2 기준점</div><div class="value" id="emissions"></div><div class="sub" id="intensity"></div></article><article class="fact"><div class="label">공시전략 Net P50</div><div class="value" id="p50"></div><div class="sub" id="p50-note"></div></article><article class="fact"><div class="label">공시전략 P90 / EBITDA</div><div class="value" id="stress"></div><div class="sub" id="stress-note"></div></article></section>
<div class="grid">
<section class="panel wide"><div class="head"><div><h2>기업 간 공시전략 프록시 비교</h2><p>선택 시나리오의 반복 평균 Net P50. 기업 규모가 아닌 감축 1t당 비용 비교다.</p></div></div><div class="compare" id="compare"></div></section>
<section class="panel"><div class="head"><div><h2>효율 경계</h2><p>기대 전환비용(P50)과 TCaR(P90−P50). ◆는 공시전략 프록시.</p></div></div><svg id="frontier" class="chart" viewBox="0 0 820 430" role="img"></svg></section>
<section class="panel"><div class="head"><div><h2>TCaR 요인 분해</h2><p>전력·수소입력·건설비 분산 기여율.</p></div></div><div class="factors" id="factors"></div></section>
<section class="panel wide"><div class="head"><div><h2>계획별 반복 실행 요약</h2><p>공시전략과 7개 공통 대안을 같은 탄소예산에서 비교한다.</p></div></div><div class="table-wrap"><table><thead><tr><th>계획</th><th>Net P50</th><th>TCaR</th><th>정책의존</th><th>정책경로 노출</th><th>정렬 CAPEX</th><th>P90/EBITDA</th><th>경계빈도</th></tr></thead><tbody id="metrics"></tbody></table></div></section>
<section class="panel"><div class="head"><div><h2>공시전략 시설 전환</h2><p>대표 seed의 최적 정렬 결과. 설비별 배분은 모델 추정.</p></div></div><div class="table-wrap"><table><thead><tr><th>시설 블록</th><th>연도</th><th>기술</th><th>CAPEX</th></tr></thead><tbody id="facilities"></tbody></table></div></section>
<section class="panel"><div class="head"><div><h2>Seed 안정성</h2><p>공시전략 프록시의 반복별 표본 결과.</p></div></div><div class="table-wrap"><table><thead><tr><th>Seed</th><th>P50</th><th>TCaR</th><th>비용 gap</th><th>위험 gap</th></tr></thead><tbody id="seeds"></tbody></table></div></section>
<section class="panel wide"><div class="head"><div><h2>공식 기준점과 데이터 경계</h2><p>링크는 분석에 사용한 기업 원문이다. 시설·시나리오·비용의 추정 여부는 아래 메모에 명시했다.</p></div></div><div class="source-grid" id="sources"></div></section>
</div><aside class="warning"><strong>해석 제한.</strong> 생산·배출·재무의 기업 총량은 공식 공시지만 경계가 완전히 같지는 않다. 특히 Kobe Steel의 14.3MtCO₂는 감축목표 경계이며, Nippon Steel·JFE·Kobelco 재무는 연결 기준이다. 환율 1JPY=9.2KRW, 설비 배분, 재투자연도, 기술비용, 정책지원, 계약비율과 가속 1.5°C 경로는 모델 가정이다.</aside><footer id="footer"></footer>
</main><script id="data" type="application/json">__DASHBOARD_DATA__</script><script>
const D=JSON.parse(document.getElementById('data').textContent);let company=D.companies[0].company_id;let scenario=D.scenarios.find(x=>x.scenario_id==='ACCELERATED_15C')?.scenario_id||D.scenarios[0].scenario_id;const $=id=>document.getElementById(id);const fmt=(v,d=1)=>Number(v).toLocaleString('ko-KR',{minimumFractionDigits:d,maximumFractionDigits:d});const rows=()=>D.aggregates.filter(r=>r.company_id===company&&r.scenario_id===scenario).sort((a,b)=>a.plan_order-b.plan_order);const current=()=>rows().find(r=>r.is_disclosed_plan);const companyInfo=()=>D.companies.find(c=>c.company_id===company);const NS='http://www.w3.org/2000/svg';const se=(tag,a={},t='')=>{const e=document.createElementNS(NS,tag);Object.entries(a).forEach(([k,v])=>e.setAttribute(k,v));if(t)e.textContent=t;return e};
function buttons(){ $('company-buttons').innerHTML=D.companies.map(c=>`<button class="btn ${c.company_id===company?'on':''}" data-company="${c.company_id}">${c.country_code==='KR'?'🇰🇷':'🇯🇵'} ${c.company_name}</button>`).join('');$('scenario-buttons').innerHTML=D.scenarios.map(s=>`<button class="btn ${s.scenario_id===scenario?'on':''}" data-scenario="${s.scenario_id}">${s.label}</button>`).join('');document.querySelectorAll('[data-company]').forEach(b=>b.onclick=()=>{company=b.dataset.company;render()});document.querySelectorAll('[data-scenario]').forEach(b=>b.onclick=()=>{scenario=b.dataset.scenario;render()})}
function facts(){const c=companyInfo(),r=current(),s=D.current_summary[company][scenario];$('production').textContent=fmt(c.production_mt,2)+' Mt';$('production-note').textContent=`${c.base_year} · ${c.reporting_boundary}`;$('emissions').textContent=fmt(c.scope12_emissions_mtco2,2)+' Mt';$('intensity').textContent=`보고/보정 집약도 ${fmt(c.reported_intensity_tco2_per_t,2)} tCO₂/t`;$('p50').textContent=fmt(r.expected_cost_p50_kkrw_per_tco2_mean)+' 천원';$('p50-note').textContent=`TCaR ${fmt(r.tcar_kkrw_per_tco2_mean)} · 비용 gap ${fmt(s.cost_gap_mean)}`;$('stress').textContent=fmt(r.p90_cost_to_ebitda_x_mean,2)+'×';$('stress-note').textContent=`P90 / 연간 CAPEX ${fmt(r.p90_cost_to_annual_capex_x_mean,2)}×`}
function compare(){const vals=D.companies.map(c=>D.aggregates.find(r=>r.company_id===c.company_id&&r.scenario_id===scenario&&r.is_disclosed_plan));const max=Math.max(...vals.map(r=>r.expected_cost_p50_kkrw_per_tco2_mean),1);$('compare').innerHTML=vals.map(r=>`<div class="compare-row"><strong>${r.company_name}</strong><div class="track"><div class="bar" style="width:${Math.max(3,100*r.expected_cost_p50_kkrw_per_tco2_mean/max)}%">TCaR ${fmt(r.tcar_kkrw_per_tco2_mean)}</div></div><span class="num">${fmt(r.expected_cost_p50_kkrw_per_tco2_mean)}</span></div>`).join('')}
function frontier(){const svg=$('frontier');svg.innerHTML='';const rr=rows(),xs=rr.map(r=>r.expected_cost_p50_kkrw_per_tco2_mean),ys=rr.map(r=>r.tcar_kkrw_per_tco2_mean),pad=(a,b)=>Math.max((b-a)*.14,2),xmin=Math.min(...xs)-pad(Math.min(...xs),Math.max(...xs)),xmax=Math.max(...xs)+pad(Math.min(...xs),Math.max(...xs)),ymin=0,ymax=Math.max(...ys)+Math.max(Math.max(...ys)*.15,2),L=72,T=30,W=715,H=330,x=v=>L+(v-xmin)/(xmax-xmin)*W,y=v=>T+(ymax-v)/(ymax-ymin)*H;for(let i=0;i<6;i++){const xv=xmin+(xmax-xmin)*i/5,yv=ymin+(ymax-ymin)*i/5;svg.append(se('line',{x1:x(xv),y1:T,x2:x(xv),y2:T+H,stroke:'#e3e8ee'}));svg.append(se('text',{x:x(xv),y:T+H+22,'text-anchor':'middle','font-size':11,fill:'#687588'},fmt(xv,0)));svg.append(se('line',{x1:L,y1:y(yv),x2:L+W,y2:y(yv),stroke:'#e3e8ee'}));svg.append(se('text',{x:L-9,y:y(yv)+4,'text-anchor':'end','font-size':11,fill:'#687588'},fmt(yv,0)))}rr.forEach(r=>{const X=x(r.expected_cost_p50_kkrw_per_tco2_mean),Y=y(r.tcar_kkrw_per_tco2_mean),front=r.frontier_frequency_pct>0;if(r.is_disclosed_plan){svg.append(se('polygon',{points:`${X},${Y-9} ${X+9},${Y} ${X},${Y+9} ${X-9},${Y}`,fill:'#a33b31'}))}else svg.append(se('circle',{cx:X,cy:Y,r:7,fill:front?'#123c69':'#aab5c0'}));svg.append(se('text',{x:X+9,y:Y-9,'font-size':11,fill:'#26384c'},r.plan_id))});svg.append(se('text',{x:L+W/2,y:420,'text-anchor':'middle','font-size':12,fill:'#657286'},'Net P50 (천원/tCO₂)'));svg.append(se('text',{x:18,y:T+H/2,transform:`rotate(-90 18 ${T+H/2})`,'text-anchor':'middle','font-size':12,fill:'#657286'},'TCaR'))}
function factorBars(){$('factors').innerHTML=rows().map(r=>{const e=100*r.electricity_variance_share_mean,h=100*r.hydrogen_variance_share_mean,c=100*r.capex_variance_share_mean;return `<div class="factor-row"><strong>${r.plan_id}</strong><div class="stack"><span class="seg elec" style="width:${e}%">${e>14?fmt(e,0)+'%':''}</span><span class="seg hyd" style="width:${h}%">${h>14?fmt(h,0)+'%':''}</span><span class="seg cap" style="width:${c}%">${c>14?fmt(c,0)+'%':''}</span></div></div>`}).join('')}
function tables(){$('metrics').innerHTML=rows().map(r=>`<tr class="${r.is_disclosed_plan?'current':''}"><td><strong>${r.plan_id}</strong> <span class="sub">${r.plan_name}</span></td><td>${fmt(r.expected_cost_p50_kkrw_per_tco2_mean)} ± ${fmt(r.expected_cost_p50_kkrw_per_tco2_std)}</td><td>${fmt(r.tcar_kkrw_per_tco2_mean)}</td><td>${fmt(r.policy_support_dependence_kkrw_per_tco2_mean)}</td><td>${fmt(r.policy_uncertainty_exposure_kkrw_per_tco2_mean)}</td><td>${fmt(r.aligned_capex_bn_krw,0)}</td><td>${fmt(r.p90_cost_to_ebitda_x_mean,2)}×</td><td><span class="pill">${fmt(r.frontier_frequency_pct,0)}%</span></td></tr>`).join('');const fr=D.facility_rows.filter(r=>r.company_id===company&&r.scenario_id===scenario&&r.plan_id==='CURRENT');$('facilities').innerHTML=fr.map(r=>`<tr><td>${r.facility_name}</td><td>${r.transition_year}</td><td>${r.technology_id}</td><td>${fmt(r.aligned_capex_bn_krw,0)}</td></tr>`).join('');const sr=D.seed_rows.filter(r=>r.company_id===company&&r.scenario_id===scenario);$('seeds').innerHTML=sr.map(r=>`<tr><td>${r.seed}</td><td>${fmt(r.current_p50_kkrw_per_tco2)}</td><td>${fmt(r.current_tcar_kkrw_per_tco2)}</td><td>${fmt(r.cost_gap_kkrw_per_tco2)}</td><td>${fmt(r.risk_gap_kkrw_per_tco2)}</td></tr>`).join('')}
function sources(){$('sources').innerHTML=D.companies.map(c=>`<article class="source"><h3>${c.company_name} · ${c.base_year}</h3><p>생산 ${fmt(c.production_mt,2)}Mt · Scope 1+2 ${fmt(c.scope12_emissions_mtco2,2)}Mt · 2030 앵커 ${fmt(c.target_2030_mtco2,2)}Mt</p><p>${c.source_note}</p><a href="${c.source_url}" target="_blank" rel="noopener">${c.source_name} ↗</a></article>`).join('')}
function render(){buttons();facts();compare();frontier();factorBars();tables();sources()}$('runs').textContent=`${D.meta.run_count}회 반복 · seeds ${D.meta.seeds.join(', ')}`;$('paths').textContent=`계획·시나리오당 ${fmt(D.meta.effective_paths_per_plan,0)} 경로`;$('years').textContent=`${D.meta.year_start}–${D.meta.year_end}`;$('footer').textContent=`Capital Allocation Pathway v${D.meta.model_version} · ${D.meta.data_status} · 대표 seed ${D.meta.representative_seed}`;render();
</script></body></html>'''
