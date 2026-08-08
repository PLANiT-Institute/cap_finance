# AUTOPILOT — CAP 듀얼 프로젝트 완성 프로토콜 (Opus 5.0, 30분 × 14 사이클)

> 이 파일이 매 사이클의 시스템 지시다. 두 저장소에 동일 사본이 있으며, 수정 시 양쪽에 동기화한다.
> - `~/Documents/GitHub/cap_finance` (이하 **FIN**) — MILP 최적화·계약 격자·석화 포함·진단 보고서
> - `~/Documents/cap-efficient` (이하 **EFF**) — stdlib 전용·증거 레지스트리·대시보드·철강 4사(POSCO+일본 3사)

## 0. 미션 (7시간 후 도달 상태)

1. **두 프로젝트가 하나의 데이터 생태계**: 공유 시설·기업·시나리오 ID 체계, crosswalk 파일, 단위 규약(KRW 십억, 1 JPY=9.2 KRW, 1 USD=1,350 KRW)으로 상호 소비 가능.
2. **Vercel 배포**: FIN 진단 보고서 + EFF 대시보드(국·영)를 한 사이트에서 탐색 (`web/` 정적 배포, `vercel.json` 존재).
3. **GitHub 공개 툴**: 양 저장소 커밋·푸쉬 완료, README에 설치→실행→산출 재현 경로, 데이터 패키지(`releases/` 또는 `data/package/` — CSV+데이터 사전+출처 등록부) 다운로드 가능.
4. **MCP 서버 스켈레톤**: 지표·경계·시설 스케줄 조회와 데이터 패키지 다운로드 URL을 제공하는 MCP 서버 1개(EFF 쪽 stdlib 구현 선호), README에 등록 방법.
5. **수치 신뢰**: 모든 헤드라인 수치가 테스트·검증 게이트를 통과하고, 추정·주입값은 전수 문서화.

## 1. 매 사이클 프로토콜 (30분)

1. **상태 읽기 (2분)**: 두 저장소의 `ITERATION_LOG.md` 최신 항목 + `git status`. 진행 중이던 작업이 있으면 그것부터 완결.
2. **선택 (3분)**: §3 백로그에서 미완 항목 중 최상위 1개(크면 반쪽)만 선택. 새 아이디어는 백로그에 추가만 하고 이번 사이클에 하지 않는다.
3. **실행 (20분)**: 작게 만들고 즉시 검증. 규칙:
   - 허위값 절대 금지 — 못 찾으면 ESTIMATE 라벨+근거, 빈칸+사유.
   - FIN: `.venv/bin/pytest tests/ -q` 그린 유지. 파이프라인 변경 시 `--sims 2000`으로 빠른 검증 후, 사이클 여유 있으면 20000 재실행.
   - EFF: `python3 -m pytest tests -q`(또는 README의 테스트 명령) 그린 유지, `validate-data` 통과.
   - 보고서/대시보드 갱신 시 실제 렌더 확인(로컬 서브 또는 DOM 검사).
4. **커밋·푸쉬 (3분)**: 사이클마다 최소 1커밋. 메시지: `autopilot(cycle N): <무엇을>`. FIN은 origin 존재. EFF는 remote 없으면 `gh repo create` 시도(§3-B1) — 실패 시 로컬 커밋만 하고 로그에 기록.
5. **로그 (2분)**: 양 저장소 `ITERATION_LOG.md`에 append:
   `## Cycle N (시각) — 한 일 / 검증 결과(테스트·수치) / 다음 사이클 인계 / 백로그 변경`.

**중단 규칙**: 같은 오류로 2사이클 소모하면 그 항목을 백로그 하단으로 내리고 로그에 원인 가설 기록 후 다음 항목 진행.

## 2. 동기화 규약 (양방향 성장의 축)

- **정본 분담**: 데이터 증거·출처·성숙도 = **EFF가 정본** (`data/*.csv`, `data_gap_registry.csv`, `technology_cost_evidence.csv`). 최적화 방법론(MILP·계약 격자·λ·wedge)·석화 커버리지 = **FIN이 정본**. 한쪽에서 개선하면 상대 저장소에 소비 경로를 만든다(복사 금지, 참조·변환 스크립트).
- **crosswalk**: `data/crosswalk_facilities.csv` (양쪽에 동일 사본): `fin_facility_id, eff_facility_id, company_id, unit_type, capacity_basis, note`. 기업 ID 규약: `POSCO, NSC, JFE, KOBE, LOTTE, MCI`. 시나리오 규약: `NZ15, B20` (EFF의 시나리오명과 매핑 행 유지).
- **수치 크로스체크**: 사이클마다 가능하면 1개 지표를 양 모형에서 대조(예: POSCO NZ15 P50·TCaR). 2배 이상 차이나면 백로그에 원인 분석 항목 생성. 차이 자체는 오류가 아님(모형 구조 다름) — **설명 가능해야 함**.
- FIN의 시설 단위 산출은 비공개 원칙(설계서 §8-2) — 공개 패키지·Vercel 공개본에는 기업 집계만. Vercel Deployment Protection 활성화 전까지 시설 표 포함본 배포 시 README에 경고 유지.

## 3. 백로그 (우선순위순 — 완료 시 [x], 새 항목은 하단 추가)

### A. FIN 미완 (긴급)
- [x] A1. **retire 퇴행 해소**: 현재 비용최소 = "20% 폐쇄+현행 유지+예산 슬랙"(capex 0, 경계 1점). 원인: NZ15 탄소가에서 슬랙 페널티·마진 대비 전환 CAPEX가 여전히 불리하게 계상. 조치 후보: ① 예산 슬랙 상한(연 배출의 5%) 추가 ② retire를 탄소 회피 편익에서 제외(baseline 대비 증분이라 폐쇄분 탄소 회피가 과대) 검토 — 증분 정의 재점검 ③ 결과가 "수소환원+부분 리트로핏+소량 폐쇄" 혼합으로 나오는지 확인. 완료 기준: 철강 비용최소 계획에 CAPEX>0, 경계 ≥4점, ② 150~400천원/t 대역.
- [x] A2. A1 후 전체 재실행(20000) → `scripts/build_report.py web/index.html` (doctype/body 래핑 포함) → 커밋·푸쉬 → Vercel 연결 확인(사용자가 Vercel 프로젝트 연결 필요 시 README에 절차 기록).
- [ ] A3. 회귀 테스트에 retire·이원화 케이스 추가(샘플 데이터에 re_price/h2_price/margin 행 보강).

### B. EFF 기반 정비
- [x] B1. 첫 커밋 + `gh repo create PLANiT-Institute/cap-efficient --private --source=. --push` 시도. 실패 시 로컬 커밋 유지, 로그에 기록.
- [ ] B2. `outputs/` 재생성 확인(`run --paths 1000 --seed 42`) + 대시보드 2종 렌더 확인.
- [ ] B3. FIN의 월별 SMP·재생 PPA·수소가·마진 시계열(FIN `data/raw/price_history.csv`의 2026-08-07 추가분)을 EFF `data/` 증거 체계로 이식(출처 필드 보존).

### C. 데이터 연계
- [ ] C1. crosswalk_facilities.csv 작성(철강 겹침: POSCO·NSC. EFF의 JFE·Kobe는 FIN에 없음 → note에 `fin:none`).
- [ ] C2. 기술 비용 대조표: EFF `technology_cost_evidence.csv` ↔ FIN `tech_options` — 항목별 채택값·차이·사유 1페이지(`docs/tech_cost_reconciliation.md`, 양쪽 커밋).
- [ ] C3. 시나리오 정의 대조: EFF `scenario_definitions.csv` ↔ FIN D2 — 탄소가·예산 앵커 차이 표. FIN의 단조성 보정 규칙을 EFF에도 적용 여부 점검.
- [ ] C4. 크로스체크 리포트: POSCO·NSC의 P50·TCaR 양 모형 비교표(`docs/cross_model_check.md`) — 차이 요인 분해(경계 정의·마진·탄소 처리).

### D. 공개 툴화
- [ ] D1. Vercel 사이트 구성: `cap_finance/web/index.html`(FIN 보고서) + `web/dashboard/` (EFF `outputs/dashboard*.html` 복사 스크립트 `scripts/sync_web.py`) + 랜딩 `web/home.html`(두 산출물 링크·프로젝트 설명·데이터 다운로드 링크). vercel.json cleanUrls.
- [ ] D2. 데이터 패키지: `data/package/` — 공개 가능 CSV(기업 집계 지표, frontier, wedge, λ, EFF plan_metrics 등) + `DATA_DICTIONARY`(양쪽 병합) + 출처 등록부 공개분 + LICENSE 문구(출처별 재배포 조건 반영, ICIS 등 no-redistribution 수치는 제외/구간화).
- [ ] D3. MCP 서버: EFF에 `cap_efficient/mcp_server.py` (stdlib JSON-RPC over stdio) — tools: `list_companies`, `get_plan_metrics(company, scenario)`, `get_frontier(company)`, `get_facility_schedule(company)`(비공개 플래그 시 거부), `get_data_package_manifest`. README에 claude mcp 등록 예시. FIN 산출도 조회되도록 D2 패키지 경로를 읽게.
- [ ] D4. 양쪽 README 재작성: 30초 스타트, 아키텍처 그림, 산출물 표, 데이터 신뢰 등급 표, 인용 방법.

### E. 데이터 정교화 (사이클 여유 시 반복)
- [ ] E1. EPSIS 월별 SMP 2015–2024 확보 시도(웹 접근 가능 경로 재탐색·부분 인용 수집) → FIN 캘리브레이션 재실행.
- [ ] E2. 일본 3사(JFE·Kobe) 시설·프로젝트 데이터를 EFF 기준으로 검증·보강(transition_projects 9건 상태 갱신).
- [ ] E3. FIN 석화 2사에 EFF 스타일 증거성숙도 등급 부여(data_gap_registry 항목 추가).
- [ ] E4. 수소·재생 PPA 시나리오별 경로화(현 flat 가정 → 목표경로 보간, 출처: 수소 로드맵 4000원@2030, METI 30엔/Nm3@2030).

## 4. 품질 게이트 (매 사이클 종료 조건)

- 두 저장소 테스트 그린 + `git status` 깨끗(커밋됨).
- 새/변경 수치에 출처 또는 ESTIMATE 라벨.
- ITERATION_LOG 갱신됨.
- 헤드라인 서사 유지 확인: "기대값에서 싸 보이는 계획은 꼬리에서 비싸다" — 결과가 이 서사를 뒤집으면 버그 우선 의심, 진짜면 로그에 명시.

## 5. 시간 배분 가이드 (14 사이클)

| 사이클 | 초점 |
|---|---|
| 1–3 | A1→A2 (FIN 퇴행 해소·재실행·배포 갱신) + B1·B2 |
| 4–5 | C1·C2 (crosswalk·기술비용 대조) |
| 6–7 | D1 (Vercel 사이트 통합) + C3 |
| 8–9 | D2 (데이터 패키지) + C4 |
| 10–11 | D3 (MCP 서버) |
| 12 | D4 (README 정비) |
| 13–14 | E항 정교화 + 총점검(전 게이트 재확인, 최종 커밋·푸쉬, 완료 보고서 `ITERATION_LOG.md` 말미에 7시간 요약) |

밀리면 D3까지를 사수하고 E는 버린다. 앞서면 E1부터 당긴다.
