import copy
import csv
from decimal import Decimal
from pathlib import Path
import unittest

from cap_kj.cost_gap_inputs import build_route_summary, validate_assumptions
from cap_kj.model import ModelInputError, capital_recovery_factor


ROOT = Path(__file__).resolve().parents[1]
ASSUMPTIONS = ROOT / "data" / "processed" / "annual_cost_gap_assumptions_mvp.csv"


def assumption_rows() -> list[dict[str, str]]:
    with ASSUMPTIONS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class AnnualCostGapInputTests(unittest.TestCase):
    def test_expected_routes_and_output_grain(self) -> None:
        summary = build_route_summary(assumption_rows())
        self.assertEqual(len(summary), 4 * 3)
        self.assertEqual(
            {row["route_id"] for row in summary},
            {
                "steel_h2_dri_eaf",
                "steel_scrap_eaf",
                "steel_eaf_efficiency",
                "petchem_electrified_cracker",
            },
        )

    def test_base_annualisation_factor_uses_crf_plus_fixed_opex(self) -> None:
        summary = build_route_summary(assumption_rows())
        row = next(
            item
            for item in summary
            if item["route_id"] == "steel_h2_dri_eaf" and item["case"] == "base"
        )
        expected = capital_recovery_factor(Decimal("0.05"), 25) + Decimal("0.025")
        self.assertEqual(row["annual_capital_and_fixed_opex_factor"], expected)

    def test_verified_market_policy_is_not_zero_filled(self) -> None:
        rows = assumption_rows()
        verified = [row for row in rows if row["parameter_group"] == "verified_market_policy"]
        self.assertEqual(len(verified), 4 * 3)
        self.assertTrue(all(row["value_type"] == "Not_available" for row in verified))
        self.assertTrue(all([row[case] for case in ("low", "base", "high")] == ["NA"] * 3 for row in verified))
        self.assertEqual(
            {row["verified_market_policy_status"] for row in build_route_summary(rows)},
            {"not_available_not_zero"},
        )

    def test_support_stress_is_an_independent_axis(self) -> None:
        summary = build_route_summary(assumption_rows())
        self.assertEqual(
            {row["support_stress_case_orientation"] for row in summary},
            {"independent_not_paired_with_resource_case"},
        )

    def test_missing_estimate_range_is_rejected(self) -> None:
        rows = copy.deepcopy(assumption_rows())
        rows[0]["low"] = "NA"
        with self.assertRaisesRegex(ModelInputError, "lacks low/base/high"):
            validate_assumptions(rows)

    def test_zero_filled_unavailable_policy_value_is_rejected(self) -> None:
        rows = copy.deepcopy(assumption_rows())
        target = next(row for row in rows if row["parameter_group"] == "verified_market_policy")
        target["base"] = "0"
        with self.assertRaisesRegex(ModelInputError, "must remain NA"):
            validate_assumptions(rows)


if __name__ == "__main__":
    unittest.main()
