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
    best = None
    for g in globs:
        for p in ROOT.glob(g):
            if p.is_file():
                m = p.stat().st_mtime
                if best is None or m > best[0]:
                    best = (m, p)
    return best


def check_freshness():
    raw = _newest("data/raw/*.csv")
    out = _newest("out/e5/*.csv")
    if raw is None or out is None:
        return False, "data/raw or out/e5 missing — pipeline has never run here"
    fresh = out[0] >= raw[0]
    rel = out[1].relative_to(ROOT)
    return fresh, (f"out/ newer than data/raw ({rel})" if fresh
                   else f"STALE: {raw[1].relative_to(ROOT)} changed after {rel} — rerun `python -m cap all`")


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
