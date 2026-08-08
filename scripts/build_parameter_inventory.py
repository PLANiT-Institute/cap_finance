"""F1 — one table of every model parameter with its evidence tier (AUTOPILOT v2 §1).

Walks FIN's prepared inputs + config and EFF's data files, assigns an evidence tier
from the source register, and flags anything that is a model estimate without a
stated range (`T5-norange`) — those are the defects F1 exists to surface.

    .venv/bin/python scripts/build_parameter_inventory.py
Writes docs/parameter_inventory.csv (both repos) and prints the audit summary.
"""

from __future__ import annotations

import json
import pathlib

import pandas as pd
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
EFF = pathlib.Path.home() / "Documents/cap-efficient"
PREP = ROOT / "data/prepared"

# source_id -> evidence tier. T1 regulatory/audited, T2 company primary,
# T3 peer-reviewed/public institution, T4 trade press/market, T5 our estimate.
TIER = {
    # T1 — regulation, audited filings, official gazette
    "KETS_P4_CONFIRM_2025": "T1", "GXETS_COLLAR_METI": "T1", "BOK_FSS_CST_2025": "T1",
    "METI_ENV_EVAL_2025": "T1", "KR_NETZERO_2050": "T1", "KR_NDC_BASIC_2023": "T1",
    "MOTIE_H2_PLAN_2021": "T1", "H2_ROADMAP_2019": "T1", "JP_H2_STRATEGY_2023": "T1",
    # T2 — company primary disclosure
    "POSCO_ESG_ROADMAP": "T2", "POSCO_FACTBOOK": "T2", "POSCO_GY_EAF": "T2",
    "POSCO_HYREX": "T2", "POSCO_IR_MEDIA": "T2", "POSCO_NEWSROOM_BF2": "T2",
    "NSC_DATABOOK_2025": "T2", "NSC_PR_20250530": "T2", "NSC_CN_COURSE50": "T2",
    "NSC_ESG_CLIMATE": "T2", "NSC_EAF_2025": "T2", "NSC_SCOURSE50_2024": "T2",
    "LOTTE_ESG_REPORTS": "T2", "LOTTE_PR_2030": "T2", "LOTTE_IR_FIN": "T2",
    "MITSUI_ESG_DATA": "T2", "MITSUI_KESSAN": "T2", "MCI_RELEASES": "T2",
    "KOBELCO_HBI_BF": "T2", "BASF_ECRACKER_2024": "T2",
    # T3 — peer-reviewed / public institution statistics
    "VOGL_2018": "T3", "DIW_DP2082": "T3", "RSC_ECRACKER_2025": "T3",
    "NATURE_STEELEFF_2025": "T3", "MDPI_METALS_BOF": "T3", "IEAGHG_STEELCCS": "T3",
    "CHEMRXIV_2025": "T3", "IEA_GHR2023_ANNEX": "T3", "IEA_GHR2024_ANNEX": "T3",
    "IEA_GHR2025_ES": "T3", "IEA_GHR2021_P111": "T3", "IEA_GECM_DOC_2025": "T3",
    "IEA_GECM_CO2PRICE": "T3", "IEA_HTHP": "T3", "NGFS_P5_OUTREACH": "T3",
    "KPX_SMP_MONTHLY": "T3", "KPX_SMP_MONTHLY_WEB": "T3", "KPX_SMP_YEARLY": "T3",
    "KEPCO_EGTIPS": "T3", "JEPX_BR": "T3", "METI_COSTWG_2021": "T3",
    "METI_COSTWG_2025": "T3", "NABO_KETS_2024": "T3", "REI_JP_PPA_2025": "T3",
    "JISF_CNAP_2025": "T3", "FX_ANNUAL_MIXED": "T3",
    # T4 — trade press, market data, secondary compilations
    "POSCO_BF_MEDIA": "T4", "LOTTE_MEDIA_2026": "T4", "NSC_IRBANK": "T4",
    "CHPS_AUCTION_2024": "T4", "ICIS_BIONAPHTHA_2025": "T4", "TODAYENERGY_LNG": "T4",
    "KR_STATS_SNIPPET": "T4", "SPGLOBAL_ENA_SPREAD": "T4", "POSCO_OPINC_SERIES": "T4",
    "KR_PPA_2026": "T4", "KR_H2_PRICE_2025": "T4", "DECARB_TECH_CRACKER": "T4",
    "KBC_CHEMENG_2024": "T4", "SNU_ELEC_2050_2023": "T4",
    # T5 — our own estimates
    "EST_D2A_V0": "T5", "EST_D2B_V0": "T5", "EST_D3_V0": "T5", "EST_D1A_REINVEST": "T5",
    "PREP_ALLOC": "T5", "PREP_BOTTOMUP": "T5", "PENDING_GCAM_KAIST": "T5",
    "model_estimate": "T5", "reported": "T2", "regulatory": "T1",
}


def tier_of(source_id) -> str:
    if not isinstance(source_id, str) or not source_id.strip():
        return "T5"
    for key in TIER:                      # prefix match handles composite labels
        if source_id.startswith(key):
            return TIER[key]
    return "T5"


def rows_from_frame(df, model, group, value_cols, id_col, unit_map, uses):
    out = []
    for r in df.itertuples():
        for c in value_cols:
            v = getattr(r, c, None)
            if v is None or (isinstance(v, float) and pd.isna(v)):
                continue
            src = getattr(r, "source_id", "")
            out.append(dict(
                param_id=f"{model}.{group}.{getattr(r, id_col)}.{c}",
                model=model, group=group, entity=str(getattr(r, id_col)), field=c,
                value=v, unit=unit_map.get(c, ""), evidence_tier=tier_of(src),
                value_low="", value_high="", source_id=src, vintage="",
                used_in=uses.get(c, ""),
            ))
    return out


def main():
    rows = []

    # ---- FIN D1a facility static
    d1a = pd.read_csv(PREP / "D1a_facility_static.csv")
    rows += rows_from_frame(
        d1a, "FIN", "facility", ["capacity", "next_reinvest_year", "reinvest_cycle_yr",
                                 "incumbent_capex_unit", "margin_kthou_t"], "facility_id",
        {"capacity": "t/yr", "next_reinvest_year": "year", "reinvest_cycle_yr": "yr",
         "incumbent_capex_unit": "천원/t능력", "margin_kthou_t": "천원/t"},
        {"capacity": "E2 capex·retire scale", "next_reinvest_year": "E2 stranded_cost_k",
         "reinvest_cycle_yr": "E2 stranded_cost_k", "incumbent_capex_unit": "E2 stranded_cost_k",
         "margin_kthou_t": "E2 retire_terms"})

    # ---- FIN D3 technologies
    d3 = pd.read_csv(PREP / "D3_tech_options.csv")
    rows += rows_from_frame(
        d3, "FIN", "technology", ["capex_unit", "opex_fixed", "opex_var", "elec_intensity",
                                  "h2_intensity", "emission_factor", "avail_year",
                                  "build_years", "lifetime", "capex_uncertainty"], "tech_id",
        {"capex_unit": "천원/t능력", "opex_fixed": "천원/t능력/yr", "opex_var": "천원/t",
         "elec_intensity": "MWh/t", "h2_intensity": "kg/t", "emission_factor": "tCO2/t",
         "avail_year": "year", "build_years": "yr", "lifetime": "yr", "capex_uncertainty": "%"},
        {"capex_unit": "E2/plancost capex", "elec_intensity": "energy cost + TCaR elec",
         "h2_intensity": "energy cost + TCaR h2", "emission_factor": "budget + carbon cost"})

    # ---- FIN D2b scenario prices (one row per variable x scenario x region, anchor years)
    d2b = pd.read_csv(PREP / "D2b_scenario_prices.csv")
    for (scen, region, var), g in d2b.groupby(["scenario", "region", "variable"]):
        g = g.sort_values("year")
        src = g.source_id.iloc[0]
        rows.append(dict(
            param_id=f"FIN.price.{scen}_{region}_{var}", model="FIN", group="price_path",
            entity=f"{scen}/{region}", field=var,
            value=f"{g.value.iloc[0]:.0f}→{g.value.iloc[-1]:.0f}", unit=g.unit.iloc[0],
            evidence_tier=tier_of(src), value_low="", value_high="", source_id=src,
            vintage="", used_in="E1 central path, E2/E4 cost"))

    # ---- FIN D2a budgets
    d2a = pd.read_csv(PREP / "D2a_scenario_budget.csv")
    for (scen, region, sector), g in d2a.groupby(["scenario", "region", "sector"]):
        g = g.sort_values("year")
        rows.append(dict(
            param_id=f"FIN.budget.{scen}_{region}_{sector}", model="FIN", group="budget",
            entity=f"{scen}/{region}/{sector}", field="carbon_budget",
            value=f"{g.carbon_budget.iloc[0]:.1f}→{g.carbon_budget.iloc[-1]:.1f}",
            unit="MtCO2/yr", evidence_tier=tier_of(g.source_id.iloc[0]), value_low="",
            value_high="", source_id=g.source_id.iloc[0], vintage="",
            used_in="E1 constraint, E2 budget"))

    # ---- FIN config (model choices, all T5 by construction)
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    cfg_items = {
        "discount_rate": ("실질 할인율", "1", "전 NPV", "0.035", "0.065"),
        "milp.retire_max_share": ("폐쇄 상한", "share", "E2 retire cap", "0.10", "0.30"),
        "milp.budget_violation_floor_thkrw": ("예산위반 페널티 바닥", "천원/tCO2", "E2 slack", "150", "600"),
        "milp.reinvest_window_halfwidth": ("재투자 창 유예", "yr", "stranded_cost_k", "0", "2"),
        "contracts.ppa_premium_pct": ("PPA 프리미엄", "share", "계약 비용", "0.03", "0.15"),
        "contracts.epc_premium_pct": ("EPC 프리미엄", "share", "계약 비용", "0.05", "0.20"),
        "contracts.ccfd_fee_pct": ("CCfD 수수료", "share", "계약 비용", "0.01", "0.05"),
        "simulation.n_sims": ("시뮬레이션 수", "count", "E3/E4", "10000", "50000"),
    }
    for key, (desc, unit, uses, lo, hi) in cfg_items.items():
        node = cfg
        for part in key.split("."):
            node = node.get(part, {}) if isinstance(node, dict) else None
        rows.append(dict(param_id=f"FIN.config.{key}", model="FIN", group="model_choice",
                         entity="config.yaml", field=desc, value=node, unit=unit,
                         evidence_tier="T5", value_low=lo, value_high=hi,
                         source_id="MODEL_CHOICE", vintage="2026-08", used_in=uses))
    for y, v in (cfg.get("carbon_auction_share") or {}).items():
        rows.append(dict(param_id=f"FIN.config.auction_share.{y}", model="FIN",
                         group="policy_assumption", entity="carbon_auction_share",
                         field=str(y), value=v, unit="share",
                         evidence_tier="T1" if int(y) <= 2030 else "T5",
                         value_low=round(v * 0.6, 2), value_high=min(1.0, round(v * 1.4, 2)),
                         source_id="KETS_P4_CONFIRM_2025" if int(y) <= 2030 else "MODEL_ESTIMATE",
                         vintage="2025", used_in="carbon cost (E2/plancost/E5)"))

    # ---- FIN prepared-layer injections (from PREP_LOG): route intensities, capacity coeff
    for name, val, unit, lo, hi, uses in [
        ("route.BF.emission_factor", 2.15, "tCO2/t", 1.9, 2.4, "D1b 시설 배출 배분"),
        ("route.BF.coal_intensity", 13.5, "GJ/t", 12.0, 15.0, "기존 조업 비용"),
        ("route.NCC.emission_factor", 0.95, "tCO2/t", 0.8, 1.2, "석화 상향식 추정"),
        ("capacity.t_per_m3_yr", 913.0, "t/m³/yr", 800.0, 1000.0, "고로 능력 추정"),
    ]:
        rows.append(dict(param_id=f"FIN.prep.{name}", model="FIN", group="prep_injection",
                         entity="prepare_raw.py", field=name, value=val, unit=unit,
                         evidence_tier="T5", value_low=lo, value_high=hi,
                         source_id="PREP_INJECTION", vintage="2026-08", used_in=uses))

    # ---- EFF technologies / facilities
    try:
        eff_t = pd.read_csv(EFF / "data/technologies.csv")
        eff_t["source_id"] = eff_t.get("data_status", "model_estimate")
        rows += rows_from_frame(
            eff_t, "EFF", "technology",
            ["capex_bn_krw_per_mtpa", "fixed_opex_kkrw_per_t", "electricity_mwh_per_t",
             "hydrogen_t_per_t", "emissions_tco2_per_t", "available_year"], "technology_id",
            {"capex_bn_krw_per_mtpa": "십억원/Mtpa", "fixed_opex_kkrw_per_t": "천원/t",
             "electricity_mwh_per_t": "MWh/t", "hydrogen_t_per_t": "t/t",
             "emissions_tco2_per_t": "tCO2/t", "available_year": "year"},
            {"capex_bn_krw_per_mtpa": "EFF 후보 평가"})
        eff_f = pd.read_csv(EFF / "data/facilities.csv")
        eff_f["source_id"] = eff_f.get("data_status", "model_estimate")
        rows += rows_from_frame(
            eff_f, "EFF", "facility",
            ["capacity_mtpa", "baseline_emissions_tco2_per_t", "baseline_electricity_mwh_per_t",
             "reinvestment_year"], "facility_id",
            {"capacity_mtpa": "Mtpa", "baseline_emissions_tco2_per_t": "tCO2/t",
             "baseline_electricity_mwh_per_t": "MWh/t", "reinvestment_year": "year"},
            {"capacity_mtpa": "EFF 블록 규모"})
        # EFF evidence layer: real project costs / official projects — these are the
        # T2 anchors that its model inputs (all self-declared model_estimate) sit on.
        ev = pd.read_csv(EFF / "data/technology_cost_evidence.csv")
        for r in ev.itertuples():
            rows.append(dict(param_id=f"EFF.evidence.{r.evidence_id}", model="EFF",
                             group="cost_evidence", entity=r.technology_id,
                             field=f"{r.evidence_scope} ({r.capacity_mtpa} Mtpa)",
                             value=getattr(r, "capex_bn_krw", ""), unit="십억원",
                             evidence_tier="T2", value_low="", value_high="",
                             source_id=r.project_id, vintage="",
                             used_in="기술비용 대조(docs/tech_cost_reconciliation.md) — 모형 입력에는 미연결"))
        pp = json.loads((EFF / "data/price_process.json").read_text())
        for k, v in pp.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, (int, float)):
                        rows.append(dict(param_id=f"EFF.price_process.{k}.{k2}", model="EFF",
                                         group="price_process", entity=k, field=k2, value=v2,
                                         unit="", evidence_tier="T5", value_low="", value_high="",
                                         source_id="EFF_PRICE_PROCESS", vintage="",
                                         used_in="EFF 확률 평가"))
    except FileNotFoundError as e:
        print(f"[inv] EFF 파일 접근 실패: {e}")

    inv = pd.DataFrame(rows)
    # audit flags
    inv["needs_range"] = (inv.evidence_tier == "T5") & (inv.value_low.astype(str) == "")
    inv["tier_rank"] = inv.evidence_tier.map({"T1": 1, "T2": 2, "T3": 3, "T4": 4, "T5": 5})
    inv = inv.sort_values(["tier_rank", "model", "group", "param_id"]).drop(columns="tier_rank")

    for root in (ROOT, EFF):
        d = root / "docs"
        if d.parent.exists():
            d.mkdir(exist_ok=True)
            inv.to_csv(d / "parameter_inventory.csv", index=False)
            print(f"[inv] {d / 'parameter_inventory.csv'} ({len(inv)} rows)")

    print("\n=== 증거등급 분포")
    print(inv.groupby(["model", "evidence_tier"]).size().unstack(fill_value=0).to_string())
    print(f"\n=== T5 중 범위 미지정(수정 대상): {int(inv.needs_range.sum())}건")
    print(inv[inv.needs_range].groupby(["model", "group"]).size().to_string())


if __name__ == "__main__":
    main()
