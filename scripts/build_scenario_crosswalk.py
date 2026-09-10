"""Scenario crosswalk: current D2 inputs vs expected official GCAM/KAIST and NGFS fields.

Cycle 4 of 2026-09-07. KAIST solved-DB CSV and NGFS numeric data are NOT received
(kaist_gcam_data_received=false; NGFS bulk download requires an e-mail request that
was not submitted). This file therefore records, per D2 variable, what the current
input is, where it came from, and the exact native field / unit / conversion chain
that must be filled when official data arrives. No value is invented.

Output: data/research_v2/gcam_reference/scenario_crosswalk.csv
        docs/research_cycles/2026-09-07/SCENARIO_CROSSWALK.md
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D2A = ROOT / "data/prepared/D2a_scenario_budget.csv"
D2B = ROOT / "data/prepared/D2b_scenario_prices.csv"
OUT_CSV = ROOT / "data/research_v2/gcam_reference/scenario_crosswalk.csv"
OUT_MD = ROOT / "docs/research_cycles/2026-09-07/SCENARIO_CROSSWALK.md"

# Native conventions confirmed from public gcam-core commit 11e128f (A323.sector.csv, A325.sector.csv, zenergy_L2323.iron_steel.R)
GCAM_UNITS = {
    "steel_price": "1975$/kg (supplysector iron and steel)",
    "chemical_price": "1975$/GJ (supplysector chemical / chemical energy use)",
    "energy_input": "EJ (input.unit); coefficients GJ/kg after /1000 in zenergy_L2323",
    "co2_price": "1990$/tC (GCAM CO2 market convention; verify in KAIST export)",
    "emissions": "MtC (GCAM convention; x44/12 -> MtCO2; verify)",
    "time_step": "5-year model periods (2025, 2030, ...); annual values are interpolations",
}
CONVERSION_CHAIN = "native -> verify variable, model, scenario, region, price basis and boundary -> PRICE units: currency/GJ *3.6=currency/MWh; currency/GJ *0.12=currency/kgH2 only with verified LHV120MJ/kg; currency/tC *12/44=currency/tCO2 (QUANTITIES use reciprocal factors) -> currency/base-year bridge with sourced indices and explicit FX convention; constant-price foreign currency must not be multiplied by future nominal FX without inflation treatment -> delivered-price components checked for overlap; no inferred values"

ROWS = [
    # variable, region, current_source(s), current_basis, gcam_native_query, gcam_native_unit, ngfs_variable, status
    ("co2_price", "Korea", "IEA_GECM_DOC_2025 NZE advanced (NZ15); EST_D2B_V0 (B20); 2025 anchor 9,450", "Checked2035/2040/2050 IEA NZE/STEPS electricity-carbon assumptions x1350 KRW/USD; not GCAM", "CO2 price, region South Korea (market 'CO2' or policy-specific)", GCAM_UNITS["co2_price"], "Price|Carbon (US$2010/t CO2)", "no_official_value; KAU25 30,100 KRW (2026-08) already 1.9x above the 2026 interpolated path (docs/price_anchor_check.md)"),
    ("co2_price", "Japan", "IEA_GECM_DOC_2025; EST_D2B_V0; 2025 anchor 27,000 (GX-ETS)", "same as Korea", "CO2 price, region Japan", GCAM_UNITS["co2_price"], "Price|Carbon", "no_official_value"),
    ("elec_price", "Korea", "EST_D2B_V0 (24 rows, all estimate)", "linear estimate from 2025 industrial tariff", "prices by sector: elect_td_ind, South Korea", "1975$/GJ", "Price|Final Energy|Industry|Electricity (US$2010/GJ)", "no_official_value; use GCAM slope only, 2025 level from D4 (decision 5)"),
    ("elec_price", "Japan", "EST_D2B_V0", "estimate", "elect_td_ind, Japan", "1975$/GJ", "Price|Final Energy|Industry|Electricity", "no_official_value"),
    ("re_price", "Korea/Japan", "KR_PPA_2026 / REI_JP_PPA_2025 (104 rows flat)", "flat real PPA anchor 175,000 / 198,000 KRW/MWh", "none (GCAM has no corporate PPA price)", "n/a", "none", "contract_input_not_scenario; keep as D4-anchored contract grid"),
    ("h2_price", "Korea", "MOTIE_H2_PLAN_2021 (2030, 2050) + EST_D2B_V0 interpolation; 2025 NA", "policy target, not market", "prices by sector: H2 industrial (or 'hydrogen' supplysector), South Korea", "1975$/GJ -> price multiplied by LHV 0.12 GJ/kg, if verified", "Price|Secondary Energy|Hydrogen (US$2010/GJ)", "no_official_value; policy targets are not scenario prices"),
    ("h2_price", "Japan", "JP_H2_STRATEGY_2023 + EST_D2B_V0", "policy target", "H2 industrial, Japan", "1975$/GJ", "Price|Secondary Energy|Hydrogen", "no_official_value"),
    ("gas_price", "Korea/Japan", "EST_D2B_V0 + IEA_GECM_DOC_2025 (LNG import, 52.0 MBtu/t)", "IEA regional gas price x fx; same path for both regions", "prices by sector: wholesale gas / delivered gas industrial", "1975$/GJ", "Price|Final Energy|Industry|Gases", "no_official_value; identical KR/JP path is an assumption"),
    ("coal_price", "Korea/Japan", "EST_D2B_V0 + IEA_GECM_DOC_2025", "IEA coal price x fx", "delivered coal (industry), region", "1975$/GJ", "Price|Final Energy|Industry|Solids|Coal", "no_official_value; coking coal is not steam coal - GCAM 'delivered coal' boundary must be checked"),
    ("carbon_budget", "Korea steel/petchem", "EST_D2A_V0 (46/48 rows) + KR_NETZERO_2050 (2050)", "linear to 2050 target; NZ15:=min(NZ15,B20) monotonic fix", "CO2 emissions by sector: iron and steel; chemical (energy use only, decision 2)", GCAM_UNITS["emissions"], "Emissions|CO2|Energy|Demand|Industry (NGFS lacks steel/chemical split at country level)", "no_official_value; sector budget applied via intensity_ratio (config) = e1 company_base x sector_budget/sector_base (code consistent)"),
    ("carbon_budget", "Japan steel/petchem", "EST_D2A_V0", "linear estimate", "same, region Japan", GCAM_UNITS["emissions"], "same", "no_official_value"),
    ("scenario_id", "NZ15", "local label", "1.5C-consistent intent", "KAIST scenario name TBD", "n/a", "NGFS Phase 5 'Net Zero 2050' (REMIND/MESSAGE/GCAM 6.0)", "label_only; map on receipt"),
    ("scenario_id", "B20", "local label", "2C intent", "KAIST scenario name TBD", "n/a", "NGFS Phase 5 'Below 2C'", "label_only; if KAIST has no Below 2C run, relabel (decision 7)"),
    ("tech_availability", "steel_h2dri/hyrex/petchem_ecracker", "D3 avail_year (2030/2035/2030)", "engineering judgement", "technology output by period (Hydrogen-based DRI etc.) in solved DB", "Mt", "none", "decision 6: fill tech_avail from GCAM tech production, separate bundle"),
]


def main():
    d2b = pd.read_csv(D2B)
    d2a = pd.read_csv(D2A)
    est_b = (d2b.source_id == "EST_D2B_V0").sum()
    est_a = d2a.source_id.str.startswith("EST_").sum()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variable", "region", "current_source", "current_basis", "gcam_native_query", "gcam_native_unit", "ngfs_variable", "status", "conversion_chain", "kaist_received", "ngfs_numeric_received"])
        for r in ROWS:
            w.writerow(list(r) + [CONVERSION_CHAIN, False, False])
    md = f"""# 공식 시나리오·GCAM 대응표 (회차 4, 2026-09-07)

KAIST GCAM solved-DB CSV 미수령, NGFS Phase 5 v5.1 수치 미확보(대량 다운로드는 이메일 요청 필요, 미제출). 따라서 이 표는 값을 채운 표가 아니라 **현재 입력의 출처와, 공식 자료 도착 시 채워야 할 네이티브 필드·단위·변환 사슬**을 고정한 표다. 재생성: `scripts/build_scenario_crosswalk.py`.

## 현재 D2의 실체

- D2b 가격 {len(d2b)}행 중 EST_D2B_V0 {est_b}행, re_price 104행은 PPA 계약 앵커(시나리오 아님), 나머지는 IEA GECM 2025·정책 목표. GCAM 유래 값은 0행.
- D2a 예산 {len(d2a)}행 중 추정 {est_a}행. 선형 보간과 NZ15:=min(NZ15,B20) 단조 보정이 들어가 있다.
- 탄소가격 2025 앵커는9,450KRW/tCO2다. 시장 관측과 비교할 때는 관측연도와 전망연도를 맞춰야 한다. 이전 문서의2025앵커 대비1.9배라는 표현은2026보간가격 비교를 혼동한 것이어서 철회한다. 기존 가격 관측 근거는 price_anchor_check.md에서 별도로 추적한다.
- 한·일 가스·석탄 가격이 동일 경로인 것은 가정이다.

## 2026-09-07 실제 회차3의 원문 대조 보완

새로 확보한 IEA2025 본문 표2.3·2.4와 `data/prepared/D2b_scenario_prices.csv`를 대조했다. 확인한 원문 기준값28행은 기존 환율1,350과 가스 열량52millionBtu/t를 적용하면 재현된다. **B20의 확인한 가격은STEPS에, NZ15는NZE에 대응한다.** B20를 검증된2°C 시나리오 또는APS라고 해석하지 않는다. 중간연도까지 포함한36행 중6행은 새로 명시한 선형보간과 달랐다. 대조 산출물은 `data/research_v2/iea_2025_scenarios/legacy_alignment_audit.csv`다.

표2.4의 제목은 전력 부문 탄소가격이다. 철강·석화의 제도별 부담으로 옮기는 근거는 별도로 필요하다. 일본 LNG 통관가격을 한국 공장 인도가격으로, 발전용 석탄을 원료탄으로 옮기는 것도 검증된 매핑이 아니다. 수치 재현과 공정·시나리오 적용의 적격성을 구분한다. WEO2025 본문은APS를 포함하지 않았다고 설명하지만 이 방법론 문서의 표2.4에는APS 가정도 실려 있다. 표2.3에서 확인한 연료 경로는CPS/STEPS/NZE이다.

## GCAM 네이티브 규약(공개 커밋 11e128f에서 확인)

| 항목 | 단위 |
|---|---|
| 철강 가격 | {GCAM_UNITS['steel_price']} |
| 화학 가격 | {GCAM_UNITS['chemical_price']} |
| 에너지 투입 | {GCAM_UNITS['energy_input']} |
| CO₂ 가격 | {GCAM_UNITS['co2_price']} |
| 배출 | {GCAM_UNITS['emissions']} |
| 시간 | {GCAM_UNITS['time_step']} |

변환 사슬: {CONVERSION_CHAIN}

디플레이터 값은 아직 넣지 않았다(출처 확보 전 숫자 금지). 실질 외화 가격은 기준연도 환율을 고정해 실질 원화로 표시하거나, 외화 인플레이션→미래 명목환율→국내 디플레이션의 일관된 사슬로 변환한다. 과거 연평균 환율을 미래 가격에 자동 대입하지 않는다.

2026-09-07 실제 회차3 정정: 이전 사슬은 에너지 수량 환산의 나눗셈을 가격에 섞어 썼다. 가격은 통화/GJ→통화/MWh에3.6을, 통화/GJ→통화/kgH2에 검증된 GJ/kg 열량을 곱한다. 수량 환산은 역수다. 단위 변경 전후 q×P가 같아야 한다. 이 대응표에는 공식 시나리오 수치가 아직 없어 이번 정정으로 기존 FIN 가격을 다시 계산하지 않는다. [NIST 단위 근거](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9)

## 도착 시 첫 5개 확인(메모리 결정)

열·단위·지역(South Korea=28, Japan=19)·연도(5년)·시나리오명. Below 2°C 실행이 없으면 B20 라벨을 바꾼다. 파생값을 GCAM 원값으로 표기하지 않고 EST_v0는 `d2_est_v0` 묶음으로 보존한다. D2 교체는 단독 커밋으로 먼저 하고 before/after 델타를 강건성 축으로 쓴다.

## 대응 행

| 변수 | 지역 | 현재 출처 | GCAM 네이티브 | NGFS 변수 | 상태 |
|---|---|---|---|---|---|
""" + "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[4]} ({r[5]}) | {r[6]} | {r[7]} |" for r in ROWS) + """

## 공정 기술 대응(회차 2·3과 연결)

공개 GCAM `Hydrogen-based DRI`는 75% DRI + 25% 스크랩, 환원에너지 83% H₂/17% NG이므로 FIN의 순수 H₂·0% 스크랩 사양과 같지 않다. GCAM에도 기술 투입계수가 있지만 화학 부문의 EJ/EJ 집계 계수를 특정 나프타 분해로의 t제품당 투입량으로 바로 읽을 수는 없다. 가격·배출계수·부문 경로와 기술 투입계수는 실제 판본·시나리오에서 확인하고, 문헌 공정 사양과 경계를 맞춰 연결한다. 모형에서 생산량이 처음 양수가 되는 연도는 경제적 채택 결과일 수 있으므로 기술적 이용 가능 연도와 같다고 자동 해석하지 않는다. KAIST 수령 전에는 연결 후보이며 검증된 매핑이 아니다.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    assert est_b == 82 and est_a == 46, (est_b, est_a)
    assert (d2b.source_id.str.contains("GCAM", case=False)).sum() == 0
    print(f"{len(ROWS)} crosswalk rows; D2b EST {est_b}/{len(d2b)}, D2a EST {est_a}/{len(d2a)}")


if __name__ == "__main__":
    main()
