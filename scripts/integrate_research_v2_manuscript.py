"""Integrate the audited research revision; preserve the v1 snapshot and tables."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'paper/methodology/TCaR_METHOD_KO.md'
SNAPSHOT=ROOT/'paper/methodology/archive/TCaR_METHOD_KO_v1_20260905.md'


def main():
    if not SNAPSHOT.exists():
        SNAPSHOT.parent.mkdir(parents=True,exist_ok=True)
        SNAPSHOT.write_text(PAPER.read_text())
    text=SNAPSHOT.read_text()
    start=text.index('**연구 원고 v1.0')
    end=text.index('**주제어:')
    text=text[:start]+'''**연구 원고 v2.1 · 2026년 9월 7일.** 방법론·조건부 사례·기술 사양 및 가격분포의 재검증을 통합한 연구 원고. 6.1–6.7절은 v1의 동결 사례이고 6.8절은 별도의 사양 민감도 실행이다. 5.7–5.9절의 경험적 가격 모듈은 연구 후보로 구현했으며 기업 사례에 적용한 것으로 표시하지 않는다. 현재 자료로 실제 기업의 장기 꼬리가 식별됐거나 저널 제출 준비가 끝났다고 주장하지 않는다.

### 초록

기후 전환계획의 비용위험은 에너지가격뿐 아니라 감축기술의 공정 경계, 에너지 수요량과 조달 방식에 따라 달라진다. 본 연구는 동일 기업의 설비·계약 대안을 공통 회계 및 배출제약 아래 비교하는 Transition Cost at Risk(TCaR) 방법론을 제시한다. 시나리오 s, 공정 사양 θ와 조건부 가격충격 ε를 구분하고, 할인 증분비용의 상위 분위수와 중앙값 간격을 평균·Expected Shortfall(ES)과 함께 보고한다. 효율경계는 실제 평가한 이산 후보의 비지배 집합이다. 한국·일본 철강 및 석유화학 네 기업의 추정 자산 사례를 재현하고, 원 연구에 기초한 사양 대안 6건을 별도로 실행했다. 철강 전력 원단위 대안에서는 선택 기술의 집합이 유지돼도 TCaR가 약 14–30% 증가했고, 석화에서는 일부 선택 기술 집합이 달라졌다. 이는 대안 사양의 조건부 영향이며 실제 기업 위험의 확정적 정정치는 아니다. World Bank 월별 벤치마크의 회고 예측 검증에서는 변동성 갱신이 적합도를 개선해도 일부 가스계열의 상위 위험을 충분히 포착하지 못했다. 공통 블록 재표집과 정확한 기대가격 보정으로 5개 가격생성법을 구현해, 같은 기대가격에서도 꼬리가 달라짐을 보였다. 공정·시나리오 대응표, 원문 위치 및 해시, Excel 통제와 재현 검사를 연결한다. 핵심 기여는 새로운 위험측도의 우월성보다, 무엇이 관측됐고 무엇이 가정됐는지를 비용분포와 실행 가능한 선택까지 추적하는 방법에 있다.

'''+text[end:]
    lit='''### 2.1 2018년 이후 산업 공정 연구와 본 연구의 추가 검증 대상

Vogl et al. (2018)은 수소 직접환원·전기로·현장 수전해가 결합된 설계를 평가했다. 논문에 제시된 총전력 3.48MWh/t 액강은 수소 구매형 설비의 전력과 다르다. 스크랩 비율과 열회수 구성까지 고정해야 가격과 물량을 연결할 수 있다. Pimm et al. (2021)의 전력계통·수소 제철 연계 연구도 저장과 운영의 결합을 다룬다. 부속 파일에 반복 인용된 Vogl 계수는 독립 공학 관측으로 세지 않는다. [Vogl et al., 2018](https://doi.org/10.1016/j.jclepro.2018.08.279); [Pimm 연구 데이터](https://doi.org/10.5518/997).

Layritz et al. (2021)은 나프타 크래커 전기화와 CCU를 비교하며 REMIND의 에너지·배출 경로를 연결한다. 따라서 산업 공정과 IAM 시나리오의 연결 자체는 이미 선행연구가 있다. 본 연구는 기관 프리프린트의 공정 물량을 추출했으며 최종 출판본과의 전체 대응은 남아 있다. 전기화로 남는 내부 메탄의 처분과 판매가치를 가격위험에 연결하는 것이 해당 공정을 기업 현금비용으로 옮길 때의 핵심이다. [Layritz et al., 2021](https://doi.org/10.1016/j.apenergy.2021.117049).

Bachorz et al. (2025)은 산업별 감축 선택을 핵심 투입가격의 변화에 따라 비교하고 공개 데이터·코드 및 웹 도구를 제공한다. 가격 민감도 지도와 유용한 도구의 존재를 본 연구의 신규성 주장에 반영해야 한다. 본 연구가 추가로 검증할 대상은 공동 가격경로의 생성, 공정 사양의 불완전한 식별, 계약과 이산 설비결정을 합친 기업 내 선택 및 상위 비용분포다. 이 결합의 학술적 기여는 실증적 검증 수준에 달려 있다. [Bachorz et al., 2025](https://doi.org/10.1038/s41467-025-59277-1).

Zang et al. (2023)을 참조하는 공개 GCAM 기술계수는 철원료 및 환원가스 혼합을 명시한다. POSTED v0.4.0은 원 출처와 편집자 변환을 함께 추적하는 데 유용하지만, 데이터베이스에 실린 수치가 자동으로 독립 검증을 거친 것은 아니다. 원 저자의 비공개 설명이나 편집자 추정은 공개 원문 수치와 구분한다. [Zang et al., 2023](https://doi.org/10.1002/srin.202200297); [POSTED v0.4.0](https://doi.org/10.5281/zenodo.18155305).

이 검토는 공정·시나리오·계약·위험이라는 사용 목적에 따른 선별 검토다. 검색 누락이 없다는 체계적 문헌고찰이나 MC를 산업 전환에 처음 사용했다는 주장은 하지 않는다. 전문을 확보하지 못한 근접 연구는 접근 대기열에 보존하고 수치 채택의 근거로 쓰지 않는다.

'''
    text=text.replace('## 3. 측정 대상과 모형의 경계',lit+'## 3. 측정 대상과 모형의 경계',1)
    method='''### 5.7 시나리오와 충격분포를 연결하는 식별 규약

시나리오 경로가 정해져도 확률분포가 자동으로 주어지지는 않는다. 조건부 비용은 C(x; s, θ, ε)로 정의한다. s는 정책·장기 시장 및 생산 조건, θ는 공정·효율·수명·열통합 사양, ε는 그 조건 아래의 공동 충격이다. θ의 문헌 간 차이는 표본추출된 반복 관측이 아니므로 그 표준편차를 기술 불확실성으로 사용하지 않는다. 서로 다른 공정의 전력·수소·가스 최소값만 조립하는 것도 허용하지 않는다.

양의 가격에 대해서 월별 가격은 ‘중심가격 × exp(누적 로그충격 − 로그 기대배율)’로 생성한다. 평균 앵커의 보정항은 log E[exp(누적 로그충격)]이며, 가우시안일 때만 분산의 절반으로 단순화된다. 중앙값 앵커가 목적이면 별도의 중앙값 보정과 해석이 필요하다. 중심가격이 IAM의 시장균형 값일 뿐 통계적 기대가격인지 정의되지 않았다면, 이를 평균으로 놓는 결정 자체를 연구 가정으로 기록한다.

무제한 Student-t 혁신을 지수화하는 경우 양의 지수모멘트가 존재하지 않으므로 위의 유한 평균 보정이 일반적으로 성립하지 않는다. 유한한 MC 표본이 정상적인 평균을 출력해도 이론적 기대값이 유한하다는 근거가 아니다. 절단, 유계 혁신 또는 다른 꼬리 모형을 쓰면 그 선택과 바뀐 극단사건의 가정을 따로 공개한다.

서로 다른 시나리오에 외부 근거가 있는 가중치가 제공되면 조건부 누적분포들의 가중합에서 분위수를 구한다. 시나리오별 분위수의 평균은 일반적으로 혼합분포의 분위수가 아니다. 가중치가 없으면 시나리오별 표와 사양별 민감도를 제시한다. 시나리오 범위를 90% 신뢰구간이나 미래 발생확률이라고 부르지 않는다.

### 5.8 실제 구현한 공동 블록 가격경로

`research_block_price_paths.py`는 World Bank의 2010년 2월–2025년 12월 191개 월별 로그변화율을 이용한다. Brent·호주 발전용 석탄·미국 및 유럽 가스·일본 LNG·철광석의 같은 달 벡터를 함께 취급한다. 각 계열의 표본평균을 제거하고, 연속된 1·6·12·24개월 블록의 시작점을 동일하게 추출한다. 블록 내부의 시차와 동시 의존성을 유지하고, 서로 다른 블록은 독립적으로 결합한다. 원자료 끝과 시작을 이어 붙이는 순환은 사용하지 않는다. 비교군은 표본 공분산을 사용하는 iid 가우시안이다. [World Bank 원자료](https://www.worldbank.org/en/research/commodity-markets).

블록 길이 L에 대해 가능한 시작점은 1부터 n−L+1이다. 각 시작점의 첫 r개월 중심화 로그변화 합을 S(r)라 하자. h=kL+r, 1≤r≤L이면 로그 기대배율은 k·log mean[exp S(L)] + log mean[exp S(r)]이다. 독립적으로 뽑힌 완전 블록 k개와 마지막 부분 블록의 지수모멘트가 곱해진다는 사실에서 따른다. 이 유한 합을 직접 계산하므로 MC 표본평균을 사후에 1로 강제하지 않는다. 경로 수나 시드를 바꾸어도 모형 자체의 앵커는 변하지 않는다. 이 등식은 평균의 내부 정합성이며 가격 과정의 경험적 타당성 증명은 아니다.

단위 월 구매량이 일정할 때 연간 가격은 12개 월 가격의 산술평균이다. 연말 가격, 연간 로그수익률 합의 지수 또는 월 가격의 기하평균으로 연간 구매지출을 대신하지 않는다. 월별 구매량이 다르면 물량 가중을 사용한다. 모든 계획과 무전환 기준선은 동일한 월별 경로를 공유하며, 경로별 연간 현금흐름과 할인을 계산한 뒤에 분위수·ES를 구한다.

블록 길이 네 개에는 발생확률을 부여하지 않았고 적합도에 따라 하나를 선택하지도 않았다. 과거 위기 빈도는 그대로 재사용되며, 블록을 이어 붙이면 과거에 없던 위기의 반복도 생길 수 있다. 블록 경계에서 장기 의존성이 끊기고 가격수준의 평균회귀를 식별하지 못한다. 따라서 5년 시연을 2050년 기업 꼬리의 검증으로 확장하지 않는다. 추정 모수 불확실성은 현재 경로에 포함하지 않았으며 외부 표본 재추정과 구분된다.

### 5.9 가격분포 검증 결과와 반증

2019년까지의 자료로 적합한 iid 가우시안, AR(1), ridge VAR(4), AR(1)–EWMA 모형을 2020–2025년 72개월에서 회고 평가했다. 다음 달 예측에는 그때까지 관측 가능한 과거값만 사용했다. 다만 모형 후보를 고를 때 전체 표본의 진단 결과를 이미 보았으므로 완전히 보존된 확증용 평가 표본은 아니다. 90% 구간의 실제 포함률은 유럽 가스에서 iid 47.2%, EWMA 68.1%, 일본 LNG에서 70.8%, 79.2%였다. 변동성 갱신이 개선을 주지만 이 계열에서 명목 90%에 충분히 도달하지 못했다. 평균 오차가 줄어드는 것과 꼬리 구간이 잘 보정되는 것은 별개다.

다기간 진단은 h개월 로그변화 합에서 그 표본평균을 제거하고 가우시안의 1.645·월 표준편차·√h와 비교한다. 이전 연구 노트의 비중심 비교와 그에 근거한 ‘평균회귀 확인’ 해석을 수정한다. 12개월 비율은 유럽 가스 1.897, 호주 석탄 1.824, 일본 LNG 1.626인 반면 60개월에는 각각 0.996, 0.957, 0.941이다. 이 결과는 단순 지평 확장이 표본의 모든 지평을 설명하지 못함을 보이지만 평균회귀 반감기나 장기 미래 확률을 식별하지 않는다. 겹치는 관측창에 독립 표본 검정을 적용하지 않는다.

![가격모형의 회고 검증과 공동 블록 재표집](figures/distribution_validation_v2.png)

**그림 4.** 왼쪽은 명목 90% 다음 달 구간의 실제 포함률이다. 오른쪽은 10,000개·60개월 경로에서 5년차 연평균 일본 LNG 가격배율의 중앙값–95% 분위수와 ES95다. 모든 방법은 이론적 기대배율 1로 맞췄다. 이 그림은 벤치마크의 조건부 가격모형 비교이며 기업 TCaR가 아니다.

'''
    block=pd.read_csv(ROOT/'data/research_v2/block_price_paths/annual_multiplier_metrics.csv')
    table='| 가격생성법 | MC 평균 | P50 | P95 | ES95 |\n|---|---:|---:|---:|---:|\n'
    for _,r in block.query('series == "japan_lng" and year_index == 5').iterrows():
        table+=f'| {r.model} | {r["mean"]:.3f} | {r.p50:.3f} | {r.p95:.3f} | {r.es95:.3f} |\n'
    method+=table+'''
동일한 기대가격에서도 블록 길이에 따라 ES가 달라진다. 이것은 더 큰 꼬리가 더 정확하다는 뜻이 아니다. 표본 외 구간 보정, 원료·수입가격과 기업 조달가격의 차이, 전력·수소·탄소 및 환율 자료를 확보해야 기업 가격경로로 채택할 수 있다. 현재 구현은 결합 재표집·평균 앵커·연간 구매가격 집계를 재현 가능한 상태로 만든 연구 후보다.

표에 사용한 MC 경로를 400회 재표집한 조건부 표본오차 검사에서 일본 LNG ES95의 95% 백분위 구간은 iid 가우시안 2.321–2.421, 24개월 블록 3.400–3.691이었다. 월별 관측을 재표집하거나 가격모형을 재추정한 구간이 아니므로 역사 자료의 추정오차·모형 선택·미관측 위기·미래 실현 불확실성을 포함하지 않는다. 시뮬레이션 수치오차와 분포 가정의 차이를 따로 보여주는 검사다.

'''
    text=text.replace('## 6. 네 기업의 조건부 사례',method+'## 6. 네 기업의 조건부 사례',1)
    cases='''### 6.8 기술 DB 재검증과 사양별 격리 실행

기술 DB는 기술명별 대표 숫자 한 개보다 공정 사양의 묶음으로 구성한다. 필요한 키는 제품·기능단위, 철원 및 원료 구성, 설비 포함 범위, 수소 조달, 장입 온도, 열·증기 통합, 전력·연료·원료 구매, 내부 이전, 공동생산물, 가동률, 비용연도, 근거 판본이다. 같은 제품 톤이라도 액강과 열연, 나프타 원료와 에틸렌 제품의 분모가 다르면 직접 비교하지 않는다.

Vogl 총전력에서 수전해 전력 51kg×33.33kWh/kg÷0.72를 차감하면 약 1.119MWh/t가 남는다. 하지만 현장 수전해의 열회수가 달라지므로 이 잔여를 구매수소형 공정의 검증된 전력이라고 부를 수 없다. 1.278은 여기에 냉간 장입 차이 0.159를 더한 조건부 대안이다. 기존 0.85의 근거가 현재 원문에서 재현되지 않았다는 판단과, 대안 1.119가 참값이라는 판단을 구분한다. 공개 GCAM의 1.167MWh·60.8kg 수소는 별도 가스·액체연료와 원료혼합·상류 경계를 포함하므로 수소와 전력 두 항만 이식하지 않는다.

Layritz 나프타 공정은 분해로 열 6.78MWh/t 에틸렌을 내부 메탄 0.488t로 공급한다. 전기화 후 총 구매전력 6.99MWh에는 기본 전력 0.21이 이미 포함된다. 추가 전력은 6.78이며 6.99에 다시 분해로 전력을 더하지 않는다. 내부 메탄은 구매가스 회피비용으로 자동 기장하지 않는다. 전력 100EUR/MWh와 메탄 판매 넷백 500EUR/t를 명시적으로 가정하면 이 두 항의 증분비용은 678−244=434EUR/t다. 판매가 불가능하고 다른 비용이 같으면 678EUR/t이며, 처리비가 있으면 별도 추가한다. 이 예시는 에너지·판매 부분 원장으로 총 전환비용이 아니다.

Linde의 코일박스·열통합 전력은 나프타 원료 톤 기준이다. 에틸렌으로 바꾸려면 일치하는 수율과 증기 수지를 확인해야 한다. Linde 값을 Layritz의 원료계수 3.58로 환산하고 기본 전력 0.21을 더한 3.25 등은 서로 다른 자료를 연결한 민감도 사양이다. 이를 검증된 공정 하한이나 6.99를 보편적인 상한으로 해석하지 않는다. 열 50%의 수소 대체도 환산상 약 102kg이지만, 효율·연소구성·부산물 처리에 따른 실제 설계 검증은 별개다.

격리 실행은 동일한 입력 복사본에서 해당 D3 값만 바꾼 6개 사양을 비교한다. 사양별 후보를 다시 생성했고, frontier 격자 4개·4,000개 경로를 사용했다. 비용 단위는 십억원이다. 다음 표는 실제 계산된 민감도이며 공학적 참값의 정정표가 아니다.

| 변경 사양 | 대상 | 평균 증분비용 변화 | TCaR 변화 | 기술 집합 |
|---|---|---:|---:|---|
| 철강 전력 1.119 | POSCO·NSC, 2개 시나리오 | +3,962~+9,263 | +13.9~+17.1% | 동일 |
| 철강 전력 1.278 | POSCO·NSC, 2개 시나리오 | +6,304~+14,652 | +21.9~+29.8% | 동일 |
| 석화 전력 3.25 | LOTTE, 2개 시나리오 | +324~+607 | −12.5~+29.2% | 변경 |
| 석화 전력 6.99 | LOTTE 2개 및 MCI NZ15 | +324~+2,655 | +11.5~+97.9% | LOTTE 변경 |

![기술 사양 대안별 TCaR 변화](figures/technology_sensitivity_v2.png)

**그림 5.** 각 사양 실행에서 선택한 계획의 TCaR90를 같은 축소 탐색 기준 실행과 비교했다. 기술명 집합이 같아도 설비 배치·가동 시점·계약 전체가 동일하다는 뜻은 아니다. 입력 경계의 불확실성이 결과 크기와 일부 선택에 영향을 주므로 사양을 하나로 고정한 가격 MC만으로 총 불확실성을 설명할 수 없다.

POSCO 회사 전체의 구매 가스·전력·원료탄과 고로 공정의 경계는 다르다. 회사 값과 원단위의 근접성은 공정 검증이 아니다. 롯데 사이트 에너지도 하공정을 포함하므로 에틸렌 생산능력으로 나눈 값을 NCC 실제 생산량당 수요나 수학적으로 보장된 상한으로 표시하지 않는다. 실제 생산량과 공정별 배분이 필요하다.

'''
    text=text.replace('## 7. Excel 통합 시스템과 실무 사용',cases+'## 7. Excel 통합 시스템과 실무 사용',1)
    interface='''### 7.3 GCAM·KAIST 연결과 현재 사용 가능한 범위

GCAM은 기술계수도 포함한다. 따라서 ‘GCAM은 공정 원단위를 주지 않는다’는 종전 노트의 표현을 수정한다. 핵심은 집계 기술의 계수가 본 연구의 제품·설비·회계 경계에 맞는지다. 공개 저장소의 철강 입력 계수와 KAIST의 지역화·기술설정 및 해를 구한 시나리오 출력은 구분한다. 현재 확보한 공개 커밋의 기술 DB, NGFS의 GCAM 6.0 시나리오, 아직 받지 않은 KAIST 모델을 같은 버전으로 취급하지 않는다.

수령 인터페이스는 model, version, scenario, region, variable, native_unit, price_base_year, year, value, source 및 transformation을 보존한다. 철강 GJ/t에서 MWh/t, EJ/Mt 및 통화 단위의 변환은 차원 검사 후 수행하고, 5년 스텝 가격의 연간 보간 규칙과 배출예산의 총량·강도 해석을 기록한다. 탄소가격은 tC와 tCO2를 구별하며 네이티브 단위를 확인하기 전 변환을 실행하지 않는다. 기술별 에너지 계수와 전력 배출계수도 같은 모델 경계에 맞춘다.

NGFS v5.1의 공식 버전 정보는 확인했지만 수치 시나리오를 확보한 것은 아니다. 로컬 NZ15·B20은 계속 자체 추정 경로로 표시한다. KAIST 자료의 수령은 이후 개선과 지역 적합성 검증의 경로이며, 현재의 방법론 정의나 재현 가능한 조건부 실험 자체를 중단할 이유는 아니다. [NGFS v5.1 공식 기록](https://zenodo.org/records/17901363).

현재 Excel 통제 워크북은 v1 기업 계산의 입력 검증·실행·재수입을 지원한다. v2 참조 등록부는 기술·회사·시나리오·검증 자료를 모은 보조 파일이며 엔진 입력이 아니다. 새 블록 가격경로도 그 기업 엔진에 연결되지 않았다. 이 세 가지의 연결을 완료하기 전에는 ‘v2 기술·분포까지 Excel에서 완전히 통제한다’고 표현하지 않는다. 편집 가능한 참조 값과 실제 계산에 반영된 입력의 상태를 분명히 표시해야 한다.

'''
    text=text.replace('## 8. 한계와 후속 검증',interface+'## 8. 한계와 후속 검증',1)
    pos=text.index('## 9. 결론'); end=text.index('## 부록 A.',pos)
    text=text[:pos]+'''## 9. 결론

TCaR의 설득력은 MC 표본 수보다 어떤 공정에 어떤 가격을 적용하고 어떤 공동 충격을 생성했는지에 달려 있다. 본 연구는 공통 경로의 증분비용, 유한 실행 가능 후보, 평균·TCaR·ES, 공정 사양과 자료 출처를 연결하는 방법을 제시했다. 동결 기업 사례와 사양별 추가 실행은 이 절차의 재현성과 입력 선택의 중요성을 보여준다. 경험적 가격 모듈은 공동 블록·정확한 기대가격 보정·연간 구매가격 집계를 구현했지만 실제 기업의 장기 분포를 검증한 결과는 아니다.

감축기술 DB와 시나리오는 서로 다른 근거 체계로 관리하되 경계·연도·단위에서 연결해야 한다. 새 자료를 받았을 때 결과가 어떻게 바뀌는지 검증할 수 있는 구조가 필요하다. 현재의 학술적 주장은 이 조건부 방법론과 반증 가능한 실험에 한정한다. 공정 열수지, 실제 조달가격, 외부 시나리오 입력과 완성된 Excel 연결이 남아 있으므로 저널 통과나 실제 기업 위험 추정의 완결성을 선언하지 않는다.

'''+text[end:]
    text+='''
15. Vogl, V., Åhman, M., & Nilsson, L. J. (2018). Assessment of hydrogen direct reduction for fossil-free steelmaking. *Journal of Cleaner Production*, 203, 736–745. [DOI](https://doi.org/10.1016/j.jclepro.2018.08.279).
16. Layritz, L. S., et al. (2021). The potential of direct steam cracker electrification and carbon capture & utilization via oxidative coupling of methane as decarbonization strategies for ethylene production. *Applied Energy*, 296, 117049. [DOI](https://doi.org/10.1016/j.apenergy.2021.117049). 확인 판본: PIK 기관 프리프린트.
17. Pimm, A. J., Cockerill, T. T., & Gale, W. F. (2021). Energy system requirements of fossil-free steelmaking using hydrogen direct reduction. *Journal of Cleaner Production*, 312, 127665. [DOI](https://doi.org/10.1016/j.jclepro.2021.127665); [Leeds 데이터 기록](https://doi.org/10.5518/997). 본문·부속 간 일부 에너지 수치 차이는 미해결로 유지.
18. Zang et al. (2023). Cost and Life Cycle Analysis for Deep CO2 Emissions Reduction for Steel Making: Direct Reduced Iron Technologies. *Steel Research International*. [DOI](https://doi.org/10.1002/srin.202200297). 원문 공정 구성과 공개 GCAM 변환을 구분.
19. Bachorz, C., Verpoort, P. C., Luderer, G., & Ueckerdt, F. (2025). Exploring techno-economic landscapes of abatement options for hard-to-electrify sectors. *Nature Communications*, 16, 3984. [DOI](https://doi.org/10.1038/s41467-025-59277-1).
20. POSTED. (2026). v0.4.0 기술 데이터. [버전 기록](https://doi.org/10.5281/zenodo.18155305).
21. World Bank. (2026). Commodity Price Data (Pink Sheet), monthly historical data. [공식 자료](https://www.worldbank.org/en/research/commodity-markets). 다운로드 판본 2026-09-02 갱신, 분석 표본 2010–2025.
22. NGFS. (2026). Climate Scenarios Data Set v5.1. [공식 버전 기록](https://zenodo.org/records/17901363). 버전 메타데이터 확인과 실제 수치 수령을 구분.
23. Sinn, T., Hofstaetter, M., Kemper, R., & Kracker, G. (2024). Powering the Transition to Net Zero with Electric Cracking Technology. *Chemical Engineering Progress*, August, 42–49. [Linde 공식 재인쇄본](https://assets.linde.com/-/media/global/engineering/engineering/home/products-and-services/process-plants/petrochemical-technologies/starbridgetm-electric-furnaces/powering-the-transition-to-net-zero-with-electric-cracking-technology.pdf). 공급사 저자의 공정 설계·실증 설명이며 전체 상업설비의 독립 측정치와 구분.

v2 자료와 변환 근거는 `data/research_v2/` 및 `docs/research_cycles/2026-09-06/`, `2026-09-07/`에 있다. v2 가격생성법의 정확한 앵커·시드·지평·계열·원자료 해시는 `block_price_paths/manifest.json`과 `exact_log_anchors.json`에 보존한다. 원고 숫자 검사는 수치 일치와 과학적 외부 검증을 구분한다.
'''
    additions=(ROOT/'paper/methodology/ASSUMPTIONS_AND_DISCLOSED_KO.md').read_text()
    disclosed,assumptions=additions.split('<!-- ASSUMPTION FIGURES -->')
    text=text.replace('## 4. 위험 통계량과 효율적 선택',disclosed.strip()+'\n\n## 4. 위험 통계량과 효율적 선택',1)
    text=text.replace('## 6. 네 기업의 조건부 사례',assumptions.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    text=text.replace('**연구 원고 v2.1 ·','**연구 원고 v2.2 ·',1)
    text=text.replace('현재 자료로 실제 기업의 장기 꼬리가 식별됐거나 저널 제출 준비가 끝났다고 주장하지 않는다.',
        '핵심 가정 그림과 선언 기반 선형 DISCLOSED PLAN 규칙을 추가했다. 선형 경로의 신규 비용 좌표는 후속 실행 대상이다. 현재 자료로 실제 기업의 장기 꼬리가 식별됐거나 저널 제출 준비가 끝났다고 주장하지 않는다.',1)
    text=text.replace('현재 엄격한 검증을 통과한 실제 공시계획 비교군은 0개이므로 새 사례의 기업별 공시 간격을 산출하지 않는다.',
        '이 동결 실행에서 상세 투자 공시를 표현한 비교군은0개였으므로 당시 공시 간격은 미산출로 보존한다. 현행3.5절은 탄소중립 선언만으로도 선형 공시경로를 허용하며, 그 경로의 비용 기준안을 새로 구성한다.')
    context,frontier=(ROOT/'paper/methodology/FRONTIER_AND_INDUSTRY_CONTEXT_KO.md').read_text().split('<!-- FRONTIER EXPLANATION -->')
    frontier,context_refs=frontier.split('<!-- CONTEXT REFERENCES -->')
    text=text.replace('## 3. 측정 대상과 모형의 경계',context.strip()+'\n\n## 3. 측정 대상과 모형의 경계',1)
    text=text.replace('### 4.4 공시계획의 달성 가능한 개선 여지',frontier.strip()+'\n\n### 4.4 공시계획의 달성 가능한 개선 여지',1)
    text=text.replace('v2 자료와 변환 근거는',context_refs.strip()+'\n\nv2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.2 · 2026년 9월 7일.**','**연구 원고 v2.3 · 2026년 9월 8일.**',1)
    text=text.replace('핵심 가정 그림과 선언 기반 선형 DISCLOSED PLAN 규칙을 추가했다.',
        '핵심 가정 그림, 선언 기반 선형 DISCLOSED PLAN 규칙, 효율경계의 경제적·수학적 의미와 한국·일본 산업 맥락을 추가했다.',1)
    text=text.replace('파란색은 표본 지배 후보를 제외한 집합의 비지배점',
        '파란색은 평균–TCaR 비지배점 가운데 표본 경로별 지배 후보를 제외한 점')
    joint_method,joint_cases=(ROOT/'paper/methodology/JOINT_EXECUTION_AND_VALIDATION_KO.md').read_text().split('<!-- JOINT CASES -->')
    joint_cases,joint_workbook=joint_cases.split('<!-- JOINT WORKBOOK -->')
    joint_workbook,joint_refs=joint_workbook.split('<!-- JOINT REFERENCES -->')
    tails=pd.read_csv(ROOT/'data/research_v2/joint_tail_precision/conditional_bootstrap_intervals.csv')
    labels={'iid_gaussian':'독립 정규','empirical_block_1':'블록 1개월','empirical_block_6':'블록 6개월','empirical_block_12':'블록 12개월','empirical_block_24':'블록 24개월'}
    tail_table='| 가격생성법 | TCaR95 | MC 구간 하단 | MC 구간 상단 | ES95 |\n|---|---:|---:|---:|---:|\n'
    for row in tails.query('horizon_years == 24').itertuples():
        tail_table+=f'| {labels[row.model]} | {row.tcar95/1000:.3f} | {row.tcar95_low/1000:.3f} | {row.tcar95_high/1000:.3f} | {row.es95/1000:.3f} |\n'
    bounds=pd.read_csv(ROOT/'data/research_v2/disclosed_feasibility/case_summary.csv')
    bound_table='| 기업 | 추정 설비 수 | 2050 하한 / 대리 기준 | 2024 투자: 첫 초과 | 2027 투자: 첫 초과 |\n|---|---:|---:|---:|---:|\n'
    for cid in ('POSCO','NSC','LOTTE','MCI'):
        early=bounds.query('company_id == @cid and scenario == "NZ15" and earliest_start_year == 2024').iloc[0]
        late=bounds.query('company_id == @cid and scenario == "NZ15" and earliest_start_year == 2027').iloc[0]
        bound_table+=f'| {cid} | {early.covered_facilities} | {early.terminal_floor_percent_of_proxy_baseline:.2f}% | {early.first_bound_violation_year} | {late.first_bound_violation_year} |\n'
    joint_cases=joint_cases.replace('<!-- TAIL TABLE -->',tail_table).replace('<!-- DISCLOSED TABLE -->',bound_table)
    text=text.replace('## 6. 네 기업의 조건부 사례',joint_method.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    text=text.replace('## 7. Excel 통합 시스템과 실무 사용',joint_cases.strip()+'\n\n## 7. Excel 통합 시스템과 실무 사용',1)
    text=text.replace('## 8. 한계와 후속 검증',joint_workbook.strip()+'\n\n## 8. 한계와 후속 검증',1)
    text=text.replace('v2 자료와 변환 근거는',joint_refs.strip()+'\n\nv2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.3 ·','**연구 원고 v2.4 ·',1)
    text=text.replace('선형 경로의 신규 비용 좌표는 후속 실행 대상이다.',
        '5.11–5.12절에 조달가격·현금원장 연결과 위험 대응을, 6.9–6.10절에 장기 NCC 부분 비용과 선형 경로의 물리적 하한을, 7.4절에 실제 Excel 재계산 연결을 추가했다. 신규 전체 기업 비용 좌표는 후속 실행 대상이다.',1)
    text=text.replace('공통 블록 재표집과 정확한 기대가격 보정으로 5개 가격생성법을 구현해, 같은 기대가격에서도 꼬리가 달라짐을 보였다.',
        '공통 블록 재표집과 정확한 기대가격 보정으로 5개 가격생성법을 구현하고 IEA 시나리오의 NCC 부분 비용에 연결했다. 24년의 조건부 실험에서는 경로 수를 늘려도 모형 간 꼬리 차이가 남았다. 선언 기반 선형 경로는 허용하되 현 기술 메뉴의 물리적 하한을 초과하는 경우 가상 비용을 부여하지 않았다.',1)
    text=text.replace('현재 사례에는 이 비교군이 없어 간격을 미산출한다.',
        '동결 기업 실행의 상세 공시 비교는 미산출로 보존하며, 새 선형 선언 경로에는 비용 산출에 앞서 물리적 충족 가능성을 진단한다.',1)
    text=text.replace('새 블록 가격경로도 그 기업 엔진에 연결되지 않았다.',
        '새 블록 가격은 7.4절의 NCC 부분 원장과 FIN에 연결했으며, 기존 네 기업 포트폴리오의 전체 재평가에는 아직 적용하지 않았다.')
    text=text.replace('공정 열수지, 실제 조달가격, 외부 시나리오 입력과 완성된 Excel 연결이 남아 있으므로',
        'IEA 시나리오와 NCC 부분 원장의 Excel 연결은 검증했으나, 전체 공정 열수지·실제 조달가격·잔여 감축·신규 기업 후보 통합은 남아 있으므로')
    steel_method,steel_cases=(ROOT/'paper/methodology/STEEL_CASH_EXECUTION_KO.md').read_text().split('<!-- STEEL CASH CASES -->')
    steel_data=pd.read_csv(ROOT/'data/research_v2/steel_reference_ledger/absolute_cost_sensitivity.csv')
    steel_table='| 가동률 | 평균 비용 | 중앙값 | 95분위 | ES95 | 평균 톤당 비용 |\n|---|---:|---:|---:|---:|---:|\n'
    for r in steel_data.query('model == "block_12" and seed == 20260908 and oxygen_sale_fraction == 0.6').itertuples():
        steel_table+=f'| {r.utilization:.0%} | {r.mean_million_source_EUR:.3f} | {r.p50_million_source_EUR:.3f} | {r.q95_million_source_EUR:.3f} | {r.ES95_million_source_EUR:.3f} | {r.mean_per_discounted_output_source_EUR_t:.3f} |\n'
    steel_cases=steel_cases.replace('<!-- STEEL CASH TABLE -->',steel_table)
    text=text.replace('## 6. 네 기업의 조건부 사례',steel_method.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    text=text.replace('## 7. Excel 통합 시스템과 실무 사용',steel_cases.strip()+'\n\n## 7. Excel 통합 시스템과 실무 사용',1)
    text=text.replace('**연구 원고 v2.4 ·','**연구 원고 v2.5 ·',1)
    text=text.replace('신규 전체 기업 비용 좌표는 후속 실행 대상이다.', '5.13·6.11절에는 구성 설비 수명과 가동률을 반영한 철강 참조 현금비용을 추가했다. 신규 전체 기업 비용 좌표는 후속 실행 대상이다.',1)
    if '34. Fischedick' not in text:
        text=text.replace('v2 자료와 변환 근거는','34. Fischedick, M., Marzinkowski, J., Winzer, P., & Weigel, M. (2014). Techno-economic evaluation of innovative steel production technologies. *Journal of Cleaner Production, 84*, 563–580. DOI:10.1016/j.jclepro.2014.05.063. 기관 저자본의 §3.2와 부록 원표를 검토했으며 최종 출판본의 불일치 수정 여부는 확인하지 않았다.\n\nv2 자료와 변환 근거는',1)
    capture=(ROOT/'paper/methodology/CAPTURE_REFERENCE_EXECUTION_KO.md').read_text()
    capture_results=pd.read_csv(ROOT/'data/research_v2/ieaghg_paired/conditional_cost_metrics.csv')
    capture_table='| EOP-L1 계약비율 | 선택 표본평균 | 독립 평가 평균 | 해석적 기대비용 | 독립 평가 ES95 |\n|---|---:|---:|---:|---:|\n'
    for h in [0.,.5,1.]:
        v=capture_results[(capture_results.model=='block_12')&(capture_results.scenario=='STEPS')&(capture_results.case=='EOP_L1')&(capture_results.incremental_gas_contract_fraction==h)]
        sel=v[v.role=='selection'].iloc[0];val=v[v.role=='validation'].iloc[0]
        capture_table+=f'| 추가 가스 {h:.0%} | {sel["mean"]:.3f} | {val["mean"]:.3f} | {val.analytic_mean:.3f} | {val.es95:.3f} |\n'
    capture=capture.replace('<!-- CAPTURE VALIDATION TABLE -->',capture_table+'\n단위: 백만 원문 USD. STEPS, 12개월 블록, EOP-L1의 추가 가스 계약 비교.')
    text=text.replace('## 7. Excel 통합 시스템과 실무 사용',capture.strip()+'\n\n## 7. Excel 통합 시스템과 실무 사용',1)
    import shutil
    for name in ['paired_capture_reference','mean_and_tail_selection_instability']:
        shutil.copyfile(ROOT/f'data/research_v2/ieaghg_paired/{name}.png',ROOT/f'paper/methodology/figures/{name}.png')
    ncc_boundary=(ROOT/'paper/methodology/NCC_SOURCE_BOUNDARY_KO.md').read_text()
    text=text.replace('## 6. 네 기업의 조건부 사례',ncc_boundary.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    ncc_cash=(ROOT/'paper/methodology/NCC_CONDITIONAL_CASH_KO.md').read_text()
    ncc_results=pd.read_csv(ROOT/'data/research_v2/ncc_reference_cash/conditional_metrics.csv')
    ncc_table='| 전기화 수명 | 잔존가치 | 평균 증분비용 | ES95 | TCaR95 |\n|---|---|---:|---:|---:|\n'
    for row in ncc_results.query('block==12 and seed==20260913 and recovery==1 and maintenance_scale==1').itertuples():
        terminal_label='없음' if row.terminal=='none' else '직선 대용치'
        ncc_table+=f'| {row.electric_life}년 | {terminal_label} | {row.mean:.3f} | {row.es95:.3f} | {row.tcar95:.3f} |\n'
    ncc_cash=ncc_cash.replace('<!-- NCC CONDITIONAL TABLE -->',ncc_table+'\n단위: 백만EUR2019 가정. 동일 생산량·같은 가격 표본이며 실증 기업 비용이 아니다.')
    text=text.replace('## 7. Excel 통합 시스템과 실무 사용',ncc_cash.strip()+'\n\n## 7. Excel 통합 시스템과 실무 사용',1)
    shutil.copyfile(ROOT/'data/research_v2/ncc_reference_cash/capital_and_tail_level.png',ROOT/'paper/methodology/figures/ncc_capital_and_tail_level.png')
    company_boundary=(ROOT/'paper/methodology/COMPANY_BOUNDARY_KO.md').read_text()
    text=text.replace('## 6. 네 기업의 조건부 사례',company_boundary.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    shutil.copyfile(ROOT/'data/research_v2/company_boundary/company_boundary_assumptions.png',ROOT/'paper/methodology/figures/company_boundary_assumptions.png')
    process_bridge=(ROOT/'paper/methodology/COMPANY_PROCESS_BRIDGE_KO.md').read_text()
    text=text.replace('## 6. 네 기업의 조건부 사례',process_bridge.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    shutil.copyfile(ROOT/'data/research_v2/company_process_bridge/production_boundary_assumptions.png',ROOT/'paper/methodology/figures/production_boundary_assumptions.png')
    supply=(ROOT/'paper/methodology/SUPPLY_CONTINUITY_KO.md').read_text()
    text=text.replace('## 6. 네 기업의 조건부 사례',supply.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    grid_provenance=(ROOT/'paper/methodology/GRID_FACTOR_PROVENANCE_KO.md').read_text()
    text=text.replace('## 6. 네 기업의 조건부 사례',grid_provenance.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    procurement=(ROOT/'paper/methodology/COMPANY_PROCUREMENT_KO.md').read_text()
    text=text.replace('## 6. 네 기업의 조건부 사례',procurement.strip()+'\n\n## 6. 네 기업의 조건부 사례',1)
    incumbent=(ROOT/'paper/methodology/INCUMBENT_REFERENCE_KO.md').read_text()
    incumbent_rows=pd.read_csv(ROOT/'data/research_v2/incumbent_ncc/conditional_metrics.csv')
    shutil.copyfile(ROOT/'data/research_v2/incumbent_ncc/incumbent_assumption_grid.png',ROOT/'paper/methodology/figures/incumbent_assumption_grid.png')
    incumbent_table=''.join(f'| {int(r.remaining_years)}년 | {r.mean:.3f} | {r.es_alpha:.3f} | {r.tcar:.3f} | {r.mean_shift:.3f} |\n' for r in incumbent_rows.query('replacement_cost_scale==1').itertuples())
    text=text.replace('## 7. Excel 통합 시스템과 실무 사용',incumbent.replace('<!-- INCUMBENT TABLE -->',incumbent_table).strip()+'\n\n## 7. Excel 통합 시스템과 실무 사용',1)
    context_bridge,feasibility_bridge=(ROOT/'paper/methodology/FRONTIER_CONTEXT_BRIDGE_KO.md').read_text().split('<!-- FEASIBILITY BEFORE FRONTIER -->')
    text=text.replace('## 3. 측정 대상과 모형의 경계',context_bridge.strip()+'\n\n## 3. 측정 대상과 모형의 경계',1)
    text=text.replace('### 4.4 공시계획의 달성 가능한 개선 여지',feasibility_bridge.strip()+'\n\n### 4.4 공시계획의 달성 가능한 개선 여지',1)
    emission_context=(ROOT/'paper/methodology/NCC_EMISSIONS_CONTEXT_KO.md').read_text()
    emission_rows=pd.read_csv(ROOT/'data/research_v2/ncc_emissions_context/illustrative_table.csv')
    emission_table=''.join(f'| {r.grid_tCO2_MWh:.1f} | {r.conventional:.4f} | {r.electric:.4f} | {r.incremental:+.4f} |\n' for r in emission_rows.itertuples())
    text=text.replace('## 7. Excel 통합 시스템과 실무 사용',emission_context.replace('<!-- EMISSIONS TABLE -->',emission_table).strip()+'\n\n## 7. Excel 통합 시스템과 실무 사용',1)
    shutil.copyfile(ROOT/'data/research_v2/ncc_emissions_context/grid_and_residual_boundary.png',ROOT/'paper/methodology/figures/grid_and_residual_boundary.png')
    # Figure captions follow their order of appearance, including old snapshots.
    import re
    from itertools import count
    counter=count(1)
    text=re.sub(r'\*\*그림 \d+\.',lambda m:'**그림 '+str(next(counter))+'.',text)
    text=text.replace('현재 Excel 통제 워크북은 v1 기업 계산의 입력 검증·실행·재수입을 지원한다.', '현재 Excel 통제 워크북은 v1 기업 계산의 입력 검증·실행·재수입을 지원한다. 별도 v2 워크북은 17개 시트의 참조·저장 결과와 편집 가능한 NCC 부분 원장을 제공한다. 전력가격·메탄 넷백·판매비율·생산량 변경에 대한 수식 재계산과 빈 입력의 노출을 검사했다. 이는 네이티브 Excel 앱에서의 실행이나 기업 MC·최적화의 연결 시험과 다르다.')
    # Keep reproduction commentary outside the numbered bibliography.
    m=re.search(r'\n문헌 확인 범위.*?\n\n(?=15\.)',text,re.S)
    if m:
        commentary=m.group().strip()
        text=text[:m.start()]+'\n\n'+text[m.end():]
        text+='\n'+commentary+'\n'
    # Connect the industrial motivation to the ledger and conditional frontier.
    decision, procurement = (ROOT/'paper/methodology/DECISION_CONTEXT_KO.md').read_text().split('<!-- PROCUREMENT EXAMPLE -->')
    procurement, gcam = procurement.split('<!-- GCAM CONTEXT -->')
    text=text.replace('## 2. 문헌과 방법론적 위치',decision.strip()+'\n\n## 2. 문헌과 방법론적 위치',1)
    text=text.replace('## 4. 위험 통계량과 효율적 선택',procurement.strip()+'\n\n## 4. 위험 통계량과 효율적 선택',1)
    text=text.replace('### 7.4 새 공동 가격 모듈의 Excel 입력–실행–결과 연결',gcam.strip()+'\n\n### 7.4 새 공동 가격 모듈의 Excel 입력–실행–결과 연결',1)
    text=text.replace('**연구 원고 v2.5 ·','**연구 원고 v2.6 ·',1)
    text=text.replace('신규 전체 기업 비용 좌표는 후속 실행 대상이다.', '1.1·3.6·7.3절에 의사결정 맥락, 원료·에너지·계약의 설명 예제와 GCAM 연결의 해석을 보강했다. 신규 전체 기업 비용 좌표는 후속 실행 대상이다.',1)
    text=text.replace('v2 자료와 변환 근거는','35. GCAM. Model Overview. 공식 온라인 모형 문서, 조회 2026-09-08. [공식 설명](https://jgcri.github.io/gcam-doc/overview.html).\n\nv2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.6 ·','**연구 원고 v2.7 ·',1)
    text=text.replace('신규 전체 기업 비용 좌표는 후속 실행 대상이다.', '6.12절에는 동일 HRC 경계의 잠정 포집 참조와 표본평균에 따른 경계 선택의 불안정을 추가했다. 신규 전체 기업 비용 좌표는 후속 실행 대상이다.',1)
    text=text.replace('v2 자료와 변환 근거는','36. IEAGHG. (2013). Iron and Steel CCS Study (Techno-Economics Integrated Steel Mill). Report 2013/04. Volume I Section E; Volume II Section D and Annex I. [공식 보고서](https://ieaghg.org/publications/2013-04%20Iron%20and%20Steel%20CCS%20Study%20%28Techno-Economics%20Integrated%20Steel%20Mill%29.pdf). 공식 웹 추출 본문 검토, 표 이미지 확인 미완료.\n\nv2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.7 ·','**연구 원고 v2.8 ·',1)
    text=text.replace('신규 전체 기업 비용 좌표는 후속 실행 대상이다.', '5.14절에는 추가 석유화학 출판본의 에너지·투자비 경계와 채택 보류 항목을 추가했다. 신규 전체 기업 비용 좌표는 후속 실행 대상이다.',1)
    literature='Tiggeloven et al. (2023)은 전기 크래커의 운영 유연성·저장·재생전원을 함께 최적화하되 비용과 배출 목적을 별도로 분석한다. 5.14절은 이 출판본의 수치 경계를 재구성한다. Naraghi et al. (2025)의 프리프린트 초록도 재생전원·시장가격 불확실성을 고려한 크래커의 확률적 운영 최적화를 제시한다. 후자는 초록까지 확인했으므로 수치 채택이나 전문 검증의 근거로 사용하지 않는다. 산업 전환에 불확실성과 운영 대안을 결합한다는 사실만을 본 연구의 신규성으로 주장하지 않는다. [Tiggeloven et al., 2023](https://doi.org/10.1021/acs.iecr.3c02226); [Naraghi et al., 2025, v1](https://arxiv.org/abs/2510.25880v1).\n\n'
    text=text.replace('이 검토는 공정·시나리오·계약·위험이라는 사용 목적에 따른 선별 검토다.',literature+'이 검토는 공정·시나리오·계약·위험이라는 사용 목적에 따른 선별 검토다.',1)
    refs='37. Tiggeloven, J. L., Faaij, A. P. C., Kramer, G. J., & Gazzani, M. (2023). Optimization of Electric Ethylene Production: Exploring the Role of Cracker Flexibility, Batteries, and Renewable Energy Integration. *Industrial & Engineering Chemistry Research, 62*, 16360–16382. [DOI](https://doi.org/10.1021/acs.iecr.3c02226). 출판본 Table1·3·4와 식(3) 시각 대조.\n\n38. Naraghi, S. G., Kareck, T., Xiao, L., Reed, R., Ramanan, P., & Jiang, Z. (2025). Decarbonization of Steam Cracking for Clean Olefins Production: Optimal Microgrid Scheduling. arXiv:2510.25880v1. [프리프린트 초록](https://arxiv.org/abs/2510.25880v1). 초록 확인; 전문 및 최종 출판 상태 검증 미완료.\n\n'
    text=text.replace('v2 자료와 변환 근거는',refs+'v2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.8 ·','**연구 원고 v2.9 ·',1)
    text=text.replace('출판본 Table1·3·4와 식(3) 시각 대조.', '출판본 Table1·3·4와 식(3), 공개 보충자료 식(1)–(3)·TableS6 시각 대조. [보충자료](https://ndownloader.figshare.com/files/42479975).',1)
    text=text.replace('**연구 원고 v2.9 ·','**연구 원고 v2.10 ·',1)
    text=text.replace('**연구 원고 v2.10 ·','**연구 원고 v2.11 ·',1)
    text=text.replace('**연구 원고 v2.11 ·','**연구 원고 v2.12 ·',1)
    text=text.replace('**연구 원고 v2.12 ·','**연구 원고 v2.13 ·',1)
    text=text.replace('v2 자료와 변환 근거는','39. Mitsui Chemicals. (2025). Mitsui Chemicals Group ESG Report 2025, Part6. PDF2·6·7쪽(인쇄280·284·285쪽), FY2024 회사·사업장 표. [공식 원문](https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/sustainability/report/esg2025web_e_part06.pdf.coredownload.pdf). 선택 표 시각 확인; 전체 보고서 검증을 뜻하지 않음.\n\nv2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.13 ·','**연구 원고 v2.14 ·',1)
    text=text.replace('v2 자료와 변환 근거는','40. LOTTE Chemical. (2025). 2024 사업보고서. PDF32·34·64쪽. 국제가격·구매 기업 범위·NC 생산실적 및 2023 생산능력 표. [원문](https://www.lottechem.com/pdfRead.do?fileId=FILE_250319162135146&voNm=irdataVo).\n\n41. Nippon Steel. (2025). FY2024 Financial Results, May 9. PDF30쪽 생산·출하 및 범위 주석. [원문](https://www.nipponsteel.com/en/ir/library/pdf/20250509_200.pdf).\n\n42. Mitsui Chemicals. (2024). August 21, OPC 재가동 지연 및 실적 전망 공시. [원문](https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/release/2024/240821e.pdf).\n\n43. Mitsui Chemicals. (2024). October 2, OPC 9월 30일 재가동 확인 공시. [원문](https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/release/2024/241002_1e.pdf).\n\n'+'v2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.14 ·','**연구 원고 v2.15 ·',1)
    text=text.replace('v2 자료와 변환 근거는','44. Mitsui Chemicals. (2025). Q3 FY2024 Earnings Conference Call, Q&A Summary. 2월4일 설명회, PDF4쪽 Q10/A10. 회사의 잠정 실적 영향 분해이며 별도 감사된 비용 명세가 아님. [원문](https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/release/2025/event_250219e.pdf).\n\nv2 자료와 변환 근거는',1)
    text=text.replace('**연구 원고 v2.15 ·','**연구 원고 v2.16 ·',1)
    text=text.replace('**연구 원고 v2.16 ·','**연구 원고 v2.17 ·',1)
    text=text.replace('**연구 원고 v2.17 ·','**연구 원고 v2.18 ·',1)
    text=text.replace('**연구 원고 v2.18 ·','**연구 원고 v2.20 ·',1)
    text=text.replace('v2 자료와 변환 근거는','45. WRI and WBCSD. (2015). GHG Protocol Scope 2 Guidance. 제4·7·11장: 두 회계 방법, 계약 품질요건 및 전력공급 변화와의 관계. [공식 지침 및 개정 안내](https://ghgprotocol.org/scope-2-guidance). 2015 판본의 구분을 인용하며 개정 절차를 새 확정 규칙으로 간주하지 않음.\n\nv2 자료와 변환 근거는',1)
    grid_refs='''46. 온실가스종합정보센터. (2024 승인, 2025 공고; 2025 승인). 국가 온실가스 배출·흡수계수. 2024 PDF1쪽 및 2025 PDF1–2쪽. [2024 승인 공고](https://www.gir.go.kr/home/board/read.do?boardId=82&boardMasterId=2&menuId=36); [2025 승인 공고](https://www.gir.go.kr/home/board/read.do?boardId=86&boardMasterId=2&menuId=36).

47. Electric Power Council for a Low Carbon Society. (2026-03-12). FY2024 CO2 emissions, final results. 조정 후 회원사 집계와 앞선 잠정치 대조. [공식 발표](https://e-lcs.jp/news/2026/03/2024-co2-1.html).

48. 일본 환경성·경제산업성. (2026-08-03 갱신). 전기사업자별 배출계수, 2026 제출용. PDF1·18쪽. [공식 표](https://policies.env.go.jp/earth/ghg-santeikohyo/files/calc/r08_denki_coefficient_rev4.pdf).

49. 한국에너지공단. 에너지온실가스 종합정보 플랫폼, 전력 배출계수 재게시 표. GIR 원문과의 특정 수치 불일치 확인, 2026-09-08 조회. [공식 플랫폼](https://tips.energy.or.kr/carbon/Ggas_tatistics03.do).

'''
    text=text.replace('v2 자료와 변환 근거는',grid_refs+'v2 자료와 변환 근거는',1)
    provenance_start=text.index('\nv2 자료와 변환 근거는')
    provenance=text[provenance_start:].strip()
    (ROOT/'paper/methodology/REPRODUCTION_LOCATIONS_KO.md').write_text('# 재현 자료 위치와 판본 범위\n\n'+provenance+'\n\n현행 판본의 완료 보완 기록은 docs/research_cycles/2026-09-07-hourly/STATE.json과 해당 completion 검증 파일을 따른다. 기업 생산·구매 자료는 data/research_v2/company_process_bridge/, 공급 연속성 자료는 data/research_v2/supply_continuity/에 별도 보존한다. 과거 원문238개 등록부가 이후 추가 자료 전체를 포함하는 것은 아니다.\n')
    text=text[:provenance_start]+'\nv2 자료와 변환 근거는 [재현 자료 안내](REPRODUCTION_LOCATIONS_KO.md)에 정리했다. 원문 위치·해시와 실행별 검증 기록을 연결하며, 역사적 수치 등록부와 현행 보완 자료를 구별한다. 현재 상태와 남은 실증 과제는 연구 회차 STATE 및 RESEARCH_LOG를 따른다.\n'
    PAPER.write_text(text)
    print(f'Integrated {len(text):,} characters; v1 snapshot preserved')


if __name__=='__main__': main()
