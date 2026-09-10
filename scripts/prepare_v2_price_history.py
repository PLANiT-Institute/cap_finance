"""Append verified World Bank CMO annual fuel series to a case's D4_price_history.csv.

v2 price factors (calibration.FACTOR_SERIES_V2) require coal and gas series in D4.
The only verified source in the repository is the World Bank Commodity Markets
"Pink Sheet" monthly workbook, already extracted with cell provenance and a
file sha256 in data/research_v2/price_history/native_monthly_prices.csv.
This script averages complete calendar years and appends:

    wb_coal_au_usd_t        Coal, Australian thermal, USD/t, annual mean of months
    wb_japan_lng_usd_mmbtu  LNG Japan cif, USD/mmbtu, annual mean of months

Usage: python scripts/prepare_v2_price_history.py --data <case data dir>
Idempotent: existing rows with the same series_id are replaced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
WB = ROOT / "data/research_v2/price_history/native_monthly_prices.csv"
MANIFEST = ROOT / "data/research_v2/price_history/manifest.json"
SERIES = {"thermal_coal_au": ("wb_coal_au_usd_t", "USD/t (연평균, WB CMO 월별 평균)"),
          "japan_lng": ("wb_japan_lng_usd_mmbtu", "USD/mmbtu (연평균, WB CMO 월별 평균)")}


def build_rows(first_year: int = 2010, last_full_year: int | None = None) -> pd.DataFrame:
    wb = pd.read_csv(WB)
    wb = wb[(~wb.is_missing) & wb.series_id.isin(SERIES)].copy()
    wb["year"] = wb.period.str[:4].astype(int)
    counts = wb.groupby(["series_id", "year"]).value.count()
    means = wb.groupby(["series_id", "year"]).value.mean()
    sha = json.loads(MANIFEST.read_text())["source"]["sha256"][:12]
    rows = []
    for (sid, year), n in counts.items():
        if year < first_year or n < 12:          # complete calendar years only
            continue
        if last_full_year is not None and year > last_full_year:
            continue
        new_id, unit = SERIES[sid]
        rows.append({"date": str(year), "series_id": new_id, "value": round(float(means[(sid, year)]), 4),
                     "unit": unit, "source_id": f"WB_CMO_2026_{sha}"})
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="case data directory containing D4_price_history.csv")
    a = ap.parse_args(argv)
    d4p = pathlib.Path(a.data) / "D4_price_history.csv"
    d4 = pd.read_csv(d4p)
    new = build_rows()
    d4 = d4[~d4.series_id.isin(new.series_id.unique())]
    out = pd.concat([d4, new], ignore_index=True)
    out.to_csv(d4p, index=False)
    print(f"D4 updated: +{len(new)} verified WB annual rows -> {d4p} "
          f"sha256 {hashlib.sha256(d4p.read_bytes()).hexdigest()[:12]}")


if __name__ == "__main__":
    main()
