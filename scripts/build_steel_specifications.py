"""Steel process specification set (research_v2, cycle 2 of 2026-09-07).

Rows include source references and explicitly unverified boundary experiments for one
FIN steel technology. Specifications are alternative theta, never averaged.
All quantities per t liquid/crude steel unless stated. Nothing here mutates
FIN/EFF inputs; FIN values are listed only for comparison.

Output: data/research_v2/technology_packages/steel_specifications.csv
        docs/research_cycles/2026-09-07/STEEL_PROCESS_BALANCE.md
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/research_v2/technology_packages/steel_specifications.csv"
OUT_MD = ROOT / "docs/research_cycles/2026-09-07/STEEL_PROCESS_BALANCE.md"

LHV_KWH_PER_KG = 33.33          # 120 MJ/kg rounded, research_v2 convention
ETA_EL = 0.72                   # V2OBS001
H2_BASE = 51.0                  # V2OBS006, 0% scrap, l=1.5
TOTAL_ONSITE = 3.48             # V2OBS011
EAF_HOT_DRI = 0.753             # V2OBS012
EAF_SCRAP = 0.667               # V2OBS005
COLD_PENALTY = 0.159            # V2OBS013
# POSTED v0.4.0 Iron Direct Reduction, h2 mode (per t DRI; reference_value in t DRI)
POSTED_DRI_ELEC = {"row24_2022": 0.065 / 1.1, "row25_2017": 0.08 / 1.0, "row27_2020": 0.1025 / 1.0}
POSTED_DRI_HEAT = {"row17_2022": 0.45 / 1.1, "row18_2017": 0.23 / 1.0, "row20_2018": 0.286 / 1.08}
DRI_PER_T_LS = 1.08             # POSTED note on Vogl row (1.1 vs 1.08 conflict held); Vogl pellets 1.504t -> HBI ~1.08t
GCAM = {"h2_gj": 7.3, "elec_gj": 4.2, "gas_gj": 3.6, "liq_gj": 1.1}
POSCO = {"coal_t_per_t_crude": 22_566_000 / 35_048_000, "ng_gj_per_t": 60_987_933 / 35_048_000,
         "elec_mwh_per_t": 10_963_428 / 35_048_000 / 3.6}

electrolysis = H2_BASE * LHV_KWH_PER_KG / ETA_EL / 1000          # MWh/t LS
residual = TOTAL_ONSITE - electrolysis                             # MWh/t LS, purchased-H2 basis before heat correction
dri_elec_lo, dri_elec_hi = min(POSTED_DRI_ELEC.values()) * DRI_PER_T_LS, max(POSTED_DRI_ELEC.values()) * DRI_PER_T_LS
dri_heat_lo, dri_heat_hi = min(POSTED_DRI_HEAT.values()) * DRI_PER_T_LS, max(POSTED_DRI_HEAT.values()) * DRI_PER_T_LS
bottom_up_hot_lo = EAF_HOT_DRI + dri_elec_lo + dri_heat_lo
bottom_up_hot_hi = EAF_HOT_DRI + dri_elec_hi + dri_heat_hi

SPECS = [
    # spec_id, fin_tech, carrier, value, unit, role, derivation, evidence_ids, status
    ("VOGL_H2DRI_ONSITE_0SCRAP_HOT", "steel_h2dri", "electricity_total", TOTAL_ONSITE, "MWh/t_LS", "purchased", "published total incl. electrolysis", "V2OBS011", "reference_only"),
    ("VOGL_H2DRI_ONSITE_0SCRAP_HOT", "steel_h2dri", "hydrogen_internal", H2_BASE, "kgH2/t_LS", "internal", "0% scrap, l=1.5", "V2OBS006", "reference_only"),
    ("VOGL_H2DRI_PURCHASEDH2_0SCRAP_HOT", "steel_h2dri", "hydrogen", H2_BASE, "kgH2/t_LS", "purchased", "same shaft balance; H2 bought at plant gate", "V2OBS006", "candidate_theta"),
    ("VOGL_H2DRI_PURCHASEDH2_0SCRAP_HOT", "steel_h2dri", "electricity", round(residual, 3), "MWh/t_LS", "purchased",
     f"3.48 - 51x{LHV_KWH_PER_KG}/{ETA_EL}/1000 = {residual:.3f}; keeps Vogl off-gas heat recovery, drops electrolyser waste heat (not quantified by Vogl)", "V2OBS011,V2OBS006,V2OBS001", "boundary_experiment_heat_unresolved"),
    ("VOGL_H2DRI_PURCHASEDH2_0SCRAP_COLD", "steel_h2dri", "electricity", round(residual + COLD_PENALTY, 3), "MWh/t_LS", "purchased", "hot spec + 0.159 cold-HBI penalty", "V2OBS013", "candidate_theta"),
    ("POSTED_BOTTOMUP_PURCHASEDH2_HOT", "steel_h2dri", "electricity_low", round(bottom_up_hot_lo, 3), "MWh/t_LS", "purchased",
     f"EAF 0.753 + DRI plant elec {dri_elec_lo:.3f} + H2 preheat {dri_heat_lo:.3f} (POSTED rows, x{DRI_PER_T_LS} t DRI/t LS)", "POSTED rows 24/25/27,17/18/20; V2OBS012", "candidate_theta"),
    ("POSTED_BOTTOMUP_PURCHASEDH2_HOT", "steel_h2dri", "electricity_high", round(bottom_up_hot_hi, 3), "MWh/t_LS", "purchased",
     f"EAF 0.753 + {dri_elec_hi:.3f} + {dri_heat_hi:.3f}", "same", "candidate_theta"),
    ("GCAM_PUBLIC_ZANG_75DRI_25SCRAP", "steel_h2dri", "hydrogen", round(GCAM["h2_gj"] / 0.12, 1), "kgH2/t_GCAM_steel", "purchased", "7.3GJ / 0.12GJ/kg; 83%H2/17%NG reductant energy", "PUBLIC_GCAM2026_H2DRI_2025", "native_energy_not_plant_purchase_verified"),
    ("GCAM_PUBLIC_ZANG_75DRI_25SCRAP", "steel_h2dri", "electricity", round(GCAM["elec_gj"] / 3.6, 3), "MWh/t_GCAM_steel", "purchased", "4.2GJ/3.6", "PUBLIC_GCAM2026_H2DRI_2025", "native_energy_not_plant_purchase_verified"),
    ("GCAM_PUBLIC_ZANG_75DRI_25SCRAP", "steel_h2dri", "gas", GCAM["gas_gj"], "GJ/t_GCAM_steel", "purchased", "native", "PUBLIC_GCAM2026_H2DRI_2025", "native_energy_not_plant_purchase_verified"),
    ("GCAM_PUBLIC_ZANG_75DRI_25SCRAP", "steel_h2dri", "refined_liquids", GCAM["liq_gj"], "GJ/t_GCAM_steel", "purchased", "native", "PUBLIC_GCAM2026_H2DRI_2025", "native_energy_not_plant_purchase_verified"),
    ("FORECAST_SITES_DRI_H2", "steel_h2dri", "hydrogen", round(6.817484 / 0.12, 1), "kgH2/t", "purchased", "fuel_demand 6.817GJ/t as H2 at 0.12GJ/kg; whether EAF is inside this row is unverified", "forecast_sites id_process38", "reference_only_boundary_unverified"),
    ("FORECAST_SITES_DRI_H2", "steel_h2dri", "electricity", round(1.7 / 3.6, 3), "MWh/t", "purchased", "1.7GJ/t; too low to include EAF, so treated as DRI step only", "forecast_sites id_process38", "reference_only_boundary_unverified"),
    ("PIMM_HOTDRI_OXYFUEL_50SCRAP", "steel_h2dri", "hydrogen_internal", 25.2, "kgH2/t_LS", "internal", "50% scrap charge, onsite electrolysis", "V2OBS023", "reference_only_scrap_share_differs"),
    ("PIMM_HOTDRI_OXYFUEL_50SCRAP", "steel_eaf", "electricity", 0.425, "MWh/t_LS", "purchased", "oxy-fuel EAF, 100% scrap, Heat Treat Consortium", "V2OBS020", "alternative_furnace_spec"),
    ("VOGL_EAF_SCRAP", "steel_eaf", "electricity", EAF_SCRAP, "MWh/t_LS", "purchased", "100% scrap, matches FIN 0.667", "V2OBS005", "match"),
    ("FIN_CURRENT", "steel_h2dri", "electricity", 0.85, "MWh/t", "purchased", "D3 elec_intensity; 'ex-electrolyser' but not reproducible from Vogl", "D3_tech_options", "not_derivable"),
    ("FIN_CURRENT", "steel_h2dri", "hydrogen", 51.0, "kg/t", "purchased", "D3 h2_intensity; valid for 0% scrap pellet feed only", "D3_tech_options", "boundary_conditional_match"),
    ("POSCO_COMPANY_2024", "BF_incumbent", "coking_coal", round(POSCO["coal_t_per_t_crude"] * 28, 2), "GJ/t_crude (28GJ/t engine factor)", "purchased", "22,566kt / 35,048kt crude x 28; company-wide incl. PCI and coke plant", "CE008/CE001", "company_reference"),
    ("POSCO_COMPANY_2024", "BF_incumbent", "natural_gas", round(POSCO["ng_gj_per_t"], 3), "GJ/t_crude", "purchased", "60.99PJ / 35.05Mt", "CE003/CE001", "company_reference"),
    ("POSCO_COMPANY_2024", "BF_incumbent", "electricity", round(POSCO["elec_mwh_per_t"], 3), "MWh/t_crude", "purchased", "10.96PJ / 35.05Mt / 3.6; net of byproduct-gas self-generation", "CE005/CE001", "company_reference"),
    ("FIN_ROUTE_BF", "BF_incumbent", "coking_coal", 13.5, "GJ/t_hot_metal", "purchased", "prepare_raw ROUTE constant, not observed", "prepare_raw.py", "unobserved"),
    ("FIN_ROUTE_BF", "BF_incumbent", "natural_gas", 0.4, "GJ/t_hot_metal", "purchased", "ROUTE constant", "prepare_raw.py", "unobserved"),
    ("FIN_ROUTE_BF", "BF_incumbent", "electricity", 0.08, "MWh/t_hot_metal", "purchased", "ROUTE constant", "prepare_raw.py", "unobserved_but_consistent_with_POSCO"),
    ("NSC_SUPERCOURSE50", "steel_h2inj", "hydrogen", None, "kg/t", "purchased", "Announcement gives 50% CO2 target by FY2050 and 12m3 test furnace; no injection rate", "nsc_h2inj_20230209", "NA_no_primary_quantity"),
]


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    # The original numerical experiments remain traceable; adoption status must
    # not imply a complete purchased-energy balance.
    for i, raw in enumerate(SPECS):
        row=list(raw)
        if row[0].startswith('POSTED_BOTTOMUP'):
            row[8]='held_cross_study_extrema_and_heat_electricity_equivalence'
        if row[0].startswith('GCAM_PUBLIC'):
            row[5]='native_energy_flow'
        if row[0].startswith('VOGL_H2DRI_PURCHASEDH2'):
            row[8]='boundary_experiment_heat_unresolved'
        SPECS[i]=tuple(row)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["spec_id", "fin_tech", "carrier", "value", "unit", "role", "derivation", "evidence_ids", "status", "automatically_adopted"])
        for s in SPECS:
            w.writerow(list(s) + [False])
    md = f"""# 철강 공정수지: 사양 집합 (회차 2, 2026-09-07)

같은 기술명 아래 서로 다른 공정 경계의 수치를 평균하지 않는다. 각 사양은 하나의 일관된 경계이며 θ 대안으로 비교한다. 재생성: `scripts/build_steel_specifications.py`. FIN/EFF 입력 변경 없음, 자동 채택 0.

## 수소환원제철(steel_h2dri) 구매수소 경계의 전력

| 사양 | 전력 MWh/t | 수소 kg/t | 경계 |
|---|---:|---:|---|
| Vogl 잔여(현장수전해 총량 − 수전해) 고온 장입 | {residual:.3f} | 51 | 0% 스크랩, l=1.5, 오프가스 열회수 유지, 수전해 폐열 손실 미정량 |
| 같은 사양, 냉간 HBI | {residual + COLD_PENALTY:.3f} | 51 | +0.159 |
| POSTED 상향식(EAF 0.753 + DRI 전력 + H₂ 예열) 고온 | {bottom_up_hot_lo:.3f}–{bottom_up_hot_hi:.3f} | 51–58 | DRI 전력 {dri_elec_lo:.3f}–{dri_elec_hi:.3f}, 예열 {dri_heat_lo:.3f}–{dri_heat_hi:.3f} (t LS 기준, ×{DRI_PER_T_LS}) |
| 공개 GCAM(Zang 2023) 75% DRI + 25% 스크랩 | {GCAM['elec_gj']/3.6:.3f} | {GCAM['h2_gj']/0.12:.1f} (+가스 3.6GJ, 액체 1.1GJ) | 환원에너지 83% H₂/17% NG, 상류 펠릿화 포함 |
| FIN 현행 | 0.85 | 51 | 도출 불가 |

해석 수정: 위 숫자는 검증된 공정 상·하한이 아니다. Vogl 잔여는 수전해 폐열을 제거한 후의 열수지를 완성하지 않았다. POSTED 상향식은 서로 다른 연구의 극값을 결합하고 열을 전력과 1:1로 더한 진단이므로 일관된 설계로 채택할 수 없다. FIN 0.85의 원문 근거는 현재 재현되지 않았다. 수소 51kg/t는 0% 스크랩 펠릿 경계에서만 유효하고, 스크랩 50%면 Vogl 25kg·Pimm 25.2kg으로 절반이 된다. 회사 후보 설비의 스크랩 비율은 미관측이므로 격리 사례에서는 0%와 50%를 θ 대안으로 둔다.

## 기준선 고로(BF_incumbent)

POSCO 2024 회사 전체: 원료탄 {POSCO['coal_t_per_t_crude']:.3f}t/t 조강 = {POSCO['coal_t_per_t_crude']*28:.1f}GJ/t(엔진 28GJ/t 기준), 구매 천연가스 {POSCO['ng_gj_per_t']:.2f}GJ/t, 구매 전력 {POSCO['elec_mwh_per_t']:.3f}MWh/t(부생가스 자가발전 차감 후). FIN ROUTE(13.5·0.4·0.08, t 용선 기준)와 비교하면 표시값의 비율은 비교할 수 있으나 단위 제품과 회사·공정 경계가 달라 이를 정확성 검증이나 일률적인 과소 추정으로 해석하지 않는다. 회사 전체 값이므로 고로 단독 원단위가 아니며, 하공정·코크스·소결 연료를 포함한다. 격리 사례에서는 ROUTE와 POSCO 회사값을 기준선 θ 대안으로 비교한다.

## 수소 취입(steel_h2inj)

NSC 2023-02-09 발표는 Super COURSE50의 12m³ 시험로와 FY2050 50% 감축 목표만 제시하며 취입량(kg/t)을 주지 않는다. FIN 28kg/t는 원 수량이 없으므로 NA 대안을 유지한다. FORECAST의 Blast furnace H2 행도 −99이다.

## 남은 일

Vogl 수전해 폐열 기여 정량화(원문 미기재), 스크랩 비율 관측, 용선/조강 환산, Zang 2023 원문→GCAM 벡터 상세 대응은 미완료다.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    assert abs(residual - 1.119) < 0.002, residual
    assert bottom_up_hot_lo < residual < bottom_up_hot_hi + 0.2
    assert all(s[3] is None or s[3] > 0 for s in SPECS)
    print(f"{len(SPECS)} spec rows; residual {residual:.3f}; bottom-up hot {bottom_up_hot_lo:.3f}-{bottom_up_hot_hi:.3f}")


if __name__ == "__main__":
    main()
