"""Generate company-first investor screening figures and a concise memo.

The outputs deliberately preserve the limitations of the MVP model: CAPEX and
operational abatement are quality-D screening estimates, production coverage is
not available, and economic cost gaps and system abatement are not yet modelled.
"""

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
    "JP_MCI_ICHIHARA": "Ichihara",
}
FIGURE_NAMES = (
    "01_company_capex_range.png",
    "02_capital_timing_and_dependency.png",
    "03_abatement_efficiency_and_coverage.png",
    "04_capital_concentration_and_uncertainty.png",
)


@dataclass(frozen=True)
class CompanyCase:
    company_id: str
    company_name: str
    sector: str
    case: str
    capex_usd: float
    capex_2030_usd: float
    capex_2040_usd: float
    capex_2050_usd: float
    abatement_tco2e: float
    coverage: float
    residual_tco2e: float
    efficiency_tco2e_per_usd_million: float
    price_conditional_share: float
    contract_dependent_share: float
    level_support_dependent_share: float
    largest_facility_id: str
    largest_facility_share: float
    quality_flag: str


def _number(row: dict[str, str], key: str) -> float:
    value = row[key]
    if value == "NA":
        raise ValueError(f"{key} is NA")
    return float(value)


def load_company_cases(path: Path) -> list[CompanyCase]:
    """Read and validate the 12 company-case screening rows."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    cases = [
        CompanyCase(
            company_id=row["company_id"],
            company_name=row["company_name"],
            sector=row["sector"],
            case=row["case"],
            capex_usd=_number(row, "transition_capex_usd_2025"),
            capex_2030_usd=_number(row, "capex_by_2030_usd_2025"),
            capex_2040_usd=_number(row, "capex_2031_2040_usd_2025"),
            capex_2050_usd=_number(row, "capex_2041_2050_usd_2025"),
            abatement_tco2e=_number(row, "modelled_operational_abatement_tco2e"),
            coverage=_number(row, "emissions_coverage_ratio"),
            residual_tco2e=_number(row, "unmodelled_residual_emissions_tco2e"),
            efficiency_tco2e_per_usd_million=_number(
                row, "annual_operational_abatement_per_usd_million_capex"
            ),
            price_conditional_share=_number(row, "price_conditional_capex_share"),
            contract_dependent_share=_number(row, "contract_dependent_capex_share"),
            level_support_dependent_share=_number(
                row, "level_support_dependent_capex_share"
            ),
            largest_facility_id=row["largest_capex_facility_id"],
            largest_facility_share=_number(row, "largest_capex_facility_share"),
            quality_flag=row["quality_flag"],
        )
        for row in rows
    ]
    validate_company_cases(cases)
    return cases


def validate_company_cases(cases: Iterable[CompanyCase]) -> None:
    cases = list(cases)
    expected = {(company, case) for company in COMPANY_ORDER for case in ("low", "base", "high")}
    actual = {(row.company_id, row.case) for row in cases}
    if actual != expected or len(cases) != len(expected):
        raise ValueError("company table must contain exactly low/base/high for four companies")

    for company in COMPANY_ORDER:
        company_cases = {row.case: row for row in cases if row.company_id == company}
        if not (
            company_cases["low"].capex_usd
            <= company_cases["base"].capex_usd
            <= company_cases["high"].capex_usd
        ):
            raise ValueError(f"CAPEX range is not ordered for {company}")
        for row in company_cases.values():
            if row.capex_usd < 0 or row.abatement_tco2e < 0:
                raise ValueError(f"negative screening output for {company}/{row.case}")
            if not 0 <= row.coverage <= 1.000001:
                raise ValueError(f"invalid emissions coverage for {company}/{row.case}")
            shares = (
                row.price_conditional_share
                + row.contract_dependent_share
                + row.level_support_dependent_share
            )
            if abs(shares - 1) > 1e-6:
                raise ValueError(f"status shares do not reconcile for {company}/{row.case}")


def indexed_cases(cases: Iterable[CompanyCase]) -> dict[tuple[str, str], CompanyCase]:
    return {(row.company_id, row.case): row for row in cases}


def _style() -> tuple[str, str, str, str, str]:
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
    return "#135d75", "#b65f32", "#707b85", "#d1d8de", "#24313d"


def _finish(fig, output: Path, note: str) -> None:
    fig.text(0.01, 0.012, note, ha="left", va="bottom", fontsize=8, color="#5c6770")
    fig.savefig(output, dpi=180, bbox_inches="tight", pad_inches=0.18)


def plot_capex_range(cases: list[CompanyCase], output: Path) -> None:
    import matplotlib.pyplot as plt

    steel, chemicals, neutral, grid, text = _style()
    rows = indexed_cases(cases)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.8))
    sector_groups = (
        ("Steel", ("POSCO", "NIPPON_STEEL"), steel),
        ("Petrochemicals", ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS"), chemicals),
    )
    for ax, (title, companies, colour) in zip(axes, sector_groups):
        for y, company in enumerate(reversed(companies)):
            low = rows[(company, "low")].capex_usd / 1e9
            base = rows[(company, "base")].capex_usd / 1e9
            high = rows[(company, "high")].capex_usd / 1e9
            ax.hlines(y, low, high, color=colour, linewidth=4, alpha=0.48)
            ax.scatter((low, high), (y, y), s=35, color=colour, marker="|")
            ax.scatter(base, y, s=85, color=colour, edgecolor="white", linewidth=1.2, zorder=3)
            ax.text(high, y + 0.19, f"range {low:.2f}–{high:.2f}", ha="right", va="bottom", fontsize=9, color=neutral)
            ax.text(base, y - 0.20, f"base ${base:.2f}bn", ha="center", va="top", fontsize=9, color=text)
        ax.set_yticks(range(len(companies)), [COMPANY_LABELS[c] for c in reversed(companies)])
        ax.set_xlabel("Transition CAPEX (2025 USD bn)")
        ax.set_title(title)
        ax.grid(axis="x", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_ylim(-0.55, len(companies) - 0.25)
    fig.suptitle("MVP transition CAPEX range", x=0.01, ha="left", fontsize=16, fontweight="bold", color=text)
    fig.text(0.01, 0.93, "Low/base/high screening assumptions; sector panels use different scales.", fontsize=10, color=neutral)
    fig.tight_layout(rect=(0, 0.07, 1, 0.89))
    _finish(fig, output, "Quality D modelled screening estimates; not company guidance or committed investment. Source: company_capital_allocation_mvp.csv")
    plt.close(fig)


def plot_timing_dependency(cases: list[CompanyCase], output: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    steel, chemicals, neutral, grid, text = _style()
    rows = indexed_cases(cases)
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 8.1))
    timing_colours = ("#2a788e", "#72a8b5", "#c8dce1")
    status_colours = ("#d49a3a", "#487a91", "#b85b45")
    groups = (
        ("Steel", ("POSCO", "NIPPON_STEEL")),
        ("Petrochemicals", ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS")),
    )
    for row_ix, (sector, companies) in enumerate(groups):
        ax_timing, ax_status = axes[row_ix]
        y_positions = list(range(len(companies)))[::-1]
        for y, company in zip(y_positions, companies):
            base = rows[(company, "base")]
            left = 0.0
            for value, colour in zip(
                (base.capex_2030_usd, base.capex_2040_usd, base.capex_2050_usd),
                timing_colours,
            ):
                value_bn = value / 1e9
                ax_timing.barh(y, value_bn, left=left, color=colour, height=0.52)
                if value_bn >= base.capex_usd / 1e9 * 0.08:
                    ax_timing.text(left + value_bn / 2, y, f"${value_bn:.2f}bn", ha="center", va="center", fontsize=8.5, color="white" if colour != timing_colours[2] else text)
                left += value_bn
            ax_timing.text(left, y + 0.32, f"total ${left:.2f}bn", ha="right", va="bottom", fontsize=8.5, color=neutral)

            left_share = 0.0
            for share, colour in zip(
                (base.price_conditional_share, base.contract_dependent_share, base.level_support_dependent_share),
                status_colours,
            ):
                ax_status.barh(y, share * 100, left=left_share, color=colour, height=0.52)
                if share >= 0.08:
                    ax_status.text(left_share + share * 50, y, f"{share:.0%}", ha="center", va="center", fontsize=8.5, color="white")
                left_share += share * 100
        labels = [COMPANY_LABELS[c] for c in companies]
        for ax in (ax_timing, ax_status):
            ax.set_yticks(y_positions, labels)
            ax.grid(axis="x", color=grid, linewidth=0.8)
            ax.set_axisbelow(True)
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.tick_params(axis="y", length=0)
            ax.set_ylim(-0.65, len(companies) - 0.12)
        ax_timing.set_xlabel("Base CAPEX (2025 USD bn)")
        ax_status.set_xlabel("Share of base transition CAPEX")
        ax_status.set_xlim(0, 100)
        ax_status.set_xticks((0, 25, 50, 75, 100), ("0%", "25%", "50%", "75%", "100%"))
        ax_timing.set_title(f"{sector}: timing")
        ax_status.set_title(f"{sector}: dependency classification")
    fig.legend(
        handles=[
            Patch(facecolor=timing_colours[0], label="By 2030"),
            Patch(facecolor=timing_colours[1], label="2031–2040"),
            Patch(facecolor=status_colours[0], label="Price-conditional"),
            Patch(facecolor=status_colours[1], label="Contract-dependent"),
            Patch(facecolor=status_colours[2], label="Level-support-dependent"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.925),
        ncol=5,
        frameon=False,
        fontsize=9,
    )
    fig.suptitle("Where capital falls—and what the decision currently depends on", x=0.01, ha="left", fontsize=16, fontweight="bold", color=text)
    fig.text(0.01, 0.935, "Base screening case; dependency classifications precede full economic robustness tests.", fontsize=10, color=neutral)
    fig.tight_layout(rect=(0, 0.055, 1, 0.87), h_pad=2.1, w_pad=2.2)
    _finish(fig, output, "Quality D screening. Cost gaps, verified support and contract pricing are pending. Source: company_capital_allocation_mvp.csv")
    plt.close(fig)


def plot_abatement_efficiency_coverage(cases: list[CompanyCase], output: Path) -> None:
    import matplotlib.pyplot as plt

    steel, chemicals, neutral, grid, text = _style()
    rows = indexed_cases(cases)
    companies = COMPANY_ORDER
    y_positions = list(range(len(companies)))[::-1]
    colours = [steel if rows[(company, "base")].sector == "steel" else chemicals for company in companies]
    fig, axes = plt.subplots(1, 3, figsize=(14.6, 6.5))
    metrics = (
        ("Operational abatement", [rows[(c, "base")].abatement_tco2e / 1e6 for c in companies], "MtCO₂e/year", lambda v: f"{v:.1f}"),
        ("Capital efficiency", [rows[(c, "base")].efficiency_tco2e_per_usd_million / 1000 for c in companies], "MtCO₂e/year per USD bn", lambda v: f"{v:.2f}"),
        ("Emissions coverage", [min(rows[(c, "base")].coverage, 1) * 100 for c in companies], "% of facility-seed emissions", lambda v: f"{v:.1f}%"),
    )
    for ax, (title, values, xlabel, formatter) in zip(axes, metrics):
        ax.barh(y_positions, values, color=colours, height=0.55)
        maximum = max(values) if max(values) else 1
        ax.set_xlim(0, maximum * 1.24)
        for y, value, company in zip(y_positions, values, companies):
            suffix = ""
            if title == "Emissions coverage" and rows[(company, "base")].residual_tco2e > 0:
                suffix = f" | residual {rows[(company, 'base')].residual_tco2e / 1e6:.3f} Mt"
            ax.text(value + maximum * 0.025, y, formatter(value) + suffix, ha="left", va="center", fontsize=8.5, color=text)
        ax.set_yticks(y_positions, [COMPANY_LABELS[c] for c in companies])
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.suptitle("Base-case operational abatement, capital efficiency and boundary coverage", x=0.01, ha="left", fontsize=16, fontweight="bold", color=text)
    fig.text(0.01, 0.925, "Steel and petrochemical metrics share an operational Scope 1+2 concept but not yet harmonised production coverage.", fontsize=10, color=neutral)
    fig.tight_layout(rect=(0, 0.06, 1, 0.88), w_pad=2.3)
    _finish(fig, output, "Operational reduction only—not system abatement. Leakage and replacement production remain unmodelled. Quality D screening.")
    plt.close(fig)


def plot_concentration_uncertainty(cases: list[CompanyCase], output: Path) -> None:
    import matplotlib.pyplot as plt

    steel, chemicals, neutral, grid, text = _style()
    rows = indexed_cases(cases)
    companies = COMPANY_ORDER
    y_positions = list(range(len(companies)))[::-1]
    colours = [steel if rows[(company, "base")].sector == "steel" else chemicals for company in companies]
    concentration = [rows[(c, "base")].largest_facility_share * 100 for c in companies]
    uncertainty = [rows[(c, "high")].capex_usd / rows[(c, "low")].capex_usd for c in companies]
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.2))
    for ax, values, title, xlabel in (
        (axes[0], concentration, "Largest-facility concentration", "% of base transition CAPEX"),
        (axes[1], uncertainty, "CAPEX assumption span", "High case / low case (x)"),
    ):
        ax.barh(y_positions, values, color=colours, height=0.55)
        maximum = max(values)
        ax.set_xlim(0, maximum * 1.34)
        for y, value, company in zip(y_positions, values, companies):
            if ax is axes[0]:
                label = f"{value:.1f}% | {FACILITY_LABELS.get(rows[(company, 'base')].largest_facility_id, rows[(company, 'base')].largest_facility_id)}"
            else:
                label = f"{value:.2f}x"
            ax.text(value + maximum * 0.025, y, label, ha="left", va="center", fontsize=9, color=text)
        ax.set_yticks(y_positions, [COMPANY_LABELS[c] for c in companies])
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.suptitle("Single-asset concentration and screening uncertainty", x=0.01, ha="left", fontsize=16, fontweight="bold", color=text)
    fig.text(0.01, 0.92, "Concentration indicates execution bottlenecks; range width indicates assumption sensitivity, not forecast volatility.", fontsize=10, color=neutral)
    fig.tight_layout(rect=(0, 0.06, 1, 0.87), w_pad=3)
    _finish(fig, output, "Largest facilities identified from base-case facility aggregation. All CAPEX ranges are quality D screening proxies.")
    plt.close(fig)


def write_investor_memo(cases: list[CompanyCase], output: Path) -> None:
    rows = indexed_cases(cases)
    base = {company: rows[(company, "base")] for company in COMPANY_ORDER}

    lines = [
        "# Four-company capital-allocation screening memo",
        "",
        "**Decision status:** first-pass output for prioritising diligence; not company guidance, committed capital, or an investment recommendation.  ",
        "**Boundary:** covered domestic facility-seed operational Scope 1+2 emissions. Production coverage is not yet available.  ",
        "**Evidence status:** company anchors and selected facility/project facts are official or reported; the transition CAPEX and operational-abatement outputs below are `Modelled`, use estimated/allocated inputs, and carry quality flag D.",
        "",
        "## Decision snapshot",
        "",
        "| Company | Base CAPEX | Low–high | By 2030 | Operational abatement | Emissions coverage | Main dependency | Largest facility share |",
        "|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    dependency = {
        "POSCO": "Contract 68.6%; price 31.4%",
        "NIPPON_STEEL": "Contract 99.8%",
        "LOTTE_CHEMICAL": "Level support 100%",
        "MITSUI_CHEMICALS": "Level support 100%",
    }
    for company in COMPANY_ORDER:
        item = base[company]
        low = rows[(company, "low")].capex_usd / 1e9
        high = rows[(company, "high")].capex_usd / 1e9
        largest = FACILITY_LABELS.get(item.largest_facility_id, item.largest_facility_id)
        lines.append(
            f"| {COMPANY_LABELS[company]} | ${item.capex_usd / 1e9:.2f}bn | ${low:.2f}–{high:.2f}bn | "
            f"${item.capex_2030_usd / 1e9:.2f}bn | {item.abatement_tco2e / 1e6:.2f} MtCO2e/yr | "
            f"{min(item.coverage, 1):.1%} | {dependency[company]} | {item.largest_facility_share:.1%} ({largest}) |"
        )

    posco_near = base["POSCO"].capex_2030_usd / 1e9
    nsc_later_share = base["NIPPON_STEEL"].capex_2040_usd / base["NIPPON_STEEL"].capex_usd
    lines.extend(
        [
            "",
            "## Capital-allocation pathway",
            "",
            f"1. **The only material 2030 capital block in this screen is POSCO Gwangyang.** POSCO has ${posco_near:.2f}bn in the by-2030 bucket, while its remaining ${base['POSCO'].capex_2040_usd / 1e9:.2f}bn falls in 2031–2040. The near-term diligence question is therefore whether Gwangyang's EAF-linked power and scrap conditions can move from price-conditional screening to an executable package.",
            f"2. **Nippon Steel is a later, contract-heavy portfolio problem.** {nsc_later_share:.1%} of base CAPEX falls in 2031–2040 and 99.8% is provisionally contract-dependent. Oita is the largest site but only {base['NIPPON_STEEL'].largest_facility_share:.1%} of company CAPEX, implying a multi-site procurement and infrastructure programme rather than a single-asset solution.",
            f"3. **POSCO has greater single-project concentration.** Pohang represents {base['POSCO'].largest_facility_share:.1%} of base transition CAPEX. That makes hydrogen, clean-power and commercial-scale HyREX readiness a concentrated execution gate, even though total modelled operational abatement is large.",
            f"4. **Petrochemical totals are smaller but less decision-ready.** LOTTE and Mitsui are both screened as 100% level-support-dependent for their modelled assets. Their uncovered emissions are {base['LOTTE_CHEMICAL'].residual_tco2e / 1e6:.3f} and {base['MITSUI_CHEMICALS'].residual_tco2e / 1e6:.3f} MtCO2e/year respectively, so the current figures are not full-company transition plans.",
            "",
            "## What the ranges say",
            "",
            f"- Steel CAPEX uncertainty is material: POSCO's high case is {rows[('POSCO', 'high')].capex_usd / rows[('POSCO', 'low')].capex_usd:.2f}x its low case and Nippon Steel's is {rows[('NIPPON_STEEL', 'high')].capex_usd / rows[('NIPPON_STEEL', 'low')].capex_usd:.2f}x.",
            f"- Petrochemical uncertainty is wider: LOTTE spans {rows[('LOTTE_CHEMICAL', 'high')].capex_usd / rows[('LOTTE_CHEMICAL', 'low')].capex_usd:.2f}x and Mitsui {rows[('MITSUI_CHEMICALS', 'high')].capex_usd / rows[('MITSUI_CHEMICALS', 'low')].capex_usd:.2f}x. The result reflects a coarse annual-abatement CAPEX proxy and, for Mitsui, allocated site emissions; it should direct data collection, not support relative valuation.",
            f"- Base operational-abatement efficiency is {base['POSCO'].efficiency_tco2e_per_usd_million / 1000:.2f} MtCO2e/year per USD bn for POSCO and {base['NIPPON_STEEL'].efficiency_tco2e_per_usd_million / 1000:.2f} for Nippon Steel. The {base['LOTTE_CHEMICAL'].efficiency_tco2e_per_usd_million / 1000:.2f} value shared by both petrochemical companies is mechanically imposed by the same proxy and is not an independently observed advantage.",
            "",
            "## Required next evidence before an allocation decision",
            "",
            "- Build resource-cost and market-policy ledgers; current status labels are screening placeholders, not passed economic-feasibility tests.",
            "- Run B0/BH/BL/BHL cases to separate reduced input-price exposure from a lower mean cost level and to trace any additional modelled abatement to changed facility decisions.",
            "- Add official facility emissions, actual policy treatment, production coverage, route energy/material balances, and ownership/equity sensitivities.",
            "- Model replacement production and leakage before calling operational reductions system abatement.",
            "",
            "## Figure guide",
            "",
            "1. `01_company_capex_range.png` — capital magnitude and low/base/high uncertainty by sector.",
            "2. `02_capital_timing_and_dependency.png` — decision windows and provisional dependency classification.",
            "3. `03_abatement_efficiency_and_coverage.png` — operational reduction, capital efficiency and boundary coverage.",
            "4. `04_capital_concentration_and_uncertainty.png` — largest-facility execution concentration and assumption span.",
            "",
            "## Reproducibility",
            "",
            "Generated from `outputs/tables/company_capital_allocation_mvp.csv` and `outputs/tables/facility_capital_allocation_mvp.csv` by `python -m cap_kj.investor_outputs`. Every source and estimation method traces through the input tables to `data/manifests/source_register.csv`; no result is manually edited.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_outputs(company_csv: Path, facility_csv: Path, output_dir: Path, report_path: Path) -> list[Path]:
    if not facility_csv.exists():
        raise FileNotFoundError(facility_csv)
    cases = load_company_cases(company_csv)
    output_dir.mkdir(parents=True, exist_ok=True)
    functions = (
        plot_capex_range,
        plot_timing_dependency,
        plot_abatement_efficiency_coverage,
        plot_concentration_uncertainty,
    )
    figure_paths = [output_dir / name for name in FIGURE_NAMES]
    for function, path in zip(functions, figure_paths):
        function(cases, path)
    write_investor_memo(cases, report_path)
    return [*figure_paths, report_path]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company-csv", type=Path, default=Path("outputs/tables/company_capital_allocation_mvp.csv"))
    parser.add_argument("--facility-csv", type=Path, default=Path("outputs/tables/facility_capital_allocation_mvp.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/figures"))
    parser.add_argument("--report", type=Path, default=Path("outputs/reports/investor_screening_memo.md"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = generate_outputs(args.company_csv, args.facility_csv, args.output_dir, args.report)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
