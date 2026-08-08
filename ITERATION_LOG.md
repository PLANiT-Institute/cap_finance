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
