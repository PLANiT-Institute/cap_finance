# 재현 자료 위치와 판본 범위

v2 자료와 변환 근거는 `data/research_v2/` 및 `docs/research_cycles/2026-09-06/`, `2026-09-07/`에 있다. v2 가격생성법의 정확한 앵커·시드·지평·계열·원자료 해시는 `block_price_paths/manifest.json`과 `exact_log_anchors.json`에 보존한다. 원고 숫자 검사는 수치 일치와 과학적 외부 검증을 구분한다.

문헌 확인 범위·판본·출처 사본 해시는 `docs/research_cycles/2026-09-05/literature_register.csv`와 `literature_access_audit.json`에 기록한다. 부록 A의 과거 위험 통계와 계약 선택은 같은 폴더의 `gap_engine_v2/risk_measure_comparison.csv`·`criterion_choices.csv`, 과거 공시 대용치 간격은 `out/e5/gap.csv`에서 가져왔다. 본문 표 7은 `research_case_expanded` 실행, 표 8–9는 `robustness_verified`, 표 22는 `excel_control` 감사 자료를 따른다. 검증 이력은 `RESEARCH_LOG.md`와 각 실행 로그를 따른다. 원문 선택 수치 238개는 `selected_primary_observation_register.csv`에 단위·기업 경계·원문 위치·출처 해시와 함께 통합했다. 세부 판단과 실패 기록은 데이터 감사서 및 회차별 연구 로그에 보존한다.

현행 판본의 완료 보완 기록은 docs/research_cycles/2026-09-07-hourly/STATE.json과 해당 completion 검증 파일을 따른다. 기업 생산·구매 자료는 data/research_v2/company_process_bridge/, 공급 연속성 자료는 data/research_v2/supply_continuity/에 별도 보존한다. 과거 원문238개 등록부가 이후 추가 자료 전체를 포함하는 것은 아니다.

표 7–9·22와 부록 A의 동결 기업 실행 입력은 `data/prepared/D1–D7*.csv`이며, `data/sample/D*.csv`는 전 행이 `SAMPLE_SYNTH`로 표시된 합성 검사 자료로 결과 산출에 쓰지 않는다. `data/research_v2/*/manifest.json`의 원문·중간 파일 해시 가운데 `tmp/` 경로는 저장소에 포함되지 않은 저자 로컬 사본을 가리키므로, 외부에서는 등록부 CSV의 값과 출처 위치만 재검할 수 있고 해시 자체는 재현 대상이 아니다.


6.16절 표19–20·그림18은 `data/research_v2/ncc_timing_frontier/`, 6.17절 표21·그림19는 `data/research_v2/steel_procurement_tail/`의 저장 실행을 따른다. 원료가격 그림의 본문용 배치는 같은 저장값으로 다시 그렸으며 새 표본을 만들지 않았다. 두 실험의 원문·입력·경로·숫자 검증 범위는 각 manifest와 독립 검증기, `NCC_TIMING_FRONTIER_KO.md`·`STEEL_PROCUREMENT_TAIL_KO.md`에 명시돼 있다. 공동 연구 통제 최신 파일은 v6이며 `docs/ALL_MODELS_CONTROL_KO.md`가 세 분석의 재계산 안내다. 본문 통합 검증은 `docs/research_cycles/2026-09-07-hourly/completion_21_verification.json`을 따른다.

2026-09-08 외부 공유판 개정(v2.21–v2.28)의 4축 심사 원문, 회차별 수정·검증 기록, 신규 검증 스크립트(`verify_criterion_decision_table.py`, `verify_theta_sensitivity_table.py`)의 출력은 `docs/research_cycles/2026-09-08-hourly/`에 있다. 2.2절 정책 수치의 원문 인용 확인은 `data/research_v2/frontier_industry_context/policy_claims_url_only.json`에 기록했다.


v2.31의 부록 C.11·표 C7·그림25는 `data/research_v2/ecb_fx_reference/`의 ECB 역사 원문과 공동9요인 패널,12개월 블록 전수 분포를 따른다. `manifest.json`은 원자료·변환, `experiment_manifest.json`은180/32,400상태 정의·정규화·분위수 규약과 결과 해시를 연결한다. 원자료·전수계산의 독립 검증은 `docs/research_cycles/2026-09-07-hourly/completion_26_verification.json`, 본문 통합·환산 지배 관계 예제·기존 표 보존은 `completion_27_verification.json`과 `completion27_evidence/`에 있다. 별도 설명은 `FX_JOINT_CONVERSION_KO.md`이며, 월별 결제의 연중 공분산 표현은 최신 본문 C.11에서 명확히 했다. 미래 환율·물가 경로 및 기업의 청구 통화·환헤지 비중은 미설정이며 기존 기업 실행·Excelv6 입력은 갱신하지 않았다.


기업 외화 공시의 후속 검증은 `data/research_v2/company_fx_scope/`와 `COMPANY_FX_SCOPE_KO.md`에 있다. 금융잔액·조건부 민감도·헤지 계약/장부값·공정 구매 흐름을 구별하며 원문120항목·38산술의34일치/4미해결, 미쓰이 당기 표 제목의 모호함과 차기 비교 표 확인을 기록한다. 검증은 `docs/research_cycles/2026-09-07-hourly/completion_28_verification.json`을 따른다. 현재 본문 v2.31 및 기업·Excel 입력에는 미반영이다.


청구가격일·지급일·통화·실질기준의 고정 물량 결제 모듈은 `src/cap/fx_settlement.py`, 설명은 `FX_SETTLEMENT_ENGINE_KO.md`에 있다. `tests/test_fx_settlement.py`의26검사와 기존 상품 원장10검사가 통과했다. `scripts/verify_fx_settlement_integration.py`는 동결된 completion26 분포195480비용·60통계를 재현하며 `data/research_v2/fx_settlement_validation/`에 기록한다. 검증 보고서는 `docs/research_cycles/2026-09-07-hourly/completion_29_verification.json`이다. 분포 재추출·기업 보정·FIN/Excel 통합은 하지 않았으며 본문/PDFv2.31·Excelv6는 보존했다.


후속 FIN 연결은 `src/cap/invoice_fin.py`의 선택적 추가 상품 원장 교체 함수다. 기존 `simulate_cost`·기본 실행은 보존한다. `INVOICE_FIN_BRIDGE_KO.md`가 동일 물량만으로는 상쇄되지 않는 조건과 지급일 예시를 설명한다. `data/research_v2/invoice_fin_bridge/`에 동결NCC40000비용·30통계 대조와 예시 입력/그림, `docs/research_cycles/2026-09-07-hourly/completion_30_verification.json`에53검사·14표값·시각검수 범위가 있다. 새MC/기업보정/Excel적용은 없으며 본문/PDFv2.31·Excelv6를 보존했다.


v2.32의7.5절과C.12·표C8·그림26은 완료28–30의 기업 외화공시·결제모듈·선택적FIN연결을 통합한다. 본문 검증은 `docs/research_cycles/2026-09-07-hourly/completion_31_verification.json`, 기존 행/수식/그림/참고항목과 최종73쪽 렌더 증거는 `completion31_evidence/`에 있다. 회사 금융잔액·공시 스트레스와 연간 구매/미래확률을 구별하며,공통 원료비 상쇄는 경로별 할인현금흐름 일치 조건이다. 표C4의 자료상태1행만 의도적으로 갱신했고 기존222표행을 보존했다. Excelv6·동결기업실행·조건부 참조분포는 변경하지 않았다.
