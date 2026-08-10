"""J2 재현 데이터 패키지 — 남이 이 결과를 다시 만들 수 있게 하는 최소 묶음.

공개 경계(설계서 §8-2)를 코드로 강제한다: **시설 단위 절대값은 나가지 않는다.**
D1a·D1b는 기업 단위로 집계해서 싣고, 나머지 D2–D7은 그대로 싣는다. 시설 해상도가
필요한 사람은 저장소 소유자에게 요청해야 한다 — 그 사실도 패키지 안에 적는다.

`manifest.json`은 파일별 SHA256과 행 수, 그리고 이 패키지를 만든 실행의 config 요약을
담는다. 해시가 다르면 다른 데이터로 만든 결과다.

`data_dictionary.csv`는 **손으로 쓰지 않는다.** `docs/TECHNICAL_GUIDE.md` §3의 필드 표를
파싱해 실제로 쓴 파일의 헤더에 맞춰 낸다. 정의가 없는 열이 하나라도 실리면 빌드가 죽는다 —
사전이 정의 없는 열을 조용히 싣던 것이 F7에서 고친 결함이다(가이드 §3.10).

    .venv/bin/python scripts/build_data_package.py
산출: data/package/
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.schemas import SCHEMAS, load_input  # noqa: E402

PKG = ROOT / "data" / "package"
# 시설 단위는 집계해서만 나간다 (설계서 §8-2)
AGGREGATE = {
    "D1a_facility_static": ("company_id", {"capacity": "sum", "facility_id": "count"}),
    "D1b_facility_panel": None,   # 아래에서 company 조인 후 집계
}


GUIDE = ROOT / "docs" / "TECHNICAL_GUIDE.md"


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _plain(cell: str) -> str:
    """Table cell -> plain text: drop emphasis, backticks and the em-dash placeholder."""
    t = re.sub(r"\*\*?([^*]+)\*\*?", r"\1", cell).replace("`", "").strip()
    return "" if t in {"—", "-", ""} else re.sub(r"\s+", " ", t)


def _cells(row: str) -> list[str]:
    """Split a markdown table row on unescaped pipes."""
    return [c.replace(r"\|", "|") for c in re.split(r"(?<!\\)\|", row.strip())[1:-1]]


def guide_fields() -> dict[tuple[str, str], dict]:
    """Parse the field tables of guide §3 — the definition of record.

    Two header shapes are understood. `| Field | Definition | ... |` under a
    `### 3.x <ID> — ...` heading defines columns of the dataset(s) named in that
    heading; `| File | Field | Definition | Unit |` (§3.10) names the file per row,
    which is how the package-only files are defined. A field cell may name several
    columns (``a`, `b``) and may narrow them to one dataset with a `(D2a)` suffix.
    """
    out: dict[tuple[str, str], dict] = {}
    section, ids, cols = "", [], None
    for line in GUIDE.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            section = line[4:].split()[0]
            ids = re.findall(r"\bD\d[ab]?\b", line)
            cols = None
            continue
        if not line.startswith("|"):
            cols = None
            continue
        head = [_plain(c) for c in _cells(line)]
        if head[:1] in (["Field"], ["File"]):
            cols = head
            continue
        if not cols or set(head) <= {"", "---"} or line.startswith("|---"):
            continue
        by_file = cols[0] == "File"
        file_key = _plain(_cells(line)[0]) if by_file else None
        raw = _cells(line)[1 if by_file else 0]
        narrow = re.search(r"\((D\d[ab]?)\)", raw)
        names = re.findall(r"`([^`]+)`", raw)
        rest = _cells(line)[2 if by_file else 1:]
        defn = _plain(rest[0]) if rest else ""
        unit = _plain(rest[1]) if len(rest) > 1 and cols[2 if by_file else 1] == "Unit" else ""
        for n in names:
            keys = [(file_key, n)] if by_file else [
                (i, n) for i in ([narrow.group(1)] if narrow else ids)]
            for k in keys:
                out.setdefault(k, dict(definition=defn, unit=unit, section=section))
    return out


def dictionary(files: list[pathlib.Path]) -> pd.DataFrame:
    """One row per column of every shipped file, defined from the guide.

    A shipped column the guide does not define is a hard failure: the dictionary
    would otherwise ship a column name with no meaning attached, which is exactly
    what it did before.
    """
    fields = guide_fields()
    rows, missing = [], []
    for f in files:
        stem = f.stem
        dataset = stem.split("_")[0]
        header = pd.read_csv(f, nrows=0, encoding="utf-8-sig").columns.tolist()
        schema = next((v for k, v in SCHEMAS.items() if k.startswith(dataset + "_")), [])
        for c in header:
            d = fields.get((stem, c)) or fields.get((dataset, c))
            if d is None:
                missing.append(f"{stem}.{c}")
                continue
            rows.append(dict(file=stem, column=c,
                             schema_required="yes" if c in schema and stem in SCHEMAS else "",
                             unit=d["unit"], definition=d["definition"],
                             defined_in=f"TECHNICAL_GUIDE.md §{d['section']}"))
    if missing:
        raise SystemExit("[package] 가이드 §3에 정의가 없는 열 — 사전을 낼 수 없다:\n  "
                         + "\n  ".join(missing))
    return pd.DataFrame(rows)


def main() -> int:
    cfg = C.load()
    ddir = C.data_dir(cfg)
    if PKG.exists():
        for f in PKG.rglob("*"):
            if f.is_file():
                f.unlink()
    PKG.mkdir(parents=True, exist_ok=True)

    written: list[tuple[str, int, str]] = []

    d1a = load_input(ddir, "D1a_facility_static")
    d1b = load_input(ddir, "D1b_facility_panel")

    # D1a → 기업×설비유형 집계 (기수·능력 합계만; 시설명·부지·연도는 제외)
    a = (d1a.groupby(["company_id", "sector", "unit_type"])
         .agg(units=("facility_id", "count"), capacity_t_yr=("capacity", "sum"))
         .reset_index())
    a.to_csv(PKG / "D1a_company_capacity.csv", index=False)

    # D1b → 기업×연도 집계
    b = (d1b.merge(d1a[["facility_id", "company_id"]], on="facility_id")
         .groupby(["company_id", "year"])
         .agg(production_t=("production", "sum"), emissions_s1_tco2=("emissions_s1", "sum"),
              emissions_s2_tco2=("emissions_s2", "sum"),
              energy_elec_mwh=("energy_elec", "sum"), energy_coal_gj=("energy_coal", "sum"),
              energy_gas_gj=("energy_gas", "sum"))
         .reset_index())
    b.to_csv(PKG / "D1b_company_panel.csv", index=False)

    for name in ["D2a_scenario_budget", "D2b_scenario_prices", "D3_tech_options",
                 "D4_price_history", "D5_policy_support", "D6_company_financials",
                 "D7_disclosed_plan"]:
        df = load_input(ddir, name)
        df.to_csv(PKG / f"{name}.csv", index=False)

    # 출처 등록부 공개 사본
    reg = ROOT / "data" / "manifests" / "source_register.csv"
    if reg.exists():
        (PKG / "source_register.csv").write_bytes(reg.read_bytes())

    # 결과 쪽: 기업 집계 지표만 (시설 단위 산출은 제외)
    for rel in ["e5/metrics_company.csv", "e5/affordability.csv", "e5/gap.csv",
                "e5/emissions_pathway.csv"]:
        src = ROOT / "out" / rel
        if src.exists():
            (PKG / f"result_{pathlib.Path(rel).name}").write_bytes(src.read_bytes())

    # 데이터 사전 — 가이드 §3에서 파생, 실제로 쓴 파일의 헤더 기준
    dic = dictionary(sorted(PKG.glob("*.csv")))
    dic.to_csv(PKG / "data_dictionary.csv", index=False)

    for f in sorted(PKG.glob("*.csv")):
        n = sum(1 for _ in f.open(encoding="utf-8-sig")) - 1
        written.append((f.name, n, sha256(f)))

    manifest = {
        "package": "CAP v2 재현 패키지",
        "boundary": ("시설 단위 절대값은 포함하지 않는다 (설계서 §8-2). D1a·D1b는 기업 단위 "
                     "집계본이며, 시설 해상도는 저장소 소유자에게 요청해야 한다."),
        "config": {
            "seed": cfg["seed"], "years": cfg["years"], "scenarios": cfg["scenarios"],
            "discount_rate": cfg["discount_rate"], "n_sims": cfg["simulation"]["n_sims"],
            "milp": {k: cfg["milp"][k] for k in
                     ["frontier_points", "solver_time_limit_s", "mip_gap_rel", "retire_max_share"]
                     if k in cfg["milp"]},
            "carbon_auction_share": cfg["carbon_auction_share"],
        },
        "reproduce": [
            "python -m cap all              # E1 → render (MILP 약 20분)",
            "python scripts/run_scenarios.py",
            "pytest tests/ -q && pytest tests/test_consistency.py -q",
        ],
        "validation": ["docs/data_audit.md", "docs/validation_backtest.md",
                       "docs/validation_external.md", "docs/cross_model_check.md",
                       "METHODOLOGY.md"],
        "files": [{"name": n, "rows": r, "sha256": h} for n, r, h in written],
    }
    (PKG / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[package] data/package/ — {len(written)}개 파일")
    for n, r, h in written:
        print(f"  {n:34} {r:>6}행  {h[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
