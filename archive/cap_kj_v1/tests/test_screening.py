from decimal import Decimal
import unittest

from cap_kj.model import ModelInputError
from cap_kj.screening import calculate_case


D = Decimal


class ScreeningCalculationTests(unittest.TestCase):
    def test_activity_driver(self) -> None:
        result = calculate_case(
            baseline_emissions=D("100"),
            activity=D("20"),
            capex_driver="activity",
            capex_intensity=D("3"),
            abatement_fraction=D("0.5"),
            modelled=True,
        )
        self.assertEqual(result.transition_emissions, D("50"))
        self.assertEqual(result.operational_abatement, D("50"))
        self.assertEqual(result.transition_capex, D("60"))

    def test_abatement_driver(self) -> None:
        result = calculate_case(
            baseline_emissions=D("100"),
            activity=None,
            capex_driver="abatement",
            capex_intensity=D("3"),
            abatement_fraction=D("0.5"),
            modelled=True,
        )
        self.assertEqual(result.transition_capex, D("150"))

    def test_unmodelled_residual_preserves_emissions(self) -> None:
        result = calculate_case(
            baseline_emissions=D("100"),
            activity=None,
            capex_driver="none",
            capex_intensity=D("0"),
            abatement_fraction=D("0"),
            modelled=False,
        )
        self.assertEqual(result.transition_emissions, D("100"))
        self.assertEqual(result.operational_abatement, D("0"))
        self.assertEqual(result.transition_capex, D("0"))

    def test_invalid_fraction_is_rejected(self) -> None:
        with self.assertRaisesRegex(ModelInputError, "abatement_fraction"):
            calculate_case(
                baseline_emissions=D("100"),
                activity=D("20"),
                capex_driver="activity",
                capex_intensity=D("3"),
                abatement_fraction=D("1.01"),
                modelled=True,
            )


if __name__ == "__main__":
    unittest.main()
