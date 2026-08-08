"""E1 — extract constraints from GCAM/NGFS scenario data (REDESIGN_SPEC §3 E1).

Downloads nothing and allocates nothing: filters the sector carbon budget and
central price/availability paths, interpolates 5-yearly budgets to annual, and
scales the sector budget to each company boundary by the intensity-ratio rule
(company budget_t = company base emissions x sector budget_t / sector base).
Facility-level allocation is deliberately NOT done here — that is E2's job.

Outputs: out/e1/constraints.csv, out/e1/price_paths_central.csv, out/e1/e1_check.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .schemas import load_input

COMPANY_REGION = {"POSCO": "Korea", "LOTTE": "Korea", "NSC": "Japan", "MCI": "Japan"}


def run(cfg: C.Config) -> dict[str, pd.DataFrame]:
    ddir = C.data_dir(cfg)
    odir = C.out_dir(cfg, "e1")
    years = np.arange(cfg.years.start, cfg.years.end + 1)

    d1a = load_input(ddir, "D1a_facility_static")
    d1b = load_input(ddir, "D1b_facility_panel")
    d2a = load_input(ddir, "D2a_scenario_budget")
    d2b = load_input(ddir, "D2b_scenario_prices")

    # company base emissions (mean of last 3 panel years, scope 1) — per-company
    # year coverage: sum per company-year first, then mean, so a company with a
    # shorter panel is not divided by another company's year count
    base_year = int(d1b.year.max())
    recent = d1b[d1b.year >= base_year - 2]
    fac2co = d1a.set_index("facility_id").company_id
    fac2sec = d1a.set_index("facility_id").sector
    recent = recent.assign(company_id=recent.facility_id.map(fac2co),
                           sector=recent.facility_id.map(fac2sec))
    multi = d1a.groupby("company_id").sector.nunique()
    if (multi > 1).any():
        raise RuntimeError(f"multi-sector companies not supported: {list(multi[multi > 1].index)}")
    co_base = (recent.groupby(["company_id", "sector", "year"]).emissions_s1.sum()
               .groupby(level=[0, 1]).mean())

    # sector budget: interpolate to annual per scenario x region x sector
    rows = []
    for (scen, region, sector), g in d2a.groupby(["scenario", "region", "sector"]):
        g = g.sort_values("year")
        annual = np.interp(years, g.year, g.carbon_budget)
        for y, b in zip(years, annual):
            rows.append([scen, region, sector, int(y), float(b)])
    sector_budget = pd.DataFrame(rows, columns=["scenario", "region", "sector", "year", "sector_budget_mt"])

    # company budget by intensity ratio (budget_scaling: intensity_ratio)
    rows = []
    for (company, sector), base_emis in co_base.items():
        region = COMPANY_REGION.get(company)
        if region is None:
            raise RuntimeError(f"unknown company '{company}' — add to COMPANY_REGION in e1_constraints.py")
        sb = sector_budget[(sector_budget.region == region) & (sector_budget.sector == sector)]
        for scen, g in sb.groupby("scenario"):
            g = g.sort_values("year")
            ratio = g.sector_budget_mt / g.sector_budget_mt.iloc[0]
            for y, r, s in zip(g.year, ratio, g.sector_budget_mt):
                rows.append([scen, company, sector, region, int(y), float(base_emis * r), float(s)])
    constraints = pd.DataFrame(rows, columns=[
        "scenario", "company_id", "sector", "region", "year",
        "company_budget_tco2", "sector_budget_mt"])

    # central price paths, annual (already annual in D2b; interpolate defensively)
    rows = []
    price_vars = [v for v in d2b.variable.unique() if not str(v).startswith("tech_avail_")]
    for (scen, region, var), g in d2b[d2b.variable.isin(price_vars)].groupby(["scenario", "region", "variable"]):
        g = g.sort_values("year")
        vals = np.interp(years, g.year, g.value)
        unit = g.unit.iloc[0]
        rows += [[scen, region, var, int(y), float(v), unit] for y, v in zip(years, vals)]
    prices = pd.DataFrame(rows, columns=["scenario", "region", "variable", "year", "value", "unit"])

    # tech availability: EVERY tech with a tech_avail_* path gets a row; a tech
    # never available in a scenario gets sentinel 9999 (absence must not silently
    # fall back to the D3 default in E2)
    avail = (d2b[d2b.variable.str.startswith("tech_avail_")]
             .assign(tech_id=lambda x: x.variable.str.replace("tech_avail_", "", regex=False)))
    first = avail[avail.value > 0].groupby(["scenario", "region", "tech_id"]).year.min()
    all_keys = avail.groupby(["scenario", "region", "tech_id"]).size().index
    avail_first = (first.reindex(all_keys).fillna(9999).astype(int)
                   .rename("avail_year_scenario").reset_index())

    # residual check: annual interpolation must preserve 5-yearly anchor values
    chk = sector_budget.merge(d2a, on=["scenario", "region", "sector", "year"])
    chk["residual"] = (chk.sector_budget_mt - chk.carbon_budget).abs()
    check = chk.groupby(["scenario", "region", "sector"]).residual.max().reset_index()

    constraints.to_csv(odir / "constraints.csv", index=False)
    prices.to_csv(odir / "price_paths_central.csv", index=False)
    avail_first.to_csv(odir / "tech_availability.csv", index=False)
    check.to_csv(odir / "e1_check.csv", index=False)
    assert check.residual.max() < 1e-9, "interpolation broke anchor-year budgets"
    return {"constraints": constraints, "prices": prices, "avail": avail_first}


if __name__ == "__main__":
    run(C.load())
    print("e1 ok")
