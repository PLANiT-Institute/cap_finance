#!/usr/bin/env python3
"""Check ④ — does this repository still work as a tool?

Every cycle asked the same four questions by hand: do the tests pass, does the
audit pass, does the MCP server answer, is the tree pushed. Doing that by hand
costs minutes a cycle and, worse, gets skipped when a cycle runs late — which is
exactly when something is broken.

It does NOT run `python -m cap all`; that is a 20-minute MILP and cannot fit in
a 30-minute cycle. Instead it reports whether out/ is older than data/raw, so a
stale-output cycle is visible rather than silent.

    python3 scripts/gate.py            # human table, exit 1 if any hard check fails
    python3 scripts/gate.py --json     # machine-readable

stdlib only, so it runs with or without the venv.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python") if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable

# A failure here means the repository is broken as a tool. WARN checks report a
# state the operator must judge (stale outputs, unpushed work) — real signals,
# but not reasons to call the build red.
HARD = {"tests", "audit", "mcp", "cli", "independence"}


def run(cmd, stdin=None, timeout=900):
    p = subprocess.run(cmd, cwd=ROOT, input=stdin, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def check_tests():
    rc, out, _ = run([PY, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider"])
    tail = [ln for ln in out.strip().splitlines() if " passed" in ln or " failed" in ln or " error" in ln]
    return rc == 0, (tail[-1] if tail else "no pytest summary line")


def check_independence():
    rc, out, _ = run([PY, "-m", "pytest", "tests/test_independence.py", "-q", "-p", "no:cacheprovider"])
    return rc == 0, "FIN and EFF do not import each other" if rc == 0 else "cross-import found — H4 is circular"


def check_audit():
    rc, out, _ = run([PY, "scripts/audit_data.py"])
    counts = {}
    for line in out.splitlines():
        parts = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(parts) >= 2 and parts[1].isdigit():
            counts[parts[0]] = int(parts[1])
    summary = ", ".join(f"{k} {v}" for k, v in counts.items() if v) or "no counts parsed"
    return rc == 0, summary


def check_mcp():
    req = (
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "gate", "version": "0"}}})
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        + "\n"
    )
    try:
        rc, out, err = run([PY, "-m", "cap.mcp_server"], stdin=req, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "server did not exit on stdin close"
    for line in out.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == 2:
            if "error" in msg:
                return False, f"tools/list error: {msg['error']}"
            names = [t["name"] for t in msg.get("result", {}).get("tools", [])]
            return bool(names), f"{len(names)} tools: {', '.join(names)}"
    return False, f"no tools/list response ({err.strip().splitlines()[-1] if err.strip() else 'silent'})"


def check_cli():
    rc, out, _ = run([PY, "-m", "cap", "--help"], timeout=120)
    return rc == 0 and "e1,e2,e3,e4,e5" in out.replace(" ", ""), "python -m cap --help wires all stages"


def _newest(*globs):
    return _pick(max, *globs)


def _oldest(*globs):
    return _pick(min, *globs)


def _pick(how, *globs):
    hits = [(p.stat().st_mtime, p) for g in globs for p in ROOT.glob(g) if p.is_file()]
    return how(hits, key=lambda h: h[0]) if hits else None


def _oldest_excluding(glob: str, *skip_dirs: str):
    """가장 낡은 파일. `skip_dirs` 이름을 경로에 가진 것은 뺀다.

    `out/scenarios/<묶음>/e1_local`은 `out/e1`을 copytree한 사본이고 `copy2`가 원본 mtime을
    보존한다 — 낡은 것이 아니라 **정의상 원본과 같은 시각**이다. 세면 그 묶음이 영원히
    `0h STALE`로 뜨고, 그 경고는 재실행으로 지울 수 없다. 지울 수 없는 경고는 읽히지 않는다.
    """
    hits = [(p.stat().st_mtime, p) for p in ROOT.glob(glob)
            if p.is_file() and not set(skip_dirs) & set(p.parts)]
    return min(hits, key=lambda h: h[0]) if hits else None


def check_freshness():
    """out/이 **입력과 모형 코드 둘 다**보다 새로운가.

    D10까지 이 검사는 data/raw만 봤다. 그래서 D6~D9이 `src/cap/`을 고치고 `cap all`을
    돌리지 않은 채 지나갔고, out/e2는 나흘 전 것이었으며 페이퍼 §0 대장은 그 낡은
    산출물에 대해 '검증됨'으로 통과했다. 코드도 입력이다 — 여기서 같이 센다.

    **입력은 가장 새 파일로, 산출은 가장 낡은 파일로 잰다.** F27이 곁가지 검사에서
    같은 것을 고쳤고 이 검사는 F28까지 `_newest("out/e5/*.csv")`로 남아 있었다 —
    e5의 아홉 파일 중 하나만 다시 써도 out/ 전체가 새것으로 보인다. 검사의 방향은
    비대칭이어야 한다: 어느 입력이라도 새로우면 낡은 것이고, 모든 산출이 새로워야
    새것이다.
    """
    src = _newest("data/raw/*.csv", "src/cap/*.py", "config.yaml")
    out = _oldest("out/e5/*.csv")
    if src is None or out is None:
        return False, "data/raw or out/e5 missing — pipeline has never run here"
    fresh = out[0] >= src[0]
    rel = out[1].relative_to(ROOT)
    return fresh, (f"out/ newer than data/raw + src/cap (oldest {rel})" if fresh
                   else f"STALE: {src[1].relative_to(ROOT)} changed after {rel} — rerun `python -m cap all`")


def check_sidecars():
    """base보다 오래된 곁가지 산출물 — 아무도 보지 않아 낡은 채 인용된다.

    freshness는 `out/e5`만 본다. F20에서 실증됐다: `out/process`·`out/scenarios`·`out/m8`이
    base보다 하루 넘게 낡은 채 가이드 §6.2에 인용되고 있었고, 게이트는 그동안 그린이었다.
    WARN인 이유는 이것이 코드 결함이 아니라 재실행 대기 상태이기 때문이다 — 파이프라인
    창을 잡을 때까지 무엇이 낡았는지 이름으로 보이는 것이 목적이다.

    **목록을 손으로 적지 않는다.** F22가 네 곳을 이름으로 박아두었고, F25에서 그 목록에
    없던 `out/sensitivity`가 base보다 24시간 낡은 채 가이드 §4의 A-01·A-02와 MCP
    `get_sensitivity`에 인용되고 있는 것이 발견됐다 — 게이트는 그 24시간 동안 그린이었다.
    이제 `out/` 아래 base(e1–e5)가 아닌 디렉터리를 전부 센다. 새 곁가지가 생겨도 숨을
    자리가 없다.

    **디렉터리는 가장 낡은 파일로 판정한다.** F26까지 `_newest`를 썼고, 그래서 파일 하나만
    다시 써도 디렉터리 전체가 최신으로 보였다. 실측된 거짓 그린 둘: `out/scenarios`가
    "최신"이던 시각에 `disc65` 팔은 base보다 43시간 낡아 있었고(부분 재계획 중이었다),
    `out/uncertainty`가 "최신"이던 시각에 `decomposition_bands.csv`는 이틀 낡은 채
    `g2_band_impact.py:44`를 거쳐 가이드 §4.5의 밴드 열로 인용되고 있었다. 곁가지의
    신선도는 그 안에서 가장 뒤처진 파일이다.
    """
    base = _newest("out/e5/*.csv")
    if base is None:
        return False, "out/e5 missing"
    stale = []
    for name in sorted(p.name for p in (ROOT / "out").iterdir()
                       if p.is_dir() and p.name not in {"e1", "e2", "e3", "e4", "e5"}):
        got = _oldest_excluding(f"out/{name}/**/*.csv", "e1_local")
        if got is None:
            stale.append(f"{name}(없음)")
        elif got[0] < base[0]:
            stale.append(f"{name}({(base[0] - got[0]) / 3600:.0f}h, "
                         f"{got[1].relative_to(ROOT / 'out' / name)})")
    return not stale, ("all sidecar outputs at or newer than out/e5" if not stale
                       else f"STALE behind out/e5: {', '.join(stale)}")


def check_provenance():
    """out/이 **정본 설정**의 전체 실행인가.

    freshness는 out/이 새것인지만 본다. D10 뒤 out/e2·e4는 새것이었지만 `--sims`를
    줄인 실행이었고, 페이퍼 §0 대장과 어긋난 쪽은 out/이었다. 각 단계가 남긴
    run_manifest.json을 config.yaml과 대조해 그 착오를 이름으로 잡는다.
    """
    p = ROOT / "out" / "run_manifest.json"
    if not p.exists():
        return False, "out/run_manifest.json 없음 — `python -m cap all`로 재생성"
    m = json.loads(p.read_text())
    cfg = json.loads(run([PY, "-c", "import sys,json;sys.path.insert(0,'src');"
                          "from cap import config as C;c=C.load();"
                          "print(json.dumps({'data_dir':str(c.data_dir),"
                          "'n_sims':c.simulation['n_sims'],'n_sims_flex':c.simulation['n_sims_flex'],"
                          "'frontier_points':c.milp['frontier_points'],'seed':c.seed}))"])[1])
    stages = ["e1", "e2", "e3", "e4", "e5", "render"]
    missing = [s for s in stages if s not in m]
    if missing:
        return False, f"단계 기록 없음: {', '.join(missing)} — 전체 실행이 아니다"
    off = [f"{s}.{k}={m[s][k]}(≠{v})" for s in stages for k, v in cfg.items() if m[s].get(k) != v]
    if off:
        return False, "정본 설정 아님 — " + ", ".join(off[:4])
    return True, f"6단계 전부 정본 설정 (n_sims {cfg['n_sims']}, seed {cfg['seed']})"


def check_git():
    _, dirty, _ = run(["git", "status", "--porcelain"])
    _, ahead, _ = run(["git", "rev-list", "--count", "@{u}..HEAD"])
    n_dirty = len([ln for ln in dirty.splitlines() if ln.strip()])
    n_ahead = int(ahead.strip() or 0)
    ok = n_dirty == 0 and n_ahead == 0
    return ok, "clean and pushed" if ok else f"{n_dirty} uncommitted, {n_ahead} unpushed"


CHECKS = [
    ("tests", "pytest tests/", check_tests),
    ("independence", "FIN ⊥ EFF (H4 precondition)", check_independence),
    ("audit", "scripts/audit_data.py", check_audit),
    ("mcp", "MCP tools/list", check_mcp),
    ("cli", "python -m cap", check_cli),
    ("freshness", "out/ vs data/raw", check_freshness),
    ("sidecars", "곁가지 out/ vs out/e5", check_sidecars),
    ("provenance", "out/ 실행 설정 = config.yaml", check_provenance),
    ("git", "committed and pushed", check_git),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = []
    for key, label, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as exc:  # a check that crashes is a failing check
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        results.append({"check": key, "label": label, "ok": ok,
                        "severity": "FAIL" if key in HARD else "WARN", "detail": detail})

    failed = [r for r in results if not r["ok"] and r["check"] in HARD]

    if args.json:
        print(json.dumps({"ok": not failed, "results": results}, ensure_ascii=False, indent=2))
    else:
        width = max(len(r["label"]) for r in results)
        for r in results:
            mark = "PASS" if r["ok"] else r["severity"]
            print(f"  [{mark:4}] {r['label']:<{width}}  {r['detail']}")
        print()
        print("gate: OK" if not failed else f"gate: FAILED ({', '.join(r['check'] for r in failed)})")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
