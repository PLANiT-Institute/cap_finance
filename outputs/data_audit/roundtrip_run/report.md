# 한·일 철강 Capital Allocation Pathway — 실행 결과

POSCO, Nippon Steel, JFE Steel, Kobe Steel의 공식 기업 총량과 명시적 모델 추정치에 상관 가격경로 100개를 적용했다.

## 가속 1.5°C 경로의 공시전략 프록시

| 기업 | 생산 Mt | Scope 1+2 Mt | Net P50 | TCaR | CAPEX | P90/EBITDA | 비용 gap |
|---|---:|---:|---:|---:|---:|---:|---:|
| POSCO | 34.54 | 69.85 | 59.3 | 16.5 | 27,588 | 9.82x | 63.8 |
| Nippon Steel | 34.30 | 72.60 | 50.0 | 13.4 | 29,124 | 3.27x | 40.0 |
| JFE Steel | 21.95 | 45.30 | 42.4 | 12.0 | 16,764 | 5.79x | 34.2 |
| Kobe Steel | 5.96 | 14.30 | 135.9 | 36.8 | 5,037 | 7.66x | 11.7 |

단위: P50·TCaR·gap은 천원/tCO₂, CAPEX는 십억원. 생산·배출 공식 총량은 HTML의 데이터 근거 표를 기준으로 본다.

## 산출 파일

- `plan_metrics.csv`: 기업 수준 ①~⑤ 지표와 스트레스 비율
- `facility_schedule.csv`: 시설별 전환 기술·시점·CAPEX
- `frontier_membership.csv`: 시나리오별 경계 포함 여부
- `run_summary.json`: gap, λ별 최적 계획, 실행 메타데이터
- `frontier_*.svg`: 기업 고유 효율 경계

## 해석 제한

기업 생산·배출·재무 총량은 공식 원문을 사용했다. 설비별 배분, 재투자연도, 공통 기술비용, 환율, 계약비율, 정책지원과 1.5°C 가속 경로는 모델 추정치다. 따라서 투자판단이 아니라 데이터 구조·상대 민감도 검증용으로 사용해야 한다.
