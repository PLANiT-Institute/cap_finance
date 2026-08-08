from pathlib import Path
import unittest

from cap_kj.investor_outputs import COMPANY_ORDER, indexed_cases, load_company_cases


ROOT = Path(__file__).resolve().parents[1]


class InvestorOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_company_cases(
            ROOT / "outputs" / "tables" / "company_capital_allocation_mvp.csv"
        )
        cls.rows = indexed_cases(cls.cases)

    def test_all_four_companies_have_three_cases(self) -> None:
        self.assertEqual(len(self.cases), 12)
        self.assertEqual({row.company_id for row in self.cases}, set(COMPANY_ORDER))

    def test_base_capex_timing_reconciles(self) -> None:
        for company in COMPANY_ORDER:
            row = self.rows[(company, "base")]
            self.assertAlmostEqual(
                row.capex_usd,
                row.capex_2030_usd + row.capex_2040_usd + row.capex_2050_usd,
                places=2,
            )

    def test_screening_quality_is_disclosed(self) -> None:
        self.assertEqual({row.quality_flag for row in self.cases}, {"D"})


if __name__ == "__main__":
    unittest.main()
