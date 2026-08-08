"""Build a policy-conditioned capital-flow bridge from pathway and support screens."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from .model import ModelInputError


D = Decimal
COMPANY_ORDER = ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS")
COMPANY_LABELS = {
    "POSCO": "POSCO",
    "NIPPON_STEEL": "Nippon Steel",
    "LOTTE_CHEMICAL": "LOTTE Chemical",
    "MITSUI_CHEMICALS": "Mitsui Chemicals",
}
MECHANISMS = ("B0", "BH", "BL", "BHL")
MECHANISM_LABELS = {
    "B0": "Current conditions",
    "BH": "Risk-only cover",
    "BL": "Level support only",
    "BHL": "Combined support",
}
OUTPUT_FIELDS = (
    "company_id",
    "company_name",
    "country",
    "sector",
    "total_pathway_capital_low_usd_2025",
    "total_pathway_capital_base_usd_2025",
    "total_pathway_capital_high_usd_2025",
    "identified_route_capital_usd_2025",
    "unidentified_physical_capital_low_usd_2025",
    "unidentified_physical_capital_base_usd_2025",
    "unidentified_physical_capital_high_usd_2025",
    "screening_investable_capital_B0_usd_2025",
    "screening_investable_capital_BH_usd_2025",
    "screening_investable_capital_BL_usd_2025",
    "screening_investable_capital_BHL_usd_2025",
    "screening_unlocked_abatement_B0_tco2e",
    "screening_unlocked_abatement_BH_tco2e",
    "screening_unlocked_abatement_BL_tco2e",
    "screening_unlocked_abatement_BHL_tco2e",
    "enabling_mechanism",
    "risk_covered_capital_at_enabling_mechanism_usd_2025",
    "level_support_equivalent_at_enabling_mechanism_usd_2025",
    "premium_relevant_exposure_before",
    "premium_relevant_exposure_after_enabling_mechanism",
    "identified_pathway_2050_gap_closure_ratio",
    "transition_risk_premium_bps",
    "risk_premium_pricing_status",
    "risk_premium_identity",
    "currency",
    "price_year",
    "value_type",
    "quality_flag",
    "source_id",
    "formula_or_method",
    "boundary_note",
)
FIGURE_NAMES = (
    "11_capital_flow_policy_bridge.png",
    "12_premium_relevant_exposure.png",
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


def build_capital_flow_bridge(
    pathway_rows: list[dict[str, str]],
    support_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    """Translate mechanism status changes into screening-investable capital and abatement."""

    pathway = {
        row["company_id"]: row
        for row in pathway_rows
        if row["year"] == "2050"
    }
    support = {
        (row["company_id"], row["mechanism_case"]): row
        for row in support_rows
        if row["assumption_case"] == "base"
    }
    if set(pathway) != set(COMPANY_ORDER):
        raise ModelInputError("2050 pathway table must contain the fixed four-company sample")
    expected_support = {(company, mechanism) for company in COMPANY_ORDER for mechanism in MECHANISMS}
    if set(support) != expected_support:
        raise ModelInputError("support table must contain four base mechanisms for each company")

    results: list[dict[str, object]] = []
    for company_id in COMPANY_ORDER:
        path = pathway[company_id]
        identified_capital = _decimal(path["cumulative_pathway_capex_usd_2025"], "identified capital")
        identified_abatement = _decimal(path["conditional_facility_abatement_tco2e"], "identified abatement")
        total_low = _decimal(path["implied_total_pathway_capital_low_usd_2025"], "total capital low")
        total_base = _decimal(path["implied_total_pathway_capital_base_usd_2025"], "total capital base")
        total_high = _decimal(path["implied_total_pathway_capital_high_usd_2025"], "total capital high")
        residual_low = _decimal(path["implied_unclosed_capital_low_usd_2025"], "residual capital low")
        residual_base = _decimal(path["implied_unclosed_capital_base_usd_2025"], "residual capital base")
        residual_high = _decimal(path["implied_unclosed_capital_high_usd_2025"], "residual capital high")
        if not D("0") <= residual_low <= residual_base <= residual_high:
            raise ModelInputError(f"residual capital range is not ordered for {company_id}")
        if not total_low <= total_base <= total_high:
            raise ModelInputError(f"total capital range is not ordered for {company_id}")

        investable: dict[str, Decimal] = {}
        unlocked: dict[str, Decimal] = {}
        for mechanism in MECHANISMS:
            support_row = support[(company_id, mechanism)]
            enabled_share = _decimal(support_row["transition_enabled_capex_share"], "enabled capital share")
            if not D("0") <= enabled_share <= D("1"):
                raise ModelInputError(f"enabled share outside zero-one for {company_id}/{mechanism}")
            investable[mechanism] = identified_capital * enabled_share
            unlocked[mechanism] = identified_abatement * enabled_share

        enabling = "BH" if investable["BH"] > 0 else "BHL" if investable["BHL"] > 0 else "none"
        if enabling == "none":
            raise ModelInputError(f"no enabling mechanism in current rule screen for {company_id}")
        enabling_row = support[(company_id, enabling)]
        potential = _decimal(enabling_row["potential_transition_capex_usd_2025"], "support potential capital")
        if potential <= 0:
            raise ModelInputError(f"support potential capital must be positive for {company_id}")
        contract_share = _decimal(enabling_row["contract_covered_capex_usd_2025"], "contract cover") / potential
        level_share = _decimal(enabling_row["screening_level_support_total_usd_2025"], "level support") / potential
        risk_covered = identified_capital * contract_share
        level_support = identified_capital * level_share
        exposure_after = _decimal(
            enabling_row["capex_weighted_residual_common_exposure_ratio"],
            "residual common exposure",
        )
        if not D("0") <= exposure_after <= D("1"):
            raise ModelInputError(f"residual exposure outside zero-one for {company_id}")

        boundary = (
            "Rule-based investability screen, not observed capital flow. Risk-covered capital is exposure coverage, not cash support; "
            "level support is a capital-equivalent stress. Risk-premium basis points require factor prices and remain NA."
        )
        if company_id == "MITSUI_CHEMICALS":
            boundary += " Mitsui support shares originate from the legacy 85% emissions boundary and are scaled to the 97.46% primary pathway capital; exact cash claims remain gated."
        results.append(
            {
                "company_id": company_id,
                "company_name": path["company_name"],
                "country": path["country"],
                "sector": path["sector"],
                "total_pathway_capital_low_usd_2025": total_low,
                "total_pathway_capital_base_usd_2025": total_base,
                "total_pathway_capital_high_usd_2025": total_high,
                "identified_route_capital_usd_2025": identified_capital,
                "unidentified_physical_capital_low_usd_2025": residual_low,
                "unidentified_physical_capital_base_usd_2025": residual_base,
                "unidentified_physical_capital_high_usd_2025": residual_high,
                **{f"screening_investable_capital_{mechanism}_usd_2025": investable[mechanism] for mechanism in MECHANISMS},
                **{f"screening_unlocked_abatement_{mechanism}_tco2e": unlocked[mechanism] for mechanism in MECHANISMS},
                "enabling_mechanism": enabling,
                "risk_covered_capital_at_enabling_mechanism_usd_2025": risk_covered,
                "level_support_equivalent_at_enabling_mechanism_usd_2025": level_support,
                "premium_relevant_exposure_before": D("1"),
                "premium_relevant_exposure_after_enabling_mechanism": exposure_after,
                "identified_pathway_2050_gap_closure_ratio": _decimal(path["required_reduction_closed_ratio"], "gap closure"),
                "transition_risk_premium_bps": "NA",
                "risk_premium_pricing_status": "exposure_estimated_market_price_of_risk_not_available",
                "risk_premium_identity": "annual transition risk premium bps = sum(cost exposure beta_k x market price lambda_k) / invested capital x 10000; lambda_k is NA",
                "currency": "USD",
                "price_year": "2025 screening proxy",
                "value_type": "modelled",
                "quality_flag": "D",
                "source_id": _join(
                    path["source_id"],
                    enabling_row["source_id"],
                    "UNDP_DREI_FRAMEWORK",
                    "OECD_DERISK_INFRA_2021",
                    "BIS_CARBON_PREMIUM_2021",
                ),
                "formula_or_method": "physical need and identified capital come from the 2050 pathway table; investable capital and unlocked abatement equal identified pathway amounts times the base B0/BH/BL/BHL enabled-capital share; risk-cover and level-support amounts scale the mechanism shares to the identified pathway capital",
                "boundary_note": boundary,
            }
        )
    return results


def _f(row: dict[str, str] | dict[str, object], field: str) -> float:
    value = row[field]
    if value == "NA":
        raise ValueError(f"{field} is NA")
    return float(value)


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
        "identified": "#28768e",
        "unidentified": "#d98455",
        "investable": "#21836f",
        "inactive": "#d8dee3",
        "risk": "#b96836",
        "text": "#24313d",
        "muted": "#65717b",
        "grid": "#d8dee3",
    }


def _finish(fig, output: Path, note: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.text(0.01, 0.012, note, ha="left", va="bottom", fontsize=7.7, color="#65717b")
    fig.savefig(output, dpi=190, bbox_inches="tight", pad_inches=0.18)


def plot_capital_flow(rows: list[dict[str, object]], output: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    colours = _style()
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 8.5))
    y_positions = {"need": 4.4, "B0": 3.0, "BH": 2.0, "BL": 1.0, "BHL": 0.0}
    for ax, company_id in zip(axes.flat, COMPANY_ORDER):
        row = next(row for row in rows if row["company_id"] == company_id)
        identified = _f(row, "identified_route_capital_usd_2025") / 1e9
        residual = _f(row, "unidentified_physical_capital_base_usd_2025") / 1e9
        total_low = _f(row, "total_pathway_capital_low_usd_2025") / 1e9
        total_base = _f(row, "total_pathway_capital_base_usd_2025") / 1e9
        total_high = _f(row, "total_pathway_capital_high_usd_2025") / 1e9
        ax.barh(y_positions["need"], identified, height=0.58, color=colours["identified"])
        ax.barh(y_positions["need"], residual, left=identified, height=0.58, color=colours["unidentified"])
        ax.hlines(y_positions["need"] + 0.38, total_low, total_high, linewidth=1.4, color=colours["text"])
        ax.scatter((total_low, total_high), (y_positions["need"] + 0.38,) * 2, marker="|", s=36, color=colours["text"])
        ax.text(identified / 2, y_positions["need"], f"${identified:.2f}bn\nroute identified", ha="center", va="center", color="white", fontsize=8.4)
        ax.text(identified + residual / 2, y_positions["need"], f"${residual:.2f}bn\nroute missing", ha="center", va="center", color="white", fontsize=8.4)
        ax.text(total_base, y_positions["need"] + 0.43, f"total ${total_base:.2f}bn", ha="center", va="bottom", fontsize=8.6, color=colours["muted"])

        for mechanism in MECHANISMS:
            capital = _f(row, f"screening_investable_capital_{mechanism}_usd_2025") / 1e9
            abatement = _f(row, f"screening_unlocked_abatement_{mechanism}_tco2e") / 1e6
            y = y_positions[mechanism]
            ax.barh(y, identified, height=0.46, color=colours["inactive"], alpha=0.55)
            if capital > 0:
                ax.barh(y, capital, height=0.46, color=colours["investable"])
                ax.text(capital / 2, y, f"${capital:.2f}bn  |  {abatement:.1f} Mt", ha="center", va="center", color="white", fontsize=8.2)
            else:
                ax.text(0, y, "0 investable", ha="left", va="center", fontsize=8.2, color=colours["muted"])
        ax.set_yticks([y_positions["need"], *[y_positions[m] for m in MECHANISMS]], ["2050 capital need", *[MECHANISM_LABELS[m] for m in MECHANISMS]])
        ax.set_title(COMPANY_LABELS[company_id], loc="left")
        ax.set_xlabel("Capital (2025 USD bn)")
        ax.set_xlim(0, total_high * 1.12)
        ax.set_ylim(-0.55, 5.05)
        ax.grid(axis="x", color=colours["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.legend(
        handles=[
            Patch(facecolor=colours["identified"], label="Identified route capital"),
            Patch(facecolor=colours["unidentified"], label="Unidentified physical capital"),
            Patch(facecolor=colours["investable"], label="Screening-investable capital"),
        ],
        loc="upper right",
        bbox_to_anchor=(0.99, 0.905),
        frameon=False,
        ncol=3,
    )
    fig.suptitle("Policy changes when capital becomes investable—and what emissions it can change", x=0.01, ha="left", fontsize=16.5, fontweight="bold", color=colours["text"])
    fig.text(0.01, 0.93, "Current-condition and policy cases are rule-based screens. Green labels connect investable capital directly to operational abatement.", fontsize=10, color=colours["muted"])
    fig.tight_layout(rect=(0, 0.075, 1, 0.835), h_pad=2.0, w_pad=2.4)
    _finish(fig, output, "B0=current; BH=risk-only cover; BL=level support only; BHL=combined. Not observed financing, company commitments or system abatement.")
    plt.close(fig)


def plot_premium_exposure(rows: list[dict[str, object]], output: Path) -> None:
    import matplotlib.pyplot as plt

    colours = _style()
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.6))
    groups = (
        ("Steel", ("POSCO", "NIPPON_STEEL")),
        ("Petrochemicals", ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS")),
    )
    for ax, (sector, companies) in zip(axes, groups):
        for y, company_id in zip((1, 0), companies):
            row = next(row for row in rows if row["company_id"] == company_id)
            before = _f(row, "premium_relevant_exposure_before") * 100
            after = _f(row, "premium_relevant_exposure_after_enabling_mechanism") * 100
            risk_cover = _f(row, "risk_covered_capital_at_enabling_mechanism_usd_2025") / 1e9
            support = _f(row, "level_support_equivalent_at_enabling_mechanism_usd_2025") / 1e9
            mechanism = str(row["enabling_mechanism"])
            ax.annotate("", xy=(after, y), xytext=(before, y), arrowprops={"arrowstyle": "-|>", "lw": 2.5, "color": colours["risk"]})
            ax.scatter(before, y, s=62, color=colours["inactive"], edgecolor=colours["text"], linewidth=0.8, zorder=3)
            ax.scatter(after, y, s=85, color=colours["investable"], edgecolor="white", linewidth=1.0, zorder=3)
            ax.text(before, y + 0.18, "100%", ha="center", va="bottom", fontsize=8.5, color=colours["muted"])
            ax.text(after, y + 0.18, f"{after:.0f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color=colours["text"])
            policy = f"{mechanism}: USD {risk_cover:.2f}bn risk-covered"
            if support > 0:
                policy += f" + USD {support:.2f}bn level support"
            ax.text((before + after) / 2, y - 0.20, policy, ha="center", va="top", fontsize=8.5, color=colours["muted"])
        ax.set_yticks((1, 0), [COMPANY_LABELS[c] for c in companies])
        ax.set_xlim(0, 108)
        ax.set_ylim(-0.55, 1.55)
        ax.set_xlabel("Residual common cost exposure (%)")
        ax.set_title(sector, loc="left")
        ax.grid(axis="x", color=colours["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.suptitle("De-risking reduces premium-relevant exposure before capital crosses the threshold", x=0.01, ha="left", fontsize=16.2, fontweight="bold", color=colours["text"])
    fig.text(0.01, 0.91, "Risk premium = exposure × market price of risk. Exposure is screened here; the market price and basis-point premium remain NA.", fontsize=10, color=colours["muted"])
    fig.tight_layout(rect=(0, 0.09, 1, 0.82), w_pad=3.0)
    _finish(fig, output, "Risk cover transfers or stabilises exposure; it is not cash support. Results are mechanism diagnostics, not measured financing-cost reductions.")
    plt.close(fig)


def _money(value: object) -> str:
    return f"${float(value) / 1e9:.2f}bn"


def write_report(rows: list[dict[str, object]], output: Path) -> None:
    lines = [
        "# Capital flow, policy closure and premium relevance — investor view v1",
        "",
        "## Analytical correction",
        "",
        "Required CAPEX is not a capital flow. A capital flow appears only when an identified facility investment crosses an investability condition. CAP-KJ now separates the physical capital need, central cost-level support, uncertainty/risk coverage, screening-investable capital and operational emissions consequence.",
        "",
        "## Company capital-flow screen",
        "",
        "| Company | Total 2050 capital need | Route-identified capital | Current-condition investable | Enabling bundle | Risk-covered capital | Level-support equivalent | Capital unlocked | Operational reduction unlocked | Residual premium-relevant exposure |",
        "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        mechanism = str(row["enabling_mechanism"])
        lines.append(
            f"| {COMPANY_LABELS[str(row['company_id'])]} | {_money(row['total_pathway_capital_base_usd_2025'])} | "
            f"{_money(row['identified_route_capital_usd_2025'])} | {_money(row['screening_investable_capital_B0_usd_2025'])} | "
            f"{mechanism} | {_money(row['risk_covered_capital_at_enabling_mechanism_usd_2025'])} | "
            f"{_money(row['level_support_equivalent_at_enabling_mechanism_usd_2025'])} | "
            f"{_money(row[f'screening_investable_capital_{mechanism}_usd_2025'])} | "
            f"{float(row[f'screening_unlocked_abatement_{mechanism}_tco2e']) / 1e6:.2f} MtCO₂e/yr | "
            f"{float(row['premium_relevant_exposure_after_enabling_mechanism']):.0%} |"
        )
    lines.extend(
        [
            "",
            "## What the investment gap contains",
            "",
            "1. **Physical route gap:** capital implied by the emissions envelope but not yet attached to a project-specific facility route.",
            "2. **Cost-level gap:** the positive central resource/economic gap that risk reduction alone cannot close; represented by a level-support-equivalent stress, not verified cash.",
            "3. **Uncertainty gap:** the portion of identified capital whose investability depends on price, input or contract risk coverage.",
            "4. **Residual risk:** common cost exposure remaining after the enabling bundle; this is the quantity relevant to a future transition risk premium.",
            "",
            "## Risk-premium interpretation",
            "",
            "A meaningful investor risk premium is the price of bearing systematic transition exposure, not the high-minus-base cost stress. CAP-KJ therefore uses the identity:",
            "",
            "`annual transition risk premium (bps) = Σ(cost exposure beta × market price of transition risk) / invested capital × 10,000`",
            "",
            "Stage 1 currently estimates a rule-based residual exposure but does not have the market price of risk. The basis-point premium is therefore `NA`, not zero. A numerical premium requires covariance-aware market histories, facility cash-flow sensitivities, observed project hurdle rates or financing spreads, and actual contract/policy terms.",
            "",
            "## Investor and policy meaning",
            "",
            "- Under the current provisional status rules, no identified block is investable in B0. This is a conservative diagnostic, not evidence that no company is investing.",
            "- Steel crosses the screen with risk-only coverage (BH): contracts, price floors, guarantees or infrastructure commitments address uncertainty without a modelled level-support payment.",
            "- Petrochemicals cross only under combined support (BHL): risk coverage alone reduces exposure, while level support alone lowers cost, but neither is sufficient by itself.",
            "- Public policy should be judged by private capital mobilised, operational reduction unlocked and residual public/risk exposure—not by subsidy amount alone.",
            "",
            "## Evidence boundary",
            "",
            "UNDP's DREI framework distinguishes public interventions that reduce, transfer or compensate investment risk. OECD evidence similarly treats public de-risking as project-risk transfer intended to mobilise private capital. BIS research shows that carbon exposure can be priced in loan spreads, but its empirical coefficient cannot be transplanted into these four companies. The current output uses those concepts while preserving the Stage 1 no-invented-premium rule.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_outputs(
    pathway_csv: Path,
    support_csv: Path,
    table_output: Path,
    figure_dir: Path,
    report_output: Path,
) -> list[Path]:
    rows = build_capital_flow_bridge(_read(pathway_csv), _read(support_csv))
    _write(table_output, rows)
    figure_paths = [figure_dir / name for name in FIGURE_NAMES]
    plot_capital_flow(rows, figure_paths[0])
    plot_premium_exposure(rows, figure_paths[1])
    write_report(rows, report_output)
    return [table_output, *figure_paths, report_output]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pathway-csv", type=Path, required=True)
    parser.add_argument("--support-csv", type=Path, required=True)
    parser.add_argument("--table-output", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        generate_outputs(args.pathway_csv, args.support_csv, args.table_output, args.figure_dir, args.report_output)
    except ModelInputError as exc:
        print(f"cap-kj capital flow: error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
