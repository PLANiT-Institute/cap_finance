# L7 — 실물옵션: 불확실성이 투자를 "앞당기는" 조건의 문헌 정식화

목적: L1~L6에서 세운 척추(조기 전환은 접근형 위험만 헤지, 6조건 성립 시만 정당화)의 이론적 심장을 검증한다. 표준 실물옵션은 "불확실성↑ → 대기옵션 가치↑ → 투자 지연"을 예측한다. CAP은 이 표준 결과의 정반대 방향 — "전환이 헤지이기 때문에 불확실성이 전환을 앞당긴다" — 을 주장하려 한다. 이 주장이 문헌에서 이미 정식화된 조건들의 특수 사례인지, 아니면 CAP이 새로 만들어야 하는 명제인지를 확인한다.

모든 항목은 WebSearch/WebFetch로 실제 확인했으며, 원문 abstract/PDF를 직접 열람한 경우와 2차 서술(검색 스니펫)로만 확인한 경우를 구분해 표시했다. 확인 불가능한 부분은 "미확인"에 명시한다.

---

## 표준 실물옵션 지연과 예외

### 표준 결과

- **[McDonald, R. & Siegel, D. (1986), "The Value of Waiting to Invest," Quarterly Journal of Economics 101(4), 707–727 | https://academic.oup.com/qje/article-abstract/101/4/707/1840173]** — 편익과 투자비용이 각각 연속시간 확률과정을 따르는 비가역적 프로젝트에서, 위험회피적이고 잘 분산된 투자자를 가정할 때 최적 투자 규칙과 투자옵션 가치의 명시적 공식을 도출. 합리적 파라미터 하에서 편익이 투자비용의 약 2배가 될 때까지 대기하는 것이 최적 — 즉 옵션가치가 투자를 지연시킨다는 정량적 벤치마크(NBER Working Paper 1019로도 유통).
- **[Dixit, A. K. & Pindyck, R. S. (1994), *Investment under Uncertainty*, Princeton University Press | https://press.princeton.edu/books/hardcover/9780691034102/investment-under-uncertainty]** — 비가역적 투자에서 미래 수익이 불확실하고 대기를 통해 그 불확실성이 해소된다면, 투자기회의 기대현재가치는 즉시 투자할 때의 기대현재가치보다 크다. "대기옵션 가치"가 표준 결과의 핵심이며, 일회성·비가역적 투자결정에 특히 잘 적용된다는 점도 명시.

### 예외 (a) — 헤지·보험 동기의 투자

- **[Miao, J. & Wang, N. (2007), "Investment, Consumption, and Hedging under Incomplete Markets," NBER Working Paper 13250, 이후 Journal of Financial Economics 게재 | https://www.nber.org/papers/w13250, https://www.nber.org/system/files/working_papers/w13250/w13250.pdf]** — 표준 실물옵션을 불완전시장으로 확장. 일시불(lump-sum) 투자 수익구조와 충분히 강한 예비적 저축동기(precautionary savings motive)를 가진 행위자에게는, 변동성 증가가 표준 실물옵션 분석과 반대로 투자를 **가속**시킬 수 있음을 보임. 행위자가 시장 포트폴리오로 투자위험을 부분적으로 헤지할 수 있을 때, 체계적 변동성은 CAPM 논리로 보상되고 특이적(idiosyncratic) 변동성은 사적 자기자본 프리미엄을 발생시킴.
- **[Ewald, C. O. & Taub, B. (2022), "Real options, risk aversion and markets: A corporate finance perspective," Journal of Corporate Finance 72, 102155 | https://www.sciencedirect.com/science/article/pii/S0929119922000074, SSRN https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3289100]** — Shackleton & Sodal (2005)을 확장해 위험회피적 행위자의 실물옵션 최적 행사를 금융시장 존재 하에서 분석. 특이적 위험(idiosyncratic risk)이 옵션 행사 속도에 미치는 효과를 명확히 규명하고, **체계적 위험(systematic risk)은 오히려 행사를 가속시키고 콜형 옵션의 가치를 낮출 수 있음**을 보임 — "가치와 행사 문턱이 모두 변동성에 대해 증가한다"는 표준 견해와 정면으로 대비되는 결과. CAP의 "전환이 체계적 노출을 낮추는 헤지"라는 주장과 구조적으로 가장 가까운 정식화.

### 예외 (b) — 성장옵션·확장옵션

- **[Hartman, R. (1972), "The Effects of Price and Cost Uncertainty on Investment," Journal of Economic Theory 5(2), 258–266 — 검색 스니펫으로 확인, 원문 미열람] / Abel, A. B. (1983), "Optimal Investment Under Uncertainty," American Economic Review 73(1), 228–233 | https://repository.upenn.edu/fnce_papers/220/]** — 규모수익불변(linearly homogeneous) 생산함수와 완전경쟁 하에서, 산출가격 불확실성 증가가 경쟁기업의 투자를 **증가**시킴(Hartman-Abel 효과). 자본의 한계생산성이 가격에 대해 볼록(convex)하기 때문에 옌센부등식에 의해 불확실성 증가가 자본의 한계가치를 높임. 단, 한계조정비용함수가 오목(concave)하면 반대 효과가 나타나 부호가 불확실해짐 — 이 조건성이 중요.
- **[검색 스니펫, ScienceDirect S105752191730039X, "Strategic growth option, uncertainty, and R&D investment," Journal of Corporate Finance — 저자/연도 원문 미확인]** — 불완전경쟁 하에서 불확실성이 성장옵션을 창출해 선점(preemption)이 R&D 투자와 불확실성의 양(+)의 관계를 만드는 핵심 동력. 경쟁이 심한 산업, 시장지배력이 낮은 기업일수록 이 효과가 뚜렷함.

### 예외 (c) — 선점 위협

- **[Chevalier-Roignant, B. & Trigeorgis, L. (2011), *Competitive Strategy: Options and Games*, MIT Press | https://mitpress.mit.edu/9780262526715/competitive-strategy/, https://direct.mit.edu/books/monograph/2194/Competitive-StrategyOptions-and-Games]** — 실물옵션과 게임이론을 결합한 "옵션게임(option games)" 접근을 체계화. 전략적 불확실성과 시장 불확실성에 동시에 노출된 경영자는 경쟁자 행동에 영향을 주기 위한 즉시 대규모 투자(commitment)와, 불리한 시장상황을 피하기 위한 대기(flexibility) 사이에서 트레이드오프에 직면. 복점(duopoly)에서의 선점 대 협조를 이산시간·연속시간 옵션게임으로 다룸 — 대기의 가치(불확실성 해소)와 대기의 비용(경쟁적 선점당함)이 명시적으로 충돌하는 구조.
- **[검색 스니펫, ScienceDirect S1058330005000029, "Real options, irreversible investment and firm uncertainty: New evidence from U.S. firms" — 원문 미열람]** — 실물옵션 이론상 기업은 높은 불확실성 하에서 투자를 줄이지만, 불완전경쟁 하에서는 불확실성이 오히려 성장옵션에 대한 투자를 촉진할 수 있다는 반례를 실증적으로 확인.

**소결**: 표준 실물옵션의 "지연" 결과를 뒤집는 예외는 (a) 헤지·보험 동기, (b) 볼록한 이윤함수·성장옵션, (c) 경쟁적 선점이라는 세 갈래로 문헌에서 이미 명확히 갈라져 있다. CAP이 기대는 것은 (a)이며, Miao & Wang (2007)과 Ewald & Taub (2022)가 이 갈래의 가장 정밀한 정식화다.

---

## Fuss 2008 방향

- **[Fuss, S., Szolgayova, J., Obersteiner, M. & Gusti, M. (2008), "Investment under market and climate policy uncertainty," Applied Energy 85(8), 708–721, DOI 10.1016/j.apenergy.2008.01.005 | https://www.sciencedirect.com/science/article/abs/pii/S0306261908000287 (원문 paywall — 403), 저자 프로필/저장소: https://pure.iiasa.ac.at/view/iiasa/101.html, https://pure.iiasa.ac.at/view/iiasa/305.html, ResearchGate 요약 https://www.researchgate.net/publication/237633986_Energy_Investments_under_Market_and_Climate_Policy_Uncertainty]**
  - **확인된 방향성**: 실물옵션 프레임에서 발전설비 투자자가 시장(가격) 불확실성과 기후정책 불확실성(정부의 정책 공약에 대한 학습)에 동시에 노출된 상황을 분석. 복수의 독립 검색 스니펫(ResearchGate 초록 요약, 일반 검색 결과 종합)이 일관되게 보고하는 결론은 **"탄소/시장 가격 변동성은 투자를 앞당길 수 있는 반면, 정책 불확실성(정책 체제의 신뢰성·지속성에 대한 불확실성)은 투자를 지연시킨다"**는 방향.
  - **주의**: ScienceDirect 원문이 403으로 차단되어 초록 원문을 직접 인용하지 못했다. 위 방향성은 논문 자체가 아니라 2차 검색 스니펫들의 일치로 확인한 것이며, 정확한 수치·메커니즘(가격 불확실성이 왜 앞당기는지의 정확한 채널)은 미확인으로 남긴다.
  - **CAP과의 관계**: CAP의 설계는 이 논문의 정책축을 고정하는 것과 구조적으로 대응한다 — CAP은 정책을 시나리오(조건)로 고정하고 투입가(에너지·탄소)와 접근(대출·보험) 축만 흔든다. Fuss et al.의 결과를 그대로 가져오면, "정책 고정 + 시장가 변동성"이라는 CAP의 설정 자체가 이미 "투자를 앞당기는 방향"에 유리한 조건을 선택한 셈이 된다 — 이는 CAP 결과 해석에서 반드시 명시해야 할 조건부성(conditionality)이다. Fuss et al.의 후속 연구인 Szolgayova et al. (2011, 아래)이 같은 저자군의 CVaR-실물옵션 결합 모델로 이어진다는 점도 CAP의 방법론적 계보를 뒷받침한다.

---

## 헤지 동기 투자 (분산↑→문턱↓)

핵심 문헌은 위 "예외 (a)"에서 이미 확인한 두 편이며, 여기서는 메커니즘을 더 구체화한다.

- **[Miao & Wang (2007/NBER WP13250)]** — 두 가지 반대 효과가 공존: (i) 표준 실물옵션 효과(변동성↑ → 옵션가치↑ → 투자 지연), (ii) 예비적/보험 동기 효과(변동성↑ → 인증등가부(certainty-equivalent) 부(wealth) 하락 → 투자를 서두름). 특이적(project-specific) 변동성이 옵션가치와 투자시점 결정에 상반된 두 채널로 작동한다는 점이 명시적으로 분리되어 있다. **"위험이 헤지 불가능해질수록(unhedgeable) 행사 문턱이 낮아진다"**는 문장이 검색 스니펫에서 확인됨 — 이는 CAP의 "접근형 위험(헤지 불가능한 자금조달 마찰)이 조기 전환의 정당화 조건"이라는 주장과 정확히 대응.
- **[Ewald & Taub (2022, JCF)]** — 체계적 위험이 클수록 행사가 가속되고 콜옵션 가치가 낮아진다는 결과는, "위험회피적 행위자가 시장에서 헤지 가능한 위험을 이미 가격에 반영하고 있을 때, 추가 위험 증가는 대기의 매력을 낮춘다"는 논리로 해석 가능. 이는 표준 real option value-of-waiting 결과가 시장 완전성·위험중립성 가정에 의존한다는 것을 보여주는 정밀한 반례.
- **[검색 스니펫, ScienceDirect S0304405X07001225 (Miao & Wang의 저널판, Journal of Financial Economics), 및 관련 "Real options, risk aversion and markets" 스니펫]** — 자연헤지(natural hedge) 관점: 기업이 이미 노출된 위험(예: 원자재 가격, 환율)을 상쇄하는 방향의 실물투자는 운영적 헤지(operational hedge)로 기능하며, "기업가치가 높아지고 투자가 가속된다"는 서술이 확인됨(단, 이 서술은 학술 데이터베이스 초록이 아니라 일반 검색 스니펫 수준이므로 신뢰도가 상대적으로 낮음 — 미확인으로 별도 표시).

**CAP 대응**: 전환투자가 무전환 반사실(counterfactual)의 탄소가·에너지가 꼬리 노출을 줄이는 방향이라면(음의 상관, 자연헤지), Miao & Wang과 Ewald & Taub의 정식화는 "그 헤지가 강할수록 변동성 증가가 투자를 앞당긴다"는 명제를 지지한다. 단, 이 명제가 성립하려면 (i) 전환투자가 실제로 기존 노출과 음의 상관을 가져야 하고(자연헤지의 존재), (ii) 그 상관이 시장에서 거래 불가능해야 한다(불완전시장 조건) — 두 조건 모두 CAP의 6조건 체크리스트에 이미 포함되어 있는지 확인이 필요하다.

---

## 확률적 탄소가 하 전환 시점

- **[Xu, S., Wang, X., Jiang, Y., Yu, B. & Wei, Y.-M. (2024), "Optimum investment strategy for hydrogen-based steelmaking project coupled with multiple uncertainties," Journal of Environmental Management 356, 120484, DOI 확인: PubMed ID 38522276 | https://pubmed.ncbi.nlm.nih.gov/38522276/, https://www.sciencedirect.com/science/article/abs/pii/S0301479724004705]** — Least Squares Monte Carlo(LSM)로 다차원 불확실성(철강가격, 탄소시장, 수소가격, 보조금) 하 수소환원제철(H-DRI) 투자의 최적 시점과 가치를 분석. 기존 연구가 특정 경로의 내재가치만 고려해 불확실성 하의 옵션가치를 과소평가한다는 문제의식에서 출발. **수소가격의 연간 하락률이 5%에 도달하면 최적 투자시점이 2036년으로 앞당겨지고, 20% 그린수소 보조금이 추가되면 2033년으로 더 앞당겨진다**는 정량적 결과 확인(검색 스니펫 경유, 원문 표는 미열람). 즉 여기서 "불확실성"이 아니라 "기대경로의 개선(가격 하락 추세, 보조금)"이 투자를 앞당기는 채널이며, 변동성 자체의 부호 효과는 이 요약에서 명시적으로 분리되지 않음 — 미확인.
- **[검색 스니펫, ScienceDirect S0360544223024519, "Decarbonization strategies for steel production with uncertainty in hydrogen direct reduction," *Energy* (2023) — 저자 원문 미확인, 한국 철강산업 에너지시스템모형 + 몬테카를로]** — 수소환원제철의 내부 불확실성(투자비용)과 외부 불확실성(수소가격, 배출계수)을 구분. **수소가격 불확실성이 수소 사용량·배출량·감축비용 편차를 좌우하는 가장 중요한 요인**이며, 철강부문 배출이 목표에서 이탈할 확률이 수소가격 불확실성 하에서 가장 높다는 결과. 이 논문은 "불확실성이 전환을 앞당긴다"는 명제를 직접 다루지 않고 "불확실성이 목표달성 리스크를 키운다"는 반대 방향의 함의에 가깝다 — CAP 주장과 대비되는 사례로 인용 가능.
- **[Tautorat, P., Iversen, J., Schmidt, T. S. & Steffen, B. (2025), "Real options analysis of decarbonization investments in the chemical industry," Applied Energy 397, 126238 | https://www.sciencedirect.com/science/article/pii/S0306261925009687, ADS 초록 https://ui.adsabs.harvard.edu/abs/2025ApEn..39726238T/abstract]** — 석유화학(chemical industry) 탈탄소 투자에 실물옵션 적용. **ETS(배출권거래제) 탄소가격 하한(price floor) 180 EUR/t이 배출권 시장의 불확실성을 상쇄해 저온 공정 적용 기술에 대한 조기 투자 확률을 높인다**는 결과 확인. 이는 "정책이 불확실성을 줄여 투자를 앞당긴다"는 방향으로, 표준 실물옵션과 일치하는 결과(불확실성↓ → 투자↑)이지 CAP이 주장하는 "불확실성↑ → 투자↑"의 직접 증거는 아니다 — 구분 필요.

**소결**: 철강·석화 실물옵션 문헌에서 확인되는 것은 주로 "기대가격 경로의 개선"이나 "정책에 의한 불확실성 축소"가 전환을 앞당긴다는 표준 방향이다. "가격 변동성 그 자체의 증가"가 전환 시점을 앞당긴다는 직접적 결과는 이번 검색에서 확인하지 못했다 — 이는 CAP이 채워야 할 간극이며, section의 "헤지 동기 투자" 프레임(Miao & Wang, Ewald & Taub)과 이 절의 산업별 실증(Xu et al., Tautorat et al.)을 CAP이 직접 연결하는 것이 새로운 기여가 될 수 있다.

---

## ES/CVaR 위험효율에서 조기 전환

- **[Fortin, I., Fuss, S., Hlouskova, J., Khabarov, N., Obersteiner, M. & Szolgayova, J. (2007), "An Integrated CVaR and Real Options Approach to Investments in the Energy Sector," IHS Economics Series Working Paper 209 (이후 Journal of Energy Markets 게재) | https://irihs.ihs.ac.at/id/eprint/1770/1/es-209.pdf (원문 PDF 직접 열람), https://www.risk.net/journal-of-energy-markets/2160790/an-integrated-cvar-and-real-options-approach-to-investments-in-the-energy-sector]**
  - **직접 확인(원문 열람)**: 실물옵션 모형(석탄/석탄+CCS, 바이오매스/바이오매스+CCS, 육상풍력 세 기술, 세 가지 CO₂ 가격 시나리오)의 수익률 분포를 산출해 이를 포트폴리오 최적화의 입력으로 사용하고, 리스크 척도로 CVaR(β=95%)을 사용. 표 3(원문 Table 3)의 확인된 수치: 시나리오 1(고탄소가격)에서 석탄의 −CVaR = 1.621, 바이오매스 = 1.717, 풍력 = 1.705 — **고탄소가격 시나리오에서 저탄소 기술(바이오매스)이 가장 낮은 꼬리위험(가장 매력적인 −CVaR)을 가짐**이 명시적으로 확인됨("Biomass is the least risky option in scenario 1 in terms of CVaR"). 이는 기대수익 기준으로는 코스트가 더 높거나 변동성이 클 수 있는 저탄소 기술이, CVaR(꼬리위험) 기준으로는 고탄소 시나리오에서 비지배적(효율적)이 될 수 있음을 보여주는 정량 사례.
  - **한계**: 이 논문은 "조기 전환의 최적 시점이 위험회피도(λ 또는 CVaR 가중치)에 따라 어떻게 이동하는가"를 명시적인 파라미터 스윕으로 제시하지는 않는다(원문에서 확인한 범위 내). 저자들이 강조하는 것은 "정규분포·평균-분산 가정이 부적절하다"는 점과 "CVaR가 두터운 꼬리를 가진 수익분포에서 분산보다 적절한 위험척도"라는 방법론적 주장이지, "위험회피가 높을수록 조기전환이 선택된다"는 CAP식 명제 자체는 아니다. 이 부분은 미확인으로 남긴다 — CAP이 직접 파라미터 스윕을 통해 검증해야 할 명제.
  - 관련 후속판: **[Szolgayová, J., Fuss, S., Khabarov, N. & Obersteiner, M. (2011), "A dynamic CVaR-portfolio approach using real options: an application to energy investments," European Transactions on Electrical Power 21(6) | https://onlinelibrary.wiley.com/doi/10.1002/etep.429, IIASA 저장소 https://pure.iiasa.ac.at/id/eprint/9512/]** — 위 IHS 워킹페이퍼의 동적(dynamic) 확장판으로 확인(원문 paywall — 403, 초록 수준만 확인). "전기 부문의 불확실한 기후정책 하 투자에 이 접근이 총량적 투자와 정책이 투자패턴·에너지믹스에 미치는 효과 평가 모두에 유용함"이라는 결론이 검색 스니펫에서 반복 확인.
- **[Ewald & Taub (2022, JCF), 위와 동일]** — 위험회피 자체가 옵션 행사 문턱과 가치에 미치는 효과를 명시적 자산가격결정(asset pricing) 관점에서 다룬다는 점에서, "위험회피도 λ가 높은 의사결정자가 조기 전환을 선택하는 조건"에 대한 이론적 기초로 이 논문을 인용하는 것이 Fortin et al. (2007)보다 더 직접적일 수 있다 — CAP이 정식화 시 참고할 후보.

**소결**: 평균-CVaR(또는 평균-ES) 평면에서 "고탄소가격 시나리오에서는 저탄소 기술이 꼬리위험 기준으로 비지배적"이라는 명제는 Fortin et al. (2007)의 실제 수치로 뒷받침된다. 그러나 "위험회피도가 높을수록 조기 전환을 선택한다"는 CAP 고유의 명제(λ에 대한 비교정학)는 기존 문헌에서 명시적 파라미터 스윕으로 확인되지 않았다 — CAP이 채워야 할 간극.

---

## CAP 정식화에 주는 함의

1. **이론적 근거는 이미 존재한다.** 표준 실물옵션(McDonald-Siegel, Dixit-Pindyck)의 "지연" 결과는 보편 법칙이 아니라 특정 가정(시장 완전성, 위험중립적 할인, 이윤함수의 오목성) 하의 결과이며, 그 가정이 깨지는 세 갈래(헤지/보험 동기, 볼록 이윤함수·성장옵션, 경쟁적 선점) 중 CAP은 명확히 첫 번째(헤지·보험 동기)에 속한다. Miao & Wang (2007)과 Ewald & Taub (2022)가 이 갈래의 가장 정밀한 기존 정식화이며, CAP은 이를 인용해 "왜 조기 전환이 표준 실물옵션과 모순되지 않는가"를 방어할 수 있다.

2. **CAP의 6조건은 Miao & Wang의 두 조건과 구조적으로 대응해야 한다.** Miao & Wang (2007)에서 "변동성이 투자를 앞당기려면" 필요한 것은 (i) 투자가 기존 노출과 음의 상관(자연헤지)을 가질 것, (ii) 그 상관이 시장에서 거래·헤지 불가능할 것(불완전시장). CAP의 6조건 중 "접근형 위험만 헤지"라는 제약이 정확히 이 (ii)를 겨냥하고 있는지, "무전환 반사실의 탄소·에너지 꼬리를 줄인다"는 서술이 (i)을 만족하는지 각각 명시적으로 대응시켜야 한다.

3. **Fuss et al. (2008)의 정책-고정 설정은 CAP 결과의 조건부성을 강화하되 동시에 제한한다.** CAP이 정책을 시나리오로 고정하는 것은 Fuss et al.이 보인 "정책 불확실성은 지연시킨다"는 효과를 사전에 차단하고 "시장가 불확실성은 앞당긴다"는 효과만 남기는 설계다. 이는 CAP의 결과가 "정책이 고정되어 있다는 조건 하에서만" 성립한다는 것을 뜻하며, 논문에서 이 조건을 명시하지 않으면 반사실적으로 지나치게 낙관적인 결과로 오독될 위험이 있다.

4. **철강·석화 실증 문헌은 아직 CAP의 핵심 주장(변동성 증가 자체가 전환을 앞당긴다)을 직접 검증하지 않았다.** Xu et al. (2024)과 Tautorat et al. (2025)이 보이는 것은 "기대가격 경로의 개선" 또는 "정책에 의한 불확실성 축소"가 투자를 앞당긴다는 것이며, Energy(2023) 논문은 오히려 "수소가격 불확실성이 목표이탈 위험을 키운다"는 반대 방향에 가깝다. CAP이 "변동성의 증가 그 자체"가 전환을 앞당긴다고 주장하려면, 이 산업별 실증들과의 차이(정책축 고정 여부, 헤지 여부 등)를 명시적으로 설명해야 한다 — 이것이 L7이 채워야 할 CAP 고유의 기여 지점이다.

5. **평균-CVaR 비지배성은 이미 사례로 확인되나, λ에 대한 비교정학은 CAP이 직접 도출해야 한다.** Fortin et al. (2007)의 실제 수치(고탄소가격 시나리오에서 바이오매스의 −CVaR이 석탄보다 우월)는 "위험 효율적 관점에서 저탄소 기술이 비지배적일 수 있다"는 CAP 5절 주장의 선례이지만, "위험회피도(λ)가 커질수록 조기 전환이 선택된다"는 명제 자체는 문헌에서 파라미터 스윕으로 확인된 바 없다 — CAP의 ES/CVaR 프레임에서 이 비교정학을 직접 수행하는 것이 이 논문의 독자적 기여가 되어야 한다.

---

## 미확인

- Fuss et al. (2008, Applied Energy)의 정확한 메커니즘·수치·초록 원문 — ScienceDirect가 403으로 차단되어 2차 검색 스니펫(ResearchGate 요약, 일반 검색 종합)으로만 방향성을 확인. 원문 열람 필요.
- Szolgayova et al. (2011, ETEP)와 관련 IIASA/Wiley 원문 — 두 URL 모두 403/access denied로 차단되어 초록 수준만 확인.
- Hartman (1972)의 원문 — 검색 스니펫에서만 확인, 1차 문헌 미열람.
- "Strategic growth option, uncertainty, and R&D investment" (ScienceDirect S105752191730039X)의 저자명·정확한 연도 — 원문 미열람, 제목과 저널(Journal of Corporate Finance 추정)만 확인.
- "Real options, irreversible investment and firm uncertainty: New evidence from U.S. firms" (ScienceDirect S1058330005000029)의 저자명·연도 — 원문 미열람.
- "자연헤지가 실물옵션에서 투자를 가속시킨다"는 일반 서술(자연헤지 섹션 인용) — 학술 데이터베이스 초록이 아닌 일반 검색 요약 수준으로, 원 출처(저자·저널) 특정 실패.
- Sarkar (2000/2003)의 평균회귀-변동성-투자확률 관계 — 검색 스니펫에서 "부호가 불확실(ambiguous)"하다는 것과 "평균회귀가 투자에 유의미한 영향을 미친다"는 것까지는 확인했으나, 정확한 저널·권호·수치는 미확인. 이번 5개 항목의 직접 임무 범위에는 포함되지 않아 본문에서 제외.
- Fehr, Hoppe 관련 문헌 — 검색 결과 전무. 사용자가 언급한 "reluctance to invest 역전 조건"의 저자로 이 이름이 맞는지 자체가 불확실. Miao & Wang (2007), Ewald & Taub (2022)로 해당 내용을 대체 확인함.
- Xu et al. (2024, J. Environ. Manage.)의 원문 표·수치(투자시점 앞당김의 정확한 메커니즘이 변동성 때문인지 기대경로 개선 때문인지) — PubMed가 쿠키 동의 화면만 반환해 원문 확인 실패, ScienceDirect 초록 요약(검색 스니펫)에만 의존.
- Fortin et al. (2007) 원문에서 "위험회피 파라미터(λ)를 스윕해 조기 전환 선택을 직접 보이는" 절이 존재하는지 여부 — 열람한 페이지(1~14쪽 상당)에서는 발견하지 못했으며, 후반부(포트폴리오 최적화 결과, 원문 20쪽 이후로 추정)를 전부 확인하지는 못함. 완전한 결론을 위해서는 추가 열람 필요.

---

# SYNTHESIS L7 (실물옵션·두 계보 결합) — 2026-09-13 · 이론 심장 정초

## 이론 부담 판정 — 세 층
1. **헤지 계보 = 정초됨.** Miao-Wang(2007): 예비적·보험 동기 + 비거래 위험이 투자 문턱을 낮춤.
   Ewald-Taub(2022): 체계적 위험이 행사를 가속(표준 정반대). CAP의 6조건(L5)이 Miao-Wang의 두
   필요조건 — **자연 헤지 존재 + 시장 비거래성** — 에 정확히 대응한다. 이게 이론 앵커.
2. **선점 계보 = 정초됨.** Grenadier(2002) 등 경쟁적 실물옵션이 대기옵션 침식을 정식화(단 위험중립).
3. **결합 = 좁은 공백.** Chronopoulos(2014)가 위험회피+복점을 결합한 유일 선행이나, CAP의
   "상태조건부 헤지 + 물량배급형 선점 + ES 비지배"는 없음. novelty를 이 좁은 형태로 정직하게 주장.

## 정식화 = 직교 분해 (구현 가능·이중계상 방어)
- (a) 헤지 효과 = **상태 함수** — 무전환 꼬리 상태에서 조기 전환이 노출 감소(시나리오 설계).
- (b) 선점 효과 = **시간 함수** — 늦을수록 배급실패확률↑·단가↑(MILP 결정론 계수).
직교(상태 vs 시간)라 이중계상 없음. 소거실험(b→0 무제한 계통, a→0 무전환 확률 0)으로 분해 보고.
가법성 주장 말고 분해 수치를 그대로 보고(Chronopoulos가 "위험회피×경쟁은 비가산" 이미 보임).

## 실증 부담은 남는다 — 그리고 반례를 녹인다
철강·석화 실증(Xu 2024·Energy 2023·Tautorat 2025)은 "변동성 증가 자체가 전환을 앞당긴다"를 직접
검증하지 않고, 하나(Energy 2023)는 반대 방향(수소가 불확실성이 목표이탈 위험↑). **반례 해소**: 그
논문들은 수소 **가격** 불확실성을 흔든 것인데, L3에서 CAP은 수소를 가격형이 아니라 접근·제도형으로
판정했다. 반례는 가격형 축, CAP 주장은 접근형 확보 — **축이 다르다.** 반대 방향 결과는 CAP과
모순이 아니라 "수소 가격을 GBM으로 흔들면 안 된다"는 L3 결론의 재확인. 다만 CAP의 고유 주장
(접근형 선점이 조기 전환을 위험효율로)은 여전히 CAP이 자기 데이터로 처음 보여야 한다 — 기여이자 부담.

## 직전(L1~L6) 비판적 재검토
L5에서 "두 계보 결합이 이론 부담"이라 했는데, L7이 그것을 **구현 문제로 축소**했다 — 새 정리가
아니라 상태축·시간축 분리 분해. 그리고 L7이 L1~L6 전체를 한 번 더 정당화한다: 위험을 세 종류로
가른 게(L1~L4) 여기서 값을 한다 — 가격형(수소 GBM 반례가 사는 곳)과 접근형(CAP 주장이 사는 곳)을
안 갈랐으면 반례에 그냥 당했을 것. 세 종류 분류가 이론적으로도 방어선이 된다.

## 분포·모형 함의 (L7)
- 헤지 효과: 무전환 반사실을 시나리오에 명시적으로 두고(이미 있음), 조기/지연 사다리에서 상태별
  노출 감소를 잰다. 종가 처리(2050 절단) 필수 — 없으면 지연이 유리해 보이는 착시(DIRECTION 조기전환 절).
- 선점 효과: 접근형 자원에 시간의존 페널티 f(t) = 배급실패확률(t)·단가승수(t). 결정론, MILP 계수.
- 소거실험 2개를 강건성 표에 — a축·b축 각각 끈 값. 이게 두 계보 결합의 검증.
- λ 비교정학(위험회피↑→조기 전환)은 CAP이 직접 도출(Fortin 2007은 사례만, 스윕 없음).
