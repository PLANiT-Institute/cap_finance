# CAP MCP 서버

`src/cap/mcp_server.py` — 표준 라이브러리만 쓰는 stdio JSON-RPC MCP 서버.
`out/`·`docs/`·`outputs/`에 이미 만들어진 결과를 **읽기 전용**으로 노출한다.
파이프라인을 돌리지 않으며, 산출물이 없으면 추측 대신 "먼저 실행하라"고 답한다.

## 등록

```bash
claude mcp add cap -- /Users/jinsu/Documents/GitHub/cap_finance/.venv/bin/python -m cap.mcp_server
```

`PYTHONPATH`가 필요하면 `src`를 넣는다 (패키지가 설치돼 있으면 불필요).

```bash
PYTHONPATH=src .venv/bin/python -m cap.mcp_server
```

## 도구

| 도구 | 답하는 질문 |
|---|---|
| `list_companies` | 무엇을 분석했나 (기업·시나리오·지원시나리오) |
| `get_metrics` | 지표 ①–⑤ — CAPEX, 기대 전환비용, TCaR, 정책노출, 유연성 |
| `get_affordability` | 지표 ⑥ — 그 돈을 감당할 수 있나 (EBITDA·순차입 대비) |
| `get_frontier` | 효율 경계 점 (기대비용 × 꼬리위험) |
| `get_gap` | 공시 계획이 경계에서 얼마나 떨어져 있나 |
| `get_parameter` | 이 숫자는 어디서 왔나 (값·등급·출처) |
| `get_sensitivity` | 어떤 가정이 결론을 좌우하나 |
| `get_data_audit` | 가짜·미사용 데이터가 있나 |
| `get_validation_summary` | 어떤 검증이 있고 **무엇이 아직 없나** |
| `get_facility_detail` | 시설 단위 — 기본 거부 (설계서 §8-2) |

## 설계 규칙

- 모든 응답에 정의(`definitions`)와 한계(`caveat`)를 같이 실어 보낸다. 숫자만 나가면 오독된다.
- `get_validation_summary`는 **없는 검증을 `missing`으로 명시**한다. 빈 곳을 채워 답하지 않는다.
- 시설 단위 결과는 요청해도 거부한다. 기업 집계가 공개 경계다.
- 서버는 결과를 계산하지 않는다 — `python -m cap all`이 만든 것만 읽는다. 값이 낡았으면 생성 시각(`note`)으로 드러난다.

## 수동 확인

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | PYTHONPATH=src .venv/bin/python -m cap.mcp_server
```
