"""Volatility / correlation calibration from D4 price history.

Shared by E2 (linear risk proxy in the MILP) and E3 (Monte Carlo generation).
Three risk factors (설계서 §3): electricity, hydrogen (derived), capex.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# factor -> D4 series used to estimate it. capex blends construction + equipment.
# elec blends spot SMP with the regulated industrial tariff: large industrials'
# realized power cost sits between contract/tariff and marginal spot exposure,
# and spot-only vol (annual obs incl. the 2022 crisis) overstates it
# smp_monthly (월별, 2025+) is the primary electricity-vol series; the annual SMP
# series stays as a level reference only (annual returns mix the 2022 crisis into
# a 10-obs sample). jepx_spot covers the Japanese market's vol.
# v2.1: hydrogen is an EXTERNALLY PROCURED commodity — independent factor. No
# mature contract-price series exists yet (CHPS 낙찰가 비공개), so vol falls back
# to the prior below until a real series lands in D4.
FACTOR_SERIES = {"elec": ["smp_monthly", "indus_tariff", "jepx_spot"],
                 "h2": ["h2_contract_krw_kg"],
                 "capex": ["constr_cost_idx", "equip_import_idx"]}


@dataclass
class Calibration:
    vol: dict[str, float]          # annualized log-return volatility per factor
    corr: pd.DataFrame             # factor correlation matrix (elec, capex)
    electrolyzer_decline: float    # ANNUAL log decline of electrolyzer capex
    electrolyzer_vol: float        # annualized
    ez_anchor: float               # last observed electrolyzer capex (KRW/kW)
    ez_anchor_year: int

    def ez_central(self, years: np.ndarray) -> np.ndarray:
        """Central electrolyzer capex path anchored at the last D4 observation.
        Single source of truth — E2/E4/E5 must all use this."""
        return self.ez_anchor * np.exp(-self.electrolyzer_decline * (np.asarray(years) - self.ez_anchor_year))


# priors when D4 lacks usable series — logged loudly. h2 prior 0.25: between the
# gas-import benchmark (~0.3) and a contracted-supply view; replace when a real
# clean-hydrogen price series exists (2차 수집 C항)
FALLBACK_VOL = {"elec": 0.15, "h2": 0.25, "capex": 0.06}


def _annual_vol(series: pd.Series) -> tuple[float, pd.Series]:
    """Frequency-aware annualized vol: monthly obs scale by sqrt(12), annual by 1."""
    spy = _steps_per_year(series.index)
    r = np.log(series).diff().dropna()
    return float(r.std() * np.sqrt(spy)), r


def _steps_per_year(idx: pd.DatetimeIndex) -> float:
    gap_days = np.median(np.diff(idx.values).astype("timedelta64[D]").astype(float))
    return 365.25 / max(gap_days, 1.0)


def calibrate(d4: pd.DataFrame) -> Calibration:
    d4 = d4.copy()
    # mixed granularity is legitimate ("2022" annual rows, "2025-01" monthly rows)
    d4["date"] = pd.to_datetime(d4.date.astype(str), format="mixed", errors="coerce")
    if d4.date.isna().any():
        bad = d4[d4.date.isna()]
        raise RuntimeError(f"D4 date parse failure ({len(bad)} rows), e.g. series "
                           f"{bad.series_id.iloc[0]!r} — use YYYY-MM")
    wide = (d4.pivot_table(index="date", columns="series_id", values="value", aggfunc="last")
            .sort_index())
    vols, rets = {}, {}
    for factor, series in FACTOR_SERIES.items():
        # 6+ obs (5 log returns) is the floor for a usable — if noisy — vol estimate
        avail = [s for s in series if s in wide.columns and wide[s].notna().sum() >= 6]
        if not avail:
            vols[factor] = FALLBACK_VOL[factor]
            print(f"[calibration] WARNING: no usable D4 series for factor '{factor}' "
                  f"({series}, need 6+ obs) — fallback prior vol={FALLBACK_VOL[factor]} used. "
                  "결과의 TCaR은 이 사전값에 의존 — D4 보강 필요")
            continue
        fv, fr = [], []
        for s in avail:
            v, r = _annual_vol(wide[s].dropna())
            fv.append(v)
            fr.append(r)
        vols[factor] = float(np.mean(fv))
        rets[factor] = pd.concat(fr, axis=1).mean(axis=1)

    if len(rets) == len(FACTOR_SERIES):
        corr = pd.concat(rets, axis=1).dropna().corr()
        if corr.isna().any().any() or len(corr) < len(FACTOR_SERIES):
            corr = pd.DataFrame(np.eye(len(FACTOR_SERIES)), index=list(FACTOR_SERIES), columns=list(FACTOR_SERIES))
            print("[calibration] WARNING: factor correlation not estimable (no overlapping obs) — identity used")
    else:
        corr = pd.DataFrame(np.eye(len(FACTOR_SERIES)), index=list(FACTOR_SERIES), columns=list(FACTOR_SERIES))
        print("[calibration] WARNING: correlation set to identity (missing factor series)")

    ez = wide.get("electrolyzer_capex")
    if ez is not None and 0 < ez.dropna().shape[0] < 3:
        # too few obs to fit a trend — anchor at last observation, prior decline/vol
        ezd = ez.dropna()
        decline, evol = 0.05, 0.10
        anchor, anchor_year = float(ezd.iloc[-1]), int(ezd.index[-1].year)
        print(f"[calibration] WARNING: electrolyzer_capex has {len(ezd)} obs — anchor "
              f"{anchor:,.0f} KRW/kW @{anchor_year} from data, decline/vol from prior (5%/10%)")
    elif ez is None or ez.dropna().empty:
        # ponytail: fallback prior, replace when D4 has the series
        decline, evol, anchor, anchor_year = 0.05, 0.10, 1_500_000.0, 2025
        print("[calibration] WARNING: no electrolyzer_capex in D4 — full prior used")
    else:
        ez = ez.dropna()
        spy = _steps_per_year(ez.index)          # frequency-aware annualization
        lr = np.log(ez).diff().dropna()
        decline = float(-lr.mean() * spy)
        evol = float(lr.std() * np.sqrt(spy))
        anchor = float(ez.iloc[-1])
        anchor_year = int(ez.index[-1].year)
    return Calibration(vol=vols, corr=corr, electrolyzer_decline=decline,
                       electrolyzer_vol=evol, ez_anchor=anchor, ez_anchor_year=anchor_year)


def hydrogen_price(elec_price, electrolyzer_capex_kw, hcfg) -> np.ndarray:
    """h2 (KRW/kg) = electricity cost per kg + amortized electrolyzer capex per kg.

    구조식 (설계서 §3): 수소 변동성은 전력·전해조 CAPEX에서 파생, 독립 추정 금지.
    elec_price in KRW/MWh.
    """
    energy = np.asarray(elec_price) * hcfg.kwh_per_kg / 1000.0
    capex = np.asarray(electrolyzer_capex_kw) * hcfg.electrolyzer_capex_amort / hcfg.electrolyzer_kg_per_kw_yr
    return energy + capex
