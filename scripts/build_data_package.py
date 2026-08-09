"""J2 재현 데이터 패키지 — 남이 이 결과를 다시 만들 수 있게 하는 최소 묶음.

공개 경계(설계서 §8-2)를 코드로 강제한다: **시설 단위 절대값은 나가지 않는다.**
D1a·D1b는 기업 단위로 집계해서 싣고, 나머지 D2–D7은 그대로 싣는다. 시설 해상도가
필요한 사람은 저장소 소유자에게 요청해야 한다 — 그 사실도 패키지 안에 적는다.

`manifest.json`은 파일별 SHA256과 행 수, 그리고 이 패키지를 만든 실행의 config 요약을
담는다. 해시가 다르면 다른 데이터로 만든 결과다.

    .venv/bin/python scripts/build_data_package.py
산출: data/package/
"""

from __future__ import annotations

import hashlib
import json
import pathlib
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


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


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

    # 데이터 사전
    dic = []
    for name, cols in SCHEMAS.items():
        for c in cols:
            dic.append(dict(file=name, column=c))
    pd.DataFrame(dic).to_csv(PKG / "data_dictionary.csv", index=False)

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
