# L7 — 두 계보 결합 정식화: 헤지(포트폴리오·보험) × 선점(경쟁적 실물옵션)

날짜: 2026-09-13. 방법: WebSearch로 각 서지를 개별 확인, 초록/핵심 결과를 재확인. 추측 서지 없음 — 확인 안 된 항목은 마지막 절에 별도 표시.

## 경쟁적 실물옵션(ROG) 확인

- **Grenadier (2002)**, "Option Exercise Games: An Application to the Equilibrium Investment Strategies of Firms," *Review of Financial Studies* 15(3): 691–721. | https://academic.oup.com/rfs/article-abstract/15/3/691/1603237
  연속시간 Cournot–Nash 틀에서 경쟁 균형 행사전략을 도출. 핵심 결과: 경쟁이 "대기옵션"의 가치를 심하게 침식(erode)해 표준 실물옵션 모형이 예측하는 것보다 훨씬 이르게 투자하게 만든다. 모형은 수요충격에 대해 **위험중립 표준편이(risk-neutral drift)**를 명시적으로 가정 — 위험회피·헤지는 다루지 않는다(확인: WebSearch 결과 "assumes a risk-neutral drift").

- **Fudenberg & Tirole (1985)**, "Preemption and Rent Equalization in the Adoption of New Technology," *Review of Economic Studies* 52(3): 383–401. | https://academic.oup.com/restud/article-abstract/52/3/383/1521386
  기술채택의 타이밍 게임을 통해 선점 효과를 정식화. 복점에서 선점 위협이 지대를 균등화시킨다는 "지대균등화 원리"를 제시(일반 과점으로는 확장 안 됨). 확률과정·위험회피 요소 없음 — 결정론적 게임이론 정식화.

- **Smit & Trigeorgis (2004)**, *Strategic Investment: Real Options and Games*, Princeton University Press. | https://press.princeton.edu/books/hardcover/9780691010397/strategic-investment
  실물옵션 가치평가(복제포트폴리오/스패닝 가정 기반 위험중립 가치평가)와 게임이론(Cournot/Stackelberg)을 결합한 표준 교과서. "언제 선점 투자, 언제 대기"를 다루지만 가치평가 축은 여전히 위험중립 옵션가격 틀 — 위험회피 의사결정자의 효용함수는 다루지 않음.

**판정**: ROG 계보 3건 모두 확인됨. 셋 다 경쟁·선점이 대기옵션을 침식한다는 동일 메커니즘을 다루지만, **위험중립 가정** 위에서 구축되어 있다. 위험회피·헤지는 이 계보의 정식화 대상이 아니다.

## 위험회피 실물옵션

- **Henderson (2007)**, "Valuing the Option to Invest in an Incomplete Market," *Mathematics and Financial Economics* 1(2): 103–128. | https://link.springer.com/article/10.1007/s11579-007-0005-z
  위험회피적 1인 의사결정자(entrepreneur)가 불완전시장에서 투자옵션을 보유. 페이오프의 일부는 헤지 가능(traded asset과 상관), 나머지는 헤지 불가능한 특이위험(idiosyncratic risk). 핵심 결과: **위험회피와 특이위험이 옵션가치를 침식하고 투자문턱을 낮춘다**(= 더 일찍 투자) — 완전시장·불완전시장 모형이 서로 다른 투자 신호를 주는 파라미터 영역이 존재.

- **Miao & Wang (2007)**, "Investment, Consumption, and Hedging under Incomplete Markets," *Journal of Financial Economics* 86(3): 608–642. | https://www.sciencedirect.com/science/article/abs/pii/S0304405X07001225 (NBER WP 13250: https://www.nber.org/system/files/working_papers/w13250/w13250.pdf)
  기업가의 사업투자·소비/저축·포트폴리오 선택을 결합. 시장포트폴리오로 체계적 위험은 CAPM식으로 헤지, 특이변동성은 사모지분 프리미엄을 발생. 핵심 결과: **일시불(lump-sum) 페이오프인 경우 위험회피가 투자를 가속**(대기옵션 침식과 방향이 같음). 단, 흐름(flow) 페이오프인 경우 위험회피는 "2차 효과로 투자를 지연"시킨다고 명시 — 방향이 페이오프 구조에 의존.

- **Chronopoulos, De Reyck & Siddiqui (2014)**, "Duopolistic Competition under Risk Aversion and Uncertainty," *European Journal of Operational Research* 236(2): 643–656. DOI 10.1016/j.ejor.2014.01.018. | https://www.sciencedirect.com/science/article/pii/S0377221714000393
  (이 논문은 "결합 선행 탐색" 절에서 핵심적으로 다시 다룸.) CARA류 효용함수를 사용해 독점자·복점 리더/팔로워의 진입시점을 분석. 핵심 결과: **독점자는 가격불확실성과 위험회피가 커질수록 진입을 지연**한다(Henderson/Miao-Wang의 가속 결과와 반대 방향 — 흐름형 페이오프·경쟁 없는 구조이기 때문으로 추정, 원문 방법론 상세는 페이월 뒤라 미확인). 반면 위험중립 하에서는 경쟁자의 존재가 진입을 앞당긴다는 표준 결과가 유지되되, **위험회피 하에서는 경쟁유형에 따라 기업가치·진입결정이 다르게 움직인다**.

- 참고(근접 사례, 게임 아님): "Risk neutral and risk averse approaches to multistage renewable investment planning under uncertainty," *European Journal of Operational Research* (2015년 10월), DOI 확인 불가(페이월) | https://www.sciencedirect.com/science/article/abs/pii/S0377221715009200 — 재생에너지 다단계 계획에 **CVaR을 명시적 위험척도**로 넣은 확률계획(SDDP) 모형. CAP의 (기대비용, ES) 평면과 방법론적으로 가장 가깝다. 그러나 이는 **단일 의사결정자** 문제로, 경쟁·선점 요소는 전혀 없음.

**판정**: 위험회피 실물옵션 문헌은 확인됨. 다만 (i) 위험회피의 방향(가속 vs 지연)이 페이오프 구조(일시불 vs 흐름)와 경쟁유무에 따라 갈린다는 점, (ii) CVaR/ES를 명시적으로 쓴 문헌은 경쟁 없는 단일주체 계획모형에 머문다는 점이 확인됨.

## 두 계보 결합 선행 탐색 (공백 판정)

검색 쿼리: "competitive real options with hedging", "preemption and risk aversion", "real options game risk averse", "duopolistic competition risk aversion uncertainty" 등.

**결합을 시도한 논문이 존재한다**: Chronopoulos, De Reyck & Siddiqui (2014, EJOR) — 복점 경쟁(선점·리더-팔로워 구조)과 위험회피(CARA류 효용)를 **같은 모형 안에** 넣은, 확인된 범위에서 유일한 논문이다. 2025년 리뷰 논문("Investments under strategic competition and uncertainty: A literature review on real option games," *Computers & Operations Research*, 2026년판, 1991–2025년 230편 이상 검토)도 위험회피를 다룬 최근 연구가 "표준 사례에 새로운 직관을 제공한다"고 언급하며 이 결합을 하나의 하위주제로 인정한다. | https://www.sciencedirect.com/science/article/abs/pii/S0305054825003570

**그러나 이것이 CAP이 필요로 하는 결합은 아니다.** 이유 세 가지, 모두 확인 가능한 차이:

1. **위험회피의 형태가 다르다.** Chronopoulos et al.은 표준 기대효용(CARA) 위험회피 — "가격이 불확실하면 위험회피자는 더 신중해진다"는 일반론이다. CAP이 필요로 하는 것은 그게 아니라 **포트폴리오·보험 문헌(Awerbuch 계보)의 특정 헤지 논리**: "무전환 시나리오(꼬리)에 노출된 자산과 상관이 낮은/역상관인 자산에 조기 투자하면, 특정 나쁜 상태의 손실을 상쇄한다"는 **상태-조건부 상쇄** 논리다. 일반 CARA 위험회피는 어떤 나쁜 상태를 상쇄하는지 특정하지 않는다.
2. **선점의 형태가 다르다.** Chronopoulos et al.의 "경쟁"은 가격/수요를 같이 쓰는 복점자 간의 표준 Cournot/Stackelberg 경쟁이다. CAP이 필요로 하는 "선점"은 **접근형 자원의 물리적 배급**(계통연계 슬롯, 원료·용량 계약, 부지)이 시간이 갈수록 소진되어 늦은 진입자의 페이오프 자체가 악화(물량 배급 실패·프리미엄 상승)되는 형태 — 이는 Grenadier식 "옵션가치 침식"이 아니라 **페이오프 분포 자체의 이동**이다.
3. **결합의 목적이 다르다.** Chronopoulos et al.은 "위험회피가 경쟁균형에 어떤 영향을 주는가"라는 비교정학 질문에 답한다. CAP이 필요로 하는 것은 "두 개의 독립된 메커니즘(헤지 절감 + 선점 페이오프 악화)이 하나의 ES 위험효율 프론티어 위에서 조기 전환을 비지배로 만드는 결합 조건"이라는 **평가 프레임워크** 질문이다.

**공백 판정**: (a) 헤지·보험 논리(상태-조건부 꼬리 위험 상쇄)와 (b) 접근형 자원 선점(페이오프 분포 이동)을 **하나의 몬테카를로/ES 분포 생성기 안에서** 결합해 조기 전환의 비지배 조건을 도출한 논문은 확인되지 않았다. Chronopoulos et al. (2014)이 "위험회피 + 경쟁"을 결합한 가장 근접한 선행연구지만, 두 메커니즘의 정의 자체가 CAP이 쓰려는 것과 다르다. 이 지점은 공백으로 판정한다 — 단, "아무도 위험회피와 경쟁을 같이 안 봤다"는 강한 주장은 틀렸고(Chronopoulos et al.이 반례), "아무도 이 두 *특정* 메커니즘(상태조건부 헤지 + 물리적 배급형 선점)을 결합 안 했다"는 좁은 주장만 정당화된다.

## CAP 정식화 방향

CAP은 계획을 (기대비용, ES) 평면 위 점으로 평가한다(MILP + 몬테카를로). 두 메커니즘을 이 분포 생성기 안에 넣는 방법:

- **(a) 헤지 효과 — 시나리오 조건부 페이오프 상쇄.** 몬테카를로 시나리오 집합에 "무전환 지속" 상태를 포함시키고(예: 탄소가격 정체·기술비용 정체 결합 시나리오), 조기 전환 계획이 그 상태에서 노출을 얼마나 줄이는지를 비용분포의 좌측 꼬리(ES) 계산에 직접 반영한다. 이건 이미 CAP의 표준 몬테카를로 구조와 정합적 — 새 메커니즘이 아니라 **시나리오 설계**(무전환 꼬리를 실제로 나쁜 상태로 파라미터화)의 문제다.
- **(b) 선점 효과 — 시간에 따라 악화되는 페이오프 함수.** 접근형 자원(계통연계·원료계약 등)에 "늦게 신청할수록 물량 배급 실패확률↑, 남은 물량의 단가↑"라는 **시간의존 페널티 함수**를 투자 페이오프에 직접 곱/가산한다. 이는 MILP의 제약식이나 목적함수 계수를 전환시점 t의 함수로 만드는 것으로 구현 가능 — 새로운 확률변수가 아니라 **결정론적 시간의존 계수**로 들어간다(선점은 "몇 번째로 도착했는가"의 함수이지 확률변수 자체가 아니기 때문).
- **비지배 조건의 형태**: 조기 전환 계획이 ES 프론티어에서 비지배가 되려면, "(a) 무전환 꼬리에서의 비용 절감분"이 "(b) 조기 전환 자체의 초기 자본비용 증가분"을 상쇄하고도 남아야 한다 — 이는 표준 평균-분산/ES 프론티어의 비지배 조건과 동일한 형태(기대비용 증가 ≤ ES 개선의 그림자가격)이며, 특별히 새로운 수학이 필요하지 않다. **novelty는 조건의 형태가 아니라, (a)와 (b)가 서로 다른 채널(상태-조건부 vs 시간-조건부)에서 같은 방향(조기 전환 유리)으로 프론티어를 이동시킨다는 것을 같은 분포 생성기 안에서 명시적으로 분리해 보여준다는 데 있다.**

## 검증 부담·이중계상

리뷰어 질문: "헤지 효과와 선점 효과를 같이 넣으면 같은 것을 두 번 세는 것 아닌가?"

최소 방어선:
1. **직교성 논증**: (a)는 *상태*(어느 시나리오가 실현되는가)의 함수, (b)는 *시간*(언제 투자했는가)의 함수다. 하나의 시뮬레이션 경로 안에서 이 둘은 서로 다른 축에 작용 — (a)를 끄고 (b)만 켠 소거실험, (b)를 끄고 (a)만 켠 소거실험을 각각 돌려서 ES 프론티어 이동폭을 분해(decomposition)해 보이면, 합이 전체효과와 같은지(가법성) 아니면 상호작용항이 있는지 수치로 확인 가능 — 이중계상 여부는 주장이 아니라 **소거실험으로 답해야 하는 실증 질문**으로 전환된다.
2. **메커니즘 스위치 테스트**: 접근형 자원이 전혀 배급되지 않는(무제한 계통연계) 반사실 케이스를 돌리면 (b)가 0이 되어야 하고, 무전환 시나리오의 발생확률을 0으로 놓으면 (a)가 0이 되어야 한다. 두 스위치가 서로 독립적으로 꺼지는지 확인하는 것이 이중계상 부재의 최소 충분조건이다.
3. Chronopoulos et al. (2014)이 보여준 것처럼 위험회피와 경쟁의 상호작용은 "단순 가산이 아니다"라는 것이 이미 문헌에서 확인된 사실이므로, CAP도 처음부터 "두 효과가 가법적"이라고 주장하지 말고 분해실험 결과를 그대로 보고하는 것이 안전하다.

## 미확인

- Chronopoulos, De Reyck & Siddiqui (2014)의 **정확한 모형 구조**(CARA 정확한 함수형, 흐름 vs 일시불 페이오프 여부, 몇 단계 게임인지)는 EJOR 본문이 페이월 뒤에 있어 초록·인용 수준까지만 확인. 원문 전체 열람 필요.
- "Risk neutral and risk averse approaches to multistage renewable investment planning" (EJOR, 2015)의 저자명·정확한 권호수는 확인하지 못함(ScienceDirect 접근 차단, 검색결과 요약만 확인). 인용 시 원문 확인 필요.
- 계통연계 대기열/접근형 자원 선점을 실물옵션으로 정식화한 **동료심사 학술논문**은 검색에서 찾지 못함 — 검색된 자료는 업계 보고서·뉴스(marketscale.com, utilitydive.com 등)뿐이며 학술 문헌으로 인용 불가. 이 부분(선점을 "물량배급+프리미엄"으로 정식화하는 것)은 문헌이 아니라 CAP 자체의 모델링 제안으로 남겨야 함.
