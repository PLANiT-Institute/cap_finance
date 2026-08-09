from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Callable, TypeVar

from .gcam_manifest import validate_gcam_manifests

from .models import (
    Company,
    CompanyConstraint,
    CompanyFinancials,
    DataBundle,
    Facility,
    Plan,
    PolicySupport,
    ScenarioDefinition,
    ScenarioPoint,
    Technology,
    TechnologyCostEvidence,
    TechnologyConstraint,
    TransitionProject,
    ResourceBenchmark,
    ResourceConstraintPoint,
)

T = TypeVar("T")


def _read_csv(path: Path, builder: Callable[[dict[str, str]], T]) -> list[T]:
    if not path.exists():
        raise FileNotFoundError(f"Required data file is missing: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [builder(row) for row in csv.DictReader(handle)]


def _as_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"Expected true/false, got {value!r}")
    return normalized == "true"


def _optional_float(value: str) -> float | None:
    normalized = value.strip()
    return float(normalized) if normalized else None


def _optional_int(value: str) -> int | None:
    normalized = value.strip()
    return int(normalized) if normalized else None


def _company(row: dict[str, str]) -> Company:
    return Company(
        company_id=row["company_id"],
        company_name=row["company_name"],
        country_code=row["country_code"],
        country_name=row["country_name"],
        base_year=int(row["base_year"]),
        reporting_boundary=row["reporting_boundary"],
        production_mt=float(row["production_mt"]),
        scope12_emissions_mtco2=float(row["scope12_emissions_mtco2"]),
        reported_intensity_tco2_per_t=float(row["reported_intensity_tco2_per_t"]),
        capacity_mtpa=float(row["capacity_mtpa"]),
        target_2030_mtco2=float(row["target_2030_mtco2"]),
        target_2040_mtco2=float(row["target_2040_mtco2"]),
        reporting_currency=row["reporting_currency"],
        fx_to_krw=float(row["fx_to_krw"]),
        capex_cost_index=float(row["capex_cost_index"]),
        data_status=row["data_status"],
        source_name=row["source_name"],
        source_url=row["source_url"],
        source_note=row["source_note"],
    )


def _facility(row: dict[str, str]) -> Facility:
    return Facility(
        facility_id=row["facility_id"],
        company_id=row["company_id"],
        facility_name=row["facility_name"],
        region=row["region"],
        capacity_mtpa=float(row["capacity_mtpa"]),
        utilization_rate=float(row["utilization_rate"]),
        baseline_technology_id=row["baseline_technology_id"],
        baseline_emissions_tco2_per_t=float(row["baseline_emissions_tco2_per_t"]),
        baseline_electricity_mwh_per_t=float(row["baseline_electricity_mwh_per_t"]),
        baseline_fixed_opex_kkrw_per_t=float(row["baseline_fixed_opex_kkrw_per_t"]),
        commission_year=int(row["commission_year"]),
        reinvestment_year=int(row["reinvestment_year"]),
        data_status=row["data_status"],
        source_note=row["source_note"],
    )


def _technology(row: dict[str, str]) -> Technology:
    return Technology(
        technology_id=row["technology_id"],
        technology_name=row["technology_name"],
        capex_bn_krw_per_mtpa=float(row["capex_bn_krw_per_mtpa"]),
        fixed_opex_kkrw_per_t=float(row["fixed_opex_kkrw_per_t"]),
        electricity_mwh_per_t=float(row["electricity_mwh_per_t"]),
        hydrogen_t_per_t=float(row["hydrogen_t_per_t"]),
        emissions_tco2_per_t=float(row["emissions_tco2_per_t"]),
        available_year=int(row["available_year"]),
        construction_years=int(row["construction_years"]),
        lifetime_years=int(row["lifetime_years"]),
        data_status=row["data_status"],
        source_note=row["source_note"],
    )


def _technology_constraint(row: dict[str, str]) -> TechnologyConstraint:
    return TechnologyConstraint(
        technology_id=row["technology_id"],
        scrap_input_t_per_t=float(row["scrap_input_t_per_t"]),
        failure_probability=float(row["failure_probability"]),
        max_failure_delay_years=int(row["max_failure_delay_years"]),
        data_status=row["data_status"],
        source_url=row["source_url"],
        source_note=row["source_note"],
    )


def _company_constraint(row: dict[str, str]) -> CompanyConstraint:
    return CompanyConstraint(
        company_id=row["company_id"],
        max_concurrent_construction_projects=int(
            row["max_concurrent_construction_projects"]
        ),
        max_portfolio_failure_probability=float(
            row["max_portfolio_failure_probability"]
        ),
        data_status=row["data_status"],
        source_url=row["source_url"],
        source_note=row["source_note"],
    )


def _resource_constraint(row: dict[str, str]) -> ResourceConstraintPoint:
    return ResourceConstraintPoint(
        company_id=row["company_id"],
        scenario_id=row["scenario_id"],
        year=int(row["year"]),
        max_scrap_supply_mt=float(row["max_scrap_supply_mt"]),
        max_hydrogen_supply_mt=float(row["max_hydrogen_supply_mt"]),
        max_incremental_grid_twh=float(row["max_incremental_grid_twh"]),
        data_status=row["data_status"],
        source_url=row["source_url"],
        source_note=row["source_note"],
    )


def _resource_benchmark(row: dict[str, str]) -> ResourceBenchmark:
    return ResourceBenchmark(
        benchmark_id=row["benchmark_id"],
        country_code=row["country_code"],
        resource_type=row["resource_type"],
        benchmark_year=int(row["benchmark_year"]),
        benchmark_value=_optional_float(row["benchmark_value"]),
        unit=row["unit"],
        geography=row["geography"],
        scope=row["scope"],
        source_org=row["source_org"],
        source_title=row["source_title"],
        source_url=row["source_url"],
        source_version=row["source_version"],
        extraction_date=row["extraction_date"],
        data_status=row["data_status"],
        comparability=row["comparability"],
        source_note=row["source_note"],
    )


def _transition_project(row: dict[str, str]) -> TransitionProject:
    return TransitionProject(
        project_id=row["project_id"],
        company_id=row["company_id"],
        related_facility_ids=row["related_facility_ids"],
        model_mapping_status=row["model_mapping_status"],
        project_name=row["project_name"],
        country_code=row["country_code"],
        project_status=row["project_status"],
        decision_stage=row["decision_stage"],
        announcement_date=row["announcement_date"],
        construction_start_date=row["construction_start_date"],
        operation_start_year=_optional_int(row["operation_start_year"]),
        operation_start_label=row["operation_start_label"],
        technology_id=row["technology_id"],
        capacity_mtpa=_optional_float(row["capacity_mtpa"]),
        capex_native_bn=_optional_float(row["capex_native_bn"]),
        capex_currency=row["capex_currency"],
        fx_to_krw=_optional_float(row["fx_to_krw"]),
        capex_bn_krw=_optional_float(row["capex_bn_krw"]),
        government_support_native_bn=_optional_float(
            row["government_support_native_bn"]
        ),
        government_support_pct=_optional_float(row["government_support_pct"]),
        disclosed_reduction_pct=_optional_float(row["disclosed_reduction_pct"]),
        avoided_emissions_mtco2_pa=_optional_float(
            row["avoided_emissions_mtco2_pa"]
        ),
        scrap_share=_optional_float(row["scrap_share"]),
        hbi_share=_optional_float(row["hbi_share"]),
        data_status=row["data_status"],
        confidence_grade=row["confidence_grade"],
        source_title=row["source_title"],
        source_url=row["source_url"],
        source_version=row["source_version"],
        extraction_date=row["extraction_date"],
        scope_note=row["scope_note"],
    )


def _technology_cost_evidence(row: dict[str, str]) -> TechnologyCostEvidence:
    return TechnologyCostEvidence(
        evidence_id=row["evidence_id"],
        project_id=row["project_id"],
        company_id=row["company_id"],
        technology_id=row["technology_id"],
        evidence_scope=row["evidence_scope"],
        capacity_mtpa=float(row["capacity_mtpa"]),
        capex_native_bn=float(row["capex_native_bn"]),
        capex_currency=row["capex_currency"],
        fx_to_krw=float(row["fx_to_krw"]),
        capex_bn_krw=float(row["capex_bn_krw"]),
        normalized_capex_bn_krw_per_mtpa=float(
            row["normalized_capex_bn_krw_per_mtpa"]
        ),
        government_support_bn_krw=_optional_float(
            row["government_support_bn_krw"]
        ),
        gross_or_net=row["gross_or_net"],
        included_assets=row["included_assets"],
        comparability=row["comparability"],
        data_status=row["data_status"],
        confidence_grade=row["confidence_grade"],
        source_url=row["source_url"],
        extraction_date=row["extraction_date"],
        calculation_note=row["calculation_note"],
    )


def _validate_transition_evidence(
    projects: tuple[TransitionProject, ...],
    cost_evidence: tuple[TechnologyCostEvidence, ...],
    companies: dict[str, Company],
    facilities: dict[str, Facility],
    technologies: dict[str, Technology],
) -> None:
    if not projects or not cost_evidence:
        raise ValueError("Transition-project evidence tables must not be empty")
    project_ids: set[str] = set()
    for project in projects:
        if project.project_id in project_ids:
            raise ValueError(f"Duplicate transition project {project.project_id}")
        project_ids.add(project.project_id)
        if project.company_id not in companies:
            raise ValueError(f"Unknown project company {project.company_id}")
        if project.country_code != companies[project.company_id].country_code:
            raise ValueError(f"Project country mismatch for {project.project_id}")
        if project.technology_id not in technologies:
            raise ValueError(f"Unknown project technology for {project.project_id}")
        for facility_id in filter(None, project.related_facility_ids.split("|")):
            if facility_id not in facilities:
                raise ValueError(
                    f"Unknown related facility {facility_id} for {project.project_id}"
                )
            if facilities[facility_id].company_id != project.company_id:
                raise ValueError(f"Project/facility company mismatch for {project.project_id}")
        if not project.source_url.startswith("https://"):
            raise ValueError(f"Project {project.project_id} requires an HTTPS source")
        for value in (project.capacity_mtpa, project.capex_native_bn, project.capex_bn_krw):
            if value is not None and value <= 0:
                raise ValueError(f"Project {project.project_id} has a non-positive value")
        if (
            project.capex_native_bn is not None
            and project.fx_to_krw is not None
            and project.capex_bn_krw is not None
            and abs(project.capex_native_bn * project.fx_to_krw - project.capex_bn_krw)
            > 0.01
        ):
            raise ValueError(f"Project FX conversion mismatch for {project.project_id}")
        for share in (
            project.government_support_pct,
            project.disclosed_reduction_pct,
            project.scrap_share,
            project.hbi_share,
        ):
            if share is not None and not 0 <= share <= 1:
                raise ValueError(f"Project share outside [0,1] for {project.project_id}")
    evidence_ids: set[str] = set()
    for item in cost_evidence:
        if item.evidence_id in evidence_ids:
            raise ValueError(f"Duplicate cost evidence {item.evidence_id}")
        evidence_ids.add(item.evidence_id)
        if item.project_id not in project_ids:
            raise ValueError(f"Unknown cost-evidence project {item.project_id}")
        if item.company_id not in companies or item.technology_id not in technologies:
            raise ValueError(f"Invalid cost evidence link {item.evidence_id}")
        if not item.source_url.startswith("https://"):
            raise ValueError(f"Cost evidence {item.evidence_id} requires an HTTPS source")
        expected_capex = item.capex_native_bn * item.fx_to_krw
        expected_unit = item.capex_bn_krw / item.capacity_mtpa
        if abs(expected_capex - item.capex_bn_krw) > 0.01:
            raise ValueError(f"Cost-evidence FX mismatch for {item.evidence_id}")
        if abs(expected_unit - item.normalized_capex_bn_krw_per_mtpa) > 0.01:
            raise ValueError(f"Cost-evidence unit mismatch for {item.evidence_id}")


def _validate_resource_benchmarks(
    benchmarks: tuple[ResourceBenchmark, ...],
) -> None:
    if not benchmarks:
        raise ValueError("resource_benchmarks.csv must not be empty")
    ids: set[str] = set()
    for item in benchmarks:
        if item.benchmark_id in ids:
            raise ValueError(f"Duplicate resource benchmark {item.benchmark_id}")
        ids.add(item.benchmark_id)
        if item.country_code not in {"KR", "JP"}:
            raise ValueError(f"Unsupported benchmark country {item.country_code}")
        if item.resource_type not in {"hydrogen", "grid", "scrap"}:
            raise ValueError(f"Unsupported benchmark resource {item.resource_type}")
        if not item.source_url.startswith("https://"):
            raise ValueError(f"Benchmark {item.benchmark_id} requires an HTTPS source")
        if item.benchmark_value is None and item.data_status != "official_qualitative":
            raise ValueError(
                f"Benchmark {item.benchmark_id} has no value but is not qualitative"
            )
        if item.benchmark_value is not None and item.benchmark_value < 0:
            raise ValueError(f"Benchmark {item.benchmark_id} must be non-negative")
        if "not_company" not in item.comparability:
            raise ValueError(
                f"Benchmark {item.benchmark_id} must state that it is not a company limit"
            )


def _scenario(row: dict[str, str]) -> ScenarioPoint:
    return ScenarioPoint(
        company_id=row["company_id"],
        scenario_id=row["scenario_id"],
        temperature_label=row["temperature_label"],
        year=int(row["year"]),
        company_carbon_budget_mtco2=float(row["company_carbon_budget_mtco2"]),
        electricity_price_krw_per_kwh=float(row["electricity_price_krw_per_kwh"]),
        carbon_price_krw_per_tco2=float(row["carbon_price_krw_per_tco2"]),
        electrolyzer_capex_index=float(row["electrolyzer_capex_index"]),
        data_status=row["data_status"],
        source_note=row["source_note"],
    )


def _scenario_definition(row: dict[str, str]) -> ScenarioDefinition:
    return ScenarioDefinition(
        scenario_id=row["scenario_id"],
        scenario_name=row["scenario_name"],
        scenario_family=row["scenario_family"],
        climate_target_c=_optional_float(row["climate_target_c"]),
        is_active=_as_bool(row["is_active"]),
        model_name=row["model_name"],
        model_version=row["model_version"],
        source_url=row["source_url"],
        source_version=row["source_version"],
        extraction_date=row["extraction_date"],
        geography=row["geography"],
        integration_status=row["integration_status"],
        data_status=row["data_status"],
        source_note=row["source_note"],
    )


def _policy(row: dict[str, str]) -> PolicySupport:
    return PolicySupport(
        country_code=row["country_code"],
        scenario_id=row["scenario_id"],
        technology_id=row["technology_id"],
        capex_subsidy_pct=float(row["capex_subsidy_pct"]),
        ccfd_opex_support_pct=float(row["ccfd_opex_support_pct"]),
        data_status=row["data_status"],
        source_note=row["source_note"],
    )


def _financials(row: dict[str, str]) -> CompanyFinancials:
    return CompanyFinancials(
        company_id=row["company_id"],
        fiscal_year=int(row["fiscal_year"]),
        revenue_bn_krw=float(row["revenue_bn_krw"]),
        ebitda_bn_krw=float(row["ebitda_bn_krw"]),
        annual_capex_bn_krw=float(row["annual_capex_bn_krw"]),
        reporting_currency=row["reporting_currency"],
        fx_to_krw=float(row["fx_to_krw"]),
        data_status=row["data_status"],
        source_note=row["source_note"],
    )


def _plan(row: dict[str, str]) -> Plan:
    return Plan(
        company_id=row["company_id"],
        plan_id=row["plan_id"],
        plan_name=row["plan_name"],
        schedule_shift_years=int(row["schedule_shift_years"]),
        min_h2_capacity_share=float(row["min_h2_capacity_share"]),
        ppa_share=float(row["ppa_share"]),
        hydrogen_contract_share=float(row["hydrogen_contract_share"]),
        fixed_epc_share=float(row["fixed_epc_share"]),
        ccfd_share=float(row["ccfd_share"]),
        contract_premium_pct=float(row["contract_premium_pct"]),
        is_disclosed_plan=_as_bool(row["is_disclosed_plan"]),
        data_status=row["data_status"],
        source_note=row["source_note"],
    )


def _validate_shares(plans: dict[str, Plan]) -> None:
    for plan in plans.values():
        shares = {
            "min_h2_capacity_share": plan.min_h2_capacity_share,
            "ppa_share": plan.ppa_share,
            "hydrogen_contract_share": plan.hydrogen_contract_share,
            "fixed_epc_share": plan.fixed_epc_share,
            "ccfd_share": plan.ccfd_share,
        }
        for name, value in shares.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{plan.company_id}.{plan.plan_id}.{name} must be in [0, 1]")


def _interpolate_scenarios(rows: list[ScenarioPoint]) -> dict[tuple[str, str], tuple[ScenarioPoint, ...]]:
    grouped: dict[tuple[str, str], list[ScenarioPoint]] = {}
    for point in rows:
        grouped.setdefault((point.company_id, point.scenario_id), []).append(point)
    expanded: dict[tuple[str, str], tuple[ScenarioPoint, ...]] = {}
    for key, anchors in grouped.items():
        ordered = sorted(anchors, key=lambda point: point.year)
        if len(ordered) < 2:
            raise ValueError(f"Scenario {key} needs at least two anchor years")
        if len({point.year for point in ordered}) != len(ordered):
            raise ValueError(f"Duplicate scenario anchor year for {key}")
        points: list[ScenarioPoint] = []
        for left, right in zip(ordered, ordered[1:]):
            width = right.year - left.year
            if width <= 0:
                raise ValueError(f"Scenario anchors must increase for {key}")
            for year in range(left.year, right.year):
                share = (year - left.year) / width
                interpolate = lambda a, b: a + share * (b - a)
                points.append(ScenarioPoint(
                    company_id=left.company_id,
                    scenario_id=left.scenario_id,
                    temperature_label=left.temperature_label,
                    year=year,
                    company_carbon_budget_mtco2=left.company_carbon_budget_mtco2,
                    electricity_price_krw_per_kwh=interpolate(
                        left.electricity_price_krw_per_kwh,
                        right.electricity_price_krw_per_kwh,
                    ),
                    carbon_price_krw_per_tco2=interpolate(
                        left.carbon_price_krw_per_tco2,
                        right.carbon_price_krw_per_tco2,
                    ),
                    electrolyzer_capex_index=interpolate(
                        left.electrolyzer_capex_index,
                        right.electrolyzer_capex_index,
                    ),
                    data_status="model_interpolation",
                    source_note=(
                        f"Milestone carbon budget held from {left.year}; market inputs "
                        f"linearly interpolated to {right.year}"
                    ),
                ))
        points.append(ordered[-1])
        expanded[key] = tuple(points)
    return expanded


def _interpolate_resource_constraints(
    rows: list[ResourceConstraintPoint],
) -> dict[tuple[str, str], tuple[ResourceConstraintPoint, ...]]:
    grouped: dict[tuple[str, str], list[ResourceConstraintPoint]] = {}
    for point in rows:
        grouped.setdefault((point.company_id, point.scenario_id), []).append(point)
    expanded: dict[tuple[str, str], tuple[ResourceConstraintPoint, ...]] = {}
    for key, anchors in grouped.items():
        ordered = sorted(anchors, key=lambda point: point.year)
        if len(ordered) < 2 or len({point.year for point in ordered}) != len(ordered):
            raise ValueError(f"Resource constraint {key} needs unique anchor years")
        points: list[ResourceConstraintPoint] = []
        for left, right in zip(ordered, ordered[1:]):
            width = right.year - left.year
            if width <= 0:
                raise ValueError(f"Resource constraint anchors must increase for {key}")
            for year in range(left.year, right.year):
                share = (year - left.year) / width
                blend = lambda a, b: a + share * (b - a)
                points.append(ResourceConstraintPoint(
                    company_id=left.company_id,
                    scenario_id=left.scenario_id,
                    year=year,
                    max_scrap_supply_mt=blend(left.max_scrap_supply_mt, right.max_scrap_supply_mt),
                    max_hydrogen_supply_mt=blend(left.max_hydrogen_supply_mt, right.max_hydrogen_supply_mt),
                    max_incremental_grid_twh=blend(left.max_incremental_grid_twh, right.max_incremental_grid_twh),
                    data_status="model_interpolation",
                    source_url="",
                    source_note=f"Linear interpolation from {left.year} to {right.year}",
                ))
        points.append(ordered[-1])
        expanded[key] = tuple(points)
    return expanded


def _validate_price_process(config: dict[str, object]) -> None:
    factors = config["factors"]
    matrix = config["correlation"]
    if not isinstance(factors, list) or not isinstance(matrix, list):
        raise ValueError("price_process factors and correlation must be lists")
    if len(matrix) != len(factors) or any(len(row) != len(factors) for row in matrix):
        raise ValueError("correlation matrix dimensions do not match factors")
    for index, row in enumerate(matrix):
        if abs(float(row[index]) - 1.0) > 1e-9:
            raise ValueError("correlation matrix diagonal must equal 1")
    recognized_share = float(config["recognized_carbon_cost_share"])
    if not 0.0 <= recognized_share <= 1.0:
        raise ValueError("recognized_carbon_cost_share must be in [0, 1]")


def _validate_scenario_registry(
    companies: dict[str, Company],
    definitions: dict[str, ScenarioDefinition],
    scenario_rows: list[ScenarioPoint],
    policies: dict[tuple[str, str, str], PolicySupport],
) -> None:
    active_ids = {
        scenario_id
        for scenario_id, definition in definitions.items()
        if definition.is_active
    }
    anchor_ids = {point.scenario_id for point in scenario_rows}
    if active_ids != anchor_ids:
        raise ValueError(
            "Active scenario definitions must exactly match scenario_anchors.csv: "
            f"active={sorted(active_ids)}, anchors={sorted(anchor_ids)}"
        )
    for definition in definitions.values():
        if definition.climate_target_c is not None and definition.climate_target_c <= 0:
            raise ValueError(f"{definition.scenario_id} climate_target_c must be positive")
        if not definition.is_active and definition.scenario_id in anchor_ids:
            raise ValueError(f"Inactive scenario {definition.scenario_id} must not have numeric anchors")
        if definition.scenario_family == "gcam_climate" and definition.is_active:
            required = {
                definition.model_version,
                definition.source_version,
                definition.extraction_date,
            }
            if any(not value or value.strip().lower() in {"pending", "tbd"} for value in required):
                raise ValueError(
                    f"Active GCAM scenario {definition.scenario_id} requires pinned model/source versions and extraction date"
                )
            statuses = {
                point.data_status
                for point in scenario_rows
                if point.scenario_id == definition.scenario_id
            }
            if not statuses or any(not status.startswith("gcam_official") for status in statuses):
                raise ValueError(
                    f"Active GCAM scenario {definition.scenario_id} requires gcam_official* anchor statuses"
                )
    for company_id in companies:
        company_ids = {
            point.scenario_id for point in scenario_rows if point.company_id == company_id
        }
        if company_ids != active_ids:
            raise ValueError(
                f"{company_id} scenario coverage mismatch: {sorted(company_ids)} vs {sorted(active_ids)}"
            )
    for point in scenario_rows:
        definition = definitions[point.scenario_id]
        if point.temperature_label != definition.scenario_name:
            raise ValueError(
                f"Scenario label mismatch for {point.company_id}/{point.scenario_id}: "
                f"{point.temperature_label!r} vs {definition.scenario_name!r}"
            )
    required_policy_technologies = {
        "BF_RELINE",
        "SCRAP_EAF",
        "H2_DRI_EAF",
        "EAF_RENEWABLE",
    }
    countries = {company.country_code for company in companies.values()}
    missing = [
        (country, scenario_id, technology_id)
        for country in sorted(countries)
        for scenario_id in sorted(active_ids)
        for technology_id in sorted(required_policy_technologies)
        if (country, scenario_id, technology_id) not in policies
    ]
    if missing:
        raise ValueError(f"Missing policy coverage for active scenarios: {missing}")


def load_data(data_dir: Path | str) -> DataBundle:
    root = Path(data_dir)
    companies = {
        item.company_id: item for item in _read_csv(root / "companies.csv", _company)
    }
    facilities = {item.facility_id: item for item in _read_csv(root / "facilities.csv", _facility)}
    technologies = {
        item.technology_id: item
        for item in _read_csv(root / "technologies.csv", _technology)
    }
    technology_constraints = {
        item.technology_id: item
        for item in _read_csv(
            root / "technology_constraints.csv", _technology_constraint
        )
    }
    company_constraints = {
        item.company_id: item
        for item in _read_csv(root / "company_constraints.csv", _company_constraint)
    }
    resource_constraints = _interpolate_resource_constraints(
        _read_csv(root / "resource_constraints.csv", _resource_constraint)
    )
    resource_benchmarks = tuple(
        _read_csv(root / "resource_benchmarks.csv", _resource_benchmark)
    )
    transition_projects = tuple(
        _read_csv(root / "transition_projects.csv", _transition_project)
    )
    technology_cost_evidence = tuple(
        _read_csv(
            root / "technology_cost_evidence.csv", _technology_cost_evidence
        )
    )
    definition_rows = _read_csv(
        root / "scenario_definitions.csv", _scenario_definition
    )
    scenario_definitions: dict[str, ScenarioDefinition] = {}
    for item in definition_rows:
        if item.scenario_id in scenario_definitions:
            raise ValueError(f"Duplicate scenario definition {item.scenario_id}")
        scenario_definitions[item.scenario_id] = item
    scenario_rows = _read_csv(root / "scenario_anchors.csv", _scenario)
    scenarios_sorted = _interpolate_scenarios(scenario_rows)
    policies = {
        (item.country_code, item.scenario_id, item.technology_id): item
        for item in _read_csv(root / "policy_support.csv", _policy)
    }
    financials = {
        item.company_id: item
        for item in _read_csv(root / "company_financials.csv", _financials)
    }
    plan_rows = _read_csv(root / "plans.csv", _plan)
    plans: dict[tuple[str, str], Plan] = {}
    for item in plan_rows:
        target_companies = companies if item.company_id == "ALL" else (item.company_id,)
        for company_id in target_companies:
            if company_id not in companies:
                raise ValueError(f"Unknown plan company {company_id}")
            expanded = replace(item, company_id=company_id)
            plans[(company_id, expanded.plan_id)] = expanded
    with (root / "price_process.json").open("r", encoding="utf-8") as handle:
        price_process = json.load(handle)

    if not companies or not facilities or not technologies or not scenarios_sorted or not plans:
        raise ValueError("Core data tables must not be empty")
    if "BF_RELINE" not in technologies:
        raise ValueError("technologies.csv must contain BF_RELINE as the counterfactual")
    if set(technology_constraints) != set(technologies):
        raise ValueError("technology_constraints.csv must cover every technology")
    if set(company_constraints) != set(companies):
        raise ValueError("company_constraints.csv must cover every company")
    for constraint in technology_constraints.values():
        if not 0.0 <= constraint.failure_probability <= 1.0:
            raise ValueError(f"{constraint.technology_id} failure_probability must be in [0, 1]")
        if not 0.0 <= constraint.scrap_input_t_per_t <= 1.5:
            raise ValueError(f"{constraint.technology_id} scrap intensity is implausible")
    for company_id in companies:
        disclosed = sum(
            plan.is_disclosed_plan
            for (plan_company_id, _), plan in plans.items()
            if plan_company_id == company_id
        )
        if disclosed != 1:
            raise ValueError(f"{company_id} must have exactly one disclosed-plan proxy")
    for facility in facilities.values():
        if facility.company_id not in companies:
            raise ValueError(f"Unknown company for {facility.facility_id}")
        if facility.baseline_technology_id not in technologies:
            raise ValueError(f"Unknown baseline technology for {facility.facility_id}")
    for scenario_key, points in scenarios_sorted.items():
        years = [point.year for point in points]
        if len(years) != len(set(years)):
            raise ValueError(f"Duplicate year in scenario {scenario_key}")
        if years != list(range(min(years), max(years) + 1)):
            raise ValueError(f"Scenario {scenario_key} must have a continuous annual path")
    for company_id, company in companies.items():
        company_facilities = [f for f in facilities.values() if f.company_id == company_id]
        modeled_output = sum(f.output_mt for f in company_facilities)
        modeled_emissions = sum(
            f.output_mt * f.baseline_emissions_tco2_per_t for f in company_facilities
        )
        if abs(modeled_output - company.production_mt) > 0.02:
            raise ValueError(f"{company_id} facility output does not reconcile to company production")
        if abs(modeled_emissions - company.scope12_emissions_mtco2) > 0.03:
            raise ValueError(f"{company_id} facility emissions do not reconcile to company total")
    _validate_shares(plans)
    _validate_price_process(price_process)
    _validate_scenario_registry(
        companies, scenario_definitions, scenario_rows, policies
    )
    expected_resource_keys = {
        (company_id, scenario_id)
        for company_id in companies
        for scenario_id, definition in scenario_definitions.items()
        if definition.is_active
    }
    if set(resource_constraints) != expected_resource_keys:
        raise ValueError("resource_constraints.csv coverage must match active company-scenarios")
    validate_gcam_manifests(root)
    _validate_resource_benchmarks(resource_benchmarks)
    _validate_transition_evidence(
        transition_projects,
        technology_cost_evidence,
        companies,
        facilities,
        technologies,
    )

    return DataBundle(
        root=root,
        companies=companies,
        facilities=facilities,
        technologies=technologies,
        technology_constraints=technology_constraints,
        company_constraints=company_constraints,
        resource_constraints=resource_constraints,
        resource_benchmarks=resource_benchmarks,
        transition_projects=transition_projects,
        technology_cost_evidence=technology_cost_evidence,
        scenario_definitions=scenario_definitions,
        scenarios=scenarios_sorted,
        policies=policies,
        financials=financials,
        plans=plans,
        price_process=price_process,
    )
