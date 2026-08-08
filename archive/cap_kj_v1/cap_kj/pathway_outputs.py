"""Create investor-facing emissions-pathway figures and a concise interpretation memo."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Sequence


COMPANY_ORDER = ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS")
COMPANY_LABELS = {
    "POSCO": "POSCO",
    "NIPPON_STEEL": "Nippon Steel",
    "LOTTE_CHEMICAL": "LOTTE Chemical",
    "MITSUI_CHEMICALS": "Mitsui Chemicals",
}
SECTOR_GROUPS = (
    ("Steel", ("POSCO", "NIPPON_STEEL"), "#176b87"),
    ("Petrochemicals", ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS"), "#b65f32"),
)
FIGURE_NAMES = (
    "07_company_emissions_pathway.png",
    "08_2050_gap_to_capital.png",
    "09_uncertainty_effect_on_cost_gap.png",
    "10_capital_timing_vs_gap_closed.png",
)


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _f(row: dict[str, str], field: str) -> float:
    value = row[field]
    if value == "NA":
        raise ValueError(f"{field} is NA")
    return float(value)


def validate_pathway_rows(rows: list[dict[str, str]]) -> None:
    expected = {(company, str(year)) for company in COMPANY_ORDER for year in (2025, 2030, 2040, 2050)}
    actual = {(row["company_id"], row["year"]) for row in rows}
    if actual != expected or len(rows) != len(expected):
        raise ValueError("pathway table must have four milestone years for four companies")
    for row in rows:
        if _f(row, "unclosed_gap_to_net_zero_tco2e") < 0:
            raise ValueError("unclosed emissions gap cannot be negative")
        if not 0 <= _f(row, "required_reduction_closed_ratio") <= 1.000001:
            raise ValueError("gap-closure ratio must be within zero and one")
        implied = [_f(row, f"implied_unclosed_capital_{case}_usd_2025") for case in ("low", "base", "high")]
        if not 0 <= implied[0] <= implied[1] <= implied[2]:
            raise ValueError("implied residual capital range is not ordered")


def validate_uncertainty_rows(rows: list[dict[str, str]]) -> None:
    factors = {"capital_annualisation", "variable_resource", "combined_model_case"}
    expected = {(company, factor) for company in COMPANY_ORDER for factor in factors}
    actual = {(row["company_id"], row["factor"]) for row in rows}
    if actual != expected or len(rows) != len(expected):
        raise ValueError("uncertainty table must have three factors for four companies")
    for row in rows:
        low = _f(row, "annual_resource_gap_low_usd_2025")
        base = _f(row, "annual_resource_gap_base_usd_2025")
        high = _f(row, "annual_resource_gap_high_usd_2025")
        if not 0 <= low <= base <= high:
            raise ValueError("uncertainty range is not ordered")


def _style() -> dict[str, str]:
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
    return {
        "cp": "#8c969f",
        "nz": "#18806c",
        "identified": "#233f5b",
        "gap": "#d98455",
        "grid": "#d8dee3",
        "text": "#24313d",
        "muted": "#65717b",
        "capital": "#3b7b98",
    }


def _finish(fig, output: Path, note: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.text(0.01, 0.012, note, ha="left", va="bottom", fontsize=7.7, color="#65717b")
    fig.savefig(output, dpi=190, bbox_inches="tight", pad_inches=0.18)


def _by_company(rows: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        result[row["company_id"]].append(row)
    for company_rows in result.values():
        company_rows.sort(key=lambda row: int(row.get("year", "0")))
    return result


def plot_emissions_pathway(rows: list[dict[str, str]], output: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    colours = _style()
    grouped = _by_company(rows)
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.5))
    for ax, company in zip(axes.flat, COMPANY_ORDER):
        values = grouped[company]
        years = [int(row["year"]) for row in values]
        cp = [_f(row, "current_policies_operational_ghg_tco2e") / 1e6 for row in values]
        nz = [_f(row, "net_zero_operational_envelope_tco2e") / 1e6 for row in values]
        pathway = [_f(row, "conditional_facility_pathway_emissions_tco2e") / 1e6 for row in values]
        ax.plot(years, cp, color=colours["cp"], linestyle=(0, (4, 3)), linewidth=2.0)
        ax.plot(years, nz, color=colours["nz"], linewidth=2.7)
        ax.step(years, pathway, where="post", color=colours["identified"], linewidth=2.7)
        ax.fill_between(years, nz, pathway, where=[p > n for p, n in zip(pathway, nz)], color=colours["gap"], alpha=0.18)
        final = values[-1]
        gap = _f(final, "unclosed_gap_to_net_zero_tco2e") / 1e6
        closed = _f(final, "required_reduction_closed_ratio") * 100
        ax.text(
            0.02,
            0.04,
            f"2050 unclosed gap  {gap:.1f} Mt\nIdentified reduction / required  {closed:.0f}%",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=9,
            color=colours["text"],
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": colours["grid"], "alpha": 0.94},
        )
        ax.set_title(COMPANY_LABELS[company], loc="left")
        ax.set_xticks(years)
        ax.set_ylabel("Operational GHG (MtCO₂e/year)")
        ax.grid(axis="y", color=colours["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylim(bottom=0)
    legend = [
        Line2D([0], [0], color=colours["cp"], linestyle=(0, (4, 3)), linewidth=2, label="Current-policies proxy"),
        Line2D([0], [0], color=colours["nz"], linewidth=2.7, label="Net-zero envelope proxy"),
        Line2D([0], [0], color=colours["identified"], linewidth=2.7, label="Identified facility pathway"),
    ]
    fig.legend(handles=legend, loc="upper right", bbox_to_anchor=(0.99, 0.905), frameon=False, ncol=3)
    fig.suptitle("Company emissions pathways expose the unfinanced physical gap", x=0.01, ha="left", fontsize=17, fontweight="bold", color=colours["text"])
    fig.text(0.01, 0.932, "Official company Scope 1+2 baseline × sector proxy; facility pathway is conditional on modelled routes.", color=colours["muted"], fontsize=10)
    fig.tight_layout(rect=(0, 0.075, 1, 0.835), h_pad=2.0, w_pad=1.4)
    _finish(fig, output, "Quality D screening result. Sector proxies are not company carbon budgets; operational reductions are not system abatement. Sources: company_emissions_pathway_mvp.csv")
    plt.close(fig)


def plot_gap_to_capital(rows: list[dict[str, str]], output: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    colours = _style()
    indexed = {(row["company_id"], row["year"]): row for row in rows}
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.3))
    for row_ix, (sector, companies, sector_colour) in enumerate(SECTOR_GROUPS):
        gap_ax, capital_ax = axes[row_ix]
        y_positions = [1, 0]
        for y, company in zip(y_positions, companies):
            row = indexed[(company, "2050")]
            identified = _f(row, "conditional_facility_abatement_tco2e") / 1e6
            residual = _f(row, "unclosed_gap_to_net_zero_tco2e") / 1e6
            capex = _f(row, "cumulative_pathway_capex_usd_2025") / 1e9
            residual_capital = _f(row, "implied_unclosed_capital_base_usd_2025") / 1e9
            total_capital_low = _f(row, "implied_total_pathway_capital_low_usd_2025") / 1e9
            total_capital_base = _f(row, "implied_total_pathway_capital_base_usd_2025") / 1e9
            total_capital_high = _f(row, "implied_total_pathway_capital_high_usd_2025") / 1e9
            annual = _f(row, "annual_resource_gap_at_committed_pathway_scope_usd_2025") / 1e9
            gap_ax.barh(y, identified, color=sector_colour, height=0.48)
            gap_ax.barh(y, residual, left=identified, color=colours["gap"], height=0.48, alpha=0.86)
            total = identified + residual
            gap_ax.text(total, y + 0.30, f"required reduction {total:.1f} Mt", ha="right", va="bottom", fontsize=8.7, color=colours["muted"])
            if identified / total >= 0.12:
                gap_ax.text(identified / 2, y, f"{identified:.1f}\nidentified", ha="center", va="center", fontsize=8.5, color="white")
            if residual / total >= 0.12:
                gap_ax.text(identified + residual / 2, y, f"{residual:.1f}\nunclosed", ha="center", va="center", fontsize=8.5, color="white")
            capital_ax.barh(y, capex, color=colours["capital"], height=0.48)
            capital_ax.barh(y, residual_capital, left=capex, color=colours["gap"], height=0.48, alpha=0.86)
            capital_ax.hlines(y + 0.31, total_capital_low, total_capital_high, color=colours["text"], linewidth=1.5)
            capital_ax.scatter((total_capital_low, total_capital_high), (y + 0.31, y + 0.31), marker="|", s=38, color=colours["text"])
            capital_ax.text(total_capital_base, y + 0.34, f"total ${total_capital_base:.2f}bn ({total_capital_low:.2f}–{total_capital_high:.2f})", ha="center", va="bottom", fontsize=8.2, color=colours["muted"])
            if capex / total_capital_base >= 0.13:
                capital_ax.text(capex / 2, y, f"${capex:.2f}bn\nidentified", ha="center", va="center", fontsize=8.1, color="white")
            if residual_capital / total_capital_base >= 0.13:
                capital_ax.text(capex + residual_capital / 2, y, f"${residual_capital:.2f}bn\nimplied", ha="center", va="center", fontsize=8.1, color="white")
            capital_ax.text(0, y - 0.31, f"annual resource gap ${annual:.2f}bn/yr", ha="left", va="top", fontsize=8.5, color=colours["gap"])
        labels = [COMPANY_LABELS[c] for c in companies]
        for ax in (gap_ax, capital_ax):
            ax.set_yticks(y_positions, labels)
            ax.grid(axis="x", color=colours["grid"], linewidth=0.8)
            ax.set_axisbelow(True)
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.tick_params(axis="y", length=0)
            ax.set_ylim(-0.65, 1.55)
        gap_ax.set_title(f"{sector}: 2050 reduction gap", loc="left")
        gap_ax.set_xlabel("MtCO₂e/year vs baseline")
        capital_ax.set_title(f"{sector}: identified + implied residual capital", loc="left")
        capital_ax.set_xlabel("Cumulative transition CAPEX (2025 USD bn)")
        capital_ax.set_xlim(right=max(_f(indexed[(c, "2050")], "implied_total_pathway_capital_high_usd_2025") / 1e9 for c in companies) * 1.12)
    fig.legend(
        handles=[Patch(facecolor="#176b87", label="Identified route / capital"), Patch(facecolor=colours["gap"], label="Unclosed gap / implied residual capital")],
        loc="upper right",
        bbox_to_anchor=(0.99, 0.905),
        frameon=False,
        ncol=2,
    )
    fig.suptitle("Translate the 2050 emissions gap into identified and implied capital", x=0.01, ha="left", fontsize=16.5, fontweight="bold", color=colours["text"])
    fig.text(0.01, 0.928, "Orange emissions have no identified facility route; orange capital extrapolates the current pathway's capital intensity. Whisker = low–high.", color=colours["muted"], fontsize=10)
    fig.tight_layout(rect=(0, 0.075, 1, 0.835), h_pad=2.0, w_pad=2.3)
    _finish(fig, output, "Sector rows use different scales. Implied residual CAPEX is a quality-D extrapolation, not an identified project, company guidance or financing commitment.")
    plt.close(fig)


def plot_uncertainty(rows: list[dict[str, str]], output: Path) -> None:
    import matplotlib.pyplot as plt

    colours = _style()
    labels = {
        "capital_annualisation": "Capital annualisation",
        "variable_resource": "Variable resources",
        "combined_model_case": "Combined model case",
    }
    indexed = {(row["company_id"], row["factor"]): row for row in rows}
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.8))
    for ax, (sector, companies, sector_colour) in zip(axes, SECTOR_GROUPS):
        y = 0
        ticks: list[int] = []
        tick_labels: list[str] = []
        for company in companies:
            for factor in ("capital_annualisation", "variable_resource", "combined_model_case"):
                row = indexed[(company, factor)]
                low = _f(row, "annual_resource_gap_low_usd_2025") / 1e9
                base = _f(row, "annual_resource_gap_base_usd_2025") / 1e9
                high = _f(row, "annual_resource_gap_high_usd_2025") / 1e9
                ax.hlines(y, low, high, color=sector_colour, linewidth=4.2, alpha=0.48)
                ax.scatter((low, high), (y, y), marker="|", s=50, color=sector_colour)
                ax.scatter(base, y, s=58, color=sector_colour, edgecolor="white", linewidth=0.9, zorder=3)
                ax.text(high, y + 0.16, f"{high / low:.1f}×", ha="right", va="bottom", fontsize=8.3, color=colours["muted"])
                ticks.append(y)
                tick_labels.append(labels[factor])
                y += 1
            y += 0.6
        for start, company in zip((0, 3.6), companies):
            ax.text(0.0, start + 3.05, COMPANY_LABELS[company], ha="left", va="bottom", fontweight="bold", fontsize=10.5, color=colours["text"], transform=ax.get_yaxis_transform())
        ax.set_yticks(ticks, tick_labels)
        ax.set_xlabel("Annual resource-gap proxy (2025 USD bn/year)")
        ax.set_title(sector, loc="left")
        ax.grid(axis="x", color=colours["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_ylim(-0.55, y - 0.35)
    fig.suptitle("Uncertainty changes the funding gap much more than the physical pathway", x=0.01, ha="left", fontsize=17, fontweight="bold", color=colours["text"])
    fig.text(0.01, 0.928, "Whisker = low–high deterministic sensitivity; dot = base. Label = high/low multiple.", color=colours["muted"], fontsize=10)
    fig.tight_layout(rect=(0, 0.075, 1, 0.88), w_pad=3.0)
    _finish(fig, output, "Fixed base pathway scope. Ranges are scenarios, not probabilities or market volatility. Verified incentives and incumbent-cost offsets remain unavailable.")
    plt.close(fig)


def plot_capital_timing(rows: list[dict[str, str]], output: Path) -> None:
    import matplotlib.pyplot as plt

    colours = _style()
    grouped = _by_company(rows)
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.4))
    for ax, company in zip(axes.flat, COMPANY_ORDER):
        values = [row for row in grouped[company] if row["year"] != "2025"]
        years = [int(row["year"]) for row in values]
        capex = [_f(row, "cumulative_pathway_capex_usd_2025") / 1e9 for row in values]
        closure = [_f(row, "required_reduction_closed_ratio") * 100 for row in values]
        bars = ax.bar(years, capex, width=4.5, color=colours["capital"], alpha=0.9)
        ax.set_ylabel("Cumulative CAPEX (USD bn)")
        ax.set_xticks(years)
        ax.set_ylim(bottom=0)
        for bar, value in zip(bars, capex):
            ax.text(bar.get_x() + bar.get_width() / 2, value, f"${value:.2f}bn", ha="center", va="bottom", fontsize=8.4, color=colours["text"])
        closure_ax = ax.twinx()
        closure_ax.plot(years, closure, color=colours["gap"], marker="o", linewidth=2.4, markersize=6)
        for year, value in zip(years, closure):
            closure_ax.text(year, value + 3.5, f"{value:.0f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color=colours["gap"])
        closure_ax.set_ylabel("Required reduction closed")
        closure_ax.set_ylim(0, 115)
        closure_ax.spines[["top"]].set_visible(False)
        closure_ax.tick_params(axis="y", colors=colours["gap"])
        ax.set_title(COMPANY_LABELS[company], loc="left")
        ax.grid(axis="y", color=colours["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Capital timing alone does not guarantee convergence with the net-zero envelope", x=0.01, ha="left", fontsize=17, fontweight="bold", color=colours["text"])
    fig.text(0.01, 0.93, "Bars show cumulative identified CAPEX; orange line shows the share of each milestone reduction requirement closed.", color=colours["muted"], fontsize=10)
    fig.tight_layout(rect=(0, 0.075, 1, 0.895), h_pad=2.2, w_pad=2.0)
    _finish(fig, output, "A closure ratio may fall after 2040 because the net-zero envelope tightens while no additional facility route is identified. Quality D screening result.")
    plt.close(fig)


def _money(value: float) -> str:
    return f"${value / 1e9:.2f}bn"


def write_report(pathway_rows: list[dict[str, str]], uncertainty_rows: list[dict[str, str]], output: Path) -> None:
    indexed = {(row["company_id"], row["year"]): row for row in pathway_rows}
    uncertainty = {(row["company_id"], row["factor"]): row for row in uncertainty_rows}
    lines = [
        "# Emissions pathway → capital allocation: investor view v1",
        "",
        "## What this output answers",
        "",
        "The model starts from each company's official operational Scope 1+2 baseline, applies a common sector emissions-envelope proxy, subtracts physically available modelled facility reductions by decision year, and attaches the corresponding transition CAPEX and annual resource-gap proxy. The residual stays visible and receives a separately labelled low/base/high implied-capital extrapolation rather than being presented as an identified project.",
        "",
        "## 2050 decision screen",
        "",
        "| Company | Identified reduction / requirement | Unclosed gap | Identified CAPEX | Implied residual CAPEX | Implied total CAPEX | Annual resource gap | Combined high/low |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for company in COMPANY_ORDER:
        row = indexed[(company, "2050")]
        sensitivity = uncertainty[(company, "combined_model_case")]
        lines.append(
            f"| {COMPANY_LABELS[company]} | {_f(row, 'required_reduction_closed_ratio'):.0%} | "
            f"{_f(row, 'unclosed_gap_to_net_zero_tco2e') / 1e6:.2f} MtCO₂e/yr | "
            f"{_money(_f(row, 'cumulative_pathway_capex_usd_2025'))} | "
            f"{_money(_f(row, 'implied_unclosed_capital_base_usd_2025'))} "
            f"({_money(_f(row, 'implied_unclosed_capital_low_usd_2025'))}–{_money(_f(row, 'implied_unclosed_capital_high_usd_2025'))}) | "
            f"{_money(_f(row, 'implied_total_pathway_capital_base_usd_2025'))} | "
            f"{_money(_f(row, 'annual_resource_gap_at_committed_pathway_scope_usd_2025'))}/yr | "
            f"{_f(sensitivity, 'high_over_low_multiple'):.1f}× |"
        )
    lines.extend(
        [
            "",
            "## Investor interpretation",
            "",
            "- **Pathway credibility:** Nippon Steel has the highest identified 2050 gap closure (77%) but also the largest identified capital requirement and annual funding gap. Its route capacities remain modelled rather than project-verified.",
            "- **Physical bottleneck:** POSCO closes only 41% of its 2050 required reduction in this screen. The disclosed 2.5 Mt/year Gwangyang EAF is applied at 13.15% of the allocated works activity rather than treating the earlier full-route screen as a committed project.",
            "- **Missing capital is analytically important:** LOTTE and Mitsui each identify roughly half of the 2050 reduction requirement. The model now gives the residual an explicit low/base/high capital extrapolation while keeping it separate from identified projects.",
            "- **Cost uncertainty dominates:** combined annual-resource-gap cases span 8.8×–14.6×. This is a deterministic sensitivity driven by screening assumptions, not a probability distribution. Variable-resource prices contribute more spread than capital annualisation alone.",
            "- **Milestone risk:** a company can appear aligned in 2040 and fall behind by 2050 if its identified facility sequence stops while the reference envelope continues to tighten. Nippon Steel illustrates this pattern.",
            "",
            "## Boundaries and next evidence gates",
            "",
            "1. The sector envelopes are global proxies scaled to company baselines, not company-specific carbon budgets or official NGFS company trajectories.",
            "2. Except for the disclosed POSCO Gwangyang EAF block, selected route capacity is not project-verified. Implied residual CAPEX extrapolates the identified pathway's base USD per annual tCO2 and scales low/high with company model-case capital intensity; it is not an identified project or financing requirement.",
            "3. Reductions are operational Scope 1+2, not system abatement. Replacement production, leakage, product demand, Scope 3 and trade effects remain outside the calculation.",
            "4. Annual resource gaps exclude verified incentives, incumbent-cost offsets, green premia and financing structure; they must not be read as EBITDA or cash-flow forecasts.",
            "5. The next highest-value data work is project-specific route capacity and decision timing, followed by verified electricity/hydrogen/feedstock price and policy/contract coverage.",
            "",
            "## Source anchors",
            "",
            "- Official company disclosures supply the four operational emissions baselines already recorded in the source register.",
            "- SBTi Steel Guidance Table 9 supplies the ore-based 2020/2030/2040/2050 intensity benchmark used to construct the steel net-zero proxy.",
            "- IEA steel and primary-chemicals pathways provide the current-policy and net-zero directional anchors; the project stores all interpolations and ranges in `data/processed/sector_emissions_pathway_anchors_mvp.csv`.",
            "- NGFS Phase V scenario definitions establish the `Current Policies` and `Net Zero 2050` framing; the current v1 does not claim to contain solved NGFS company-level outputs.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_outputs(pathway_csv: Path, uncertainty_csv: Path, output_dir: Path, report: Path) -> list[Path]:
    pathway_rows = _read(pathway_csv)
    uncertainty_rows = _read(uncertainty_csv)
    validate_pathway_rows(pathway_rows)
    validate_uncertainty_rows(uncertainty_rows)
    paths = [output_dir / name for name in FIGURE_NAMES]
    plot_emissions_pathway(pathway_rows, paths[0])
    plot_gap_to_capital(pathway_rows, paths[1])
    plot_uncertainty(uncertainty_rows, paths[2])
    plot_capital_timing(pathway_rows, paths[3])
    write_report(pathway_rows, uncertainty_rows, report)
    return [*paths, report]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pathway-csv", type=Path, required=True)
    parser.add_argument("--uncertainty-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    generate_outputs(args.pathway_csv, args.uncertainty_csv, args.output_dir, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
