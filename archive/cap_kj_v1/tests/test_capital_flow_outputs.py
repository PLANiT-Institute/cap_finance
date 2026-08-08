from pathlib import Path
import tempfile
import unittest

from cap_kj.capital_flow_outputs import (
    COMPANY_ORDER,
    FIGURE_NAMES,
    _read,
    build_capital_flow_bridge,
    generate_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class CapitalFlowOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = build_capital_flow_bridge(
            _read(ROOT / "outputs/tables/company_emissions_pathway_mvp.csv"),
            _read(ROOT / "outputs/tables/company_support_experiment_mvp.csv"),
        )
        cls.indexed = {str(row["company_id"]): row for row in cls.rows}

    def test_fixed_company_grain(self) -> None:
        self.assertEqual(len(self.rows), 4)
        self.assertEqual(set(self.indexed), set(COMPANY_ORDER))

    def test_physical_capital_bridge_reconciles(self) -> None:
        for row in self.rows:
            identified = float(row["identified_route_capital_usd_2025"])
            residual = float(row["unidentified_physical_capital_base_usd_2025"])
            total = float(row["total_pathway_capital_base_usd_2025"])
            self.assertAlmostEqual(identified + residual, total, places=2)
            self.assertLessEqual(float(row["total_pathway_capital_low_usd_2025"]), total)
            self.assertLessEqual(total, float(row["total_pathway_capital_high_usd_2025"]))

    def test_current_conditions_unlock_no_capital_under_provisional_rules(self) -> None:
        for row in self.rows:
            self.assertEqual(float(row["screening_investable_capital_B0_usd_2025"]), 0)
            self.assertEqual(float(row["screening_unlocked_abatement_B0_tco2e"]), 0)

    def test_mechanism_pattern_matches_current_rules(self) -> None:
        self.assertEqual(self.indexed["POSCO"]["enabling_mechanism"], "BH")
        self.assertEqual(self.indexed["NIPPON_STEEL"]["enabling_mechanism"], "BH")
        self.assertEqual(self.indexed["LOTTE_CHEMICAL"]["enabling_mechanism"], "BHL")
        self.assertEqual(self.indexed["MITSUI_CHEMICALS"]["enabling_mechanism"], "BHL")
        for company in ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
            self.assertEqual(float(self.indexed[company]["screening_investable_capital_BH_usd_2025"]), 0)
            self.assertEqual(float(self.indexed[company]["screening_investable_capital_BL_usd_2025"]), 0)

    def test_policy_never_unlocks_more_than_identified_pathway(self) -> None:
        for row in self.rows:
            identified = float(row["identified_route_capital_usd_2025"])
            for mechanism in ("B0", "BH", "BL", "BHL"):
                self.assertLessEqual(float(row[f"screening_investable_capital_{mechanism}_usd_2025"]), identified)

    def test_risk_premium_is_not_invented(self) -> None:
        for row in self.rows:
            self.assertEqual(row["transition_risk_premium_bps"], "NA")
            self.assertIn("market_price_of_risk_not_available", row["risk_premium_pricing_status"])
            self.assertLess(float(row["premium_relevant_exposure_after_enabling_mechanism"]), 1)

    def test_output_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            outputs = generate_outputs(
                ROOT / "outputs/tables/company_emissions_pathway_mvp.csv",
                ROOT / "outputs/tables/company_support_experiment_mvp.csv",
                target / "capital_flow.csv",
                target / "figures",
                target / "report.md",
            )
            self.assertEqual(len(outputs), 4)
            self.assertEqual({path.name for path in outputs[1:3]}, set(FIGURE_NAMES))
            self.assertTrue(all(path.exists() and path.stat().st_size > 1000 for path in outputs))


if __name__ == "__main__":
    unittest.main()
