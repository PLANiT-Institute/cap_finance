# TCaR 정독 프로그램 — 접근 전 읽을 논문과 순서 (2026-09-01)

`docs/literature_map.md`가 "본문 미확인"으로 남긴 구멍을 메우는 목록. 전 서지는 웹 검색으로
교차 확인했고, 확인 실패 항목은 끝에 정직하게 남겼다. 우선순위 A = 접근 전 필독.

## A. 꼬리위험 방법론 원전

| 논문 | 왜 | 순위 |
|---|---|---|
| Rockafellar & Uryasev (2000), "Optimization of Conditional Value-at-Risk", *J. of Risk* 3: 21–41 | TCaR(P90−P50)의 정식 계보. "TCaR이 뭔가"라는 리뷰어 질문의 앵커 | **A** |
| Battiston, Mandel, Monasterolo, Schütze, Visentin (2017), "A climate stress-test of the financial system", *Nat. Clim. Chg.* 7: 283–288 | Monasterolo 계열 방법론 원전 — CAP의 시설 위험을 금융권 위험으로 확장할 때의 뿌리 | **A** |
| Dietz, Bowen, Dixon, Gradwell (2016), "'Climate value at risk' of global financial assets", *Nat. Clim. Chg.* 6: 676–679 | Climate VaR 원조 — Dietz 접근용 | 배경 |
| Sautner, van Lent, Vilkov, Zhang (2023), "Firm-Level Climate Change Exposure", *J. Finance* 78(3) | 기업 단위 기후위험 정량화의 재무학 선례 (NLP vs 우리 MILP+MC 대비) | B |

## B. 불확실성 하 철강 투자 (가장 가까운 방법론 사촌)

| 논문 | 왜 | 순위 |
|---|---|---|
| "Optimum investment strategy for hydrogen-based steelmaking project coupled with multiple uncertainties", *J. Env. Management* (2024), doi:10.1016/j.jenvman.2024.120484 | LSM 실물옵션 + 철강·수소·탄소 3축 확률화 — 확률화 대상 대비표의 반대편. 공저자 미확인, 원문 확보 필요 | **A** |
| Lee, Hwarang 외 (2023), "Decarbonization strategies for steel production with uncertainty in hydrogen direct reduction", *Energy* | 수소환원 투입가·기술계수 몬테카를로 — "수소가 최대 결정 인자"의 철강판 선례 | **A** |
| Bruno, Ahmed, Shapiro, Street (2016), "Risk neutral and risk averse approaches to multistage renewable investment planning under uncertainty", *EJOR* 250: 979–989 | CVaR 다단계 확률계획의 교과서적 인용처 | B |

## C. 철강 비용 원전·앵커

| 논문 | 왜 | 순위 |
|---|---|---|
| Vogl, Åhman, Nilsson (2018), "Assessment of hydrogen direct reduction for fossil-free steelmaking", *J. Cleaner Prod.* 203: 736–745 | CAP CAPEX 앵커 계보의 뿌리 (863천원/t = DIW = 이 계보) | **A** |
| IEA, *Iron and Steel Technology Roadmap* (2020) | validation_external §5의 미확보 LCOA 앵커 1차 후보 | **A** |

## D. 전환계획 평가 프레임 + 최근접 선행

| 논문 | 왜 | 순위 |
|---|---|---|
| **Wolf, A. (2025), "The uncertain costs of decarbonization policies: a risk analysis for the European steel industry", *Economia e Politica Industriale*, doi:10.1007/s40812-025-00343-6** | **최근접 선행 — 최우선 정독.** CCfD·그린리드마켓의 위험 배분("누가 위험을 떠안나"). CAP의 "누구 손익계산서에 꼬리위험이 남나"로 재서술 가능. CCfD 미평가(P2) 공백을 채울 때의 대화 상대 | **A(1순위)** |
| Nicolajsen, Bjørn, McAloone, Pigosso (2025), "Decoding corporate climate transition plans: A comparative analysis of 14 frameworks", *J. Env. Management* | "조화된 정의 부재" — 공시계획 gap 챕터의 이론적 배경 | **A** |
| "Do credible climate transition plans matter for carbon performance?", *Frontiers Env. Sci.* (2026, 저자 미확인) | 신뢰성 지수 × 실제 이행의 최신 실증 | B |
| TPI *State of the Corporate Transition 2025* (보고서) | Dietz 접근 시 여는 문서 | B |

## E. 이론적 위치 설정

| 논문 | 왜 | 순위 |
|---|---|---|
| van der Ploeg & Rezai (2020), "Stranded Assets in the Transition to a Carbon-Free Economy", *Ann. Rev. Resource Econ.* 12: 281–298 | TCaR = 좌초 위험의 미시 정량화라는 위치 설정. 거시 중심이라 우리 시설 단위가 메우는 공백 뚜렷 | **A** |
| Engle, Giglio, Kelly, Lee, Stroebel (2020), "Hedging Climate Change News", *RFS* 33(3): 1184–1216 | Engle 접근용 — "헤지할 대상을 기업 단위로 어떻게 계산하나"라는 상류 질문 | B |

## 읽기 순서

1. **좌표 확정**: Wolf 2025 → Kampmann 2026(보유) → Vogl 3부작(보유)
2. **방법 앵커**: Rockafellar & Uryasev 2000 → Battiston 2017 → Bruno 2016
3. **사촌 대비표**: JEnvMan 2024 → Lee 2023 — "확률화 대상: 정책 vs 투입가" 표 작성
4. **비용 앵커**: Vogl 2018 → IEA ISTR
5. **프레임**: Nicolajsen 2025 → Frontiers 2026 → TPI
6. **이론**: van der Ploeg & Rezai 2020

## 교수별 접근용 논문

- **Shrimali**: Wolf 2025를 딛고 — "APA의 배출 정합 판정과 Wolf의 위험 배분 사이에 CAP이 기업·시설 단위 TCaR로 다리를 놓는다"
- **Dietz**: Dietz et al. 2016 — "거시 Climate VaR을 기업·시설 단위로 미시화하면 무엇이 남는가" + TPI 공시 신뢰성 문제의식 연결
- **Monasterolo**: Battiston et al. 2017 — 하향식 스트레스테스트에 상향식 미시 기반을 제공하는 보완 관계
- **Engle**: Engle et al. 2020 — 헤지 팩터 구성의 상류에 있는 "헤지 대상 계산" 문제

## 미확인 — 인용 전 원문 확인 필수

- Material Economics / Agora Industry LCOA 보고서: 제목·연도 미특정 (validation_external §5 앵커 공백 지속)
- "Steel Decarbonization—from Optimization to Transformation" (*Ann. Rev. Env. Res.* 추정): 존재만 포착
- JEnvMan 2024·Lee 2023의 완전한 공저자 명단: 기관 접속으로 원문 확인 필요
- LSE Grantham CA100+ 효과성 워킹페이퍼: 동료심사 전, 저자 미확인
