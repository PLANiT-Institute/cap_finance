# 데이터 진위·활용 감사 (scripts/audit_data.py 자동 생성)

입력 9개 파일 / 컬럼 88개.

| 판정 | 개수 | 뜻 |
|---|---|---|
| ok | 73 | 채워져 있고 엔진이 참조 |
| CONSTANT | 3 | 전 행 동일값 — 변수 아님(자리표시자 의심) |
| UNUSED | 12 | 수집했으나 엔진이 안 읽음 |
| EMPTY | 0 | 스키마 필수인데 전부 빈칸 |
| EMPTY-extra | 0 | 스키마 외 빈 컬럼 |

## UNUSED

| 파일 | 컬럼 | 채움% |
|---|---|---|
| D1a_facility_static | site | 100.0 |
| D1a_facility_static | commissioning_year | 100.0 |
| D1b_facility_panel | emissions_s2 | 100.0 |
| D1b_facility_panel | energy_naphtha | 100.0 |
| D2a_scenario_budget | gcam_version | 100.0 |
| D3_tech_options | capex_uncertainty | 100.0 |
| D5_policy_support | param_type | 100.0 |
| D6_company_financials | total_debt | 100.0 |
| D6_company_financials | interest_expense | 100.0 |
| D6_company_financials | cash | 100.0 |
| D7_disclosed_plan | resolution | 100.0 |
| D7_disclosed_plan | quote | 100.0 |

## CONSTANT

| 파일 | 컬럼 | 채움% |
|---|---|---|
| D5_policy_support | support_scenario | 100.0 |
| D5_policy_support | instrument | 100.0 |
| D5_policy_support | tech_id | 100.0 |

## 출처·진위 경고

- UNSOURCED: D1b_facility_panel uses 'PREP_ALLOC' (model estimate / not received)
- UNSOURCED: D1b_facility_panel uses 'PREP_BOTTOMUP' (model estimate / not received)
- UNSOURCED: D2a_scenario_budget uses 'EST_D2A_V0' (model estimate / not received)
- UNSOURCED: D2b_scenario_prices uses 'EST_D2B_V0' (model estimate / not received)
