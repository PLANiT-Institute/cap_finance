# L1 — 철강: 전환 후 전력 조달과 비용위험 구조

9루프 연구 L1(철강 파트) 문헌 종합. 목적: 지금 모형이 "전환 전기 = 계통(SMP, LNG 연동, σ 높음)"으로 가정해 조기 전환에 벌을 주는 구조를, "전환 전기 = 재생 PPA·자가발전(설비비 기반, 고정·하락)" 관점으로 재구성하기 위한 근거 확보. 모든 항목 WebSearch/WebFetch로 실제 확인. 확인 못 한 것은 마지막 섹션에 별도 표시.

---

## 전력 수요 특성

- **H₂-DRI 전력 수요 규모**: H-DR(수소 직접환원) 제철은 액체강 1톤당 **3.48 MWh**의 전력이 필요하며, 이 중 대부분이 전해조(electrolyser)의 수소 생산에 들어간다. 독일 전체 1차 철강 생산(연 2,950만 톤)을 H-DR로 전환하면 약 **103 TWh**, 스웨덴(연 310만 톤)은 약 **10.8 TWh**의 추가 전력 수요가 발생한다. 탄소가격 34~68 €/tCO₂, 전력가격 40 €/MWh 수준에서 H-DR이 통합 고로 대비 비용 경쟁력을 갖는다.
  [Vogl, V., Åhman, M., Nilsson, L.J. (2018), "Assessment of hydrogen direct reduction for fossil-free steelmaking," Journal of Cleaner Production, 203, 736–745 | https://www.sciencedirect.com/science/article/pii/S0959652618326301]

- **부하 특성(전해조 vs EAF, 저장 필요량)**: H-DR+EAF 시스템에 대한 장기 에너지시스템 계획 모형 결과, 비용 최적 구성은 전해조 1.3 GW·풍력 3 GW·태양광 2.5 GW·CCGT(CCS 부착) 60 MW·수소 저장 600 GWh(600 MW)·압축공기저장 30 GWh(130 MW)이다. 디스패처블 발전(가스+CCS 등)을 전혀 허용하지 않으면 수소 저장이 600 GWh 필요하지만, 전력수요의 20%를 디스패처블 발전으로 충당하도록 허용하면 저장 요구량이 **140 GWh로 급감**한다 — 즉 전해조/DRI 부하 자체는 유연화 가능하지만, 완전 재생 전용으로 갈수록 저장 비용이 비선형적으로 커진다.
  [Pimm, A.J., Cockerill, T.T., Gale, W.F. (2021), "Energy system requirements of fossil-free steelmaking using hydrogen direct reduction," Journal of Cleaner Production, 312, 127665 | https://www.sciencedirect.com/science/article/pii/S0959652621018837 — 본문 유료장벽으로 원문 접근 실패, 요약은 검색엔진이 제공한 발췌에 근거함, 수치는 교차확인 필요]

- **전기로(EAF) 부하 특성**: EAF는 배치(batch) 공정 특성상 급격한 전력 스파이크(수십 MW급 아크 변동)를 가지지만, 하루 단위로는 상대적으로 예측 가능한 반복 사이클이며 전통적으로 계통 전력(often 야간 저가 시간대 활용)에 의존해왔다. H-DR로 전환 시 EAF 자체 부하보다 전해조 부하(연속적, 대용량)가 지배적이 된다.
  [Vogl et al. (2018), 상동]

---

## 재생 PPA 조달 사례·구조

- **Stegra(구 H2 Green Steel, 스웨덴 보덴)** — 여러 건의 재생 PPA를 순차 체결:
  - Statkraft: 2 TWh/년, 7년(2026–2032), 북스웨덴 수력 기반, 재생에너지 보증서(GO) 포함.
  - Fortum: 프레임 계약 총 2.3 TWh/년 — 지수연동(index-based) PPA 1.3 TWh(5년 헤지 구간, 2026~), 고정가 PPA 1 TWh(최대 9년, 2027~).
  - Uniper: 6 TWh, 6년(2027–2032).
  - Axpo Nordic: 2.25 TWh, 3년(2027~).
  → 이는 **단일 계약이 아니라 만기·가격구조(지수형 vs 고정형)를 분산한 PPA 포트폴리오**로 조달하고 있음을 뜻한다.
  [Stegra 뉴스룸, "H2 Green Steel partners with Statkraft for 14 TWh of renewable electricity" 및 "H2 Green Steel has entered into a long-term frame agreement with Fortum" 및 "Stegra and Axpo sign 2 TWh electricity deal" | https://stegra.com/en/news-and-stories/ ; ESG Today, "Stegra Signs 6 TWh Electricity Deal to Power Green Steel Production" | https://www.esgtoday.com/stegra-signs-6-twh-electricity-deal-to-power-green-steel-production/]

- **SSAB/HYBRIT(스웨덴)** — LKAB·Vattenfall과의 합작. 옐리바레(Gällivare) 신규 수소생산시설에 약 **500 MW 전해조**를 설치하며, 전력은 주로 **수력(연중 가용) + 풍력**으로 조달한다. 수력을 "연중 계통 변동의 안정화 요소(stabiliser)"로 명시.
  [SSAB, "HYBRIT: Six years of research paves the way for fossil-free iron and steel production" | https://www.ssab.com/en/news/2024/08/... ; Vattenfall Group, "HYBRIT – Vattenfall partnership with LKAB and SSAB" | https://group.vattenfall.com/sustainability/climate-action/industry-decarbonisation/hybrit/]

- **ArcelorMittal** — 2018년 스페인 태양광 2개소로부터 연 8.6 GWh 조달 계약 체결(EAF 대상). 프랑스에서는 EDF와 장기계약으로 저탄소 원자력 전력의 전용 지분(dedicated share)을 확보. "안정적인 그린 전력 접근 없이는 탈탄소 프로젝트 실행이 불가능"이라고 명시하며, 재생 PPA 확대와 REC 구매를 병행 전략으로 제시.
  [ArcelorMittal Corporate, "Climate change" | https://corporate.arcelormittal.com/sustainability/approach/climate-change ; northamerica.arcelormittal.com/sustainability/climate]

- **Boston Metal(미국, MOE 용융산화물전해)** — 수소를 전혀 거치지 않고 1600°C 용융염 전해조에서 **재생전력을 직접** 사용해 철광석을 액체금속으로 환원. "수소 인프라·탄소포집·공정수가 필요 없는 경로"로 자체 설명 — 전력조달 구조상으로는 H₂-DRI보다 단순하지만, 전력의 연속성(고온 셀 유지) 요구는 오히려 더 엄격할 수 있음(본 문서에서 정량 확인 못함, 미확인 참조).
  [Boston Metal, "Zero CO2 Steel by Molten Oxide Electrolysis" | https://www.bostonmetal.com/news/zero-co2-steel-by-molten-oxide-electrolysis-a-path-to-100-global-steel-decarbonization/]

- **기업 오프테이커의 계약 선호(스위스 실증)**: 기업 PPA 구매자 91곳·860건의 가상 의사결정 실험 결과, 오프테이커는 **저가격·단기 만기(짧은 tenor)**를 뚜렷이 선호하고, 특히 중소기업은 5년 계약에 더 큰 프리미엄을 지불할 의향이 있음(장기계약보다). 대기업은 발전기술 종류에 더 민감. 장기 구속력과 계약 복잡성이 주요 저해요인으로 확인됨.
  [Mili, S., Côté, E. (2025), "Green on demand? Offtaker preferences for corporate power purchase agreements," Energy Policy, 196, 114408 | https://doi.org/10.1016/j.enpol.2024.114408 — PDF 원문 직접 확인, 저자명 검증 완료]

---

## 연료위험→설비위험 전환 논리 (문헌)

- **기업 PPA의 재무 위험 헤지 효과**: 여러 기술·입지에 걸친 CPPA(기업 PPA) 포트폴리오를 최적화하면 재무 성과와 위험노출 간 최적의 트레이드오프를 제공한다. 가상전력구매계약(VPPA)은 산업 오프테이커에게 탈탄소 효과와 **위험 최소화 헤지**를 동시에 제공하는 금융적 헤지 수단으로 기능한다. CPPA 동인으로 탈탄소 목표뿐 아니라 "장기 비용 가시성"과 "상승·변동성 있는 전력시장 가격에 대한 헤지"가 명시적으로 꼽힌다.
  [Gabrielli, P., Aboutalebi, R., Sansavini, G. (2022), "Mitigating financial risk of corporate power purchase agreements via portfolio optimization," Energy Economics, 109, 105980 | https://www.sciencedirect.com/science/article/pii/S0140988322001542]

- **연료가격 위험 대 설비(자본)위험의 포트폴리오 이론적 근거**: 발전 포트폴리오의 평균-분산(mean-variance) 최적화에서, 가스-전력가격의 높은 상관관계(유럽 시장에서 관찰)는 가스발전의 "체감 위험"을 낮춰 가스 비중이 큰 포트폴리오를 유리하게 만든다. 그러나 **장기 전력구매계약과 낮은 자본비용**은 포트폴리오를 원자력·석탄 등 자본집약·무연료 자산 쪽으로 재균형시킨다 — 이는 재생에너지(무연료, 자본집약)에도 같은 논리가 적용됨을 시사: 장기 PPA는 연료가격 변동성을 자본비용/고정가격으로 치환하는 제도적 장치다.
  [Roques, F.A., Newbery, D.M., Nuttall, W.J. (2008), "Fuel mix diversification incentives in liberalized electricity markets: A Mean-Variance Portfolio theory approach," Energy Economics, 30(4), 1831–1849 | https://ideas.repec.org/a/eee/eneeco/v30y2008i4p1831-1849.html]

- **재생에너지의 화석연료가격 헤지 효과(고전 계보)**: Awerbuch(1993, 1994, 2003) 이래, 무연료 재생자산을 "위험자산 포트폴리오 내 무위험자산(risk-free asset)"으로 취급하는 계보가 확립되어 있으며, 후속 연구는 풍력을 천연가스 가격에 대한 헤지로 정량화한다. 관련 실증으로 Bolinger, M., Wiser, R., Bachrach, D., Golove, W.가 에너지효율·재생에너지가 변동성 큰 천연가스가격에 대해 제공하는 헤지가치를 정량화했다.
  [Bolinger, M., Wiser, R., Bachrach, D., Golove, W. (2002), "Quantifying the Value that Energy Efficiency and Renewable Energy Provide as a Hedge Against Volatile Natural Gas Prices," LBNL/eScholarship | https://escholarship.org/uc/item/0t4653n0 — 저자·기관 확인, 정확한 발표 매체(학술지 vs 컨퍼런스 프로시딩)는 추가 확인 필요]
  [CEC(북미환경협력위원회), "Renewable Energy as a Hedge Against Fuel Price Fluctuation" | https://www.cec.org/publications/renewable-energy-as-a-hedge-against-fuel-price-fluctuation/ — 개별 저자명 미확인, 기관 발간물로만 확인]

- **머릿오더 효과(merit-order effect)**: 재생에너지의 한계비용이 낮아 계통에 투입될수록 평균 도매전력가격을 낮추는 효과가 확인되어 있다. 다만 이는 재생발전사업자 자신에게는 "고산출 시간대에 낮은 가격을 받는" 형태(shape risk/cannibalization)로 되돌아오며, 이 형태 위험(shape risk)을 헤지하기 위한 Quality Factor(QF) 지수 기반 계약이 별도로 연구되고 있다 — 즉 "재생 = 무조건 저위험"이 아니라, 오프테이커(구매기업) 입장의 위험(연료가격 노출 제거)과 발전사업자 입장의 위험(형태/물량 위험)이 분리된다는 점이 문헌의 핵심 경고.
  [Roques & Finon (2017) 관련 논의는 "missing markets for long-term contracts" 문헌에서 재인용 확인; 원문 직접 확인 못함, 미확인 참조]
  [MDPI, "Hedging Shape Risk in Renewable Energy Markets: Empirical Evidence on Hedging Effectiveness Using the Quality Factor (QF) Index," Energies, 19(13), 3044(2026) | https://www.mdpi.com/1996-1073/19/13/3044]

---

## 제도 차이

- **한국**: SMP(계통한계가격)가 LNG 수입가격에 강하게 연동됨이 실증됨 — 2001~2011년 월별 데이터로 단위근·공적분·오차수정모형(ECM) 분석 결과, **LNG연료가격 → 도매전력가격(SMP)으로의 단방향 인과관계**가 단기·장기 모두에서 강하게 확인됨. 이는 계통전력을 조달원으로 쓰는 한 철강기업이 SMP를 통해 LNG 가격변동에 그대로 노출됨을 의미.
  [Chae, Y., Kim, M., Yoo, S.-H. (2012), "Does natural gas fuel price cause system marginal price, vice-versa, or neither? A causality analysis," Energy, 47(1), 199–204 | https://www.sciencedirect.com/science/article/abs/pii/S0360544212007268]
  - 제도적으로는 2021년 **제3자 PPA**(trilateral, 한전 경유), 2022년 **직접 PPA**(bilateral, 한전 미경유) 두 트랙이 도입됨. 직접 PPA는 REC 미발급(잉여전력만 REC 발급)이 원칙이며, 중소기업 대상으로는 1년간 송배전망 이용료 면제 인센티브가 있음. RE100 이행 확인서(CREU)는 두 트랙 모두 실사용량 기준으로 발급.
  [RE100/there100.org, "South Korea's PPA System: Status and Opportunities for Renewable Energy Development" | https://www.there100.org/our-work/publications/south-koreas-ppa-system-status-and-opportunities-renewable-energy-development ; Mayer Brown, "South Korea Opens Door for Direct PPAs for Renewable Projects" (2022) | https://www.mayerbrown.com/en/insights/publications/2022/02/south-korea-opens-door-for-direct-ppas-for-renewable-projects]

- **일본**: 2012년 후쿠시마 이후 FIT(고정가매입) 도입 → 2022년 4월부터 신규 설비는 **FIP(고정프리미엄)**로 전환. FIP 하에서 재생발전사업자는 도매시장 또는 기업 PPA로 직접 판매하면서 시장연동 프리미엄을 별도 수령 — 즉 일본의 기업 PPA 성장은 FIT 축소와 정확히 맞물려 있다. 발전사업자가 최종수요자에 직접 판매하려면 소매전기사업자 등록(라이선스)이 필요해 실무적으로는 도매사업자를 낀 3자 계약 구조가 일반적.
  [Clifford Chance, "Life after FIT? Corporate PPAs in Japan" (2022) | https://www.cliffordchance.com/content/dam/cliffordchance/briefings/2022/09/Corporate%20PPAs%20in%20Japan.pdf]

- **유럽(EU)**: 산업용 전력요금에서 **망 이용료(grid fee)가 총 청구액의 약 1/3**을 차지 — 국가 간 차이의 상당 부분이 도매가격이 아니라 망요금에서 발생. 도매전력가격 자체도 국가별 편차가 커 북유럽(€0.11–0.13/kWh)이 프랑스(€0.18/kWh)·독일(€0.27/kWh)보다 현저히 낮다. 고로→EAF 전환 시 개별 사업장 전력사용량이 최대 5배까지 급증하는 것으로 추정되어, 망 접속·요금 설계가 전환 경로 자체를 좌우하는 변수로 취급됨.
  [UK Steel, "Industrial Electricity Prices – Barrier to growth and competitiveness" | https://www.uksteel.org/electricity-prices ; Eurofer, "Position Paper – EU Electrification Action Plan (EAP)" | https://www.eurofer.eu/assets/publications/position-papers/eu-electrification-action-plan-eap/EUROFER-Position-Paper-on-the-Electrification-Action-Plan-EAP-vFinal.pdf]

- **비교 요약**: 한국(SMP 단일 도매가+LNG연동, PPA는 2021~22년에야 법제화되어 아직 성숙 초기) vs 일본(FIT→FIP 이행 중, 라이선스 장벽으로 3자 구조) vs 유럽(도매가+망요금 이원 구조, PPA 시장은 상대적으로 성숙하나 망요금이 국가 간 승패를 가름) — 세 지역 모두 "재생 PPA가 연료위험을 없애준다"는 명제가 **망 접근성·제도적 마찰**이라는 별도 변수에 의해 제약된다는 공통점이 있다.

---

## 기저부하 한계

- **간헐성 대 24시간 조업의 근본적 불일치**: DRI 공정은 통상 연속 가동을 전제하는데, 재생전력 대부분은 간헐적(풍력·태양광)이다. 완전 재생 기반 24시간 가동을 위해서는 에너지 저장이 필수이며, 저장 없이 재생만으로 완전히 충당하는 시나리오는 저장용량 요구가 비선형적으로 폭증한다(위 Pimm et al. 2021의 600 GWh vs 140 GWh 대비가 이를 수치로 보여줌).
- **오버빌드(설비 과잉) 전략**: 그리드 연결(grid-connected), 완전 격리(islanded/behind-the-meter), 혼합모드(semi-islanded) 세 운영 시나리오 중 **혼합모드가 가장 비용효율적**이라는 결과가 보고됨. 저장수단 비교에서는 극단적 변동성이 아닌 한 **수소저장 또는 고가 시간대 선택적 계통구매**가 배터리저장보다 우수한 것으로 나타남.
  [Roulier, A., Kwan, T.A., Eckelman, M.J. (2026), "Hybrid Grid-Renewable Strategies for Green Steel Production under Electricity Market Uncertainty," Industrial & Engineering Chemistry Research, 65(17), 8903–8921 | https://pubs.acs.org/doi/10.1021/acs.iecr.5c03878]
- **잔여 계통 노출의 불가피성**: 위 문헌들이 공통적으로 시사하는 것은, 재생 PPA·자가발전으로 철강 전력수요의 상당 부분(예: SSAB의 수력처럼 연중 가용한 특수 케이스 제외)을 커버하더라도 **잔여 부분은 여전히 계통(및 그 계통의 가격형성 메커니즘 — 한국이라면 SMP-LNG 연동)에 노출**된다는 것이다. 즉 "전환 = 안정적 설비위험으로의 완전한 치환"이 아니라 "연료위험의 부분적·확률적 치환"이며, 커버되지 않는 잔여 비율과 그 잔여가 노출되는 계통의 변동성(σ)이 여전히 헤지의 한계를 규정한다.
- **PPA 계약 자체의 잔존 위험**: Stegra 사례에서 보듯 기업들은 지수연동형(index-based)과 고정가형(fixed-price) PPA를 **혼합**해서 쓴다(Fortum 계약: 1.3 TWh 지수연동 + 1 TWh 고정). 이는 실무에서도 "PPA = 완전 고정가격"이 아니라 PPA 포트폴리오 내에서도 변동-고정 배분을 조정한다는 뜻이며, 100% 고정가격 전환은 실제로 관찰되지 않는다.

---

## 분포에 반영할 함의 (철강 전력 노출을 어떻게 흔들어야 하나)

현재 모형의 결함(F1 계열: 전환 후 전력을 SMP/LNG 연동 계통으로 가정 → σ 상승 → 조기전환 벌점)을 고치기 위해 분포 생성기에 반영할 구체적 방향:

1. **전환 후 전력조달을 단일 값이 아니라 혼합계약으로 모델링**: Stegra/Fortum 사례처럼 지수연동 비중(α)과 고정가 비중(1-α)을 파라미터화. α=1(완전 계통노출, 현재 모형)부터 α=0(완전 고정 PPA)까지의 스펙트럼을 만들고, 실제 관측된 계약 사례들(Stegra: 약 43% 고정/57% 지수연동, ArcelorMittal 스페인: 고정가 태양광)을 앵커로 삼아 α의 사전분포를 캘리브레이션.
2. **잔여 계통노출 비율을 명시적 변수로 분리**: Pimm et al.(2021)의 "20% 디스패처블 발전 허용 시 저장 140 GWh"처럼, 100% 재생조달이 아니라 **"β = 잔여 계통의존 비율"**을 별도 변수로 두고, β 몫에 대해서만 현재의 SMP-LNG 연동 변동성(σ_grid)을 적용. 완전 재생 전용(β=0)은 저장비용 급증으로 별도 자본비용 항에 반영해야 하며, 이 자본비용 항이 "설비위험"의 실체다.
3. **설비위험을 학습곡선형 고정비용 + 낮은 변동성으로 분리 표현**: PPA/자가발전 몫(1-β)의 가격은 연료가 아니라 **재생설비 LCOE**(자본비용·학습률 기반)에서 나오므로, 이 몫의 변동성은 SMP σ가 아니라 (i) 정책/입찰 변동성, (ii) 계약 갱신 시점의 재협상 위험만 반영 — 즉 σ_PPA ≪ σ_grid로 별도 캘리브레이션하되 0으로 두지 않음(Mili & Côté 2025가 보여준 대로 SME는 짧은 tenor를 선호하고, 짧은 tenor는 재계약 리스크를 재도입하기 때문).
4. **기저부하 확보 실패 시나리오를 꼬리위험으로 남김**: 저장 요구량이 비선형적으로 폭증하는 구간(β→0에 가까워질수록)을 감쇄 없는 볼록 비용함수로 반영하여, "완전 전환 = 완전 무위험"이라는 낙관을 모형이 스스로 차단하게 함. 이는 F3(비등가 감축) 문제와도 연결될 수 있음 — 재생 커버리지가 낮은 상태에서의 조기전환은 여전히 상당한 잔여노출을 갖는다는 점을 왜곡 없이 반영.
5. **국가별 α, β 사전분포를 제도 차이로 앵커링**: 한국은 PPA 제도가 2021~22년에야 도입되어 초기 성숙도가 낮으므로 β(잔여 계통의존)의 사전분포를 유럽보다 높게(즉 SMP-LNG 노출을 더 크게) 설정하는 것이 문헌상 정당화됨(Chae/Kim/Yoo 2012의 SMP-LNG 연동 실증 + RE100 자료의 "PPA 시장 초기 단계" 서술). 일본은 FIT→FIP 이행기의 라이선스 마찰을 β 상향 요인으로 반영. 유럽은 망요금(총 청구액의 1/3)을 β와 별도의 고정비용 항(연료위험과 무관하지만 사이트별로 국가 편차가 큰 요금)으로 분리.

---

## 미확인

- Pimm, Cockerill & Gale (2021) 원문(ScienceDirect, 유료장벽으로 403) — 본문 수치는 검색엔진 발췌 요약에 의존, 원문 대조 미완.
- Boston Metal MOE 공정의 전력 연속성 요구(24시간 셀 온도 유지에 필요한 최소 부하율) — 정량 문헌 확인 못함.
- "Roques & Finon (2017), missing markets for long-term contracts" — 원문 서지사항(저널명·권호) 직접 확인 못함, 2차 인용으로만 확인.
- CEC(북미환경협력위원회) "Renewable Energy as a Hedge Against Fuel Price Fluctuation" 보고서의 개별 저자명 — 기관 발간물로만 확인, 저자 미상.
- Bolinger, Wiser, Bachrach, Golove(2002) 논문의 정확한 발표 매체(학술지 게재 여부 vs ACEEE 컨퍼런스 프로시딩) — LBNL/eScholarship 사본만 확인, 정식 서지사항 추가 확인 필요.
- "재생 오버빌드 134~153%/134~152%/161~178%" 수치(북유럽 최적화 연구) — 검색엔진 요약에서만 확인, 원 저자·저널명 특정 못해 본문에서 제외함. 후속 조사 시 ScienceDirect "Renewable hydrogen based direct iron ore reduction and steel making with grid assistance" 원문 대조 필요.
- Ghiassi-Farrokhfal et al.(2021), Mendicino et al.(2019) — 사용자가 지정한 CPPA 헤지효과 문헌으로, Mili & Côté(2025) 논문 서론에서 인용된 것은 확인했으나 각 논문의 개별 서지사항(제목·저널)과 본문 내용은 직접 확인 못함.

---

**출처 요약(전체 URL 목록)**
- https://www.sciencedirect.com/science/article/pii/S0959652618326301 (Vogl et al. 2018)
- https://www.sciencedirect.com/science/article/pii/S0959652621018837 (Pimm et al. 2021)
- https://pubs.acs.org/doi/10.1021/acs.iecr.5c03878 (Roulier, Kwan & Eckelman 2026)
- https://stegra.com/en/news-and-stories/ (Stegra PPA 뉴스룸, 다수 게시물)
- https://www.esgtoday.com/stegra-signs-6-twh-electricity-deal-to-power-green-steel-production/
- https://www.ssab.com/en/news/2024/08/hybrit-six-years-of-research-paves-the-way-for-fossilfree-iron-and-steel-production-on-an-industrial
- https://group.vattenfall.com/sustainability/climate-action/industry-decarbonisation/hybrit/
- https://corporate.arcelormittal.com/sustainability/approach/climate-change
- https://www.bostonmetal.com/news/zero-co2-steel-by-molten-oxide-electrolysis-a-path-to-100-global-steel-decarbonization/
- https://doi.org/10.1016/j.enpol.2024.114408 (Mili & Côté 2025)
- https://www.sciencedirect.com/science/article/pii/S0140988322001542 (Gabrielli et al. 2022)
- https://ideas.repec.org/a/eee/eneeco/v30y2008i4p1831-1849.html (Roques, Newbery & Nuttall 2008)
- https://escholarship.org/uc/item/0t4653n0 (Bolinger et al. 2002)
- https://www.cec.org/publications/renewable-energy-as-a-hedge-against-fuel-price-fluctuation/
- https://www.mdpi.com/1996-1073/19/13/3044 (QF index shape-risk hedging)
- https://www.sciencedirect.com/science/article/abs/pii/S0360544212007268 (Chae, Kim & Yoo 2012)
- https://www.there100.org/our-work/publications/south-koreas-ppa-system-status-and-opportunities-renewable-energy-development
- https://www.mayerbrown.com/en/insights/publications/2022/02/south-korea-opens-door-for-direct-ppas-for-renewable-projects
- https://www.cliffordchance.com/content/dam/cliffordchance/briefings/2022/09/Corporate%20PPAs%20in%20Japan.pdf
- https://www.uksteel.org/electricity-prices
- https://www.eurofer.eu/assets/publications/position-papers/eu-electrification-action-plan-eap/EUROFER-Position-Paper-on-the-Electrification-Action-Plan-EAP-vFinal.pdf

---

# SYNTHESIS L1 (전력 조달·재생 PPA) — 2026-09-13

## 한 발견
재생 관점은 전환을 "연료 위험 → 설비 위험"의 깔끔한 스왑으로 만들지 **않는다**. 연료 위험 하나를
**셋**으로 분해한다:
1. **PPA 계약가 노출** — σ가 계통보다 낮지만 0이 아니다(정책·재계약·망요금 위험). 100% 고정가는
   실증에서 관찰 안 됨 — 실제는 지수연동 α + 고정가 (1−α) 포트폴리오(Stegra: Statkraft·Fortum·
   Uniper·Axpo 만기·구조 분산).
2. **형태·물량 불일치 잔여** — 연속 조업(DRI 전해조·연속 크래커) vs 간헐 재생. 잔여 계통 β에만
   σ_grid(SMP-LNG). 재생 비중 100%로 갈수록 저장비용 **비선형 폭증**(Pimm: 저장 600→140 GWh는
   디스패처블 20% 허용 시). → "완전 전환 = 완전 무위험"은 거짓.
3. **석화 전용 셋째 노출** — 부생가스(tail gas) 넷백. 전기화가 자가연료 수요를 없애 tail gas가
   캡티브 연료에서 판매 상품으로. 양·음 비대칭.

## 그럼에도 방향은 개선
혼합 PPA(α 지수 + (1−α) 고정)의 σ < 순수 계통 SMP σ. 즉 전환 전기를 재생으로 조달하면 노출의
**수준**이 아니라 **변동성**이 내려간다 — 사용자 원 직관이 여기서 부분 성립한다. 단 "부분"인 이유는
위 잔여 β와 저장 볼록비용, 그리고 석화 30% 감축 한계(Layritz: 전기화만으론 원료 배출 잔존).

## 분포를 흔드는 첫 설계 (L1 결론, 이후 루프가 검증)
전환 부하 전력 = α·(지수 PPA, σ_idx) + (1−α)·(고정 PPA, σ_PPA≈정책) + β·(계통, σ_grid). α·β는
제도(한국 β 높음·일본 라이선스 마찰·유럽 망요금 별도)와 시간(희소성 경로, L5)에 종속. 저장은 β→0에서
볼록. 석화는 tail gas 넷백 노드 추가. **핵심 파라미터는 σ가 아니라 β와 α의 시간 경로** — 이것이
L5(희소성)와 만난다.

## 직전(기존 v2.3) 비판
v2.3은 전환 전기 = SMP×1.08 하나로 뭉갰다. 재생 PPA를 "+8% 프리미엄 헤지 옵션"으로만 둬서
(a) 노출 이동을 과대(전부 σ_grid), (b) 조달 형태의 시간 변화(β 경로)를 못 봄, (c) 저장 볼록비용
누락. D2b에 `re_price`(한 175·일 198천원/MWh 실측)가 이미 있는데 v2.3이 계통가로 덮은 것 —
되돌리면 σ가 아니라 조달 구조가 바뀐다.
