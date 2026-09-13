# L3 — 기업 CFO의 헤지 수단 (전환비용 분포의 상방 꼬리 중심)

방향 확인: 새 이론 없음. 기존 기업재무·전환금융 문헌에 철강·석화 전환비용 분포를 얹는다.
"CAP이 처음"이 아니라 "이미 있는 틀에 이 숫자가 들어간다"가 목표.

---

## 기업 위험관리 이론 (FSS 등)

- **[Froot, Scharfstein & Stein (1993), "Risk Management: Coordinating Corporate Investment and Financing Policies", Journal of Finance 48(5), 1629–1658 | https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1993.tb05123.x, NBER WP 4084: https://www.nber.org/papers/w4084]**
  핵심 논리: 외부자금이 내부자금보다 비쌀 때(정보 비대칭·대리비용), 현금흐름 변동성이 크면 좋은 투자 기회가 왔을 때 내부자금이 모자라 투자를 포기하거나 비싼 외부자금을 써야 한다. 헤지는 그 자체로 가치를 만드는 게 아니라 **"투자 정책과 재무 정책을 조율"**해서 이 과소투자(underinvestment)를 막는 데서 가치가 나온다. 즉 헤지 대상은 이익이 아니라 "투자를 계속할 수 있는 능력"이다.
  → 전환비용 적용: 철강·석화 기업이 전환비용 분포의 상방 꼬리(비용 폭발)를 헤지하는 이유는 "그 꼬리가 실현됐을 때도 전환투자(및 통상적 CAPEX)를 중단하지 않기 위해서"다. FSS 프레임을 그대로 대입하면 — 전환비용이 예상보다 커지는 상태는 정확히 "내부현금흐름이 부족한 상태에서 투자기회(남은 전환 이니셔티브, 통상 유지보수 CAPEX)가 여전히 남아있는" FSS의 시나리오다. 헤지 없이 이 상태에 놓이면 기업은 전환을 중도에 멈추거나(=본 연구의 "미완주" 시나리오), 비싼 외부자금(디스트레스드 대출·지분 희석)을 써야 한다.
  이 논문은 전환비용에 대해 말한 바 없음 — 순수 일반 기업재무 이론. 얹는 것은 우리 쪽 일.

- **[Smith & Stulz (1985), "The Determinants of Firms' Hedging Policies", Journal of Financial and Quantitative Analysis 20(4), 391–405 | https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/determinants-of-firms-hedging-policies/8035EEB5F9B1A1E07EFFC2573D55A62B]**
  세금 볼록성, 계약비용(파산비용 포함), 투자정책에 대한 영향을 헤지 동기로 제시. FSS보다 앞서 "왜 헤지하는가"의 표준 이론 축을 세움 — 기업은 리스크 자체가 아니라 리스크가 유발하는 파산 근접 비용·과소투자를 헤지한다.
  → 적용: 전환비용 상방 꼬리가 실현되면 레버리지가 급등하고 파산 근접 비용(공급사·고객 신뢰 상실, 조달 조건 악화)이 커진다 — 이 채널이 철강사가 전환비용을 헤지할 두 번째 이유(FSS의 과소투자 채널과 별개).

이 둘은 "전환금융"이나 "기후"를 다루지 않는다. 우리가 하는 일은 이 표준 프레임의 빈칸("외부자금이 비쌀 때"="전환기 철강사는 이미 레버리지가 높고 그린프리미엄 매출이 불확실해 외부자금이 특히 비싸다")에 CAP이 만든 분포를 넣는 것.

---

## 상방 꼬리 헤지 수단

전환비용 분포의 상방(비용 폭발) 꼬리를 좁히는 계약 수단. 실제로 그린스틸 프로젝트 파이낸싱에서 쓰이는 것과 문헌상 제안되는 것을 구분.

1. **EPC 고정가/턴키·GMP(Guaranteed Maximum Price) 계약, 성능보증**
   확인: EPC 업체(예: Andritz 등)가 그린수소/P2X 플랜트에 "full performance guarantee"를 포함한 EPC를 제공한다는 사실은 확인됨 [Andritz, "Decarbonizing the steel industry with green hydrogen" | https://www.andritz.com/power-to-x-en/use-cases/green-steel]. RMI는 최초 상용화(FOAK) 플랜트의 뱅커빌리티 확보 전략으로 "EPC/기술계약상 성능보증"과 "마일스톤 연동 기술위험 커버"를 제시함 [RMI, "Five Lessons for Industrial Project Finance from H2 Green Steel" | https://rmi.org/five-lessons-for-industrial-project-finance-from-h2-green-steel/].
   분포 효과: 건설비 초과(construction cost overrun) 성분을 계약 상대(EPC사)로 이전 — 분포의 우측 꼬리 중 "시공 단계 초과비용" 성분을 자른다. 단, EPC사 자신의 파산위험(캡 있는 손해배상 한도)까지는 못 지운다 — 완전한 절단이 아니라 절단점 이동.
   실무 현황: **미확인** — 그린스틸 프로젝트에서 GMP/비용초과 상한이 실제로 어느 정도 채택됐는지 구체 계약조건은 검색으로 확인 못함. 위 RMI 문서도 "제안 전략"으로 서술, 실제 체결 사례의 계약조건 공시는 찾지 못함.

2. **에너지 PPA (전력가 고정)**
   확인: PPA는 5~20년 장기로 사전 협상된 가격에 전력을 구매하는 계약이며, 철강·화학 등 하드투어베이트 산업의 탈탄소화에 널리 쓰인다는 서술 확인 [TotalEnergies, "What is a PPA?" | https://totalenergies.com/news/news/what-power-purchase-agreement-ppa; ENGIE Impact PPA guide]. 실사례: Enery-Lenzing AG(오스트리아, 2022, 20년 계약)로 산업 탈탄소화용 PPA 확인.
   분포 효과: 전환비용 중 "운영 단계 에너지 투입비" 성분의 가격 변동성을 없앤다 — 이는 CAP의 총전환비용 분포에서 "운영기 그린에너지 프리미엄" 성분에 해당하는 축을 좁히는 것과 정확히 대응. 단, PPA는 가격만 고정하지 **물량**(실제 가동률에 따라 필요한 전력량)은 고정 못함 — 가동률이 계획보다 낮으면 물량 미스매치 위험이 남음(take-or-pay 조항 없으면).

3. **원료 장기계약·선물 (예: 철광석, 나프타)**
   미확인 — 이번 검색에서 철강/석화 원료 장기계약이 "전환비용" 관점에서(전환 후 원료 배합 변화 관련) 다뤄진 자료를 특정하지 못함. 원료 헤지 자체는 표준 상품헤지 관행이므로 존재는 자명하나, 전환비용 분포와 연결한 문헌은 미확인으로 남김.

4. **수소 오프테이크 (take-or-pay)**
   확인: take-or-pay 조항은 구매자가 수소를 인수하거나 인수하지 않아도 대금을 지불하게 해 프로젝트에 최소 매출을 보장 — "merchant risk"를 줄인다 [GH2, "Key considerations for green hydrogen offtake agreements" (2024) | https://gh2.org/sites/default/files/2024-05/GH2_Considerations%20for%20Hydrogen%20Offtake%20Agreements_2024.pdf]. 실사례: H2 Green Steel(현 Stegra)이 초기 생산량 250만톤 중 150만톤 이상을 BMW·Mercedes-Benz·Porsche·Scania·Volvo와 5~7년 오프테이크로 사전판매, 이를 근거로 은행이 35억 유로 채무를 커밋 [RMI 위 문서; EnkiAI, "Stegra Hydrogen 2026" | https://enkiai.com/hydrogen/stegra-green-steel-financing/].
   분포 효과: 이건 **비용측** 헤지가 아니라 **매출측** 헤지 — 전환비용이 얼마가 됐든 매출을 사전 고정해 "순현금흐름"의 하방을 받친다. FSS 프레임에서 정확히 "내부현금흐름 확보"에 해당. 단, 오프테이크는 비용 폭발 자체를 지우지 않는다 — 비용이 오프테이크 계약가보다 더 오르면(그린프리미엄 계약가 고정 vs 실제 원가 상승) 마진이 압축될 뿐 기업은 여전히 비용초과를 흡수해야 함.

5. **실패 사례가 보여주는 헤지의 한계 — Stegra(옛 H2 Green Steel) 2025년 유동성 위기**
   확인: 위 오프테이크·EPC 보증에도 불구하고 Stegra는 2025년 하반기 최대 9.75억 유로의 추가 자금을 필요로 하는 유동성 위기에 처함 — 원인은 "예상보다 높은 프로젝트 비용, 예기치 못한 인프라 비용, 정부 보조금 지급 지연" [CleanTechnica, "Hydrogen's Brutal Month" (2025) | https://cleantechnica.com/2025/07/07/hydrogens-brutal-month-billions-lost-as-mega-projects-collapse/; Vogon Today, "Is Swedish green steel on the verge of collapse?" (2025) | https://www.vogon.today/economic-scenarios/is-swedish-green-steel-on-the-verge-of-collapse-stegra-in-crisis-amidst-enormous-costs-and-the-ghost-of-northvolt/2025/10/23/].
   해석: 오프테이크(매출 헤지)와 EPC 성능보증이 있어도 **분포 우측 꼬리 전체를 못 지운다** — 특히 "정부 보조금 지급 지연"은 계약으로 넘길 수 없는 정책 실행위험이며, 이는 뒤의 "기업이 못 헤지하는 잔여" 절과 직결.

---

## 전환금융 실무 틀 (얹혀갈 대상)

- **[ICMA, Climate Transition Finance Handbook, 2020년 12월 초판 / 2023년 6월 개정 / 2025년 11월 최신판 | https://www.icmagroup.org/assets/documents/Sustainable-finance/2025-updates/Climate-Transition-Finance-Handbook-November-2025.pdf]**
  이 핸드북 자체는 "비용 분포"를 정량적으로 다루지 않는다 — 발행자가 공시해야 할 4대 요소(전환전략·거버넌스, 비즈니스모델의 환경중대성, 과학기반 목표와의 정합, 이행의 투명성)를 정하는 **공시 프레임**이다. 우리가 얹을 지점: CAP의 전환비용 분포(및 그 상방/하방 시나리오)는 "이행의 투명성" 요소에서 요구하는 "자본지출 계획과 그 가정"을 구체화하는 정량 도구로 위치할 수 있음 — 즉 CAP은 ICMA 핸드북이 요구하는 공시 항목에 숫자를 채우는 역할이지, 새 공시 기준을 만드는 게 아님.

- **Sustainability-Linked Bond/Loan (SLB/SLL)**
  확인: SLB는 자금 용도를 제한하지 않고(green/전환본드와 달리) 발행자의 지속가능성 목표(대개 온실가스 KPI) 달성 여부에 따라 쿠폰 등 조건이 바뀐다 [Lexology, "ICMA Updates..." ; Luxembourg Stock Exchange, "Exploring Sustainability-Linked Bonds"]. SLL은 대출시장에서 먼저 시작되어 ICMA가 채권시장으로 확장 적용.
  → 기업 관점에서 비용 위험 처리 방식: SLB/SLL은 "비용이 얼마 드는가"가 아니라 "감축목표를 달성했는가"에 연동 — 즉 **비용 분포 자체를 헤지하는 상품이 아니라, 목표 미달 시 재무적 페널티(쿠폰 상승)를 부과하는 상품**이다. 이는 기업의 전환비용 상방 꼬리를 좁혀주지 않고 오히려 목표 미달 시 자금조달비용을 얹어 하방(전환 포기) 유인을 만들 수도 있다는 점에서, CAP 분포 프레임에서는 "헤지 수단"이 아니라 "인센티브 계약"으로 분류해야 함 — 이 구분은 미확인 문헌 종합이 아니라 이번 조사에서 도출한 해석이므로 표시.

- **한국 전환금융 가이드라인**
  확인: 정부(금융위)는 2026~2035년 790조원 규모 기후금융 공급 로드맵을 발표, K-Taxonomy(그린 분류체계, 환경부 소관)와 "업종별 탄소감축 이행 로드맵"(산업부 소관) 기반 전환금융 두 트랙을 병행한다는 보도 확인 [비즈니스포스트, "[기후경쟁력포럼⑤] EU·일본 모델 섞은 한국형 전환금융..." | https://www.businesspost.co.kr/BP?command=article_view&num=439795; Kim & Chang, "한국형 녹색분류체계(K-Taxonomy) 가이드라인 발표" | https://www.kimchang.com/ko/insights/detail.kc?sch_section=4&idx=24605]. 기업 관점에서 이 틀이 비용 분포를 어떻게 다루는지 구체 방법론(예: 정량 기준선)은 **미확인** — 언론 보도 수준의 정책 발표 확인이며, 가이드라인 원문의 비용 산정 방법론까지는 접근하지 못함.

---

## 헤지 회계·자본예산 (CFaR)

- **[Andrén, Jankensgård & Oxelheim (2005), "Exposure-Based Cash-Flow-at-Risk: An Alternative to VaR for Industrial Companies", Journal of Applied Corporate Finance 17(3), 76–86 | https://ideas.repec.org/a/bla/jacrfn/v17y2005i3p76-86.html, SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1010123]**
  CFaR = VaR의 현금흐름판. "노출기반(exposure-based)" CFaR는 거시/시장변수(환율·원자재가·금리 등)가 기업 현금흐름에 미치는 민감도(노출계수)를 추정한 뒤, 그 변수들의 결합분포로 미래 현금흐름의 분포를 시뮬레이션한다. Norsk Hydro 실제 적용 사례 포함.
  → 적용: CAP의 전환비용 분포는 정확히 이 틀의 입력이 될 수 있다 — "전환비용"을 하나의 노출 변수로 놓고, 그 분포가 회사 현금흐름 분포에 어떻게 투영되는지가 CFaR 계산의 다음 단계. CAP은 "전환비용 분포를 만드는" 앞단, CFaR는 "그 분포를 기업 현금흐름 위험도로 바꾸는" 뒷단 — 두 틀은 이어붙는 관계지 경쟁 관계가 아님.
  일반적 정의: CFaR는 주어진 신뢰수준·기간에서 미래 현금흐름이 기대치보다 얼마나 부족할 수 있는지를 나타내는 지표 [ION Group, "Why corporates must consider cash flow at risk (CFaR)"].

- **자본예산·실물옵션에서 비용 분포를 넣는 법**
  확인 가능한 일반론: 표준 NPV는 "투자 유연성(옵션성)을 무시하는" 한계가 있고, 경영진은 자본예산과 위험관리 결정을 별개로 다뤄서는 안 된다는 서술 확인 [Auburn Univ. ETD, "Using Real Options Analytics to Improve the Capital Budgeting Process under Uncertainty"]. 그러나 이 자료는 전환비용에 특정된 것이 아니라 일반 자본예산 방법론 서술 — 철강·석화 전환투자에 실물옵션을 적용한 구체 논문은 이번 검색에서 특정하지 못함(미확인).
  → 얹는 지점: 전환투자는 전형적인 "지연 옵션"(wait-and-see) 대상 자산 — CAP의 분포가 우측으로 두꺼운 꼬리를 가질수록(본 8루프 L2 결론) 실물옵션가치상 "지금 투자 대신 정보를 더 얻고 나중에 투자"할 옵션가치가 커진다는 표준 결과와 연결됨. 이 연결 자체는 실물옵션 표준이론의 자명한 함의이며 CAP이 새로 발견한 것 아님.

---

## 기업이 못 헤지하는 잔여

계약으로 못 넘어가는 위험, 즉 기업 헤지의 한계 = 다음 주체(투자자·정부, L4·L5)의 자리.

1. **탄소가격 하방(정책 후퇴·이행 지연) — 정부로 넘어가야 함**
   CCfD(Carbon Contracts for Difference) 문헌이 이 지점을 정확히 짚음: CCfD는 "탄소가격의 불확실성을 줄이고 비용격차(cost gap)를 메우는" 정부-기업 양방향 계약으로, 시장 탄소가격이 계약 행사가(strike price) 밑으로 떨어지면 정부가 차액을 지불한다 [ScienceDirect/PMC, "Carbon contracts-for-difference: How to de-risk innovative investments for a low-carbon industry?" | https://www.sciencedirect.com/science/article/pii/S2589004222009725]. 철강 사례 정량치 확인: CCfD로 탄소완화비용을 최대 27%까지 낮출 수 있으나, 프로젝트가 뱅커블하려면 **CCfD 가격의 79% 수준의 가격 하한(price floor)**이 필요하다는 추정 확인 [동 자료]. 독일 정부는 2023년 6월 500억 유로(15년) 규모로 철강·화학·제지·시멘트 CCfD를 발표 [동 자료].
   → 이것은 기업이 시장에서 살 수 있는 상품이 아니라 정부만 공급 가능한 계약 — L5(정부 헤지)의 핵심 수단으로 넘어감. FSS/Smith-Stulz 틀 안에서는 이 위험이 "시장에 헤지 상품이 존재하지 않는(incomplete markets) 위험"에 해당.

2. **접근형(access-type) 물량 위험 — 선점(오프테이크)으로만 부분 해결, 완전 해결은 안 됨**
   오프테이크(수소, 그린스틸 프리미엄 구매계약)는 매출 물량을 사전 확보하지만, 이는 "먼저 계약한 기업이 유리한" 선점 경쟁 구조를 만들 뿐 — 시장 전체의 물량 위험(예: 그린스틸 프리미엄 수요가 애초에 기대만큼 형성되지 않는 위험)은 개별 계약으로 지워지지 않는다. SteelOnTheNet, "Green Steel Premiums: Promise or Illusion?"가 이 회의론을 다룸(제목 확인, 본문 상세 미확인).
   → 후발기업에게는 이 물량이 이미 선점된 상태로 넘어감 — 이는 헤지 수단의 부재라기보다 "누가 먼저 계약했는가"의 순서 문제이며, 시장 메커니즘으로 재분배되지 않음. 정부/투자자 개입(예: 산업클러스터 단위 공동조달)의 필요성으로 이어지는 지점이나, 이번 조사에서 이를 다루는 구체 문헌은 특정하지 못함(미확인).

3. **정책 실행위험(보조금 집행 지연) — Stegra 사례가 실증**
   위 5번 항목에서 확인한 대로 Stegra의 2025년 위기 원인 중 하나가 "정부 보조금 지급 지연"이었음 — 이는 계약으로 사전에 이전할 수 없는 위험이다(정부의 이행 신뢰도 자체가 위험 원천). CCfD 같은 계약형 정부 수단도 정부의 예산·집행 역량이라는 상위 위험까지는 못 지운다.

4. **원가 자체의 구조적 상승(그린프리미엄 원가가 계약가보다 더 오르는 경우)**
   오프테이크는 매출가를 고정하지만 원가가 계약가보다 더 오르면 마진압축을 기업이 그대로 흡수 — PPA·원료 장기계약으로 각 원가 성분을 개별적으로 고정하지 않는 한 완전 헤지가 안 됨. 현실에서는 모든 원가 성분을 동시에 장기 고정하는 사례를 확인하지 못함(미확인) — 부분적 헤지가 실무 현황으로 보임.

---

## 얹혀갈 선행 (어느 틀에 얹나)

CAP 분포가 새 이론을 만드는 게 아니라, 다음 세 틀 각각의 "빈 칸"에 숫자를 넣는 역할로 위치시킨다.

1. **FSS(1993)/Smith-Stulz(1985) 기업 헤지 이론** — 빈 칸: "비용 충격의 크기와 분포 형태"가 구체적으로 얼마나 되는지는 FSS가 답하지 않음(그 이론은 정성적·일반균형적). CAP은 철강·석화 전환비용이라는 구체 산업의 그 분포를 만들어 FSS의 과소투자 채널이 실제로 얼마나 심각한지 정량화하는 입력을 제공.
2. **CFaR (Andrén et al. 2005) 기업 재무 실무** — 빈 칸: 전환비용을 "노출 변수"로 다룬 CFaR 적용 사례가 없음(적어도 이번 검색 범위에서 미확인). CAP의 분포를 CFaR의 노출 변수 중 하나로 투입하면 이 틀의 첫 사례가 될 수 있음(단, 이는 "CAP이 최초"라는 주장이 아니라 "이 틀을 이 산업에 처음 적용"이라는, 훨씬 좁고 안전한 주장).
3. **ICMA Climate Transition Finance Handbook의 "이행 투명성" 공시 요구** — 빈 칸: 핸드북은 기업이 자본지출 계획과 가정을 공시하라고 요구하지만 그 불확실성 범위(분포)를 어떻게 정량화할지는 규정하지 않음. CAP은 그 공시 항목에 채울 정량 방법론 중 하나로 위치.

이 세 틀 중 어디에 얹을지는 논문 프레이밍의 선택 문제이며, 8루프 후반(L7·L8)에서 CAP 최종 산출물의 용도에 따라 결정.

---

## 미확인 (검색으로 확정하지 못한 것들 — 목록)

- 그린스틸 프로젝트 파이낸싱에서 GMP/비용초과 상한 계약조건의 구체 수치(존재 여부는 방향상 확인, 계약조건 공시는 미확인)
- 철강/석화 원료(철광석·나프타) 장기계약·선물을 "전환비용 분포" 관점에서 다룬 학술 문헌
- 한국 전환금융 가이드라인 원문의 비용 산정 방법론(정책 발표 수준만 확인, 가이드라인 세부는 미확인)
- 전환투자에 실물옵션을 명시적으로 적용한 철강/석화 특정 논문
- SLB/SLL을 "헤지 수단"이 아니라 "인센티브 계약"으로 분류하는 것은 이번 조사의 해석이며 이렇게 명시적으로 구분한 선행문헌은 특정하지 못함
- 접근형 물량 위험(그린스틸 프리미엄 시장 형성 불확실성)을 다루는 구체 학술 문헌 — SteelOnTheNet 글의 제목만 확인, 본문 논지 미확인

---

# SYNTHESIS L3 (기업 CFO 헤지) — 2026-09-13 · 얹혀가기 확정 + TCaR 위치

## TCaR의 위치 (사용자 확정 2026-09-13)
TCaR는 **새 위험측도가 아니다.** Expected Shortfall(Rockafellar-Uryasev 2000)을 기업 **전환비용 분포**에
적용한 것의 **이름**이고, Climate VaR(Dietz et al. 2016)·Carbon VaR·MSCI Transition VaR 계보를 잇는다.
발명이 아니라 명명. 논문 한 문장으로 못박는다:
> "TCaR는 새 위험측도가 아니라, expected shortfall을 기업 전환비용 분포에 적용해 Climate VaR·Carbon
> VaR 계보를 잇는 것이다."

**두 꼬리가 TCaR를 정당화한다** (L2 활용): 전환비용은 상방(비용 폭발)·하방(좌초) 두 꼬리가 다른
원천. 그냥 "VaR"는 어느 꼬리인지 안 보인다. TCaR를 두 꼬리로 정의 — **상방 TCaR(비용 위험)·
하방 TCaR(좌초 위험)** — 하면 이름이 정보를 담는다. 이게 Climate VaR보다 더하는 작은 것(거창하지 않게).

## 기업은 first-loss 층, 계약으로 부분 헤지, 나머지 위로
- **헤지하는 것**: 상방 일부 — EPC/GMP 캡(비용초과), PPA(전력가), take-or-pay 오프테이크(매출측).
  단 **부분만**(h*<1, Ederington 1979 표준 — 베이시스 위험+헤지비용). Stegra 실증: 오프테이크+EPC
  보증에도 €975M 유동성 위기(비용초과+보조금 지연) → 계약형 헤지 불완전.
- **못 헤지해 위로 넘기는 것**: 탄소 하방(→정부 CCfD), 접근형 물량(→선점), 정책 실행 위험, 구조적
  원가 상승. = 다음 주체(투자자 L4·정부 L5)의 자리.

## 얹혀갈 틀 = CFaR (핵심)
CFaR(Andrén-Jankensgård-Oxelheim 2005, 노출기반 현금흐름 위험): CAP 분포가 그 틀의 **"노출 변수"
입력**으로 이어붙는다 — 경쟁이 아니라 전/후단. **CAP은 새 방법이 아니라 기존 CFaR에 더 나은 노출
입력(전환비용 분포).** 왜 헤지하나는 FSS 1993(외부자금 비싸 과소투자 방지).

## 얹혀가기 스택 (L3 확정 — 거창함 방지)
| 층 | 얹혀갈 기존 틀 | CAP이 더하는 것 |
|---|---|---|
| 위험측도 | ES/CVaR (Rockafellar-Uryasev), Climate VaR(Dietz) | TCaR 명명 + 두 꼬리 분해 |
| 왜 헤지 | FSS 1993, Smith-Stulz 1985 | 전환비용에 적용 |
| 어떻게 재나 | CFaR (Andrén 2005) | 전환비용 분포를 노출 입력으로 |
| 얼마나 헤지 | 부분헤지 h*<1 (Ederington) | 전환 계약 격자 π |
| 누가 지나 | blended finance layering (OECD) | 기업·투자자·정부를 두 꼬리에 매핑 |
| 최근접 선행 | Wolf 2025 (유럽 철강 전환비용 위험) | 한·일 확장 + 세 주체 |
새 이론 0. 전부 기존 틀에 케이스를 넣는다.

## 직전(L1·L2) 비판적 재검토
L2의 "세 주체가 분포의 다른 부분을 진다"가 L3에서 **blended finance layering이라는 기존 언어**를 얻었다 —
발명이 아니라 매핑. 기업=first-loss, 그 위 잔여가 투자자·정부로. Stegra가 계약형 헤지의 불완전성을
실증(first-loss 층도 다 못 막음). 거창하게 "CAP이 계층화를 전환에 도입"이라 하지 말고 "전환비용
분포를 기존 계층화·CFaR의 입력으로"라 쓴다.
