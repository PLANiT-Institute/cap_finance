# 자동 개선 진행 기록

## 1회차 — 2026-08-07 02:10–02:36 KST (약 26분)

### 이번 회차의 목표와 수행 내용

- 기존 `ACCELERATED_15C`가 공식 GCAM 1.5°C 산출값처럼 읽힐 위험을 우선 제거했다.
- `data/scenario_definitions.csv`를 새 단일 시나리오 레지스트리로 만들고 공시경로, 내부 스트레스, 공식 GCAM 1.5°C 대기, 공식 GCAM 2.0°C 대기의 출처·상태·버전·지역·추출일 필드를 분리했다.
- 현재 수치가 있는 `DISCLOSED_PATH`와 `ACCELERATED_15C`만 활성화했다. `GCAM_15C`와 `GCAM_2C`는 공식 DB 추출 전까지 `pending_official_extract`로 비활성화하고 숫자 앵커를 넣지 않았다.
- `ACCELERATED_15C` 화면명과 모든 앵커 라벨을 `내부 1.5°C 스트레스 (비-GCAM)`으로 변경했다.
- 로더에 다음 실행 게이트를 추가했다: 활성 레지스트리와 앵커 집합의 완전 일치, 회사별 시나리오 완전성, 레지스트리-앵커 라벨 일치, 활성 시나리오의 정책지원 조합 완전성, 비활성 시나리오의 숫자 앵커 금지, 공식 GCAM 활성화 시 모델/출처 버전·추출일·`gcam_official*` 상태 의무화.
- 모든 개별 실행에 `scenario_registry.json`을 생성하고, `run_summary.json`에 활성/대기 시나리오 ID를 기록했다. 반복 대시보드 payload에도 전체 레지스트리를 내장했다.
- 대시보드 시나리오 버튼과 하단 출처 경계에 비-GCAM 표기, 선택 시나리오의 데이터 상태, 비활성 GCAM 1.5°C/2.0°C 슬롯을 표시했다.
- 동일한 `plan_id`가 현재 시나리오별로 다시 최적화되어 물리적으로 동일한 계획이 아닐 수 있음을 `METHODOLOGY.md`에 명시했다. 다음 회차의 고정 포트폴리오 재평가 설계를 확정했다.
- Excel 감사본에 `Scenario_Definitions` 시트를 추가하고 긴 출처·주의 문구가 보이도록 열 너비와 행 높이를 조정했다. CSV 매니페스트, 파일 수, Sources의 GCAM 공식 문서 4건, 시나리오 품질평가를 갱신했다.

### 수집·검증한 공식 자료

이번 회차에는 기업별 또는 지역별 GCAM 수치 자체를 수집하지 않았다. 아래 자료로 모델 기능과 향후 추출 절차만 확인했으며, 문서 설명을 숫자로 변환하거나 임의의 1.5°C/2.0°C 값을 만들지 않았다.

| ID | 1차 출처 | 확인 내용 | 수치 사용 여부 |
|---|---|---|---|
| GCAM-POL | https://jgcri.github.io/gcam-doc/policies.html | GCAM은 탄소/GHG 가격, 배출제약, 기후제약을 지원하며 기후목표를 만족하는 가격 경로를 탐색할 수 있음 | 사용 안 함 |
| GCAM-HEC | https://jgcri.github.io/gcam-doc/hector.html | GCAM 배출이 Hector로 전달되고 온도가 계산되며 온도 제약이 가능함 | 사용 안 함 |
| GCAM-STL | https://jgcri.github.io/gcam-doc/demand_energy.html | 철강 부문은 BOF, 스크랩 EAF, DRI-EAF와 수소·전력 등 투입을 경쟁시키고 철강 생산을 Mt 단위로 보고함 | 사용 안 함 |
| GCAM-EXT | https://jgcri.github.io/gcam-doc/dev-guide/analysis.html | ModelInterface, rgcam, gcam_reader 등 DB 결과 추출 경로가 있으며 정확한 query와 DB 버전 고정이 필요함 | 사용 안 함 |

공식 문서는 프레임워크 근거일 뿐 이 프로젝트에 필요한 한국·일본 철강 경로의 수치 export가 아니다. 따라서 GCAM 모델 버전, 실행 configuration, DB/source version, query XML, 추출 CSV, SHA256을 확보하기 전에는 두 GCAM 시나리오를 활성화하지 않는다.

### 변경 파일

- 새 파일: `data/scenario_definitions.csv`, `outputs/automation_progress.md`
- 모델/검증: `cap_efficient/models.py`, `cap_efficient/loader.py`, `cap_efficient/pipeline.py`
- 대시보드: `cap_efficient/dashboard.py`, `cap_efficient/dashboard_template.py`, `cap_efficient/dashboard_script.py`, `data/scenario_anchors.csv`
- 감사·왕복: `scripts/build_data_audit_workbook.mjs`, `scripts/export_verified_csv.py`
- 테스트·문서: `tests/test_pipeline.py`, `README.md`, `DATA_DICTIONARY.md`, `METHODOLOGY.md`
- 재생성 산출물: `outputs/dashboard.html`, `outputs/repeat_summary.json`, 반복 CSV, `outputs/runs/seed_*`, `outputs/report.md`, `outputs/run_summary.json`, `outputs/scenario_registry.json`, 계획/시설/경계 CSV·SVG, `outputs/data_audit/Capital_Allocation_Baseline_Audit.xlsx`, 렌더 PNG, `roundtrip_audit.json`, `model_parity.json`, 기준/왕복 모델 실행 폴더

### 실행한 명령과 검증 결과

- `python3 -m unittest discover -s tests -v`
  - 초기 4개 PASS, 신규 GCAM 오활성화 방지 테스트 추가 후 최종 5개 PASS.
  - `GCAM_2C`를 버전·추출·앵커 없이 활성화한 복제 입력은 의도대로 로더 오류가 발생했다.
- `python3 -m cap_efficient validate-data`
  - 4개 기업, 17개 시설 블록, 6개 기술, 8개 회사-활성시나리오, 32개 회사-계획 검증 PASS.
- `python3 -m cap_efficient dashboard --paths 1000 --seeds 40,41,42`
  - 3회 × 1,000경로, 계획·시나리오당 총 3,000경로 반복 완료.
  - 반복 집계 64행, 활성 시나리오 2개, 비활성 GCAM 슬롯 2개가 payload에 기록됨.
- `python3 -m cap_efficient run --data-dir data --output-dir outputs --paths 1000 --seed 42`
  - 메인 보고서와 실행 산출물 전체 재생성 완료.
- 번들 Node 런타임으로 `scripts/build_data_audit_workbook.mjs` 반복 실행
  - 15개 시트 렌더 완료, 수식 오류 검색 0건.
  - Cover, Scenario_Definitions, Sources 시트를 이미지로 직접 확인하고 긴 필드 폭/행 높이를 보정함.
- 번들 Python 런타임으로 `scripts/export_verified_csv.py` 실행
  - CSV 8개 + JSON 1개, 총 9/9 의미상 왕복 일치 PASS. 원본·export SHA256을 기록함.
- 원본 입력과 Excel 재생성 입력으로 각각 `--paths 100 --seed 42` 모델 실행 후 `scripts/verify_model_parity.py` 실행
  - `plan_metrics.csv`, `facility_schedule.csv`, `frontier_membership.csv` 3/3 바이트·SHA256 동일성 PASS.
- 최신 `dashboard.html` 정적 검증
  - 템플릿 placeholder 없음, `내부 1.5°C 스트레스 (비-GCAM)`, `GCAM_15C`, `GCAM_2C`, `scenario-provenance` 포함 확인.
  - in-app Browser에서 로컬 `file://` 탭 새로고침/DOM 검사는 URL 보안 정책으로 차단되어 이번 회차에는 회귀테스트와 HTML 정적검사로 대체했다.

### 새로 확인한 중요한 문제

1. 현재 최적화는 시나리오마다 기술 조합과 전환연도를 다시 고른다. 따라서 두 점 사이 연결선이나 signed delta를 그리기 전에 동일 액션 집합을 고정해 모든 시나리오에서 재평가하는 계층이 필요하다.
2. `expected_cost / avoided_emissions`의 회피배출 분모가 시나리오·스케줄에 따라 달라져 단위비용 차이가 총 NPV 차이와 반대로 움직일 수 있다. 절대 NPV와 공통 기준 분모를 함께 보존해야 한다.
3. 탄소가격의 45%를 인식된 회피 현금비용으로 차감하는 현재 규칙은 `carbon_value`를 실제 현금수익처럼 오해하게 할 수 있다. 실제 현금비용, 회피가치, 정책지원, 회계/경제가치를 별도 지표로 분리해야 한다.
4. 공식 GCAM 1.5°C/2.0°C 숫자 export와 실행 버전은 아직 없다. 공개 문서의 기능 설명만으로 경로 값을 추정해서는 안 된다.
5. 스크랩, 전력망, 수소공급, 공사기간, 동시공사, 실패/지연 제약과 수백 개 후보 생성은 아직 미구현이다.

### 다음 회차 우선순위

1. 기준 시나리오에서 생성한 `Schedule.actions`를 불변 포트폴리오 ID로 직렬화하고, 그 동일 액션 집합을 공시·내부 스트레스 및 향후 GCAM 경로에 재평가하는 `evaluate_fixed_schedule` 흐름과 교차시나리오 CSV를 구현한다.
2. 절대 P50/P90 NPV, 실제 현금비용, 탄소 회피가치, 정책지원, 공통 회피배출 분모, 시나리오 고유 분모를 분리하고 구성요소 합계·부호 테스트를 추가한다.
3. GCAM 공식 추출 매니페스트 스키마(DB/model version, configuration, query XML, region, variable, unit, extraction date, hashes)를 만들고 재현 가능한 공개 DB/export 후보를 계속 조사한다.
4. 이후 signed ΔP50·ΔTCaR·ΔNPV·ΔCAPEX와 동일계획 연결선을 대시보드에 추가한다.

## 2회차 — 2026-08-07 03:12–03:42 KST (약 30분)

### 이번 회차의 목표와 수행 내용

- 시나리오별 재최적화를 중단하고 회사·계획별 `DISCLOSED_PATH` 물리 포트폴리오를 한 번만 만든 뒤, 동일한 시설·기술·전환연도를 모든 활성 시나리오에서 재평가하도록 실행 구조를 바꿨다.
- 시설 액션 직렬화와 SHA256 기반 `portfolio_id`를 추가했다. 64개 계획-시나리오 결과에서 시나리오 간 액션·포트폴리오 ID drift가 0건임을 검증했다.
- 고정 포트폴리오가 각 시나리오의 연도별 회사 탄소예산을 충족하는지 별도로 진단하고 `scenario_feasible`, 최초 위반연도, 최대 연간 초과량, 최소 여유량을 보존했다. 부적합안은 결과값은 남기되 효율경계와 추천 후보에서는 제외했다.
- 실제 현금원가(투자·고정비·전력·수소·계약), 정책지원, 정책지원 후 순현금비용, 회피 탄소비용 가치, 경제적 순비용을 분리했다. 절대 P50/P90 NPV와 공시경로 고정 회피배출 공통분모 단위비용을 함께 보존했다.
- 서로 다른 분포에서 별도 계산한 P50은 가산되지 않는다는 점을 `cash_policy_p50_nonadditivity_bn_krw`로 명시했다. `economic cost = net cash − avoided carbon value` P50 정의 점검값은 전 행 0.0십억원이었다.
- `scenario_comparison.csv`와 `repeat_scenario_comparison.csv`를 신설했다. 동일 포트폴리오에 대해 `to − from` signed ΔP50(공통분모), ΔTCaR, Δ절대 P50/P90 NPV, Δ순현금, Δ탄소가치, Δ정책지원, ΔCAPEX를 저장한다.
- 대시보드에 고정 포트폴리오 ID, 목표경로 적합성, 위반연도·초과량, 공통분모, 동일계획 시나리오 변화 카드를 추가했다. 경계·지배계획·최적점은 연도별 탄소예산 적합안만 사용하도록 수정했다.
- `facility_schedule.csv`에도 시설별 기준 현금원가, 정책지원 후 순현금, 회피 탄소비용 가치를 별도 열로 추가했다.
- Excel 감사본에 16번째 `Scenario_Comparison` 시트를 추가했다. 렌더 검토 중 논리형 COUNTIF가 동일 포트폴리오와 적합 계획 수를 0으로 표시하는 문제를 찾아 PASS/FAIL 감사값으로 교정했다. 최종 요약은 비교행 32, 동일 포트폴리오 32, CAPEX 불변 32, 내부 목표경로 적합 15다.
- Markdown 실행 보고서를 고정 포트폴리오·현금/탄소가치 분리·적합성 기준으로 갱신했다.

### 수집·검증한 데이터와 출처

이번 회차에는 새로운 공식 외부 수치를 추가하지 않았다. 1회차에 등록한 기업 공시 총량과 GCAM 공식 문서 메타데이터를 유지했고, 확인되지 않은 GCAM 1.5°C·2.0°C 숫자를 만들지 않았다. 주된 작업은 이미 출처가 있는 입력을 동일 물리 포트폴리오·동일 분모·분리된 비용 정의로 다시 계산하고 감사하는 것이었다.

### 주요 정량 결과와 해석

- 공시경로: 32/32 고정 포트폴리오가 연도별 회사 예산에 적합했다.
- 내부 1.5°C 스트레스: 15/32만 적합했다. 기업별 적합 계획은 POSCO P6~P7, Nippon Steel P5~P7, JFE Steel P2·P4~P7·CURRENT, Kobe Steel P4~P7이다.
- 32개 시나리오 비교행 모두 `same_physical_portfolio=True`; signed ΔCAPEX는 전 행 0.0십억원이었다.
- 공시계획 프록시를 내부 스트레스에 놓으면 경제적 P50 NPV는 네 회사 모두 감소하지만 순현금 P50은 증가했다. 이는 더 높은 탄소가격의 회피가치가 경제적 비용을 낮추는 동시에 실제 현금부담은 높일 수 있음을 보여준다. 경제적 비용 감소를 현금절감으로 해석해서는 안 된다.
- 공시계획 프록시의 내부 스트레스 적합성은 POSCO FAIL(2030), Nippon Steel FAIL(2035), JFE Steel PASS, Kobe Steel FAIL(2035)로 계산됐다.
- 별도 P50의 비가산 감사 차이는 최대 105.582십억원이었다. 이는 오류가 아니라 상관된 경로별 비용의 주변분위수를 따로 뽑았기 때문이며, 경로별 합계에서 계산한 경제적 P50과 중앙경로 브리지를 우선 사용해야 한다.

### 변경 파일

- 모델·비용·시뮬레이션: `cap_efficient/models.py`, `cap_efficient/costing.py`, `cap_efficient/simulation.py`, `cap_efficient/schedule.py`, `cap_efficient/pipeline.py`
- 대시보드·보고서: `cap_efficient/dashboard.py`, `cap_efficient/dashboard_script.py`, `cap_efficient/dashboard_template.py`, `cap_efficient/report.py`, `cap_efficient/__init__.py`
- 데이터·검증: `data/scenario_definitions.csv`, `scripts/verify_model_parity.py`, `scripts/build_data_audit_workbook.mjs`, `tests/test_pipeline.py`
- 문서: `README.md`, `METHODOLOGY.md`, `DATA_DICTIONARY.md`
- 재생성 산출물: `outputs/dashboard.html`, 반복 집계 CSV/JSON, `outputs/plan_metrics.csv`, `outputs/facility_schedule.csv`, `outputs/frontier_membership.csv`, `outputs/scenario_comparison.csv`, `outputs/report.md`, 실행 JSON·SVG, Excel 감사본·16개 렌더, 왕복 감사·동일성 결과

### 실행한 명령과 검증 결과

- `python3 -m cap_efficient dashboard --paths 1000 --seeds 42,2025,314159`
  - 3회 × 1,000경로, 계획·시나리오당 총 3,000경로 반복 완료. 반복 계획 64행, 반복 시나리오 비교 32행 생성.
- `python3 -m cap_efficient run --paths 1000 --seed 42`
  - 메인 1,000경로 실행과 전체 산출물 재생성 완료.
- 최신 `dashboard.html`의 인라인 JavaScript를 Node `new Function`으로 컴파일
  - 구문 PASS, 템플릿 placeholder 없음.
- `python3 -m cap_efficient validate-data --data-dir data`
  - 4개 기업, 17개 시설, 6개 기술, 8개 회사-활성시나리오, 32개 회사-계획 PASS.
- `python3 -m unittest discover -s tests -v`
  - 최종 5/5 PASS. 고정 액션·포트폴리오 ID, 예산 위반 진단, 비용 정의, 공통분모, 비교행, CAPEX 불변, 부적합 경계 제외, 반복 대시보드 출력을 포함해 검증.
- 번들 `@oai/artifact-tool`로 `scripts/build_data_audit_workbook.mjs` 반복 실행
  - 16개 시트 렌더 전수 확인, 수식 오류 검색 0건. 잘못된 논리형 COUNTIF 요약을 시각 검토로 발견·수정.
- `scripts/export_verified_csv.py`
  - CSV 8개 + JSON 1개, 총 9/9 의미상 Excel→CSV 왕복 PASS. 최신 원본·export SHA256 기록.
- 원본 입력과 Excel 재생성 입력으로 각각 `--paths 100 --seed 42` 실행 후 `scripts/verify_model_parity.py`
  - `plan_metrics.csv`, `facility_schedule.csv`, `frontier_membership.csv`, 신규 `scenario_comparison.csv` 4/4 바이트·SHA256 동일 PASS.

### 새로 확인한 중요한 문제

1. 현재 후보는 8개 계획 프록시뿐이고 공시경로에서 비용 최소 조합을 고르는 구조다. 스크랩·전력망·수소공급·공사기간·동시공사·기술실패 제약을 가진 수백 개 고유 물리 포트폴리오가 아직 필요하다.
2. 내부 스트레스의 탄소가격·예산·정책지원은 공식 GCAM이 아니다. GCAM DB/version/configuration/query XML/추출 CSV/hash를 확보하기 전 공식 1.5°C·2.0°C 경계로 표시할 수 없다.
3. 탄소가치가 커질수록 경제적 NPV가 낮아져 보이더라도 순현금비용은 상승할 수 있다. 화면과 보고서에서 두 값을 계속 나란히 유지해야 한다.
4. 공통분모는 동일 포트폴리오의 공시경로 회피배출이다. 향후 GCAM 연계 시 회사·시나리오 간 절대 NPV와 동일한 기준 생산량/회피배출 규칙을 추가로 문서화해야 한다.
5. 효율경계는 적합안만 남기도록 개선됐지만 최대후회비용, 강건 경계, 경로별 실패·지연 확률은 아직 구현되지 않았다.

### 다음 회차 우선순위

1. GCAM 공식 추출 매니페스트 스키마와 검증기를 구현하고, 공개 배포 DB/configuration/query XML에서 한국·일본 철강, 탄소가격, 전력·수소 가격/배출계수 경로를 재현 가능하게 추출할 수 있는지 확인한다.
2. 설비별 스크랩·전력망·수소공급 상한, 기술별 공사기간, 회사별 동시공사 한도, 기술실패·지연 확률 데이터 구조와 검증 규칙을 추가한다.
3. 제약을 만족하는 수백 개 포트폴리오 생성기를 만들고 동일 후보 집합을 모든 시나리오에서 평가한다.
4. 시나리오별 최대후회비용·강건 경계·위험선호 λ 최적점을 고정 후보 집합 위에서 다시 정의하고 대시보드·보고서에 연결한다.

## 3회차 — 2026-08-07 04:13–04:51 KST (약 38분)

### 이번 회차의 목표와 수행 내용

- JGCRI 공식 GCAM 9.1 배포본을 직접 내려받아 release asset SHA256, configuration, policy target 예제와 공식 query XML을 검증했다. 공개 배포본에 곧바로 쓸 수 있는 한국·일본 철강 1.5°C/2.0°C 숫자 결과는 없음을 확인했으며, 숫자를 추정해 활성화하지 않았다.
- 공식 target-finder schema를 사용하는 프로젝트 작성 `temperature=1.5°C`와 `temperature=2.0°C` 입력 XML을 추가했다. 두 파일은 JGCRI가 발표한 결과가 아니라 향후 공식 binary 실행을 위한 입력이며, 실행 전 상태를 명시했다.
- `gcam_run_manifest.csv`와 `gcam_query_manifest.csv`를 만들었다. release/tag/commit/asset/config/query/target hash와 세계 온도·forcing, 한국/일본 탄소가격·철강 생산/투입/배출·전력·수소, 회사 탄소예산 변환, 전해조 CAPEX 외부 가정 등 시나리오별 10개 필수 출력을 고정했다.
- GCAM 매니페스트 검증기를 구현했다. target XML의 SHA256·XML 내용·목표값, 두 시나리오와 20개 query 행의 완전성, pending 산출물의 허위 hash 금지, 실제 DB/CSV/hash가 없는 GCAM 시나리오의 활성화 금지를 검사한다.
- 현실 제약 입력을 추가했다. 회사별 동시공사·포트폴리오 실패확률 상한, 기술별 스크랩 투입·실패확률·최대 지연, 회사·시나리오·연도별 스크랩·수소·증분 전력망 상한을 별도 CSV로 만들었다. 모두 아직 공식값이 아닌 `model_estimate`이며 빈 출처 URL과 주의 문구로 표시했다.
- 고정 포트폴리오별 연간 물리제약 진단을 모델에 연결했다. 자원별 최대 초과량·최초 위반연도, 공사 중첩 수·허용 한도, 결합 실패확률 `1−Π(1−p)`와 기대 지연을 계산하고, 기존 탄소예산과 합쳐 `scenario_feasible`을 통합 실행가능성으로 재정의했다. 비용은 부적합안에도 보존하되 효율경계·추천에서 제외한다.
- 대시보드에 탄소예산, 스크랩·수소·계통, 동시공사, 실패위험을 한 카드에서 구분해 보여주도록 수정하고 실패 문구를 `실행 제약 미충족`으로 통일했다. 인라인 JavaScript 구문검사를 통과했다.
- Markdown 보고서의 경로 판정을 통합 실행가능성으로 고쳤다. 공시계획 프록시가 실패하면 탄소예산, 자원·계통, 동시공사, 기술실패위험 중 실제 미충족 사유와 연도를 표시한다.
- Excel 감사본에 현실 제약 3개 탭과 GCAM 매니페스트 2개 탭을 추가해 총 21개 시트로 확장했다. target XML 2개와 가격 JSON은 변경 없이 복사되는 지원파일로 해시 감사하며, 오래된 렌더 PNG가 남지 않도록 렌더 디렉터리를 매번 정리한다.

### 수집·검증한 공식 자료

| ID | 1차 출처 | 확인 내용 | 프로젝트 사용 방식 |
|---|---|---|---|
| GCAM-REL | https://github.com/JGCRI/gcam-core/releases/tag/gcam-v9.1 | GCAM 9.1, 2026-06-02 release, tag `gcam-v9.1`, commit `11e128f` | 공식 Mac release asset를 내려받아 SHA256 고정; 수치 결과로는 사용하지 않음 |
| GCAM-ASSET | https://github.com/JGCRI/gcam-core/releases/download/gcam-v9.1/gcam-v9.1-Mac-Release-Package.zip | 328,183,673 bytes, SHA256 `b009e58a9eafdf9b77a02440c50904a95e14f1df29ca28874e90ab90e4d0868a` | 로컬 `tmp/`에 보관하고 GitHub digest와 일치 확인 |
| GCAM-TGT | https://jgcri.github.io/gcam-doc/user-guide.html | target finder가 `target-type=temperature`, 목표값·허용오차·세금경로 탐색을 지원 | 프로젝트 1.5°C/2.0°C target XML schema 근거 |
| GCAM-QRY | https://github.com/JGCRI/gcam-core/blob/gcam-v9.1/output/queries/Main_queries.xml | global mean temperature, total forcing, CO2 prices, iron and steel production/inputs/emissions, electricity/hydrogen price query 확인 | 필요한 공식 query title을 매니페스트에 고정 |
| GCAM-ANL | https://jgcri.github.io/gcam-doc/dev-guide/analysis.html | DB query/export와 후처리 경로 | 향후 원단위·지역경계·output hash 감사 절차 근거 |

검증한 공식 배포파일 내부 hash는 `configuration_policy.xml`=`4aa38bf0…942b`, `policy_target_1p9_spa1.xml`=`39b1d0…`, `policy_target_2p6_spa1.xml`=`a5ddc…`, `Main_queries.xml`=`715eacf6…fe5d`이다. 공식 예제의 1.9/2.6 W/m² forcing 목표를 1.5/2.0°C 숫자 경로로 오인하지 않았다. 현재 `GCAM_15C`와 `GCAM_2C`는 모두 `planned_not_run`, 필수 query 0/10 verified, `ready_to_activate=false`다.

### 주요 정량 결과와 해석

- 내부 1.5°C 스트레스: 32개 고정 계획 중 탄소예산 적합 15개, 물리제약 적합 24개, 둘을 동시에 만족한 계획 9개다. 통합 적합안은 POSCO P6, Nippon Steel P5·P6, JFE Steel P4·P5, Kobe Steel P4~P7이다.
- 공시경로: 탄소예산은 32/32 적합하지만 물리제약을 포함한 통합 적합안은 13/32다. 이 결과는 공시 탄소목표 충족과 실제 자원·공사 실행가능성이 다른 문제임을 보여준다.
- 내부 스트레스의 23개 부적합안에는 탄소예산 17건, 수소 4건, 스크랩 4건, 전력망 2건, 동시공사 1건의 중복 사유가 있었다. 실패확률 상한 위반은 이번 screening 가정에서는 발생하지 않았다.
- 공시계획 프록시를 내부 스트레스에 놓으면 POSCO는 탄소예산, Nippon Steel은 탄소예산, JFE Steel은 자원·계통, Kobe Steel은 탄소예산과 자원·계통 때문에 모두 통합 FAIL이다. 이는 과거 탄소예산만 본 JFE PASS 판정을 현실 제약이 바꾼 사례다.
- 이 제약 한도들은 시설·공급계약의 공식 검증값이 아니라 후보 screening용 추정치다. 따라서 `FAIL`은 실제 사업 불가능 판정이 아니라 어떤 공식 데이터와 계약 검증이 필요한지를 가리키는 진단이다.

### 변경 파일

- 새 데이터: `data/gcam_run_manifest.csv`, `data/gcam_query_manifest.csv`, `data/gcam/policy_target_temperature_1p5.xml`, `data/gcam/policy_target_temperature_2p0.xml`, `data/company_constraints.csv`, `data/technology_constraints.csv`, `data/resource_constraints.csv`
- GCAM 검증: `cap_efficient/gcam_manifest.py`, `scripts/validate_gcam_manifest.py`, `cap_efficient/loader.py`, `cap_efficient/pipeline.py`
- 현실 제약·모델: `cap_efficient/models.py`, `cap_efficient/schedule.py`, `cap_efficient/pipeline.py`
- 대시보드·보고서: `cap_efficient/dashboard.py`, `cap_efficient/dashboard_script.py`, `cap_efficient/dashboard_template.py`, `cap_efficient/report.py`, `cap_efficient/__init__.py`
- 감사·왕복: `scripts/build_data_audit_workbook.mjs`, `scripts/export_verified_csv.py`
- 테스트·문서: `tests/test_pipeline.py`, `README.md`, `METHODOLOGY.md`, `DATA_DICTIONARY.md`, `data/scenario_definitions.csv`
- 재생성 산출물: `outputs/dashboard.html`, 반복 집계·시나리오 비교, 메인 CSV/JSON/SVG/보고서, `gcam_manifest_validation.json`, Excel 감사본·21개 렌더, 왕복 감사·모델 동일성 결과

### 실행한 명령과 검증 결과

- 공식 release asset 다운로드·`sha256sum`·ZIP 중앙목록/내부 XML 추출 검사
  - 328MB asset SHA256이 GitHub 공식 digest와 일치. 필요한 configuration/policy/query 파일과 공식 query title 확인.
- `python3 scripts/validate_gcam_manifest.py --data-dir data --output outputs/gcam_manifest_validation.json`
  - `PASS`는 매니페스트·target hash 무결성에 한정. 두 GCAM 시나리오는 수치실행 미검증으로 활성화 차단 PASS.
- `python3 -m cap_efficient dashboard --data-dir data --output-dir outputs --paths 1000 --seeds 42,2025,314159`
  - 3회 × 1,000경로, 계획·시나리오당 3,000경로 반복 완료. 최신 `dashboard.html` 생성.
- `python3 -m cap_efficient run --data-dir data --output-dir outputs --paths 1000 --seed 42`
  - 메인 모델과 통합 제약 사유가 포함된 Markdown 보고서 전체 재생성 완료.
- `python3 -m pytest -q`
  - 6/6 PASS. GCAM target hash 변조 차단, 제약 입력 수, 물리제약 진단, 통합 feasible 항등식, 기존 고정 포트폴리오·비용·경계 회귀검증 포함.
- `python3 -m cap_efficient validate-data --data-dir data`
  - 4개 기업, 17개 시설, 6개 기술, 8개 회사-활성시나리오, 32개 회사-계획 검증 PASS.
- Node 구문검사 및 최신 `dashboard.html` 인라인 script를 `new Function`으로 컴파일
  - JavaScript 구문 PASS.
- `scripts/build_data_audit_workbook.mjs` 반복 실행
  - 21개 시트 렌더 전수 확인, 수식 오류 검색 0건. GCAM·제약 탭 열 너비와 감사 결론을 보정함.
- `scripts/export_verified_csv.py`
  - CSV 13개 + JSON 1개 + XML 2개, 총 16/16 Excel→CSV 의미상 또는 지원파일 byte 왕복 PASS.
- 원본·Excel 재생성 입력을 각각 `--paths 250 --seed 42`로 실행 후 `scripts/verify_model_parity.py`
  - `plan_metrics.csv`, `facility_schedule.csv`, `frontier_membership.csv`, `scenario_comparison.csv` 4/4 바이트·SHA256 동일 PASS.
- 인앱 브라우저 대시보드 자동 상호작용 검사
  - 기존 로컬 탭을 확인했으나 `file://` URL 제어가 브라우저 보안 정책으로 차단됐다. 우회하지 않았고 정적 JavaScript 컴파일·회귀테스트로 보완했다.

### 새로 확인한 중요한 문제

1. 공식 GCAM 9.1 binary·입력·query는 고정했지만 target-finder 실행과 한국/일본 결과 DB export는 아직 수행하지 않았다. 설정만으로 공식 1.5°C/2.0°C 경계라 부를 수 없다.
2. 지역 GCAM 철강 결과를 POSCO·Nippon Steel·JFE·Kobe로 배분하는 규칙은 공식 GCAM 출력이 아니다. 공개 생산·배출 기준연도 share, 시설 기술구성, 회사 목표를 사용하는 투명한 별도 변환과 감사표가 필요하다.
3. 스크랩·수소·전력망·동시공사·실패위험 구조는 구현됐지만 한도값은 screening 추정치다. 기업 공시, 국가 공급전망, 계통계획, EPC 일정 데이터로 대체되기 전 투자 승인용이 아니다.
4. 후보는 여전히 회사당 8개, 총 32개다. 현실 제약을 적용한 수백 개 고유 포트폴리오 생성, 강건 경계, 최대후회비용은 아직 미구현이다.
5. 로컬 `file://` 대시보드의 자동 브라우저 상호작용은 정책상 불가하다. 다음 회차에는 안전한 로컬 HTTP 정적 서버 또는 HTML 구조 회귀테스트를 검토하되, 외부 배포는 하지 않는다.

### 다음 회차 우선순위

1. 검증된 GCAM 9.1 package의 target-finder를 별도 작업 디렉터리에서 실행해 1.5°C와 2.0°C target 달성 여부, DB, query export, raw unit, SHA256을 기록한다. 실행에 실패해도 configuration·로그·플랫폼 호환 문제를 남긴다.
2. 회사당 수십~수백 개 액션 조합을 생성하는 고유 포트폴리오 catalog를 만들고, 탄소·자원·공사·실패 screening 후 동일 후보 집합을 모든 시나리오에서 평가한다.
3. 고정 후보 집합의 시나리오별 regret, maximum regret, robust dominance, λ 최적점을 다시 계산해 이중 경계와 동일계획 연결선에 연결한다.
4. 현실 제약 추정치의 공식 대체자료를 기업 공시·한국/일본 에너지/수소/스크랩·계통 1차 출처에서 수집하고 URL·단위·연도·지역경계를 채운다.

## 4회차 — 2026-08-07 05:15–05:40 KST (약 25분)

### 이번 회차의 목표와 수행 내용

- 공식 GCAM 9.1 Mac 실행파일을 실제로 구동해 플랫폼 호환성을 확인했다. 바이너리와 호스트는 모두 arm64였으나 현재 호스트에 Java 런타임이 없어 `@rpath/libjvm.dylib` 로딩에서 exit 134로 중단됐다. 이 사실을 다시 실행 가능한 `scripts/probe_gcam_runtime.py`와 `outputs/gcam_runtime_probe.json`에 명령·exit code·stderr·바이너리/configuration SHA256과 함께 기록했다.
- GCAM 수치 실행이 실패한 상태에서 1.5°C/2.0°C 값을 추정하지 않았고 `GCAM_15C`, `GCAM_2C`를 계속 비활성으로 유지했다. 활성 시나리오 레지스트리와 모델 버전은 `0.6.0`으로 맞췄다.
- `cap_efficient/candidates.py`를 신설해 시설별 허용기술, 전환연도, P1–P7 계약 프로필을 조합하는 후보 생성기를 구현했다. 총 910개 고유 의사결정 패키지와 456개 고유 물리 포트폴리오를 만들고 동일 패키지를 두 활성 시나리오에 고정 적용했다.
- 910개 후보×2개 시나리오=1,820행을 중앙가격으로 먼저 스크리닝한 뒤 회사당 최대 64개, 총 217개 후보를 seed당 100개 Monte Carlo 경로로 평가하는 2단계 계산을 구현했다. 기준 P1–P7은 기존 1,000경로를 유지했다.
- 후보별 시나리오 최저 적격 P50 대비 regret, maximum/mean regret, worst P50, worst TCaR, 전 시나리오 적격성, 최대후회-최악TCaR 강건 비지배경계, λ=0/1/4 최적점을 계산했다.
- 후보 결과에 현금비용·정책지원·탄소회피가치·절대 P50/P90 NPV·공통분모를 유지하고, 동일 `candidate_id`·`physical_portfolio_id`의 signed ΔP50·ΔTCaR·ΔNPV·ΔCAPEX를 별도 파일로 만들었다.
- 대시보드에 `강건 후보 지도 · 동일 후보의 시나리오 이동` 패널을 추가했다. 동일 후보 연결선, 시나리오별 적격 효율경계, 강건경계, 최대후회, 최악 TCaR, λ=0/1/4 추천점, 후보 수와 경로 수를 표시한다. 공식 GCAM이 아닌 두 활성 경로만 비교한다는 경고를 차트 바로 옆에 고정했다.
- 실행 보고서와 README·방법론·데이터사전에 후보 생성 규칙, 2단계 평가, 후회·강건경계·λ 정의, 후보 경로수 차이, GCAM JVM blocker를 문서화했다.
- Excel 감사본에 `Candidate_Catalog`, `Robust_Candidates`, `Candidate_Comparison` 3개 시트를 추가해 총 24개 시트로 확장하고 전 시트를 다시 렌더했다. 원천 탭과 생성 결과 탭을 구분하고 조건·불리언·signed delta를 그대로 감사할 수 있게 했다.

### 수집·검증한 데이터와 출처

이번 회차에는 새로운 외부 수치자료를 추가하지 않았다. 3회차에 hash를 고정한 JGCRI 공식 GCAM 9.1 Mac release package를 로컬에서 직접 실행해 런타임 의존성만 검증했다.

| 항목 | 확인값 | 해석 |
|---|---|---|
| 호스트/바이너리 | host `arm64`, GCAM Mach-O `arm64` | CPU 아키텍처는 호환 |
| GCAM executable SHA256 | `b2ac5520bfaa1fc9e1dde34751cc918215c525f288f6c884f1bb4bfaefc169cd` | 압축 해제된 실행파일 고정 |
| 실행 명령 | `./gcam -C configuration_policy.xml` | 공식 package의 정책 configuration 직접 시도 |
| 실행 결과 | exit 134, `Library not loaded: @rpath/libjvm.dylib` | Java 런타임 부재로 모델 계산 전 중단 |
| 수치 산출 | 없음 | 공식 GCAM 1.5°C/2.0°C 경로는 계속 pending |

기존 공식 출처는 [JGCRI GCAM 9.1 release](https://github.com/JGCRI/gcam-core/releases/tag/gcam-v9.1), [target finder/user guide](https://jgcri.github.io/gcam-doc/user-guide.html), [공식 query XML](https://github.com/JGCRI/gcam-core/blob/gcam-v9.1/output/queries/Main_queries.xml)을 유지한다. 후보 910개와 현실제약 판정값은 공식 기업 공시사업이 아니라 `model_generated_candidate`와 `model_estimate`다.

### 주요 정량 결과와 해석

- 생성 후보는 POSCO 211, Nippon Steel 603, JFE Steel 71, Kobe Steel 25, 합계 910개다. 계약 프로필을 제외한 고유 물리 전환 패키지는 456개다.
- 217개 확률평가 후보 중 두 활성 시나리오에 모두 적합한 후보는 POSCO 14, Nippon Steel 23, JFE Steel 3, Kobe Steel 6개다.
- 3개 seed 중 한 번이라도 강건경계에 포함된 후보는 POSCO 3, 나머지 회사 각 1개다. λ=1 추천 후보는 모든 seed에서 POSCO `CAND-6339E6B83A8408`, Nippon Steel `CAND-7400D0EA735D98`, JFE Steel `CAND-E8FAD9BDD034A5`, Kobe Steel `CAND-4D158AE8BC3521`로 안정적이었다.
- λ=1 추천 후보의 3-seed 평균 최대후회/최악 TCaR은 각각 POSCO 54.8/14.2, Nippon Steel 59.2/18.2, JFE Steel 27.9/26.4, Kobe Steel 92.1/30.2천원/tCO₂다. 최대후회가 0이 아니므로 어느 한 경로에 최적인 계획이 다른 경로에서도 최적이라는 뜻은 아니다.
- 후보 시나리오 비교 217행은 모두 같은 물리 포트폴리오이며 signed ΔCAPEX 절대최대는 0.0십억원이다. 시나리오 변화는 물리계획 교체가 아니라 가격·정책·탄소예산 변화다.

### 변경 파일

- 신규 후보·GCAM probe: `cap_efficient/candidates.py`, `scripts/probe_gcam_runtime.py`
- 모델·집계: `cap_efficient/pipeline.py`, `cap_efficient/dashboard.py`, `cap_efficient/__init__.py`
- 대시보드·보고서: `cap_efficient/dashboard_template.py`, `cap_efficient/dashboard_script.py`, `cap_efficient/report.py`
- 감사·동일성: `scripts/build_data_audit_workbook.mjs`, `scripts/verify_model_parity.py`, `tests/test_pipeline.py`
- 데이터·문서: `data/scenario_definitions.csv`, `README.md`, `METHODOLOGY.md`, `DATA_DICTIONARY.md`
- 재생성 산출물: `outputs/dashboard.html`, `outputs/report.md`, 후보 CSV 5종, 반복 후보 CSV 3종, `outputs/repeat_summary.json`, `outputs/gcam_runtime_probe.json`, Excel 감사본·24개 렌더, `roundtrip_audit.json`, `model_parity_audit.json`, 기준/왕복 모델 실행 폴더

### 실행한 명령과 검증 결과

- `./gcam -C configuration_policy.xml`
  - exit 134. `@rpath/libjvm.dylib`를 찾지 못해 모델 초기화 전 중단. `scripts/probe_gcam_runtime.py`로 같은 상태를 `BLOCKED_MISSING_JAVA`로 재현했다.
- `python3 -m cap_efficient dashboard --paths 1000 --seeds 42,2025,314159`
  - 3회×1,000 기준경로 완료. 910개 생성, 1,820행 screening, 217개 후보×2시나리오 확률평가, 후보당 반복합계 300경로를 대시보드에 내장했다.
- `python3 -m cap_efficient run --paths 1000 --seed 42`
  - 메인 보고서, 기준 계획·시설·경계, 후보 catalog/screening/metric/robust/comparison 전체 재생성 완료.
- 최신 `dashboard.html`에서 인라인 script를 추출해 `node --check`
  - JavaScript 구문 PASS. `robust-chart`, 동일후보 연결, 공식 GCAM 비활성 경고와 model version 0.6.0 포함 확인.
- `python3 -m pytest -q` 및 `python3 -m unittest discover -s tests -v`
  - 올바른 모듈 실행은 6/6 PASS. 후보 ≥800, 고유 ID, 회사별 강건적격·λ=1 추천, 동일 물리 패키지, ΔCAPEX=0, 반복 대시보드 산출을 회귀검증했다. 셸의 독립 `pytest -q`는 Homebrew entrypoint의 import 경로 문제로 수집 실패했으나 `python3 -m pytest`에서 동일 환경 테스트가 정상 통과했다.
- `scripts/build_data_audit_workbook.mjs`
  - 24개 시트 렌더, 수식 오류 검색 0건. Reasonableness와 신규 후보 3개 시트, CSV Manifest를 이미지로 직접 확인했다.
- `scripts/export_verified_csv.py`
  - CSV 13개 + JSON 1개 + XML 2개, 16/16 의미상 또는 byte 왕복 PASS.
- 원본과 Excel 재생성 입력을 각각 `--paths 100 --seed 42`로 실행한 뒤 `scripts/verify_model_parity.py`
  - 기존 계획/시설/경계/시나리오 비교 4개와 신규 후보 5개, 총 9/9 파일 byte·SHA256 동일 PASS.
- `scripts/validate_gcam_manifest.py`
  - 매니페스트 무결성 PASS. 두 공식 GCAM 경로는 query 0/10, `ready_to_activate=false`로 올바르게 차단됨.
- in-app Browser 로컬 대시보드 검사
  - 기존 `file://` 탭 제어가 URL 보안 정책으로 차단되어 우회하지 않았다. 정적 JS 구문, 회귀테스트, HTML 내장 필드 검사로 보완했다.

### 새로 확인한 중요한 문제

1. 공식 GCAM 수치 실행의 즉시 blocker는 Java/JVM 부재다. Java를 갖춰도 target-finder 수렴, 온도 기준, DB/query export, 원시단위, 한국·일본 지역경계와 회사 배분 규칙을 모두 추가 검증해야 한다.
2. 후보 수는 충분해졌지만 Nippon Steel 603개와 Kobe Steel 25개처럼 회사별 설비 블록 수에 따라 탐색밀도가 크게 다르다. 다음 회차에는 기술/시점 변형을 늘리거나 회사별 동일 후보예산을 쓰는 계층화 샘플링을 검토해야 한다.
3. 후보 Monte Carlo는 계산량 때문에 seed당 100경로이며 기준계획 1,000경로보다 분포 정밀도가 낮다. 상위 강건 후보는 후속 회차에서 1,000경로 재평가가 필요하다.
4. 현재 강건성은 공식 GCAM이 아닌 공시경로와 내부 스트레스 두 경로에 한정된다. 공식 1.5°C/2.0°C가 들어오면 regret 기준점과 강건경계를 전체 재계산해야 한다.
5. 생성 후보의 요인분해는 아직 생략돼 있다. 상위 강건 후보에 대해 전력·수소·건설비 단독 및 상호작용 분해를 추가해야 한다.

### 다음 회차 우선순위

1. 안전한 범위에서 이용 가능한 Java 런타임을 확인하고, 설치/환경변경 없이 연결할 수 있으면 GCAM 1.5°C·2.0°C target-finder를 재시도한다. 불가능하면 실행환경 요구사항과 명령을 더 명확히 문서화한다.
2. 네 회사 λ=1 및 강건경계 후보를 각각 1,000경로로 재평가해 최대후회·최악 TCaR의 신뢰성을 높이고 seed 안정성을 비교한다.
3. 강건 후보의 시설별 action signature를 사람이 읽는 전환지도와 비용·배출·자원 브리지로 대시보드에 연결한다.
4. 강건 후보 상위점에 전력·수소·건설비 요인분해와 상호작용 잔차를 계산하고, 후보 Excel 시트에 추천 요약 상단을 추가한다.
5. 공식 현실제약 대체자료를 한국·일본 정부·전력망·수소·스크랩 1차 출처에서 수집해 추정치와 별도 열로 비교한다.

## 5회차 — 2026-08-07 06:15–06:36 KST (약 21분)

### 이번 회차의 목표와 수행 내용

- 4회차의 저해상도 후보 확률평가를 반복하지 않고, 중앙가격 screening으로 seed와 무관하게 고정되는 정밀 shortlist 선택기를 추가했다. 모든 활성 시나리오 적격 후보 중 결정론 최악비용이 낮은 후보와 각 시나리오 최저비용 후보를 합쳐 POSCO 10, Nippon Steel 10, JFE Steel 7, Kobe Steel 10, 총 37개를 고정했다.
- 37개 후보를 두 활성 시나리오에 동일한 물리 포트폴리오로 적용해 후보·시나리오당 요청 전체 1,000경로로 다시 평가했다. 전력·수소입력·건설 CAPEX 단독분산도 각각 1,000경로로 재계산하고 정밀 shortlist 안에서 regret, maximum regret, worst TCaR, 강건경계, λ=0/1/4 추천을 다시 만들었다.
- 정밀 후보 37개×2시나리오=74개 지표행, 37개 강건요약, 37개 signed 시나리오 비교, 316개 후보-시나리오-시설행, 1,110개 후보-시나리오-연도 자원행을 추가했다. 시설행에는 CAPEX·순현금·탄소가치·경제 NPV·감축을, 자원행에는 스크랩·수소·증분계통 수요/공급/여유/활용률을 보존했다.
- 대시보드의 강건 후보 지도는 저해상도 후보 대신 정밀 반복결과를 우선 사용하도록 바꾸고, 현재 λ 추천 후보의 시설 전환표와 2030/2035/2040 자원 수요·공급, 최대 활용률·최소 여유를 같은 패널에 연결했다. 정밀 경로수와 반복합계, 요인분해 해석 제한도 화면에 명시했다.
- 보고서에 정밀 후보 표와 λ=1 추천 후보의 기준배출·2040 잔여배출·연간감축·정렬 CAPEX·스크랩/수소/계통 최대 활용률을 추가했다. 전력/수소/건설 비중은 총비용 구성비가 아니라 TCaR 단독분산 비중이며, 수소 제조의 전력가격 노출이 전력 요인에 들어간다는 설명을 추가했다.
- Excel 감사본을 24개에서 30개 시트로 확장했다. `Refined_Decision` 요약과 `Refined_Metrics`, `Refined_Robust`, `Refined_Comparison`, `Refined_Facilities`, `Refined_Resources` 원시 시트를 추가해 HTML의 최종 판단을 Excel에서 다시 추적할 수 있게 했다.
- 모델 버전을 `0.7.0`으로 올리고 README·방법론·데이터사전에 결정론 고정 shortlist, 전체경로 재평가, shortlist 내 후회 기준점, 정밀 시설·자원 산출물을 문서화했다.

### 수집·검증한 데이터와 출처

이번 회차에는 새로운 외부 수치자료를 추가하지 않았다. 기존 공식 기업 기준점과 JGCRI 공식 GCAM 9.1 release/문서/query 매니페스트를 유지하고, 새로 생성한 후보·시설·자원값은 모두 `model_generated_candidate` 또는 `model_estimate`로 표시했다. 검증되지 않은 GCAM 1.5°C·2.0°C 수치를 만들지 않았고 두 공식 시나리오는 계속 비활성이다.

| 데이터 계층 | 확인값 | 출처·상태 |
|---|---|---|
| 기업 기준점 | 4개 기업, 17개 시설 블록, 생산·Scope 1+2 총량 조정 PASS | 기존 기업 공식 공시 URL 유지 |
| GCAM 구조 | 매니페스트 2행, 필수 query 20행, target XML hash PASS | JGCRI GCAM 9.1 공식 release·문서·query; 수치 실행은 pending |
| 생성 후보 | 910개 전체, 217개 100경로 1차 평가, 37개 1,000경로 정밀 평가 | 모델 생성값; 기업 공시사업 아님 |
| 자원 프로필 | 스크랩·수소·증분계통 1,110행 | 공급한도는 `model_estimate`; 승인용 실측자료 아님 |
| Excel 기준 데이터 | CSV 13개 + JSON 1개 + XML 2개 | 16/16 Excel→CSV 의미상/byte 왕복 PASS |

### 주요 정량 결과와 해석

- 3개 seed×1,000경로 반복에서 정밀 λ=1 추천은 네 회사 모두 100% 동일했다: POSCO `CAND-6339E6B83A8408`, Nippon Steel `CAND-7400D0EA735D98`, JFE Steel `CAND-E8FAD9BDD034A5`, Kobe Steel `CAND-4D158AE8BC3521`. 모두 P3 계약·시점 템플릿 계열이다.
- 3-seed 평균 최대후회/최악 TCaR은 POSCO 54.17/15.26, Nippon Steel 58.99/18.72, JFE Steel 27.20/27.50, Kobe Steel 94.09/27.24천원/tCO₂다. 추천이 안정적이어도 최대후회가 0은 아니므로 모든 시나리오에 동시에 최적인 계획이라는 뜻은 아니다.
- 최악 TCaR 시나리오는 네 회사 모두 `ACCELERATED_15C`였다. 전력·수소입력·건설비 단독분산 비중은 POSCO 94.5%/0.4%/5.1%, Nippon 97.2%/0.2%/2.6%, JFE 98.2%/0.3%/1.5%, Kobe 98.5%/0.4%/1.1%였다. 수소 제조의 전력가격 노출은 전력 요인에 포함되고 `hydrogen_input`은 비전력 전해조 성분만 변동하므로 이를 총비용 구성비로 읽으면 안 된다.
- λ=1 정밀 추천의 기준배출→2040 잔여배출/연간감축/정렬 CAPEX는 POSCO 69.8→10.4/59.5Mt/27,588bn KRW, Nippon 72.6→12.2/60.4Mt/29,348bn, JFE 45.3→6.0/39.3Mt/20,429bn, Kobe 14.3→1.9/12.4Mt/5,037bn이다.
- 같은 추천후보의 스크랩/수소/증분계통 최대 활용률은 POSCO 71.2%/35.8%/68.8%, Nippon 78.2%/24.3%/65.9%, JFE 69.9%/39.0%/71.1%, Kobe 58.4%/46.4%/63.9%로 추정 한도 안이었다. 이 여유는 공식 계약·계통자료가 아니라 screening 추정값이다.
- 공시경로→내부 스트레스의 같은 추천후보 signed ΔP50/ΔTCaR/Δ절대 NPV P50은 POSCO +12.686/−0.928/+5,444.100, Nippon +11.340/−1.108/+5,156.897, JFE +9.581/−1.521/+3,144.685, Kobe +10.282/−1.153/+1,052.799다. 엄격 경로에서 중앙비용은 증가하지만 이 모형의 P90−P50 폭은 소폭 축소됐다.

### 변경 파일

- 정밀 후보·자원 구조: `cap_efficient/candidates.py`, `cap_efficient/schedule.py`, `cap_efficient/pipeline.py`
- 대시보드·보고서: `cap_efficient/dashboard.py`, `cap_efficient/dashboard_script.py`, `cap_efficient/dashboard_template.py`, `cap_efficient/report.py`, `cap_efficient/__init__.py`
- 검증·감사: `tests/test_pipeline.py`, `scripts/verify_model_parity.py`, `scripts/build_data_audit_workbook.mjs`
- 데이터·문서: `data/scenario_definitions.csv`, `README.md`, `METHODOLOGY.md`, `DATA_DICTIONARY.md`
- 재생성 산출물: `outputs/dashboard.html`, `outputs/report.md`, 정밀 후보 CSV 5종, 반복 정밀 CSV 3종, `repeat_summary.json`, Excel 감사본·30개 렌더, `roundtrip_audit.json`, `model_parity_audit.json`, Excel 재생성 모델 폴더

### 실행한 명령과 검증 결과

- `python3 -m cap_efficient dashboard --paths 1000 --seeds 42,2025,314159`
  - 3회×1,000경로 완료. 기준계획과 정밀 후보 모두 계획/후보·시나리오당 반복합계 3,000경로, v0.7.0 `dashboard.html` 생성.
- `python3 -m cap_efficient run --paths 1000 --seed 42`
  - 대표 seed의 계획·시설·후보·정밀후보 CSV와 시설·자원 연결 보고서 재생성 완료.
- `python3 -m pytest -q`
  - 6/6 PASS. 정밀 파일 존재, 경로수, 요인비중 합계 1, 회사별 λ=1 단일 선택, 후보-시설 ID 일치, 자원 공급−수요=여유 항등식, 반복 대시보드 정밀 산출을 추가 검증.
- `python3 -m cap_efficient validate-data` 및 `python3 scripts/validate_gcam_manifest.py`
  - 입력 구조 PASS. GCAM 매니페스트 무결성 PASS이나 두 공식 경로는 query 0/10, `ready_to_activate=false`로 올바르게 차단.
- 최신 `dashboard.html` 인라인 JavaScript 컴파일
  - 구문 PASS. 로컬 `file://` 탭의 자동 렌더링 제어는 브라우저 URL 보안정책으로 차단되어 우회하지 않았다.
- `scripts/build_data_audit_workbook.mjs`
  - 30개 시트 렌더 완료, 수식 오류 검색 0건. `Refined_Decision`, `Refined_Facilities`, `Refined_Resources` 이미지를 직접 확인하고 수소 위험비중을 소수 1자리로 보정했다.
- `scripts/export_verified_csv.py`
  - 16/16 Excel→CSV 의미상 또는 byte 왕복 PASS.
- Excel 재생성 입력으로 `--paths 1000 --seed 42` 전체 모델 재실행 후 `scripts/verify_model_parity.py`
  - 기존 9개 산출물과 정밀 5개 산출물, 총 14/14 파일 바이트·SHA256 동일 PASS.

### 새로 확인한 중요한 문제

1. 공식 GCAM 1.5°C/2.0°C 수치경로의 blocker는 여전히 JVM과 성공한 target-finder DB/query export 부재다. 구조·hash PASS를 수치결과 검증으로 오해하면 안 된다.
2. 정밀 maximum regret의 시나리오별 최저비용 기준점은 전체 910개가 아니라 중앙가격으로 고정한 37개 shortlist 안에 있다. 전체 후보를 모두 1,000경로로 계산한 전역 regret가 아니다.
3. 단독분산 정규화는 상관·상호작용을 엄밀히 배분한 Shapley 분해가 아니다. 특히 수소 전력소비 가격위험이 전력 요인에 들어가므로 `hydrogen_input` 비중이 작게 보인다.
4. 추천후보의 자원 활용률은 추정 한도 안이지만 스크랩·수소·계통 공급한도 자체가 공식 현장·계약자료로 보정되지 않았다.
5. 회사별 전체 후보 수가 25–603개로 불균형하다. Kobe Steel은 설비 블록이 적어 기술·시점 탐색밀도가 상대적으로 낮다.
6. 인앱 브라우저의 로컬 `file://` 자동 렌더링 검사는 보안정책상 불가능했다. 정적 JavaScript 컴파일, HTML 내장데이터, 회귀테스트는 통과했지만 실제 브라우저 픽셀 QA는 수동 확인 영역이다.

### 다음 회차 우선순위

1. 한국·일본 정부·전력망·수소·철스크랩 1차 출처에서 공식 공급 전망을 수집해 현재 자원 한도와 단위·연도·지역경계를 나란히 비교하고, 수치가 직접 대응하지 않으면 조정하지 않는다.
2. 전력·수소·건설 단독분산에 상호작용 잔차 또는 순열 Shapley 근사를 추가해 전력 지배의 원인을 더 엄밀히 설명한다.
3. 회사별 동일 후보예산 또는 계층화 기술·시점 샘플링을 도입해 Kobe Steel과 JFE의 후보 탐색밀도를 높이고, 결정론 shortlist 고정성 회귀테스트를 추가한다.
4. 공식 GCAM 실행환경은 새 설치나 시스템 변경 없이 이용 가능한 JVM이 생겼는지 확인하고, 가능할 때만 target-finder와 DB/query export를 재시도한다.
5. 기존 DOCX 보고서를 최신 v0.7.0 정밀 후보·시설·자원 결과와 감사 결론으로 갱신하고 페이지 렌더 QA를 수행한다.

## 6회차 — 2026-08-07 07:17–07:39 KST (약 22분)

### 이번 회차의 목표와 수행 내용

- 5회차의 모델 실행을 단순 반복하지 않고, 한국·일본의 수소·전력망·철스크랩 공식 국가 벤치마크를 `data/resource_benchmarks.csv` 11행으로 새로 만들었다. URL·발표/보고서 버전·추출일·단위·지역·범위·비교가능성 경고를 모두 보존했다.
- 국가 전체의 MtH₂, GW/MW/MVA, Mt/년을 회사별 Mt·TWh 공급한도와 억지로 환산하지 않았다. 모든 행에 `national_context_not_company_*_limit`를 넣고 대시보드·보고서·Excel에서 “회사 한도 아님”으로 분리했다. 한국 스크랩은 검증된 정량값을 찾지 못해 값을 만들지 않고 `official_qualitative`로 남겼다.
- 정밀 shortlist 요인분해를 단독분산 정규화에서 정확한 3요인 Shapley 분산배분으로 확장했다. 전력·수소입력·건설 CAPEX의 모든 8개 부분집합을 동일 seed의 공통난수로 평가하며, 상관·비선형 상호작용을 배분하고 `shapley_reconciliation_delta`로 전체분산 합계를 감사한다. 기존 P1–P7 단독분산 진단은 호환성을 위해 유지하고 화면에서 두 방식을 명확히 구분했다.
- 대시보드 정밀 실행패널에 Shapley 전력/수소/건설 비중과 선택 회사의 공식 국가 벤치마크 카드를 연결했다. 보고서에는 공식 국가 벤치마크 표와 Shapley 해석을 추가했다.
- 모델 버전을 `0.8.0`으로 통일하고 `ResourceBenchmark` 데이터 클래스·로더·검증을 추가했다. 잘못된 국가/자원유형, HTTPS가 아닌 출처, 정성행이 아닌데 값이 없는 경우, 회사한도 비비교 경고가 없는 경우를 차단한다.
- Excel 감사본에 `Resource_Benchmarks` 원천시트를 추가해 31개 시트로 확장하고, `Refined_Decision`의 위험비중을 Shapley 평균으로 바꿨다. CSV→Excel→CSV 왕복과 재생성 모델 동일성을 다시 검증했다.

### 수집·검증한 데이터와 공식 출처

| 국가·자원 | 보존한 공식 값 | 공식 1차 출처 | 비교 제한 |
|---|---|---|---|
| 한국 수소 | 2030 국내 청정수소 1.0MtH₂/년 | 탄소중립녹색성장위원회, https://www.pcccr.go.kr/base/board/read?boardManagementNo=10&boardNo=124&menuLevel=2&menuNo=18&page=2 | 국가 목표, 철강·기업 배분 아님 |
| 한국 계통 | 2038 목표수요 129.3GW, 신규 필요설비 10.3GW | 산업부/MOTIR 제11차 전력수급기본계획, https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/170183/view | 전력량 TWh·사업장 접속한도 아님 |
| 한국 스크랩 | 순환자원 인정·등급/지역/수급통계 구축 방향 | 2050 탄소중립녹색성장위원회 기본계획, https://www.2050cnc.go.kr/storage/board/base/2023/02/17/BOARD_ATTACH_1676595021015.pdf | 정성 정책만 검증; 정량 공급값 없음 |
| 일본 수소 | 2030/2040/2050 3/12/20MtH₂-eq/년 | METI Basic Hydrogen Strategy, https://www.meti.go.jp/policy/energy_environment/global_warming/transition/jcr_climate_transition_bond_framework_spo_eng.pdf | 암모니아 수소환산 포함, 기업 배분 아님 |
| 일본 계통 | FY2032까지 변압기 30,163MVA, AC/DC 변환 1,200MW | OCCTO Annual Report 2023, https://www.occto.or.jp/assets/en/information_disclosure/annual_report/files/2023_annualreport_240131.pdf | 국가·광역 개발계획, 에너지 TWh 아님 |
| 일본 스크랩 | 2022 발생 43.16Mt/년; 2030 고급스크랩 추가 가공 2.0Mt/년 | 일본 환경성 보고서 https://www.env.go.jp/content/000315009.pdf 및 2026 백서 https://www.env.go.jp/policy/hakusyo/r08/html/hj26010401.html | 국가 발생량/가공능력, 회사 조달량 아님 |

### 주요 정량 결과와 해석

- 74개 정밀 후보-시나리오 행의 3-seed 평균 Shapley 비중 합계 최대오차는 `1.0e-9`, 평균 분산조정 오차의 최대 절댓값은 `0.0`이었다. 음의 Shapley 비중 행은 없었다.
- λ=1 추천 후보는 5회차와 동일하고 세 seed에서 모두 선택빈도 100%였다. 최악 TCaR 경로의 Shapley 전력/수소입력/건설비 비중은 POSCO 88.5%/3.7%/7.8%, Nippon Steel 92.9%/2.3%/4.8%, JFE Steel 94.0%/2.9%/3.1%, Kobe Steel 93.8%/3.6%/2.6%였다.
- 기존 단독분산 비중보다 수소·건설비가 커지고 전력 비중이 낮아졌다. 이는 비용 구성비 변화가 아니라 상관·상호작용을 Shapley로 재배분한 결과다. 그래도 전력위험이 88.5–94.0%로 지배적이므로 장기 PPA·계통접속·수소전력 조달이 여전히 핵심 검증항목이다.
- 정밀 추천의 최대후회/최악 TCaR은 POSCO 54.17/15.26, Nippon 58.99/18.72, JFE 27.20/27.50, Kobe 94.09/27.24천원/tCO₂로 이전과 동일했다. 요인분해 개선은 추천 목적함수 자체를 바꾸지 않았기 때문이다.

### 변경 파일

- 데이터 구조·검증: `cap_efficient/models.py`, `cap_efficient/loader.py`, `data/resource_benchmarks.csv`
- 모델·집계: `cap_efficient/pipeline.py`, `cap_efficient/dashboard.py`, `cap_efficient/__init__.py`, `pyproject.toml`, `data/scenario_definitions.csv`
- 대시보드·보고서: `cap_efficient/dashboard_template.py`, `cap_efficient/dashboard_script.py`, `cap_efficient/report.py`
- Excel·왕복: `scripts/build_data_audit_workbook.mjs`, `scripts/export_verified_csv.py`
- 회귀·문서: `tests/test_pipeline.py`, `README.md`, `METHODOLOGY.md`, `DATA_DICTIONARY.md`
- 재생성 산출물: `outputs/dashboard.html`, `outputs/report.md`, 전체 기준/후보/정밀 CSV, `outputs/data_audit/Capital_Allocation_Baseline_Audit.xlsx`, 31개 시트 렌더, `roundtrip_audit.json`, `model_parity_audit.json`, Excel 재생성 모델 폴더

### 실행한 명령과 검증 결과

- `python3 -m cap_efficient dashboard --paths 1000 --seeds 42,2025,314159`
  - 3회×1,000 전체 재실행 완료. 910개 생성후보, 37개 정밀후보, 정밀 8개 요인부분집합과 v0.8.0 HTML 재생성.
- `python3 -m cap_efficient run --paths 1000 --seed 42`
  - 대표 seed 보고서·CSV 전체 재생성 완료.
- `python3 -m pytest -q`, `python3 -m compileall -q cap_efficient scripts tests`, `python3 -m cap_efficient validate-data`
  - 7/7 PASS, 구문검사 PASS, 4회사·17시설·6기술·8 회사-시나리오·32 회사-계획·11 공식 벤치마크 로드 PASS.
- 최신 `dashboard.html` 인라인 JavaScript를 `new Function`으로 컴파일
  - 구문 PASS. 기본 단독분산/정밀 Shapley 문구, 공식 벤치마크 데이터와 카드 로직 포함 확인.
- `python3 scripts/validate_gcam_manifest.py`
  - 구조·hash PASS. GCAM 1.5°C/2.0°C는 query 0/10, `ready_to_activate=false`로 계속 올바르게 차단.
- `node scripts/build_data_audit_workbook.mjs`
  - 31개 시트 렌더, 수식오류 검색 0건. Cover, Resource_Benchmarks, Refined_Decision, CSV_Manifest 이미지를 직접 확인했다.
- `python3 scripts/export_verified_csv.py ...`
  - CSV 14개 + JSON 1개 + XML 2개, 17/17 의미상/byte 왕복 PASS. 신규 `resource_benchmarks.csv`도 PASS.
- Excel 재생성 입력으로 `--paths 1000 --seed 42` 모델 재실행 후 `scripts/verify_model_parity.py --paths 1000 --seed 42`
  - 기준/후보/정밀 산출물 14/14 byte·SHA256 동일 PASS.
- Playwright CLI wrapper 및 독립 Chrome headless 렌더 시도
  - wrapper package에서 `playwright-cli` 실행파일을 찾지 못했고, 설치된 Chrome은 별도 Claude Science 로그인 페이지로 리디렉션됐다. 잘못 캡처된 이미지는 프로젝트 밖 `/tmp`로 이동했다. Excel 렌더·정적 HTML·JS·회귀검증은 완료했지만 HTML 픽셀 QA는 이번 회차에서 완결하지 못했다.

### 새로 확인한 중요한 문제

1. 공식 국가 수치는 회사별 공급한도와 직접 비교할 수 없다. 특히 계통 GW/MW/MVA와 모델 TWh, 국가 수소 MtH₂-eq와 기업 수소 Mt를 변환하려면 시간가동률·지역배분·철강 할당·계약조건이 추가로 필요하다.
2. 한국 철스크랩은 공식 정책 방향만 확보했고 검증 가능한 국가 정량 공급경로를 아직 연결하지 못했다. 값을 꾸며 넣지 않고 정성행으로 남긴 상태다.
3. Shapley 분해는 현재 확률요인 3개에 한정된다. 기술실패·공사지연·정책지원·탄소가격 경로를 모두 확률게임에 넣은 전위험 분해는 아니다.
4. 공식 GCAM 1.5°C/2.0°C 수치경로는 JVM·성공 DB/query export 부재로 여전히 비활성이다. 매니페스트 PASS는 수치경로 검증 PASS가 아니다.
5. 대시보드 실제 픽셀 렌더 자동화는 로컬 브라우저 실행환경 문제로 미완료다. 사용자 브라우저에서의 수동 확인 또는 정상 Playwright/인앱 Browser 세션이 필요하다.

### 다음 회차 우선순위

1. 기존 DOCX 설계서와 최신 v0.8.0 결과를 연결한 전문 보고서를 갱신하고 페이지 렌더 QA를 수행한다.
2. 국가 벤치마크→회사 입력의 단위·범위 변환에 필요한 미확보 자료를 별도 gap registry로 만들고, 추정값을 공식값처럼 보이지 않게 한다.
3. JFE·Kobe의 후보 탐색밀도를 높이는 계층화 시점/기술 샘플링과 동일 후보예산을 구현하되, 기존 추천의 변화와 탐색범위 확장을 분리 보고한다.
4. 안전한 범위의 JVM 존재 여부만 다시 확인하고 가능할 때만 GCAM target-finder·query export를 재시도한다. 실패하면 다른 검증·문서화 작업을 계속한다.
5. 정상 인앱 Browser 또는 Playwright 세션이 가능하면 대시보드 상단·효율경계·강건후보·시설/공급 패널을 실제 렌더로 확인한다.

## 7회차 — 2026-08-07 08:16–08:43 KST (약 27분)

### 이번 회차의 목표와 수행 내용

- 기존 7페이지 DOCX 보고서와 원본 `Capital_Allocation_Pathway_설계서사.docx`를 각각 PDF/PNG로 렌더해 전 페이지를 먼저 읽었다. 기존 보고서는 표·여백·한글 폰트가 안정적이었지만 8개 입력/3개 parity/100 paths, 과거 공시계획 결과, 단독분산 정규화 등 v0.8.0 이전 내용이 남아 있어 의사결정 보고서로는 최신 모델과 일치하지 않았다.
- Documents 스킬의 `standard_business_brief` 및 memo masthead 규칙을 적용해 기존 안정적인 문서 시스템은 유지하고, 본문을 v0.8.0 기준 10페이지로 전면 갱신했다. 결론→감사 추적성→강건 추천→17개 시설 실행계획→현금·탄소·정책 비용 bridge→자원 병목→정확한 Shapley→공식 국가 벤치마크→일본 EAF CAPEX→승인 게이트→직접 URL·재현 산출물 순서로 재구성했다.
- `scripts/build_reasonableness_report.py`가 최신 `repeat_refined_candidate_*.csv`, 시설·자원 프로필, `resource_benchmarks.csv`, `roundtrip_audit.json`, `model_parity_audit.json`을 직접 읽어 표와 차트를 동적으로 만들도록 확장했다. λ=1 후보는 강건 적격안 중 반복 선택빈도 내림차순·최대후회 오름차순으로 선택한다.
- 공시경로와 내부 1.5°C 스트레스를 명확히 분리하고, `ACCELERATED_15C`가 공식 GCAM이 아님을 첫 두 페이지와 승인 게이트에 반복 표기했다. 효율경계 위 빨간 점은 회사 평가가 아니라 같은 비교집합 안에서 지배안이 존재하는 ‘계획 개선 여지’라고 설명했다.
- 실제 현금 P50, 탄소회피가치, 정책지원, 경제 NPV를 별도 열로 보존했다. 시설별 기술·전환연도·CAPEX·연간 감축 17행과 두 활성 시나리오·전 기간 자원 최대 이용률을 함께 제시했다.
- 정확한 3요인 Shapley는 이번 DOCX에서 `DISCLOSED_PATH` 기준으로 표시하고 비용 구성비가 아니라 비용분산 배분임을 명시했다. 기존 Markdown 보고서의 ‘최악 TCaR 시나리오’ Shapley와 정의가 다르므로 시나리오 라벨을 표와 각주에 보존했다.
- 최종 DOCX를 세 차례 재생성·렌더하면서 11페이지로 밀린 단독 각주와 CAPEX 차트 단위 겹침을 제거했다. 최종 10페이지를 모두 직접 확인했고 잘림, 겹침, 빈 페이지, 한글 누락이 없음을 확인했다. 마지막 회사 정렬 변경 후에는 페이지 1·2·4·5·7·8·9·10 PNG hash가 동일함을 확인하고 변경된 3·6페이지를 다시 직접 검사했으며, 최종 각주 변경 뒤 5페이지도 다시 검사했다.

### 사용·검증한 데이터와 출처

이번 회차에는 새로운 외부 수치를 추가하지 않았다. 6회차에 확보한 11개 공식 국가 벤치마크와 기존 기업 공식 공시를 그대로 사용했으며, DOCX에 직접 URL·확인일·비교 제한을 실었다.

| 데이터 | 보고서 반영 내용 | 출처·상태 |
|---|---|---|
| 기업·시설 | 4개 기업, 17개 시설 블록, λ=1 시설별 기술·연도·CAPEX·연간감축 | 기업 총량은 기존 공식 공시; 시설 배분은 `model_estimate` |
| 국가 자원 | KR 수소 1Mt/년, 계통 129.3/10.3GW, 스크랩 정성정책; JP 수소 3/12/20MtH₂-eq, 계통 30,163MVA/1,200MW, 스크랩 43.16/2Mt/년 | 탄녹위·MOTIR·METI·OCCTO·일본 환경성 직접 URL; 국가 맥락이며 회사 한도 아님 |
| 정밀 의사결정 | 37개 고정 shortlist, 3 seeds×1,000 paths, 최대후회·최악 TCaR·λ=1 | `repeat_refined_candidate_robust_summary.csv` |
| 비용·위험 | 현금·탄소회피·정책지원·경제 NPV와 공시경로 Shapley | `repeat_refined_candidate_scenario_metrics.csv` |
| 감사 | 입력 17/17, 모델 산출물 14/14 | `roundtrip_audit.json`, `model_parity_audit.json` |

### 주요 정량 결과와 해석

- λ=1 추천은 POSCO `CAND-6339E6B83A8408`, Nippon Steel `CAND-7400D0EA735D98`, JFE Steel `CAND-E8FAD9BDD034A5`, Kobe Steel `CAND-4D158AE8BC3521`이며 네 회사 모두 3회 반복 선택빈도 100%였다. 최대후회/최악 TCaR은 54.17/15.26, 58.99/18.72, 27.20/27.50, 94.09/27.24kKRW/tCO₂다.
- 공시경로의 지원후 현금 P50/탄소회피가치/정책지원/경제 NPV는 POSCO 42,741/15,556/3,877/27,185, Nippon 53,072/15,921/5,718/37,151, JFE 52,723/11,501/5,467/41,222, Kobe 18,629/3,576/1,800/15,053bn KRW다. 정책지원은 현금 P50에 이미 반영되고 경제 NPV는 현금 P50−탄소회피가치다.
- 공시경로 Shapley 전력/수소입력/CAPEX 비중은 POSCO 85.3%/4.7%/10.1%, Nippon 91.1%/2.9%/6.0%, JFE 92.5%/3.6%/4.0%, Kobe 92.6%/4.3%/3.1%다. 세 요인의 합계와 전체 분산 재조정 오차는 표시 정밀도에서 0이다.
- 두 활성 시나리오·전 기간 최대 스크랩/수소/증분계통 이용률은 POSCO 90.0%/49.8%/89.8%, Nippon 95.8%/33.8%/88.2%, JFE 84.4%/56.8%/99.5%, Kobe 71.6%/72.1%/78.6%다. JFE 계통과 Nippon 스크랩이 가장 가까운 실행 병목이지만 공급한도 자체는 `model_estimate`다.
- 일본 모델 SCRAP_EAF 616bn KRW/Mtpa는 JFE Kurashiki 공시 1,515의 40.7%, Nippon Steel 3개 EAF 공시 2,756의 22.4%다. 공정범위가 완전 동등하지 않더라도 low/base/high와 scope bridge 없이 절대 NPV를 승인용으로 쓰면 안 된다.

### 변경 파일과 산출물

- 보고서 생성기: `scripts/build_reasonableness_report.py`
- 최종 DOCX: `outputs/data_audit/Capital_Allocation_Reasonableness_Report.docx` (2,535,391 bytes, SHA256 `209ee545269c8a3556bf77a44eb60728163c90547f06ac45b5fdfd384b51f8db`)
- 보고서 차트: `outputs/data_audit/report_assets/robust_results.png`, `shapley_risk.png`, `eaf_capex_benchmark.png`
- 최종 시각 QA: `outputs/docx_qa/v080_release2/`의 PDF와 page-1~10 PNG; PDF 851,610 bytes, SHA256 `7aca3a25c6084646b8a6815b56370125018beffac539ae64f0d196350844fc27`

### 실행한 명령과 검증 결과

- bundled Python으로 `scripts/build_reasonableness_report.py` 구문검사 및 실행
  - 최신 CSV/JSON에서 DOCX·3개 차트 생성 PASS, Nanum Gothic 내장 PASS.
- Documents 스킬 `render_docx.py --emit_pdf`
  - 최종 10페이지 PDF/PNG 렌더 PASS. 전 페이지 시각검사 PASS, 빈 페이지·겹침·잘림·한글 누락 없음.
- `pdfinfo`, 페이지별 PNG SHA256 비교, `unzip -t`
  - 제목 v0.8.0, 10페이지, 비변경 페이지 hash 동일, DOCX 압축 무결성 PASS.
- `python3 -m pytest -q`
  - 7/7 PASS.
- 원본 설계서 8페이지와 기존 보고서 7페이지 PDF/PNG 렌더
  - 원본의 의도된 P50/TCaR·효율경계·이중경계 구조와 기존 문서의 시각체계를 확인하고 새 보고서에 반영.

### 새로 확인한 중요한 문제

1. `outputs/report.md`의 자원 최대활용은 최악 TCaR 시나리오(`ACCELERATED_15C`)만 선택해 POSCO 71.2%, Nippon 78.2%, JFE 69.9%, Kobe 58.4%의 스크랩 최대치를 보인다. 새 DOCX는 두 활성 시나리오 전체의 보수적 최댓값 90.0%, 95.8%, 84.4%, 71.6%를 쓴다. 둘 다 계산상 맞지만 집계범위 라벨이 약하면 숫자 충돌로 보이므로 Markdown·대시보드에서 ‘선택 시나리오 최대’와 ‘전 시나리오 최대’를 명시해야 한다.
2. Shapley 역시 `outputs/report.md`는 최악 TCaR 시나리오, 새 DOCX는 공시경로를 표시한다. 시나리오가 달라 값이 다른 것이므로 모든 화면에서 시나리오 라벨과 분석 목적을 더 분명히 해야 한다.
3. 공식 GCAM 1.5°C/2.0°C는 여전히 공식 DB/JVM 성공 실행과 경로별 query 0/10 때문에 비활성이다. 새 보고서도 이를 승인 P0 게이트로 유지했다.
4. 국가 자원 공식값은 회사 공급한도를 검증하는 직접 분모가 아니다. 특히 TWh 대 GW/MW/MVA, 회사 수소 대 국가 H₂-eq를 환산하지 않았다.
5. 일본 대형 EAF CAPEX의 full-scope 공시 대비 모델 원단위가 22~41%에 머무는 하방 편향 가능성은 여전히 해소되지 않았다.

### 8회차 최종 우선순위

1. 전체 모델을 3 seeds×1,000 paths로 다시 실행하고 대시보드·Markdown·CSV·Excel·DOCX가 같은 최종 입력을 가리키도록 동기화한다.
2. `report.md`와 대시보드의 자원 이용률·Shapley에 시나리오/집계범위 라벨을 보강해 같은 후보의 값이 왜 다른지 바로 보이게 한다.
3. Excel→CSV 17/17, 모델 parity 14/14, 7/7 테스트, GCAM 활성화 게이트를 최종 재검증한다.
4. 가능하면 정상 브라우저 세션에서 `dashboard.html`의 상단·이중경계·강건후보·시설/자원·공식 벤치마크 패널을 실제 픽셀로 확인한다. 불가능하면 정적 JS·DOM 내장데이터 검증과 제한사항을 최종 명시한다.
5. 최종 산출물, 핵심 결론, 공식값/추정값 경계, 남은 P0 한계를 한 번에 정리한다.

## 8회차 — 2026-08-07 09:16–09:37 KST (약 21분, 최종)

### 이번 회차의 목표와 수행 내용

- 시작 시 최신 소스·출력·7회차 기록·테스트를 다시 읽고 이미 완료된 국가 벤치마크·Shapley 확장은 반복하지 않았다. 7회차에서 남긴 집계범위 혼동을 직접 해소한 뒤 전체 최종 실행과 감사를 수행했다.
- 대시보드 `λ 추천 강건후보 · 시설과 공급여력`에 현재 선택 시나리오 라벨을 붙이고 시설 액션·Shapley·자원 최대활용이 그 시나리오의 2026–2040 범위임을 명시했다. Markdown 보고서는 각 기업 λ=1 추천의 최악 TCaR 시나리오를 선택한 값이라는 문구를 표 앞과 단위 각주에 넣었다.
- `dashboard --paths 1000 --seeds 42,2025,314159`로 기준계획·후보·정밀후보를 전부 재실행하고, `run --paths 1000 --seed 42`로 대표 CSV·Markdown을 같은 최종 입력에 맞췄다.
- Excel 감사본을 두 번 재생성했다. 첫 생성→17파일 export·감사→감사결과를 포함한 최종 생성→최종 workbook 재-export 순서로 stale 감사상태가 남지 않게 했다. 최종 31개 시트 PNG를 모두 직접 확인했다.
- 최종 Excel에서 내보낸 독립 CSV 폴더로 1,000경로 모델을 다시 실행하고 기준 산출물과 14개 파일을 비교했다. 동일 물리 포트폴리오, 공통분모, CAPEX 불변, signed delta와 비용 bridge 항등식도 별도 수치검증했다.
- 최신 CSV/JSON·감사결과에서 10페이지 DOCX를 다시 생성하고 PDF/PNG로 렌더했다. 10페이지 전부를 원본 해상도로 확인했으며 잘림·겹침·빈 페이지·한글 누락이 없었다. 접근성 감사도 high/medium/low 0/0/0이었다.
- 최종 상태와 승인 한계를 `outputs/final_validation_summary.md`에 한 페이지 감사요약으로 고정하고 핵심 산출물 SHA256을 기록했다.

### 수집 데이터와 출처

- 이번 회차에는 외부 수치를 새로 추가하지 않았다. 6회차에서 검증한 한국 탄녹위·산업부, 일본 METI·OCCTO·환경성 1차 출처 11행과 기존 기업 공식 공시를 그대로 사용했다.
- 새 수치를 찾은 것처럼 꾸미지 않았고, 공식 GCAM 1.5°C·2.0°C는 `pending_official_extract`, 시설·자원 한도·기술비용·지원은 `model_estimate`로 유지했다.
- 입력 최종 상태: 기업 4개는 공식 총량 기반, 시설 17개·기술 6개·계획 11개·회사제약 4개·자원제약 32개는 명시적 모델 추정, 공식 국가 벤치마크 10개 정량+1개 정성, GCAM query spec 20개는 출력 대기다.

### 주요 정량 결과와 해석

- 모델 v0.8.0, 4개 기업·17개 시설·2개 활성경로·2026–2040년. 910개 생성후보→217개 확률후보→37개 정밀 shortlist, 3 seeds×정밀후보·시나리오당 1,000경로=3,000 유효경로다.
- λ=1 추천은 POSCO `CAND-6339E6B83A8408`, Nippon Steel `CAND-7400D0EA735D98`, JFE Steel `CAND-E8FAD9BDD034A5`, Kobe Steel `CAND-4D158AE8BC3521`이며 모두 P3, 선택빈도 100%다.
- 최대후회/최악 TCaR(kKRW/tCO₂)는 POSCO 54.17/15.26, Nippon 58.99/18.72, JFE 27.20/27.50, Kobe 94.09/27.24다.
- 전체 37개 시나리오 연결은 37/37 동일 물리 포트폴리오이며 `Δaligned CAPEX` 최대 절댓값은 0이다. 선택 추천의 내부 스트레스→공시경로 `ΔP50`은 +9.58~+12.69, `ΔTCaR`은 −1.52~−0.93, `Δabsolute NPV P50`은 +1,052.8~+5,444.1bn KRW다.
- 선택 추천의 정확한 Shapley 비중 합계 최대오차는 `1.0e-9`, 전체분산 재조정 오차는 0이다. 지원후 현금비용−탄소회피가치=경제 NPV P50의 최대 잔차는 CSV 반올림 후 `0.000334bn KRW`다.
- 선택 추천은 시나리오별 34개 시설행, 고유 물리시설 17개이며 120개 연도별 자원행이 모두 실행제약을 통과했다. 두 활성 시나리오 전체 최대 이용률은 스크랩 95.8%, 수소 72.1%, 증분계통 99.5%지만 공급한도는 `model_estimate`다.

### 변경 파일과 최종 산출물

- 범위 라벨·보고서: `cap_efficient/dashboard_template.py`, `cap_efficient/dashboard_script.py`, `cap_efficient/report.py`
- 회귀검증: `tests/test_pipeline.py`
- 최종 감사요약: `outputs/final_validation_summary.md`
- 재생성 모델: `outputs/dashboard.html`, `outputs/report.md`, 기준/후보/정밀/반복 CSV·JSON·SVG 전체
- Excel 감사본: `outputs/data_audit/Capital_Allocation_Baseline_Audit.xlsx` 및 `rendered_workbook/` 31 PNG
- 보고서: `outputs/data_audit/Capital_Allocation_Reasonableness_Report.docx`, `outputs/docx_qa/final_8b/Capital_Allocation_Reasonableness_Report.pdf`, page-1~10 PNG
- 감사: `outputs/data_audit/roundtrip_audit.json`, `model_parity_audit.json`, `report_accessibility_audit.json`
- SHA256: dashboard `e1990a6d…6bff6`, Excel `2d2a0252…bd462`, DOCX `7819cdaa…a6f`, QA PDF `09dec37a…d39`.

### 실행한 명령과 검증 결과

- `python3 -m cap_efficient dashboard --paths 1000 --seeds 42,2025,314159`
  - PASS. 3회×1,000, 계획·정밀후보/시나리오당 3,000 유효경로, 910/217/37 후보 파이프라인과 v0.8.0 HTML 재생성.
- `python3 -m cap_efficient run --paths 1000 --seed 42`
  - PASS. 대표 seed의 전체 CSV·Markdown·요약 JSON 재생성.
- bundled Node로 `scripts/build_data_audit_workbook.mjs` 두 차례 실행 및 `scripts/export_verified_csv.py`
  - PASS. 31개 시트, 수식오류 검색 0건, CSV 14+JSON 1+XML 2 = 17/17 의미상 또는 byte 왕복. 최종 31개 시트 전수 시각검사 PASS.
- Excel export를 `--data-dir`로 `run --paths 1000 --seed 42` 재실행 후 `scripts/verify_model_parity.py`
  - PASS. 기준·후보·정밀 산출물 14/14 byte·SHA256 동일.
- `python3 -m unittest discover -s tests -v`, `compileall`, 대시보드 인라인 JavaScript `new Function`
  - PASS. 7/7 회귀테스트, Python 구문, JavaScript 구문 모두 통과.
- `python3 -m cap_efficient validate-data`, `python3 scripts/validate_gcam_manifest.py`
  - 입력구조 PASS. GCAM 매니페스트 구조·release/target hash PASS이나 1.5°C/2.0°C 모두 query 0/10, `ready_to_activate=false`로 올바르게 차단.
- Documents 런타임으로 DOCX 생성, `render_docx.py --emit_pdf`, `a11y_audit.py`, `unzip -t`, `pdfinfo`
  - PASS. 10페이지 전수 시각 QA, 접근성 0/0/0, DOCX 압축무결성, Letter 10페이지 PDF 확인.
- 인앱 Browser로 기존 로컬 결과탭 연결 및 새로고침 시도
  - Browser 세션은 복구했으나 `file://` URL 정책이 최종 강제 새로고침을 차단했다. 정책을 우회하지 않고 기존 결과탭을 deliverable로 보존했으며 정적 HTML·JS·내장데이터·회귀검증으로 보완했다.

### 최종 한계와 승인 게이트

1. 공식 GCAM 9.1 1.5°C·2.0°C는 구조만 준비됐고 수치경로는 아직 없다. JVM 성공 실행, 각 경로 10개 query export, raw unit·지역·DB hash 검증 전에는 이중 ‘공식 GCAM 효율경계’라고 부를 수 없다.
2. 국가 수소·계통·스크랩 공식값은 회사 공급한도와 단위·범위가 다르다. 사업장 계약·인도·접속 자료로 32개 자원제약을 교체해야 한다.
3. 모델 일본 SCRAP_EAF 원단위는 비교 가능한 공시 full-scope 사례의 약 22–41%다. 범위 bridge와 low/base/high CAPEX 승인 전 절대 NPV는 screening 값이다.
4. Shapley는 전력·수소 비전력입력·건설 CAPEX 3요인에 대한 정확 배분이다. 기술실패·지연·생산량·환율·정책·탄소가격까지 포함한 전위험 분해는 후속 과제다.
5. 회사별 환경·생산·재무 경계가 완전히 같지 않다. 회사 간 순위와 기업가치 판단은 금지하고 같은 회사 내부 후보·시설·계약 민감도에만 사용한다.
6. 최종 회차의 대시보드 실제 픽셀 새로고침 QA는 로컬 URL 보안정책으로 미완료다. Excel 31/31, DOCX 10/10은 실제 렌더로 완결했다.

### 후속 P0 우선순위

1. 공식 GCAM 실행환경과 경로별 10개 query export 확보·검증 후 `GCAM_15C`/`GCAM_2C`를 활성화하고 같은 고정 포트폴리오의 이중 효율경계를 다시 생성한다.
2. 사업장별 자원 계약·계통 접속·공사 일정·기술 성능보증으로 모델 추정 제약을 교체하고 후보를 다시 생성한다.
3. EAF/H₂-DRI CAPEX scope bridge와 회사 재무경계를 승인한 뒤에만 절대 NPV·투자규모를 위원회 자료로 승격한다.

## 수동 후속 — 2026-08-07 15:45–16:12 KST (영문 대시보드)

### 수행 내용

- 기존 한국어 `dashboard.html`은 보존하고 동일 모델 payload를 사용하는 독립 실행형 영문판 `dashboard_en.html`을 추가했다.
- 정적 제목뿐 아니라 JavaScript가 생성하는 추천문·효율경계 상태·강건후보·시설/자원표·툴팁·출처 및 경계 메모까지 번역했다. POSCO 한국 시설명과 한국어로 저장된 일본 설비/지역명도 영문화했다.
- 한·영 상단에 상호 언어 전환 링크를 추가하고, 이후 `python3 -m cap_efficient dashboard` 실행 시 두 파일이 항상 동시에 생성되도록 파이프라인에 연결했다.
- 영문 HTML 전체에 한글이 한 글자라도 남으면 실패하는 생성 검증과 한·영 내장 payload 구조·비문자 값 동일성을 확인하는 `scripts/validate_bilingual_dashboard.py`를 추가했다.

### 변경 파일과 산출물

- `cap_efficient/dashboard_localization.py`: 전체 화면·내장 데이터 영문 로컬라이제이션과 미번역 검출.
- `cap_efficient/dashboard.py`, `dashboard_template.py`, `__main__.py`: 이중언어 생성·언어 링크·CLI 출력.
- `tests/test_pipeline.py`, `README.md`: 영문판 회귀검증 및 실행 안내.
- `outputs/dashboard_en.html`: 영문 의사결정 대시보드.
- `outputs/bilingual_dashboard_audit.json`: 한·영 payload 동일성 감사.

### 검증 결과

- `python3 -m unittest discover -s tests -v`: 7/7 PASS.
- `python3 scripts/validate_bilingual_dashboard.py`: PASS.
- 영문 HTML 한글 문자 0개, 필수 영문 UI 6/6, 내장 payload leaf 154,156개 구조 동일, 모든 비문자 값 동일, 번역된 문자열 값 3,882개.
- 브라우저 자동 탐색은 로컬 `file://` 보안정책으로 차단되어 우회하지 않았다. 대신 독립 HTML 생성, UI marker, 언어 링크, 내장 JSON 수치 동일성 및 회귀테스트로 검증했다.
- SHA256: 한국어 dashboard `cdc4fb38…4c499`, 영문 dashboard `45ea2753…957df`, bilingual audit `f3ebb70b…e84`.

## 수동 후속 — 2026-08-08 00:20–00:53 KST (공식 프로젝트 증거층)

### 수행 내용

- 기존 의사결정 입력의 데이터 상태를 전수 진단했다. 시설 17/17, 기술 6/6, 회사 제약 4/4, 자원 제약 32/32가 모델 추정임을 확인하고, 이를 숨기지 않는 데이터 심도 평가와 P0/P1 보강 레지스트리를 만들었다.
- POSCO·Nippon Steel·JFE Steel·Kobe Steel의 공식 발표에서 9개 전환·시연·과거 프로젝트를 구조화했다. 프로젝트별 상태, 결정 단계, 용량, CAPEX, 정부지원, 가동시점, 관련 시설, 모델 매핑 상태와 scope 경고를 저장했다.
- 공식 프로젝트 CAPEX 7건을 원화 환산·Mtpa 정규화한 별도 비용 증거층으로 만들었다. full-project, expansion, restart/modification, hybrid melter, historical reline을 한 평균으로 합치지 않고 비교가능성 등급을 유지했다.
- 프로젝트 증거는 범위와 기존 합성 시설블록의 1:1 대응이 검증되기 전 최적화 입력을 자동 덮어쓰지 않도록 게이트했다. 대시보드와 Markdown에는 공시단가와 모델단가를 병렬 표시하고 scope 차이를 명시했다.
- Excel 감사본에 `Transition_Projects`, `Technology_Cost_Evidence`, `Data_Gaps`를 추가하고 34개 시트를 다시 생성·렌더했다. 새 시트 3개와 Cover를 원본 해상도로 시각 확인했다.

### 변경 파일과 산출물

- 입력·감사: `data/transition_projects.csv`, `data/technology_cost_evidence.csv`, `data/data_gap_registry.csv`
- 모델·표시: `cap_efficient/models.py`, `loader.py`, `dashboard.py`, `dashboard_template.py`, `dashboard_script.py`, `dashboard_localization.py`, `report.py`, `pipeline.py`, `__main__.py`
- 검증·문서: `scripts/assess_data_depth.py`, `scripts/build_data_audit_workbook.mjs`, `scripts/export_verified_csv.py`, `tests/test_pipeline.py`, `DATA_DICTIONARY.md`, `README.md`
- 산출물: `outputs/data_depth_assessment.csv/json`, `outputs/dashboard.html`, `outputs/dashboard_en.html`, `outputs/report.md`, `outputs/data_audit/Capital_Allocation_Baseline_Audit.xlsx`

### 공식 데이터와 출처

- POSCO: 광양 2.5Mtpa EAF, 6,000억원, 2026년 6월 가동; 0.3Mtpa HyREX 실증 계획. POSCO Newsroom 2026-06-22.
- Nippon Steel: Yawata 2.0Mtpa·6,302억엔·지원 최대 1,799억엔, Hirohata 0.5Mtpa·1,400억엔·428억엔, Shunan 0.4Mtpa·985억엔·287억엔. Nippon Steel 2025-05-30 공식 투자결정 자료.
- JFE Steel: Kurashiki 2.0Mtpa·3,294억엔·지원 최대 1,045억엔, FY2028 1분기 가동 목표. JFE Steel 2025-04-10.
- Kobe Steel: Kakogawa 0.7Mtpa scrap melting furnace·약 1,000억엔·2030년대 초 indicative, BF3 2016년 reline 200억엔, HBI 투입 BF CO2 약 20% 감축 시연. Kobe Steel 공식 발표.
- 모든 값은 `official_project_disclosure` 또는 `official_derived`로 표시했고, 확인되지 않은 항목은 공란으로 유지했다.

### 실행과 검증 결과

- `python3 -m cap_efficient validate-data`: PASS, 4개사·17시설·6기술·9공시 프로젝트.
- `python3 -m cap_efficient run --paths 1000 --seed 42` 및 `dashboard --paths 1000 --seeds 42,2025,314159`: PASS.
- `python3 scripts/assess_data_depth.py`: PASS, 가중 증거성숙도 40.6%, 공식 프로젝트 9건, 공식 비용증거 7건, 미해결 P0 8건. 점수는 정확도가 아니라 증거성숙도 지표다.
- Excel→CSV: 17개 시트 CSV + 3개 보조파일 = 20/20 의미상 또는 byte 일치.
- Excel-export CSV로 1,000경로 재실행 후 모델 parity: 14/14 핵심 산출물 byte·SHA256 동일.
- `python3 -m unittest discover -s tests -v`: 7/7 PASS.
- 영문 대시보드 감사: PASS, 한글 0자, 한·영 payload 구조·비문자 154,650개 동일.
- 대시보드 실제 픽셀 자동검사는 `file://` 보안정책으로 차단되어 우회하지 않았다. 정적 생성·회귀·내장 payload 검증으로 보완했다.

### 새로 명확해진 한계와 다음 P0

1. 시설 17개는 여전히 합성 블록이다. 회사별 공식 사업장·고로/EAF/압연라인 registry와 생산·Scope 1/2 경계를 연결해야 한다.
2. 공식 프로젝트 원가는 부대 물류·전력·정련·항만을 포함하는 범위가 서로 달라 단순 평균이 금지된다. low/base/high scope bridge가 필요하다.
3. 회사별 스크랩 계약, 수소 인도량, 계통 접속용량·일정은 아직 없다. 국가 공식 벤치마크를 회사 제약으로 직접 치환하지 않는다.
4. 공식 GCAM 1.5°C·2.0°C는 여전히 query 0/10과 0/10으로 비활성이다. JVM 실행·DB hash·원단위 export가 최우선이다.
5. 다음 심화 순서는 공식 asset registry → 프로젝트-시설 대체/증분 매핑 → 회사 resource contract → CAPEX scope bridge → 공식 GCAM 활성화다.

### 보고서 동기화 추가 검증 — 2026-08-08 00:53–00:59 KST

- DOCX 보고서에 공식 전환 프로젝트 9건, 비용증거 7건, 증거성숙도 40.6%, 데이터 상태 정의와 최신 20/20 왕복 결과를 반영했다.
- 12페이지 PDF/PNG를 전수 시각검사했다. 프로젝트 표의 상태·매핑 라벨을 축약해 읽기 쉽게 수정했고 마지막 부록의 과도한 여백을 데이터 상태 규칙으로 보완했다.
- 접근성 감사 high/medium/low 0/0/0, DOCX 압축무결성 PASS, Letter 12페이지 PDF 확인.
- 최신 보고서: `outputs/data_audit/Capital_Allocation_Reasonableness_Report.docx`; QA PDF: `outputs/docx_qa/depth_evidence/Capital_Allocation_Reasonableness_Report.pdf`.
