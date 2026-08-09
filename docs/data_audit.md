# 데이터 진위·활용 감사 (scripts/audit_data.py 자동 생성)

입력 9개 파일 / 컬럼 88개.

| 판정 | 개수 | 뜻 |
|---|---|---|
| ok | 67 | 채워져 있고 엔진이 참조 |
| CONSTANT | 2 | 전 행 동일값 — 변수 아님(자리표시자 의심) |
| UNUSED | 11 | 수집했으나 엔진이 안 읽음 |
| PARTIAL | 6 | 일부 행이 빈칸 — 보간·집계에서 조용히 번진다 |
| EMPTY | 2 | 스키마 필수인데 전부 빈칸 |
| EMPTY-extra | 0 | 스키마 외 빈 컬럼 |

## EMPTY

| 파일 | 컬럼 | 채움% |
|---|---|---|
| D1b_facility_panel | energy_naphtha | 0.0 |
| D7_disclosed_plan | coverage_pct | 0.0 |

## PARTIAL

| 파일 | 컬럼 | 채움% |
|---|---|---|
| D2b_scenario_prices | value | 99.1 |
| D6_company_financials | revenue | 95.5 |
| D6_company_financials | capex_total | 50.0 |
| D6_company_financials | net_debt | 40.9 |
| D7_disclosed_plan | facility_id | 66.7 |
| D7_disclosed_plan | tech_id | 66.7 |

## UNUSED

| 파일 | 컬럼 | 채움% |
|---|---|---|
| D1a_facility_static | site | 100.0 |
| D1a_facility_static | commissioning_year | 60.9 |
| D1b_facility_panel | emissions_s2 | 100.0 |
| D2a_scenario_budget | gcam_version | 100.0 |
| D3_tech_options | capex_uncertainty | 100.0 |
| D5_policy_support | param_type | 100.0 |
| D6_company_financials | total_debt | 40.9 |
| D6_company_financials | interest_expense | 9.1 |
| D6_company_financials | cash | 45.5 |
| D7_disclosed_plan | resolution | 100.0 |
| D7_disclosed_plan | quote | 100.0 |

## CONSTANT

| 파일 | 컬럼 | 채움% |
|---|---|---|
| D5_policy_support | support_scenario | 100.0 |
| D5_policy_support | tech_id | 100.0 |

## 출처·진위 경고

- UNSOURCED: D1b_facility_panel uses 'PREP_ALLOC' (model estimate / not received)
- UNSOURCED: D1b_facility_panel uses 'PREP_BOTTOMUP' (model estimate / not received)
- UNSOURCED: D2a_scenario_budget uses 'EST_D2A_V0' (model estimate / not received)
- UNSOURCED: D2b_scenario_prices uses 'EST_D2B_V0' (model estimate / not received)
