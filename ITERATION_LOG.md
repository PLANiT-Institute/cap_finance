# ITERATION LOG

## Cycle 0 (준비, 2026-08-07 오후) — AUTOPILOT.md 배치. FIN 상태: v2.1(수소 외부조달·전력 이원화·retire) 코드 완료, retire 퇴행(A1) 미해소, 마지막 전체 실행 15:01. EFF 상태: 커밋 0개, remote 없음. 다음: A1부터.

## Cycle 1–2 (A1+A2 완료)
**한 일**: retire 퇴행 근본원인 2건 수정.
1. 전해조 전력 이중계상 — v2.1에서 수소를 외부조달로 전환했으나 `steel_h2dri`/`steel_hyrex`의 elec_intensity가 Vogl 총 SEC(수전해 포함)로 남아 수소 대금+전해조 전력 동시 부과. 0.85 MWh/t(샤프트+EAF+부대)로 보정 → 수소환원 연간 자원비용 958→498천원/t.
2. 무상할당 미반영 — 탄소비용을 배출 전량 부과(2050 726천원/t vs 철강 마진 70천원/t)해 "전 설비 폐쇄"가 최적해. `carbon_auction_share` 도입(K-ETS 4차 발전외 15% 앵커, 2030 이후 ESTIMATE 램프). 배출량은 예산 제약에 전량 계상 유지.

**검증**: 테스트 13/13 그린. 완료 기준 충족 — CAPEX>0(POSCO NZ15 11.0조), 경계 5–10점(NZ15), ② 96–331천원/t. POSCO 최적 = 효율개선 4기 + 수소환원 2기(2036/2038) + 폐쇄 2기(광양1고로 2028 = 재투자 창과 일치, FINEX3 2026) — 혼합 해로 정상화.

**다음**: B1(EFF 커밋·remote 완료됨) 확인 후 C1(crosswalk) → D1(Vercel 사이트 통합).
**백로그 변경**: A1·A2·B1 완료 처리.

## Cycle 3–4 (B2·C1·C2) — 상세는 EFF 로그. 요약: crosswalk 33행 생성(FIN 고로 ↔ EFF 블록), 기술비용 대조표 작성. EFF의 H2-DRI 전력 0.58이 FIN A1 수정(0.85)을 교차확증. 능력 기준 12% 차이는 추적 항목.

## Cycle 5 (D1 Vercel 사이트 통합)
**한 일**: `scripts/build_site.py` — FIN 보고서 + EFF 대시보드(국·영) + 랜딩을 `web/`으로 조립하는 단일 명령. vercel.json에 noindex·no-referrer 헤더 추가(시설 표 포함본 보호).
**검증**: 로컬 서브 index/report/dashboard 전부 200, 렌더 육안 확인. 중첩 앵커(a 안 a)로 카드 레이아웃 깨진 것 수정. web/ 12MB (대시보드 6MB×2).
**Vercel 연결 절차**(사용자 작업): Vercel > New Project > PLANiT-Institute/cap_finance > Framework: Other, Output Directory `web` > Deploy. 시설 단위 표 포함이므로 Settings > Deployment Protection 활성화 권장.
**다음**: C3(시나리오 정의 대조) 또는 D2(데이터 패키지).

## Cycle 6 (F1 파라미터 인벤토리) — AUTOPILOT v2 체제 시작
**한 일**: `scripts/build_parameter_inventory.py` — FIN·EFF 전 입력 파라미터 408건을 증거등급(T1~T5)·출처·사용처와 함께 단일 표로. `docs/parameter_inventory.csv` 양 저장소.
**결과**:
| 모형 | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|
| FIN | 3 | 130 | 41 | 79 | 42 |
| EFF | 0 | 7 | 0 | 0 | 113 |

**발견 2건**:
1. **EFF 모형 입력 113건이 전부 자기선언 `model_estimate`(T5)** — README가 명시한 설계대로지만, 별도 증거 파일(`technology_cost_evidence` 실제 프로젝트 7건 = T2)이 **모형 입력에 연결돼 있지 않다**. 증거는 있는데 쓰이지 않는 구조. → 백로그 신규 항목.
2. **T5 중 범위 미지정 139건** — FIN 26건(EST_v0 예산·가격 경로), EFF 113건. AUTOPILOT §1 규칙 위반이므로 F3에서 범위 부여 대상.
**결론 영향**: 없음(측정만). 단 다음 사이클 F2의 작업 순서를 이 표가 결정.
**다음**: C7 = F2 사전 민감도 스크리닝 — 어느 파라미터가 헤드라인을 좌우하는지 측정, 상위 10의 tier가 데이터 승급 순서가 됨.

## Cycle 7 (긴급 수정 — 테스트가 실산출물 오염)
**발견**: `tests/test_pipeline.py`가 `data/sample`(합성)로 전 파이프라인을 돌리며 `out_dir`을 실행본과 공유 → **실데이터 산출물 `out/`을 합성 결과로 덮어씀**. 그 상태에서 생성된 보고서·웹이 합성 수치를 게재(석화 ② −960천원/tCO₂ = "전환하면 돈 번다"는 불가능한 값).
**조치**: 테스트 `out_dir="out_test"` 격리 + 재발 방지 테스트 `test_outputs_isolated_from_production` 추가 + .gitignore.
**실데이터 정상 재실행 결과** (NZ15, support=none):
| 기업 | CAPEX(조) | 피크 | P50(조) | ②(천원/tCO₂) | TCaR(조) |
|---|---|---|---|---|---|
| POSCO | 21.7 | 2030 | 73.8 | 130 | 51.5 |
| NSC | 33.4 | 2032 | 83.8 | 173 | 57.8 |
| LOTTE | 1.4 | 2046 | 0.5 | 257 | 1.7 |
| MCI | 0.6 | 2045 | 0.2 | 264 | 0.8 |
경계 점 NZ15 4–6. ② 130–264천원/tCO₂ = 문헌 대역 내(H3에서 정식 대조 예정).
**교훈**: v1 기준("테스트 그린")으로는 통과했을 결함. v2의 "출처·재현·검증" 기준이 잡아냄. 재현성 게이트를 품질 게이트에 명시적으로 추가할 것.
**다음**: C8 = F2 사전 민감도 스크리닝.

## Cycle 8 (F2 사전 민감도 스크리닝)
**방법**: E2 계획 집합 고정(perturbation마다 MILP 재해는 7분 소요라 비현실적) → E4/E5 경제성만 재평가. 파라미터 25종 ×(±30%) × 4사, n=3,000. 계획 선택 채널은 I1/I2 전체 재실행으로 별도 확인.
**기준선(NZ15, 계획 고정)**: POSCO LCOA 131 / NSC 165 / MCI 191 / LOTTE 233 천원/tCO₂.
**상위 12 (4사 중 최대 |Δ|%)**:
| 순위 | 파라미터 | tier | ΔLCOA% | ΔTCaR% |
|---|---|---|---|---|
| 1 | fac.ef_inc (기존 시설 배출 원단위) | **T5** | 86.4 | 0 |
| 2 | tech.emission_factor | T3 | 85.8 | 0 |
| 3 | cfg.discount (할인율) | T5 | 7.3 | 42.5 |
| 4 | vol.h2 (수소 변동성) | **T5** | 10.8 | 41.9 |
| 5 | tech.h2_intensity | T3 | 12.1 | 30.7 |
| 6 | price.h2 | **T5** | 12.1 | 30.7 |
| 7 | vol.elec | T3 | 0.9 | 25.8 |
| 8 | fac.capacity | T2/T5 | 17.8 | 1.4 |
| 9 | tech.capex | T3 | 17.4 | 1.4 |
| 10 | tech.elec_intensity | T3 | 7.4 | 13.6 |

**핵심 발견**: 1위가 `fac.ef_inc` — **기존 설비의 배출 원단위**이고 현재 **T5(루트 표준값 주입, BF 2.15 tCO₂/t)**. LCOA를 86% 움직이는 파라미터가 가장 약한 증거 위에 있다. 이것이 G1(시설 실측 배출) 최우선 근거.
수소 관련 3종(vol.h2·price.h2·h2_intensity)이 TCaR의 30~42%를 좌우 — 수소 가격 시계열 부재(사전값 vol 0.25)가 두 번째 승급 대상.
**승급 작업 순서 확정**: ① fac.ef_inc → G1 시설 실측 ② price.h2/vol.h2 → 수소 계약가 시계열 ③ fac.capacity → G3 ④ 할인율은 데이터가 아닌 선택이므로 I1 강건성으로 처리.
**다음**: C9 = H1 내부 일관성 테스트(순서 조정 — G1 웹수집 전에 검증층부터), 이어서 G1.

## Cycle 9 (J6 일부 — 증거·민감도 시각화 페이지)
**한 일**: `scripts/build_evidence_page.py` → `web/evidence.html`. 3개 차트: ① 우선순위 매트릭스(가로 영향력 × 세로 증거등급, 위험구역 음영) ② 토네이도(LCOA/TCaR 영향 이중 막대, 등급별 색) ③ 등급 분포(FIN vs EFF 누적). build_site.py에 통합돼 사이트에서 도달 가능.
**설계 근거**: 등급은 순서형이라 단일 색상 램프를 쓰되 T4/T5는 상태색(경고/위험)으로 분기 — "증거가 약하다"는 상태 정보를 색으로 전달. 매트릭스 우하단이 위험구역.
**다음**: C10 = H1 내부 일관성 테스트.
