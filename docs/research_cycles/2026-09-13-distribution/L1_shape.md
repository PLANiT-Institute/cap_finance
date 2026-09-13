# L1 — 전환비용 분포의 모양 (CAP 8루프, L1)

프레임: 전환 총비용을 하나의 분포로 볼 때 그 모양(평균·꼬리·왜도·다봉성)이 헤지 전략의 출발점이다.
방법: WebSearch로 확인된 문헌만 기입. 추측 서지 없음. 확인 안 된 항목은 마지막 "미확인" 절에 별도 표기.

---

## 프로젝트 비용 분포 모양 (Flyvbjerg)

- 대형 건설 프로젝트 평균 비용 초과는 62%이며, 20개 분야 136개국 16,000개 프로젝트 표본에서 비용·기간 목표를 동시에 달성한 프로젝트는 8.5%에 불과하다.
  [Flyvbjerg, B. & Gardner, D. (2023), *How Big Things Get Done*, Macmillan | 요약: https://readingraphics.com/book-summary-how-big-things-get-done/]

- 기술별 평균 비용 초과율(에너지·인프라 프로젝트 데이터베이스 기준): 원자력 +120%, 수력댐 +75%, 화력발전 +16%, 풍력 +13%, 송전선 +8%, 태양광 +1%. 태양광·풍력처럼 공장에서 사전 제작해 현장 조립하는 모듈형 기술이 비용 리스크가 가장 낮은 쪽에 위치한다.
  [Flyvbjerg, B. (미상 연도, 인프라 프로젝트 데이터베이스 분석), *How Big Things Get Done* 인용 | https://www.fastcompany.com/90844859/why-massive-wind-and-solar-projects-will-succeed-where-nuclear-has-failed ; 최근 재추정치(원자력 +117.3%, 수력 +70.6%): https://orennia.com/insights/typical-energy-project-cost-overruns]

- 수력댐 표본(245개, 여러 대륙)에서 예산 대비 실제비용 비체계적 과소추정을 교정하기 위한 상향 조정치(de-biasing uplift)는 +99%이며, 10건 중 2건은 실제비용이 2배 이상, 10건 중 1건은 3배 이상으로 증가했다.
  [Ansar, A., Flyvbjerg, B., Budzier, A. & Lunn, D. (2014), "Should We Build More Large Dams? The Actual Costs of Hydropower Megaproject Development", *Energy Policy*, 69, 43–56 | https://www.sciencedirect.com/science/article/abs/pii/S0301421513010926 ; 원문 PDF: https://arxiv.org/pdf/1409.0002]

- 258건 교통 인프라 프로젝트(900억 달러 규모) 분석에서 비용 과소추정은 오차(honest error)가 아니라 전략적 허위진술(strategic misrepresentation)로 가장 잘 설명되며, 이는 참조집단 예측(reference class forecasting)의 도입 근거가 되었다.
  [Flyvbjerg, B., Holm, M. S. & Buhl, S. (2002), "Underestimating Costs in Public Works Projects: Error or Lie?", *Journal of the American Planning Association*, 68(3), 279–295 | https://ppp.worldbank.org/library/underestimating-costs-public-works-projects-error-or-lie]

- IT 프로젝트(1,471건) 분석에서 평균 비용 초과는 27%이지만 이는 팻테일을 가린다: 표본의 1/6은 "블랙스완" 프로젝트로 평균 200% 비용 초과·70% 일정 초과를 기록한다. 후속 연구는 IT 프로젝트 비용 초과가 정규분포가 아니라 멱함수(power-law) 분포를 따른다는 것을 보인다(초과 시 평균 447%로 전 프로젝트 유형 중 최고).
  [Flyvbjerg, B. & Budzier, A. (2011), "Why Your IT Project May Be Riskier Than You Think", *Harvard Business Review* | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2229735 ; 후속: Flyvbjerg, B., Budzier, A., Lee, J. S., Keil, M., Lunn, D. & Bester, D. W. (2022), "The Empirical Reality of IT Project Cost Overruns: Discovering a Power-Law Distribution" | https://arxiv.org/pdf/2210.01573]

- "팻테일" 프로젝트 유형(원자력·댐·IT·올림픽)과 "신테일(thin-tail)" 프로젝트 유형(풍력·태양광·도로)의 구분: 신테일형은 정규분포에 가까워 관리 가능하지만, 팻테일형은 정규분포를 벗어나 극단적 결과(대규모 초과 또는 파국적 실패)의 확률이 벨커브 예측보다 훨씬 높게 유지된다.
  [Flyvbjerg, B. & Gardner, D. (2023), *How Big Things Get Done* | https://cleantechnica.com/2024/08/14/how-big-things-get-done-talking-with-megaproject-expert-professor-bent-flyvbjerg/]

**전환 설비의 참조집단 위치**: H2-DRI·전해조·CCUS 같은 신규 대형 산업 설비는 "공장 모듈 조립형"(태양광·풍력 계열, 신테일)이 아니라 "커스텀 현장시공 대형 열/화학 공정"(원자력·수력·화력 계열, 팻테일) 참조집단에 더 가깝다는 것이 Flyvbjerg 분류의 함의다 — 단, H2-DRI·전해조 자체를 참조집단으로 직접 분류한 논문은 확인하지 못했다(미확인 절 참조).

---

## FOAK 비대칭

- Merrow는 35년간 318개 이상의 산업 메가프로젝트(정유·화학·금속·해양플랜트·댐 등)를 분석해, 절반 이상이 예산·일정·가동 성능 기준에서 "저조한 성과(poor results)"를 보였다고 결론짓는다. Merrow는 낙관 편향(optimism bias, 의도적 왜곡이 아닌 자기기만)을 프로젝트 전방기획(front-end definition) 부족의 결과로 설명하며, 이를 교정하기 위한 해법으로 전방기획 강화를 제시한다.
  [Merrow, E. W. (2011), *Industrial Megaprojects: Concepts, Strategies, and Practices for Success*, Wiley | https://www.ipaglobal.com/resources/books/industrial-megaprojects-2nd-edition-ed-merrow/ ; 리뷰: https://www.kingsfieldacademy.com/why-do-projects-perform-badly/]

- 탄소포집(CCS) 발전소의 FOAK 대비 NOAK 비용 절감: NOAK 플랜트는 균등화발전비용(LCOE)을 10~11%, 회피비용(avoided cost of capture)을 21~23% 낮출 수 있다(NGCC+PCC 조합에서는 LCOE가 FOAK 대비 12~20.4% 저렴). FOAK 포집비용은 평균적으로 NOAK 대비 약 150% 높다.
  [Rubin, E. S. 계열 학습곡선 연구 인용, 관련 최신 정량화: "Progressing from first-of-a-kind to Nth-of-a-kind: Applying learning rates to carbon capture deployment in Sweden", *International Journal of Greenhouse Gas Control* 계열 | https://www.sciencedirect.com/science/article/pii/S1750583624001695 ; FOAK/NOAK 배수 논의: https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2022.987166/full]

- FOAK 비용 추정 시 NOAK 대비 100~200%의 컨틴전시(contingency) 가산이 관행적으로 적용된다 — 즉 FOAK 비용 분포는 NOAK를 중심으로 상방에 두꺼운 꼬리를 갖는 형태로 실무에서 이미 취급되고 있다.
  [상동, Frontiers in Energy Research 2022 | https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2022.987166/full]

- 그린스틸(H2-DRI) 사례에서 FOAK 리스크의 실증: ArcelorMittal은 보조금 13억 유로가 투입된 독일 그린스틸 프로젝트 2건을 "비용이 지속 불가능하고 그린프리미엄에 대한 시장 수요가 약하다"는 이유로 취소했다. 이는 FOAK 산업 탈탄소화 설비의 상방 비용 리스크가 실제 투자 결정을 뒤집을 만큼 크다는 사례다.
  [보도 종합, Council Fire 정리 | https://www.councilfire.org/guides/hydrogen-steelmaking-opportunities-barriers/]

- H2-DRI 그린스틸 원가는 톤당 약 562달러로 기존 제강 대비 약 5% 높은 그린프리미엄을 갖지만, 이는 수소가격 가정(중국 기준 $5/kg 수소가정 시 프리미엄 톤당 약 225달러)에 따라 크게 변동하며, 미국 기준 손익분기 수소가격은 $1.4/kg 수준으로 추정된다 — 즉 중심추정치 자체가 입력변수(수소가격) 하나에 극도로 민감하다.
  [Green Steel Economics 계열 분석, Transition Asia | https://transitionasia.org/greensteeleconomics_es/ ; https://forourclimate.org/research/520]

**해석**: FOAK 비대칭의 메커니즘은 (i) 전방기획 부족에 따른 자기기만적 낙관(Merrow), (ii) NOAK 대비 관행적 상방 컨틴전시(150%, CCS 사례), (iii) 핵심 투입가격(수소가격) 불확실성이 곱해지는 구조로 3중이다. 셋 다 "상방으로 치우친" 방향으로 작용하며 하방(비용이 기대보다 낮게 나오는) 메커니즘을 상쇄할 만한 대칭적 문헌은 확인되지 않았다.

---

## 왜도·다봉성

- 프로젝트 비용(총비용·기간)은 이론적으로도 로그정규(log-normal) 분포로 모델링되는 것이 표준 관행이다: 로그정규는 우측으로 긴 꼬리를 가지며 큰 양(+)의 이탈은 가능하지만 음(-)의 값은 불가능한 프로젝트 비용의 물리적 제약(비용이 0 밑으로 갈 수 없음)과 부합한다.
  [Monte Carlo 비용리스크분석 방법론 정리 | https://risk-companion.com/blog/monte-carlo-simulation-risk-management-plain-language-guide/]

- IT/건설 프로젝트 비용 초과 표본에서 실측 왜도(skewness)가 정량화되어 있으며, IT 표본의 우측 왜도가 건설 표본 대비 2배 이상 크게 나타난다 — 즉 왜도의 크기 자체가 산업(참조집단)에 따라 체계적으로 다르다.
  [Flyvbjerg, B. & Budzier, A. 계열, "Double Whammy — How ICT Projects are Fooled by Randomness and Screwed by Political Intent" | https://arxiv.org/pdf/1304.4590]

- 철강 탈탄소화 최소비용 경로 연구는 기간별로 서로 다른 봉우리를 갖는 구조를 보여준다: 2030년 이전에는 에너지효율 개선·스크랩 재사용이 최저비용(각각 tCO2당 -8.5달러, +0.3달러)이고, 2030년 이후에는 용융환원+CCS가 지역별로 tCO2당 7~75달러의 넓은 비용 범위에서 등장한다 — 이는 "시점"과 "지역"이라는 두 개의 이산 축을 따라 비용이 서로 다른 군집(클러스터)으로 나뉘는 사실상의 다봉적 구조다.
  [Wu, X., Meng, J., Liang, X., Sun, L., Coffman, D., Kontoleon, A. & Guan, D. (2025), "Technological pathways for cost-effective steel decarbonization", *Nature* | https://www.nature.com/articles/s41586-025-09658-9 ; PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12589104/]

- IPCC IAM 기반 완화 경로 문헌에 대한 비판: 표준 IAM 앙상블은 근사 최악 시나리오에 과도하게 표본이 쏠려 있고 그럴듯한 시나리오 공간을 충분히 탐색하지 못하는 반면, 태양광·풍력·배터리 같은 모듈형 기술의 실제 비용 하락은 과거 IAM 예측보다 훨씬 빨랐다 — 즉 IAM 기술비용 분포 자체가 모델링 관행 때문에 실제보다 좁고 상방 편향되어 있을 가능성이 지적된다.
  [IPCC AR6 WG3 Technical Summary 관련 논의 및 비판, Way, R., Ives, M. C., Mealy, P. & Farmer, J. D. (2022), "Empirically Grounded Technology Forecasts and the Energy Transition", *Joule*, 6(9), 2057–2082 | https://www.cell.com/joule/fulltext/S2542-4351(22)00410-X]

**해석**: 전환비용의 다봉성은 기술 선택 자체(H2-DRI vs CCUS vs EAF 스크랩)의 이산성보다는, 관측된 문헌에서는 "시점(사전/사후 2030)"과 "지역/정책조건"의 이산적 조합에서 더 명확히 확인된다. "기술경로별 봉우리"라는 원래 가설을 직접 검증한 논문(예: 특정 국가 철강산업의 시나리오 앙상블 히스토그램에서 다봉 형태를 명시적으로 보고한 논문)은 이번 검색에서 확인하지 못했다 — 미확인 절 참조.

---

## 어느 꼬리가 위험인가

**상방 꼬리 (비용 폭발)**
- 위 "FOAK 비대칭" 절의 CAPEX 초과 메커니즘(Merrow, CCS FOAK/NOAK 150%, 원자력/수력 +75~120%)이 상방 꼬리의 1차 원천이다.
- 에너지가격 급등이 상방 꼬리에 기여하는 경로: H2-DRI 손익분기가 수소가격 $1.4~1.63/kg에서 결정되므로(위 인용), 에너지 투입가격이 이 임계치를 넘으면 그린프리미엄이 급격히 확대된다.
  [https://forourclimate.org/research/520]

**하방 꼬리 (좌초 — 감축가치 증발)**
- 화석연료 좌초자산의 잠재 손실 규모: 업스트림 석유·가스 부문에서 기후정책 기대 변화만으로도 미래 손실 이익의 현재가치 기준 1조 달러 이상이 좌초 가능하며, 화석 발전자산은 전 세계적으로 1.4조 달러가 좌초 위험에 노출되어 있다.
  [Nature Climate Change 계열, "Stranded fossil-fuel assets translate to major losses for investors in advanced economies" | https://www.nature.com/articles/s41558-022-01356-y]

- 전환리스크(transition risk)는 탄소가격·좌초자산·넷제로 공약의 신뢰격차에서 발생하며, "탄소버블(carbon bubble)"은 탄소집약 기업의 자산가치가 온도목표 달성을 위해 필요한 매장자원 좌초 위험을 반영하지 못해 과대평가된 상태를 가리킨다 — 이는 CAP 프레임에서 "탄소가 붕괴하면 감축설비의 감축가치(탄소가격 연동 수익)가 증발한다"는 하방 메커니즘과 대칭된다.
  [Grantham Research Institute, "What are stranded assets?" | https://www.lse.ac.uk/granthaminstitute/explainers/what-are-stranded-assets/]

**해석 — 두 꼬리는 서로 다른 확률변수에서 온다**: 상방 꼬리는 CAPEX·에너지가격(비용 측, 설비를 짓는 데 드는 돈)에서 오고, 하방 꼬리는 탄소가격·정책신뢰(수익 측, 감축설비가 만들어내는 돈)에서 온다. 두 꼬리를 하나의 대칭 분산으로 뭉뚱그리면 헤지 수단이 서로 다른 두 리스크(EPC 고정가 vs CCfD 하한)를 하나의 도구(예: 단순 변동성 헤지)로 잘못 처리하게 된다는 것이 5절 매핑의 근거다.

---

## 분포 모양 → 헤지 수단 매핑

- CCfD(Carbon Contracts for Difference)는 정부·기업 간 파생계약으로, 기준 탄소가격이 계약상 행사가격(strike price) 아래로 떨어지면 정부가 차액을 지급(=가격 하한, 좌초/하방 꼬리 헤지)하고, 위로 오르면 기업이 초과분을 반환(=상한, 캡)하는 구조다. 목적은 정책연동 가격노출을 매수자(기업)에서 매도자(정부)로 이전해, 그린수소·CCS 같은 자본집약적 저탄소 프로젝트의 장기 가격 안정성을 확보하는 것이다.
  [Florence School of Regulation, "Carbon Contracts for Difference" | https://fsr.eui.eu/carbon-contracts-for-difference/ ; 설계 논의: KU Leuven 작업논문 | https://www.mech.kuleuven.be/en/tme/research/energy-systems-integration-modeling/pdf-publications/wp-esim2023-07.pdf]

- CCfD는 혁신가(innovator)에서 정부로 (부분적) 리스크 이전을 가능케 하는 탈위험화(de-risking) 도구로 제시되며, 저탄소 기술이 현재 탄소가격(예: EU ETS)에서 경쟁력을 갖기엔 지나치게 비쌀 때 투자를 가능케 하는 장치로 명시된다.
  [Florence School of Regulation | https://fsr.eui.eu/carbon-contracts-for-difference/]

- EPC(설계·조달·시공) 고정가(lump-sum fixed-price) 계약은 비용·일정 리스크를 발주자에서 시공사로 이전하며, GMP(Guaranteed Maximum Price) 방식은 총비용에 상한을 씌우면서 절감분을 분배하는 구조다 — 이는 상방 꼬리(CAPEX 초과)를 계약적으로 캡핑하는 수단이다.
  [LexisNexis, "EPC/Turnkey Contracts: Key Features, Risk Allocation, Pricing..." | https://www.lexisnexis.com/en-gb/legal/guidance/introduction-to-epc-contracts ; Wikipedia, "Lump sum turnkey" | https://en.wikipedia.org/wiki/Lump_sum_turnkey]

- 참조집단 예측(reference class forecasting)은 개별 프로젝트의 하향식(bottom-up) 추정 대신 유사 완공 프로젝트군과의 비교로 예산을 수립하는 기법으로, 미국계획협회(APA) 등이 승인했고 영국·네덜란드·홍콩·덴마크·스위스 등에서 메가프로젝트 비용·편익 예측에 활용된다 — 이는 헤지 수단이라기보다 분포 자체(중심·꼬리)를 사전에 더 정확히 추정해 계약설계(캡·하한 수준)를 보정하는 상류(upstream) 절차다.
  [Flyvbjerg 계열 정리 | https://www.scl.org/3872-reference-class-forecasting-and-realistic-tech-contracts/]

**매핑 요약 (문헌 기반, 대칭 분산헤지 관련 문헌은 이번 검색에서 별도 확인하지 못함)**

| 분포 모양 | 위험의 성격 | 문헌상 확인된 대응 수단 |
|---|---|---|
| 상방 팻테일 (CAPEX 초과, FOAK) | 비용이 예상보다 훨씬 커질 확률이 두껍다 | EPC 고정가/GMP 계약으로 상한 캡 (LexisNexis; Wikipedia lump-sum turnkey) |
| 하방 꼬리 (탄소가격 붕괴·좌초) | 감축설비의 수익(탄소가격 연동분)이 증발할 확률 | CCfD 하한(가격이 행사가 아래로 떨어지면 정부가 보전) (FSR; KU Leuven) |
| 상방·하방 동시 노출 | 정책가격 변동성 자체 | CCfD의 양방향 정산 구조(하한 지급 + 상한 환수) 자체가 캡·플로어를 한 계약에 결합 (FSR) |
| 분포 중심·꼬리의 사전 추정 오류 | 계약설계(캡·하한 수준)를 잘못 잡을 위험 | 참조집단 예측으로 사전 보정 (Flyvbjerg 계열) |

---

## 미확인

다음은 이번 WebSearch로 직접 확인하지 못했으며, 서지를 추측하지 않고 항목만 남긴다.

1. H2-DRI·전기분해로(전해조)를 명시적으로 Flyvbjerg 참조집단 분류체계(원자력/수력/화력/풍력/태양광 중 하나)에 배정한 논문 — 확인 안 됨. 위 "프로젝트 비용 분포 모양" 절의 결론은 유추이지 직접 인용이 아님을 명시.
2. "기술경로별 봉우리(peak)"가 명시적으로 다봉 히스토그램/커널밀도로 보고된 전환비용 논문(즉 H2-DRI vs CCUS vs EAF 각각이 별도 봉우리로 시각화된 원 논문) — 확인 안 됨. Wu et al. (2025, Nature)는 시점·지역별 군집을 보이지만 "다봉분포"라는 용어를 직접 쓰는지는 원문 전체를 읽지 않아 확정할 수 없음.
3. Rubin의 CCS 학습곡선 원 논문(Rubin, E. S. et al. 2007, 정확한 저널·권호) — 2차 인용을 통해서만 확인, 원 논문 서지사항(저널명·연도·DOI) 직접 확인 안 됨.
4. "대칭 분포 → 분산 헤지(전통적 계약)" 매핑을 직접 다룬 논문 — 이번 검색에서 확인 안 됨. 5절 표의 세 번째 행(대칭 분포)에 대응하는 문헌은 공백으로 남김.
5. Awerbuch/Roques류 포트폴리오 이론 문헌(과거 CAP 세미나 메모에 언급된 계열)과 본 L1 주제(분포 모양)의 직접 연결 논문 — 이번 검색 범위에서 별도로 재확인하지 않음(과거 P08 문헌으로 기존 확인된 것으로 추정되나 이번 세션에서 재검증 안 됨).
6. Merrow(2011)의 FOAK 관련 구체 챕터·페이지 수준 인용 — 책 원문 확인 안 됨, 2차 서술(IPA, Kingsfield Academy)에 의존.
