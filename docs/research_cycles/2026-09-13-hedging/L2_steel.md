# L2 — 철강 원료(feedstock) 위험 문헌 종합

**작업일**: 2026-09-13
**선행**: L1 (전환 전기 조달) — 핵심 통찰 "위험이 가격형(변동성)인가 접근형(확보 가능성·시점)인가"를 원료에 적용
**방법**: WebSearch/WebFetch 실제 확인. 추측 서지 없음. 본문 확인 못한 문헌은 "미확인"에 별도 표시.

---

## 원료탄·철광석 가격 위험

**가격 발견 체제 자체가 2010년 이후 근본적으로 바뀌었다.** 2010년 이전 원료탄(coking/metallurgical coal)은 연간 고정계약(annual benchmark)으로 거래되었으나, 2010년 호주 홍수로 공급이 타격을 입으면서 분기별 벤치마크로, 이후 점점 더 많은 물량이 일별 현물지수(S&P Global Platts PLV, 2010년 10월 출시)에 연동되는 방식으로 이행했다. 철광석도 마찬가지로 연 단위 고정계약에서 2008년 Platts IODEX 일별 현물지수 출시 이후 사실상 일일 가격결정 체제로 전환되었다.
[Is coking coal pricing moving away from quarterly benchmarks?, MINING.COM | https://www.mining.com/coking-coal-pricing-moving-away-quarterly-benchmarks/]
[Platts Premium Low Vol Coking Coal Prices methodology, S&P Global | https://www.spglobal.com/commodityinsights/en/our-methodology/price-assessments/metals/premium-low-vol-coking-coal-metals-prices]

**변동성 규모.** 원료탄은 2011년 중반 톤당 330달러까지 급등했고, 2010년 9월~2012년 9월 2년간 200달러를 상회했다. 최근 학술 연구(2011~2024년 일별 현물가 기반 VaR 비교)는 철광석은 상대적으로 안정적 모델링이 가능하지만("Historical Simulation VaR가 고신뢰수준에서 비교적 신뢰할 만한 예측 제공"), 원료탄 시장은 99% 신뢰수준에서 어떤 모델도 일관된 정확도를 달성하지 못했고 "뚜렷한 팻테일 리스크와 변동성 군집(volatility clustering)"이 나타난다고 밝혔다.
[Comparative performance of value at risk models in iron ore and coking coal markets, International Journal of System Assurance Engineering and Management | https://link.springer.com/article/10.1007/s13198-026-03357-y]
[Coking coal price crashes through $100 / 2년간 $200 상회 이력, MINING.COM | https://www.mining.com/chart-coking-coal-surge-kill-quarterly-pricing]

**헤지 관행.** 철강사는 (i) 생산자와의 장기계약(pre-negotiated rate)을 통한 물리적 헤지, (ii) 원료탄 선물계약(매수·매도 의무 확정)을 통한 금융적 헤지 두 경로를 모두 사용한다. "철광석 가격 변동성은 장기계약으로 완화될 수 있다"는 서술이 확인되나, 이는 일반론 수준이며 헷지 비율·프리미엄 규모를 정량화한 학술 출처는 이번 검색에서 확인하지 못했다(미확인 항목 참조).
[The Critical Impact of Coking Coal Pricing on Steel Industry Profitability, Shanghai Metals Market | https://news.metal.com/newscontent/102965137]

**전환이 이 노출을 없애는가.** 고로(BF-BOF) 폐쇄는 원료탄 노출을 소멸시킨다 — 원료탄은 코크스 제조에만 쓰이므로 H₂-DRI 또는 스크랩-EAF 경로에는 원료탄 수요 자체가 없다. 그러나 철광석 노출은 소멸하지 않고 **형태를 바꿔 이전**된다: 고로용 저품위(Fe~62%) 소결광/괴광 노출이 H₂-DRI용 고품위(Fe>67%) DR급 펠릿 노출로 대체된다. 이 대체가 이번 문헌 종합의 핵심 — 다음 절에서 다룬다.

---

## DR급 펠릿 희소성 (접근형 위험)

**핵심 사실: DR급(Fe≥67%) 펠릿은 현재 전 세계 철광석 공급의 약 4%에 불과하다.** 미드렉스(Midrex) 발표 자료(2018년 국제철금속협회 Chris Barrington)는 "DR급 철광석 펠릿 공급은 언제나 타이트했다"고 명시하며, 남미(Vale, Samarco), 북미(Rio Tinto IOC, ArcelorMittal), 유럽(LKAB), 중동(이란, 바레인) 4대 생산권역과 각 지역 생산능력(캐나다 합산 ~22.7Mt/y, 스웨덴 LKAB ~26Mt/y 실효용량 중 수출 ~7Mt/y, 이란 31Mt/y이나 대부분 내수 소비)을 제시한다.
[DR-Grade Iron Ore Pellets: A Supply Overview, Chris Barrington (IIMA Fellow), Midrex Technologies, 2018 | https://www.midrex.com/tech-article/dr-grade-iron-ore-pellets-a-supply-overview/]

**공급-수요 격차 전망.** Vale는 2020년 기준 해상 물동량(seaborne supply) 중 Fe 66% 이상 비중이 약 3%에 불과했고, 2030년까지도 이 비중이 "largely unchanged"할 것으로 전망한다고 밝혔다 — 즉 채굴·정광(beneficiation) 능력 자체가 단기간에 늘지 않는다는 공급측 경직성이 핵심이다. 국제철금속협회(IIMA)는 기존 펠릿 생산자의 가동률이 완전 소진되면서 DR급 펠릿 공급에 "상당한 부족(significant shortfall)"이 발생할 것으로 분석하며, IEA 지속가능발전 시나리오상 2050년 DRI 수요 411Mt 기준으로는 잠재 펠릿 수요가 2019년 전 세계 펠릿 생산량(463Mt)을 초과할 수 있다고 지적한다.
[Global DRI push to be crimped by lack of pellet feed concentrate, Fastmarkets | https://www.fastmarkets.com/insights/global-dri-push-to-be-crimped-by-lack-of-pellet-feed-concentrate/]

**IEEFA는 이를 명시적으로 "가격이 아니라 물량/품질 제약"으로 프레이밍한다.** IEEFA 보고서(2022)는 "고품위(Fe>67.0%) 철광석의 희소성이 가스기반 DR-EAF 공정 발전을 가로막는 결정적 제약(pivotal constraint)으로 부상했다"고 서술하며, Vale는 정광 공정(beneficiation)의 난이도와 고품위 매장량 고갈을 공급 확대가 어려운 이유로 든다. IEEFA는 동시에 "일부 화석연료 기반 제철 기득권 진영이 이 희소성을 근거로 DRI 기반 저탄소 전환의 한계를 주장한다"는 점도 지적 — 즉 이 병목이 정치적으로도 쟁점화되어 있다.
[Solving Iron Ore Quality Issues for Low-Carbon Steel, IEEFA, 2022 (PDF) | https://ieefa.org/sites/default/files/2022-08/Solving%20Iron%20Ore%20Quality%20Issues%20for%20Low-Carbon%20Steel_0.pdf]
[Green steelmaking will need technology and mining advances, IEEFA | https://ieefa.org/resources/green-steelmaking-will-need-technology-and-mining-advances]

**기술적 우회 경로도 존재한다** — Tenova의 open slag bath furnace(OSBF)는 저품위 고로용 펠릿으로도 DRI를 만드는 용융 공정을 개발 중이며, 여러 업체가 철광석 미분(fines)을 그대로 사용해 펠릿화(pelletisation) 자체를 생략하는 유동층 환원(fluidised bed reduction) 공정을 개발 중이다. 이는 "접근형 위험이 기술로 완전히 해소될 수 있는가"라는 반론 축으로, 우리 분포 모형에서 시나리오 분기 요소가 될 수 있다.
[Solving iron ore quality issues for low-carbon steel, IEEFA | https://ieefa.org/resources/solving-iron-ore-quality-issues-low-carbon-steel]

**공급측 대응: Vale의 메가허브 전략.** Vale는 2030년까지 DR급 철광석 공급 부족을 연 7,000만 톤(70Mtpa) 규모로 전망하고, 이를 메우기 위해 오만·사우디아라비아·UAE에 "메가허브(Mega Hub)"를 구축 중이다. 2026년 1월 사우디 라스알카이르 산업단지에 토지사용 계약을 체결했고, 이 시설은 연 1,200만 톤(12Mt)의 냉간성형철(CBI, cold briquetted iron)을 생산할 계획이다. Rio Tinto와 Fortescue도 아프리카에서 고품위 광산 프로젝트를 추진 중이며, Fortescue는 필바라의 Iron Bridge에서 이미 DR급 기준을 충족하는 생산을 시작했다.
[Big iron ore's long-term strategies diverging in the face of steel decarbonisation, IEEFA | https://ieefa.org/resources/big-iron-ores-long-term-strategies-diverging-face-steel-decarbonisation]
[Australia faces growing green iron competition from overseas, IEEFA, 2023 (PDF) | https://ieefa.org/sites/default/files/2023-08/Australia%20faces%20growing%20green%20iron%20competition%20from%20overseas_Sep23.pdf]

**Fe>67% 요구조건 자체는 야금학 문헌에서 재확인된다.** ScienceDirect에 실린 최근 연구는 Fe 함량 59~68% 범위 펠릿의 수소 환원 거동을 실험적으로 비교하며, 저품위 펠릿일수록 환원 효율·에너지 소비 측면에서 불리함을 정량화한다 — 즉 "DR급 요구조건은 임의적 산업 관행이 아니라 공정 열역학·경제성에 근거한 제약"임을 뒷받침한다.
[Hydrogen-based direct reduction behavior of iron ore pellets with iron grades ranging from 59% to 68%, ScienceDirect | https://www.sciencedirect.com/science/article/abs/pii/S0360319925016167]

**First-mover 계약 선점 사례 → 다음 "실증·사례" 절에서 Stegra·LKAB 상술.**

---

## 스크랩·HBI 위험

**수급 반전이 향후 5년 내 발생한다.** BCG(2024년 3월, Lee·Voigt·Feth·Chhibbar)는 스크랩 수요 CAGR 약 3.3% vs 공급 CAGR 약 3.0%로, "2030년까지 현재의 900만 톤 흑자가 1,500만 톤 적자로 전환"된다고 추정한다. 특히 고품질(prime) 스크랩은 2030년까지 최대 3,000만 톤 부족이 예상되는데, 이는 제조업체가 점점 더 깨끗한 원료를 요구하기 때문이다. 전 세계 스크랩 무역량은 연 1억1,000만 톤에서 2030년 약 9,300만 톤으로(~15% 감소) 축소될 전망이며, 캐나다의 대미 프라임 스크랩 수출은 50% 급감, 유럽 수출은 약 1/4 감소가 예상된다.
[Shortfalls in Scrap Will Challenge the Steel Industry, BCG, 2024-03-12, Lee/Voigt/Feth/Chhibbar | https://www.bcg.com/publications/2024/shortfalls-in-scrap-will-challenge-steel-industry]

**유럽 관점에서도 동일한 구조.** Roland Berger(2025-07-15)는 EU-27 유럽 EAF 비중이 1990년 ~30%→2024년 ~45%로 상승했고, 1990년 이래 철강 수요가 스크랩 가용성보다 연 0.4%p 더 빠르게 증가해왔다고 지적한다. 유럽은 2030년까지 순수출국에서 약 300만 톤 규모의 순수입국으로 전환될 전망이다. 대응으로 Cleveland-Cliffs의 Ferrous Processing and Trading 인수(7.75억 달러), Steel Dynamics의 멕시코 Roca Acero 인수, ArcelorMittal·Salzgitter의 유럽 내 스크랩 처리시설 인수 등 "수직계열화를 통한 선제적 확보(first-mover)" 사례가 이미 진행 중이다. 보고서는 "지금 스크랩 공급망을 선제적으로 확보하는 기업이 비용구조·제품역량·지속가능성 신뢰도에서 상당한 우위를 가질 것"이라고 명시한다.
[The growing battle for scrap steel in green steel production, Roland Berger, 2025-07-15 | https://www.rolandberger.com/en/Insights/Publications/The-growing-battle-for-scrap-steel-in-green-steel-production.html]

**품질(tramp element) 제약은 무역/공급 위험과 별개 축이다.** 구리(copper)는 스크랩 오염원 중 가장 문제적인 원소로 지목되며, 자동차 배선·전자폐기물(WEEE)·철거폐기물이 주 오염원이다. 0.1wt% 초과 시 열간 균열(hot shortness)을 유발해 자동차용 고급 강판 등 고품질 용도에 부적합해진다. 국제 비교연구(Panasiuk et al. 2022, Journal of Industrial Ecology)는 중국·일본·베트남·우크라이나·네덜란드 5개국 500여 개 EAF 철근 샘플을 분석해, 일본에서는 구리 축적의 2/3가 불충분한 스크랩 분리에서, 1/3이 합금원소에서 기인함을 밝혔다. 동 연구는 EU에서 저품질 스크랩 잉여 증가로 2050년까지 사용 가능한 스크랩 비중이 55%로 제약될 것이라 전망한다 — 이는 신철(virgin steel) 희석이나 저품질 스크랩 수출이 불가피해짐을 뜻한다.
[International comparison of impurities mixing and accumulation in steel scrap, Panasiuk et al., Journal of Industrial Ecology, 2022 | https://onlinelibrary.wiley.com/doi/10.1111/jiec.13246]

Nakajima et al.(2017, *Environmental Science & Technology*, "How Will Copper Contamination Constrain Future Global Steel Recycling?")는 2008년 철강 공급사슬 데이터와 글로벌 재고-포화(stock-saturation) 모형을 이용해 전 세계 스크랩 구리 함량이 언제 허용한도를 넘어설지 추정했다는 점은 검색 결과로 확인되나, 구체적인 임계 연도·수치는 초록/요약 수준에서 확보하지 못했다(미확인 표시).
[How Will Copper Contamination Constrain Future Global Steel Recycling?, Nakajima et al., Environmental Science & Technology, 2017 | https://pubs.acs.org/doi/10.1021/acs.est.7b00997]

**HBI는 스크랩의 보완재이자 "희석제(diluent)" 역할을 한다.** HBI는 DRI를 650°C 이상에서 압축해 밀도 5,000kg/m³ 이상으로 만든 제품으로, 일관된 품질과 낮은 불순물 덕에 "변동성 높은 스크랩 시장에 대한 의존도를 낮추는" 스크랩 대체재로 부상하고 있다. 시장 조사에 따르면 주요 철강사들의 고급 원료 수요가 EAF 전환과 스크랩 품질 문제로 18~22% 증가했으며, 유럽이 세계 HBI 생산의 약 49%를 차지(Metalloinvest·Voestalpine·Cleveland-Cliffs 상위 3사가 약 72% 점유)한다. 즉 HBI는 저품위 스크랩을 구리 등 불순물 없는 물량으로 "희석"해 최종 강재의 tramp element 농도를 규격 이내로 관리하는 용도로 쓰인다 — 스크랩 순환자원의 물리적 품질 제약을 HBI(신규 생산 원료)가 보완하는 구조.
[Hot Briquetted Iron (HBI) Market Size & Insights Report, Business Research Insights / 시장조사 종합 | https://www.businessresearchinsights.com/market-reports/hot-briquetted-iron-hbi-market-117785]

**EU 스크랩 수출 통제는 실제로 진행 중이며 정책 방향이 유동적이다.** EU 집행위는 2025년 7월 23일부로 철·비철 스크랩 수출입에 대한 세관 감시(customs surveillance) 체계를 가동해 물동량을 추적 중이며, 이 데이터가 내년(2027년) 공식 평가로 이어져 수출관세·수출허가제·재생원료 함량 의무화 중 정책 옵션이 결정될 예정이다. 2024년 3월 EU 이사회가 채택한 폐기물 이송 규정(Waste Shipment Regulation) 개정안은 비OECD국으로의 비유해 폐기물(스크랩 포함) 수출을 제한하며 2027년 5월 21일부터 발효된다. 2024년 EU는 제3국에 1,670만 톤의 철스크랩을 수출했다 — 이 규제가 시행되면 이 물량의 상당 부분이 역내로 재배치되거나 차단될 수 있다.
[Commission introduces surveillance of imports and exports of metal scrap, European Commission, 2025-07-23 | https://taxation-customs.ec.europa.eu/news/commission-introduces-surveillance-imports-and-exports-metal-scrap-2025-07-23_en]
[48 countries have already restricted scrap exports, GMK Center, 2025 | https://gmk.center/en/infographic/48-countries-have-already-restricted-scrap-exports/]
[10 Key Takeaways of the European Steel and Metals Action Plan, Mayer Brown, 2025-03 | https://www.mayerbrown.com/en/insights/publications/2025/03/10-key-takeaways-of-the-european-steel-and-metals-action-plan]

---

## 전환에 따른 원료 위험 재편

전환은 원료 위험을 **없애는 것이 아니라 재배치**한다. 고로 폐쇄로 원료탄 노출은 소멸하지만, 그 자리에 최소 세 가지 새로운 노출이 들어선다:

1. **DR급 펠릿 접근 위험** — 채굴·정광 능력이 단기간에 늘지 않는 물리적 병목(글로벌 공급의 4%, Vale 전망상 2030년까지도 고품위 비중 불변). 가격을 아무리 지불해도 물량 자체가 없을 수 있다는 점에서 **접근형(access-type)**.
2. **스크랩/HBI 가격·품질 위험** — 스크랩은 가격 변동성(공급-수요 반전, 2030년 1,500만 톤 적자)과 품질 열화(구리 등 tramp element 축적, 2050년 EU 가용 스크랩 55%로 제약)라는 이중 위험을 가진다. HBI는 품질 위험을 완화하지만 그 자체가 별도 원료시장(전 세계 생산의 49%가 유럽 집중)으로 새로운 지리적 집중 위험을 도입한다.
3. **수소** — L3에서 별도로 다룰 노출(전력 대비 별개의 계약·인프라 구조를 가짐).

**계약으로 헤지 가능한 것과 접근형이라 조기 확보만이 답인 것의 구분이 핵심이다.**
- 스크랩 **가격**은 지수·선물 유사 메커니즘(Platts/Fastmarkets 스크랩 지수 등)으로 부분적으로 헤지 가능한 가격형 위험에 가깝다 — 원료탄과 유사하게 시장이 두텁고 가격발견이 기능한다.
- 스크랩 **품질**(tramp element 규격)은 계약으로 사후 조정 불가능하다 — 사실 시장에서 구리를 상업적으로 제거할 기술이 없으므로("cannot currently be removed commercially once in the melt"), 이는 사전에 저오염 스크랩/HBI를 물리적으로 확보하는 것 외에 대안이 없는 접근형 위험이다.
- **DR급 펠릿**은 정의상 접근형이다 — Stegra·SSAB 사례(다음 절)가 보여주듯, 장기 오프테이크 계약도 "가격을 정하는 계약"이 아니라 "물량을 배정받는 계약"으로 기능한다. LKAB가 애초 철도(Malmbanan) 용량 제약을 이유로 Stegra에 판매를 거부했다가 이후 합의한 사례는, 이 위험이 가격 협상이 아니라 **물리적 배분(rationing)**의 문제임을 직접 보여준다.
[LKAB and Stegra plan for test deliveries of iron ore pellets, Stegra, 2025 | https://stegra.com/en/news-and-stories/lkab-stegra-plan-test-deliveries-iron-ore-pellets]

---

## 가격형 vs 접근형 판정 (표)

| 원료 노출 | 위험 성격 | 근거 | 계약으로 헤지 가능한가 |
|---|---|---|---|
| 원료탄(코크스용) | 가격형 (전환 시 소멸) | 2010년 이후 지수화·팻테일 변동성(연구: 99% VaR 모델 전부 실패) | 선물·장기계약으로 부분 헤지, 전환 후엔 노출 자체가 사라짐 |
| 고로용 철광석(Fe~62%) | 가격형 (전환 시 소멸) | 일별 현물지수(IODEX) 체제, 장기계약으로 변동성 완화 가능 | 예 — 시장이 두텁고 유동적 |
| DR급 펠릿(Fe>67%) | **접근형** | 세계 공급의 4%, Vale 전망상 2030년까지 고품위 비중 불변, "always tight"(Midrex) | 제한적 — 장기 오프테이크는 "물량 배정" 성격, LKAB-Stegra처럼 인프라(철도) 제약까지 얽힘 |
| 스크랩 가격 | 가격형 | 지수 시장 존재, BCG/Roland Berger의 수급 전망 정량화 가능 | 부분적 — 지수 연동·선매입 |
| 스크랩 품질(tramp element) | **접근형** | 구리 등 상업적 제거 기술 부재, 2050년 EU 가용 스크랩 55%로 제약(축적성·비가역) | 아니오 — 저오염 스크랩 물리적 선점(수직계열화, M&A)만이 답 |
| HBI | 혼합형 (가격형 원료 + 접근형 완충재) | 생산이 유럽 49% 집중, 수요 18~22% 증가 | 부분적 — 시장 존재하나 지리적 집중 위험 |
| 수소(별도) | L3에서 판정 | — | — |

---

## 분포에 반영할 함의

1. **DR급 펠릿과 스크랩 품질은 현재 CAP의 "결정론적 원료 가격 경로" 가정과 구조적으로 맞지 않는다.** 이 둘은 가격 분포가 아니라 **물량 배분 실패 확률**(원하는 시점에 원하는 물량을 확보하지 못할 확률)로 모형화해야 한다 — L1에서 전력 PPA에 적용한 "접근형 위험은 확률적 물량 제약, 가격형 위험은 확률적 가격 분포"라는 이분법이 원료에도 그대로 적용된다.
2. **선점(first-mover) 효과는 분포의 비대칭성을 만든다.** Stegra·Vale 메가허브·Cleveland-Cliffs식 수직계열화 사례는 "일찍 계약한 기업은 물량을 확보하고, 늦은 기업은 물량 자체가 없는" 이산적(discrete) 결과를 시사한다 — 연속분포보다 임계치(threshold)/배급(rationing) 구조가 더 적합할 수 있다.
3. **스크랩 가격과 품질을 분리해서 모형화해야 한다.** 현재처럼 스크랩을 단일 가격 변수로 두면 품질 열화로 인한 "저품질 스크랩만 남고 고품질은 고갈"되는 시장 분리(prime vs obsolete scrap) 효과를 놓친다. BCG의 프라임 스크랩 3,000만 톤 적자 전망은 CAP가 스크랩을 등급별로 분리해야 함을 시사한다.
4. **HBI를 별도 노출 축으로 추가할지 검토가 필요하다.** 현재 모형에 HBI가 없다면, 스크랩 품질 위험을 헤지하는 유일한 실질적 수단이 누락된 것이다 — 다만 HBI 자체가 유럽 집중형 공급망이라는 점에서 이를 추가하면 새로운 지리적 상관관계 변수가 필요해진다(ponytail 관점: 필요성이 확인되기 전엔 추가하지 않는다 — 우선 원료탄→DR펠릿, 스크랩 가격→스크랩 품질의 두 축 분리부터).
5. **원료탄 노출 소멸은 무조건적 리스크 축소가 아니다.** 원료탄(가격형, 헤지 가능)이 DR급 펠릿(접근형, 헤지 어려움)으로 대체되는 것은 "변동성 감소, 꼬리위험 유형 변화"로 봐야 한다 — F3(비등가 감축) 문제와 유사하게, 감축 후 남는 위험의 통계적 성질이 감축 전과 다르다는 점을 분포 생성기에 반영해야 한다.

---

## 실증·사례 (본문 통합)

- **Stegra(구 H2 Green Steel) × LKAB**: 2025년 5월 시험 배송 합의, 2026년 말 철도 인프라 완공 후 본 배송 예정. LKAB는 애초 Malmbanan 철도 용량 제약을 이유로 Stegra에 판매를 거부했다가 이후 합의로 전환 — 원료 확보가 가격 협상이 아니라 물리적 인프라 배분 문제임을 보여주는 직접 사례.
  [LKAB and Stegra plan for test deliveries of iron ore pellets, Global Hydrogen Review, 2025-05-14 | https://www.globalhydrogenreview.com/hydrogen/14052025/lkab-and-stegra-plan-for-test-deliveries-of-iron-ore-pellets/]
- **Vale 메가허브(오만·사우디·UAE)**: DR급 광석 부족(2030년까지 70Mtpa 전망)에 대응해 정광·응집(agglomerate) 생산을 DRI 플랜트와 공동 입지시키는 전략. 2026년 1월 사우디 라스알카이르에 12Mt/y CBI 생산시설 토지사용 계약 체결.
  [Big iron ore's long-term strategies diverging in the face of steel decarbonisation, IEEFA | https://ieefa.org/resources/big-iron-ores-long-term-strategies-diverging-face-steel-decarbonisation]
- **Fortescue Iron Bridge(호주 필바라)**: 이미 DR급 기준을 충족하는 생산 개시 — 호주 철광석사 중 유일하게 상업적 DR급 생산을 실현한 사례로 언급됨.
  [Australia faces growing green iron competition from overseas, IEEFA, 2023 | https://ieefa.org/resources/australia-faces-growing-green-iron-competition-overseas]
- **스크랩 수직계열화**: Cleveland-Cliffs의 Ferrous Processing and Trading 인수(7.75억 달러), Steel Dynamics의 Roca Acero(멕시코) 인수, ArcelorMittal의 스코틀랜드·독일·네덜란드·폴란드 스크랩 처리시설 인수, Salzgitter의 Must Metalle Container Recycling 인수 — 모두 2023~2025년 사이 발표.
  [The growing battle for scrap steel in green steel production, Roland Berger, 2025-07-15]

---

## 미확인

- 원료탄·철광석 장기계약의 **헤지 비율(hedge ratio)**이나 프리미엄 규모를 정량화한 학술 논문(SSRN/저널)은 이번 검색에서 찾지 못했다. "장기계약이 변동성을 완화한다"는 서술은 업계 보도(Shanghai Metals Market) 수준에 그친다 — 계량경제 추정치가 필요하면 추가 검색 필요.
- **Agora Industry 보고서(파일명 abb-25.pdf)**: 검색 결과 제목("How the bottleneck of DR-grade pellets can be addressed")만 확인, WebFetch로는 PDF 본문(Illustrator 메타데이터만 반환)을 확보하지 못했다. 로컬에 바이너리는 저장됨(`/Users/jinsu/.claude/projects/-Users-jinsu-Documents-GitHub-cap-finance/8d5dbe72-d444-4a6a-be60-89cd7807ac49/tool-results/webfetch-1789265894916-q9v8ec.pdf`) — 필요시 PDF 텍스트 추출 도구로 재확인 요망.
- **Nakajima et al. (2017, ES&T)**의 "전 세계 스크랩 구리 함량이 한도를 초과하는 시점" 구체 연도·수치는 초록 수준에서 확인되지 않음 — 원문 확인 필요.
- **IEEFA "Solving Iron Ore Quality Issues for Low-Carbon Steel" 웹페이지 버전**은 403으로 접근 차단됨(PDF 버전은 검색 스니펫으로만 확인). 저자명 미확인.
- **DR급 펠릿 first-mover 장기계약이 가격 프리미엄을 정량적으로 어떻게 반영하는지**(예: Stegra-LKAB 계약가 구조)는 상업적 비밀정보로 공개되지 않은 것으로 보이며, 본 검색에서 수치를 확인하지 못했다.
- 중동 DRI 허브(이란·사우디 외 개별 프로젝트 규모·가동 시점)에 대한 세부 수치는 이번 라운드에서 깊이 파지 못했다 — 필요시 후속 검색 대상.

---

# SYNTHESIS L2 (원료) — 2026-09-13

## 한 발견: 전환은 위험의 개수가 아니라 종류를 바꾼다
L1은 "전환이 연료 위험 하나를 셋으로 분해한다"고 했다. L2가 더한다 — **분해된 위험의 종류가
가격형에서 접근형으로 바뀐다.** 원료탄·철광석은 가격형(팻테일이지만 선물·장기계약으로 헤지 가능).
전환은 이를 소멸시키고 **DR급 펠릿(세계 공급 4%, 배급 성격)·스크랩 품질(구리 축적 비가역)**이라는
접근형 위험으로 대체한다. LKAB가 철도 용량 때문에 Stegra 판매를 처음 거부한 것이 증거 — 가격
협상이 아니라 물리적 배분.

## 조기 전환 논리의 첫 실증
접근형 위험은 **선점으로만 확보**된다(계약가로 못 산다). 그래서 조기 전환 = DR펠릿·스크랩·재생 PPA
물량의 선점 = 헤지. 이것이 사용자 원 직관("조기 전환이 대비")이 문헌으로 서는 자리다 — 단
**가격형이 아니라 접근형 위험에서만.** 가격형 위험은 전환 안 해도 계약으로 헤지되므로 조기 전환의
근거가 아니다. (L5 희소성·L7 실물옵션이 이 명제를 정식화한다.)

## 철강·석화 비대칭 (중요 — 한 프레임에 담기는지 재검토 필요)
- **철강**: 접근형 병목(DR펠릿)이 뚜렷하고, 전환이 배출을 거의 다 없앤다. 조기 전환 = 선점 헤지가
  깨끗이 성립.
- **석화**: 원료 탄소가 **제품에 고정(embedded)** — 전기화는 연소분(Scope1의 90%)의 30%만 감축,
  원료 탄소는 CCU/CCS·순환만 대응(현 CCUS 1.8 Mtpa로 미미). 바이오나프타는 접근형(부산물,
  +2,564달러/t). 즉 조기 전환이 **감축 가치를 구조적으로 못 올린다** — DIRECTION의 "감축 가치"
  축이 석화에선 상한. → 석화의 조기 전환 논리는 철강보다 약하다.

## 직전(L1) 비판적 재검토
L1은 재생 PPA를 σ 낮추는 헤지로만 봤다 — 맞지만 절반. L2가 보완: 재생 PPA "물량"도 접근형
위험(β 경로가 PPA 가용 물량에 종속, L1 각주에서 이미 예감). 즉 L1의 β(잔여 계통 비율)는 전력만의
문제가 아니라 **원료·수소·전력을 관통하는 하나의 접근형 축**일 가능성. 세 자원의 선점 경쟁이
공통 구조. L5에서 통합.

## 분포에 반영할 함의 (L1+L2 누적)
- 접근형 위험은 가우시안 σ가 아니라 **물량 배급 실패 확률 + 프리미엄**으로. 이산 임계(선점 성공/실패).
- 석화 감축기술 축은 "연소 전기화"와 "원료 탄소(CCU/순환)"를 분리 — 단일 변수로 뭉치면 embedded
  배출 잔존분 과소평가.
- 철강·석화를 한 표에 나란히 두되 조기 전환 결론은 섹터별로 다르게 — 철강 강, 석화 약.
