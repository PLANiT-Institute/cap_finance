# L4 — 투자자·대출자의 전환비용 분포 가격화

날짜: 2026-09-13. 목적: L1~L3에서 얻은 "전환비용은 분포이고 세 주체(기업 first-loss·투자자 mezzanine·정부 catastrophe)가 다른 층을 진다"는 blended finance 언어 위에, 투자자·대출자가 실제로 이 분포(특히 상방 잔여, 즉 비용초과 꼬리)를 어떻게 인수하고 가격 매기는지 기존 문헌으로 확인한다. 새 이론 없음 — 전부 기존 신용리스크·프로젝트파이낸스·기관투자 실무 문헌에 얹음. WebSearch로 실제 확인한 것만 기재. 확인 못한 것은 마지막 섹션에 별도 표시.

---

## 전환리스크 신용·자본비용 가격화

기존 문헌은 "전환리스크가 신용스프레드·주식비용에 실제로 가격화된다"는 사실 자체는 여러 채널에서 반복 확인했다. 세 갈래로 나뉜다.

1. **CDS 스프레드 채널.** Kölbel, Leippold, Rillaerts, Wang (2024)는 BERT 기반 텍스트 분류기로 기업 공시에서 전환리스크·물리적리스크 언급을 분리하고, 파리협정(2015) 이후 전환리스크 공시가 CDS 기간구조(term structure)의 스프레드를 확대시킴을 보였다 — 공시가 새 리스크를 드러내면 스프레드 확대, 불확실성을 줄이면 축소라는 방향성 조건부 결과. [Kölbel, Leippold, Rillaerts, Wang (2024), "Ask BERT: How Regulatory Disclosure of Transition and Physical Climate Risks Affects the CDS Term Structure", Journal of Financial Econometrics 22(1), pp.30-69 | https://ideas.repec.org/a/oup/jfinec/v22y2024i1p30-69..html]

2. **주식 프리미엄(탄소 프리미엄) 채널.** Bolton & Kacperczyk (2021)은 14,400개 이상 기업·77개국 패널에서 탄소배출량·배출증가율이 높은 기업의 실현주식수익률이 체계적으로 높다는 "탄소 프리미엄"을 발견 — 투자자가 전환리스크를 반영해 자기자본비용을 더 요구한다는 해석. 이후 Bolton & Kacperczyk (2023, Journal of Finance)는 이를 글로벌 표본으로 확장("Global Pricing of Carbon-Transition Risk"). 다만 Aswani et al.의 반론 연구는 배출집약도(매출 대비) 또는 공시배출량 기준으로 보면 프리미엄이 유의하지 않다고 지적 — 논쟁 진행 중. [Bolton & Kacperczyk (2021), "Do Investors Care about Carbon Risk?", Journal of Financial Economics 142(2), pp.517-549 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3398441] [Bolton & Kacperczyk (2023), "Global Pricing of Carbon-Transition Risk", Journal of Finance | https://onlinelibrary.wiley.com/doi/10.1111/jofi.13272]

3. **회사채 스프레드·신용등급 채널.** Seltzer, Starks & Zhu는 파리협정을 규제 기대 충격으로 이용해, 고탄소·환경프로파일이 나쁜 발행사의 회사채 신용등급 하락·스프레드 확대에 대한 인과관계를 제시. 스프레드 확대는 자산가치 변화보다 자산변동성(volatility) 변화에서 온다는 점을 강조 — 즉 규제 불확실성이 꼬리 리스크(변동성)를 통해 가격에 반영된다는 뜻. **주의: 이 논문은 2026-09-13 확인 시점 기준 NBER Working Paper (No. 29994, 2022) 및 New York Fed Staff Report (No.1014, 2025년 3월 개정본)로만 확인되며, 동료심사 저널 게재 여부는 확인하지 못함 — 인용 시 working paper로 표기 필요.** [Seltzer, Starks & Zhu, "Climate Regulatory Risk and Corporate Bonds", NBER Working Paper No. 29994 / FRB New York Staff Report No. 1014 | https://www.nber.org/papers/w29994 , https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1014.pdf]

**우리 논문과의 관계**: 이 세 편은 전환비용 분포의 "상방 꼬리"가 신용·자본시장에서 이미 가격화된다는 것을 보여주지만, 전부 사후적(realized/disclosed risk)·횡단면 가격 반응 추정이다. 얼마의 전환비용 분포가 정확히 몇 bp의 스프레드로 번역되는지는 다루지 않는다 — CAP TCaR이 만드는 기업별 전환비용 분포를 이 스프레드 문헌의 우변(설명변수)으로 얹을 수 있는 자리.

---

## 프로젝트 파이낸스 뱅커빌리티

그린스틸·수소 등 FOAK(first-of-a-kind) 산업전환 프로젝트의 뱅커빌리티는 "오프테이크 계약이 있는가"로 사실상 결정된다는 것이 RMI 문헌의 반복된 결론이다.

- **오프테이크가 뱅커빌리티의 핵심.** RMI는 H2 Green Steel 사례를 분석하며, 스폰서가 다운사이드 리스크를 지는 오프테이커에게 비의결권 지분(non-voting equity)으로 보상하는 방식이 FOAK 오프테이크 계약을 뱅커블하게 만드는 핵심 장치라고 정리한다. H2 Green Steel은 초기 연간 생산량의 60% 이상을 Mercedes·Scania 등에 사전판매했고, 유럽투자은행(EIB)·수출신용기관(ECA)·스웨덴 국가부채청이 초기 투자 위험 경감에 핵심적 역할을 했다. [RMI, "Five Lessons for Industrial Project Finance from H2 Green Steel" | https://rmi.org/resources/five-lessons-for-industrial-project-finance-from-h2-green-steel/]
- **FOAK 리스크 분산의 논리.** FOAK 금융의 핵심은 "다수 투자자에게 프로젝트 리스크를 효율적으로 분산시켜 개별 투자자의 리스크를 낮추는 것" — 오프테이커에게 비의결권 지분 지급, 신용리스크를 국가 대차대조표(수출신용기관 등)로 이전하는 방식이 반복 등장. [RMI, 위 자료]
- **구속력 있는 계약이 뱅커빌리티의 관건.** 2030년대 초 납기를 맞추려는 공급자에게는 장기·구속력 있는 take-or-pay 오프테이크 계약을 확보하는 것이 정책 지원 불확실성·에너지가격 변동성에 대한 헤지로서 뱅커빌리티의 핵심(lynchpin)이라는 진단. [RMI, "How Financing Industrial Decarbonization Is Moving from Disclosures to Dealmaking" | https://rmi.org/how-financing-industrial-decarbonization-is-moving-from-disclosures-to-dealmaking/]
- **DSCR 벤치마크.** 재생에너지·인프라 프로젝트 중 장기 오프테이크 계약이 있는 경우 통상 DSCR 1.20x~1.35x가 요구되며, 국가리스크·통화리스크·오프테이크 계약 품질에 따라 문턱이 크게 달라진다는 것이 프로젝트파이낸스 실무 자료의 일반론. 그린수소 프로젝트는 오프테이커가 투자등급(BBB-/Baa 이상) 신용도를 갖추거나 그에 상응하는 보증을 제공할 것을 대출자가 요구하는 경우가 많다. [Green Hydrogen Organisation, "Key considerations for green hydrogen offtake agreements" (2024) | https://gh2.org/sites/default/files/2024-05/GH2_Considerations%20for%20Hydrogen%20Offtake%20Agreements_2024.pdf ; ProjectsRH, "Debt Service Coverage Ratio (DSCR) in Project Finance" | https://projectsrh.com/blog/debt-service-coverage-ratio/]

**대출자가 상방 꼬리를 어떻게 인수/전가하나**: 위 문헌들이 공통으로 보여주는 메커니즘은 "대출자는 상방 꼬리(비용 초과)를 직접 인수하지 않고 오프테이크·보증·수출신용기관·정부 지분참여로 전가한다"는 것 — 즉 대출자가 원하는 것은 분포 전체가 아니라 좁은 하방 구간(투자등급 오프테이커가 보장하는 현금흐름)이고, 상방 꼬리는 오프테이커의 비의결권 지분, ECA의 국가신용, 또는 정부 보조금으로 떠넘겨진다. 이는 L1~L3의 "정부=catastrophe layer" 프레임과 정확히 일치하지만, RMI 문헌은 이를 분포 언어로 정식화하지 않고 사례 서술(case narrative)에 머문다 — CAP가 채울 자리.

---

## Climate VaR 기관투자자 실무 (TCaR 계보)

- **원조: Dietz, Bowen, Dixon & Gradwell (2016)**. 전 세계 금융자산에 대해 "climate VaR"를 정의 — 21세기 기후변화가 금융자산 시장가치에 미치는 영향을 현재가치 손실 기대값으로 환산. business-as-usual 경로에서 전 세계 금융자산의 기대 climate VaR을 1.8%로 추정, 2°C 억제가 투자자에게 재무적으로 합리적이라는 결론. 이 논문이 "기후리스크를 포트폴리오 VaR로 환산한다"는 아이디어의 학술적 시조. [Dietz, Bowen, Dixon & Gradwell (2016), "'Climate value at risk' of global financial assets", Nature Climate Change 6, pp.676-679 | https://www.nature.com/articles/nclimate2972]
- **실무화: MSCI Climate VaR.** 기관투자자 실무에서 가장 널리 쓰이는 버전. 상장기업 1만개 이상·국채 9천개 이상을 커버하며, Scope 1·3 배출량, 전력소비, EVIC(기업가치+현금)를 입력으로 하여 그림자 탄소가격 등 시나리오 가정 하에 향후 50년 탈탄소화 비용을 현금흐름에 반영해 Transition Risk Climate VaR를 산출. 물리적 리스크는 보험업 방식(기대손실 = 취약도×위험도×노출도)을 차용. Scope 1 배출집약도가 가장 강한 설명변수, Scope 3가 두 번째. [MSCI, "Understanding the Drivers of Transition-Risk Climate VaR" | https://www.msci.com/research-and-insights/blog-post/understanding-the-drivers-of-transition-risk-climate-var]
- **경쟁·보완 상품: WTW Climate Transition VaR.** WTW(옛 Willis Towers Watson)도 7,000개 이상 기업 대상 전환리스크 데이터와 포트폴리오 전환리스크 평가 상품을 제공 — MSCI와 유사한 계보의 상업화 버전. [WTW, "Climate Transition Value-at-Risk" | https://www.wtwco.com/en-us/solutions/products/climate-transition-value-at-risk]
- **바젤 규제로의 확장 시도.** Climate VaR 부가치(add-on)를 개별 종목의 지역·업종·재무제표 정보만으로 계산할 수 있어, 규제당국이 바젤 III 기준의 표준화된 VaR add-on으로 정의할 수 있다는 제안이 학계에서 나오고 있음(계량 은행자본규제 연구). [MDPI, "Macroeconomic Modelling of Climate Value-at-Risk and Capital Adequacy" (2025) | https://www.mdpi.com/2225-1154/13/12/245]

**TCaR이 이 계보에 앉는 자리**: Dietz(2016)→MSCI/WTW로 이어지는 계보는 전부 "포트폴리오 전체 가치의 기대손실 백분율"을 산출하는 하향식(top-down) 지표다. 이들은 개별 기업의 전환비용을 분포로 재구성하지 않고, 시나리오별 point estimate(또는 그 가중평균)를 현금흐름 할인에 곧바로 반영한다. TCaR은 이 계보와 같은 문제의식(전환리스크의 VaR화)을 공유하지만, 기업 단위에서 원단위(θ) 불확실성을 명시적 분포로 다룬다는 점에서 MSCI/WTW의 "단일 시나리오 현금흐름 할인"과 다르다 — 이 차이가 우리 논문이 이 계보에 기여하는 지점이다(TCaR research_v2 기록 참조: 철강 TCaR 원단위 격리 실행 +14~30%, 원 연구 경계 미도출은 별도 확인 필요 항목).

---

## 전환채·SLB 가격

- **SLB의 "그리니엄(greenium)" 존재 증거.** Kölbel & Lambillon (2022)은 매칭된 채권쌍(102쌍) 비교를 통해 SLB가 동일 발행사의 일반채권보다 발행 시점에 평균 29.2bp 낮은 금리로 발행됨을 발견 — 즉 지속가능성 연계 목표를 건 채권에 투자자가 프리미엄(낮은 수익률 수용)을 지불. 페널티(쿠폰 스텝업)가 이 프리미엄보다 작으면 발행사는 목표를 달성하지 못해도 SLB 발행만으로 자본비용을 낮출 수 있다는 구조적 허점도 지적. [Kölbel & Lambillon (2022/2024), "Who Pays for Sustainability? An Analysis of Sustainability-Linked Bonds" / 게재본 "The pricing of sustainability-linked bonds on the primary and secondary bond markets", Journal of Asset Management | https://link.springer.com/article/10.1057/s41260-024-00390-z ; SSRN https://dx.doi.org/10.2139/ssrn.4007629]
- **그리니엄 소멸 논쟁 (그린본드 전반).** 그린본드 프리미엄은 2015년경 약 6bp에서 2020년 통계적으로 무의미한 수준으로 축소, 2023년 더 축소되다 2024년에는 사실상 소멸했다는 것이 최근 문헌의 대체적 진단. 국채 시장에서도 그리니엄은 선진국 약 2bp, 신흥국 10bp 남짓으로 작고 불안정(regime-dependent)하다는 평가. 수요초과가 초기 프리미엄을 만들었으나 공급 확대로 소멸했다는 해석이 다수. [IEEFA, "Green bonds: Issues, incentives, and the green premium debate" | https://ieefa.org/resources/green-bonds-issues-incentives-and-green-premium-debate ; Nordic ESG Lab (CBS), "No More Greenium" | https://nordicesglab.cbs.dk/no-more-greenium-what-the-vanishing-green-bond-premium-means-for-sustainable-finance/]

**투자자가 전환목표 위험을 가격에 반영하는 방식**: SLB 문헌이 시사하는 바는, 투자자가 "전환실패 리스크"를 직접 채권가격에 할인하기보다 쿠폰 스텝업(페널티 조항)이라는 명시적 파생 구조로 분리해서 받는다는 것이다 — 이는 CAP의 "정부/투자자가 분포의 다른 층을 진다"는 blended finance 언어와 유사하지만, SLB에서는 그 층 구분이 목표 달성 여부라는 이산적(discrete) 트리거로 이루어지지, 연속적 분포의 상방 꼬리로 이루어지지 않는다 — 이 점이 TCaR(연속분포)과 SLB(이산 트리거) 구조의 핵심 차이.

---

## 한·일 케이스

- **한국: 790조원 기후금융 로드맵과 K-Taxonomy 전환금융.** 금융위원회는 2026~2035년 10년간 790조원 규모 기후금융 공급 계획을 발표했고, 철강·화학·시멘트 등 고탄소 업종의 설비효율화·연료전환 투자를 지원하는 "한국형 전환금융"을 도입 중이다. 금융감독원과 함께 전환금융 TF를 운영하며 EU·일본 체계를 전략적으로 융합한 가이드라인을 마련 중이고, 자금사용자에게 K-Taxonomy 기준 충족 서약서·확인서·전환전략 실행계획 제출을 요구하며 이 서류들이 금융계약상 법적 구속력을 가질 수 있다는 점이 확인된다. [비즈니스포스트, "EU·일본 모델 섞은 한국형 전환금융, 금융위 790조 기후금융 시대 연다" | https://www.businesspost.co.kr/BP?command=article_view&num=439795 ; ESG타임즈, "금융위, '2035년까지 790조 기후금융' 발표" | https://www.esgn.co.kr/news/articleView.html?idxno=8577]
- **일본: GX 이행국채(GX Economy Transition Bonds), 20조엔.** 일본 정부는 2024년 2월부터 세계 최초의 국가 발행 전환국채(sovereign transition bond)를 발행 시작, 향후 10년간 20조엔 규모로 GX(그린전환) 지원을 목표로 한다. 2024년 한 해에만 5회 입찰로 2.65조엔(약 170억 달러) 발행. 목적은 향후 10년간 150조엔 이상의 민관 GX 투자를 유도하는 마중물(pump-priming) 성격. [Japan Gov (METI), "Climate Transition Bonds Show Japan's Commitment to Carbon Neutrality" | https://www.japan.go.jp/kizuna/2024/09/climate_transition_bonds.html ; LSEG, "Japan's $1trn bet on the climate transition" | https://www.lseg.com/en/insights/ftse-russell/japans-1trn-dollar-bet-on-the-climate-transition]
- **POSCO — 공개된 조달 구조.** 포스코홀딩스는 지속가능금융 관리체계(Sustainable Financing Framework, 2024년 3월 정립)를 기반으로 그린본드를 발행(공개된 사례: 7억 달러 규모 글로벌 그린본드, 에너지소재 사업에 사용). 수소환원제철(HyREX) 기술 자체는 국책 R&D·자체 투자로 진행 중이며, 이 기술 개발에 특정된 프로젝트파이낸스(오프테이크·DSCR 구조를 갖춘 논-리코스 대출) 사례는 이번 검색에서 확인되지 않음 — 확인된 것은 그린본드(리코스, 기업 신용 기반) 조달까지다. [POSCO Newsroom, "포스코홀딩스, 7억달러 규모 글로벌 그린본드 발행" | https://newsroom.posco.com/kr/%ED%8F%AC%EC%8A%A4%EC%BD%94%ED%99%80%EB%94%A9%EC%8A%A4-7%EC%96%B5%EB%8B%AC%EB%9F%AC-%EA%B7%9C%EB%AA%A8-%EA%B8%80%EB%A1%9C%EB%B2%8C-%EA%B7%B8%EB%A6%B0%EB%B3%B8%EB%93%9C-%EB%B0%9C%ED%96%89/]
- **일본제철(Nippon Steel) — 공개된 조달 구조.** ICMA Green Bond Principles와 일본 Green Bond Guidelines(2022)에 따라 그린본드 프레임워크를 수립, 전기차 모터용 무방향성 전자강판 생산설비·연구에 자금 사용. 전로(BF)→전기로(EAF) 전환에 2029년까지 약 8,667억엔(약 60억 달러) 투자 계획, 이 중 최대 2,514억엔(약 17억 달러)을 정부 보조금으로 지원받는 구조 — 즉 자체 투자+정부 보조금 혼합이며, 은행 신디케이트의 논-리코스 프로젝트파이낸스 구조는 확인되지 않음. 참고로 시민사회 분석(Anthropocene Fixed Income Institute)은 일본제철 그린본드를 "bare minimum strategy"로 비판. [Nippon Steel, "Green Transformation (GX) Initiatives" IR 자료 | https://www.nipponsteel.com/en/ir/library/pdf/20250313_100.pdf ; AFII, "Nippon Steel green bonds: A bare minimum strategy" | https://anthropocenefii.org/downloads/AFII_NipponGreenBond.pdf]
- **한·일 은행의 전환 프로젝트 인수 실태.** KDB(산업은행)가 일반적 프로젝트파이낸스(미래현금흐름 담보) 상품을 운용한다는 것은 확인했으나, 철강·수소 전환 프로젝트에 특정된 인수 사례·조건(DSCR, 오프테이크 요구 등)은 이번 검색으로 확인하지 못함 — 미확인 항목으로 이월.

**시사점**: 한·일 모두 국가 단위 전환금융은 "국채/공적자금이 대규모 지원 프레임을 깔고, 개별 기업은 그 위에서 그린본드(무담보 회사채, 기업 신용 의존)로 조달"하는 2단 구조로 보인다. RMI가 서구 그린스틸(H2 Green Steel)에서 본 "오프테이크+비의결권 지분+ECA 신용이전"의 논-리코스 프로젝트파이낸스 구조가 한·일 대형 철강사(POSCO, Nippon Steel)의 공개 조달에서는 확인되지 않는다 — 이들은 프로젝트 단위가 아니라 기업(코퍼레이트) 단위로 그린본드를 발행하며, 상방 꼬리는 기업의 대차대조표 전체가 흡수하는 구조로 보인다. 이는 L1~L3의 "세 층(기업/투자자/정부)" 분리가 한·일 대형 철강사 사례에서는 project-level이 아니라 corporate-level로 뭉쳐 있다는 뜻일 수 있다 — 다만 이는 이번 검색 범위 내 확인된 공개 정보의 해석이며, 비공개 대출계약 조건까지 확인한 것은 아니다.

---

## 투자자가 분포의 어느 층을 지나

L1~L3에서 확립한 3층 구조(기업 first-loss / 투자자 mezzanine / 정부 catastrophe) 위에, 이번 조사로 확인된 문헌들을 층별로 배치하면 다음과 같다.

| 층 | 인수 주체 | 가격화 메커니즘 (확인된 문헌) | 다루는 구간 |
|---|---|---|---|
| First-loss (하방~중심) | 발행기업 | 그린본드/전환국채의 코퍼레이트 신용스프레드(POSCO·Nippon Steel 사례) | 예상 전환비용 중심값 근방 |
| Mezzanine (중심~상방 일부) | 회사채·CDS 투자자, SLB 투자자 | 탄소프리미엄(Bolton-Kacperczyk), CDS 전환리스크 프라이싱(Kölbel et al.), SLB greenium(Kölbel-Lambillon)의 쿠폰 스텝업 조항 | 공시된/예견된 리스크의 점추정 반영, 이산적 트리거(SLB) |
| Mezzanine (프로젝트 단위) | 프로젝트파이낸스 대출자 | DSCR 1.2~1.35x 문턱 + 오프테이크 계약으로 좁힌 현금흐름 구간만 인수 (RMI/H2 Green Steel) | 좁은 하방 구간, 상방·하방 꼬리 모두 전가 |
| Catastrophe (상방 꼬리) | 오프테이커 지분참여자, ECA, 정부(GX국채·K-Taxonomy 재정지원) | 비의결권 지분, 수출신용 국가이전, 국채 마중물 재정(RMI, METI GX) | 비용초과·FOAK 실패 시나리오 |

기존 문헌이 공통으로 보여주는 것은, 투자자·대출자는 전환비용 분포의 상방 꼬리를 "가격에 반영"하기보다 "계약구조로 좁히거나 떠넘긴다"는 점이다 — CDS·회사채 투자자는 사후적으로 공시된 리스크만 스프레드에 반영하고(사전 분포 자체를 가격 매기지 않음), 프로젝트 대출자는 오프테이크·DSCR로 인수 대상 자체를 좁은 시나리오로 한정하며, SLB 투자자는 연속분포가 아니라 이산 트리거(목표 달성/실패)로만 가격을 분리한다. 이 "연속분포 vs 이산·좁힌 구간"의 간극이 CAP TCaR이 기존 가격화 실무에 기여할 수 있는 지점이다 — 다만 이는 방법론적 관찰이며 이번 L4의 임무(문헌 확인)를 넘는 해석이므로, 후속 L5에서 별도로 검증 필요.

---

## 미확인

아래는 이번 조사에서 확인하지 못했거나 불완전하게만 확인된 항목이다. 추측 서지로 채우지 않고 그대로 남긴다.

1. **Seltzer, Starks & Zhu 논문의 최종 게재 저널** — NBER Working Paper (No. 29994, 2022) / FRB New York Staff Report (No. 1014, 2025년 3월 개정)로만 확인. 동료심사 저널(예: Review of Financial Studies, Journal of Finance 등) 게재 여부·게재 시 권/호는 미확인.
2. **POSCO·Nippon Steel의 프로젝트 단위(논-리코스) 전환 프로젝트파이낸스 구조** — 두 회사 모두 코퍼레이트 그린본드 발행은 확인되나, 그린스틸/수소환원제철 설비에 대한 오프테이크·DSCR을 갖춘 프로젝트파이낸스 계약 세부조건은 검색으로 확인되지 않음. 비공개 계약일 가능성.
3. **한·일 은행(KDB, 신한·하나·미즈호·MUFG 등)의 전환 프로젝트 대출 특정 조건(DSCR, 오프테이크 요구, 신디케이션 구조)** — 일반적 프로젝트파이낸스 상품 소개 수준만 확인, 철강·수소 전환에 특정된 조건은 미확인.
4. **한국 K-Taxonomy 전환금융 가이드라인의 확정 텍스트(최종본) 및 시행일** — 로드맵·TF 운영 사실은 확인되나, 가이드라인 최종 확정본 발간 여부·구체 조항은 미확인(2026-09-13 기준 진행 중인 것으로 보임).
5. **Aswani et al.의 탄소프리미엄 반론 논문의 정확한 서지(연도·저널)** — 검색 결과에 "Aswani et al. (2024a)"로만 언급, 정식 서지 미확인.
6. **MSCI Climate VaR·WTW Climate Transition VaR과 TCaR의 정량적 비교(동일 기업·동일 시나리오 산출값 비교)** — 방법론 개요 수준만 확인, 실제 수치 비교는 이번 조사 범위 밖.

---

*작성: CAP 8루프 L4. 다음 단계는 이 문헌 지도를 바탕으로 "TCaR 상방 꼬리 → 어떤 가격화 실무(신용스프레드/DSCR/SLB 스텝업/재정 마중물) 중 어디에 얹을 것인가"를 결정하는 L5.*

---

# SYNTHESIS L4 (투자자·대출자 헤지) — 2026-09-13

## layering이 실무 표준과 정확히 대응 (얹혀가기 확정)
OECD/Convergence 블렌디드 파이낸스 3계층(junior/first-loss·mezzanine·senior)이 L3의 "기업 first-loss·
투자자 mezzanine·정부 catastrophe"와 정확히 대응. CAP은 이 언어를 전환비용 분포에 매핑할 뿐 — 발명
아님. Convergence 8,500+ 딜 집계가 실무 두께.

## 채권은 몸통, 꼬리는 별도 (수단이 분포의 어디를 커버하나)
그린본드/전환본드(ICMA CTBG 2025, 다섯 번째 라벨)는 분포 **중앙값(정상 전환 capex)**만 커버. 채권
투자자는 **발행자 신용 위험**을 지지 프로젝트별 초과비용·좌초를 지는 게 아니다(use-of-proceeds는
recourse, SLB는 이표 유인만). → 꼬리는 별도 보증·후순위 필요. 이게 "채권만으론 mezzanine/catastrophe
못 채운다"의 확인.

## 두 긴장 (L5로 넘김)
1. **정부가 이미 mezzanine까지 흡수** — H2 Green Steel 실물: Riksgälden 그린보증·Euler Hermes ECA가
   원금 80~95% 커버. 이상형("정부는 catastrophe만")과 현실이 다르다. 정부 층이 생각보다 두껍다.
2. **정부가 자기 위험을 자기 재보험** — catastrophe 층(탄소가 좌초)은 정부가 만든 위험이라 Arrow-Lind
   안 걸림(수익이 총소비와 독립이어야 하는데 정책은 내생). 도덕적 해이·시간불일치. 시장은 이미
   "정부가 결국 보상"을 가격에 반영(정책전환위험 실증).

## 한·일 케이스 (무게중심)
- **일본**: GX-ETS 연계 **국채형 전환본드**(2024.2~, 20조엔, 민관 150조엔 유도). 정부가 발행자가 되어
  탄소 붕괴 위험을 **자기 부채 상환 리스크로 내재화** — 특수하고 강한 사례.
- **한국**: 제도(790조 가이드라인, K-Taxonomy + 업종 로드맵 두 갈래) 있으나 **계층화 실무 선례 미축적**.
- **POSCO·NSC**: corporate-level 그린본드(POSCO 7억 달러, NSC 8,667억엔 중 2,514억엔 정부보조).
  서구 그린스틸(오프테이크+지분+ECA project finance)과 달리 **위험을 기업 신용에 통째로 진다**.
  → Wolf 2025 유럽과 다른 우리 케이스의 값. (단 비공개 PF는 미확인.)

## TCaR 기여 지점 재확인 (L4 근거)
기존 실무는 전환리스크를 **top-down 점추정**(MSCI Climate VaR)·**이산 트리거**(SLB 목표 달성/실패)로만
가격 매긴다. TCaR는 기업 단위 원단위 불확실성을 **명시적 연속 분포**로 — Climate VaR 계보에 앉으면서
그 계보가 안 하는 것(연속·bottom-up). 딱 그만큼의 기여, 거창하지 않음.

## 직전(L1~L3) 비판적 재검토
L3의 "투자자=mezzanine" 예감이 실무(3계층)로 확인. 그러나 L4가 이상형을 흔든다 — 현실에선 정부(ECA)가
mezzanine까지 내려와 흡수하고, 채권 투자자는 꼬리가 아니라 신용을 진다. 즉 "누가 어느 층"의 경계가
제도·시장 성숙도에 따라 움직인다(유럽 ECA 두껍고, 한국 미축적). L6(상호작용)에서 이 경계를 케이스로
정식화. layering은 이상형이 아니라 제도 의존적 분업이다.
