"""The two implementations must not import each other.

H4 (cross-model check) is only evidence if FIN and EFF are independent
implementations. Merging them into one repository (2026-08-10) removed the
folder-level barrier that used to enforce this by accident, so enforce it
explicitly: a shared import would make the cross-check circular and void the
"independent implementation" defence in AUTOPILOT §7.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# `import cap`, `from cap import ...`, `from cap.e2_milp import ...` — but not
# `import cap_efficient`, which is a different top-level package.
FIN_IMPORT = re.compile(r"^\s*(?:from\s+cap(?:\.\S*)?\s+import\b|import\s+cap(?:\.\S*)?\s*(?:as\b|$|,))", re.M)
EFF_IMPORT = re.compile(r"^\s*(?:from\s+cap_efficient(?:\.\S*)?\s+import\b|import\s+cap_efficient\b)", re.M)


def _py_files(*rel_dirs):
    for rel in rel_dirs:
        d = ROOT / rel
        if d.is_dir():
            yield from sorted(p for p in d.rglob("*.py") if "__pycache__" not in p.parts)


def _offenders(files, pattern):
    hits = []
    for p in files:
        for m in pattern.finditer(p.read_text(encoding="utf-8")):
            line_no = p.read_text(encoding="utf-8")[: m.start()].count("\n") + 1
            hits.append(f"{p.relative_to(ROOT)}:{line_no}: {m.group(0).strip()}")
    return hits


def test_eff_does_not_import_fin():
    files = list(_py_files("cap-efficient/cap_efficient", "cap-efficient/scripts", "cap-efficient/tests"))
    assert files, "EFF source tree not found — did the subtree move?"
    assert not _offenders(files, FIN_IMPORT), (
        "EFF imports FIN — cross-model check becomes circular:\n"
        + "\n".join(_offenders(files, FIN_IMPORT))
    )


def test_fin_does_not_import_eff():
    files = list(_py_files("src/cap", "scripts", "tests"))
    assert files, "FIN source tree not found"
    assert not _offenders(files, EFF_IMPORT), (
        "FIN imports EFF — cross-model check becomes circular:\n"
        + "\n".join(_offenders(files, EFF_IMPORT))
    )
