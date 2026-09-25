# CAP 인접 문헌 — PDF·원문 링크 모음 (2026-09-25)

`docs/reading_program.md`(2026-09-01)가 "무엇을 읽을지"를 정했고, 이 문서는 **어디서 받는지**와
그 이후 나온 **2025–26년 최근접 연구·연구그룹**을 보탠다. 웹 검색으로 서지와 링크를 확인했다.
이 세션의 네트워크는 Springer·Elsevier·SSRN·arXiv·Nature 도메인 직접 접속이 차단돼 있어
**링크 실동작과 OA 여부는 검색 결과 스니펫 기준**이다. "OA" 표기가 없는 항목은 기관 접속이 필요할 수 있다.

CAP 좌표(기억용): 시설 단위 MILP × 투입가 상관 몬테카를로 × (P50, TCaR) 효율경계 × 공시계획 frontier gap.
아래 각 항목의 "CAP과의 관계" 열은 이 좌표 기준이다.

---

## 0. 먼저 읽을 6편 (순서대로)

| # | 논문 | 링크 | CAP과의 관계 |
|---|---|---|---|
| 1 | **Kampmann, Rekker, Ruan, Shrimali (2026)** "Assessing corporate transition plans using a production asset-based planning approach", *Nat. Commun.* 17:6410 | [Nature OA](https://www.nature.com/articles/s41467-026-72703-2) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13376426/) · [SSRN WP](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4983999) | 최근접 선행(배출 공간). POSCO 포함 철강 10사. 비용 미모형화를 자인 → 우리 ③의 빈자리 |
| 2 | **Saleh, Battiston, Monasterolo, Barreau, Tankov (2026)** "Estimating firms' emissions from asset level data helps revealing (mis)alignment to net zero targets", *Nat. Commun.* 17:3640 | [Nature OA](https://www.nature.com/articles/s41467-026-70481-5) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13096287/) · [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5100945) | 자산 단위 상향식의 두 번째 축(Monasterolo 계열). 950+ 철강 플랜트. 역시 배출 공간 |
| 3 | **Klein, Polzin, Urbach (2026)** "Planning to fail? Credibility and financing of corporate transition plans in hard-to-abate sectors", *iScience* 29(6) | [PMC OA](https://pmc.ncbi.nlm.nih.gov/articles/PMC13264030/) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/42291270/) | **신규 발견.** 411사 전환계획 × 재무특성(레버리지·조달)이 신뢰성에 미치는 영향. 우리 ⑥ 조달부담과 직접 대화 상대 |
| 4 | **Wolf, A. (2025)** "The uncertain costs of decarbonization policies: a risk analysis for the European steel industry", *Econ. Polit. Ind.* 52(4):913–934 | [Springer](https://doi.org/10.1007/s40812-025-00343-6) · [RePEc](https://ideas.repec.org/a/spr/epolin/v52y2025i4d10.1007_s40812-025-00343-6.html) — **비OA**, 저자(André Wolf) 사본 요청 필요 | CCfD·그린리드마켓의 위험 이전("누가 위험을 떠안나"). TCaR을 손익계산서 귀속 문제로 재서술할 때의 앵커 |
| 5 | **Bălașa & Sandberg (2025)** "Pricing the green transition: An investment appraisal of Romanian low-carbon steel", *J. Ind. Ecol.* 29:1322–1334 | [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/jiec.70054) · [ResearchGate](https://www.researchgate.net/publication/392761862) | **방법론 쌍둥이.** 저탄소 철강 투자 NPV를 **10,000회 몬테카를로**로 분포화. 단일 프로젝트·경계 없음 → 우리와의 차이가 선명 |
| 6 | **Hüttel & Lehner (2024)** "Revisiting Investment Costs for Green Steel", DIW DP 2082 | [DIW PDF](https://www.diw.de/documents/publikationen/73/diw_01.c.901039.de/dp2082.pdf) · [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4816049) | CAPEX 우편향 분포·기업 대차대조표 영향. 우리 `tech_bands.csv` 계보 |

---

## 1. 2025–26 최근접 연구 (기존 문헌지도 이후)

### 1-1. 철강 자산 단위·락인·재투자 창

| 논문 | 링크 | 왜 |
|---|---|---|
| Bachorz, Dürrwächter, Gong et al. (2026) "Averting the steel carbon lock-in through strategic green investments", *Nat. Clim. Chang.* | [Nature](https://www.nature.com/articles/s41558-026-02635-8) · [Research Square 프리프린트](https://www.researchsquare.com/article/rs-8435240/v1) · [PIK](https://publications.pik-potsdam.de/pubman/faces/ViewItemOverviewPage.jsp?itemId=item_34453_1) | 1,000+ 플랜트 committed emissions ≈60 GtCO₂, 2030 이전 투자가 53% 저렴. 우리 재투자 창 가정의 외부 대조 |
| Bachorz et al. (2026) Policy Brief "The window to avoid locking in decades of steel emissions is closing fast" | [Nature](https://www.nature.com/articles/s41558-026-02634-9) · [PIK](https://publications.pik-potsdam.de/pubman/faces/ViewItemOverviewPage.jsp?itemId=item_34461_1) | 위 논문의 2쪽 요약 |
| Wu, Meng, Liang et al. (2025) "Technological pathways for cost-effective steel decarbonization", *Nature* 647:93–101 | [PMC OA](https://pmc.ncbi.nlm.nih.gov/articles/PMC12589104/) · [Nature](https://www.nature.com/articles/s41586-025-09658-9) | 전 세계 플랜트 단위 최소비용 경로. 한·일 플랜트 CCS 비용 US$26–75/t. **결정론** — 우리 위험축의 대비군 |
| Xu, Tong, Davis et al. (2023) "Plant-by-plant decarbonization strategies for the global steel industry", *Nat. Clim. Chang.* 13:1067 | [Nature](https://www.nature.com/articles/s41558-023-01808-z) · [GID 모델](http://gidmodel.org.cn/?p=1996&lang=en) | 시설 단위 배출 DB의 원조. 선진국은 age-to-capacity 지표가 유효 |
| Johnson, Åhman, Nilsson, Li (2025) "Emerging green steel markets surrounding the EU ETS and CBAM", *Nat. Commun.* | [Nature OA](https://www.nature.com/articles/s41467-025-64440-9) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12518805/) | 수소환원 철강의 경쟁력 도달 시점(2026~). 탄소가격 경로 앵커 |
| Nykvist, Gong, Algers, Åhman (2025) "Renewables pull and strategic push – What drives hydrogen-based steel relocation?", *Appl. Energy* | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0306261925009195) · [SEI](https://www.sei.org/publications/renewables-pull-and-strategic-push/) · [Lund LUP](https://lup.lub.lu.se/search/publication/20b1e6b9-a499-4e3f-acfb-23780fc1005a) | 전력가 민감도가 "이전에 알던 것보다 약하다" — 우리 전력 위험인자 크기의 대조 |
| Algers, Gong, Nykvist, Åhman (2025) "Competition and climate policy in the steel transition: Comparing costs and subsidies in the US and the EU", *Energy Policy* 198:114507 | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S030142152500014X) · [SEI](https://www.sei.org/publications/competition-and-climate-policy-in-the-steel-transition/) | 보조금 > 재생전력 비용. 우리 정책 시나리오 축 |
| Algers, Åhman, Nilsson (2025) "Steel Decarbonization—from Optimization to Transformation", *Annu. Rev. Environ. Resour.* 50 | [Annual Reviews](https://www.annualreviews.org/content/journals/10.1146/annurev-environ-111523-101851) | 철강 문헌 전체 서베이 — 인용 누락 점검용 |
| "Decarbonizing global steel production" (2026), *Nat. Rev. Earth Environ.* | [Nature](https://www.nature.com/articles/s43017-026-00786-y) | 최신 리뷰(저자 미확인). 배출계수 앵커(BF-BOF 2.3, EAF 0.68 tCO₂/t) |
| Di Bella, Seibold, Brown, Tavoni (2025) "Pursuing decarbonization and competitiveness: a narrow corridor for European green industrial transformation" | [arXiv PDF](https://arxiv.org/pdf/2510.08199) | PyPSA-Eur로 철강·HVC 동시 모형. 석화까지 포함한 드문 사례 |

### 1-2. 위험 배분·계약 (CCfD, PPA)

| 논문 | 링크 | 왜 |
|---|---|---|
| Hoogsteyn, Bruninx, Delarue (2025) "Carbon contracts for difference design: Managing carbon price risk in a low-carbon industry", *Joule* 9(5) | [KU Leuven WP PDF](https://www.mech.kuleuven.be/en/tme/research/energy-systems-integration-modeling/pdf-publications/wp-esim2023-07.pdf) · [TU Delft 리포지터리](https://research.tudelft.nl/en/publications/carbon-contracts-for-difference-design-managing-carbon-price-risk) · [Cell](https://www.cell.com/joule/abstract/S2542-4351(25)00102-3) | "어떤 설계도 탄소가격 위험을 완전히 없애지 못한다". 우리 `ccfd=0` 강제의 근거 진술 |
| Richstein & Neuhoff (2022) "Carbon contracts-for-difference: How to de-risk innovative investments for a low-carbon industry?", *iScience* | [Cell OA](https://www.cell.com/iscience/fulltext/S2589-0042(22)00972-5) | CCfD 원전. 철강 사례: 완화비용 −27%, 뱅커빌리티에 CCfD 가격의 79% 플로어 필요 |
| Fraunhofer ISI, "Carbon Contracts for Difference as …" (ECEEE Summer Study) | [Fraunhofer PDF](https://publica.fraunhofer.de/bitstreams/b3a1949c-97f6-4d69-a37d-9cb2458fb03b/download) | 회색문헌, 설계 변형 카탈로그 |
| (2026) "Mitigating business risks from renewable PPA power sourcing uncertainties for European green hydrogen production" | [arXiv PDF](https://arxiv.org/pdf/2606.13215) | PPA 불확실성 → 수소 원가. 우리 수소 = f(전력, 전해조 CAPEX) 구조식의 옆동네 |

### 1-3. 기업 단위 전환위험 측정·자금조달

| 논문 | 링크 | 왜 |
|---|---|---|
| Fliegel (2026) "How you measure transition risk matters", *J. Corp. Finance* 98 | [GRASFI WP PDF](https://sustainablefinancealliance.org/wp-content/uploads/2024/08/Fliegel_2024_Transition-Risk-Metric-Evaluation_vSSRN_8_8_24.pdf) · [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S092911992500207X) | 배출량·E스코어 기반 지표는 전환위험 충격에 반응 안 함, **택소노미 CAPEX 정합**은 반응. 우리 "비용·위험 공간" 주장의 재무학 측 근거 |
| Fliegel (2025) "How (Not) to Measure Companies' Climate Transition Risk: A Framework and Categorized Literature Review", *CSR Env. Mgmt.* | [Wiley OA](https://onlinelibrary.wiley.com/doi/full/10.1002/csr.3094) | 전환위험 측정법 분류 리뷰 — 우리 TCaR을 어디에 놓을지 |
| Zhang, Wirjanto, Porth, Tan (2025) "Strategic Investment to Mitigate Transition Risks" | [arXiv PDF](https://arxiv.org/pdf/2501.02383) · [Waterloo PDF](https://uwaterloo.ca/ctr-sustainability-performance-management/sites/default/files/uploads/documents/strategic-investment-to-mitigate-transition-risks.pdf) | 다기간 기업 투자 × 4개 전환속도 시나리오. 우리 시나리오 축의 보험수리 판 |
| Noera & Versini (2026) *Cost of Capital, Climate Risks and Corporate Transition Plans: The empirical evidence*, ECCO 기술보고서 | [ECCO PDF](https://eccoclimate.org/wp-content/uploads/2026/02/Cost-of-capital-climate-risks-and-transition-plans_technical-report.pdf) | 전환계획 → 자본비용 실증 정리. ⑥ 조달부담을 할인율로 연결할 때 |
| Pichler (2024) "Transition dynamics of electricity asset-owning firms" | [arXiv PDF](https://arxiv.org/pdf/2412.11597) | 14만 건 자산 투자로 본 기업 내 기술전환의 희소성(<3%). "기업 내부 좌표"가 왜 필요한지의 실증 |
| "Too Fast to Transition? Decarbonization Speed, Profitability, and Corporate Default Risk" (2026) | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1059056026006192) | "안전속도 회랑" — 너무 빠른 전환도 부도위험. 우리 frontier gap의 반대편 해석 |
| Daumas (2024) "Financial stability, stranded assets and the low-carbon transition – A critical review", *J. Econ. Surv.* 38:601–716 | [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1111/joes.12551) | 좌초자산 문헌 116쪽 서베이. 위치 설정용 |
| AbdulRafiu (2026) "Stranded futures? Quantifying the asset risks of industrial decarbonisation in developed economies", *ERSS* 133:104621 | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2214629626000927) — 비OA | 철강·화학 포함 5업종 × 한국·일본 포함 6개국. 우리 4사 대상과 정확히 겹침 |

### 1-4. 전환계획 신뢰성 프레임

| 논문 | 링크 | 왜 |
|---|---|---|
| Kampmann, Rose, Shrimali (2023) *Assessing the Credibility of Climate Transition Plans in the Steel Sector*, Oxford SSEE DP | [Oxford PDF](https://sustainablefinance.ox.ac.uk/wp-content/uploads/2023/07/SSEE-Discussion-Paper-Steel_final_AR.pdf) | 문헌지도 §5에서 "텍스트 추출 실패"로 남았던 것. 링크 확인됨 |
| Rekker, Hofmann-Riem, Kampmann, Rose, Shrimali (2025) "Assessing the Compatibility of Transition Plans with Equity Principles" | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5427235) | 같은 그룹의 후속 |
| Oxford BSG (2026-06) *Varieties of Green Transition Planning*, Working Paper | [BSG PDF](https://www.bsg.ox.ac.uk/sites/default/files/2026-06/Varieties%20of%20Green%20Transition%20Planning%20-%20Working%20Paper%20-June2026.pdf) | 국가별 전환계획 제도 비교 |
| Nicolajsen, Bjørn, McAloone, Pigosso (2025) "Decoding corporate climate transition plans: A comparative analysis of 14 frameworks", *J. Env. Manage.* 393 | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5167369) · [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0301479725030385) | 13 구성요소·38 하위요소 — "자본배분" 항목이 어디에 있는지 |
| (2026) "Do credible climate transition plans matter for carbon performance? Evidence from Fortune Global 500", *Front. Env. Sci.* | [Frontiers PDF](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2026.1907357/pdf) | 신뢰성 지수 × 실제 배출 실적 |
| TPI Centre (2025) *State of the Corporate Transition 2025* | [TPI PDF](https://transitionpathwayinitiative.org/publications/uploads/2025-state-of-the-corporate-transition-2025.pdf) · [LSE eprints](https://eprints.lse.ac.uk/130118/) | 2,000사 평가. Dietz 접근용 |
| Global Energy Monitor (2026) *Pedal to the Metal 2026* | [GEM PDF](https://globalenergymonitor.org/sites/default/files/2026-05/Pedal%20to%20the%20Metal%202026.pdf) | 1,293 플랜트 자산 DB 최신판. D1a `last_reline_year` 강화 경로(백로그 G7) |
| Agora Industry · Wuppertal · Lund (2024) *Low-carbon technologies for the global steel transformation* | [Agora 다운로드 페이지](https://www.agora-industry.org/publications/low-carbon-technologies-for-the-global-steel-transformation) · [Wuppertal OPUS](https://epub.wupperinst.org/frontdoor/index/index/year/2024/docId/8559) | 8개 기술의 생산비·감축비용 — `validation_external.md` §5 LCOA 앵커 공백 |

### 1-5. 한국·일본 맥락

| 논문 | 링크 | 왜 |
|---|---|---|
| (2026) "From industrialization to industrial decarbonization: Divergent steel decarbonization pathways in South Korea and Germany", *ERSS* | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2214629626003282) · [Tufts CPL 요약](https://www.climatepolicylab.org/climatesmart/2026/7/24/what-drives-the-green-steel-transition) | 한국 H2-DRI 실증펀드(2026~) 등 제도 비교. 논문 §정책맥락 |
| Jeon, Kiyong (2026) "Low-Carbon Investment, Incumbent Retirement, and Transitional Overcapacity in Steel" | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7368899) | **신규.** 저탄소 설비 확대 vs 기존 설비 퇴출 속도 → 과잉설비. 우리 폐쇄상한(closure cap) 시나리오의 거시 판 |
| Lim, Chansu (2026) "Naphtha Feedstock Lock-in in Korean Manufacturing", 2016–2022 | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7102727) | 한국 석화 원료 락인 — LOTTE 쪽 배경 |
| Fitriasari et al. (2025) "Decarbonization Strategies in Naphtha Cracking: Insights from South Korea", *ACS Sustain. Chem. Eng.* 13:9913 | [ACS](https://pubs.acs.org/doi/10.1021/acssuschemeng.4c09854) | NCC 대안 기술 메뉴·CAC(블루암모니아 50% 혼소 $88/t) |
| Fukuda & Ino (2026) "Fiscal sustainability of transition finance: Implications for the GX economy transition bonds in Japan" | [CIRJE DP PDF](https://www.cirje.e.u-tokyo.ac.jp/research/dp/2026/2026cf1268.pdf) | GX 채권 상환 구조 — Nippon Steel·Mitsui 조달 환경 |
| Park, Hyejin (2026) "Carbon Markets and the Direction of Green Innovation: Evidence from Korea's ETS" | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7013522) | K-ETS 노출 → 순수 녹색혁신 감소. 우리 탄소가격 변동성(36.3%) 서술의 옆 근거 |
| 기후솔루션(SFOC) *수소환원제철 상용화 정부 재원 마련 방안: 해외 정부 재정 개입과 위험 분담 구조* | [SFOC](https://forourclimate.org/ko/research/634) | **한국어, 위험 분담 구조 정면** — Wolf 2025의 한국판 대화 상대 |
| 기후솔루션 *NCC 전기화 감축 경로·비용* | [SFOC](https://forourclimate.org/research/633) | 석화 감축비용 국내 앵커 |
| SteelWatch (2025) *No Time For Caution — Nippon Steel Corporate Climate Assessment* | [SteelWatch PDF](https://steelwatch.org/wp-content/uploads/2025/05/250507_NS_CCA_EN.pdf) | Nippon Steel 공시계획의 외부 평가 |
| Nippon Steel (2025) *GX Initiatives* IR 자료 | [NSC PDF](https://www.nipponsteel.com/en/ir/library/pdf/20250313_100.pdf) | 1차 공시 — CAPEX 4–5조엔 |

---

## 2. 방법론 원전 — PDF 직접 링크

| 논문 | PDF |
|---|---|
| Rockafellar & Uryasev (2000) "Optimization of Conditional Value-at-Risk", *J. Risk* 3:21–41 | [UFL PDF](https://www.ise.ufl.edu/uryasev/cvar.pdf) · 대안: [Uryasev 강의노트 PDF](https://www2.mathematik.hu-berlin.de/~romisch/SP01/Uryasev.pdf) |
| Battiston, Mandel, Monasterolo, Schütze, Visentin (2017) "A climate stress-test of the financial system", *Nat. Clim. Chang.* 7:283 | [Stanford EMF PDF](https://web.stanford.edu/group/emf-research/docs/sm/2019/wk2/battiston.pdf) · [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2726076) |
| Dietz, Bowen, Dixon, Gradwell (2016) "'Climate value at risk' of global financial assets", *Nat. Clim. Chang.* 6:676 | [LSE PDF](https://researchonline.lse.ac.uk/id/eprint/66226/1/Dietz_Climate%20Value%20at%20risk.pdf) |
| Roques, Newbery, Nuttall (2008) "Fuel mix diversification incentives…: A Mean-Variance Portfolio theory approach", *Energy Econ.* 30:1831 | [EPRG WP 0626](https://ideas.repec.org/p/enp/wpaper/eprg0626.html) · [Open Univ. ORO](https://oro.open.ac.uk/35424) |
| Ehrenmann & Smeers (2011) "Generation capacity expansion in a risky environment", *Oper. Res.* 59:1332 | [Springer 장 PDF(동일 저자 확장판)](https://webhomes.maths.ed.ac.uk/mckinnon/blackouts/StochOptFinanceAndEnergySpringer/Chap13_SmeersCapacityExpansion.pdf) · [Semantic Scholar PDF](https://pdfs.semanticscholar.org/04ad/fc46b9089eac44203cca4a3b3c9a1df994ab.pdf) |
| Bruno, Ahmed, Shapiro, Street (2016) "Risk neutral and risk averse approaches to multistage renewable investment planning", *EJOR* 250:979 | [PUC-Rio LAMPS](https://www.lamps.ind.puc-rio.br/en/publicacao/risk-neutral-and-risk-averse-approaches-to-multistage-renewable-investment-planning-under-uncertainty/) · [Shapiro 출판목록](https://sites.gatech.edu/alexander-shapiro/publications/) |
| Fuss, Szolgayova, Obersteiner, Gusti (2008) "Investment under market and climate policy uncertainty", *Appl. Energy* 85:708 | [IIASA PURE](https://pure.iiasa.ac.at/view/iiasa/101.html) (저자 페이지에서 항목 검색) |
| Kesicki & Ekins (2012) "Marginal abatement cost curves: a call for caution", *Clim. Policy* 12:219 | [T&F](https://www.tandfonline.com/doi/full/10.1080/14693062.2011.582347) · 보완: Vogt-Schilb & Hallegatte, "MACC and the optimal timing of mitigation" [World Bank PDF](https://openknowledge.worldbank.org/server/api/core/bitstreams/b5d947dc-0ea5-5036-ab77-a29679675253/content) |
| van der Ploeg & Rezai (2020) "Stranded Assets in the Transition to a Carbon-Free Economy", *Annu. Rev. Resour. Econ.* 12:281 | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3716735) · [VU 리포지터리](https://research.vu.nl/en/publications/stranded-assets-in-the-transition-to-a-carbon-free-economy) |
| Vogl, Olsson, Nykvist (2021) "Phasing out the blast furnace to meet global climate targets", *Joule* 5:2646 | [Cell OA](https://www.cell.com/joule/fulltext/S2542-4351(21)00435-9) · [SEI](https://www.sei.org/publications/phasing-out-blast-furnace-climate-targets/) |
| Xu, Wang, Jiang, Yu, Wei (2024) "Optimum investment strategy for hydrogen-based steelmaking project coupled with multiple uncertainties", *J. Env. Manage.* 356:120484 | [PubMed](https://pubmed.ncbi.nlm.nih.gov/38522276/) — 비OA. 저자: 北京理工大 CEEP |
| Lee, Hwarang (2023) "Decarbonization strategies for steel production with uncertainty in hydrogen direct reduction", *Energy* | [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0360544223024519) · [ResearchGate](https://www.researchgate.net/publication/373853616) — 비OA |

---

## 3. 이 문헌을 모으고 있는 연구그룹 (팔로우 대상)

| 그룹 | 핵심 인물 | 무엇을 모으나 | 진입점 |
|---|---|---|---|
| **Oxford Sustainable Finance Group** — Net Zero Transition Plans 프로그램 | Gireesh Shrimali, David Kampmann, Adrien Rose(→LSE), Saphira Rekker(UQ) | 업종별 전환계획 신뢰성 DP 시리즈(철강·석유가스·전력·항공·해운), APA 오픈소스 | [프로그램 페이지](https://sustainablefinance.ox.ac.uk/net-zero-transition-plans/) · [CGFI 미러](https://cgfi.ac.uk/transition-risk/net-zero-transition-plans/) |
| **Utrecht Copernicus + UZH + CREST/ENSAE** | Irene Monasterolo, Stefano Battiston, Friedemann Polzin, Peter Tankov, Hamada Saleh | 자산 단위 상향식 배출·정합, 기후 스트레스테스트, 전환계획 × 자금조달 | [Battiston 출판목록](https://www.df.uzh.ch/en/people/professor/battiston/publications.html) · [Tankov 출판목록](https://sites.google.com/site/petertankov/publications) |
| **Lund EESS + SEI** | Max Åhman, Lars J. Nilsson, Jonas Algers, Björn Nykvist, Jindan Gong, Valentin Vogl | 철강 전환 경제학 전체(비용·입지·정책·시장) — 가장 많이 쏟아내는 그룹 | [Åhman 포털](https://portal.research.lu.se/en/persons/max-%C3%A5hman/) · [SEI 철강](https://www.sei.org/publications/) |
| **PIK Energy Transition Lab** | Clara Bachorz, Jindan Gong, Falko Ueckerdt | 철강 락인·committed emissions·투자 타이밍 | [PIK 출판목록](https://www.pik-potsdam.de/en/institute/labs/energy-transition/publications) |
| **DIW Berlin Climate Policy** | Karsten Neuhoff, Jörn Richstein, Alexandra Hüttel, Judith Lehner | CCfD 설계 원전, 그린스틸 CAPEX, 기업 대차대조표 | [DIW DP 시리즈](https://ideas.repec.org/s/diw/diwwpp.html) |
| **KU Leuven ESIM / TU Delft** | Erik Delarue, Kenneth Bruninx, Alexander Hoogsteyn | CCfD 설계 × 탄소가격 위험 | [ESIM WP](https://www.mech.kuleuven.be/en/tme/research/energy-systems-integration-modeling/pdf-publications/) |
| **TPI Centre @ LSE Grantham** | Simon Dietz | 기업 전환 상태 연례 평가, Carbon Performance 방법론 | [TPI 출판](https://www.transitionpathwayinitiative.org/publications?tags=State+of+Transition&types=Publications) |
| **GRASFI (Global Research Alliance for Sustainable Finance)** | — | 지속가능금융 워킹페이퍼 큐레이션(Fliegel 등) — 전환위험 측정 논문이 여기 먼저 뜬다 | [GRASFI 논문 목록](https://sustainablefinancealliance.org/) |
| **Global Energy Monitor** | — | GIST 자산 DB, 연례 Pedal to the Metal | [GEM 철강](https://globalenergymonitor.org/research/pedal-metal-2026) |
| **Agora Industry + Wuppertal** | — | 기술별 LCOS·감축비용, Global Steel Transformation Tracker | [Tracker](https://www.agora-industry.org/data-tools/global-steel-transformation-tracker) |
| **기후솔루션(SFOC)** | — | 한국 철강·석화 감축비용·재원·위험분담 보고서 | [연구 목록](https://forourclimate.org/ko/research) |
| **Transition Asia · SteelWatch** | — | POSCO·Nippon Steel 공시계획 외부 평가, 일본 정책 리뷰 | [Transition Asia](https://transitionasia.org/) · [SteelWatch](https://steelwatch.org/) |
| **Tufts Climate Policy Lab** | — | 한국·독일 그린스틸 정책 비교 | [CPL](https://www.climatepolicylab.org/) |
| **Tsinghua GID / UCL Bartlett / UMD** | Ruochong Xu, Dan Tong, Jing Meng | 글로벌 플랜트 단위 배출·비용 DB | [GID 모델](http://gidmodel.org.cn/) |

---

## 4. 이번 검색으로 문헌지도가 바뀌어야 할 곳

1. **주장 ③ "비용·위험 공간은 우리가 처음"** — 여전히 반례 없음. 다만 Bălașa & Sandberg (2025)가
   저탄소 철강 투자를 10,000회 몬테카를로로 분포화했다. 단일 프로젝트 NPV이고 계획집합·경계·공시계획
   참조점이 없어 ③은 유지되나, "확률적 비용 분포 자체"는 이제 **부분 있음**으로 내려야 한다.
2. **⑥ 조달부담** — Klein, Polzin, Urbach (2026)가 411사에서 재무특성과 전환계획 신뢰성을 연결했다.
   방향은 반대(재무 → 신뢰성)지만 같은 변수를 다룬다. 논문 §2에 인용 필수.
3. **Wolf 2025** — 비OA 확정. 저자 사본 요청이 실제 경로다.
4. **Kampmann 2023 SSEE DP** — PDF 링크 확인됨. `data_gap_registry.md`의 "텍스트 추출 실패" 항목을 재시도.
5. **Fliegel (2026)** — "택소노미 CAPEX 정합이 전환위험 충격에 반응하고 배출량은 반응하지 않는다"는
   결과는 우리가 배출 공간이 아니라 **자본배분 공간**에서 잰다는 선택의 재무학 측 근거다.

## 5. 못 찾은 것 (정직하게)

- 몬테카를로·시설 단위·한국 철강을 셋 다 갖춘 국내 학술논문은 검색되지 않았다. 국내는 정책보고서(SFOC, 산업부) 층이다.
- *Nat. Rev. Earth Environ.* 2026 철강 리뷰와 "Too Fast to Transition?" 2026의 저자 명단은 스니펫에서 확인 못 함.
- Material Economics / MPP LCOA 원전은 이번에도 미시도 (Agora 2024가 대체 후보).
