# L1 — 석유화학 전환 후 전력 조달과 비용위험 구조 (문헌 종합)

작성일 2026-09-13. WebSearch/WebFetch로 확인된 내용만 기재. 확인 불가 항목은 마지막 절에 별도 표시.

---

## 전기화 전력 수요

- **Layritz, L. S., Dolganova, I., Finkbeiner, M., Luderer, G., Penteado, A. T., Ueckerdt, F., & Repke, J.-U. (2021)**, "The potential of direct steam cracker electrification and carbon capture & utilization via oxidative coupling of methane as decarbonization strategies for ethylene production," *Applied Energy*, 296, 117049. | https://ideas.repec.org/a/eee/appene/v296y2021ics0306261921005079.html
  두 경로를 비교한다. (1) 직접 전기화 — 크래커 가열을 재생전력으로 대체 시 최대 배출 감축은 **30%**에 그친다(원료 유래 공정 배출은 남기 때문). (2) OCM–PtG(부생 메탄의 산화커플링 + Power-to-Gas) 경로는 완전 탈탄소 전력과 제품 재활용을 전제로 넷제로에 도달할 수 있지만, 이 조건은 파리협정에 부합하는 매우 강한 기후정책 하에서도 2030년 이후에나 충족될 가능성이 높고, 현재로선 비용 경쟁력이 없다.

- **Tijani, M. E. H., Zondag, H., & Van Delft, Y. (2022)**, "Review of Electric Cracking of Hydrocarbons," *ACS Sustainable Chemistry & Engineering*, 10(49), 16070–16089. | https://pubs.acs.org/doi/10.1021/acssuschemeng.2c03427
  전 세계 스팀크래커의 가스연소 노(furnace)에서 발생하는 CO2가 연간 약 366 Mt에 달한다는 배경 위에서, 전기가열은 배가스(flue gas) 열손실이 없어 에너지 효율 자체는 개선되지만, 현재 전력 단가가 가스 단가보다 높아 전기분해로 운전비용은 재래식 대비 높다. 기존 크래커에 레트로핏 가능한 스케일업 용이성은 장점으로 지목된다.

- **Tiggeloven, T., Faaij, A., Kramer, G. J., & Gazzani, M. (2023)**, "Optimization of Electric Ethylene Production: Exploring the Role of Cracker Flexibility, Batteries, and Renewable Energy Integration," *Industrial & Engineering Chemistry Research*, 62(40). | https://pubs.acs.org/doi/10.1021/acs.iecr.3c02226
  MILP 모델로 전기크래커의 가동 유연성(운전범위·램핑시간·기동정지시간)이 비용에 미치는 영향을 정량화. 계통전력 + 배터리 조합에서 유연 운전은 비용을 최대 5.5% 절감하고, 재생에너지 직결 시스템에서는 최대 58% 절감. 계통 유연운전은 배출을 90.4% 감축(고정운전 대비 54.6% 감축과 비교). 재생에너지 직결 방식은 크래커 자체가 유연해야만 재생설비·배터리의 비현실적 과대설계를 피할 수 있다 — 즉 **PPA로 전력을 조달하는 것과, 그 전력을 실제로 소화할 수 있는 유연성을 갖추는 것은 별개의 조건**이라는 결론.

- 부하 특성: 위 세 문헌 모두 공통적으로 전제하는 사실은, 재래식 나프타 크래커는 화학반응 안정성 때문에 전통적으로 **거의 100% 가동률의 연속(baseload) 공정**이라는 점이다. Tiggeloven et al.(2023)의 핵심 기여는 바로 이 "연속 가동이 당연하다"는 전제를 깨고 전기크래커에 한해 유연성을 설계 변수로 둔 것 — 이는 재래식 크래커에는 없던 선택지다.

## 재생 PPA 조달 사례

- **BASF — Hollandse Kust Zuid 해상풍력.** BASF는 Vattenfall로부터 네덜란드 북해 Hollandse Kust Zuid 해상풍력발전소 지분 49.5%를 인수(€300M, 건설 자금 포함 총 투입 약 €16억). 해당 발전소는 터빈 140기, 총 설비용량 1.5GW로 보조금 없이 건설된 프로젝트다. BASF는 지분 49.5%에 해당하는 발전량 대부분을 **장기 고정가 기업 PPA(CPPA)** 로 수취하며, 이를 유럽 여러 생산기지의 저탄소 공정에 투입할 계획이다. | [Offshore Magazine](https://www.offshore-mag.com/renewable-energy/article/14205783/basf-takes-stake-in-hollandse-kust-zuid-offshore-wind-farm), [Windpower Monthly](https://www.windpowermonthly.com/article/1735054/chemicals-giant-basf-divest-part-dutch-offshore-wind-farm-stake), [Energy Global](https://www.energyglobal.com/wind/24062021/vattenfall-and-bsaf-agree-sale-on-hollandse-kust-zuid-wind-farm/)
  BASF는 이를 "make and buy" 전략의 일환으로 명시 — 직접 지분투자(make)와 Ørsted Borkum Riffgrund 3 PPA, RWE 2GW 북해 프로젝트 공급계약(buy) 등을 병행한다. | https://www.basf.com/nz/en/who-we-are/sustainability/our-contributions-to-enabling-the-green-transformation/climate-protection/OLD-carbon-management/increasing-renewable-energies

- **LyondellBasell.** 2030년까지 전력의 최소 50%를 재생원으로 조달한다는 목표 하에 다수의 PPA 체결. 최근 발표분은 216MW/연 628,000MWh 규모로 연 CO2 약 225,000톤 감축 효과. 2025년 1월, Vattenfall과 15년 계약으로 독일 해상풍력 연 450GWh 확보, wpd와 10년 계약으로 이탈리아 시칠리아 Licata 육상풍력 연 79GWh(2026년 개시) 확보. | [PR Newswire](https://www.prnewswire.com/news-releases/lyondellbasell-announces-renewable-energy-power-purchase-agreements-301575887.html), [LyondellBasell 발표](https://www.lyondellbasell.com/en/who-we-are/updates-events/corporate--financial-news/lyondellbasell-announces-renewable-energy-power-purchase-agreements/), [Renewables Now](https://renewablesnow.com/news/lyondellbasell-secures-560-mw-of-renewables-supply-via-new-ppas-813376/)

- **Dow.** 신규 재생 PPA 8건 추가 체결, 연간 scope 2 배출 60만 톤CO2e 이상 감축 예상. | [Dow 보도자료](https://corporate.dow.com/en-us/news/press-releases/dow-adds-eight-new-renewable-power-agreements--reducing-emission.html)

- 공통점: 세 회사 모두 **고정가 장기 PPA**를 전력가격 변동 헤지 수단이자 재생전력 조달 수단으로 동시에 사용하고 있으며, 지분투자(BASF)와 순수 오프테이크(LyondellBasell, Dow)라는 두 계약형태가 공존한다.

## 전력-원료-연료 재편

- 나프타 크래커는 열분해 과정에서 부생가스(주로 메탄·수소를 포함하는 tail gas)를 발생시키며, 이를 노(furnace) 자체의 연료로 태워 자가소비하는 것이 재래식 설계다. 전기화는 이 자가연료 수요를 없애므로 tail gas의 용도가 바뀐다.
  **ADI Analytics, "Steam cracker electrification and tail gas analysis."** | https://adi-analytics.com/industries/chemicals-and-plastics/polyolefins/steam-cracker-electrification-and-tail-gas-analysis/
  전기화 이전에는 tail gas가 대체수단이 없는 캡티브 연료(포획 가치만 있음)였으나, 전기화 이후에는 내부 연료 수요가 사라지면서 tail gas를 외부 판매 또는 타 공정 원료로 회수(monetize)할 수 있는 잠재적 상품으로 전환된다. ADI는 실제로 한 화주(client)를 위해 "전기화된 미래 시나리오"에서 tail gas 조성·에너지함량·회수 잠재력을 분석해, tail gas를 자사 공정기술의 원료로 사이징·밸류에이션했다.

- **Layritz et al. (2021)** 의 OCM–PtG 경로는 바로 이 부생 메탄을 산화커플링(OCM)으로 전환해 에틸렌 수율을 추가로 끌어올리는 설계로, "부생 연료를 태울 것인가, 화학적으로 전환할 것인가"가 전기화 설계에서 이미 경쟁하는 선택지임을 보여준다.

- Tijani et al. (2022) 리뷰는 전기가열이 배가스 손실을 없앤다는 점에서 에너지효율 이득이 있음을 확인하지만, 이는 "연료를 덜 쓴다"는 효율 이득이지 "부생가스를 판다"는 원료 재편과는 별개의 채널이다 — 즉 전기화의 경제성에는 최소 두 개의 분리된 채널(① 노 연료 대체에 따른 OPEX 변화, ② 부생가스 넷백 재평가)이 걸려 있다.

## 설비위험 전환이 석화에서 성립하나

§7.3(철강)의 논리는 "전력가격 위험을 재생 PPA로 고정하면, 남는 위험은 설비(CAPEX) 위험뿐"이라는 것이었다. 석화에서 이 논리가 그대로 성립하는지는 문헌상 세 가지 이유로 불완전하다.

1. **CAPEX 프리미엄 자체가 불확실.** 검색된 자료 중 한 학술 자료는 재래식 대비 전기화 플랜트의 자본비용 차이를 1% 미만으로 추정한다고 나타났으나, 시장조사 보고서 부류(신뢰도 낮음, 아래 미확인 참고)는 높은 자본비용을 상용화의 핵심 장벽으로 지목한다. Tijani et al.(2022)은 "비용 프리미엄은 주로 전력단가 대 가스단가 차이에서 온다"고 명시 — 즉 CAPEX보다 **OPEX(연료비 스프레드)** 가 우선 지목된 프리미엄 원천이다. 철강의 DRI-EAF처럼 "설비를 한번 짓고 나면 전력가격만 남는다"는 이분법이 석화에서는 CAPEX와 연료비 스프레드 어느 쪽이 지배적인지부터 문헌 간 정리가 안 되어 있다.

2. **PPA 고정이 유연성 문제를 풀지 않는다.** Tiggeloven et al.(2023)의 핵심 결과는, 재생에너지에 직결된 전기크래커가 비용 이득을 실현하려면 크래커 자체의 가동 유연성이 필요하며, 유연성이 없으면 재생설비·배터리를 비현실적으로 과대설계해야 한다는 것이다. BASF·LyondellBasell식 고정가 PPA는 **가격 위험**은 고정하지만, 크래커의 전통적 연속가동 요구와 재생 발전의 간헐성 사이의 **물량·시점 불일치**는 그대로 남는다. 이 불일치를 흡수하려면 배터리·계통 발란싱·유연 운전 중 하나에 추가 투자가 필요하며, 이는 §7.3의 "PPA=완전 헤지" 단순화가 성립하지 않을 수 있음을 시사한다.

3. **부생연료 넷백이라는 두 번째 노출이 새로 생긴다.** 위 절에서 확인했듯 전기화는 tail gas의 가치를 재평가시킨다(ADI Analytics). 철강에는 없는 이 채널은 전력가격 고정만으로 헤지되지 않는 별도의 상품가격 노출(메탄/수소 부생물의 판매가 또는 대체연료 가격)이다.

종합하면: 재생 PPA는 석화에서도 **전력 조달가격 위험**을 고정하는 헤지로는 작동하지만, 철강처럼 "그러면 남는 건 설비위험뿐"이라고 단언하기는 이르다 — (i) CAPEX 프리미엄의 크기 자체가 문헌 간 불일치, (ii) 유연성 투자라는 추가 설비위험이 남고, (iii) 부생연료 넷백이라는 세 번째 노출이 생긴다.

## 구조조정 맥락

- **유럽.** 2024년 4월 이후 ExxonMobil·Shell·SABIC·Dow·Versalis·TotalEnergies가 2027년까지 크래커 7기를 영구 폐쇄(완료·발표 포함). ExxonMobil은 프랑스 Notre-Dame-de-Gravenchon(42.5만 톤/년)을 2024년 4분기 폐쇄, 스코틀랜드 Mossmorran(83만 톤/년)은 2026년 2월까지 폐쇄 예정. TotalEnergies는 벨기에 Antwerp 크래커를 2027년 말까지, Dow는 독일 Böhlen 크래커를 2027년 말까지 폐쇄 발표. Versalis(이탈리아 국영)는 Brindisi(44만 톤)·Priolo(53만 톤)를 2025년 말까지 폐쇄. EU 에틸렌 총 설비 2,450만 톤 중 최대 40%가 고위험·중위험 폐쇄 대상으로 지목됨. INEOS의 신규 Project One 에탄크래커(벨기에 Antwerp, 140만 톤/년, 2026년 말 가동)가 폐쇄분의 약 37%를 상쇄할 전망. | [S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/chemicals/070725-a-perfect-storm-europes-steam-cracker-closures-highlight-continents-struggles-with-competitiveness), [SOCI/Dow](https://www.soci.org/news/2025/7/dow-plans-european-ethylene-cracker-closure), [ICIS](https://www.icis.com/explore/resources/cracker-closures-europe/)

- **한국.** 산업통상부가 승인한 '여수 1호 프로젝트'(여천NCC·롯데케미칼·한화솔루션·DL케미칼)는 향후 3년간 에틸렌 설비 2기 가동을 중단해 연 139만 톤을 감축. '대산 1호'(HD현대케미칼·롯데케미칼)는 두 회사 합산 NCC 195만 톤을 85만 톤으로 줄여 약 110만 톤 감축. 두 프로젝트 합산 감축량 249만 톤은 정부 목표(270만~370만 톤)의 67~92%에 해당. | [더밸류뉴스](https://www.thevaluenews.co.kr/news/195388), [블로터](https://www.bloter.net/news/articleView.html?idxno=668613), [이데일리](https://edaily.co.kr/News/Read?mediaCodeNo=257&newsId=02824086645517472), [서울경제](https://www.sedaily.com/article/20012814)

- **일본.** 2025년 3월 에틸렌 가동률이 사상 최저 75.1%까지 하락, 4년 연속 80% 밑돌음. Idemitsu Kosan은 2027년 7월 크래커 폐쇄 후 Mitsui Ichihara 부지로 생산 통합. Maruzen Petrochemical은 자사 에틸렌 플랜트를 폐쇄하고 Sumitomo Chemical과의 합작사 Keiyo Ethylene로 이전. ENEOS는 가와사키 2개 라인을 2027년 말까지 1개로 통합. Mitsubishi Chemical·Asahi Kasei·Mitsui Chemicals는 나프타 크래커를 통합하며 Mizushima 크래커를 폐쇄하고 오사카로 생산을 이전. 총 약 175만 톤/년 설비 폐쇄. 일본은 나프타의 60% 이상을 수입(그 중 약 70%가 중동산)에 의존. | [ICIS](https://www.icis.com/explore/resources/news/2026/05/15/11207890/japan-speeds-up-petrochemical-consolidation-decarbonization-amid-oversupply/), [C&EN](https://cen.acs.org/business/reckoning-Japans-petrochemical-industry/102/web/2024/01)

## 분포에 반영할 함의 (석화 전력·연료 노출을 어떻게 흔들어야 하나)

1. **부하-발전 불일치를 별도 확률변수로 넣어야 한다.** 철강 모형처럼 "PPA 고정가 = 전력가격 위험 소거"로 접지 않는다. Tiggeloven et al.(2023)에 따르면 전기크래커가 재생전력을 실제로 소화하려면 유연 운전(또는 배터리 과대설계)이 필요하므로, 분포에는 (a) PPA 고정가격 노출과 별개로 (b) 유연성 미달로 인한 잔여 계통조달·발란싱 비용을 추가 노드로 넣어야 한다. 이는 §7.3의 "전력위험→설비위험" 단일 변환이 석화에서는 "전력위험→(설비위험 + 유연성투자위험)"의 이중 변환이 됨을 뜻한다.

2. **부생연료 넷백을 두 번째 상품 노출로 추가한다.** ADI Analytics 분석대로 전기화는 tail gas(메탄·수소)의 용도를 캡티브 연료에서 판매 가능 상품으로 바꾼다. 분포생성기는 전력가격 노드 외에 "부생가스 판매가/대체연료가" 노드를 최소 하나 더 가져야 하며, 이 노드의 부호는 양(추가 수익)일 수도 음(판로 미확보 시 처분비용)일 수도 있다 — 대칭 분포가 아니라 채택된 하위기술(직접전기화 vs OCM-PtG)에 따라 조건부로 갈릴 가능성이 큼(Layritz et al. 2021의 두 경로 비교가 이 조건부 구조의 근거).

3. **CAPEX 프리미엄의 크기를 고정 파라미터로 쓰지 말고 폭으로 잡는다.** 문헌 간 자체가 불일치(<1% vs "높은 자본비용이 장벽")하므로, 철강처럼 단일 CAPEX 승수를 가정하면 안 되고 넓은 사전 분포(prior)로 처리해야 한다.

4. **표본선택 문제 — 오늘의 설비군이 내일의 전환 대상이 아니다.** 유럽·한국·일본 모두 구조조정이 "누가 살아남는가"를 먼저 정리하는 국면이며, 전기화 투자는 생존이 확정된 축소된 설비군에서만 논의될 개연성이 높다. 현재 가동 중인 전체 NCC 스톡을 모집단으로 분포를 추정하면, 실제로 전환 투자 결정에 놓일 (구조조정 이후) 축소된 설비군과 괴리가 생긴다 — 이는 검색 결과 자체가 아니라 위 구조조정 사실들로부터의 해석이므로 강한 주장으로 쓰지 말고 가정으로 명시할 것.

## 미확인

- **"FUREC"이라는 프로젝트명**을 원문 그대로 확인하지 못했다. BASF·SABIC·Linde의 전기가열 크래커 데모플랜트는 뉴스·보도자료상 고유명이 없거나 Linde의 상표명 "STARBRIDGE™"(구 "eFurnace")로 지칭되며, 6개사 컨소시엄은 "Cracker of the Future"(BASF·Borealis·BP·LyondellBasell·SABIC·Total, 2019년 결성)로 확인된다. "6대 전기 크래커 프로젝트"가 이 컨소시엄을 지칭하는 것이라면 명칭은 "Cracker of the Future"이며 "FUREC"은 확인되지 않는다.
- 임무 설명에 있던 "1.5 MMt/y 에탄크래커 전기화 시 전력수요 1,000MW 초과, 24시간"이라는 수치는 이번 검색에서 재확인되지 않았고 정확한 1차 출처(Layritz et al. 2021인지 다른 자료인지)를 특정하지 못했다. 인용 없이 본문에 넣지 않았다.
- e-cracker와 재래식 나프타 크래커 간 **정확한 전력원단위(MWh/t 에틸렌) 비교 수치**는 S&P Global 보고서(RP29O, "Ethylene e-Cracker: Comparative Analysis of Electricity...")가 존재함을 확인했으나 유료 보고서라 본문 수치를 확보하지 못했다. | https://www.spglobal.com/content/dam/spglobal/ci/en/documents/products/1025/reports/RP29O_TOC.pdf (목차만 확인)
- "$28.42 Billion Electric Steam Cracker Market to 2040" 등 시장조사 보도자료성 수치는 방법론이 확인되지 않아 근거로 사용하지 않았다.
- 한국·일본 구조조정 관련 사실관계는 언론(더밸류뉴스, 블로터, 이데일리, 서울경제, ICIS, C&EN) 출처이며 학술 문헌이 아니다 — 시의성 있는 산업 맥락으로만 사용하고, 논문의 1차 인용 근거로는 부적절함을 표시해 둔다.
