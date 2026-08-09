"""M3 데이터 절의 재료 — 출처·연도·신뢰등급 표를 원자료에서 재계산한다.

논문 §4가 "우리 데이터가 무엇에 근거하는가"를 주장하려면 그 주장 자체가 파일에서
재생성돼야 한다. 이 스크립트는 세 가지를 낸다.

1. `out/m3/datasets.csv`      — D1–D7 원자료 파일별 행수·엔티티·기간·출처 수
2. `out/m3/tier_summary.csv`  — 파라미터 인벤토리의 등급 분포와 [low, high] 밴드 보유
3. `out/m3/source_integrity.csv` — 인용된 `source_id`가 실제로 등록부에 있는가
4. `out/m3/top10_tier.csv`    — F2 민감도 상위 10의 등급 (§1 규칙: T3 이상 필수)

3번이 이 사이클의 검사다. AUTOPILOT §1은 "인용은 `source_register`의 `source_id`로만"
이라고 규정하는데, 인벤토리의 `source_id` 열에는 (a) 등록부 id, (b) EFF 프로젝트 id,
(c) `model_estimate` 같은 **출처가 아닌 표식**이 섞여 있다. `build_parameter_inventory.tier_of`는
모르는 문자열을 조용히 T5로 떨어뜨리므로 오탈자가 등급 하락으로만 나타나고 오류로 뜨지 않는다.
여기서 셋을 갈라 세고, 미해소가 남으면 그 사실을 페이퍼 §4가 적는다.

Run: .venv/bin/python scripts/data_section_table.py
"""

import csv
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EFF = ROOT / "cap-efficient"
OUT = ROOT / "out" / "m3"

# 출처가 아니라 "출처 없음"을 뜻하는 표식. 대소문자 두 벌인 것은 FIN 상수와 EFF
# `data_status` 열이 각자 쓰기 때문이고, 이 목록 자체가 §4가 보고하는 사실이다.
SENTINELS = {"model_estimate", "MODEL_ESTIMATE", "MODEL_CHOICE", "PREP_INJECTION",
             "EFF_PRICE_PROCESS"}

# D 번호 ↔ 원자료 파일 (PREP_LOG·audit_data.py와 같은 명명)
DATASETS = [
    ("D1a", "facility_static.csv", "facility_id", None),
    ("D1b", "facility_panel.csv", "facility_id", "year"),
    ("D1c", "jp_site_emissions.csv", "site_key", "fiscal_year"),
    ("D2a", "scenario_budget.csv", "scenario", "year"),
    ("D2b", "scenario_prices.csv", "scenario", "year"),
    ("D3", "tech_options.csv", "tech_id", None),
    ("D4", "price_history.csv", "series_id", "date"),
    ("D5", "policy_support.csv", "instrument", None),
    ("D6", "company_financials.csv", "company_id", "year"),
    ("D7", "disclosed_plan.csv", "company_id", "year_stated"),
]

TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    register = read(RAW / "source_register.csv")
    reg_ids = {r["source_id"] for r in register}
    # EFF 정본(§3)에 사는 프로젝트 id — CSV로만 참조한다(코드 독립성 불가침).
    eff_ids = set()
    for name in ("transition_projects.csv", "technology_cost_evidence.csv"):
        p = EFF / "data" / name
        if p.exists():
            eff_ids |= {r.get("project_id", "") for r in read(p)} - {""}

    # ---- 1. 데이터셋 표
    ds_rows = []
    for did, fname, ent, per in DATASETS:
        rows = read(RAW / fname)
        srcs = {t for r in rows for t in TOKEN.findall(r.get("source_id") or "") if t in reg_ids}
        years = []
        if per:
            for r in rows:
                m = re.search(r"\d{4}", r.get(per) or "")
                if m:
                    years.append(int(m.group()))
        ds_rows.append(dict(
            dataset=did, file=f"data/raw/{fname}", rows=len(rows),
            entities=len({r.get(ent) for r in rows}),
            period=f"{min(years)}–{max(years)}" if years else "",
            sources=len(srcs), source_ids=" ".join(sorted(srcs))))

    # ---- 2. 등급 분포
    inv = read(ROOT / "docs" / "parameter_inventory.csv")
    tiers = Counter(r["evidence_tier"] for r in inv)
    banded = sum(1 for r in inv if r["value_low"].strip() and r["value_high"].strip())
    tier_rows = [dict(tier=t, rows=tiers.get(t, 0),
                      banded=sum(1 for r in inv if r["evidence_tier"] == t
                                 and r["value_low"].strip() and r["value_high"].strip()))
                 for t in ("T1", "T2", "T3", "T4", "T5")]
    tier_rows.append(dict(tier="ALL", rows=len(inv), banded=banded))

    # ---- 3. 출처 무결성
    integrity, kinds = [], Counter()
    for r in inv:
        raw_src = r["source_id"]
        toks = set(TOKEN.findall(raw_src))
        if toks & reg_ids:
            kind = "registered"
        elif toks & SENTINELS:
            kind = "sentinel"          # 출처 없음을 선언한 것 — 결함이 아니라 표식
        elif toks & eff_ids:
            kind = "eff_namespace"     # 실재하나 FIN 등록부에 없다 — §1 위반
        else:
            kind = "unresolved"        # 아무 데도 없다 — 진짜 결함
        kinds[kind] += 1
        if kind != "registered":
            integrity.append(dict(param_id=r["param_id"], tier=r["evidence_tier"],
                                  source_id=raw_src, resolution=kind))

    # ---- 4. F2 상위 10의 등급
    rank = read(ROOT / "out" / "sensitivity" / "ranking.csv")[:10]
    top10 = [dict(rank=i + 1, param=r["base_param"], tier=r["tier"],
                  score=round(float(r["score"]), 1),
                  meets_t3=r["tier"] in ("T1", "T2", "T3"))
             for i, r in enumerate(rank)]
    t3plus = sum(1 for r in top10 if r["meets_t3"])
    t5only = sum(1 for r in top10 if r["tier"] == "T5")

    # ---- 5. 페이퍼 §0 대장이 대조할 한 줄짜리 요약
    audit = read(ROOT / "docs" / "data_audit.csv")
    summary = [
        dict(key="m3_raw_datasets", value=len(ds_rows)),
        dict(key="m3_sources_registered", value=len(reg_ids)),
        dict(key="inv_rows", value=len(inv)),
        dict(key="inv_banded", value=banded),
        # 증거 등급(T2·T3·T4)에 밴드가 하나도 없다는 사실이 §4.2의 발견이다.
        dict(key="inv_banded_t2t3t4",
             value=sum(r["banded"] for r in tier_rows if r["tier"] in ("T2", "T3", "T4"))),
        dict(key="inv_src_registered", value=kinds["registered"]),
        dict(key="inv_src_sentinel", value=kinds["sentinel"]),
        dict(key="inv_src_eff", value=kinds["eff_namespace"]),
        dict(key="inv_src_unresolved", value=kinds["unresolved"]),
        dict(key="top10_t3plus", value=t3plus),
        dict(key="top10_t5", value=t5only),
        dict(key="audit_partial_cols", value=sum(1 for r in audit if r["verdict"] == "PARTIAL")),
    ]

    for name, rows in (("datasets", ds_rows), ("tier_summary", tier_rows),
                       ("source_integrity", integrity), ("top10_tier", top10),
                       ("summary", summary)):
        with open(OUT / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    print(f"[m3] 원자료 {len(ds_rows)}종, 등록부 {len(reg_ids)}건")
    print(f"[m3] 인벤토리 {len(inv)}행 — 등급 {dict(sorted(tiers.items()))}, 밴드 {banded}")
    print(f"[m3] 출처 해소 {dict(kinds)}")
    print(f"[m3] F2 상위 10 — T3 이상 {t3plus}, T5 {t5only}")
    if kinds["unresolved"]:
        print(f"[m3] 경고: 해소 불가 {kinds['unresolved']}행 — 등록부에도 EFF에도 없다")


if __name__ == "__main__":
    main()
