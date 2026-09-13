# L6 — 석유화학 헤지 가능성 종합 지도 (문헌 종합)

작성일 2026-09-13. 9루프 L6. 맥락: L1(전력·재생PPA)~L5(공급 희소성·재투자 창·선점)가 세운 척추 —
위험 세 종류(가격형/접근형/제도형), 조기 전환은 **접근형만** 헤지하며 그것도 6조건(자원 희소성·경쟁
강도·커미트먼트 신뢰성·기술 성숙·보완 역량·자기정당화 배제, L5_firstmover.md)이 성립할 때만.
L4는 탄소 강화(제도형)가 CBAM을 통해 시장 접근(접근형)으로 번역돼 철강의 조기 전환 헤지를
강화한다는 것을 보였다. L2는 석화에서 원료 탄소가 제품에 embedded돼 전기화로 배출의 최대 30%만
감축된다는 구조적 비대칭을 열었다. 이 문서는 L1~L5를 종합하고 부족한 실증을 WebSearch로 보강해,
석화의 모든 위험을 (위험 종류)×(헤지 수단)×(조기 전환 위치)로 매핑하고 왜 조기 전환 논리가
철강보다 약한지 정식화한다.

모든 서지는 WebSearch/WebFetch로 실제 확인했다. 추측 서지는 넣지 않았으며, 확인 강도가 낮은
항목(시장조사·언론)은 본문에 명시하고 "미확인" 절에 재정리했다.

---

## 석화 위험 노출 전체 지도

| 노출 | 위험 종류 | 헤지 수단 존재? | 조기 전환의 위치 |
|---|---|---|---|
| **(a) 나프타·에탄 가격/스프레드** | 가격형 | **있음, 이미 성립** — 선물·스왑(원유·나프타 파생상품), 그리고 flexi-cracker 원료 전환 유연성. 톤당 200–400달러의 나프타-에탄 스프레드에 대응해 다중원료 크래커가 상대 수익성에 따라 전환한다[Imubit, "Feedstock Flexibility in Petrochemical Plants"; AIChE 2016 Spring Meeting Paper443344]. 이 유연성 자체가 실물옵션으로 학술 평가 대상이다[ScienceDirect, "Real options valuation for refinery and petrochemical investments: A feasibility study in Indonesia", *Cleaner Engineering and Technology* (2025) \| https://sciencedirect.com/science/article/pii/S2352484725000071] | **없음/불필요** — 이 헤지는 전환(탈탄소) 여부와 무관하게 이미 화석연료 체제 안에서 작동한다. "조기 전환"이 추가할 옵션가치가 거의 없다(§3 참조). |
| **(b) 바이오/순환 원료** | 접근형 | **부분적** — 부산물 생산구조(바이오나프타는 HVO/SAF 부산물, 열분해유는 폐플라스틱 공급 제약)로 물량이 배급됨. 장기 오프테이크 계약이 유일한 확보 수단[BASF-Braven Environmental 장기 재활용원료 공급계약, 2025-03 \| https://www.basf.com/us/en/media/news-releases/2025/03/P-US-25-06]. 2025년 기준 발표된 열분해 설비 대비 수요 공급적자 약 64%, 2030년 약 62%로 추정[IndexBox, "Plastic Waste Pyrolysis Oil Market Forecast to 2035" — 시장조사, 방법론 미확인 \| https://www.indexbox.io/blog/plastic-waste-pyrolysis-oil-chemical-recycling-feedstock-market-demand-to-accelerate-by-2035-driven-by-circular-economy-mandates/] | **있음, 좁은 의미** — 조기 오프테이크 계약으로 물량 선점 가능(§2). 단 이 헤지는 **가격 프리미엄 회피**를 위한 것이지 탄소노출 축소가 아니다(embedded 배출 상한은 그대로). |
| **(c) 전력(e-cracker)** | 가격형, 그러나 감축은 30%만 | **있음, 그러나 미완성** — 장기 고정가 PPA(BASF Hollandse Kust Zuid, LyondellBasell, Dow, L1)가 가격은 고정하지만, 전기크래커의 재래식 연속가동 요구와 재생 간헐성 사이 불일치는 남아 유연 운전·배터리 투자가 추가로 필요[Tiggeloven et al. (2023), *Ind. Eng. Chem. Res.* 62(40) \| https://pubs.acs.org/doi/10.1021/acs.iecr.3c02226] | **부분적** — L1 결론대로 "전력위험→설비위험" 단일 변환이 아니라 "전력위험→(설비위험+유연성투자위험)"의 이중 변환. 게다가 감축 가치 자체가 30%에 상한[Layritz et al. (2021), *Applied Energy* 296 \| https://ideas.repec.org/a/eee/appene/v296y2021ics0306261921005079.html]. |
| **(d) embedded 배출(원료 탄소)** | 구조적 잔존 — 판정 대상 아님 | **없음, CCU/CCS·순환만** — 2024년 기준 화학산업 CCUS 처리용량 연 180만 톤에 불과[IEA, "CCUS in Clean Energy Transitions" \| https://www.iea.org/reports/ccus-in-clean-energy-transitions/ccus-in-the-transition-to-net-zero-emissions]. 1990–2016년 미국 비연료 석화 제품 제조 시 잠재 탄소의 60% 이상이 제품에 저장(전기화·연료대체로 못 건드림)[Kleinman Center for Energy Policy, "Balancing Act" \| https://kleinmanenergy.upenn.edu/research/publications/balancing-act-can-petrochemicals-be-both-emissions-free-and-zero-waste/; Levi, P. G. & Cullen, J. M. (2018), "Mapping Global Flows of Chemicals", *Environ. Sci. Technol.* 52(4), 1725–1734] | **없음 — 조기 전환으로도 못 없앤다.** 이것이 §3·§4의 핵심. |
| **(e) tail gas 넷백** | 가격형, 신규 노출 | **없음/미성숙 시장** — 전기화가 노(furnace) 자체 연료수요를 없애 부생가스(메탄·수소)가 캡티브 연료에서 판매 가능 상품으로 전환되지만[ADI Analytics, "Steam cracker electrification and tail gas analysis" \| https://adi-analytics.com/industries/chemicals-and-plastics/polyolefins/steam-cracker-electrification-and-tail-gas-analysis/], 정형화된 넷백 가격지표·유동적 판로가 확인되지 않음(L1 미확인 항목) | **역방향** — 이것은 조기 전환이 "헤지하는" 위험이 아니라 조기 전환 자체가 "만들어내는" 새 노출이다. |
| **(f) 구조조정·과잉설비(NCC 폐쇄)** | 수요형 | **있음, 그러나 통폐합이지 전환이 아님** — 폐쇄·통합이 유일한 대응. 유럽 최대 40%(2,450만 톤 중), 한국 10대 기업 NCC 능력 최대 25% 감축, 일본 175만 톤 폐쇄[S&P Global(2025); Wood Mackenzie, "Petrochemicals in peril" \| https://www.woodmac.com/news/opinion/petrochemicals-in-peril-oversupply-crisis-and-energy-transition-threaten-industry-survival/; ICIS(2026)] | **경쟁 관계 — 자본을 두고 전환과 경합.** 과잉설비 국면의 첫 자본 결정은 전환이 아니라 폐쇄/통합이다(§3(b)). |
| **(g) 탄소 수준(제도형)** | 제도형 | **CBAM 미적용(2026 현재)** — 석유화학(유기화학·폴리머)은 EU CBAM 현행 대상(철강·시멘트·알루미늄·비료·수소·전력)에서 **제외**돼 있다. 2030년 확대가 검토되나 기술적 난점(embedded 배출 계산)으로 유보돼 왔다[Minten, H., Hausweiler, J., Probst, B., Reinert, C., Meys, R., & Bardow, A. (2025), "Embodied emissions of chemicals within the EU Carbon Border Adjustment Mechanism", *Nature Sustainability* 8(11), 1381–1390 \| https://www.nature.com/articles/s41893-025-01618-5]. 확대되더라도 에틸렌·폴리에틸렌 생산배출의 **39–60%만 커버**(원료 유래·정유공정 상류배출 제외)한다는 것이 같은 논문의 정량 추정[동일] | **없음 — 철강과 결정적으로 다른 지점.** L4의 "CBAM이 제도형을 접근형으로 번역해 조기 전환을 헤지로 만든다"는 메커니즘이 석화에는 (i) 현재 미적용, (ii) 확대돼도 반쪽짜리라 성립하지 않는다. |

---

## 순환·CCU는 접근형인가

**결론: 접근형이 1차, 제도형(기술 미성숙)은 그 위에 얹힌 2차 제약 — 그러나 조기 물량 선점이 "완화가 아니라 지연"일 위험이 크다.**

1. **물량 제약이 근본이다.** 바이오나프타는 그 자체를 목적으로 짓는 설비가 없고 HVO/SAF 바이오연료 생산의 부산물로만 나온다[S&P Global Commodity Insights (2021-08-19), "Regulation, consumer demand drive bionaphtha use"]. 열분해유(화학적 재활용)도 마찬가지로 폐플라스틱 수거·품질이라는 물리적 상한이 있다. 2025년 기준 발표된 열분해 설비 대비 수요 공급적자가 약 64%, 2030년 약 62%로 추정된다[IndexBox — 시장조사 방법론 미확인, 방향성만 참고]. 이는 순수한 **접근형(volume rationing)** — 돈이 있어도 원하는 시점에 원하는 물량을 살 수 없다.

2. **가격 프리미엄이 접근형 위험의 화폐화(monetization)다.** 유럽 UCO 기반 바이오나프타는 화석 나프타 대비 톤당 약 2,564달러 프리미엄(L2, Argus/S&P Global 데이터). 인증 순환 폴리올레핀은 화석 대비 톤당 수백~1,000달러 이상 프리미엄이 관찰된다[World Bio Market Insights, "Closing the Plastics Loop" \| https://worldbiomarketinsights.com/closing-the-plastics-loop-can-chemical-recycling-deliver-on-the-promise/]. 이 프리미엄은 "규제(순환 함량 의무)가 유지되는 한 지속될 것"으로 전망되며 순수 상품경제가 아니라 **컴플라이언스가 프리미엄을 지탱**한다는 점에서, 접근형 위험이 제도형 요인(순환 함량 의무 강도)에 조건부라는 이중구조를 보인다.

3. **오프테이크 계약이 물량 선점의 실제 형태다.** BASF는 Braven Environmental과 장기 첨단 재활용원료 공급계약을 체결했다[BASF 보도자료(2025-03) \| https://www.basf.com/us/en/media/news-releases/2025/03/P-US-25-06]. 그러나 업계 조사는 "브랜드가 장기 오프테이크에 프리미엄을 지불하기를 꺼려 수요보증이 불충분했다"고 지적하며, 규제 세부사항 확정 전까지 석화기업·브랜드오너가 투자결정·대규모 오프테이크를 지연시키고 있다고 보고한다[World Bio Market Insights, 동일 출처]. 즉 계약형 물량 선점이라는 **수단 자체는 존재**하지만(철강의 DR펠릿 오프테이크와 구조적으로 동일), 수요 측의 지불의지 부족이 계약 성립 자체를 제약한다.

4. **"완화가 아니라 지연"이라는 비판이 핵심 긴장이다.** 순환탄소 서사는 글로벌 노스의 기존 산업조직·생활양식과 양립 가능한 단순한 기술적 해법을 제공하지만, "실현되지 않는 물질적 약속"(1형)과 "완화를 지연시키는 비물질적 약속"(3형)의 mitigation deterrence로 이어질 수 있다는 학술적 비판이 있다[ScienceDirect, "Imagining circular carbon: A mitigation (deterrence) strategy for the petrochemical industry" \| https://www.sciencedirect.com/science/article/pii/S1462901123002897]. 순환 원료를 조기에 물량 선점하는 것은 (a) 프리미엄 회피라는 **좁은 의미의 접근형 헤지**로는 작동하지만, (b) 그 자체로 embedded 배출 상한을 올리지 않는다 — 재활용 원료도 결국 제품 내 탄소를 다시 저장할 뿐 소각·매립 시점에 배출을 재현하며(L2), 진정한 탈탄소(CCU/CCS·비탄소 원료)를 대체하는 "다음 세대로 미루기"로 기능할 위험이 있다.

**판정**: 순환·CCU는 **1차로 접근형**(물량 배급 + 가격 프리미엄으로 화폐화)이고, 그 위에 **제도형 조건**(규제 강도가 프리미엄을 지탱, 기술 미성숙이 물량 확장을 제약)이 얹혀 있다. 조기 물량 선점은 프리미엄 회피 헤지로는 성립하나, embedded 배출을 줄이는 감축 헤지로는 성립하지 않는다 — L2의 mitigation deterrence 우려가 여기서 정식화된다.

---

## 왜 석화는 조기 전환 논리가 약한가

세 가지 이유를 문헌으로 뒷받침한다. 철강(L1~L5)의 "조기 전환=선점 헤지"가 성립하는 조건(L5 6조건표)과 대조하면, 석화는 조건 자체가 구조적으로 결여돼 있다.

**(a) 감축 가치 상한 — embedded 배출로 조기 전환해도 원료 탄소는 남는다.**
직접 전기화 경로는 시스템 전체 배출 감축을 최대 30%까지만 끌어올릴 수 있다(원료 유래 공정 배출은 그대로 남기 때문)[Layritz et al. (2021), *Applied Energy* 296]. 1990–2016년 미국에서 비연료 석화 제품 제조 시 잠재 탄소의 60% 이상이 화학제품 자체에 저장됐다는 추정도 같은 구조를 보여준다[Kleinman Center for Energy Policy, "Balancing Act"; Levi & Cullen (2018), *Environ. Sci. Technol.* 52(4)]. 완전 탈탄소(OCM–PtG 등)는 파리협정 부합 시나리오에서도 2030년 이후에나 비용 경쟁력을 가질 가능성이 높다(L1, Layritz et al. 2021). 이는 L5 6조건표의 "기술 성숙도" 조건(채택 기술이 후발주자에 쉽게 추월당하지 않을 만큼 성숙)이 아니라, 그보다 근본적인 조건 — **채택 기술이 애초에 노출을 닫을 수 있는가** — 가 실패하는 사례다. 조기에 전환해도 문 닫힌 노출의 크기가 애초에 작다.

**(b) 과잉설비·구조조정으로 첫 자본 결정이 전환이 아니라 통폐합이다.**
2024년 이후 유럽에서만 ExxonMobil·Shell·SABIC·Dow·Versalis·TotalEnergies가 크래커 7기를 영구 폐쇄, EU 에틸렌 설비 2,450만 톤 중 최대 40%가 고·중위험 폐쇄 대상(L1, S&P Global 2025). 한국 10대 화학기업이 나프타분해설비 능력을 최대 25% 감축하는 구조조정에 합의했고[Wood Mackenzie, "Petrochemicals in peril: oversupply crisis and energy transition threaten industry survival" \| https://www.woodmac.com/news/opinion/petrochemicals-in-peril-oversupply-crisis-and-energy-transition-threaten-industry-survival/], 일본 에틸렌 가동률은 2025년 3월 사상 최저 75.1%까지 하락했다(L1, ICIS 2026). ExxonMobil은 싱가포르 크래커 1기를 영구 폐쇄 준비 중이라고 보도됐다[OilPrice.com, "ExxonMobil Prepares to Permanently Close Singapore Petrochemical Unit"]. 전략경영 문헌은 만성 과잉설비 국면에서 퇴출장벽이 무임승차 문제를 낳아 소규모·저품질 설비만 먼저 문 닫고, 결국 대형 인수합병을 기반으로 한 용량 감축이 정체를 해소한다는 것을 보인다 — 이는 화학산업이 아닌 점토벽돌 산업 사례이지만 자본배분의 순서 논리(퇴출/통폐합이 성장형 투자에 선행)는 구조적으로 동형이다[Wood, S. (2009), "Capacity rationalization and exit strategies", *Strategic Management Journal* 30(1), 25–44]. 요컨대 과잉설비 산업의 이사회가 마주하는 첫 자본배분 질문은 "어디에 전환 투자를 할까"가 아니라 "어느 설비를 닫을까"이며, 이는 L5 6조건표의 "커미트먼트의 비가역성과 신뢰성" 조건과 정면 충돌한다 — 통폐합이 진행 중인 자산군에 조기 전환 투자를 얹는 것은 신뢰할 수 있는 선점 신호가 아니라 생존 자체가 불확실한 설비에 대한 이중 베팅이 된다.

**(c) 원료 스위칭(flexi-cracker)이라는 가격형 헤지가 이미 존재해 조기 전환 없이도 대응 가능하다.**
다중원료 크래커는 나프타-에탄 상대가격에 따라 원료를 전환하는 유연성을 이미 갖추고 있으며, 유가 급등기 스프레드가 톤당 최대 400달러까지 벌어져도 이 유연성으로 대응한다(L2, Imubit; AIChE 2016). 이 유연성 자체가 학술적으로 실물옵션 평가 대상이다[ScienceDirect, "Real options valuation for refinery and petrochemical investments: A feasibility study in Indonesia", *Cleaner Engineering and Technology* (2025)]. 즉 석화 기업은 **탈탄소 전환과 무관하게** 이미 가격형 위험에 대한 옵션을 보유하고 있다 — 철강의 고로(BF)에는 이런 원료 전환 유연성이 구조적으로 없으므로(원료탄·철광석을 다른 원료로 실시간 전환할 수 없음), 철강에서는 "조기 전환(DRI-EAF)"이 곧 새로운 헤지 수단의 도입이지만, 석화에서는 "조기 전환(전기화·원료전환)"이 **이미 있는 가격형 헤지 위에 얹는 추가 옵션**에 불과해 한계가치가 낮다. L5의 선점이론(Grenadier 2002; Fudenberg & Tirole 1985)이 요구하는 "경쟁자가 실제로 같은 자원을 노리는 레이스"도 이 채널에서는 성립하지 않는다 — 원료 전환은 이미 산업 표준 관행이라 "먼저 하지 않으면 경쟁자에게 뺏긴다"는 희소성 경쟁 구도가 없다.

---

## 석화는 대조군인가 별도 헤지인가

**판정: 두 프레임이 서로 다른 위험 축에서 동시에 맞다 — 단일 프레임으로 뭉뚱그리면 안 된다.**

1. **탄소·제도형 축에서는 대조군이다.** L4가 확립한 "CBAM이 제도형 탄소강화를 접근형 시장접근으로 번역해 철강의 조기 전환을 보험으로 만든다"는 메커니즘은 석화에서 성립하지 않는다 — CBAM은 현재 유기화학·폴리머를 제외하며, 2030년 확대되더라도 에틸렌·PE 생산배출의 39–60%만 커버한다(원료·정유 상류배출 제외)[Minten et al. (2025), *Nature Sustainability* 8(11)]. 게다가 (a)에서 확인했듯 전기화 자체의 감축 상한이 30%다. 두 제약이 겹치면 "조기 전환 → 탄소노출 축소 → 시장접근 보험"이라는 철강의 인과사슬이 석화에서는 **두 지점에서 끊긴다**: 감축 자체가 상한에 막히고, 그 감축이 시장접근으로 번역될 CBAM 채널도 반쪽이다. 이 축에서 석화는 "철강이 성립시키는 조기 전환=선점 헤지"의 대조군 — **전환으로도 안 되는 것**의 사례다.

2. **원료 접근·가격 축에서는 별도의, 더 좁은 헤지가 존재한다.** 순환·바이오 원료의 조기 물량 선점(BASF-Braven Environmental 오프테이크 등)은 철강의 DR펠릿 선점과 구조적으로 동일한 접근형 헤지 문법을 따른다 — 그러나 그 헤지가 막는 위험은 "탄소노출"이 아니라 "원료 프리미엄·물량 부족"이며(§2), embedded 배출 상한을 올리지 않는다. 동시에 나프타-에탄 스프레드에 대한 flexi-cracker 유연성은 **전환과 무관하게 이미 존재하는** 가격형 헤지다(§3c) — 철강에는 이런 원료 전환 옵션이 원천적으로 없다는 점에서, 이는 조기 전환이 아니라 "산업 표준 운영 유연성"이 이미 헤지 역할을 하고 있다는 뜻이다.

3. **종합 프레임: 석화는 하나의 이야기가 아니라 세 개로 쪼개진다.** (i) 원료 가격형 위험 — flexi-cracker가 이미 헤지(전환 논의와 독립), (ii) 원료 접근형 위험(바이오/순환) — 조기 오프테이크가 좁은 의미의 헤지(프리미엄 회피, 탄소축소 아님), (iii) 탄소·제도형 위험 — 조기 전환이 헤지가 안 됨(감축상한 + CBAM 미적용/반쪽). CAP가 석화를 철강과 나란히 놓을 때, "조기 전환"이라는 단일 정책 변수로 세 축을 동시에 대표하면 (i)에서는 과잉평가(이미 있는 헤지에 가치를 이중계상), (iii)에서는 과소평가(상한을 무시하고 무한 감축 가능한 것처럼 취급)의 반대 방향 오류가 동시에 생긴다.

---

## 분포에 반영할 함의

1. **탄소·제도형 노출에 대해 석화의 조기 전환 보험가치를 철강과 다른 함수로 처리한다.** L4의 CBAM 접근형 번역 메커니즘(강화될수록 조기 전환 보험가치 상승)을 석화에 그대로 이식하면 안 된다 — CBAM이 현재 미적용이고 확대돼도 39–60%만 커버하므로(Minten et al. 2025), 석화의 탄소노출-시장접근 연결계수는 철강 대비 구조적으로 낮게(또는 0에 가깝게) 잡아야 한다. 동시에 감축 자체의 상한(30%, Layritz et al. 2021)을 페이오프 함수에 명시적 캡(cap)으로 넣어, "완전 전환=완전 감축"을 가정하는 철강형 구조식을 그대로 쓰지 않는다.

2. **원료 접근형 위험(바이오/순환)은 별도의 물량배급+프리미엄 결합 노드로 넣되, 감축축과 분리한다.** L2의 함의를 재확인 — 바이오나프타·열분해유는 가우시안 가격변수가 아니라 ISCC 인증 물량 상한 내 배급으로 모델링해야 한다. 이 노드의 조기 확보(오프테이크 선점)는 "프리미엄 리스크"를 낮추는 것으로만 페이오프에 반영하고, "탄소노출 축소"에는 연결하지 않는다 — mitigation deterrence 우려(§2)를 분포 설계에서 명시적으로 반영하는 방법이다.

3. **원료 가격형 위험(나프타-에탄 스프레드)에는 flexi-cracker 옵션가치를 기준선(baseline)에 이미 내재된 것으로 처리한다.** 조기 전환 시나리오와 무전환(BAU) 시나리오 모두에 이 옵션이 존재하므로, 두 시나리오의 차분(조기 전환의 증분가치)을 계산할 때 flexi-cracker 헤지 효과가 양쪽에서 상쇄돼야 한다 — 상쇄하지 않으면 조기 전환의 가격형 헤지가치를 이중계상하게 된다(§4 종합 프레임의 (i) 과잉평가 오류).

4. **구조조정·과잉설비를 감축기술 축과 경쟁하는 별도의 자본배분 제약으로 넣는다.** 현재 CAP가 "전환 대 무전환"의 이분법으로 설계돼 있다면, 석화에는 세 번째 대안 — "통폐합/폐쇄"(전환도 무전환 유지도 아닌 자본 철수) — 가 실제 의사결정 세트에 있다는 것을 반영해야 한다. 유럽·한국·일본 구조조정 사실(L1, S&P Global·Wood Mackenzie·ICIS)은 이 세 번째 대안이 이론적 가능성이 아니라 현재 실행 중인 선택지임을 보여준다.

5. **tail gas 넷백은 조기 전환이 "만드는" 새 노출로 별도 부호를 가진 노드로 넣는다.** L1의 결론을 재확인 — 이 노드는 전기화의 편익 측이 아니라 전기화가 유발하는 추가 상품가격 노출(양 또는 음)이다. 정량화는 미완이므로 폭넓은 사전분포로 처리한다.

---

## 미확인

- **IndexBox의 열분해유 공급적자 수치(2025년 64%, 2030년 62%)** — 시장조사 애그리게이터로 방법론·1차 데이터가 공개되지 않음. 방향성(구조적 공급부족)만 참고하고 수치는 인용 신뢰도 낮음으로 분류.
- **World Bio Market Insights의 인증 순환 폴리올레핀 프리미엄(톤당 수백~1,000달러 이상)** — 업계 매체 기사로 1차 데이터·조사방법 미확인.
- **Wood, S. (2009, Strategic Management Journal)의 사례는 점토벽돌 산업이며 석유화학 직접 사례가 아니다** — 자본배분 순서 논리(퇴출장벽→통폐합 선행)의 구조적 유비로만 인용했고, 석화산업에 이 논문의 정량 결과(무임승차 계수 등)를 직접 적용하지 않았다.
- **ExxonMobil 싱가포르 크래커 폐쇄 준비 보도(OilPrice.com)** — 1차 공시·보도자료 대조 없이 뉴스 기사 단일 출처로만 확인.
- **BASF-Braven Environmental 계약의 정확한 물량·기간·가격 조건** — 보도자료에서 "장기 공급계약" 체결 사실만 확인, 구체 조건(물량 톤수, 계약기간, 가격 공식)은 공개되지 않아 미확인.
- **CBAM 2030 확대 시나리오의 확정 여부** — Minten et al. (2025)와 산업분석(Sandbag, ICAP, IISD)이 "검토 중", "2030년 목표"라고 서술하나 2026-09 현재 법제화 여부는 확인하지 못했다. "논의 중"과 "확정"을 구분해 인용할 것.
- **flexi-cracker 실물옵션 논문(ScienceDirect, Indonesia feasibility study, 2025)의 정량 결과(옵션가치 수준, 임계 스프레드)** — 검색 스니펫으로 존재·주제만 확인, 본문 수치는 열람하지 못함.
- **한국 나프타 순수입 의존과 CBAM 미적용의 결합 함의**(한국이 탄소노출은 있으나 EU 수출 시장접근 채널로 조기 전환을 헤지할 유인이 철강보다 약할 것이라는 추론) — 이 문서의 해석이며 직접적인 실증 문헌은 확인하지 못했다. 가정으로만 명시.

---

*작성: 2026-09-13. 대상 파일: `docs/research_cycles/2026-09-13-hedging/L6_petchem.md`*
