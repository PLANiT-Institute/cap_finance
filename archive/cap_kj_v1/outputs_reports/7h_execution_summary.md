# CAP-KJ 7시간 집중 실행 요약

**누적 실행:** Run 0–13, 총 14회  
**기준 시점:** 2026-08-05 07:23 KST  
**현재 판정:** 내부 분석용 MVP 완성 / 대외 공개는 조건부 보류  

## 1. 무엇을 만들었는가

14회 실행에서 공식·규제·회사 자료 18건을 등록하고, 25개 시설/지역의 물리·배출·경로 정보를 회사 수준으로 집계했다. 결과물은 9개 CSV 의사결정 표, 6개 투자자용 그림, 2개 감사 가능한 워크북과 재현 가능한 보고서 묶음이다.

핵심 분석 사슬은 `공식 회사 기준선 → 시설 배분/관측 → 전환 경로와 시점 → CAPEX 및 연간 resource-gap → B0/BH/BL/BHL 지원 조건 → 회사별 잔여 공통위험`으로 구현됐다. 관측값, 배분값, 추정값과 미확인 값은 서로 다른 라벨로 유지했다.

주요 산출물:

- 회사·시설 capital-allocation 경로: `outputs/tables/company_capital_allocation_mvp.csv`, `facility_capital_allocation_mvp.csv`
- 회사·시설 연간 resource-gap: `outputs/tables/company_annual_cost_gap_mvp.csv`, `facility_annual_cost_gap_mvp.csv`
- B0/BH/BL/BHL 위험·지원 실험: `outputs/tables/company_support_experiment_mvp.csv`, `facility_support_experiment_mvp.csv`
- 생산 커버리지와 물리 제약: `outputs/tables/company_production_coverage_status_mvp.csv`, `facility_physical_constraint_mvp.csv`
- 투자자 그림 6종: CAPEX 범위, 시점·의존성, 감축효율·커버리지, 집중도·불확실성, 연간 비용격차, risk-to-abatement
- 감사: `outputs/reports/qa_reproducibility_report.md`, `outputs/diagnostics/qa_checks.csv`

## 2. 회사별 capital-allocation pathway

금액은 실질 2025 USD screening proxy이며 회사 지침이나 확정 투자액이 아니다. CAPEX와 연간 resource-gap은 각각 low/base/high, 2030 비중은 기존 경로 시간표 기준이다. Mitsui 수치는 공식 SHK 배분을 적용한 현재 비용 경계이며 지원실험은 아직 85% 구경계를 사용한다.

| 회사 | 배출 커버리지 | 생산 커버리지 | 전환 CAPEX USD bn L/B/H | 연간 resource-gap USD bn L/B/H | 2030까지 CAPEX | 최대 비용격차 시설 | 지금의 자본배분 판단 |
|---|---:|---:|---:|---:|---:|---:|---|
| POSCO | 100.0% | NA | 9.509/18.153/31.120 | 0.685/3.416/9.317 | 31.4% | Pohang 76.4% | Pohang 수소·청정전력 계약 우선; 광양은 공개 프로젝트와 추가 증설을 분리 |
| Nippon Steel | 100.0% | 100% | 16.846/26.966/40.481 | 1.758/6.017/15.441 | 0.2% | Oita 24.8% | 분산형 2031–2040 포트폴리오; Oita 단일 집중보다 전사 프로그램 관리 |
| LOTTE Chemical | 92.7% | NA | 0.299/0.747/1.742 | 0.067/0.280/0.809 | 0.0% | Yeosu Basic 52.1% | 전력·기술비용 위험 커버와 수준 지원을 함께 검증 |
| Mitsui Chemicals | 97.5% | NA | 0.204/0.566/1.452 | 0.046/0.212/0.674 | 0.0% | Osaka 43.8% | 지원실험을 SHK 경계로 재실행하기 전 정확한 결합 수치 금지 |

## 3. 투자자와 기업에 유의미한 핵심 인사이트

1. **자본 규모보다 병목의 종류가 중요하다.** 현재 1차 경계의 철강 base 전환 CAPEX는 USD 45.120bn, 화학은 USD 1.312bn이다. 다만 이는 서로 다른 품질-D 경로 프록시이므로 업종 간 우열이나 기업가치 순위로 해석할 수 없다. 투자 판단은 금액이 아니라 계약, 전력, 수소, 원료, 설비 용량의 해결 순서에 둬야 한다.
2. **Nippon은 가장 큰 비용격차이지만 분산형 프로그램이다.** base 연간 resource-gap은 USD 6.017bn으로 가장 크고 Oita 기여는 24.8%다. 단일 프로젝트보다 2031–2040년 다수 제철소의 공통 수소·전력 계약 구조가 핵심이다.
3. **POSCO는 Pohang에 경제적 위험이 집중된다.** base 연간 resource-gap은 USD 3.416bn이며 Pohang이 76.4%를 차지한다. CAPEX 기준 집중도 68.6%보다 높아, 수소·청정전력 비용이 단순 설비비보다 더 강한 자본배분 게이트임을 보여준다.
4. **현재 규칙에서는 철강과 화학의 지원 경로가 다르다.** BH만으로 철강의 modelled operational abatement 109.804 MtCO2e/년이 조건부 활성화되지만, 화학은 BHL에서야 4.133 MtCO2e/년이 활성화된다. 이는 사전 정의된 상태전환 결과이지 정책의 인과효과나 system abatement가 아니다.
5. **광양은 확정 프로젝트와 전체 경로를 분리해야 한다.** 공개된 2.5 Mt/년 EAF는 현재 배분 활동량의 13.15%만 커버하고 전체 적용에는 7.61배 용량이 필요하다. 계획 scrap 수요 2.0 Mt/년은 2024년 구매 scrap의 97.5%다. 따라서 전체 광양 CAPEX·감축량은 확정 투자액이 아니라 추가 증설·원료·전력 조건이 붙은 잠재 경로다.
6. **화학 비용 프록시는 아직 회사 비교력을 갖지 못했다.** LOTTE와 Mitsui의 base 연간 resource-gap은 각각 USD 0.280bn, USD 0.212bn이지만 동일한 electrified-cracker 프록시가 동일한 단위 감축비용을 기계적으로 만든다. 실제 프로젝트별 설비·전력·원료 데이터로 교체하기 전 비교우위 결론은 금지한다.

## 4. 데이터 품질과 사용 가능 범위

| 계층 | 현재 상태 | 품질/라벨 | 허용되는 사용 | 금지되는 해석 |
|---|---|---|---|---|
| 회사 배출 기준선 | 4개사 공식 Scope 1+2 앵커 | 주로 Reported A/B | 규모와 시설 커버리지 분모 | 기간·연결범위가 다른 기업 순위 |
| 시설 배출 | LOTTE 보고값, Mitsui 규제자료 브리지, POSCO·Nippon 일부 배분 | Reported B / Allocated C–D | 시설 기여도와 경계 민감도 | 모두가 같은 품질의 관측값이라는 주장 |
| 생산 | Nippon 11개 거점 34.88 Mt 대 회사 34.30 Mt | Derived from Reported, B | 허용오차 내 100% 커버리지 | POSCO·LOTTE·Mitsui를 0%로 처리 |
| 기술·CAPEX·연간 비용 | 공식 벤치마크와 프로젝트 관측에 저·중·고 추정치 결합 | Estimated/Modelled, D | 자본 규모·시점·민감도 스크린 | 회사 지침, 확정 예산, 투자수익률 |
| 지원·계약 | 규칙 기반 B0/BH/BL/BHL 및 독립 support stress | Estimated, D | 어떤 조건 조합이 상태를 바꾸는지 진단 | 실제 보조금, 계약 현금흐름, 인과효과 |
| 물리 제약 | 광양 EAF 용량·투자·원료계획은 공식, 전체 공장 분모는 배분 | Reported A/B + Derived D | 공개 프로젝트 대비 전체 경로 스케일 경고 | 달성 이용률이나 확정 추가증설 |

## 5. 검증 상태와 공개 게이트

최종 자동 검증은 **22 PASS, 7 WARN, 0 FAIL**, Python 테스트는 **59/59 통과**다. 8개 핵심 표는 격리된 임시 디렉터리에서 byte-for-byte 재생성됐고, 시설 합계가 회사 CAPEX·배출·감축·연간 비용·지원 값에 일치했다.

대외 공개를 막는 핵심 조건:

- Mitsui 비용 경계 97.46%와 지원실험 경계 85.00%를 통일해야 한다. 현재 두 정확한 금액을 한 결론으로 결합할 수 없다.
- 생산 커버리지는 1/4개사만 공개 가능하며, Nippon의 새 100% 값도 main pathway/support 표에 아직 전파되지 않았다.
- 광양 전체 경로를 project-backed로 표시하려면 추가 EAF/HBI/scrap/전력 설비가 식별돼야 한다.
- verified incentive-adjusted gap은 전 회사 `NA`다. support stress를 실제 현금으로 표시할 수 없다.
- 누출·대체생산이 없어 operational abatement를 system abatement로 부를 수 없다.
- 분석 파일은 재현 가능하지만 13개 최상위 항목이 아직 버전 이력으로 보호되지 않는다.

## 6. 다음 우선순위

1. **경계 통일:** Mitsui SHK 브리지를 capital screen과 B0/BH/BL/BHL 실험 전체에 전파하고 기존 85% 결과는 sensitivity로 격리한다.
2. **물리 경로 현실화:** 광양 2.5 Mt 프로젝트 블록을 전체 공장 경로에서 분리하고, 나머지 용량의 EAF/HBI/scrap/전력 요구량과 투자 시점을 별도 행으로 만든다.
3. **생산 분모 확보:** POSCO·LOTTE·Mitsui의 회사/시설 생산량을 같은 제품·기간·운영경계로 확보하고 Nippon 생산 커버리지를 main outputs에 전파한다.
4. **현금성 비용격차:** 실제 전력·수소·원료 가격, ETS 의무·무상할당, 계약 프리미엄, 정책 적격성과 실현 지원을 시설별 ledger로 연결한다.
5. **system abatement:** 폐쇄·감산의 대체생산과 누출을 모델링한 뒤에만 시스템 감축량을 공개한다.
6. **릴리스 보호:** 재현 명령을 깨끗한 환경에서 다시 실행하고 승인된 범위로 버전 이력을 만든다.

## 7. 최종 해석

이번 7시간 실행은 ‘어느 회사가 더 녹색인가’를 답하지 않는다. 대신 어느 시설에 얼마의 잠재 자본이 걸려 있고, 비용격차가 어디에서 생기며, 어떤 계약·지원·물리 조건이 감축을 활성화하고, 그 뒤에도 어떤 공통위험이 남는지를 회사 수준에서 추적할 수 있는 MVP를 만들었다. 현재 결과는 내부 자본 우선순위와 데이터 보완 순서를 결정하는 데 유용하지만, 확정 투자·실현 보조금·system abatement·기업가치 판단에는 사용할 수 없다.
