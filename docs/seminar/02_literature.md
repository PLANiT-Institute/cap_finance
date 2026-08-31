# 2회차 — 학술 문헌: 전환리스크가 실제로 가격에 반영되는가

작성 2026-09-01. 1회차 논지(T1: "라벨은 생겼는데 판정 기준이 없다")를 문헌으로 시험한 회차.
**결과: 논지가 강화됐다. 그리고 대안 신호가 무엇인지도 문헌이 답을 주고 있다.**

---

## 발견

### L1. '탄소 프리미엄'은 무너졌다 — 그것도 최상위 저널에서

전환금융 논의의 밑돌은 "시장이 전환리스크를 가격에 반영한다"는 명제였다. 근거는
**Bolton & Kacperczyk (2021 JFE, 2023 JF)** — 배출 수준·증가율이 높은 기업이 높은 실현수익률을
낸다, 즉 자기자본비용이 높다, 즉 전환리스크가 가격에 반영돼 있다.

이게 두 번 공격받고 무너졌다.

**1차 — Aswani, Raghunandan & Rajgopal (2024, *Review of Finance* 28(1):75).**
탄소 프리미엄은 다음 두 경우 유의성을 잃는다:
- 배출을 매출로 스케일링(탄소집약도)하면
- 벤더 *추정치*가 아니라 기업 *공시* 배출량만 쓰면

즉 수익률과 상관을 보이는 것은 **데이터 벤더가 추정한 비스케일 절대배출량**뿐이다. 벤더 추정치는
기업 공시치와 체계적으로 다르고 재무 펀더멘털과 강하게 상관한다. 프리미엄은 탄소가 아니라
펀더멘털을 잡고 있었다는 것. Bolton & Kacperczyk가 같은 호(28(1):107)에서 "절대배출량이
전환리스크의 올바른 척도"라고 반박했고, 저자들이 재반박했다. **미해결.**

**2차 — Zhang (2025, *Journal of Finance*), "Carbon Returns across the Globe".** 더 결정적이다.
배출 데이터는 회계연도 종료 후 **10~12개월 뒤**에 공시된다. 그런데 배출은 매출과 매우 강하게
묶여 있다(매출이 배출 변동의 **50~71%** 설명). 배출 데이터를 수익률과 동시점으로 쓰면
**미래 매출 정보가 새어 들어간다(look-ahead bias)**.

공시 시차를 제대로 넣으면 결과가 뒤집힌다:
- 미국: 탄소집약 기업이 **음(−)의 수익률** — 월 −0.39% ~ −0.27% (가치가중),
  FF6요인 조정 알파 **−0.40%, −0.34%**
- 전 세계(40개국+, 2009–2021, Trucost): **유의하지 않음**
- 선진국에서 음의 탄소수익률이 더 강함

Zhang은 B&K 방법론을 그대로 복제하면 양의 프리미엄이 재현되지만, **동시점 매출성장률을
통제하는 순간 프리미엄이 완전히 사라진다**고 보인다.

### L2. 크레딧 시장은 더 나쁘다 — 고탄소가 오히려 스프레드 *할인*을 받는다

미국 회사채 유통시장 연구(실측 Scope 1·2 집약도만 사용, 추정치 배제):
탄소집약도가 높은 기업이 중위 기업 대비 **낮은** 신용스프레드로 거래된다.
- 2020년 이전: 약 **−11bp** 할인
- 2020–2022년 A등급: **−16bp**로 할인 확대

신디케이트론에서는 반대 방향으로 **+3~7bp** 탄소 리스크 프리미엄이 관측된다. 은행은 직접
전환리스크는 대출전략에 반영했지만 **공급망에 숨은 탄소발자국은 놓치고 있다**는 연구,
그리고 탄소 관련 여신 집중이 **전환충격 시 은행 시스템 리스크를 증폭**시킨다는 연구가 있다.

정리: 주식에서 프리미엄은 사라졌고, 채권에서는 부호가 반대이며, 대출에서만 한 자릿수 bp가 있다.
**"시장이 이미 반영하고 있다"는 전제로 세미나를 시작하면 안 된다.**

### L3. 그런데 좌초자산 손실 자체는 실재하고, 그 부담은 OECD 투자자에게 온다

**Semieniuk et al. (2022, *Nature Climate Change* 12(6)).** 기후정책 기대의 그럴듯한 변화만으로
상류 석유·가스 부문의 미래이익 현재가치 손실이 **1조 달러**를 넘는다.

방법이 이 세미나에 쓸모 있다: **43,439개 석유·가스 생산자산**을 **180만 개 기업**의 글로벌
지분 네트워크를 따라 **최종 소유자까지 추적**했다. 결과 —
- 시장리스크 대부분이 **민간 투자자**, 압도적으로 **OECD** 소재
- **연기금**을 통한 상당한 노출
- 전 세계 좌초자산 리스크의 **15% 초과분이 OECD 투자자로 순이전**

즉 리스크는 실재하는데 가격에는 없다(L1·L2). 이 간극이 문제의 본체다.

### L4. 배제는 자본비용을 못 움직인다. 관여는 움직이지만 조건부다.

**Berk & van Binsbergen (2024, *JFE*), "The impact of impact investing".**
배제(divestment)의 자본비용 효과는 세 파라미터의 함수로 근사된다 — 사회적 자본의 비중,
대상 기업의 비중, 대상 기업과 시장의 수익률 상관. **현재 데이터로 캘리브레이션하면 그 효과는
실물 투자결정을 바꿀 만큼 크지 않다.** ESG 지위 변경 사건 연구에서도 대상 기업 자본비용에
탐지 가능한 영향이 없었다. 저자들의 결론: 영향을 주려면 팔지 말고 **보유하고 통제권을 행사하라**.

**Broccardo, Hart & Zingales (2022, *JPE* 130(12)), "Exit versus Voice".**
투자자 다수가 **조금이라도** 사회적 선호를 가지면 **voice(관여)가 사회적 최적을 달성**하고
exit(배제)은 못 한다 — exit이 작동하려면 모두가 *상당히* 사회적이어야 한다. 또한 exit에
참여할 개인 유인은 사회적 유인과 정렬되지 않는 반면, 분산투자자가 목소리를 낼 수 있으면 정렬된다.
투자자 다수가 순수 이기적이면 exit이 더 낫지만, 어느 쪽도 일반적으로 최선에 이르지 못한다.

**Dimson, Karakaş & Li, "Coordinated Engagements".** 협력적 E&S 관여 성공률 **52.7%**
(단독·협력 혼합 표본의 이전 연구는 45.2%). 리드 투자자 + 지원 투자자의 **2계층 구조**가 효과적이고,
성공 후 대상 기업 성과 개선과 펀드 자금유입 증가가 따라온다. 리드가 될 확률은 지분·노출이 크고,
공식 관여 프로세스가 있고, 협력 이니셔티브 참여가 넓을수록 높다.

**반대편**: EDHEC Climate Institute는 *Active Ownership as a Tool of Greenwashing*에서
관여 자체가 그린워싱 수단으로 쓰인다고 지적한다. 그리고 기관투자자 보유가 평균적으로는
탄소발자국의 의미 있는 감소로 이어지지 않으며, **최상위 오염기업에 한해 제한적 감소**만
관측된다는 증거가 있다.

### L5. 전환계획은 지금 '심사 불가능' 상태다 — 이게 핵심 숫자다

**CDP (2024)**: 2023년에 **약 6,000개 기업이 1.5°C 정합 전환계획을 보고**했다.
그런데 신뢰성 평가에 필요한 **21개 지표 전부를 공시한 기업은 140개**.

**2.3%.**

즉 1회차에서 본 표준의 빈칸(CTFH가 평가 *도구 목록*만 제시)은 방법론 문제이기 이전에
**데이터 문제**다. 판정하고 싶어도 판정할 입력이 없다.

### L6. 그래서 자본지출이 남는다 — 유일하게 관측 가능한 신호

**Clarity AI**, 8개 탄소집약 부문(항공·알루미늄·자동차·시멘트·전력·해운·석유가스·철강),
MSCI ACWI 중 **녹색 capex를 공시하는 232개사** 표본:

| 부문 | 녹색 capex 비중 |
|---|---|
| 항공 | 71% |
| 전력 | 46% |
| 해운·자동차 | 30% 미만 |
| **철강·시멘트·석유가스** | **10% 미만** |

공시 자체가 희소하다:
- 세계 최대 배출기업의 **50% 미만**이 녹색 capex를 공시
- 유럽 밖에서는 **약 30%**
- EU-27 및 유럽 평균 21~23% (공시율이 높아 생존편향이 덜함 — 다른 지역의 높은 수치는
  자발적 보고자만 남은 **생존편향**)
- ACT 방법론은 전력에 **95%** 문턱을 두는데, 표본 전력사 중 **14개사(17%)만** 충족

Clarity AI의 문장: 탈탄소가 가장 절실한 부문에서 **자본의 대부분이 여전히 고탄소 운영 유지로
간다.** 그리고 금속·광업, 석유·가스, 건설·부동산에서는 전환정합 capex 비중이 높은 기업이
**더 높은 밸류에이션**을 받는다 — 투자자가 이미 리더와 후발주자를 구분하고 있다.

### L7. 신뢰성이 실제 배출 성과로 이어진다는 첫 계량 증거

**Silvia et al. (2026-08-10, *Frontiers in Environmental Science*).**
Fortune Global 500 비금융 **239개사, 1,126 기업-연도, 2018–2023**.
6개 차원 24개 항목의 Climate Transition Plan Credibility Index(CTPCI) 구성 —
목표 신뢰성(5), 배출 범위 커버리지(3), 이행 전략(5), 거버넌스·책임(4), 리스크·전략 통합(4),
진척 보고(3).

- 전환계획 신뢰성이 높을수록 **후속 배출 변화가 유의하게 낮음** (계수 **−0.057, p<0.01**)
- **외부검증(assurance)이 이 관계를 강화** (상호작용 **−0.036, p<0.05**)
- 의무공시 환경의 조절효과는 약함
- 저자 스스로 관찰 패널 설계이므로 **인과가 아니라 체계적 연관**이라고 못 박음

### L8. 난감축 부문에서 무너지는 지점은 '중기'다

**"Planning to fail? Credibility and financing of corporate transition plans in hard-to-abate
sectors"** (*iScience*, 2026-06-08). 난감축 부문 **상장 411개사**의 전환계획과 재무데이터.
근시(2027/2028)·중기(2035)·장기(2050) 세 시계에서 탄소성과 정합을 평가.

- **1.5°C 정합이 가장 약한 구간은 중기(2035)** — 변혁적 감축이 가장 필요한 바로 그 시점
- 많은 기업이 야심찬 기후 약속을 내놓지만 **재무계획에 충분히 내장돼 있지 않다**
- **capex–기후목표 정합이 강하고 조달비용이 낮을수록** 전환전략의 신뢰성이 높은 것과 연관

L6·L8이 같은 말을 다른 데이터로 한다: **말과 예산 사이의 간극, 그리고 그 간극이 벌어지는
시점은 2030년대 중반.**

---

## 투자자 함의

**I1. "시장이 이미 반영하고 있다"는 전제를 버려야 한다.**
탄소 프리미엄은 최상위 저널에서 look-ahead bias로 판명됐다(Zhang 2025 JF). 회사채에서는
부호가 반대다(고탄소 −11~−16bp 할인). 그런데 좌초자산 손실은 1조 달러 규모로 실재하고
OECD 연기금이 그 부담을 진다(Semieniuk 2022). **가격과 리스크가 분리돼 있다.**
→ 이건 알파 이야기가 아니라 **미가격화된 부채(unpriced liability)** 이야기다.

**I2. 배제로는 안 된다. 관여는 되는데, 판정 기준이 있어야 한다.**
Berk–van Binsbergen: 배제의 자본비용 효과는 실물투자를 못 바꾼다. BHZ: voice가 우월.
Dimson et al.: 협력 관여 성공률 52.7%. **그런데 관여의 성공 판정 기준이 없으면 관여 자체가
그린워싱이 된다(EDHEC).** 관여를 정당화하려면 "무엇이 개선되면 성공인가"를 사전에 못 박아야 한다.

**I3. 배출 데이터로는 심사할 수 없다.**
벤더 추정치는 펀더멘털의 대리변수이고(Aswani et al.), 공시 시차 때문에 동시점 사용은 편향이며
(Zhang), 6,000개 중 140개만 신뢰성 평가가 가능하다(CDP). **배출량 스크리닝은 사실상 작동하지 않는다.**

**I4. 남는 관측 가능한 신호는 자본지출과 자산단위 계획이다.**
철강·시멘트·석유가스의 녹색 capex는 10% 미만이고, 공시 자체가 최대배출기업의 절반도 안 된다.
그런데 capex 정합이 높은 기업은 이미 더 높은 밸류에이션과 더 낮은 조달비용을 받는다(Clarity AI,
iScience 2026). **즉 신호는 이미 가격에 일부 들어가 있는데, 그 신호를 측정하는 투자자가 소수다.**

**I5. 심사의 시간축은 2035년이다.**
난감축 411사에서 정합이 가장 깨지는 구간이 중기(2035)다. 2050 넷제로 선언과 2030 중간목표
사이의 **빈 구간**이 실제 위험 구간이고, 대부분의 전환계획이 거기서 침묵한다.
→ 질문 하나로 요약: **"2035년에 당신 자산에서 무슨 일이 일어나는가?"**

---

## 반론 / 확인 필요

- **R1.** Zhang(2025)이 학계 합의는 아니다. B&K가 재반박할 여지가 있고, "절대배출량 vs 집약도"
  논쟁은 미해결. 세미나에서는 **"프리미엄이 없다"가 아니라 "프리미엄의 존재가 논쟁 중이며
  가장 최근 최상위 저널 증거는 부정적"** 으로 말해야 안전하다.
- **R2.** 회사채 −11~−16bp 할인은 단일 연구(미국 유통시장). 부호가 놀라운 만큼 다른 연구와
  교차확인 필요 — 7회차에서 한국 회사채·KP물 스프레드와 대조.
- **R3.** Clarity AI는 상업 데이터 제공사다. 232개사 표본은 자발적 공시자만이라 **생존편향**을
  본인들도 인정한다. 부문별 수치를 인용할 때 표본 성격을 붙여야 한다.
- **R4.** Silvia et al.의 −0.057은 관찰 연관이지 인과가 아니다. 저자 본인이 명시. 세미나에서
  "신뢰할 만한 계획이 배출을 줄인다"로 말하면 과장.
- **R5.** iScience 411사 연구는 2026-06 게재로 아직 인용이 얕다. 표본 구성(어느 부문, 어느 지역)을
  원문에서 확인해야 함 — ScienceDirect 403으로 초록만 확보. **미해결 확인 항목.**
- **R6.** 한국 표본 문헌은 아직 안 봤다. K-ETS 하 기업의 전환리스크 가격반영 실증이 있는지
  3회차에서 확인.

---

## 1회차 논지에 대한 영향

**T1 강화.** 1회차는 "라벨은 있는데 판정 기준이 없다"였다. 2회차가 두 가지를 추가한다:

1. **가격도 판정해주지 않는다.** 시장가격을 판정 대체물로 쓸 수 없다(L1, L2).
2. **대안이 무엇인지 문헌이 이미 가리키고 있다** — capex 정합, 자산단위 계획, 2035년 중기 구간
   (L6, L7, L8). 그리고 그걸 측정하는 투자자가 소수라 **차별화 여지가 있다**(Clarity AI 밸류에이션 결과).

→ **세미나 논지 T1'**: *"라벨도 가격도 전환의 신뢰성을 판정해주지 않는다.
남은 것은 자본지출과 자산단위 계획이고, 그 심문은 2035년을 겨눠야 한다."*

---

## 출처

- [CEPR VoxEU — Why carbon emissions are associated with higher stock returns](https://cepr.org/voxeu/columns/why-carbon-emissions-are-associated-higher-stock-returns)
- [Aswani, Raghunandan & Rajgopal — Are Carbon Emissions Associated with Stock Returns? *Review of Finance* 28(1):75 (2024)](https://academic.oup.com/rof/article/28/1/75/7100359)
- [Bolton & Kacperczyk — Are Carbon Emissions Associated with Stock Returns? Comment. *Review of Finance* 28(1):107](https://academic.oup.com/rof/article-abstract/28/1/107/7152290)
- [Aswani, Raghunandan & Rajgopal — Reply (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4442200)
- [Zhang — Carbon Returns across the Globe. *Journal of Finance* (2025)](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13402)
- [Does the Carbon Premium Reflect Risk or Mispricing? (ECGI working paper, PDF)](https://www.ecgi.global/sites/default/files/working_papers/documents/doesthecarbonpremiumreflectriskormispricing.pdf)
- [Corporate climate risk and bond credit spreads (*Finance Research Letters*)](https://www.sciencedirect.com/science/article/abs/pii/S1544612324007712)
- [Carbon intensity disclosure and corporate credit spreads (*J. Industrial Ecology*, 2026)](https://link.springer.com/article/10.1007/s44498-026-00052-w)
- [Carbon-related credit concentration and banking systemic risk due to climate transition shocks](https://www.sciencedirect.com/science/article/abs/pii/S1057521925004983)
- [Semieniuk et al. — Stranded fossil-fuel assets translate to major losses for investors in advanced economies. *Nature Climate Change* 12(6), 2022](https://www.nature.com/articles/s41558-022-01356-y)
- [Semieniuk et al. — Fossil-fuel stranded asset risks held by individuals in OECD countries and non-OECD governments. *Nature Climate Change*](https://www.nature.com/articles/s41558-022-01373-x)
- [Berk & van Binsbergen — The impact of impact investing. *Journal of Financial Economics* (2024)](https://www.sciencedirect.com/science/article/pii/S0304405X24001958)
- [Broccardo, Hart & Zingales — Exit versus Voice. *Journal of Political Economy* 130(12), 2022](https://www.journals.uchicago.edu/doi/abs/10.1086/720516)
- [Dimson, Karakaş & Li — Coordinated Engagements (ECGI Finance WP 721/2021, PDF)](https://www.ecgi.global/sites/default/files/working_papers/documents/dimsonkaracaslifinal.pdf)
- [EDHEC Climate Institute — Active Ownership as a Tool of Greenwashing](https://climateinstitute.edhec.edu/news/active-ownership-tool-greenwashing)
- [Silvia et al. — Do credible climate transition plans matter for carbon performance? *Frontiers in Environmental Science* (2026-08-10)](https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2026.1907357/full)
- [Planning to fail? Credibility and financing of corporate transition plans in hard-to-abate sectors. *iScience* (2026-06-08)](https://www.sciencedirect.com/science/article/pii/S2589004226016573)
- [Clarity AI — The Truth in the Budget: What Green CapEx Reveals About the Climate Transition](https://clarity.ai/research-and-insights/climate/the-truth-in-the-budget-what-green-capex-reveals-about-the-climate-transition/)
- [CDP — Technical note: Climate transition plans (PDF)](https://cdn.cdp.net/cdp-production/cms/guidance_docs/pdfs/000/003/101/original/CDP_technical_note_-_Climate_transition_plans.pdf)
- [OMFIF — Assessing transition plan credibility (2025-11)](https://www.omfif.org/2025/11/ensuring-a-credible-transition/)
