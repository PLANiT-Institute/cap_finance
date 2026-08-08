import csv
from decimal import Decimal
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
D = Decimal


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class MitsuiRegistryUpgradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = read(
            ROOT / "data" / "processed" / "mci_shk_facility_emissions_2023.csv"
        )
        cls.bridge = read(
            ROOT / "data" / "processed" / "mci_shk_to_fy2024_bridge.csv"
        )

    def test_reported_registry_records_are_preserved(self) -> None:
        self.assertEqual(len(self.registry), 12)
        self.assertEqual(len({row["registry_record_id"] for row in self.registry}), 12)
        self.assertEqual(
            sum((D(row["reported_ghg_tco2"]) for row in self.registry), D("0")),
            D("3560757"),
        )
        self.assertEqual({row["value_type"] for row in self.registry}, {"Reported"})

    def test_bridge_reconciles_registry_company_total(self) -> None:
        self.assertEqual(len(self.bridge), 9)
        self.assertEqual(
            sum((D(row["observed_2023_tco2e"]) for row in self.bridge), D("0")),
            D("3571026"),
        )
        self.assertEqual(
            sum((D(row["registry_share"]) for row in self.bridge), D("0")),
            D("1.000000000001"),
        )

    def test_allocated_base_reconciles_fy2024_parent_anchor(self) -> None:
        self.assertEqual(
            sum((D(row["allocated_base_tco2e"]) for row in self.bridge), D("0")),
            D("3869000"),
        )
        for row in self.bridge:
            self.assertLessEqual(D(row["allocated_low_tco2e"]), D(row["allocated_base_tco2e"]))
            self.assertLessEqual(D(row["allocated_base_tco2e"]), D(row["allocated_high_tco2e"]))
            self.assertEqual(row["allocated_value_type"], "Allocated")
            self.assertEqual(row["price_year"], "not_applicable")
            self.assertEqual(row["quality_flag"], "C")

    def test_every_registry_record_is_used_once(self) -> None:
        used = [
            record_id
            for row in self.bridge
            if row["registry_record_ids"] != "NA"
            for record_id in row["registry_record_ids"].split("|")
        ]
        self.assertEqual(len(used), 12)
        self.assertEqual(set(used), {row["registry_record_id"] for row in self.registry})

    def test_all_external_sources_are_registered(self) -> None:
        source_register = read(
            ROOT / "data" / "manifests" / "source_register.csv"
        )
        registered = {row["source_id"] for row in source_register}
        referenced = {
            source_id
            for row in (*self.registry, *self.bridge)
            for source_id in row["source_id"].split("|")
        }
        self.assertFalse(referenced - registered)

    def test_modelled_site_coverage_signal_improves(self) -> None:
        modelled = {"JP_MCI_OSAKA", "JP_MCI_ICHIHARA", "JP_MCI_OMUTA", "JP_MCI_IWAKUNI"}
        allocated = sum(
            (D(row["allocated_base_tco2e"]) for row in self.bridge if row["seed_facility_id"] in modelled),
            D("0"),
        )
        self.assertGreater(allocated / D("3869000"), D("0.97"))


if __name__ == "__main__":
    unittest.main()
