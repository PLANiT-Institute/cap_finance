# L3 — 전해조 학습곡선·수소 가격 위험 (CAP 9루프)

**범위**: CAP는 `h2_price = elec_price × 52 kWh/kg / 1000 + electrolyzer_capex × 0.12 / 150`
(`platform/engine/src/cap/calibration.py::hydrogen_price`, config.yaml:84-87)로 수소가를 구조식
파생하고, v2 캘리브레이션(`calibrate_v2`, calibration.py:83-128)은 `electrolyzer_decline=0.0`,
`electrolyzer_vol=0.0`을 **하드코딩**한다(line 116). v1 레거시 경로(`calibrate`, line 148-206)는
D4에 전해조 CAPEX 관측치가 3개 미만이면 `decline=0.05, vol=0.10`을 사전값으로 쓴다(line 189,
195). h2 자체의 GBM/OU 변동성 사전값은 `FALLBACK_VOL = {"h2": 0.25}`(line 48)이며, 코드 주석은
"h2 prior 0.25: between the gas-import benchmark (~0.3) and a contracted-supply view;
replace when a real clean-hydrogen price series exists"라고 명시한다 — 즉 근거 없는 자리표시자임을
스스로 인정한다.

---

## 확률적 학습곡선 (Way 2022)

- **[Way, R., Ives, M. C., Mealy, P. & Farmer, J. D. (2022), "Empirically grounded technology
  forecasts and the energy transition", *Joule* 6(9), 2057-2082 |
  https://doi.org/10.1016/j.joule.2022.08.009]** — 태양광·풍력·배터리·**전해조** 4개 기술에
  대해 라이트 법칙(Wright's Law)의 확률적 버전을 적용해 배치(deployment) 조건부 비용 예측을
  생성한다. 방법은 50개 이상 기술에 대한 백테스트로 통계적으로 검증됐다고 명시한다. 결론부는
  "태양광·풍력·배터리·전해조가 현재의 지수적 배치 증가 추세를 10년 더 유지하면 25년 내 탄소중립에
  근접한 에너지시스템에 도달할 수 있다"는 정책적 함의를 강조한다. **[미확인]**: 전해조 개별
  하락률·불확실성 밴드의 정확한 수치(중앙값 %/더블링, 신뢰구간 폭)는 원문(Joule/Cell Press,
  유료)과 INET 워킹페이퍼 PDF 모두 바이너리 추출 실패로 직접 확인하지 못했다. 원문 확인 없이
  구체적 하락률을 인용하지 않는다.
- 원문 접근 실패와 별개로, 이후 문헌(아래 CleanTechnica/CRU/TNO)이 인용하는 **경험적 학습률**은
  다음과 같다: **[CleanTechnica (2025.11.10), "Why Hydrogen Isn't Cutting Costs Like Solar or
  Batteries" | https://cleantechnica.com/2025/11/10/why-hydrogen-isnt-cutting-costs-like-solar-or-batteries/]**
  — PEM 전해조 학습률 12–15%, 알칼라인 10–15% (태양광 20–24%, 배터리 ~19% 대비 현저히 낮음).
  전해조는 "소량·현장맞춤 생산"이라 태양광·배터리의 "대량 표준화 생산"과 학습 메커니즘 자체가
  다르다고 설명한다.
- **[TNO/energy.nl (2022), "Projections of electrolyzer investment cost reduction through
  learning curve analysis" | https://energy.nl/wp-content/uploads/tno-2022-p10111_detzweeda_projections-of-electrolyzer-investment-cost-reduction-through-learning-curve-analysis.pdf]**
  — 검색 스니펫 기준 알칼라인 25.1%, PEM 36.4% 학습률을 보고한 사례도 있어 문헌 간 학습률
  추정치의 편차가 매우 크다(10%~36%). **[미확인, 원문 직접 접근 안 함]**.
- **[CleanTechnica (2026.09.05), "Hydrogen Learning Curves Are Counting The Wrong Doublings" |
  https://cleantechnica.com/2026/09/05/electrolyzer-learning-rates-plant-scale/]** — 2025년
  유럽 전해조 프로젝트 데이터의 원시 학습률(더블링당 전체 23.3%, PEM 32.1%, 알칼라인 22.9%)은
  플랜트 규모 경제 효과를 통제하면 각각 13.3%, 17.6%, 7.3%로 급락하고 알칼라인은 통계적 유의성을
  잃는다. 원인: (1) 100MW 플랜트가 1MW 플랜트의 100배 압축기·변압기를 필요로 하지 않는 설비
  스케일 효과, (2) 스택 단위 용량이 커지면 설치용량 더블링 횟수가 실제 제조 스택 생산 더블링
  횟수를 과대평가, (3) 스택은 설치 자본비의 15-20%에 불과하고(BOP 25-30%, 엔지니어링·시공이
  절반 이상) 스택 20% 원가 절감이 총 프로젝트 원가의 약 4%만 낮춘다는 시스템 경계 혼동. 결론:
  "전력이 변동비를 지배하며 제조 학습은 이를 소거할 수 없다."

**CAP의 "하락률 0"과의 배치**: v2의 `electrolyzer_decline=0.0` 하드코딩은 Way(2022)류의
낙관적 학습곡선(양의 하락률)과도, v1 프라이어(5%/년)와도 다르다. 더 중요한 문제는 이것이
"중립"이 아니라는 점이다 — 아래 절에서 보듯 2021-2024년 실현치는 오히려 **비용 상승**이었으므로,
0% 고정은 학습곡선 낙관 시나리오보다는 낮고 최근 실현 추세(상승)보다는 높은, 실증적으로
정당화되지 않는 중간값이다.

## 전해조 CAPEX 실제 경로·반등

- **[BNEF, "Electrolyzer Price Survey 2024: Rising Costs, Glitchy Tech" (2024), 인용:
  pv-magazine (2024.03.21) "Electrolyzer prices – what to expect" |
  https://www.pv-magazine.com/2024/03/21/electrolyzer-prices-what-to-expect/ ; 재인용 CRU/
  fuelcellchina 기사 | https://www.fuelcellchina.com/Industry_information_details/3725.html]**
  — 전해조 시스템 설치 자본비가 BNEF의 2022년 서베이가 예측한 "연 최대 10% 하락"과 반대로,
  **중앙값 57% 상승**했다. 원인: 서구권의 자재·유틸리티(전력·용수)·인건비 인플레이션, 보조금
  집행 지연에 따른 규모의 경제 미실현.
- **[BNEF/CRU 재인용, energycentral (2025), "China's Electrolyzer Cost Crash — What the LCOH
  Breakdown Actually Shows" |
  https://www.energycentral.com/energy-biz/post/china-s-electrolyzer-cost-crash----what-the-lcoh-breakdown-actually-shows-l1MezO36KAGP7tR]**
  — 2025년 기준 중국산 알칼라인 전해조 시스템 ≈$1.0M/MW, 서구권 ≈$2.0–2.5M/MW (서구가
  중국의 약 2–4배). 참고 LCOH 기준값 $3.50/kg 구성에서 전해조 CAPEX 15–35%, 재생 전력 60–70%.
- **[CRU Group (2025), "Electrolyser costs stall as green hydrogen reality sets in" |
  https://www.crugroup.com/en/communities/thought-leadership/2025/electrolyser-costs-stall-as-green-hydrogen-reality-sets-in/]**
  — CRU 자체 데이터베이스(중국 제외, 글로벌 200개 이상 프로젝트) 기준: 알칼라인 ≈$2M/MW(범위
  $1.9–3.0M/MW), PEM ≈$3M/MW, 최근 프로젝트 중앙값 $2.25M/MW. 2018–2020년 하락 후 코로나
  이후 정체, 2021–2022년 니켈·이리듐·백금·티타늄 등 핵심 소재 가격 급등으로 자본비 상승 압력,
  2022년 이후 "추세로 회귀"했으나 "하락 속도는 명백히 둔화". 원인 3가지: (1) 소재가 변동성,
  (2) "모듈형 함정" — 전해조가 소규모 유닛의 단순 반복 설치로 이뤄져 대형화 시 규모의 불경제
  발생, (3) 전해조 자본비는 그린수소 총 인도비용의 약 40%에 불과해 추가 절감의 총원가 영향이
  제한적. 사용자가 참조한 "CRU 2025 반등 +57%"는 이 CRU 기사 자체가 아니라 위 BNEF 서베이
  수치와 결합해 재인용된 것으로 보이며, CRU 자체 문구는 "정체(stall)"에 가깝고 "반등(rebound)"
  표현은 BNEF 쪽이 원출처다. **[구분 필요]**.
- **[CleanTechnica (2025.02.24), "Hydrogen Electrolysis Cost Projections from Major
  Organizations Low by 60% to 300%" |
  https://cleantechnica.com/2025/02/24/hydrogen-electrolysis-cost-projections-from-major-organizations-low-by-60-to-300/]**
  — IRENA·IEA·BNEF·Hydrogen Council·CSIRO·LUT의 2020년대 초 전해조 비용 전망이 실제치보다
  60–300% 낮게 예측됐다고 주장. 2024년 실제 전해조 시스템 비용 평균 $3,000/kW vs CSIRO가
  인용한 Aurecon 추정 $1,800/kW (약 67% 괴리). BNEF의 2050년 $1.60–5.09/kg 전망도 "여전히
  지나치게 낙관적"이라고 비판. 실패 원인으로 (a) 전해조 스택이 시스템 총원가의 20%에 불과해
  스택 학습률을 시스템 학습률로 확대 적용한 오류, (b) 압축·수송연결·저장·예비비 등 누락, (c)
  그린수소 물량이 블루/화이트수소에 잠식되면 규모의 경제 자체가 실현되지 않는 물량 가정 오류를
  지적.
- **결론**: 2020-24년 전해조 CAPEX는 코드가 가정하는 "0% 고정"도, Way(2022)류 학습곡선이
  함의하는 "지속 하락"도 아니다. 실현 경로는 **정체 또는 상승**(BNEF 중앙값 +57%, CRU
  "정체")이며, 유일한 뚜렷한 하락은 중국 공급망(저가 알칼라인, 서구 대비 2–4배 저가)에
  국한된다. 이는 지역적으로 완전히 다른 두 개의 비용 경로가 공존한다는 뜻이며, 단일 하락률로
  이를 대표할 수 없다.

## LCOH 불확실성 분해

- **[Global Hydrogen Hub 재인용 IEA, "Green hydrogen cost: reaching 4 €/kg by 2030 and 3 €/kg
  by 2050" | https://globalhydrogenhub.com/green-hydrogen-cost-reaching-4-e-kg-by-2030-and-3-e-kg-by-2050.html]**
  — IEA는 2030년 LCOH를 재생에너지원·전력 공급비용에 따라 €1.4–7.5/kg으로 폭넓게 전망(5배
  이상 범위).
  **[IEA/2030 $2/kg 목표 관련, 검색 스니펫]** — $2/kg 달성에는 전해조 CAPEX 반감, 재생전력
  <$20/MWh, 이용률 50% 이상이 조건으로 제시됨.
- **[ScienceDirect, "Cost-competitiveness of green hydrogen and its sensitivity to major
  financial and technical variables" (2024), *International Journal of Hydrogen Energy* |
  https://www.sciencedirect.com/science/article/pii/S0360319924042599]** — 재생에너지
  **이용률(capacity factor)**이 LCOH에 가장 큰 영향을 미치고, 그 다음이 재생 발전설비
  CAPEX/OPEX. 독일 태양광 기준 사례에서 전력가 ±25% 변동은 LCOH ±15%, 동일 폭의 CAPEX
  변동은 LCOH ±10.03% 변화를 유발. **[원문 직접 접근 실패(403), 검색 스니펫 기반 — 논문
  본문·표는 미확인]**.
- **일관된 정성적 결론(복수 출처 교차확인)**: 전력 접근성(가격×이용률)이 전해조 자체 성능·CAPEX
  보다 LCOH 분산을 더 많이 설명한다. 전기요금이 LCOH의 **57–87%**를 차지한다는 범위가
  여러 출처에서 반복 확인됨(검색 종합, 개별 논문 대조는 미실시): 그리드 연계 시스템은 전력비
  비중이 낮고(예: on-grid 44%), 오프그리드·전용 재생에너지 연계 시스템은 CAPEX/이용률 비중이
  커짐. 2050년 장기 전망에서는 자본비가 무시할 만큼 낮아져 "LCOH ≈ 전력가"에 수렴한다는 주장도
  있음(단일 출처, 미검증).
- **[energycentral 재인용 CRU/BNEF 데이터]** — 앞서 인용한 LCOH $3.50/kg 기준 분해: 전해조
  CAPEX 15–35%, 재생 전력 60–70%. CRU 자체 기사는 전해조 자본비가 "그린수소 총 인도비용의
  약 40%"라고 명시해 출처 간 15–40%의 편차가 있음 — 정의(시스템 CAPEX만 vs 시스템+BOP+설치
  포함)에 따라 다른 것으로 추정되나 **[정의 차이 미확인]**.

## 수소 가격 위험은 가격형인가

- 수소는 유동적 현물시장이 없다. 가격은 **장기 오프테이크 계약과 경매**로 결정된다.
- **[H2Global Foundation, "The H2Global Instrument" | https://h2-global.org/the-h2global-instrument/]**
  — Hintco가 생산자와의 장기 구매계약(HPA)과 수요자와의 단기 판매계약(HSA)을 동시에 경매하는
  이중경매(double-sided auction) 구조. 생산자는 장기 수익 확실성을, 구매자는 단기·유연 조달을
  원하는 계약기간 불일치(contract horizon mismatch)를 이 구조로 메운다.
- **[Oxford Institute for Energy Studies, "Hydrogen Offtake Agreements" (2025.08), ET50 |
  https://www.oxfordenergy.org/wpcms/wp-content/uploads/2025/08/ET50-Hydrogen-Offtake-Agreements.pdf
  (직접 접근 403, 검색 스니펫 기반)]** — "투명한 가격 벤치마크나 성숙한 거래 플랫폼이 없는
  시장에서, 오프테이크 계약이 가격 형성(price formation)의 기초 역할을 한다." 오프테이크 계약은
  미래 현물가가 계약가 아래로 떨어져도 구매자가 정해진 물량을 인수하도록 의무화 — "이는 성숙한
  수소 현물시장의 부재를 반영하며, 장기계약이 1차적 가격발견 메커니즘"이라고 명시.
- **[UK Hydrogen Production Business Model, OIES ET34/ET39 인용 |
  https://www.oxfordenergy.org/wpcms/wp-content/uploads/2024/04/ET34-Contracts-for-Difference.pdf]**
  — 영국의 첫 수소 CfD는 판매계약의 가중평균(achieved sales price)을 기준가로 사용하며, 이는
  "생산과 오프테이크 계약이 체결되면서 시간에 따라 가격발견이 이뤄지도록 유도하는" 설계 —
  즉 가격은 시장에서 사후적으로 관측되는 것이 아니라 정책설계가 유도하는 것.
- **CHPS(청정수소발전 입찰) 맥락**: CAP 코드 자체 주석(calibration.py:22)이 "no mature
  contract-price series exists yet (CHPS 낙찰가 비공개)"라고 명시 — 한국의 청정수소 경매
  낙찰가는 공개되지 않는다. 이는 국내 맥락에서도 수소가가 시장 발견형이 아니라 비공개 입찰·
  정책목표형임을 그대로 확인한다.
- **종합**: 수소 "가격 변동성"이라는 프레임 자체가 성립하지 않는다. 관측 가능한 것은 계약가
  협상 결과(오프테이크 단가, CfD 행사가, CHPS 낙찰가)이며 이는 정책목표(탄소중립 로드맵의
  청정수소 비중 목표, 보조금 예산)와 협상력(생산자 대 구매자, 정부 대 발전사)의 함수다. 확률
  분포로 모델링해야 할 대상은 "가격의 시장 변동성(σ)"이 아니라 "계약가가 어느 밴드에서
  타결될지"와 "낙찰물량·시점이 계획 대비 지연될지"이며, 이는 CAP가 이미 다루는 **정책 지연·
  물량 위험**의 범주에 더 가깝다.
- **CAP의 h2 σ=0.25 사전값과의 연결**: `FALLBACK_VOL["h2"]=0.25`는 코드 주석상 "가스 수입
  벤치마크(~0.3)와 계약공급 관점의 중간"이라는 자체 설명 외에 문헌적 근거가 없다. 위 종합에
  따르면 애초에 "GBM형 연율 변동성"으로 표현할 대상이 아니므로, 25%라는 특정 숫자의 타당성
  여부를 따지기 전에 **분포 형태 자체가 잘못 설정**되어 있을 가능성이 높다. (다행히 v2
  캘리브레이션은 이미 h2를 독립 인자에서 제외하고 전력에서 구조적으로 파생시켜 이 문제를
  우회했다 — 아래 구조식 검증 참조.)

## CAP 구조식 검증

- CAP의 `hydrogen_price = elec_price × 52/1000 + electrolyzer_capex × 0.12/150`
  (calibration.py:209-217)는 수소가를 전력가와 전해조 CAPEX의 선형 함수로 파생한다. v2
  캘리브레이션 주석(calibration.py:57-59)은 이를 명시적으로 정당화: "Hydrogen is NOT an
  independent factor... its shock is derived structurally from electricity through the
  electricity share of the hydrogen cost."
- **문헌과의 정합성**: 위 "LCOH 불확실성 분해" 절에서 확인했듯 전력가(×이용률)가 LCOH 분산의
  지배 요인이며, 여러 출처가 전력비중 57–87%를 보고한다. CAP가 수소 위험을 독립 추정하지 않고
  전력에서 파생시키는 것은 **방향은 문헌과 일치**한다.
- **간극 1 — 전해조 CAPEX 항의 처리**: 구조식은 전력항 + 전해조 CAPEX항의 합이지만, v2
  캘리브레이션은 전해조 CAPEX 자체를 `decline=0, vol=0`으로 고정해 사실상 **결정론적 상수**로
  만든다(calibration.py:116). 이는 구조식의 두 번째 항을 사실상 죽이는 것과 같다 — 전해조
  CAPEX가 LCOH의 15-40%를 차지한다는 문헌(위 절)에 비춰보면, 이 항의 변동을 완전히 제거하는
  것은 과소평가다. 특히 2021-24년 실현 경로가 상승(BNEF +57%)이었다는 점에서, "0% 고정"은
  최근 추세와 반대 방향으로 편향돼 있다.
- **간극 2 — h2_elec_share 계산의 데이터 의존성**: e3_prices.py:98-107은 D2b의 h2_price/
  elec_price 쌍에서 전력 비중을 역산한다(`share = elec_cost_per_kg / h2_price`, 0-1로
  clip). 이 비중이 문헌이 보고하는 57-87% 범위 안에 있는지는 실제 D2b 데이터를 열어봐야
  확인 가능하다 — 코드 로직 자체는 문헌과 같은 방향이지만, 산출된 숫자가 그 범위 안에 드는지는
  **[이번 조사 범위 밖, 별도 확인 필요]**.
- **간극 3 — 위험의 성격 오분류**: 앞 절 결론대로 수소가는 계약가·정책목표형이므로, 설사
  전력항이 정확히 파생되더라도 "전해조 CAPEX 변동"을 GBM형 연속 확률변수로 모델링하는 것
  자체가 현실과 괴리될 수 있다. 전해조 CAPEX는 (a) 소재가 변동성(니켈·이리듐 등 상품시장
  연동, 연속형에 가까움)과 (b) 중국 대 서구 공급망 선택이라는 이산적 정책/조달 결정이 혼재된
  위험이다. 후자는 확률분포보다 시나리오 분기(중국산 조달 허용 여부, 관세, 원산지 규정)로
  표현하는 편이 더 적절할 수 있다.

## 분포에 반영할 함의

1. **전해조 CAPEX를 상방·하방 모두 열어둔 확률변수로 바꾼다.** 현재 v2의 `decline=0, vol=0`
   하드코딩(calibration.py:116)은 "불확실성 없음"을 뜻하지 않고 "리스크를 구조적으로
   지운 것"이다. 최소한 v1 프라이어(decline 5%/vol 10%)를 v2에도 이식하거나, BNEF
   서베이의 연도별 실현 CAPEX(2018-2024, 하락 후 +57% 반등)로부터 직접 연율 변동성을
   추정해야 한다. 방향은 "0"이 아니라 "불확실 — 중국 공급망 확대 시 하락, 소재가·관세
   충격 시 상승"이라는 양방향 리스크다.
2. **h2를 독립 GBM 인자로 사전값(σ=0.25) 부여하는 방식은 폐기하는 것이 맞다** — v2가 이미
   그렇게 하고 있으므로 이 방향을 유지·강화한다. h2_elec_share 파생 로직(e3_prices.py:98-107)의
   산출값이 문헌 범위(57-87%)와 정합적인지 D2b 데이터로 검증하는 후속 작업이 필요하다.
3. **"가격 위험"과 "계약·정책 위험"을 분리해서 모델링한다.** CHPS 낙찰가 비공개, H2Global
   이중경매, UK CfD 사례 모두 수소가가 협상·정책 산출물임을 보여준다. 전력파생항(연속 확률
   변동)과 별개로, 수소 조달 자체의 **지연·미달 위험**(경매 유찰, 계약 재협상, 목표 축소)을
   CAP의 기존 "정책 지연" 축에 통합하는 것이 "가격형 σ"를 늘리는 것보다 구조적으로 타당하다.
4. **학습곡선을 낙관적 중심 시나리오로 쓰지 않는다.** Way(2022)류 확률적 학습곡선은 배치
   증가가 지속된다는 조건부 예측이며, 2021-2024년 실현치(BNEF +57%, CRU "정체")는 그
   조건이 최근 충족되지 않았음을 보여준다. 중심경로를 "학습곡선 하락"으로 잡을 근거가
   약하고, 오히려 최근 실현 추세(정체~상승)를 중심값에 가깝게 반영하고 상방(중국발 공급
   과잉 시 급락) 꼬리를 별도로 열어두는 비대칭 분포가 더 방어 가능하다.

## 미확인

- Way, Ives, Mealy & Farmer (2022, Joule)의 전해조 항목 구체적 수치(중앙값 하락률, 신뢰구간
  폭, 2030/2050 예측 구간): 원문(Cell Press, 403)과 INET/ORA PDF(바이너리 추출 실패) 모두
  접근하지 못해 정성적 방법론 설명 이상은 확인하지 못함.
- ScienceDirect "Cost-competitiveness of green hydrogen..." (S0360319924042599) 원문: 403으로
  차단, 검색엔진 스니펫만 확인. 표·회귀계수 등 세부 수치는 미검증.
- OIES ET50 "Hydrogen Offtake Agreements" (2025.08) 원문 PDF: 403, 검색 스니펫 기반 인용.
- IEA Global Hydrogen Review 2023/2024/2025 및 Assumptions Annex PDF: 접근은 했으나 바이너리
  추출 실패로 본문 텍스트를 읽지 못함. 전해조 CAPEX 공식 수치·2030/2050 전망 구간은 3자 재인용
  (CleanTechnica, energycentral, CRU)에 의존했으며 IEA 원문 대조는 못 했음.
- "CRU 2025 전해조 비용 정체·반등 +57%"라는 사용자 배경 진술: 조사 결과 **+57%는 BNEF
  Electrolyzer Price Survey 2024**의 수치이고, CRU 자체 발표(2025 "Electrolyser costs
  stall...")는 "정체(stall)"라는 표현을 쓸 뿐 57%라는 숫자를 직접 보도하는지는 원문 전체를
  확인하지 못해 **[출처 혼선 가능성 있음, 재확인 필요]**.
- 전해조 CAPEX가 LCOH에서 차지하는 비중: 출처별로 15-35%(energycentral/BNEF 재인용), 40%
  (CRU), 20%(스택만, CleanTechnica) 등으로 갈려 통일된 수치를 제시하지 못함 — 정의 범위
  (스택만 vs 시스템 vs 시스템+BOP+설치) 차이로 추정되나 각 출처 원문의 정의를 대조하지
  않았음.
- 중국 vs 서구 전해조 가격차의 근본 원인(인건비·공급망 성숙도 외에 품질·인증·수명 차이가
  총소유비용(TCO)에 미치는 영향): 이번 조사에서 다루지 않음.
