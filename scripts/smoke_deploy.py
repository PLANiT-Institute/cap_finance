"""Deployment smoke test (L7, 2026-09-11).

Checks that the deployed API answers GET /api/simulate with JSON whose
engine_version equals platform/public/data/catalog.json — i.e. the live
function runs and was built from the same engine bundle as the published
page. Exit code 0 on success, 1 on any mismatch or HTTP failure.

Usage: python scripts/smoke_deploy.py [https://tcar-transition-finance.vercel.app]
"""
import json, sys, urllib.request, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
base = (sys.argv[1] if len(sys.argv) > 1 else "https://tcar-transition-finance.vercel.app").rstrip("/")
local = json.loads((ROOT / "platform/public/data/catalog.json").read_text())["engine_version"]
try:
    with urllib.request.urlopen(base + "/api/simulate", timeout=30) as r:
        body = r.read(); ctype = r.headers.get("content-type", "")
        if "json" not in ctype:
            print(f"FAIL: non-JSON response ({ctype}); function likely not running"); sys.exit(1)
        remote = json.loads(body).get("engine_version")
except Exception as e:
    print(f"FAIL: {base}/api/simulate -> {e}"); sys.exit(1)
if remote != local:
    print(f"FAIL: engine_version mismatch remote={remote[:12]} local={local[:12]} — rebuild data and redeploy"); sys.exit(1)
print(f"OK: live engine {remote[:12]} == published catalog"); sys.exit(0)
