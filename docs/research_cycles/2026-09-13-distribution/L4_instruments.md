# L4 — 전환금융 수단·위험이전 (2026-09-13)

목적: L3에서 얻은 blended finance layering(기업 first-loss·투자자 mezzanine·정부 catastrophe)이 실제 전환금융 실무 문헌·시장에서 어떻게 쓰이는지 확인하고, CAP 8루프의 "전환비용 분포" 중 어느 부분을 어느 수단이 커버하는지 매핑한다. 새 이론 없음 — 기존 문헌/실무에 얹혀감. 무게중심은 한·일 케이스.

---

## Blended finance 계층화 실무

- 구조화 블렌디드 펀드의 표준 3계층: **junior/first-loss**(공여자·양허성 자본, 초기 손실 흡수) → **mezzanine**(DFI·미션 투자자, 하위층 보호 아래서 일부 위험 인수) → **senior**(연기금·보험사 등 기관투자자, 가장 안정적 부분, 낮은 위험·낮은 수익). [OECD, "Making blended finance work: Why fund structure is the real driver of mobilisation" (2026) | https://www.oecd.org/en/blogs/2026/02/making-blended-finance-work-why-fund-structure-is-the-real-driver-of-mobilisation.html]
- OECD DAC 공식 가이던스도 동일 구조를 "junior/mezzanine/senior tranche가 위험·수익 선호를 균형 잡는 계층화된 위험완화 메커니즘"으로 규정. [OECD, "OECD DAC Blended Finance Guidance 2025 — Principle 2" | https://www.oecd.org/en/publications/oecd-dac-blended-finance-guidance-2025_e4a13d2c-en/full-report/principle-2-design-blended-finance-to-increase-the-mobilisation-of-commercial-finance_996e5e2d.html]
- 보증(guarantee)은 신디케이트 대출에 이어 민간자본 동원 2위 메커니즘: 2023년 동원된 민간자금 700억 달러 중 170억 달러가 보증을 통해 동원됨. [OECD DAC 관련 통계, "DAC Working Party on Development Finance Statistics" (2026) | https://one.oecd.org/document/DCD/DAC/STAT(2026)8/en/pdf]
- 남아공 사례: 중소기업 에너지효율 프로그램에 first-loss guarantee 1,600만 달러를 투입해 레버리지 1:16, 총 2억 6,100만 달러 동원. [MDB Reform Accelerator, "Blended Finance Best Practice: Case Studies and Lessons Learned" | https://mdbreformaccelerator.cgdev.org/blended-finance-best-practice-case-studies-and-lessons-learned/index.html]
- Convergence는 2008년 이후 8,500건 이상의 블렌디드 파이낸스 딜을 집계·추적하는 최초의 글로벌 플랫폼. [Convergence 관련 서술, OECD 자료 인용 (위 OECD 블로그 내) | https://www.oecd.org/en/blogs/2026/02/making-blended-finance-work-why-fund-structure-is-the-real-driver-of-mobilisation.html]
- **전환 프로젝트 적용 사례**: 검색 범위 내에서 "전환(transition) 프로젝트"에 명시적으로 이 3계층 구조를 적용한 개별 딜 사례(예: 철강·시멘트 등)는 확인하지 못함 — 재생에너지·중소기업 대출 사례가 대부분. 아래 "보증" 절의 H2 Green Steel은 블렌디드 파이낸스가 아니라 ECA 보증부 상업대출 구조라는 점에서 구분됨 (미확인 항목 참조).

**CAP 매핑**: 이 계층화는 L3에서 이미 도출한 "기업 first-loss·투자자 mezzanine·정부 catastrophe" 구조와 정확히 대응한다. 즉 CAP 분포의 하단(중앙값 근접, 발생확률 높음)은 기업이, 중간(꼬리 진입부)은 투자자가, 최상단 꼬리는 정부가 진다는 매핑이 실무 표준과 일치.

---

## 그린본드·전환본드 위험 이전

- ICMA는 2025년 11월 **Climate Transition Bond Guidelines(CTBG)**를 발표. 그린·소셜·지속가능·SLB에 이어 다섯 번째 라벨로 "전환본드(Climate Transition Bond)"를 신설. [ICMA, "Climate Transition Bond Guidelines (CTBG)" (Nov 2025) | https://www.icmagroup.org/assets/documents/Sustainable-finance/2025-updates/Climate-Transition-Bond-Guidelines-CTBG-November-2025.pdf]
- CTBG는 **use-of-proceeds 방식**(조달자금을 특정 전환 프로젝트에 배정)과 **SLB 방식**(발행자 차원의 기후 목표 달성에 재무 조건을 연동) 양쪽에 모두 적용 가능하도록 설계됨 — 즉 전환 라벨은 특정 구조가 아니라 두 기존 구조 위에 얹히는 신뢰성 기준(발행자 차원 전환전략, 저탄소 대안의 상업적 미성숙 근거, 인정된 택소노미·1.5도 경로 부합 증빙)이다. [ICMA CTBG (2025); PwC Luxembourg, "Climate Transition Bond Guidelines (CTBG): A new era for sustainable finance" | https://www.pwc.lu/en/press/press-articles-2025/climate-transition-bond-guidelines.html]
- **위험 이전의 성격**: use-of-proceeds형 채권(그린본드·전환본드)에서 신용위험은 발행자의 일반 신용(recourse)에 남고, 투자자는 그 신용위험을 통상적인 채권 가격결정(스프레드)으로 인수한다 — 즉 채권 구조 자체가 프로젝트의 성패 위험을 투자자에게 이전하는 것이 아니라, 발행자 전체의 상환능력에 베팅하는 구조. SLB는 여기에 이표(coupon) 조정이라는 발행자 유인장치를 얹을 뿐, 신용위험의 이전 방식은 동일. (일반 채권시장의 확립된 원리이며 위 ICMA 문서들이 이 구조를 전제로 라벨을 설계함.) [ICMA CTBG (2025) | 위 링크]
- CTB는 그린·SLB만으로는 다루기 어려웠던 고배출 산업(철강·시멘트·항공 등)의 프로젝트 단위 탈탄소화 자금조달을 메우기 위해 설계됨. [Energy Digital, "Explained: The ICMA's Climate Transition Bond Guidelines" | https://energydigital.com/news/explained-the-icmas-climate-transition-bond-guidelines]

**CAP 매핑**: 그린본드/전환본드는 CAP 분포의 **중앙값 근처(정상적 전환 capex)**를 커버하는 조달 수단이지, 꼬리 위험을 이전하는 수단이 아니다. 채권 투자자가 지는 것은 "발행자 신용 위험"이지 "프로젝트별 초과비용·좌초 위험"이 아니라는 점이 L4의 핵심 확인 사항 — 즉 채권만으로는 L3의 mezzanine/catastrophe 계층을 채울 수 없고, 별도의 보증·후순위 구조가 필요하다.

---

## 보증·개런티·보험

- **H2 Green Steel(스웨덴, Stegra) 사례** — 세계 최초 대형 그린스틸 플랜트, 총 부채조달 약 42억~65억 유로 규모. 핵심 구조: 스웨덴 국가채무청(Riksgälden)의 그린 신용보증과 독일 Euler Hermes의 수출신용보증이 각각 12억 유로씩, 대출원금의 80%·95%를 커버. EIB가 3.14억 유로(이 중 2억 유로는 InvestEU 보증부), NIB가 5,700만 유로를 참여. [Impact Investor, "EIB and NIB commit €371m to H2 Green Steel with EU backing" | https://impact-investor.com/eib-and-nib-commit-e371m-to-h2-green-steel-with-eu-backing/; PRNewswire/Stegra, "H2 Green Steel raises more than €4 billion in debt financing..." | https://www.h2greensteel.com/latestnews/h2-green-steel-raises-more-than-4-billion-in-debt-financing-for-the-worlds-first-large-scale-green-steel-plant; RMI, "Five Lessons for Industrial Project Finance from H2 Green Steel" | https://rmi.org/five-lessons-for-industrial-project-finance-from-h2-green-steel/]
- 이 구조는 "보증 기관이 대출 원금의 특정 %를 커버"하는 방식으로, 상업은행(선순위 대출 실행자)이 지는 신용위험을 국가수출신용기관(ECA)·다자개발은행이 부분적으로 인수 — 즉 **꼬리 위험(채무불이행 시 손실) 중 상당 부분을 공적기관이 재보증**하는 구조. [RMI, 위 링크]
- MIGA(세계은행그룹 다자간투자보증기구)는 정치위험보험(수용, 송금제한, 전쟁·테러, 계약파기, 정부의 금융의무 불이행 등)을 제공하여 투자자·대출자를 정부발(政府發) 위험으로부터 보호. [MIGA, "Political Risk Insurance" | https://www.miga.org/political-risk-insurance; Wikipedia, "Multilateral Investment Guarantee Agency" | https://en.wikipedia.org/wiki/Multilateral_Investment_Guarantee_Agency]
- ECA·정치위험보험자는 통상 "자국 투자자·대출자가 개발도상국으로 나가는" 거래를 지원하는 구조이며, 신용/관할위험으로 상업대출이 불가능한 거래를 신용보증을 통해 가능하게 만드는 역할. [Mayer Brown, "Export Credit Agencies and Political Risk Insurers in International Project Financing" (2019) | https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2019/05/export-credit-agencies-and-political-risk-insurers-in-internatinal-project-financing_v5.pdf]

**CAP 매핑**: 보증·정치위험보험은 CAP 분포에서 **투자자가 질 수 있는 상한선을 정하는 수단** — 즉 mezzanine 계층의 "위쪽 경계"를 공적기관 보증으로 깎아내는 역할. H2 Green Steel처럼 보증 커버리지가 80~95%에 달하면, 사실상 상업대출자는 이미 얇은 잔여 위험만 지고 나머지는 국가(ECA)로 이전된 것 — 이는 L3의 "정부는 catastrophe layer만"이라는 이상형과 달리, **현실의 그린스틸 project finance에서는 정부(ECA)가 이미 mezzanine 상당 부분까지 흡수하고 있다는 시사점**이며 L5에서 다뤄야 할 긴장.

---

## 정부 층으로 넘어가는 위험

- **왜 정부만 지는가 (Arrow-Lind)**: Arrow-Lind 정리는 공공투자의 위험이 공적으로(널리) 부담될 때, 인구가 커질수록 위험부담의 사회적 비용이 0에 수렴 — 정부는 위험을 "풀링"해서가 아니라 조세·차입 능력을 통해 대규모 인구에 위험을 분산시킬 수 있기 때문에 불확실성을 무시하고 기대순편익만으로 평가해도 무방하다는 결론. [Arrow-Lind principle, Wikipedia 요약 및 원 정리 | https://en.wikipedia.org/wiki/Arrow%E2%80%93Lind_principle; Roy Gardner, "The Arrow-Lind Theorem in a Continuum Economy," American Economic Review 69(3), 1979 | https://ideas.repec.org/a/aea/aecrev/v69y1979i3p420-22.html]
- 단, 이 정리의 전제(수익이 총소비와 통계적으로 독립적)가 깨지면 성립하지 않음 — 국가 재난위험처럼 반대로 "국가 위험회피"가 정당화되는 경우도 문헌에 존재. [Research on Sovereign disaster risk, "Revisiting Arrow-Lind: Managing Sovereign Disaster Risk" | https://www.researchgate.net/publication/259785886_Revisiting_Arrow-Lind_Managing_Sovereign_Disaster_Risk]
- **정책 붕괴·좌초자산 위험은 정부가 만든 위험이라 정부만 진다는 논리**: 좌초자산 문헌에서 시장위험의 대부분(특히 상류 화석연료 부문)은 이미 민간 투자자, 그중에서도 OECD 소재 투자자(연기금 등)에게 전가되어 있다는 실증 — 즉 "정부가 만든 정책위험"이 실제로는 민간에 전가된 현실이 확인됨. [Semieniuk, Holden, Mercure et al., "Stranded fossil-fuel assets translate to major losses for investors in advanced economies," Nature Climate Change (2022) | https://www.nature.com/articles/s41558-022-01356-y]
- 탄소가격·정책위험은 "전통적 의미로는 헤지 불가능"하지만, 구조적·전략적 설계 선택을 통해 부분적으로 축소 가능하다는 것이 보험·금융공학 문헌의 절충적 입장. [arXiv, "Carbon-Sensitive Fund Construction and Hedging for Green Unit-Linked Life Insurance" (2025) | https://arxiv.org/pdf/2509.05676]
- 투자자들은 "좌초 석탄발전이 보상받을 것"이라 기대하는 경향이 있다는 관찰 — 이는 로비력 때문일 수 있다고 지적되며, 이는 사실상 민간이 감당 못하는 정책 붕괴 위험을 정부가 사후에 흡수해줄 것이라는 시장의 암묵적 기대를 보여줌. [ScienceDirect, "Policy transition risk, carbon premiums, and asset prices" (2025) | https://www.sciencedirect.com/science/article/pii/S0304393225000510] — **저자명·정확한 인용정보는 페이월로 미확인, 초록 수준만 확인.**
- **정부가 최후의 보험자(insurer of last resort)가 되는 이유**: 민간보험자가 감당 못하는(비보험 가능) 위험 영역에서 역사적으로 정부가 최후 보험자 역할을 맡아온 사례(재난보험 잔여시장 프로그램 등)가 일반적 패턴으로 확인됨. [WEF, "Climate finance is stuck. How can insurance unblock it?" (2025) | https://www.weforum.org/stories/2025/12/climate-finance-can-insurance-help-unblock-it/]
- 위험 계층화의 표준 원칙: 고빈도·저심도 위험은 준비금 등 위험보유(retention) 수단으로, 저빈도·고심도(catastrophe) 위험은 보험·캣본드 같은 위험이전 수단으로 다룬다는 것이 재해리스크금융 문헌의 표준 틀. [Adaptation Community / World Bank 계열 자료, "Climate and Disaster Risk Finance and Insurance" | https://www.adaptationcommunity.net/climate-disaster-risk-finance-insurance/]

**CAP 매핑**: L5로 넘어갈 핵심 논지 — (1) Arrow-Lind는 "정부가 지는 것이 효율적"이라는 정상적 근거이지만, (2) 정책 붕괴·탄소가격 좌초 같은 catastrophe layer는 애초에 "정부가 만든" 위험이라는 점에서 통상적 공공투자 위험과 질적으로 다르다 — 정부가 스스로 만든 위험을 스스로 재보험하는 구조이므로 도덕적 해이·시간불일치 문제가 별도로 발생. (3) 그럼에도 시장은 이미 "정부가 결국 보상할 것"이라는 기대를 가격에 반영하고 있다는 실증(투자자의 좌초석탄 보상 기대)이 확인됨.

---

## 한·일 전환금융 수단

### 일본
- **GX 경제이행채(GX Economy Transition Bond)**: 2024년 2월 세계 최초로 1.6조 엔 규모 발행, 향후 10년간 총 20조 엔 발행 계획. 민관 합동으로 10년간 150조 엔 규모 투자를 유도하는 것이 목표. [KIEP, "일본의 'GX 경제 이행채' 추진 현황 및 시사점" | https://www.kiep.go.kr/galleryDownload.es?bid=0004&list_no=11240&seq=1; EIEC(KDI), 동 제목 | https://eiec.kdi.re.kr/policy/domesticView.do?ac=0000183206]
- **GX-ETS 연계**: 상환재원은 GX-ETS(배출권거래), 전력부문 배출권 유상할당(경매), 화석연료 부과 GX 부담금(surcharge)으로 구성된 탄소가격 수입. GX-ETS는 2023~2025 자발적 시행 3년을 거쳐 2026년 4월부터 의무 2단계(2026~2032, 7년)에 진입. [KOTRA, "GX채 발행으로 알아보는 日정부의 탈탄소 정책 방향" | https://dream.kotra.or.kr/kotranews/cms/news/actionKotraBoardDetail.do?SITE_NO=3&MENU_ID=80&CONTENTS_NO=2&bbsGbn=242&bbsSn=242&pNttSn=212550; ICAP, "Japan transitions its GX-ETS to the mandatory phase" | https://icapcarbonaction.com/en/news/japan-transitions-its-gx-ets-mandatory-phase]
- **METI 전환금융(Transition Finance) 프레임워크**: 정부가 산업별 전환로드맵 기반 전환금융을 공식 지원. [METI, "Transition Finance" | https://www.meti.go.jp/english/policy/energy_environment/transition_finance/index.html]
- **JBIC의 역할**: JBIC은 저탄소 원료(가공철광석 등) 조달 대출(2024년 3월, Vale 대상 4.8억 달러)을 통해 철강 탈탄소를 간접 지원하며, 구리 등 GX 핵심광물의 안정공급을 위한 금융지원도 수행. 다만 검색 범위 내에서 JBIC이 국내(일본) 그린스틸 프로젝트에 직접 보증/후순위 형태로 참여한 구체 사례는 확인하지 못함 — Nippon Steel 대상 대출(2025)은 US Steel 인수 관련 거래로 전환금융 성격이 아님. [JBIC, "Financing for greener steelmaking realized under new arrangement" (2025) | https://www.jbic.go.jp/en/information/today/today_2025sp/jtd_202502_sp7.html; JBIC, "Loan to Nippon Steel Corporation..." | https://www.jbic.go.jp/en/information/press/press-2025/press_00188.html]

### 한국
- **전환금융 가이드라인(2025년 제정)**: 금융위원회·금융감독원이 기후에너지환경부·산업통상부와 공동으로 마련. 두 갈래 체계 — ① EU 개념체계를 벤치마킹한 **K-Taxonomy 기반** 전환금융, ② 일본 방식과 유사한 **업종별 탄소감축 이행 로드맵 기반** 전환금융. [KDI(EIEC), "전환금융 제도화의 전환점: 2025년 가이드라인 제정과 금융사" | https://eiec.kdi.re.kr/policy/domesticView.do?ac=0000200777]
- **정책금융기관**: 기후금융 공급의 5대 축은 산업은행(KDB)·기업은행·수출입은행(KEXIM)·신용보증기금·기술보증기금이며, 다배출업종 저탄소 전환 지원을 새 축으로 추가하는 방향. [위 KDI 자료 동일 출처]
- **KDB 그린본드 프레임워크**: KDB는 자체 "한국형 녹색채권 관리체계"를 운용 중(2022년, 2023년 개정판 확인). 이는 그린본드 프레임워크이며, 검색 범위 내에서 KDB의 "전환본드(transition bond)" 전용 프레임워크 발행은 확인하지 못함. [KDB, "한국형 녹색채권 관리체계" (2023.6) | https://www.kdb.co.kr/wcmscontents/pdf/01_KDB_K_Green_Bond_Framework.pdf]
- **금융위 녹색·전환금융 공급 로드맵**: 금융위원회가 녹색·전환금융에 총 790조 원 공급을 목표로 하는 로드맵을 발표. [Lexology, "금융위, 녹색·전환금융 790조원 공급 로드맵 발표" | https://www.lexology.com/library/detail.aspx?g=71c9b19a-039a-48a7-baca-c4f1a57d1400]
- 산업은행·정책금융공사·수출입은행이 개별 한국 철강/화학 전환 프로젝트에 blended finance 계층(예: 후순위 대출, 보증)으로 참여한 구체적 딜 사례는 검색 범위 내에서 확인하지 못함 (미확인 항목 참조).

**CAP 매핑**: 일본은 GX-ETS라는 명시적 탄소가격 연계 상환재원을 가진 국채형 전환본드를 이미 실행 중 — 이는 정부 자신이 발행자가 되어 "탄소가격 붕괴 위험"을 스스로 국채 상환 리스크로 흡수하는 특수 사례(사실상 Arrow-Lind형 위험분산 + 정책신뢰 리스크를 정부가 자기 부채로 내재화). 한국은 아직 가이드라인 단계이며 개별 프로젝트의 계층 구조(누가 first-loss/mezzanine/catastrophe를 지는지)를 특정할 만한 공개 사례가 부족 — 이는 한국 케이스가 "제도는 있으나 계층화 실무 선례가 아직 축적되지 않은 단계"라는 관찰로 정리 가능.

---

## 미확인

- Convergence 플랫폼 자체 문헌에서 "전환(transition) 프로젝트"에 특정해 first-loss/mezzanine/senior 비율을 제시한 표준이나 벤치마크 수치는 확인하지 못함 (일반 개발금융 사례가 대부분).
- H2 Green Steel 구조는 학계에서 "blended finance"로 분류되는 자료를 직접 확인하지 못함 — ECA 보증부 상업대출(export credit-backed senior debt) 구조이며, 공여자 first-loss 자본이 명시적으로 존재하는지는 확인 안 됨. L4 본문에서는 "보증을 통한 위험이전" 사례로만 인용.
- "Policy transition risk, carbon premiums, and asset prices" (ScienceDirect, 2025)의 저자명·정확한 저널·권호는 페이월로 확인하지 못함 — URL과 제목만 확인.
- 한국·일본에서 정책금융기관(KDB·KEXIM·JBIC)이 개별 철강/화학 전환 프로젝트에 대해 first-loss 또는 mezzanine 계층으로 명시적으로 참여한 공개 딜 구조 사례는 확인하지 못함.
- 한국 K-Taxonomy 기반 전환금융 가이드라인의 확정 발표일·구체 조문(공식 원문)은 확인하지 못함 — KDI/하나금융연구원 등 2차 해설 자료만 확인.
- 그린스틸 프로젝트에 대한 "초과비용 보증(cost-overrun guarantee)"이 별도 상품으로 존재한다는 사례는 검색 범위 내에서 명시적으로 확인하지 못함 — H2 Green Steel 사례의 보증은 원금 커버리지(80%/95%) 형태로 확인됨.
