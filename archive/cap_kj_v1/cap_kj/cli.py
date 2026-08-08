"""Command-line interface for CSV-to-CSV CAP-KJ calculations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .io import INPUT_FIELDS, read_facility_inputs, write_results
from .model import (
    CompanyResult,
    FacilityResult,
    ModelInputError,
    aggregate_company_results,
    calculate_facility,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cap-kj",
        description="Calculate facility cost gaps and company capital-allocation metrics.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    calculate = subparsers.add_parser(
        "calculate", help="transform facility input CSV into facility and company CSVs"
    )
    calculate.add_argument("--input", type=Path, required=True)
    calculate.add_argument("--facility-output", type=Path, required=True)
    calculate.add_argument("--company-output", type=Path, required=True)
    subparsers.add_parser("schema", help="print required input CSV columns")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "schema":
        print(",".join(INPUT_FIELDS))
        return 0

    try:
        inputs = read_facility_inputs(args.input)
        facility_results = [calculate_facility(record) for record in inputs]
        company_results = aggregate_company_results(facility_results)
        write_results(args.facility_output, facility_results, FacilityResult)
        write_results(args.company_output, company_results, CompanyResult)
    except ModelInputError as exc:
        print(f"cap-kj: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

