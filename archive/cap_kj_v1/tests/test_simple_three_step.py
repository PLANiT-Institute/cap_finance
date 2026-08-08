import csv
from pathlib import Path
import tempfile
import unittest

from cap_kj.simple_three_step import (
    COMPANY_ORDER,
    FIGURE_NAMES,
    _read,
    build_simple_three_step,
    generate_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class SimpleThreeStepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = build_simple_three_step(
            _read(ROOT / "outputs/tables/company_emissions_pathway_mvp.csv"),
            _read(ROOT / "outputs/tables/company_pathway_uncertainty_mvp.csv"),
            _read(ROOT / "outputs/tables/company_capital_flow_bridge_mvp.csv"),
            _read(ROOT / "data/processed/simple_three_step_assumptions.csv"),
        )
        cls.indexed = {str(row["company_id"]): row for row in cls.rows}

    def test_fixed_company_grain_and_sector_allocation(self) -> None:
        self.assertEqual(len(self.rows), 4)
        self.assertEqual(set(self.indexed), set(COMPANY_ORDER))
        for sector in ("steel", "petrochemicals"):
            self.assertAlmostEqual(
                sum(float(row["company_gcap_allocation_weight"]) for row in self.rows if row["sector"] == sector),
                1,
            )

    def test_gcap_and_capital_gap_reconcile(self) -> None:
        for row in self.rows:
            required = float(row["gcam_aligned_2050_required_reduction_tco2e"])
            intensity = float(row["gcap_capital_intensity_base_usd_2025_per_annual_tco2e"])
            gcap = float(row["company_gcap_base_usd_2025"])
            self.assertAlmostEqual(gcap, required * intensity, places=2)
            self.assertAlmostEqual(
                float(row["identified_route_capital_usd_2025"]) + float(row["capital_level_gap_base_usd_2025"]),
                gcap,
                places=2,
            )

    def test_level_and_premium_rates_reconcile_to_high_case(self) -> None:
        for row in self.rows:
            self.assertAlmostEqual(
                float(row["level_gap_rate_on_gcap"]) + float(row["transition_premium_proxy_rate_on_gcap"]),
                float(row["total_high_case_hurdle_rate_on_gcap"]),
            )
            self.assertGreater(float(row["transition_premium_proxy_rate_on_gcap"]), 0)

    def test_mechanism_result_is_simple_and_bounded(self) -> None:
        for row in self.rows:
            self.assertEqual(float(row["level_only_gap_closure_ratio"]), 0)
            self.assertGreater(float(row["combined_gap_closure_ratio"]), 0)
            self.assertLess(float(row["combined_gap_closure_ratio"]), 1)
        for company in ("POSCO", "NIPPON_STEEL"):
            self.assertGreater(float(self.indexed[company]["premium_mitigation_only_gap_closure_ratio"]), 0)
        for company in ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
            self.assertEqual(float(self.indexed[company]["premium_mitigation_only_gap_closure_ratio"]), 0)

    def test_market_risk_premium_is_not_invented(self) -> None:
        for row in self.rows:
            self.assertEqual(row["transition_risk_premium_bps"], "NA")
            self.assertIn("not_market_priced", row["premium_proxy_status"])
            self.assertIn("not WACC", row["boundary_note"])

    def test_assumption_metadata_is_explicit(self) -> None:
        with (ROOT / "data/processed/simple_three_step_assumptions.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["value_type"], "estimated")
            self.assertEqual(row["price_year"], "2025")
            self.assertEqual(row["quality_flag"], "D")
            self.assertTrue(row["source_id"])
            self.assertTrue(row["formula_or_method"])
            self.assertTrue(row["boundary_note"])
            self.assertLessEqual(float(row["value_low"]), float(row["value_base"]))
            self.assertLessEqual(float(row["value_base"]), float(row["value_high"]))

    def test_output_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            outputs = generate_outputs(
                ROOT / "outputs/tables/company_emissions_pathway_mvp.csv",
                ROOT / "outputs/tables/company_pathway_uncertainty_mvp.csv",
                ROOT / "outputs/tables/company_capital_flow_bridge_mvp.csv",
                ROOT / "data/processed/simple_three_step_assumptions.csv",
                target / "table.csv",
                target / "figures",
                target / "report.md",
            )
            self.assertEqual(len(outputs), 5)
            self.assertEqual({path.name for path in outputs[1:4]}, set(FIGURE_NAMES))
            self.assertTrue(all(path.exists() and path.stat().st_size > 1000 for path in outputs))


if __name__ == "__main__":
    unittest.main()
