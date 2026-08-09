# 한·일 철강 Capital Allocation Pathway — 실행 결과

POSCO, Nippon Steel, JFE Steel, Kobe Steel의 공식 기업 총량과 명시적 모델 추정치에 상관 가격경로 1,000개를 적용했다.

## 내부 1.5°C 스트레스에서 공시경로 고정 포트폴리오 재평가

| 기업 | 통합 실행가능성 | 미충족 제약 | 순현금 P50 | 탄소회피가치 | 경제적 Net P50 | TCaR | CAPEX | P90/EBITDA |
|---|---|---|---:|---:|---:|---:|---:|---:|
| POSCO | FAIL | 탄소예산(2030) | 48,474 | 15,183 | 116.7 | 32.4 | 22,752 | 10.05x |
| Nippon Steel | FAIL | 탄소예산(2035) | 40,216 | 17,046 | 69.5 | 19.1 | 23,974 | 3.01x |
| JFE Steel | FAIL | 자원·계통(2027) | 35,825 | 19,589 | 42.2 | 14.4 | 16,764 | 6.03x |
| Kobe Steel | FAIL | 탄소예산(2035)·자원·계통(2028) | 10,629 | 5,541 | 46.8 | 17.8 | 5,000 | 2.71x |

단위: 순현금·탄소회피가치·CAPEX는 십억원 NPV, Net P50·TCaR은 천원/tCO₂. 탄소회피가치는 인식된 회피비용이며 현금수익이 아니다.

## 생성 후보와 강건성 진단

시설 기술조합·전환연도·계약 프로필 910개를 두 활성 시나리오에서 결정론적으로 선별하고, 회사별 대표 217개를 seed당 100경로로 재평가했다.

| 기업 | 확률평가 후보 | 모든 활성 시나리오 적격 | 강건 경계 | λ=1 후보 | 최대후회 P50 | 최악 TCaR |
|---|---:|---:|---:|---|---:|---:|
| POSCO | 64 | 14 | 2 | CAND-6339E6B83A8408 | 54.5 | 12.0 |
| Nippon Steel | 64 | 23 | 1 | CAND-7400D0EA735D98 | 59.2 | 16.3 |
| JFE Steel | 64 | 3 | 1 | CAND-E8FAD9BDD034A5 | 28.2 | 22.9 |
| Kobe Steel | 25 | 6 | 1 | CAND-4D158AE8BC3521 | 91.7 | 31.4 |

최대후회는 각 시나리오에서 가장 낮은 적격 후보 P50 대비 비용 차이의 최댓값이다. λ=1 후보는 최대후회 + 최악 TCaR을 최소화한 강건 적격안이다. 공식 GCAM 경로가 아직 비활성이므로 현재 강건성은 공시경로와 내부 스트레스 사이의 예비 진단이다.

## 상위 강건후보 고정밀 재평가

결정론 기준으로 고정한 상위 후보 37개를 후보당·시나리오당 1,000경로로 다시 평가하고 전력·수소입력·건설 CAPEX의 정확한 3요인 Shapley 분산배분을 재계산했다.

| 기업 | 정밀 후보 | λ=1 후보 | 최대후회 P50 | 최악 TCaR | 최악경로 전력 | 수소입력 | 건설비 |
|---|---:|---|---:|---:|---:|---:|---:|
| POSCO | 10 | CAND-6339E6B83A8408 | 54.2 | 14.7 | 88.0% | 3.7% | 8.3% |
| Nippon Steel | 10 | CAND-7400D0EA735D98 | 58.9 | 18.7 | 92.4% | 2.3% | 5.3% |
| JFE Steel | 7 | CAND-E8FAD9BDD034A5 | 27.1 | 27.4 | 93.7% | 2.9% | 3.3% |
| Kobe Steel | 10 | CAND-4D158AE8BC3521 | 93.2 | 27.9 | 93.6% | 3.6% | 2.9% |

요인비중은 총비용 구성비가 아니라 최악 TCaR 시나리오의 분산을 모든 8개 요인부분집합으로 재평가해 배분한 Shapley 비중이다. 같은 seed의 공통난수를 사용하며 상관·비선형 상호작용 때문에 개별 기여가 음수일 수도 있지만 합계는 전체 분산과 일치한다. 수소 제조의 전력가격 노출은 전력 요인에 포함되고, `수소입력`은 비전력 전해조 비용성분만 흔든다.

### λ=1 정밀 추천의 시설·배출·공급여력

아래 시설·배출·자원값은 각 기업 λ=1 추천의 **최악 TCaR 시나리오**를 선택한 뒤, 해당 시나리오 안에서 계산한다. 자원 활용률은 그 경로의 2026–2040 최댓값이며 두 활성 시나리오 전체의 보수적 최댓값은 아니다.

| 기업 | 기준배출 | 2040 잔여배출 | 연간 감축 | 정렬 CAPEX | 스크랩 최대활용 | 수소 최대활용 | 증분계통 최대활용 |
|---|---:|---:|---:|---:|---:|---:|---:|
| POSCO | 69.8 | 10.4 | 59.5 | 27,588 | 71.2% | 35.8% | 68.8% |
| Nippon Steel | 72.6 | 12.2 | 60.4 | 29,348 | 78.2% | 24.3% | 65.9% |
| JFE Steel | 45.3 | 6.0 | 39.3 | 20,429 | 69.9% | 39.0% | 71.1% |
| Kobe Steel | 14.3 | 1.9 | 12.4 | 5,037 | 58.4% | 46.4% | 63.9% |

단위: 배출·감축은 MtCO₂/년, CAPEX는 십억원. 표의 자원 최대활용은 각 기업 최악 TCaR 시나리오 내 전 기간 최댓값이다. 공급한도와 활용률은 아직 `model_estimate`이므로 계약·계통 승인 전 screening 지표다.

정밀 후보집합은 seed가 아니라 중앙가격 screening으로 고정해 반복 간 후보 변경을 막았다. 최대후회 기준점은 이 shortlist 안의 시나리오별 최저 적격안이며, 전체 910개 후보를 모두 1,000경로로 평가한 결과는 아니다.

## 공식 국가 자원 벤치마크

아래 값은 회사 공급한도를 대체하지 않는다. 국가 전체·서로 다른 단위의 정책 및 인프라 맥락을 별도 감사층으로 보존한 것이다.

| 국가 | 자원 | 연도 | 공식 값 | 범위 | 출처 |
|---|---|---:|---:|---|---|
| KR | hydrogen | 2030 | 1.00 MtH2/year | Domestic clean-hydrogen supply policy target | [Presidential Commission on Carbon Neutrality and Green Growth](https://www.pcccr.go.kr/base/board/read?boardManagementNo=10&boardNo=124&menuLevel=2&menuNo=18&page=2) |
| KR | grid | 2038 | 129.30 GW | National target electricity demand | [MOTIR](https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/170183/view) |
| KR | grid | 2038 | 10.30 GW | Additional national generation capacity requirement | [MOTIR](https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/170183/view) |
| KR | scrap | 2023 | 정성 정책 | Policy to recognize steel scrap as a circular resource and improve grade-region-flow statistics | [2050 Carbon Neutrality and Green Growth Commission](https://www.2050cnc.go.kr/storage/board/base/2023/02/17/BOARD_ATTACH_1676595021015.pdf) |
| JP | hydrogen | 2030 | 3.00 MtH2-eq/year | Hydrogen and ammonia supply target in hydrogen-equivalent terms | [METI](https://www.meti.go.jp/policy/energy_environment/global_warming/transition/jcr_climate_transition_bond_framework_spo_eng.pdf) |
| JP | hydrogen | 2040 | 12.00 MtH2-eq/year | Hydrogen and ammonia supply target in hydrogen-equivalent terms | [METI](https://www.meti.go.jp/policy/energy_environment/global_warming/transition/jcr_climate_transition_bond_framework_spo_eng.pdf) |
| JP | hydrogen | 2050 | 20.00 MtH2-eq/year | Hydrogen and ammonia supply target in hydrogen-equivalent terms | [METI](https://www.meti.go.jp/policy/energy_environment/global_warming/transition/jcr_climate_transition_bond_framework_spo_eng.pdf) |
| JP | grid | 2032 | 30,163.00 MVA | Ten-year cross-regional transmission development plans through FY2032 | [OCCTO](https://www.occto.or.jp/assets/en/information_disclosure/annual_report/files/2023_annualreport_240131.pdf) |
| JP | grid | 2032 | 1,200.00 MW | Ten-year cross-regional transmission development plans through FY2032 | [OCCTO](https://www.occto.or.jp/assets/en/information_disclosure/annual_report/files/2023_annualreport_240131.pdf) |
| JP | scrap | 2022 | 43.16 Mt/year | National steel-scrap generation total | [Ministry of the Environment Japan](https://www.env.go.jp/content/000315009.pdf) |
| JP | scrap | 2030 | 2.00 Mt/year | Additional domestic high-grade steel-scrap processing capacity target | [Ministry of the Environment Japan](https://www.env.go.jp/policy/hakusyo/r08/html/hj26010401.html) |

## 산출 파일

- `plan_metrics.csv`: 기업 수준 ①~⑤ 지표와 스트레스 비율
- `facility_schedule.csv`: 시설별 전환 기술·시점·CAPEX
- `frontier_membership.csv`: 시나리오별 경계 포함 여부
- `scenario_comparison.csv`: 동일 설비·기술·연도의 시나리오 간 signed ΔP50·ΔTCaR·ΔNPV·ΔCAPEX
- `candidate_portfolios.csv`: 생성된 전체 후보의 시설 액션·계약 프로필·공통분모
- `candidate_screening.csv`: 전체 후보의 시나리오별 탄소·자원·공사·실패 제약 진단
- `candidate_scenario_metrics.csv`: 대표 후보의 P50·P90·TCaR·현금·탄소가치·정책지원
- `candidate_robust_summary.csv`: 최대후회·최악 TCaR·강건 경계·λ 최적점
- `candidate_scenario_comparison.csv`: 동일 생성 후보의 signed 시나리오 변화
- `refined_candidate_scenario_metrics.csv`: 고정된 상위 후보의 전체 경로·요인분해 재평가
- `refined_candidate_robust_summary.csv`: 정밀 shortlist의 최대후회·강건경계·λ 최적점
- `refined_candidate_facility_schedule.csv`: 정밀 후보별 시설 기술·전환연도·비용·감축
- `refined_candidate_resource_profile.csv`: 연도별 스크랩·수소·증분계통 수요·공급·여유
- `resource_benchmarks.csv`: 공식 국가 자원·계통 맥락(회사 공급한도와 비비교)
- `gcam_manifest_validation.json`: GCAM release·target XML·query 매니페스트 무결성과 활성화 게이트
- `run_summary.json`: gap, λ별 최적 계획, 실행 메타데이터
- `frontier_*.svg`: 기업 고유 효율 경계

## 해석 제한

기업 생산·배출·재무 총량은 공식 원문을 사용했다. 설비 포트폴리오는 기업 공시경로에서 한 번 고정한 뒤 다른 시나리오에 그대로 재평가한다. 탄소예산 또는 스크랩·수소·전력망·동시공사·실패위험 제약을 충족하지 못한 계획은 비용을 보존하되 효율경계와 추천에서 제외한다. 생성 후보는 기업 공시안이 아니라 모델 조합이며, 설비별 배분, 재투자연도, 공통 기술비용, 환율, 계약비율, 정책지원, 내부 1.5°C 스트레스와 현실 제약 한도는 검증 전 모델 추정치다. GCAM 1.5°C/2.0°C는 공식 9.1 실행·추출·hash 검증이 끝나기 전까지 활성 시나리오가 아니다.
