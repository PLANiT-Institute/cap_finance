# L5 — 정부 개입의 한계와 정직한 형태

배경: L4에서 확인한 두 긴장 — (1) 유럽 실제 ECA 사례는 정부(EU 예산 보증)가 mezzanine 층까지 흡수하고 있음, (2) CCfD 같은 catastrophe 층 보장은 탄소가 붕괴(정책이 만든 위험)를 정부가 재보험하는 구조. 이 노트는 "정부가 지면 싸다"는 표준 논거(Arrow-Lind)가 왜 이 자리에서 안 걸리는지, 그리고 CAP이 정직하게 쓸 수 있는 정책 함의의 형태를 정리한다. 새 이론 없음 — 기존 공공경제·정책신뢰성 문헌에 얹음.

---

## Arrow-Lind와 한계

Arrow & Lind (1970)의 핵심 결과: 공공 투자의 위험을 다수의 납세자에게 분산하면(위험 부담을 인구 n으로 나누면), 1인당 위험비용은 1/n에 비례해 0으로 수렴한다. 정부가 위험을 지는 것이 민간보다 싸다는 표준 논거의 근거다. 단, 이 결과는 **위험이 총소비(사회 전체의 다른 소득 흐름)와 통계적으로 독립적일 때만** 성립한다 — 즉 위험이 분산 가능(diversifiable)해야 한다.

[Arrow, K.J. & Lind, R.C. (1970), "Uncertainty and the Evaluation of Public Investment Decisions", *American Economic Review*, 60(3), 364–378 | https://econpapers.repec.org/article/aeaaecrev/v_3a60_3ay_3a1970_3ai_3a3_3ap_3a364-78.htm]

Gardner (1979)는 이 결과를 이산 모형에서 연속체 경제(continuum economy)로 재구성해 더 일반적인 틀에서 재도출했다 — 다수 납세자에 걸친 위험분산이라는 논리 자체는 강화되지만, 독립성 가정은 그대로 유지된다.

[Gardner, R. (1979), "The Arrow-Lind Theorem in a Continuum Economy", *American Economic Review*, 69(3), 420–422 | https://ideas.repec.org/a/aea/aecrev/v69y1979i3p420-22.html]

**이 자리에 왜 안 걸리는가**: CAP의 catastrophe 층(탄소가 붕괴, 정책 위험)은 개별 프로젝트의 특이위험(idiosyncratic risk)이 아니라 정책 그 자체가 만드는 **체계적·내생적 위험**이다. 탄소가가 무너지는 사건은 정부의 정책 결정(감축목표 완화, ETS 무상할당 확대, 탄소가격 상한 도입 등)에 직접 연동되어 있고, 이런 정책 위험은 다시 거시경제 상황(경기침체기에 산업 보호를 위해 탄소가격을 낮추는 압력)과 상관된다 — 즉 총소비/재정여력과 독립이 아니다. Arrow-Lind가 요구하는 독립성 조건이 구조적으로 깨지는 자리이므로, "정부가 지는 게 이론적으로 거의 공짜"라는 논거를 이 특정 위험 층에 직접 적용할 수 없다.

Mechler & Hochrainer-Stigler (2014)는 이 논점을 재난위험 맥락에서 명시적으로 다룬다: 주권국가가 지는 재해 위험이 상관·파국적(catastrophic, correlated) 성격을 가질 때 Arrow-Lind의 "위험비용 0 수렴"이 성립하지 않으며, 이런 위험은 사전 재원조달(계약형 신용, 재보험 풀)이 필요하다고 주장한다. (서지 확인, 논지 요약은 초록·2차 인용 기반 — 전문 접근 제한으로 본문 상세 미확인.)

[Mechler, R. & Hochrainer-Stigler, S. (2014), "Revisiting Arrow-Lind: Managing Sovereign Disaster Risk", *Journal of Natural Resources Policy Research*, 6(1), 93–100 | https://www.tandfonline.com/doi/abs/10.1080/19390459.2013.873186]

Baumstark & Gollier (2013/2014)도 같은 방향에서 Arrow-Lind의 "관련성과 한계"를 다룬다 — 위험이 총소비와 상관될 때 정부 할인율에 위험 프리미엄이 다시 들어가야 한다는 논지로 이해됨. (서지는 확인, 본문 논증 세부는 PDF 파싱 실패로 미확인 — 제목·초록 수준만 확인.)

[Baumstark, L. & Gollier, C. (2013/2014), "The relevance and the limits of the Arrow-Lind Theorem", HAL/TSE working paper | https://shs.hal.science/halshs-00958510]

---

## 자기 위험 재보험의 도덕적 해이·시간불일치

CCfD(탄소차액계약)에서 정부는 탄소가가 행사가격(strike price) 아래로 떨어지면 차액을 기업에 지급한다. 그런데 탄소가 수준 자체가 정부의 정책 결정(ETS 공급량, 무상할당, 상한가격 등)의 산물이다. 이는 표준적인 도덕적 해이 구도를 뒤집는다 — 통상 도덕적 해이는 "보험 가입자가 위험을 키운다"이지만, 여기서는 **보험자(정부)가 보험사고(탄소가 하락)를 일으킬 수 있는 정책 레버를 쥐고 있다.** 정부가 감축 속도를 늦추거나 무상할당을 늘리면 탄소가가 낮아지고 CCfD 지급액이 커진다 — 정부 자신의 사후 정책 선택이 자신의 재정 부담을 결정한다.

이 구조는 Kydland & Prescott (1977)의 시간불일치 문제와 정확히 같은 형태다: 사전에 최적으로 설계된 정책(엄격한 감축 경로 + CCfD 보장)이, 사후적으로는 정부에게 그 약속을 깨뜨릴 유인(감축을 늦춰 단기 산업 충격을 줄이거나, 반대로 CCfD 지급 부담을 회피하기 위해 탄소가를 인위적으로 방어)을 만든다. 재량(discretion)이 최적이 아니라 규칙(commitment)이 필요하다는 논지가 그대로 적용된다.

[Kydland, F.E. & Prescott, E.C. (1977), "Rules Rather than Discretion: The Inconsistency of Optimal Plans", *Journal of Political Economy*, 85(3), 473–491 | https://www.journals.uchicago.edu/doi/abs/10.1086/260580]

기후·탄소정책에 특화된 신뢰성 문헌도 같은 문제를 직접 다룬다. Helm, Hepburn & Mash (2003)는 탄소정책의 시간불일치가 (i) 다목적성(경쟁력 보호 vs 감축), (ii) 에너지투자의 비가역성, (iii) 사후에 정책수단(탄소세·배출권)을 재조정할 유인 때문에 발생한다고 정리한다.

[Helm, D., Hepburn, C. & Mash, R. (2003), "Credible Carbon Policy", *Oxford Review of Economic Policy*, 19(3), 438–450 | https://academic.oup.com/oxrep/article-abstract/19/3/440598]

Brunner, Flachsland & Marschinski (2012)는 외부 강제장치 없이는 정부의 장기 탄소정책 약속이 언제든 철회 가능하며, 이것이 투자자의 신뢰 부족·시장위험·투자보류(hold-up)로 이어진다고 분석하고, 법적·정치적 신뢰장치(commitment device)를 논의한다.

[Brunner, S., Flachsland, C. & Marschinski, R. (2012), "Credible commitment in carbon policy", *Climate Policy*, 12(2), 255–271 | https://www.tandfonline.com/doi/abs/10.1080/14693062.2011.582327]

**실제 사례 확인**: 캐나다 정부의 CCfD 프로그램에서 재정위험 문제가 실제로 제기되었다 — 탄소가격 보증에 따른 연방정부 재정비용 위험이 "정부 스스로 통제하는 미래 정책 결정"(배출권거래제 기준선 변경, 오프셋 기준 변경 등)에 달려 있다는 점이 지적되었다. 이는 이 노트가 말하는 자기 위험 재보험의 시간불일치 문제가 이론이 아니라 현재 진행형 정책 논쟁이라는 근거다.

[출처: 2024 캐나다 연방예산 및 관련 정책 분석 | https://www.millerthomson.com/en/insights/esg-and-carbon-finance/de-risk-and-innovate-a-primer-on-carbon-contracts-for-difference/]

---

## 위험 이전이지 소멸 아님

Wolf (2025)는 유럽 철강산업을 대상으로 CCfD와 쿼터 기반 그린리드마켓(quota-based green lead markets)을 분석하며, 이 두 수단이 효과를 내려면 **"그린 철강 설비 투자자로부터 철강 구매자 또는 납세자로의 상당한 위험 이전"**이 필요하다고 명시한다. 즉 정책수단은 위험을 없애는 것이 아니라 누가 지느냐를 재배치할 뿐이며, 두 수단을 결합하면 위험 배분이 더 균형 있게 되어 공공 수용성이 높아진다고 논한다.

[Wolf, A. (2025), "The uncertain costs of decarbonization policies: a risk analysis for the European steel industry", *Economia e Politica Industriale (Journal of Industrial and Business Economics)*, 52(4), 913–934 | https://link.springer.com/article/10.1007/s40812-025-00343-6]

CAP의 맥락에서 이 논지를 그대로 적용하면: 정부가 CCfD로 catastrophe 층 하방을 잘라준다는 것은 사회 전체의 위험이 사라진다는 뜻이 아니라, 기업 대차대조표 → 정부 재정(결국 납세자) 이라는 경로로 **꼬리가 옮겨간다**는 뜻이다. "정부가 지면 사회적으로 싸다"는 주장은 Arrow-Lind 조건(독립성)이 성립할 때만 정당화되는데, 위에서 확인했듯 이 위험은 그 조건을 만족하지 않는다 — 따라서 위험 이전은 순수한 사회적 이득이 아니라 **회계적 재배치**로 취급해야 한다.

---

## 최적 층 경계 (정부가 어디까지 내려와야 하나)

L4에서 확인한 긴장: 유럽 실제 사례(ECA 감사 대상 EU 예산보증)에서는 정부가 catastrophe 층뿐 아니라 mezzanine까지 흡수하고 있다. EU 예산보증 익스포저는 2022년 말 2,483억 유로에서 2023년 말 2,980억 유로로 증가했고, ECA는 위험 계층을 동심원(first layer → 후속 layer)으로 감사한다.

[유럽회계감사원(European Court of Auditors), 2023 EU audit in brief | https://op.europa.eu/webpub/eca/audit-in-brief-2023/en/]

이 확장이 정당화되는 표준 논거는 "crowding-in"(마중물 효과)이다. 기후금융 실무 문헌은 보증·후순위 지분 같은 첫손실(first-loss) 구조가 민간자본을 끌어들이는 효과가 크다고 보고한다(자본동원배율이 대출 대비 6~25배라는 보고 포함 — 실무 보고서 수치로, 학술 peer-review 확인은 아님).

[Climate Policy Initiative, "Guarantees" toolkit | https://www.climatepolicyinitiative.org/toolkit-instrument/guarantees-3/]

그러나 "crowding-out"(민간 구축) 우려에 대한 학술 실증은 엇갈린다. Deleidi, Mazzucato & Semieniuk (2020)은 재생에너지 발전 프로젝트에서 공공 직접투자가 민간투자를 구축(crowding-out)하지도, 명확히 견인(crowding-in)하지도 않는다는 실증 결과를 제시하며, 거시경제적 구축효과 개념을 부문 단위(섹터-레벨) 연구에 그대로 적용하는 것은 부적절하다고 주장한다. 즉 "정부가 어디까지 내려가야 크라우딩아웃이 시작되는가"에 대한 합의된 임계값은 학술적으로 확립되어 있지 않다.

[Deleidi, M., Mazzucato, M. & Semieniuk, G. (2020), "Neither crowding in nor out: Public direct investment mobilising private investment into renewable electricity projects", *Energy Policy*, 140, 111195 | https://doi.org/10.1016/j.enpol.2019.111195]

**최적 첫손실 규모에 대한 정형화된 이론**(예: 신용보증에서 최적 tranche 크기를 도출하는 공공경제 모형)은 이번 검색에서 CAP의 층 구조에 바로 대응시킬 만한 단일 정설을 찾지 못했다 — 실무 규제 기준(예: 인도 RBI가 대출 포트폴리오의 5%까지 첫손실 보증을 허용한다는 보고)은 있으나 이는 규제 관행이지 이론적 최적치 도출은 아니다. 이 항목은 아래 미확인에도 표시.

[참고: 신용 tranche 구조에 관한 일반 논의 — CBO, "Public-Private Risk Sharing in Federal Credit Programs" | https://www.cbo.gov/publication/60713]

**CAP이 취할 수 있는 정직한 입장**: "정부가 catastrophe 층만 져야 한다"는 규범적 처방을 이론(Arrow-Lind)에서 직접 연역할 수 없다 — 그 조건이 이 위험에는 안 맞기 때문이다. 대신 CAP은 분포 형태(어느 구간이 기업 자기자본으로 흡수 가능하고 어느 구간이 꼬리인지)를 계량적으로 보여주는 데 그치고, "이 지점부터는 시장에 남기면 프로젝트가 좌초한다"는 실증적 관찰과 "이 지점부터는 정부가 만든 위험이라 정부가 재보험하는 순환이 발생한다"는 구조적 관찰을 **분리해서** 제시해야 한다.

---

## 정직한 정책 함의의 형태

CAP 분포가 정부에 줄 수 있는 것과 줄 수 없는 것을 구분한다.

1. **줄 수 있는 것 — 위험 이전의 회계.** "분포의 상위 X%(catastrophe 층)는 현재 기업 대차대조표로 흡수 불가능한 규모이며, 이를 CCfD 등으로 정부가 흡수할 경우 예상 재정부담은 Y, 꼬리 시나리오에서 Z"라는 정량적 서술. 이는 Wolf (2025)식 "위험 이전 회계" 프레임과 동일한 성격 — 위험이 어디서 어디로 옮겨가는지 크기를 보여주는 것.

2. **줄 수 없는 것 — 사회적 가치 판단.** "정부가 이 층을 지는 것이 사회적으로 최적이다/싸다"는 주장은 CAP 분포 자체에서 나오지 않는다. Arrow-Lind가 성립하지 않는 위험(정책이 내생적으로 만드는 위험)에 대해 "정부가 지면 거의 공짜"라는 논거를 재사용하면 안 된다 — 이는 위 절에서 확인한 이론적 조건 위반이다.

3. **경계해야 할 순환.** "정부가 만든 위험을 정부가 진다"는 구조(CCfD ← 탄소가 ← 정책)를 CAP이 "정부 개입이 필요하다"는 결론의 근거로 쓰면 논리적으로 자기지시적(self-referential)이 된다. 정직한 서술은: "이 위험층의 존재 자체가 정책설계(감축 경로의 신뢰성)에 달려 있으므로, CAP이 보여주는 catastrophe 층의 크기는 고정된 자연 상수가 아니라 정책 신뢰성의 함수다"라는 조건부 서술이어야 한다. Kydland-Prescott/Helm-Hepburn-Mash 계열 문헌이 이 조건부성을 뒷받침한다.

4. **쓰는 법.** CAP 논문/브리프에서는 "정부가 하방을 잘라야 한다"는 처방형 문장 대신, "분포의 이 구간은 (a) 현재 민간이 못 지는 규모이고 (b) 정부가 지려면 자신이 만든 위험을 재보험하는 형태가 되므로 (c) 신뢰성 장치(규칙 기반 감축 경로, 독립기구, 사전 재원조달) 없이 이 층을 정부에 넘기면 시간불일치 문제가 재정 비용으로 재귀한다"는 조건부·기술형 문장으로 쓴다. 사회후생 극대화를 주장하지 않는다.

---

## 미확인

- Mechler & Hochrainer-Stigler (2014)의 본문 논증 세부(수식·모형)는 페이월로 접근하지 못해 제목·초록·2차 인용 수준에서만 확인했다. 서지사항(저자·저널·권호·페이지)은 검색으로 교차 확인됨.
- Baumstark & Gollier (2013/2014) 논문 본문은 PDF 파싱 실패로 읽지 못했다 — 제목·저자·소속(TSE)만 확인. 정식 출판 저널·연도(HAL 워킹페이퍼인지 저널 게재본인지)는 검색 결과가 엇갈려(HAL 2013 vs 저널 2014 언급) 최종 확정하지 못함.
- "최적 첫손실(first-loss) 규모"를 도출하는 표준 이론 논문 — 이번 검색 범위에서 CAP의 layer 구조에 직접 대응하는 정설 논문을 특정하지 못했다. Arrow-Lind 계열과 신용보증 tranche 실무 문헌은 확인했으나 이 둘을 통합한 단일 이론 논문은 미확인으로 남긴다.
- 인도 RBI의 "첫손실 보증 5% 상한" 서술은 실무 보고 성격의 2차 출처(웹 검색 요약)에서 나온 것으로, 원 규제문서를 직접 확인하지 않았다.
- CCfD의 캐나다 사례(2024 연방예산, Canada Green Bond Fund 백스톱)는 로펌(Miller Thomson) 해설 기사 기반이며, 원 예산문서·정부 1차 자료는 직접 확인하지 않았다.
