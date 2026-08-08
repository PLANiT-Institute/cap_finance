"""CSV boundary for the CAP-KJ cost-gap model."""

from __future__ import annotations

import csv
from dataclasses import asdict, fields
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, TypeVar

from .model import CompanyResult, FacilityInput, FacilityResult, ModelInputError


TEXT_FIELDS = {
    "company_id",
    "facility_id",
    "analysis_year",
    "scenario",
    "sector",
    "route_id",
    "currency",
    "output_unit",
    "value_type",
    "quality_flag",
    "source_id",
}
INTEGER_FIELDS = {"incumbent_lifetime_years", "transition_lifetime_years"}
INPUT_FIELDS = tuple(field.name for field in fields(FacilityInput))

ResultT = TypeVar("ResultT", FacilityResult, CompanyResult)


def _parse_decimal(value: str, field_name: str, row_number: int) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ModelInputError(
            f"row {row_number}: {field_name} is not a decimal: {value!r}"
        ) from exc
    if not parsed.is_finite():
        raise ModelInputError(
            f"row {row_number}: {field_name} must be a finite decimal"
        )
    return parsed


def _parse_integer(value: str, field_name: str, row_number: int) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ModelInputError(
            f"row {row_number}: {field_name} is not an integer: {value!r}"
        ) from exc


def read_facility_inputs(path: Path) -> list[FacilityInput]:
    """Read and validate the complete, explicit facility input schema."""

    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise ModelInputError(f"cannot open input CSV {path}: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ModelInputError("input CSV has no header")
        missing = [name for name in INPUT_FIELDS if name not in reader.fieldnames]
        if missing:
            raise ModelInputError("input CSV is missing columns: " + ", ".join(missing))

        records: list[FacilityInput] = []
        for row_number, row in enumerate(reader, start=2):
            values: dict[str, Any] = {}
            for field_name in INPUT_FIELDS:
                raw_value = row[field_name]
                if raw_value is None or raw_value.strip() == "":
                    raise ModelInputError(
                        f"row {row_number}: {field_name} cannot be blank"
                    )
                value = raw_value.strip()
                if field_name in TEXT_FIELDS:
                    values[field_name] = value
                elif field_name in INTEGER_FIELDS:
                    values[field_name] = _parse_integer(
                        value, field_name, row_number
                    )
                else:
                    values[field_name] = _parse_decimal(
                        value, field_name, row_number
                    )
            try:
                records.append(FacilityInput(**values))
            except ModelInputError as exc:
                raise ModelInputError(f"row {row_number}: {exc}") from exc
    return records


def _serialise(value: Any) -> str | int:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        rendered = format(value, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return "0" if rendered in {"", "-0"} else rendered
    return value


def write_results(path: Path, results: list[ResultT], result_type: type[ResultT]) -> None:
    """Write deterministic CSV output, including an empty table header."""

    field_names = [field.name for field in fields(result_type)]
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = path.open("w", encoding="utf-8", newline="")
    except OSError as exc:
        raise ModelInputError(f"cannot open output CSV {path}: {exc}") from exc
    with handle:
        writer = csv.DictWriter(handle, fieldnames=field_names)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {name: _serialise(value) for name, value in asdict(result).items()}
            )

