"""Company-reported energy use -> purchased-energy intensities (research_v2).

Transcribed from local copies of company reports (tmp/pdfs, not tracked). Each
row keeps the native number, unit, page/line anchor and the accounting boundary.
Derived intensities divide company totals by company crude steel; they are
company-wide, not per-furnace, and are compared with the ROUTE constants that
scripts/prepare_raw.py injects. Nothing here mutates FIN/EFF inputs.

Output: data/research_v2/evidence/company_energy_observations.csv
        data/research_v2/evidence/company_energy_intensities.csv
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/research_v2/evidence"
GJ_PER_T_COAL = 28.0  # src/cap/plancost.py GJ_PER_T_COAL — engine convention, not POSCO's coal LHV

SRC = {
    "posco_factbook_2024": ("tmp/pdfs/tcar_steel_sources/posco_factbook_2024.pdf", "https://sustainability.posco.co.kr/assets/file/2024_POSCO_ESG_Factbook.pdf"),
    "nsc_databook_2025": ("tmp/pdfs/tcar_steel_sources/nsc_databook_2025.pdf", "https://www.nipponsteel.com/en/ir/library/pdf/nsc_en_ir_2025_databook_print.pdf"),
    "lotte_esg_2025": ("tmp/pdfs/tcar_petchem_sources/lotte_esg_2025.pdf", "https://www.lottechem.com/pdfRead.do?fileId=FILE_260803112356995"),
}

# (obs_id, source, txt_line, item, year, value, unit, boundary)
OBS = [
    ("CE001", "posco_factbook_2024", 70, "crude_steel_production", 2024, 35_048_000, "t", "POSCO company (전사)"),
    ("CE002", "posco_factbook_2024", 166, "energy_use_total", 2024, 359_242_804, "GJ", "K-ETS energy + renewable; coal reported as reductant/raw material and excluded (note 2, line 1133)"),
    ("CE003", "posco_factbook_2024", 170, "natural_gas", 2024, 60_987_933, "GJ", "purchased fuel"),
    ("CE004", "posco_factbook_2024", 172, "byproduct_gas", 2024, 284_088_474, "GJ", "internal (COG/BFG/LDG); not purchased"),
    ("CE005", "posco_factbook_2024", 188, "electricity", 2024, 10_963_428, "GJ", "purchased electricity, unit conversion factor applied by POSCO (note 3); excludes renewable purchases"),
    ("CE006", "posco_factbook_2024", 190, "steam", 2024, 255_703, "GJ", "purchased steam"),
    ("CE007", "posco_factbook_2024", 194, "energy_intensity_crude_steel", 2024, 10.25, "GJ/t", "K-ETS basis, coal excluded"),
    ("CE008", "posco_factbook_2024", 84, "coking_coal_use", 2024, 22_566_000, "t", "raw material table; feedstock, not in energy table"),
    ("CE009", "posco_factbook_2024", 82, "iron_ore_use", 2024, 49_369_000, "t", "raw material table"),
    ("CE010", "posco_factbook_2024", 111, "scope12_intensity_crude_steel", 2024, 2.03, "tCO2e/t", "Scope1+2, company"),
    ("CE011", "nsc_databook_2025", 1377, "energy_consumption_nonconsol", 2024, 869, "PJ", "FY2024 Non-Consol.; includes energy for purchased coke and oxygen (notes 3,4); excludes IPP (note 2); Japanese accounting includes coal"),
    ("CE012", "nsc_databook_2025", 1377, "energy_consumption_total", 2024, 924, "PJ", "FY2024 incl. EAF subsidiaries and Sanso Center"),
    ("CE013", "nsc_databook_2025", 1223, "crude_steel_production_nonconsol", 2024, 34_300_000, "t", "FY2024 Non-Consol.; PDF page19, printed page18; 3430 ten-thousand tons"),
    ("CE014", "lotte_esg_2025", 5662, "site_energy_yeosu_basic", 2024, 52_707, "TJ", "여수공장(기초) whole site incl. downstream; column order 2025|2024|2023"),
    ("CE015", "lotte_esg_2025", 5664, "site_energy_daesan", 2024, 44_385, "TJ", "대산공장 whole site"),
    ("CE016", "lotte_esg_2025", 5669, "nonrenewable_fuel", 2024, 74_919, "TJ", "company fuel; purchased vs internal fuel-gas split not disclosed"),
    ("CE017", "lotte_esg_2025", 5670, "nonrenewable_electricity", 2024, 21_822, "TJ", "company electricity"),
    ("CE018", "lotte_esg_2025", 5671, "nonrenewable_steam", 2024, 16_334, "TJ", "company steam"),
    ("CE019", "lotte_esg_2025", 5682, "self_generation", 2024, 12_787, "TJ", "총 자가발전 생산량"),
    ("CE020", "lotte_esg_2025", 5602, "scope1_yeosu_basic", 2024, 1_886_740, "tCO2e", "final statement 2024"),
    ("CE021", "lotte_esg_2025", 5605, "scope1_daesan", 2024, 1_534_019, "tCO2e", "final statement 2024"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "missing_local_copy"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hashes = {k: sha(ROOT / v[0]) for k, v in SRC.items()}
    with (OUT / "company_energy_observations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["observation_id", "source_id", "source_url", "local_sha256", "txt_line", "item", "year", "value", "unit", "boundary", "automatically_adopted"])
        for o in OBS:
            w.writerow([o[0], o[1], SRC[o[1]][1], hashes[o[1]], o[2], o[3], o[4], o[5], o[6], o[7], False])
    v = {o[0]: o[5] for o in OBS}
    q = v["CE001"]
    rows = [
        ("POSCO", "purchased_natural_gas", v["CE003"] / q, "GJ/t_crude", "CE003/CE001", 0.4, "ROUTE BF gas GJ/t (per t hot metal)"),
        ("POSCO", "purchased_electricity", None, "MWh/t_crude", "withheld: source energy conversion coefficient unspecified", 0.08, "Do not infer purchased MWh using3.6; footnote3 states conversion coefficient applied without its value"),
        ("POSCO", "reported_electricity_energy_ratio", v["CE005"] / q, "reported_GJ/t_crude", "CE005/CE001", None, "Reported accounting-energy ratio; not purchased MWh intensity"),
        ("POSCO", "internal_byproduct_gas", v["CE004"] / q, "GJ/t_crude", "CE004/CE001", None, "not a FIN field; internal transfer"),
        ("POSCO", "coking_coal", v["CE008"] / q * GJ_PER_T_COAL, "GJ/t_crude (28GJ/t engine factor)", "CE008/CE001*28", 13.5, "ROUTE BF coal GJ/t; GCAM BLASTFUR 17.1; FORECAST 16.7"),
        ("POSCO", "kets_energy_intensity", v["CE007"], "GJ/t_crude", "CE007", None, "coal excluded"),
        ("NSC", "total_energy_incl_coal", v["CE011"] * 1e6 / v["CE013"], "GJ/t_crude", "CE011/CE013", 25.3, "GCAM BLASTFUR gas_intensive 2025 sum (17.1+6.6+1.6); boundary differs (coke/oxygen upstream included)"),
        ("LOTTE", "site_energy_yeosu_basic_per_t_ethylene_capacity", v["CE014"] * 1e3 / 1_230_000, "GJ/t_ethylene_capacity", "CE014/1.23Mt", 8.0 + 0.35 * 3.6, "Capacity-normalized whole-site statistic; NOT an upper bound on actual NCC intensity without utilization and process-energy share"),
        ("LOTTE", "site_energy_daesan_per_t_ethylene_capacity", v["CE015"] * 1e3 / 1_100_000, "GJ/t_ethylene_capacity", "CE015/1.1Mt", 8.0 + 0.35 * 3.6, "Capacity-normalized whole-site statistic; utilization and NCC energy share unresolved"),
    ]
    with (OUT / "company_energy_intensities.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["company", "quantity", "value", "unit", "derivation", "fin_route_value", "comparison_note", "use_status"])
        for r in rows:
            w.writerow([r[0], r[1], None if r[2] is None else round(r[2], 4), r[3], r[4], r[5], r[6], "withheld_missing_conversion" if r[2] is None else "company_wide_reference_not_furnace_input"])
    assert abs(v["CE003"] / q - 1.74) < 0.01
    print({r[0] + ":" + r[1]: None if r[2] is None else round(r[2], 3) for r in rows})


if __name__ == "__main__":
    main()
