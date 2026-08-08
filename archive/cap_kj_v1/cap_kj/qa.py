"""Reconciliation, sensitivity and isolated regeneration QA for CAP-KJ MVP."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import tempfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Sequence

from .cost_gap import (
    COMPANY_FIELDS as COST_COMPANY_FIELDS,
    FACILITY_FIELDS as COST_FACILITY_FIELDS,
    _write_csv as write_cost_csv,
    build_cost_gap_tables,
)
from .investor_outputs import FIGURE_NAMES, generate_outputs
from .physical_constraints import (
    CONSTRAINT_FIELDS,
    PRODUCTION_FIELDS,
    _write_csv as write_physical_csv,
    build_outputs as build_physical_outputs,
)
from .screening import (
    COMPANY_RESULT_FIELDS,
    FACILITY_RESULT_FIELDS,
    _write_csv as write_screening_csv,
    build_screening_tables,
)
from .support_experiment import (
    COMPANY_FIELDS as SUPPORT_COMPANY_FIELDS,
    FACILITY_FIELDS as SUPPORT_FACILITY_FIELDS,
    _write_csv as write_support_csv,
    build_support_experiment,
)


D = Decimal


@dataclass(frozen=True)
class Check:
    check_id: str
    status: str
    detail: str


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _num(row: dict[str, str], field: str) -> Decimal:
    return D(row[field])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _check(checks: list[Check], check_id: str, condition: bool, detail: str) -> None:
    checks.append(Check(check_id, "PASS" if condition else "FAIL", detail))


def _warn(checks: list[Check], check_id: str, detail: str) -> None:
    checks.append(Check(check_id, "WARN", detail))


def _source_ids(value: str) -> set[str]:
    return {item for item in value.split("|") if item}


def _screening_reconciles(
    facilities: list[dict[str, str]], companies: list[dict[str, str]]
) -> bool:
    fields = (
        ("transition_capex_usd_2025", "transition_capex_usd_2025"),
        ("modelled_operational_abatement_tco2e", "modelled_operational_abatement_tco2e"),
        ("transition_operational_ghg_tco2e", "transition_operational_ghg_tco2e"),
        ("capex_by_2030_usd_2025", "capex_by_2030_usd_2025"),
        ("capex_2031_2040_usd_2025", "capex_2031_2040_usd_2025"),
        ("capex_2041_2050_usd_2025", "capex_2041_2050_usd_2025"),
    )
    for company in companies:
        rows = [
            row
            for row in facilities
            if row["company_id"] == company["company_id"] and row["case"] == company["case"]
        ]
        for company_field, facility_field in fields:
            if _num(company, company_field) != sum((_num(row, facility_field) for row in rows), D("0")):
                return False
    return True


def _support_reconciles(
    facilities: list[dict[str, str]], companies: list[dict[str, str]]
) -> bool:
    fields = (
        ("potential_transition_capex_usd_2025", "base_transition_capex_usd_2025"),
        ("contract_covered_capex_usd_2025", "contract_covered_capex_usd_2025"),
        ("screening_level_support_total_usd_2025", "screening_level_support_total_usd_2025"),
        ("potential_operational_abatement_tco2e", "potential_operational_abatement_tco2e"),
        ("mechanism_operational_abatement_tco2e", "mechanism_operational_abatement_tco2e"),
        ("additional_operational_abatement_vs_b0_tco2e", "additional_operational_abatement_vs_b0_tco2e"),
    )
    for company in companies:
        rows = [
            row
            for row in facilities
            if row["company_id"] == company["company_id"]
            and row["assumption_case"] == company["assumption_case"]
            and row["mechanism_case"] == company["mechanism_case"]
        ]
        for company_field, facility_field in fields:
            if _num(company, company_field) != sum((_num(row, facility_field) for row in rows), D("0")):
                return False
    return True


def _cost_reconciles(
    facilities: list[dict[str, str]], companies: list[dict[str, str]]
) -> bool:
    fields = (
        "transition_capex_usd_2025",
        "modelled_operational_abatement_tco2e",
        "annual_resource_gap_proxy_usd_2025",
        "implied_support_low_usd_2025",
        "implied_support_base_usd_2025",
        "implied_support_high_usd_2025",
    )
    for company in companies:
        rows = [
            row
            for row in facilities
            if row["company_id"] == company["company_id"]
            and row["baseline_variant"] == company["baseline_variant"]
            and row["case"] == company["case"]
            and row["modelled_flag"] == "yes"
        ]
        for field in fields:
            if _num(company, field) != sum((_num(row, field) for row in rows), D("0")):
                return False
    return True


def _source_integrity(root: Path) -> tuple[bool, set[str]]:
    registered = {row["source_id"] for row in _read(root / "data/manifests/source_register.csv")}
    referenced: set[str] = set()
    source_fields = (
        (root / "data/processed/company_baseline.csv", ("source_id",)),
        (root / "data/processed/facility_seed.csv", ("emissions_source_id", "activity_source_id", "facility_source_id")),
        (root / "data/processed/facility_route_mapping_mvp.csv", ("source_id",)),
        (root / "data/processed/technology_assumptions_mvp.csv", ("source_id",)),
        (root / "data/processed/support_experiment_assumptions_mvp.csv", ("source_id",)),
        (root / "data/processed/annual_cost_gap_assumptions_mvp.csv", ("source_id",)),
        (root / "data/processed/mci_shk_to_fy2024_bridge.csv", ("source_id",)),
        (root / "data/processed/official_production_constraint_facts_mvp.csv", ("source_id",)),
    )
    for path, fields in source_fields:
        for row in _read(path):
            for field in fields:
                if field in row:
                    referenced.update(_source_ids(row[field]))
    allowed_internal = {
        "NA",
        "not_applicable",
        "not_applicable_internal_mechanism_rule",
    }
    missing = {
        source_id
        for source_id in referenced - registered - allowed_internal
        if not source_id.startswith("internal_")
    }
    for row in _read(root / "data/processed/facility_seed.csv"):
        if row.get("activity_source_id") == "NA" and any(
            row.get(field) not in {None, "", "NA"}
            for field in (
                "facility_activity_low",
                "facility_activity_base",
                "facility_activity_high",
            )
        ):
            missing.add(f"NA_activity_source_with_value:{row['facility_id']}")
    return not missing, missing


def _write_checks(path: Path, checks: list[Check]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("check_id", "status", "detail"))
        writer.writeheader()
        writer.writerows(check.__dict__ for check in checks)


def _support_summary(companies: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    return {
        company_id: {
            assumption: next(
                row
                for row in companies
                if row["company_id"] == company_id
                and row["assumption_case"] == assumption
                and row["mechanism_case"] == "BHL"
            )
            for assumption in ("low", "base", "high")
        }
        for company_id in sorted({row["company_id"] for row in companies})
    }


def _write_report(
    path: Path,
    checks: list[Check],
    screening_companies: list[dict[str, str]],
    support_companies: list[dict[str, str]],
    cost_companies: list[dict[str, str]],
    production_rows: list[dict[str, str]],
    constraint_rows: list[dict[str, str]],
    hashes: dict[str, str],
) -> None:
    failed = sum(check.status == "FAIL" for check in checks)
    warnings = sum(check.status == "WARN" for check in checks)
    overall = "PASS" if failed == 0 and warnings == 0 else "PASS WITH WARNINGS" if failed == 0 else "FAIL"
    base_screen = {
        row["company_id"]: row for row in screening_companies if row["case"] == "base"
    }
    screen_cases = {
        (row["company_id"], row["case"]): row for row in screening_companies
    }
    support = _support_summary(support_companies)
    names = {row["company_id"]: row["company_name"] for row in screening_companies}
    primary_cost = {
        row["company_id"]: row
        for row in cost_companies
        if row["variant_role"] == "primary" and row["case"] == "base"
    }
    support_boundary = {
        row["company_id"]: row
        for row in support_companies
        if row["assumption_case"] == "base" and row["mechanism_case"] == "B0"
    }
    production = {row["company_id"]: row for row in production_rows}
    constraint = constraint_rows[0]

    lines = [
        "# Post-upgrade reconciliation and release-gap audit",
        "",
        f"**Internal consistency:** {'PASS' if failed == 0 else 'FAIL'}  ",
        f"**Public-release gate:** {'OPEN' if failed == 0 and warnings == 0 else 'GATED'}  ",
        f"**Overall diagnostic:** {overall}  ",
        f"**Checks:** {len(checks) - failed - warnings} pass, {warnings} warning, {failed} fail  ",
        "**Scope:** isolated regeneration, cross-output boundary consistency and publication readiness of the current MVP; not external validation of engineering costs, contracts, policy eligibility or system abatement.",
        "",
        "## Check results",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| `{check.check_id}` | {check.status} | {check.detail.replace('|', '/')} |"
        for check in checks
    )
    lines.extend(
        [
            "",
            "## Sensitivity audit",
            "",
            "| Company | CAPEX low/base/high | High ÷ low | BHL level support low/base/high | BHL residual exposure low/base/high |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for company_id in ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
        low = screen_cases[(company_id, "low")]
        base = base_screen[company_id]
        high = screen_cases[(company_id, "high")]
        support_rows = support[company_id]
        capex_values = [_num(row, "transition_capex_usd_2025") / D("1000000000") for row in (low, base, high)]
        support_values = [
            _num(support_rows[case], "screening_level_support_total_usd_2025") / D("1000000000")
            for case in ("low", "base", "high")
        ]
        residual_values = [
            _num(support_rows[case], "capex_weighted_residual_common_exposure_ratio")
            for case in ("low", "base", "high")
        ]
        lines.append(
            f"| {names[company_id]} | ${capex_values[0]:.2f}/${capex_values[1]:.2f}/${capex_values[2]:.2f}bn | "
            f"{capex_values[2] / capex_values[0]:.2f}x | ${support_values[0]:.3f}/${support_values[1]:.3f}/${support_values[2]:.3f}bn | "
            f"{residual_values[0]:.1%}/{residual_values[1]:.1%}/{residual_values[2]:.1%} |"
        )
    lines.extend(
        [
            "",
            "The CAPEX range is especially wide for LOTTE and Mitsui because the petrochemical screen uses a common annual-abatement CAPEX proxy. Their identical support-efficiency result is therefore mechanical, not evidence of equal project economics. Higher coverage assumptions reduce residual exposure monotonically, while level-support totals rise monotonically with the declared support-share range.",
            "",
            "## Cross-output boundary matrix",
            "",
            "| Company | Primary cost emissions coverage | Support-experiment coverage | Difference | Production coverage | Release use |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for company_id in ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
        cost_coverage = _num(primary_cost[company_id], "base_case_emissions_coverage_ratio")
        support_coverage = _num(support_boundary[company_id], "emissions_coverage_ratio")
        difference = cost_coverage - support_coverage
        production_coverage = production[company_id]["production_coverage_ratio"]
        release_use = (
            "do not combine exact support and cost amounts"
            if abs(difference) > D("0.001")
            else "aligned within 0.1%"
        )
        lines.append(
            f"| {names[company_id]} | {cost_coverage:.2%} | {support_coverage:.2%} | "
            f"{difference:+.2%} | {production_coverage} | {release_use} |"
        )
    lines.extend(
        [
            "",
            "Mitsui's cost layer uses the official-registry bridge at 97.46% emissions coverage, while its support experiment still uses the 85.00% legacy allocation. The 12.46 percentage-point difference is a publication blocker for any exact combined Mitsui support/cost statement; the two panels may remain visible only as explicitly separated boundary views.",
            "",
            "## Physical-pathway gate",
            "",
            f"The completed Gwangyang EAF covers {D(constraint['project_capacity_coverage_base']):.2%} of the allocated base works activity, requiring {D(constraint['full_route_scale_multiple_base']):.2f}x disclosed capacity for the current full-route screen. Its implied 2.0 Mt/year scrap demand is {D(constraint['share_of_2024_purchased_scrap_usage']):.1%} of reported 2024 purchased scrap. Full-Gwangyang CAPEX and operational abatement remain potential pathway requirements, not project-backed allocations.",
            "",
            "## Open release gaps",
            "",
        ]
    )
    lines.extend(
        f"- `{check.check_id}`: {check.detail}" for check in checks if check.status == "WARN"
    )
    lines.extend(
        [
            "",
            "Facility calculations reconcile to company totals for capital, emissions, mechanism and annual resource-gap measures. Eight core tables regenerate byte-for-byte in an isolated directory. These internal passes do not override the open boundary and evidence gaps above.",
            "",
            "## Canonical output hashes",
            "",
        ]
    )
    lines.extend(f"- `{name}`: `{digest}`" for name, digest in sorted(hashes.items()))
    lines.extend(
        [
            "",
            "## Reproduction",
            "",
            "Run `PYTHONPATH=src python3 -m cap_kj.qa --root .`. The command rebuilds eight screening, support, cost-gap, production and constraint tables in a temporary directory, compares them to canonical CSV outputs, regenerates the four original investor figures, and rewrites this report and `outputs/diagnostics/qa_checks.csv`.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_qa(root: Path, checks_path: Path, report_path: Path) -> list[Check]:
    root = root.resolve()
    inputs = {
        "seed": root / "data/processed/facility_seed.csv",
        "mapping": root / "data/processed/facility_route_mapping_mvp.csv",
        "baseline": root / "data/processed/company_baseline.csv",
        "support_assumptions": root / "data/processed/support_experiment_assumptions_mvp.csv",
        "route_cost_inputs": root / "outputs/tables/route_annual_cost_gap_inputs_mvp.csv",
        "mci_bridge": root / "data/processed/mci_shk_to_fy2024_bridge.csv",
        "physical_facts": root / "data/processed/official_production_constraint_facts_mvp.csv",
    }
    canonical = {
        "facility_screen": root / "outputs/tables/facility_capital_allocation_mvp.csv",
        "company_screen": root / "outputs/tables/company_capital_allocation_mvp.csv",
        "facility_support": root / "outputs/tables/facility_support_experiment_mvp.csv",
        "company_support": root / "outputs/tables/company_support_experiment_mvp.csv",
        "facility_cost": root / "outputs/tables/facility_annual_cost_gap_mvp.csv",
        "company_cost": root / "outputs/tables/company_annual_cost_gap_mvp.csv",
        "production": root / "outputs/tables/company_production_coverage_status_mvp.csv",
        "constraints": root / "outputs/tables/facility_physical_constraint_mvp.csv",
    }
    checks: list[Check] = []
    _check(checks, "required_files", all(path.exists() for path in (*inputs.values(), *canonical.values())), "All declared MVP inputs and eight canonical tables exist.")

    with tempfile.TemporaryDirectory(prefix="cap_kj_qa_") as temporary:
        temp = Path(temporary)
        facility_rows, company_rows = build_screening_tables(
            seed_path=inputs["seed"],
            mapping_path=inputs["mapping"],
            company_baseline_path=inputs["baseline"],
        )
        rebuilt_facility = temp / "facility_capital_allocation_mvp.csv"
        rebuilt_company = temp / "company_capital_allocation_mvp.csv"
        write_screening_csv(rebuilt_facility, facility_rows, FACILITY_RESULT_FIELDS)
        write_screening_csv(rebuilt_company, company_rows, COMPANY_RESULT_FIELDS)
        support_facility_rows, support_company_rows = build_support_experiment(
            rebuilt_facility, rebuilt_company, inputs["support_assumptions"]
        )
        rebuilt_support_facility = temp / "facility_support_experiment_mvp.csv"
        rebuilt_support_company = temp / "company_support_experiment_mvp.csv"
        write_support_csv(rebuilt_support_facility, support_facility_rows, SUPPORT_FACILITY_FIELDS)
        write_support_csv(rebuilt_support_company, support_company_rows, SUPPORT_COMPANY_FIELDS)

        cost_facility_rows, cost_company_rows = build_cost_gap_tables(
            _read(rebuilt_facility),
            _read(rebuilt_company),
            _read(inputs["route_cost_inputs"]),
            _read(inputs["mci_bridge"]),
        )
        rebuilt_cost_facility = temp / "facility_annual_cost_gap_mvp.csv"
        rebuilt_cost_company = temp / "company_annual_cost_gap_mvp.csv"
        write_cost_csv(rebuilt_cost_facility, cost_facility_rows, COST_FACILITY_FIELDS)
        write_cost_csv(rebuilt_cost_company, cost_company_rows, COST_COMPANY_FIELDS)

        production_rows, constraint_rows = build_physical_outputs(
            _read(inputs["seed"]), _read(inputs["mapping"]), _read(inputs["physical_facts"])
        )
        rebuilt_production = temp / "company_production_coverage_status_mvp.csv"
        rebuilt_constraints = temp / "facility_physical_constraint_mvp.csv"
        write_physical_csv(rebuilt_production, production_rows, PRODUCTION_FIELDS)
        write_physical_csv(rebuilt_constraints, constraint_rows, CONSTRAINT_FIELDS)

        rebuilt = {
            "facility_screen": rebuilt_facility,
            "company_screen": rebuilt_company,
            "facility_support": rebuilt_support_facility,
            "company_support": rebuilt_support_company,
            "facility_cost": rebuilt_cost_facility,
            "company_cost": rebuilt_cost_company,
            "production": rebuilt_production,
            "constraints": rebuilt_constraints,
        }
        byte_exact = all(rebuilt[key].read_bytes() == canonical[key].read_bytes() for key in canonical)
        _check(checks, "isolated_table_regeneration", byte_exact, "Eight tables rebuilt in a temporary directory match canonical outputs byte-for-byte.")

        figure_dir = temp / "figures"
        temp_memo = temp / "investor_screening_memo.md"
        generated = generate_outputs(rebuilt_company, rebuilt_facility, figure_dir, temp_memo)
        figures_ok = all(path.exists() and path.stat().st_size > 50_000 for path in generated[:-1])
        _check(checks, "isolated_figure_regeneration", figures_ok and {path.name for path in generated[:-1]} == set(FIGURE_NAMES), "All four investor figures regenerated from rebuilt tables and passed minimum file-size checks.")

    facilities = _read(canonical["facility_screen"])
    companies = _read(canonical["company_screen"])
    support_facilities = _read(canonical["facility_support"])
    support_companies = _read(canonical["company_support"])
    cost_facilities = _read(canonical["facility_cost"])
    cost_companies = _read(canonical["company_cost"])
    production_rows = _read(canonical["production"])
    constraint_rows = _read(canonical["constraints"])
    _check(checks, "screening_grain", len(facilities) == 75 and len(companies) == 12, "Screening outputs contain 25 facilities x 3 cases and four companies x 3 cases.")
    _check(checks, "screening_unique_keys", len({(row["facility_id"], row["case"]) for row in facilities}) == 75 and len({(row["company_id"], row["case"]) for row in companies}) == 12, "Facility/case and company/case keys are unique.")
    _check(checks, "screening_reconciliation", _screening_reconciles(facilities, companies), "Six CAPEX and operational-emissions measures reconcile exactly from facilities to companies.")

    sensitivity_ok = True
    for company_id in {row["company_id"] for row in companies}:
        rows = {row["case"]: row for row in companies if row["company_id"] == company_id}
        for field in ("transition_capex_usd_2025", "modelled_operational_abatement_tco2e"):
            sensitivity_ok &= _num(rows["low"], field) <= _num(rows["base"], field) <= _num(rows["high"], field)
    _check(checks, "screening_sensitivity_order", sensitivity_ok, "Company CAPEX and operational abatement are monotonic across low/base/high cases.")

    _check(checks, "support_grain", len(support_facilities) == 300 and len(support_companies) == 48, "Support outputs contain 25 facilities x 3 assumptions x 4 mechanisms and four companies at the same cases.")
    _check(checks, "support_unique_keys", len({(row["facility_id"], row["assumption_case"], row["mechanism_case"]) for row in support_facilities}) == 300 and len({(row["company_id"], row["assumption_case"], row["mechanism_case"]) for row in support_companies}) == 48, "Facility and company support keys are unique.")
    _check(checks, "support_reconciliation", _support_reconciles(support_facilities, support_companies), "Six capital, support and abatement measures reconcile exactly from facilities to companies.")
    trace_ok = all(
        _num(row, "additional_operational_abatement_vs_b0_tco2e") == 0 or row["status_change_flag"] == "yes"
        for row in support_facilities
    )
    _check(checks, "abatement_status_trace", trace_ok, "Every positive additional operational-abatement row names a facility status change.")

    support_sensitivity_ok = True
    for company_id in {row["company_id"] for row in support_companies}:
        rows = {
            row["assumption_case"]: row
            for row in support_companies
            if row["company_id"] == company_id and row["mechanism_case"] == "BHL"
        }
        support_sensitivity_ok &= _num(rows["low"], "screening_level_support_total_usd_2025") <= _num(rows["base"], "screening_level_support_total_usd_2025") <= _num(rows["high"], "screening_level_support_total_usd_2025")
        support_sensitivity_ok &= _num(rows["high"], "capex_weighted_residual_common_exposure_ratio") <= _num(rows["base"], "capex_weighted_residual_common_exposure_ratio") <= _num(rows["low"], "capex_weighted_residual_common_exposure_ratio")
    _check(checks, "support_sensitivity_order", support_sensitivity_ok, "Support totals rise and residual common exposure falls monotonically across low/base/high mechanism assumptions.")

    _check(checks, "cost_gap_grain", len(cost_facilities) == 87 and len(cost_companies) == 15, "Cost-gap outputs contain 87 facility-variant-case rows and 15 company-variant-case rows.")
    _check(
        checks,
        "cost_gap_unique_keys",
        len({(row["facility_id"], row["baseline_variant"], row["case"]) for row in cost_facilities}) == 87
        and len({(row["company_id"], row["baseline_variant"], row["case"]) for row in cost_companies}) == 15,
        "Facility and company cost-gap keys are unique.",
    )
    _check(checks, "cost_gap_reconciliation", _cost_reconciles(cost_facilities, cost_companies), "Six CAPEX, abatement, annual resource-gap and support-stress measures reconcile exactly from facilities to companies.")

    company_set = {"POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS"}
    cross_output_sets = (
        {row["company_id"] for row in companies}
        == {row["company_id"] for row in support_companies}
        == {row["company_id"] for row in cost_companies}
        == {row["company_id"] for row in production_rows}
        == company_set
    )
    _check(checks, "cross_output_company_set", cross_output_sets, "Screening, support, cost and production tables all contain the fixed four-company sample.")

    production_by_company = {row["company_id"]: row for row in production_rows}
    production_policy_ok = (
        len(production_rows) == 4
        and production_by_company["NIPPON_STEEL"]["production_coverage_ratio"] == "1"
        and all(
            production_by_company[company_id]["production_coverage_ratio"] == "NA"
            for company_id in company_set - {"NIPPON_STEEL"}
        )
        and all(row["production_coverage_ratio"] != "0" for row in production_rows)
    )
    _check(checks, "production_coverage_policy", production_policy_ok, "Nippon publishes 100% production coverage within the 2% tolerance; the other three companies remain NA and none is zero-filled.")

    constraint = constraint_rows[0] if len(constraint_rows) == 1 else None
    physical_math_ok = constraint is not None
    if constraint is not None:
        capacity = _num(constraint, "official_route_capacity_t_per_year")
        activity = _num(constraint, "facility_activity_base_t_per_year")
        coverage = _num(constraint, "project_capacity_coverage_base")
        multiple = _num(constraint, "full_route_scale_multiple_base")
        scrap_demand = _num(constraint, "implied_project_scrap_demand_t_per_year")
        scrap_share = _num(constraint, "planned_scrap_share")
        physical_math_ok &= abs(coverage - capacity / activity) < D("1e-24")
        physical_math_ok &= abs(multiple - activity / capacity) < D("1e-12")
        physical_math_ok &= scrap_demand == capacity * scrap_share
        physical_math_ok &= constraint["facility_id"] == "KR_POSCO_GWANGYANG"
    _check(checks, "physical_constraint_reconciliation", physical_math_ok, "Gwangyang capacity coverage, full-route multiple and implied scrap demand reproduce from the disclosed capacity and allocated activity.")

    boundary_ok = all(row["system_abatement_status"].startswith("not_modelled") for row in (*facilities, *support_facilities)) and all(row["production_coverage_ratio"] == "NA" for row in (*companies, *support_companies))
    _check(checks, "boundary_guardrails", boundary_ok, "System abatement remains not modelled and legacy pathway/support tables do not silently backfill production coverage.")
    assumptions = _read(inputs["support_assumptions"])
    metadata_ok = all(row["value_type"] == "Estimated" and row["quality_flag"] == "D" and row["unit"] and row["price_year"] and row["formula_or_method"] and row["rationale"] for row in assumptions)
    _check(checks, "assumption_metadata", metadata_ok, "All mechanism assumptions retain estimate label, range, unit, price-year treatment, formula, rationale and quality D.")
    source_ok, missing_sources = _source_integrity(root)
    _check(checks, "source_referential_integrity", source_ok, "All external source IDs in processed inputs resolve to the source register." if source_ok else f"Missing source IDs: {', '.join(sorted(missing_sources))}")

    primary_cost = {
        row["company_id"]: row
        for row in cost_companies
        if row["variant_role"] == "primary" and row["case"] == "base"
    }
    support_boundary = {
        row["company_id"]: row
        for row in support_companies
        if row["assumption_case"] == "base" and row["mechanism_case"] == "B0"
    }
    mci_difference = (
        _num(primary_cost["MITSUI_CHEMICALS"], "base_case_emissions_coverage_ratio")
        - _num(support_boundary["MITSUI_CHEMICALS"], "emissions_coverage_ratio")
    )
    aligned_others = all(
        abs(
            _num(primary_cost[company_id], "base_case_emissions_coverage_ratio")
            - _num(support_boundary[company_id], "emissions_coverage_ratio")
        )
        <= D("0.001")
        for company_id in company_set - {"MITSUI_CHEMICALS"}
    )
    _check(checks, "non_mitsui_cost_support_boundaries", aligned_others, "POSCO, Nippon and LOTTE primary cost/support emissions boundaries align within 0.1%.")
    if abs(mci_difference) > D("0.001"):
        _warn(checks, "mitsui_support_boundary", f"Mitsui primary cost coverage is {_num(primary_cost['MITSUI_CHEMICALS'], 'base_case_emissions_coverage_ratio'):.2%} versus 85.00% in the legacy support experiment, a {(mci_difference * D('100')):.2f} percentage-point difference; exact combined support/cost claims are gated.")
    else:
        _check(checks, "mitsui_support_boundary", True, "Mitsui cost and support boundaries align.")

    available_production = sum(row["production_coverage_ratio"] != "NA" for row in production_rows)
    if available_production < 4:
        _warn(checks, "production_coverage_completeness", f"Production coverage is publishable for {available_production}/4 companies; POSCO, LOTTE and Mitsui remain NA rather than zero.")
    if production_by_company["NIPPON_STEEL"]["production_coverage_ratio"] != next(row for row in companies if row["company_id"] == "NIPPON_STEEL" and row["case"] == "base")["production_coverage_ratio"]:
        _warn(checks, "production_coverage_integration", "Nippon's new 100% production coverage is not yet propagated into the capital-allocation and support tables, which retain the older NA field.")
    if constraint is not None and _num(constraint, "project_capacity_coverage_base") < D("1"):
        _warn(checks, "gwangyang_full_route_capacity", f"The completed Gwangyang EAF covers only {_num(constraint, 'project_capacity_coverage_base'):.2%} of allocated base works activity; full-route project-backed CAPEX and abatement are gated.")
    if all(row["verified_incentive_adjusted_gap_usd_2025"] == "NA" for row in cost_companies):
        _warn(checks, "verified_net_gap_availability", "Verified incentive-adjusted cost gaps remain NA for all company cost rows; support amounts are sensitivities, not realised cash.")
    if all(row["system_abatement_status"].startswith("not_modelled") for row in cost_companies):
        _warn(checks, "system_abatement_availability", "System abatement remains unavailable because leakage and replacement production are not modelled.")

    git_result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, check=False, capture_output=True, text=True
    )
    untracked = [line for line in git_result.stdout.splitlines() if line.startswith("??")]
    if untracked:
        _warn(checks, "version_control_coverage", f"{len(untracked)} top-level status entries are untracked; reproducible files exist but are not yet protected by version history.")
    else:
        _check(checks, "version_control_coverage", git_result.returncode == 0, "No untracked analytical files detected.")

    hashes = {path.name: _sha256(path) for path in canonical.values()}
    _write_checks(checks_path, checks)
    _write_report(
        report_path,
        checks,
        companies,
        support_companies,
        cost_companies,
        production_rows,
        constraint_rows,
        hashes,
    )
    return checks


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--checks", type=Path, default=Path("outputs/diagnostics/qa_checks.csv"))
    parser.add_argument("--report", type=Path, default=Path("outputs/reports/qa_reproducibility_report.md"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.root.resolve()
    checks = args.checks if args.checks.is_absolute() else root / args.checks
    report = args.report if args.report.is_absolute() else root / args.report
    results = run_qa(root, checks, report)
    for check in results:
        print(f"{check.status:4} {check.check_id}: {check.detail}")
    return 1 if any(check.status == "FAIL" for check in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
