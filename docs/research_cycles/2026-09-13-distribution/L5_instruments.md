# L5 — 정부 수단이 분포의 어느 부분을 자르나

전제(L1~L4 이어받음): 전환비용을 분포로 보고, 기업(first-loss)·투자자(mezzanine)·정부(catastrophe)가 층을 나눠 진다는 blended finance 언어. 유럽은 정부(ECA)가 mezzanine까지 흡수. 여기서는 새 이론 없이 기존 문헌에 얹혀, 각 정부 수단의 페이오프가 분포의 어느 부분(하방 꼬리/상방 꼬리/몸통)을 자르는지만 정리.

---

## CCfD 페이오프

**메커니즘 (양방향, two-way).** Carbon Contract for Difference는 정부와 기업 간 계약으로, 행사가(strike price)를 정해두고: 시장 탄소가 < 행사가 → 정부가 차액을 기업에 지급(하방 보전). 시장 탄소가 > 행사가 → 기업이 차액을 정부에 환수(상방 캡). 이는 순수 보조금과 달리 "국가는 저탄소 기술의 추가비용만 지원하고, 프로젝트가 예상보다 저렴해지면 그 이득을 환수"하는 구조.
[Carbon Contracts for Difference (CCfD) 설명, Homaio glossary | https://www.homaio.com/glossary/ccfds]

**원 논문.** Jörn C. Richstein & Karsten Neuhoff (2022), "Project-based carbon contracts-for-difference: how to de-risk innovative investments for a low-carbon industry?", *iScience* (2022년 7월). 철강 사례 연구에서 CCfD가 감축 비용을 최대 27% 낮출 수 있음을 보였고, 가동비용(OPEX) 증분이 커서 프로젝트가 은행 대출 가능(bankable)해지려면 가격하한(price floor)이 CCfD 가격의 79% 수준으로 필요하다고 제시.
[Richstein & Neuhoff (2022), "Project-based Carbon Contracts for Differences or Price Floors: how to de-risk innovative investments for a low-carbon industry", iScience | https://www.sciencedirect.com/science/article/pii/S2589004222009725]

**분포와의 관계.** 양방향 CCfD는 정확히 하방 좌초 꼬리(시장 탄소가가 예상보다 낮아 저탄소 설비가 손실을 보는 시나리오)를 자르는 동시에, 상방에서 기업이 초과이익을 정부에 반환하게 해 정부 부담의 꼬리도 제한한다. 즉 페이오프가 대칭적인 "밴드 고정"이지, 분포 전체를 이동시키는 보조금이 아니다.

**독일 실증(KSV, Klimaschutzverträge).** 1차 입찰 라운드: 17개 응찰 중 15개 프로젝트 선정, 최대 재원 규모 약 €28억(2.8 billion), 15년 계약 기간, 향후 15년간 최대 1,700만 tCO2e 감축 예상. 기업이 "톤당 감축에 필요한 정부 지원액"을 경쟁 입찰로 제시하는 역경매(reverse auction) 구조.
[Clean Energy Wire, "Germany awards first companies with pioneering 'climate contract' scheme to slash industry emissions" | https://www.cleanenergywire.org/news/germany-awards-first-companies-pioneering-climate-contract-scheme-slash-industry-emissions]
[Clean Energy Wire, "Germany launches first auction for pioneering industry decarbonisation subsidy scheme" | https://www.cleanenergywire.org/news/germany-launches-first-auction-pioneering-industry-decarbonisation-subsidy-scheme]
[BMWK, FAQ – Carbon Contracts for Difference (Klimaschutzverträge) | https://www.klimaschutzvertraege.info/lw_resource/datapool/systemfiles/agent/ewbpublications/f7531bfd-eb98-11ee-8b39-a0369fe1b6c9/live/document/2403_EN_BMWK-FAQ_Klimaschutzvertraege.pdf]

독일은 2라운드를 €50억(5 billion) 규모로 추가 진행 중.
[Clean Energy Wire, "Germany launches 5-billion-euro second round of industry transition support scheme" | https://www.cleanenergywire.org/news/germany-launches-5-billion-euro-second-round-industry-transition-support-scheme]

**비대칭 설계 문헌(참고, 미완독).** "Designing carbon contracts for difference under asymmetric information" (ScienceDirect, 저자·연도 미확인 — 페이월로 상세 확인 못함). 정보 비대칭 하에서 CCfD 설계를 다루는 후속 문헌이 존재한다는 사실만 확인, 내용은 [미확인]으로 분류.
[ScienceDirect 항목 페이지 | https://www.sciencedirect.com/science/article/abs/pii/S0165176525004367]

---

## 가격하한·밴드·보증

**가격하한(price floor) — 풋 성격, 하방만 절단.** 영국 Carbon Price Floor(CPF, 2013년 시행)는 EU ETS 배출권 가격에 Carbon Price Support(CPS)를 얹어 정부가 정한 최저 수준까지 끌어올리는 구조 — "top-up tax." 편도(one-sided) 보호: 가격이 바닥 밑으로 떨어지는 것은 막지만 상단 캡은 없음.
[House of Commons Library, "Carbon Price Floor (CPF) and the price support mechanism" | https://commonslibrary.parliament.uk/research-briefings/sn05927/]

풋옵션과의 유비: 가격하한은 발행자(정부)가 쓴 풋을 보유자(투자자·기업)에게 무상 제공하는 것과 동일한 페이오프 — 하방 좌초 꼬리만 자르고 상방은 손대지 않음. (이 비유 자체는 일반적 옵션 이론 서술이며 특정 논문 인용은 아님 — 표시: [일반론, 특정 서지 미확인])

**일본 GX-ETS 밴드 — 칼라(collar) 구조.** 2026회계연도부터 GX-ETS(Phase 2)가 의무화되며 가격에 하한 1,700엔/tCO2·상한 4,300엔/tCO2의 밴드를 설정. 매년 인플레이션+3% 수준으로 상승. Phase 2는 연간 배출량 10만 tCO2 이상인 약 300~400개 기업 대상.
[ICAP, "Japan GX-ETS" | https://icapcarbonaction.com/en/ets/japan-gx-ets]
[METI/UNFCCC, "Overview of Japan's GX Policy and Carbon Pricing", April 2026 | https://unfccc.int/sites/default/files/resource/Session_02_01_Japan_GX-ETS.pdf]

밴드(칼라)는 하한에서 풋, 상한에서 콜을 매도한 조합 — 하방 좌초 꼬리와 상방 규제비용 폭발 꼬리를 동시에, 그러나 CCfD처럼 기업별 프로젝트 단위가 아니라 시장 전체 가격 수준에서 자른다는 점이 다르다.

**공적 보증(ECA) — 상방 비용초과 흡수.** 수출신용기관(ECA) 보증은 대출기관을 차주 채무불이행으로부터 보호하는 신용보강 수단이며, 상업적 자금조달이 어렵거나 비경제적인 국경간 거래에 정부 신용을 붙인다. 다만 검색된 자료 기준으로 ECA 보증이 EPC 계약의 "비용초과(cost overrun)"를 직접 커버하는 표준 상품이라는 근거는 약함 — ECA 보증의 주된 대상은 대출 원리금 상환 리스크(차주/국가 리스크)이며, EPC 계약 자체 내에서 시공사의 대규모 비용초과·이탈을 완전히 막을 장치는 제한적이라는 점이 실무 문헌에서 지적됨.
[Norton Rose Fulbright, "Export credit agency financing: Ten key questions answered" | https://www.nortonrosefulbright.com/en/knowledge/publications/ef4acd99/export-credit-agency-financing-ten-key-questions-answered]
[Long International, "EPC Contract Risk Analysis: Projects in Developing Countries" | https://www.long-intl.com/articles/epc-contract-risk-analysis/]

→ **[미확인]**: "ECA가 상방 비용초과 꼬리를 자른다"는 명제는 유럽 대형 프로젝트(예: 원자력·수소환원제철 신기술) 사례에서 정책적으로 언급되지만, 본 검색에서 그 메커니즘을 정량적으로 다룬 학술 논문은 찾지 못함. L4에서 확인한 "유럽 ECA가 mezzanine까지 흡수" 사실과의 정합성은 별도 문헌으로 재확인 필요.

**Blended finance 일반 이론 — 정부가 최하층(first-loss).** 전형적 블렌디드 구조는 상업은행의 선순위(senior), 개발금융기관(DFI)의 메자닌(mezzanine), 기후펀드·공여자의 후순위/최하층(junior/first-loss)으로 쌓인다. 후순위 자본이 손실을 먼저 흡수해 선순위 투자자의 참여를 유도하며, 사용 빈도는 낮지만 투입한 공적자금 대비 민간자금 동원 효과(mobilisation)가 더 크다는 것이 OECD 최근 분석의 요지.
[OECD, "Making blended finance work: Why fund structure is the real driver of mobilisation" (2026) | https://www.oecd.org/en/blogs/2026/02/making-blended-finance-work-why-fund-structure-is-the-real-driver-of-mobilisation.html]

---

## 수단↔분포 부분 매핑

| 정부 수단 | 페이오프 구조 | 자르는 부분 | 근거 |
|---|---|---|---|
| CCfD (독일 KSV) | 양방향: 시장가<행사가 시 정부 지급, >행사가 시 기업 환수 | **하방 좌초 꼬리**를 정밀 절단 + 상방 초과이익 환수(정부 부담 꼬리도 제한) | Richstein & Neuhoff (2022); Clean Energy Wire (KSV 1차) |
| 탄소가격 하한 (영국 CPF) | 편도: 가격이 바닥 아래로 가면 정부/제도가 차액만큼 부과·보전 | **하방 좌초 꼬리만** (풋 성격) | House of Commons Library (2013 CPF) |
| 가격 밴드/칼라 (일본 GX-ETS) | 하한 풋 + 상한 콜 매도 | **하방 꼬리 + 상방 꼬리**, 단 시장 전체 수준에서 (프로젝트별 아님) | ICAP; METI/UNFCCC (2026) |
| 공적 보증 (ECA) | 채무불이행·대출 원리금 리스크 인수 | **상방 비용초과·신용 꼬리** (단, EPC 비용초과 직접 커버는 [미확인]) | Norton Rose Fulbright; Long International |
| 보조금/무상할당 (K-ETS 4기 등) | 비용 수준을 일률적으로 낮춤, 상태(state)에 연동되지 않음 | **몸통(수준 이동)** — 꼬리를 자르지 않음 | ICAP, Korea K-ETS Phase 4 |
| CBAM (EU, 외부 정부) | 무전환 기업의 EU 시장접근 비용을 부과 | 한·일 수출기업 입장에서는 **자국 정부가 다루지 않는 꼬리를 외부 정부가 대신 자름** (시장접근 상실 리스크) | OECD; European Commission |

---

## 한·일 정부 수단 실태

### 한국

- **CCfD: 부재하나 법제화 착수 단계(2024~2026).** 환경부(現 기후에너지환경부)가 "탄소차액계약제도 운영방안 및 시범적용 연구"를 추진, 2024년 법적 근거 마련·운영지침 개발, 2025년 시범사업 예정. 대상은 철강·석유화학·시멘트 등 탄소 다배출·난감축(hard-to-abate) 업종, 수소환원제철·전기로·CCUS 등 혁신설비, 10~15년 장기계약 구조로 설계 중. 즉 **아직 가동 중인 CCfD는 없음** — 하방 좌초 꼬리를 자르는 수단이 설계도 단계에 머물러 있다는 것이 정확한 현황.
  [전자신문, "한국형 탄소차액계약제 나오나…환경부 제도 구체화 착수" (2024-02-25) | https://www.etnews.com/20240225000067]
  [시사저널e, "[단독] 철강·화학 탄소감축 비용, 정부가 메워준다···탄소차액계약제 법제화 착수" | https://www.sisajournal-e.com/news/articleView.html?idxno=421635]

- **K-ETS 4기(2026~2030): 무상할당 100% 유지.** 2025년 11월 확정된 국가 배출권 할당계획에 따르면 철강·비철금속·석유화학·시멘트·반도체 등 탄소누출 우려 업종(산업부문 배출량의 약 95%)은 4기에도 100% 무상할당 유지. 발전부문 유상할당 비중은 2030년까지 50%로 단계적 확대, 비발전 부문은 15% 유상. K-MSR·신규진입자 예비분 제외 전체 유상비율은 약 11%.
  [ICAP, "Korea approves Phase 4 K-ETS allocation plan for 2026–2030" | https://icapcarbonaction.com/en/news/korea-approves-phase-4-k-ets-allocation-plan-2026-2030]

  → 무상할당은 **몸통을 통째로 낮추는 수단**(비용 수준 이동)이며, 분포의 어느 꼬리도 겨냥해 자르지 않는다는 점이 CCfD·가격하한과 본질적으로 다르다.

- **790조원 기후금융 로드맵(2026~2035).** 금융위원회가 기존 2024~2030년 420조원 계획을 2026~2035년 790조원으로 확대 발표. 재원의 절반 이상을 지방에, 70% 이상을 중소기업에 배분 목표. 5대 정책금융기관(산업은행·기업은행·수출입은행·신용보증기금·기술보증기금)이 주 공급자. '한국형 전환금융'을 도입해 철강·화학·시멘트 등 고탄소 업종의 설비효율화·연료전환 지원.
  [Lexology, "금융위, 녹색·전환금융 790조원 공급 로드맵 발표" | https://www.lexology.com/library/detail.aspx?g=71c9b19a-039a-48a7-baca-c4f1a57d1400]
  [ESG타임즈, "금융위, '2035년까지 790조 기후금융' 발표…전환금융 확대·가이드라인 착수" | https://www.esgn.co.kr/news/articleView.html?idxno=8577]

  → 이 자금은 대출·보증·출자 등 정책금융 수단의 총량이며, 페이오프 구조(꼬리를 자르는지 수준을 낮추는지)가 개별 상품별로 다를 것이나 본 검색으로는 상품별 페이오프 상세를 확인하지 못함 — **[미확인]**.

- **참여연대 등 비판.** 790조원 기후금융이 "산업 지원 금융으로 전락할 우려"가 있다는 시민단체 비판 존재(내용 상세는 미확인, 제목만 확인).
  [한국NGO신문, "참여연대 '금융위원회 790조 원 규모 기후금융, 산업 지원 금융 전락 우려'" | https://www.ngonews.kr/news/articleView.html?idxno=225528]

**한국 정부가 실제로 다루는 부분:** 몸통(무상할당, 정책금융 대출·보증 총량). **다루지 않는 부분:** 하방 좌초 꼬리(CCfD 미가동), 상방 비용폭발 꼬리(전용 보증상품 확인 안 됨) — 즉 분포의 양쪽 꼬리 모두 설계 공백 상태이고, 이 공백을 메우려는 시도가 지금 법제화 중인 CCfD.

### 일본

- **GX-ETS 밴드(하한 1,700엔·상한 4,300엔/tCO2, 2026회계연도~).** 위 "가격하한·밴드·보증" 절 참조. 하방·상방 꼬리를 시장 전체 수준에서 동시 절단하는, 한국에는 없는 수단.
  [ICAP; METI/UNFCCC — 위 인용 동일]

- **GX 경제이행채(GX Economic Transition Bonds), 약 20조엔.** 2023년 GX추진법 제정 후 향후 10년간 150조엔 규모의 민관 GX 투자를 유도하기 위한 마중물로 약 20조엔 규모의 국채 발행. 2024년 2월 첫 발행(1.6조엔), "세계 최초의 국가 주도 전환국채(sovereign transition bond)".
  [METI, "Japan Climate Transition Bond Framework" (2023, 2025 개정) | https://www.meti.go.jp/policy/energy_environment/global_warming/climate_transition_bond_framework_en.pdf]
  [JapanGov, "Climate Transition Bonds Show Japan's Commitment to Carbon Neutrality" | https://www.japan.go.jp/kizuna/2024/09/climate_transition_bonds.html]

- **METI 부문별 전환금융 기술로드맵.** 철강·화학·전력·가스/석유·시멘트·제지펄프·자동차 등 8개 부문(일본 CO2 배출의 약 80% 커버)에 대해 2050 탄소중립까지의 기술 경로를 제시하는 로드맵을 2021~2023년 순차 발표. 철강은 수소환원·CCUS로 2030년까지 고로 배출 약 30% 감축, 2050 탄소중립 목표.
  [METI, "Technology Roadmap for 'Transition Finance' in Iron and Steel Sector" | https://www.meti.go.jp/policy/energy_environment/global_warming/transition/transition_finance_technology_roadmap_iron_and_steel_eng.pdf]
  [METI, "Technology Roadmap ... Chemical Sector" (2021.12) | https://www.meti.go.jp/policy/energy_environment/global_warming/transition/transition_finance_technology_roadmap_chemistry_eng.pdf]

  → 로드맵 자체는 페이오프 구조가 아니라 "어떤 기술이 어느 시점에 필요한가"를 정하는 정보재(information good)이며, GX 국채는 그 로드맵을 따르는 프로젝트에 자금(주로 채권 조달)을 붙이는 몸통형 수단. 국채 자금이 분포의 꼬리를 자르는지(예: 국채 보증·매입 프로그램이 하방 손실을 흡수하는지)는 본 검색에서 확인 못함 — **[미확인]**.

**일본 정부가 실제로 다루는 부분:** 몸통(GX 국채, 로드맵)과 시장 전체 수준의 양쪽 꼬리(GX-ETS 밴드). 프로젝트 단위 CCfD형 수단은 일본에서 확인되지 않음(있다면 [미확인]으로 별도 조사 필요).

---

## CBAM (외부 정부)

EU CBAM(2026.1.1 정식 시행)은 EU 역내 생산자가 부담하는 ETS 비용을 수입품에도 반영해 탄소누출을 막고 EU 산업 경쟁력을 보호하려는 장치. 철강·시멘트·비료·알루미늄·전력·수소 등을 대상으로 하며, 고위험 업종에 대한 무상할당을 CBAM으로 대체해 나가는 설계.
[European Commission, "Carbon Border Adjustment Mechanism (CBAM)" | https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en]
[OECD, "EU Carbon Border Adjustment Mechanism: What is it, how does it work and what are the effects?" (2025) | https://www.oecd.org/en/blogs/2025/03/eu-carbon-border-adjustment-mechanism-what-is-it-how-does-it-work-and-what-are-the-effects.html]

CBAM은 EU 정부가 자국 산업을 위해 설계한 수단이지만, 한·일 수출기업 입장에서는 **자신의 정부가 아니라 EU라는 외부 정부가 자신들이 속한 분포를 바꾸는** 사례다: 전환하지 않은(저탄소화 안 된) 기업은 EU 시장접근 비용이 올라가는 방식으로 상방 비용 꼬리가 새로 생기고, 이는 한국·일본 정부의 CCfD·보증·로드맵과 무관하게 외부에서 부과된다. 인도·러시아·튀르키예 등이 수출경쟁력 타격이 크다는 연구가 있으며, CBAM 비대상 다운스트림 업종·EU 역내 고탄소 수출업조차 경쟁력 손실 우려가 제기됨.
[OECD (2025), 상동]

→ 한국·일본의 철강 등 대EU 수출업종에는 이 CBAM이 사실상 "제3의 정부 수단"으로 작용 — 국내 CCfD·보증·로드맵과 별도로 분포의 상방 꼬리(시장접근 상실) 일부를 이미 외부에서 자르고 있다는 것이 여기서 확인되는 사실. 정량적으로 한·일 개별 기업의 CBAM 노출액을 다룬 논문은 이번 검색에서 확인하지 못함 — **[미확인]**.

---

## 미확인

1. ECA 보증 상품이 EPC 계약의 "비용초과(cost overrun)"를 표준적으로 직접 커버하는지 — 실무 문헌은 주로 대출 원리금 상환 리스크를 다루며, 비용초과 자체를 커버하는 상품 구조에 대한 학술 근거는 찾지 못함.
2. "Designing carbon contracts for difference under asymmetric information" (ScienceDirect, S0165176525004367) — 저자·발행연도·핵심 결과를 페이월로 인해 확인하지 못함. 제목만 확인.
3. 한국 790조원 기후금융 중 개별 정책금융 상품(대출/보증/출자)별 페이오프 구조 — 꼬리를 자르는지 수준을 이동시키는지 상품 단위로 확인하지 못함.
4. 일본 GX 국채 자금이 실제로 손실 흡수(보증·매입) 기능을 갖는지, 아니면 순수 조달 채널인지 — 확인하지 못함.
5. CBAM이 한국·일본 개별 기업(특히 철강)에 미치는 정량적 노출액을 다룬 학술 논문 — 이번 검색 범위에서 찾지 못함(뉴스/정책분석 수준만 확인).
6. 참여연대 등 시민단체의 790조원 기후금융 비판 상세 내용 — 기사 제목만 확인, 본문 미독.
7. 가격하한을 "풋옵션과 동일한 페이오프"로 보는 비유는 옵션이론의 일반적 서술이며, 이를 명시적으로 CCfD/가격하한 맥락에서 정식화한 특정 학술 서지는 확인하지 못함.

---

# SYNTHESIS L5 (정부 헤지) — 2026-09-13 · 세 주체 종합

## 수단↔분포 매핑 완성 (세 주체 통합)
| 층 | 주체 | 수단 | 자르는 부분 |
|---|---|---|---|
| 몸통 | 기업 | corporate 그린본드·자본예산 | 정상 전환 capex |
| 몸통 | 정부 | 보조금·무상할당(K-ETS)·정책금융 | 수준 이동(꼬리 안 자름) |
| 상방(비용 폭발) | 기업 | EPC/GMP 캡·PPA·오프테이크 | 부분(h*<1, Stegra 불완전) |
| 상방 | 투자자 | 채권 신용 스프레드(꼬리 아닌 신용) | 발행자 신용 |
| 상방 | 정부 | 보증·ECA | 신용 꼬리(EPC 초과 직접커버는 미확인) |
| 하방(좌초) | 정부 | CCfD(양방향)·가격하한·밴드 | 하방 좌초 꼬리 정밀 절단 |
| 상방(시장접근) | 외부 정부(EU) | CBAM | 무전환 기업 시장접근 |

## 세 개의 정직한 결론
1. **자기 위험 재보험의 뒤집힌 도덕적 해이.** CCfD는 보험자(정부)가 보험사고(탄소가 하락)를 일으킬
   정책 레버를 쥔다 — 통상 도덕적 해이(가입자가 위험 키움)의 역. Kydland-Prescott 시간불일치와
   동형. 캐나다 CCfD 재정위험 논쟁 실재.
2. **Arrow-Lind 안 걸림.** catastrophe 층은 정책이 만든 체계·내생 위험이라 총소비 독립 아님 →
   "정부가 지면 싸다" 논거 적용 불가(Mechler-Hochrainer 주권 재난위험). 위험 이전은 사회적 이득이
   아니라 **회계적 재배치**(Wolf 2025).
3. **CAP은 처방이 아니라 조건부 기술.** 줄 수 있는 것=위험 이전의 회계(이 층 크기 X, 정부 흡수 시
   재정부담 Y). 줄 수 없는 것=사회적 최적 판단. "catastrophe 층 크기는 정책 신뢰성의 함수"라는
   조건부 서술. 사회후생 극대화 주장 금지.

## 한·일 케이스의 결정적 발견 (무게중심)
- **한국 = 꼬리 무주공산.** 기업 corporate 그린본드로 통째로(L4) + 정부 몸통만(무상할당·790조) +
  양쪽 꼬리 아무도 안 자름(CCfD 미가동·법제화 착수, 보증 미확인). **분포의 꼬리가 비어 있다.**
- **일본 = 양쪽 꼬리(GX-ETS 밴드) + 몸통(GX 국채) 다 다룸.** 정부가 발행자로 탄소 붕괴 위험 내재화.
- 이게 Wolf 2025 유럽이 못 보는 한·일 대비. **정책 함의 핵심**: 한국은 전환비용 분포의 꼬리를
  누가 질지가 제도적으로 미정 — 그 공백 자체가 CAP이 보여줄 것.

## 직전(L1~L4) 비판적 재검토
L4의 두 긴장(정부가 mezzanine까지·자기 재보험)이 L5에서 정직한 형태를 얻었다 — 층 경계는 이론에서
연역 안 되고(최적 first-loss 정설 없음, Deleidi crowding 엇갈림), CAP은 분포 형태만 보여주고 규범은
분리. 지난 9루프 감사(cap-audit)의 "정부가 낼 값이라 쓰지 말 것"이 여기서 문헌으로 재확인 —
π는 위험 이전 회계이지 사회적 가치 아님.

## L6으로 (세 주체 상호작용)
세 주체가 분포의 어느 층을 지는지 다 그렸다. L6은 그 경계가 어떻게 움직이나(제도 성숙도)·누가 어느
꼬리를 지는 게 실제 한·일에서 어떻게 갈리나·layering의 빈 칸(한국 꼬리)을 정식화.
