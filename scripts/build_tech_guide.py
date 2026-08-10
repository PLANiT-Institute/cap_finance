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
from cap.calibration import FALLBACK_VOL  # noqa: E402

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
            "it contains. Three of these fields are documentation to every *modelling* stage — "
            "no stage branches on `D1a.status`, `D1a.capacity_unit` or `D7.resolution`. `status` "
            "carries one exception that sits upstream of this table: `prepare_raw.py` drops a row "
            "whose status contains `폐쇄예정` before writing the prepared file, which is why no "
            "such value appears above (§3.1). `D5.instrument` is the near-miss: only the one "
            "`auction_share` row is read, and by `plancost.auction_share` rather than by the "
            "support axis — the other six rows are read by nothing (§3.6). The rest "
            "decide behaviour.")
    return _md(rows, ["Field", "Distinct", "Values (count)"]) + note


def gen_register_filter():
    """Which raw facility rows never reach the model, and on what test.

    Deliberately a *diff* of raw against prepared, not a re-implementation of
    `prepare_raw.py`'s exclusion logic: a copy of that logic here would agree with
    the guide and disagree with the pipeline the moment either moved. The reason
    column is attributed, not recomputed.
    """
    raw = ROOT / "data" / "raw" / "facility_static.csv"
    prep = prepared() / "D1a_facility_static.csv"
    if not (raw.exists() and prep.exists()):
        return "_D1a not available._"
    r = pd.read_csv(raw, dtype=str)
    keep = set(pd.read_csv(prep, dtype=str).facility_id)
    rows = []
    for t in r.itertuples():
        if t.facility_id in keep:
            continue
        status = str(t.status or "")
        year = pd.to_numeric(pd.Series([t.commissioning_year]), errors="coerce").iloc[0]
        has_vol = bool(re.search(r"[\d,]+\s*m³", str(t.unit_name or "")))
        cap = pd.to_numeric(pd.Series([t.capacity]), errors="coerce").iloc[0]
        if "폐쇄예정" in status:
            why = "`status` contains the literal `폐쇄예정`"
        elif pd.notna(year) and year > 2026:
            why = f"`commissioning_year` {int(year)} > 2026 (not yet operating)"
        elif pd.isna(cap) and not has_vol:
            why = "no `capacity`, and `unit_name` carries no `m³` token to estimate one from"
        else:
            why = "dropped — reason not reproducible from the raw row"
        rows.append([f"`{t.facility_id}`", t.site, t.unit_type, status or "—", why])
    note = (f"\n\n{len(r)} rows collected, {len(keep)} reach the model. The three tests are "
            "applied in `scripts/prepare_raw.py:54-62`, before the prepared file is written, "
            "so an excluded unit is invisible to every later stage and to the schema check. "
            "Two of them are worth stating plainly: the closure test is a **substring match on "
            "one Korean string**, so the units whose status says `휴지예정` or `가동중단 계획` "
            "stay in the model; and a capacity that has to be estimated is estimated from a "
            "`m³` figure parsed out of the unit's *name*, so an operating furnace whose name "
            "happens not to carry that token is excluded by a text format, not by a decision.")
    if not rows:
        return "_No raw facility row is excluded._" + note
    return _md(rows, ["Facility", "Site", "Unit", "Raw `status`", "Excluded because"]) + note


def gen_d1b_intensity():
    """The incumbent coefficients E2 actually builds, and where they vary."""
    d = prepared()
    p, q = d / "D1b_facility_panel.csv", d / "D1a_facility_static.csv"
    if not (p.exists() and q.exists()):
        return "_D1b not available._"
    d1b = pd.read_csv(p)
    d1a = pd.read_csv(q)
    recent = d1b[d1b.year >= d1b.year.max() - 2].groupby("facility_id").mean(numeric_only=True)
    f = d1a.set_index("facility_id").join(recent)
    f["ef_inc"] = f.emissions_s1 / f.production
    f["coal_gj_t"] = f.energy_coal / f.production
    f["gas_gj_t"] = f.energy_gas / f.production
    f["elec_mwh_t"] = f.energy_elec / f.production
    rows = []
    for ut, g in f.groupby("unit_type"):
        def rng(col, dp=2):
            lo, hi = g[col].min(), g[col].max()
            return f"{lo:.{dp}f}" if abs(hi - lo) < 10 ** -dp else f"{lo:.{dp}f}–{hi:.{dp}f}"
        rows.append([f"`{ut}`", len(g), f"{g.production.sum() / 1e6:.2f}",
                     rng("ef_inc"), rng("coal_gj_t", 1), rng("gas_gj_t", 1), rng("elec_mwh_t")])
    note = (f"\n\nColumns 4–7 are the coefficients `_prep_company` builds "
            f"(`src/cap/e2_milp.py:49-55`) over the {len(f)} facilities carrying "
            f"{f.production.sum() / 1e6:.1f} Mt/yr of incumbent output. A single value in a range "
            "column means every facility of that unit type carries the identical number: the "
            "three energy columns are **not observations**. They were absent from the collected "
            "panel and are written as `production × ROUTE[unit_type]` in "
            "`scripts/prepare_raw.py:100-107,190,211`, so `energy_x / production` returns the "
            "route constant by construction and no facility-level energy information exists in "
            "the model. `ef_inc` is the one incumbent coefficient that varies within a unit "
            "type, and only for steel — petrochemical Scope 1 is itself `production × "
            "ROUTE[NCC][0]`, which is why the injected 0.95 tCO₂/t *is* the petrochemical "
            "level rather than an input to it (**A-03**).")
    return _md(rows, ["Unit type", "Facilities", "Q (Mt/yr)", "`ef_inc` tCO₂/t",
                      "coal GJ/t", "gas GJ/t", "elec MWh/t"]) + note


def gen_d2_provenance():
    """Which scenario rows carry an external anchor and which are our own line.

    §3.3 said only the interpolated rows are labelled `EST_*`, which reads as if
    anchors were the common case. They are not, and the split is not uniform
    across variables — one price path has no anchored row at all. Resolution uses
    `audit_data.source_parts` rather than a second copy of the splitting rule.
    """
    d = prepared()
    reg = ROOT / "data" / "raw" / "source_register.csv"
    if not reg.exists():
        return "_source_register.csv not available._"
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_data import source_parts
    known = set(pd.read_csv(reg, dtype=str, encoding="utf-8-sig").source_id.str.strip())

    def split(df):
        anchored, est = [], []
        for sid in df.source_id.fillna(""):
            ps = source_parts(sid)
            (est if any(p.startswith(("EST_", "PENDING_", "PREP_")) for p in ps)
             else anchored).append(sid)
        return anchored, est

    rows = []
    a = pd.read_csv(d / "D2a_scenario_budget.csv")
    for reg_name, g in a.groupby("region"):
        anc, est = split(g)
        rows.append([f"**D2a** budgets", f"`{reg_name}`", len(g), len(anc),
                     ", ".join(sorted({s for s in anc})) or "**none**"])
    b = pd.read_csv(d / "D2b_scenario_prices.csv")
    for (reg_name, var), g in b.groupby(["region", "variable"]):
        anc, est = split(g)
        rows.append([f"D2b `{var}`", f"`{reg_name}`", len(g), len(anc),
                     ", ".join(sorted({s.split(" (")[0] for s in anc})) or "**none**"])
    # scenario differentiation: does NZ15 differ from B20 anywhere in the path?
    p = b.pivot_table(index=["region", "variable", "year"], columns="scenario", values="value")
    same = (p.NZ15 == p.B20).groupby(level=["region", "variable"]).all()
    flat = [f"{r} `{v}`" for (r, v), ok in same.items() if ok]
    note = (f"\n\n{len(split(a)[1])} of {len(a)} budget rows and "
            f"{len(split(b)[1])} of {len(b)} price rows are "
            "our own construction (`EST_D2A_V0` / `EST_D2B_V0`); the rest carry a register key. "
            "Rows with a key are the anchors the line is drawn between, so a variable showing "
            "**none** was drawn without one.")
    if flat:
        note += ("\n\nIdentical under both scenarios in every year: "
                 + ", ".join(flat) + ". `re_price` is flat by construction (**A-05**), but a "
                 "differentiated variable that does not differentiate is an input the scenario "
                 "cannot reach — electrification economics in that region see the same power "
                 "price at 1.5 °C and at 2 °C.")
    return _md(rows, ["Series", "Region", "Rows", "Anchored", "Anchor source"]) + note


def gen_d3_reach():
    """Which technologies any facility can actually take.

    E2 matches on `applies_to_unit == unit_type` exactly (`e2_milp.py:148`), so a
    measure whose target unit type is absent from the register — or is the literal
    `NONE` — is priced in D3 and never offered. Generated because both sides of
    the match are data.
    """
    d = prepared()
    t = pd.read_csv(d / "D3_tech_options.csv")
    f = pd.read_csv(d / "D1a_facility_static.csv")
    units = sorted(set(t.applies_to_unit) | set(f.unit_type))
    rows = []
    for u in units:
        techs = sorted(t[t.applies_to_unit == u].tech_id)
        n_fac = int((f.unit_type == u).sum())
        rows.append([f"`{u}`", n_fac, f"{f[f.unit_type == u].capacity.sum() / 1e6:.1f}",
                     len(techs),
                     ", ".join(f"`{x}`" for x in techs) if techs else "**none**"])
    orphan_tech = sorted(t[~t.applies_to_unit.isin(f.unit_type)].tech_id)
    orphan_fac = sorted(f[~f.unit_type.isin(t.applies_to_unit)].facility_id)
    note = (f"\n\nThe two ends of this table are the ones to read. Measures targeting a unit type "
            f"no facility has, and so never adoptable: {len(orphan_tech)} of {len(t)} "
            f"({', '.join('`' + x + '`' for x in orphan_tech)}). Facilities offered no measure at "
            f"all, able only to run on or retire: {len(orphan_fac)} of {len(f)} "
            f"({', '.join('`' + x + '`' for x in orphan_fac)}). "
            "Both follow from the same exact-string match and neither is an error the schema "
            "or the audit can see — every row is present, typed and sourced.")
    return _md(rows, ["Unit type", "Facilities", "Capacity (Mt/yr)", "Measures", "Which"]) + note


def gen_d3b_bands():
    """Every evidence band, and where the central value sits in it."""
    d = prepared()
    t = pd.read_csv(d / "D3_tech_options.csv").set_index("tech_id")
    b = pd.read_csv(d / "D3b_tech_bands.csv")
    rows, outside = [], []
    for r in b.itertuples():
        v = float(t.loc[r.tech_id, r.field])
        pos = ("**below band**" if v < r.value_low else "**above band**" if v > r.value_high
               else "at lower bound" if v == r.value_low
               else "at upper bound" if v == r.value_high else "interior")
        if "band" in pos:
            outside.append(f"`{r.tech_id}.{r.field}`")
        rows.append([f"`{r.tech_id}`", f"`{r.field}`", f"{v:g}",
                     f"{r.value_low:g} – {r.value_high:g}", pos, r.evidence_tier])
    banded = b.groupby("tech_id").size()
    note = (f"\n\n**{len(b)} bands over {len(banded)} of {len(t)} technologies and "
            f"{b.field.nunique()} of {t.select_dtypes('number').shape[1]} numeric fields** — "
            "this is a spot check "
            "on two steel CAPEX values, not a band layer over the option set. Every other "
            "central value in D3 is a point with a source and no stated range, which is why "
            "CAPEX dispersion enters the model through `capex_uncertainty` (**A-22**) instead. "
            "No central value sits strictly inside its band: two sit on a bound and "
            f"{len(outside)} sits outside ({', '.join(outside)}). That is deliberate and tested — "
            "`steel_eaf` at 240 is POSCO's Gwangyang project on a reused site, below a "
            "literature band built from greenfield builds "
            "(`data/manifests/estimation_notes_D2_v0.md`), and it is the evidence that the "
            "central values were not quietly snapped to the literature.")
    return _md(rows, ["Tech", "Field", "Central", "Band", "Position", "Tier"]) + note


def gen_price_series():
    """D4 series against the factors that actually read them.

    The obs count alone said "estimated" for any series with 6+ observations,
    which reads as though eleven series were estimating something. Only the
    series named in `calibration.FACTOR_SERIES` are ever opened, so the factor
    map is imported rather than restated — if a factor's series list changes,
    this table changes with it.
    """
    d = prepared() / "D4_price_history.csv"
    if not d.exists():
        return "_D4 not available._"
    from cap.calibration import FACTOR_SERIES, FALLBACK_VOL
    reads = {s: f for f, ss in FACTOR_SERIES.items() for s in ss}
    reads["electrolyzer_capex"] = "ez"          # read directly by `calibrate`, not via a factor
    df = pd.read_csv(d, dtype=str)
    df["date"] = pd.to_datetime(df.date, format="mixed")
    df["value"] = pd.to_numeric(df.value, errors="coerce")
    g = (df.groupby("series_id")
           .agg(n=("value", "size"), first=("date", "min"), last=("date", "max"),
                unit=("unit", "first")))
    g = g.sort_values("n", ascending=False)
    rows = [[f"`{i}`", r.n, f"{r.first:%Y-%m}", f"{r.last:%Y-%m}",
             (f"`{reads[i]}`" if i in reads else "—"), str(r.unit)[:44]]
            for i, r in g.iterrows()]
    used = [s for s in reads if s in g.index and g.loc[s, "n"] >= 6]
    unread = len(g) - len([s for s in reads if s in g.index])
    missing = [s for s in reads if s not in g.index]
    prior = [f"`{f}` ({FALLBACK_VOL[f]})" for f, ss in FACTOR_SERIES.items()
             if not any(s in g.index and g.loc[s, "n"] >= 6 for s in ss)]
    ez = df[df.series_id == "electrolyzer_capex"].sort_values("date")
    note = (f"\n\n**{len(g)} series, {int(g.n.sum())} observations. "
            f"{unread} of them are read by nothing** — they are level references and "
            "provenance for the price paths in D2b, not inputs to the volatility "
            f"calibration. Of the {len(reads)} series the calibration names, "
            f"{len(used)} clear the 6-observation floor ({', '.join('`' + s + '`' for s in used)})"
            + (f", and {', '.join('`' + s + '`' for s in missing)} "
               f"{'is' if len(missing) == 1 else 'are'} named but absent from D4" if missing else "")
            + f". So {len(prior)} of the {len(FACTOR_SERIES)} factors take a prior instead of an "
              f"estimate: {', '.join(prior)}. The factor correlation matrix is the identity for the "
              "same reason — with two factors producing no return series there is nothing to "
              "correlate, so identity is the absence of an estimate, not a finding of independence.")
    if len(ez) >= 2:
        a, b = ez.iloc[0], ez.iloc[-1]
        note += (f" The electrolyzer capex path is anchored on the last of {len(ez)} observations "
                 f"({b.value:,.0f} KRW/kW @{b.date:%Y}) with its decline rate and volatility taken "
                 f"from priors (5%/yr, 0.10); note the two observations *rise* "
                 f"{100 * (b.value / a.value - 1):.0f}% while the imposed path falls.")
    return _md(rows, ["Series", "Obs", "From", "To", "Read as", "Unit"]) + note


def gen_d6_coverage():
    """Which D6 columns are actually populated, and which are read.

    The prose listed seven financial columns as though the table were a filled
    rectangle. Only `ebitda` is complete, and the two firms with no leverage rows
    are exactly the two whose leverage ratios come out blank downstream.
    """
    d = prepared() / "D6_company_financials.csv"
    if not d.exists():
        return "_D6 not available._"
    df = pd.read_csv(d)
    # consumers verified against src/cap/e5_metrics.py:104-112 — everything else in
    # the table is collected context that no stage opens
    READ = {"revenue": "⑥ `capex_total_to_revenue_pct` (latest year)",
            "ebitda": "⑥ reference earnings (mean of last 3 reported)",
            "net_debt": "⑥ `netdebt_to_ebitda_now/post` (latest year)"}
    cols = [c for c in df.columns if c not in ("company_id", "year", "source_id")]
    rows = []
    for c in cols:
        firms = sorted(df.company_id[df[c].notna()].unique())
        rows.append([f"`{c}`", f"{int(df[c].notna().sum())} / {len(df)}",
                     ", ".join(firms) if len(firms) < df.company_id.nunique() else "all four",
                     READ.get(c, "—")])
    af = ROOT / "out" / "e5" / "affordability.csv"
    span = ""
    if af.exists():
        a = pd.read_csv(af).drop_duplicates("company_id")
        span = (" Reference earnings are the last three *reported* years, which differ by firm: "
                + "; ".join(f"{COMPANY_NAME.get(r.company_id, r.company_id)} "
                            f"{str(r.ebitda_years).replace(';', '–')}"
                            for r in a.itertuples()) + ".")
    unread = [c for c in cols if c not in READ]
    note = (f"\n\n{len(df)} company-years. **{len(unread)} of the {len(cols)} financial columns are "
            f"read by no stage** (`{'`, `'.join(unread)}`) — they were collected, they pass the "
            "schema check, and metric ⑥ never opens them. Of the three that are read, `net_debt` "
            "exists only for the two Japanese firms, so the net-debt multiple — the leverage half "
            "of ⑥ — is blank for POSCO and LOTTE by entity boundary, not by oversight." + span)
    return _md(rows, ["Column", "Non-null", "Firms", "Read by"]) + note


def gen_package():
    """What the public package contains, against what the model reads.

    The two are not the same set and the difference is not a subset relation:
    two input files are replaced by firm-level aggregates and five files are added.
    Reading the file listing off `manifest.json` and the column counts off the
    generated dictionary means this table cannot claim a file the build did not write.
    """
    pkg = ROOT / "data" / "package"
    man, dic = pkg / "manifest.json", pkg / "data_dictionary.csv"
    if not (man.exists() and dic.exists()):
        return "_Package not built — run `scripts/build_data_package.py`._"
    files = {f["name"]: f for f in json.loads(man.read_text(encoding="utf-8"))["files"]}
    d = pd.read_csv(dic)
    KIND = {"D1a_company_capacity": "aggregate of D1a", "D1b_company_panel": "aggregate of D1b"}
    rows = []
    for stem, g in d.groupby("file", sort=False):
        name = f"{stem}.csv"
        kind = KIND.get(stem, "results" if stem.startswith("result_")
                        else "register" if stem == "source_register" else "input, as loaded")
        secs = sorted(set(g.defined_in.str.split("§").str[-1]))
        rows.append([f"`{name}`", kind, f"{files[name]['rows']:,}", str(len(g)),
                     "§" + ", §".join(secs)])
    shipped = sorted(files)
    inputs = [s for s in SCHEMAS if not any(f.startswith(s) for f in shipped)]
    note = (f"\n\n{len(rows)} data files, {len(d)} columns, every one of them defined in §3 — the "
            f"build refuses to write the dictionary otherwise. **{len(inputs)} of the "
            f"{len(SCHEMAS)} input files ship under a different name and a different grain** "
            f"(`{'`, `'.join(inputs)}` → the two aggregates above), so the package is not the "
            f"input set with rows removed. `data_dictionary.csv` ships alongside these and holds "
            f"one row per column above, {len(d)} in total.")
    return _md(rows, ["Package file", "Kind", "Rows", "Columns", "Defined in"]) + note


def gen_d7_enforcement():
    """Row-by-row verdict on the disclosed plan, obtained by *calling* the engine's
    `_disclosed_fixed` rather than restating its precondition chain in prose. A
    re-implementation here would drift from `e2_milp.py` the moment either moved,
    and the interesting cases are precisely the ones that leave no trace.
    """
    import numpy as np
    from cap import config as C
    from cap.schemas import load_input
    from cap.e2_milp import COMPANY_REGION, _disclosed_fixed, _prep_company
    cfg = C.load()
    ddir = C.data_dir(cfg)
    av_path = ROOT / "out" / "e1" / "tech_availability.csv"
    if not (ddir / "D7_disclosed_plan.csv").exists() or not av_path.exists():
        return "_D7 or E1 availability not available._"
    d7 = load_input(ddir, "D7_disclosed_plan")
    fac, d3, _ = _prep_company(cfg, ddir)
    avail = pd.read_csv(av_path)
    years = np.arange(cfg.years.start, cfg.years.end + 1)

    verdicts, levers = {}, {}
    for company in sorted(fac.company_id.unique()):
        cf = fac[fac.company_id == company]
        for scen in cfg.scenarios:
            av = (avail[(avail.scenario == scen) & (avail.region == COMPANY_REGION[company])]
                  .set_index("tech_id").avail_year_scenario)
            f = _disclosed_fixed(d7, cf, d3[d3.sector == cf.sector.iloc[0]], years, av)
            forced = {(fid, tk): ta for (fid, tk, ta) in f["x"]}
            levers[company] = (f["ppa"], f["epc"], f["ccfd"])
            for r in d7[d7.company_id == company].itertuples():
                if r.item_type != "tech_commit":
                    v = f"context only (`{r.item_type}`)"
                elif (r.facility_id, r.tech_id) in forced:
                    ta = forced[(r.facility_id, r.tech_id)]
                    build = int(d3.set_index("tech_id").build_years.get(r.tech_id, 0))
                    clamp = ta - (int(r.year_stated) - build)
                    v = (f"**forced**, adopt {ta} (operational {ta + build})"
                         + (f", clamped +{clamp}y by availability" if clamp else ""))
                elif any(str(x).startswith(f"{r.facility_id}/{r.tech_id}:") for x in f["dropped"]):
                    v = "dropped, **reason recorded**"
                elif pd.isna(r.facility_id):
                    v = "dropped **silently** — no `facility_id` in the disclosure"
                elif r.facility_id not in cf.index:
                    v = "dropped **silently** — `facility_id` not in D1a"
                else:
                    v = "dropped **silently**"
                verdicts.setdefault((company, r.Index), set()).add(v)
    rows = []
    for r in d7.itertuples():
        vs = verdicts.get((r.company_id, r.Index), {"—"})
        rows.append([COMPANY_NAME.get(r.company_id, r.company_id),
                     f"`{r.item_type}`",
                     f"`{r.facility_id}`" if pd.notna(r.facility_id) else "—",
                     f"`{r.tech_id}`" if pd.notna(r.tech_id) else "—",
                     "" if pd.isna(r.year_stated) else int(r.year_stated),
                     f"`{r.resolution}`",
                     " / ".join(sorted(vs))])
    n_forced = sum("forced" in v for vs in verdicts.values() for v in vs)
    n_silent = sum("silently" in v for vs in verdicts.values() for v in vs)
    n_rec = sum("recorded" in v for vs in verdicts.values() for v in vs)
    note = (f"\n\nOf the {len(d7)} rows, **{n_forced} become a forced decision**, "
            f"{n_rec} are dropped with a reason written to `out/e2/disclosed_skipped.csv`, and "
            f"**{n_silent} are dropped without a trace** — the skip file has no line for them, so a "
            "reader counting that file undercounts what the disclosed coordinate is missing. "
            "`resolution` appears in none of it: the two `high` rows that are dropped silently are "
            "dropped for the same reason a `mid` row would be. Verdicts are identical across "
            "both scenarios."
            if len({v for vs in verdicts.values() for v in vs}) else "")
    if levers and all(l == (0.0, 0, 0) for l in levers.values()):
        note += (" The same call also fixes the three contract levers: because D7 contains no "
                 "`ppa`, `epc` or `ccfd` rows, every disclosed coordinate is solved with "
                 "`ppa = 0, epc = 0, ccfd = 0` while the optimum may buy all three. Part of every "
                 "frontier gap is therefore a hedging difference no firm ever disclosed either "
                 "way (§6.4).")
    return _md(rows, ["Company", "Type", "Facility", "Tech", "Year", "Res.", "What the engine does"]) + note


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


def _e4_base_plans():
    """E4 authoritative results joined to E2's surrogate ordering, one row per base plan.

    `support=none` only: the axis duplicates every row (§3.6). Returns None if the
    pipeline has not been run.
    """
    s = ROOT / "out" / "e4" / "summary.csv"
    pi = ROOT / "out" / "e2" / "plan_index.csv"
    if not (s.exists() and pi.exists()):
        return None
    d = pd.read_csv(s).query("support == 'none'")
    return d.merge(pd.read_csv(pi)[["plan_id", "risk_proxy"]], on="plan_id")


def _rho(a, b):
    """Rank correlation without scipy — rank, then Pearson (ties get the mean rank)."""
    return float(a.rank().corr(b.rank()))


def gen_surrogate():
    """How badly E2's linear surrogate orders plans against E4's authoritative result.

    F9 found this stated as a hand-written sector range that was wrong by an order
    of magnitude on the steel side ("−0.05 to 0.00"; NSC is −0.564), and stated
    without saying it covered one scenario. Both failures come from writing a range
    by hand, so the per-bundle numbers are generated instead.
    """
    d = _e4_base_plans()
    if d is None:
        return "_No pipeline run in `out/`. Run `python -m cap all`._"
    rows, match = [], 0
    for (co, sc), g in d.groupby(["company_id", "scenario"]):
        cheapest = g.loc[g.e2_surrogate_cost.idxmin(), "plan_id"] == g.loc[g.p50.idxmin(), "plan_id"]
        match += int(cheapest)
        rows.append([COMPANY_NAME.get(co, co), sc, len(g),
                     f"{_rho(g.e2_surrogate_cost, g.p50):+.2f}",
                     f"{_rho(g.risk_proxy, g.tcar):+.2f}",
                     "yes" if cheapest else "**no**"])
    rows.sort(key=lambda r: (r[0], r[1]))
    head = _md(rows, ["Firm", "Scenario", "Plans", "ρ(surrogate cost, P50)",
                      "ρ(risk proxy, TCaR)", "Surrogate's cheapest = authoritative cheapest"])
    n = len(rows)
    return head + (
        f"\n\nThe surrogate's cheapest plan is the authoritative cheapest in **{match} of {n}** "
        f"(firm × scenario) bundles. Rank correlation runs from "
        f"{min(float(r[3]) for r in rows):+.2f} to {max(float(r[3]) for r in rows):+.2f} on cost — "
        f"it is not a sector split, and the worst cell is a steel one.")


def gen_plan_distinct():
    """Enumerated plans vs. plans that are actually different once E4 prices them."""
    d = _e4_base_plans()
    if d is None:
        return "_No pipeline run in `out/`. Run `python -m cap all`._"
    grp = d.groupby(["company_id", "scenario"])
    distinct = int(grp.central_cost.apply(lambda x: x.round(6).nunique()).sum())
    collapsed = sum(len(g) - g.central_cost.round(6).nunique() == 1 for _, g in grp)
    how_many = ("Every one of the" if collapsed == grp.ngroups else f"{collapsed} of the")
    return (f"Separately, of {len(d)} enumerated plans only **{distinct}** are distinct under "
            f"authoritative evaluation. {how_many} {grp.ngroups} bundles collapses "
            f"exactly one pair, which differs only in whether a CCfD is signed — under "
            f"`support=none` the CCfD strike is undefined, so the two plans are numerically "
            f"identical downstream while the surrogate charges a premium and prices them apart.")


def gen_frontier_shape():
    """How wide the frontier is that every gap number is a distance to.

    §6.3 says the frontier is thin in aggregate ("4 of 32 forced schedules survive").
    That is a statement about the technology sweep, not about the object the gap is
    measured against — which is the per-bundle non-dominated set, and is smaller
    still. A reviewer asking "distance to what, exactly?" gets no answer from the
    guide's prose, so the answer is generated here from the same file §6.4 quotes.
    """
    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if not fp.exists():
        return "_No pipeline run in `out/`. Run `python -m cap all`._"
    f = pd.read_csv(fp)
    f = f[f.support == "none"]          # the support axis duplicates every row (§3.6)
    gap = ROOT / "out" / "e5" / "gap.csv"
    g = pd.read_csv(gap) if gap.exists() else pd.DataFrame(columns=["company_id", "scenario"])
    g = g[g.support == "none"] if "support" in g.columns else g
    rows = []
    for (co, sc), d in f.groupby(["company_id", "scenario"]):
        hit = g[(g.company_id == co) & (g.scenario == sc)]
        rows.append([COMPANY_NAME.get(co, co), sc, len(d), int(d.on_frontier.sum()),
                     f"{hit.iloc[0].gap_cost_bnkrw:,.0f} / {hit.iloc[0].gap_risk_bnkrw:,.0f}"
                     if len(hit) else "**no coordinate**"])
    rows.sort(key=lambda r: (r[0], r[1]))
    head = _md(rows, ["Firm", "Scenario", "Candidate plans", "On frontier",
                      "Gap cost / risk (bn KRW)"])
    lo, hi = min(r[3] for r in rows), max(r[3] for r in rows)
    thin = [r for r in rows if r[4] != "**no coordinate**"]
    worst = min(thin, key=lambda r: r[3]) if thin else None
    note = (f"\n\nThe efficient frontier is **{lo} to {hi} plans** per firm × scenario, out of "
            f"{min(r[2] for r in rows)}–{max(r[2] for r in rows)} candidates. A frontier gap is a "
            f"distance to that set, so it is a distance to a handful of points, not to a curve.")
    if worst:
        note += (f" The thinnest case that carries a gap is {worst[0]} under {worst[1]}: "
                 f"**{worst[3]} non-dominated plans**, and the reported "
                 f"{worst[4]} bn KRW is the distance to them.")
    vd = ROOT / "out" / "e5" / "variance_decomp.csv"
    if vd.exists():
        v = pd.read_csv(vd)
        v = v[v.factor == "h2"].groupby("company_id").variance_share.mean()
        note += (f"\n\nAnd the axis that gap is measured on is the one with no market evidence: "
                 f"hydrogen carries {v.min():.0%}–{v.max():.0%} of cost variance across the four "
                 f"firms, while its volatility is the prior of {FALLBACK_VOL['h2']:.2f}, "
                 f"not an estimate "
                 f"(§3.5). Tail-risk *levels*, and therefore `gap_risk` levels, inherit that.")
    return head + note


FIGURE = ROOT / "docs" / "figures" / "frontier_gap.svg"

# Panel geometry, in the figure's own user units. Four firms across, two scenarios down.
PW, PH, COLS = 250, 272, 4
PAD_L, PAD_R, PAD_T, PAD_B = 52, 16, 40, 44

SVG_STYLE = """
  .bg{fill:none}
  .ttl{font:600 12px system-ui,sans-serif;fill:#191C24}
  .sub{font:11px system-ui,sans-serif;fill:#8B909C}
  .tick{font:9.5px system-ui,sans-serif;fill:#8B909C}
  .ax{fill:none;stroke:#C9CAC4;stroke-width:1}
  .cand{fill:#8B909C;opacity:.5}
  .fr{fill:none;stroke:#2a78d6;stroke-width:1.6}
  .frp{fill:#2a78d6}
  .disc{fill:#e34948}
  .gap{stroke:#e34948;stroke-width:1.2;stroke-dasharray:3 3}
  .gapend{fill:none;stroke:#e34948;stroke-width:1.2}
  .glab{font:9.5px system-ui,sans-serif;fill:#e34948}
  @media (prefers-color-scheme:dark){
    .ttl{fill:#EDEEF0} .ax{stroke:#3A3F49}
    .fr{stroke:#3987e5} .frp{fill:#3987e5}
    .disc{fill:#e66767} .gap,.gapend{stroke:#e66767} .glab{fill:#e66767}}
"""


def _x(v):
    """A ratio, read as a multiple — 1.01x must not print as the 1x that hides it."""
    return f"{v:,.0f}×" if v >= 10 else f"{v:.2f}×"


def _panel(x0, y0, d, gaprow, title):
    """One (P50, TCaR) panel: candidates, frontier, disclosed coordinate, both gap legs."""
    lo_x, hi_x = d.p50.min(), d.p50.max()
    lo_y, hi_y = d.tcar.min(), d.tcar.max()
    px, py = (hi_x - lo_x) * .10 or 1.0, (hi_y - lo_y) * .10 or 1.0
    lo_x, hi_x, lo_y, hi_y = lo_x - px, hi_x + px, lo_y - py, hi_y + py
    w, h = PW - PAD_L - PAD_R, PH - PAD_T - PAD_B

    def X(v):
        return x0 + PAD_L + (v - lo_x) / (hi_x - lo_x) * w

    def Y(v):
        return y0 + PAD_T + h - (v - lo_y) / (hi_y - lo_y) * h

    s = [f'<text class="ttl" x="{x0 + PAD_L}" y="{y0 + 16}">{title}</text>',
         f'<path class="ax" d="M{x0 + PAD_L} {y0 + PAD_T} V{y0 + PAD_T + h} '
         f'H{x0 + PAD_L + w}"/>']
    for v, lab in ((lo_y, f"{lo_y:,.0f}"), (hi_y, f"{hi_y:,.0f}")):
        s.append(f'<text class="tick" x="{x0 + PAD_L - 5}" y="{Y(v) + 3}" '
                 f'text-anchor="end">{lab}</text>')
    for v, anc in ((lo_x, "start"), (hi_x, "end")):
        s.append(f'<text class="tick" x="{X(v)}" y="{y0 + PAD_T + h + 14}" '
                 f'text-anchor="{anc}">{v:,.0f}</text>')
    s.append(f'<text class="sub" x="{x0 + PAD_L}" y="{y0 + PAD_T + h + 30}">P50 →</text>')

    for r in d[~d.on_frontier & ~d.is_disclosed].itertuples():
        s.append(f'<circle class="cand" cx="{X(r.p50):.1f}" cy="{Y(r.tcar):.1f}" r="2.8"/>')
    fr = d[d.on_frontier].sort_values("tcar")
    s.append('<polyline class="fr" points="'
             + " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in zip(fr.p50, fr.tcar)) + '"/>')
    for a, b in zip(fr.p50, fr.tcar):
        s.append(f'<circle class="frp" cx="{X(a):.1f}" cy="{Y(b):.1f}" r="3.2"/>')

    disc = d[d.is_disclosed]
    if disc.empty:
        s.append(f'<text class="sub" x="{x0 + PAD_L + w / 2}" y="{y0 + PAD_T + 14}" '
                 f'text-anchor="middle">no disclosed coordinate (§6.4)</text>')
        return "\n".join(s)
    p = disc.iloc[0]
    dx, dy = X(p.p50), Y(p.tcar)
    if gaprow is not None:
        tx, ty = X(p.p50 - gaprow.gap_cost_bnkrw), Y(p.tcar - gaprow.gap_risk_bnkrw)
        s += [f'<line class="gap" x1="{dx:.1f}" y1="{dy:.1f}" x2="{tx:.1f}" y2="{dy:.1f}"/>',
              f'<circle class="gapend" cx="{tx:.1f}" cy="{dy:.1f}" r="3"/>',
              f'<line class="gap" x1="{dx:.1f}" y1="{dy:.1f}" x2="{dx:.1f}" y2="{ty:.1f}"/>',
              f'<circle class="gapend" cx="{dx:.1f}" cy="{ty:.1f}" r="3"/>',
              f'<text class="glab" x="{(dx + tx) / 2:.1f}" y="{dy - 6:.1f}" '
              f'text-anchor="middle">{gaprow.gap_cost_bnkrw:,.0f}</text>',
              f'<text class="glab" x="{dx + 5:.1f}" y="{(dy + ty) / 2:.1f}">'
              f'{gaprow.gap_risk_bnkrw:,.0f}</text>']
    s.append(f'<rect class="disc" x="{dx - 3.6:.1f}" y="{dy - 3.6:.1f}" width="7.2" '
             f'height="7.2" transform="rotate(45 {dx:.1f} {dy:.1f})"/>')
    return "\n".join(s)


def gen_gap_figure():
    """The figure Arc asked for: frontier, disclosed coordinate, gap, in one screen.

    Drawing it is also a check on the prose. `_gap` in `src/cap/e5_metrics.py` measures
    two axis-aligned distances and clamps to the frontier's endpoint when the disclosed
    point sits outside the frontier's span on the axis being measured — so the leg does
    not end on the frontier at all in that case, which no amount of prose had made
    visible. The caption counts the clamped legs rather than asserting anything.
    """
    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if not fp.exists():
        return "_No pipeline run in `out/`. Run `python -m cap all`._"
    f = pd.read_csv(fp)
    f = f[f.support == "none"]          # the support axis duplicates every row (§3.6)
    g_all = pd.read_csv(ROOT / "out" / "e5" / "gap.csv")
    g = g_all[g_all.support == "none"]

    panels, clamp_cost, clamp_risk, overshoot = [], 0, 0, []
    for row, scen in enumerate(["NZ15", "B20"]):
        for col, co in enumerate(["POSCO", "NSC", "LOTTE", "MCI"]):
            d = f[(f.company_id == co) & (f.scenario == scen)]
            if d.empty:
                continue
            hit = g[(g.company_id == co) & (g.scenario == scen)]
            gaprow = hit.iloc[0] if len(hit) else None
            panels.append(_panel(col * PW, row * PH, d, gaprow,
                                 f"{COMPANY_NAME.get(co, co)} · {scen}"))
            if gaprow is None:
                continue
            fr = d[d.on_frontier]
            p = d[d.is_disclosed].iloc[0]
            if p.tcar > fr.tcar.max():
                clamp_cost += 1
                overshoot.append(p.tcar / fr.tcar.max() if fr.tcar.max() else float("inf"))
            if p.p50 > fr.p50.max():
                clamp_risk += 1

    w, h = PW * COLS, PH * 2 + 30
    legend = (f'<g transform="translate({PW * COLS - 480},{h - 10})">'
              f'<circle class="cand" cx="6" cy="-4" r="2.8"/>'
              f'<text class="sub" x="14" y="0">candidate plan</text>'
              f'<circle class="frp" cx="112" cy="-4" r="3.2"/>'
              f'<text class="sub" x="120" y="0">efficient frontier</text>'
              f'<rect class="disc" x="234" y="-7.6" width="7.2" height="7.2" '
              f'transform="rotate(45 237.6 -4)"/>'
              f'<text class="sub" x="248" y="0">disclosed plan</text>'
              f'<line class="gap" x1="350" y1="-4" x2="372" y2="-4"/>'
              f'<text class="sub" x="378" y="0">gap (bn KRW)</text></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
           f'height="{h}" role="img" aria-label="Efficient frontier, disclosed plan '
           f'coordinate and frontier gap, by firm and scenario">'
           f'<style>{SVG_STYLE}</style>'
           f'<text class="sub" transform="translate(14,{h / 2}) rotate(-90)" '
           f'text-anchor="middle">TCaR (bn KRW) →</text>'
           + "\n".join(panels) + legend + "</svg>")
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    FIGURE.write_text(svg, encoding="utf-8")

    return (f"![Efficient frontier, disclosed coordinate and frontier gap, "
            f"per firm and scenario](figures/frontier_gap.svg)\n\n"
            f"Each panel is one firm under one scenario, on its own axes. The dashed legs are the "
            f"two gap numbers, and where they end is the point of the figure: `_gap` "
            f"(`src/cap/e5_metrics.py:61`) interpolates along the frontier only while the disclosed "
            f"point lies within the frontier's span on the axis being measured, and otherwise "
            f"clamps to the endpoint. Of the {len(g)} distinct gaps in `out/e5/gap.csv`, "
            f"**{clamp_cost} of {len(g)} cost legs and {clamp_risk} of {len(g)} risk legs are "
            f"clamped**: every disclosed plan sits above the frontier's whole tail-risk span — by "
            f"{_x(min(overshoot))} to {_x(max(overshoot))} the tail risk of the riskiest plan on "
            f"its own frontier — so a cost leg is never an interpolated distance, it is the "
            f"distance to the frontier's riskiest endpoint. Clamped legs are lower bounds by "
            f"construction: that endpoint reaches the same cost saving with *less* risk than an "
            f"interpolated point would have. {len(g_all)} rows appear in the file because the "
            f"`support` axis duplicates each one (§3.6, O7).")


BLOCKS = {
    "stamp": gen_stamp,
    "gap_figure": gen_gap_figure,
    "axis_impact": gen_axis_impact,
    "surrogate": gen_surrogate,
    "plan_distinct": gen_plan_distinct,
    "frontier_shape": gen_frontier_shape,
    "dataset_inventory": gen_dataset_inventory,
    "vocab": gen_vocab,
    "register_filter": gen_register_filter,
    "d1b_intensity": gen_d1b_intensity,
    "d2_provenance": gen_d2_provenance,
    "d3_reach": gen_d3_reach,
    "d3b_bands": gen_d3b_bands,
    "price_series": gen_price_series,
    "d6_coverage": gen_d6_coverage,
    "d7_enforcement": gen_d7_enforcement,
    "package": gen_package,
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
