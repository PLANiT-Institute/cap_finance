# 데이터 진위·활용 감사 (scripts/audit_data.py 자동 생성)

입력 9개 파일 / 컬럼 88개.

| 판정 | 개수 | 뜻 |
|---|---|---|
| ok | 68 | 채워져 있고 엔진이 참조 |
| CONSTANT | 0 | 전 행 동일값 — 변수 아님(자리표시자 의심) |
| UNUSED | 0 | 수집했으나 엔진이 안 읽음 |
| PARTIAL | 4 | 일부 행이 빈칸 — 보간·집계에서 조용히 번진다 |
| EMPTY | 0 | 스키마 필수인데 전부 빈칸 |
| EMPTY-extra | 0 | 스키마 외 빈 컬럼 |
| 설계상 정상 | 16 | 비었거나 안 쓰이는 것이 맞는 컬럼 — 사유 기재 |

## PARTIAL

| 파일 | 컬럼 | 채움% | 사유·비고 |
|---|---|---|---|
| D2b_scenario_prices | value | 99.1 |  |
| D6_company_financials | revenue | 95.5 |  |
| D6_company_financials | capex_total | 50.0 |  |
| D6_company_financials | net_debt | 40.9 |  |

## 설계상 정상

| 파일 | 컬럼 | 채움% | 사유·비고 |
|---|---|---|---|
| D1a_facility_static | site | 100.0 | 시설 부지명 — 시설 단위 비공개 원칙(§8-2)상 모형이 읽지 않는 것이 맞다. |
| D1a_facility_static | commissioning_year | 60.9 | **준비 단계에서 소비**된다(prepare_raw: 2027년 이후 신설 제외, 재투자 창 결측 보정). 엔진이 직접 읽지 않을 뿐 버려지는 값이 아니다. |
| D1b_facility_panel | emissions_s2 | 100.0 | 수집·보존하되 지표 경계는 Scope 1이다(A-21). 예산이 기업 자체 base에 앵커되므로 수준 중립이고, 넣으면 전기화가 더 유리해지는 방향의 구조 대안. |
| D1b_facility_panel | energy_naphtha | 0.0 | 석화 원료비는 물량×가격이 아니라 **에틸렌-납사 스프레드 마진**(D1a margin_kthou_t)으로 들어온다 — 전환 계획이 원료를 바꾸지 않는 한 증분비용에서 상쇄된다. 다만 원료가격 변동은 TCaR에 잡히지 않는다(한계로 기재). |
| D2a_scenario_budget | gcam_version | 100.0 | 출처 추적용 라벨. EST_v0 잠정이라 전 행 동일한 것이 맞다. |
| D5_policy_support | support_scenario | 100.0 | 수집된 지원 시나리오가 `current` 하나뿐이라 전 행 동일한 것이 맞다. **확정된 직접 지원이 없다는 것 자체가 발견**이다(PREP_LOG D5). |
| D5_policy_support | tech_id | 100.0 | 수집된 정책이 전부 업종 전반(`all`) 적용이라 기술별 값이 없다 — 기술 특정 지원이 존재하지 않는다는 뜻. |
| D5_policy_support | param_type | 100.0 | **준비 단계에서 소비**된다 — `_instrument`가 이 값으로 유상할당/상한/하한을 분류하고, 엔진은 분류된 `instrument`를 읽는다. |
| D6_company_financials | total_debt | 40.9 | `net_debt`(= total_debt − cash)가 지표 ⑥에 쓰이고 이 컬럼은 그 구성요소다. POSCO·LOTTE 미확보는 단순 미공시가 아니라 **경계 문제**다 — D6의 POSCO 행은 철강 별도(매출 37.6조)인데 DART에서 바로 얻히는 것은 홀딩스 연결(자산 103조) 또는 홀딩스 별도(순수지주)여서 EBITDA 분모와 어긋난다. 맞지 않는 수를 넣느니 비워 둔다. |
| D6_company_financials | interest_expense | 9.1 | 이자보상배율용이나 22행 중 2행만 공시돼 지표를 만들 수 없다. **공시 부재가 기록으로 남는 편이 낫다.** |
| D6_company_financials | cash | 45.5 | 위와 같음 — `net_debt`의 구성요소. |
| D7_disclosed_plan | facility_id | 66.7 | `target` 행(회사 전체 목표)은 시설이 없는 것이 정상이다. 채움률 67%는 결손이 아니라 행 종류 구성. |
| D7_disclosed_plan | tech_id | 66.7 | 위와 같음 — `target`·`timing` 행은 기술 특정이 없다. |
| D7_disclosed_plan | coverage_pct | 0.0 | PPA·EPC 커버리지 비율용 컬럼. 현재 수집된 공시에 해당 항목이 없다 — 비어 있는 것이 곧 '그런 공시가 없다'는 발견. |
| D7_disclosed_plan | resolution | 100.0 | 공시 해상도 등급. 엔진 입력은 아니지만 **gap 미산출 사유 판정**의 근거이고 `disclosed_skipped.csv` 해석에 필요하다. |
| D7_disclosed_plan | quote | 100.0 | 공시 원문. 엔진이 읽지 않지만 **검증에서 결정적으로 쓰였다** — 미쓰이 설비집약 공시의 능력·감축량이 여기 있었고 그것으로 NCC 배출계수를 역산했다(H3 §4-1-a). |

## 출처·진위 경고

- UNSOURCED: D1b_facility_panel uses 'PREP_ALLOC' (model estimate / not received)
- UNSOURCED: D1b_facility_panel uses 'PREP_BOTTOMUP' (model estimate / not received)
- UNSOURCED: D2a_scenario_budget uses 'EST_D2A_V0' (model estimate / not received)
- UNSOURCED: D2b_scenario_prices uses 'EST_D2B_V0' (model estimate / not received)
