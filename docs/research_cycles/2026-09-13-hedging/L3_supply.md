# L3 — 그린수소 공급·물량·조달 위험 문헌 종합

**작업일**: 2026-09-13
**선행**: L1(전력)·L2(원료) — 반복 통찰 "전환은 가격형 위험을 접근형 위험(선점·물량·시점)으로 바꾸고,
조기 전환이 헤지가 되는 것은 접근형에서다". 철강 DR펠릿(글로벌 공급 4%), 재생 PPA 물량이 접근형 사례.
**과제**: 그린수소가 세 번째 접근형 사례인지 검증.
**방법**: WebSearch/WebFetch 실제 확인. 추측 서지 없음. 미확인 사항은 마지막 절에 별도 표시.

---

## 물량 위험 vs 가격 위험

**핵심 문헌은 Odenweller & Ueckerdt(2024/2025, *Nature Energy*, "The green hydrogen ambition and
implementation gap")다.** 이 논문은 전 세계 그린수소 프로젝트 발표치와 실제 가동치를 3년간 추적해
"이행 격차(implementation gap)"를 정의·정량화한다. 검색 결과 간 세부 수치에 일부 불일치가 있다 —
한 출처는 "190개 프로젝트, 2023년 기준 예정대로 완공된 발표 물량 7%"를, 같은 논문의 arXiv 프리프린트
페이지(2406.07210)는 "137개 프로젝트, 2022년 기준 2%, 파이프라인 441GW로 3년간 거의 3배 증가"를
제시한다. 두 수치 모두 같은 저자·같은 계열 논문(연차별 갱신판일 가능성)에서 나온 것으로 보이나,
원문 전체(Nature 사이트는 로그인 장벽으로 직접 확인 불가)를 대조하지 못해 **정확한 연도별 수치는
미확정**이다. 다만 방향성과 규모(수 %대의 이행률, 파이프라인 규모는 400GW대, 3년 내 3배 성장)는
여러 독립 출처(ScienceDaily, EurekAlert, PIK 보도자료 계열)에서 일관되게 재확인된다.
[The green hydrogen ambition and implementation gap, Odenweller & Ueckerdt, Nature Energy, 2024/2025 | https://www.nature.com/articles/s41560-024-01684-7]
[arXiv preprint version, 2406.07210 | https://arxiv.org/abs/2406.07210]
[Green hydrogen: Big gaps between ambition and implementation, ScienceDaily | https://www.sciencedaily.com/releases/2025/01/250114124759.htm]

**Hydrogen Council(산업 컨소시엄) 데이터도 독립적으로 같은 결론을 뒷받침한다.** 2024년 5월 기준
전 세계 발표된 전해조 용량 중 **FID(최종투자결정) 통과 비율은 7% 미만**, 이후 2024년 하반기
S&P Global 집계로는 FID 도달 용량이 20GW(최근 12개월간 6.5GW 추가)로 개선되었으나, 여전히 **초대형
프로젝트(gigaproject)의 FID 통과율은 9%**에 그친다. 원인으로 비용 상승, 수요측 지불의사 부족,
보조금·규제 불확실성이 지목된다.
[Global hydrogen FID capacity reaches 6 million mt/year, S&P Global, 2025-09 | https://www.spglobal.com/energy/en/news-research/latest-news/energy-transition/090925-global-hydrogen-fid-capacity-reaches-6-million-mtyear-hydrogen-council]
[Investing in Green Hydrogen 2024, Cleantech Group | http://cleantech.com/investing-in-green-hydrogen-2024-tackling-green-hydrogens-growing-pains/]

**이것이 가격 위험이 아니라 물량 위험이라는 프레이밍이 핵심.** Odenweller & Ueckerdt는 탄소가격이
없는 상태에서 발표된 프로젝트를 전부 실현하려면 전 세계적으로 1.3~1.6조 달러(범위 0.8~2.6조 달러)의
보조금이 필요하다고 추정한다 — 즉 "가격을 지불할 의사가 있어도, 정책·자본·설비가 그 규모로 물량을
만들어낼 준비가 안 되어 있다"는 구조다. IEA Global Hydrogen Review 2024/2025는 오프테이크 계약
자체가 2023년 2.4Mtpa에서 2024년 1.7Mtpa로 **위축**되었고 그중 확정(firm) 계약은 20%에 불과했다고
보고한다 — 발표는 늘어도 확정 물량은 줄어드는 전형적 접근형 위험 패턴.
[Executive summary, Global Hydrogen Review 2024, IEA | https://www.iea.org/reports/global-hydrogen-review-2024/executive-summary]
[Demand, Global Hydrogen Review 2025, IEA | https://www.iea.org/reports/global-hydrogen-review-2025/demand]

**L1·L2와의 접점.** 철강 DR펠릿(공급 4%)과 재생 PPA 물량은 "물리적 채굴·설비 능력이 단기간에
늘지 않는 경직성"이 병목이었다. 그린수소는 병목이 하나 더 있다 — 자본(보조금 1.3조 달러)과
정책 확정성(오프테이크 계약의 확정 비율 20%) 자체가 공급 병목이라는 점에서, 순수 물리적 병목보다
한 겹 더 정책·금융 의존적인 접근형 위험이다.

---

## 수입 vs 자가 수전해

**한국·일본은 구조적으로 수입국 전략을 취한다.** 일본은 2023년 6월 개정 "수소기본전략"에서 2030년
공급 300만 톤, 2040년 1,200만 톤, 2050년 2,000만 톤 목표를 제시하고, 이를 위해 향후 15년간 15조 엔
이상의 공공·민간 투자를 유도하며 2025 회계연도에 5,860억 엔(약 37억 달러) 예산을 배정했다. 목표
공급단가(CIF 기준)는 2030년 30엔/Nm³, 2050년 20엔/Nm³, 암모니아는 2030년 15~20엔/Nm³(수소 환산) —
즉 처음부터 **수입가(CIF)를 정책 목표 변수로 설정**하는 구조다.
[Basic Hydrogen Strategy, METI, 2023-06-06 | https://www.meti.go.jp/shingikai/enecho/shoene_shinene/suiso_seisaku/pdf/20230606_5.pdf]

**공급망은 호주·중동에 집중된다.** 일본 최대 정유사 ENEOS는 사우디 아람코와 CO2-free 수소·암모니아
공급망 개발 MOU를 체결했고, 사우디 SABIC 생산 암모니아가 이미 일본 소데가우라 정유소에 공급되어
석탄 혼소에 쓰이고 있다. 한국은 삼성물산이 호주 필럿에너지(Mid West Clean Energy Project, 연산
120만 톤 CCS 기반 암모니아, 2027년 가동 목표)와 오프테이크 계약을 추진 중이며, SK E&S는 호주
우드사이드와 수소·암모니아 밸류체인 MOU(2024-01, 비구속적)를 체결했다. 포스코는 호주·사우디
양쪽에 수소 생산 투자 확대를 발표했다.
[CCS-based ammonia exports from Australia & Canada to South Korea, Ammonia Energy Association | https://ammoniaenergy.org/articles/ccs-based-ammonia-exports-from-australia-canada-to-south-korea/]
[SK E&S and Woodside Collaborate on Hydrogen and Ammonia, Marine Link, 2024-01 | https://www.marinelink.com/news/sk-es-woodside-collaborate-hydrogen-510597]

**수입 오프테이크의 위험 구조는 "비구속적 MOU 단계에 몰려 있다"는 것.** 위에 확인된 한국·일본
계약 대부분이 MOU·타당성조사(feasibility study) 단계이며, 구속력 있는 장기 오프테이크로 전환된
사례는 검색 범위에서 명확히 확인하지 못했다(Fertiglobe-H2Global 계약처럼 유럽 사례는 구속력 있는
계약이 존재 — 아래 절 참조). S&P Global(2024-04)은 "비용이 높은 호주산 재생수소가 향후 예정된
공급 계약을 미국·중동에 뺏길 수 있다"고 분석 — **수입국 입장에서 조달 위험은 가격 경쟁력이 아니라
공급원 자체가 계약 단계에서 경쟁사(다른 수입국)에 선점당할 위험**으로 나타난다.
[Costly Australian renewable hydrogen may lose upcoming supply deals to Middle East, US, S&P Global, 2024-04-25 | https://www.spglobal.com/commodityinsights/en/market-insights/latest-news/energy-transition/042524-costly-australian-renewable-hydrogen-may-lose-upcoming-supply-deals-to-middle-east-us]

**자가 수전해(재생전력×전해조) 위험 구조는 다르다.** 포스코의 HyREX(수소환원제철) 전략은 상용화를
2030년까지 목표로 하며, 검색 결과 "엔지니어링팀이 (아마도 자체 전해조를 통한) 수소 공급계약을
확보하는 데 주력할 것"이라는 서술은 확인되나, 구체적 전해조 발주·용량·공급사 계약은 확인하지 못했다
— 즉 한국 철강사조차 아직 "수입이냐 자가생산이냐"의 조달 경로 자체가 확정되지 않은 단계다. 자가
수전해의 위험은 **수입국 경쟁이 아니라 전해조 납기·재생전력 확보(L1의 재생 PPA 물량 위험)로 전이**된다
— 즉 자가 경로를 택해도 접근형 위험이 소멸하지 않고 상류(전해조·재생전력)로 이동할 뿐이다.
[From CCUS to HyREX, POSCO Newsroom | https://newsroom.posco.com/en/from-ccus-to-hyrex-the-full-lineup-of-posco-groups-decarbonization-strategies-for-a-sustainable-steel-industry/]

---

## 조달 정책·입찰 불확실성

**한국 CHPS(청정수소발전 입찰시장) 2025-10 전격 중단.** 기후에너지환경부는 2025년 청정수소발전
경쟁입찰 마감일(10월 17일) 당일 입찰 자체를 취소했다. 사유는 "낙찰받은 석탄발전소를 15년 이상
가동시키는 CHPS 설계"가 "2040년 탈석탄" 국정과제와 정합하지 않는다는 판단 — 즉 **제도 설계 결함이
사후에 발견되어 조달 채널 자체가 중단**된 사례다. 2025-12 기준 CHPS·LNG 용량시장 모두 이듬해(2026)로
연기된 것으로 확인되며, 2026-05 기사는 "CHPS 입찰 재개 임박"을 전하지만 재개 시점은 유동적이다.
D4 앵커(h2_contract_krw_kg 10,000원, 2024-12)가 이후 갱신할 시장가 자체를 만들어내지 못하는 구조적
이유가 이것 — **정책 조달 채널의 존속 여부 자체가 불확실**하다.
[이재명 정부, 청정수소발전 입찰 전격 중단, 다음뉴스/뉴스타파, 2025-10-20 | https://v.daum.net/v/20251020172612785]
[청정수소발전(CHPS)·LNG 용량시장, 결국 내년으로, 에너지경제, 2025-12-29 | https://edata.ekn.kr/article/view/ekn202512290003]
[CHPS 입찰 재개 임박, 에너지경제, 2026-05-20 | https://m.ekn.kr/view.php?key=20260520022086161]

**유럽은 구속력 있는 조달 인프라를 이미 가동 중이지만 규모가 작다.** European Hydrogen Bank
1차 경매(2024-04-30 결과 발표)는 7개 프로젝트에 총 7.2억 유로를 배정, 10년간 158만 톤 재생수소
생산 계획이며 낙찰 프리미엄은 kg당 0.37~0.48유로(상한 4.5유로 대비 크게 낮음) — 스페인·포르투갈·
노르웨이·핀란드 프로젝트에 국한되고 동아시아 수입국과는 무관하다. H2Global(독일 주도, 네덜란드
공동)의 이중경매(double-sided auction) 방식은 시범경매에서 Fertiglobe가 낙찰(최대 계약가치
3.97억 유로, 2027년 유럽 항만 인도)받아 재생 암모니아를 생산 중이며, 2차 경매는 독일·네덜란드
합산 25억 유로 규모로 확대되었다. 즉 유럽은 "가격 프리미엄을 국가가 흡수하는" 계약 인프라를
갖췄지만, 한국·일본은 이런 CfD형 조달 메커니즘 자체가 아직 CHPS 중단 사례처럼 시행착오 단계다.
[2nd European Hydrogen Bank Auction Results, Green Hydrogen Organisation | https://gh2.org/2nd-european-hydrogen-bank-auction-results-mandates-and-finance-must-work-together-green-hydrogen]
[Results of the pilot auction, H2Global | https://h2-global.org/news/results-of-the-pilot-auction/]
[Massive boost for green hydrogen exporters as Germany allocates €3.5bn to H2Global auction subsidies, Hydrogen Insight | https://www.hydrogeninsight.com/production/massive-boost-for-green-hydrogen-exporters-as-germany-allocates-3-5bn-to-h2global-auction-subsidies/2-1-1597237]

**조달 계약 인프라의 미성숙이 공통 패턴.** 일본은 CfD형 "가격차액계약" 지원제도를 2024~25년
시행 예정이었으나, 검색된 분석(S&P Global 계열)은 "중동·미국이 저비용 연료·기존 공급망 덕에
일본·한국 수요를 채우기에 더 유리한 위치"라고 평가 — 정책 설계는 진행 중이나 실제 낙찰까지
이어진 사례는 확인하지 못했다.

---

## 전해조·인프라 병목

**전해조 제조 능력 자체가 병목이다.** IEA·산업 분석 종합에 따르면 2027년 세제혜택 일몰(미국
IRA 45V 관련 추정)을 앞두고 기가와트급 발주가 한꺼번에 몰리면서 "제조 슬롯, 장납기 설비, 숙련
인력에 대한 경쟁이 격화"되었고, 이전에는 관리 가능한 수준이던 전해조 납기가 이제는 "critical path
item"이 되었다. 중국이 전 세계 설치용량·FID 통과 용량의 65%, 전해조 제조능력의 약 60%를 점유해
비중국 제조사는 매출 급감·손실 확대에 직면했다는 분석도 확인된다.
[Electrolysers, IEA Energy System | https://www.iea.org/energy-system/low-emission-fuels/electrolysers]
[European Electrolyser Capacity vs. Project Pipeline: EIC Report, IndexBox, 2026 | https://www.indexbox.io/blog/european-electrolyser-makers-face-project-shortage-despite-ample-capacity/]

**FID 지연이 물리적 병목보다 앞선 병목이라는 지적도 존재.** 한 출처(2024 Pathways to Commercial
Liftoff 계열 분석)는 "2030년 목표 31GW 중 실제 FID 도달은 약 3GW에 불과"하다고 지적하며, 원인으로
높은 생산비용, 불확실한 수요, 유동적 규제, 장기 오프테이크 계약 부족을 꼽는다 — 즉 **전해조
제조능력이 부족해서가 아니라, 그 이전 단계(계약·자금조달)에서 프로젝트가 막혀 있어 아직 제조
병목까지 도달하지 못한 프로젝트가 대다수**라는 뜻이다. 이는 향후 오프테이크·자금조달이 풀리면
제조 병목이 뒤늦게 현재화될 수 있음을 시사 — L2에서 확인한 "타이밍 불일치(선투자 필요 vs 수요
확정 시점 지연)"와 동일한 구조다.
[UPDATE 2024 Pathways to Commercial Liftoff: Clean Hydrogen, DOE, 2024-12 | https://climateprogramportal.org/wp-content/uploads/2025/02/Pathways-to-Commercial-Liftoff_Clean-Hydrogen_December-2024-Update.pdf]

**파이프라인·터미널·저장 등 하류 인프라의 선투자 필요성**은 검색에서 일반론 수준(수소 공급망은
전해조뿐 아니라 압축·액화·운송·저장 설비까지 별도 CAPEX·리드타임이 필요하다는 산업 서술)으로만
확인되며, 정량화된 학술 추정치는 이번 검색에서 확보하지 못했다(미확인 항목 참조).

---

## 수요 경쟁과 선점 가치

**H2-DRI 수소 원단위는 약 54kg H2/톤 DRI(화학양론적 최소 요구량)로 확인된다.** LBNL(Lawrence
Berkeley National Laboratory) 연구(Patrizio et al., *Energy & Environmental Science*, "Green
steel: design and cost analysis of hydrogen-based direct iron reduction")가 이 수치의 근거로
검색되며, 실제 산업 운전에서는 열손실·공정 비효율로 이보다 높을 수 있다는 단서가 붙는다. IEEFA는
H2-DRI-EAF 공정이 잔여 천연가스 사용을 제외하면 톤당 약 160kg CO2 수준까지 직접배출을 낮출 수
있다고 평가한다.
[Green steel: design and cost analysis of hydrogen-based direct iron reduction, Patrizio et al., Energy & Environmental Science, LBNL | https://eta.lbl.gov/publications/green-steel-design-and-cost-analysis]
[Hydrogen unleashed: H2-DRI-EAF pathway beyond 2024, IEEFA | https://ieefa.org/resources/hydrogen-unleashed-opportunities-and-challenges-evolving-h2-dri-eaf-pathway-beyond-2024]

**석유화학 부문은 이미 그린수소의 최대 흡수처다.** 정유는 기존에 대량의 그레이수소를 수첨탈황·
수소화분해 공정에 써왔기 때문에 "공정 재설계 없이" 전해수소로 전환하기 가장 쉬운 부문으로 지목되며,
실제로 유럽 EHB 경매 낙찰 물량 흐름에서도 정유 부문이 초기 물량을 흡수하는 경향이 확인된다.
화학 부문(암모니아 합성 전환, e-메탄올 선박연료·화학원료용) 이 가장 빠르게 성장하는 세그먼트로
지목된다. IEA는 2024년 오프테이크 서명 물량이 2023년 2.4Mtpa에서 1.7Mtpa로 줄었고, "정유 부문은
긍정적 진전, 철강·비료 부문은 불확실한 결과"라고 명시 — **철강이 석유화학보다 오프테이크 확보
경쟁에서 뒤처져 있다는 근거**다.
[Demand, Global Hydrogen Review 2025, IEA | https://www.iea.org/reports/global-hydrogen-review-2025/demand]

**수요 초과 시 조기 확보(선점)의 가치는 정성적으로만 확인된다.** 정유·화학이 이미 물량을 선점해가는
구조라면, 철강사가 뒤늦게 그린수소 확보 경쟁에 뛰어들 경우 (a) 남은 저비용 공급원(호주·중동
대형 프로젝트)의 오프테이크가 이미 정유·화학사에 배분되었거나, (b) 자체 전해조 경로로 갈 수밖에
없어 L1의 재생 PPA 병목에 다시 부딪히는 구조다. 이를 정량화한 학술 문헌(철강 대 석유화학의 상대적
지불여력·계약 순번을 모형화한 연구)은 이번 검색에서 확인하지 못했다 — 이는 우리 분포 모형이
직접 채워야 할 간극일 수 있다.

---

## 접근형 축 세번째 확인 판정

**그린수소는 L1(전력)·L2(원료)와 동일한 접근형(access-type) 구조를 보이며, 오히려 더 심한 버전이다.**

| 특성 | L1 재생 PPA | L2 DR펠릿 | L3 그린수소 |
|---|---|---|---|
| 물량 제약의 원천 | 계통·부지·PPA 계약 슬롯 | 채굴·정광 물리적 능력(공급 4%) | 전해조 제조+정책 조달 채널+오프테이크 확정성 |
| 가격 vs 물량 | 물량형 | 물량형 | **물량형 — 문헌이 명시적으로 프레이밍**(Odenweller & Ueckerdt) |
| 정책 채널 안정성 | 상대적으로 안정 | 안정(상업적 계약) | **불안정 — 한국 CHPS 자체가 중단됨** |
| 조기 확보의 헤지 가치 | 확인됨(L1) | 확인됨(Stegra·LKAB, L2) | **정성적으로만 확인 — 정유·화학이 이미 선점 중이므로 철강의 후발 확보는 오히려 penalty 위험** |

세 가지 점에서 그린수소는 앞선 두 사례보다 접근형 성격이 **더 강하다**: (1) 이행률 자체가
문헌에서 명시적으로 "물량 위험"으로 정의된 유일한 사례(Odenweller & Ueckerdt), (2) 조달 정책
채널의 존속 여부 자체가 불확실(CHPS 중단은 재생 PPA나 DR펠릿 조달에는 없는 종류의 리스크 —
"계약이 비쌀 위험"이 아니라 "계약할 창구 자체가 사라질 위험"), (3) 수요 경쟁에서 철강이 정유·
화학보다 후순위라는 근거(IEA 오프테이크 통계)가 있어, "조기 전환이 헤지가 된다"는 명제가 철강
그린수소 조달에는 **경쟁자보다 늦으면 헤지가 안 된다는 조건부** 형태로 나타난다.

**판정: 세 번째 접근형 사례로 확인(confirmed), 단 조건부.** 가격형이 아니라는 점은 명확히
확인되나, "조기 확보=헤지"라는 단순 명제는 유지되지 않는다 — 철강사가 정유·화학사와 동시에
움직이는 경쟁적 확보(competitive pre-emption) 구조이므로, 조기성 자체보다 **상대적 확보 순위**가
헤지 성립의 조건이다. 이는 L1·L2의 "먼저 움직이면 헤지"보다 한 단계 더 미묘한 구조 — 분포
모형에 반영 시 이 조건성을 명시해야 한다.

---

## 분포에 반영할 함의

1. **물량 미달 확률분포를 가격 분포와 분리해서 모형화해야 한다.** Odenweller & Ueckerdt류 이행률
   (한 자릿수~10%대)을 참고해, "계약을 체결했음에도 실제 인도되는 물량이 계획 대비 하방 이탈할
   확률"을 별도 축으로 넣을 근거가 있다 — D4의 h2_contract_krw_kg 같은 가격 앵커만으로는 이
   리스크가 전혀 포착되지 않는다.
2. **정책 조달 채널의 존속 자체를 불확실성 변수로 넣어야 한다.** CHPS 중단 사례는 "정책이 방향을
   바꿔서 불리해지는" 통상적 정책 리스크가 아니라 "채널이 사라져 조달 경로 자체가 없어지는"
   리스크 — F2(공시점 계약 비대칭) 논의와 연결해, 수소는 계약 자체를 맺을 수 있는 창구의
   존재 여부가 변수가 되어야 한다.
3. **경쟁 우선순위(철강 vs 정유·화학) 변수 도입 검토.** 조기 전환이 헤지가 되려면 "남보다 먼저"
   여야 하는데, 정유·화학이 이미 앞서 있다는 근거가 있으므로 철강 부문에 한정된 분포에서는
   조기 확보의 기대효과를 L1·L2보다 보수적으로(할인) 잡아야 한다.
4. **자가 수전해 선택도 접근형 위험을 소멸시키지 않고 L1(재생 PPA·전해조 납기)으로 이전할 뿐**
   이므로, 수입/자가 두 조달 경로를 별도 확률과정으로 두되 상관관계(둘 다 같은 상류 병목—재생전력·
   전해조 제조능력—을 공유)를 모형에 반영해야 한다.

---

## 미확인

- Odenweller & Ueckerdt 논문의 **정확한 연도별 이행률·프로젝트 수·파이프라인 GW**: 검색 스니펫 간
  불일치(7% vs 2%, 190개 vs 137개 프로젝트, 422GW vs 441GW) — Nature 원문은 로그인 장벽으로 직접
  대조하지 못함. 인용 시 범위로만 사용 권고.
- 철강·석유화학 간 **그린수소 확보 경쟁을 정량 모형화한 학술 문헌**: 오프테이크 통계(IEA)로 정성적
  추세는 확인되나, 부문별 지불여력·계약 순번을 다룬 전용 연구는 확인하지 못함.
- **파이프라인·터미널·저장 등 수소 하류 인프라의 선투자 필요 규모(CAPEX, 리드타임)를 정량화한
  학술 출처**: 산업 일반론 수준 서술만 확인, 전용 연구 미확인.
- **포스코 HyREX의 구체적 수소 조달 계약(전해조 발주처·용량, 수입 계약 여부)**: 뉴스룸 자료는
  전략 단계 서술에 그치고 구체적 계약 내용 미확인.
- 한국 CHPS 재개 시점 및 개정된 제도 설계(석탄 연계 조항 삭제 여부): 2026-05 기사가 "재개 임박"을
  전하나 확정 공고 시점·조건은 이번 검색에서 확인하지 못함.

---

# SYNTHESIS L3 (그린수소) — 2026-09-13

## 접근형 축, 세 번째 확인 — 그러나 "조기 = 헤지"의 단순형은 깨진다
전력 β(L1)·DR펠릿(L2)·수소(L3) 셋 다 접근형. 수소가 세 번째지만 명제를 두 번 정련한다:
1. **상대적 확보 순위** — 철강은 정유·화학보다 수소 오프테이크 후순위(IEA: "정유 긍정, 철강 불확실").
   조기 전환해도 경쟁에서 밀리면 못 확보 → 헤지는 "일찍"이 아니라 "일찍 **그리고** 상대적으로
   앞서서"일 때만 성립. L2의 깨끗한 철강 스토리를 여기서 누그러뜨린다.
2. **정책 창구 존재 위험** — CHPS 2025-10 중단은 "계약이 비쌀 위험"이 아니라 "계약 창구가
   사라질 위험." 이것은 접근형의 하위형이 아니라 **정책·제도 존재 위험**이라는 넷째 종류로 보인다
   → L4(탄소·정책)에서 다룬다.

## 가격형/접근형 이분법의 수정
L1~L2는 위험을 가격형/접근형 둘로 갈랐다. L3가 셋째를 연다 — **정책·제도 존재 위험**(조달 채널·
할당 규칙·입찰 시장이 있느냐 없느냐). 수소가는 시장에서 발견되지 않고 경매·CfD로 정해지므로
"수소 가격 변동성(GBM σ)"은 애초에 잘못된 프레임. 세 종류로 정리: 가격형(계약 헤지) / 접근형(선점) /
제도형(정책이 만들거나 없앰). 조기 전환은 접근형만 헤지하고, 제도형은 기업이 못 헤지한다 —
정부만 만들 수 있다(DIRECTION의 "커미트먼트" 수단이 여기 붙는다).

## CAP 모형 수정 방향 (L3 근거)
- 수소 학습곡선 시나리오 층(Way 2022 하락) **폐기** — 학습 약함(12–15%)·CAPEX 반등(+57%).
  DIRECTION의 "감축기술 학습 = 시나리오 층"은 낙관 허구였다. 수소는 학습이 아니라 접근·제도.
- 수소가 = 전력 파생(구조식 방향 맞음, 전력 57–87% 지배) + **물량 미달 확률 + 조달 채널 존재 확률**.
  σ=0.25 독립 GBM 폐기(코드 주석도 근거 없음 자인).
- 전해조 CAPEX는 결정론 상수 대신 양방향 확률(반등 실현치 반영).

## 직전(L2) 비판적 재검토
L2는 "조기 전환 = 선점 헤지"를 철강에서 깨끗하다 했다. L3가 정련: 선점은 **상대 순위** 문제라
철강이 자동으로 이기지 않는다(수소 후순위). 그리고 L2의 "접근형"에 L3가 "제도형"을 분리해냈다 —
CHPS처럼 창구 자체가 사라지는 건 선점으로도 못 막는다. 접근형 축은 유지되나 그 위에 제도형이
얹힌다.
