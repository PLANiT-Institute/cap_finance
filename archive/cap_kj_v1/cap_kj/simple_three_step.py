"""Build the simplified G-CAP, transition-premium and emissions-closure view."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from .model import ModelInputError


D = Decimal
COMPANY_ORDER = ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS")
SECTOR_ORDER = ("steel", "petrochemicals")
TECHNOLOGIES = {
    "POSCO": "Scrap-EAF + H2-DRI / HyREX",
    "NIPPON_STEEL": "H2-DRI / EAF + EAF efficiency",
    "LOTTE_CHEMICAL": "NCC electrification",
    "MITSUI_CHEMICALS": "NCC electrification + cracker consolidation",
}
FIGURE_NAMES = (
    "13_gcap_company_capital_gap.png",
    "14_level_gap_and_premium_proxy.png",
    "15_support_to_emissions_closure.png",
)
OUTPUT_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "representative_technology",
    "official_baseline_operational_ghg_tco2e",
    "gcam_aligned_2050_required_reduction_tco2e",
    "sector_required_reduction_tco2e",
    "company_gcap_allocation_weight",
    "gcap_capital_intensity_low_usd_2025_per_annual_tco2e",
    "gcap_capital_intensity_base_usd_2025_per_annual_tco2e",
    "gcap_capital_intensity_high_usd_2025_per_annual_tco2e",
    "company_gcap_low_usd_2025",
    "company_gcap_base_usd_2025",
    "company_gcap_high_usd_2025",
    "identified_route_capital_usd_2025",
    "capital_level_gap_base_usd_2025",
    "identified_capital_coverage_ratio",
    "full_path_annual_level_gap_usd_2025",
    "full_path_annual_high_case_gap_usd_2025",
    "annual_uncertainty_buffer_usd_2025",
    "level_gap_rate_on_gcap",
    "transition_premium_proxy_rate_on_gcap",
    "total_high_case_hurdle_rate_on_gcap",
    "premium_share_of_high_case_hurdle",
    "level_only_unlocked_abatement_tco2e",
    "premium_mitigation_only_unlocked_abatement_tco2e",
    "combined_unlocked_abatement_tco2e",
    "level_only_gap_closure_ratio",
    "premium_mitigation_only_gap_closure_ratio",
    "combined_gap_closure_ratio",
    "residual_reduction_after_combined_tco2e",
    "transition_risk_premium_bps",
    "premium_proxy_status",
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


def _decimal(value: object, label: str) -> Decimal:
    try:
        result = D(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ModelInputError(f"{label} is not numeric: {value!r}") from exc
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


def _join(*values: str) -> str:
    parts: set[str] = set()
    for value in values:
        parts.update(part for part in value.split("|") if part and part != "NA")
    return "|".join(sorted(parts))


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _serialise(row[field]) for field in OUTPUT_FIELDS})


def _validate_assumptions(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    assumptions = {
        row["sector"]: row
        for row in rows
        if row["metric"] == "gcap_capital_intensity"
    }
    if set(assumptions) != set(SECTOR_ORDER) or len(assumptions) != len(rows):
        raise ModelInputError("G-CAP assumptions must contain one capital intensity for each sector")
    for sector, row in assumptions.items():
        values = [_decimal(row[f"value_{case}"], f"{sector} {case} intensity") for case in ("low", "base", "high")]
        if not D("0") < values[0] <= values[1] <= values[2]:
            raise ModelInputError(f"invalid G-CAP intensity range for {sector}")
        for field in ("unit", "price_year", "value_type", "source_id", "formula_or_method", "quality_flag", "boundary_note"):
            if not row[field]:
                raise ModelInputError(f"missing {field} for {sector} G-CAP assumption")
        if row["value_type"].lower() != "estimated":
            raise ModelInputError("G-CAP proxy assumptions must be explicitly estimated")
    return assumptions


def build_simple_three_step(
    pathway_rows: list[dict[str, str]],
    uncertainty_rows: list[dict[str, str]],
    bridge_rows: list[dict[str, str]],
    assumption_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    """Return one company row linking required capital, uncertainty and emissions closure."""

    pathway = {row["company_id"]: row for row in pathway_rows if row["year"] == "2050"}
    uncertainty = {
        row["company_id"]: row
        for row in uncertainty_rows
        if row["factor"] == "combined_model_case"
    }
    bridge = {row["company_id"]: row for row in bridge_rows}
    expected = set(COMPANY_ORDER)
    if set(pathway) != expected or set(uncertainty) != expected or set(bridge) != expected:
        raise ModelInputError("all three input tables must contain the fixed four-company sample")
    assumptions = _validate_assumptions(assumption_rows)

    sector_required = {
        sector: sum(
            (
                _decimal(pathway[company]["required_reduction_from_baseline_tco2e"], "required reduction")
                for company in COMPANY_ORDER
                if pathway[company]["sector"] == sector
            ),
            D("0"),
        )
        for sector in SECTOR_ORDER
    }
    if any(value <= 0 for value in sector_required.values()):
        raise ModelInputError("sector required reduction must be positive")

    results: list[dict[str, object]] = []
    for company_id in COMPANY_ORDER:
        path = pathway[company_id]
        risk = uncertainty[company_id]
        flow = bridge[company_id]
        sector = path["sector"]
        assumption = assumptions[sector]
        required = _decimal(path["required_reduction_from_baseline_tco2e"], "required reduction")
        sector_total = sector_required[sector]
        allocation_weight = required / sector_total
        intensities = {
            case: _decimal(assumption[f"value_{case}"], f"{sector} {case} intensity")
            for case in ("low", "base", "high")
        }
        sector_gcap = {case: sector_total * intensities[case] for case in intensities}
        company_gcap = {case: sector_gcap[case] * allocation_weight for case in intensities}
        identified_capital = _decimal(flow["identified_route_capital_usd_2025"], "identified route capital")
        if identified_capital > company_gcap["base"]:
            raise ModelInputError(f"identified capital exceeds base G-CAP for {company_id}")
        capital_gap = company_gcap["base"] - identified_capital

        pathway_scope = _decimal(risk["pathway_scope_abatement_tco2e"], "uncertainty pathway scope")
        if pathway_scope <= 0:
            raise ModelInputError(f"uncertainty pathway scope must be positive for {company_id}")
        scale_to_full_path = required / pathway_scope
        annual_level = _decimal(risk["annual_resource_gap_base_usd_2025"], "base annual gap") * scale_to_full_path
        annual_high = _decimal(risk["annual_resource_gap_high_usd_2025"], "high annual gap") * scale_to_full_path
        if annual_high < annual_level:
            raise ModelInputError(f"high annual gap is below base for {company_id}")
        uncertainty_buffer = annual_high - annual_level
        level_rate = annual_level / company_gcap["base"]
        premium_rate = uncertainty_buffer / company_gcap["base"]
        total_rate = annual_high / company_gcap["base"]

        level_abatement = _decimal(flow["screening_unlocked_abatement_BL_tco2e"], "level-only abatement")
        premium_abatement = _decimal(flow["screening_unlocked_abatement_BH_tco2e"], "premium-mitigation abatement")
        combined_abatement = _decimal(flow["screening_unlocked_abatement_BHL_tco2e"], "combined abatement")
        if max(level_abatement, premium_abatement, combined_abatement) > required:
            raise ModelInputError(f"screened abatement exceeds required reduction for {company_id}")

        boundary = (
            "G-CAP is a GCAM-aligned sector-envelope proxy allocated by each company's share of the sector sample's 2050 required reduction; "
            "an actual GCAM Korea/Japan capital extract is pending. The transition-premium proxy is the deterministic high-minus-base annual resource-gap buffer divided by G-CAP, not WACC, a probability-weighted expectation, a security spread or a risk premium in basis points. "
            "BL/BH/BHL emissions changes are provisional rule-screen outcomes and operational reductions, not causal policy estimates or system abatement."
        )
        if company_id == "MITSUI_CHEMICALS":
            boundary += " Mitsui support mechanics retain the documented legacy-boundary warning. Cracker consolidation is not treated as system abatement."
        results.append(
            {
                "company_id": company_id,
                "company_name": path["company_name"],
                "country": path["country"],
                "sector": sector,
                "representative_technology": TECHNOLOGIES[company_id],
                "official_baseline_operational_ghg_tco2e": _decimal(path["official_baseline_operational_ghg_tco2e"], "official baseline"),
                "gcam_aligned_2050_required_reduction_tco2e": required,
                "sector_required_reduction_tco2e": sector_total,
                "company_gcap_allocation_weight": allocation_weight,
                **{f"gcap_capital_intensity_{case}_usd_2025_per_annual_tco2e": intensities[case] for case in intensities},
                **{f"company_gcap_{case}_usd_2025": company_gcap[case] for case in company_gcap},
                "identified_route_capital_usd_2025": identified_capital,
                "capital_level_gap_base_usd_2025": capital_gap,
                "identified_capital_coverage_ratio": identified_capital / company_gcap["base"],
                "full_path_annual_level_gap_usd_2025": annual_level,
                "full_path_annual_high_case_gap_usd_2025": annual_high,
                "annual_uncertainty_buffer_usd_2025": uncertainty_buffer,
                "level_gap_rate_on_gcap": level_rate,
                "transition_premium_proxy_rate_on_gcap": premium_rate,
                "total_high_case_hurdle_rate_on_gcap": total_rate,
                "premium_share_of_high_case_hurdle": uncertainty_buffer / annual_high if annual_high > 0 else D("0"),
                "level_only_unlocked_abatement_tco2e": level_abatement,
                "premium_mitigation_only_unlocked_abatement_tco2e": premium_abatement,
                "combined_unlocked_abatement_tco2e": combined_abatement,
                "level_only_gap_closure_ratio": level_abatement / required,
                "premium_mitigation_only_gap_closure_ratio": premium_abatement / required,
                "combined_gap_closure_ratio": combined_abatement / required,
                "residual_reduction_after_combined_tco2e": required - combined_abatement,
                "transition_risk_premium_bps": "NA",
                "premium_proxy_status": "annual_high_minus_base_cost_buffer_per_gcap_not_market_priced",
                "currency": "USD",
                "price_year": "2025 screening proxy",
                "value_type": "modelled_from_estimated_and_allocated_inputs",
                "quality_flag": "D",
                "source_id": _join(path["source_id"], risk["source_id"], flow["source_id"], assumption["source_id"]),
                "formula_or_method": "sector G-CAP = sector 2050 required reduction x sector capital intensity; company G-CAP = sector G-CAP x company share of sector required reduction; capital gap = base G-CAP - route-identified capital; level-gap rate = full-path-scaled base annual resource gap / base G-CAP; transition-premium proxy = full-path-scaled (high-base) annual resource gap / base G-CAP; policy closure = BL, BH or BHL unlocked operational reduction / 2050 required reduction",
                "boundary_note": boundary,
            }
        )
    return results


def _f(row: dict[str, object], field: str) -> float:
    return float(row[field])


def _style() -> dict[str, str]:
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelcolor": "#34404a",
            "axes.edgecolor": "#aab3ba",
            "xtick.color": "#52606b",
            "ytick.color": "#27333d",
            "figure.facecolor": "#fbfcfd",
            "axes.facecolor": "#fbfcfd",
            "savefig.facecolor": "#fbfcfd",
        }
    )
    return {
        "navy": "#174a65",
        "teal": "#1f8a78",
        "orange": "#df7d3e",
        "amber": "#e5aa45",
        "light": "#e7ecef",
        "text": "#27333d",
        "muted": "#697782",
    }


def plot_gcap_gap(rows: list[dict[str, object]], output: Path) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    colors = _style()
    sectors = (
        ("STEEL", [row for row in rows if row["sector"] == "steel"]),
        ("PETROCHEMICALS / NCC", [row for row in rows if row["sector"] == "petrochemicals"]),
    )
    fig, axes = plt.subplots(2, 1, figsize=(12.6, 8.0))
    for ax, (sector_label, sector_rows) in zip(axes, sectors):
        ordered = sorted(sector_rows, key=lambda row: COMPANY_ORDER.index(str(row["company_id"])))
        labels = [str(row["company_name"]) for row in ordered]
        identified = np.array([_f(row, "identified_route_capital_usd_2025") / 1e9 for row in ordered])
        gap = np.array([_f(row, "capital_level_gap_base_usd_2025") / 1e9 for row in ordered])
        low = np.array([_f(row, "company_gcap_low_usd_2025") / 1e9 for row in ordered])
        base = identified + gap
        high = np.array([_f(row, "company_gcap_high_usd_2025") / 1e9 for row in ordered])
        y = np.array([1.0, 0.0])
        ax.barh(y, identified, height=0.55, color=colors["teal"], zorder=2)
        ax.barh(y, gap, left=identified, height=0.55, color=colors["orange"], zorder=2)
        ax.errorbar(base, y, xerr=np.vstack((base - low, high - base)), fmt="none", ecolor=colors["navy"], capsize=5, lw=1.8, zorder=3)
        for index, row in enumerate(ordered):
            ax.text(identified[index] / 2, y[index], f"${identified[index]:.1f}bn\nidentified", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
            ax.text(identified[index] + gap[index] / 2, y[index], f"${gap[index]:.1f}bn\ngap", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
            ax.text(high[index] + max(high) * 0.02, y[index], f"G-CAP ${base[index]:.1f}bn", va="center", color=colors["text"], fontsize=9.5, fontweight="bold")
            ax.text(0, y[index] - 0.36, str(row["representative_technology"]), va="top", color=colors["muted"], fontsize=8.5)
        ax.set_yticks(y, labels)
        ax.set_ylim(-0.65, 1.55)
        ax.set_xlim(0, max(high) * 1.24)
        ax.set_xlabel("USD 2025 billion")
        ax.grid(axis="x", color="#dfe4e8", lw=0.8, zorder=0)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=12)
        ax.set_title(sector_label, loc="left", color=colors["navy"], fontsize=10, pad=8)
    fig.suptitle("1  |  G-CAP allocation reveals the capital still missing", x=0.075, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.075, 0.925, "Company allocation = share of sector 2050 required reduction. Whiskers show the low–high capital-intensity range.", color=colors["muted"], fontsize=10)
    fig.text(0.075, 0.015, "G-CAP is a GCAM-aligned proxy, not yet a direct GCAM capital output. Estimated/modelled, quality D.", color=colors["muted"], fontsize=8.5)
    fig.subplots_adjust(left=0.25, right=0.96, top=0.86, bottom=0.08, hspace=0.42)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=190, bbox_inches="tight")
    plt.close(fig)


def plot_premium_proxy(rows: list[dict[str, object]], output: Path) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    colors = _style()
    ordered = [next(row for row in rows if row["company_id"] == company) for company in COMPANY_ORDER]
    labels = [str(row["company_name"]) for row in ordered]
    level = np.array([_f(row, "level_gap_rate_on_gcap") * 100 for row in ordered])
    premium = np.array([_f(row, "transition_premium_proxy_rate_on_gcap") * 100 for row in ordered])
    y = np.array([3.2, 2.2, 0.9, -0.1])

    fig, ax = plt.subplots(figsize=(12.6, 6.8))
    ax.barh(y, level, height=0.56, color=colors["navy"], zorder=2)
    ax.barh(y, premium, left=level, height=0.56, color=colors["amber"], zorder=2)
    for index, row in enumerate(ordered):
        total = level[index] + premium[index]
        ax.text(level[index] / 2, y[index], f"Base cost\n{level[index]:.1f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        ax.text(level[index] + premium[index] / 2, y[index], f"Uncertainty\n+{premium[index]:.1f}%", ha="center", va="center", color=colors["text"], fontsize=9, fontweight="bold")
        ax.text(total + 2, y[index], f"{total:.1f}%/yr high-case hurdle", va="center", color=colors["text"], fontsize=9.5, fontweight="bold")
        annual_buffer = _f(row, "annual_uncertainty_buffer_usd_2025") / 1e9
        ax.text(0, y[index] - 0.39, f"Uncertainty buffer: ${annual_buffer:.1f}bn/yr  •  {row['representative_technology']}", va="top", color=colors["muted"], fontsize=8.5)
    ax.axhline(1.55, color="#ccd4da", lw=1)
    ax.text(0, 3.72, "STEEL", color=colors["navy"], fontsize=9, fontweight="bold")
    ax.text(0, 1.42, "PETROCHEMICALS / NCC", color=colors["navy"], fontsize=9, fontweight="bold")
    ax.set_yticks(y, labels)
    ax.set_xlim(0, max(level + premium) * 1.28)
    ax.set_xlabel("Annual burden as % of base G-CAP")
    ax.grid(axis="x", color="#dfe4e8", lw=0.8, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.set_title("2  |  The investment hurdle has a base cost gap and an uncertainty premium", loc="left", fontsize=17, pad=28)
    ax.text(0, 1.025, "Transition premium proxy = (high-case − base annual resource gap) ÷ G-CAP. It is a stress-rate equivalent, not WACC or a traded spread.", transform=ax.transAxes, color=colors["muted"], fontsize=10)
    fig.text(0.07, 0.018, "A rate above 100% means the modelled high-case annual resource burden exceeds the one-time capital envelope; it is a cost-risk warning, not an expected return.", color=colors["muted"], fontsize=8.3)
    fig.subplots_adjust(bottom=0.10)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=190, bbox_inches="tight")
    plt.close(fig)


def plot_emissions_closure(rows: list[dict[str, object]], output: Path) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    colors = _style()
    ordered = [next(row for row in rows if row["company_id"] == company) for company in COMPANY_ORDER]
    metrics = (
        ("level_only_gap_closure_ratio", "Level support only", colors["navy"]),
        ("premium_mitigation_only_gap_closure_ratio", "Premium mitigation only", colors["amber"]),
        ("combined_gap_closure_ratio", "Combined", colors["teal"]),
    )
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 8.2), sharex=True)
    for ax, row in zip(axes.flat, ordered):
        values = np.array([_f(row, field) * 100 for field, _, _ in metrics])
        y = np.arange(len(metrics))
        ax.barh(y, np.full(3, 100.0), height=0.58, color=colors["light"], zorder=1)
        ax.barh(y, values, height=0.58, color=[color for _, _, color in metrics], zorder=2)
        for index, value in enumerate(values):
            ax.text(max(value + 2, 3), index, f"{value:.1f}% closed", va="center", color=colors["text"], fontsize=9.5, fontweight="bold")
        residual = _f(row, "residual_reduction_after_combined_tco2e") / 1e6
        ax.set_yticks(y, [label for _, label, _ in metrics])
        ax.invert_yaxis()
        ax.set_xlim(0, 108)
        ax.grid(axis="x", color="#dfe4e8", lw=0.8, zorder=0)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_title(str(row["company_name"]), loc="left", color=colors["navy"], pad=30)
        ax.text(0, 1.04, str(row["representative_technology"]), transform=ax.transAxes, color=colors["muted"], fontsize=8.4)
        ax.text(1, 1.16, f"Residual: {residual:.1f} MtCO₂e/yr", transform=ax.transAxes, ha="right", color=colors["orange"], fontsize=9.2, fontweight="bold")
    fig.suptitle("3  |  Closing the funding gap is not the same as closing the emissions gap", x=0.07, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.07, 0.925, "Current rule screen: level support alone unlocks no identified route; premium mitigation unlocks steel; chemicals need both. No company reaches 100%.", color=colors["muted"], fontsize=10)
    fig.supxlabel("Share of allocated 2050 reduction closed (%)", y=0.055, color=colors["text"])
    fig.text(0.07, 0.015, "Operational-reduction screen only. Results are deterministic mechanism rules, not causal policy estimates or system abatement.", color=colors["muted"], fontsize=8.5)
    fig.subplots_adjust(left=0.19, right=0.97, top=0.79, bottom=0.11, hspace=0.68, wspace=0.25)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=190, bbox_inches="tight")
    plt.close(fig)


def write_report(rows: list[dict[str, object]], output: Path) -> None:
    total_gcap = sum((_decimal(row["company_gcap_base_usd_2025"], "G-CAP") for row in rows), D("0"))
    total_gap = sum((_decimal(row["capital_level_gap_base_usd_2025"], "capital gap") for row in rows), D("0"))
    sector_gcap = {
        sector: sum(
            (_decimal(row["company_gcap_base_usd_2025"], "G-CAP") for row in rows if row["sector"] == sector),
            D("0"),
        )
        for sector in SECTOR_ORDER
    }
    lines = [
        "# Simple three-step investor model",
        "",
        "## The whole model in three equations",
        "",
        "1. **Company G-CAP** = sector GCAM-aligned capital envelope proxy × company share of sector 2050 required reduction.",
        "2. **Transition premium proxy** = full-path annual high-minus-base resource-gap buffer ÷ company G-CAP.",
        "3. **Emissions closure** = operational reduction unlocked under level-only, premium-mitigation-only or combined support ÷ allocated 2050 required reduction.",
        "",
        f"The four-company base G-CAP is **USD {total_gcap / D('1000000000'):.1f}bn**: steel USD {sector_gcap['steel'] / D('1000000000'):.1f}bn and petrochemicals/NCC USD {sector_gcap['petrochemicals'] / D('1000000000'):.1f}bn. Route-identified projects leave a **USD {total_gap / D('1000000000'):.1f}bn** capital level gap.",
        "",
        "| Company | Sector allocation key | Representative technology | G-CAP | Capital gap | Base cost-gap rate | Premium proxy | Combined emissions closure |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['company_name']} | {_decimal(row['company_gcap_allocation_weight'], 'allocation weight') * 100:.1f}% | {row['representative_technology']} | "
            f"USD {_decimal(row['company_gcap_base_usd_2025'], 'G-CAP') / D('1000000000'):.1f}bn | "
            f"USD {_decimal(row['capital_level_gap_base_usd_2025'], 'capital gap') / D('1000000000'):.1f}bn | "
            f"{_decimal(row['level_gap_rate_on_gcap'], 'level rate') * 100:.1f}%/yr | "
            f"+{_decimal(row['transition_premium_proxy_rate_on_gcap'], 'premium rate') * 100:.1f}%/yr | "
            f"{_decimal(row['combined_gap_closure_ratio'], 'closure') * 100:.1f}% |"
        )
    lines.extend(
        [
            "",
            "## Concrete investor conclusions",
            "",
            "- The missing investment has two different components. The one-time capital level gap is distinct from the recurring cost uncertainty that can raise the required hurdle after the asset is built.",
            "- Under the current provisional mechanism rule, level support by itself unlocks none of the identified route. Premium mitigation through contracts, guarantees or other common-risk coverage unlocks the identified steel pathway, while the NCC pathways need both level and risk treatment.",
            "- Even combined support closes only the identified physical pathway. It does not eliminate the residual emissions gap, so finance policy cannot substitute for missing technology capacity, clean power, hydrogen, feedstock and project timing.",
            "- The premium proxy is deliberately comparable across companies as an annual percentage of G-CAP, but it is not a market-observed WACC increment or security risk premium. `transition_risk_premium_bps` remains `NA`.",
            "",
            "## Evidence boundary",
            "",
            "G-CAP currently uses transparent sector capital-intensity proxies around a GCAM-aligned emissions requirement. It is not yet a direct GCAM Korea/Japan capital output. Low/base/high values, source IDs, formulae, 2025 price basis and quality-D flags are retained in the generated company table. BL/BH/BHL results are deterministic screening rules and model operational reduction, not probability-weighted investment response, causal policy impact or system abatement.",
            "",
            "## Primary outputs",
            "",
            "- `outputs/figures/13_gcap_company_capital_gap.png`",
            "- `outputs/figures/14_level_gap_and_premium_proxy.png`",
            "- `outputs/figures/15_support_to_emissions_closure.png`",
            "- `outputs/tables/company_simple_three_step_mvp.csv`",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_outputs(
    pathway_csv: Path,
    uncertainty_csv: Path,
    bridge_csv: Path,
    assumptions_csv: Path,
    table_output: Path,
    figure_dir: Path,
    report_output: Path,
) -> list[Path]:
    rows = build_simple_three_step(
        _read(pathway_csv),
        _read(uncertainty_csv),
        _read(bridge_csv),
        _read(assumptions_csv),
    )
    _write(table_output, rows)
    figure_paths = [figure_dir / name for name in FIGURE_NAMES]
    plot_gcap_gap(rows, figure_paths[0])
    plot_premium_proxy(rows, figure_paths[1])
    plot_emissions_closure(rows, figure_paths[2])
    write_report(rows, report_output)
    return [table_output, *figure_paths, report_output]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pathway-csv", type=Path, required=True)
    parser.add_argument("--uncertainty-csv", type=Path, required=True)
    parser.add_argument("--bridge-csv", type=Path, required=True)
    parser.add_argument("--assumptions-csv", type=Path, required=True)
    parser.add_argument("--table-output", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        generate_outputs(
            args.pathway_csv,
            args.uncertainty_csv,
            args.bridge_csv,
            args.assumptions_csv,
            args.table_output,
            args.figure_dir,
            args.report_output,
        )
    except ModelInputError as exc:
        print(f"cap-kj simple three-step: error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
