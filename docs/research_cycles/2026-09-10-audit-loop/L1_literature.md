# L1 · 문헌·이론 서포팅 (2026-09-11 03:05 KST)

관점: v2의 (μ, ES_abs) 프런티어가 어떤 문헌 위에 서 있고, 어디가 비어 있는가. 모든 항목은 WebSearch/WebFetch로 저자·연도·학술지·DOI를 확인했다(대부분 초록 수준). 확인 못 한 것은 말미에 따로 적고 채택하지 않는다.

## 확인된 문헌

**평균–CVaR 선택.** Rockafellar & Uryasev (2000, *J. Risk* 2(3)) 와 (2002, *JBF* 26(7), 10.1016/S0378-4266(02)00271-6)이 원전이다. 후자가 이산 몬테카를로 표본에서의 CVaR를 정당화하므로 v2의 ES90 계산 근거다. 에너지 응용으로는 ShahNazari et al. (2015, *Energy Procedia* 75, 10.1016/j.egypro.2015.07.367)이 실물옵션+CVaR로 "위험을 줄이는 자산 추가"(화석 발전 포트폴리오에 풍력)를 평가했고, Zhang et al. (2024, *RSER* 189, 10.1016/j.rser.2023.113943)이 중국 발전기업의 탄소중립 포트폴리오를 평균–분산·CVaR·실물옵션으로 다뤘다. 둘 다 발전부문이고 계약은 후보에 없다.

**산업 탈탄소 옵션과 가격 불확실성.** Bachorz et al. (2025, *Nat. Commun.* 16:3984, 10.1038/s41467-025-59277-1)은 수소·CO₂ 가격 격자 위에서 최소비용 옵션 지형도를 그린다 — 결정론적 민감도이며 꼬리위험이 없다. Vogl, Åhman & Nilsson (2018, *JCP* 203, 10.1016/j.jclepro.2018.08.279)은 H₂-DRI가 전력가격에 매우 민감함을, Layritz et al. (2021, *Applied Energy* 296, 10.1016/j.apenergy.2021.117049)은 e-cracker 성과가 전력 탈탄소화에 달려 있음을 보인다. Tiggeloven et al. (2023, *I&EC Res.* 62(40), 10.1021/acs.iecr.3c02226)은 운전 유연성이 노출을 줄이는 수단임을, Langhorst et al. (2026, *J. Ind. Ecol.*, 10.1007/s44498-026-00166-1)은 H₂-DRI-EAF 전환 시 전력수요가 약 18배가 됨을 보인다(물질흐름분석이므로 노출 확대의 근거로만 인용). Lee (2023, *Energy* 283, 10.1016/j.energy.2023.129057)는 한국 철강에 몬테카를로를 결합해 수소가격 불확실성이 가장 중요하다고 보고한 직접 선행연구다.

**전력–LNG 연동과 헤지.** Chae, Kim & Yoo (2012, *Energy* 47(1), 10.1016/j.energy.2012.09.047)는 LNG 연료가격→SMP의 일방향 인과를, Moon & Jung (2020, *Utilities Policy* 67, 10.1016/j.jup.2020.101132)은 LNG 수입가–SMP의 지속적 양의 상관을 보였다. v2가 추정한 전력–LNG 0.905는 이 구조와 부합한다. Bolinger, Wiser & Golove (2006, *Energy Policy* 34(6))는 연료가격 위험이 없는 대안의 헤지 가치를, Bielefeld et al. (2025, *Energy* 335)은 전력가격 변동성이 산업 전기화 설비 규모를 바꿈을 보인다.

**PPA·조달 헤지.** Gabrielli, Aboutalebi & Sansavini (2022, *Energy Economics* 109, 10.1016/j.eneco.2022.105980)는 PPA 포트폴리오를 CVaR로 최적화했고, Trivella, Mohseni-Taheri & Nadarajah (2023, *Management Science* 69(1), 10.1287/mnsc.2022.4354)는 VPPA 조달을 MDP로 풀었다. Mohseni Taheri et al. (2025, *EJOR* 320(1), 10.1016/j.ejor.2024.08.002)은 물리 vs 가상 PPA를 비용–현금흐름 안정성 상충으로, Qorbanian, Löhndorf & Wozabal (2025, *EJOR* 326(3), 10.1016/j.ejor.2025.05.054)은 구매자 관점 PPA 가치를 다룬다.

**탄소가격 확률과정.** Benz & Trück (2009, *Energy Economics* 31(1))은 EUA 수익률의 왜도·첨도·변동성 국면 때문에 마르코프 스위칭·AR-GARCH를 권고한다 — v2의 연간 GBM에 대한 가장 직접적인 반론이다. Chevallier (2009, *Energy Economics* 31(4))는 탄소선물과 거시변수의 약한 연결을 보여, 탄소–연료 상관을 따로 추정해야 함을 뒷받침한다(v2 추정치 0.01–0.20). Jang et al. (2024, *RSER* 195, 10.1016/j.rser.2024.114346)은 K-ETS·EU ETS를 GARCH로 시뮬레이션해 KAU가 기관 전망가에 도달할 확률이 15% 미만임을 보였다 — KAU 분포 설정의 직접 근거다. Abadie & Chamorro (2008, *Energy Economics* 30(6))와 Zhou et al. (2010, *Applied Energy* 87(7))은 확률적 탄소가격 아래 CCS 투자시점의 실물옵션 선례다. Daskalakis, Psychoyios & Markellos (2009, *JBF* 33(7))는 서지만 확인했고 "점프확산 최적" 결론은 초록에서 확인하지 못했다.

**기업·자산 수준 전환위험.** Dietz et al. (2016, *Nat. Clim. Change* 6, 10.1038/nclimate2972)의 climate VaR, Battiston et al. (2017, 10.1038/nclimate3255), Bolton & Kacperczyk (2021, *JFE* 142(2)), Kampmann et al. (2026, *Nat. Commun.* 17:6410 — 20개사 중 3개사만 파리 정합, 철강 자산 42%가 2030년 전 재투자 필요), Ostrovnaya et al. (2026, *Commun. Earth Environ.* 7:524 — 비용전가율이 재무회복력을 좌우, 철강 자본수요가 시총의 최대 600%). 어느 것도 계획별 비용분포의 꼬리를 비교하지 않는다. IFRS S2(2023) 문단 22·B1–B18은 "기업 상황에 상응하는 시나리오 분석으로 회복력 평가"를 요구하되 정량 분석을 의무화하지 않는다.

**위험척도 이론.** Artzner et al. (1999, *Math. Finance* 9(3), 10.1111/1467-9965.00068): 분위수는 준가법성을 만족하지 않는다. Rockafellar, Uryasev & Zabarankin (2006, *Finance Stoch.* 10, 10.1007/s00780-005-0165-8): ES−μ 형태의 편차척도 공리. ES가 정합적이라는 결론은 Acerbi–Tasche 계열 후속연구이며 이번에 별도 확인하지 않았다.

## 이 연구가 메우는 빈틈 (한 문단)

CVaR 기반 선택은 발전 포트폴리오(ShahNazari; Zhang)와 전력 조달계약(Gabrielli; Trivella)에 따로따로 적용돼 왔고, 산업 탈탄소 문헌(Bachorz; Vogl; Layritz; Lee)은 투입가격을 결정론적 격자나 단일변수 몬테카를로로 다룬다. 한국에서 SMP가 LNG에 연동된다는 사실은 확립돼 있지만(Chae; Moon & Jung), 그 연동이 철강·석화의 연료전환 설비투자에 주는 자연 헤지·역헤지 효과 — 전기화가 탄소·석탄 노출을 줄이는 대신 LNG 연동 전력 노출을 키운다는 것 — 를 정량화한 연구는 찾지 못했다. 기업 전환위험 문헌(Kampmann; Ostrovnaya)은 배출경로와 마진을 제시할 뿐 계획별 비용분포의 꼬리를 비교하지 않는다. 따라서 설비투자와 계약을 같은 후보집합에 놓고, 전력·탄소·석탄·LNG의 결합 가격경로 아래 계획 자체의 절대비용 ES90과 기대 증분비용을 축으로 하는 기업 단위 프런티어는 비어 있는 자리다. 이것이 "불확실성을 줄이는 자본지출의 효율성"을 IFRS S2 문단 22의 회복력 평가에 바로 쓸 수 있는 형태로 재는 방법이다.

## 정직한 중복과 한계

평균–CVaR 프런티어 자체는 표준 기법이고, 계약을 CVaR 후보로 두는 발상은 Gabrielli(2022)·Mohseni Taheri(2025)와, 헤지 자산 추가를 CVaR로 재는 것은 ShahNazari(2015)와 겹친다. 기여는 방법이 아니라 적용 — 한·일 산업, 네 가격의 결합 시뮬레이션, 설비와 계약의 통합 — 에 있다. 연간 GBM은 Benz & Trück·Jang의 국면전환·GARCH 결과와 충돌하므로 대안 확률과정 강건성이 필요하다(L5). 전력–LNG 0.91은 한국 제도(SMP 결정구조·규제요금)에 좌우되므로 일본에 그대로 옮기기 어렵다 — JEPX 별도 추정이 필요하다(L3). ES_abs는 준가법적이지만 ES−μ 형태는 편차척도 공리를 따로 확인해야 하며, 포트폴리오 합산 주장은 이 구분을 명시해야 한다(L5).

## 확인하지 못해 제외한 것

K-ETS 시장안정화조치의 동료심사 논문(ICAP·IETA 보고서만 검색됨), "carbon cost at risk" 명칭의 학술 방법론(S&P Trucost 방법론 문서만 존재), Wolf (2025, *Economia e Politica Industriale* 52(4)) 유럽 철강 CCfD 위험배분(서지만 확인), 수소제철 복수 불확실성 투자전략(PubMed 38522276, 저자·학술지 미확인).
