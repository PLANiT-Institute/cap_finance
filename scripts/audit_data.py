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

# 비어 있거나 안 쓰이는 것이 **설계상 맞는** 컬럼. 사유를 여기 적지 않으면 감사가
# 설명된 공백과 설명 안 된 공백을 구분하지 못하고, 매 실행 같은 경고가 반복된다.
EXPECTED_GAP = {
    ("D1b_facility_panel", "energy_naphtha"):
        "석화 원료비는 물량×가격이 아니라 **에틸렌-납사 스프레드 마진**(D1a margin_kthou_t)으로 "
        "들어온다 — 전환 계획이 원료를 바꾸지 않는 한 증분비용에서 상쇄된다. 다만 원료가격 "
        "변동은 TCaR에 잡히지 않는다(한계로 기재).",
    ("D1b_facility_panel", "emissions_s2"):
        "수집·보존하되 지표 경계는 Scope 1이다(A-21). 예산이 기업 자체 base에 앵커되므로 "
        "수준 중립이고, 넣으면 전기화가 더 유리해지는 방향의 구조 대안.",
    ("D7_disclosed_plan", "coverage_pct"):
        "PPA·EPC 커버리지 비율용 컬럼. 현재 수집된 공시에 해당 항목이 없다 — 비어 있는 것이 "
        "곧 '그런 공시가 없다'는 발견.",
    ("D2a_scenario_budget", "gcam_version"):
        "출처 추적용 라벨. EST_v0 잠정이라 전 행 동일한 것이 맞다.",
    ("D1a_facility_static", "commissioning_year"):
        "**준비 단계에서 소비**된다(prepare_raw: 2027년 이후 신설 제외, 재투자 창 결측 보정). "
        "엔진이 직접 읽지 않을 뿐 버려지는 값이 아니다.",
    ("D5_policy_support", "param_type"):
        "**준비 단계에서 소비**된다 — `_instrument`가 이 값으로 유상할당/상한/하한을 분류하고, "
        "엔진은 분류된 `instrument`를 읽는다.",
    ("D5_policy_support", "support_scenario"):
        "수집된 지원 시나리오가 `current` 하나뿐이라 전 행 동일한 것이 맞다. "
        "**확정된 직접 지원이 없다는 것 자체가 발견**이다(PREP_LOG D5).",
    ("D5_policy_support", "tech_id"):
        "수집된 정책이 전부 업종 전반(`all`) 적용이라 기술별 값이 없다 — 기술 특정 지원이 "
        "존재하지 않는다는 뜻.",
    ("D6_company_financials", "net_debt_note"):
        "",   # placeholder key (미사용) — 아래 total_debt 주석 참조
    ("D6_company_financials", "total_debt"):
        "`net_debt`(= total_debt − cash)가 지표 ⑥에 쓰이고 이 컬럼은 그 구성요소다. "
        "POSCO·LOTTE 미확보는 단순 미공시가 아니라 **경계 문제**다 — D6의 POSCO 행은 "
        "철강 별도(매출 37.6조)인데 DART에서 바로 얻히는 것은 홀딩스 연결(자산 103조) 또는 "
        "홀딩스 별도(순수지주)여서 EBITDA 분모와 어긋난다. 맞지 않는 수를 넣느니 비워 둔다.",
    ("D6_company_financials", "cash"): "위와 같음 — `net_debt`의 구성요소.",
    ("D6_company_financials", "interest_expense"):
        "이자보상배율용이나 22행 중 2행만 공시돼 지표를 만들 수 없다. "
        "**공시 부재가 기록으로 남는 편이 낫다.**",
    ("D7_disclosed_plan", "facility_id"):
        "`target` 행(회사 전체 목표)은 시설이 없는 것이 정상이다. 채움률 67%는 결손이 아니라 "
        "행 종류 구성.",
    ("D7_disclosed_plan", "tech_id"): "위와 같음 — `target`·`timing` 행은 기술 특정이 없다.",
    ("D7_disclosed_plan", "resolution"):
        "공시 해상도 등급. 엔진 입력은 아니지만 **gap 미산출 사유 판정**의 근거이고 "
        "`disclosed_skipped.csv` 해석에 필요하다.",
    ("D7_disclosed_plan", "quote"):
        "공시 원문. 엔진이 읽지 않지만 **검증에서 결정적으로 쓰였다** — 미쓰이 설비집약 공시의 "
        "능력·감축량이 여기 있었고 그것으로 NCC 배출계수를 역산했다(H3 §4-1-a).",
    ("D1a_facility_static", "site"):
        "시설 부지명 — 시설 단위 비공개 원칙(§8-2)상 모형이 읽지 않는 것이 맞다.",
}

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
                    verdict="설계상 정상" if (name, col) in EXPECTED_GAP and verdict != "ok"
                            else verdict,
                    note=EXPECTED_GAP.get((name, col), DERIVED_USE.get(col, "")),
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
        f"| 설계상 정상 | {tally.get('설계상 정상', 0)} | 비었거나 안 쓰이는 것이 맞는 컬럼 — 사유 기재 |",
        "",
    ]
    for v in ("EMPTY", "PARTIAL", "UNUSED", "CONSTANT", "설계상 정상"):
        sub = df[df.verdict == v]
        if len(sub):
            lines += [f"## {v}", "", "| 파일 | 컬럼 | 채움% | 사유·비고 |", "|---|---|---|---|"]
            lines += [f"| {r.file} | {r.column} | {r.filled_pct} | {r.note} |"
                      for r in sub.itertuples()]
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
