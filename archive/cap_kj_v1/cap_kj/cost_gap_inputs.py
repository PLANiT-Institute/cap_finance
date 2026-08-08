"""Validate and summarise annual cost-gap proxy assumptions.

The resource ledger is calculable from explicit screening estimates.  The
verified market-policy ledger remains unavailable until facility-specific cash
effects are observed, so this module never converts missing incentives to zero.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from .model import ModelInputError, capital_recovery_factor


D = Decimal
CASES = ("low", "base", "high")
REQUIRED_RESOURCE_PARAMETERS = {
    "transition_lifetime_years",
    "real_discount_rate",
    "incremental_fixed_opex_fraction_of_transition_capex",
    "incremental_variable_resource_cost_per_operational_tco2e_abated",
}
REQUIRED_VERIFIED_PARAMETERS = {
    "verified_avoided_actual_carbon_cost_per_operational_tco2e_abated",
    "verified_realised_green_premium_per_operational_tco2e_abated",
    "verified_support_per_operational_tco2e_abated",
}
SUPPORT_STRESS_PARAMETER = "support_stress_share_of_annual_resource_gap"

SUMMARY_FIELDS = (
    "sector",
    "route_id",
    "case",
    "transition_lifetime_years",
    "real_discount_rate",
    "capital_recovery_factor",
    "incremental_fixed_opex_fraction_of_transition_capex",
    "annual_capital_and_fixed_opex_factor",
    "incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated",
    "resource_gap_formula",
    "verified_market_policy_status",
    "support_stress_low",
    "support_stress_base",
    "support_stress_high",
    "support_stress_case_orientation",
    "stress_adjusted_gap_formula",
    "value_type",
    "quality_flag",
    "boundary_note",
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


def _serialise(value: object) -> object:
    if isinstance(value, Decimal):
        rendered = format(value, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return "0" if rendered in {"", "-0"} else rendered
    return value


def validate_assumptions(rows: list[dict[str, str]]) -> None:
    """Reject ambiguous ranges, zero-filled market-policy gaps, and route gaps."""

    if not rows:
        raise ModelInputError("cost-gap assumption table is empty")
    ids = [row["assumption_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ModelInputError("cost-gap assumption_id must be unique")

    by_route: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_route.setdefault(row["route_id"], {})[row["parameter_name"]] = row
        if not row["formula_or_method"] or not row["rationale"] or not row["boundary_note"]:
            raise ModelInputError(f"missing audit metadata for {row['assumption_id']}")
        if not row["unit"] or not row["price_year"] or not row["quality_flag"]:
            raise ModelInputError(f"missing unit/price year/quality for {row['assumption_id']}")

        values = [row[case] for case in CASES]
        if row["value_type"] == "Estimated":
            if any(value == "NA" or value == "" for value in values):
                raise ModelInputError(f"estimate lacks low/base/high for {row['assumption_id']}")
            parsed = [_decimal(value, row["assumption_id"]) for value in values]
            if row["case_orientation"] == "independent_support_axis":
                if not D("0") <= parsed[0] <= parsed[1] <= parsed[2] <= D("1"):
                    raise ModelInputError(f"invalid support stress range for {row['assumption_id']}")
        elif row["value_type"] == "Not_available":
            if values != ["NA", "NA", "NA"]:
                raise ModelInputError(
                    f"unavailable market-policy value must remain NA: {row['assumption_id']}"
                )
        else:
            raise ModelInputError(f"unsupported value_type for {row['assumption_id']}")

    required = REQUIRED_RESOURCE_PARAMETERS | REQUIRED_VERIFIED_PARAMETERS | {
        SUPPORT_STRESS_PARAMETER
    }
    for route_id, parameters in by_route.items():
        missing = required - set(parameters)
        extra = set(parameters) - required
        if missing or extra:
            raise ModelInputError(
                f"route {route_id} parameter mismatch; missing={sorted(missing)}, extra={sorted(extra)}"
            )
        for name in REQUIRED_VERIFIED_PARAMETERS:
            if parameters[name]["value_type"] != "Not_available":
                raise ModelInputError(f"verified policy field is not gap-labelled: {route_id}/{name}")


def build_route_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Return annualisation factors while retaining an explicit net-gap data gap."""

    validate_assumptions(rows)
    routes: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        routes.setdefault(row["route_id"], {})[row["parameter_name"]] = row

    summary: list[dict[str, object]] = []
    for route_id in sorted(routes):
        parameters = routes[route_id]
        support = parameters[SUPPORT_STRESS_PARAMETER]
        for case in CASES:
            lifetime = int(_decimal(parameters["transition_lifetime_years"][case], "lifetime"))
            rate = _decimal(parameters["real_discount_rate"][case], "discount rate")
            fixed = _decimal(
                parameters["incremental_fixed_opex_fraction_of_transition_capex"][case],
                "fixed OPEX fraction",
            )
            variable = _decimal(
                parameters[
                    "incremental_variable_resource_cost_per_operational_tco2e_abated"
                ][case],
                "variable resource cost",
            )
            crf = capital_recovery_factor(rate, lifetime)
            summary.append(
                {
                    "sector": parameters["transition_lifetime_years"]["sector"],
                    "route_id": route_id,
                    "case": case,
                    "transition_lifetime_years": lifetime,
                    "real_discount_rate": rate,
                    "capital_recovery_factor": crf,
                    "incremental_fixed_opex_fraction_of_transition_capex": fixed,
                    "annual_capital_and_fixed_opex_factor": crf + fixed,
                    "incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated": variable,
                    "resource_gap_formula": (
                        "transition_capex_usd_2025 * annual_capital_and_fixed_opex_factor "
                        "+ modelled_operational_abatement_tco2e * variable_resource_cost"
                    ),
                    "verified_market_policy_status": "not_available_not_zero",
                    "support_stress_low": _decimal(support["low"], "support stress"),
                    "support_stress_base": _decimal(support["base"], "support stress"),
                    "support_stress_high": _decimal(support["high"], "support stress"),
                    "support_stress_case_orientation": "independent_not_paired_with_resource_case",
                    "stress_adjusted_gap_formula": (
                        "annual_resource_gap - max(annual_resource_gap, 0) * "
                        "independently_selected_support_stress_share"
                    ),
                    "value_type": "Modelled_from_estimated_inputs",
                    "quality_flag": "D",
                    "boundary_note": (
                        "Incremental annual proxy only; incumbent cost, early retirement, verified incentives "
                        "and system abatement are not modelled. Stress-adjusted gap is not realised net gap."
                    ),
                }
            )
    return summary


def write_summary(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _serialise(row[field]) for field in SUMMARY_FIELDS})


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build route annual cost-gap input summary")
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        write_summary(args.output, build_route_summary(_read_csv(args.assumptions)))
    except ModelInputError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
