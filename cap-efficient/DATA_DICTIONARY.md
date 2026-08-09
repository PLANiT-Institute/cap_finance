# 데이터 사전

입력 행에는 `data_status`와 `source_note`가 있다. `official` 계열은 기업 원문 수치, `model_estimate`는 공개되지 않은 설비 배분·비용·계약 가정, `model_anchor`는 시나리오 가정을 뜻한다.

## `companies.csv` — 기업 기준점

기업명·국가·기준연도·보고경계와 생산(Mt), Scope 1+2(MtCO₂), 집약도, 2030/2040 앵커, 통화·환율·일본 CAPEX 비용지수, 공식 원문 URL을 보관한다. `capacity_mtpa`는 Nippon Steel을 제외하면 모델 블록 합계일 수 있으므로 `source_note`를 함께 읽어야 한다.

## `facilities.csv` — 시설 블록

| 필드 | 단위 | 설명 |
|---|---|---|
| `capacity_mtpa` | Mt/년 | 모델 명목능력 |
| `utilization_rate` | 0–1 | 기준 생산량을 만드는 가동률 |
| `baseline_technology_id` | 키 | `BF_BOF` 또는 `EAF_BASELINE` |
| `baseline_emissions_tco2_per_t` | tCO₂/t | 기업 총량에 합계되는 보정 집약도 |
| `baseline_electricity_mwh_per_t` | MWh/t | 기준 전력 원단위 추정 |
| `reinvestment_year` | 연도 | 기술전환이 가능한 모델 재투자 창 |

로더는 기업별 `Σ capacity×utilization = 공식 생산`, `Σ output×집약도 = 공식 배출`을 검증한다.

## `scenario_anchors.csv` — 기업별 이정표

키는 `(company_id, scenario_id, year)`다. 탄소예산은 다음 이정표 전까지 유지하고, 전력가격·탄소가격·전해조 지수는 매년 선형 보간한다.

- `DISCLOSED_PATH`: 기업의 2030/2040/2050 공시를 절대량으로 바꾼 경로
- `ACCELERATED_15C`: 공시보다 빠른 감축을 요구하는 내부 모델 스트레스. 공식 GCAM 경로가 아니다.

## `scenario_definitions.csv` — 시나리오 레지스트리

키는 `scenario_id`다. `scenario_family`, `climate_target_c`, `is_active`, 모델·출처 버전, 추출일, 지역경계, 통합상태를 보관한다. `GCAM_15C`와 `GCAM_2C`는 현재 `pending_official_extract`이며 비활성이다. 두 행은 공식 GCAM DB 버전, 실행 configuration, query XML, 원시 추출 CSV와 SHA256을 확보한 뒤에만 활성화한다. `scenario_anchors.csv`의 활성 경로 집합은 이 레지스트리의 `is_active=true` 집합과 정확히 같아야 한다.

## GCAM 재현성 매니페스트

- `gcam_run_manifest.csv`: 공식 릴리스 tag/commit/asset SHA256, configuration·target XML·query hash, 온도목표, 실행 DB·추출 상태
- `gcam_query_manifest.csv`: 시나리오별 필수 출력 10종의 공식 query title, 지역, 원시단위 확인상태, 변환규칙, 출력 파일·SHA256
- `gcam/policy_target_temperature_*.xml`: 공식 GCAM target-finder 스키마를 사용한 프로젝트 실행 설정. JGCRI가 발표한 결과가 아니며 실행·온도 검증 전에는 수치 데이터가 아니다.

## 현실 제약 입력

- `company_constraints.csv`: 회사별 동시공사 상한과 결합 기술실패확률 상한
- `technology_constraints.csv`: 기술별 스크랩 원단위, 독립 실패확률, 최대 지연연도
- `resource_constraints.csv`: 회사×활성시나리오×연도별 스크랩(Mt), 수소(Mt), 증분계통(TWh) 공급 한도. 현재 모두 `model_estimate`이며 이정표 사이를 선형 보간한다.
- `resource_benchmarks.csv`: 공식 국가 자원 맥락. `benchmark_id`, 국가, 자원유형, 연도, 값·단위, 지역·범위, 출처기관·URL·버전·추출일, 데이터 상태와 비교가능성 경고를 보존한다. 값이 없는 `official_qualitative` 행도 허용한다. 모든 행은 국가 맥락이며 회사 공급한도를 대체하지 않는다.

## 공식 전환 프로젝트와 비용 증거

- `transition_projects.csv`: 회사가 공식 발표한 EAF·HyREX·BF 개수·HBI 실증 프로젝트를 별도 증거층으로 보관한다. 용량, 총사업비, 최대 정부지원, 가동시점, 공시 감축률, 원료비중, 의사결정 단계, 출처일·추출일·신뢰등급과 현재 모델 시설의 연결상태를 기록한다. 신규 프로젝트는 생산능력 대체·폐쇄 규칙이 확인되기 전까지 최적화 시설로 자동 편입하지 않는다.
- `technology_cost_evidence.csv`: 공식 프로젝트 총사업비를 KRW bn과 KRW bn/Mtpa로 환산한 관측치다. `included_assets`와 `comparability`가 공시 범위를 명시하며, 부두·물류·전력·후공정·혼합공정을 포함한 총사업비는 `technologies.csv`의 표준화 장비비를 직접 대체하지 않는다.
- `data_gap_registry.csv`: 시설·배출·재투자·기술비용·자원·정책·실행위험·GCAM별 남은 증거 격차, P0/P1 우선순위와 모델 편입 게이트를 관리한다.

## `technologies.csv`

비용 단위는 `bn KRW/Mtpa`, 고정 OPEX는 `kKRW/t`, 전력은 `MWh/t`, 수소는 `tH₂/t`, 배출은 `tCO₂/t`다. BF 블록은 `BF_RELINE`, `SCRAP_EAF`, `H2_DRI_EAF` 중 하나를, 기존 EAF는 `EAF_RENEWABLE`을 선택한다.

## `policy_support.csv`

키는 `(country_code, scenario_id, technology_id)`다. `capex_subsidy_pct`는 기준설비 비용을 초과하는 CAPEX 지원율, `ccfd_opex_support_pct`는 양(+)의 증분 OPEX 보전 한도다. 실제 보전액은 계획별 `ccfd_share`를 다시 곱한다.

## `company_financials.csv`

매출·EBITDA·연간 CAPEX를 KRW 십억원으로 저장한다. 일본 기업의 원문은 JPY이며 `fx_to_krw=9.2`로 환산했다. Nippon Steel과 Kobe Steel EBITDA는 사업/영업이익에 감가상각을 더한 프록시임을 `source_note`에 표시한다.

## `plans.csv`

`company_id=ALL`인 P1–P7은 네 기업에 공통 확장된다. `CURRENT`는 기업별 공시 기술방향을 반영한 프록시다. 실제 미공개 계약비율을 뜻하지 않는다.

## `price_process.json`

전력, 수소 입력비, 건설 CAPEX 로그 충격의 변동성·평균회귀·상관을 정의한다. 수소가격은 `비전력비 + 52kWh/kg×전력가격 + 전해조 비용성분` 구조식으로 계산한다.

## 주요 산출 필드

- `portfolio_id`: 공시경로에서 고정한 시설·기술·전환연도 집합의 SHA256 기반 식별자
- `scenario_feasible`: 탄소예산과 현실 스크리닝 제약을 모두 충족한 통합 적합성
- `carbon_budget_feasible`, `physical_constraints_feasible`: 탄소와 자원·공사·실패 제약의 분리 판정
- `first_resource_breach_year`, `max_scrap_supply_excess_mt`, `max_hydrogen_supply_excess_mt`, `max_incremental_grid_excess_twh`: 공급제약 위반 진단
- `max_concurrent_construction_projects`, `portfolio_failure_probability`, `expected_failure_delay_years`: 공사·기술 실행위험 진단
- `cash_cost_before_support_p50_bn_krw`: 정책지원·탄소가치 전 실제 증분 현금비용 P50
- `net_cash_cost_after_support_p50_bn_krw`: 정책지원 차감 후 실제 순현금비용 P50
- `avoided_carbon_cost_value_p50_bn_krw`: 양(+)으로 표시한 인식 탄소비용 회피가치. 현금수익이 아님
- `absolute_npv_p50_bn_krw`, `absolute_npv_p90_bn_krw`: 탄소가치와 정책지원을 반영한 경제적 순비용 절대 NPV
- `scenario_avoided_emissions_mtco2`, `common_avoided_emissions_mtco2`: 시나리오 고유 분모와 교차시나리오 공통 분모
- `scenario_comparison.csv`: 같은 `portfolio_id`에 대한 `to_scenario − from_scenario` signed 변화
- `cash_policy_p50_nonadditivity_bn_krw`: 서로 다른 분포에서 별도로 계산한 P50은 일반적으로 가산되지 않으므로, `P50(net cash) − [P50(cash before support) − P50(policy)]`를 명시한 감사 차이
- `economic_cost_p50_identity_delta_bn_krw`: `P50(economic cost) − [P50(net cash) − P50(avoided carbon value)]`; 0 근처여야 하는 비용 정의 점검값

## 생성 후보 산출물

- `candidate_portfolios.csv`: 910개 생성 의사결정 패키지. `candidate_id`는 계약조건까지, `physical_portfolio_id`는 시설·기술·전환연도만 식별한다. `action_signature`로 시설별 전환을 사람이 감사할 수 있다.
- `candidate_screening.csv`: 모든 후보×활성 시나리오의 중앙가격 비용과 탄소·물리 제약 진단. 확률 P50이 아니라 1차 스크리닝 값이다.
- `candidate_scenario_metrics.csv`: 선별 후보의 시나리오별 Monte Carlo 지표. 후보당 경로 수는 `run_summary.json`의 `candidate_path_count`로 확인한다.
- `candidate_robust_summary.csv`: 시나리오별 후회비용, 최대·평균후회, 최악 TCaR, 전 시나리오 적합성, 강건경계, λ=0/1/4 추천 플래그.
- `candidate_scenario_comparison.csv`: 동일 `candidate_id`·`physical_portfolio_id`에 대한 `to − from` signed ΔP50(공통분모), ΔTCaR, Δ절대 NPV, ΔCAPEX, Δ순현금비용, Δ탄소가치, Δ정책지원. 동일 물리패키지 비교이므로 ΔCAPEX는 0이어야 한다.
- `refined_candidate_scenario_metrics.csv`: 중앙가격으로 seed와 무관하게 고정한 shortlist의 요청 전체 경로 재평가. `refinement_shortlist_rank`, `candidate_path_count`, 기존 단독분산 비중과 `*_shapley_variance_share`, `shapley_full_variance`, `shapley_reconciliation_delta`를 함께 보존한다. Shapley 값은 동일 seed 공통난수로 3요인의 모든 8개 부분집합을 평가한다.
- `refined_candidate_robust_summary.csv`, `refined_candidate_scenario_comparison.csv`: 정밀 shortlist 안에서 다시 계산한 최대후회·강건경계·λ 추천 및 동일 후보 signed 변화. 최대후회 기준점은 전체 910개가 아니라 이 shortlist의 시나리오별 최저 적격안이다.
- `refined_candidate_facility_schedule.csv`: 정밀 후보×시나리오×시설의 기술·전환연도·CAPEX·순현금·탄소가치·경제 NPV·감축량.
- `refined_candidate_resource_profile.csv`: 정밀 후보×시나리오×연도의 스크랩·수소·증분계통 수요, 공급, 여유, 활용률과 적격성.

`repeat_candidate_*`와 `repeat_refined_candidate_*` 파일은 여러 seed의 평균·표준편차와 선택 빈도를 보존한다. 생성 후보는 기업 공시사업 목록이 아니라 `model_generated_candidate`이므로 승인용 사업계획으로 읽지 않는다.
