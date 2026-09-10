# L4 · 범위 규율 (2026-09-11 06:44 KST)

관점: 중심 문장 하나 — **효율경계(frontier)를 만들어 불확실성을 줄이는 자본투자의 효율성을 재는 것** — 에 비추어 저장소 전체를 핵심·부속·중심 밖으로 나눈다. 지우지 않는다. 표기만 바꾼다.

## 분류

| 구분 | 구성요소 | 판정 근거 |
|---|---|---|
| **핵심** (경계를 만드는 것) | `src/cap`: e1_constraints, e2_milp, e3_prices, calibration, price_process, plancost, capital_ledger, carbon_accounting, commodity_ledger, energy_balance, component_capital, company_boundary, production_bounds, input_boundaries, solver_validation, e4_revalue, e5_metrics, risk_metrics, tail_attribution, schemas, config, __main__, render · `scripts/prepare_raw.py`, `prepare_v2_price_history.py`, `expand_research_candidates.py`, `verify_research_case.py`, `build_web_platform.py` · `tests/test_v2_audit_fixes.py`, `test_pipeline.py`, `test_capital_ledger.py`, `test_block_moments.py`, `test_budget_contract.py` · 웹 탭 "전환계획 비교"·"데이터"·"모형의 원리" · `paper/methodology/TCaR_METHOD_V2_KO.md`, `TCaR_METHOD_KO.md` §3–6 | 후보 생성 → 결합 가격경로 → 현금원장 → (μ, ES_abs) 경계까지의 한 줄 파이프라인 |
| **부속** (핵심을 검증·설명하지만 경계를 만들지 않음) | `src/cap`: reference_ncc, reference_steel, reference_timing, reference_incumbent, reference_delivery, joint_prices, scenario_prices, block_moments, fx_settlement, invoice_fin, supply_network, grid_factors, financial_reference, disclosed_path, disclosed_feasibility · `scripts`: ncc_joint_control, ncc_cash_workbook_control, timing_workbook_control, joint_workbook_control, all_models_workbook_control, research_control(+contract), xlsx_*, research_block_price_paths, build_tiggeloven_supplement, verify_ncc_*, verify_steel_*, verify_joint_control, audit_* · `data/research_v2`의 참조 원장 34개 폴더 · 웹 탭 "참조 실험"(Simulator) · `docs/*_CONTROL_KO.md` 5종 · `paper/methodology`의 NCC/STEEL/FX/INVOICE 부속 문서 20여 개 | 공정 참조 원장·Excel 컨트롤·FX 정산은 입력의 타당성을 점검하는 도구다. 기업 경계의 좌표를 바꾸지 않으며, 각각 별도 범위·통화연도·시드·α를 쓴다 |
| **중심 밖** (다른 목적의 라인) | `src/cap/mcp_server.py` · `cap-efficient/`(독립 EFF 도구) · `docs/seminar`, `docs/climate_finance_seminar_1`(세미나 리서치 8회차) · `paper/pilot_review`(외부 검토용 배포) · `AUTOPILOT.md`·`ITERATION_LOG.md`(475KB) · `output/`, `out_test/` | 경계의 정의·데이터·결과에 기여하지 않는다. 보존하되 README·웹에서 언급하지 않는다 |

핵심 코드는 40개 모듈 중 23개, 스크립트는 192개 중 대략 6개다. 나머지는 검증 부속이거나 다른 라인이다.

## 확산 본능 계수

2026-08-11 이후 30일 동안 새로 열린 라인을 폴더 생성 기준으로 세면 다음과 같다. `data/research_v2` 하위 참조 원장 45개 폴더(전부 신규), 연구 사이클 기록 7묶음, 참조 모형 3종(NCC joint·cash·timing)과 철강·incumbent·delivery 참조 3종, Excel 컨트롤 4종, 웹 플랫폼, MCP 서버, 세미나 리서치 8회차, pilot_review, journal_prep. 스크립트 175개가 30일 안에 새로 생겼다. 커밋 메시지 기준으로는 autopilot 13회, 세미나 리서치 8회, 검증 루프 4회가 병렬로 돌았다.

같은 기간에 핵심 경계의 정의(A1 위험 축)와 가격 모형의 실체(A3 단위행렬)는 8월 문서(`frontier_degeneracy.md`, 실행 로그)에 이미 적힌 채 그대로였다. 확산은 넓이가 아니라 중심을 비운 채 넓어졌다는 점이 문제다. 이 루프의 L0–L3가 한 일은 새 라인을 여는 것이 아니라 중심을 채우는 것이었고, 남은 회차도 그렇게 간다.

## 표기 변경

README의 첫 문단과 "웹 연구 도구" 절에 핵심/부속 구분을 적고, 웹 참조 실험 탭의 설명을 "부속 · 기업 경계 결과와 무관"으로 바꾼다. 영문·국문 투고 초안의 초록·1.2·1.4·8절을 v2.2 정본에 맞게 다시 썼다(TCaR 자금수량 해석 삭제, 철회된 공시 gap 헤드라인 삭제, P50=기대비용 표현 삭제, 기여를 "응용 하나 + 결과 둘"로 격하, 핵심 결과를 "수소가격 기준과 할당 규칙이 철강 전환의 부호와 꼬리 감소를 정한다"는 조건부 발견으로 재서술). 본문 §5–6의 수치는 아직 v1 실행 기준이므로 초록과 본문이 잠시 어긋난다 — L6에서 E2 재실행 후 본문 표를 갱신하기 전까지 투고하지 않는다.

## 이 회차가 하지 않은 것

파일을 지우거나 옮기지 않았다. cap-efficient·MCP·세미나 라인의 존폐는 사용자 결정이다. 투고 초안 본문(§5–6 표)은 v1 수치 그대로다.
