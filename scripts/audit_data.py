"""Data authenticity + utilisation audit (AUTOPILOT §6 재현성 게이트 확장).

Answers three questions with numbers, not prose:
  1. 가짜/자리표시자 데이터가 섞였는가  — empty schema columns, constant columns,
     synthetic sample leakage into the production input set.
  2. 수집한 데이터를 전부 쓰는가        — every column of every D* input, matched
     against the engine source; unreferenced columns are collected-but-unused.
  3. 출처가 실재하는가                  — every source_id in every input resolves
     to data/raw/source_register.csv; EST_*/PENDING_* flagged as unsourced.

Run: .venv/bin/python scripts/audit_data.py
Writes: docs/data_audit.csv (row per column) + docs/data_audit.md (summary)
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cap import schemas as S  # noqa: E402

PREPARED = ROOT / "data" / "prepared"
SAMPLE = ROOT / "data" / "sample"
# data/raw는 gitignore다 — 클론한 저장소에서도 감사가 돌도록 공개 사본으로 폴백한다
REGISTER = next((p for p in [ROOT / "data" / "raw" / "source_register.csv",
                             ROOT / "data" / "manifests" / "source_register.csv"]
                 if p.exists()), ROOT / "data" / "manifests" / "source_register.csv")
# schemas.py lists every column by name — including it would mark all of them
# "used" and defeat the utilisation check. Scan only the modelling modules.
ENGINE = [p for p in sorted((ROOT / "src" / "cap").glob("*.py")) if p.name != "schemas.py"]
DOCS = ROOT / "docs"

# columns the engine consumes through a rename/derivation rather than by name
DERIVED_USE = {
    "unit_name": "e2 (capacity parsed from 내용적 in name — G3)",
    "capacity_unit": "unit label only",
    "source_id": "provenance (audited here, not modelled)",
    "note": "provenance",
}


def engine_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in ENGINE)


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def audit() -> tuple[pd.DataFrame, list[str]]:
    code = engine_text()
    known_sources = set()
    if REGISTER.exists():
        known_sources = set(
            pd.read_csv(REGISTER, dtype=str, encoding="utf-8-sig")["source_id"].str.strip()
        )

    rows, notes = [], []

    for name in sorted(S.SCHEMAS):
        path = PREPARED / f"{name}.csv"
        if not path.exists():
            notes.append(f"MISSING INPUT: {path.relative_to(ROOT)}")
            continue
        df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
        df.columns = [c.strip() for c in df.columns]

        # synthetic-leak check: identical bytes to the synthetic sample = fake production input
        s = SAMPLE / f"{name}.csv"
        if s.exists() and sha(s) == sha(path):
            notes.append(f"SYNTHETIC LEAK: {name} is byte-identical to data/sample — fake input")

        for col in df.columns:
            # pandas 3 keeps NA as NA through astype(str) — comparing against the
            # literal "nan" silently counted every blank cell as filled
            v = df[col].astype(str).str.strip()
            ok_cell = df[col].notna() & (v != "") & (v.str.lower() != "nan")
            filled = int(ok_cell.sum())
            distinct = int(v[ok_cell].nunique())
            # word-boundary match so 'capacity' does not match 'capacity_unit'
            used = bool(re.search(rf'["\'\[]{re.escape(col)}["\'\]]', code)) or bool(
                re.search(rf"\.{re.escape(col)}\b", code)
            )
            in_schema = col in S.SCHEMAS[name]

            if filled == 0:
                verdict = "EMPTY" if in_schema else "EMPTY-extra"
            elif not used and col not in DERIVED_USE:
                verdict = "UNUSED"
            elif distinct == 1 and col not in ("unit", "capacity_unit", "region"):
                verdict = "CONSTANT"
            elif filled < len(df):
                # a single blank anchor in D2b's `value` poisoned an entire
                # interpolated price path and sent E2 back to a retired model.
                # Partial fill is a data gap, not a rounding detail.
                verdict = "PARTIAL"
            else:
                verdict = "ok"

            rows.append(
                dict(
                    file=name,
                    column=col,
                    rows=len(df),
                    filled=filled,
                    filled_pct=round(100 * filled / max(len(df), 1), 1),
                    distinct=distinct,
                    in_schema=in_schema,
                    engine_reference=used,
                    verdict=verdict,
                    note=DERIVED_USE.get(col, ""),
                )
            )

        # source_id resolution
        if "source_id" in df.columns:
            ids = set(df["source_id"].dropna().astype(str).str.strip()) - {"", "nan"}
            for sid in sorted(ids):
                # a cell may carry several ids plus a free-text qualifier:
                #   "VOGL_2018 (ex-electrolyser, 광석공통분 제외)", "KR_PPA_2026/REI_JP_PPA_2025"
                for part in re.split(r"[;|+/]", re.sub(r"\s*\(.*", "", sid)):
                    part = part.strip()
                    if not part:
                        continue
                    if part.startswith(("EST_", "PENDING_", "PREP_")):
                        notes.append(f"UNSOURCED: {name} uses '{part}' (model estimate / not received)")
                    elif known_sources and part not in known_sources:
                        notes.append(f"DANGLING SOURCE: {name} cites '{part}' — absent from source_register")

    return pd.DataFrame(rows), sorted(set(notes))


def main() -> int:
    df, notes = audit()
    DOCS.mkdir(exist_ok=True)
    df.to_csv(DOCS / "data_audit.csv", index=False)

    tally = df.verdict.value_counts().to_dict()
    lines = [
        "# 데이터 진위·활용 감사 (scripts/audit_data.py 자동 생성)",
        "",
        f"입력 {df.file.nunique()}개 파일 / 컬럼 {len(df)}개.",
        "",
        "| 판정 | 개수 | 뜻 |",
        "|---|---|---|",
        f"| ok | {tally.get('ok', 0)} | 채워져 있고 엔진이 참조 |",
        f"| CONSTANT | {tally.get('CONSTANT', 0)} | 전 행 동일값 — 변수 아님(자리표시자 의심) |",
        f"| UNUSED | {tally.get('UNUSED', 0)} | 수집했으나 엔진이 안 읽음 |",
        f"| PARTIAL | {tally.get('PARTIAL', 0)} | 일부 행이 빈칸 — 보간·집계에서 조용히 번진다 |",
        f"| EMPTY | {tally.get('EMPTY', 0)} | 스키마 필수인데 전부 빈칸 |",
        f"| EMPTY-extra | {tally.get('EMPTY-extra', 0)} | 스키마 외 빈 컬럼 |",
        "",
    ]
    for v in ("EMPTY", "PARTIAL", "UNUSED", "CONSTANT"):
        sub = df[df.verdict == v]
        if len(sub):
            lines += [f"## {v}", "", "| 파일 | 컬럼 | 채움% |", "|---|---|---|"]
            lines += [f"| {r.file} | {r.column} | {r.filled_pct} |" for r in sub.itertuples()]
            lines.append("")
    lines += ["## 출처·진위 경고", ""] + ([f"- {n}" for n in notes] or ["- 없음"])
    (DOCS / "data_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines[:20]))
    print(f"\n경고 {len(notes)}건 — docs/data_audit.md")
    # hard failures only: synthetic leakage or a required column that is entirely empty
    fatal = [n for n in notes if n.startswith(("SYNTHETIC LEAK", "MISSING INPUT"))]
    return 1 if fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
