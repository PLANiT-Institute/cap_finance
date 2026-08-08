# CAP 데이터 수집 가이드 (Cowork용)

**작업 대상 파일:** `data/CAP_data_collection_template.xlsx`
**기준 사양:** `REDESIGN_SPEC.md` §2 (컬럼 정의·단위는 그 문서와 템플릿 5행이 최종 기준)
**이 문서만 읽고 작업 가능하도록 작성됨. 대화 맥락 불필요.**

---

## 1. 과제 요약

탈탄소 전환비용 분석 프로젝트의 입력 데이터 수집. 대상 기업 4사:

| 기업 | 국가 | 섹터 | 분석 대상 사업장 |
|---|---|---|---|
| POSCO (포스코, 철강법인) | 한국 | 철강 | 포항, 광양 |
| Nippon Steel (일본제철) | 일본 | 철강 | 국내 제철소 전체 (기미쓰·나고야·야하타 등) |
| LOTTE Chemical (롯데케미칼) | 한국 | 석유화학 | 여수(기초·첨단), 대산, 울산 |
| Mitsui Chemicals (미쓰이화학) | 일본 | 석유화학 | 국내 주요 콤비나트 (이치하라·오사카 등) |

수집 결과는 엑셀 템플릿의 시트 10개를 채우는 것. 각 시트가 나중에 CSV 1개로 변환되어 분석 코드에 입력된다.

## 2. 절대 규칙

1. **값을 지어내지 않는다.** 못 찾으면 셀을 비우고 `quality_note`(또는 인접 셀 메모)에 "확보 불가 — 사유" 기록. 빈칸은 허용, 허위값은 프로젝트 전체를 오염시킴.
2. **모든 값에 `source_id` 필수.** 값을 적기 전에 `source_register` 시트에 출처를 먼저 등록. URL은 랜딩 페이지가 아니라 해당 문서·표에 도달 가능한 구체 주소. `location` 필드에 페이지·표 번호까지.
3. **원 출처의 단위·통화·기간·경계를 그대로 보존.** 환산(엔→원, 명목→실질)은 하지 않는다 — 코드가 수행. 단위 컬럼에 원 단위 명기.
4. **보고·규제값 > 회사 공시값 > 제3자 추정값** 순서. 추정값 사용 시 `quality_note`에 추정 주체·방법 기록.
5. **Scope 1과 Scope 2는 절대 합산하지 않는다.** 합산값만 공시된 경우 합산값을 적고 `quality_note`에 "S1+S2 합산만 공시" 기록.
6. **템플릿 구조 변경 금지.** 4행 컬럼명 수정·추가 금지(분석 코드가 이 이름을 읽음). 6행 회색 예시행은 실제 입력 시작 시 삭제.
7. 수집 중 판단이 필요한 경계 사례(예: 어느 법인 경계인지 불명확)는 임의 결정하지 말고 `quality_note`에 선택지를 기록하고 진행.

## 3. 작업 순서와 우선순위

```
1순위 (공개·정형 데이터, 즉시 착수):  source_register 등록 병행
  D4 가격 이력  →  D2a/D2b 시나리오
2순위 (핵심·노동집약):
  D1a 시설 기본  →  D1b 시설 패널
3순위:
  D3 기술 비용  →  D7 공시 계획
4순위 (상대적으로 쉬움):
  D6 기업 재무  →  D5 정책지원
```

D1이 가장 중요하고 가장 오래 걸림. D4·D2를 먼저 끝내 성과를 확정한 뒤 D1에 시간을 집중할 것.

---

## 4. 시트별 지침

### D4_price_history — 가격 이력 (1순위)

목표: 월별 시계열. **smp, kau, 건설공사비지수는 최소 10년(2015~현재), 월별.**

| series_id | 내용 | 출처 |
|---|---|---|
| `smp_krw_mwh` | 계통한계가격 (육지, 가중평균) | 전력거래소 EPSIS (epsis.kpx.or.kr) — 통계 > 전력시장 > SMP |
| `indus_tariff` | 산업용(을) 전력 평균판매단가 | 한전 전력통계월보 / KEPCO 사이버지점 |
| `kau_krw` | K-ETS 배출권(KAU) 종가 | KRX 배출권시장 정보플랫폼 (ets.krx.co.kr) |
| `lng_import` | LNG 수입단가 | 관세청 수출입무역통계 or 에너지통계월보 (KEEI) |
| `coal_import` | 원료탄(coking coal) 수입단가 | 관세청 / KEEI 에너지통계월보 |
| `constr_cost_idx` | 건설공사비지수 | 한국건설기술연구원 (kict.re.kr) 매월 공표 |
| `equip_import_idx` | 자본재 수입물가지수 | 한국은행 ECOS (ecos.bok.or.kr) |
| `electrolyzer_capex` | 수전해 설비 단가 (연도별 글로벌 추정 허용) | IEA Global Hydrogen Review (연간, 무료 PDF), BNEF 인용치는 2차 인용 출처 명기 |
| `usdkrw` | 원/달러 환율 (월평균) | 한국은행 ECOS |
| `cpi` | 소비자물가지수 (2020=100) | 통계청 KOSIS / ECOS |

일본 쪽 보조 시리즈(JEPX 현물가, 일본 CPI, JPY/KRW)는 여유 있으면 추가 — series_id는 `jepx_spot`, `cpi_jp`, `jpykrw`로.

**완료 기준:** 필수 3개 시리즈 월별 10년+, 나머지 최소 5년 또는 가용 전 기간.

### D2a/D2b — 시나리오 (1순위)

출처: **NGFS Scenario Explorer** (IIASA 호스팅, 무료 가입 후 다운로드. data.ene.iiasa.ac.at/ngfs). 모형 = **GCAM 6.0 NGFS**, Phase 5.

- `NZ15` ← NGFS "Net Zero 2050" / `B20` ← NGFS "Below 2°C"
- 지역: 한국·일본 개별 지역이 없으면 해당 R10 권역값을 쓰고 `quality_note`에 권역명 기록
- D2a 변수: 철강 = `Emissions|CO2|Energy|Demand|Industry|Steel` 계열, 화학 = `...|Chemicals` 계열. 정확한 변수명이 다르면 가장 근접한 변수 사용 후 변수명 원문을 `quality_note`에 기록
- D2b 변수: 전력가격(`Price|Secondary Energy|Electricity`), 수소가격(`Price|Secondary Energy|Hydrogen`), 탄소가격(`Price|Carbon`), 석탄·가스 1차에너지 가격
- 연도: 2025~2050, 5년 간격
- NGFS에 섹터 해상도가 부족한 항목은 IEA (Iron & Steel Technology Roadmap, The Future of Petrochemicals)로 보완하고 별도 source_id

### D1a_facility_static — 시설 기본 (2순위, 최중요)

행 단위 = **설비 1기** (고로 1기, BOF shop, EAF 1기, NCC 1기 등). 사업장 합계 아님.

| 기업 | 출처 |
|---|---|
| POSCO | 기업시민보고서·ESG 데이터북, 사업보고서(DART), 고로 개수 보도자료 (포항 2·3·4고로, 광양 1~5고로 각각의 최근 개수 연도), 파이넥스 설비 |
| Nippon Steel | **Data Book (통합보고서 부속, IR 페이지)** — 제철소별 설비 목록·고로 기수·용적 수록. 개수 이력은 보도자료 |
| LOTTE Chemical | ESG 보고서, 제품·공정 기술 가이드 (NCC 에틸렌 100만t/여수 등), 사업보고서 |
| Mitsui Chemicals | ESG 데이터·유가증권보고서(EDINET), 공장 소개 페이지 |

핵심 필드 = `next_reinvest_year` (재투자 창). 고로: 최근 개수 연도 + 개수 주기(15~20년, 실적 기반). NCC/분해로: 대정비 주기. **공표된 계획이 있으면 그것을 우선**, 없으면 `last_reline_year + reinvest_cycle_yr`로 계산하고 `quality_note`에 "계산값" 표기.

**완료 기준:** 4사 합계 주요 배출 설비 커버리지 — 각사 Scope 1의 80% 이상을 설명하는 설비 목록.

### D1b_facility_panel — 시설×연도 패널 (2순위)

기간: **2020~최신** (가용하면 2015~).

| 국가 | 시설 배출 출처 |
|---|---|
| 한국 | **환경부 온실가스종합정보센터(GIR) 명세서 배출량 공개** — 공공데이터포털(data.go.kr) "온실가스 배출량 명세서" 사업장 단위. 할당대상업체 지정 현황도 참조 |
| 일본 | **환경성 온실가스 배출량 산정·보고·공표제도(SHK/EEGS)** — ghg-santeikohyo.env.go.jp 사업소 단위 공표 |

생산량: 회사 공시(제철소별 조강, 콤비나트별)가 없으면 사업장 능력 비례 배분하지 말고 빈칸 + note. 에너지: 회사 환경데이터의 사업장별 값이 있으면 사용, 전사값만 있으면 전사값 행(facility_id = `<회사>_TOTAL`)으로 별도 기록.

### D3_tech_options — 기술 비용 (3순위)

섹터별 필수 옵션:

- 철강: `steel_eaf`(스크랩 EAF 전환), `steel_h2dri`(수소환원제철), `steel_ccus`(고로+CCUS), `steel_eff`(효율 개선), `steel_finex_h2`(가용 시)
- 석화: `petchem_ecracker`(전기 분해로), `petchem_h2fuel`(수소 연료 전환), `petchem_ccus`, `petchem_bio`(바이오나프타/순환원료), `petchem_eff`

출처 우선순위: ① IEA Iron and Steel Technology Roadmap / The Future of Petrochemicals ② Mission Possible Partnership (steel/chemicals Sector Transition Strategy) ③ 학술 (H2-DRI: Vogl et al. 2018 등) ④ 회사 공시 투자액 (HyREX 실증 투자 발표 등). CAPEX 원단위는 출처 간 편차가 크므로 **복수 출처를 각각 행으로 기록**해도 됨 (`tech_id`에 `_alt` 접미사) — 대표값 선택은 분석 단계에서.

### D7_disclosed_plan — 공시 계획 (3순위)

각사 탄소중립 로드맵·중기 경영계획·IR 자료에서 **실행 약속만** 추출 (비전 선언 제외). 반드시 `quote`에 원문 인용.

- POSCO: 2050 탄소중립 로드맵, HyREX 실증 일정, 광양 전기로(2026 가동) 발표, 재생에너지·PPA 계약 공시
- Nippon Steel: COURSE50/Super COURSE50 일정, 야하타·히로하타 등 **대형 EAF 전환 결정 공시**(투자액·가동 연도 포함), GX 관련 발표
- LOTTE Chemical: 2030 탄소중립성장 로드맵, 재생에너지 조달(PPA)·CCU 발표
- Mitsui Chemicals: 카본뉴트럴 전략, 나프타 분해로 관련 발표(오사카 e-cracker 검토 등)

`resolution` 판정: 시설+연도 특정 = `high` / 기술+시기만 = `mid` / 방향 선언만 = `low`.

### D6_company_financials — 기업 재무 (4순위)

기간 2020~최신. **경계 주의:** POSCO는 지주사(POSCO홀딩스)가 아니라 **철강법인 포스코** 별도 재무 기준 — DART 포스코 감사보고서. Nippon Steel·Mitsui는 유가증권보고서(EDINET) 연결 기준으로 적되 `quality_note`에 "연결" 명기. LOTTE Chemical은 DART 별도 기준.

### D5_policy_support — 정책지원 (4순위)

- 한국: K-ETS 4차 계획기간(2026~) 유상할당 비율, 조세특례제한법 국가전략기술(수소환원제철 포함 여부) 세액공제율, 산업부 탄소중립 산업핵심기술개발 보조
- 일본: GX-ETS 단계별 규칙, GX 경제이행채 기반 지원(수소환원제철 보조 — 그린 이노베이션 기금 프로젝트 금액), CCfD형 수소 차액지원 (価格差支援) 파라미터
- `support_scenario`: 현행 확정 제도만 `current`, 발표·검토 단계는 `enhanced`

---

## 5. 진행 관리

- 시트마다 마지막 열 다음에 메모 쓰지 말 것 — 모든 코멘트는 `quality_note`/`quote` 필드 안에.
- 하루 작업 종료 시 파일 저장 위치 유지 (`data/CAP_data_collection_template.xlsx` 덮어쓰기, 사본 만들지 않기).
- 진행률 보고 형식: 시트별 `채운 행 수 / 완료 기준` + 막힌 항목 목록 (무엇을, 어디서 찾았으나, 왜 실패).

## 5-1. 2차 수집 (1차 실행 진단 반영 — 우선순위 최상)

1차 실행 결과 효율 경계 형성에 필요한 데이터가 부족했다. 아래 항목은 기존 시트에 **추가 행/열**로 수집한다.

### A. 기술 DB 확충 (D3 — 최우선)

섹터당 7~8개 수단, **부분 감축 수단 포함**. 반드시 운영비(opex) 포함 완전 비용, 출처 2개 이상 병기(`_alt` 행).

| 섹터 | 필수 추가 수단 | 비고 |
|---|---|---|
| 철강 | 수소취입(고로 부분감축, COURSE50형), 스크랩 배합 증대, HBI/펠릿 장입, BF 가스재활용(TGR), FINEX→HyREX 경로(별도 행) | 기존 수소환원 행은 opex 보완 |
| 석화 | 전기가열 분해로(단계: 하이브리드/완전), 열펌프·폐열, 수소 연료전환 h2_intensity 실측치 | 바이오나프타 프리미엄 시장가 |

신규 컬럼: `max_applicability_pct`(해당 수단이 커버 가능한 설비 능력 비율 상한 — 스크랩 수급, 취입 한계 등), `storage_transport_cost`(CCUS 전용, 천원/tCO2).

### B. CCUS 제약 (신규 — 없으면 CCUS가 만능해가 되어 분석 붕괴)

- 한국·일본 연간 CO2 저장 가능량 전망(정부 로드맵: 한국 2030 4Mt/2050 30Mt급, 일본 연 6~12Mt 목표), 기업별 확보 프로젝트(포스코-동해, 일본 서일본 허브 등)
- 포집+수송+저장 비용 분리 (천원/tCO2)

### C. 수소 외부 조달 가격 (D2b·D4 — 구조 변경)

수소는 자가 생산이 아니라 **외부 구매**로 모형화한다.
- D2b `h2_price`: 국가별 공급단가 경로(청정수소 입찰가, CfD 낙찰가, 수입 암모니아 크래킹 단가) — 기존 수집분 보강
- D4 신규 시리즈 `h2_contract_krw_kg`: 청정수소 발전 입찰(CHPS) 낙찰가, 일본 보조 기준가 등 **변동성 캘리브레이션용 시계열** (없으면 LNG 변동성 프록시 명기)

### D. 재생에너지 전력 분리 (D2b·D4 — 구조 변경)

전환 기술의 전력은 재생 조달로 별도 가격을 쓴다.
- D2b 신규 변수 `re_price`: 기업 재생 PPA 체결가 수준 경로 (한국 RE100 PPA 실거래대, 일본 corporate PPA)
- D4 신규 시리즈 `re_ppa_krw_mwh`: REC+SMP 합산가 또는 공표 PPA 가격 시계열

### D-2. 제품 마진 (신규 — 조기폐쇄 옵션 요건)

조기폐쇄의 기회비용 = 상실 마진. 없으면 폐쇄가 공짜 감축이 되어 모형에 넣을 수 없다.
- D4 신규 시리즈: `steel_spread_krw_t`(열연-원료 스프레드 또는 t당 영업마진 근사), `ethylene_naphtha_spread`(에틸렌-납사 스프레드, USD/t) — 연별 5년+ 이력
- 출처: 철강협회/업계 리서치, ICIS/플랫츠 인용 2차 자료 허용 (출처 명기)

### E. 시설 보완 (D1a)

- 포항 2고로 내용적/능력 (현재 탈락 상태), 고로별 공칭 능력 공식값
- 제철소별(포항/광양, 각 제철소) 생산·에너지 실적 — 배분 가정 축소용
- FINEX 2·3공장 폐쇄/전환 계획

### F. D2 재추정 (결함 수정)

- **예산 단조성**: 모든 연도에서 B20 예산 ≥ NZ15 예산 보장. NZ15는 초반 급감형(IEA NZE 정합)으로 재보간
- 전력가: 원전 비중 대용 대신 시나리오별 발전믹스 기반 LCOE/도매가 전망 사용

## 6. 최종 완료 체크리스트

- [ ] source_register: 값이 참조하는 모든 source_id 등록, URL 접속 확인
- [ ] D4: smp·kau·constr_cost_idx 월별 10년+
- [ ] D2: NZ15·B20 × Korea·Japan × steel·petchem, 2025~2050
- [ ] D1a: 4사 Scope 1의 80%+ 커버 설비 목록, 전 설비 `next_reinvest_year` 채움(계산값 표기 포함)
- [ ] D1b: 2020~최신, 시설 단위 규제 배출값 (한 GIR / 일 SHK)
- [ ] D3: 섹터별 필수 옵션 전부, CAPEX·원단위·avail_year 채움
- [ ] D7: 4사 각 3건 이상, 전 행 quote 포함
- [ ] D6: 4사 × 2020~최신
- [ ] D5: 한·일 각 3개 수단 이상
- [ ] 6행 예시행 전부 삭제됨
- [ ] 빈칸에는 모두 사유 note 존재
