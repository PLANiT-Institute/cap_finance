import csv
from decimal import Decimal
from pathlib import Path
import unittest

from cap_kj.cost_gap import build_cost_gap_tables


ROOT = Path(__file__).resolve().parents[1]
D = Decimal


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class CostGapAggregationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facilities, cls.companies = build_cost_gap_tables(
            read(ROOT / "outputs" / "tables" / "facility_capital_allocation_mvp.csv"),
            read(ROOT / "outputs" / "tables" / "company_capital_allocation_mvp.csv"),
            read(ROOT / "outputs" / "tables" / "route_annual_cost_gap_inputs_mvp.csv"),
            read(ROOT / "data" / "processed" / "mci_shk_to_fy2024_bridge.csv"),
        )

    def company(self, company_id: str, case: str = "base", variant_role: str = "primary"):
        return next(
            row
            for row in self.companies
            if row["company_id"] == company_id
            and row["case"] == case
            and row["variant_role"] == variant_role
        )

    def test_output_grain_includes_primary_and_mitsui_legacy_sensitivity(self) -> None:
        self.assertEqual(len(self.facilities), 75 + 4 * 3)
        self.assertEqual(len(self.companies), 4 * 3 + 3)
        self.assertEqual(
            {row["baseline_variant"] for row in self.companies if row["company_id"] == "MITSUI_CHEMICALS"},
            {"primary_mci_shk_bridge", "legacy_mci_judgement_sensitivity"},
        )

    def test_facility_resource_gap_formula(self) -> None:
        row = next(
            row
            for row in self.facilities
            if row["facility_id"] == "KR_POSCO_POHANG"
            and row["case"] == "base"
        )
        expected = (
            row["transition_capex_usd_2025"] * row["annual_capital_and_fixed_opex_factor"]
            + row["modelled_operational_abatement_tco2e"]
            * row["incremental_variable_resource_cost_usd_2025_per_operational_tco2e_abated"]
        )
        self.assertEqual(row["annual_resource_gap_proxy_usd_2025"], expected)

    def test_company_resource_gap_reconciles_to_facilities(self) -> None:
        for company in self.companies:
            facilities = [
                row
                for row in self.facilities
                if row["company_id"] == company["company_id"]
                and row["baseline_variant"] == company["baseline_variant"]
                and row["case"] == company["case"]
                and row["modelled_flag"] == "yes"
            ]
            self.assertEqual(
                company["annual_resource_gap_proxy_usd_2025"],
                sum((row["annual_resource_gap_proxy_usd_2025"] for row in facilities), D("0")),
            )

    def test_mitsui_registry_bridge_improves_primary_coverage(self) -> None:
        primary = self.company("MITSUI_CHEMICALS")
        legacy = self.company("MITSUI_CHEMICALS", variant_role="sensitivity")
        self.assertGreater(primary["base_case_emissions_coverage_ratio"], D("0.97"))
        self.assertEqual(legacy["base_case_emissions_coverage_ratio"], D("0.85"))
        self.assertGreater(primary["annual_resource_gap_proxy_usd_2025"], legacy["annual_resource_gap_proxy_usd_2025"])

    def test_coverage_is_a_base_boundary_not_a_cost_case_range(self) -> None:
        for company_id in ("POSCO", "NIPPON_STEEL", "LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
            values = {
                row["base_case_emissions_coverage_ratio"]
                for row in self.companies
                if row["company_id"] == company_id and row["variant_role"] == "primary"
            }
            self.assertEqual(len(values), 1)
            self.assertLessEqual(next(iter(values)), D("1"))

    def test_verified_net_gap_is_never_zero_filled(self) -> None:
        self.assertEqual(
            {row["verified_incentive_adjusted_gap_usd_2025"] for row in self.companies},
            {"NA"},
        )
        self.assertEqual(
            {row["verified_market_policy_status"] for row in self.companies},
            {"not_available_not_zero"},
        )

    def test_support_stress_reduces_gap_without_becoming_verified(self) -> None:
        for row in self.companies:
            self.assertLessEqual(row["stress_adjusted_gap_high_usd_2025"], row["stress_adjusted_gap_base_usd_2025"])
            self.assertLessEqual(row["stress_adjusted_gap_base_usd_2025"], row["stress_adjusted_gap_low_usd_2025"])

    def test_unmodelled_facilities_remain_na_not_zero(self) -> None:
        unmodelled = [row for row in self.facilities if row["modelled_flag"] != "yes"]
        self.assertTrue(unmodelled)
        self.assertEqual({row["annual_resource_gap_proxy_usd_2025"] for row in unmodelled}, {"NA"})


if __name__ == "__main__":
    unittest.main()
