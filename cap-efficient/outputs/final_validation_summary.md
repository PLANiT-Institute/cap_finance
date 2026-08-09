# Capital Allocation Pathway — 최종 검증 요약

기준시각: 2026-08-08 00:59 KST  
모델: v0.8.0 · 구조 검증용 / 투자 승인용 부적합

## 최종 판정

이 모델은 POSCO·Nippon Steel·JFE Steel·Kobe Steel 내부에서 전환 후보의 상대적 비용·위험·실행제약을 비교하는 **의사결정 screening 도구로는 사용 가능**하다. 입력 추적성, 동일 물리 포트폴리오 비교, 반복 Monte Carlo, Excel 왕복, 모델 동일성, 정확한 3요인 Shapley 재조정은 검증됐다.

공식 기업 발표 9건과 정규화 비용증거 7건을 별도 증거층으로 추가했지만, 범위·시설 매핑 검증 전에는 최적화 입력을 자동 변경하지 않는다. 공식 GCAM 1.5°C·2.0°C 수치경로가 아직 비활성이고 회사별 자원 공급한도와 대형 전기로/H₂-DRI CAPEX 범위가 추정치이므로 **기업 간 가치 순위, 절대 NPV, 투자위원회 승인에는 사용하지 않는다**.

## 계산 범위와 핵심 결과

- 4개 기업, 17개 시설 블록, 2개 활성 경로, 2026–2040년.
- 910개 생성후보 → 217개 확률평가 후보 → 37개 고정 정밀 shortlist.
- 3개 seed(42, 2025, 314159) × 정밀후보·시나리오당 1,000경로 = 3,000 유효경로.
- λ=1 추천은 POSCO·Nippon Steel·JFE Steel·Kobe Steel 모두 P3 계열이며 3회 선택빈도 100%.
- 최대후회/최악 TCaR(kKRW/tCO₂): POSCO 54.17/15.26, Nippon Steel 58.99/18.72, JFE Steel 27.20/27.50, Kobe Steel 94.09/27.24.
- 추천안의 37/37 시나리오 연결은 동일 물리 포트폴리오이고 정렬 CAPEX 차이는 0이다. 선택 추천의 내부 스트레스→공시경로 ΔP50은 +9.58~+12.69, ΔTCaR은 −1.52~−0.93, Δ절대 NPV P50은 +1,052.8~+5,444.1bn KRW다.
- 선택 추천의 정확한 Shapley 합계 최대오차는 `1.0e-9`, 전체분산 재조정 오차는 0이다. 현금비용−탄소회피가치=경제 NPV 항등식의 최대 차이는 CSV 반올림 후 0.000334bn KRW다.
- 17개 고유 시설 액션을 두 활성 시나리오에서 동일하게 평가했다. 선택 추천의 120개 연도별 자원행은 모두 제약을 통과했으며 전 시나리오 최대 이용률은 스크랩 95.8%, 수소 72.1%, 증분계통 99.5%다. 이 분모는 `model_estimate`다.

## 재현성과 감사

| 검증 | 결과 |
|---|---:|
| 입력 구조 검증 | PASS — 4회사·17시설·6기술·8 회사-시나리오·32 회사-계획 |
| 공식 프로젝트 증거 | 9건; 정규화 비용증거 7건; 모델 입력과 분리 |
| 데이터 증거성숙도 | 40.6% — 정확도 점수가 아님; 미해결 P0 8건 |
| Excel→CSV 왕복 | PASS — 17개 CSV 시트 + 3개 보조파일 = 20/20 |
| Excel 재생성 모델 동일성 | PASS — 14/14 |
| 회귀테스트 | PASS — 7/7 |
| 한·영 대시보드 동일성 | PASS — 비문자 payload 값 동일, 영문판 한글 0자 |
| 대시보드 인라인 JavaScript | PASS |
| Excel 수식 오류 검색 | PASS — 0건 |
| Excel 시각 QA | PASS — 34/34 시트(기존 31개 유지 + 신규 3개·Cover 재확인) |
| DOCX 접근성 감사 | PASS — high/medium/low 0/0/0 |
| DOCX 시각 QA | PASS — 12/12 페이지 |
| GCAM 매니페스트 | 구조·hash PASS; 1.5°C/2.0°C query 0/10, 활성화 차단 |

## 최종 산출물

- 의사결정 대시보드: 한국어 `outputs/dashboard.html`, 영어 `outputs/dashboard_en.html`
- 한·영 동일성 감사: `outputs/bilingual_dashboard_audit.json`
- 데이터 감사본: `outputs/data_audit/Capital_Allocation_Baseline_Audit.xlsx`
- 전문 보고서: `outputs/data_audit/Capital_Allocation_Reasonableness_Report.docx`
- 보고서 PDF QA본: `outputs/docx_qa/depth_evidence/Capital_Allocation_Reasonableness_Report.pdf`
- 데이터 심도 감사: `outputs/data_depth_assessment.csv`, `outputs/data_depth_assessment.json`
- Excel 왕복감사: `outputs/data_audit/roundtrip_audit.json`
- 모델 동일성감사: `outputs/data_audit/model_parity_audit.json`
- 전체 실행기록: `outputs/automation_progress.md`

| 산출물 | SHA256 |
|---|---|
| `dashboard.html` | `9b78c745ed130f1055208850a21081fcca31bc1895a1bb97587dc9b4f3227870` |
| `dashboard_en.html` | `8eea6b6df77700cb7d70a3a3c539471059b168775264f2be94388309c0549a9f` |
| `Capital_Allocation_Baseline_Audit.xlsx` | `34f725c2dfe29c46f3af77fb9703a157af742c20889fd2a2a4ee30fb0c383f01` |
| `Capital_Allocation_Reasonableness_Report.docx` | `31d95a9b5263be9cb10430af17c6fbedda202c9f8ca2448b90dddd3b8006b345` |
| 최종 QA PDF | `6cc0409c0bfb1139d3bc3b6d72078bac3e8d2e179aa84f0a5af18593caf20492` |
| `data_depth_assessment.json` | `3d197a0ab2b73f58b7ee76d7fc3db21aed13d32ef9286074a8b5e120ab1da026` |

## 남은 승인 게이트

1. GCAM 9.1 JVM 성공 실행과 1.5°C/2.0°C 각각 10개 공식 query export, SHA256·단위·지역경계 검증.
2. 회사·사업장별 고급 스크랩 계약량, 청정수소 인도량, 계통 접속용량 및 공사일정으로 현재 추정 한도 교체.
3. 일본 대형 EAF와 H₂-DRI의 공정범위를 맞춘 low/base/high CAPEX bridge 승인. 현재 모델 SCRAP_EAF 원단위는 공시 full-scope 사례의 약 22–41%다.
4. 기술실패·공사지연·생산량·환율·정책지원·탄소가격까지 확장한 전위험 분해와 회사 재무경계 통일.
5. 인앱 브라우저의 `file://` 보안정책 때문에 이번 최종 회차의 강제 새로고침 픽셀 QA는 수행하지 못했다. 정적 HTML·JavaScript·내장데이터·회귀검사는 통과했고 기존 결과 탭은 보존했다.
