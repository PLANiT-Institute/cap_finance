import csv
from dataclasses import asdict
from pathlib import Path
import tempfile
import unittest

from cap_kj.cli import main
from cap_kj.io import INPUT_FIELDS

from test_model import facility_input


class CliTests(unittest.TestCase):
    def test_schema_lists_complete_input_contract(self) -> None:
        self.assertIn("early_retirement_exposure", INPUT_FIELDS)
        self.assertIn("quality_flag", INPUT_FIELDS)
        self.assertIn("value_type", INPUT_FIELDS)

    def test_csv_input_produces_facility_and_company_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_path = root / "input.csv"
            facility_path = root / "facility.csv"
            company_path = root / "company.csv"
            row = asdict(facility_input())
            with input_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=INPUT_FIELDS)
                writer.writeheader()
                writer.writerow(row)

            status = main(
                [
                    "calculate",
                    "--input",
                    str(input_path),
                    "--facility-output",
                    str(facility_path),
                    "--company-output",
                    str(company_path),
                ]
            )

            self.assertEqual(status, 0)
            with facility_path.open(encoding="utf-8", newline="") as handle:
                (facility_row,) = csv.DictReader(handle)
            with company_path.open(encoding="utf-8", newline="") as handle:
                (company_row,) = csv.DictReader(handle)
            self.assertEqual(facility_row["resource_cost_gap_per_output"], "8")
            self.assertEqual(facility_row["early_retirement_exposure"], "999")
            self.assertEqual(company_row["transition_capex"], "2000")
            self.assertEqual(company_row["modelled_abatement_tco2e"], "150")
            self.assertEqual(company_row["quality_flag"], "engineering-range")


if __name__ == "__main__":
    unittest.main()
