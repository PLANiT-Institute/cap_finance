# ITERATION LOG

## Cycle 0 (준비, 2026-08-07 오후) — AUTOPILOT.md 배치. FIN 상태: v2.1(수소 외부조달·전력 이원화·retire) 코드 완료, retire 퇴행(A1) 미해소, 마지막 전체 실행 15:01. EFF 상태: 커밋 0개, remote 없음. 다음: A1부터.

## Cycle 1–2 — FIN 측 A1/A2 진행(상세는 FIN 로그). EFF는 B1 완료(초기 커밋·origin 생성·푸쉬). 다음: B2 재현 확인.

## Cycle 3–4 (B2·C1·C2)
**한 일**: B2 EFF 재현 확인(validate 4사17시설 통과, run 200paths 12초, tests 7/7). C1 `scripts/build_crosswalk.py` — FIN 개별 고로 ↔ EFF 사이트 블록 매핑 33행 + 시나리오 매핑, 양 저장소 동일 사본. C2 `docs/tech_cost_reconciliation.md`.
**검증/발견**:
- **교차검증 성과**: EFF `H2_DRI_EAF`의 전력 0.58 MWh/t(전해조 제외)이 FIN A1 수정값 0.85와 수렴 — 독립 두 모형이 "수소 외부조달 시 전해조 전력 제외" 원칙에 도달. FIN의 이중계상 버그를 EFF 대조로 확증.
- CAPEX 863(FIN, DIW) vs 900(EFF, 프로젝트 기반) = 4% 이내 정합.
- **불일치 발견**: 공통 17기 능력 합 FIN 77.2 vs EFF 68.8 Mtpa (12%) — FIN 내용적×913 계수 상방 편의 가설. 백로그 E5로 추적.
- 스크랩 EAF는 EFF가 정본(실제 프로젝트 6건 증거), FIN은 전환 옵션에서 제외(설계 차이 명시).
**다음**: D1 Vercel 사이트 통합.
