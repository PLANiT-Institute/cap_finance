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
import datetime as dt
import hashlib
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


# Substantive state = code, inputs, config, results. Deliberately not a commit SHA:
# no SHA can be correct here, because the stamp is written inside the very commit it
# would have to name — the guide goes stale the instant it is committed. Restricting
# the SHA to commits touching these paths only narrows how often that happens; it did
# not stop it (F16 deleted one file under data/ and the gate went red on the next
# cycle). A digest of the *content* of these paths is knowable before the commit, so
# it is stable across the commit that carries it, and it still moves whenever code,
# inputs, config or results move. Prose-only commits leave it alone.
STATE_PATHS = ["src", "data", "config.yaml", "out", "docs/*.csv"]

# `git ls-files` only sees *tracked* files, and `.gitignore:31` ignores `out/**`. So the
# digest that advertised itself as covering results was reading 2 of 847 files under
# `out/` (F28): a full `python -m cap all` could move every number the guide quotes and
# the stamp would not budge, while `--check` and the stamp test stayed green. Results are
# enumerated from disk instead — 847 files, 397 MB, 0.6 s to hash, which is not a reason
# to prefer a stamp that is blind to them.
DISK_STATE = "out"


def _state_files():
    tracked = subprocess.run(["git", "ls-files", "-z", *STATE_PATHS],
                             cwd=ROOT, capture_output=True, text=True).stdout.split("\0")
    on_disk = [str(p.relative_to(ROOT)) for p in (ROOT / DISK_STATE).rglob("*")
               if p.is_file() and not any(s.startswith(".") for s in p.parts)]
    return sorted(set(f for f in tracked if f) | set(on_disk))


def state_digest() -> str:
    h = hashlib.sha256()
    for name in _state_files():
        p = ROOT / name
        h.update(name.encode())
        # a tracked path deleted in the working tree is a state change, not a crash
        h.update(p.read_bytes() if p.is_file() else b"<absent>")
    return h.hexdigest()[:12]


def gen_stamp():
    man = ROOT / "out" / "run_manifest.json"
    run = json.loads(man.read_text())["e5"]["finished"] if man.exists() else "no run recorded"
    return (f"> **Repository state.** Code, inputs, config, results and the derived records "
            f"this document cites (`{'`, `'.join(STATE_PATHS)}` — {len(_state_files()):,} files, "
            f"results read from disk because `out/` is not tracked) hash to "
            f"`{state_digest()}`. Results in this document "
            f"come from the pipeline run finished `{run}`. Rebuild the generated blocks with "
            f"`python3 scripts/build_tech_guide.py`; `--check` fails if this document no longer "
            f"matches that state. The stamp is a content digest, not a commit SHA, because a SHA "
            f"is not knowable inside the commit that writes it.")


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


def gen_d3_excluded():
    """Raw D3 rows that never reach the solver.

    F19: the guide said "13 rows in total" and stopped there, so a reader could not
    tell that CCUS is priced in the raw table and excluded from the run — and §4.2's
    A-10 said the opposite ("CCUS and efficiency are retrofits"). Both sides of the
    filter are data, so the count and the names are generated.
    """
    raw = pd.read_csv(ROOT / "data" / "raw" / "tech_options.csv")
    kept = pd.read_csv(prepared() / "D3_tech_options.csv")
    dropped = raw[~raw.tech_id.isin(kept.tech_id)]
    ccus = sorted(dropped[dropped.tech_id.str.contains("ccus")].tech_id)
    alt = dropped[dropped.tech_id.str.endswith("_alt")]
    pairs = []
    for r in alt.itertuples():
        base = r.tech_id[: -len("_alt")]
        adopted = kept.loc[kept.tech_id == base, "capex_unit"]
        pairs.append(f"`{r.tech_id}` {r.capex_unit:,.0f} against the adopted "
                     f"{adopted.iloc[0]:,.0f}" if len(adopted) else f"`{r.tech_id}`")
    other = sorted(set(dropped.tech_id) - set(ccus) - set(alt.tech_id))
    return (
        f"**The model sees {len(kept)} of the {len(raw)} rows in "
        f"`data/raw/tech_options.csv`.** {len(dropped)} are filtered out in preparation and "
        f"nothing downstream can adopt them. "
        f"{len(ccus)} of them are the CCUS measures ({', '.join('`' + c + '`' for c in ccus)}): "
        "**CCUS is not in the option set at all** — a user scope decision of 2026-08-06, taken "
        "until storage-capacity and cost data exist, applied at `scripts/prepare_raw.py:303`. "
        f"The other {len(alt)} are alternative-source CAPEX estimates kept for sensitivity and "
        f"read by nothing in this run ({'; '.join(pairs)} thousand KRW/t of capacity). "
        + (f"Also dropped: {', '.join('`' + o + '`' for o in other)}. " if other else "")
        + "This is the one exclusion in §3 that removes a measure firms actually name in their "
        "own disclosures — see §6.4 for what it costs the disclosed-plan comparison.")


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
            "`steel_eaf` at 240 is POSCO's Gwangyang project on a reused site, and the band it "
            "sits below is stated to be greenfield EAF builds in the `derivation` column of "
            "`data/raw/tech_bands.csv` — that is where the greenfield attribution lives, not in "
            "the estimation notes this sentence used to cite. It is the evidence that the "
            "central values were not quietly snapped to the literature." + _eaf_evidence_note())
    return _md(rows, ["Tech", "Field", "Central", "Band", "Position", "Tier"]) + note


def _eaf_evidence_note():
    """How low 240 is against every primary EAF project figure we hold.

    F19: the band explanation ("reused site, not greenfield") is true and not the whole
    reading. The independent implementation collected six primary project figures for
    the same technology, and Gwangyang is the lowest of them by a factor of five.
    """
    p = ROOT / "cap-efficient" / "data" / "technology_cost_evidence.csv"
    if not p.exists():
        return ""
    e = pd.read_csv(p)
    e = e[e.technology_id == "SCRAP_EAF"]
    if e.empty:
        return ""
    v = e.normalized_capex_bn_krw_per_mtpa.astype(float)
    lo = e.loc[v.idxmin()]
    rest = v.drop(v.idxmin())
    partial = sorted(e.loc[e.comparability.str.startswith("partial"), "project_id"])
    return (
        f" The independent implementation puts a sharper reading on the same number: of the "
        f"{len(e)} primary EAF project figures in "
        f"`cap-efficient/data/technology_cost_evidence.csv`, Gwangyang's "
        f"{lo.normalized_capex_bn_krw_per_mtpa:,.0f} is the lowest"
        + (f" and the only one flagged partial-scope ({len(partial)} of {len(e)})" if len(partial) == 1
           else "")
        + f", while the other {len(rest)} normalise to {rest.min():,.0f}–{rest.max():,.0f} thousand "
        "KRW/t because they are gross figures covering government support and downstream measures. "
        "Read 240 as a defensible floor rather than a central EAF cost. It costs this model nothing "
        "either way, because `steel_eaf` is the row no facility can adopt (above) — it costs the "
        "other model, which does allow the conversion, and that is recorded in "
        "[`docs/tech_cost_reconciliation.md`](tech_cost_reconciliation.md).")


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
    silent_keys = [k for k, vs in verdicts.items() if any("silently" in v for v in vs)]
    n_high_silent = sum(d7.resolution.loc[i] == "high" for _, i in silent_keys)
    # scenario-invariance is measured, and when it holds the reason is named: the
    # scenario availability table E1 writes is what could have split a verdict.
    n_split = sum(1 for vs in verdicts.values() if len(vs) > 1)
    if n_split:
        scen = (f" Verdicts differ between scenarios for {n_split} of the "
                f"{len(verdicts)} rows.")
    elif not len(avail):
        scen = (f" Verdicts are identical across all {len(cfg.scenarios)} scenarios, and not by "
                f"coincidence: `out/e1/tech_availability.csv` has {len(avail)} rows, so the "
                "scenario term in the availability test never binds (test 5 above).")
    else:
        scen = (f" Verdicts are identical across all {len(cfg.scenarios)} scenarios even though "
                f"the scenario availability table carries {len(avail)} rows.")
    note = (f"\n\nOf the {len(d7)} rows, **{n_forced} become a forced decision**, "
            f"{n_rec} are dropped with a reason written to `out/e2/disclosed_skipped.csv`, and "
            f"**{n_silent} are dropped without a trace** — the skip file has no line for them, so a "
            "reader counting that file undercounts what the disclosed coordinate is missing. "
            f"`resolution` appears in none of it: {n_high_silent} of the {n_silent} silently "
            "dropped rows are tagged `high`, and they go for the same reason a `mid` row would."
            + scen
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


def _metrics(path, scen="NZ15", supp="none"):
    """(company, scenario, support) -> (②, ③) for one metrics_company.csv."""
    m = pd.read_csv(path)
    if scen:
        m = m[(m.scenario == scen) & (m.support == supp)]
    return {(r.company_id, r.scenario, r.support):
            (r.cost_per_tco2_thkrw, r.tcar_bnkrw) for r in m.itertuples()}


def _drift(control, current):
    """Largest signed % divergence of a diagnostic's own control from the live run.

    Every off-pipeline diagnostic in `out/` carries an arm configured identically to the
    headline. If that arm no longer reproduces the headline, the diagnostic was computed
    against a base run that no longer exists — F20 found the price-process arms a full E2
    re-solve behind, which is why this is measured rather than asserted.
    """
    hits = []
    for k, v in control.items():
        c = current.get(k)
        if c is None:
            continue
        d2 = 100 * (v[0] / c[0] - 1) if c[0] else 0.0
        dt = 100 * (v[1] / c[1] - 1) if c[1] else 0.0
        if abs(d2) > 0.05 or abs(dt) > 0.05:
            hits.append((k, d2, dt))
    if not hits:
        return 0, "—", "—"
    firms = len({k[0] for k, _, _ in hits})
    w2 = max(hits, key=lambda h: abs(h[1]))
    wt = max(hits, key=lambda h: abs(h[2]))
    return (firms,
            f"{w2[1]:+.2f}% ({COMPANY_NAME.get(w2[0][0], w2[0][0])}, {w2[0][1]})",
            f"{wt[2]:+.2f}% ({COMPANY_NAME.get(wt[0][0], wt[0][0])}, {wt[0][1]})")


def _mtime(p):
    return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def _arms(root: Path, rel: str):
    """A sidecar's per-arm result files, oldest first.

    F26: the drift table dated each sidecar by its **summary** file and measured drift on
    its **control arm alone**. Both are rewritten by a partial re-run, so a directory in
    which one arm had been re-solved and ten had not reported itself fresh and undrifted —
    which is precisely the state `out/scenarios` was in mid-campaign on 2026-08-12. Date a
    sidecar by its oldest arm instead, and count how many arms predate the base run.
    """
    arms = [(d.name, (d / rel)) for d in sorted(root.iterdir()) if (d / rel).exists()]
    return sorted(arms, key=lambda a: a[1].stat().st_mtime)


def _eff_file(rel: str):
    """EFF exists twice — the copy committed here (canonical) and a separate repository."""
    for base in (ROOT / "cap-efficient", Path.home() / "Documents" / "cap-efficient"):
        p = base / rel
        if p.exists():
            return p
    return None


def gen_reline_anchors():
    """Every external anchor on the blast-furnace reline replacement cost, not just one.

    F21: the guide carried "fails external validation, 4.2x a disclosed actual" in two
    places. That verdict is from a single observation and `docs/validation_external.md`
    §1-1 retired it on 2026-08-10 (L1, `docs/literature_map.md` §4-1): with three anchors
    our 200 is above two of them and *inside* the third. Constants and FX come from
    `scripts/validate_external.py` so the two documents cannot print different anchors.
    """
    ev = _eff_file("data/technology_cost_evidence.csv")
    if ev is None:
        return "_EFF evidence file not found — cannot rebuild the reline anchors._"
    sys.path.insert(0, str(ROOT / "scripts"))
    from validate_external import (ACCR_RELINE_USD_M, EURKRW,  # noqa: E402
                                  NATCOMM_RELINE_EUR_T, USDKRW)
    rl = pd.read_csv(ev)
    rl = rl[rl.technology_id == "BF_RELINE"]
    if rl.empty:
        return "_No `BF_RELINE` row in the EFF evidence file._"
    kobe = float(rl.normalized_capex_bn_krw_per_mtpa.iloc[0])

    d1a = pd.read_csv(prepared() / "D1a_facility_static.csv")
    bf = d1a[d1a.unit_type == "BF"]
    ours = float(bf.incumbent_capex_unit.median())
    cap = float(bf.capacity.median()) / 1e6          # Mt/yr
    natcomm = NATCOMM_RELINE_EUR_T * EURKRW / 1000
    lo, hi = (v * USDKRW / 1e3 / cap for v in ACCR_RELINE_USD_M)

    rows = [
        [f"Kobe Steel No. 3 reline, 2016 (shell reused, 90 days)", f"{kobe:,.0f}",
         "disclosed project cost", "`KOBELCO_HBI_BF`", f"ours is {ours / kobe:.1f}× this"],
        ["Literature reline unit cost", f"{natcomm:,.0f}", f"€{NATCOMM_RELINE_EUR_T:g}/t",
         "`NATCOMM_APA_2026`", f"ours is {ours / natcomm:.1f}× this"],
        ["Replacement cost per furnace ÷ our median BF capacity",
         f"{lo:,.0f} – {hi:,.0f}",
         f"US${ACCR_RELINE_USD_M[0]:,.0f}–{ACCR_RELINE_USD_M[1]:,.0f}M per furnace "
         f"÷ {cap:.2f} Mt/yr", "`ACCR_BF_RELINE_2025`",
         "**ours is inside this band**"],
        [f"**Ours** (`incumbent_capex_unit`, median of {len(bf)} BFs)", f"**{ours:,.0f}**",
         "injected per unit type", "—", "—"],
    ]
    head = _md(rows, ["Anchor", "thousand KRW/t capacity", "Original figure",
                      "source_id", "Against ours"])
    return head + (
        f"\n\n**The three anchors do not converge — {kobe:,.0f}, {natcomm:,.0f}, "
        f"[{lo:,.0f}, {hi:,.0f}] — so the finding is a {hi / kobe:.0f}× dispersion in the "
        f"reline unit cost, not a point error in ours.** Two qualifications belong in the "
        f"same sentence as the numbers. First, the ACCR figure is per furnace and its source "
        f"does not state a currency; USD is assumed, and on the AUD reading the band falls to "
        f"[{lo * 0.65:,.0f}, {hi * 0.65:,.0f}] and our {ours:,.0f} sits **above** it — the "
        f"'inside the band' verdict is contingent on an assumption the source does not "
        f"settle. Second, `NATCOMM_APA_2026`'s H2-DRI-EAF figure is exactly `VOGL_2018`'s, so "
        f"its reline figure may be a secondary citation of the same lineage rather than an "
        f"independent observation: count 2.5 anchors, not 3. What follows for the model is a "
        f"range, not a replacement: only the low end has been re-run "
        f"(`reline_cheap`, ×{kobe / ours:.3f}), and nothing has been run at "
        f"×{hi / ours:.2f} — the upper end of the same band.")


def gen_band_vs_convention():
    """§4.5 — what the ±30% convention costs, read off `out/g2` rather than typed.

    F26: this sentence was hand-written and the sidecar under it had been re-run, so it
    carried NSC's pre-band parameter share as 23% where `out/g2/f3_compare.csv` says 21.4%.
    The multipliers, the two steel firms and the petrochemical claim all come from the same
    two files, so all of them are generated together.
    """
    b, f = ROOT / "out" / "g2" / "bands.csv", ROOT / "out" / "g2" / "f3_compare.csv"
    if not (b.exists() and f.exists()):
        return "_No band comparison in `out/g2`. Run `scripts/g2_band_impact.py`._"
    bd, fc = pd.read_csv(b), pd.read_csv(f)
    W = 0.15
    d = fc[fc.width == W].set_index("company_id")
    # `capex_unit` carries a band on two technology rows; the envelope across them is the
    # claim, so aggregate rather than keeping whichever row happened to be last.
    mult = {fl: (g.mult_low.min(), g.mult_high.max()) for fl, g in bd.groupby("field")}
    steel = [c for c in ("POSCO", "NSC") if c in d.index]
    moves = " and ".join(
        f"{d.loc[c, 'param_share_pct_conv']:.0f}% to {d.loc[c, 'param_share_pct_band']:.0f}% "
        f"({COMPANY_NAME.get(c, c)})" for c in steel)
    worst = max((abs(d.loc[c, "param_share_pct_band"] - d.loc[c, "param_share_pct_conv"])
                 for c in d.index), default=0.0)
    lo, hi = mult.get("capex_unit", (0, 0))
    elo, ehi = mult.get("emission_factor", (0, 0))
    txt = (f"The evidence puts `tech.capex` at [{lo:.2f}, {hi:.2f}]× our central value and "
           f"`tech.emission_factor` at [{elo:.2f}, {ehi:.2f}]×, both one-sided, while the "
           f"convention draws symmetrically around 1. Substituting the bands for the convention "
           f"moves the steel parameter share of TCaR from {moves} at ±{W:.0%} width, and no "
           f"firm by more than {worst:.1f} percentage points.")
    if worst >= 0.5:
        return txt
    # F26: the substitution costing nothing is not evidence that the convention is harmless.
    # Say which banded parameter the decomposition actually draws, and where the one with the
    # wide band sits in the screen that decides what gets drawn.
    dec = ROOT / "out" / "uncertainty" / "decomposition_bands.csv"
    rk = ROOT / "out" / "sensitivity" / "ranking.csv"
    if not (dec.exists() and rk.exists()):
        return txt
    dc = pd.read_csv(dec).iloc[0]
    drawn = str(dc.params).split("|") if "params" in dc.index else []
    r = pd.read_csv(rk).reset_index(drop=True)
    pos = {p: i + 1 for i, p in enumerate(r.base_param)}
    absent = [p for p in ("tech.capex",) if p not in drawn]
    return txt + (
        f" **That is not evidence that the convention is harmless.** Of the {len(drawn)} "
        f"parameters the decomposition draws, {int(dc.n_banded)} carries a literature band, and "
        + (f"`{', '.join(absent)}` — the one whose band is wide and one-sided — is not among "
           f"them: it ranks {pos.get(absent[0], 0)} of {len(r)} in the screen that chooses what "
           f"gets drawn (`out/sensitivity/ranking.csv`), below the cut. The one place we hold "
           f"evidence against the ±30% convention is a place this test cannot reach."
           if absent else
           "the band it carries is narrower than the convention on both sides."))


def gen_seed_cv():
    """§6.1 sampling-noise table.

    F26: this table and the caveat under it were hand-written, and the seed sweep had moved
    under them — `docs/seed_stability.csv` was 18h behind the base run, and re-running it
    (17 seconds) changed every Nippon Steel row. A table of numbers that must be re-derived
    whenever a sidecar is re-run belongs to the generator, and the "is the sweep current"
    question is answered here by comparison rather than asserted in prose.
    """
    p = ROOT / "docs" / "seed_stability.csv"
    cur_p = ROOT / "out" / "e5" / "metrics_company.csv"
    if not (p.exists() and cur_p.exists()):
        return "_No seed sweep in `docs/seed_stability.csv`. Run `scripts/seed_stability.py`._"
    from cap import config as C
    d = pd.read_csv(p)
    cv = lambda x: 100 * x.std(ddof=1) / abs(x.mean())
    rows, worst = [], {}
    for label, col in [("② P50 / abatement cost", "cost_per_tco2_thkrw"),
                       ("③ TCaR", "tcar_bnkrw"),
                       ("⑤ Flexibility", "flex_value_bnkrw")]:
        g = d.groupby("company_id")[col].agg(cv)
        read = ("The digits as printed" if g.max() < 1 else
                "**Two significant figures**" if g.max() < 3 else
                "**One significant figure**")
        rows.append([label, f"{g.min():.1f}–{g.max():.1f}%", read])
        worst[col] = g.idxmax()
    head = _md(rows, ["Metric", "Coefficient of variation", "Read to"])

    seed = C.load().seed
    pin = d[d.seed == seed].set_index("company_id")
    cur = pd.read_csv(cur_p).query("scenario == 'NZ15' and support == 'none'") \
                            .set_index("company_id")
    off = []
    for co in sorted(set(pin.index) & set(cur.index)):
        for col, m in (("cost_per_tco2_thkrw", "②"), ("tcar_bnkrw", "③")):
            a, b = float(pin.loc[co, col]), float(cur.loc[co, col])
            if b and abs(a / b - 1) > 5e-4:
                off.append(f"{COMPANY_NAME.get(co, co)} {m} {a:,.1f} against {b:,.1f}")
    tc = worst["tcar_bnkrw"]
    ex = (f"\n\nThe binding row is ③: at {d[d.company_id == tc].tcar_bnkrw.agg(cv):.1f}% on "
          f"{COMPANY_NAME.get(tc, tc)} the printed "
          f"{cur.loc[tc, 'tcar_bnkrw']:,.0f} bn KRW carries about "
          f"{cur.loc[tc, 'tcar_bnkrw'] * d[d.company_id == tc].tcar_bnkrw.agg(cv) / 100:,.0f} bn "
          f"of pure sampling noise, which is why §6 rounds it.")
    if off:
        return head + ex + (
            f"\n\n**The sweep is older than the current run.** Its pinned-seed rows "
            f"(`seed={seed}`) no longer reproduce §6: {'; '.join(off)}. The plan menu moved "
            f"after the sweep was taken, so read these CVs as the order of magnitude of seed "
            f"noise, not as an error bar on the table above. `scripts/seed_stability.py` "
            f"re-runs it in under a minute.")
    return head + ex + (
        f"\n\nThe sweep is **taken on the plan menu now in `out/`**: its pinned-seed rows "
        f"(`seed={seed}`) reproduce §6's ② and ③ for all {len(cur)} firms to within a "
        f"twentieth of a percent, so these CVs are an error bar on the table above rather than "
        f"a measurement on a menu that has since moved. That was not true before 2026-08-12, "
        f"and the guide said so; what closed it was re-running the sweep, which costs seconds.")


def gen_diagnostic_drift():
    base = ROOT / "out" / "e5" / "metrics_company.csv"
    if not base.exists():
        return "_No pipeline run in `out/`. Run `python -m cap all`._"
    cur_all = _metrics(base, scen=None)
    cur_nz = {k: v for k, v in cur_all.items() if k[1] == "NZ15" and k[2] == "none"}

    t_base = base.stat().st_mtime
    rows, stale, partial = [], [], []

    def _add(label, root, rel, ctl_file, ctl_label, ctl_map, cur):
        """One sidecar row. Dated by its **oldest** arm, not by its summary file."""
        arms = _arms(root, rel) if root else []
        behind = [a for a, p in arms if p.stat().st_mtime < t_base]
        oldest = _mtime(arms[0][1]) if arms else _mtime(ctl_file)
        n, d2, dt_ = _drift(ctl_map, cur) if ctl_map is not None else ("—", "—", "—")
        rows.append([label, oldest,
                     f"{len(behind)} of {len(arms)}" if arms else "—",
                     ctl_label, n, d2, dt_])
        if behind or (not arms and ctl_file.stat().st_mtime < t_base):
            stale.append(f"`{label.split('`')[1]}`")
        # 대조 팔은 새것인데 섭동 팔이 낡은 경우 — 표의 drift 열이 0을 보고하면서
        # 그 0이 아무것도 보증하지 않는 상태다. F26에서 실제로 그렇게 됐다.
        if behind and n == 0:
            partial.append((label.split('`')[1], len(behind), len(arms)))

    proc = ROOT / "out" / "process" / "gbm" / "e5" / "metrics_company.csv"
    if proc.exists():
        _add("`out/process` price-process arms", ROOT / "out" / "process",
             "e5/metrics_company.csv", proc, "`gbm`", _metrics(proc), cur_nz)
    sc = ROOT / "out" / "scenarios" / "summary.csv"
    if sc.exists():
        s = pd.read_csv(sc)
        ctl = {(r.company_id, r.scenario, r.support):
               (r.cost_per_tco2_thkrw, r.tcar_bnkrw)
               for r in s[s.bundle == "base"].itertuples()}
        _add("`out/scenarios` bundle matrix", ROOT / "out" / "scenarios",
             "e5/metrics_company.csv", sc, "`bundle=base`", ctl, cur_all)
    m8 = ROOT / "out" / "m8" / "summary.csv"
    if m8.exists():
        _add("`out/m8` ε-constraint sweep", None, "", m8, "none — unmeasurable", None, None)
    if not rows:
        return "_No side diagnostics in `out/`._"

    head = _md(rows, ["Diagnostic", "Oldest arm written", "Arms behind base", "Control arm",
                      "Firms drifted", "Largest ② drift", "Largest ③ drift"])
    warn = "".join(
        f"\n\n**`{d}` is part re-run, and its drift column is therefore not evidence.** "
        f"{n} of its {t} arms predate the base run while the control arm does not, so the control "
        f"reproduces the headline exactly and the table reads 0 — the arms that are actually "
        f"behind are the ones the control cannot see. Read this row as unmeasured until the "
        f"campaign completes."
        for d, n, t in partial)
    if not stale:
        return head + (f"\n\nEvery arm of every diagnostic above post-dates the base run "
                       f"(`out/e5`, {_mtime(base)}), so the perturbations are measured "
                       f"against the headline as printed.") + warn
    return head + (
        f"\n\n**Not all of these are measured against the run in §6.** The base pipeline was last "
        f"written {_mtime(base)}; {', '.join(stale)} "
        f"{'carries' if len(stale) == 1 else 'carry'} at least one arm that predates it and "
        f"was computed against an earlier E2 plan set. Each row is dated by its **oldest** arm, "
        f"not by its summary file, because a summary is rewritten by a partial re-run and would "
        f"otherwise date a mostly-stale directory as fresh. Where a diagnostic carries a control "
        f"arm configured identically to the headline, the table measures how far that arm has "
        f"drifted; where it carries none, the drift exists but is unquantified. The drift is a "
        f"property of the **baseline**, not of the perturbation — an arm and its own control move "
        f"together — so the *differences* quoted from these files stay internally consistent while "
        f"the *levels* in them do not match §6. Re-running the diagnostics after a base re-solve "
        f"is what closes this, and until it is closed `scripts/gate.py` names these files and "
        f"their lag in its `sidecars` check — a warning rather than a failure, because a stale "
        f"diagnostic is work not yet re-run, not a defect in the code.") + warn


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
    bundles, cells = 0, 0
    sc = ROOT / "out" / "scenarios" / "summary.csv"
    if sc.exists():
        s = pd.read_csv(sc)
        # `base` is the reference the others are differenced against, not an assumption bundle.
        # F12 found it counted as one here, and the inflated 12 copied into §4.3 and O8.
        bundles = s[s.bundle != "base"].bundle.nunique()
        cells = int(s[s.bundle == "base"].shape[0])
    note = (f"\n\nScenario NZ15, `support=none`. Read TCaR to two significant figures (§6.1).\n\n"
            f"A frontier gap is computed for **{n_gap} of {m.company_id.nunique()} firms**; "
            f"§6.4 explains why the other two are not a disclosure failure. "
            f"{bundles} assumption bundles have been evaluated against the `base` run, "
            f"each over {cells} firm × scenario × support cells.")
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
        # F26: this used to send the reader to an `m5` CLI stage. There is none —
        # the CLI has e1–e5, render, all; `out/m5` is written by the script below.
        return ("_No bundle sweep in `out/m5`. Run `scripts/run_scenarios.py` then "
                "`scripts/robustness_section_table.py`._")
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_scenarios import REPLAN_MINUTES, REPLAN_REQUIRED
    # F21: "not needed" was printed for every bundle outside REPLAN_REQUIRED, including
    # `reline_cheap` — whose scale reaches E2 through `stranded_cost_k`, so holding the plan
    # menu fixed measures the write-off saving at an adoption year the assumption should have
    # moved. The scenario page already says so; take its list rather than keeping a second one.
    from build_scenario_page import PARTIAL_EFFECT
    b = pd.read_csv(p).sort_values("d_tcar_pct", ascending=False)
    rows = [[f"`{r.bundle}`", AXIS.get(r.bundle, ("—", "—"))[0],
             AXIS.get(r.bundle, ("—", r.bundle))[1],
             ("yes" if r.replanned else
              "**no — required**" if r.bundle in REPLAN_REQUIRED else
              "**no — lower bound**" if r.bundle in PARTIAL_EFFECT else "not needed"),
             f"{r.d_m2_pct:.1f}%", f"{r.d_tcar_pct:.1f}%"]
            for r in b.itertuples()]
    head = _md(rows, ["Bundle", "Assumption", "What it varies", "Re-planned",
                      "Δ② (max, %)", "Δ③ (max, %)"])
    stale = sorted(set(b[~b.replanned].bundle) & REPLAN_REQUIRED)
    # F26: the prose above this block claimed these were maxima over all sixteen
    # firm × scenario × support cells. They are not — `robustness_section_table.py`
    # computes them on the headline cell only, and the two are far apart. Say which
    # cells they are here, where the generator owns it, and print both.
    from robustness_section_table import SCEN, SUPP
    s = pd.read_csv(ROOT / "out" / "scenarios" / "summary.csv")
    n_cells = len(s.query("bundle == 'base' and scenario == @SCEN and support == @SUPP"))
    n_all = len(s[s.bundle == "base"])
    w = b.loc[b.d_tcar_pct_all.idxmax()]
    # F26: which cell the wide maximum sits in was asserted in prose ("the B20 scenario and
    # the support=current cells"). Read it off instead — the answer moves with the sweep.
    idx = ["company_id", "scenario", "support"]
    base = s[s.bundle == "base"].set_index(idx).tcar_bnkrw
    x = s[s.bundle == w.bundle].set_index(idx).tcar_bnkrw
    r = (x / base.reindex(x.index) - 1).abs()
    co, scen, supp = r.idxmax()
    note = (
        f"\n\n**Δ② and Δ③ above are the largest move across the {n_cells} firms in the "
        f"headline cell (`{SCEN}`, `support={SUPP}`) — not across all {n_all} "
        f"firm × scenario × support cells.** That is the definition §6 of the paper uses, "
        f"and it is the narrower one: over all {n_all} cells the same sweep reaches "
        f"**{b.d_m2_pct_all.max():.1f}%** on ② and **{b.d_tcar_pct_all.max():.1f}%** on ③, "
        f"both on `{w.bundle}`, whose headline figures are {w.d_m2_pct:.1f}% and "
        f"{w.d_tcar_pct:.1f}%. That widest ③ move is "
        f"{COMPANY_NAME.get(co, co)} under `{scen}` with `support={supp}` — an assumption can "
        f"bite several times harder outside the cell that is reported than inside it.")
    note += (
        f"\n\nLargest mover on ③ is `{b.iloc[0].bundle}` ({b.iloc[0].d_tcar_pct:.1f}%); "
        f"on ② it is `{b.loc[b.d_m2_pct.idxmax()].bundle}` ({b.d_m2_pct.max():.1f}%) — "
        f"not the same bundle, so no single axis dominates both metrics.")
    # F26: this count was hand-written above the block ("Two of those five have been
    # re-planned") and went stale the moment a bundle was re-planned. The generator owns it.
    done = sorted(set(b[b.replanned].bundle) & REPLAN_REQUIRED)
    note += (
        f"\n\n**{len(done)} of the {len(REPLAN_REQUIRED)} E2-only axes have been re-planned** "
        f"({', '.join('`' + s + '`' for s in done)})"
        + (f"; `{'`, `'.join(stale)}` still have not." if stale else
           ", so every axis in this table has been solved through the plan optimiser rather "
           "than merely re-priced.")
        + f" Re-planning one bundle costs about {REPLAN_MINUTES} minutes of solver time.")
    if stale:
        note += (
            f"\n\n**Read {', '.join('`' + s + '`' for s in stale)} as unmeasured, not as flat.** "
            f"Those axes are read only inside E2, so with the plan menu held fixed they can "
            f"re-price a plan but not change it; their Δ② / Δ③ are an artefact of that.")
    partial = sorted(set(b[~b.replanned].bundle) & set(PARTIAL_EFFECT))
    if partial:
        note += (
            f"\n\n**{', '.join('`' + s + '`' for s in partial)} is measured, but what is "
            f"measured is a lower bound.** The replacement cost enters E2 through the "
            f"stranding term, so its main effect is to **pull adoption years forward**; with "
            f"the plan menu shared, all that is left is the smaller write-off at an adoption "
            f"year the assumption should have moved. `run_scenarios.py --replan "
            f"{partial[0]}` is what would measure it.")
    r = ROOT / "out" / "sensitivity" / "ranking.csv"
    if r.exists():
        rk = pd.read_csv(r)
        s = rk.head(5)
        note += ("\n\nOne-at-a-time parameter screening, top 5 by worst-metric move: "
                 + ", ".join(f"`{t.base_param}` ({t.tier}, {t.score:.0f}%)"
                             for t in s.itertuples()) + ". "
                 f"`{rk.iloc[0].base_param}` is {rk.iloc[0].score / rk.iloc[1].score:.1f}× "
                 f"the next parameter, which is the quantity A-02 in §4.1 quotes. "
                 f"The screen perturbs every parameter by a symmetric ±30% — the convention "
                 f"§4.5 shows to be wrong in its *center* wherever literature bands exist — "
                 f"**with the E2 plan menu held fixed** (`scripts/sensitivity_screening.py`), so like "
                 f"`reline_cheap` above it re-prices plans rather than re-choosing them — the "
                 f"same ceiling, and it too understates. These ranks are read from "
                 f"`out/sensitivity/ranking.csv` at build time.")
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
    out = (f"Separately, of {len(d)} enumerated plans only **{distinct}** are distinct under "
           f"authoritative evaluation. {how_many} {grp.ngroups} bundles collapses "
           f"exactly one pair, which differs only in whether a CCfD is signed — under "
           f"`support=none` the CCfD strike is undefined, so the two plans are numerically "
           f"identical downstream while the surrogate charges a premium and prices them apart.")
    # F13: E4 keeps E2's contracts, E5 does not — it dedupes to technology schedules
    # and rebuilds the contract dimension. That second collapse is the larger one and
    # was in neither this guide nor METHODOLOGY.
    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if fp.exists():
        f = pd.read_csv(fp)
        f = f[(f.support == "none") & ~f.is_disclosed]
        sched = f.base_plan_id.nunique()
        per = sorted(f.groupby("base_plan_id").size().unique())
        grid = per[0] if len(per) == 1 else None
        out += (f"\n\nThe collapse E5 applies is larger still, and in the other direction. The "
                f"frontier is not built on E2's plans: E5 reduces them to their **{sched}** distinct "
                f"technology schedules — dropping the contract choice E2 made for each — and "
                f"regenerates the contract dimension itself"
                + (f", {grid} variants per schedule" if grid else "")
                + f" (`src/cap/e5_metrics.py:184-201`). So the {len(d)} enumerated plans carry "
                f"{sched} distinct investment programmes between them, and every \"candidate plan\" "
                f"count in §9.1 counts E5's regenerated set, not E2's output (§10).")
    return out


def _ccfd_note(f, pi):
    """Why no frontier point carries a CCfD — construction, not outcome (F13).

    Both the guide and METHODOLOGY §9-6 item 10 read "no frontier point in the
    current run signs a CCfD" as an observation about this run. It cannot be
    anything else: E5 rebuilds every non-disclosed candidate with ccfd=0, and D5
    has no ccfd row, so the instrument is inert in the authoritative revaluation
    for two independent reasons. E2 nevertheless signs it, because its surrogate
    credits CCfD against a proxy carbon-volatility term E4/E5 do not have.
    """
    d5 = ROOT / "data" / "prepared" / "D5_policy_support.csv"
    strikes = int((pd.read_csv(d5).instrument == "ccfd").sum()) if d5.exists() else 0
    signed, total = int(pi.ccfd.sum()), len(pi)
    if int(f.ccfd.max()) or strikes:
        return ("\n\nCCfD is signed on some revalued point or a strike now exists in D5 — this "
                "passage was written for a run where neither was true and must be rewritten.")
    return (
        f"\n\nThe third contract instrument is absent from all of this by construction. **No "
        f"frontier point signs a CCfD, and none can.** E5 does not revalue the contracts E2 chose: "
        f"it dedupes E2's plans "
        f"down to technology schedules and rebuilds each one across a fixed contract grid with "
        f"`ccfd=0` on every point (`src/cap/e5_metrics.py:201`), and D5 carries **{strikes}** CCfD "
        f"strike rows, so a signed CCfD would price identically anyway "
        f"(`src/cap/plancost.py:258`). E2 signs a CCfD in **{signed} of {total}** enumerated plans "
        f"— it is credited there against a proxy carbon-volatility term the authoritative "
        f"revaluation does not carry (`src/cap/e2_milp.py:263`) — and not one of those signatures "
        f"reaches a reported number. P2 (§1) is therefore untested for CCfD in this run, and the "
        f"frontier's financing axis is PPA share and fixed-price EPC only.")


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
    pi = pd.read_csv(ROOT / "out" / "e2" / "plan_index.csv")
    rows, one_sched, last_ranked, bottom_half = [], 0, 0, 0
    multi_avail, multi_collapsed = 0, 0
    for (co, sc), d in f.groupby(["company_id", "scenario"]):
        hit = g[(g.company_id == co) & (g.scenario == sc)]
        fr = d[d.on_frontier & ~d.is_disclosed]
        sched = fr.base_plan_id.nunique()
        one_sched += int(sched == 1)
        # F13: a bundle whose candidate set holds ONE schedule cannot show a second
        # one on its frontier — the collapse is arithmetic there, and only the
        # bundles that had a choice test the claim.
        avail = d[~d.is_disclosed].base_plan_id.nunique()
        multi_avail += int(avail > 1)
        multi_collapsed += int(avail > 1 and sched == 1)
        # where the frontier's schedule sits in the surrogate's own cost ordering
        p = pi[(pi.company_id == co) & (pi.scenario == sc)]
        rank = p.npv_cost_bnkrw.rank()[p.plan_id.isin(set(fr.base_plan_id))]
        last_ranked += int(rank.max() == len(p))
        bottom_half += int(rank.min() > len(p) / 2)
        rows.append([COMPANY_NAME.get(co, co), sc, len(d), avail, int(d.on_frontier.sum()), sched,
                     f"{hit.iloc[0].gap_cost_bnkrw:,.0f} / {hit.iloc[0].gap_risk_bnkrw:,.0f}"
                     if len(hit) else "**no coordinate**"])
    rows.sort(key=lambda r: (r[0], r[1]))
    head = _md(rows, ["Firm", "Scenario", "Candidate plans", "Schedules available", "On frontier",
                      "Distinct schedules on frontier", "Gap cost / risk (bn KRW)"])
    lo, hi = min(r[4] for r in rows), max(r[4] for r in rows)
    thin = [r for r in rows if r[6] != "**no coordinate**"]
    worst = min(thin, key=lambda r: r[4]) if thin else None
    note = (f"\n\nThe efficient frontier is **{lo} to {hi} plans** per firm × scenario, out of "
            f"{min(r[2] for r in rows)}–{max(r[2] for r in rows)} candidates. A frontier gap is a "
            f"distance to that set, so it is a distance to a handful of points, not to a curve.")
    if worst:
        note += (f" The thinnest case that carries a gap is {worst[0]} under {worst[1]}: "
                 f"**{worst[4]} non-dominated plans**, and the reported "
                 f"{worst[6]} bn KRW is the distance to them.")
    note += (
        f"\n\nThe column to read first is *Distinct schedules on frontier*. In **{one_sched} of "
        f"{len(rows)}** bundles every non-dominated point is a contract variant of a **single** "
        f"technology schedule — same facilities, same technologies, same years, same total CAPEX — "
        f"differing only in PPA share and the fixed-price EPC flag. Read that against the column "
        f"before it: in **{len(rows) - multi_avail} of {len(rows)}** bundles the candidate set "
        f"holds only one schedule to begin with, so there the collapse is arithmetic and not a "
        f"finding. The claim rests on the other {multi_avail} bundles, where the optimiser did "
        f"offer a choice of two or three schedules — and there the frontier still keeps one, in "
        f"**{multi_collapsed} of {multi_avail}**. The "
        f"frontier therefore slopes along the *financing* axis and "
        f"is a single point on the *technology* axis, so a frontier gap answers \"could this firm "
        f"have contracted its programme better\" and not \"could it have chosen a better "
        f"programme\". And that schedule is not one the surrogate liked: it is the surrogate's "
        f"most expensive plan in **{last_ranked} of {len(rows)}** bundles and in its bottom half in "
        f"**{bottom_half} of {len(rows)}**, which is the same failure §2 measures, seen from the "
        f"frontier's side (O11).")
    note += _ccfd_note(f, pi)
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

    `_gap` has THREE outcomes per leg, not two: interpolate inside the span, clamp
    beyond the high end, and NaN below the low end (clamping there would fabricate a
    gap the frontier cannot reach — `e5_metrics.py:61-81` says so in its own docstring).
    Counting only the clamped legs left the other two indistinguishable, so a leg that
    is blank in `out/e5/gap.csv` would have been reported as a measured distance. All
    three are counted here and cross-checked against the nulls in the file itself.
    """
    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if not fp.exists():
        return "_No pipeline run in `out/`. Run `python -m cap all`._"
    f = pd.read_csv(fp)
    f = f[f.support == "none"]          # the support axis duplicates every row (§3.6)
    g_all = pd.read_csv(ROOT / "out" / "e5" / "gap.csv")
    g = g_all[g_all.support == "none"]

    def _state(v, lo, hi):
        """Which of `_gap`'s three branches this leg lands in."""
        return "clamped" if v > hi else ("unmeasurable" if v < lo else "interpolated")

    panels, overshoot = [], []
    cost = {"clamped": 0, "interpolated": 0, "unmeasurable": 0}
    risk = {"clamped": 0, "interpolated": 0, "unmeasurable": 0}
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
            # the cost leg is measured along TCaR, the risk leg along P50 (`_gap`)
            cost[_state(p.tcar, fr.tcar.min(), fr.tcar.max())] += 1
            risk[_state(p.p50, fr.p50.min(), fr.p50.max())] += 1
            if p.tcar > fr.tcar.max():
                overshoot.append(p.tcar / fr.tcar.max() if fr.tcar.max() else float("inf"))
    # read the same fact from the other side: a NaN leg is a blank cell in the file
    null_cost = int(g.gap_cost_bnkrw.isna().sum())
    null_risk = int(g.gap_risk_bnkrw.isna().sum())

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

    span = (f"Every disclosed plan sits above the frontier's whole tail-risk span — by "
            f"{_x(min(overshoot))} to {_x(max(overshoot))} the tail risk of the riskiest plan "
            f"on its own frontier — so a cost leg is never an interpolated distance, it is the "
            f"distance to the frontier's riskiest endpoint. "
            if overshoot and cost["clamped"] == len(g) else "")

    return (f"![Efficient frontier, disclosed coordinate and frontier gap, "
            f"per firm and scenario](figures/frontier_gap.svg)\n\n"
            f"Each panel is one firm under one scenario, on its own axes. The dashed legs are the "
            f"two gap numbers, and where they end is the point of the figure. `_gap` "
            f"(`src/cap/e5_metrics.py:61-81`) has **three** outcomes per leg, not two: it "
            f"interpolates along the frontier while the disclosed point lies within the frontier's "
            f"span on the axis being measured; beyond the high end it clamps to the endpoint; and "
            f"below the low end it returns **NaN rather than extrapolating**, because a frontier "
            f"that cannot reach that risk or cost level has no distance to report and clamping "
            f"there would fabricate one. Of the {len(g)} distinct gaps in `out/e5/gap.csv`, "
            f"**cost legs are {cost['clamped']} clamped, {cost['interpolated']} interpolated and "
            f"{cost['unmeasurable']} unmeasurable; risk legs {risk['clamped']}, "
            f"{risk['interpolated']} and {risk['unmeasurable']}**. Read from the other side the "
            f"file agrees: {null_cost} blank cost legs and {null_risk} blank risk legs. "
            f"{span}Clamped legs are lower bounds by "
            f"construction: that endpoint reaches the same cost saving with *less* risk than an "
            f"interpolated point would have. An unmeasurable leg is not a zero gap — it is no "
            f"number at all, and §6 reports none where it occurs. {len(g_all)} rows appear in the "
            f"file because the `support` axis duplicates each one (§3.6, O7).")


def gen_limits():
    """Sizes for the §8 claims that were stated without one.

    A limitation with no magnitude is a disclaimer, not a limitation: a reader
    cannot tell whether it moves the answer. Every row here is recomputed from
    the artefacts, so a claim that stops being true stops being printed.
    """
    rows = []

    d1a = pd.read_csv(prepared() / "D1a_facility_static.csv")
    d1b = pd.read_csv(prepared() / "D1b_facility_panel.csv")
    site = ROOT / "data" / "raw" / "jp_site_emissions.csv"
    if site.exists():
        keys = set(pd.read_csv(site).site_key)
        d1a = d1a.assign(k=d1a.facility_id.str.split("_").str[1])
        at_site = d1a[d1a.k.isin(keys)]
        alloc = set(d1b[d1b.source_id == "PREP_ALLOC"].facility_id)
        used = at_site[at_site.facility_id.isin(alloc)]
        by = ", ".join(f"{c} {n}" for c, n in at_site.company_id.value_counts().items())
        rows.append([
            "1 — facility absolutes",
            f"**0 of {len(d1a)}** facilities carry a measured facility-level emission. "
            f"{len(at_site)} sit at a site with a measured *site* total ({by}), and the "
            f"site data reaches D1b for **{len(used)}** of them, as an inter-site "
            f"distribution only — every level is the company Scope 1 total rescaled",
            "`data/raw/jp_site_emissions.csv` × `D1a` × `D1b.source_id`"])

    pet = d1b[d1b.facility_id.str.startswith(("MCI_", "LOTTE_"))]
    if len(pet):
        ef = (pet.emissions_s1 / pet.production).round(6).unique()
        varies = int((pet.groupby("facility_id").production.nunique() > 1).sum())
        fp = pd.read_csv(ROOT / "data" / "raw" / "facility_panel.csv")
        cov = []
        for co, tot in (("MCI_", "MITSUI_TOTAL"), ("LOTTE_", "LOTTE_TOTAL")):
            t = fp[(fp.facility_id == tot) & fp.emissions_s1.notna()]
            s = pet[pet.facility_id.str.startswith(co)]
            if len(t) and len(s):
                y = s.year.max()
                cov.append(f"{co.rstrip('_')} {100 * s[s.year == y].emissions_s1.sum() / float(t.sort_values('year').emissions_s1.iloc[-1]):.0f}%")
        rows.append([
            "2 — petrochemical intensity",
            f"every petrochemical facility-year carries the same implied intensity "
            f"(**{'/'.join(f'{e:g}' for e in ef)} tCO₂/t**, the injected NCC route factor), "
            f"production is flat across {_span(pet, 'year')} for "
            f"**{len(pet.facility_id.unique()) - varies} of "
            f"{len(pet.facility_id.unique())}** units, and the modelled units cover "
            f"{', '.join(cov)} of the company Scope 1 total",
            "`D1b_facility_panel.csv` × `data/raw/facility_panel.csv`"])

    pp = ROOT / "docs" / "price_process_test.csv"
    if pp.exists():
        t = pd.read_csv(pp)
        rows.append([
            "3 — TCaR levels",
            f"the unit-root test rejects in **0 of {len(t)}** series ({t.n_obs.min()}–"
            f"{t.n_obs.max()} observations), and its power against a mean-reverting "
            f"alternative with a 10-year half-life is "
            f"**{100 * t.power_vs_ou_hl10y.min():.1f}–{100 * t.power_vs_ou_hl10y.max():.1f}%** "
            f"at a nominal 5% size — the test cannot tell the two processes apart, so "
            f"\"untestable\" is measured, not rhetorical",
            "`docs/price_process_test.csv`"])

    gp = ROOT / "out" / "e5" / "gap.csv"
    if gp.exists():
        g = pd.read_csv(gp)
        piv = g.pivot_table(index=["company_id", "scenario"], columns="support",
                            values=["gap_cost_bnkrw", "gap_risk_bnkrw", "p50", "tcar"])
        diff = max(float(abs(piv[c]["current"] - piv[c]["none"]).max())
                   for c in ["gap_cost_bnkrw", "gap_risk_bnkrw", "p50", "tcar"])
        rows.append([
            "5 — the `support` axis",
            f"`gap.csv` holds {len(g)} rows for "
            f"**{g.groupby(['company_id', 'scenario']).ngroups} distinct gaps**, and the "
            f"largest disagreement between `support=current` and `support=none` on any "
            f"reported quantity is **{diff:g}**",
            "`out/e5/gap.csv`"])

    bm = ROOT / "out" / "m5" / "bundle_matrix.csv"
    if bm.exists():
        sys.path.insert(0, str(ROOT / "scripts"))
        from run_scenarios import REPLAN_REQUIRED
        b = pd.read_csv(bm)
        stale = sorted(set(b[~b.replanned].bundle) & REPLAN_REQUIRED)
        # F26: the empty case rendered as "**0** of the rest need re-planning ()" — write the
        # closed state as a sentence instead, and say what re-planning them turned up.
        top2 = b.sort_values("d_tcar_pct", ascending=False).iloc[0]
        m2 = b.loc[b.d_m2_pct.idxmax()]
        note = (
            f"**{int(b.replanned.sum())} of {len(b)}** bundles were re-planned; "
            + (f"**{len(stale)}** of the rest need re-planning to be read at all "
               f"({', '.join('`' + s + '`' for s in stale)}), so their Δ② / Δ③ are "
               f"unmeasured rather than flat (§4.3)"
               if stale else
               f"every axis that E2 reads has now been solved through it, and none of the "
               f"remaining bundles reaches E2. Re-planning changed the reading: the largest "
               f"movers are `{top2.bundle}` on ③ ({top2.d_tcar_pct:.1f}%) and `{m2.bundle}` "
               f"on ② ({m2.d_m2_pct:.1f}%), both of which read 0.0% while they were only "
               f"being re-priced (§4.3)"))
        rows.append([
            "6 — the plan-selection channel", note,
            "`out/m5/bundle_matrix.csv` × `scripts/run_scenarios.py::REPLAN_REQUIRED`"])

    fpp = ROOT / "out" / "e5" / "frontier_points.csv"
    if fpp.exists() and gp.exists():
        f = pd.read_csv(fpp).query("support == 'none'")
        g1 = pd.read_csv(gp).query("support == 'none'")
        cc = cr = 0
        over = []
        for r in g1.itertuples():
            d = f[(f.company_id == r.company_id) & (f.scenario == r.scenario)]
            fr, p = d[d.on_frontier], d[d.is_disclosed].iloc[0]
            if p.tcar > fr.tcar.max():
                cc += 1
                over.append(p.tcar / fr.tcar.max())
            cr += int(p.p50 > fr.p50.max())
        rows.append([
            "9 — the gaps are lower bounds",
            f"**{cc} of {len(g1)}** cost legs and **{cr} of {len(g1)}** risk legs are "
            f"clamped to a frontier endpoint, the disclosed plan sitting "
            f"{_x(min(over))}–{_x(max(over))} above the tail risk of the riskiest plan on "
            f"its own frontier. At the top of that range the frontier is not a "
            f"neighbourhood of the disclosed plan at all",
            "`out/e5/frontier_points.csv` × `out/e5/gap.csv`"])

    # which claims the table does *not* cover is read off §8 itself — hand-typing the
    # list left it naming three claims after a fourth had been added (F29).
    sec8 = (GUIDE.read_text(encoding="utf-8")
            .split("## 8. What we do not claim")[-1].split("<!-- GEN:limits -->")[0])
    stated = [int(n) for n in re.findall(r"^(\d+)\. ", sec8, re.M)]
    covered = {int(r[0].split(" —")[0]) for r in rows}
    rest = [str(n) for n in stated if n not in covered]
    if not rest:
        return _md(rows, ["Claim", "The size of it", "Recomputed from"]) + (
            f"\n\nEvery one of the {len(stated)} claims above is sized here.")
    tail = (rest[0] if len(rest) == 1
            else ", ".join(rest[:-1]) + f" and {rest[-1]}")
    return _md(rows, ["Claim", "The size of it", "Recomputed from"]) + (
        f"\n\n{'Claim' if len(rest) == 1 else 'Claims'} {tail} carry their size in the "
        "sentence itself. The table is the ones that did not.")


def gen_crossmodel_band():
    """The one level-space check the cross-model layer actually supports — and its limits.

    F22: §7 said the layer supports "same direction, not that their levels agree" and
    stopped there. `docs/cross_model_check.md` §3 has carried a level-space result since
    C16 — FIN's per-tonne cost against the range EFF's feasible candidates span — and the
    guide never carried it. It is a weak test and worth stating as one: the band's lower
    edge *is* EFF's own pick (its selection rule is min gross cost), so the check can only
    fail from above. And it is tree-dependent: F20 read the range from an EFF copy that is
    not committed here, and on the committed copy NSC falls outside.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from cross_model_check import (CAND, PAIR, cost_band,  # noqa: E402
                                   eff_divergence, eff_file)
    m = pd.read_csv(ROOT / "out" / "e5" / "metrics_company.csv").query(
        "scenario=='NZ15' and support=='none'").set_index("company_id")
    src = eff_file(CAND)
    if src is None:
        return "_EFF candidate metrics not found — cannot rebuild the cross-model band._"
    band = cost_band(src)
    div = eff_divergence(CAND)
    alt = cost_band(div[1]) if div is not None else None

    rows, verdicts = [], []
    for fin, eff in PAIR.items():
        if fin not in m.index or eff not in band.index:
            continue
        ours = float(m.loc[fin, "cost_per_tco2_thkrw"])
        lo, hi = float(band.loc[eff, "min"]), float(band.loc[eff, "max"])
        pos = 100 * (ours - lo) / (hi - lo)
        inside = lo <= ours <= hi
        cell = "**inside**" if inside else "**above**"
        if alt is not None and eff in alt.index:
            a_lo, a_hi = float(alt.loc[eff, "min"]), float(alt.loc[eff, "max"])
            other = a_lo <= ours <= a_hi
            cell += f" — {'inside' if other else 'above'} on the uncommitted copy"
            if other != inside:
                cell = cell.replace("uncommitted copy", "uncommitted copy, **verdict flips**")
        rows.append([f"**{fin}**", f"{ours:,.0f}", f"{lo:,.1f}", f"{hi:,.1f}",
                     f"{hi / lo:.1f}×", f"{ours / lo:.1f}×", f"{pos:.0f}%", cell])
        verdicts.append((fin, inside))
    if not rows:
        return "_No company pairs available for the cross-model band._"
    tbl = _md(rows, ["Firm", "Ours ② (thousand KRW/tCO₂)", "EFF feasible min", "EFF feasible max",
                     "Band width", "Ours ÷ EFF's pick", "Position in band", "Verdict"])
    ins = [f for f, i in verdicts if i]
    return tbl + (
        f"\n\nEFF's selection rule is minimum gross cost, so **the band's lower edge is EFF's "
        f"own answer** and ours cannot fall below it by construction — this check can only fail "
        f"from above, and a band {rows[0][4]} wide is a loose bound to be inside. What it "
        f"supports is narrow: our plans cost more per tonne than the cheapest plan EFF calls "
        f"feasible, and for {', '.join(ins) if ins else 'no firm'} still less than the most "
        f"expensive one. "
        + (f"It is also **not tree-invariant**: EFF exists as a copy committed here and a "
           f"separate repository, the two differ in `{CAND}`, and the verdict above is computed "
           f"from the committed copy so that it is reproducible from this repository alone. "
           f"Until F20 this comparison was read from the uncommitted copy, where the second "
           f"firm reads inside. The band is the weakest link in this layer, not the strongest."
           if div is not None else
           "Both EFF trees agree on the candidate file, so the verdict is tree-invariant."))


def gen_criterion_swap():
    """The robustness axis that changes what the model calls optimal.

    F23: §6.2 listed the perturbations the ranking survives — discount rate, price
    process, shock normalisation, scenario bundles — and left out the one that swaps
    the objective itself. `docs/robustness_structural.md` has carried it since I2: pick
    each firm's plan by minimising P90 instead of P50 and the ordering is unchanged,
    but the tail is nothing like the same thickness in the two sectors. The guide cited
    that document once (§1, claim P2) and never carried its table.

    Recomputed here from `out/e5/frontier_points.csv` through the same `pick` the
    document uses, so the two cannot drift apart.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from robustness_structural import CONAME, SECTOR, pick  # noqa: E402

    fp = ROOT / "out" / "e5" / "frontier_points.csv"
    if not fp.exists():
        return "_out/e5/frontier_points.csv not available — cannot re-select on P90._"
    fr = pd.read_csv(fp).query("scenario=='NZ15' and support=='none'")
    g = fr[~fr.is_disclosed & fr.budget_ok]
    if g.empty:
        return "_No budget-feasible plan in out/e5 — cannot re-select on P90._"

    p50, p90 = pick(g, "p50"), pick(g, "p90")
    order = lambda d: [c for c in d.sort_values("lcoa").index]  # noqa: E731
    EN = {"철강": "Steel", "석화": "Petrochemicals"}

    rows, mult = [], {}
    for c in order(p50):
        if c not in p90.index:
            continue
        a, b = float(p50.loc[c, "lcoa"]), float(p90.loc[c, "lcoa"])
        mult[c] = b / a
        rows.append([f"**{CONAME[c]}**", EN.get(SECTOR[c], SECTOR[c]),
                     f"{a:,.0f}", f"{b:,.0f}", f"**×{b / a:.1f}**"])
    if not rows:
        return "_No firm carries both a P50-optimal and a P90-optimal plan._"

    tbl = _md(rows, ["Firm", "Sector", "② risk-neutral (minimise P50)",
                     "② risk-averse (minimise P90)", "Tail multiple"])
    band = lambda k: (min(v for c, v in mult.items() if SECTOR[c] == k),  # noqa: E731
                      max(v for c, v in mult.items() if SECTOR[c] == k))
    st, pc = band("철강"), band("석화")
    same = order(p50) == order(p90)
    verdict = ("**unchanged** — the criterion swap does not change which firm the model "
               "points at" if same else
               "**reversed** — which firm looks cheap depends on the risk attitude")
    lo50 = min(float(p50.loc[c, "lcoa"]) for c in mult)
    hi50 = max(float(p50.loc[c, "lcoa"]) for c in mult)
    lo90 = min(float(p90.loc[c, "lcoa"]) for c in mult)
    hi90 = max(float(p90.loc[c, "lcoa"]) for c in mult)
    return tbl + (
        f"\n\nThe ordering is {verdict}. What the swap does change is how far the bad "
        f"case sits from the expected one, and that is **sector-specific**: steel "
        f"×{st[0]:.1f}–{st[1]:.1f} against petrochemicals ×{pc[0]:.1f}–{pc[1]:.1f}. "
        f"Cheapest to dearest firm spans {hi50 / lo50:.1f}× on expected cost and "
        f"{hi90 / lo90:.1f}× on the bad case. The petrochemical problem is the "
        f"**variance** of the cost, not its level.")


def gen_gate_checks():
    """How many checks the gate runs, and how many can fail it.

    F23: this count was hand-written as "Eight checks … Five of the eight are hard",
    and F22 added a ninth (`sidecars`) without the guide following. Reading it off
    `gate.CHECKS`/`gate.HARD` means the next check added cannot leave the guide behind.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from gate import CHECKS, HARD  # noqa: E402

    keys = [k for k, _, _ in CHECKS]
    hard = [k for k in keys if k in HARD]
    soft = [k for k in keys if k not in HARD]
    fmt = lambda ks: ", ".join(f"`{k}`" for k in ks)  # noqa: E731
    return (f"**{len(CHECKS)} checks.** {len(hard)} are hard — a non-zero exit: "
            f"{fmt(hard)}. The other {len(soft)} report and do not block: {fmt(soft)}.")


def gen_frontier_degeneracy():
    """The ε-constraint counts behind §6.3, read off `out/m8/summary.csv`.

    F24: these were hand-written (4 of 32, one bundle, 7 of 8, 25 of 32). They were
    correct, but `out/m8` is one of the stale side-diagnostics the gate's `sidecars`
    check names — so the re-run that closes that warning would have falsified four
    numbers in the guide with nothing to catch it. The guide already told the reader
    which columns they come from; now it reads them.
    """
    p = ROOT / "out" / "m8" / "summary.csv"
    if not p.exists():
        return "_`out/m8/summary.csv` not available._"
    m = pd.read_csv(p)
    tried, nb = int(m.caps_tried.sum()), len(m)
    head, l2 = int(m.nondominated_headline.sum()), int(m.nondominated_l2.sum())
    hb = m[m.nondominated_headline > 0]
    l2b = int((m.nondominated_l2 > 0).sum())
    where = (" and those "
             f"{head} are all in **one** bundle ({hb.iloc[0].company_id} under "
             f"{hb.iloc[0].scenario}). In the other **{nb - len(hb)} of {nb}** bundles not a "
             "single forced schedule survives, so the thinness is not a near-miss."
             if len(hb) == 1 else
             f" and they are spread over {len(hb)} of the {nb} bundles.")
    return (f"Forcing technology schedules with an ε-constraint on cumulative emissions — an axis "
            f"contracts cannot buy — shows that **all {tried} caps are feasible and every one "
            f"yields a new schedule**: the degrees of freedom exist. But under the headline risk "
            f"convention only **{head}** remain non-dominated in (P50, TCaR),{where}\n\n"
            f"The mechanism is that abatement moves exposure *out of* carbon, which is "
            f"deterministic, and *into* electricity, hydrogen and construction cost, which are "
            f"stochastic. So **abating increases TCaR**. Under the alternative convention where "
            f"carbon price is itself stochastic, {l2} of the same {tried} become non-dominated and "
            f"the technology axis returns in {l2b} of {nb} bundles. The frontier's thinness is a "
            f"property of the risk convention, not of the candidate generator.")


def gen_capacity_basis():
    """How many capacity figures are estimated, against how many are published.

    F24: this was hand-written as "16 of the 23 rows, all blast furnaces", which
    reads as *every* blast furnace while A-13 in §4.1 counts 17 of them. The gap
    is the calibration anchor: the one blast furnace with a published capacity is
    the point the multiplier was fitted on, so nothing here is out-of-sample.
    """
    p = prepared() / "D1a_facility_static.csv"
    if not p.exists():
        return "_D1a not available._"
    d = pd.read_csv(p)
    est = d.capacity_unit.astype(str).str.contains("추정")
    bf = d.unit_type.astype(str).eq("BF")
    anchors = d[bf & ~est]
    names = ", ".join(f"`{t.facility_id}`" for t in anchors.itertuples()) or "none"
    return (f"{int(est.sum())} of the {len(d)} rows are estimated and all of them are blast "
            f"furnaces — but that is {int((est & bf).sum())} of the {int(bf.sum())} blast "
            f"furnaces, not all of them. The {len(anchors)} blast furnace left out ({names}) is "
            f"the one whose capacity is published, and it is also the single point the multiplier "
            f"was calibrated on. **No estimated row can be checked against a published figure**, "
            f"because the only blast furnace that carries one was spent fixing the constant. The "
            f"remaining {int((~est & ~bf).sum())} published rows are not blast furnaces and are "
            f"stated on other bases (§3.0), so they cannot check it either.")


def _ledger_sections():
    """Which section each A-id is treated in, read off the guide's own tables.

    §4.4 used to name those sets in prose. §4.1 grew from five rows to eight over the
    cycles and the prose did not: A-05 and A-07 ended up in no index, and A-19 was
    filed under §4.2 where it has never been. The tables are the fact, so the index
    is derived from them. Only `| **A-xx** |` row starts count, which is why the
    sentence this produces — bold ids in running text — cannot feed itself.

    The minor ids are the exception: no table carries them, so they are read from
    §4.4's *first* paragraph, the one that names and explains them. Reading them
    instead as `ledger - tabled` would be the same bug in a new place — a new
    METHODOLOGY id nobody wrote about would be absorbed into "the ones above" and
    the map would claim to place an id the guide never mentions.
    """
    text = GUIDE.read_text(encoding="utf-8")
    sec, tables, in_three = "0", {}, set()
    for line in text.split("\n"):
        h = re.match(r"^#{2,4}\s+([0-9]+(?:\.[0-9]+)?)\b", line)
        if h:
            sec = h.group(1)
        row = re.match(r"^\|\s*\*\*(A-\d{2})\*\*\s*\|", line)
        if row:
            tables.setdefault(sec, set()).add(row.group(1))
        elif sec.startswith("3"):
            in_three |= set(re.findall(r"\bA-\d{2}\b", line))
    para = re.search(r"^### 4\.4[^\n]*\n\n(.*?)\n\n", text, re.S | re.M)
    minor = set(re.findall(r"\*\*(A-\d{2})\*\*", para.group(1))) if para else set()
    ledger = set(re.findall(r"\bA-\d{2}\b", (ROOT / "METHODOLOGY.md").read_text(encoding="utf-8")))
    return tables, in_three, minor, ledger


def _ids(s):
    return ", ".join(f"**{a}**" for a in sorted(s))


def gen_ledger_map():
    tables, in_three, minor, ledger = _ledger_sections()
    tabled = {a for s in tables.values() for a in s}
    placed = tabled | minor
    # §4 claims every ledger id appears somewhere in the guide. These two say when it stops being true.
    missing = ledger - placed
    extra = placed - ledger
    out = [f"{_ids(tables.get('4.1', set()))} are treated in §4.1; "
           f"{_ids(tables.get('4.2', set()))} in §4.2; "
           f"{_ids(minor)} are the {len(minor)} named in the paragraph above."]
    out.append(f"\n\nThat places {len(placed & ledger)} of the ledger's {len(ledger)} identifiers. "
               f"Dataset-level consequences of {_ids(in_three & ledger)} additionally appear in §3 — "
               f"an assumption is indexed here by where it is *stated*, not by everywhere it bites.")
    if extra:
        out.append(f"\n\n**{_ids(extra)} appear in this guide but not in the METHODOLOGY ledger.**")
    if missing:
        out.append(f"\n\n**{_ids(missing)} are in the ledger and in no index here** — §4's claim that "
                   f"every identifier appears somewhere in this guide is currently false.")
    return "".join(out)


BLOCKS = {
    "stamp": gen_stamp,
    "ledger_map": gen_ledger_map,
    "capacity_basis": gen_capacity_basis,
    "frontier_degeneracy": gen_frontier_degeneracy,
    "criterion_swap": gen_criterion_swap,
    "gate_checks": gen_gate_checks,
    "crossmodel_band": gen_crossmodel_band,
    "limits": gen_limits,
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
    "d3_excluded": gen_d3_excluded,
    "d3b_bands": gen_d3b_bands,
    "price_series": gen_price_series,
    "d6_coverage": gen_d6_coverage,
    "d7_enforcement": gen_d7_enforcement,
    "package": gen_package,
    "tier_distribution": gen_tier_distribution,
    "config": gen_config,
    "headline": gen_headline,
    "band_vs_convention": gen_band_vs_convention,
    "seed_cv": gen_seed_cv,
    "diagnostic_drift": gen_diagnostic_drift,
    "reline_anchors": gen_reline_anchors,
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
