from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass
from typing import Iterable

from .models import DataBundle, Schedule, TransitionAction
from .schedule import (
    TRANSITION_TECHNOLOGIES,
    physical_constraint_diagnostics,
    portfolio_id,
    portfolio_signature,
    rebase_fixed_schedule,
    schedule_budget_diagnostics,
)


@dataclass(frozen=True)
class CandidatePortfolio:
    candidate_id: str
    company_id: str
    template_plan_id: str
    origin_scenario_id: str
    schedule: Schedule


def active_scenario_ids(bundle: DataBundle, company_id: str) -> list[str]:
    return [
        scenario_id
        for scenario_id, definition in bundle.scenario_definitions.items()
        if definition.is_active and (company_id, scenario_id) in bundle.scenarios
    ]


def _candidate_id(schedule: Schedule) -> str:
    decision_signature = f"{schedule.plan_id}|{portfolio_signature(schedule)}"
    digest = hashlib.sha256(decision_signature.encode("utf-8")).hexdigest()
    return f"CAND-{digest[:14].upper()}"


def enumerate_candidate_portfolios(
    bundle: DataBundle,
    company_id: str,
) -> list[CandidatePortfolio]:
    """Enumerate auditable technology/timing/contract-profile decision packages.

    Each package fixes the facility, technology and transition year once in the
    disclosed-path calendar, then reuses those actions in every scenario. The
    seven generic plans supply timing and contracting assumptions; CURRENT is
    excluded because it is a company disclosure proxy, not a generated option.
    """
    scenario_ids = active_scenario_ids(bundle, company_id)
    origin_scenario_id = (
        "DISCLOSED_PATH" if "DISCLOSED_PATH" in scenario_ids else scenario_ids[0]
    )
    scenario = bundle.scenarios[(company_id, origin_scenario_id)]
    first_year, last_year = scenario[0].year, scenario[-1].year
    facilities = sorted(
        (
            facility
            for facility in bundle.facilities.values()
            if facility.company_id == company_id
        ),
        key=lambda facility: facility.facility_id,
    )
    bf_capacity = sum(
        facility.capacity_mtpa
        for facility in facilities
        if facility.baseline_technology_id == "BF_BOF"
    )
    candidate_plans = sorted(
        (
            plan
            for (candidate_company_id, _), plan in bundle.plans.items()
            if candidate_company_id == company_id and not plan.is_disclosed_plan
        ),
        key=lambda plan: plan.plan_id,
    )
    candidates: dict[str, CandidatePortfolio] = {}
    for plan in candidate_plans:
        technology_options = []
        for facility in facilities:
            technology_ids = TRANSITION_TECHNOLOGIES.get(
                facility.baseline_technology_id
            )
            if technology_ids is None:
                raise ValueError(
                    f"No transition set for {facility.baseline_technology_id}"
                )
            technology_options.append(technology_ids)
        for technology_ids in itertools.product(*technology_options):
            h2_capacity = sum(
                facility.capacity_mtpa
                for facility, technology_id in zip(
                    facilities, technology_ids, strict=True
                )
                if technology_id == "H2_DRI_EAF"
            )
            if bf_capacity > 0 and (
                h2_capacity / bf_capacity + 1e-9 < plan.min_h2_capacity_share
            ):
                continue
            actions = tuple(
                TransitionAction(
                    facility_id=facility.facility_id,
                    technology_id=technology_id,
                    transition_year=min(
                        last_year,
                        max(
                            first_year,
                            bundle.technologies[technology_id].available_year,
                            facility.reinvestment_year + plan.schedule_shift_years,
                        ),
                    ),
                )
                for facility, technology_id in zip(
                    facilities, technology_ids, strict=True
                )
            )
            provisional = Schedule(
                company_id=company_id,
                scenario_id=origin_scenario_id,
                plan_id=plan.plan_id,
                actions=actions,
                deterministic_net_cost_bn_krw=0.0,
                cumulative_avoided_emissions_mtco2=0.0,
            )
            fixed_schedule = rebase_fixed_schedule(
                bundle, provisional, origin_scenario_id
            )
            candidate_id = _candidate_id(fixed_schedule)
            candidates[candidate_id] = CandidatePortfolio(
                candidate_id=candidate_id,
                company_id=company_id,
                template_plan_id=plan.plan_id,
                origin_scenario_id=origin_scenario_id,
                schedule=fixed_schedule,
            )
    return [candidates[key] for key in sorted(candidates)]


def candidate_catalog_row(
    bundle: DataBundle,
    candidate: CandidatePortfolio,
) -> dict[str, object]:
    facilities = {
        facility_id: facility
        for facility_id, facility in bundle.facilities.items()
        if facility.company_id == candidate.company_id
    }
    total_capacity = sum(
        facilities[action.facility_id].capacity_mtpa
        for action in candidate.schedule.actions
    )
    technology_capacity: dict[str, float] = {}
    for action in candidate.schedule.actions:
        technology_capacity[action.technology_id] = (
            technology_capacity.get(action.technology_id, 0.0)
            + facilities[action.facility_id].capacity_mtpa
        )
    years = [action.transition_year for action in candidate.schedule.actions]
    plan = bundle.plans[(candidate.company_id, candidate.template_plan_id)]
    return {
        "candidate_id": candidate.candidate_id,
        "company_id": candidate.company_id,
        "company_name": bundle.companies[candidate.company_id].company_name,
        "template_plan_id": candidate.template_plan_id,
        "template_plan_name": plan.plan_name,
        "physical_portfolio_id": portfolio_id(candidate.schedule),
        "origin_scenario_id": candidate.origin_scenario_id,
        "facility_action_count": len(candidate.schedule.actions),
        "earliest_transition_year": min(years),
        "latest_transition_year": max(years),
        "bf_reline_capacity_share": round(
            technology_capacity.get("BF_RELINE", 0.0) / total_capacity, 6
        ),
        "scrap_eaf_capacity_share": round(
            technology_capacity.get("SCRAP_EAF", 0.0) / total_capacity, 6
        ),
        "h2_dri_eaf_capacity_share": round(
            technology_capacity.get("H2_DRI_EAF", 0.0) / total_capacity, 6
        ),
        "renewable_eaf_capacity_share": round(
            technology_capacity.get("EAF_RENEWABLE", 0.0) / total_capacity, 6
        ),
        "ppa_share": plan.ppa_share,
        "hydrogen_contract_share": plan.hydrogen_contract_share,
        "fixed_epc_share": plan.fixed_epc_share,
        "ccfd_share": plan.ccfd_share,
        "contract_premium_pct": plan.contract_premium_pct,
        "common_avoided_emissions_mtco2": round(
            candidate.schedule.cumulative_avoided_emissions_mtco2, 6
        ),
        "action_signature": portfolio_signature(candidate.schedule),
        "data_status": "model_generated_candidate",
        "source_note": (
            "Generated from disclosed-path facility calendar, technology set and "
            "template contracting assumptions; not a company-announced project"
        ),
    }


def screen_candidate(
    bundle: DataBundle,
    candidate: CandidatePortfolio,
    scenario_id: str,
) -> tuple[Schedule, dict[str, object]]:
    schedule = rebase_fixed_schedule(bundle, candidate.schedule, scenario_id)
    diagnostics = schedule_budget_diagnostics(bundle, schedule)
    diagnostics.update(physical_constraint_diagnostics(bundle, schedule))
    diagnostics["scenario_feasible"] = bool(
        diagnostics["carbon_budget_feasible"]
        and diagnostics["physical_constraints_feasible"]
    )
    common_avoided = candidate.schedule.cumulative_avoided_emissions_mtco2
    row: dict[str, object] = {
        "candidate_id": candidate.candidate_id,
        "company_id": candidate.company_id,
        "company_name": bundle.companies[candidate.company_id].company_name,
        "template_plan_id": candidate.template_plan_id,
        "physical_portfolio_id": portfolio_id(candidate.schedule),
        "scenario_id": scenario_id,
        "common_avoided_emissions_mtco2": round(common_avoided, 6),
        "deterministic_economic_npv_bn_krw": round(
            schedule.deterministic_net_cost_bn_krw, 3
        ),
        "deterministic_cost_common_kkrw_per_tco2": round(
            schedule.deterministic_net_cost_bn_krw / common_avoided, 6
        ),
        **diagnostics,
    }
    return schedule, row


def select_stochastic_candidates(
    candidates: Iterable[CandidatePortfolio],
    screening_rows: Iterable[dict[str, object]],
    scenario_ids: Iterable[str],
    maximum: int = 64,
) -> list[CandidatePortfolio]:
    candidate_list = list(candidates)
    row_list = list(screening_rows)
    rows_by_candidate: dict[str, list[dict[str, object]]] = {}
    for row in row_list:
        rows_by_candidate.setdefault(str(row["candidate_id"]), []).append(row)
    chosen: list[str] = []

    def add(candidate_ids: Iterable[str]) -> None:
        for candidate_id in candidate_ids:
            if candidate_id not in chosen and len(chosen) < maximum:
                chosen.append(candidate_id)

    scenario_id_list = list(scenario_ids)
    robust = [
        candidate
        for candidate in candidate_list
        if all(
            bool(row["scenario_feasible"])
            for row in rows_by_candidate[candidate.candidate_id]
        )
    ]
    add(
        candidate.candidate_id
        for candidate in sorted(
            robust,
            key=lambda item: max(
                float(row["deterministic_cost_common_kkrw_per_tco2"])
                for row in rows_by_candidate[item.candidate_id]
            ),
        )[:24]
    )
    for scenario_id in scenario_id_list:
        feasible_rows = sorted(
            (
                row
                for row in row_list
                if row["scenario_id"] == scenario_id
                and bool(row["scenario_feasible"])
            ),
            key=lambda row: float(
                row["deterministic_cost_common_kkrw_per_tco2"]
            ),
        )
        add(str(row["candidate_id"]) for row in feasible_rows[:24])
    add(candidate.candidate_id for candidate in candidate_list)
    by_id = {candidate.candidate_id: candidate for candidate in candidate_list}
    return [by_id[candidate_id] for candidate_id in chosen]


def select_refinement_candidates(
    candidates: Iterable[CandidatePortfolio],
    screening_rows: Iterable[dict[str, object]],
    scenario_ids: Iterable[str],
    robust_maximum: int = 6,
    per_scenario: int = 2,
) -> list[CandidatePortfolio]:
    """Select a deterministic, seed-independent high-precision shortlist.

    The shortlist contains the lowest worst-case deterministic-cost portfolios
    that pass every active scenario plus the lowest-cost feasible portfolios in
    each individual scenario. This preserves both robust options and the
    scenario-specific regret baselines without letting Monte Carlo seed noise
    change the candidate set between repeated runs.
    """
    candidate_list = list(candidates)
    row_list = list(screening_rows)
    rows_by_candidate: dict[str, list[dict[str, object]]] = {}
    for row in row_list:
        rows_by_candidate.setdefault(str(row["candidate_id"]), []).append(row)
    chosen: list[str] = []

    def add(candidate_ids: Iterable[str]) -> None:
        for candidate_id in candidate_ids:
            if candidate_id not in chosen:
                chosen.append(candidate_id)

    robust = [
        candidate
        for candidate in candidate_list
        if all(
            bool(row["scenario_feasible"])
            for row in rows_by_candidate[candidate.candidate_id]
        )
    ]
    add(
        candidate.candidate_id
        for candidate in sorted(
            robust,
            key=lambda item: max(
                float(row["deterministic_cost_common_kkrw_per_tco2"])
                for row in rows_by_candidate[item.candidate_id]
            ),
        )[:robust_maximum]
    )
    for scenario_id in scenario_ids:
        feasible_rows = sorted(
            (
                row
                for row in row_list
                if row["scenario_id"] == scenario_id
                and bool(row["scenario_feasible"])
            ),
            key=lambda row: float(row["deterministic_cost_common_kkrw_per_tco2"]),
        )
        add(str(row["candidate_id"]) for row in feasible_rows[:per_scenario])
    by_id = {candidate.candidate_id: candidate for candidate in candidate_list}
    return [by_id[candidate_id] for candidate_id in chosen]


def build_robust_summary(
    candidate_metrics: list[dict[str, object]],
    scenario_ids_by_company: dict[str, list[str]],
) -> list[dict[str, object]]:
    best_by_scenario: dict[tuple[str, str], float] = {}
    for company_id, scenario_ids in scenario_ids_by_company.items():
        for scenario_id in scenario_ids:
            feasible = [
                float(row["expected_cost_p50_kkrw_per_tco2"])
                for row in candidate_metrics
                if row["company_id"] == company_id
                and row["scenario_id"] == scenario_id
                and bool(row["scenario_feasible"])
            ]
            if not feasible:
                raise ValueError(
                    f"No feasible generated candidate for {company_id}/{scenario_id}"
                )
            best_by_scenario[(company_id, scenario_id)] = min(feasible)
    for row in candidate_metrics:
        row["scenario_regret_p50_kkrw_per_tco2"] = round(
            float(row["expected_cost_p50_kkrw_per_tco2"])
            - best_by_scenario[(str(row["company_id"]), str(row["scenario_id"]))],
            6,
        )

    rows_by_candidate: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in candidate_metrics:
        rows_by_candidate.setdefault(
            (str(row["company_id"]), str(row["candidate_id"])), []
        ).append(row)
    summary_rows: list[dict[str, object]] = []
    for (company_id, candidate_id), rows in sorted(rows_by_candidate.items()):
        expected_scenarios = scenario_ids_by_company[company_id]
        feasible_count = sum(bool(row["scenario_feasible"]) for row in rows)
        summary_rows.append({
            "company_id": company_id,
            "company_name": rows[0]["company_name"],
            "candidate_id": candidate_id,
            "template_plan_id": rows[0]["template_plan_id"],
            "physical_portfolio_id": rows[0]["physical_portfolio_id"],
            "scenario_count": len(expected_scenarios),
            "feasible_scenario_count": feasible_count,
            "robust_feasible": feasible_count == len(expected_scenarios),
            "worst_case_p50_kkrw_per_tco2": round(
                max(float(row["expected_cost_p50_kkrw_per_tco2"]) for row in rows),
                6,
            ),
            "worst_case_tcar_kkrw_per_tco2": round(
                max(float(row["tcar_kkrw_per_tco2"]) for row in rows), 6
            ),
            "maximum_regret_p50_kkrw_per_tco2": round(
                max(float(row["scenario_regret_p50_kkrw_per_tco2"]) for row in rows),
                6,
            ),
            "mean_regret_p50_kkrw_per_tco2": round(
                sum(float(row["scenario_regret_p50_kkrw_per_tco2"]) for row in rows)
                / len(rows),
                6,
            ),
            "robust_frontier": False,
            "lambda_0_optimal": False,
            "lambda_1_optimal": False,
            "lambda_4_optimal": False,
        })

    for company_id in scenario_ids_by_company:
        eligible = [
            row
            for row in summary_rows
            if row["company_id"] == company_id and bool(row["robust_feasible"])
        ]
        frontier = [
            row
            for row in eligible
            if not any(
                other["candidate_id"] != row["candidate_id"]
                and float(other["maximum_regret_p50_kkrw_per_tco2"])
                <= float(row["maximum_regret_p50_kkrw_per_tco2"])
                and float(other["worst_case_tcar_kkrw_per_tco2"])
                <= float(row["worst_case_tcar_kkrw_per_tco2"])
                and (
                    float(other["maximum_regret_p50_kkrw_per_tco2"])
                    < float(row["maximum_regret_p50_kkrw_per_tco2"])
                    or float(other["worst_case_tcar_kkrw_per_tco2"])
                    < float(row["worst_case_tcar_kkrw_per_tco2"])
                )
                for other in eligible
            )
        ]
        frontier_ids = {str(row["candidate_id"]) for row in frontier}
        for row in eligible:
            row["robust_frontier"] = str(row["candidate_id"]) in frontier_ids
        for risk_aversion, field in (
            (0.0, "lambda_0_optimal"),
            (1.0, "lambda_1_optimal"),
            (4.0, "lambda_4_optimal"),
        ):
            if eligible:
                choice = min(
                    eligible,
                    key=lambda row: float(
                        row["maximum_regret_p50_kkrw_per_tco2"]
                    )
                    + risk_aversion
                    * float(row["worst_case_tcar_kkrw_per_tco2"]),
                )
                choice[field] = True
    return summary_rows


def build_candidate_scenario_comparisons(
    candidate_metrics: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows_by_candidate: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in candidate_metrics:
        rows_by_candidate.setdefault(
            (str(row["company_id"]), str(row["candidate_id"])), []
        ).append(row)
    comparisons: list[dict[str, object]] = []
    for (company_id, candidate_id), rows in sorted(rows_by_candidate.items()):
        ordered = sorted(rows, key=lambda row: str(row["scenario_id"]))
        for origin, target in itertools.combinations(ordered, 2):
            comparisons.append({
                "company_id": company_id,
                "company_name": origin["company_name"],
                "candidate_id": candidate_id,
                "template_plan_id": origin["template_plan_id"],
                "physical_portfolio_id": origin["physical_portfolio_id"],
                "from_scenario_id": origin["scenario_id"],
                "to_scenario_id": target["scenario_id"],
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
    return comparisons
