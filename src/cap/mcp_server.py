"""CAP MCP 서버 — 결과·증거·감사 결과를 도구로 노출 (stdlib 전용, stdio JSON-RPC).

설계 원칙
  - **읽기 전용**. 파이프라인을 돌리지 않는다. `out/`에 있는 것만 답한다.
  - **모든 수치는 출처를 달고 나간다**: 파라미터 조회는 tier·source_id·범위를 함께 반환.
  - **시설 단위는 기본 거부** (설계서 §8-2). 기업 집계만 공개.
  - 산출물이 없으면 추측하지 않고 "먼저 실행하라"고 답한다.

등록:
    claude mcp add cap -- /path/to/.venv/bin/python -m cap.mcp_server
수동 확인:
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | .venv/bin/python -m cap.mcp_server
"""

from __future__ import annotations

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "out"
DOCS = ROOT / "docs"
PROTOCOL_VERSION = "2024-11-05"


# ------------------------------------------------------------------ 자료 접근

def _rows(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _num(v):
    if v in (None, "", "nan", "NaN"):
        return None
    try:
        f = float(v)
    except ValueError:
        return v
    return int(f) if f.is_integer() and abs(f) < 1e15 else round(f, 4)


def _clean(rows: list[dict], keep: list[str] | None = None) -> list[dict]:
    return [{k: _num(v) for k, v in r.items() if keep is None or k in keep} for r in rows]


def _filter(rows: list[dict], **eq) -> list[dict]:
    for k, v in eq.items():
        if v is not None:
            rows = [r for r in rows if str(r.get(k, "")).upper() == str(v).upper()]
    return rows


def _stale_note() -> str:
    m = OUT / "e5" / "metrics_company.csv"
    if not m.exists():
        return ""
    import datetime
    ts = datetime.datetime.fromtimestamp(m.stat().st_mtime)
    return f"(산출물 생성 시각 {ts:%Y-%m-%d %H:%M})"


# ------------------------------------------------------------------ 도구 구현

def t_list_companies(_):
    rows = _rows(OUT / "e5" / "metrics_company.csv")
    names = {"POSCO": "POSCO (철강, 한국)", "NSC": "Nippon Steel (철강, 일본)",
             "LOTTE": "LOTTE Chemical (석유화학, 한국)", "MCI": "Mitsui Chemicals (석유화학, 일본)"}
    ids = sorted({r["company_id"] for r in rows})
    return {"companies": [{"company_id": c, "label": names.get(c, c)} for c in ids],
            "scenarios": sorted({r["scenario"] for r in rows}),
            "support_scenarios": sorted({r["support"] for r in rows}),
            "note": _stale_note()}


def t_get_metrics(a):
    rows = _filter(_rows(OUT / "e5" / "metrics_company.csv"),
                   company_id=a.get("company_id"), scenario=a.get("scenario"),
                   support=a.get("support"))
    return {
        "definitions": {
            "capex_total_bnkrw": "① 전환 총 자본지출 (십억원, 공사기간 분산)",
            "capex_peak_year": "① 자본지출 피크 연도",
            "p50_bnkrw": "② 기대 전환비용 = 자원비용 NPV의 P50 (탄소비용 분리)",
            "cost_per_tco2_thkrw": "② 감축 단가 (천원/tCO₂, 할인 감축량 기준)",
            "tcar_bnkrw": "③ TCaR = P90 − P50, 가격 변동에서만 발생",
            "policy_exposure_bnkrw": "④ 시나리오 간 비용 차 (NZ15 − B20)",
            "flex_value_bnkrw": "⑤ 경로별 계획 전환 가치의 하한",
        },
        "sampling_error": ("시드 5개 기준 변동계수 — ② 0.3~0.8%, ③ TCaR 1.1~1.8%, "
                           "⑤ 유연성 3~9%. ③은 두 자리, ⑤는 자릿수 하나로만 읽는다 "
                           "(docs/seed_stability.md)."),
        "rows": _clean(rows), "note": _stale_note()}


def t_get_affordability(a):
    rows = _filter(_rows(OUT / "e5" / "affordability.csv"),
                   company_id=a.get("company_id"), scenario=a.get("scenario"),
                   support=a.get("support"))
    return {
        "definitions": {
            "ebitda_ref_bnkrw": "기준이익 = 최근 3개 회계연도 EBITDA 평균 (D6 공시)",
            "capex_peak_to_ebitda": "피크연도 CAPEX ÷ 기준 EBITDA (1배 초과 = 외부조달 필수)",
            "netdebt_to_ebitda_post": "전액 차입 가정 상한 — 조달 구성 예측이 아님",
        },
        "caveat": "기준 EBITDA가 0 이하인 기업은 비율을 산출하지 않는다(의미 없음). "
                  "net_debt 미공시 기업은 레버리지 항목이 null.",
        "rows": _clean(rows), "note": _stale_note()}


def t_get_frontier(a):
    rows = _rows(OUT / "e5" / "frontier_points.csv")
    rows = _filter(rows, company_id=a.get("company_id"), scenario=a.get("scenario"),
                   support=a.get("support"))
    if a.get("on_frontier_only", True):
        rows = [r for r in rows if str(r.get("on_frontier")).lower() == "true"]
    keep = ["plan_id", "company_id", "scenario", "support", "p50", "p90", "tcar",
            "ppa_share", "epc", "ccfd", "capex_total", "capex_peak", "capex_peak_year",
            "abated_tco2_disc", "is_disclosed", "on_frontier", "budget_ok"]
    return {"axes": "가로 p50 = 기대 전환비용(십억원), 세로 tcar = P90−P50(십억원). "
                    "경계 위 점은 같은 기대비용에서 더 낮은 꼬리위험이 없는 계획.",
            "rows": _clean(rows, keep), "note": _stale_note()}


def t_get_gap(a):
    rows = _filter(_rows(OUT / "e5" / "gap.csv"), company_id=a.get("company_id"),
                   scenario=a.get("scenario"), support=a.get("support"))
    return {"meaning": "공시 계획 좌표와 효율 경계 사이의 거리. gap_cost = 같은 위험에서 "
                       "더 쓸 수 있었던 비용, gap_risk = 같은 비용에서 더 줄일 수 있었던 꼬리위험.",
            "rows": _clean(rows), "note": _stale_note()}


def t_get_parameter(a):
    rows = _rows(DOCS / "parameter_inventory.csv")
    q = (a.get("query") or "").lower()
    if q:
        rows = [r for r in rows if q in json.dumps(r, ensure_ascii=False).lower()]
    tier = a.get("tier")
    if tier:
        rows = [r for r in rows if r.get("evidence_tier", "").upper() == tier.upper()]
    return {"tier_scale": {"T1": "규제·검증·법정 공시", "T2": "기업 1차 공시",
                           "T3": "동료심사·공적기관", "T4": "업계·시장 인용",
                           "T5": "모델 추정 (범위 필수)"},
            "count": len(rows), "rows": _clean(rows[:200]),
            "truncated": len(rows) > 200}


def t_get_sensitivity(a):
    rows = _rows(ROOT / "out" / "sensitivity" / "ranking.csv")
    n = int(a.get("top", 15))
    return {"method": "E2 계획 집합을 고정하고 E4/E5 경제성만 ±30%(또는 인벤토리 범위) "
                      "재평가한 OAT 스크리닝. 계획 선택 채널은 전체 재실행으로 별도 확인.",
            "rows": _clean(rows[:n])}


def t_get_data_audit(_):
    rows = _rows(DOCS / "data_audit.csv")
    tally: dict[str, int] = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    flagged = [r for r in rows if r["verdict"] != "ok"]
    md = DOCS / "data_audit.md"
    warn = []
    if md.exists():
        body = md.read_text(encoding="utf-8")
        warn = [ln[2:] for ln in body.splitlines() if ln.startswith("- ") and ":" in ln]
    return {"verdict_tally": tally, "flagged_columns": _clean(flagged),
            "provenance_warnings": warn,
            "meaning": "UNUSED = 수집했으나 엔진이 읽지 않는 컬럼, CONSTANT = 전 행 동일값, "
                       "EMPTY = 스키마 필수인데 빈칸. 합성 샘플 누출은 감사 실행 자체를 실패시킨다."}


def t_get_validation_summary(_):
    out: dict = {"available": {}, "missing": []}
    for label, p in [("data_audit", DOCS / "data_audit.md"),
                     ("parameter_inventory", DOCS / "parameter_inventory.csv"),
                     ("sensitivity_ranking", ROOT / "out" / "sensitivity" / "ranking.csv"),
                     ("cross_model_check", DOCS / "cross_model_check.md"),
                     ("validation_backtest", DOCS / "validation_backtest.md"),
                     ("validation_external", DOCS / "validation_external.md"),
                     ("seed_stability", DOCS / "seed_stability.md"),
                     ("robustness_structural", DOCS / "robustness_structural.md"),
                     ("process_alternative", DOCS / "process_alternative.md"),
                     ("methodology", ROOT / "METHODOLOGY.md")]:
        (out["available"].__setitem__(label, str(p.relative_to(ROOT)))
         if p.exists() else out["missing"].append(label))
    conv = OUT / "e4" / "convergence.csv"
    if conv.exists():
        rows = _clean(_rows(conv))
        worst = max((abs(r.get("p50_reldiff") or 0) for r in rows), default=0)
        out["monte_carlo_convergence_max_reldiff_pct"] = round(100 * worst, 2)
    out["note"] = ("missing 항목은 아직 만들지 않은 검증이다. 없는 것을 있다고 답하지 않는다.")
    return out


def t_get_data_package_manifest(_):
    p = ROOT / "data" / "package" / "manifest.json"
    if not p.exists():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))


def t_get_facility_detail(_):
    raise PermissionError(
        "시설 단위 산출은 공개 대상이 아니다 (설계서 §8-2). 기업 집계만 조회 가능하다. "
        "시설 결과가 필요하면 저장소 소유자에게 out/render/facility_confidential 접근을 요청하라.")


TOOLS = [
    ("list_companies", "분석 대상 기업·시나리오·지원시나리오 목록", {}, t_list_companies),
    ("get_metrics", "기업별 지표 ①–⑤ (CAPEX·기대전환비용·TCaR·정책노출·유연성)",
     {"company_id": "선택", "scenario": "NZ15|B20", "support": "none|current"}, t_get_metrics),
    ("get_affordability", "지표 ⑥ 조달 부담 — 전환 CAPEX 대비 EBITDA·순차입 (D6 공시 재무)",
     {"company_id": "선택", "scenario": "선택", "support": "선택"}, t_get_affordability),
    ("get_frontier", "효율 경계 점 (기대비용 × 꼬리위험 평면)",
     {"company_id": "선택", "scenario": "선택", "support": "선택",
      "on_frontier_only": "기본 true"}, t_get_frontier),
    ("get_gap", "공시 계획과 효율 경계의 거리",
     {"company_id": "선택", "scenario": "선택", "support": "선택"}, t_get_gap),
    ("get_parameter", "파라미터 인벤토리 조회 — 값·단위·증거등급·출처",
     {"query": "이름/출처 부분일치", "tier": "T1~T5"}, t_get_parameter),
    ("get_sensitivity", "결론을 좌우하는 파라미터 랭킹", {"top": "기본 15"}, t_get_sensitivity),
    ("get_data_audit", "데이터 진위·활용 감사 결과 (미사용 컬럼·출처 경고)", {}, t_get_data_audit),
    ("get_validation_summary", "존재하는 검증과 아직 없는 검증", {}, t_get_validation_summary),
    ("get_data_package_manifest", "재현 패키지 목록·해시·재실행 명령", {},
     t_get_data_package_manifest),
    ("get_facility_detail", "시설 단위 상세 — 기본 거부(비공개)", {}, t_get_facility_detail),
]
IMPL = {name: fn for name, _, _, fn in TOOLS}


def _schema(props: dict) -> dict:
    return {"type": "object",
            "properties": {k: {"type": "string", "description": v} for k, v in props.items()},
            "required": []}


# ------------------------------------------------------------------ JSON-RPC

def handle(req: dict) -> dict | None:
    mid, method, params = req.get("id"), req.get("method"), req.get("params") or {}

    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    if method == "initialize":
        return ok({"protocolVersion": PROTOCOL_VERSION,
                   "capabilities": {"tools": {}},
                   "serverInfo": {"name": "cap", "version": "2.1"}})
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": [{"name": n, "description": d, "inputSchema": _schema(p)}
                             for n, d, p, _ in TOOLS]})
    if method == "tools/call":
        name = params.get("name")
        if name not in IMPL:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32601, "message": f"unknown tool: {name}"}}
        try:
            payload = IMPL[name](params.get("arguments") or {})
            text = json.dumps(payload, ensure_ascii=False, indent=1)
        except FileNotFoundError as e:
            text = json.dumps({"error": f"산출물 없음: {e}. `python -m cap all` 실행 후 다시 조회하라."},
                              ensure_ascii=False)
        except PermissionError as e:
            return ok({"content": [{"type": "text", "text": str(e)}], "isError": True})
        except Exception as e:  # noqa: BLE001 — surface, never fabricate
            return ok({"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}],
                       "isError": True})
        return ok({"content": [{"type": "text", "text": text}]})
    return {"jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"unknown method: {method}"}}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
