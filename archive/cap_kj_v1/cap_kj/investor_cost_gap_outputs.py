"""Generate investor-facing annual cost-gap and risk-to-abatement outputs."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


COMPANY_ORDER = ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS")
COMPANY_LABELS = {
    "POSCO": "POSCO",
    "NIPPON_STEEL": "Nippon Steel",
    "LOTTE_CHEMICAL": "LOTTE Chemical",
    "MITSUI_CHEMICALS": "Mitsui Chemicals",
}
FACILITY_LABELS = {
    "KR_POSCO_POHANG": "Pohang",
    "JP_NSC_OITA": "Oita",
    "KR_LOTTE_YEOSU_BASIC": "Yeosu Basic",
    "JP_MCI_OSAKA": "Osaka",
}
MECHANISMS = ("B0", "BH", "BL", "BHL")
FIGURE_NAMES = (
    "05_company_annual_resource_gap.png",
    "06_risk_to_abatement_pathway.png",
)


@dataclass(frozen=True)
class CostGapCase:
    company_id: str
    sector: str
    baseline_variant: str
    variant_role: str
    case: str
    coverage: float
    residual_tco2e: float
    capex_usd: float
    abatement_tco2e: float
    resource_gap_usd: float
    resource_gap_per_tco2e: float
    base_support_usd: float
    base_stress_adjusted_gap_usd: float
    largest_facility_id: str
    largest_facility_share: float
    verified_gap: str
    quality_flag: str


@dataclass(frozen=True)
class MechanismPoint:
    company_id: str
    mechanism: str
    residual_exposure: float
    operational_abatement_tco2e: float
    level_support_usd: float
    contract_covered_capex_usd: float
    coverage: float
    quality_flag: str


def _number(row: dict[str, str], key: str) -> float:
    value = row[key]
    if value == "NA":
        raise ValueError(f"{key} is NA")
    return float(value)


def load_cost_gap_cases(path: Path) -> list[CostGapCase]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    cases = [
        CostGapCase(
            company_id=row["company_id"],
            sector=row["sector"],
            baseline_variant=row["baseline_variant"],
            variant_role=row["variant_role"],
            case=row["case"],
            coverage=_number(row, "base_case_emissions_coverage_ratio"),
            residual_tco2e=_number(
                row, "base_case_unmodelled_residual_emissions_tco2e"
            ),
            capex_usd=_number(row, "transition_capex_usd_2025"),
            abatement_tco2e=_number(row, "modelled_operational_abatement_tco2e"),
            resource_gap_usd=_number(row, "annual_resource_gap_proxy_usd_2025"),
            resource_gap_per_tco2e=_number(
                row,
                "annual_resource_gap_proxy_usd_2025_per_operational_tco2e_abated",
            ),
            base_support_usd=_number(row, "implied_support_base_usd_2025"),
            base_stress_adjusted_gap_usd=_number(
                row, "stress_adjusted_gap_base_usd_2025"
            ),
            largest_facility_id=row["largest_resource_gap_facility_id"],
            largest_facility_share=_number(
                row, "largest_resource_gap_facility_share"
            ),
            verified_gap=row["verified_incentive_adjusted_gap_usd_2025"],
            quality_flag=row["quality_flag"],
        )
        for row in rows
    ]
    validate_cost_gap_cases(cases)
    return cases


def validate_cost_gap_cases(cases: Iterable[CostGapCase]) -> None:
    cases = list(cases)
    primary = [row for row in cases if row.variant_role == "primary"]
    expected = {
        (company_id, case)
        for company_id in COMPANY_ORDER
        for case in ("low", "base", "high")
    }
    if len(primary) != 12 or {(row.company_id, row.case) for row in primary} != expected:
        raise ValueError("cost-gap table must contain 12 primary company-case rows")
    legacy = [row for row in cases if row.variant_role == "sensitivity"]
    if len(legacy) != 3 or {row.company_id for row in legacy} != {"MITSUI_CHEMICALS"}:
        raise ValueError("cost-gap table must retain three Mitsui legacy sensitivity rows")
    for company_id in COMPANY_ORDER:
        ordered = {
            row.case: row.resource_gap_usd
            for row in primary
            if row.company_id == company_id
        }
        if not ordered["low"] <= ordered["base"] <= ordered["high"]:
            raise ValueError(f"annual resource-gap range is not ordered for {company_id}")
    if {row.verified_gap for row in cases} != {"NA"}:
        raise ValueError("verified incentive-adjusted gaps must remain NA")
    if {row.quality_flag for row in cases} != {"D"}:
        raise ValueError("investor cost-gap screen must disclose quality D")


def load_base_mechanisms(path: Path) -> list[MechanismPoint]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["assumption_case"] == "base"
        ]
    points = [
        MechanismPoint(
            company_id=row["company_id"],
            mechanism=row["mechanism_case"],
            residual_exposure=_number(
                row, "capex_weighted_residual_common_exposure_ratio"
            ),
            operational_abatement_tco2e=_number(
                row, "mechanism_operational_abatement_tco2e"
            ),
            level_support_usd=_number(row, "screening_level_support_total_usd_2025"),
            contract_covered_capex_usd=_number(
                row, "contract_covered_capex_usd_2025"
            ),
            coverage=min(_number(row, "emissions_coverage_ratio"), 1.0),
            quality_flag=row["quality_flag"],
        )
        for row in rows
    ]
    expected = {
        (company_id, mechanism)
        for company_id in COMPANY_ORDER
        for mechanism in MECHANISMS
    }
    if len(points) != 16 or {(row.company_id, row.mechanism) for row in points} != expected:
        raise ValueError("support table must contain 16 base company-mechanism rows")
    if {row.quality_flag for row in points} != {"D"}:
        raise ValueError("risk-to-abatement screen must disclose quality D")
    return points


def _primary_index(cases: Iterable[CostGapCase]) -> dict[tuple[str, str], CostGapCase]:
    return {
        (row.company_id, row.case): row
        for row in cases
        if row.variant_role == "primary"
    }


def _mechanism_index(
    points: Iterable[MechanismPoint],
) -> dict[tuple[str, str], MechanismPoint]:
    return {(row.company_id, row.mechanism): row for row in points}


def _style() -> tuple[str, str, str, str, str, str]:
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelcolor": "#24313d",
            "axes.edgecolor": "#a8b2bc",
            "xtick.color": "#46525e",
            "ytick.color": "#24313d",
            "figure.facecolor": "#ffffff",
            "axes.facecolor": "#ffffff",
            "savefig.facecolor": "#ffffff",
        }
    )
    return "#135d75", "#b65f32", "#22806b", "#707b85", "#d1d8de", "#24313d"


def _finish(fig, output: Path, note: str) -> None:
    fig.text(0.01, 0.012, note, ha="left", va="bottom", fontsize=8, color="#5c6770")
    fig.savefig(output, dpi=180, bbox_inches="tight", pad_inches=0.18)


def plot_annual_resource_gap(cases: list[CostGapCase], output: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    steel, chemicals, support_colour, neutral, grid, text = _style()
    primary = _primary_index(cases)
    legacy = {
        row.case: row
        for row in cases
        if row.company_id == "MITSUI_CHEMICALS" and row.variant_role == "sensitivity"
    }
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.1))
    groups = (
        ("Steel", ("POSCO", "NIPPON_STEEL"), steel),
        ("Petrochemicals", ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS"), chemicals),
    )
    for ax, (title, companies, colour) in zip(axes, groups):
        for y, company_id in enumerate(reversed(companies)):
            low = primary[(company_id, "low")].resource_gap_usd / 1e9
            base_row = primary[(company_id, "base")]
            base = base_row.resource_gap_usd / 1e9
            high = primary[(company_id, "high")].resource_gap_usd / 1e9
            adjusted = base_row.base_stress_adjusted_gap_usd / 1e9
            ax.hlines(y, low, high, color=colour, linewidth=4, alpha=0.42)
            ax.scatter((low, high), (y, y), s=38, color=colour, marker="|")
            ax.plot((adjusted, base), (y, y), color=support_colour, linewidth=2.5)
            ax.scatter(base, y, s=85, color=colour, edgecolor="white", linewidth=1.2, zorder=3)
            ax.scatter(adjusted, y, s=58, color=support_colour, marker="D", edgecolor="white", linewidth=0.8, zorder=4)
            ax.text(
                base,
                y + 0.22,
                f"resource ${base:.2f}bn/yr",
                ha="center",
                va="bottom",
                fontsize=8.6,
                color=text,
            )
            ax.text(
                adjusted,
                y - 0.23,
                f"stress-adjusted ${adjusted:.2f}bn",
                ha="center",
                va="top",
                fontsize=8.2,
                color=neutral,
            )
            if company_id == "MITSUI_CHEMICALS":
                legacy_base = legacy["base"].resource_gap_usd / 1e9
                ax.scatter(
                    legacy_base,
                    y,
                    s=72,
                    facecolors="none",
                    edgecolors=neutral,
                    marker="o",
                    linewidth=1.4,
                    zorder=4,
                )
                ax.text(
                    legacy_base,
                    y + 0.43,
                    f"legacy 85%: ${legacy_base:.2f}bn",
                    ha="center",
                    va="bottom",
                    fontsize=7.8,
                    color=neutral,
                )
        ax.set_yticks(
            range(len(companies)),
            [COMPANY_LABELS[company_id] for company_id in reversed(companies)],
        )
        ax.set_xlabel("Annual gap (2025 USD bn/year)")
        ax.set_title(title)
        ax.grid(axis="x", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_ylim(-0.62, len(companies) - 0.02)
    fig.legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=steel, markeredgecolor="white", markersize=8, label="Base resource gap"),
            Line2D([0], [0], marker="D", color=support_colour, markerfacecolor=support_colour, markersize=6, label="After base support stress"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=neutral, markersize=7, label="Mitsui legacy allocation"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.905),
        ncol=3,
        frameon=False,
        fontsize=9,
    )
    fig.suptitle(
        "Annual resource gap: size, uncertainty and support stress",
        x=0.01,
        ha="left",
        fontsize=16,
        fontweight="bold",
        color=text,
    )
    fig.text(
        0.01,
        0.925,
        "Primary low/base/high resource proxies; sector panels use different scales.",
        fontsize=10,
        color=neutral,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.86), w_pad=3.0)
    _finish(
        fig,
        output,
        "Support is an independent stress on positive gaps—not verified cash or realised net gap. Quality D. Source: company_annual_cost_gap_mvp.csv",
    )
    plt.close(fig)


def plot_risk_to_abatement(points: list[MechanismPoint], output: Path) -> None:
    import matplotlib.pyplot as plt

    steel, chemicals, combined, neutral, grid, text = _style()
    rows = _mechanism_index(points)
    mechanism_colours = {"B0": neutral, "BH": steel, "BL": chemicals, "BHL": combined}
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.4))
    for ax, company_id in zip(axes.flat, COMPANY_ORDER):
        company = {mechanism: rows[(company_id, mechanism)] for mechanism in MECHANISMS}
        segments = (("B0", "BH"), ("B0", "BL"), ("BH", "BHL"), ("BL", "BHL"))
        for start, end in segments:
            a, b = company[start], company[end]
            ax.plot(
                (a.residual_exposure * 100, b.residual_exposure * 100),
                (a.operational_abatement_tco2e / 1e6, b.operational_abatement_tco2e / 1e6),
                color=grid,
                linewidth=1.4,
                zorder=1,
            )
        grouped: dict[tuple[float, float], list[str]] = {}
        for mechanism, point in company.items():
            xy = (
                round(point.residual_exposure * 100, 8),
                round(point.operational_abatement_tco2e / 1e6, 8),
            )
            grouped.setdefault(xy, []).append(mechanism)
            ax.scatter(
                xy[0],
                xy[1],
                s=78,
                color=mechanism_colours[mechanism],
                edgecolor="white",
                linewidth=0.9,
                zorder=3,
            )
        ymax = max(point.operational_abatement_tco2e for point in company.values()) / 1e6
        label_lift = max(ymax * 0.06, 0.08)
        for (x, y), mechanisms in grouped.items():
            label = "/".join(mechanisms)
            if y == 0:
                offset = label_lift
            else:
                offset = label_lift * 0.45
            ax.text(x, y + offset, label, ha="center", va="bottom", fontsize=8.5, color=text)
        top = max(ymax * 1.22, 0.5)
        ax.set_xlim(105, 0)
        ax.set_ylim(-top * 0.03, top)
        ax.set_title(COMPANY_LABELS[company_id] + ("*" if company_id == "MITSUI_CHEMICALS" else ""))
        ax.set_xlabel("Residual common exposure (%) — lower is better")
        ax.set_ylabel("Enabled operational abatement (MtCO₂e/year)")
        ax.grid(color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(
        "What unlocks abatement: risk coverage, level support, or both?",
        x=0.01,
        ha="left",
        fontsize=16,
        fontweight="bold",
        color=text,
    )
    fig.text(
        0.01,
        0.93,
        "B0 none | BH risk coverage | BL level support | BHL combined; base rule experiment.",
        fontsize=10,
        color=neutral,
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.89), h_pad=2.4, w_pad=2.5)
    _finish(
        fig,
        output,
        "Rule-based, not causal; operational reduction is not system abatement. *Mitsui mechanism panel retains the legacy 85% boundary; cost-gap view uses SHK 97.46%. Quality D.",
    )
    plt.close(fig)


def write_investor_update(
    cases: list[CostGapCase], points: list[MechanismPoint], output: Path
) -> None:
    primary = _primary_index(cases)
    mechanisms = _mechanism_index(points)
    base = {company_id: primary[(company_id, "base")] for company_id in COMPANY_ORDER}
    legacy_mci = next(
        row
        for row in cases
        if row.company_id == "MITSUI_CHEMICALS"
        and row.variant_role == "sensitivity"
        and row.case == "base"
    )
    lines = [
        "# Investor cost-gap and risk-to-abatement update",
        "",
        "**Decision status:** auditable quality-D screening for capital-priority diligence; not company guidance, an investment recommendation, or a verified net-cost forecast.  ",
        "**Boundary:** domestic operational Scope 1+2 facility screen. Production coverage, replacement production and system abatement remain unresolved.  ",
        "**Market-policy rule:** actual avoided compliance cost, realised green premium and verified support are unavailable; the incentive-adjusted gap remains `NA`, not zero.",
        "",
        "## Decision table",
        "",
        "| Company | Base annual resource gap | Low–high | Gap per operational tCO2 | Base support stress | Gap after stress | Base coverage | Largest gap facility |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for company_id in COMPANY_ORDER:
        row = base[company_id]
        low = primary[(company_id, "low")].resource_gap_usd / 1e9
        high = primary[(company_id, "high")].resource_gap_usd / 1e9
        facility = FACILITY_LABELS.get(row.largest_facility_id, row.largest_facility_id)
        lines.append(
            f"| {COMPANY_LABELS[company_id]} | ${row.resource_gap_usd / 1e9:.3f}bn/yr | "
            f"${low:.3f}–{high:.3f}bn | ${row.resource_gap_per_tco2e:.1f}/tCO2 | "
            f"${row.base_support_usd / 1e9:.3f}bn/yr | "
            f"${row.base_stress_adjusted_gap_usd / 1e9:.3f}bn/yr | {row.coverage:.2%} | "
            f"{row.largest_facility_share:.1%} ({facility}) |"
        )
    mci_delta = base["MITSUI_CHEMICALS"].resource_gap_usd - legacy_mci.resource_gap_usd
    lines.extend(
        [
            "",
            "## What changes the capital-allocation view",
            "",
            f"1. **Nippon Steel carries the largest absolute annual gap.** Its base resource proxy is ${base['NIPPON_STEEL'].resource_gap_usd / 1e9:.3f}bn/year across eleven costed facilities. Oita contributes {base['NIPPON_STEEL'].largest_facility_share:.1%}, so the economic burden is material but distributed rather than a single-asset bet.",
            f"2. **Pohang dominates POSCO more on annual economics than on CAPEX.** Pohang contributes {base['POSCO'].largest_facility_share:.1%} of the base annual gap, versus 68.6% of the earlier CAPEX screen, because its H2 and clean-power proxy is more expensive than Gwangyang's scrap-EAF case.",
            f"3. **The mechanism test separates the steel and chemical problems.** Under the rule experiment, BH alone unlocks {mechanisms[('POSCO', 'BH')].operational_abatement_tco2e / 1e6:.2f} MtCO2/year for POSCO and {mechanisms[('NIPPON_STEEL', 'BH')].operational_abatement_tco2e / 1e6:.2f} MtCO2/year for Nippon. For LOTTE and Mitsui, BH reduces residual exposure but unlocks no operational abatement; only BHL changes the rule-based facility status to no-regret.",
            f"4. **Official Mitsui facility evidence materially raises covered exposure.** The SHK bridge moves base emissions coverage from 85.0% to {base['MITSUI_CHEMICALS'].coverage:.2%} and raises the covered annual resource gap by ${mci_delta / 1e6:.1f}m/year. The separate mechanism chart still uses the legacy 85% boundary and must be recalibrated before exact support totals are combined with the SHK cost view.",
            "5. **Chemical equality is mechanical, not comparative evidence.** LOTTE and Mitsui both show the same base dollars per operational tCO2 because one electrified-cracker proxy is applied to both. It cannot support a company ranking.",
            "",
            "## Diligence priorities",
            "",
            "- For POSCO, test Pohang clean-hydrogen and clean-power contractability before treating the large abatement block as investable.",
            "- For Nippon Steel, test portfolio-wide procurement and infrastructure coverage; no single facility closes the company gap.",
            "- For LOTTE and Mitsui, replace the common electrified-cracker proxy with site production, energy balance and ownership-specific project economics, then rerun BHL on the same boundary.",
            "- Acquire verified facility policy cash effects before publishing an incentive-adjusted net gap; support stresses are decision sensitivities only.",
            "",
            "## Figure guide",
            "",
            "1. `05_company_annual_resource_gap.png` — low/base/high annual resource gap, base support stress and Mitsui boundary sensitivity.",
            "2. `06_risk_to_abatement_pathway.png` — whether risk coverage, level support or both unlocks operational abatement under the rule experiment.",
            "",
            "## Reproducibility",
            "",
            "Generated from `outputs/tables/company_annual_cost_gap_mvp.csv` and `outputs/tables/company_support_experiment_mvp.csv` by `python -m cap_kj.investor_cost_gap_outputs`. No displayed number is manually edited.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_outputs(
    cost_gap_csv: Path,
    support_csv: Path,
    output_dir: Path,
    report_path: Path,
) -> list[Path]:
    cases = load_cost_gap_cases(cost_gap_csv)
    points = load_base_mechanisms(support_csv)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [output_dir / name for name in FIGURE_NAMES]
    plot_annual_resource_gap(cases, paths[0])
    plot_risk_to_abatement(points, paths[1])
    write_investor_update(cases, points, report_path)
    return [*paths, report_path]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cost-gap-csv",
        type=Path,
        default=Path("outputs/tables/company_annual_cost_gap_mvp.csv"),
    )
    parser.add_argument(
        "--support-csv",
        type=Path,
        default=Path("outputs/tables/company_support_experiment_mvp.csv"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/figures"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("outputs/reports/investor_cost_gap_update.md"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = generate_outputs(
        args.cost_gap_csv, args.support_csv, args.output_dir, args.report
    )
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
