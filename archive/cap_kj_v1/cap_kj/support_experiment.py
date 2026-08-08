"""Rule-based B0/BH/BL/BHL support experiment for the CAP-KJ MVP.

This is a mechanism screen, not a completed economic-feasibility model. It uses
the base facility screening outputs, explicit low/base/high contract-coverage and
capital-equivalent support assumptions, and a conservative decision rule:
operational abatement is counted only when a facility reaches ``no-regret``.
System abatement remains unavailable until leakage and replacement production are
modelled.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

from .model import ModelInputError


D = Decimal
MECHANISMS = ("B0", "BH", "BL", "BHL")
ASSUMPTION_CASES = ("low", "base", "high")
MODELLED_STATUSES = (
    "no-regret",
    "price-conditional",
    "contract-dependent",
    "level-support-dependent",
)

FACILITY_FIELDS = (
    "company_id",
    "company_name",
    "facility_id",
    "facility_name",
    "country",
    "sector",
    "assumption_case",
    "mechanism_case",
    "mean_cost_treatment",
    "risk_exposure_treatment",
    "coverage_theta",
    "screening_level_support_capex_share",
    "screening_level_support_total_usd_2025",
    "status_before",
    "status_after",
    "status_change_flag",
    "transition_enabled_flag",
    "trigger_factor",
    "base_transition_capex_usd_2025",
    "contract_covered_capex_usd_2025",
    "baseline_operational_ghg_tco2e",
    "potential_operational_abatement_tco2e",
    "mechanism_operational_abatement_tco2e",
    "additional_operational_abatement_vs_b0_tco2e",
    "mechanism_transition_operational_ghg_tco2e",
    "system_abatement_status",
    "residual_common_factor_exposure_ratio",
    "dominant_common_factor",
    "production_coverage_ratio",
    "emissions_coverage_note",
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
    "assumption_case",
    "mechanism_case",
    "official_company_baseline_tco2e",
    "facility_seed_baseline_tco2e",
    "emissions_coverage_ratio",
    "production_coverage_ratio",
    "modelled_facility_count",
    "total_facility_count",
    "potential_transition_capex_usd_2025",
    "transition_enabled_capex_usd_2025",
    "transition_enabled_capex_share",
    "status_changed_capex_usd_2025",
    "status_changed_capex_share",
    "contract_covered_capex_usd_2025",
    "screening_level_support_total_usd_2025",
    "potential_operational_abatement_tco2e",
    "mechanism_operational_abatement_tco2e",
    "additional_operational_abatement_vs_b0_tco2e",
    "company_operational_emissions_tco2e",
    "system_abatement_status",
    "changed_facility_count",
    "changed_facility_ids",
    "capex_weighted_residual_common_exposure_ratio",
    "additional_operational_abatement_per_usd_million_level_support",
    "additional_operational_abatement_per_usd_million_contract_covered_capex",
    "dominant_common_factors",
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
        result = D(raw)
    except InvalidOperation as exc:
        raise ModelInputError(f"{label} is not numeric: {raw!r}") from exc
    if not result.is_finite():
        raise ModelInputError(f"{label} must be finite")
    return result


def _serialise(value: object) -> object:
    if isinstance(value, Decimal):
        rendered = format(value, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return "0" if rendered in {"", "-0"} else rendered
    return value


def _write_csv(path: Path, rows: list[dict[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _serialise(row[field]) for field in fields})


def _join(values: Iterable[str]) -> str:
    labels: set[str] = set()
    for value in values:
        labels.update(label for label in value.split("|") if label)
    return "|".join(sorted(labels))


def status_after_mechanism(status_before: str, mechanism: str) -> str:
    """Apply the pre-declared mechanism-to-status transition rule."""
    if mechanism not in MECHANISMS:
        raise ModelInputError(f"unsupported mechanism: {mechanism}")
    if status_before == "unmodelled-residual":
        return status_before
    if status_before not in MODELLED_STATUSES:
        raise ModelInputError(f"unsupported facility status: {status_before}")
    if status_before == "no-regret" or mechanism == "B0":
        return status_before
    if mechanism == "BH":
        if status_before in {"price-conditional", "contract-dependent"}:
            return "no-regret"
        return "level-support-dependent"
    if mechanism == "BL":
        if status_before == "level-support-dependent":
            return "price-conditional"
        return status_before
    return "no-regret"


def load_assumptions(path: Path) -> dict[tuple[str, str, str], Decimal]:
    rows = _read_csv(path)
    expected = {
        (status, parameter)
        for status in (
            "price-conditional",
            "contract-dependent",
            "level-support-dependent",
        )
        for parameter in ("coverage_theta", "level_support_capex_share")
    }
    actual = {(row["facility_status"], row["parameter"]) for row in rows}
    if actual != expected or len(rows) != len(expected):
        raise ModelInputError("support assumptions require one coverage and support row per conditional status")

    result: dict[tuple[str, str, str], Decimal] = {}
    for row in rows:
        if row["value_type"] != "Estimated" or row["quality_flag"] != "D":
            raise ModelInputError("mechanism assumptions must remain Estimated and quality D")
        values = [_decimal(row[case], f"{row['assumption_id']} {case}") for case in ASSUMPTION_CASES]
        if not values[0] <= values[1] <= values[2]:
            raise ModelInputError(f"assumption range is not ordered: {row['assumption_id']}")
        if any(value < 0 or value > 1 for value in values):
            raise ModelInputError(f"assumption must be a share: {row['assumption_id']}")
        for case, value in zip(ASSUMPTION_CASES, values):
            result[(row["facility_status"], row["parameter"], case)] = value
    return result


def build_support_experiment(
    facility_results_path: Path,
    company_results_path: Path,
    assumptions_path: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Build facility and company mechanism tables for all assumption cases."""
    facility_rows = [
        row for row in _read_csv(facility_results_path) if row["case"] == "base"
    ]
    company_screening = {
        row["company_id"]: row
        for row in _read_csv(company_results_path)
        if row["case"] == "base"
    }
    assumptions = load_assumptions(assumptions_path)
    if len({row["facility_id"] for row in facility_rows}) != len(facility_rows):
        raise ModelInputError("base facility result has duplicate facility_id")

    output: list[dict[str, object]] = []
    for assumption_case in ASSUMPTION_CASES:
        for row in facility_rows:
            modelled = row["modelled_flag"] == "yes"
            status_before = row["facility_status"] if modelled else "unmodelled-residual"
            baseline = _decimal(row["baseline_operational_ghg_tco2e"], "baseline emissions")
            potential_abatement = _decimal(
                row["modelled_operational_abatement_tco2e"], "potential abatement"
            )
            capex = _decimal(row["transition_capex_usd_2025"], "transition CAPEX")
            if not modelled and (potential_abatement != 0 or capex != 0):
                raise ModelInputError(f"unmodelled residual carries model output: {row['facility_id']}")

            for mechanism in MECHANISMS:
                if modelled and status_before != "no-regret":
                    theta_required = assumptions[
                        (status_before, "coverage_theta", assumption_case)
                    ]
                    support_share_required = assumptions[
                        (status_before, "level_support_capex_share", assumption_case)
                    ]
                else:
                    theta_required = D("0")
                    support_share_required = D("0")

                theta = theta_required if mechanism in {"BH", "BHL"} else D("0")
                support_share = (
                    support_share_required if mechanism in {"BL", "BHL"} else D("0")
                )
                support_total = capex * support_share
                covered_capex = capex * theta
                status_after = status_after_mechanism(status_before, mechanism)
                transition_enabled = status_after == "no-regret"
                b0_abatement = (
                    potential_abatement if status_before == "no-regret" else D("0")
                )
                mechanism_abatement = potential_abatement if transition_enabled else D("0")
                additional_abatement = mechanism_abatement - b0_abatement
                transition_emissions = baseline - mechanism_abatement
                residual_exposure: Decimal | str = (
                    D("1") - theta if modelled else "NA"
                )
                source_ids = row["source_id"]
                if support_share:
                    source_ids = _join((source_ids, "MCI_WEST_JAPAN_2026"))
                output.append(
                    {
                        "company_id": row["company_id"],
                        "company_name": row["company_name"],
                        "facility_id": row["facility_id"],
                        "facility_name": row["facility_name"],
                        "country": row["country"],
                        "sector": row["sector"],
                        "assumption_case": assumption_case,
                        "mechanism_case": mechanism,
                        "mean_cost_treatment": (
                            "screening capital-equivalent level support applied"
                            if mechanism in {"BL", "BHL"}
                            else "unchanged"
                        ),
                        "risk_exposure_treatment": (
                            "reduced; central cost level held unchanged"
                            if mechanism in {"BH", "BHL"}
                            else "unchanged"
                        ),
                        "coverage_theta": theta,
                        "screening_level_support_capex_share": support_share,
                        "screening_level_support_total_usd_2025": support_total,
                        "status_before": status_before,
                        "status_after": status_after,
                        "status_change_flag": "yes" if status_after != status_before else "no",
                        "transition_enabled_flag": "yes" if transition_enabled else "no",
                        "trigger_factor": row["dominant_common_factor"] if modelled else "unmodelled boundary",
                        "base_transition_capex_usd_2025": capex,
                        "contract_covered_capex_usd_2025": covered_capex,
                        "baseline_operational_ghg_tco2e": baseline,
                        "potential_operational_abatement_tco2e": potential_abatement,
                        "mechanism_operational_abatement_tco2e": mechanism_abatement,
                        "additional_operational_abatement_vs_b0_tco2e": additional_abatement,
                        "mechanism_transition_operational_ghg_tco2e": transition_emissions,
                        "system_abatement_status": "not_modelled; leakage and replacement production pending",
                        "residual_common_factor_exposure_ratio": residual_exposure,
                        "dominant_common_factor": row["dominant_common_factor"],
                        "production_coverage_ratio": "NA",
                        "emissions_coverage_note": "company ratio reported in company support table",
                        "value_type": "Modelled" if modelled else "Not_modelled",
                        "quality_flag": "D",
                        "source_id": source_ids,
                        "formula_or_method": "Status-transition rule by B0/BH/BL/BHL; abatement is counted only after a no-regret state; level support equals base CAPEX times estimated share; residual exposure equals 1-theta.",
                        "boundary_note": "Rule-based mechanism screen, not a completed cost-gap, contract-pricing or system-abatement result.",
                    }
                )

    company_output: list[dict[str, object]] = []
    for assumption_case in ASSUMPTION_CASES:
        for mechanism in MECHANISMS:
            for company_id, company in company_screening.items():
                rows = [
                    row
                    for row in output
                    if row["company_id"] == company_id
                    and row["assumption_case"] == assumption_case
                    and row["mechanism_case"] == mechanism
                ]
                if not rows:
                    raise ModelInputError(f"missing mechanism rows for {company_id}")
                modelled_rows = [row for row in rows if row["value_type"] == "Modelled"]
                capex = sum((row["base_transition_capex_usd_2025"] for row in rows), D("0"))
                enabled_capex = sum(
                    (
                        row["base_transition_capex_usd_2025"]
                        for row in rows
                        if row["transition_enabled_flag"] == "yes"
                    ),
                    D("0"),
                )
                changed_capex = sum(
                    (
                        row["base_transition_capex_usd_2025"]
                        for row in rows
                        if row["status_change_flag"] == "yes"
                    ),
                    D("0"),
                )
                covered_capex = sum((row["contract_covered_capex_usd_2025"] for row in rows), D("0"))
                support_total = sum((row["screening_level_support_total_usd_2025"] for row in rows), D("0"))
                potential_abatement = sum((row["potential_operational_abatement_tco2e"] for row in rows), D("0"))
                mechanism_abatement = sum((row["mechanism_operational_abatement_tco2e"] for row in rows), D("0"))
                additional_abatement = sum(
                    (row["additional_operational_abatement_vs_b0_tco2e"] for row in rows),
                    D("0"),
                )
                seed_emissions = sum((row["baseline_operational_ghg_tco2e"] for row in rows), D("0"))
                residual_exposure = (
                    sum(
                        row["base_transition_capex_usd_2025"]
                        * row["residual_common_factor_exposure_ratio"]
                        for row in modelled_rows
                    )
                    / capex
                    if capex
                    else D("0")
                )
                changed = sorted(
                    row["facility_id"] for row in rows if row["status_change_flag"] == "yes"
                )
                official = _decimal(company["official_company_baseline_tco2e"], "official baseline")
                company_output.append(
                    {
                        "company_id": company_id,
                        "company_name": company["company_name"],
                        "country": company["country"],
                        "sector": company["sector"],
                        "assumption_case": assumption_case,
                        "mechanism_case": mechanism,
                        "official_company_baseline_tco2e": official,
                        "facility_seed_baseline_tco2e": seed_emissions,
                        "emissions_coverage_ratio": _decimal(company["emissions_coverage_ratio"], "coverage"),
                        "production_coverage_ratio": "NA",
                        "modelled_facility_count": len(modelled_rows),
                        "total_facility_count": len(rows),
                        "potential_transition_capex_usd_2025": capex,
                        "transition_enabled_capex_usd_2025": enabled_capex,
                        "transition_enabled_capex_share": enabled_capex / capex if capex else D("0"),
                        "status_changed_capex_usd_2025": changed_capex,
                        "status_changed_capex_share": changed_capex / capex if capex else D("0"),
                        "contract_covered_capex_usd_2025": covered_capex,
                        "screening_level_support_total_usd_2025": support_total,
                        "potential_operational_abatement_tco2e": potential_abatement,
                        "mechanism_operational_abatement_tco2e": mechanism_abatement,
                        "additional_operational_abatement_vs_b0_tco2e": additional_abatement,
                        "company_operational_emissions_tco2e": seed_emissions - mechanism_abatement,
                        "system_abatement_status": "not_modelled; leakage and replacement production pending",
                        "changed_facility_count": len(changed),
                        "changed_facility_ids": "|".join(changed),
                        "capex_weighted_residual_common_exposure_ratio": residual_exposure,
                        "additional_operational_abatement_per_usd_million_level_support": (
                            additional_abatement / (support_total / D("1000000"))
                            if support_total
                            else "NA"
                        ),
                        "additional_operational_abatement_per_usd_million_contract_covered_capex": (
                            additional_abatement / (covered_capex / D("1000000"))
                            if covered_capex
                            else "NA"
                        ),
                        "dominant_common_factors": _join(row["dominant_common_factor"] for row in modelled_rows),
                        "currency": "USD",
                        "price_year": "2025 screening proxy",
                        "value_type": "Modelled",
                        "quality_flag": "D",
                        "source_id": _join(row["source_id"] for row in rows),
                        "method_note": "Rule-based mechanism result. BH reduces exposure without lowering the central cost level; BL applies a capital-equivalent level screen without reducing exposure; BHL combines both. Operational abatement appears only after a no-regret status. System abatement and economic cost gaps remain pending.",
                    }
                )
    return output, company_output


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build CAP-KJ MVP B0/BH/BL/BHL support experiment")
    parser.add_argument("--facility-results", type=Path, required=True)
    parser.add_argument("--company-results", type=Path, required=True)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--facility-output", type=Path, required=True)
    parser.add_argument("--company-output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        facility_rows, company_rows = build_support_experiment(
            args.facility_results, args.company_results, args.assumptions
        )
        _write_csv(args.facility_output, facility_rows, FACILITY_FIELDS)
        _write_csv(args.company_output, company_rows, COMPANY_FIELDS)
    except ModelInputError as exc:
        print(f"cap-kj support experiment: error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
