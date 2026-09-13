# L1 — 전환비용 분포 생성 파트: 문헌 지도

CAP 8루프 연구, L1(전환비용 분포 생성). 프레임: 기업 탈탄소 전환의 총비용을 하나의 불확실한 확률분포로 보고, "그 분포를 어떻게 만드는가"를 문헌으로 판다. 아래 모든 항목은 WebSearch/WebFetch로 실제 확인한 것만 실었고, 저자명·수치 등을 원문에서 직접 확인하지 못한 경우 해당 항목 또는 미확인 절에 명시했다.

---

## 전환비용의 확률적 모형화

기업·프로젝트 단위 전환비용(또는 감축비용)을 확정값이 아니라 분포로 다룬 연구는 대체로 그린수소·철강·해운 등 개별 자산급 기술경제성(techno-economic) 분석에서 몬테카를로를 얹는 형태로 등장한다. 무엇을 확률변수로 두는지가 연구마다 다르다.

- 브라질 이타주바와 독일 쾰른의 소규모 그린수소 투자를 대상으로, 수전해 CAPEX·전력가격·이용률·할인율 등 다수 가정을 상관 몬테카를로(5,000회)로 결합해 균등화수소비용(LCOH)의 분포를 만들고, 그 분포의 95% 신뢰수준에서 VaR-LCOH(이타주바 8.39달러, 쾰른 8.21달러)를 산출했다. 가정들 간 상관관계를 넣고 빼는지에 따라 LCOH 분포 자체가 달라진다는 점을 명시적으로 보였다. [Bessa de Andrade, da Costa, Bonatto, Áquila, Pamplona, Bhandari (2023), "Perspective under uncertainty and risk in green hydrogen investments: A stochastic approach using Monte Carlo simulation", International Journal of Hydrogen Energy | https://www.sciencedirect.com/science/article/abs/pii/S0360319923044439] (저자 목록은 WebSearch 스니펫 기반이며 원문 초록을 직접 열람하지 못했다 — 미확인 절 참조)

- 한국 철강산업 에너지시스템모형에 수소환원제철(H2-DRI) 전환을 넣고, 수소환원 설비의 투자비를 내부 불확실성으로, 수소가격과 수소의 배출계수를 외부 불확실성으로 두어 몬테카를로를 돌렸다. 결과는 수소가격의 불확실성이 수소 이용량·배출량·감축비용 세 지표 모두에서 가장 지배적인 변동 요인이며, 배출목표 이탈 확률도 수소가격이 불확실할 때 가장 크다는 것. [저자 미확인 (2023), "Decarbonization strategies for steel production with uncertainty in hydrogen direct reduction", Energy | https://www.sciencedirect.com/science/article/abs/pii/S0360544223024519]

- 해운 부문에 수소 기반 합성연료(e-fuel) 도입 시 톤당 탄소회피비용(carbon abatement cost)을 일반 프레임워크로 정식화하고, 예측 불확실성 문제에 대응하기 위해 몬테카를로로 확률분포를 도출했다. 중앙값 기준 CO2 회피비용은 톤당 661달러이며, 녹색금융 조달금리 혜택을 반영하면 중앙값이 553달러로 낮아진다 — 즉 할인율·금리 가정이 분포의 중심 자체를 이동시킨다. [저자 미확인 (2021), "Carbon abatement cost of hydrogen based synthetic fuels – A general framework exemplarily applied to the maritime sector", International Journal of Hydrogen Energy | https://www.sciencedirect.com/science/article/abs/pii/S0360319921044219]

- 유럽 철강산업의 탈탄소 정책비용을 위험(risk) 문제로 재정식화하여, 탄소차액계약(Carbon Contracts for Difference)과 쿼터 기반 그린리드마켓 두 정책수단이 비용 불확실성을 투자자·구매자·납세자 사이에서 어떻게 재분배하는지를 분석했다. 두 수단 모두 "그린 철강 투자자로부터 구매자 또는 납세자로의 위험 이전"을 전제로 하며, 두 수단을 결합하면 위험 분배가 더 균형적이라는 결론. 전환비용을 확률변수가 아니라 "누가 그 분포의 꼬리를 떠안는가"의 정책 설계 문제로 다룬다는 점에서, CAP의 "분포를 만든 다음 헤지 대상을 정한다"는 문제의식과 직접 맞닿는다. [Wolf, A. (2025), "The uncertain costs of decarbonization policies: a risk analysis for the European steel industry", Journal of Industrial and Business Economics (Economia e Politica Industriale), 52(4), 913–934 | https://link.springer.com/article/10.1007/s40812-025-00343-6]

**CAP 논문 포지셔닝**: 위 문헌은 모두 특정 기술(수전해, H2-DRI, 합성연료) 단일 설비의 LCOH/LCOA 분포에 머문다. CAP처럼 시설 단위 MILP로 짠 다년도 전환 "일정" 전체의 총비용을 1만 개 가격경로 몬테카를로로 분포화한 연구는 검색 범위 내에서 확인되지 않았다 — 개별 기술의 원가 불확실성과 "언제·무엇을 설치하는가"라는 일정 결정 자체의 불확실성을 결합한 연구가 비어 있다.

---

## 분포 생성 방법·함정

- 상품가격을 GBM(기하 브라운 운동)이 아니라 평균회귀 과정(로그가격이 장기평균으로 회귀하는 1-요인 모형, 나아가 편의수익률·이자율까지 포함하는 2·3요인 모형)으로 모형화해야 한다는 표준 준거. 실물옵션 문헌에서 GBM이 가장 널리 쓰이지만 "일반적으로 부적절"하며 평균회귀 과정이 균형 조건에서 더 타당하다는 점이 지적되어 왔다 — 24년 같은 장기 호라이즌에서 GBM을 그대로 복리화하면 분산이 시간에 비례해 무한정 벌어져 꼬리가 비현실적으로 과장되는 반면, 평균회귀는 장기 분산을 유한한 수준으로 묶는다. [Schwartz, E.S. (1997), "The Stochastic Behavior of Commodity Prices: Implications for Valuation and Hedging", The Journal of Finance, 52(3), 923–973 | https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1997.tb02721.x]

- 대규모 프로젝트 비용추정에서 계획자가 과거 유사 프로젝트의 실제 비용분포("바깥 관점")를 무시하고 각 비용 항목을 개별적으로 지나치게 낙관적으로 추정하는 경향(optimism bias)을 실증했다. 준거집단 기반 예측(reference class forecasting)은 유사 프로젝트들의 실제 비용실현 분포를 가져와 그 분포에서 원하는 신뢰수준의 값(예: 80% 확률로 초과하지 않는 비용)을 보정값으로 쓴다 — 이는 CAP가 몬테카를로로 분포를 만들 때 "평균을 정규화 기준으로 쓸 것인가, 아니면 과거 실현치 분포의 특정 분위수를 쓸 것인가"라는 함정과 정확히 같은 문제를 실측 데이터로 보여준다. 도로·철도·픽스드링크 프로젝트에서 20% 초과위험 기준 비용 상향폭이 각각 32%, 57%, 55%로 나타난다. [Flyvbjerg, B., "Curbing Optimism Bias and Strategic Misrepresentation in Planning: Reference Class Forecasting in Practice", 관련 진술 다수 논문에서 반복 인용 | https://www.researchgate.net/publication/233258056_Curbing_Optimism_Bias_and_Strategic_Misrepresentation_in_Planning_Reference_Class_Forecasting_in_Practice] (정확한 발표연도·저널은 원문 미열람으로 미확인 — 통상 Flyvbjerg 2006/2008 인용되는 계열 논문임)

- 여러 비용 상승률(컴퓨터·센서·통신·전력 등 개별 원가 항목의 에스컬레이션율)을 서로 독립으로 두고 각각 몬테카를로 샘플링하면, 실제로는 이들이 상관되어 있기 때문에 최종 프로젝트 비용의 분산을 과소추정하게 된다는 실무 지적. 상관관계를 넣지 않은 몬테카를로는 분포를 인위적으로 좁혀서, 정규분포 근사에 가깝게 왜곡한다. [PMI(Project Management Institute), "Monte Carlo simulation in cost estimating", 실무 가이드(동료심사 학술논문 아님) | https://www.pmi.org/learning/library/monte-carlo-simulation-cost-estimating-6195]

- 시나리오 기반 MILP에 몬테카를로 표본을 결합해, 불확실한 투자비·감축효과의 여러 실현치(시나리오)마다 시나리오별 최적 투자계획을 구하고 이를 평균 할인비용 최소화 기준으로 통합하는 프레임 — CAP의 "MILP로 일정을 짜고 몬테카를로로 총비용 분포를 만든다"는 파이프라인과 구조적으로 같은 결합 방식이 산업 스케줄링 문헌에 존재함을 확인. [저자·구체 서지 미확인 — WebSearch 스니펫에서만 확인, 산업 에너지 스케줄링 계열 논문 | 검색 질의: "correlated Monte Carlo price path simulation MILP investment scheduling cost distribution industrial decarbonization"]

**CAP 논문 포지셔닝**: 24년 호라이즌에 GBM을 그대로 복리화하는 것이 위험하다는 것은 Schwartz(1997) 계열의 표준 지적이며, CAP가 평균회귀 과정을 채택(했다면/해야 한다면) 그 근거로 직접 인용 가능하다. Flyvbjerg의 실증은 "평균 정규화 대 분위수 기준" 논쟁에 실측 근거를 제공하지만, 에너지·산업 전환비용에 특화된 준거집단 데이터는 없다 — 이 지점이 CAP의 몬테카를로가 채워야 할 자리다.

---

## MACC 불확실성

- MACC(한계감축비용곡선)에 대한 표준 비판 논문. MACC는 불확실성을 제한적으로만 다루고, 시점 간 동학(intertemporal dynamics)을 배제하며, 가정의 투명성이 부족하다고 지적. 특히 매킨지식 MACC는 "기술 내 프로젝트별 비용의 변동폭이 경쟁 기술 간 평균비용의 변동폭보다 훨씬 클 수 있음에도 기술별 평균비용만 요약한다"는 점, 단일 연도의 배출량만 제시하고 그 배출량이 그 이전의 감축행동에 의존한다는 점을 지적한다. [Kesicki, F. & Ekins, P. (2012), "Marginal abatement cost curves: a call for caution", Climate Policy, 12(2), 219–236 | https://www.tandfonline.com/doi/abs/10.1080/14693062.2011.582347]

- MACC를 병렬적으로 시행 가능한 조치들의 상호작용, 그리고 비용추정의 불확실성 데이터까지 반영해 재구성하는 방법론을 제시하고, 이를 영국 철강 소재효율화(구조용 빔 재사용, 빔 스펙 최적화, 소형차 선택, 차체 고강도강 사용) MACC에 적용했다. 이 네 조치로 영국 철강 수요 및 관련 글로벌 배출량을 약 12% 줄일 수 있고, 사용단계 배출저감까지 포함하면 2030년 정부 탄소가격 기준으로 잠재량의 약 60%가 경제적으로 타당해진다. 불확실성을 넣은 MACC는 조치 간 비용 순위가 점추정 MACC보다 훨씬 자주 뒤바뀔 수 있음을 보여준다는 점에서 CAP과 직접 관련. [Dunant, C.F., Skelton, A.C.H., Drewniok, M.P., Cullen, J.M., Allwood, J.M. (2019), "A marginal abatement cost curve for material efficiency accounting for uncertainty", Resources, Conservation and Recycling | https://www.sciencedirect.com/science/article/abs/pii/S0921344919300229]

- 배출기술 간 한계감축비용을 점추정이 아니라 분위수회귀(quantile regression)로 추정해, 중앙값 기준 순위와 상·하위 분위수 기준 순위가 달라질 수 있음을 계량적으로 보인다 — "평균적으로 싼 기술"과 "꼬리에서 싼 기술"이 다를 수 있다는 것을 통계적으로 정식화한 최근 연구. [Delnava, H. & Dai, S. (2025), "Quantile estimation of CO2 marginal abatement cost across emission-generating technologies", arXiv:2508.11912 | https://arxiv.org/pdf/2508.11912]

- 도시 단위 MACC에 반등효과(rebound effect)라는 행태적 불확실성을 결합하기 위해 몬테카를로(모수적 불확실성)와 베이지안 네트워크(조건부 추론)를 결합한 확률적 MACC 프레임워크. 전통적 MACC는 행태적 되먹임(반등효과)을 무시해 감축잠재량을 과대추정하는 경향이 있다고 지적. [Rodriguez-Sanchez, A.E., Tello-Leal, E., Macías-Hernández, B.A., Hernandez-Resendiz, J.D. (2026), "Data-Driven Probabilistic MACCs for Smart Cities: Monte Carlo Simulation and Bayesian Inference of Rebound Effects", Data, 11(4), 87 | https://www.mdpi.com/2306-5729/11/4/87] (저자명은 WebSearch 스니펫 기반, MDPI 원문은 403으로 직접 열람 실패 — 미확인 절 참조)

**CAP 논문 포지셔닝(MACC 대비)**: MACC는 "특정 연도에 특정 조치를 실행했을 때의 한계비용"이라는 정태적·개별 조치 단위 개념이다. 반면 CAP의 전환비용 분포는 (i) 다년도 시설 일정 전체의 총 NPV, (ii) 가격경로라는 확률과정에서 나오는 것으로, MACC가 다루는 "조치 간 순위 불확실성"이 아니라 "이미 고정된 일정(순위가 정해진 이후)의 총비용이 얼마나 벌어지는가"를 다룬다는 점에서 대상 자체가 다르다. Kesicki & Ekins(2012)와 Dunant et al.(2019)이 지적한 "MACC는 시점 간 동학과 불확실성을 제대로 못 담는다"는 비판이 CAP의 존재 근거(=MILP+몬테카를로로 시점 간 동학과 가격 불확실성을 동시에 담는다) 그 자체다.

---

## 분포 폭을 지배하는 요인

- 한국 철강 H2-DRI 전환 몬테카를로에서, 투자비(내부 불확실성)보다 수소가격(외부 불확실성)이 수소 이용량·배출량·감축비용 세 지표 모두에서 지배적 변동 요인으로 확인됨 — "투입 에너지가격이 CAPEX보다 분포 폭을 지배한다"는 CAP의 9루프 결과와 같은 방향. [저자 미확인 (2023), "Decarbonization strategies for steel production with uncertainty in hydrogen direct reduction", Energy | https://www.sciencedirect.com/science/article/abs/pii/S0360544223024519]

- 그린수소 LCOH 몬테카를로에서, 가정들(전력가격·CAPEX·이용률 등) 간 상관관계를 넣고 빼는지가 LCOH 분포 자체를 유의하게 바꾼다 — 즉 분포 폭을 지배하는 것은 개별 변수의 분산만이 아니라 변수 간 상관구조라는 점을 명시. [Bessa de Andrade et al. (2023), International Journal of Hydrogen Energy | https://www.sciencedirect.com/science/article/abs/pii/S0360319923044439]

- 탄소포집·활용·저장(CCUS) 전체 공정 몬테카를로 민감도분석(Sobol 전역민감도)에서 전력가격의 전역(total-order) 민감도지수가 0.658로 가장 크고, 배가스 유입유량·배관 직경·배관 재질단가·주입압력 등이 뒤를 잇는다 — 에너지가격이 다른 공정변수보다 총비용 분산에 훨씬 크게 기여한다는 것을 Sobol 분해로 정량화한 사례. [저자 미확인(2025), "Monte Carlo Sensitivity Analysis for a Carbon Capture, Utilization, and Storage Whole-Process System", Processes, 13(5), 1356 | https://doi.org/10.3390/pr13051356]

- 전역 분산분해(Sobol 등) 방법 자체가 모수가 많은 고차원 모형에는 모형 평가 횟수가 기하급수적으로 늘어 적용이 어렵다는 방법론적 한계도 함께 지적됨 — CAP가 가격경로·CAPEX·이용률·탄소가 등 다수 확률변수를 동시에 다룰 때 분산분해를 그대로 적용하기 어려울 수 있다는 시사점. [WebSearch 스니펫 기반, 구체 서지 미확인 — 질의: "variance decomposition sensitivity analysis high-dimensional model evaluations"]

**CAP 논문 포지셔닝**: 위 두 개별사례(한국 철강 H2-DRI, CCUS 공정)는 모두 "에너지가격이 분포 폭을 지배한다"는 CAP의 9루프 결론과 같은 방향의 개별 증거이지만, 둘 다 단일 설비·단일 연도 스냅샷이다. CAP처럼 시설 단위 다년도 MILP 일정 전체에 대해 에너지가격·탄소가·CAPEX·이용률 네 변수의 상대적 기여도를 전역 분산분해로 공식 정량화한 선행연구는 확인되지 않았다 — 이 지점이 5번 항목(분포=헤지의 출발점)과 맞물려 CAP이 채울 수 있는 자리다.

---

## 분포가 헤지의 출발점인 이유

- CVaR(조건부 VaR, 기대손실)을 리스크 측도로 정식화하고 그 최적화 방법을 제시한 정초 논문. CVaR은 손실분포의 꼬리(하위 신뢰수준을 넘는 손실의 조건부 기댓값)를 정의하며, VaR과 달리 서브가법성을 만족하는 정합적(coherent) 리스크 측도임을 증명 — "분포가 있어야 꼬리를 정의할 수 있고, 꼬리를 정의해야 헤지 대상(=꼬리 위험)을 특정할 수 있다"는 CAP의 논리적 순서가 기대는 표준 정의 그 자체. [Rockafellar, R.T. & Uryasev, S. (2000), "Optimization of Conditional Value-at-Risk", Journal of Risk, 3, 21–41 | https://www.researchgate.net/publication/263048322_Optimization_of_Conditional_Value-At-Risk]

- 그린수소 투자의 LCOH 몬테카를로 분포에서 95% 신뢰수준의 VaR-LCOH를 직접 산출한 선례 — "먼저 몬테카를로로 비용분포를 만들고, 그 분포에서 VaR을 뽑아낸다"는 CAP의 파이프라인과 동일한 2단계 구조를 전환/에너지 프로젝트 비용에 적용한 사례. [Bessa de Andrade et al. (2023), International Journal of Hydrogen Energy | https://www.sciencedirect.com/science/article/abs/pii/S0360319923044439]

- 유럽 배출권거래제 옵션 가격에서 도출한 "Carbon VIX"(탄소가격 불확실성의 시장 내재 변동성 지수)를 이용해, 탄소가격 불확실성 증가가 기업의 탈탄소 투자를 지연시키는 효과가 탄소가격 하락 효과와 비슷한 크기로 크다는 것을 보인다. 즉 (기댓값이 아니라) 분포의 폭 자체가 투자 의사결정에 독립적인 인과효과를 가지며, 이는 "왜 분포를 만드는 것이 먼저인가"에 대한 실물옵션 이론적 근거를 제공한다 — 불확실성이 크면 기업은 옵션가치를 지키기 위해 투자를 늦춘다. [Fuchs, M., Stroebel, J., Terstegge, J. (2024), "Carbon VIX: Carbon Price Uncertainty and Decarbonization Investments", NBER Working Paper No. 32937 | https://www.nber.org/papers/w32937]

- 기후 전환위험을 자산가치·현금흐름에 대한 몬테카를로 시나리오 충격으로 변환해 CVaR(Climate VaR)로 산출하는 실무 프레임워크가 1만 개 이상 기업·국채에 적용되고 있음 — 학술 논문은 아니지만, "전환비용 분포 → CVaR"라는 파이프라인이 이미 기관투자자 실무에서 표준화되어 있다는 정황 증거. [MSCI, "Understanding the Drivers of Transition-Risk Climate VaR" (실무 자료, 동료심사 아님) | https://www.msci.com/research-and-insights/blog-post/understanding-the-drivers-of-transition-risk-climate-var]

**CAP 논문 포지셔닝**: Rockafellar & Uryasev(2000)이 CVaR을 일반적인 손실분포에 대해 정의한 정초라면, Bessa de Andrade et al.(2023)은 그 정의를 에너지 프로젝트 비용분포에 처음 적용한 선례이고, Fuchs et al.(2024)은 "분포의 폭(불확실성) 자체가 투자를 지연시킨다"는 인과적 근거를 제공한다. 그러나 세 문헌 모두 (i) 단일 설비/기업의 정태적 비용 또는 (ii) 시장 내재 변동성 지수에 머물고, CAP처럼 시설 단위 MILP 일정의 다년도 NPV 분포에 CVaR/ES를 직접 적용해 "이 전환일정의 어느 부분이 꼬리위험을 만드는가"까지 역추적한 연구는 확인되지 않았다.

---

## 미확인

아래는 이번 검색에서 존재는 확인했으나 서지 정보(저자명·정확한 발표연도/저널) 또는 원문 내용을 완전히 확인하지 못한 항목이다. 인용 전 원문 직접 확인 필요.

1. "Decarbonization strategies for steel production with uncertainty in hydrogen direct reduction" (Energy, 2023, ScienceDirect S0360544223024519) — 저자명 미확인. 한국 철강산업 대상이라 CAP과 관련성이 높아 원문 확보 우선순위 높음.
2. "Carbon abatement cost of hydrogen based synthetic fuels – A general framework exemplarily applied to the maritime sector" (International Journal of Hydrogen Energy, 2021, ScienceDirect S0360319921044219) — 저자명 미확인.
3. Bessa de Andrade, da Costa, Bonatto, Áquila, Pamplona, Bhandari (2023) 그린수소 IJHE 논문 — 저자 목록은 WebSearch 스니펫에서만 확인, ScienceDirect·ResearchGate 원문 모두 403으로 직접 열람 실패. 저자 순서·소속 재확인 필요.
4. Rodriguez-Sanchez, Tello-Leal, Macías-Hernández, Hernandez-Resendiz (2026), "Data-Driven Probabilistic MACCs for Smart Cities" (Data, 11(4), 87) — 저자명은 WebSearch 스니펫 기반, MDPI 원문 403으로 직접 열람 실패.
5. Flyvbjerg의 준거집단예측(reference class forecasting) 논문 — 정확한 발표연도·저널(통상 2006 Project Management Journal 또는 2008 계열로 알려짐)을 원문에서 직접 확인하지 못함. 인용 시 정확한 서지 재확인 필요.
6. "correlated Monte Carlo price path simulation" + "MILP investment scheduling"을 결합한 산업 스케줄링 논문 — 존재는 WebSearch 스니펫으로 확인되나 저자·정확한 논문 제목·저널을 특정하지 못함.
7. 전역 분산분해(Sobol 등)가 고차원 모형에서 계산비용 때문에 적용이 어렵다는 진술의 출처 논문 — 구체 서지 미확인.
8. "Monte Carlo Sensitivity Analysis for a Carbon Capture, Utilization, and Storage Whole-Process System" (Processes, 13(5), 1356) — 저자명 미확인.
9. PMI(Project Management Institute)의 몬테카를로 비용추정 가이드, MSCI Climate VaR 자료 — 둘 다 동료심사 학술논문이 아닌 실무자료이므로, 논문 본문에는 "실무 프레임워크"로만 인용하고 학술 선례로는 사용하지 않을 것.

---

# SYNTHESIS L1 (전환비용 분포) — 2026-09-13

## 대상 = 하나의 전환비용 분포
이번 8루프의 대상은 위험 종류가 아니라 **전환 총비용 C(x)의 확률분포** 하나다. L1이 셋을 확정:
1. **생성 — CAP의 자리.** 기존 문헌은 전부 단일 설비 LCOH/LCOA 분포(그린수소·H2-DRI·해운). MILP
   다년도 일정 전체를 1만 가격경로로 분포화하고 "일정의 어느 구간이 꼬리를 만드나"까지 역추적한
   선례 없음. MACC 비판(Kesicki-Ekins 2012: 정태·개별조치·순위 뒤집힘)이 CAP 존재 근거.
2. **모양 — 팻테일·두 꼬리·비대칭.** 전환 설비(H2-DRI·전해조·CCUS)는 팻테일 참조집단(원자력 +120%·
   수력 +75%), 신테일(태양광 +1%) 아님(Flyvbjerg). FOAK 비대칭 3중(Merrow 낙관편향 + NOAK 대비
   150% 컨틴전시 + 수소가 민감도). **두 꼬리가 다른 확률변수에서 온다** — 상방(CAPEX·에너지=짓는 돈)/
   하방(탄소·정책=버는 돈, 좌초 $1조+).
3. **헤지의 출발점.** 분포가 있어야 꼬리 정의·헤지 대상 특정. CVaR(Rockafellar-Uryasev 2000)이 도구.

## 두 꼬리 = 두 헤지 (L1의 헤지 함의)
| 꼬리 | 원천(확률변수) | 헤지 수단 |
|---|---|---|
| 상방(비용 폭발) | CAPEX 초과·에너지가 | EPC 고정가/GMP 캡 |
| 하방(좌초) | 탄소가 붕괴·정책 신뢰 | CCfD 하한(정부만) |
하나의 대칭 분산으로 뭉치면 둘 다 잘못 다룬다. CCfD 양방향(하한 지급+상한 환수)=칼라가 둘을 한 계약에.
→ 이게 세 주체 헤지(L3~L5)의 씨앗: 상방은 기업(EPC)·투자자, 하방은 정부(CCfD).

## 지난 9루프와의 연결 (버리지 않음)
위험 세 종류(가격형·접근형·제도형)가 이 분포의 **어디에 사는지**를 설명한다:
- 가격형 → 분포의 **몸통/분산**(계약으로 좁힘)
- 접근형 → 분포 **전체를 밀어올림**(배급 실패 = 평균↑ + 상방 꼬리↑, 선점으로 막음)
- 제도형 → **하방 꼬리**(탄소 붕괴 = 좌초, 정부만 막음)
지난 작업이 이번 분포 프레임의 요인 지도가 된다.

## 분포 생성 함정 (L1 방법)
GBM 24년 복리는 분산 과대(Schwartz 1997 평균회귀 준거). 상관 빼면 분산 과소(PMI). 평균 정규화 vs
중앙값. 이 함정들은 DIRECTION의 T1(GBM vs OU)·A-24와 이미 연결 — 분포의 모양이 이것에 민감.

## L2로
분포의 모양(왜도·다봉성·꼬리 지수)을 더 정밀히, 그리고 두 꼬리의 상대 크기를 판다. 그 다음 L3~L5가
세 주체(기업·투자자·정부)가 분포의 어느 부분을 어떻게 헤지하는지.
