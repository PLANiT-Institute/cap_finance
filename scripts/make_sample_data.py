"""Generate synthetic sample CSVs in data/sample/ matching the template schemas.

Purpose: prove the E1–E5 pipeline end-to-end before real data arrives.
Values are order-of-magnitude plausible but FABRICATED — never mix with data/raw.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)

SRC = "SAMPLE_SYNTH"

# ---------------- D1a facility static ----------------
facs = [
    # facility_id, company, sector, site, unit_type, name, capacity(t/yr), reline, cycle, next
    ("POSCO_POH_BF2", "POSCO", "steel", "Pohang", "BF", "BF No.2", 5_300_000, 2015, 17, 2032),
    ("POSCO_POH_BF3", "POSCO", "steel", "Pohang", "BF", "BF No.3", 4_600_000, 2013, 17, 2030),
    ("POSCO_GWY_BF1", "POSCO", "steel", "Gwangyang", "BF", "BF No.1", 5_500_000, 2019, 17, 2036),
    ("POSCO_GWY_BF4", "POSCO", "steel", "Gwangyang", "BF", "BF No.4", 5_300_000, 2014, 17, 2031),
    ("NSC_KIM_BF3", "NSC", "steel", "Kimitsu", "BF", "BF No.3", 4_800_000, 2016, 18, 2034),
    ("NSC_KIM_BF4", "NSC", "steel", "Kimitsu", "BF", "BF No.4", 5_200_000, 2012, 18, 2030),
    ("NSC_NGO_BF1", "NSC", "steel", "Nagoya", "BF", "BF No.1", 4_500_000, 2018, 18, 2036),
    ("LOTTE_YEO_NCC", "LOTTE", "petchem", "Yeosu", "NCC", "NCC No.1", 1_200_000, 2018, 8, 2026),
    ("LOTTE_DAE_NCC", "LOTTE", "petchem", "Daesan", "NCC", "NCC", 1_100_000, 2021, 8, 2029),
    ("MCI_ICH_NCC", "MCI", "petchem", "Ichihara", "NCC", "Cracker", 600_000, 2020, 8, 2028),
    ("MCI_OSK_NCC", "MCI", "petchem", "Osaka", "NCC", "Cracker", 500_000, 2017, 8, 2025),
]
d1a = pd.DataFrame(facs, columns=[
    "facility_id", "company_id", "sector", "site", "unit_type", "unit_name",
    "capacity", "last_reline_year", "reinvest_cycle_yr", "next_reinvest_year"])
d1a["capacity_unit"] = np.where(d1a.sector == "steel", "t_hot_metal/yr", "t_ethylene/yr")
d1a["commissioning_year"] = d1a.last_reline_year - d1a.reinvest_cycle_yr * 2
d1a["status"] = "operating"
d1a["source_id"] = SRC
d1a = d1a[[c for c in [
    "facility_id", "company_id", "sector", "site", "unit_type", "unit_name",
    "capacity", "capacity_unit", "commissioning_year", "last_reline_year",
    "reinvest_cycle_yr", "next_reinvest_year", "status", "source_id"]]]

# ---------------- D1b facility panel ----------------
rows = []
for _, f in d1a.iterrows():
    for year in range(2020, 2025):
        util = rng.uniform(0.85, 0.98)
        prod = f.capacity * util
        if f.sector == "steel":
            ef1, ef2 = 1.9, 0.03  # tCO2/t hot metal scope1, scope2
            rows.append([f.facility_id, year, prod, prod * ef1, prod * ef2,
                         prod * 13.0, prod * 0.4, prod * 0.08, "", SRC])
        else:
            ef1, ef2 = 0.9, 0.15
            rows.append([f.facility_id, year, prod, prod * ef1, prod * ef2,
                         0.0, prod * 8.0, prod * 0.35, prod * 3.2, SRC])
d1b = pd.DataFrame(rows, columns=[
    "facility_id", "year", "production", "emissions_s1", "emissions_s2",
    "energy_coal", "energy_gas", "energy_elec", "energy_naphtha", "source_id"])

# ---------------- D2a scenario budget ----------------
rows = []
base = {"steel": {"Korea": 75.0, "Japan": 90.0}, "petchem": {"Korea": 25.0, "Japan": 20.0}}
decline = {"NZ15": 0.92, "B20": 0.96}  # per-5yr multiplier ~ pathway shape
for scen in ["NZ15", "B20"]:
    for region in ["Korea", "Japan"]:
        for sector in ["steel", "petchem"]:
            b = base[sector][region]
            for i, year in enumerate(range(2025, 2055, 5)):
                mult = decline[scen] ** (i * 5) * (1 - (0.10 if scen == "NZ15" else 0.05) * i)
                rows.append([scen, region, sector, year, max(b * mult, b * 0.05), "GCAM 6.0 NGFS P5", SRC])
d2a = pd.DataFrame(rows, columns=["scenario", "region", "sector", "year", "carbon_budget", "gcam_version", "source_id"])

# ---------------- D2b scenario prices ----------------
rows = []
central = {  # 2025 level, annual drift per scenario
    "elec_price": {"lvl": 130_000, "unit": "KRW/MWh", "drift": {"NZ15": 0.012, "B20": 0.006}},
    "h2_price": {"lvl": 6_500, "unit": "KRW/kgH2", "drift": {"NZ15": -0.035, "B20": -0.020}},
    "coal_price": {"lvl": 220_000, "unit": "KRW/t", "drift": {"NZ15": -0.01, "B20": 0.0}},
    "gas_price": {"lvl": 780_000, "unit": "KRW/t", "drift": {"NZ15": 0.0, "B20": 0.005}},
    "co2_price": {"lvl": 25_000, "unit": "KRW/tCO2", "drift": {"NZ15": 0.11, "B20": 0.07}},
}
for scen in ["NZ15", "B20"]:
    for region in ["Korea", "Japan"]:
        for var, p in central.items():
            for year in range(2025, 2051):
                v = p["lvl"] * (1 + p["drift"][scen]) ** (year - 2025)
                rows.append([scen, region, var, year, round(v, 1), p["unit"], SRC])
        for tech in ["steel_h2dri", "steel_eaf", "steel_ccus", "petchem_ecracker", "petchem_h2fuel", "petchem_bio"]:
            avail = {"steel_h2dri": 2030, "steel_eaf": 2025, "steel_ccus": 2032,
                     "petchem_ecracker": 2030, "petchem_h2fuel": 2028, "petchem_bio": 2026}[tech]
            for year in range(2025, 2051):
                rows.append([scen, region, f"tech_avail_{tech}", year, int(year >= avail), "0/1", SRC])
d2b = pd.DataFrame(rows, columns=["scenario", "region", "variable", "year", "value", "unit", "source_id"])

# ---------------- D3 tech options ----------------
techs = [
    # tech_id, sector, applies_to, capex(천원/t), opex_f, opex_v, elec MWh/t, h2 kg/t, ef tCO2/t, avail, build, life, capex_unc%
    ("steel_eaf", "steel", "BF", 550, 30, 90, 0.55, 0, 0.35, 2025, 2, 25, 20),
    ("steel_h2dri", "steel", "BF", 1_250, 45, 120, 3.5, 55, 0.15, 2030, 3, 25, 30),
    ("steel_ccus", "steel", "BF", 700, 55, 140, 0.35, 0, 0.55, 2032, 3, 20, 35),
    ("steel_eff", "steel", "BF", 120, 5, 10, 0.0, 0, 1.60, 2025, 1, 15, 15),
    ("petchem_ecracker", "petchem", "NCC", 900, 35, 60, 4.2, 0, 0.12, 2030, 3, 25, 30),
    ("petchem_h2fuel", "petchem", "NCC", 400, 20, 45, 0.3, 30, 0.30, 2028, 2, 20, 25),
    ("petchem_bio", "petchem", "NCC", 300, 15, 220, 0.1, 0, 0.45, 2026, 2, 20, 20),
    ("petchem_eff", "petchem", "NCC", 90, 4, 8, 0.0, 0, 0.75, 2025, 1, 15, 15),
]
d3 = pd.DataFrame(techs, columns=[
    "tech_id", "sector", "applies_to_unit", "capex_unit", "opex_fixed", "opex_var",
    "elec_intensity", "h2_intensity", "emission_factor", "avail_year",
    "build_years", "lifetime", "capex_uncertainty"])
d3["source_id"] = SRC

# ---------------- D4 price history (monthly 2015-01 .. 2025-12) ----------------
dates = pd.period_range("2015-01", "2025-12", freq="M").astype(str)
n = len(dates)


def series(start, vol_m, drift_m=0.0, corr_with=None, rho=0.0):
    z = rng.standard_normal(n)
    if corr_with is not None:
        z = rho * corr_with + np.sqrt(1 - rho**2) * z
    logp = np.log(start) + np.cumsum(drift_m + vol_m * z)
    return np.exp(logp), z


smp, z_smp = series(90.0, 0.06, 0.001)
tariff, _ = series(105.0, 0.02, 0.001, corr_with=z_smp, rho=0.6)
kau, _ = series(20_000, 0.08, 0.002)
lng, z_lng = series(650_000, 0.07, 0.0, corr_with=z_smp, rho=0.5)
coal, _ = series(180_000, 0.06, 0.0)
constr, z_c = series(100.0, 0.008, 0.002)
equip, _ = series(100.0, 0.012, 0.001, corr_with=z_c, rho=0.4)
usdkrw, _ = series(1150, 0.02, 0.0004)
cpi, _ = series(95.0, 0.002, 0.0015)

rows = []
for sid, vals, unit in [
    ("smp_krw_mwh", smp, "KRW/kWh"), ("indus_tariff", tariff, "KRW/kWh"),
    ("kau_krw", kau, "KRW/tCO2"), ("lng_import", lng, "KRW/t"),
    ("coal_import", coal, "KRW/t"), ("constr_cost_idx", constr, "index"),
    ("equip_import_idx", equip, "index"), ("usdkrw", usdkrw, "KRW/USD"),
    ("cpi", cpi, "2020=100"),
]:
    rows += [[d, sid, round(v, 3), unit, SRC] for d, v in zip(dates, vals)]
for i, year in enumerate(range(2015, 2026)):  # annual electrolyzer capex, declining
    rows.append([f"{year}-12", "electrolyzer_capex", round(2_600_000 * 0.93**i, 0), "KRW/kW", SRC])
d4 = pd.DataFrame(rows, columns=["date", "series_id", "value", "unit", "source_id"])

# ---------------- D5 policy support ----------------
d5 = pd.DataFrame([
    ["current", "subsidy_capex", "steel_h2dri", "subsidy_pct", 15, "%", 2027, 2035, SRC],
    ["current", "subsidy_capex", "petchem_ecracker", "subsidy_pct", 10, "%", 2027, 2035, SRC],
    ["current", "ccfd", "all", "strike_krw_tco2", 60_000, "KRW/tCO2", 2028, 2040, SRC],
], columns=["support_scenario", "instrument", "tech_id", "param_type", "value", "unit",
            "valid_from", "valid_to", "source_id"])

# ---------------- D6 company financials ----------------
rows = []
fin = {"POSCO": (38_000, 4_500, 4_800, 15_000, 8_000, 450, 7_000),
       "NSC": (60_000, 7_500, 5_500, 25_000, 15_000, 600, 10_000),
       "LOTTE": (18_000, 900, 1_800, 9_000, 6_000, 320, 3_000),
       "MCI": (14_000, 1_600, 1_200, 6_000, 4_000, 180, 2_000)}
for cid, (rev, ebitda, capex, debt, ndebt, intr, cash) in fin.items():
    for year in range(2020, 2025):
        g = 1.02 ** (year - 2022)
        rows.append([cid, year, rev * g, ebitda * g, capex * g, debt, ndebt, intr, cash, SRC])
d6 = pd.DataFrame(rows, columns=["company_id", "year", "revenue", "ebitda", "capex_total",
                                 "total_debt", "net_debt", "interest_expense", "cash", "source_id"])

# ---------------- D7 disclosed plan ----------------
d7 = pd.DataFrame([
    # POSCO: early tech commitment, no contracts — the '약속과 계약 사이 공백' case (설계서 §6)
    ["POSCO", "tech_commit", "POSCO_POH_BF2", "steel_h2dri", 2032, "", "mid", SRC, "HyREX 상용화 목표 (sample)"],
    ["POSCO", "tech_commit", "POSCO_POH_BF3", "steel_eaf", 2030, "", "high", SRC, "전기로 전환 (sample)"],
    ["NSC", "tech_commit", "NSC_KIM_BF4", "steel_eaf", 2030, "", "high", SRC, "EAF 전환 결정 (sample)"],
    ["NSC", "ppa", "", "", 2030, 40, "mid", SRC, "재생에너지 조달 40% (sample)"],
    ["LOTTE", "tech_commit", "LOTTE_YEO_NCC", "petchem_h2fuel", 2030, "", "mid", SRC, "수소 연료 전환 (sample)"],
    ["LOTTE", "ppa", "", "", 2028, 60, "high", SRC, "PPA 60% (sample)"],
    ["MCI", "tech_commit", "MCI_OSK_NCC", "petchem_ecracker", 2032, "", "low", SRC, "e-cracker 검토 (sample)"],
], columns=["company_id", "item_type", "facility_id", "tech_id", "year_stated",
            "coverage_pct", "resolution", "source_id", "quote"])

for name, df in [("D1a_facility_static", d1a), ("D1b_facility_panel", d1b),
                 ("D2a_scenario_budget", d2a), ("D2b_scenario_prices", d2b),
                 ("D3_tech_options", d3), ("D4_price_history", d4),
                 ("D5_policy_support", d5), ("D6_company_financials", d6),
                 ("D7_disclosed_plan", d7)]:
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"{name}: {len(df)} rows")

sys.exit(0)
