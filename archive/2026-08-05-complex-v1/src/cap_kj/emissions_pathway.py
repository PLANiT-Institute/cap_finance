"""Translate company emissions envelopes into facility abatement and capital pathways."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

from .model import ModelInputError


D = Decimal
YEARS = (2025, 2030, 2040, 2050)
COMPANY_ORDER = ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS")

FACILITY_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "allocation_order",
    "facility_id",
    "facility_name",
    "selected_route",
    "decision_year",
    "dependency_status",
    "baseline_operational_ghg_tco2e",
    "gross_modelled_operational_abatement_tco2e",
    "physical_availability_ratio",
    "physically_available_operational_abatement_tco2e",
    "assigned_abatement_to_2050_gap_tco2e",
    "assigned_transition_capex_usd_2025",
    "assigned_annual_resource_gap_usd_2025",
    "assigned_abatement_per_usd_million_capex",
    "share_of_company_2050_required_reduction",
    "project_evidence_status",
    "capital_classification",
    "production_coverage_ratio",
    "emissions_coverage_ratio",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
    "boundary_note",
)

COMPANY_PATHWAY_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "year",
    "official_baseline_operational_ghg_tco2e",
    "current_policies_emissions_index",
    "current_policies_operational_ghg_tco2e",
    "net_zero_emissions_index",
    "net_zero_operational_envelope_tco2e",
    "current_policies_to_net_zero_gap_tco2e",
    "required_reduction_from_baseline_tco2e",
    "conditional_facility_abatement_tco2e",
    "conditional_facility_pathway_emissions_tco2e",
    "unclosed_gap_to_net_zero_tco2e",
    "required_reduction_closed_ratio",
    "cumulative_pathway_capex_usd_2025",
    "residual_capital_intensity_low_usd_2025_per_annual_tco2e",
    "residual_capital_intensity_base_usd_2025_per_annual_tco2e",
    "residual_capital_intensity_high_usd_2025_per_annual_tco2e",
    "implied_unclosed_capital_low_usd_2025",
    "implied_unclosed_capital_base_usd_2025",
    "implied_unclosed_capital_high_usd_2025",
    "implied_total_pathway_capital_low_usd_2025",
    "implied_total_pathway_capital_base_usd_2025",
    "implied_total_pathway_capital_high_usd_2025",
    "annual_resource_gap_at_committed_pathway_scope_usd_2025",
    "modelled_transition_facility_count",
    "emissions_coverage_ratio",
    "production_coverage_ratio",
    "pathway_status",
    "system_abatement_status",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
    "boundary_note",
)

UNCERTAINTY_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "factor",
    "factor_definition",
    "annual_resource_gap_low_usd_2025",
    "annual_resource_gap_base_usd_2025",
    "annual_resource_gap_high_usd_2025",
    "downside_change_vs_base_usd_2025",
    "upside_change_vs_base_usd_2025",
    "high_to_low_span_usd_2025",
    "high_over_low_multiple",
    "pathway_scope_abatement_tco2e",
    "unit",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
    "boundary_note",
)


def _read(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        raise ModelInputError(f"cannot read {path}: {exc}") from exc


def _decimal(raw: str, label: str) -> Decimal:
    try:
        value = D(raw)
    except (InvalidOperation, TypeError) as exc:
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


def _write(path: Path, rows: list[dict[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _serialise(row[field]) for field in fields})


def _join(values: Iterable[str]) -> str:
    result: set[str] = set()
    for value in values:
        result.update(part for part in value.split("|") if part and part != "NA")
    return "|".join(sorted(result))


def _validate_anchors(rows: list[dict[str, str]]) -> dict[tuple[str, str, int], dict[str, str]]:
    anchors = {(row["sector"], row["scenario"], int(row["year"])): row for row in rows}
    if len(anchors) != len(rows):
        raise ModelInputError("duplicate sector/scenario/year pathway anchor")
    expected = {
        (sector, scenario, year)
        for sector in ("steel", "petrochemicals")
        for scenario in ("current_policies_proxy", "net_zero_1p5c_proxy")
        for year in YEARS
    }
    if set(anchors) != expected:
        raise ModelInputError("pathway anchors must cover two sectors, two scenarios and four years")
    for row in rows:
        values = [_decimal(row[f"emissions_index_{case}"], row["anchor_id"]) for case in ("low", "base", "high")]
        if not values[0] <= values[1] <= values[2] or values[0] < 0:
            raise ModelInputError(f"invalid pathway range: {row['anchor_id']}")
        if not row["source_id"] or not row["formula_or_method"] or not row["boundary_note"]:
            raise ModelInputError(f"missing pathway metadata: {row['anchor_id']}")
    return anchors


def build_pathway_tables(
    facility_cost_rows: list[dict[str, str]],
    company_cost_rows: list[dict[str, str]],
    production_rows: list[dict[str, str]],
    constraint_rows: list[dict[str, str]],
    anchor_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Build facility gap-to-capital assignments and four-company trajectories."""

    anchors = _validate_anchors(anchor_rows)
    if len(constraint_rows) != 1:
        raise ModelInputError("expected one physical constraint row")
    constraint = constraint_rows[0]
    if constraint["facility_id"] != "KR_POSCO_GWANGYANG":
        raise ModelInputError("physical constraint must be the Gwangyang EAF row")
    physical_ratio = _decimal(constraint["project_capacity_coverage_base"], "Gwangyang coverage")
    if not D("0") < physical_ratio < D("1"):
        raise ModelInputError("Gwangyang physical coverage must be between zero and one")

    primary_base_cost = {
        row["company_id"]: row
        for row in company_cost_rows
        if row["variant_role"] == "primary" and row["case"] == "base"
    }
    production = {row["company_id"]: row for row in production_rows}
    if set(primary_base_cost) != set(COMPANY_ORDER) or set(production) != set(COMPANY_ORDER):
        raise ModelInputError("company cost and production tables must contain the fixed sample")

    facility_assignments: list[dict[str, object]] = []
    company_facilities: dict[str, list[dict[str, object]]] = {}
    for company_id in COMPANY_ORDER:
        company = primary_base_cost[company_id]
        sector = company["sector"]
        baseline = _decimal(company["official_company_baseline_tco2e"], "company baseline")
        nz_2050 = _decimal(
            anchors[(sector, "net_zero_1p5c_proxy", 2050)]["emissions_index_base"],
            "2050 net-zero index",
        )
        required_2050 = baseline * (D("1") - nz_2050)
        candidates = [
            row
            for row in facility_cost_rows
            if row["company_id"] == company_id
            and row["variant_role"] == "primary"
            and row["case"] == "base"
            and row["modelled_flag"] == "yes"
        ]
        if not candidates:
            raise ModelInputError(f"no modelled primary facilities for {company_id}")
        candidates.sort(
            key=lambda row: (
                int(row["decision_horizon"]),
                _decimal(row["annual_resource_gap_proxy_usd_2025_per_operational_tco2e_abated"], "unit gap"),
                row["facility_id"],
            )
        )
        remaining = required_2050
        assigned_rows: list[dict[str, object]] = []
        for order, row in enumerate(candidates, start=1):
            gross_abatement = _decimal(row["modelled_operational_abatement_tco2e"], "gross abatement")
            capex = _decimal(row["transition_capex_usd_2025"], "transition CAPEX")
            annual_gap = _decimal(row["annual_resource_gap_proxy_usd_2025"], "annual gap")
            availability = physical_ratio if row["facility_id"] == "KR_POSCO_GWANGYANG" else D("1")
            available = gross_abatement * availability
            assigned = min(available, remaining)
            assignment_ratio = assigned / gross_abatement
            assigned_capex = capex * assignment_ratio
            assigned_gap = annual_gap * assignment_ratio
            remaining -= assigned
            source_id = row["source_id"]
            project_status = "route_capacity_not_project_verified"
            capital_class = row["facility_status"]
            quality = "D"
            if row["facility_id"] == "KR_POSCO_GWANGYANG":
                source_id = _join((source_id, constraint["source_id"]))
                project_status = "official_2p5mt_capacity_and_krw600bn_investment_observed"
                capital_class = "physically_constrained_beyond_disclosed_project"
            assigned_row: dict[str, object] = {
                "company_id": company_id,
                "company_name": company["company_name"],
                "country": company["country"],
                "sector": sector,
                "allocation_order": order,
                "facility_id": row["facility_id"],
                "facility_name": row["facility_name"],
                "selected_route": row["selected_route"],
                "decision_year": int(row["decision_horizon"]),
                "dependency_status": row["facility_status"],
                "baseline_operational_ghg_tco2e": _decimal(row["baseline_operational_ghg_tco2e"], "facility baseline"),
                "gross_modelled_operational_abatement_tco2e": gross_abatement,
                "physical_availability_ratio": availability,
                "physically_available_operational_abatement_tco2e": available,
                "assigned_abatement_to_2050_gap_tco2e": assigned,
                "assigned_transition_capex_usd_2025": assigned_capex,
                "assigned_annual_resource_gap_usd_2025": assigned_gap,
                "assigned_abatement_per_usd_million_capex": assigned / (assigned_capex / D("1000000")) if assigned_capex else "NA",
                "share_of_company_2050_required_reduction": assigned / required_2050,
                "project_evidence_status": project_status,
                "capital_classification": capital_class,
                "production_coverage_ratio": production[company_id]["production_coverage_ratio"],
                "emissions_coverage_ratio": _decimal(company["base_case_emissions_coverage_ratio"], "emissions coverage"),
                "currency": "USD",
                "price_year": "2025 screening proxy",
                "value_type": "allocated",
                "quality_flag": quality,
                "source_id": source_id,
                "formula_or_method": "available abatement = base modelled operational abatement x physical availability; assignment follows decision year then annual resource-gap efficiency and is capped by the company 2050 reduction requirement; capital and annual gap scale pro rata",
                "boundary_note": "Conditional operational Scope 1+2 pathway only. Except for the disclosed Gwangyang block, route capacity is not project-verified; replacement production and system abatement remain unmodelled.",
            }
            facility_assignments.append(assigned_row)
            assigned_rows.append(assigned_row)
        company_facilities[company_id] = assigned_rows

    pathway_rows: list[dict[str, object]] = []
    for company_id in COMPANY_ORDER:
        company = primary_base_cost[company_id]
        sector = company["sector"]
        baseline = _decimal(company["official_company_baseline_tco2e"], "company baseline")
        facilities = company_facilities[company_id]
        total_assigned_abatement = sum(
            (_decimal(str(row["assigned_abatement_to_2050_gap_tco2e"]), "assigned abatement") for row in facilities),
            D("0"),
        )
        total_assigned_capex = sum(
            (_decimal(str(row["assigned_transition_capex_usd_2025"]), "assigned CAPEX") for row in facilities),
            D("0"),
        )
        if total_assigned_abatement <= 0:
            raise ModelInputError(f"assigned pathway abatement must be positive for {company_id}")
        identified_capital_intensity = total_assigned_capex / total_assigned_abatement
        company_case_rows = [
            row
            for row in company_cost_rows
            if row["company_id"] == company_id and row["variant_role"] == "primary"
        ]
        if {row["case"] for row in company_case_rows} != {"low", "base", "high"}:
            raise ModelInputError(f"missing company capital intensity cases for {company_id}")
        case_intensities = {
            row["case"]: _decimal(row["transition_capex_usd_2025"], "company CAPEX")
            / _decimal(row["modelled_operational_abatement_tco2e"], "company abatement")
            for row in company_case_rows
        }
        base_case_intensity = case_intensities["base"]
        intensity_low = identified_capital_intensity * min(case_intensities.values()) / base_case_intensity
        intensity_base = identified_capital_intensity
        intensity_high = identified_capital_intensity * max(case_intensities.values()) / base_case_intensity
        sources = _join(
            [row["source_id"] for row in facilities]
            + [
                anchors[(sector, "current_policies_proxy", 2025)]["source_id"],
                anchors[(sector, "net_zero_1p5c_proxy", 2025)]["source_id"],
            ]
        )
        for year in YEARS:
            cp_index = _decimal(
                anchors[(sector, "current_policies_proxy", year)]["emissions_index_base"],
                "current policies index",
            )
            nz_index = _decimal(
                anchors[(sector, "net_zero_1p5c_proxy", year)]["emissions_index_base"],
                "net-zero index",
            )
            cp_emissions = baseline * cp_index
            nz_emissions = baseline * nz_index
            available_rows = [row for row in facilities if int(row["decision_year"]) <= year]
            abatement = sum(
                (_decimal(str(row["assigned_abatement_to_2050_gap_tco2e"]), "assigned abatement") for row in available_rows),
                D("0"),
            )
            pathway_emissions = max(D("0"), baseline - abatement)
            required_reduction = max(D("0"), baseline - nz_emissions)
            unclosed = max(D("0"), pathway_emissions - nz_emissions)
            closed_ratio: Decimal = (
                min(D("1"), abatement / required_reduction) if required_reduction else D("1")
            )
            capex = sum(
                (_decimal(str(row["assigned_transition_capex_usd_2025"]), "assigned CAPEX") for row in available_rows),
                D("0"),
            )
            implied_unclosed_low = unclosed * intensity_low
            implied_unclosed_base = unclosed * intensity_base
            implied_unclosed_high = unclosed * intensity_high
            annual_gap = sum(
                (_decimal(str(row["assigned_annual_resource_gap_usd_2025"]), "assigned annual gap") for row in available_rows),
                D("0"),
            )
            status = "on_envelope_at_common_start" if year == 2025 else (
                "identified_pathway_closes_envelope" if unclosed == 0 else "unclosed_emissions_gap"
            )
            if company_id == "POSCO" and year >= 2030:
                status += "; Gwangyang_full_route_physically_constrained"
            pathway_rows.append(
                {
                    "company_id": company_id,
                    "company_name": company["company_name"],
                    "country": company["country"],
                    "sector": sector,
                    "year": year,
                    "official_baseline_operational_ghg_tco2e": baseline,
                    "current_policies_emissions_index": cp_index,
                    "current_policies_operational_ghg_tco2e": cp_emissions,
                    "net_zero_emissions_index": nz_index,
                    "net_zero_operational_envelope_tco2e": nz_emissions,
                    "current_policies_to_net_zero_gap_tco2e": max(D("0"), cp_emissions - nz_emissions),
                    "required_reduction_from_baseline_tco2e": required_reduction,
                    "conditional_facility_abatement_tco2e": abatement,
                    "conditional_facility_pathway_emissions_tco2e": pathway_emissions,
                    "unclosed_gap_to_net_zero_tco2e": unclosed,
                    "required_reduction_closed_ratio": closed_ratio,
                    "cumulative_pathway_capex_usd_2025": capex,
                    "residual_capital_intensity_low_usd_2025_per_annual_tco2e": intensity_low,
                    "residual_capital_intensity_base_usd_2025_per_annual_tco2e": intensity_base,
                    "residual_capital_intensity_high_usd_2025_per_annual_tco2e": intensity_high,
                    "implied_unclosed_capital_low_usd_2025": implied_unclosed_low,
                    "implied_unclosed_capital_base_usd_2025": implied_unclosed_base,
                    "implied_unclosed_capital_high_usd_2025": implied_unclosed_high,
                    "implied_total_pathway_capital_low_usd_2025": capex + implied_unclosed_low,
                    "implied_total_pathway_capital_base_usd_2025": capex + implied_unclosed_base,
                    "implied_total_pathway_capital_high_usd_2025": capex + implied_unclosed_high,
                    "annual_resource_gap_at_committed_pathway_scope_usd_2025": annual_gap,
                    "modelled_transition_facility_count": len(available_rows),
                    "emissions_coverage_ratio": _decimal(company["base_case_emissions_coverage_ratio"], "emissions coverage"),
                    "production_coverage_ratio": production[company_id]["production_coverage_ratio"],
                    "pathway_status": status,
                    "system_abatement_status": "not_modelled; leakage and replacement production pending",
                    "currency": "USD",
                    "price_year": "2025 screening proxy",
                    "value_type": "estimated",
                    "quality_flag": "D",
                    "source_id": sources,
                    "formula_or_method": "scenario emissions = official company baseline x sector index; conditional pathway emissions = baseline minus physically available assigned facility abatement at or before the decision year; unclosed gap = max(pathway emissions minus net-zero envelope, zero); implied residual capital = unclosed gap x the identified-pathway base capital per annual tCO2, with low/high scaled by the minimum/maximum company model-case capital intensity relative to base",
                    "boundary_note": "Sector proxies are scaled to company Scope 1+2 and are not corporate carbon budgets. Implied residual capital is a quality-D extrapolation, not an identified project or financing requirement. Conditional facility reductions are operational, not system abatement; production, leakage and replacement output are not modelled.",
                }
            )
    return facility_assignments, pathway_rows


def build_uncertainty_table(
    facility_cost_rows: list[dict[str, str]],
    company_cost_rows: list[dict[str, str]],
    route_cost_rows: list[dict[str, str]],
    facility_assignments: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Calculate one-factor and combined annual resource-gap ranges on fixed pathway scope."""

    route_inputs = {(row["route_id"], row["case"]): row for row in route_cost_rows}
    if len(route_inputs) != len(route_cost_rows):
        raise ModelInputError("duplicate route/case annual cost input")
    base_facilities = {
        row["facility_id"]: row
        for row in facility_cost_rows
        if row["variant_role"] == "primary" and row["case"] == "base" and row["modelled_flag"] == "yes"
    }
    assignment = {str(row["facility_id"]): row for row in facility_assignments}
    combined_rows = {
        (row["company_id"], row["case"]): row
        for row in company_cost_rows
        if row["variant_role"] == "primary"
    }
    results: list[dict[str, object]] = []
    definitions = {
        "capital_annualisation": "Route life, analytical discount rate and incremental fixed-OPEX factor vary together; base CAPEX, abatement and variable-resource proxy stay fixed.",
        "variable_resource": "Incremental hydrogen, electricity, scrap/feedstock and variable-OPEX proxy varies; base CAPEX, abatement and annualisation stay fixed.",
        "combined_model_case": "Existing low/base/high technology, activity, abatement and cost assumptions vary together on the fixed base pathway allocation scope.",
    }
    for company_id in COMPANY_ORDER:
        assigned = [row for row in facility_assignments if row["company_id"] == company_id]
        if not assigned:
            raise ModelInputError(f"no assigned facilities for uncertainty: {company_id}")
        name = str(assigned[0]["company_name"])
        country = str(assigned[0]["country"])
        sector = str(assigned[0]["sector"])
        total_assigned_abatement = sum(
            (_decimal(str(row["assigned_abatement_to_2050_gap_tco2e"]), "assigned abatement") for row in assigned),
            D("0"),
        )
        factor_values: dict[str, dict[str, Decimal]] = {
            factor: {case: D("0") for case in ("low", "base", "high")}
            for factor in definitions
        }
        source_values: list[str] = []
        for assigned_row in assigned:
            facility_id = str(assigned_row["facility_id"])
            base = base_facilities[facility_id]
            route = base["selected_route"]
            gross_abatement = _decimal(base["modelled_operational_abatement_tco2e"], "gross abatement")
            scope_ratio = _decimal(str(assigned_row["assigned_abatement_to_2050_gap_tco2e"]), "assigned abatement") / gross_abatement
            base_capex = _decimal(base["transition_capex_usd_2025"], "base CAPEX") * scope_ratio
            base_abatement = gross_abatement * scope_ratio
            base_input = route_inputs[(route, "base")]
            base_factor = _decimal(base_input["annual_capital_and_fixed_opex_factor"], "base annual factor")
            base_variable = _decimal(base_input["incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated"], "base variable proxy")
            for case in ("low", "base", "high"):
                case_input = route_inputs[(route, case)]
                annual_factor = _decimal(case_input["annual_capital_and_fixed_opex_factor"], "annual factor")
                variable = _decimal(case_input["incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated"], "variable proxy")
                factor_values["capital_annualisation"][case] += base_capex * annual_factor + base_abatement * base_variable
                factor_values["variable_resource"][case] += base_capex * base_factor + base_abatement * variable
            source_values.append(base["source_id"])

        for case in ("low", "base", "high"):
            case_facilities = [
                row
                for row in facility_cost_rows
                if row["company_id"] == company_id
                and row["variant_role"] == "primary"
                and row["case"] == case
                and row["modelled_flag"] == "yes"
            ]
            by_id = {row["facility_id"]: row for row in case_facilities}
            for assigned_row in assigned:
                facility_id = str(assigned_row["facility_id"])
                base = base_facilities[facility_id]
                ratio = _decimal(str(assigned_row["assigned_abatement_to_2050_gap_tco2e"]), "assigned abatement") / _decimal(base["modelled_operational_abatement_tco2e"], "base gross abatement")
                factor_values["combined_model_case"][case] += _decimal(by_id[facility_id]["annual_resource_gap_proxy_usd_2025"], "combined annual gap") * ratio

        for factor, definition in definitions.items():
            values = factor_values[factor]
            low, base, high = values["low"], values["base"], values["high"]
            if not low <= base <= high:
                raise ModelInputError(f"uncertainty ordering failed for {company_id}/{factor}")
            results.append(
                {
                    "company_id": company_id,
                    "company_name": name,
                    "country": country,
                    "sector": sector,
                    "factor": factor,
                    "factor_definition": definition,
                    "annual_resource_gap_low_usd_2025": low,
                    "annual_resource_gap_base_usd_2025": base,
                    "annual_resource_gap_high_usd_2025": high,
                    "downside_change_vs_base_usd_2025": low - base,
                    "upside_change_vs_base_usd_2025": high - base,
                    "high_to_low_span_usd_2025": high - low,
                    "high_over_low_multiple": high / low if low > 0 else "NA",
                    "pathway_scope_abatement_tco2e": total_assigned_abatement,
                    "unit": "USD_2025/year",
                    "currency": "USD",
                    "price_year": "2025 screening proxy",
                    "value_type": "estimated",
                    "quality_flag": "D",
                    "source_id": _join((*source_values, "annual_cost_gap_assumptions_mvp")),
                    "formula_or_method": "one-factor cases hold the base physical pathway scope fixed and vary either the route annualisation factor or variable-resource proxy; combined case applies existing low/base/high facility model outputs scaled by the base gap assignment ratio",
                    "boundary_note": "Ranges are deterministic sensitivities, not probabilities or forecast volatility. Verified incentives, incumbent costs and system abatement remain unavailable.",
                }
            )
    return results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facility-cost", type=Path, required=True)
    parser.add_argument("--company-cost", type=Path, required=True)
    parser.add_argument("--production", type=Path, required=True)
    parser.add_argument("--constraints", type=Path, required=True)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--route-cost", type=Path, required=True)
    parser.add_argument("--facility-output", type=Path, required=True)
    parser.add_argument("--company-output", type=Path, required=True)
    parser.add_argument("--uncertainty-output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        facilities, companies = build_pathway_tables(
            _read(args.facility_cost),
            _read(args.company_cost),
            _read(args.production),
            _read(args.constraints),
            _read(args.anchors),
        )
        uncertainty = build_uncertainty_table(
            _read(args.facility_cost),
            _read(args.company_cost),
            _read(args.route_cost),
            facilities,
        )
        _write(args.facility_output, facilities, FACILITY_FIELDS)
        _write(args.company_output, companies, COMPANY_PATHWAY_FIELDS)
        _write(args.uncertainty_output, uncertainty, UNCERTAINTY_FIELDS)
    except ModelInputError as exc:
        print(f"cap-kj emissions pathway: error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
