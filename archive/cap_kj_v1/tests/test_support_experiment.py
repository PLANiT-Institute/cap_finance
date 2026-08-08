from pathlib import Path
import unittest

from cap_kj.support_experiment import build_support_experiment, status_after_mechanism


ROOT = Path(__file__).resolve().parents[1]


class SupportMechanismRuleTests(unittest.TestCase):
    def test_bh_unlocks_risk_dependent_statuses_only(self) -> None:
        self.assertEqual(status_after_mechanism("price-conditional", "BH"), "no-regret")
        self.assertEqual(status_after_mechanism("contract-dependent", "BH"), "no-regret")
        self.assertEqual(
            status_after_mechanism("level-support-dependent", "BH"),
            "level-support-dependent",
        )

    def test_bl_reduces_level_gap_but_leaves_price_exposure(self) -> None:
        self.assertEqual(
            status_after_mechanism("level-support-dependent", "BL"),
            "price-conditional",
        )
        self.assertEqual(
            status_after_mechanism("contract-dependent", "BL"),
            "contract-dependent",
        )

    def test_bhl_unlocks_all_modelled_conditional_statuses(self) -> None:
        for status in (
            "price-conditional",
            "contract-dependent",
            "level-support-dependent",
        ):
            self.assertEqual(status_after_mechanism(status, "BHL"), "no-regret")


class SupportExperimentAggregationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facilities, cls.companies = build_support_experiment(
            ROOT / "outputs" / "tables" / "facility_capital_allocation_mvp.csv",
            ROOT / "outputs" / "tables" / "company_capital_allocation_mvp.csv",
            ROOT / "data" / "processed" / "support_experiment_assumptions_mvp.csv",
        )

    def company(self, company_id: str, mechanism: str, assumption_case: str = "base"):
        return next(
            row
            for row in self.companies
            if row["company_id"] == company_id
            and row["mechanism_case"] == mechanism
            and row["assumption_case"] == assumption_case
        )

    def test_expected_output_grain(self) -> None:
        self.assertEqual(len(self.facilities), 25 * 3 * 4)
        self.assertEqual(len(self.companies), 4 * 3 * 4)

    def test_b0_and_bl_do_not_create_operational_abatement(self) -> None:
        for company_id in ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
            self.assertEqual(self.company(company_id, "B0")["mechanism_operational_abatement_tco2e"], 0)
            self.assertEqual(self.company(company_id, "BL")["mechanism_operational_abatement_tco2e"], 0)

    def test_bh_unlocks_steel_but_not_level_dependent_chemicals(self) -> None:
        for company_id in ("POSCO", "NIPPON_STEEL"):
            row = self.company(company_id, "BH")
            self.assertEqual(
                row["mechanism_operational_abatement_tco2e"],
                row["potential_operational_abatement_tco2e"],
            )
        for company_id in ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
            self.assertEqual(self.company(company_id, "BH")["mechanism_operational_abatement_tco2e"], 0)

    def test_bhl_unlocks_all_modelled_potential(self) -> None:
        for company_id in ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
            row = self.company(company_id, "BHL")
            self.assertEqual(
                row["mechanism_operational_abatement_tco2e"],
                row["potential_operational_abatement_tco2e"],
            )

    def test_system_abatement_is_never_claimed(self) -> None:
        self.assertEqual(
            {row["system_abatement_status"] for row in self.facilities},
            {"not_modelled; leakage and replacement production pending"},
        )

    def test_additional_abatement_requires_status_change(self) -> None:
        for row in self.facilities:
            if row["additional_operational_abatement_vs_b0_tco2e"] > 0:
                self.assertEqual(row["status_change_flag"], "yes")


if __name__ == "__main__":
    unittest.main()
