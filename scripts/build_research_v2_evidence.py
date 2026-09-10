"""Rebuild a provenance-bearing evidence register; never mutate FIN inputs.

Numeric observations are curated transcriptions from inspected original pages.
Hash and page-anchor checks guard the transcription context, not physical validity.
Published model assumptions are not measurements or calibrated distributions.
"""
from pathlib import Path
import csv
import hashlib
import json
import sqlite3
from xlsx_table_reader import read_cells

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "tmp/pdfs/tcar_research_v2"
OUT = ROOT / "data/research_v2/evidence"
AUDIT = ROOT / "docs/research_cycles/2026-09-06"


def write_csv(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {x["source_id"]: x for x in json.loads(
        (AUDIT / "source_access_round1.json").read_text()) if x.get("sha256")}
    specs = {
        "vogl_2018": ("10.1016/j.jclepro.2018.08.279", "Published thermodynamic model; liquid steel; no casting/rolling; hot-base interpretation supported by p740 and POSTED author-correspondence note, correspondence not independently accessed"),
        "pimm_2021": ("10.1016/j.jclepro.2021.127665", "Vogl-derived model with hot DRI and updated EAF; not independent replication"),
        "linde_ecracker": ("", "Linde engineering article, CEP August 2024; normalized furnace heat balance, not plant intensity"),
    }
    for sid in specs:
        assert hashlib.sha256((RAW / (sid + ".pdf")).read_bytes()).hexdigest() == sources[sid]["sha256"]
    rows = []

    def add(sid, page, parameter, value, unit, route, condition, anchor):
        page_text = (RAW / (sid + ".txt")).read_text().split("\f")[page - 1]
        assert anchor in page_text, (sid, page, anchor)
        rows.append(dict(observation_id=f"V2OBS{len(rows)+1:03d}", source_id=sid,
            doi=specs[sid][0], source_url=sources[sid]["url"],
            source_sha256=sources[sid]["sha256"], pdf_page=page,
            parameter=parameter, value=value, unit=unit, route=route,
            condition=condition, source_boundary=specs[sid][1],
            extraction="manual_transcription_visual_QA_plus_hash_and_page_anchor",
            evidence_type="published_model_input_or_result" if sid != "linde_ecracker" else "vendor_engineering_claim",
            use_status="reference_only_pending_boundary_mapping",
            calibrated_uncertainty=False, automatically_adopted=False))

    v = "vogl_2018"
    add(v, 3, "electrolyser_efficiency", .72, "fraction_LHV", "onsite_electrolysis", "LHV basis; not HHV", "72%")
    add(v, 3, "electrolyser_temperature", 70, "degC", "onsite_electrolysis", "Process assumption", "70")
    add(v, 3, "shaft_temperature", 800, "degC", "H2_DRI", "Process assumption", "800")
    add(v, 3, "condenser_efficiency", .70, "fraction_HHV", "heat_recovery", "Not identical to Pimm Table1 75%", "70%")
    add(v, 3, "EAF_electricity_scrap", .667, "MWh/t_liquid_steel", "EAF_scrap", "100% scrap; source calibration", "0.667")
    add(v, 4, "hydrogen_input", 51, "kgH2/t_liquid_steel", "H2_DRI_EAF_base_HBI", "100% HBI; excludes H2 losses", "51 kg")
    add(v, 4, "pellet_input", 1504, "kg/t_liquid_steel", "H2_DRI_EAF_base_HBI", "100% HBI", "1504")
    add(v, 4, "hydrogen_input", 25, "kgH2/t_liquid_steel", "H2_DRI_EAF_base_HBI", "50:50 HBI/scrap charge", "25 kg")
    add(v, 4, "pellet_input", 738, "kg/t_liquid_steel", "H2_DRI_EAF_base_HBI", "50:50 HBI/scrap charge", "738")
    add(v, 4, "scrap_input", 536, "kg/t_liquid_steel", "H2_DRI_EAF_base_HBI", "50:50 HBI/scrap charge", "536")
    add(v, 4, "total_electricity", 3.48, "MWh/t_liquid_steel", "H2_DRI_EAF_onsite_H2", "Includes electrolysis; 100% HBI; not purchased-H2 electricity", "3.48")
    add(v, 5, "EAF_electricity_DRI", .753, "MWh/t_liquid_steel", "EAF_base_HBI", "100% DRI/HBI; hot-base interpretation; previous cold label withdrawn; POSTED private author clarification not independently accessed", "753")
    add(v, 5, "cold_charge_penalty", .159, "MWh/t_liquid_steel", "EAF_cold_vs_hot", "Cold HBI relative to hot direct feed; process-specific", "159")
    add(v, 6, "carbon_lime_electrode_emissions", .053, "tCO2/t_liquid_steel", "H2_DRI_EAF", "Includes lime-related emissions; not automatically onsite Scope1", "53 kg")
    p = "pimm_2021"
    add(p, 4, "electrolyser_efficiency", .72, "fraction", "onsite_electrolysis", "Table1 cites Vogl; inherited assumption", "72%")
    add(p, 4, "heat_exchanger_efficiency", .75, "fraction", "heat_recovery", "Table1 cites Vogl but differs from Vogl condenser HHV value", "75%")
    add(p, 4, "electrolyser_temperature", 70, "degC", "onsite_electrolysis", "Table1", "70")
    add(p, 4, "shaft_temperature", 800, "degC", "H2_DRI", "Table1", "800")
    add(p, 4, "metallisation", .94, "fraction", "H2_DRI", "Table1", "94%")
    add(p, 4, "EAF_electricity_scrap", .425, "MWh/t_liquid_steel", "EAF_scrap_oxyfuel", "Table1; oxy-fuel burners; not pure all-electric EAF equivalence", "425")
    add(p, 8, "total_energy", 3.43, "MWh/t_liquid_steel", "H2_DRI_EAF_hot", "Section3.1; reconcile against Table6 before adoption", "3.43")
    add(p, 8, "total_energy_scrap", .450, "MWh/t_liquid_steel", "EAF_scrap", "Section3.1; 100% scrap; broader than Table1 EAF alone", "450")
    add(p, 8, "hydrogen_input", 25.2, "kgH2/t_liquid_steel", "H2_DRI_EAF_hot", "50% scrap charge", "25.2")
    for scrap, h2, elec in [(0, 1.42, .51), (25, 1.06, .47), (50, .70, .43)]:
        add(p, 8, "hydrogen_demand_power", h2, "GW", "UK_system_H2_DRI_EAF", f"Table6; 7.2MtLS/yr; {scrap}% scrap; rounded power", "Hydrogen Demand")
        add(p, 8, "non_H2_electricity_power", elec, "GW", "UK_system_H2_DRI_EAF", f"Table6; 7.2MtLS/yr; {scrap}% scrap; rounded power", "Non-H2 Electricity")
    l = "linde_ecracker"
    add(l, 4, "electric_heat_transfer_efficiency_lower_claim", .95, "fraction", "electric_cracking_furnace", "At least95%; vendor engineering claim; not total plant SEC", "95%")
    for param, value in [("reaction_heat", 44), ("feed_steam_heating", 38), ("steam_superheat", 11), ("flue_gas_loss", 6), ("casing_loss", 1)]:
        add(l, 4, param, value, "percent_of_conventional_fired_heat", "conventional_cracker_furnace", "Figure4 normalized heat balance; no conversion to MWh/t without throughput and heat duty", "44%")
    write_csv("primary_process_observations.csv", rows)

    # Diagnostic only: rounded LHV is an explicit conversion assumption.
    e_h2 = (120 / 3.6) / .72
    residue = 3.48 - 51 * e_h2 / 1000
    legacy = .85
    diagnostic = dict(
        source="Vogl2018", electrolyser_LHV_efficiency=.72,
        hydrogen_LHV_conversion_assumption_MJ_per_kg=120,
        implied_electrolyser_kWh_per_kg=e_h2,
        total_electricity_MWh_per_t=3.48, hydrogen_kg_per_t=51,
        inferred_non_electrolyser_electricity_MWh_per_t=residue,
        legacy_FIN_electricity_MWh_per_t=legacy,
        difference_MWh_per_t=residue-legacy,
        difference_relative_to_legacy=residue/legacy-1,
        use_status="diagnostic_not_adopted",
        reasons=["Rounded aggregate values; supply temperature and heat recovery boundary require reconciliation",
                 "Do not charge total onsite electrolysis electricity plus purchased hydrogen",
                 "51kWh/kg is not the efficiency assumption of the cited Vogl model"],
        pimm_table6_0scrap_non_H2_MWh_per_t=.51*8760/7200,
        pimm_table6_0scrap_total_if_H2_LHV_and_eta72=(1.42/.72+.51)*8760/7200,
        pimm_section31_total_MWh_per_t=3.43,
        pimm_status="unresolved_cross_table_boundary_or_reporting_difference; do_not_average")
    (OUT / "steel_boundary_diagnostics.json").write_text(json.dumps(diagnostic, indent=2)+"\n")

    supplements = json.loads((RAW / "pimm_data_downloads.json").read_text())
    supplement = next(x for x in supplements if x["file"] == "pimm_hydrogen_steelmaking_inputs.xlsx")
    path = RAW / supplement["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == supplement["sha256"]
    cells = read_cells(path)["Sheet1"]
    supplement_rows = []
    for r in range(2,24):
        assert all(cells[(r,c)]["formula"] is None for c in (1,2,3))
        supplement_rows.append(dict(observation_id=f"PIMM_SI_{r:02d}",
            parameter=cells[(r,1)]["value"], value=cells[(r,2)]["value"], unit=cells[(r,3)]["value"],
            source_url=supplement["url"], source_sha256=supplement["sha256"], sheet="Sheet1",
            value_cell=f"B{r}", source_doi="10.5518/997", upstream_source="Vogl2018 per A25",
            currency_conversion="1.10 EUR/GBP per A26", price_year_verified=False,
            independent_of_Vogl=False, scope="Native published input; tLS and tCS retained as printed; not normalized",
            use_status="reference_only_pending_boundary_and_price_year_verification", automatically_adopted=False))
    write_csv("pimm_published_input_cells.csv", supplement_rows)

    metadata = json.loads((RAW / "forecast_sites_download.json").read_text())
    db = RAW / "forecast_sites_input.sqlite"
    assert hashlib.sha256(db.read_bytes()).hexdigest() == metadata["sha256"]
    con = sqlite3.connect("file:"+str(db)+"?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    native = [dict(r) for r in con.execute("SELECT p.name product_name, t.name process_name, m.* FROM product_process_mapping_jrc m JOIN id_product p ON p.id=m.id_product JOIN id_process t ON t.id=m.id_process WHERE m.id_product IN (22,51) ORDER BY m.id_product,m.id_process")]
    carriers = {}
    for table, field in [("process_energy_carrier_mapping_jrc", "fuel_share"), ("process_feedstock_mapping_jrc", "feedstock_share"), ("process_steam_mapping_jrc", "steam_share")]:
        for r in con.execute("SELECT * FROM "+table+" WHERE id_product IN (22,51)"):
            carriers.setdefault((r["id_product"], r["id_process"]), {}).setdefault(field, []).append({"native_energy_carrier_id":r["id_energy_carrier"], "share":r[field]})
    for r in native:
        sentinel = [k for k,v in r.items() if isinstance(v, (float,int)) and v == -99]
        r.update(repository_commit=metadata["repository_commit"], source_sha256=metadata["sha256"], source_url=metadata["url"],
                 paper_snapshot_match_verified=False,
                 missing_sentinel_fields=";".join(sentinel),
                 carrier_mapping_json=json.dumps(carriers.get((r["id_product"],r["id_process"]),{}), sort_keys=True),
                 use_status="blocked_missing_sentinel" if sentinel else "reference_pending_physical_scope_and_price_year_verification",
                 automatically_adopted=False)
        if r["id_product"] == 22 and r["id_process"] == 44:
            r["use_status"] = "blocked_H2_feedstock_route_not_verified_as_NCC_furnace_fuel"
    con.close()
    write_csv("forecast_sites_native_selected.csv", native)
    result = dict(primary_numeric_observations=len(rows), source_documents=len(specs),
                  published_supplement_numeric_cells=len(supplement_rows),
                  forecast_sites_native_rows=len(native), forecast_rows_with_sentinel=sum(bool(r["missing_sentinel_fields"]) for r in native),
                  automatically_adopted_coefficients=0, calibrated_distributions=0,
                  semantic_checks="original page inspection; not independent process-model replication",
                  legacy_engine_mutated=False)
    (OUT / "manifest.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
