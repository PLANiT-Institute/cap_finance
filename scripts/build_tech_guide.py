#!/usr/bin/env python3
"""Refresh the generated blocks in docs/TECHNICAL_GUIDE.md.

The guide is prose written by hand — that part is the point of the document and a
generator would only flatten it. What a generator *is* good for is the facts that
go stale silently: row counts, coverage windows, evidence-tier tallies, the
config the results were produced under, and the headline numbers themselves.

So prose lives in the file and the volatile facts live between markers:

    <!-- GEN:name -->   ...replaced on every build...   <!-- /GEN:name -->

    python3 scripts/build_tech_guide.py           # rewrite in place
    python3 scripts/build_tech_guide.py --check   # exit 1 if stale (used by tests)

The --check mode is what stops the guide drifting: a cycle that changes the data
and forgets the guide fails the test suite rather than shipping stale numbers to
an external reader.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "TECHNICAL_GUIDE.md"
sys.path.insert(0, str(ROOT / "src"))

from cap.schemas import SCHEMAS  # noqa: E402

# D-code -> (human name, grain). Order is the order they appear in the guide.
DATASETS = {
    "D1a_facility_static": ("D1a", "Facility register", "one row per production unit"),
    "D1b_facility_panel": ("D1b", "Facility panel", "one row per facility-year"),
    "D2a_scenario_budget": ("D2a", "Scenario carbon budgets", "scenario x region x sector x year"),
    "D2b_scenario_prices": ("D2b", "Scenario price paths", "scenario x region x variable x year"),
    "D3_tech_options": ("D3", "Technology options", "one row per abatement measure"),
    "D4_price_history": ("D4", "Price history", "one row per series-date"),
    "D5_policy_support": ("D5", "Policy support", "one row per instrument-window"),
    "D6_company_financials": ("D6", "Company financials", "one row per company-year"),
    "D7_disclosed_plan": ("D7", "Disclosed plan", "one row per commitment"),
}

COMPANY_NAME = {"POSCO": "POSCO", "NSC": "Nippon Steel",
                "LOTTE": "LOTTE Chemical", "MCI": "Mitsui Chemicals"}

# Categorical fields whose documented value set went stale in F1: the guide named
# `CR` as a unit_type and `operating/idle/closed` as statuses, neither of which
# occurs in the data. Enumerating them by hand is what produced that, so they are
# generated from the prepared files instead.
VOCAB = [
    ("D1a_facility_static", "sector"), ("D1a_facility_static", "unit_type"),
    ("D1a_facility_static", "capacity_unit"), ("D1a_facility_static", "status"),
    ("D2a_scenario_budget", "scenario"), ("D2a_scenario_budget", "region"),
    ("D2b_scenario_prices", "variable"), ("D2b_scenario_prices", "unit"),
    ("D3_tech_options", "applies_to_unit"), ("D3_tech_options", "retrofit"),
    ("D5_policy_support", "support_scenario"), ("D5_policy_support", "instrument"),
    ("D7_disclosed_plan", "item_type"), ("D7_disclosed_plan", "resolution"),
]


def prepared() -> Path:
    from cap import config as C
    return C.data_dir(C.load())


def _md(rows, header):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _span(df, col):
    """Coverage of an integer-year column, as a compact string."""
    if col not in df.columns:
        return "—"
    y = pd.to_numeric(df[col], errors="coerce").dropna().astype(int)
    if y.empty:
        return "—"
    lo, hi = y.min(), y.max()
    return f"{lo}" if lo == hi else f"{lo}–{hi}"


# Substantive state = code, inputs, config, results. Deliberately not HEAD: stamping
# HEAD makes the guide stale the instant it is committed, because the commit that
# writes the stamp becomes a commit the stamp does not name. That is what left the
# gate red at the start of the F window, and it is a property of the stamp, not of
# the cycle that hit it. A prose-only commit now leaves the stamp alone.
STATE_PATHS = ["src", "data", "config.yaml", "out"]


def gen_stamp():
    sha, when = subprocess.run(
        ["git", "log", "-1", "--format=%h %cs", "--", *STATE_PATHS],
        cwd=ROOT, capture_output=True, text=True).stdout.strip().split(maxsplit=1)
    man = ROOT / "out" / "run_manifest.json"
    run = json.loads(man.read_text())["e5"]["finished"] if man.exists() else "no run recorded"
    return (f"> **Repository state.** Last commit to code, inputs or results: `{sha}` ({when}). "
            f"Results in this document come from the pipeline run finished `{run}`. Regenerate the "
            f"generated blocks with `python3 scripts/build_tech_guide.py`.")


def gen_dataset_inventory():
    d = prepared()
    rows = []
    for stem, (code, name, grain) in DATASETS.items():
        p = d / f"{stem}.csv"
        if not p.exists():
            rows.append([f"**{code}**", name, grain, "**missing**", "—", "—"])
            continue
        df = pd.read_csv(p, dtype=str)
        keys = []
        for k, label in [("company_id", "firms"), ("facility_id", "facilities"),
                         ("tech_id", "techs"), ("series_id", "series"),
                         ("variable", "variables"), ("scenario", "scenarios"),
                         ("instrument", "instruments")]:
            # a domain of one is not a domain — reporting "1 techs" for D5's `all`
            # placeholder reads as coverage where there is none
            if k in df.columns and df[k].dropna().nunique() > 1:
                keys.append(f"{df[k].dropna().nunique()} {label}")
        rows.append([f"**{code}**", name, grain, len(df),
                     _span(df, "year") if "year" in df.columns else _span(df, "year_stated"),
                     ", ".join(keys) or "—"])
    families = len({code.rstrip("ab") for code, _, _ in DATASETS.values()})
    note = (f"\n\n{len(SCHEMAS)} files across {families} dataset families, "
            f"{sum(len(v) for v in SCHEMAS.values())} schema-required columns in total. "
            "Extra columns are permitted and preserved; required ones are not optional.")
    return _md(rows, ["ID", "Dataset", "Grain", "Rows", "Years", "Domains"]) + note


def gen_vocab():
    d = prepared()
    rows = []
    for stem, col in VOCAB:
        p = d / f"{stem}.csv"
        if not p.exists():
            continue
        s = pd.read_csv(p, dtype=str)[col].dropna()
        vals = ", ".join(f"`{v}` ({n})" for v, n in s.value_counts().items())
        rows.append([f"`{stem.split('_')[0]}.{col}`", s.nunique(), vals])
    note = ("\n\nThese are the values that **occur**, not the values the schema permits — "
            "`load_input` checks that a column exists and is numeric where required, never what "
            "it contains. Three of these fields are documentation rather than input and no stage "
            "branches on them: `D1a.status`, `D1a.capacity_unit` and `D7.resolution`. Nor is any "
            "`D5` row read — see §3.6. The rest decide behaviour.")
    return _md(rows, ["Field", "Distinct", "Values (count)"]) + note


def gen_price_series():
    d = prepared() / "D4_price_history.csv"
    if not d.exists():
        return "_D4 not available._"
    df = pd.read_csv(d, dtype=str)
    df["date"] = pd.to_datetime(df.date, format="mixed")
    g = (df.groupby("series_id")
           .agg(n=("value", "size"), first=("date", "min"), last=("date", "max"),
                unit=("unit", "first")))
    g = g.sort_values("n", ascending=False)
    rows = [[f"`{i}`", r.n, f"{r.first:%Y-%m}", f"{r.last:%Y-%m}",
             ("**prior**" if r.n < 6 else "estimated"), str(r.unit)[:44]]
            for i, r in g.iterrows()]
    thin = int((g.n < 6).sum())
    note = (f"\n\n**{len(g)} series, {int(g.n.sum())} observations total. "
            f"{thin} of {len(g)} series have fewer than 6 observations** and therefore contribute a "
            "prior rather than an estimate. This is the binding constraint on metric ③.")
    return _md(rows, ["Series", "Obs", "From", "To", "Volatility", "Unit"]) + note


def gen_tier_distribution():
    p = ROOT / "docs" / "parameter_inventory.csv"
    if not p.exists():
        return "_parameter_inventory.csv not available._"
    pi = pd.read_csv(p, dtype=str)
    tiers = ["T1", "T2", "T3", "T4", "T5"]
    ct = pd.crosstab(pi.group, pi.evidence_tier).reindex(columns=tiers, fill_value=0)
    rows = [[f"`{g}`"] + [r[t] for t in tiers] + [int(r.sum())] for g, r in ct.iterrows()]
    total = [f"**{len(pi)} parameters**"] + [int(ct[t].sum()) for t in tiers] + [len(pi)]
    norange = 0
    if "needs_range" in pi.columns:
        flag = pi.needs_range.astype(str).str.lower()
        norange = int(((pi.evidence_tier == "T5") & flag.isin(["1", "true", "yes"])).sum())
    note = (f"\n\nT5 accounts for {ct['T5'].sum()} of {len(pi)} parameters"
            + (f"; {norange} of those are still flagged as lacking a range." if norange
               else "; all carry a range.")
            + f" Models: " + ", ".join(f"{k} {v}" for k, v in pi.model.value_counts().items()) + ".")
    return _md(rows + [total], ["Group"] + tiers + ["Total"]) + note


def gen_config():
    from cap import config as C
    c = C.load()
    rows = [
        ["Horizon", f"{c.years.start}–{c.years.end}", "annual steps"],
        ["Scenarios", ", ".join(c.scenarios), "D2 pathways"],
        ["Support scenarios", ", ".join(c.support_scenarios), "`none` = gross"],
        ["Discount rate", f"{c.discount_rate:.1%} real",
         "sensitivity " + ", ".join(f"{x:.1%}" for x in c.discount_rate_sensitivity)],
        ["Monte Carlo paths", f"{c.simulation['n_sims']:,}",
         f"convergence checked at {c.simulation['convergence_check_n']:,}"],
        ["Flexibility subsample", f"{c.simulation['n_sims_flex']:,}", "metric ⑤ re-optimisation"],
        ["Price process", c.price_process,
         f"alternative: mean reversion, half-life {c.ou_halflife_years} yr"],
        ["Shock normalisation", c.shock_normalisation, "A-24 — see §4.1"],
        ["Frontier grid", f"{c.milp['frontier_points']} points", "ε-constraint sweep"],
        ["MIP relative gap", f"{c.milp['mip_gap_rel']:.0%}", "surrogate objective (A-14)"],
        ["Solver time limit", f"{c.milp['solver_time_limit_s']} s", "feasible solutions accepted"],
        ["Solver threads", str(c.milp["solver_threads"]),
         "**1 is a reproducibility requirement**, not a performance setting"],
        ["Early-retirement cap", f"{c.milp['retire_max_share']:.0%} of production", "A-09"],
        ["Violation price floor", f"{c.milp['budget_violation_floor_thkrw']:,} thousand KRW/tCO₂", "A-11"],
        ["Seed", str(c.seed), "pinned in `config.yaml`"],
    ]
    ramp = " → ".join(f"{y} {s:.0%}" for y, s in sorted(c.carbon_auction_share.items()))
    prem = c.contracts
    extra = (f"\n\n**Auction share ramp (A-07):** {ramp}. Anchored on the confirmed K-ETS Phase 4 "
             f"non-power share; everything after 2030 is an assumption.\n\n"
             f"**Contract premia:** renewable PPA +{prem['ppa_premium_pct']:.0%} over the central "
             f"electricity price, fixed-price EPC +{prem['epc_premium_pct']:.0%} over central CAPEX, "
             f"CCfD fee {prem['ccfd_fee_pct']:.0%} of covered carbon cost.")
    return _md(rows, ["Setting", "Value", "Note"]) + extra


def gen_headline():
    p = ROOT / "out" / "e5" / "metrics_company.csv"
    if not p.exists():
        return "_No pipeline run in `out/`. Run `python -m cap all`._"
    m = pd.read_csv(p)
    v = m[(m.scenario == "NZ15") & (m.support == "none")]
    v = v.sort_values("cost_per_tco2_thkrw")
    rows = [[COMPANY_NAME.get(r.company_id, r.company_id),
             f"{r.cost_per_tco2_thkrw:,.1f}", f"{r.tcar_bnkrw:,.0f}",
             f"{r.capex_total_bnkrw:,.0f}", int(r.capex_peak_year)]
            for r in v.itertuples()]
    head = _md(rows, ["Firm", "② Abatement cost (thousand KRW/tCO₂)", "③ TCaR (bn KRW)",
                      "① Total CAPEX (bn KRW)", "Peak CAPEX year"])
    gap = ROOT / "out" / "e5" / "gap.csv"
    n_gap = 0
    if gap.exists():
        g = pd.read_csv(gap)
        n_gap = g.company_id.nunique()
    bundles = 0
    sc = ROOT / "out" / "scenarios" / "summary.csv"
    if sc.exists():
        bundles = pd.read_csv(sc).bundle.nunique()
    note = (f"\n\nScenario NZ15, `support=none`. Read TCaR to two significant figures (§6.1).\n\n"
            f"A frontier gap is computed for **{n_gap} of {m.company_id.nunique()} firms**; "
            f"§6.4 explains why the other two are not a disclosure failure. "
            f"{bundles} assumption bundles have been evaluated.")
    return head + note


# bundle -> (assumption it varies, English gloss). Bundles absent from this map still
# render, so a bundle added to run_scenarios.py cannot be dropped from the guide silently.
AXIS = {
    "carbon_fast": ("A-07", "full auctioning by 2040 (CBAM-alignment pressure)"),
    "carbon_slow": ("A-07", "auction share reaches only 60% by 2050"),
    "disc35": ("—", "discount rate 3.5%"),
    "disc65": ("—", "discount rate 6.5%"),
    "elec_high": ("—", "grid and PPA electricity prices +30%"),
    "h2_cheap": ("A-05", "hydrogen price −30%"),
    "h2_expensive": ("A-05", "hydrogen price +30%"),
    "penalty_none": ("A-11", "budget-violation floor 300 → 0"),
    "ppa_costly": ("A-15", "renewable PPA premium doubled"),
    "reline_cheap": ("A-13", "BF replacement cost ×0.235, at the disclosed Kobe actual"),
    "retire_free": ("A-09", "early-retirement cap 20% → 40%"),
}


def gen_axis_impact():
    p = ROOT / "out" / "m5" / "bundle_matrix.csv"
    if not p.exists():
        return "_No bundle sweep in `out/m5`. Run `python -m cap m5`._"
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_scenarios import REPLAN_REQUIRED
    b = pd.read_csv(p).sort_values("d_tcar_pct", ascending=False)
    rows = [[f"`{r.bundle}`", AXIS.get(r.bundle, ("—", "—"))[0],
             AXIS.get(r.bundle, ("—", r.bundle))[1],
             ("yes" if r.replanned else
              "**no — required**" if r.bundle in REPLAN_REQUIRED else "not needed"),
             f"{r.d_m2_pct:.1f}%", f"{r.d_tcar_pct:.1f}%"]
            for r in b.itertuples()]
    head = _md(rows, ["Bundle", "Assumption", "What it varies", "Re-planned",
                      "Δ② (max, %)", "Δ③ (max, %)"])
    stale = sorted(set(b[~b.replanned].bundle) & REPLAN_REQUIRED)
    note = (
        f"\n\nLargest mover on ③ is `{b.iloc[0].bundle}` ({b.iloc[0].d_tcar_pct:.1f}%); "
        f"on ② it is `{b.loc[b.d_m2_pct.idxmax()].bundle}` ({b.d_m2_pct.max():.1f}%) — "
        f"not the same bundle, so no single axis dominates both metrics.")
    if stale:
        note += (
            f"\n\n**Read {', '.join('`' + s + '`' for s in stale)} as unmeasured, not as flat.** "
            f"Those axes are read only inside E2, so with the plan menu held fixed they can "
            f"re-price a plan but not change it; their Δ② / Δ③ are an artefact of that. "
            f"Re-planning each costs about ten minutes of solver time and has not been spent.")
    r = ROOT / "out" / "sensitivity" / "ranking.csv"
    if r.exists():
        s = pd.read_csv(r).head(5)
        note += ("\n\nOne-at-a-time parameter screening, top 5 by worst-metric move: "
                 + ", ".join(f"`{t.base_param}` ({t.tier}, {t.score:.0f}%)"
                             for t in s.itertuples()) + ".")
    return head + note


BLOCKS = {
    "stamp": gen_stamp,
    "axis_impact": gen_axis_impact,
    "dataset_inventory": gen_dataset_inventory,
    "vocab": gen_vocab,
    "price_series": gen_price_series,
    "tier_distribution": gen_tier_distribution,
    "config": gen_config,
    "headline": gen_headline,
}


def render(text: str) -> str:
    for name, fn in BLOCKS.items():
        pat = re.compile(rf"(<!-- GEN:{name} -->)(.*?)(<!-- /GEN:{name} -->)", re.S)
        if not pat.search(text):
            raise SystemExit(f"marker <!-- GEN:{name} --> missing from {GUIDE.name}")
        body = fn()
        text = pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text, count=1)
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the guide's generated blocks are stale")
    args = ap.parse_args()

    old = GUIDE.read_text(encoding="utf-8")
    new = render(old)
    if args.check:
        if old == new:
            print(f"{GUIDE.relative_to(ROOT)}: generated blocks current")
            return 0
        print(f"{GUIDE.relative_to(ROOT)}: STALE — run `python3 scripts/build_tech_guide.py`")
        return 1
    GUIDE.write_text(new, encoding="utf-8")
    print(f"-> {GUIDE.relative_to(ROOT)} ({len(BLOCKS)} blocks, {len(new):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
