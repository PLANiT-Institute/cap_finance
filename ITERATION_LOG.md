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

## Cycle 10 (데이터 진위·활용 감사 + 조달부담 지표 ⑥) — 사용자 5개 점검 체제 시작
**한 일**
1. `scripts/audit_data.py` — 입력 9파일 88컬럼을 (a) 채움률 (b) 엔진 참조 여부 (c) 출처 해소 여부로 전수 판정. `docs/data_audit.csv` + `.md`. 합성 샘플과 바이트 동일하면 실패 종료(가짜 주입 게이트).
2. **config 기본값 결함**: `data_dir: data/raw`인데 파이프라인은 `D*.csv`(=`data/prepared`)를 읽어 `python -m cap` 무인자 실행이 SchemaError로 죽었다. `data/prepared`로 수정 — "한 명령 재현"이 실제로 성립.
3. **CAPEX 시점 결함(근본)**: `plancost.build_profile`이 CAPEX 전액을 채택연도 1년에 계상, `build_years`는 가동개시만 이동시켰다. 공사기간 균등 분산으로 수정. 피크가 최대 공사기간 배수만큼 과대였음.
4. **지표 ⑥ 조달부담 신설**: D6 재무 6개 컬럼(revenue/ebitda/total_debt/net_debt/interest/cash)이 **전량 미사용**이던 것을 소비 → `out/e5/affordability.csv` + 보고서 2절(표+피크배수 막대).

**검증(수치)**
- 감사 판정: ok 70 / UNUSED 15 / CONSTANT 3 / EMPTY 0 / 합성누출 0 / 미해소 출처 0 / 추정라벨 4(EST_D2A_V0·EST_D2B_V0·PREP_ALLOC·PREP_BOTTOMUP).
- CAPEX 분산 전후 피크(NZ15, none): POSCO 18.6조→**5.6조**, NSC 23.8조→**8.6조**, LOTTE 0.75→0.71, MCI 0.34→0.32.
- 헤드라인 ②(천원/tCO₂) 전후: POSCO 130→128, NSC 173→170, LOTTE 257→251, MCI 264→258. **결론 불변**(할인시점 이동분만).
- 테스트 14/14 그린.

**결론 영향(신규)**: 조달부담이 순위를 뒤집는다. 비용/tCO₂로는 POSCO(128)가 가장 싸지만 피크배수 3.1×·총 CAPEX/EBITDA 12.2×로 부담은 최대. LOTTE는 CAPEX 1.4조로 최소지만 **기준 EBITDA가 음수(−0.72조)라 자체 조달 자체가 불가**. MCI만 피크 0.3×로 여유. → "얼마 드는가"와 "감당 가능한가"가 다른 기업을 지목한다.

**데이터 공백(정직 기록)**: POSCO·LOTTE의 net_debt/total_debt 공시 미확보 → 사후 레버리지 미산출. D6 보강 대상.
**백로그 신규**: 미사용 15컬럼 중 실질 3건 — `D1b.emissions_s2`(전 행 0, Scope2 미모형화), `D3.capex_uncertainty`(기술별 불확실성 미전파 → F3), `D5.param_type`(유상할당 비율이 데이터에 있는데 config 하드코딩 사용, 2030년 값 데이터 50% vs config 15% **충돌**).
**다음**: C11 = D5 유상할당 충돌 해소(데이터를 정본으로) + H1 내부 일관성 테스트.

## Cycle 11 (정책 입력 정본화 · 가격경로 결함 · 실행가능성 · MCP)
**한 일**
1. **D5 유상할당 충돌은 충돌이 아니라 정보 소실이었다.** 원자료는 발전부문 50%(2030)와 **발전외(철강·석화) 15%(2026–2030)**를 구분해 두었는데 `prepare_raw`가 `instrument`를 전부 `"other"`로 눌러 구분이 사라졌고, config는 별도 하드코딩 램프를 썼다. `instrument`를 `auction_share`(발전외)/`auction_share_power`/`price_cap`/`price_floor`로 분류하고, `plancost.auction_share`가 **확정 할당계획을 config 추정 램프보다 우선**하도록 했다. 2026–2029 유상할당 0.11→0.15(확정값).
2. **가격 경로 결함(중대)**: D2b의 Korea `h2_price` 2025 셀이 비어 있었고 E1이 그 NaN을 그대로 보간해 경로 전체를 오염시켰다. E2는 오염된 경로를 거부하고 **v2.1에서 폐기한 전해조 구조식으로 조용히 되돌아가 있었다** — 안내는 로그 14줄 뒤 `note` 한 줄뿐. 즉 한국 2사(POSCO·LOTTE)의 수소 비용이 설계와 다른 모형으로 계산되고 있었다. E1이 결측 앵커를 제거·평탄 외삽하고 **그 사실을 경고로 알리며**, 보간 결과에 NaN이 남으면 즉시 실패하도록 수정. 실행 후 구조식 대체 발동 **14회 → 0회**.
3. **실행가능성**: E2가 20분 넘게 무출력으로 돌아 정지와 구분이 불가능했다. 조합별 진행 표시 추가 + `mip_gap_rel: 0.005` 도입 — E2 목적함수는 계획 **순서만** 정하는 대리이고 정본 비용은 E4가 낸다. 조합당 36초로 안정.
4. **감사 스크립트 자체 결함 2건**: (a) `schemas.py`가 엔진 스캔에 포함돼 전 스키마 컬럼이 "사용됨"으로 오판. (b) pandas 3에서 `astype(str)`이 NaN을 `"nan"`으로 바꾸지 않아 **빈 셀이 전부 채워진 것으로 계수**됐다. 둘 다 수정, `PARTIAL` 판정 신설.
5. `tests/test_consistency.py` (H1) — 실산출물 대상 12개 항등식: 자원비용 정의, TCaR 정의, 분산 몫 합=1, 기준선 배출의 원자료 왕복, 전환이 배출을 늘리지 않음, CAPEX 피크≤총액·공사기간 분산 회귀방지, 조달비율 재계산 가능, 가격경로 무결성, 수소 구조식 미발동, 확정 할당계획 우선, 발전부문 값 미유입, 경계점 파레토 비지배.
6. **MCP 서버** `src/cap/mcp_server.py` (stdlib, stdio JSON-RPC) + `docs/mcp_server.md`. 10개 도구, 모든 응답에 정의·한계 동봉, `get_validation_summary`는 **없는 검증을 missing으로 명시**, 시설 단위는 기본 거부.
7. E2가 매 실행 이전 실행의 잉여 계획 파일을 남기던 것 정리(`plans/` 초기화).

**데이터 감사 재판정** (결측 계수 수정 후): ok 67 / UNUSED 11 / PARTIAL 6 / EMPTY 2 / CONSTANT 2.
- **EMPTY 2건**: `D1b.energy_naphtha` 0/69 — 석화 NCC의 **주 원료가 미수집**. `D7.coverage_pct` 0/12.
- **PARTIAL 6건**: `D2b.value` 222/224(위 §2 원인), `D6.capex_total` 11/22·`net_debt` 9/22, `D7.facility_id/tech_id` 8/12(= 공시 해상도 부족으로 gap 미산출되는 그 행들).

**미해결·다음 사이클로**: `prepare_raw`가 **원자료의 Scope 2 배출을 0으로 덮어쓰고 있다** — raw 36/37행에 값이 있고 NSC는 11.9 MtCO₂(scope 1의 19%). 수집해 놓고 버리는 중이며, 기존 설비는 계통전력을 쓰고 전환설비는 재생 PPA를 쓰는 모형 구조상 **경계 불일치**다. C12에서 보존 + 경계를 config로 명시.
**다음**: C12 = Scope 2 보존·경계 명시 → 시나리오 러너 실행 → 시나리오 페이지.
