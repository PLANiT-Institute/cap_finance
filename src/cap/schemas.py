"""Input CSV schemas (mirror of the Excel template, REDESIGN_SPEC §2) and loaders.

Every pipeline stage loads inputs through `load_input`, which fails fast with a
message naming the missing file / columns — per spec: 스키마 검증 실패 시 즉시 중단.
"""

from __future__ import annotations

import pathlib

import pandas as pd

# file stem -> required columns. Extra columns are allowed and preserved.
SCHEMAS: dict[str, list[str]] = {
    "D1a_facility_static": [
        "facility_id", "company_id", "sector", "site", "unit_type", "unit_name",
        "capacity", "capacity_unit", "commissioning_year", "last_reline_year",
        "reinvest_cycle_yr", "next_reinvest_year", "status", "source_id",
    ],
    "D1b_facility_panel": [
        "facility_id", "year", "production", "emissions_s1", "emissions_s2",
        "energy_coal", "energy_gas", "energy_elec", "energy_naphtha", "source_id",
    ],
    "D2a_scenario_budget": [
        "scenario", "region", "sector", "year", "carbon_budget", "gcam_version", "source_id",
    ],
    "D2b_scenario_prices": [
        "scenario", "region", "variable", "year", "value", "unit", "source_id",
    ],
    "D3_tech_options": [
        "tech_id", "sector", "applies_to_unit", "capex_unit", "opex_fixed", "opex_var",
        "elec_intensity", "h2_intensity", "emission_factor", "avail_year",
        "build_years", "lifetime", "capex_uncertainty", "source_id",
    ],
    "D4_price_history": ["date", "series_id", "value", "unit", "source_id"],
    "D5_policy_support": [
        "support_scenario", "instrument", "tech_id", "param_type", "value", "unit",
        "valid_from", "valid_to", "source_id",
    ],
    "D6_company_financials": [
        "company_id", "year", "revenue", "ebitda", "capex_total", "total_debt",
        "net_debt", "interest_expense", "cash", "source_id",
    ],
    "D7_disclosed_plan": [
        "company_id", "item_type", "facility_id", "tech_id", "year_stated",
        "coverage_pct", "resolution", "source_id", "quote",
    ],
}

NUMERIC = {
    "capacity", "commissioning_year", "last_reline_year", "reinvest_cycle_yr",
    "next_reinvest_year", "year", "production", "emissions_s1", "emissions_s2",
    "energy_coal", "energy_gas", "energy_elec", "energy_naphtha", "carbon_budget",
    "value", "capex_unit", "opex_fixed", "opex_var", "elec_intensity", "h2_intensity",
    "emission_factor", "avail_year", "build_years", "lifetime", "capex_uncertainty",
    "incumbent_capex_unit", "margin_kthou_t", "retrofit", "valid_from", "valid_to", "revenue", "ebitda", "capex_total", "total_debt",
    "net_debt", "interest_expense", "cash", "year_stated", "coverage_pct",
}


class SchemaError(RuntimeError):
    pass


def load_input(data_dir: pathlib.Path, name: str) -> pd.DataFrame:
    if name not in SCHEMAS:
        raise SchemaError(f"unknown input '{name}'; known: {sorted(SCHEMAS)}")
    path = data_dir / f"{name}.csv"
    if not path.exists():
        raise SchemaError(f"missing input file: {path}\n→ 엑셀 시트 '{name}'를 CSV로 변환해 이 경로에 두어야 함")
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").rename(columns=lambda c: c.strip())
    missing = [c for c in SCHEMAS[name] if c not in df.columns]
    if missing:
        raise SchemaError(f"{path}: missing columns {missing}\n→ 템플릿 4행 컬럼명 기준 (REDESIGN_SPEC §2)")
    for c in df.columns:
        if c in NUMERIC:
            raw = df[c]
            df[c] = pd.to_numeric(raw.astype(str).str.replace(",", "", regex=False), errors="coerce")
            # fail fast: a non-blank cell that coerced to NaN is corrupt input
            # (Excel artifacts like "N/A", stray text) — never let it flow into the LP
            bad = df[c].isna() & raw.notna() & (raw.astype(str).str.strip() != "")
            if bad.any():
                i = int(bad.idxmax())
                raise SchemaError(f"{path}: column '{c}' has {int(bad.sum())} non-numeric "
                                  f"value(s), e.g. row {i + 2}: {raw[i]!r}")
    return df
