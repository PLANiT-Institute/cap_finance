# L2 — 상방 꼬리(비용 폭발) 정량화: FOAK 초과율, CAPEX 팻테일, 에너지가 급등, 철강 vs 석화

맥락: L1에서 전환비용 분포가 두 꼬리 비대칭(상방=CAPEX·에너지 폭발, 하방=탄소가 붕괴로 좌초)임을 확인. 본 문서는 상방 꼬리의 크기와 형태, 섹터 차이를 다룬다. 모든 항목은 WebSearch로 실제 확인한 것만 기재하고, 확인 못한 추정치는 "## 미확인"에 별도 표시했다.

---

## FOAK 초과율 분포의 정량

### 참조집단(발전 인프라, Flyvbjerg/Ansar 데이터베이스)

Flyvbjerg의 약 16,000개 프로젝트(136개국) 데이터베이스 중 401개 발전·송전 프로젝트(57개국) 분석 기준, 기술별 평균 비용 초과율:

- **원자력: +120%** (한 버전에서는 +122%)
- **수력댐: +75%** (다른 분석에서는 +96%)
- **화력(석탄·가스·오일·디젤): +16%** (다른 분석에서는 +31%)
- **풍력: +13%**
- **송전선: +8%**
- **태양광: +1%**

401개 프로젝트 중 4분의 3이 비용을 과소추정했고, 초과·미달이 전혀 없는 프로젝트는 39개뿐이었다.
[Flyvbjerg, B. et al., "Construction Cost Overruns and Electricity Infrastructure: An Unavoidable Risk?", ScienceDirect | https://www.sciencedirect.com/science/article/abs/pii/S1040619014000761] [Ansar, A. et al. (2014), "Should we build more large dams? The actual costs of hydropower megaproject development" | https://arxiv.org/pdf/1409.0002]

### 산업 메가프로젝트 참조집단 (Merrow/IPA)

Merrow(2011)의 318개 산업 메가프로젝트(정유·화학·금속·가스전 등) 분석: 약 66%가 예산·일정을 25% 이상 초과. "절반 이상이 형편없는 결과"(대규모 초과·장기 지연·낮은 가동률)로 요약된다.
[Merrow, E.W. (2011), *Industrial Megaprojects: Concepts, Strategies, and Practices for Success* | https://www.ipaglobal.com/resources/books/industrial-megaprojects-2nd-edition-ed-merrow/]

### 소형모듈원자로(SMR) — FOAK 참조집단으로서

다중모듈 원전 플랜트가 공기 지연에 가장 취약했고, 소형모듈 BWR이 가장 덜 취약했다. 다만 **최초(FOAK) 호기는 비용·일정 초과 중앙값 약 +130%**이며, 마지막(뒤에 지어진) 호기는 점진적으로 초과율이 줄어든다.
[ScienceDirect, "Construction schedule and cost risk for large and small light water reactors" | https://www.sciencedirect.com/science/article/pii/S0029549323001541]

### 전환 설비별 — 실제 확인된 사례

- **CCUS 결합 IGCC (Kemper County, 미국)**: 최초 견적 $2.8~2.9B → 최종 $7.5~7.8B (일부 보도는 $9B까지). 즉 원 견적 대비 **약 +160~180%** 초과(가장 보수적 계산도 +150% 이상). 사업은 결국 CCS 없이 가스발전으로 전환되며 사실상 취소됨.
  [MIT Sequestration, "Kemper County IGCC" | https://sequestration.mit.edu/tools/projects/kemper.html] [Forbes, "The Largest Clean Coal Power Plant In America Turns To Natural Gas" | https://www.forbes.com/sites/jamesconca/2017/07/11/the-largest-clean-coal-power-plant-in-america-turns-to-natural-gas/]
- **CCS 레트로핏 (Boundary Dam 3, 캐나다)**: 최초 견적 $1.2B → 최종 $1.47B, **약 +22.5%** 초과. SaskPower는 이 초과가 CCS 자체보다 50년 노후 석탄 보일러 레트로핏 이슈에 더 기인한다고 밝힘 — 즉 같은 "CCS" 항목 안에서도 그린필드 vs 레트로핏 여부에 따라 초과율이 크게 갈린다(+22% vs +160%대).
  [Global Energy Monitor, "Boundary Dam Integrated Carbon Capture & Storage Demonstration Project" | https://www.gem.wiki/Boundary_Dam_Integrated_Carbon_Capture_%26_Storage_Demonstration_Project]
- **H2-DRI 철강 (Stegra/H2 Green Steel, 스웨덴 보덴)**: 정확한 초과율(%) 수치는 확인하지 못했으나, 수소플랜트·환원철플랜트·제강·수처리 설비 전반에서 비용 초과가 발생해 **$1B 이상의 자금 경색**과 €975M 추가 조달 필요 상태에 이름. 생산 목표(2025)는 반복 지연.
  [Canary Media, "Europe's flagship green-steel project gets a financial lifeline" | https://www.canarymedia.com/articles/green-steel/europes-flagship-green-steel-project-gets-a-financial-lifeline-stegra-hy24] [OECD, "Stegra (formerly H2 Green Steel) Case Study 2024" | https://www.oecd.org/content/dam/oecd/en/about/programmes/cefim/green-hydrogen/update-case-studies/H2-Green-Steel-Case-Study-2024.pdf]
- **그린수소 프로젝트 일반**: 전해조 비용은 2021년 이후 **+20~45%** 상승했고, IEA는 2030년까지 하락폭도 기존 전망보다 완만한 **-15~30%**로 하향 조정(즉 팻테일이 코스트 커브 자체를 밀어올림). 다만 이는 개별 프로젝트의 견적 대비 실적 초과율이 아니라 산업 전체 코스트 커브의 상방 이동임에 유의.
  [Argus Media, "IEA raises 2030 renewable H2 cost estimates" | https://www.argusmedia.com/en/news-and-insights/latest-market-news/2614112-iea-raises-2030-renewable-h2-cost-estimates] [IEA, Global Hydrogen Review 2024, "Investment, finance and innovation" | https://www.iea.org/reports/global-hydrogen-review-2024/investment-finance-and-innovation]

### 초과율 분포의 형태 (로그정규 vs 멱함수)

- IT 프로젝트 비용 초과는 **멱함수(power-law) 분포**를 따른다 — 다수의 소규모 초과 + 소수의 극단적 초과로 이뤄진 팻테일. 관리자가 이를 정규분포로 오인하면 극단 리스크를 심각하게 과소평가한다.
  [Flyvbjerg, B. et al. (2022), "The Empirical Reality of IT Project Cost Overruns: Discovering A Power-Law Distribution", *Journal of Management Information Systems* | https://arxiv.org/pdf/2210.01573]
- 올림픽 개최비용 초과 데이터는 **멱함수와 로그정규 분포 모두 적합**하며, 둘 다 팻테일이다. 올림픽 비용은 (멱함수 지수가 낮아) **평균·분산이 발산(infinite mean and variance)**하는 영역에 있다고 추정됨 — 예측 가능성 자체가 무너지는 수준.
  [Flyvbjerg, B., Budzier, A., Lunn, D. (2021), "Regression to the tail: Why the Olympics blow up", *Environment and Planning A* | https://journals.sagepub.com/doi/full/10.1177/0308518X20958724]
- 대형 댐: 10건 중 2건은 실제비용이 최초 견적의 2배를 초과, 10건 중 1건은 3배를 초과 — 명백한 팻테일.
  [Ansar et al. (2014), 위 arxiv 링크]
- 최초계획 대비 착공시점 비용 변화 분포는 **오른쪽으로 심하게 치우친(skewed) 팻테일**이며 최빈값은 0 부근이다 — 즉 "보통은 안 튀지만, 튀면 크게 튄다"는 형태.
  [ScienceDirect, "Cost overruns of infrastructure projects – distributions, causes and remedies" (관련 diva-portal 요약) | https://www.diva-portal.org/smash/get/diva2:1971277/FULLTEXT01.pdf]

---

## CAPEX 팻테일 원천

### 초도 설비 낙관편향 (Merrow)

Merrow는 산업 메가프로젝트 실패의 근본 원인으로 낙관적 견적·전략적 저평가·설계 미성숙 상태에서의 조기 확정(FEED 이전 예산 확정)을 지목한다. 318개 프로젝트의 66%가 예산·일정을 25% 이상 초과한 것은 무작위 오차가 아니라 **체계적 편향**의 결과로 해석된다.
[Merrow (2011), 위 링크; PMI, "From Nobel Prize to project management" | https://www.pmi.org/learning/library/nobel-project-management-reference-class-forecasting-8068]

### 규모·복잡도와 컨틴전시

전해조의 경우 EPC(설계·조달·시공)와 컨틴전시가 설치 자본비의 **절반 이상**을 차지할 수 있다는 점이 확인됨. 스택 자체는 설치비의 15~20%에 불과하고 25~30%는 BOP(전력전자·배관·압축기·가스처리)다 — 즉 "스택 기술 발전"만으로는 총 CAPEX 팻테일을 줄이는 데 한계가 있고, EPC·BOP·컨틴전시 쪽이 초과율의 실제 진원지다.
[NREL/IEA 인용, "Updated Manufactured Cost Analysis for PEM..." 및 IEA 2025 전해조 비용 구성 | https://docs.nrel.gov/docs/fy24osti/87625.pdf]

**주의**: "FOAK 대비 NOAK 컨틴전시 150%"라는 구체적 수치는 이번 검색에서 확인하지 못했다(미확인 항목 참조). 확인된 것은 EPC+컨틴전시가 전해조 설치비의 "절반 이상"이라는 정성적 사실뿐이다.

### 전환 설비의 모듈성 스펙트럼 — 신테일 vs 팻테일

- **전해조**: 스택 단위는 모듈형(컨테이너·스킷 단위로 복제 가능)이나, BOP·배관·컨플라이언스는 부지별 커스텀. 즉 "부분적 모듈형" — SMR과 유사하게 반복생산에 의한 학습효과 기대는 있으나 **아직 첫 상업 규모 호기가 없어 검증되지 않음**.
  [ScienceDirect, SMR 관련 "anticipated cost reductions are greatest for SMRs... though the first SMR has yet to be built" | https://www.sciencedirect.com/science/article/pii/S0029549323001541]
- **H2-DRI 플랜트(전해조+DRI샤프트+EAF 통합)**: 커스텀 대형 통합 공정 — 신규 부지에 수전해·환원철·제강·수처리를 동시에 짓는 그린필드 메가프로젝트. Stegra 사례가 보여주듯 여러 서브시스템(수소플랜트·DRI플랜트·제강·수처리)에서 **동시다발적** 초과가 발생 — 이는 팻테일형(커스텀 대형공정) 리스크 프로파일에 해당.
  [Canary Media, 위 링크]
- **e-cracker(전기가열 스팀크래커)**: 현재까지는 **6MW급 데모 플랜트**(BASF·SABIC·Linde, 루드비히스하펜) 수준이며, 상업 규모(500MW+)로의 스케일업 실적은 아직 없음. 기존 크래커에 대한 "레트로핏" 개념(노(furnace)만 전기화, 나머지 공정은 기존 자산 재사용)이 핵심 — 이는 Boundary Dam형(기존 자산 부분 개조) 리스크 프로파일에 가깝다. Shell·Dow도 암스테르담에서 별도 레트로핏 실험 유닛 가동.
  [SABIC, "BASF, SABIC and Linde start Construction..." | https://www.sabic.com/en/news/36814-basf-sabic-and-linde-start-construction-of-the-worlds-first-large-scale-electrically-heated-steam-cracker-furnaces] [Linde Engineering, "It's Electrifying! Steam Crackers Go Electric" | https://www.linde-engineering.com/products-and-services/success-stories/2024/it-is-electrifying-steam-crackers-go-electric]

### 모듈성과 팻테일의 일반 관계 (Big is Fragile)

Flyvbjerg·Ansar의 "Big is Fragile" 논지: 대형·커스텀 자본투자는 장기 게스테이션·이행 기간 동안 불확실성에 **비선형적으로(과도하게)** 노출되어 팻테일 실패를 만든다. 반대로 태양광·풍력처럼 **모듈형·반복설계** 프로젝트는 소규모·빠른 반복(iteration)을 통해 학습하므로 압도적으로 우수한 성과를 낸다. 메가프로젝트의 99.5%가 예산·일정·편익 중 하나 이상에서 실패한다는 것이 이 연구의 헤드라인 수치.
[Ansar, A., Flyvbjerg, B., Budzier, A., Lunn, D. (2016), "Big Is Fragile: An Attempt at Theorizing Scale" | https://arxiv.org/pdf/1603.01416] [HBR, "Make Megaprojects More Modular" | https://hbr.org/2021/11/make-megaprojects-more-modular]

---

## 에너지가 급등 기여

### H2-DRI의 수소가 민감도

H2-DRI 통합 제철소에서 **환원+가열 모두에 수소를 쓸 경우** 손익분기 수소조달가는 **$1.63/kg 이하**여야 하고, **환원에만 수소를 쓸 경우** **$1.70/kg**에서 경제성이 확보된다(각각 CO2 배출 85%, 76% 감축 시나리오). NG-DRI에서 가열용만 수소로 대체하는 경우는 **$1.06~1.19/kg**의 낮은 수소가에서도 손익분기.
민감도 분석 결과, **손익분기 LCOH는 천연가스(NG) 가격에 매우 민감**하다 — NG 가격이 높은 지역(매사추세츠·캘리포니아)일수록 손익분기 LCOH가 올라가고, NG가 저렴한 지역(텍사스·오클라호마)일수록 손익분기 LCOH가 낮아짐. 즉 H2-DRI의 상방 리스크는 수소가 자체뿐 아니라 **경쟁재(NG) 가격과의 스프레드**에 좌우된다.
[NCBI/PMC, "The Role of Hydrogen in Decarbonizing U.S. Iron and Steel Production" | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11924224/]

### 에너지가 vs CAPEX의 상방 기여 비중

이번 검색에서 "상방 꼬리 안에서 에너지가 기여분 대 CAPEX 기여분"을 직접 분해한 정량 연구는 확인하지 못했다(미확인 항목 참조). 다만 간접 증거:
- 그린수소 산업 전체의 LCOH 상방 이동은 **전해조 CAPEX 상승(+20~45%)**과 **BOP 비용 상승**이 동시에 작용한 결과로 보도됨 — 순수 전력가 상승만이 아니라 설비비 상승이 함께 LCOH를 밀어올렸다.
  [Argus Media, 위 링크]
- 유럽에서 그린수소의 미보조 LCOH(€4~7/kg)와 산업 구매자가 지불 의사(<€3/kg)의 격차가 "프로젝트 모델이 가정했던 것보다 넓고 지속적"이라는 서술은, 에너지가(전력가)와 CAPEX 상승이 결합해 손익분기를 예상보다 훨씬 밀어냈음을 시사.
  [Energy Solutions, "Green Hydrogen Production Costs 2026" | https://energy-solutions.co/articles/sub/green-hydrogen-production-costs]

---

## 철강 vs 석화 상방 차이

| 항목 | 철강 (H2-DRI) | 석화 (e-cracker) |
|---|---|---|
| 설비 성격 | 그린필드 대형 통합공정(수전해+DRI+EAF) — 커스텀 | 기존 크래커 노(furnace)만 전기화하는 레트로핏 가능성 — 부분 모듈형 |
| 상업 규모 실적 | 없음(Stegra가 최초 상업 규모 시도, 자금 위기 진행 중) | 없음(6MW 데모가 최대, 상업 규모 미검증) |
| 참조집단 근접성 | 원자력·대형 IGCC-CCS(Kemper, +150~180%)에 가까움 — 신규 대형·통합·커스텀 공정 | Boundary Dam형 레트로핏(+22.5%)에 가까울 잠재력 — 단, 노(furnace) 교체가 공정 전체 통합에 미치는 영향은 미검증 |
| 서브시스템 리스크 중첩 | 수소플랜트·DRI플랜트·제강·수처리 4개 서브시스템이 각각 초과 리스크를 가지며 **동시 발생 시 누적** | 크래커 자체는 기존 자산이므로 신규 리스크는 전기가열 모듈 부분에 국한 — 리스크 표면적이 좁음 |
| 잠정 판단 | **상방 꼬리가 더 두껍다**: 서브시스템 다중 통합 + 그린필드 + 참조집단(원자력/IGCC급) 근접 | 상방 꼬리가 상대적으로 얇을 가능성: 리스크가 노 교체 모듈에 국한, 다만 상업 규모 실증이 없어 **불확실성 자체는 큼**(꼬리 두께를 판단할 데이터 부족) |

이 비교는 **직접적으로 철강 vs 석화 상방 꼬리를 계량 비교한 논문을 찾지 못했다는 전제 하의 추론**이다 — 위 표의 "잠정 판단" 행은 참조집단 유비(analogy)에 기반한 것이며, 두 섹터 모두 상업 규모의 실제 초과율 데이터가 아직 없다는 점이 근본적 한계다(미확인 항목 참조).

---

## 상방 꼬리 측정법

### 팻테일 계량화 방법

- **분포 적합(fitting)**: 멱함수 vs 로그정규 분포를 후보로 놓고 최대우도추정(MLE)으로 꼬리지수(α, tail index)를 추정. α가 낮을수록 꼬리가 두껍고 극단값 위험이 큼 — Flyvbjerg 올림픽 연구에서 α값이 낮아 평균·분산이 사실상 발산하는 영역으로 추정됨.
  [Flyvbjerg et al. (2021), 위 링크; arxiv 2210.01573 (IT 프로젝트 멱함수)]
- **상방 CVaR/ES(조건부 꼬리 기댓값)**: 초과율 분포의 상위 X%(예: 상위 10%) 구간의 조건부 평균을 계산해 "꼬리가 실현될 때 평균적으로 얼마나 튀는가"를 포착. 검색 범위 내에서 CAP류 전환비용 분포에 CVaR을 직접 적용한 논문은 확인하지 못했으나(미확인), NGFS는 거시 전환비용 시나리오에서 "꼬리 리스크"를 분포 상위 구간(예: 2100년 GDP손실 중심 30% vs 꼬리 50%)으로 명시적으로 구분해 보고한다 — 방법론적 유비로 참고 가능.
  [Green Central Banking, "NGFS scenarios foresee climate hit to global growth" | https://greencentralbanking.com/2025/05/15/ngfs-scenarios-foresee-climate-hit-to-global-growth-before-2030/]
- **왜도(skewness)**: 최초계획 대비 착공시점 비용 변화 분포가 최빈값 0 부근에 오른쪽 꼬리를 가진 것으로 보고됨 — 왜도가 양(+)이며 큰 값을 가짐을 시사(구체적 왜도 수치는 확인하지 못함).
  [diva-portal, 위 링크]

### 참조집단 예측으로 상방 보정하는 법 (Reference Class Forecasting)

Flyvbjerg의 준거집단예측(RCF) 3단계:
1. 통계적으로 유의미하되 진짜 비교 가능한 **준거집단**을 식별(예: "화력발전" vs "원자력" vs "대형 커스텀 화학공정").
2. 그 준거집단의 **초과율 확률분포**를 구축(정규분포 가정 금지 — 팻테일 반영).
3. 대상 프로젝트를 준거집단 분포에 대입해 **낙관편향 보정폭(uplift)**을 산정, 기본 견적에 리스크 컨틴전시로 가산.
영국 재무부·교통부는 2004년부터 이 방법을 대형 교통 인프라 예산에 실제 적용 중.
[PMI, "From Nobel Prize to project management" | https://www.pmi.org/learning/library/nobel-project-management-reference-class-forecasting-8068; arxiv 1302.3642]

CAP 맥락에서의 함의: 전환 설비(H2-DRI, 전해조, e-cracker)는 "화력발전"이나 "재생에너지" 준거집단에 넣기엔 부적절하고, 오히려 **"원자력/대형 커스텀 화학공정"(상방 두꺼움) vs "모듈형 재생에너지"(상방 얇음)** 사이 스펙트럼에서 설비별로 어디 앉는지 판정한 뒤 그 준거집단의 초과율 분포를 상방 보정에 사용해야 한다.

---

## 분포에 반영할 함의

1. **상방 꼬리는 정규분포·로그정규 단일모수로 과소적합될 위험이 크다.** 유사 팻테일 사례(IT, 올림픽, 댐)가 멱함수 적합을 지지하므로, CAP의 상방 꼬리도 정규/로그정규 대신 **멱함수 또는 혼합분포(bulk는 로그정규 + 극단꼬리는 멱함수)** 후보를 검토해야 한다.
2. **설비별로 서로 다른 준거집단을 배정해야 한다.** 전해조=SMR급 참조집단(중앙값 초과 +130%, 학습효과 기대), H2-DRI 통합플랜트=원자력·대형IGCC-CCS 참조집단(+120~180%대), e-cracker=아직 준거집단 자체가 없음(6MW 데모만 존재) — 단일 "전환설비" 준거집단으로 뭉뚱그리면 상방을 과소 또는 과대평가.
3. **레트로핏 vs 그린필드 구분이 초과율의 1차 분기점이다.** 같은 "CCS" 항목에서도 Boundary Dam(레트로핏, +22.5%)과 Kemper(그린필드 신공정, +150~180%)의 격차가 7배 이상 — 철강 H2-DRI(그린필드)와 e-cracker(레트로핏 가능성)의 상방 격차도 이 축을 따라갈 가능성이 높다.
4. **에너지가 급등은 CAPEX 초과와 독립적으로 작동하며 손익분기를 통해 증폭된다.** H2-DRI의 손익분기 수소가 민감도($1.06~1.70/kg 범위, NG가격에 좌우)는 CAPEX가 고정되어도 에너지가 하나만으로 손익분기를 넘나들 수 있음을 보여준다 — 즉 상방 꼬리는 "CAPEX 팻테일"과 "에너지가 팻테일"의 **결합(joint) 꼬리**로 모델링해야 하며, 두 리스크를 독립으로 가정하면 상방을 과소평가.
5. **철강 상방 > 석화 상방이라는 잠정 결론은 참조집단 유비이지 직접 증거가 아니다.** 두 섹터 모두 상업 규모 실증이 아직 없어 데이터 기반 꼬리지수 추정 자체가 불가능한 상태 — CAP 분포 생성기에서는 "철강 꼬리를 더 두껍게" 하되, 그 차이의 크기(계수)는 전문가 판단/시나리오 값으로 명시하고 하드 데이터로 위장하지 않아야 한다.

---

## 미확인

- "FOAK 대비 NOAK 컨틴전시 150%"라는 구체적 수치 — 확인 못함. 확인된 것은 전해조 EPC+컨틴전시가 설치비의 "절반 이상"이라는 정성적 서술뿐(NREL/IEA).
- H2-DRI 상업 플랜트(Stegra)의 **정량적 비용 초과율(%)** — 자금 위기·지연 규모($1B+ 경색, €975M 추가조달)는 확인했으나 "원 견적 대비 +X%"로 환산 가능한 단일 수치는 확인하지 못함.
- 전해조 프로젝트의 **개별 프로젝트 단위 초과율(견적 대비 실적, %)** — IEA 등은 산업 전체 코스트 커브 상승(+20~45%)은 보고하나, 이는 시장가 변동이지 개별 FOAK 프로젝트의 견적 초과율과 같은 개념이 아님. 별도 확인 필요.
- e-cracker의 **상업 규모(500MW+) 비용 추정치 자체** — 6MW 데모 단계이며 상업 규모 CAPEX 추정은 검색에서 확인하지 못함(고위 수준 추정이 존재한다는 언급만 확인, 수치 미확인).
- 전환비용 분포 상방 꼬리에서 **에너지가 기여 vs CAPEX 기여의 정량적 분해(%)** — 직접 연구 확인하지 못함. 정성적 동시작용 증거만 확보.
- CVaR/ES를 산업 전환설비 CAPEX 초과율 분포에 **직접 적용한 논문** — 확인하지 못함. NGFS의 거시 시나리오 꼬리 리스크 서술은 방법론적 유비일 뿐 동일 대상이 아님.
- 올림픽/IT 프로젝트 멱함수의 **정확한 꼬리지수(α) 수치** — "낮다"는 서술은 확인했으나 논문 원문의 구체적 α값은 이번 검색 결과 요약에서 확인하지 못함(원문 arxiv PDF 직접 열람 필요).
- 왜도(skewness)의 **구체적 수치** — "오른쪽으로 치우침"은 확인했으나 계량값은 확인하지 못함.

---

# SYNTHESIS L2 (분포 모양·두 꼬리) — 2026-09-13

## 두 꼬리 다 실재, 모양이 다르다
| | 상방(비용 폭발) | 하방(좌초) |
|---|---|---|
| 형태 | 멱함수·팻테일(평균·분산 발산) | 문헌 미정량이나 **실증적으로 구속력** |
| 앵커 | Kemper CCS $2.8B→$7.8B 취소, 원자력 +120%, SMR FOAK +130% | **ArcelorMittal €13억 보조금 포기·H2-DRI 취소(2025-06)** |
| 원천 | CAPEX·에너지(짓는 돈) | 탄소 붕괴(EU €30→€2.63, K-ETS −59%)·그린프리미엄 수요 부재(>$330/t 지불 0%) |

## 섹터 비대칭 (L1 두 꼬리를 섹터로 갈라)
- **철강**: 상방 **두껍다**(그린필드 4서브시스템 = 원자력·IGCC-CCS 참조집단), 하방 **이산적**(확률 낮되
  좌초 시 큰 손실 — ArcelorMittal 실제 취소). **두 꼬리 다 있는 문제.**
- **석화**: 상방 **얇다**(노 교체 레트로핏, 리스크 표면적 좁음), 하방 **연속적**(embedded로 전환 후에도
  가스 회귀 가능, Tautorat). **몸통 이동이지 꼬리 아님.**
- **레트로핏 vs 그린필드가 상방 초과율의 1차 분기점** — 이게 철강·석화 상방 차이의 뿌리.

## 함의: 분포 모양이 헤지를 정한다
철강 = 양쪽 꼬리 → 상방 캡(EPC/GMP) + 하방 하한(CCfD) 둘 다 필요.
석화 = 얇은 상방 + 연속 하방 몸통 → 캡보다 몸통 이동 관리(원료·flexi 헤지), 하한은 덜 이산적.
지난 9루프의 철강·석화 비대칭이 여기서 **분포 모양의 언어**로 재확인 — 다른 렌즈, 같은 결론.

## 가장 센 실증 앵커
ArcelorMittal 취소 = 하방 꼬리 실재·구속력의 증거. €13억 보조금 받은 기업이 분포 하방(약한
프리미엄 + 높은 비용 → NPV 음수)에서 걸어나갔다. "전환비용 분포" 프레임 전체의 현실 증거이자,
L1이 "MILP 전체 분포화 선례 없음"이라 한 CAP의 자리가 왜 중요한지의 실물.

## 직전(L1) 비판적 재검토
L1은 "두 꼬리, 두 헤지"라 했다. L2 정련: 두 꼬리의 **모양과 상대 크기가 섹터로 다르다**. 그리고 하방은
문헌에 미정량이나 실증적으로 구속력(ArcelorMittal). 또 정책 후퇴를 뭉치면 안 됨 — 미국형(IRA 후퇴
실재) vs EU형(CBAM 강화, 반대). L1의 "하방=정부 CCfD"는 유지되나, 하방 자체가 정책 방향에 따라
갈린다(후퇴는 하방 키우고 강화는 상방으로 번역 — L4 지난 루프 CBAM).

## 분포·모형 함의 (L2)
- 단일 로그정규 대신 **멱함수/혼합분포** 검토(상방). 설비별 별도 참조집단(레트로핏/그린필드).
- 하방: NPV<0 비중=좌초 확률, 조건부 평균손실=하방 CVaR. 철강 이산형/석화 연속형 다른 분포족.
- CVaR 주지표, VaR 보조. 탄소 "수준"과 "불확실성" 별개 채널(효과 크기 비슷 — Carbon VIX).
- 정책 후퇴 3분류: 미국형 세액공제 후퇴 / EU형 CBAM 강화 / 시장설계 붕괴(K-ETS 이월).
- CBAM 무상할당 폐지 스케줄(2026 97.5%→2034 0%)을 결정론 변조 변수로.
