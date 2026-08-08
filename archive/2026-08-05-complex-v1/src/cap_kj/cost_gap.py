"""Facility-to-company annual resource cost-gap screening.

This layer joins transition CAPEX and operational-abatement screens to explicit
annualisation inputs.  Support scenarios are kept separate from the verified
market-policy ledger, whose unavailable values remain NA rather than zero.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

from .model import ModelInputError


D = Decimal
CASES = ("low", "base", "high")
PRIMARY_VARIANT = "primary_current"
MCI_PRIMARY_VARIANT = "primary_mci_shk_bridge"
MCI_LEGACY_VARIANT = "legacy_mci_judgement_sensitivity"

FACILITY_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "facility_id",
    "facility_name",
    "baseline_variant",
    "variant_role",
    "case",
    "baseline_period",
    "baseline_operational_ghg_tco2e",
    "baseline_emissions_value_type",
    "selected_route",
    "decision_horizon",
    "facility_status",
    "modelled_flag",
    "transition_capex_usd_2025",
    "modelled_operational_abatement_tco2e",
    "annual_capital_and_fixed_opex_factor",
    "annualised_capital_and_fixed_opex_usd_2025",
    "incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated",
    "annual_variable_resource_gap_usd_2025",
    "annual_resource_gap_proxy_usd_2025",
    "annual_resource_gap_proxy_usd_2025_per_operational_tco2e_abated",
    "support_stress_low",
    "support_stress_base",
    "support_stress_high",
    "implied_support_low_usd_2025",
    "implied_support_base_usd_2025",
    "implied_support_high_usd_2025",
    "stress_adjusted_gap_low_usd_2025",
    "stress_adjusted_gap_base_usd_2025",
    "stress_adjusted_gap_high_usd_2025",
    "verified_market_policy_status",
    "verified_incentive_adjusted_gap_usd_2025",
    "system_abatement_status",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
    "boundary_note",
)

COMPANY_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "baseline_variant",
    "variant_role",
    "case",
    "official_company_baseline_tco2e",
    "modelled_facility_baseline_tco2e",
    "base_case_emissions_coverage_ratio",
    "base_case_unmodelled_residual_emissions_tco2e",
    "costed_facility_count",
    "transition_capex_usd_2025",
    "modelled_operational_abatement_tco2e",
    "annual_resource_gap_proxy_usd_2025",
    "annual_resource_gap_proxy_usd_2025_per_operational_tco2e_abated",
    "annual_resource_gap_as_share_of_transition_capex",
    "largest_resource_gap_facility_id",
    "largest_resource_gap_facility_share",
    "implied_support_low_usd_2025",
    "implied_support_base_usd_2025",
    "implied_support_high_usd_2025",
    "stress_adjusted_gap_low_usd_2025",
    "stress_adjusted_gap_base_usd_2025",
    "stress_adjusted_gap_high_usd_2025",
    "verified_market_policy_status",
    "verified_incentive_adjusted_gap_usd_2025",
    "system_abatement_status",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "method_note",
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        raise ModelInputError(f"cannot read {path}: {exc}") from exc


def _decimal(raw: str, label: str) -> Decimal:
    try:
        value = D(raw)
    except InvalidOperation as exc:
        raise ModelInputError(f"{label} is not numeric: {raw!r}") from exc
    if not value.is_finite():
        raise ModelInputError(f"{label} must be finite")
    return value


def _join_labels(values: Iterable[str]) -> str:
    labels: set[str] = set()
    for value in values:
        labels.update(part for part in value.split("|") if part and part != "NA")
    return "|".join(sorted(labels))


def _serialise(value: object) -> object:
    if isinstance(value, Decimal):
        rendered = format(value, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return "0" if rendered in {"", "-0"} else rendered
    return value


def _bounded_coverage(modelled_baseline: Decimal, official: Decimal) -> Decimal:
    ratio = modelled_baseline / official
    if ratio > D("1.001"):
        raise ModelInputError(f"base emissions coverage materially exceeds one: {ratio}")
    return min(D("1"), ratio)


def _write_csv(path: Path, rows: list[dict[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _serialise(row[field]) for field in fields})


def _mci_bridge_rows(
    facility_screen: list[dict[str, str]], bridge: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Recalculate the four costed MCI facilities under official-registry shares."""

    bridge_by_facility = {
        row["seed_facility_id"]: row
        for row in bridge
        if row["bridge_scope"] == "mapped_seed"
    }
    current = [
        row
        for row in facility_screen
        if row["company_id"] == "MITSUI_CHEMICALS" and row["modelled_flag"] == "yes"
    ]
    if len(current) != 4 * 3:
        raise ModelInputError("expected four modelled Mitsui facilities across three cases")
    result: list[dict[str, str]] = []
    for original in current:
        if original["facility_id"] not in bridge_by_facility:
            raise ModelInputError(f"Mitsui bridge missing {original['facility_id']}")
        if original["capex_driver"] != "abatement":
            raise ModelInputError("Mitsui SHK sensitivity requires abatement-driven CAPEX")
        case = original["case"]
        bridge_row = bridge_by_facility[original["facility_id"]]
        baseline = _decimal(bridge_row[f"allocated_{case}_tco2e"], "Mitsui bridge emissions")
        abatement_fraction = _decimal(original["abatement_fraction"], "abatement fraction")
        abatement = baseline * abatement_fraction
        capex = abatement * _decimal(original["capex_intensity"], "CAPEX intensity")
        row = dict(original)
        row.update(
            {
                "baseline_period": bridge_row["allocation_target_period"],
                "baseline_emissions_value_type": bridge_row["allocated_value_type"],
                "baseline_operational_ghg_tco2e": str(baseline),
                "transition_operational_ghg_tco2e": str(baseline - abatement),
                "modelled_operational_abatement_tco2e": str(abatement),
                "transition_capex_usd_2025": str(capex),
                "capex_by_2030_usd_2025": str(capex if original["decision_horizon"] == "2030" else D("0")),
                "capex_2031_2040_usd_2025": str(capex if original["decision_horizon"] == "2040" else D("0")),
                "capex_2041_2050_usd_2025": str(capex if original["decision_horizon"] == "2050" else D("0")),
                "quality_flag": "D",
                "source_id": _join_labels((original["source_id"], bridge_row["source_id"])),
                "formula_or_method": (
                    "Mitsui FY2024 parent emissions allocated by FY2023 official SHK site share; "
                    "route abatement and abatement-driven CAPEX then recalculated for the same case"
                ),
                "boundary_note": (
                    "Primary Mitsui sensitivity uses time-bridged official-registry shares, not reported "
                    "FY2024 facility emissions; system abatement remains unmodelled."
                ),
            }
        )
        result.append(row)
    return result


def _cost_one(
    screen: dict[str, str], cost_input: dict[str, str], baseline_variant: str, variant_role: str
) -> dict[str, object]:
    modelled = screen["modelled_flag"] == "yes"
    common: dict[str, object] = {
        "company_id": screen["company_id"],
        "company_name": screen["company_name"],
        "country": screen["country"],
        "sector": screen["sector"],
        "facility_id": screen["facility_id"],
        "facility_name": screen["facility_name"],
        "baseline_variant": baseline_variant,
        "variant_role": variant_role,
        "case": screen["case"],
        "baseline_period": screen["baseline_period"],
        "baseline_operational_ghg_tco2e": _decimal(
            screen["baseline_operational_ghg_tco2e"], "baseline emissions"
        ),
        "baseline_emissions_value_type": screen["baseline_emissions_value_type"],
        "selected_route": screen["selected_route"],
        "decision_horizon": screen["decision_horizon"],
        "facility_status": screen["facility_status"],
        "modelled_flag": screen["modelled_flag"],
        "system_abatement_status": screen["system_abatement_status"],
        "currency": "USD",
        "price_year": "2025 screening proxy",
        "source_id": screen["source_id"],
    }
    if not modelled:
        common.update(
            {
                field: "NA"
                for field in (
                    "transition_capex_usd_2025",
                    "modelled_operational_abatement_tco2e",
                    "annual_capital_and_fixed_opex_factor",
                    "annualised_capital_and_fixed_opex_usd_2025",
                    "incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated",
                    "annual_variable_resource_gap_usd_2025",
                    "annual_resource_gap_proxy_usd_2025",
                    "annual_resource_gap_proxy_usd_2025_per_operational_tco2e_abated",
                    "support_stress_low",
                    "support_stress_base",
                    "support_stress_high",
                    "implied_support_low_usd_2025",
                    "implied_support_base_usd_2025",
                    "implied_support_high_usd_2025",
                    "stress_adjusted_gap_low_usd_2025",
                    "stress_adjusted_gap_base_usd_2025",
                    "stress_adjusted_gap_high_usd_2025",
                )
            }
        )
        common.update(
            {
                "verified_market_policy_status": "not_applicable_unmodelled_route",
                "verified_incentive_adjusted_gap_usd_2025": "NA",
                "value_type": "Not_modelled",
                "quality_flag": screen["quality_flag"],
                "formula_or_method": "No route cost applied to explicit unmodelled residual",
                "boundary_note": "Unmodelled emissions are not assigned a zero cost gap.",
            }
        )
        return common

    capex = _decimal(screen["transition_capex_usd_2025"], "transition CAPEX")
    abatement = _decimal(
        screen["modelled_operational_abatement_tco2e"], "operational abatement"
    )
    if abatement <= 0:
        raise ModelInputError(f"modelled facility has no abatement: {screen['facility_id']}")
    annual_factor = _decimal(cost_input["annual_capital_and_fixed_opex_factor"], "annual factor")
    variable_unit = _decimal(
        cost_input[
            "incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated"
        ],
        "variable resource cost",
    )
    capital_fixed = capex * annual_factor
    variable = abatement * variable_unit
    resource_gap = capital_fixed + variable

    support_shares = {
        case: _decimal(cost_input[f"support_stress_{case}"], "support stress")
        for case in CASES
    }
    positive_gap = max(D("0"), resource_gap)
    support_amounts = {case: positive_gap * share for case, share in support_shares.items()}
    adjusted = {case: resource_gap - support_amounts[case] for case in CASES}
    common.update(
        {
            "transition_capex_usd_2025": capex,
            "modelled_operational_abatement_tco2e": abatement,
            "annual_capital_and_fixed_opex_factor": annual_factor,
            "annualised_capital_and_fixed_opex_usd_2025": capital_fixed,
            "incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated": variable_unit,
            "annual_variable_resource_gap_usd_2025": variable,
            "annual_resource_gap_proxy_usd_2025": resource_gap,
            "annual_resource_gap_proxy_usd_2025_per_operational_tco2e_abated": resource_gap / abatement,
            "support_stress_low": support_shares["low"],
            "support_stress_base": support_shares["base"],
            "support_stress_high": support_shares["high"],
            "implied_support_low_usd_2025": support_amounts["low"],
            "implied_support_base_usd_2025": support_amounts["base"],
            "implied_support_high_usd_2025": support_amounts["high"],
            "stress_adjusted_gap_low_usd_2025": adjusted["low"],
            "stress_adjusted_gap_base_usd_2025": adjusted["base"],
            "stress_adjusted_gap_high_usd_2025": adjusted["high"],
            "verified_market_policy_status": cost_input["verified_market_policy_status"],
            "verified_incentive_adjusted_gap_usd_2025": "NA",
            "value_type": "Modelled_from_estimated_inputs",
            "quality_flag": "D",
            "source_id": _join_labels((screen["source_id"], "annual_cost_gap_assumptions_mvp")),
            "formula_or_method": (
                "resource gap proxy = transition CAPEX * annual capital-and-fixed-OPEX factor "
                "+ modelled operational abatement * variable-resource proxy; independent support axes "
                "apply only to a positive gap"
            ),
            "boundary_note": (
                "Incremental annual resource proxy only; incumbent cost and early retirement are absent. "
                "Support outputs are stresses, not verified cash; verified net gap remains NA."
            ),
        }
    )
    return common


def build_cost_gap_tables(
    facility_screen: list[dict[str, str]],
    company_screen: list[dict[str, str]],
    route_cost_inputs: list[dict[str, str]],
    mci_bridge: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Build facility and company cost-gap tables plus the Mitsui bridge sensitivity."""

    cost_by_route_case = {
        (row["route_id"], row["case"]): row for row in route_cost_inputs
    }
    if len(cost_by_route_case) != len(route_cost_inputs):
        raise ModelInputError("duplicate route/case cost input")
    company_screen_by_key = {
        (row["company_id"], row["case"]): row for row in company_screen
    }

    tagged: list[tuple[dict[str, str], str, str]] = []
    for row in facility_screen:
        if row["company_id"] == "MITSUI_CHEMICALS":
            tagged.append((row, MCI_LEGACY_VARIANT, "sensitivity"))
        else:
            tagged.append((row, PRIMARY_VARIANT, "primary"))
    tagged.extend(
        (row, MCI_PRIMARY_VARIANT, "primary")
        for row in _mci_bridge_rows(facility_screen, mci_bridge)
    )

    facility_results: list[dict[str, object]] = []
    for row, baseline_variant, variant_role in tagged:
        key = (row["selected_route"], row["case"])
        if row["modelled_flag"] == "yes" and key not in cost_by_route_case:
            raise ModelInputError(f"missing cost input for route/case {key}")
        cost_input = cost_by_route_case.get(key, {})
        facility_results.append(_cost_one(row, cost_input, baseline_variant, variant_role))

    company_results: list[dict[str, object]] = []
    groups = sorted(
        {
            (str(row["company_id"]), str(row["baseline_variant"]), str(row["case"]))
            for row in facility_results
        }
    )
    base_boundary: dict[tuple[str, str], Decimal] = {}
    for company_id, baseline_variant, _ in groups:
        key = (company_id, baseline_variant)
        if key in base_boundary:
            continue
        base_boundary[key] = sum(
            (
                _decimal(str(row["baseline_operational_ghg_tco2e"]), "base modelled baseline")
                for row in facility_results
                if row["company_id"] == company_id
                and row["baseline_variant"] == baseline_variant
                and row["case"] == "base"
                and row["modelled_flag"] == "yes"
            ),
            start=D("0"),
        )
    for company_id, baseline_variant, case in groups:
        rows = [
            row
            for row in facility_results
            if row["company_id"] == company_id
            and row["baseline_variant"] == baseline_variant
            and row["case"] == case
        ]
        modelled = [row for row in rows if row["modelled_flag"] == "yes"]
        if not modelled:
            raise ModelInputError(f"no modelled facilities for {company_id}/{baseline_variant}/{case}")
        screen_company = company_screen_by_key[(company_id, case)]
        official = _decimal(screen_company["official_company_baseline_tco2e"], "official baseline")
        base_modelled_baseline = base_boundary[(company_id, baseline_variant)]
        modelled_baseline = sum(
            (_decimal(str(row["baseline_operational_ghg_tco2e"]), "modelled baseline") for row in modelled),
            start=D("0"),
        )
        capex = sum(
            (_decimal(str(row["transition_capex_usd_2025"]), "CAPEX") for row in modelled),
            start=D("0"),
        )
        abatement = sum(
            (_decimal(str(row["modelled_operational_abatement_tco2e"]), "abatement") for row in modelled),
            start=D("0"),
        )
        resource_gap = sum(
            (_decimal(str(row["annual_resource_gap_proxy_usd_2025"]), "resource gap") for row in modelled),
            start=D("0"),
        )
        support = {
            support_case: sum(
                (
                    _decimal(str(row[f"implied_support_{support_case}_usd_2025"]), "support")
                    for row in modelled
                ),
                start=D("0"),
            )
            for support_case in CASES
        }
        adjusted = {support_case: resource_gap - support[support_case] for support_case in CASES}
        largest = max(modelled, key=lambda row: _decimal(str(row["annual_resource_gap_proxy_usd_2025"]), "resource gap"))
        largest_gap = _decimal(str(largest["annual_resource_gap_proxy_usd_2025"]), "resource gap")
        company_results.append(
            {
                "company_id": company_id,
                "company_name": rows[0]["company_name"],
                "country": rows[0]["country"],
                "sector": rows[0]["sector"],
                "baseline_variant": baseline_variant,
                "variant_role": rows[0]["variant_role"],
                "case": case,
                "official_company_baseline_tco2e": official,
                "modelled_facility_baseline_tco2e": modelled_baseline,
                "base_case_emissions_coverage_ratio": _bounded_coverage(
                    base_modelled_baseline, official
                ),
                "base_case_unmodelled_residual_emissions_tco2e": max(
                    D("0"), official - base_modelled_baseline
                ),
                "costed_facility_count": len(modelled),
                "transition_capex_usd_2025": capex,
                "modelled_operational_abatement_tco2e": abatement,
                "annual_resource_gap_proxy_usd_2025": resource_gap,
                "annual_resource_gap_proxy_usd_2025_per_operational_tco2e_abated": resource_gap / abatement,
                "annual_resource_gap_as_share_of_transition_capex": resource_gap / capex,
                "largest_resource_gap_facility_id": largest["facility_id"],
                "largest_resource_gap_facility_share": largest_gap / resource_gap,
                "implied_support_low_usd_2025": support["low"],
                "implied_support_base_usd_2025": support["base"],
                "implied_support_high_usd_2025": support["high"],
                "stress_adjusted_gap_low_usd_2025": adjusted["low"],
                "stress_adjusted_gap_base_usd_2025": adjusted["base"],
                "stress_adjusted_gap_high_usd_2025": adjusted["high"],
                "verified_market_policy_status": "not_available_not_zero",
                "verified_incentive_adjusted_gap_usd_2025": "NA",
                "system_abatement_status": "not_modelled; leakage and replacement production pending",
                "currency": "USD",
                "price_year": "2025 screening proxy",
                "value_type": "Modelled_from_estimated_inputs",
                "quality_flag": "D",
                "source_id": _join_labels(str(row["source_id"]) for row in modelled),
                "method_note": (
                    "Facility resource-gap proxies summed to company; coverage uses modelled facility "
                    "baseline over the official company anchor. Support stresses are independent and "
                    "verified incentive-adjusted gap remains NA."
                ),
            }
        )
    return facility_results, company_results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build facility/company annual cost-gap tables")
    parser.add_argument("--facility-screen", type=Path, required=True)
    parser.add_argument("--company-screen", type=Path, required=True)
    parser.add_argument("--route-cost-inputs", type=Path, required=True)
    parser.add_argument("--mci-bridge", type=Path, required=True)
    parser.add_argument("--facility-output", type=Path, required=True)
    parser.add_argument("--company-output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        facilities, companies = build_cost_gap_tables(
            _read_csv(args.facility_screen),
            _read_csv(args.company_screen),
            _read_csv(args.route_cost_inputs),
            _read_csv(args.mci_bridge),
        )
        _write_csv(args.facility_output, facilities, FACILITY_FIELDS)
        _write_csv(args.company_output, companies, COMPANY_FIELDS)
    except ModelInputError as exc:
        print(f"cap-kj cost-gap: error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
