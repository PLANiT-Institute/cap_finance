# L3: 최적 헤지 비율 — 기존 이론에 얹기

방향: 새 이론 없음. CAP은 "전환비용 분포"(L1-L2 산출)를 기존 헤지 최적화 문헌의 입력으로 넣는 자리를 찾는 것이지, 헤지 이론 자체를 만드는 게 아니다. 아래 모든 항목은 실제 검색·확인 결과이며, 확인 못 한 것은 "미확인"에 명시.

---

## 최적 헤지 비율 이론

정착된 결과: 완전 헤지(h=1)는 스팟-선물 상관계수가 1이고 베이시스 위험이 없을 때만 최소분산 헤지 비율과 일치한다. 그 외에는 h*<1이 최소분산 해다.

- **최소분산 헤지 비율의 원형**: h* = ρ·(σ_S/σ_F). ρ<1(불완전 상관, 베이시스 위험)이면 h*<1. 고전적 도출은 Johnson(1960)과 Ederington(1979)에서 시작.
  [Ederington, L. H. (1979), "The Hedging Performance of the New Futures Markets," Journal of Finance 34, 157–170]
  후속 리뷰: [Chen, Lee & Shrestha, "Futures hedge ratios: a review," Applied Economics / Springer Handbook chapter — https://link.springer.com/rwe/10.1007/978-1-4614-5360-4_74]

- **완전 헤지가 최적이 아닌 이유(이론적 근거, CAP이 얹을 자리)**:
  1) 베이시스 위험 — 헤지 수단과 노출 자산의 가격이 완전히 같이 움직이지 않음. 상관계수 <1이면 100% 헤지가 오히려 분산을 키울 수 있음.
     [Homework.Study.com 요약이 인용하는 표준 교과서 정의; 원 출처는 Hull, Options Futures and Other Derivatives — 교과서 자체는 미확인, 위키/서머리로만 확인]
  2) 헤지 비용(프리미엄) — 헤지가 무비용이면 완전 헤지가 항상 최적이라는 명제가 성립하지만, 실제로는 헤지에 비용이 들기 때문에 부분 헤지가 최적이 됨.
     [검색 요약 인용 — 원 논문 특정 못 함, "미확인"으로 표시]

- **에너지 헤지 문헌**: 전력·PPA 맥락에서 최적 헤지 비율(OHR)은 스팟 위치를 고정하고 선물/PPA 비중을 분산 최소화 또는 기대효용 극대화로 정함.
  [Deep Hedging of Green PPAs in Electricity Markets, Biegler-König & Oeltz (2025), arXiv:2503.13056 — 재생에너지 PPA는 날씨 위험이 거래 불가능(non-tradable)한 불완전시장이라 완전 헤지가 원천적으로 불가능하다는 점을 명시]
  [Variance optimal hedging with application to Electricity markets, arXiv:1711.03733 — 미확인(초록만 확인, 본문 미독)]

---

## CVaR 헤지 최적화

- **Rockafellar-Uryasev 원 논문**: CVaR을 볼록 최적화 문제로 표현 — CVaR_α = min_η F_α(w,η). 옵션 포트폴리오 헤지 사례를 포함해 선형계획법으로 CVaR 최소화·제약을 동시에 다룸.
  [Rockafellar, R.T. & Uryasev, S. (2000), "Optimization of Conditional Value-at-Risk," Journal of Risk 3, 21–41. DOI: 10.21314/JOR.2000.038 — PDF: https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf]

- **CVaR 헤지와 최소분산 헤지의 관계**: 정규분포·마팅게일 가정 하에서는 VaR/CVaR 최소 헤지와 최소분산 헤지가 일치. 수익률 분포가 비타원형(non-elliptical, 즉 두꺼운 꼬리·비대칭)이면 CVaR 최소 헤지는 최소분산 헤지와 뚜렷이 달라짐 — 특히 국면전환(regime-switching) 모형에서 공동 폭락(joint crash) 시나리오가 있으면 헤지 비중이 커짐.
  [Cross hedging 관련: "VaR- and CVaR-minimal Futures Hedging Strategies," Mannheim Working Paper Series, MADOC — https://madoc.bib.uni-mannheim.de/31097/1/mm186.pdf]
  → **CAP L1-L2와의 직결점**: 전환비용 분포는 정규분포가 아니라 비대칭 두 꼬리(상방/하방)를 가진다고 이미 확인했으므로, 이 문헌이 정확히 "CVaR 헤지가 최소분산 헤지와 갈라지는 조건"을 제공. CAP이 "처음"이 아니라 이 조건에 해당하는 사례로 얹는 것.

- **복수 헤지 수단의 조합(포트폴리오 헤지)**: CVaR은 코히런트 리스크 척도이자 볼록함수이므로 여러 헤지 수단(파생상품 조합)에 대한 최적화도 볼록 최적화로 풀림. 실무적으로는 주성분분석(PCA)으로 복수 헤지 수단을 하나의 합성 헤지로 축약하는 접근도 존재.
  [MathWorks 예제, "Hedging Using CVaR Portfolio Optimization" — https://www.mathworks.com/help/finance/hedging-using-cvar-portfolio-optimization.html — 실무 튜토리얼 성격, 학술 출처 아님. 참고용]
  [Minimizing CVaR and VaR for a Portfolio of Derivatives, Yuying Li et al. — https://cs.uwaterloo.ca/~yuying/papers/cvarJBF.pdf — 미확인(서지 정보만, 본문 미독)]

---

## 부분 헤지가 최적인 이유

- **비용이 있으면 부분 헤지가 최적**: 헤지가 무비용일 때만 완전 헤지가 항상 최적. 현실에서는 프리미엄·거래비용이 존재하므로 한계비용=한계편익 지점에서 h*<1로 멈춤. (위 "완전 헤지가 최적이 아닌 이유" 참조, 원 논문 미특정)

- **기업이 완전 헤지 안 하는 이유 — 자금제약·유동성**: 재무적으로 제약된 기업일수록 헤지를 덜 하고 리스(lease)를 더 한다는 결과 — 완전 헤지에 쓸 자본 자체가 부족.
  [ScienceDirect 요약 인용 — 원 논문 특정 못 함, 리스-헤지 대체 관계를 다룬 코퍼레이트 파이낸스 논문으로 추정되나 저자·연도 미확인]

- **투자 자금조달과 헤지 — 표준 이론**: 외부자금 조달비용이 내부자금보다 비쌀 때, 헤지는 내부현금흐름을 안정시켜 과소투자 문제를 완화하는 역할을 한다. 이는 "완전 헤지"가 아니라 "투자 기회를 지킬 만큼만 헤지"하는 것이 최적이라는 함의를 가짐 — CEO가 성장기회를 포기하면서까지 헤지하지는 않는다는 실증과 부합.
  [Froot, K.A., Scharfstein, D.S. & Stein, J.C. (1993), "Risk Management: Coordinating Corporate Investment and Financing Policies," Journal of Finance 48(5), 1629–1658. NBER WP w4084]

- **CAP 지난 결과와의 연결(계약 격자 π = 꼬리 1원당 0.6~0.9전)**: 이는 CAP 내부 산출로, 이번 검색으로 확인한 외부 문헌이 아님 — 인용 표시 없이 "CAP 자체 결과"로만 사용할 것. 위 Froot-Scharfstein-Stein류 이론이 이 결과에 경제적 해석(π<완전헤지 비용은 과소투자 회피의 그림자가격)을 부여하는 자리로 얹을 수 있음. 이 연결 자체는 CAP의 해석이며 외부 문헌이 직접 검증한 것은 아님.

- **전력 PPA의 부분 헤지 실무**: 기업 PPA 실무에서는 부분 토링(partial tolls), 부분 OTC 헤지, 매출보험형 구조를 통해 상방을 일부 유지하면서 하방만 줄이는 방식이 쓰이며, 최적 헤지 비율은 반복적 축소 탐색이나 모델링으로 결정.
  [GridBeyond, "Corporate PPA & Hedging" — https://gridbeyond.com/energy-user-btm/corporate-ppa-hedging/ — 업계 자료, 학술 출처 아님. 참고용]

---

## 못 헤지하는 잔여·layering

- **재보험 layering 개념(원 선례)**: 초과손실(excess-of-loss) 재보험에서 여러 재보험사가 순차적으로 다른 손실 구간(layer)을 인수. 보험사는 임계값 이하 손실을 보유(retain)하고, 그 이상은 추가 layer로 넘김 — 재보험은 비용이 들기 때문에 비용과 편익의 균형에서 layer 구매량이 정해짐(완전 재보험은 최적이 아님, 위 부분 헤지 논리와 동형).
  [Fu, L. & Khury, C.K.S., "Optimal Layers for Catastrophe Reinsurance," Variance — https://variancejournal.org/article/141998-optimal-layers-for-catastrophe-reinsurance.pdf]
  [Management Study Guide, "Layering Approach in Reinsurance" — https://www.managementstudyguide.com/layering-approach-in-reinsurance.htm — 개론 자료, 학술 출처 아님]

- **재해채권(CAT bond) — 자본시장으로의 꼬리 이전**: 트리거 발생 시 원금이 스폰서(보험사/정부)에게 지급되고, 미발생 시 투자자에게 원금+쿠폰 반환. 즉 CAT bond 투자자가 지는 것은 정확히 "꼬리" 구간이며, 평상시에는 프리미엄(쿠폰)을 받는 구조 — CAP의 "잔여 꼬리를 투자자에게 넘긴다"는 그림과 구조적으로 동일.
  [Climate Policy Initiative, "Catastrophe Bonds" — https://www.climatepolicyinitiative.org/wp-content/uploads/2026/01/Catastrophe-Bonds.pdf]
  [Wikipedia, "Catastrophe bond" — 개요 확인용, 1차 출처 아님]
  → 기후 전환 맥락 적용 선례: CPI 자료가 "Loss and Damage 재원에 CAT bond를 적용하자는 논의가 COP28(2023) 이후 늘었다"고 언급 — 그러나 이는 물리적 기후재해(loss & damage) 맥락이지, 전환비용(transition cost) 맥락에 CAT bond가 실제 적용된 선례는 이번 검색에서 확인 못 함. **미확인**: "전환비용에 CAT bond형 구조를 적용한 선례"는 찾지 못함.

- **잔여 꼬리의 성격**: 헤지 후에도 남는 것은 (i) 베이시스 위험(헤지 수단이 노출을 완전히 못 따라감), (ii) 헤지 안 한 부분(h*<1로 의도적으로 남긴 부분), (iii) 헤지 수단 자체의 신용/거래상대 위험. CAP 맥락에서는 이 중 (ii)가 핵심 — 정책설계상 "왜 기업이 일부러 다 안 덮는가"의 답이 위 이론들.

---

## 전환금융 위험 계층화 (얹혀갈 대상)

- **블렌디드 파이낸스의 layering — 정착된 실무**: 공적/양허성 자본(concessional capital)이 후순위(first-loss/junior) 지분·후순위채로 먼저 손실을 흡수해 민간 투자자의 위험-수익을 투자 가능한 수준으로 이동시킴. 각 layer는 서로 다른 위험-수익 기대를 가지며, 위험은 가장 위험감내적인 자본 쪽으로, 수익은 가장 수익민감적인 자본 쪽으로 흐르는 구조.
  [Convergence, "Blended Finance" 개요 — https://www.convergence.finance/blended-finance]
  [OECD, "Making blended finance work: Why fund structure is the real driver of mobilisation" (2026) — https://www.oecd.org/en/blogs/2026/02/making-blended-finance-work-why-fund-structure-is-the-real-driver-of-mobilisation.html]
  [OECD DAC, "Blended Finance Guidance 2025" 사례집 — https://www.oecd.org/en/publications/oecd-dac-blended-finance-guidance-2025_e4a13d2c-en/full-report/case-studies_f6e822b0.html]
  → 수치(참고, 미검증 수준의 집계 통계): Convergence 발표 기준 2025년 중반까지 누적 블렌디드 파이낸스 거래 2,130억 달러, 1,200여 건, 양허성 자금 1달러당 평균 민간자본 4달러 동원.

- **CAP이 얹을 정확한 자리**: 블렌디드 파이낸스의 layering은 "기업(1차, first-loss) → 민간투자자(중간 layer) → 공적자본/정부(최후 layer, catastrophe-equivalent)"라는 CAP L3 가설과 구조적으로 동일한 언어(first-loss, junior/senior tranche)를 이미 갖고 있음. CAP이 할 일은 이 언어를 전환비용 분포의 두 꼬리(상방/하방)에 매핑하는 것이지, layering 개념 자체를 새로 제안하는 게 아님.

- **전환금융에서 정부의 역할 — 배킹은 있으나 "테일 layer"로 정식화한 선례는 미확인**: 그린 중앙은행 논의는 중앙은행이 개발금융기관에 저리 장기대출(climate-TLTRO)을 공급하거나 전환채권을 매입하는 방식의 정책 수단을 제시하지만, 이를 "재보험형 catastrophe layer"로 명시적으로 구조화한 논문·정책 문서는 이번 검색에서 확인하지 못함.
  [Green Central Banking, "Transition risk: how central banks can de-risk the transition" — https://greencentralbanking.com/2025/03/04/de-risking-the-transition/ — 미확인 수준: 정책 제안 성격 기사, 학술 논문 아님]

---

## 미확인

- "헤지가 무비용이면 완전 헤지가 항상 최적"이라는 명제의 원 출처 논문(저자·연도) — 검색 결과에 요약만 있고 1차 문헌을 특정하지 못함.
- 재무제약 기업의 헤지-리스 대체(hedge-vs-lease) 실증 논문의 정확한 저자·연도·저널 — ScienceDirect 요약만 확인, 서지 미특정.
- "전환비용(transition cost)"에 CAT bond 또는 재보험형 layering을 명시적으로 적용한 선행 연구 — 찾지 못함. 물리적 기후재해(loss & damage)에는 CAT bond 논의가 있으나 전환비용 맥락 적용 선례는 없음.
- Variance optimal hedging with application to Electricity markets (arXiv:1711.03733) — 초록 수준만 확인, 본문(방법론 세부) 미독.
- Minimizing CVaR and VaR for a Portfolio of Derivatives (Yuying Li et al., Waterloo) — 서지 정보만 확인, 본문 미독.
- CAP 계약 격자 결과(π=꼬리1원당 0.6~0.9전)를 Froot-Scharfstein-Stein 과소투자 이론과 직접 연결하는 것은 CAP 자체의 해석이며, 외부 문헌이 이 특정 수치를 검증하거나 언급한 바 없음 — 인용 시 "CAP 해석" 표시 필수.
- 규제 유틸리티의 가스/전력 조달 헤지 비율 실무 수치(예: 50~90% 헤지)는 이번 검색에서 특정 사례(CPUC 문서)의 세부 숫자(25%, 80%)만 확인되었고, 일반화된 업계 표준 수치는 확인 못 함.
