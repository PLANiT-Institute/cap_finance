from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Company:
    company_id: str
    company_name: str
    country_code: str
    country_name: str
    base_year: int
    reporting_boundary: str
    production_mt: float
    scope12_emissions_mtco2: float
    reported_intensity_tco2_per_t: float
    capacity_mtpa: float
    target_2030_mtco2: float
    target_2040_mtco2: float
    reporting_currency: str
    fx_to_krw: float
    capex_cost_index: float
    data_status: str
    source_name: str
    source_url: str
    source_note: str


@dataclass(frozen=True)
class Facility:
    facility_id: str
    company_id: str
    facility_name: str
    region: str
    capacity_mtpa: float
    utilization_rate: float
    baseline_technology_id: str
    baseline_emissions_tco2_per_t: float
    baseline_electricity_mwh_per_t: float
    baseline_fixed_opex_kkrw_per_t: float
    commission_year: int
    reinvestment_year: int
    data_status: str
    source_note: str

    @property
    def output_mt(self) -> float:
        return self.capacity_mtpa * self.utilization_rate


@dataclass(frozen=True)
class Technology:
    technology_id: str
    technology_name: str
    capex_bn_krw_per_mtpa: float
    fixed_opex_kkrw_per_t: float
    electricity_mwh_per_t: float
    hydrogen_t_per_t: float
    emissions_tco2_per_t: float
    available_year: int
    construction_years: int
    lifetime_years: int
    data_status: str
    source_note: str


@dataclass(frozen=True)
class TechnologyConstraint:
    technology_id: str
    scrap_input_t_per_t: float
    failure_probability: float
    max_failure_delay_years: int
    data_status: str
    source_url: str
    source_note: str


@dataclass(frozen=True)
class CompanyConstraint:
    company_id: str
    max_concurrent_construction_projects: int
    max_portfolio_failure_probability: float
    data_status: str
    source_url: str
    source_note: str


@dataclass(frozen=True)
class ResourceConstraintPoint:
    company_id: str
    scenario_id: str
    year: int
    max_scrap_supply_mt: float
    max_hydrogen_supply_mt: float
    max_incremental_grid_twh: float
    data_status: str
    source_url: str
    source_note: str


@dataclass(frozen=True)
class ResourceBenchmark:
    benchmark_id: str
    country_code: str
    resource_type: str
    benchmark_year: int
    benchmark_value: float | None
    unit: str
    geography: str
    scope: str
    source_org: str
    source_title: str
    source_url: str
    source_version: str
    extraction_date: str
    data_status: str
    comparability: str
    source_note: str


@dataclass(frozen=True)
class TransitionProject:
    project_id: str
    company_id: str
    related_facility_ids: str
    model_mapping_status: str
    project_name: str
    country_code: str
    project_status: str
    decision_stage: str
    announcement_date: str
    construction_start_date: str
    operation_start_year: int | None
    operation_start_label: str
    technology_id: str
    capacity_mtpa: float | None
    capex_native_bn: float | None
    capex_currency: str
    fx_to_krw: float | None
    capex_bn_krw: float | None
    government_support_native_bn: float | None
    government_support_pct: float | None
    disclosed_reduction_pct: float | None
    avoided_emissions_mtco2_pa: float | None
    scrap_share: float | None
    hbi_share: float | None
    data_status: str
    confidence_grade: str
    source_title: str
    source_url: str
    source_version: str
    extraction_date: str
    scope_note: str


@dataclass(frozen=True)
class TechnologyCostEvidence:
    evidence_id: str
    project_id: str
    company_id: str
    technology_id: str
    evidence_scope: str
    capacity_mtpa: float
    capex_native_bn: float
    capex_currency: str
    fx_to_krw: float
    capex_bn_krw: float
    normalized_capex_bn_krw_per_mtpa: float
    government_support_bn_krw: float | None
    gross_or_net: str
    included_assets: str
    comparability: str
    data_status: str
    confidence_grade: str
    source_url: str
    extraction_date: str
    calculation_note: str


@dataclass(frozen=True)
class ScenarioPoint:
    company_id: str
    scenario_id: str
    temperature_label: str
    year: int
    company_carbon_budget_mtco2: float
    electricity_price_krw_per_kwh: float
    carbon_price_krw_per_tco2: float
    electrolyzer_capex_index: float
    data_status: str
    source_note: str


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    scenario_name: str
    scenario_family: str
    climate_target_c: float | None
    is_active: bool
    model_name: str
    model_version: str
    source_url: str
    source_version: str
    extraction_date: str
    geography: str
    integration_status: str
    data_status: str
    source_note: str


@dataclass(frozen=True)
class PolicySupport:
    country_code: str
    scenario_id: str
    technology_id: str
    capex_subsidy_pct: float
    ccfd_opex_support_pct: float
    data_status: str
    source_note: str


@dataclass(frozen=True)
class CompanyFinancials:
    company_id: str
    fiscal_year: int
    revenue_bn_krw: float
    ebitda_bn_krw: float
    annual_capex_bn_krw: float
    reporting_currency: str
    fx_to_krw: float
    data_status: str
    source_note: str


@dataclass(frozen=True)
class Plan:
    company_id: str
    plan_id: str
    plan_name: str
    schedule_shift_years: int
    min_h2_capacity_share: float
    ppa_share: float
    hydrogen_contract_share: float
    fixed_epc_share: float
    ccfd_share: float
    contract_premium_pct: float
    is_disclosed_plan: bool
    data_status: str
    source_note: str


@dataclass(frozen=True)
class TransitionAction:
    facility_id: str
    technology_id: str
    transition_year: int


@dataclass(frozen=True)
class Schedule:
    company_id: str
    scenario_id: str
    plan_id: str
    actions: tuple[TransitionAction, ...]
    deterministic_net_cost_bn_krw: float
    cumulative_avoided_emissions_mtco2: float


@dataclass(frozen=True)
class MarketState:
    electricity_price_krw_per_kwh: float
    hydrogen_price_krw_per_kg: float
    construction_capex_multiplier: float


@dataclass(frozen=True)
class CostResult:
    gross_cost_bn_krw: float
    net_cost_bn_krw: float
    cash_cost_before_support_bn_krw: float
    net_cash_cost_after_support_bn_krw: float
    avoided_carbon_cost_value_bn_krw: float
    policy_support_bn_krw: float
    avoided_emissions_mtco2: float
    capex_cost_bn_krw: float
    fixed_opex_cost_bn_krw: float
    electricity_cost_bn_krw: float
    hydrogen_cost_bn_krw: float
    contract_premium_bn_krw: float
    carbon_value_bn_krw: float


@dataclass(frozen=True)
class DataBundle:
    root: Path
    companies: dict[str, Company]
    facilities: dict[str, Facility]
    technologies: dict[str, Technology]
    technology_constraints: dict[str, TechnologyConstraint]
    company_constraints: dict[str, CompanyConstraint]
    resource_constraints: dict[tuple[str, str], tuple[ResourceConstraintPoint, ...]]
    resource_benchmarks: tuple[ResourceBenchmark, ...]
    transition_projects: tuple[TransitionProject, ...]
    technology_cost_evidence: tuple[TechnologyCostEvidence, ...]
    scenario_definitions: dict[str, ScenarioDefinition]
    scenarios: dict[tuple[str, str], tuple[ScenarioPoint, ...]]
    policies: dict[tuple[str, str, str], PolicySupport]
    financials: dict[str, CompanyFinancials]
    plans: dict[tuple[str, str], Plan]
    price_process: dict[str, Any]
