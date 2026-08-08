"""Build production-coverage status and facility physical-constraint outputs."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

from .model import ModelInputError


D = Decimal
COMPANY_ORDER = ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS")
PRODUCTION_TOLERANCE = D("0.02")

PRODUCTION_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "reporting_period",
    "production_metric",
    "company_reported_production",
    "facility_activity_sum",
    "unit",
    "facility_activity_value_types",
    "raw_reconciliation_ratio",
    "absolute_difference",
    "reconciliation_tolerance",
    "production_coverage_ratio",
    "coverage_status",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
    "boundary_note",
)

CONSTRAINT_FIELDS = (
    "constraint_id",
    "company_id",
    "facility_id",
    "selected_route",
    "project_status",
    "evidence_date",
    "official_route_capacity_t_per_year",
    "official_project_investment_krw",
    "facility_activity_low_t_per_year",
    "facility_activity_base_t_per_year",
    "facility_activity_high_t_per_year",
    "project_capacity_coverage_low",
    "project_capacity_coverage_base",
    "project_capacity_coverage_high",
    "uncovered_activity_low_t_per_year",
    "uncovered_activity_base_t_per_year",
    "uncovered_activity_high_t_per_year",
    "full_route_scale_multiple_low",
    "full_route_scale_multiple_base",
    "full_route_scale_multiple_high",
    "planned_scrap_share",
    "implied_project_scrap_demand_t_per_year",
    "share_of_2024_total_scrap_usage",
    "share_of_2024_purchased_scrap_usage",
    "constraint_status",
    "capital_allocation_action",
    "capacity_unit",
    "investment_currency",
    "investment_price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
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


def _write_csv(path: Path, rows: list[dict[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _serialise(row[field]) for field in fields})


def _validate_facts(facts: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_id = {row["fact_id"]: row for row in facts}
    if len(by_id) != len(facts):
        raise ModelInputError("official fact_id must be unique")
    required = {
        "POSCO_GW_EAF_CAPACITY",
        "POSCO_GW_EAF_INVESTMENT",
        "POSCO_GW_EAF_SCRAP_SHARE",
        "POSCO_TOTAL_SCRAP_2024",
        "POSCO_PURCHASED_SCRAP_2024",
        "NSC_CRUDE_STEEL_FY2024",
    }
    if set(by_id) != required:
        raise ModelInputError(
            f"official fact set mismatch; missing={sorted(required - set(by_id))}, "
            f"extra={sorted(set(by_id) - required)}"
        )
    for row in facts:
        if row["value_type"] != "Reported":
            raise ModelInputError(f"official fact is not reported: {row['fact_id']}")
        values = [_decimal(row[case], row["fact_id"]) for case in ("low", "base", "high")]
        if len(set(values)) != 1:
            raise ModelInputError(f"reported point must repeat across cases: {row['fact_id']}")
        if not row["source_id"] or not row["formula_or_method"] or not row["boundary_note"]:
            raise ModelInputError(f"official fact lacks audit metadata: {row['fact_id']}")
    return by_id


def build_outputs(
    seeds: list[dict[str, str]],
    mappings: list[dict[str, str]],
    facts: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Return four-company production status and the Gwangyang EAF constraint."""

    facts_by_id = _validate_facts(facts)
    seed_by_id = {row["facility_id"]: row for row in seeds}
    mapping_by_id = {row["facility_id"]: row for row in mappings}
    if len(seed_by_id) != len(seeds) or len(mapping_by_id) != len(mappings):
        raise ModelInputError("facility seed or mapping IDs are not unique")

    production_rows: list[dict[str, object]] = []
    for company_id in COMPANY_ORDER:
        company_seeds = [row for row in seeds if row["company_id"] == company_id]
        if not company_seeds:
            raise ModelInputError(f"no seed facilities for {company_id}")
        numeric = [row for row in company_seeds if row["facility_activity_base"] != "NA"]
        facility_sum = sum(
            (_decimal(row["facility_activity_base"], "facility activity") for row in numeric),
            start=D("0"),
        )
        activity_types = _join_labels(row["activity_value_type"] for row in company_seeds)
        source_ids = _join_labels(row["activity_source_id"] for row in company_seeds)
        common: dict[str, object] = {
            "company_id": company_id,
            "company_name": company_seeds[0]["company_name"],
            "country": company_seeds[0]["country"],
            "sector": company_seeds[0]["sector"],
            "facility_activity_sum": facility_sum if numeric else "NA",
            "facility_activity_value_types": activity_types,
            "reconciliation_tolerance": PRODUCTION_TOLERANCE,
            "price_year": "not_applicable",
        }
        if company_id == "NIPPON_STEEL":
            fact = facts_by_id["NSC_CRUDE_STEEL_FY2024"]
            company_total = _decimal(fact["base"], "Nippon company production")
            ratio = facility_sum / company_total
            difference = facility_sum - company_total
            within = abs(ratio - D("1")) <= PRODUCTION_TOLERANCE
            common.update(
                {
                    "reporting_period": "FY2024",
                    "production_metric": "crude_steel_production",
                    "company_reported_production": company_total,
                    "unit": "t crude steel/year",
                    "raw_reconciliation_ratio": ratio,
                    "absolute_difference": difference,
                    "production_coverage_ratio": D("1") if within else "NA",
                    "coverage_status": (
                        "reconciled_within_2pct_tolerance; rounded facility sum exceeds company total"
                        if within
                        else "failed_reconciliation"
                    ),
                    "value_type": "Derived_from_reported",
                    "quality_flag": "B" if within else "D",
                    "source_id": _join_labels((source_ids, fact["source_id"])),
                    "formula_or_method": (
                        "sum 11 FY2024 reported works/area crude-steel values divided by separately "
                        "reported FY2024 company crude-steel production; publish coverage=1 only when "
                        "absolute difference is within the pre-specified 2% tolerance"
                    ),
                    "boundary_note": (
                        "Facility values sum to 34.88 Mt versus the company statement of 34.30 Mt. "
                        "The 0.58 Mt excess is retained, not scaled away."
                    ),
                }
            )
        else:
            if company_id == "POSCO":
                status = "not_available; facility activity is allocated and no like-for-like reported production denominator acquired"
                metric = "steel_product_activity_proxy"
                unit = "t steel product/year"
                quality = "D"
                value_type = "Not_available|Allocated"
            else:
                status = "not_available; facility production and like-for-like company denominator not acquired"
                metric = "production_not_available"
                unit = "NA"
                quality = "NA"
                value_type = "Not_available"
            common.update(
                {
                    "reporting_period": company_seeds[0]["baseline_period"],
                    "production_metric": metric,
                    "company_reported_production": "NA",
                    "unit": unit,
                    "raw_reconciliation_ratio": "NA",
                    "absolute_difference": "NA",
                    "production_coverage_ratio": "NA",
                    "coverage_status": status,
                    "value_type": value_type,
                    "quality_flag": quality,
                    "source_id": source_ids or "NA",
                    "formula_or_method": "No coverage ratio calculated without like-for-like reported numerator and denominator",
                    "boundary_note": "Unknown production coverage is not zero-filled.",
                }
            )
        production_rows.append(common)

    facility_id = "KR_POSCO_GWANGYANG"
    seed = seed_by_id[facility_id]
    mapping = mapping_by_id[facility_id]
    capacity_fact = facts_by_id["POSCO_GW_EAF_CAPACITY"]
    investment_fact = facts_by_id["POSCO_GW_EAF_INVESTMENT"]
    scrap_fact = facts_by_id["POSCO_GW_EAF_SCRAP_SHARE"]
    total_scrap_fact = facts_by_id["POSCO_TOTAL_SCRAP_2024"]
    purchased_scrap_fact = facts_by_id["POSCO_PURCHASED_SCRAP_2024"]
    capacity = _decimal(capacity_fact["base"], "EAF capacity")
    activity = {
        case: _decimal(seed[f"facility_activity_{case}"], "Gwangyang activity")
        for case in ("low", "base", "high")
    }
    scrap_share = _decimal(scrap_fact["base"], "planned scrap share")
    implied_scrap = capacity * scrap_share
    total_scrap = _decimal(total_scrap_fact["base"], "total scrap")
    purchased_scrap = _decimal(purchased_scrap_fact["base"], "purchased scrap")
    sources = _join_labels(
        (
            seed["activity_source_id"],
            mapping["source_id"],
            capacity_fact["source_id"],
            investment_fact["source_id"],
            scrap_fact["source_id"],
            total_scrap_fact["source_id"],
            purchased_scrap_fact["source_id"],
        )
    )
    constraint_rows: list[dict[str, object]] = [
        {
            "constraint_id": "POSCO_GW_EAF_CAPACITY_SCRAP_2026",
            "company_id": "POSCO",
            "facility_id": facility_id,
            "selected_route": mapping["selected_route"],
            "project_status": "construction_completed_and_low_carbon_steel_production_started",
            "evidence_date": "2026-06-22",
            "official_route_capacity_t_per_year": capacity,
            "official_project_investment_krw": _decimal(
                investment_fact["base"], "project investment"
            ),
            "facility_activity_low_t_per_year": activity["low"],
            "facility_activity_base_t_per_year": activity["base"],
            "facility_activity_high_t_per_year": activity["high"],
            "project_capacity_coverage_low": capacity / activity["high"],
            "project_capacity_coverage_base": capacity / activity["base"],
            "project_capacity_coverage_high": capacity / activity["low"],
            "uncovered_activity_low_t_per_year": activity["low"] - capacity,
            "uncovered_activity_base_t_per_year": activity["base"] - capacity,
            "uncovered_activity_high_t_per_year": activity["high"] - capacity,
            "full_route_scale_multiple_low": activity["low"] / capacity,
            "full_route_scale_multiple_base": activity["base"] / capacity,
            "full_route_scale_multiple_high": activity["high"] / capacity,
            "planned_scrap_share": scrap_share,
            "implied_project_scrap_demand_t_per_year": implied_scrap,
            "share_of_2024_total_scrap_usage": implied_scrap / total_scrap,
            "share_of_2024_purchased_scrap_usage": implied_scrap / purchased_scrap,
            "constraint_status": "physically_constrained_for_full_facility_transition; additional route capacity and scrap supply required",
            "capital_allocation_action": (
                "separate the completed 2.5 Mt EAF from unannounced additional buildout before "
                "treating full Gwangyang CAPEX or abatement as investable"
            ),
            "capacity_unit": "t steel/year",
            "investment_currency": "KRW",
            "investment_price_year": investment_fact["price_year"],
            "value_type": "Derived_from_reported_and_allocated",
            "quality_flag": "D",
            "source_id": sources,
            "formula_or_method": (
                "coverage low/base/high = official 2.5 Mt capacity divided by allocated activity "
                "high/base/low; uncovered activity = allocated activity minus capacity; scrap demand "
                "= capacity x reported planned 80% scrap share"
            ),
            "boundary_note": (
                "Capacity, investment, completion and planned mix are official. Full-works activity "
                "is an allocated steel-product proxy, not reported Gwangyang crude-steel production; "
                "ratios are a physical-screening warning rather than achieved utilisation."
            ),
        }
    ]
    return production_rows, constraint_rows


def write_report(
    production_rows: list[dict[str, object]],
    constraint_rows: list[dict[str, object]],
    output: Path,
) -> None:
    nsc = next(row for row in production_rows if row["company_id"] == "NIPPON_STEEL")
    constraint = constraint_rows[0]
    lines = [
        "# Production coverage and physical-constraint upgrade",
        "",
        "## Output-first result",
        "",
        f"Nippon Steel is the first company with publishable production coverage: 11 official FY2024 works/area values sum to {D(str(nsc['facility_activity_sum'])) / D('1000000'):.2f} Mt crude steel versus the separate company statement of {D(str(nsc['company_reported_production'])) / D('1000000'):.2f} Mt. The raw reconciliation is {D(str(nsc['raw_reconciliation_ratio'])):.2%}, a 0.58 Mt excess that remains visible but falls within the protocol's ±2% reported-production tolerance. Published coverage is therefore 100%, quality B, not 101.69%.",
        "",
        "POSCO, LOTTE Chemical and Mitsui Chemicals remain `NA`, not zero: POSCO facility activity is an allocated steel-product proxy without a like-for-like reported company denominator; the chemical companies lack facility production on the current boundary.",
        "",
        "## Gwangyang EAF constraint",
        "",
        f"POSCO's official June 2026 update confirms that the Gwangyang EAF is completed and producing, with 2.5 Mt/year capacity and approximately KRW 600bn cumulative investment. That project covers only {D(str(constraint['project_capacity_coverage_base'])):.2%} of the current 19.02 Mt/year base Gwangyang activity proxy, with a 12.05%–14.46% range. Applying the scrap-EAF route to the whole works requires {D(str(constraint['full_route_scale_multiple_base'])):.2f} times the disclosed EAF capacity and leaves 16.52 Mt/year without identified route capacity in the base case.",
        "",
        f"The Green Bond project mix is 80% scrap, implying 2.0 Mt/year scrap demand at nameplate capacity. That equals {D(str(constraint['share_of_2024_total_scrap_usage'])):.1%} of POSCO's reported 2024 total scrap use and {D(str(constraint['share_of_2024_purchased_scrap_usage'])):.1%} of reported purchased scrap. These are scale comparisons, not proof that the project will consume the same 2024 sourcing pool.",
        "",
        "## Capital-allocation implication",
        "",
        "The completed 2.5 Mt project is an observable investable block, but the current model's full-Gwangyang route is not. Future outputs must separate the disclosed project from additional unannounced EAF/HBI/scrap/power buildout. Until that is done, the by-2030 Gwangyang CAPEX and abatement totals are potential pathway requirements rather than project-backed allocations, and the facility should carry a full-transition physical-constraint warning in addition to price exposure.",
        "",
        "Auditable tables: `outputs/tables/company_production_coverage_status_mvp.csv` and `outputs/tables/facility_physical_constraint_mvp.csv`.",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--production-output", type=Path, required=True)
    parser.add_argument("--constraint-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        production, constraints = build_outputs(
            _read_csv(args.seed), _read_csv(args.mapping), _read_csv(args.facts)
        )
        _write_csv(args.production_output, production, PRODUCTION_FIELDS)
        _write_csv(args.constraint_output, constraints, CONSTRAINT_FIELDS)
        write_report(production, constraints, args.report_output)
    except ModelInputError as exc:
        print(f"cap-kj physical constraints: error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
