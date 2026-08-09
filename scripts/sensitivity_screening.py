"""F2 — one-at-a-time sensitivity screening on the headline metrics (AUTOPILOT v2 §4-F2).

Holds the E2 plan set fixed (perturbing it would require a 7-minute MILP re-solve per
run) and re-evaluates E4/E5 economics under each perturbation. This measures
"given the menu of plans, which parameter moves the answer" — the plan-selection
channel is covered separately by the full re-runs in I1/I2.

Perturbations are ±30% by default, or the [low, high] range recorded in the
parameter inventory where one exists.

    .venv/bin/python scripts/sensitivity_screening.py [--sims 4000]
Writes outputs/sensitivity_screening.csv + prints the top-10 ranking with tiers.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import replace

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.e1_constraints import COMPANY_REGION  # noqa: E402
from cap.e2_milp import _prep_company  # noqa: E402
from cap.e3_prices import load_shocks  # noqa: E402
from cap.e4_revalue import _central_px  # noqa: E402
from cap.plancost import (auction_share, build_profile, simulate_cost,  # noqa: E402
                          support_params)
from cap.schemas import load_input  # noqa: E402

SCEN = "NZ15"
CONTRACTS = [(0.0, 0), (0.5, 0), (1.0, 0), (1.0, 1)]   # coarse frontier probe


def headline(cfg, fac, d3, d5, prices, plans, shocks, px_scale=None, tier_note=""):
    """Return per-company (p50, tcar, lcoa) for the cost-min plan + frontier width."""
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc = (1 + cfg.discount_rate) ** -(years - years[0])
    auc = auction_share(years, cfg)
    sp = support_params(d5, "none", years)
    out = {}
    for company, plist in plans.items():
        px = _central_px(prices, COMPANY_REGION[company], SCEN, years, cfg, None)
        if px_scale:
            px = {k: (v * px_scale.get(k, 1.0)) for k, v in px.items()}
        base = build_profile(_empty(company), fac, d3, px, years, cfg)
        bs = simulate_cost(base, px, shocks, sp, cfg)
        cb = float((base.emissions * px["co2"] * auc / 1000.0 * disc).sum() * 1e-6)
        pts = []
        for pdf in plist:
            prof0 = build_profile(pdf, fac, d3, px, years, cfg)
            dc = float((prof0.emissions * px["co2"] * auc / 1000.0 * disc).sum() * 1e-6) - cb
            abated = float(((base.emissions - prof0.emissions) * disc).sum())
            for ppa, epc in CONTRACTS:
                s = simulate_cost(replace(prof0, ppa=ppa, epc=epc), px, shocks, sp, cfg)
                inc = s - bs
                p50 = float(np.median(inc)) - dc
                p90 = float(np.percentile(inc, 90)) - dc
                pts.append((p50, p90 - p50, abated))
        pts.sort()
        p50, tcar, abated = pts[0]
        lcoa = p50 * 1e6 / abated if abated > 0 else np.nan
        # frontier width = spread of non-dominated (p50, tcar) pairs
        best_t, front = np.inf, 0
        for c, t, _ in sorted(pts):
            if t < best_t - 1e-9:
                best_t, front = t, front + 1
        out[company] = dict(p50=p50, tcar=tcar, lcoa=lcoa, front=front)
    return out


def _empty(company):
    return pd.DataFrame([{"facility_id": None, "tech_id": None, "adopt_year": None,
                          "op_year": None, "company_id": company, "scenario": "-",
                          "ppa_share": 0.0, "epc": 0, "ccfd": 0}])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=4000)
    a = ap.parse_args()
    cfg = C.load(data_dir="data/prepared")
    cfg["simulation"] = dict(cfg["simulation"], n_sims=a.sims)
    ddir = C.data_dir(cfg)
    fac, d3, cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    idx = pd.read_csv(C.out_dir(cfg, "e2") / "plan_index.csv")
    idx = idx[(idx.scenario == SCEN) & (~idx.is_disclosed)]
    plans = {}
    for co, g in idx.groupby("company_id"):
        seen, lst = set(), []
        for pid in g.plan_id:
            pdf = pd.read_csv(C.out_dir(cfg, "e2") / "plans" / f"plan_{pid}.csv")
            key = tuple(sorted((r.facility_id, r.tech_id, int(r.adopt_year))
                               for r in pdf.itertuples() if pd.notna(r.tech_id)))
            if key not in seen:
                seen.add(key)
                lst.append(pdf)
        plans[co] = lst
    shocks = {k: v[:a.sims] for k, v in load_shocks(cfg).items()}

    base = headline(cfg, fac, d3, d5, prices, plans, shocks)
    print("=== 기준선 (NZ15, 계획 고정)")
    for co, v in base.items():
        print(f"  {co:6} P50 {v['p50']:9,.0f}bn  TCaR {v['tcar']:9,.0f}bn  "
              f"LCOA {v['lcoa']:7,.0f}천원/tCO2  경계 {v['front']}점")

    # ---- perturbation catalogue: (id, tier, kind, apply_fn)
    def scale_df(df, col, f, mask=None):
        d = df.copy()
        m = mask if mask is not None else pd.Series(True, index=d.index)
        d.loc[m, col] = d.loc[m, col] * f
        return d

    steel = d3.sector == "steel"
    tests = []
    for f, tag in [(0.7, "low"), (1.3, "high")]:
        tests += [
            # price paths (T3-T5 depending on series)
            (f"price.elec×{tag}", "T4", dict(px={"elec": f})),
            (f"price.re×{tag}", "T4", dict(px={"re": f})),
            (f"price.h2×{tag}", "T5", dict(px={"h2": f})),
            (f"price.co2×{tag}", "T5", dict(px={"co2": f})),
            (f"price.coal×{tag}", "T3", dict(px={"coal": f})),
            (f"price.gas×{tag}", "T3", dict(px={"gas": f})),
            # technology parameters
            (f"tech.capex×{tag}", "T3", dict(d3=("capex_unit", f, None))),
            (f"tech.opex_fixed×{tag}", "T3", dict(d3=("opex_fixed", f, None))),
            (f"tech.opex_var×{tag}", "T4", dict(d3=("opex_var", f, None))),
            (f"tech.elec_intensity×{tag}", "T3", dict(d3=("elec_intensity", f, None))),
            (f"tech.h2_intensity×{tag}", "T3", dict(d3=("h2_intensity", f, None))),
            (f"tech.emission_factor×{tag}", "T3", dict(d3=("emission_factor", f, None))),
            (f"tech.steel_capex×{tag}", "T3", dict(d3=("capex_unit", f, steel))),
            # facility parameters
            (f"fac.capacity×{tag}", "T2/T5", dict(fac=("capacity", f))),
            (f"fac.ef_inc×{tag}", "T5", dict(fac=("ef_inc", f))),
            (f"fac.elec_int_inc×{tag}", "T5", dict(fac=("elec_int_inc", f))),
            (f"fac.coal_int_inc×{tag}", "T5", dict(fac=("coal_int_inc", f))),
            (f"fac.margin×{tag}", "T4", dict(fac=("margin_kthou_t", f))),
            # model choices
            (f"cfg.discount×{tag}", "T5", dict(cfg=("discount_rate", f))),
            (f"cfg.auction_share×{tag}", "T1/T5", dict(auction=f)),
            (f"cfg.ppa_premium×{tag}", "T5", dict(cfg2=("contracts", "ppa_premium_pct", f))),
            (f"cfg.epc_premium×{tag}", "T5", dict(cfg2=("contracts", "epc_premium_pct", f))),
            # stochastic calibration
            (f"vol.elec×{tag}", "T3", dict(vol=("elec", f))),
            (f"vol.h2×{tag}", "T5", dict(vol=("h2", f))),
            (f"vol.capex×{tag}", "T5", dict(vol=("capex", f))),
        ]

    rows = []
    for name, tier, spec in tests:
        c2, f2, d32, sh2, pxs = cfg, fac, d3, shocks, None
        if "px" in spec:
            pxs = spec["px"]
        if "d3" in spec:
            col, f, mask = spec["d3"]
            d32 = scale_df(d3, col, f, mask)
        if "fac" in spec:
            col, f = spec["fac"]
            f2 = scale_df(fac, col, f)
        if "cfg" in spec:
            k, f = spec["cfg"]
            c2 = C.Config({**cfg, k: cfg[k] * f})
        if "cfg2" in spec:
            grp, k, f = spec["cfg2"]
            c2 = C.Config({**cfg, grp: {**cfg[grp], k: cfg[grp][k] * f}})
        if "auction" in spec:
            f = spec["auction"]
            c2 = C.Config({**cfg, "carbon_auction_share":
                           {y: min(1.0, v * f) for y, v in cfg["carbon_auction_share"].items()}})
        if "vol" in spec:
            fkey, f = spec["vol"]
            sh2 = {k: (np.exp(np.log(v) * f) if k == fkey or (fkey == "h2" and k == "h2") else v)
                   for k, v in shocks.items()}
        try:
            h = headline(c2, f2, d32, d5, prices, plans, sh2, px_scale=pxs)
        except Exception as e:                      # noqa: BLE001 — record, don't crash the sweep
            print(f"  [skip] {name}: {e}")
            continue
        for co in base:
            b, v = base[co], h[co]
            rows.append(dict(param=name, tier=tier, company=co,
                             d_lcoa_pct=100 * (v["lcoa"] - b["lcoa"]) / abs(b["lcoa"]) if b["lcoa"] else np.nan,
                             d_p50_pct=100 * (v["p50"] - b["p50"]) / abs(b["p50"]) if b["p50"] else np.nan,
                             d_tcar_pct=100 * (v["tcar"] - b["tcar"]) / abs(b["tcar"]) if b["tcar"] else np.nan,
                             d_front=v["front"] - b["front"]))

    df = pd.DataFrame(rows)
    outdir = ROOT / "outputs"
    outdir.mkdir(exist_ok=True)
    df.to_csv(outdir / "sensitivity_screening.csv", index=False)

    # rank by max |ΔLCOA| and |ΔTCaR| across companies, averaged over the ± pair
    df["base_param"] = df.param.str.replace(r"×(low|high)$", "", regex=True)
    rank = (df.groupby(["base_param", "tier"])[["d_lcoa_pct", "d_tcar_pct", "d_p50_pct"]]
            .apply(lambda g: g.abs().max()).reset_index()
            .assign(score=lambda x: x[["d_lcoa_pct", "d_tcar_pct"]].max(axis=1))
            .sort_values("score", ascending=False))
    rank.to_csv(outdir / "sensitivity_ranking.csv", index=False)
    print("\n=== 상위 12 (±30% 최대 영향, 4사 중 최대치 %)")
    print(rank.head(12).round(1).to_string(index=False))
    low = rank.head(10)[rank.head(10).tier.str.contains("T4|T5")]
    print(f"\n=== 상위 10 중 T4/T5(증거 취약): {len(low)}건 → 데이터 승급 대상")
    print(low[["base_param", "tier", "score"]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
