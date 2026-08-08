import csv
from decimal import Decimal
from pathlib import Path
import unittest

from cap_kj.physical_constraints import build_outputs


ROOT = Path(__file__).resolve().parents[1]
D = Decimal


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ProductionCoverageConstraintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facts = read(
            ROOT / "data" / "processed" / "official_production_constraint_facts_mvp.csv"
        )
        cls.production, cls.constraints = build_outputs(
            read(ROOT / "data" / "processed" / "facility_seed.csv"),
            read(ROOT / "data" / "processed" / "facility_route_mapping_mvp.csv"),
            cls.facts,
        )

    def test_official_facts_are_reported_and_registered(self) -> None:
        self.assertEqual(len(self.facts), 6)
        self.assertEqual({row["value_type"] for row in self.facts}, {"Reported"})
        registered = {
            row["source_id"]
            for row in read(ROOT / "data" / "manifests" / "source_register.csv")
        }
        referenced = {
            source_id
            for row in self.facts
            for source_id in row["source_id"].split("|")
        }
        self.assertFalse(referenced - registered)

    def test_nippon_production_reconciles_with_visible_excess(self) -> None:
        row = next(row for row in self.production if row["company_id"] == "NIPPON_STEEL")
        self.assertEqual(row["facility_activity_sum"], D("34880000"))
        self.assertEqual(row["company_reported_production"], D("34300000"))
        self.assertEqual(row["absolute_difference"], D("580000"))
        self.assertLessEqual(abs(row["raw_reconciliation_ratio"] - D("1")), D("0.02"))
        self.assertEqual(row["production_coverage_ratio"], D("1"))

    def test_unknown_company_production_coverage_remains_na(self) -> None:
        unknown = [row for row in self.production if row["company_id"] != "NIPPON_STEEL"]
        self.assertEqual({row["production_coverage_ratio"] for row in unknown}, {"NA"})

    def test_gwangyang_official_capacity_is_only_partial(self) -> None:
        (row,) = self.constraints
        self.assertEqual(row["official_route_capacity_t_per_year"], D("2500000"))
        self.assertGreater(row["project_capacity_coverage_base"], D("0.13"))
        self.assertLess(row["project_capacity_coverage_base"], D("0.14"))
        self.assertGreater(row["full_route_scale_multiple_base"], D("7.6"))
        self.assertIn("physically_constrained", row["constraint_status"])

    def test_scrap_scale_is_explicit(self) -> None:
        (row,) = self.constraints
        self.assertEqual(row["implied_project_scrap_demand_t_per_year"], D("2000000"))
        self.assertGreater(row["share_of_2024_purchased_scrap_usage"], D("0.97"))
        self.assertLess(row["share_of_2024_purchased_scrap_usage"], D("0.98"))

    def test_official_project_is_not_silently_scaled_to_full_works(self) -> None:
        (row,) = self.constraints
        self.assertEqual(row["value_type"], "Derived_from_reported_and_allocated")
        self.assertEqual(row["quality_flag"], "D")
        self.assertIn("not reported Gwangyang", row["boundary_note"])


if __name__ == "__main__":
    unittest.main()
