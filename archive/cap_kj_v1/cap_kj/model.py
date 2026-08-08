"""Core facility cost-gap calculations and company aggregation.

The model deliberately keeps early-retirement exposure outside both cost-gap
ledgers. It is reported alongside them so that users may analyse it without
silently treating an engineering exposure as an operating cost or impairment.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal


ZERO = Decimal("0")


class ModelInputError(ValueError):
    """Raised when model input would make the calculation ambiguous."""


@dataclass(frozen=True)
class FacilityInput:
    """One selected incumbent-to-transition comparison for a facility-year."""

    company_id: str
    facility_id: str
    analysis_year: str
    scenario: str
    sector: str
    route_id: str
    currency: str
    output_unit: str
    annual_output_quantity: Decimal
    incumbent_capex: Decimal
    incumbent_lifetime_years: int
    incumbent_discount_rate: Decimal
    incumbent_feedstock_cost_per_output: Decimal
    incumbent_energy_cost_per_output: Decimal
    incumbent_om_cost_per_output: Decimal
    incumbent_transport_storage_cost_per_output: Decimal
    incumbent_decommissioning_cost_per_output: Decimal
    transition_capex: Decimal
    transition_lifetime_years: int
    transition_discount_rate: Decimal
    transition_feedstock_cost_per_output: Decimal
    transition_energy_cost_per_output: Decimal
    transition_om_cost_per_output: Decimal
    transition_transport_storage_cost_per_output: Decimal
    transition_decommissioning_cost_per_output: Decimal
    avoided_actual_carbon_cost_per_output: Decimal
    realised_green_premium_per_output: Decimal
    verified_support_per_output: Decimal
    incumbent_emissions_tco2e: Decimal
    transition_emissions_tco2e: Decimal
    early_retirement_exposure: Decimal
    value_type: str
    quality_flag: str
    source_id: str

    def __post_init__(self) -> None:
        identity = {
            "company_id": self.company_id,
            "facility_id": self.facility_id,
            "analysis_year": self.analysis_year,
            "scenario": self.scenario,
            "sector": self.sector,
            "route_id": self.route_id,
            "currency": self.currency,
            "output_unit": self.output_unit,
            "value_type": self.value_type,
            "quality_flag": self.quality_flag,
            "source_id": self.source_id,
        }
        empty_fields = [name for name, value in identity.items() if not value.strip()]
        if empty_fields:
            raise ModelInputError(
                "required text fields are empty: " + ", ".join(empty_fields)
            )
        if self.annual_output_quantity <= ZERO:
            raise ModelInputError("annual_output_quantity must be greater than zero")
        if self.incumbent_lifetime_years <= 0:
            raise ModelInputError("incumbent_lifetime_years must be greater than zero")
        if self.transition_lifetime_years <= 0:
            raise ModelInputError("transition_lifetime_years must be greater than zero")
        if self.incumbent_discount_rate < ZERO:
            raise ModelInputError("incumbent_discount_rate cannot be negative")
        if self.transition_discount_rate < ZERO:
            raise ModelInputError("transition_discount_rate cannot be negative")


@dataclass(frozen=True)
class FacilityResult:
    company_id: str
    facility_id: str
    analysis_year: str
    scenario: str
    sector: str
    route_id: str
    currency: str
    output_unit: str
    annual_output_quantity: Decimal
    incumbent_annualised_capex_per_output: Decimal
    transition_annualised_capex_per_output: Decimal
    incumbent_resource_cost_per_output: Decimal
    transition_resource_cost_per_output: Decimal
    resource_cost_gap_per_output: Decimal
    avoided_actual_carbon_cost_per_output: Decimal
    realised_green_premium_per_output: Decimal
    verified_support_per_output: Decimal
    incentive_adjusted_gap_per_output: Decimal
    annual_resource_cost_gap: Decimal
    annual_incentive_adjusted_gap: Decimal
    transition_capex: Decimal
    incumbent_emissions_tco2e: Decimal
    transition_emissions_tco2e: Decimal
    modelled_abatement_tco2e: Decimal
    early_retirement_exposure: Decimal
    value_type: str
    quality_flag: str
    source_id: str


@dataclass(frozen=True)
class CompanyResult:
    company_id: str
    analysis_year: str
    scenario: str
    sector: str
    currency: str
    output_unit: str
    facility_count: int
    annual_output_quantity: Decimal
    transition_capex: Decimal
    annual_resource_cost_gap: Decimal
    annual_incentive_adjusted_gap: Decimal
    resource_cost_gap_per_output: Decimal
    incentive_adjusted_gap_per_output: Decimal
    incumbent_emissions_tco2e: Decimal
    transition_emissions_tco2e: Decimal
    modelled_abatement_tco2e: Decimal
    modelled_abatement_per_capex: Decimal | None
    annual_resource_cost_per_tco2e_abated: Decimal | None
    annual_incentive_adjusted_cost_per_tco2e_abated: Decimal | None
    early_retirement_exposure: Decimal
    value_type: str
    quality_flag: str
    source_id: str


def capital_recovery_factor(discount_rate: Decimal, lifetime_years: int) -> Decimal:
    """Return the annual capital recovery factor for a rate and lifetime."""

    if lifetime_years <= 0:
        raise ModelInputError("lifetime_years must be greater than zero")
    if discount_rate < ZERO:
        raise ModelInputError("discount_rate cannot be negative")
    if discount_rate == ZERO:
        return Decimal(1) / Decimal(lifetime_years)
    growth = (Decimal(1) + discount_rate) ** lifetime_years
    return discount_rate * growth / (growth - Decimal(1))


def calculate_facility(record: FacilityInput) -> FacilityResult:
    """Calculate annualised facility costs, gaps, and modelled abatement."""

    incumbent_annualised_capex = (
        capital_recovery_factor(
            record.incumbent_discount_rate, record.incumbent_lifetime_years
        )
        * record.incumbent_capex
        / record.annual_output_quantity
    )
    transition_annualised_capex = (
        capital_recovery_factor(
            record.transition_discount_rate, record.transition_lifetime_years
        )
        * record.transition_capex
        / record.annual_output_quantity
    )

    incumbent_resource_cost = sum(
        (
            incumbent_annualised_capex,
            record.incumbent_feedstock_cost_per_output,
            record.incumbent_energy_cost_per_output,
            record.incumbent_om_cost_per_output,
            record.incumbent_transport_storage_cost_per_output,
            record.incumbent_decommissioning_cost_per_output,
        ),
        start=ZERO,
    )
    transition_resource_cost = sum(
        (
            transition_annualised_capex,
            record.transition_feedstock_cost_per_output,
            record.transition_energy_cost_per_output,
            record.transition_om_cost_per_output,
            record.transition_transport_storage_cost_per_output,
            record.transition_decommissioning_cost_per_output,
        ),
        start=ZERO,
    )
    resource_gap = transition_resource_cost - incumbent_resource_cost
    incentive_adjusted_gap = resource_gap - sum(
        (
            record.avoided_actual_carbon_cost_per_output,
            record.realised_green_premium_per_output,
            record.verified_support_per_output,
        ),
        start=ZERO,
    )

    return FacilityResult(
        company_id=record.company_id,
        facility_id=record.facility_id,
        analysis_year=record.analysis_year,
        scenario=record.scenario,
        sector=record.sector,
        route_id=record.route_id,
        currency=record.currency,
        output_unit=record.output_unit,
        annual_output_quantity=record.annual_output_quantity,
        incumbent_annualised_capex_per_output=incumbent_annualised_capex,
        transition_annualised_capex_per_output=transition_annualised_capex,
        incumbent_resource_cost_per_output=incumbent_resource_cost,
        transition_resource_cost_per_output=transition_resource_cost,
        resource_cost_gap_per_output=resource_gap,
        avoided_actual_carbon_cost_per_output=(
            record.avoided_actual_carbon_cost_per_output
        ),
        realised_green_premium_per_output=record.realised_green_premium_per_output,
        verified_support_per_output=record.verified_support_per_output,
        incentive_adjusted_gap_per_output=incentive_adjusted_gap,
        annual_resource_cost_gap=resource_gap * record.annual_output_quantity,
        annual_incentive_adjusted_gap=(
            incentive_adjusted_gap * record.annual_output_quantity
        ),
        transition_capex=record.transition_capex,
        incumbent_emissions_tco2e=record.incumbent_emissions_tco2e,
        transition_emissions_tco2e=record.transition_emissions_tco2e,
        modelled_abatement_tco2e=(
            record.incumbent_emissions_tco2e - record.transition_emissions_tco2e
        ),
        early_retirement_exposure=record.early_retirement_exposure,
        value_type=record.value_type,
        quality_flag=record.quality_flag,
        source_id=record.source_id,
    )


def _joined_unique(values: Iterable[str]) -> str:
    """Keep every distinct provenance label in a deterministic form."""

    return "|".join(sorted(set(values)))


def aggregate_company_results(
    facility_results: Iterable[FacilityResult],
) -> list[CompanyResult]:
    """Aggregate compatible facility results to company headline metrics.

    Currency and physical output units form part of the aggregation key, which
    prevents silent addition of incomparable monetary or production values.
    """

    groups: dict[tuple[str, ...], list[FacilityResult]] = {}
    seen: set[tuple[str, str, str, str]] = set()
    for result in facility_results:
        unique_key = (
            result.company_id,
            result.facility_id,
            result.analysis_year,
            result.scenario,
        )
        if unique_key in seen:
            raise ModelInputError(
                "duplicate facility-year-scenario result: " + "/".join(unique_key)
            )
        seen.add(unique_key)
        group_key = (
            result.company_id,
            result.analysis_year,
            result.scenario,
            result.sector,
            result.currency,
            result.output_unit,
        )
        groups.setdefault(group_key, []).append(result)

    company_results: list[CompanyResult] = []
    for group_key in sorted(groups):
        members = groups[group_key]
        output = sum((item.annual_output_quantity for item in members), start=ZERO)
        capex = sum((item.transition_capex for item in members), start=ZERO)
        resource_gap = sum((item.annual_resource_cost_gap for item in members), start=ZERO)
        net_gap = sum(
            (item.annual_incentive_adjusted_gap for item in members), start=ZERO
        )
        incumbent_emissions = sum(
            (item.incumbent_emissions_tco2e for item in members), start=ZERO
        )
        transition_emissions = sum(
            (item.transition_emissions_tco2e for item in members), start=ZERO
        )
        abatement = sum(
            (item.modelled_abatement_tco2e for item in members), start=ZERO
        )
        early_retirement = sum(
            (item.early_retirement_exposure for item in members), start=ZERO
        )
        company_results.append(
            CompanyResult(
                company_id=group_key[0],
                analysis_year=group_key[1],
                scenario=group_key[2],
                sector=group_key[3],
                currency=group_key[4],
                output_unit=group_key[5],
                facility_count=len(members),
                annual_output_quantity=output,
                transition_capex=capex,
                annual_resource_cost_gap=resource_gap,
                annual_incentive_adjusted_gap=net_gap,
                resource_cost_gap_per_output=resource_gap / output,
                incentive_adjusted_gap_per_output=net_gap / output,
                incumbent_emissions_tco2e=incumbent_emissions,
                transition_emissions_tco2e=transition_emissions,
                modelled_abatement_tco2e=abatement,
                modelled_abatement_per_capex=(
                    abatement / capex if capex != ZERO else None
                ),
                annual_resource_cost_per_tco2e_abated=(
                    resource_gap / abatement if abatement != ZERO else None
                ),
                annual_incentive_adjusted_cost_per_tco2e_abated=(
                    net_gap / abatement if abatement != ZERO else None
                ),
                early_retirement_exposure=early_retirement,
                value_type=_joined_unique(item.value_type for item in members),
                quality_flag=_joined_unique(item.quality_flag for item in members),
                source_id=_joined_unique(item.source_id for item in members),
            )
        )
    return company_results

