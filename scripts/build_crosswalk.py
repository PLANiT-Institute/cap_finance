"""Build data/crosswalk_facilities.csv — the join key between the two CAP models.

FIN (cap_finance) models individual furnaces/crackers; EFF (cap-efficient) models
site blocks. The crosswalk maps FIN facility ids onto EFF blocks by works/site
membership so that either model's facility output can be aggregated to the other's
unit of analysis. Capacity totals per block are reported so a user can see how much
of an EFF block the mapped FIN units account for.

Run from either repo root:
    python3 scripts/build_crosswalk.py [path_to_fin_repo]
Writes an identical file to both repos when the FIN path is available.
"""

from __future__ import annotations

import csv
import pathlib
import sys

EFF_ROOT = pathlib.Path(__file__).resolve().parents[1]
FIN_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / "Documents/GitHub/cap_finance"

# FIN facility id -> EFF block id. Membership follows Nippon Steel's works
# structure (East Nippon = 君津·鹿島, Kyushu = 八幡/戸畑·大分, Kansai = 和歌山,
# Setouchi = 広畑, Hokkaido = 室蘭 — no EFF block) and POSCO's two works.
# POSCO block A/B split is not published; FIN units are assigned by works and the
# A/B distinction is left to the capacity note (mapping_confidence = site).
FIN_TO_EFF = {
    "POSCO_POH_BF2": "POS-POH-N", "POSCO_POH_BF3": "POS-POH-N", "POSCO_POH_BF4": "POS-POH-S",
    "POSCO_GWY_BF1": "POS-GWY-W", "POSCO_GWY_BF3": "POS-GWY-W",
    "POSCO_GWY_BF4": "POS-GWY-E", "POSCO_GWY_BF5": "POS-GWY-E",
    "POSCO_GWY_EAF1": "POS-GWY-EAF",
    "POSCO_POH_FINEX2": None, "POSCO_POH_FINEX3": None,   # FINEX has no EFF block
    "NSC_KAS_BF1": "NS-EAST", "NSC_KIM_BF2": "NS-EAST", "NSC_KIM_BF4": "NS-EAST",
    "NSC_NGO_BF1": "NS-NAGOYA", "NSC_NGO_BF3": "NS-NAGOYA",
    "NSC_WAK_BF2": "NS-KANSAI",
    "NSC_TOB_BF4": "NS-KYUSHU", "NSC_OIT_BF1": "NS-KYUSHU", "NSC_OIT_BF2": "NS-KYUSHU",
    "NSC_YAW_EAF1": "NS-KYUSHU", "NSC_HIR_EAF2": "NS-SETOUCHI",
    "NSC_MUR_BF2": None,                                   # 室蘭 (Hokkaido) — no EFF block
}
COMPANY_MAP = {"POSCO": "POSCO_KR", "NSC": "NIPPON_STEEL_JP", "LOTTE": None, "MCI": None}
SCENARIO_MAP = [("NZ15", "ACCELERATED_15C", "FIN 1.5°C 정합 ↔ EFF 내부 1.5°C 스트레스. 공식 GCAM_15C 추출 시 그쪽으로 이동"),
                ("B20", "GCAM_2C", "FIN 2°C ↔ EFF GCAM 2.0°C(추출 대기). 활성화 전까지 비교는 잠정")]


def read_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    eff_fac = {r["facility_id"]: r for r in read_csv(EFF_ROOT / "data/facilities.csv")}
    fin_path = FIN_ROOT / "data/prepared/D1a_facility_static.csv"
    fin_fac = {r["facility_id"]: r for r in read_csv(fin_path)} if fin_path.exists() else {}
    if not fin_fac:
        print(f"[crosswalk] warning: FIN facilities not found at {fin_path} — FIN columns left blank")

    rows = []
    for fin_id, eff_id in FIN_TO_EFF.items():
        f = fin_fac.get(fin_id, {})
        e = eff_fac.get(eff_id, {}) if eff_id else {}
        fin_cap_mt = float(f["capacity"]) / 1e6 if f.get("capacity") else ""
        rows.append({
            "fin_facility_id": fin_id,
            "eff_facility_id": eff_id or "",
            "fin_company_id": (fin_id.split("_")[0] if fin_id.startswith(("POSCO", "NSC")) else ""),
            "eff_company_id": e.get("company_id", ""),
            "unit_type": f.get("unit_type", ""),
            "site": f.get("site", "") or e.get("region", ""),
            "fin_capacity_mtpa": round(fin_cap_mt, 3) if fin_cap_mt != "" else "",
            "eff_block_capacity_mtpa": e.get("capacity_mtpa", ""),
            "in_fin_model": "yes" if fin_id in fin_fac else "no",
            "mapping_confidence": "site" if eff_id else "none",
            "note": ("EFF 블록 없음 (FINEX/室蘭 — EFF 모델 범위 밖)" if eff_id is None else
                     ("FIN 모형 제외 설비 (신설·능력 미상)" if fin_id not in fin_fac else "")),
        })
    # EFF-only blocks (JFE, Kobe, and any block with no FIN unit)
    mapped = {v for v in FIN_TO_EFF.values() if v}
    for eid, e in eff_fac.items():
        if eid in mapped:
            continue
        rows.append({
            "fin_facility_id": "", "eff_facility_id": eid, "fin_company_id": "",
            "eff_company_id": e["company_id"], "unit_type": "", "site": e.get("region", ""),
            "fin_capacity_mtpa": "", "eff_block_capacity_mtpa": e.get("capacity_mtpa", ""),
            "in_fin_model": "no", "mapping_confidence": "none",
            "note": "FIN 모델 범위 밖 (JFE·Kobe 등 EFF 전용 기업)",
        })
    # FIN-only companies (petrochemicals)
    for fid, f in fin_fac.items():
        if fid in FIN_TO_EFF:
            continue
        rows.append({
            "fin_facility_id": fid, "eff_facility_id": "", "fin_company_id": f["company_id"],
            "eff_company_id": "", "unit_type": f.get("unit_type", ""), "site": f.get("site", ""),
            "fin_capacity_mtpa": round(float(f["capacity"]) / 1e6, 3) if f.get("capacity") else "",
            "eff_block_capacity_mtpa": "", "in_fin_model": "yes", "mapping_confidence": "none",
            "note": "EFF 모델 범위 밖 (석유화학 — FIN 전용)",
        })

    cols = list(rows[0])
    for root in [EFF_ROOT, FIN_ROOT]:
        out = root / "data/crosswalk_facilities.csv"
        if not out.parent.exists():
            continue
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        print(f"[crosswalk] {out} ({len(rows)} rows)")

    # scenario map
    for root in [EFF_ROOT, FIN_ROOT]:
        out = root / "data/crosswalk_scenarios.csv"
        if not out.parent.exists():
            continue
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["fin_scenario_id", "eff_scenario_id", "note"])
            w.writerows(SCENARIO_MAP)
        print(f"[crosswalk] {out}")

    # coverage summary
    both = [r for r in rows if r["fin_facility_id"] and r["eff_facility_id"] and r["in_fin_model"] == "yes"]
    fin_cap = sum(float(r["fin_capacity_mtpa"]) for r in both if r["fin_capacity_mtpa"])
    eff_cap = sum(float(eff_fac[b]["capacity_mtpa"]) for b in {r["eff_facility_id"] for r in both})
    print(f"[crosswalk] 양 모형 공통 설비 {len(both)}기 — FIN 능력 합 {fin_cap:.1f} Mtpa / "
          f"대응 EFF 블록 능력 합 {eff_cap:.1f} Mtpa "
          f"(비율 {fin_cap / eff_cap:.2f} — 1에서 멀면 블록 경계·능력 기준 차이 점검)")


if __name__ == "__main__":
    main()
