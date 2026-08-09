"""Deterministic per-plan quantity profiles + vectorized simulated costing.

Single source of truth for "what does this plan buy each year" — used by E4
(simulation) and E5 (metrics). Mirrors the cost structure of the E2 objective;
E4 writes the wedge between central-path cost and the E2 surrogate objective to
summary.csv (they differ by the slack penalty and contract linearization — spec §3 E4).
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from . import config as C
from .schemas import load_input

SCALE = 1e-6  # KRW thousands -> billions
# D3 capex_uncertainty is a per-technology band in % (spec §D3, 30–60 across our set).
# The calibrated market shock (E3) carries the LEVEL of construction-cost risk; this
# column carries how much MORE or LESS uncertain a given technology is than the rest.
# Using it as a relative amplitude avoids inventing a band convention the spec never
# states, while no longer throwing the column away. — A-22
CAPEX_UNC_REF = 40.0
GJ_PER_T_COAL = 28.0
GJ_PER_T_GAS = 54.0


@lru_cache(maxsize=8)
def _d5_auction_windows(ddir: str) -> tuple:
    """(from, to, share) windows for 발전외 유상할당 from D5 — the allocation rule
    our four companies actually face. Cached: called once per simulated path."""
    try:
        d5 = load_input(pathlib.Path(ddir), "D5_policy_support")
    except Exception:  # optional refinement — the config ramp stands on its own
        return ()
    g = d5[d5.instrument == "auction_share"]
    return tuple((float(r.valid_from), float(r.valid_to), float(r.value) / 100.0)
                 for r in g.itertuples() if pd.notna(r.value))


def auction_share(years: np.ndarray, cfg) -> np.ndarray:
    """Share of emissions actually facing the carbon price (유상할당). Free
    allocation is why an emitting plant stays solvent at a carbon price many times
    its product margin; charging 100% makes 'close everything' the optimum.
    Emissions still count fully toward the budget.

    Confirmed allocation windows come from D5 (K-ETS 4기 발전외 15%, 2026–2030);
    cfg.carbon_auction_share is the ESTIMATE ramp that covers the years no
    allocation plan has been published for. Data wins wherever data exists."""
    tbl = cfg.get("carbon_auction_share") or {2025: 1.0}
    ky = np.array(sorted(int(k) for k in tbl))
    kv = np.array([float(tbl[int(k)]) for k in ky])
    yrs = np.asarray(years, dtype=float)
    out = np.interp(yrs, ky, kv)
    for lo, hi, v in _d5_auction_windows(str(C.data_dir(cfg))):
        out[(yrs >= lo) & (yrs <= hi)] = v
    return out


def stranded_cost_k(fr, ta: int, cfg) -> float:
    """Remaining depreciated book value (KRW thousands) of the incumbent campaign
    asset written off by converting at ta. Straight-line over the reinvestment
    cycle; campaign anchors at last_reline + k*cycle, so converting right at an
    anchor (relining due) writes off nothing and converting just after a reline
    writes off nearly the full campaign asset. Grace window: halfwidth years
    before the anchor count as on-window."""
    cycle = float(fr.reinvest_cycle_yr)
    inc = float(fr.get("incumbent_capex_unit", 200.0) if hasattr(fr, "get")
                else getattr(fr, "incumbent_capex_unit", 200.0))
    if pd.isna(inc):
        inc = 200.0
    # H3 외부 대조: 공시된 실제 개수(고베 3고로 2016) 47천원/t 대비 주입값 200이 ×4.2다.
    # 이 값이 조기 전환의 벌점을 정하므로 결론 불변성을 시나리오로 흔들 수 있어야 한다.
    inc *= float(cfg.get("incumbent_capex_scale", 1.0))
    k = max(1, int(np.ceil((ta - fr.last_reline_year) / cycle)))
    anchor = fr.last_reline_year + k * cycle
    remaining = max(0.0, anchor - ta - cfg.milp.reinvest_window_halfwidth) / cycle
    return remaining * inc * fr.capacity


def salvage_fraction(tk, op_year: int, end_year: int) -> float:
    """Straight-line book value fraction of the NEW asset remaining at horizon end
    — credited back so late adoptions aren't charged full capex for partial use."""
    used = end_year - op_year + 1
    return max(0.0, 1.0 - used / float(tk.lifetime))


@dataclass
class PlanProfile:
    grid_mwh: np.ndarray      # (T,) incumbent-process electricity (grid tariff/SMP)
    re_mwh: np.ndarray        # transition-tech electricity (renewable procurement)
    h2_kg: np.ndarray         # externally procured hydrogen
    other_cost_k: np.ndarray  # coal+gas+opex+margin-loss+write-offs, KRW thousands (deterministic)
    capex_k: np.ndarray       # KRW thousands spent per year, incl. stranded penalty
    capex_by_tech: dict[str, np.ndarray]
    capex_unc: dict[str, float]   # D3 capex_uncertainty (%) per adopted tech — A-22
    emissions: np.ndarray     # tCO2 scope1
    ppa: float
    epc: int
    ccfd: int


RETIRE = "retire"  # pseudo-tech: early closure — no D3 row, handled structurally


def build_profile(plan_df: pd.DataFrame, fac: pd.DataFrame, techs: pd.DataFrame,
                  px_central: dict[str, np.ndarray], years: np.ndarray, cfg) -> PlanProfile:
    """v2.1: grid electricity (incumbent process) and renewable-procured electricity
    (transition techs) are separate channels; hydrogen is externally procured.
    'retire' rows close the facility at adopt_year: emissions/energy stop, the
    campaign asset's book value is written off, and future margin is forfeit."""
    T = len(years)
    grid = np.zeros(T)
    re = np.zeros(T)
    h2 = np.zeros(T)
    other = np.zeros(T)
    capex = np.zeros(T)
    capex_by_tech: dict[str, np.ndarray] = {}
    capex_unc: dict[str, float] = {}
    emis = np.zeros(T)
    tk_idx = techs.set_index("tech_id")
    adopt = {r.facility_id: r for r in plan_df.itertuples() if pd.notna(r.tech_id)}

    company = plan_df.company_id.iloc[0]
    for fid, fr in fac[fac.company_id == company].iterrows():
        a = adopt.get(fid)
        op_year = int(a.op_year) if a is not None else 10**9
        is_retire = a is not None and a.tech_id == RETIRE
        margin = float(fr.get("margin_kthou_t", 0) or 0)
        if pd.isna(margin):
            margin = 0.0
        for i, t in enumerate(years):
            if is_retire and t >= op_year:
                # forfeited operating margin. Margin (영업이익/t) is already net of
                # energy costs, so the model's own energy-cost savings must be
                # neutralized (added back deterministically) to avoid double
                # counting — closure's genuine benefits are carbon avoidance and
                # the removal of price-risk exposure, not a second energy saving.
                other[i] += (margin * fr.production
                             + fr.elec_int_inc * fr.production * px_central["elec"][i] / 1000.0
                             + fr.coal_int_inc * fr.production * px_central["coal"][i] / 1000.0
                             + fr.gas_int_inc * fr.production * px_central["gas"][i] / 1000.0)
                continue
            incumbent_energy = t < op_year
            if not incumbent_energy:
                tk = tk_idx.loc[a.tech_id]
                incumbent_energy = bool(int(tk.get("retrofit", 0) or 0))  # retrofit keeps process energy
                re[i] += tk.elec_intensity * fr.production   # transition power = renewable procurement
                h2[i] += tk.h2_intensity * fr.production
                emis[i] += tk.emission_factor * fr.production
                # opex_var per tonne produced; opex_fixed per tonne CAPACITY (spec D3)
                other[i] += tk.opex_var * fr.production + tk.opex_fixed * fr.capacity
            else:
                emis[i] += fr.ef_inc * fr.production if t < op_year else 0.0
            if incumbent_energy:
                grid[i] += fr.elec_int_inc * fr.production
                other[i] += (fr.coal_int_inc * fr.production * px_central["coal"][i] / 1000.0
                             + fr.gas_int_inc * fr.production * px_central["gas"][i] / 1000.0)
        if a is not None:
            ta = int(a.adopt_year)
            if years[0] <= ta <= years[-1]:
                i = int(ta - years[0])
                if is_retire:
                    # book write-off is deterministic — no market capex shock applies
                    other[i] += stranded_cost_k(fr, ta, cfg)
                else:
                    tk = tk_idx.loc[a.tech_id]
                    base = tk.capex_unit * fr.capacity
                    # EPC drawdown: construction spend spreads evenly across the
                    # build, it is not a lump at FID. Charging it in one year
                    # overstated the peak-year funding need by up to build_years×
                    # — which is exactly what ① 자본 피크 and 조달부담(⑥) measure.
                    bv = tk.get("build_years", 1)
                    nb = max(int(bv) if pd.notna(bv) else 1, 1)
                    by_tech = capex_by_tech.setdefault(a.tech_id, np.zeros(T))
                    u = tk.get("capex_uncertainty", np.nan)
                    capex_unc[a.tech_id] = float(u) if pd.notna(u) else CAPEX_UNC_REF
                    for j in range(nb):
                        if i + j < T:
                            capex[i + j] += base / nb
                            by_tech[i + j] += base / nb
                    # the incumbent's book write-off is an accounting event at
                    # conversion, not construction spend — stays a lump at ta
                    stranded = stranded_cost_k(fr, ta, cfg)
                    capex[i] += stranded
                    by_tech[i] += stranded
                    # horizon-end salvage of the new asset (deterministic credit;
                    # capex shocks not applied to salvage — second-order)
                    other[T - 1] -= base * salvage_fraction(tk, int(a.op_year), int(years[-1]))

    for name, arr in [("grid", grid), ("re", re), ("h2", h2), ("other", other),
                      ("capex", capex), ("emissions", emis)]:
        if not np.isfinite(arr).all():
            raise RuntimeError(f"plan {plan_df.plan_id.iloc[0] if 'plan_id' in plan_df else '?'}: "
                               f"NaN in {name} profile — facility data gap (D1a/D1b)")

    def _num(v, cast):
        return cast(0) if pd.isna(v) else cast(v)

    return PlanProfile(grid, re, h2, other, capex, capex_by_tech, capex_unc, emis,
                       _num(plan_df.ppa_share.iloc[0], float),
                       _num(plan_df.epc.iloc[0], int), _num(plan_df.ccfd.iloc[0], int))


def simulate_cost(p: PlanProfile, px: dict[str, np.ndarray], shocks: dict[str, np.ndarray],
                  support: dict, cfg, freeze: str | None = None) -> np.ndarray:
    """NPV cost per sim (KRW billions). shocks arrays are (N,T); pass mult=1 arrays for central.

    v2.1 channels: grid electricity (incumbent, elec shock), renewable-procured
    electricity (transition techs — PPA share fixed at re_price+premium, rest
    floats with the elec shock), externally procured hydrogen (own shock, no
    power hedge). freeze pins ONE cost channel at central for decomposition (③):
    'elec' = both power channels, 'h2', 'capex'."""
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc = (1 + cfg.discount_rate) ** -(years - years[0])
    N = shocks["elec"].shape[0]

    e_shock = np.ones_like(shocks["elec"]) if freeze == "elec" else shocks["elec"]
    h_shock = np.ones_like(shocks["h2"]) if freeze == "h2" else shocks["h2"]

    grid_sim = px["elec"][None, :] * e_shock                            # (N,T) KRW/MWh
    re_sim = px["re"][None, :] * e_shock                                # uncontracted 재생 조달은 시장 연동
    h2_sim = px["h2"][None, :] * h_shock                                # KRW/kg, 외부 조달

    ppa_grid = px["elec"] * (1 + cfg.contracts.ppa_premium_pct)         # fixed contract prices
    ppa_re = px["re"] * (1 + cfg.contracts.ppa_premium_pct)

    elec_cost = (p.grid_mwh[None, :] * ((1 - p.ppa) * grid_sim + p.ppa * ppa_grid[None, :])
                 + p.re_mwh[None, :] * ((1 - p.ppa) * re_sim + p.ppa * ppa_re[None, :])) / 1000.0
    h2_cost = (p.h2_kg[None, :] * h2_sim) / 1000.0                      # no power hedge on H2

    # capex: per-year subsidy (valid_from/valid_to windows) by tech, then EPC fix or shock.
    # The shock amplitude is scaled per technology by D3 capex_uncertainty (A-22): a
    # hydrogen-reduction plant and a heat-recovery retrofit do not carry the same
    # construction-cost risk, and the data says so.
    capex_cost = np.zeros((N, len(years)))
    for tech_id, arr in p.capex_by_tech.items():
        sub_t = support["subsidy"].get(tech_id, support["subsidy"].get("all"))
        eff = arr * (1 - sub_t) if sub_t is not None else arr
        if p.epc:
            capex_cost += np.tile(eff * (1 + cfg.contracts.epc_premium_pct), (N, 1))
        elif freeze == "capex":
            capex_cost += np.tile(eff, (N, 1))
        else:
            amp = p.capex_unc.get(tech_id, CAPEX_UNC_REF) / CAPEX_UNC_REF
            capex_cost += eff[None, :] * (1 + (shocks["capex"] - 1) * amp)

    carbon_price = px["co2"][None, :] * auction_share(years, cfg)[None, :]   # (1,T) 유상할당 반영, KRW/tCO2
    # L2/FC4: 탄소가격은 기본적으로 시나리오 축(결정론)이다 — 정책 위험을 뺀 위험을 재고
    # 있다는 뜻이다. shocks에 'co2'가 있으면 (N,T)로 확률화된다. 없으면 (1,T) 그대로라
    # 기존 파이프라인 수치는 불변이다.
    carbon_price = carbon_price * shocks.get("co2", 1.0)
    strike_t = support.get("ccfd_strike")                              # (T,) with inf outside window
    if p.ccfd and strike_t is not None:
        capped = np.minimum(carbon_price, strike_t[None, :])
        fee = cfg.contracts.ccfd_fee_pct * np.isfinite(strike_t)       # fee only in covered years
        carbon_cost = p.emissions[None, :] * capped * (1 + fee)[None, :] / 1000.0
    else:
        carbon_cost = p.emissions[None, :] * carbon_price / 1000.0

    total_k = elec_cost + h2_cost + capex_cost + carbon_cost + p.other_cost_k[None, :]
    return (total_k * disc[None, :]).sum(axis=1) * SCALE


def support_params(d5: pd.DataFrame, support_scenario: str, years: np.ndarray) -> dict:
    """Per-year support arrays honouring valid_from/valid_to windows.

    subsidy: {tech_id: (T,) rate array, 0 outside window}
    ccfd_strike: (T,) strike array, +inf outside window; None if no CCfD row.
    """
    if support_scenario == "none":
        return {"subsidy": {}, "ccfd_strike": None}
    g = d5[d5.support_scenario == support_scenario]

    def window(r):
        lo = years[0] if pd.isna(r.valid_from) else r.valid_from
        hi = years[-1] if pd.isna(r.valid_to) else r.valid_to
        return (years >= lo) & (years <= hi)

    subsidy: dict[str, np.ndarray] = {}
    for r in g[g.instrument == "subsidy_capex"].itertuples():
        arr = subsidy.setdefault(r.tech_id, np.zeros(len(years)))
        np.maximum(arr, np.where(window(r), r.value / 100.0, 0.0), out=arr)

    strike = None
    for r in g[g.instrument == "ccfd"].itertuples():
        if strike is None:
            strike = np.full(len(years), np.inf)
        strike = np.where(window(r), np.minimum(strike, r.value), strike)
    return {"subsidy": subsidy, "ccfd_strike": strike}
