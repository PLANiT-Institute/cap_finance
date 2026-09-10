"""Transcribe and audit selected institutional-preprint inventories.

Keep inconsistent source cells visible; no silent correction or FIN export.
"""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "tmp/pdfs/tcar_research_v2"
OUT = ROOT / "data/research_v2/evidence"


def main():
    source = json.loads((RAW / "layritz_2021_preprint.json").read_text())
    assert hashlib.sha256((RAW / "layritz_2021_preprint.pdf").read_bytes()).hexdigest() == source["sha256"]
    pages = (RAW / "layritz_2021_preprint.txt").read_text().split("\f")
    assert "Table Appendix A.2: Conventional Steam Cracking" in pages[34]
    assert "Table Appendix A.3: Electrified Steam Cracking" in pages[35]
    rows = []

    def add(page, route, stream, field, value, unit, category, use):
        rows.append(dict(observation_id=f"LAY{len(rows)+1:03d}",
            source_url=source["url"], source_sha256=source["sha256"],
            source_version="institutional_preprint_not_verified_against_final_version",
            doi="10.1016/j.apenergy.2021.117049", pdf_page=page, printed_page=page-1,
            table="A.2" if page==35 else "A.3", route=route, stream=stream,
            field=field, value=value, unit=unit, flow_category=category,
            use_status=use, extraction="manual_table_transcription_with_visual_QA",
            automatically_adopted=False))

    ref="reference_pending_final_version_and_scope"
    for page,route in [(35,"conventional_naphtha"),(36,"electrified_naphtha")]:
        add(page,route,"naphtha","mass",3.58,"t/t_ethylene","purchased_feedstock",ref)
        add(page,route,"naphtha","energy",44.2,"MWh/t_ethylene","feedstock_LHV_not_process_fuel",ref)
        add(page,route,"naphtha","carbon",3.19,"tC/t_ethylene","feedstock_carbon",ref)
        add(page,route,"ethylene","mass",1.,"t/t_ethylene","main_product",ref)
        add(page,route,"hydrogen_export","mass",.032,"tH2/t_ethylene","coproduct_export_not_H2_purchase",ref)
        add(page,route,"byproducts","mass",2.03,"t/t_ethylene","aggregated_coproducts",ref)
    add(35,"conventional_naphtha","electricity","energy",.21,"MWh/t_ethylene","purchased_electricity",ref)
    add(35,"conventional_naphtha","heat","energy",6.78,"MWh/t_ethylene","internal_methane_combustion_not_purchased_gas",ref)
    add(35,"conventional_naphtha","methane_fuel","mass",.488,"tCH4/t_ethylene","internal_recycle",ref)
    add(35,"conventional_naphtha","methane_export","mass",.057,"tCH4/t_ethylene","coproduct_export",ref)
    add(35,"conventional_naphtha","methane_export","carbon",.02,"tC/t_ethylene","coproduct_carbon","held_inconsistent_with_system_expansion_0.043")
    add(35,"conventional_naphtha_expanded","methane_export","carbon",.043,"tC/t_ethylene","coproduct_carbon",ref)
    add(35,"conventional_naphtha_expanded","additional_grid","energy",3.39,"MWh/t_ethylene","LCA_system_expansion_not_cracker_purchase",ref)
    add(35,"conventional_naphtha_expanded","electricity_output","energy",4.32,"MWh/t_ethylene","LCA_functional_unit_not_cracker_power_demand",ref)
    add(36,"electrified_naphtha","electricity","energy",6.99,"MWh/t_ethylene","total_including_furnace_interpretation_pending",ref)
    add(36,"electrified_naphtha","furnace_electricity","energy",6.78,"MWh/t_ethylene","component_do_not_add_to_6.99",ref)
    add(36,"electrified_naphtha","methane_export","mass",.55,"tCH4/t_ethylene","rounded_coproduct_export",ref)
    add(36,"electrified_naphtha","methane_export","carbon",.76,"tC/t_ethylene","coproduct_carbon","held_carbon_mass_exceeds_total_methane_mass")
    add(36,"electrified_naphtha_expanded","methane_export","mass",.545,"tCH4/t_ethylene","coproduct_export",ref)
    add(36,"electrified_naphtha_expanded","methane_export","carbon",.409,"tC/t_ethylene","coproduct_carbon",ref)
    add(36,"electrified_naphtha_expanded","electricity_output","energy",4.32,"MWh/t_ethylene","LCA_functional_unit_not_cracker_power_demand",ref)
    with (OUT / "layritz_preprint_inventory_cells.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    checks=[]

    def check(name,lhs,rhs,tolerance,interpretation):
        checks.append(dict(check=name,reported_or_left=lhs,independent_or_right=rhs,
            difference=lhs-rhs,absolute_tolerance=tolerance,
            agrees=abs(lhs-rhs)<=tolerance,interpretation=interpretation))

    check("electricity_total_equals_base_plus_furnace",6.99,.21+6.78,1e-10,
          "Supports nested-total interpretation; adding6.99+6.78 double counts furnace")
    check("methane_before_and_after_electrification",.545,.488+.057,1e-10,
          "Furnace fuel becomes export; not a reduction in purchased natural gas")
    check("methane_carbon_A3",.76,.55*12/16,.006,
          "Source preprint carbon mass exceeds total methane mass; hold cell")
    check("methane_carbon_A2",.02,.057*12/16,.001,
          "Conflicts with chemical stoichiometry and same-page system-expansion0.043")
    check("methane_carbon_A3_system_expansion",.409,.545*12/16,.001,
          "Rounded elemental stoichiometry compatible; no silent replacement of other cell")
    check("naphtha_mass_balance_conventional",3.58,1+.488+.057+.032+2.03,.03,
          "Rounded aggregate outputs; not a full chemical-species process validation")
    (OUT / "layritz_preprint_checks.json").write_text(json.dumps(dict(
        source=source,numeric_cells=len(rows),checks=checks,
        source_cells_held=sum(r["use_status"].startswith("held_") for r in rows),
        preliminary_cost_difference="6.78*electricity_price_per_MWh -0.488*exportable_methane_netback_per_t; before capex, steam, compression and other changes",
        preliminary_cost_formula_status="conditional_algebra_only; exportability and process heat assumptions not established for Korean/Japanese NCC",
        final_published_inventory_match_verified=False,FIN_input_exported=False),indent=2)+"\n")
    print(json.dumps({"numeric_cells":len(rows),"arithmetic_checks":len(checks),
        "unresolved_source_inconsistencies":sum(not c["agrees"] for c in checks),"FIN_input_exported":False}))


if __name__=="__main__":main()
