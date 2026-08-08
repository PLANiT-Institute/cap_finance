"""CAP-KJ facility cost-gap and company aggregation model."""

from .model import (
    CompanyResult,
    FacilityInput,
    FacilityResult,
    ModelInputError,
    aggregate_company_results,
    calculate_facility,
    capital_recovery_factor,
)

__all__ = [
    "CompanyResult",
    "FacilityInput",
    "FacilityResult",
    "ModelInputError",
    "aggregate_company_results",
    "calculate_facility",
    "capital_recovery_factor",
]

