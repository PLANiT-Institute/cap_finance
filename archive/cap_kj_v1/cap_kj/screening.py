"""Output-first capital-allocation screening tables.

This module intentionally produces a screening result rather than a full cost-gap
decision. It combines facility baselines with explicit low/base/high route mapping
assumptions, keeps uncovered emissions as a residual, and never labels operational
emissions reduction as system abatement.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

from .model import ModelInputError


D = Decimal
CASES = ("low", "base", "high")
ANCHOR_RECORDS = {
    "POSCO": "POSCO_2025_S12",
    "NIPPON_STEEL": "NSC_FY2024_GHG_TOTAL",
    "LOTTE_CHEMICAL": "LOTTE_2025_PARENT_S12",
    "MITSUI_CHEMICALS": "MCI_FY2024_PARENT_S12",
}
QUALITY_ORDER = {"A": 1, "B": 2, "C": 3, "D": 4}


FACILITY_RESULT_FIELDS = (
    "company_id",
    "company_name",
    "facility_id",
    "facility_name",
    "country",
    "sector",
    "baseline_period",
    "case",
    "primary_scope_status",
    "baseline_emissions_value_type",
    "baseline_operational_ghg_tco2e",
    "selected_route",
    "decision_horizon",
    "readiness_year",
    "facility_status",
    "status_basis",
    "action_view",
    "modelled_flag",
    "capex_driver",
    "capex_intensity",
    "capex_unit",
    "transition_capex_usd_2025",
    "abatement_fraction",
    "transition_operational_ghg_tco2e",
    "modelled_operational_abatement_tco2e",
    "system_abatement_status",
    "capex_by_2030_usd_2025",
    "capex_2031_2040_usd_2025",
    "capex_2041_2050_usd_2025",
    "binding_constraint",
    "dominant_common_factor",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
    "boundary_note",
)


COMPANY_RESULT_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "case",
    "official_company_baseline_tco2e",
    "facility_seed_baseline_tco2e",
    "facility_reconciliation_ratio",
    "modelled_facility_count",
    "total_facility_count",
    "emissions_coverage_ratio",
    "production_coverage_ratio",
    "unmodelled_residual_emissions_tco2e",
    "transition_operational_ghg_tco2e",
    "modelled_operational_abatement_tco2e",
    "system_abatement_status",
    "transition_capex_usd_2025",
    "capex_by_2030_usd_2025",
    "capex_2031_2040_usd_2025",
    "capex_2041_2050_usd_2025",
    "cumulative_capex_2030_usd_2025",
    "cumulative_capex_2040_usd_2025",
    "cumulative_capex_2050_usd_2025",
    "annual_operational_abatement_per_usd_million_capex",
    "no_regret_capex_share",
    "price_conditional_capex_share",
    "contract_dependent_capex_share",
    "level_support_dependent_capex_share",
    "largest_capex_facility_id",
    "largest_capex_facility_share",
    "dominant_common_factors",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "method_note",
)


@dataclass(frozen=True)
class ScreeningMetrics:
    transition_emissions: Decimal
    operational_abatement: Decimal
    transition_capex: Decimal


def calculate_case(
    *,
    baseline_emissions: Decimal,
    activity: Decimal | None,
    capex_driver: str,
    capex_intensity: Decimal,
    abatement_fraction: Decimal,
    modelled: bool,
) -> ScreeningMetrics:
    """Calculate one facility/case screening result with explicit driver units."""

    if baseline_emissions < 0:
        raise ModelInputError("baseline_emissions cannot be negative")
    if capex_intensity < 0:
        raise ModelInputError("capex_intensity cannot be negative")
    if not D("0") <= abatement_fraction <= D("1"):
        raise ModelInputError("abatement_fraction must be between zero and one")
    if not modelled:
        return ScreeningMetrics(baseline_emissions, D("0"), D("0"))

    abatement = baseline_emissions * abatement_fraction
    if capex_driver == "activity":
        if activity is None or activity <= 0:
            raise ModelInputError("activity driver requires positive facility activity")
        capex = activity * capex_intensity
    elif capex_driver == "abatement":
        capex = abatement * capex_intensity
    else:
        raise ModelInputError(f"unsupported capex_driver: {capex_driver}")
    return ScreeningMetrics(
        transition_emissions=baseline_emissions - abatement,
        operational_abatement=abatement,
        transition_capex=capex,
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


def _activity(seed: dict[str, str], case: str) -> Decimal | None:
    raw = seed[f"facility_activity_{case}"]
    return None if raw in {"", "NA"} else _decimal(raw, "facility activity")


def _emissions(seed: dict[str, str], case: str) -> Decimal:
    return _decimal(
        seed[f"operational_ghg_{case}_tco2e"], "facility operational GHG"
    )


def _anchor_tco2e(row: dict[str, str]) -> Decimal:
    value = _decimal(row["value"], "company baseline")
    if row["unit"] == "tCO2e":
        return value
    if row["unit"] == "ktCO2e":
        return value * D("1000")
    raise ModelInputError(f"unsupported company emissions unit: {row['unit']}")


def _join_labels(values: Iterable[str]) -> str:
    labels: set[str] = set()
    for value in values:
        labels.update(item for item in value.split("|") if item)
    return "|".join(sorted(labels))


def _worst_quality(values: Iterable[str]) -> str:
    return max(values, key=lambda value: QUALITY_ORDER.get(value, 99))


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
            writer.writerow({key: _serialise(row[key]) for key in fields})


def build_screening_tables(
    *,
    seed_path: Path,
    mapping_path: Path,
    company_baseline_path: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Build facility/case and company/case output tables."""

    seeds = _read_csv(seed_path)
    mappings = _read_csv(mapping_path)
    baselines = _read_csv(company_baseline_path)

    seed_by_id = {row["facility_id"]: row for row in seeds}
    if len(seed_by_id) != len(seeds):
        raise ModelInputError("facility seed contains duplicate facility_id")
    mapping_by_id = {row["facility_id"]: row for row in mappings}
    if len(mapping_by_id) != len(mappings):
        raise ModelInputError("route mapping contains duplicate facility_id")
    if set(seed_by_id) != set(mapping_by_id):
        missing = sorted(set(seed_by_id) - set(mapping_by_id))
        extra = sorted(set(mapping_by_id) - set(seed_by_id))
        raise ModelInputError(f"facility mapping mismatch; missing={missing}, extra={extra}")

    baseline_by_record = {row["record_id"]: row for row in baselines}
    anchors = {
        company_id: _anchor_tco2e(baseline_by_record[record_id])
        for company_id, record_id in ANCHOR_RECORDS.items()
    }

    facility_results: list[dict[str, object]] = []
    for seed in seeds:
        mapping = mapping_by_id[seed["facility_id"]]
        modelled = mapping["modelled_flag"] == "yes"
        for case in CASES:
            baseline_emissions = _emissions(seed, case)
            capex_intensity = _decimal(
                mapping[f"capex_intensity_{case}"], "capex intensity"
            )
            abatement_fraction = _decimal(
                mapping[f"abatement_fraction_{case}"], "abatement fraction"
            )
            metrics = calculate_case(
                baseline_emissions=baseline_emissions,
                activity=_activity(seed, case),
                capex_driver=mapping["capex_driver"],
                capex_intensity=capex_intensity,
                abatement_fraction=abatement_fraction,
                modelled=modelled,
            )
            horizon = mapping["decision_horizon"]
            by_2030 = metrics.transition_capex if horizon == "2030" else D("0")
            by_2040 = metrics.transition_capex if horizon == "2040" else D("0")
            by_2050 = metrics.transition_capex if horizon == "2050" else D("0")
            source_id = _join_labels(
                (
                    seed["emissions_source_id"],
                    seed["activity_source_id"],
                    mapping["source_id"],
                )
            )
            facility_results.append(
                {
                    "company_id": seed["company_id"],
                    "company_name": seed["company_name"],
                    "facility_id": seed["facility_id"],
                    "facility_name": seed["facility_name"],
                    "country": seed["country"],
                    "sector": seed["sector"],
                    "baseline_period": seed["baseline_period"],
                    "case": case,
                    "primary_scope_status": seed["primary_scope_status"],
                    "baseline_emissions_value_type": seed["emissions_value_type"],
                    "baseline_operational_ghg_tco2e": baseline_emissions,
                    "selected_route": mapping["selected_route"],
                    "decision_horizon": horizon,
                    "readiness_year": mapping["readiness_year"],
                    "facility_status": mapping["facility_status"],
                    "status_basis": mapping["status_basis"],
                    "action_view": mapping["action_view"],
                    "modelled_flag": mapping["modelled_flag"],
                    "capex_driver": mapping["capex_driver"],
                    "capex_intensity": capex_intensity,
                    "capex_unit": mapping["capex_unit"],
                    "transition_capex_usd_2025": metrics.transition_capex,
                    "abatement_fraction": abatement_fraction,
                    "transition_operational_ghg_tco2e": metrics.transition_emissions,
                    "modelled_operational_abatement_tco2e": metrics.operational_abatement,
                    "system_abatement_status": "not_modelled; leakage and replacement production pending",
                    "capex_by_2030_usd_2025": by_2030,
                    "capex_2031_2040_usd_2025": by_2040,
                    "capex_2041_2050_usd_2025": by_2050,
                    "binding_constraint": mapping["binding_constraint"],
                    "dominant_common_factor": mapping["dominant_common_factor"],
                    "currency": mapping["currency"],
                    "price_year": mapping["price_year"],
                    "value_type": "Modelled" if modelled else "Not_modelled",
                    "quality_flag": _worst_quality(
                        (seed["quality_flag"], mapping["quality_flag"])
                    ),
                    "source_id": source_id,
                    "formula_or_method": mapping["formula_or_method"],
                    "boundary_note": mapping["notes"],
                }
            )

    company_results: list[dict[str, object]] = []
    for company_id in ANCHOR_RECORDS:
        company_rows = [row for row in facility_results if row["company_id"] == company_id]
        if not company_rows:
            raise ModelInputError(f"no facility results for {company_id}")
        base_rows = [row for row in company_rows if row["case"] == "base"]
        modelled_base = sum(
            (row["baseline_operational_ghg_tco2e"] for row in base_rows if row["modelled_flag"] == "yes"),
            start=D("0"),
        )
        seed_base = sum(
            (row["baseline_operational_ghg_tco2e"] for row in base_rows), start=D("0")
        )
        official_anchor = anchors[company_id]
        emissions_coverage = modelled_base / official_anchor
        facility_reconciliation = seed_base / official_anchor

        for case in CASES:
            rows = [row for row in company_rows if row["case"] == case]
            capex_total = sum((row["transition_capex_usd_2025"] for row in rows), start=D("0"))
            capex_2030 = sum((row["capex_by_2030_usd_2025"] for row in rows), start=D("0"))
            capex_2040 = sum((row["capex_2031_2040_usd_2025"] for row in rows), start=D("0"))
            capex_2050 = sum((row["capex_2041_2050_usd_2025"] for row in rows), start=D("0"))
            abatement = sum(
                (row["modelled_operational_abatement_tco2e"] for row in rows),
                start=D("0"),
            )
            transition_emissions = sum(
                (row["transition_operational_ghg_tco2e"] for row in rows),
                start=D("0"),
            )
            seed_case = sum(
                (row["baseline_operational_ghg_tco2e"] for row in rows), start=D("0")
            )
            unmodelled_case = sum(
                (
                    row["baseline_operational_ghg_tco2e"]
                    for row in rows
                    if row["modelled_flag"] != "yes"
                ),
                start=D("0"),
            )
            capex_by_status = {
                status: sum(
                    (
                        row["transition_capex_usd_2025"]
                        for row in rows
                        if row["facility_status"] == status
                    ),
                    start=D("0"),
                )
                for status in (
                    "no-regret",
                    "price-conditional",
                    "contract-dependent",
                    "level-support-dependent",
                )
            }
            modelled_rows = [row for row in rows if row["modelled_flag"] == "yes"]
            largest = max(modelled_rows, key=lambda row: row["transition_capex_usd_2025"])
            per_million = (
                abatement / (capex_total / D("1000000")) if capex_total else D("0")
            )
            company_results.append(
                {
                    "company_id": company_id,
                    "company_name": rows[0]["company_name"],
                    "country": rows[0]["country"],
                    "sector": rows[0]["sector"],
                    "case": case,
                    "official_company_baseline_tco2e": official_anchor,
                    "facility_seed_baseline_tco2e": seed_case,
                    "facility_reconciliation_ratio": facility_reconciliation,
                    "modelled_facility_count": len(modelled_rows),
                    "total_facility_count": len(rows),
                    "emissions_coverage_ratio": emissions_coverage,
                    "production_coverage_ratio": "NA",
                    "unmodelled_residual_emissions_tco2e": unmodelled_case,
                    "transition_operational_ghg_tco2e": transition_emissions,
                    "modelled_operational_abatement_tco2e": abatement,
                    "system_abatement_status": "not_modelled; leakage and replacement production pending",
                    "transition_capex_usd_2025": capex_total,
                    "capex_by_2030_usd_2025": capex_2030,
                    "capex_2031_2040_usd_2025": capex_2040,
                    "capex_2041_2050_usd_2025": capex_2050,
                    "cumulative_capex_2030_usd_2025": capex_2030,
                    "cumulative_capex_2040_usd_2025": capex_2030 + capex_2040,
                    "cumulative_capex_2050_usd_2025": capex_total,
                    "annual_operational_abatement_per_usd_million_capex": per_million,
                    "no_regret_capex_share": capex_by_status["no-regret"] / capex_total if capex_total else D("0"),
                    "price_conditional_capex_share": capex_by_status["price-conditional"] / capex_total if capex_total else D("0"),
                    "contract_dependent_capex_share": capex_by_status["contract-dependent"] / capex_total if capex_total else D("0"),
                    "level_support_dependent_capex_share": capex_by_status["level-support-dependent"] / capex_total if capex_total else D("0"),
                    "largest_capex_facility_id": largest["facility_id"],
                    "largest_capex_facility_share": largest["transition_capex_usd_2025"] / capex_total if capex_total else D("0"),
                    "dominant_common_factors": _join_labels(
                        row["dominant_common_factor"] for row in modelled_rows
                    ),
                    "currency": "USD",
                    "price_year": "2025 screening proxy",
                    "value_type": "Modelled",
                    "quality_flag": _worst_quality(row["quality_flag"] for row in rows),
                    "source_id": _join_labels(row["source_id"] for row in rows),
                    "method_note": "Facility calculation and company aggregation; screening CAPEX and operational abatement only. Cost gap, verified support, system abatement and production coverage remain pending.",
                }
            )
    return facility_results, company_results


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build CAP-KJ MVP screening tables")
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--company-baseline", type=Path, required=True)
    parser.add_argument("--facility-output", type=Path, required=True)
    parser.add_argument("--company-output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        facility_rows, company_rows = build_screening_tables(
            seed_path=args.seed,
            mapping_path=args.mapping,
            company_baseline_path=args.company_baseline,
        )
        _write_csv(args.facility_output, facility_rows, FACILITY_RESULT_FIELDS)
        _write_csv(args.company_output, company_rows, COMPANY_RESULT_FIELDS)
    except ModelInputError as exc:
        print(f"cap-kj screening: error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
