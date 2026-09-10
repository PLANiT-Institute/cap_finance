# TCaR 연구용 Excel 통제 시스템

이 도구는 Excel의 모형 입력을 검사하고, 별도 실행 폴더에서 정수계획과 가격경로를 계산한 뒤 통합 워크북을 갱신한다. 연구판의 현금·배출권·구입 에너지·실행 가능성 규약을 사용한다. 저장된 Excel 수식만으로 최적화가 실행되지는 않는다.

정본 원고는 [TCaR 방법론](../paper/methodology/TCaR_METHOD_KO.md), 검증 과정은 [연구 기록](research_cycles/2026-09-05/RESEARCH_LOG.md)을 따른다. 루트 `config.yaml`은 과거 결과의 재현 설정이다. 새 연구판은 워크북에 포함된 별도 설정으로 실행한다.

## 작업 순서

저장소 루트에서 다음 명령을 실행한다. Python 환경에는 저장소의 프로젝트 의존성이 설치돼 있어야 한다. 출력 폴더는 아직 존재하지 않는 경로를 선택한다.

```bash
.venv/bin/python scripts/research_control.py validate \
  --workbook outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_research_control.xlsx

.venv/bin/python scripts/research_control.py run \
  --workbook outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_research_control.xlsx \
  --out-root tmp/my_research_case

.venv/bin/python scripts/research_control.py refresh \
  --run-root tmp/my_research_case \
  --out tmp/my_research_case/TCaR_updated.xlsx
```

`validate`는 변경한 셀과 거부 사유를 보여준다. `run`은 검증·내보내기·E1–E5 실행과 설정된 배출량 방향 후보 확장을 수행한다. `refresh`는 성공 실행의 입력·코드·출력 해시를 다시 확인하고 Excel을 생성·수치 검사한다. 실패하거나 완료되지 않은 실행으로는 갱신할 수 없다. 기존 워크북을 의도적으로 갱신할 때만 `refresh --replace`를 사용한다.

CSV 내보내기만 하려면 `run` 대신 `export`를 사용한다. 실행 폴더를 재사용해 과거 로그를 덮어쓰는 동작은 허용하지 않는다. 실행이 오래 걸려도 같은 폴더에 두 번째 계산을 시작하지 말고 `pipeline.log`, `expansion.log`, `control_manifest.json`을 확인한다.

Excel 생성·갱신에는 Codex 번들 Node 및 Artifact Tool이 필요하다. 기본 경로를 사용할 수 없으면 `TCAR_NODE`, `TCAR_NODE_MODULES`를 지정한다. Python 검증·내보내기·계산과 CSV 결과는 이 Excel 생성 런타임과 별개다. 현재 GitHub용 코드는 Excel 생성까지 독립적인 공개 런타임만으로 작동한다고 주장하지 않는다.

## 워크북을 읽고 수정하는 방법

| 시트 | 역할 | 수정 규칙 |
|---|---|---|
| Overview, Case results | 마지막 성공 실행의 대표 후보와 비용 | 엔진 실행 후 갱신 |
| Selected schedules, Annual capital | 선택된 44개 시설 일정과 192개 연간 자본 원장 | 엔진 실행 후 갱신, 자본 원장은 계약·지원·충격 적용 전 |
| Risk measures | 후보별 평균·중앙값·TCaR·ES·PPA·지배 관계 | 엔진 실행 후 갱신 |
| Attainable gaps | 실제 공시 비교군의 표현 가능성 | 현재 네 회사 모두 미표현, 개선액 미산출 |
| Settings | 할인율·시드·가격과정·예산·계약 프리미엄·탐색 설정 | value 열 수정 |
| Input checks | 수치·ID·단위의 변경 표시 | 수식, 직접 수정하지 않음 |
| D1a–D6, D3b | 설비·생산·배출·가격·기술·재무의 모형 입력 | 노란 수치 셀 수정 |
| D7 | 공시 커밋과 현재 검토 상태 | 정확한 기술·설비·시점 검토 전에는 수정 입력으로 사용하지 않음 |
| Primary observations | 원문에서 확인한 수치와 범위·단위·원문 위치 | 원문 관측, 직접 변경하지 않음 |
| Energy assumptions | 기술별 구입 에너지 잔존 가정 | D3를 수정하고 실행·갱신하면 반영 |
| Parameters | FIN·EFF 기존 모수의 증거·범위 등록부 | 모형의 직접 입력 시트가 아님 |
| Sources, Literature, Issues | 출처·문헌 확인 범위·검증 과제 | 검증 기록을 갱신한 뒤 재생성 |
| Control schema | 기준 입력 CSV·설정·해시 | 자동 저장, 직접 변경하지 않음 |

표를 정렬해도 내보낼 때 원래의 레코드 순서를 복구한다. ID 중복·삭제, 단위 변경, 열 이름 변경, 필수값 결측, 숫자 대신 문자열, 범위 밖 잔존율, 입력 수식은 거부한다. 모형이 이미 명시한 결측은 유지하며 0으로 채우지 않는다. 원문 또는 결과 시트의 수치를 직접 바꾼 경우도 검증에서 거부한다.

표시 수식은 짧은 수치·ID·단위 변경을 알려준다. 긴 출처 문장, 입력 수식 및 참조표 전체의 검사는 Python 검증기가 수행한다. Overview의 변경 표시가 없다는 사실은 외부 데이터의 정확성 또는 모든 검증 통과를 뜻하지 않는다.

이 판본은 기존 22개 모형 설비와 기술 목록 안의 수치 가정을 통제하는 고정 템플릿이다. 설비·기술·국가를 추가하거나 단위를 바꾸려면 원자료, 스키마, 기술 적용 범위와 공시 매핑을 검토하고 새 템플릿을 생성해야 한다. 실제 회사 명부를 Excel에서 임의로 늘려 완전한 기업 경계처럼 만들지 않는다.

## 현재 실행에서 쓰이는 입력

노란 셀은 수정·추적 가능한 입력이라는 뜻이며 모두가 기본 목적함수에 직접 쓰인다는 뜻은 아니다. D3b의 범위는 기본 E1–E5에서 모수 표본 추출에 사용하지 않는다. D5는 현재 지원 시나리오 `none`에서 비활성이며 경매비율을 총 탄소의무 비용에 곱하지 않는다. D4도 지정된 계열과 충분한 관측 수에 따라 사용되므로 모든 이력 행이 활성 요인은 아니다. D6은 재무 참조이며 설비·위험 경계를 직접 최적화하지 않는다. 새 기능으로 범위를 활성화하려면 모형 규약을 명시하고 별도 검증해야 한다.

## 변경 예시

D3의 `petchem_h2fuel` 행, `retained_gas_fraction` 열을0.50에서0.25로 바꾼다. 이 값은 기존 구매 가스 중 유지되는 비율이다. 효율·내부 부산물 열수지가 확인된 측정값이라는 뜻은 아니다.

저장하면 Overview는 재실행 필요를 표시한다. `validate`가 기술 ID·필드·이전값·변경값을 보고한다. `run`은 원문 관측을 유지하고 바뀐 모형 행을 `user_assumption_override`로 표시한다. 잔존 에너지 가정 등록부에도 변경을 반영한다. `refresh` 후에는 새 입력이 기준 스냅샷이 되며 이전 변경은 실행 기록에 남는다.

재무 숫자를 수정하면 해당 행의 원문 검증 상태를 해제한다. 변경 EBITDA를 여전히 검증된 공시 EBITDA로 취급하지 않으며, 엄격한 자금규모 비교 요건을 충족하지 않는 비율은 미산출한다.

## 실행 폴더

| 파일·폴더 | 내용 |
|---|---|
| `data/` | 실행용 입력, 원자료 폴더를 덮어쓰지 않음 |
| `config.yaml` | 워크북 설정과 이 실행의 경로 |
| `control_manifest.json` | 워크북 해시·변경 셀·입력 해시·실행 상태 |
| `pipeline.log` | 원래 후보 생성과 재평가 기록 |
| `run/run_manifest.json` | 단계별 실행과 입력·코드·출력 해시 |
| `expanded/` | 설정한 경우의 배출량 방향 후보 확장과 재평가 |
| `workbook_validation.json` | 갱신된 Excel의 표·수식·입력 계약 검사 |
| `workbook_previews/` | 갱신된 워크북의 시트별 검토 화면 |

새로운 입력이나 결과를 과거 실행 파일에 수동으로 섞지 않는다. 소스 또는 저장 결과가 실행 이후 바뀌면 갱신은 중단한다. 보고하려는 실행의 manifest와 입력 범위를 먼저 확인한다.

## 검증과 해석 범위

회차6의 무수정 왕복에서17개 CSV는 원본과 바이트 단위로 일치했고,450개 후보의5개 통계량2,250개는 재실행 후에도 차이가0이었다. 별도 위험 계산도 이 결과를 재검증했다. [왕복 검증](research_cycles/2026-09-05/excel_control/roundtrip_reproduction.json).

현재 연구 사례는2027–2050년 고정 생산, 폐쇄 없음, 누적 Scope1 예산, 명시적 갱신 투자, 종료 수입0, 총 탄소의무 가격 노출을 사용한다. 공시 비교군은0개다. 조건부 계산의 일치가 기업 전체 설비 범위, 실제 할당량, 열·부산물 수지 또는 미래 가격분포의 정확성을 입증하지 않는다. TCaR는 P90−P50 간격이며 단독 자본 요구량이 아니다. 평균·ES·현금흐름과 함께 해석한다.

원천 데이터·설비별 스냅샷·실행 결과는 로컬에 보존한다. 저장소의 설비 데이터 공개 규약을 무시하고 워크북이나 실행 폴더를 자동 업로드하지 않는다.

7회차 보강: 기준 450개 후보의 다섯 통계량이 모두 일치하는 실행에만 Analytic means, Sampling intervals, Sensitivity, Equivalent plans의 네 감사 시트를 첨부한다. 다른 입력의 계산에는 기준 민감도·구간을 승계하지 않는다. 현재 기본 워크북은 29개 시트·25,179개 표 셀·526개 입력 검사행을 대조했으며 수식 오류는 0개다.

환경 점검: `.venv/bin/python scripts/research_control.py doctor`는 Python 패키지·CBC 솔버·선택적 Excel 런타임의 준비 여부를 출력한다.
