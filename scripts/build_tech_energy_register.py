"""Build the per-technology energy-demand register (research_v2, cycle 2026-09-07).

One row per (FIN technology, energy carrier). Each row pairs the value the FIN
engine currently uses (data/prepared/D3_tech_options.csv or the ROUTE constants
injected by scripts/prepare_raw.py) with the best primary-research reference
found so far (data/research_v2/technology_packages/reference_process_packages.json,
GCAM public defaults, FORECAST-Sites rows) and states whether the two share a
process boundary. Nothing here mutates FIN/EFF inputs.

Output: data/research_v2/technology_packages/tech_energy_demand_register.csv
        docs/research_cycles/2026-09-07/TECH_ENERGY_REGISTER.md
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D3 = ROOT / "data/prepared/D3_tech_options.csv"
PKG = ROOT / "data/research_v2/technology_packages/reference_process_packages.json"
OUT_CSV = ROOT / "data/research_v2/technology_packages/tech_energy_demand_register.csv"
OUT_MD = ROOT / "docs/research_cycles/2026-09-07/TECH_ENERGY_REGISTER.md"

LHV_H2_GJ_PER_KG = 0.120  # rounded LHV used throughout research_v2 diagnostics
MWH_PER_GJ = 1 / 3.6
# scripts/prepare_raw.py ROUTE: (EF, elec MWh/t, coal GJ/t, gas GJ/t) — injected, not observed
ROUTE = {"BF": (2.15, 0.08, 13.5, 0.4), "FINEX": (2.05, 0.10, 13.0, 0.4),
         "EAF": (0.45, 0.55, 0.0, 1.0), "NCC": (0.95, 0.35, 0.0, 8.0)}


def load_d3() -> dict[str, dict]:
    with D3.open(encoding="utf-8-sig") as f:
        return {r["tech_id"]: r for r in csv.DictReader(f)}


def load_pkg() -> dict[str, dict]:
    pk = json.loads(PKG.read_text())["packages"]
    return {p["package_id"]: {f["flow_id"]: f for f in p["flows"]} for p in pk}


def flow(pkgs, pid, fid):
    return pkgs[pid][fid]["quantity"]


def rows(d3, pkgs):
    v_el = flow(pkgs, "VOGL2018_ONSITE_H2_BASE", "electricity_total")
    v_h2 = flow(pkgs, "VOGL2018_ONSITE_H2_BASE", "hydrogen_internal")
    v_eaf = flow(pkgs, "VOGL2018_ONSITE_H2_BASE", "EAF_electricity")
    vogl_electrolysis_mwh = v_h2 * LHV_H2_GJ_PER_KG / 0.72 * MWH_PER_GJ  # V2OBS001 efficiency 72% LHV
    vogl_residual = v_el - vogl_electrolysis_mwh
    g_h2 = flow(pkgs, "PUBLIC_GCAM2026_H2DRI_2025", "H2 industrial")
    g_el = flow(pkgs, "PUBLIC_GCAM2026_H2DRI_2025", "elect_td_ind")
    g_gas = flow(pkgs, "PUBLIC_GCAM2026_H2DRI_2025", "wholesale gas")
    l_el0 = flow(pkgs, "LAYRITZ2021_NCC_BASE", "electricity")
    l_heat = flow(pkgs, "LAYRITZ2021_NCC_BASE", "heat")
    l_ch4 = flow(pkgs, "LAYRITZ2021_NCC_BASE", "methane_fuel")
    l_el1 = flow(pkgs, "LAYRITZ2021_NCC_ELECTRIC", "electricity")
    l_naph = flow(pkgs, "LAYRITZ2021_NCC_BASE", "naphtha")
    fin = lambda t, k: float(d3[t][k])

    R = []

    def add(tech, carrier, fin_value, fin_unit, fin_source, ref_value, ref_unit, ref_id, ref_boundary,
            status, derivation, next_step):
        R.append(dict(tech_id=tech, carrier=carrier, fin_value=fin_value, fin_unit=fin_unit,
                      fin_source=fin_source, reference_value=ref_value, reference_unit=ref_unit,
                      reference_id=ref_id, reference_boundary=ref_boundary, boundary_status=status,
                      derivation=derivation, next_step=next_step, automatically_adopted=False))

    # ---------------- steel ----------------
    add("steel_h2dri", "electricity", fin("steel_h2dri", "elec_intensity"), "MWh/t", d3["steel_h2dri"]["source_id"],
        round(vogl_residual, 3), "MWh/t_liquid_steel", "V2OBS011-V2OBS006/V2OBS001 (Vogl2018 residual)",
        "Vogl total 3.48 incl. onsite electrolysis; residual after subtracting 51kg x 0.12GJ/kg / 0.72 LHV",
        "boundary_mismatch",
        f"3.48 - {vogl_electrolysis_mwh:.3f} = {vogl_residual:.3f}; FIN 0.85 not derivable from Vogl; GCAM public 4.2GJ={g_el*MWH_PER_GJ:.3f}MWh/t (75%DRI+scrap, incl. upstream pellet boundary)",
        "Cycle2: fix purchased-H2 boundary (shaft heating, heat recovery, EAF hot charge) then set value with explicit derivation")
    add("steel_h2dri", "hydrogen", fin("steel_h2dri", "h2_intensity"), "kg/t", d3["steel_h2dri"]["source_id"],
        v_h2, "kgH2/t_liquid_steel", "V2OBS006 (Vogl2018 base, 100% pellet, no scrap)",
        "Pure H2 shaft, 1.504t pellets, no scrap; Pimm hot route 25.2kg uses scrap share",
        "boundary_conditional_match",
        f"GCAM public 7.3GJ = {g_h2/LHV_H2_GJ_PER_KG:.1f}kg/t but that is 83%H2/17%NG reductant energy with 75% DRI feed",
        "Cycle2: record scrap share of Korean/Japanese candidate plants; 51kg valid only for zero-scrap pellet feed")
    add("steel_h2dri", "gas", 0.0, "GJ/t", "not a D3 field (retained_gas_fraction=0)",
        g_gas, "GJ/t_GCAM_steel", "PUBLIC_GCAM2026_H2DRI_2025 wholesale gas",
        "GCAM H2-DRI keeps 17% NG reductant energy; Vogl pure H2 keeps none",
        "specification_difference",
        "Zero purchased gas is the pure-H2 specification; GCAM/KAIST scenario technology is not pure H2",
        "Cycle4: carry both specifications as alternative theta, do not average")
    add("steel_eaf", "electricity", fin("steel_eaf", "elec_intensity"), "MWh/t", d3["steel_eaf"]["source_id"],
        0.667, "MWh/t_liquid_steel", "V2OBS005 (Vogl2018 scrap EAF)",
        "Scrap EAF, liquid steel; Pimm oxyfuel EAF 0.425 (V2OBS020) is a different furnace specification",
        "match", "FIN 0.667 equals Vogl scrap-EAF value", "Cycle2: keep; note POSCO Gwangyang EAF actual not observed")
    add("steel_hyrex", "electricity", fin("steel_hyrex", "elec_intensity"), "MWh/t", d3["steel_hyrex"]["source_id"],
        None, "", "none", "POSCO HyREX fluidized-bed fines route; no primary process balance in research_v2",
        "no_primary_source", "Copied from steel_h2dri", "Cycle2: search POSCO/RIST HyREX publications; else keep NA with theta alternative")
    add("steel_hyrex", "hydrogen", fin("steel_hyrex", "h2_intensity"), "kg/t", d3["steel_hyrex"]["source_id"],
        None, "", "none", "same as above", "no_primary_source", "Copied from steel_h2dri", "Cycle2")
    add("steel_h2inj", "hydrogen", fin("steel_h2inj", "h2_intensity"), "kg/t", d3["steel_h2inj"]["source_id"],
        None, "", "none", "BF hydrogen injection; NSC Super COURSE50 is a demonstration, internal coke-oven gas H2 vs purchased H2 unresolved",
        "no_primary_source", "Company programme value", "Cycle2: FORECAST 'Blast furnace H2' row is -99; need engineering study (e.g. Yilmaz 2017, Nogami) with injection rate")
    add("steel_h2inj", "electricity", fin("steel_h2inj", "elec_intensity"), "MWh/t", d3["steel_h2inj"]["source_id"],
        None, "", "none", "", "no_primary_source", "", "Cycle2")
    for t in ("steel_eff", "steel_scrap", "steel_hbi"):
        add(t, "coal", ROUTE["BF"][2], "GJ/t (retained 100%)", "ROUTE injection + retained_coal_fraction=1",
            None, "", "none", "Retrofit keeps full incumbent purchased coal; emission factor drop not linked to a coal saving",
            "internal_inconsistency", f"EF {fin(t,'emission_factor')} vs incumbent 2.15 implies coal saving that the energy ledger does not book",
            "Cycle2: either book coke-rate reduction per t or state that EF drop is not energy-linked")
    add("BF_incumbent", "coal", ROUTE["BF"][2], "GJ/t", "ROUTE injection (not observed)",
        17.1, "GJ/t_GCAM_steel", "GCAM public BLASTFUR gas_intensive 2025 delivered coal; FORECAST BF fuel 16.7GJ/t",
        "GCAM/FORECAST: whole integrated route incl. coke ovens/sinter; FIN 13.5 origin undocumented",
        "unobserved_incumbent", "GCAM 17.1 + gas 6.6 + elec 1.6 = 25.3GJ/t vs FIN 13.5+0.4+0.29 = 14.2GJ/t",
        "Cycle2: pull POSCO/NSC energy consumption from factbook/databook (already local) and derive per-t purchased energy")
    add("BF_incumbent", "electricity", ROUTE["BF"][1], "MWh/t", "ROUTE injection (not observed)",
        round(1.6 * MWH_PER_GJ, 3), "MWh/t_GCAM_steel", "GCAM public BLASTFUR elect_td_ind 2025",
        "", "unobserved_incumbent", "FIN 0.08 is 5.6x below GCAM default", "Cycle2 as above")
    add("EAF_incumbent", "electricity", ROUTE["EAF"][1], "MWh/t", "ROUTE injection (not observed)",
        0.667, "MWh/t_liquid_steel", "V2OBS005", "", "unobserved_incumbent",
        "Incumbent EAF 0.55 differs from transition steel_eaf 0.667 for the same furnace type", "Cycle2: unify or justify")

    # ---------------- petchem (all per t ethylene; D1a NCC capacity unit is t ethylene/yr) ----------------
    heat_gj = l_heat * 3.6
    add("NCC_incumbent", "gas", ROUTE["NCC"][3], "GJ/t_ethylene", "ROUTE injection (not observed)",
        round(heat_gj, 1), "GJ/t_ethylene (fired furnace duty)", "LAY014 (Layritz2021 A.2 heat 6.78MWh) ; FORECAST steam cracking fuel 33.94GJ/t",
        "Furnace fuel is internal byproduct methane 0.488t/t (LAY015), not purchased gas",
        "boundary_mismatch",
        f"FIN books 8GJ/t as purchased gas; primary sources give {heat_gj:.1f}-33.9GJ/t of furnace duty supplied internally. Purchased-gas share of Korean/Japanese NCCs not observed",
        "Cycle3: split furnace duty into internal fuel gas vs purchased LNG using site data; 8GJ/t stays NA until sourced")
    add("NCC_incumbent", "electricity", ROUTE["NCC"][1], "MWh/t_ethylene", "ROUTE injection (not observed)",
        l_el0, "MWh/t_ethylene", "LAY013 (Layritz2021 A.2)", "Purchased electricity, steam-driven compressors",
        "order_of_magnitude_consistent", "0.35 vs 0.21; both exclude electric compressor drives", "Cycle3: LOTTE Scope2 -> site electricity if disclosed")
    add("petchem_ecracker", "electricity", fin("petchem_ecracker", "elec_intensity"), "MWh/t_ethylene", d3["petchem_ecracker"]["source_id"],
        l_el1, "MWh/t_ethylene", "LAY021 (Layritz2021 A.3 total electric, incl. 6.78 furnace)",
        "Fully electric furnace, same naphtha 3.58t/t, methane 0.55t/t becomes export",
        "boundary_mismatch",
        f"FIN 2.8 is {l_el1/fin('petchem_ecracker','elec_intensity'):.2f}x below Layritz; BASF 1.5MWh/t is per t hydrocarbon FEED ({1.5*l_naph:.2f}MWh/t ethylene at 3.58t naphtha/t)",
        "Cycle3: re-derive on t-ethylene basis; keep methane export as separate netback flow; Fitriasari2026 for plasma/direct heating")
    add("petchem_ecracker_hybrid", "electricity", fin("petchem_ecracker_hybrid", "elec_intensity"), "MWh/t_ethylene", d3["petchem_ecracker_hybrid"]["source_id"],
        round(0.4 * l_el1, 2), "MWh/t_ethylene", "0.4 x LAY021", "40% furnace electrification blend",
        "derived_from_mismatched_base", "1.0 vs 2.8 (0.4x6.99) if blended on Layritz basis", "Cycle3: recompute after ecracker fix")
    h2_gj = fin("petchem_h2fuel", "h2_intensity") * LHV_H2_GJ_PER_KG
    add("petchem_h2fuel", "hydrogen", fin("petchem_h2fuel", "h2_intensity"), "kg/t_ethylene", d3["petchem_h2fuel"]["source_id"],
        round(0.5 * heat_gj / LHV_H2_GJ_PER_KG, 1), "kgH2/t_ethylene (50% of Layritz furnace duty)", "0.5 x LAY014 / 0.12GJ/kg",
        "50% fuel displacement of fired duty", "internal_inconsistency",
        f"83kg = {h2_gj:.1f}GJ of H2 but FIN displaces only 50% x 8GJ = 4GJ purchased gas (retained_gas_fraction 0.5); on Layritz duty 50% = {0.5*heat_gj:.1f}GJ = {0.5*heat_gj/LHV_H2_GJ_PER_KG:.0f}kg",
        "Cycle3: tie H2 quantity to displaced furnace duty and boiler efficiency; Mitsui Osaka is ammonia not H2")
    add("petchem_hp_whr", "electricity", fin("petchem_hp_whr", "elec_intensity"), "MWh/t_ethylene", d3["petchem_hp_whr"]["source_id"],
        None, "", "none", "", "no_primary_source", "IEA HTHP generic", "Cycle3: keep as T5 assumption")
    return R, dict(vogl_electrolysis_mwh=vogl_electrolysis_mwh, vogl_residual=vogl_residual, layritz_duty_gj=heat_gj)


def main():
    d3, pkgs = load_d3(), load_pkg()
    R, diag = rows(d3, pkgs)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0].keys()))
        w.writeheader(); w.writerows(R)
    counts = {}
    for r in R:
        counts[r["boundary_status"]] = counts.get(r["boundary_status"], 0) + 1
    md = ["# 기술별 에너지 수요 등록부 (회차 1, 2026-09-07)", "",
          "FIN 엔진이 현재 쓰는 값과 research_v2에서 확인한 원 연구 값을 같은 행에 놓고 공정 경계 일치 여부를 판정한다. "
          "자동 채택 0건. 재생성: `scripts/build_tech_energy_register.py`.", "",
          "| 상태 | 행 수 |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in sorted(counts.items())] + ["",
          "| 기술 | 캐리어 | FIN 값 | 원 연구 값 | 원 연구 ID | 판정 | 도출 |", "|---|---|---:|---:|---|---|---|"]
    for r in R:
        rv = "NA" if r["reference_value"] is None else r["reference_value"]
        md.append(f"| {r['tech_id']} | {r['carrier']} | {r['fin_value']} {r['fin_unit']} | {rv} {r['reference_unit']} | {r['reference_id']} | {r['boundary_status']} | {r['derivation']} |")
    md += ["", f"진단값: Vogl 수전해 전력 {diag['vogl_electrolysis_mwh']:.3f}MWh/t, 잔여 {diag['vogl_residual']:.3f}MWh/t; Layritz 분해로 열 {diag['layritz_duty_gj']:.1f}GJ/t 에틸렌.",
           "", "이 등록부는 FIN/EFF 입력을 바꾸지 않는다. 판정 `match`는 값과 경계가 같다는 뜻이며 국내 설비 실측이라는 뜻이 아니다."]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    # self-check
    assert all(r["automatically_adopted"] is False for r in R)
    assert abs(diag["vogl_residual"] - (3.48 - 51 * 0.12 / 0.72 / 3.6)) < 1e-9
    assert counts.get("boundary_mismatch", 0) >= 3, counts
    print(f"{len(R)} rows -> {OUT_CSV.relative_to(ROOT)}; statuses {counts}")


if __name__ == "__main__":
    main()
