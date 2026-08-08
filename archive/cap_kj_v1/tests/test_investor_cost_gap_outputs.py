from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cap_kj.investor_cost_gap_outputs import (
    COMPANY_ORDER,
    generate_outputs,
    load_base_mechanisms,
    load_cost_gap_cases,
)


ROOT = Path(__file__).resolve().parents[1]
COST = ROOT / "outputs" / "tables" / "company_annual_cost_gap_mvp.csv"
SUPPORT = ROOT / "outputs" / "tables" / "company_support_experiment_mvp.csv"


class InvestorCostGapOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_cost_gap_cases(COST)
        cls.mechanisms = load_base_mechanisms(SUPPORT)

    def test_cost_gap_grain_and_mitsui_sensitivity(self) -> None:
        self.assertEqual(len(self.cases), 15)
        primary = [row for row in self.cases if row.variant_role == "primary"]
        self.assertEqual(len(primary), 12)
        self.assertEqual({row.company_id for row in primary}, set(COMPANY_ORDER))
        self.assertEqual(
            len([row for row in self.cases if row.variant_role == "sensitivity"]),
            3,
        )

    def test_verified_net_gap_is_not_plotted_as_zero(self) -> None:
        self.assertEqual({row.verified_gap for row in self.cases}, {"NA"})

    def test_base_mechanism_grain(self) -> None:
        self.assertEqual(len(self.mechanisms), 16)
        self.assertEqual(
            {(row.company_id, row.mechanism) for row in self.mechanisms},
            {
                (company_id, mechanism)
                for company_id in COMPANY_ORDER
                for mechanism in ("B0", "BH", "BL", "BHL")
            },
        )

    def test_steel_bh_and_chemical_bhl_rule_pattern(self) -> None:
        rows = {(row.company_id, row.mechanism): row for row in self.mechanisms}
        for company_id in ("POSCO", "NIPPON_STEEL"):
            self.assertGreater(rows[(company_id, "BH")].operational_abatement_tco2e, 0)
        for company_id in ("LOTTE_CHEMICAL", "MITSUI_CHEMICALS"):
            self.assertEqual(rows[(company_id, "BH")].operational_abatement_tco2e, 0)
            self.assertGreater(rows[(company_id, "BHL")].operational_abatement_tco2e, 0)

    def test_output_generation_writes_two_pngs_and_audited_memo(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = generate_outputs(COST, SUPPORT, root / "figures", root / "memo.md")
            self.assertEqual(len(paths), 3)
            for path in paths[:2]:
                self.assertTrue(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertGreater(path.stat().st_size, 20_000)
            memo = paths[2].read_text(encoding="utf-8")
            self.assertIn("incentive-adjusted gap remains `NA`", memo)
            self.assertIn("Mitsui", memo)


if __name__ == "__main__":
    unittest.main()
