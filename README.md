# TCaR — 기후 전환비용의 불확실성과 기업 내 효율경계

프로젝트의 중심은 하나다. **효율경계(frontier)를 만들어 불확실성을 줄이는 자본투자의 효율성을 재는 것.** 핵심은 `src/cap`의 E1–E5 파이프라인과 `paper/methodology/TCaR_METHOD_V2_KO.md`이고, NCC·철강 참조 원장, Excel 컨트롤, 웹의 "참조 실험" 탭, MCP 서버, 세미나 라인은 부속 또는 중심 밖이다. 분류표는 [L4 범위 규율](docs/research_cycles/2026-09-10-audit-loop/L4_scope.md)에 있다.

설비 전환 일정과 전력·건설 계약을 같은 가격경로에서 비교하는 연구 도구다. POSCO·Nippon Steel(철강), LOTTE Chemical·Mitsui Chemicals(석유화학)의 회사 정보와 추정 자산 포트폴리오를 사용한다.

[방법론 논문 v1](paper/methodology/TCaR_METHOD_KO.md), [v2 수정 노트 (2026-09-10, 정본 경계·검증 계열 요인)](paper/methodology/TCaR_METHOD_V2_KO.md), [기업 사례 Excel 사용법](docs/RESEARCH_CONTROL.md), [실제 시간 단위 연구 기록](docs/research_cycles/2026-09-07-hourly/RESEARCH_LOG.md)에서 정의·출처·계산·결론을 연결한다. [이전 검토 기록](docs/research_cycles/2026-09-05/RESEARCH_LOG.md)과 [영문 기술 가이드](docs/TECHNICAL_GUIDE.md)는 과거 실행의 감사 자료로 구분한다.

2026-09-08 통합 갱신 v4: [공동 가격·NCC 부분 비용 Excel 사용법](docs/JOINT_RESEARCH_CONTROL_KO.md). IEA 시나리오·공동 월별 충격·나프타·전력·메탄 판매를 연결하고, Control의15개·NCC cash의18개 입력을 각각 읽어 두 FIN 모형을 함께 재계산하고, 두 결과 검증 후 기존 파일을 보존하며 새 파일을 생성한다. 이 부분 모듈을 아래 450개 기업 후보의 새로운 전체 비용 재평가로 해석하지 않는다.

## 무엇을 계산하는가

- 손실은 같은 경로의 무전환 기준선에 대한 할인 **증분 현금비용**이다. 건설·기존 설비 갱신·전환 설비 갱신을 포함하고 비현금 장부손실은 분리한다.
- **TCaR90 = P90−P50**다. 중앙값 위 비용 간격이며 자금요구량이 아니다. MC 평균·P50·P90·ES90와 표본 손실 지배 검사를 함께 제공한다.
- 경계는 실제 평가한 유한 후보의 비지배점이다. 후보 사이를 보간해 실행 가능한 계획으로 해석하지 않는다.
- 현재 예산은 기간 누적 Scope1 상한이다. 연간 상한 준수와 다르다.
- 탄소중립 선언만으로 선형 DISCLOSED PLAN을 허용한다. 상세 기술 공시는 경로 생성의 전제조건이 아니다. 비용 비교에는 그 경로를 충족하는 투자 일정이 필요하며, 현 고정생산·기술 메뉴의 하한을 초과하는 경로에 가상 비용을 부여하지 않는다. 기존 정확한 기술·시설 공시 매핑 비교는 별도로 유지한다.

## 검증된 조건부 연구 사례

| 항목 | 현재 결과 |
|---|---|
| 정보 기준일 / 결정 기간 | 2026-09-05 / 2027–2050 |
| 설비 / 일정 / 계약 후보 | 추정 자산 22개 / 45개 / 450개 |
| 가격경로 | N=10,000, 평균 정규화 양수 GBM형 배율 |
| 위험 통계 대조 | 450개 × 5개 = 2,250개 |
| 누적 / 전 기간 연간예산 충족 | 45개 / 0개 일정 |
| Excel 무수정 왕복 | 입력 17개 CSV 동일, 2,250개 통계량 차이 0 |
| 원문 선택 관측 | 238개, 원문 단위·범위·위치 유지 |
| 표본·구조 검증 | 17개 설정, 7,650개 후보 평가, 105개 고정 후보 구간 |
| 통합 Excel | 기준 사례 29개 시트, 25,179개 표 셀 대조 |

두 독립 난수 표본에서 평균 최소 선택은 유지됐지만 일부 TCaR 최소 계약은 바뀌었다. POSCO NZ15에는 추정 시설 특성 때문에 같은 비용분포를 갖는 동률 일정이 있다. [민감도 감사](docs/research_cycles/2026-09-05/ROBUSTNESS_AUDIT.md)를 따른다.

시나리오 NZ15·B20은 로컬 `EST_v0` 대용치이며 다운로드한 NGFS/GCAM 데이터가 아니다. 자산 배분·구매 에너지 잔존비율·기술비용·수소 및 CAPEX 변동성에 가정이 포함된다. 원문 수치의 확인과 전체 기업·공정·미래 분포의 외부 타당성을 같은 검증으로 부르지 않는다.

## Excel 입력에서 새 결과까지

Python 3.11 이상이 필요하다. 저장소에서 설치한다.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

제공된 워크북을 작업 폴더에 두고 `Settings`와 D1a–D6의 노란 숫자 셀을 수정·저장한다. 다음은 파일명이 `TCaR_research_control.xlsx`인 경우다.

```bash
.venv/bin/python scripts/research_control.py validate --workbook TCaR_research_control.xlsx
.venv/bin/python scripts/research_control.py run --workbook TCaR_research_control.xlsx --out-root runs/my_case
.venv/bin/python scripts/research_control.py refresh --run-root runs/my_case --out TCaR_my_case.xlsx
```

`run`은 새 폴더만 허용한다. 입력·설정·코드·결과 해시, 변경 셀과 성공·실패 로그를 보존한다. 실패 실행의 결과 재수입은 거부한다. 숫자·단위·ID·수식·범위·필수 결측을 검사하고, 수정한 원문 기반 재무값은 사용자 가정으로 재분류한다.

Excel 생성·갱신에는 Codex의 Node/Artifact Tool 런타임이 필요하다. `TCAR_NODE`와 `TCAR_NODE_MODULES`로 경로를 지정할 수 있다. Python 입력 검증·내보내기·계산 및 CSV 결과는 해당 런타임 없이 사용할 수 있다. Excel 자체에서 MILP가 실행되지는 않는다.

기준 감사 시트는 450개 후보의 다섯 통계량이 기준 결과와 일치할 때만 첨부한다. 변경된 실행에 기존 민감도·구간을 자동 적용하지 않는다. 자세한 명령과 제한은 [사용법](docs/RESEARCH_CONTROL.md)에 있다.

## 검증과 저장 구조

```bash
.venv/bin/pytest tests/ -q
.venv/bin/python scripts/verify_methodology_manuscript.py
.venv/bin/python scripts/verify_research_robustness.py
```

마지막 두 명령은 감사에 사용한 로컬 결과 파일을 요구한다. 새 실행의 위험값·현금원장 확인은 `scripts/verify_research_case.py --config runs/my_case/expanded/config.yaml --out runs/my_case/audit`로 수행한다. 이 검증기는 본문과 같은 누적예산·고정생산 사례용이다.

- `src/cap`: E1 제약, E2 일정, E3 가격, E4 현금비용, E5 통계·선택.
- `scripts/research_control.py`: 워크북 검증·내보내기·실행·재수입.
- `paper/methodology`: 정본 원고와 독립 그림.
- `docs/research_cycles/2026-09-05`: 출처·반례·데이터·구현·민감도 감사와 연구 기록.
- `cap-efficient`: 독립 EFF 도구. FIN 코드와 교차 import하지 않는다.

루트 `config.yaml`은 v2 연구 규약이고, 과거 재현 규약은 `config_legacy.yaml`(`python -m cap <stage> --config config_legacy.yaml`)이다. `out/`은 과거 산출물이다. 새 사례를 재현하려면 제공 워크북의 입력과 설정을 사용한다. [과거 실행 설명](docs/LEGACY_WORKFLOW.md)은 감사 목적으로 보존했다. 시설 단위 입력과 로컬 실행·워크북·비공개 재현 묶음은 공개 배포 대상에서 제외한다.

환경 점검: `.venv/bin/python scripts/research_control.py doctor`는 Python 패키지·CBC 솔버·선택적 Excel 런타임의 준비 여부를 출력한다.

## 웹 연구 도구

[TCaR 웹 도구](https://tcar-transition-finance.vercel.app/) (`platform/`)는
K-ETS Outlook의 Next.js·React 구성과 PLANiT 화면 스타일을 따른
별도 Vercel 앱이다. 450개 기업 후보의 저장 결과(v2.2 정본, v2.1·v2.0·v1 보존), 14개 공개 데이터프레임을 보여 주고,
공동 가격·NCC 현금비용·전환 시점의 세 참조 시뮬레이터는 **부속**으로 따로 둔다(기업 경계 결과와 무관).
기업 후보 전체 MILP 재실행과 공정 참조 모형의 재계산은 구분한다.
시설 입력과 비공개 워크북은 배포하지 않는다.
데이터 갱신·로컬 실행·검증 절차는 [웹 도구 안내](platform/README.md)에 있다.
