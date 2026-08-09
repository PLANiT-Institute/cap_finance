from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


def quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def sample_variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def cholesky(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    size = len(matrix)
    lower = [[0.0] * size for _ in range(size)]
    for row in range(size):
        for column in range(row + 1):
            residual = float(matrix[row][column]) - sum(
                lower[row][k] * lower[column][k] for k in range(column)
            )
            if row == column:
                if residual <= 0.0:
                    raise ValueError("correlation matrix must be positive definite")
                lower[row][column] = math.sqrt(residual)
            else:
                lower[row][column] = residual / lower[column][column]
    return lower


def matrix_vector_product(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    return [sum(value * vector[index] for index, value in enumerate(row)) for row in matrix]


def pareto_frontier(rows: Iterable[dict[str, float | str]]) -> list[dict[str, float | str]]:
    candidates = list(rows)
    frontier: list[dict[str, float | str]] = []
    for candidate in candidates:
        cost = float(candidate["p50"])
        risk = float(candidate["tcar"])
        dominated = any(
            float(other["p50"]) <= cost
            and float(other["tcar"]) <= risk
            and (
                float(other["p50"]) < cost
                or float(other["tcar"]) < risk
            )
            for other in candidates
            if other is not candidate
        )
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier, key=lambda row: float(row["p50"]))

