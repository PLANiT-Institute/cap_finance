"""Naphtha steam-cracker process specification set (research_v2, cycle 3 of 2026-09-07).

All quantities per t ethylene unless stated (D1a NCC capacity unit is t ethylene/yr).
Specifications are alternative theta with explicit boundaries; never averaged.
Nothing here mutates FIN/EFF inputs.

Sources (local copies, tmp/pdfs, untracked):
  Layritz et al. 2021 preprint A.2/A.3 (LAY001-LAY027)
  Sinn et al., Linde Engineering, CEP Aug 2024 p47-49 (three heat-integration approaches)
  FORECAST-Sites steam cracking row (id_process 100)
  Lotte Chemical ESG 2025 site energy (CE014, CE015)

Output: data/research_v2/technology_packages/petchem_specifications.csv
        docs/research_cycles/2026-09-07/PETCHEM_PROCESS_BALANCE.md
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/research_v2/technology_packages/petchem_specifications.csv"
OUT_MD = ROOT / "docs/research_cycles/2026-09-07/PETCHEM_PROCESS_BALANCE.md"

NAPHTHA_T = 3.58           # LAY001 t naphtha / t ethylene
FURNACE_MWH = 6.78         # LAY014 fired furnace heat, internal methane
BASE_ELEC = 0.21           # LAY013 purchased electricity, conventional
CH4_FUEL = 0.488           # LAY015 t CH4 burned internally
CH4_EXPORT_BASE = 0.057    # LAY016
CH4_EXPORT_ELEC = 0.55     # LAY023 (rounded; 0.545 in system expansion)
ELEC_TOTAL_LAYRITZ = 6.99  # LAY021
LHV_CH4_GJ_PER_T = 50.0    # rounded LHV, check only
LHV_H2_GJ_PER_KG = 0.120
FORECAST = {"fuel_gj": 33.94, "elec_gj": 1.56, "feed_gj": 102.5}
# Linde CEP 2024, Figure 8 / text: specific power of coilbox + heat-integration unit, and net VHP steam surplus, per t naphtha
LINDE = {"A1_keep_steam": (1.26, 0.5), "A2_reduced_steam": (1.06, 0.2), "A3_min_steam": (0.85, 0.01)}
FIN = {"gas_gj": 8.0, "elec": 0.35, "ecracker_elec": 2.8, "hybrid_elec": 1.0, "h2fuel_kg": 83.0, "hp_whr_elec": 0.19}
LOTTE = {"yeosu_tj": 52_707, "yeosu_cap_t": 1_230_000, "daesan_tj": 44_385, "daesan_cap_t": 1_100_000}

furnace_gj = FURNACE_MWH * 3.6
ch4_check_gj = CH4_FUEL * LHV_CH4_GJ_PER_T
h2_50pct_layritz = 0.5 * furnace_gj / LHV_H2_GJ_PER_KG
h2_50pct_forecast = 0.5 * FORECAST["fuel_gj"] / LHV_H2_GJ_PER_KG
linde_per_t_eth = {k: (v[0] * NAPHTHA_T, v[1] * NAPHTHA_T) for k, v in LINDE.items()}

SPECS = [
    ("LAYRITZ_NCC_BASE", "NCC_incumbent", "naphtha", NAPHTHA_T, "t/t_eth", "purchased_feedstock", "A.2", "LAY001", "reference"),
    ("LAYRITZ_NCC_BASE", "NCC_incumbent", "electricity", BASE_ELEC, "MWh/t_eth", "purchased", "A.2; steam-driven compressors", "LAY013", "reference"),
    ("LAYRITZ_NCC_BASE", "NCC_incumbent", "furnace_heat", round(furnace_gj, 1), "GJ/t_eth", "internal", f"6.78MWh x3.6; consistent with 0.488t CH4 x50GJ/t = {ch4_check_gj:.1f}GJ", "LAY014,LAY015", "reference"),
    ("LAYRITZ_NCC_BASE", "NCC_incumbent", "purchased_gas", None, "GJ/t_eth", "purchased", "Furnace fired by internal methane; purchased-gas share not given by Layritz. Linde: 'methane fraction byproduct and natural gas'", "LAY015; linde p42", "NA_not_observed"),
    ("LAYRITZ_NCC_BASE", "NCC_incumbent", "methane_export", CH4_EXPORT_BASE, "tCH4/t_eth", "potential_export", "A.2", "LAY016", "reference"),
    ("FORECAST_STEAM_CRACKING", "NCC_incumbent", "fuel", FORECAST["fuel_gj"], "GJ/t_eth", "fuel_unspecified_origin", "fuel_demand; internal/purchased split not given", "id_process100", "reference_boundary_unverified"),
    ("FORECAST_STEAM_CRACKING", "NCC_incumbent", "electricity", round(FORECAST["elec_gj"] / 3.6, 3), "MWh/t_eth", "purchased", "1.56GJ/3.6", "id_process100", "reference"),
    ("FIN_ROUTE_NCC", "NCC_incumbent", "purchased_gas", FIN["gas_gj"], "GJ/t_eth", "purchased", "prepare_raw ROUTE constant, not observed; 1/3 of Layritz furnace duty and booked as purchased", "prepare_raw.py", "unobserved_boundary_mismatch"),
    ("FIN_ROUTE_NCC", "NCC_incumbent", "electricity", FIN["elec"], "MWh/t_eth", "purchased", "ROUTE constant", "prepare_raw.py", "unobserved_order_of_magnitude_ok"),
    ("LOTTE_SITE_2024", "NCC_incumbent", "site_energy_per_capacity_yeosu", round(LOTTE["yeosu_tj"] * 1e3 / LOTTE["yeosu_cap_t"], 1), "GJ/t_eth_capacity", "site_total", "52,707TJ / 1.23Mt; whole site incl. downstream polymers; K-ETS counts internal fuel gas", "CE014", "capacity_ratio_not_process_intensity_or_bound"),
    ("LOTTE_SITE_2024", "NCC_incumbent", "site_energy_per_capacity_daesan", round(LOTTE["daesan_tj"] * 1e3 / LOTTE["daesan_cap_t"], 1), "GJ/t_eth_capacity", "site_total", "44,385TJ / 1.1Mt", "CE015", "capacity_ratio_not_process_intensity_or_bound"),
    ("LAYRITZ_NCC_ELECTRIC", "petchem_ecracker", "electricity", ELEC_TOTAL_LAYRITZ, "MWh/t_eth", "purchased", "A.3 total; furnace 6.78 replaces fired duty 1:1 (equal efficiency assumption) + 0.21", "LAY021,LAY022", "published_equal_efficiency_spec_not_upper_bound"),
    ("LAYRITZ_NCC_ELECTRIC", "petchem_ecracker", "methane_export", CH4_EXPORT_ELEC, "tCH4/t_eth", "potential_export", "A.3; +0.49t vs base, netback must be supplied", "LAY023", "candidate_theta"),
]
for k, (p, s) in linde_per_t_eth.items():
    SPECS.append((f"LINDE_2024_{k}", "petchem_ecracker", "electricity_furnace_and_HIU", round(p, 2), "MWh/t_eth",
                  "purchased", f"{LINDE[k][0]}MWh/t naphtha x{NAPHTHA_T}; coilbox+heat-integration only, excludes compressors/separation and the base 0.21", "linde p47-49", "candidate_theta"))
    SPECS.append((f"LINDE_2024_{k}", "petchem_ecracker", "vhp_steam_surplus", round(s, 2), "t_steam/t_eth",
                  "internal_transfer", f"{LINDE[k][1]}t/t naphtha x{NAPHTHA_T}; lower surplus means separation-section steam must be replaced (unquantified)", "linde p47-49", "candidate_theta"))
SPECS += [
    ("LINDE_2024_A3_plus_base", "petchem_ecracker", "electricity_cross_source_experiment", round(linde_per_t_eth["A3_min_steam"][0] + BASE_ELEC, 2), "MWh/t_eth", "purchased", "0.85x3.58 + 0.21; still excludes replacement of lost steam export", "linde,LAY013", "cross_source_experiment_steam_yield_unresolved"),
    ("FIN_CURRENT", "petchem_ecracker", "electricity", FIN["ecracker_elec"], "MWh/t_eth", "purchased", "D3; below the lowest Linde approach even before adding base electricity", "D3_tech_options", "below_all_primary_specs"),
    ("FIN_CURRENT", "petchem_ecracker_hybrid", "electricity", FIN["hybrid_elec"], "MWh/t_eth", "purchased", "D3 40% blend of a mismatched base", "D3_tech_options", "derived_from_mismatched_base"),
    ("H2FUEL_50PCT_LAYRITZ", "petchem_h2fuel", "hydrogen", round(h2_50pct_layritz, 1), "kgH2/t_eth", "purchased", f"0.5 x {furnace_gj:.1f}GJ / 0.12GJ/kg; displaced fuel is INTERNAL methane, so the saving is surplus methane (0.244t) netback, not purchased gas", "LAY014,LAY015", "candidate_theta"),
    ("H2FUEL_50PCT_FORECAST", "petchem_h2fuel", "hydrogen", round(h2_50pct_forecast, 1), "kgH2/t_eth", "purchased", "0.5 x 33.94GJ / 0.12", "id_process100", "candidate_theta"),
    ("FIN_CURRENT", "petchem_h2fuel", "hydrogen", FIN["h2fuel_kg"], "kg/t_eth", "purchased", "D3; 10GJ of H2 against a 4GJ purchased-gas saving (retained_gas_fraction 0.5 x 8GJ)", "D3_tech_options", "internal_inconsistency"),
    ("MITSUI_OSAKA_2023", "petchem_h2fuel", "fuel_switch_target", None, "", "", "Osaka plan is clean AMMONIA furnace fuel, not hydrogen; quantities not published", "mci_osaka_cn_2023", "NA_different_fuel"),
    ("FIN_CURRENT", "petchem_hp_whr", "electricity", FIN["hp_whr_elec"], "MWh/t_eth", "purchased", "IEA HTHP generic", "D3_tech_options", "no_primary_source"),
]


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["spec_id", "fin_tech", "carrier", "value", "unit", "role", "derivation", "evidence_ids", "status", "automatically_adopted"])
        for s in SPECS:
            w.writerow(list(s) + [False])
    l = linde_per_t_eth
    md = f"""# 나프타 분해 공정수지: 사양 집합 (회차 3, 2026-09-07)

t 에틸렌 기준(D1a NCC 능력 단위). 사양은 θ 대안이며 평균하지 않는다. 재생성: `scripts/build_petchem_specifications.py`. FIN/EFF 무변경, 자동 채택 0.

## 기준선 NCC: 분해로 연료는 구매가스가 아니다

Layritz 2021 A.2: 나프타 3.58t, 구매 전력 0.21MWh, 분해로 열 6.78MWh = {furnace_gj:.1f}GJ/t. 이 열은 내부 부생 메탄 0.488t(×50GJ/t = {ch4_check_gj:.1f}GJ, 질량·열 일치)으로 공급된다. FORECAST-Sites 스팀크래킹은 연료 33.94GJ/t, 전력 {FORECAST['elec_gj']/3.6:.2f}MWh/t. Linde 2024도 "플랜트 메탄 분율 부산물과 천연가스"를 연소한다고 쓴다. 구매 천연가스 비중은 어느 원문에도 없다. FIN ROUTE의 8GJ/t 구매가스는 분해로 열의 1/3 크기이며 전량 구매로 기장한 값이다. 롯데 사이트 에너지(여수기초 {LOTTE['yeosu_tj']*1e3/LOTTE['yeosu_cap_t']:.1f}·대산 {LOTTE['daesan_tj']*1e3/LOTTE['daesan_cap_t']:.1f}GJ/t 에틸렌 능력)는 하공정 포함 에너지/능력 비율이다. 실제 생산량당 NCC 원단위의 상한은 아니다.

## 전기가열 분해로(petchem_ecracker)

| 사양 | 전력 MWh/t 에틸렌 | VHP 증기 잉여 t/t 에틸렌 | 경계 |
|---|---:|---:|---|
| Layritz A.3 | {ELEC_TOTAL_LAYRITZ} | – | 소성 열 6.78을 전기로 1:1 대체 + 0.21; 메탄 수출 0.55t |
| Linde 접근 1(증기 유지) | {l['A1_keep_steam'][0]:.2f} | {l['A1_keep_steam'][1]:.2f} | 코일박스+열통합 유닛만, 1.26MWh/t 나프타 |
| Linde 접근 2 | {l['A2_reduced_steam'][0]:.2f} | {l['A2_reduced_steam'][1]:.2f} | 1.06MWh/t 나프타 |
| Linde 접근 3(증기 최소) | {l['A3_min_steam'][0]:.2f} | {l['A3_min_steam'][1]:.2f} | 0.85MWh/t 나프타; 분리계 증기 대체 필요 |
| Linde 3 + 기본 전력 | {l['A3_min_steam'][0]+BASE_ELEC:.2f} | – | 조건부 사양, 증기 대체 전력 미포함 |
| FIN 현행 | {FIN['ecracker_elec']} | – | 어느 원 연구 사양보다 낮음 |

Linde 값은 원료 t 기준이므로 3.58t 나프타/t 에틸렌으로 환산했다. 낮은 접근일수록 증기 잉여가 사라져 분리계 증기·압축기 구동을 전력으로 대체해야 하므로 플랜트 전체 전력은 표보다 크다. 표시 대안은 {l['A3_min_steam'][0]+BASE_ELEC:.1f}와 {ELEC_TOTAL_LAYRITZ} 등이다. 서로 다른 자료의 수율·기본 전력을 결합했으므로 보편적인 상·하한으로 승인하지 않는다. FIN 2.8의 같은 경계 원문 근거는 아직 재현되지 않았다.

## 수소 연료 전환(petchem_h2fuel)

분해로 열 50% 대체는 Layritz 기준 {h2_50pct_layritz:.0f}kg H₂/t, FORECAST 기준 {h2_50pct_forecast:.0f}kg. FIN 83kg(10GJ)은 8GJ 구매가스의 절반(4GJ)을 대체한다고 가정한 값이라 에너지가 맞지 않는다. 더 중요한 구조 문제: 대체되는 연료가 내부 메탄이면 절감은 구매가스가 아니라 잉여 메탄 0.244t/t의 판매·대체 가치(넷백)다. 판로가 없으면 절감이 0에 가깝다. Mitsui Osaka 계획은 암모니아 연료이며 수소가 아니다.

## 남은 일

구매 천연가스 비중(회사 사이트 자료), 압축기 전기화·증기 대체 전력, Layritz 최종 출판본 대응, Fitriasari 2026 원문(플라즈마·직접가열), 하이브리드 40% 재산출은 미완료다.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    assert abs(ch4_check_gj - furnace_gj) / furnace_gj < 0.01, (ch4_check_gj, furnace_gj)
    assert l["A3_min_steam"][0] + BASE_ELEC > FIN["ecracker_elec"]
    assert h2_50pct_layritz > FIN["h2fuel_kg"]
    print(f"{len(SPECS)} rows; furnace {furnace_gj:.1f}GJ; linde per t eth {[round(v[0],2) for v in l.values()]}; h2 50% {h2_50pct_layritz:.0f}/{h2_50pct_forecast:.0f}kg")


if __name__ == "__main__":
    main()
