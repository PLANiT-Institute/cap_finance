# 한·일 철강 Capital Allocation Pathway

POSCO와 일본의 Nippon Steel, JFE Steel, Kobe Steel을 같은 구조로 비교하는 탈탄소 자본배분 모델이다. 기업이 공개한 생산·Scope 1+2·재무 총량을 기준점으로 고정하고, 설비 블록·전환시점·기술비용·계약·정책지원은 행 단위로 `model_estimate`를 표시한다.

핵심 지표는 실제 순현금비용, 탄소비용 회피가치, 정책지원, 경제적 순비용(P50), `TCaR = P90−P50`, 경로 적합성, P90 비용/EBITDA다. 모든 기업의 통화는 KRW 십억원으로 비교하며 일본 3사는 모델 환율 `1 JPY = 9.2 KRW`를 적용한다.

## 실행

Python 3.11 이상만 필요하고 외부 패키지는 없다.

```bash
python3 -m cap_efficient validate-data
python3 scripts/validate_gcam_manifest.py
python3 -m cap_efficient run --paths 1000 --seed 42
python3 -m cap_efficient dashboard --paths 1000 --seeds 40,41,42
```

독립 실행형 의사결정 화면은 한국어 `outputs/dashboard.html`과 영어 `outputs/dashboard_en.html`로 동시에 생성된다. 두 파일의 상단 언어 링크로 전환할 수 있으며 모델 결과와 내장 데이터는 동일하다. 기업·시나리오·계획을 바꾸면 연간 배출경로, 효율경계 판정, 설비별 전환지도, P50 비용 브리지와 TCaR 요인분해가 함께 갱신된다. 실행 결과는 다음과 같다.

- `plan_metrics.csv`: 기업×시나리오×계획별 P50, TCaR, 정책·재무 지표
- `facility_schedule.csv`: 시설 블록별 배출·기술·전환연도·CAPEX·기준가격 NPV 상세
- `frontier_membership.csv`: 기업별 효율경계 포함 여부
- `scenario_comparison.csv`: 동일 고정 포트폴리오의 시나리오 간 signed ΔP50·ΔTCaR·ΔNPV·ΔCAPEX
- `scenario_registry.json`: 활성·비활성 시나리오, 모델/버전/지역/추출일/출처 상태
- `gcam_manifest_validation.json`: 공식 릴리스·target XML·query·추출파일·SHA256 활성화 게이트
- `run_summary.json`: 공시전략 gap과 위험회피도별 최적 대안
- `frontier_<기업>_<시나리오>.svg`: 기업 고유 효율경계
- `repeat_plan_summary.csv`: seed 반복 평균·표준편차와 P50 비용 구성요소
- `repeat_seed_results.csv`, `repeat_scenario_comparison.csv`, `repeat_summary.json`: 반복 안정성·교차시나리오 변화 및 HTML 내장 데이터
- `candidate_portfolios.csv`, `candidate_screening.csv`: 910개 생성 후보의 고정 설비패키지와 전 시나리오 결정론 스크리닝
- `candidate_scenario_metrics.csv`, `candidate_robust_summary.csv`: 선별 후보의 확률평가와 최대후회·최악 TCaR·강건경계·위험회피도별 추천
- `candidate_scenario_comparison.csv`: 동일 후보의 시나리오 이동에 대한 signed ΔP50·ΔTCaR·ΔNPV·ΔCAPEX
- `refined_candidate_scenario_metrics.csv`, `refined_candidate_robust_summary.csv`: 중앙가격으로 고정한 상위 후보의 요청 전체 경로 재평가·정확한 3요인 Shapley 분산배분·강건 추천
- `refined_candidate_facility_schedule.csv`, `refined_candidate_resource_profile.csv`: 정밀 후보별 시설 액션과 연도별 스크랩·수소·증분계통 수요/공급/여유
- `data/resource_benchmarks.csv`: 한국·일본 정부·공공기관의 수소·계통·스크랩 공식 국가 벤치마크. 회사별 공급한도를 대체하지 않는 별도 감사층이다.
- `data/transition_projects.csv`: POSCO·Nippon Steel·JFE Steel·Kobe Steel의 공식 EAF·HyREX·BF/HBI 프로젝트 9건과 모델 시설 연결상태.
- `data/technology_cost_evidence.csv`: 프로젝트 총사업비·지원액·용량을 공통 KRW/Mtpa로 환산한 7개 비용 증거와 범위 비교가능성 경고.
- `data/data_gap_registry.csv`, `outputs/data_depth_assessment.json`: 입력별 증거성숙도와 P0/P1 보강 우선순위.

테스트:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_bilingual_dashboard.py
```

## 검증 가능한 Excel → CSV 왕복

기준 CSV를 공식 출처·수식 검증이 포함된 Excel 감사본으로 만들고, 그 Excel의 원천 탭에서 실행용 CSV를 다시 생성할 수 있다.

```bash
/Users/jinsu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  scripts/build_data_audit_workbook.mjs

/Users/jinsu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  scripts/export_verified_csv.py \
  --workbook outputs/data_audit/Capital_Allocation_Baseline_Audit.xlsx \
  --source-dir data \
  --output-dir outputs/data_audit/csv_export \
  --audit-json outputs/data_audit/roundtrip_audit.json

python3 -m cap_efficient validate-data --data-dir outputs/data_audit/csv_export
```

`roundtrip_audit.json`은 행·열·값의 의미상 동일성 및 SHA256을 기록한다. 감사본은 원천 CSV 컬럼을 각 탭의 왼쪽에 그대로 유지하고, 오른쪽에만 수식 검증열을 추가하므로 재생성 CSV에 감사열이 섞이지 않는다.

## 시나리오 출처와 활성화 규칙

`data/scenario_definitions.csv`가 시나리오의 단일 레지스트리다. 현재 실행되는 경로는 기업 공시경로와 내부 1.5°C 스트레스뿐이다. `GCAM_15C`와 `GCAM_2C`는 공식 DB 추출을 받을 자리만 만든 `pending` 비활성 행이며 수치 앵커가 없다. `gcam_run_manifest.csv`와 `gcam_query_manifest.csv`는 GCAM 9.1 공식 릴리스 자산 SHA256, 프로젝트 target XML, 필수 쿼리 10종, 원시단위·변환·추출상태를 별도로 감사한다. 공식 arm64 바이너리는 확인했으나 현재 호스트에 JVM이 없어 `libjvm.dylib` 로딩 단계에서 실행이 중단된다. 성공한 target-finder 실행, 온도 기준 검증, DB/CSV hash가 모두 없으면 공식 경로는 활성화되지 않는다.

공식 구조 근거는 [GCAM 정책·기후 제약](https://jgcri.github.io/gcam-doc/policies.html), [Hector 온도 모듈](https://jgcri.github.io/gcam-doc/hector.html), [철강 부문 기술 구조](https://jgcri.github.io/gcam-doc/demand_energy.html), [DB 분석·추출 도구](https://jgcri.github.io/gcam-doc/dev-guide/analysis.html)다. 이 문서들은 모델 기능의 근거이지 프로젝트의 기업별 GCAM 수치를 제공하는 데이터셋은 아니다.

## 데이터 경계

| 기업 | 기준연도 | 공식 생산 | 모델 기준 Scope 1+2 | 주의할 경계 |
|---|---:|---:|---:|---|
| POSCO | 2025 | 34.537 Mt | 69.846 Mt | 국내 사업장·별도 재무 |
| Nippon Steel | FY2024 | 34.30 Mt | 72.6 Mt | 일본 모회사 상공정·연결 재무 |
| JFE Steel | FY2024 | 21.95 Mt | 45.3 Mt | 비연결 철강 환경값·JFE 연결 재무 |
| Kobe Steel | FY2024 | 5.96 Mt | 14.3 Mt | 14.3Mt는 감축목표 경계·연결 재무 |

원문 URL과 경계 메모는 `data/companies.csv` 및 HTML 하단에 포함된다. 시설별 생산·집약도는 위 공식 총량에 정확히 합계되도록 배분했지만 개별 시설의 실제 공개값을 의미하지 않는다.

## 계산 흐름

```text
기업 공식 총량 + 시설 블록 + 시나리오 앵커 + 기술비용 + 정책 + 재무
                                 │
                                 ▼
       기업 공시경로에서 탄소예산을 지키는 기술 조합 완전열거
                                 │
                                 ▼
          설비·기술·전환연도를 포트폴리오 ID로 한 번 고정
                                 │
                                 ▼
 모든 시나리오에 동일 포트폴리오 적용 → 탄소·자원·공사·실패 제약 진단
                                 │
                                 ▼
  전력·수소입력·건설비 상관 Monte Carlo와 계약 헤지 적용
                                 │
                                 ▼
 현금비용 · 탄소회피가치 · 정책지원 · P50 · TCaR · signed delta
```

현재 탄소예산은 2030/2035/2040 이정표 사이에서 계단식으로 유지한다. 전력·탄소가격·전해조 비용지수는 이정표 사이를 선형 보간한다.

비용 항등식은 `경제적 순비용 = 실제 증분 현금비용 − 정책지원 − 인식된 탄소비용 회피가치`다. 탄소회피가치는 모델의 경제적 가치이며 현금수익으로 해석하지 않는다. 시나리오 고유 회피배출 분모와 공시경로 포트폴리오의 공통 분모를 모두 보존하고, 절대 P50/P90 NPV도 함께 출력한다.

후보 생성기는 공통 P1–P7의 전환연도·계약 프로필과 시설별 기술조합을 결합해 910개 의사결정 패키지를 만든다. 모든 후보는 두 활성 시나리오에 동일하게 적용해 먼저 결정론 스크리닝하고, 회사당 최대 64개를 100개 확률경로로 1차 평가한다. 이어 중앙가격 기준으로 seed와 무관하게 고정한 강건·시나리오 최저 후보를 요청된 전체 경로 수로 재평가하고 전력·수소입력·건설비의 정확한 Shapley 분산배분과 시설·자원 프로필을 붙인다. 최대후회는 각 시나리오 최저 feasible P50 대비 추가비용의 최댓값이며, 강건경계는 `최대후회비용`과 `최악 TCaR`가 동시에 비지배인 후보 집합이다. 위험회피도 λ 추천은 `최대후회 + λ×최악 TCaR`가 최소인 후보다.

## 제한

- `ACCELERATED_15C`는 GCAM 산출이 아니라 공시경로를 앞당긴 내부 스트레스 가정이다. 공식 GCAM 1.5°C·2.0°C는 아직 비활성이다.
- 공식 GCAM 9.1 Mac 바이너리는 arm64와 릴리스 hash를 확인했지만 Java 런타임이 없어 수치 target run은 아직 수행되지 않았다. 이 제약을 해소해도 온도 도달 검증과 DB/query export hash가 추가로 필요하다.
- 완전열거는 17개 시설을 기업별 3~5개 블록으로 나눠 계산한다. 대규모 실제 설비 패널은 MILP로 바꿔야 한다.
- 전체 후보 확률평가는 계산량을 통제하기 위해 회사당 최대 64개·후보당 100개 경로로 제한한다. 최종 정밀 shortlist만 기준 P1–P7과 같은 요청 전체 경로 수를 사용한다. 따라서 전체 910개 후보가 동일한 확률 정밀도로 평가된 것은 아니다.
- 스크랩·수소·증분계통, 동시공사, 기술실패·최대지연은 현재 명시적 `model_estimate` 스크리닝 제약이다. 공식 공급·현장 공정자료로 보정되기 전 승인용 제약이 아니다.
- 제품 믹스와 생산량 내생성은 아직 제약식에 없다.
- 결과는 투자 의견이나 목표주가가 아니라 데이터 구조와 상대 민감도 검증용이다.
