# 한·일 철강 Capital Allocation Pathway — 실행 결과

POSCO, Nippon Steel, JFE Steel, Kobe Steel의 공식 기업 총량과 명시적 모델 추정치에 상관 가격경로 250개를 적용했다.

## 내부 1.5°C 스트레스에서 공시경로 고정 포트폴리오 재평가

| 기업 | 경로 적합 | 순현금 P50 | 탄소회피가치 | 경제적 Net P50 | TCaR | CAPEX | P90/EBITDA |
|---|---|---:|---:|---:|---:|---:|---:|
| POSCO | FAIL (2030) | 48,689 | 15,183 | 117.4 | 29.7 | 22,752 | 9.93x |
| Nippon Steel | FAIL (2035) | 40,200 | 17,046 | 69.4 | 18.9 | 23,974 | 3.00x |
| JFE Steel | FAIL (None) | 36,113 | 19,589 | 43.0 | 12.7 | 16,764 | 5.94x |
| Kobe Steel | FAIL (2035) | 10,696 | 5,541 | 47.4 | 16.1 | 5,000 | 2.67x |

단위: 순현금·탄소회피가치·CAPEX는 십억원 NPV, Net P50·TCaR은 천원/tCO₂. 탄소회피가치는 인식된 회피비용이며 현금수익이 아니다.

## 산출 파일

- `plan_metrics.csv`: 기업 수준 ①~⑤ 지표와 스트레스 비율
- `facility_schedule.csv`: 시설별 전환 기술·시점·CAPEX
- `frontier_membership.csv`: 시나리오별 경계 포함 여부
- `scenario_comparison.csv`: 동일 설비·기술·연도의 시나리오 간 signed ΔP50·ΔTCaR·ΔNPV·ΔCAPEX
- `run_summary.json`: gap, λ별 최적 계획, 실행 메타데이터
- `frontier_*.svg`: 기업 고유 효율 경계

## 해석 제한

기업 생산·배출·재무 총량은 공식 원문을 사용했다. 설비 포트폴리오는 기업 공시경로에서 한 번 최적화한 뒤 다른 시나리오에 그대로 재평가하며, 연도별 예산 미충족안은 비용을 보존하되 효율경계와 추천에서 제외한다. 설비별 배분, 재투자연도, 공통 기술비용, 환율, 계약비율, 정책지원과 내부 1.5°C 스트레스는 모델 추정치다.
