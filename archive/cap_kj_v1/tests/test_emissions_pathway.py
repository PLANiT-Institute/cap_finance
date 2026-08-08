import csv
from pathlib import Path
import tempfile
import unittest

from cap_kj.emissions_pathway import (
    COMPANY_ORDER,
    _read,
    build_pathway_tables,
    build_uncertainty_table,
)
from cap_kj.pathway_outputs import FIGURE_NAMES, generate_outputs


ROOT = Path(__file__).resolve().parents[1]


class EmissionsPathwayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facilities, cls.pathways = build_pathway_tables(
            _read(ROOT / "outputs/tables/facility_annual_cost_gap_mvp.csv"),
            _read(ROOT / "outputs/tables/company_annual_cost_gap_mvp.csv"),
            _read(ROOT / "outputs/tables/company_production_coverage_status_mvp.csv"),
            _read(ROOT / "outputs/tables/facility_physical_constraint_mvp.csv"),
            _read(ROOT / "data/processed/sector_emissions_pathway_anchors_mvp.csv"),
        )
        cls.uncertainty = build_uncertainty_table(
            _read(ROOT / "outputs/tables/facility_annual_cost_gap_mvp.csv"),
            _read(ROOT / "outputs/tables/company_annual_cost_gap_mvp.csv"),
            _read(ROOT / "outputs/tables/route_annual_cost_gap_inputs_mvp.csv"),
            cls.facilities,
        )

    def test_four_company_milestone_grain(self) -> None:
        self.assertEqual(len(self.pathways), 16)
        self.assertEqual(
            {(row["company_id"], row["year"]) for row in self.pathways},
            {(company, year) for company in COMPANY_ORDER for year in (2025, 2030, 2040, 2050)},
        )

    def test_common_start_matches_official_baseline(self) -> None:
        for row in self.pathways:
            if row["year"] == 2025:
                baseline = float(row["official_baseline_operational_ghg_tco2e"])
                self.assertAlmostEqual(float(row["current_policies_operational_ghg_tco2e"]), baseline)
                self.assertAlmostEqual(float(row["net_zero_operational_envelope_tco2e"]), baseline)
                self.assertAlmostEqual(float(row["conditional_facility_pathway_emissions_tco2e"]), baseline)

    def test_2050_gap_identity_and_capital_reconciliation(self) -> None:
        for company in COMPANY_ORDER:
            row = next(row for row in self.pathways if row["company_id"] == company and row["year"] == 2050)
            company_facilities = [facility for facility in self.facilities if facility["company_id"] == company]
            assigned = sum(float(facility["assigned_abatement_to_2050_gap_tco2e"]) for facility in company_facilities)
            capex = sum(float(facility["assigned_transition_capex_usd_2025"]) for facility in company_facilities)
            annual_gap = sum(float(facility["assigned_annual_resource_gap_usd_2025"]) for facility in company_facilities)
            baseline = float(row["official_baseline_operational_ghg_tco2e"])
            envelope = float(row["net_zero_operational_envelope_tco2e"])
            pathway = float(row["conditional_facility_pathway_emissions_tco2e"])
            self.assertAlmostEqual(pathway, baseline - assigned, places=3)
            self.assertAlmostEqual(float(row["unclosed_gap_to_net_zero_tco2e"]), max(pathway - envelope, 0), places=3)
            self.assertAlmostEqual(float(row["cumulative_pathway_capex_usd_2025"]), capex, places=2)
            self.assertAlmostEqual(float(row["annual_resource_gap_at_committed_pathway_scope_usd_2025"]), annual_gap, places=2)
            implied = [float(row[f"implied_unclosed_capital_{case}_usd_2025"]) for case in ("low", "base", "high")]
            self.assertLessEqual(implied[0], implied[1])
            self.assertLessEqual(implied[1], implied[2])
            self.assertAlmostEqual(
                float(row["implied_total_pathway_capital_base_usd_2025"]),
                capex + implied[1],
                places=2,
            )

    def test_gwangyang_uses_disclosed_project_capacity_constraint(self) -> None:
        row = next(row for row in self.facilities if row["facility_id"] == "KR_POSCO_GWANGYANG")
        self.assertAlmostEqual(float(row["physical_availability_ratio"]), 0.13145794475141562)
        self.assertEqual(row["project_evidence_status"], "official_2p5mt_capacity_and_krw600bn_investment_observed")

    def test_uncertainty_ranges_are_ordered_and_fixed_grain(self) -> None:
        self.assertEqual(len(self.uncertainty), 12)
        for row in self.uncertainty:
            low = float(row["annual_resource_gap_low_usd_2025"])
            base = float(row["annual_resource_gap_base_usd_2025"])
            high = float(row["annual_resource_gap_high_usd_2025"])
            self.assertLessEqual(low, base)
            self.assertLessEqual(base, high)

    def test_system_abatement_is_never_claimed(self) -> None:
        for row in self.pathways:
            self.assertIn("not_modelled", row["system_abatement_status"])
        for row in self.facilities:
            self.assertIn("system abatement", row["boundary_note"])

    def test_investor_output_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            outputs = generate_outputs(
                ROOT / "outputs/tables/company_emissions_pathway_mvp.csv",
                ROOT / "outputs/tables/company_pathway_uncertainty_mvp.csv",
                target / "figures",
                target / "report.md",
            )
            self.assertEqual(len(outputs), 5)
            self.assertEqual({path.name for path in outputs[:-1]}, set(FIGURE_NAMES))
            self.assertTrue(all(path.exists() and path.stat().st_size > 1000 for path in outputs))


class PathwayAnchorTests(unittest.TestCase):
    def test_anchor_metadata_and_ranges(self) -> None:
        with (ROOT / "data/processed/sector_emissions_pathway_anchors_mvp.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 16)
        for row in rows:
            low, base, high = (float(row[f"emissions_index_{case}"]) for case in ("low", "base", "high"))
            self.assertLessEqual(low, base)
            self.assertLessEqual(base, high)
            self.assertTrue(row["source_id"])
            self.assertTrue(row["formula_or_method"])
            self.assertTrue(row["boundary_note"])
            self.assertIn(row["value_type"], {"observed", "estimated", "allocated"})


if __name__ == "__main__":
    unittest.main()
