# L7 — 분포 위 헤지 전략의 정식화 (CAP 8루프, 종합 단계)

전제(L1~L6 이어받음, 새 문헌 조사 최소): 전환비용은 MILP(일정)+MC(가격경로 1만)로 만든 하나의 분포
C(x)다. 두 꼬리 — 상방(CAPEX·에너지, 짓는 돈)·하방(탄소 붕괴·좌초, 버는 돈) — 는 서로 다른 확률변수에서
오고(L1·L2), 세 주체(기업·투자자·정부)가 blended finance/재보험 layering 언어로 서로 다른 층을 진다
(L3~L6). 본 루프는 새 이론·새 측도·새 정리를 만들지 않는다. 기존 CVaR 헤지·포트폴리오 문헌 위에
이 분포를 얹어 표기만 정확히 한다. WebSearch는 아래 두 건(평균-CVaR 효율 프론티어 표준, 최소분산
헤지비율 표준)만 최소로 썼고, 나머지는 L1~L6가 이미 확인한 문헌을 재사용한다.

---

## 평균-CVaR 효율 헤지(표준)

**CVaR 최적화의 원 정식화.** Rockafellar & Uryasev는 손실분포의 CVaR(=Expected Shortfall)를
볼록 함수로 표현해 선형계획법으로 최적화할 수 있음을 보였다 — CVaR_α(x) = min_η F_α(x,η), F_α는
η와 초과손실의 가중합으로 정의되는 볼록함수. 옵션 포트폴리오 헤지 사례를 포함해, 여러 헤지 수단에
대한 CVaR 최소화·제약이 동시에 볼록 최적화 문제로 풀린다는 것을 원 논문에서 이미 보였다.
[Rockafellar, R.T. & Uryasev, S. (2000), "Optimization of Conditional Value-at-Risk", *Journal of
Risk* 3, 21–41 | https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf]

**평균-CVaR 효율 프론티어.** 이 볼록성을 포트폴리오 선택으로 확장해, (기대손실, CVaR) 평면에서
효율 프론티어를 도출하고 복수의 CVaR 제약(서로 다른 신뢰수준 α에서)을 동시에 부과할 수 있는 선형
계획 정식화를 제시했다. 평균-분산 프론티어(Markowitz)의 CVaR판이며, 여러 신뢰수준의 CVaR를 동시에
제약할 수 있다는 점이 이번 8루프의 "상방 CVaR·하방 CVaR 동시 관리"와 구조적으로 맞닿는다.
[Krokhmal, P., Palmquist, J. & Uryasev, S. (2002), "Portfolio Optimization with Conditional
Value-at-Risk Objective and Constraints", *Journal of Risk* 4(2), 43–68 |
https://www.researchgate.net/publication/228751792]

**CAP이 이 자리에 얹는 것.** CAP의 (기대 전환비용 E[C], TCaR_α(C)) 쌍은 정확히 이 프론티어의 한
점이다. 헤지 수단(EPC/GMP 캡·PPA·오프테이크·CCfD)의 조합 h = (h₁,…,h_k)를 바꿔가며 이 프론티어를
그리면, "얼마를 더 헤지하면 기대비용이 얼마나 오르고 TCaR이 얼마나 내려가는가"의 트레이드오프를
전환비용 분포 위에서 처음으로 숫자로 보여준다 — 새 방법이 아니라 이 표준 프론티어에 철강·석화
한·일 케이스의 숫자를 채우는 것.

**완전 헤지가 최적이 아닌 이유 — 부분헤지 h*<1 (표준).** 최소분산 헤지비율의 고전적 결과: h* =
ρ·(σ_S/σ_F). 스팟-선물 상관 ρ<1(베이시스 위험)이면 h*<1이 최적이며, 헤지에 비용이 들면(거래비용·
프리미엄) 그 자체로도 완전 헤지에서 h*를 더 낮춘다. 헤지 기간이 길수록(전환 프로젝트처럼 다년도)
헤지 유연성이 줄어 최적 h*가 더 낮아진다는 것도 표준 결과다.
[Ederington, L.H. (1979), "The Hedging Performance of the New Futures Markets", *Journal of
Finance* 34(1), 157–170]

**CVaR-최소 헤지와 분산-최소 헤지가 갈라지는 조건 — CAP이 정확히 그 조건에 해당.** 정규분포·타원형
분포 가정 하에서는 CVaR 최소 헤지와 최소분산 헤지가 일치한다. 수익률(비용) 분포가 비타원형 —
두꺼운 꼬리·비대칭 — 이면 둘은 뚜렷이 갈라지고, 특히 국면전환(공동 폭락) 시나리오가 있으면 CVaR
최소 헤지 비율이 최소분산 헤지 비율보다 커진다.
[Mannheim Working Paper Series (MADOC), "VaR- and CVaR-minimal Futures Hedging Strategies" |
https://madoc.bib.uni-mannheim.de/31097/1/mm186.pdf]

L2가 이미 확인했듯 CAP의 전환비용 분포는 비타원형이다 — 상방은 멱함수 팻테일(FOAK 초과율), 하방은
이산적 좌초(ArcelorMittal형). 즉 CAP은 "최소분산 헤지로는 안 되고 CVaR 헤지가 필요한" 표준 조건에
해당하는 사례이지, 새 조건을 만드는 것이 아니다.

---

## 두 꼬리 조합 최적화·페이오프 변환

**페이오프 변환 = 헤지 수단의 공통 언어(DIRECTION.md 재확인).** 정본 방향 문서가 이미 정의한
v(S) = ES₉₀(C) − ES₉₀(T_S(C)), T ∈ {부분고정, 상수차감, 하방절단, 차액정산, 상방캡}이 이번 8루프가
L1~L6에서 확인한 개별 수단들의 페이오프를 통합하는 표기다. 각 수단은 이 다섯 변환 중 하나(또는
조합)로 정확히 쓰인다:

| 수단 | 변환 T_S | 자르는 부분 | 근거(L1~L6에서 이미 확인) |
|---|---|---|---|
| EPC 고정가/GMP 캡 | 상방캡(cap) | 상방 꼬리(비용초과) | L1·L3 — LexisNexis EPC/Turnkey; Wikipedia lump-sum turnkey |
| PPA(전력가 고정) | 부분고정 | 몸통(에너지 투입비 변동성) | L3 — TotalEnergies; ENGIE |
| take-or-pay 오프테이크 | 상수차감(매출측) | 몸통~상방(순현금흐름 하방 받침) | L3 — GH2; H2 Green Steel 사례 |
| CCfD(양방향) | 차액정산+하방절단+상방캡 | 하방 꼬리 정밀 절단 + 상방 초과이익 환수 | L5 — Richstein & Neuhoff (2022), *iScience*; 독일 KSV |
| 가격하한(영국 CPF) | 하방절단(풋) | 하방 꼬리만 | L5 — House of Commons Library |
| 가격밴드(일본 GX-ETS) | 하방절단+상방캡 = 칼라 | 상방·하방 동시(시장 전체 수준) | L5 — ICAP; METI/UNFCCC |
| ECA·공적보증 | 상수차감(신용) | 상방 신용 꼬리 | L4 — RMI; Impact Investor(H2 Green Steel) |

CCfD와 GX-ETS 밴드가 둘 다 **칼라(collar)** — 하한에서 풋 매도, 상한에서 콜 매도의 조합 — 라는 것은
L5·L6에서 이미 옵션 유비로 확인했다. 칼라는 "두 개의 단방향 변환(하방절단+상방캡)을 한 계약에
합성한 것"이므로, 아래 조합 최적화의 가장 단순한 예다 — CCfD는 프로젝트 단위, GX-ETS 밴드는 시장
전체 수준이라는 것이 유일한 차이(L5).

**조합 최적화가 볼록 문제로 남는 이유.** CVaR은 코히런트(coherent) 리스크 척도이자 볼록함수이므로,
여러 헤지 수단(파생상품·계약 조합)에 대한 최적화도 볼록 최적화로 풀린다 — 이는 Rockafellar-Uryasev
(2000) 원 논문이 이미 옵션 포트폴리오 사례로 보인 성질이며, Krokhmal-Palmquist-Uryasev(2002)가
복수의 CVaR 제약(서로 다른 신뢰수준)을 동시에 부과하는 선형계획 정식화로 확장했다. 따라서 "상방
TCaR를 EPC/GMP로, 하방 TCaR를 CCfD로" 두 개의 서로 다른 수단·서로 다른 꼬리를 동시에 최적화하는
문제는 목적함수를 min E[C(h)] + λ_up·TCaR_up,α(C(h)) + λ_down·TCaR_down,α(C(h))로 두면 정확히
이 틀 — 새 최적화 이론이 아니라 기존 다중-CVaR 제약 정식화에 CAP의 두 꼬리를 대입한 것.

**왜 두 꼬리를 하나의 수단으로 못 묶나 (L1·L2 재확인).** 상방은 CAPEX·에너지가(짓는 돈), 하방은
탄소가·정책신뢰(버는 돈) — 서로 다른 확률변수에서 온다(L1). 대칭 분산 헤지(단일 변동성 축소 수단)
하나로 두 꼬리를 동시에 줄이려는 문헌은 이번 검색에서 확인되지 않았다(L1_shape 미확인 4번) — 이는
결함이 아니라, 두 꼬리가 서로 다른 리스크 요인에서 오므로 애초에 단일 대칭 수단으로 묶을 이론적
근거가 없다는 뜻이다. 조합 최적화(상방 수단 + 하방 수단, 각각 다른 λ)가 자연스러운 정식화이지,
단일 수단으로 대체할 수 있는 것을 CAP이 일부러 복잡하게 만든 것이 아니다.

**재보험 layering과의 대응 (L6 재사용).** 고빈도·저심도는 보유(retention, 기업 몸통), 저빈도·고심도는
이전(excess-of-loss, 정부 하방 catastrophe)이라는 재해리스크금융 표준 원칙이 CAP의 두 꼬리와 정확히
대응한다는 것을 L6이 이미 확인했다. 조합 최적화는 이 표준 원칙을 "누가 얼마나 지는가"의 정성적
서술에서 "각 층의 절단점·크기를 원화로 얼마"의 정량 문제로 바꾸는 것 — layering 개념 자체를 새로
제안하는 것이 아니다.
[Adaptation Community/World Bank, "Climate and Disaster Risk Finance and Insurance" |
https://www.adaptationcommunity.net/climate-disaster-risk-finance-insurance/]
[Fu, L. & Khury, C.K.S., "Optimal Layers for Catastrophe Reinsurance", *Variance* |
https://variancejournal.org/article/141998-optimal-layers-for-catastrophe-reinsurance.pdf]

---

## TCaR 안착(Climate VaR 계보 한 줄)

**한 문장(사용자 확정, L3 SYNTHESIS 재확인).**
> TCaR는 새 위험측도가 아니라, expected shortfall을 기업 전환비용 분포에 적용해 Climate VaR·Carbon
> VaR 계보를 잇는 것이다.

**계보.** ES/CVaR 원 정식화(Rockafellar-Uryasev 2000) → 포트폴리오 전체 가치에 적용한 Climate VaR
원조(Dietz, Bowen, Dixon & Gradwell 2016, business-as-usual 경로에서 전 세계 금융자산 기대손실
1.8%) → 기관투자자 실무화(MSCI Climate VaR, WTW Climate Transition VaR — 상장기업 1만개+·국채
9천개+ 커버, 향후 50년 탈탄소화 비용을 시나리오 가정으로 현금흐름에 반영) → **TCaR(본 연구, 기업
전환비용 분포에 적용, 두 꼬리로 분해)**.
[Dietz, S., Bowen, A., Dixon, C. & Gradwell, P. (2016), "'Climate value at risk' of global financial
assets", *Nature Climate Change* 6, 676–679 | https://www.nature.com/articles/nclimate2972]
[MSCI, "Understanding the Drivers of Transition-Risk Climate VaR" |
https://www.msci.com/research-and-insights/blog-post/understanding-the-drivers-of-transition-risk-climate-var]

**정의 — 두 꼬리로 분해.**
- 상방 TCaR_α(C) = ES_α(C) = E[C | C ≥ VaR_α(C)] — 전환비용 C의 상위 (1−α) 구간 조건부 평균
  (비용 폭발·FOAK 초과 위험).
- 하방 TCaR_α(V) = ES_α(−V) — 전환 순가치 V(= 감축 편익 − 전환비용)의 하위 (1−α) 구간 조건부
  평균의 부호 반전(좌초 위험). 이는 "탄소가가 오르면 얼마나 위험에 노출되는가"를 묻는 통상 Carbon
  VaR의 거울상 — "탄소가가 오르지 않으면(정책이 후퇴하면) 이미 지은 감축설비의 순가치가 얼마나
  위험에 노출되는가"를 묻는다(L2_downtail).
  [Homaio, "Carbon VaR – Carbon Value at Risk Metric" | https://www.homaio.com/glossary/carbon-value-at-risk]

**왜 이 계보가 안 하는 것인가 (L4 재확인, 기여 지점).** Dietz(2016)→MSCI/WTW 계보는 전부 하향식
(top-down) — 포트폴리오·기업 단위의 시나리오 점추정(또는 그 가중평균)을 현금흐름 할인에 곧바로
반영한다. 개별 기업의 전환비용을 명시적 분포로 재구성하지 않는다. TCaR은 같은 문제의식(전환리스크의
VaR화)을 공유하되, MILP+MC로 만든 기업 단위 상향식(bottom-up) 연속분포에 ES를 적용하고 이를 두
꼬리로 분해한다는 점에서 다르다 — 이것이 이 계보에 대한 CAP의 기여 지점이며, 그 이상을 주장하지
않는다(L3·L4 SYNTHESIS의 "거창하게 가지 않는다" 규율).

---

## CAP 구현(계산 엔진)

L6 위험 배분 지도(표 1·2)를 만드는 계산 엔진을 파이프라인으로 정식화한다. 새 알고리즘이 아니라
L1~L6에서 이미 서술한 단계를 하나의 흐름으로 압축한다.

1. **일정 생성(MILP).** 시설 단위로 "언제 무엇을 설치하는가"의 다년도 전환 일정을 짠다(L1).
2. **가격경로 시뮬레이션(MC, 1만 회).** 에너지가·탄소가를 확률과정(현재: GBM: T1 통과 전엔 GBM/OU
   순위 미확정, DIRECTION.md 선행조건)으로 반복 추출.
3. **전환비용 분포 C(x) 산출.** 위 일정을 각 가격경로에 적용해 다년도 총비용(NPV)의 경험적 분포를
   얻는다 — 이것이 L1이 "선례 없음"이라 확인한 CAP의 자리다.
4. **층 경계 산정.** C(x)에서 몸통(중심 구간)·상방 꼬리(VaR_α 이상)·하방 꼬리(순가치 V(x)의
   VaR_α 이하)를 분위수로 절단.
5. **TCaR 산출.** 상방 TCaR_α(C), 하방 TCaR_α(V)를 원화로 계산 — 이것이 층 "크기"다(L6이 "기존
   layering은 정성적, CAP은 크기를 잰다"고 확인한 지점).
6. **수단별 페이오프 변환 적용.** 위 표의 T_S를 순서대로(또는 조합으로) C(x)에 적용해 v(S) =
   ES₉₀(C) − ES₉₀(T_S(C))를 계산 — 소거실험(아래)의 단위 연산.
7. **주체 배분.** 변환 후 잔여 분포를 재보험 layering 언어로 세 주체에 배정: 기업(보유, 몸통 +
   h*<1만큼의 상방 잔여) → 투자자(DSCR로 좁힌 구간, 상방 진입부) → 정부(하방 catastrophe, CCfD/
   밴드 가동 시) → 미가동이면 빈 tranche(한국 ②③, L6).

이 6~7단계가 L6 표 1·2를 만드는 엔진이며, 산출은 표 3처럼 요약된다.

| 산출 | 정의 | L6과의 대응 |
|---|---|---|
| 몸통 크기(원화) | C(x)의 IQR 또는 지정 중심구간 | 표1 "몸통" 행 |
| 상방 TCaR(원화) | ES_α(C) | 표1 "상방(비용폭발)" 행 |
| 하방 TCaR(원화) | ES_α(−V) | 표1 "하방(좌초)" 행 |
| 수단별 v(S) | ES₉₀(C) − ES₉₀(T_S(C)) | 각 수단이 자르는 크기 — 표 매핑 |
| 한국 빈 tranche 크기 | v(S)=0인 층(CCfD 미가동)의 TCaR | L6 "한국 꼬리 공백"의 원화 버전 |

**검증 — 소거실험과 λ 스윕(과장 없는 검증법).**
- **소거실험(수단 끄기).** 수단 집합에서 하나씩 제거(예: CCfD를 끈 C(x) vs 켠 C(x))하고 하방
  TCaR의 변화를 v(S)로 직접 읽는다 — 이는 CVaR이 코히런트·가법적으로 다룰 수 있는 척도라는 성질
  (Rockafellar-Uryasev 2000)에 기댄 것이지 새 검증법이 아니다.
- **λ 스윕(비교정학).** min E[C(h)] + λ_up·TCaR_up + λ_down·TCaR_down에서 λ_up, λ_down을
  바꿔가며 최적 h*(λ)의 경로를 추적 — 평균-CVaR 효율 프론티어(Krokhmal-Palmquist-Uryasev 2002)를
  그리는 표준 방법을 그대로 적용.
- 두 검증 모두 DIRECTION.md의 "선행조건 통과 후"(T1·T2·T3) 및 9루프 감사(cap-audit-2026-08-30)가
  요구한 소거실험·λ 스윕과 동일 — 이번 루프가 새로 만든 테스트가 아니라 이미 예정된 테스트를 이
  정식화 안에 정확히 위치시킨 것.

---

## 정직한 한계

1. **부분헤지·페이오프 변환·두 꼬리 ES 전부 기존 것이다.** 완전 헤지가 최적이 아니라는 것(Ederington
   1979), CVaR을 볼록 최적화로 다루는 것(Rockafellar-Uryasev 2000), 평균-CVaR 효율 프론티어
   (Krokhmal-Palmquist-Uryasev 2002), 재보험 layering(retention/insurance/excess-of-loss, 표준
   재해리스크금융 원칙), 칼라·CfD의 옵션 유비 — 이 여섯 개 중 CAP이 새로 만든 것은 없다. CAP이
   더하는 것은 이 여섯 개를 **한·일 철강·석화 전환비용 분포에 적용해 각 층 크기를 원화로 재는 것**
   뿐이다(L6 SYNTHESIS "CAP이 더하는 것" 그대로 재확인).
2. **새 정리 없음.** 다중 CVaR 제약 하의 볼록 최적화는 Krokhmal-Palmquist-Uryasev(2002)가 이미
   증명한 정리를 그대로 쓴다. CAP은 이 정리의 새 증명이나 일반화를 제시하지 않는다 — 입력(전환비용
   분포)을 바꿔 끼울 뿐이다.
3. **CAP은 처방 도구가 아니라 측정 도구다(L5·L6 규율 재확인).** "정부가 하방 catastrophe 층을
   얼마나 져야 하는가"는 CAP이 답할 수 없다 — Arrow-Lind의 독립성 조건이 이 위험(정책이 만드는
   내생적 위험)에는 성립하지 않고(L5_limits: Arrow & Lind 1970; Mechler & Hochrainer-Stigler 2014),
   CCfD 같은 자기보험 구조는 Kydland-Prescott(1977) 시간불일치 문제와 형태가 같다. L7이 줄 수 있는
   것은 조합 최적화의 **회계**(이 층 크기 X, 이 수단으로 자르면 v(S)만큼 준다)이지, 사회후생
   최적화가 아니다.
4. **분포 자체의 함정이 정식화 위에도 그대로 남는다.** GBM 24년 복리의 분산 과대(Schwartz 1997
   평균회귀 준거, L1), 상관 없는 몬테카를로의 분산 과소(PMI 실무 지적, L1), 상방(멱함수 팻테일)·
   하방(이산 좌초)의 분포족이 섹터마다 다르다는 것(L2) — 효율 프론티어·TCaR 수치 자체가 이 함정에
   민감하다. DIRECTION.md의 T1(GBM vs OU)·T2(요금 재보정)를 통과하기 전에는 본 정식화의 **수준**
   (원화 크기)은 잠정치로만 다뤄야 한다 — **방향**(어느 수단이 어느 꼬리를 자르는가의 부호·순서)은
   이번 정식화만으로도 견고하다.
5. **검증은 소거실험·λ 스윕뿐, 외부표본 백테스트 없음.** 전환비용 분포는 미래 가격경로의 몬테카를로
   산출물이라 실현치와 대조하는 표준 백테스트가 원천적으로 불가능하다 — 이는 CAP만의 한계가 아니라
   실물옵션·시나리오 기반 전환리스크 연구 전반의 공통 한계다(L1~L4에서 반복 확인).
6. **한·일 케이스의 실증 공백은 정식화가 못 메운다.** ECA가 EPC 비용초과 자체를 직접 커버하는지,
   한국 project-level PF가 실재하는지, CBAM의 한·일 기업별 정량 노출액 — 이 정식화가 만드는 v(S)·
   TCaR 계산은 이 공백들이 채워질 때까지 구조(수단→어느 꼬리)는 맞아도 계수(수단이 실제로 몇 %를
   자르는가)는 가정치에 의존한다(L4·L5·L6 미확인 항목 그대로 승계).

---

## 미확인

L1~L6에서 이월된 것 중 L7 정식화에 직접 걸리는 항목만 압축(전체 목록은 각 루프 파일의 "미확인" 절).

1. **CVaR 최소 헤지와 최소분산 헤지가 정확히 얼마나 갈라지는가(계수 수준)** — Mannheim WP는 방향
   (비타원형이면 갈라진다)만 확인, CAP의 두 꼬리 분포에 적용했을 때 구체적 h*_CVaR 대 h*_variance
   격차는 CAP 자체 시뮬레이션이 필요(외부 문헌에 없음).
2. **다중 CVaR 제약 정식화(Krokhmal-Palmquist-Uryasev 2002)의 원문 세부(정확한 제약식·해법)** —
   이번 WebSearch는 초록·요약 수준만 확인, 원문 PDF는 직접 열람하지 못함. 인용 전 원문 재확인 필요.
3. **복수 파생상품 조합의 CVaR 최소화(Yuying Li et al., Waterloo)** — L3_optimal에서 이미 서지만
   확인, 본문 미독으로 이월.
4. **"헤지가 무비용이면 완전 헤지가 항상 최적"이라는 명제의 1차 출처** — L3_optimal에서 이미
   확인 못함, 이번 루프도 재확인하지 못해 그대로 이월.
5. **전환비용에 CAT bond형 구조(자본시장의 직접적 꼬리 인수)를 적용한 선례** — L3_optimal·L6에서
   반복 확인 시도했으나 없음. 조합 최적화의 네 번째 층("자본시장 이전")은 CAP 케이스에서는 이론적
   가능성으로만 표기.
6. **"최적 첫손실(first-loss) 규모"를 도출하는 단일 정설 이론** — L5_limits에서 이미 확인 못함;
   L7의 층 경계(몸통-상방/하방 진입점)를 어느 분위수(α=90%? 95%?)로 잡을지의 규범적 근거는 CAP
   외부 문헌에 없고, CAP 자체의 정책·데이터 판단(참조집단·분위수 선택)에 의존함을 명시한다.

---

# SYNTHESIS L7 (분포 위 헤지 정식화) — 2026-09-13

## 방법을 어디에 얹는지 확정 (거창하지 않게)
- 평균-CVaR 효율 헤지(Rockafellar-Uryasev 2000 → Krokhmal 2002)에 CAP은 **사례**로 얹힌다.
- 부분 헤지 h*<1 표준(Ederington). **CVaR-최소가 분산-최소와 갈라지는 조건 = 팻테일·비대칭 = CAP의
  두 꼬리 분포가 정확히 그것.** CAP은 그 조건의 사례이지 새 발견 아님.
- TCaR 안착: Rockafellar-Uryasev → Dietz 2016 Climate VaR → MSCI/WTW → TCaR(상방 ES·하방 ES).
  유일 기여 = bottom-up 연속분포 + 두 꼬리 분해.

## 두 연구의 합류 (중요)
지난 9루프의 v(S)=ES(C)−ES(T_S(C))(수단별 페이오프 변환)와 이번 8루프의 두 꼬리·세 주체가 **같은
정식화로 만났다.** T∈{하방절단(CCfD·가격하한)·상방캡(EPC·보증)·칼라(CCfD·GX밴드)}가 L1~L6의 개별
수단을 통합하는 공통 표기. CVaR 볼록성 덕에 다수 수단·다수 신뢰수준 조합도 볼록 문제. 두 꼬리가
다른 확률변수(상방 CAPEX·에너지 / 하방 탄소·정책)라 단일 대칭 수단으로 못 묶음. 우연이 아니라 같은
대상(전환비용 분포)을 두 렌즈로 판 결과 — 두 연구가 한 논문으로 합쳐질 수 있다는 신호.

## CAP 계산 엔진 (L6 지도의 엔진)
MILP 일정 → MC 1만 경로 → 전환비용 분포 C(x) → 층 경계(분위수) → TCaR(상방/하방 원화) →
수단별 v(S) 적용 → 세 주체 배분(기업 보유·투자자 mezzanine·정부 catastrophe, 미가동=빈 tranche).
검증 = 소거실험(수단 끄기)·λ 스윕 — DIRECTION·9루프 감사와 동일 테스트.

## 정직한 한계 (재확인)
부분헤지·CVaR 볼록최적화·평균-CVaR 프론티어·재보험 layering·칼라 유비 전부 기존 것. CAP은 한·일
전환비용 분포에 적용해 층 크기를 원화로 재는 것뿐, 새 정리 없음. GBM 등 분포 함정은 **수준**에
영향, **방향**(어느 수단이 어느 꼬리)은 견고. 외부표본 백테스트 불가(미래 시나리오 산출물).

## 직전(L1~L6) 비판적 재검토
L1~L6이 판 것이 L7에서 하나의 정식화로 닫혔다 — 그리고 지난 9루프 v(S)와 합류했다. 이게 얹혀가기의
완성: 모든 수학이 남의 것(CVaR·부분헤지·layering·Climate VaR)이고, CAP은 그것들이 만나는 자리에
한·일 케이스를 놓는다. L8은 이 전부를 종합·설계·시각화로 착지.
