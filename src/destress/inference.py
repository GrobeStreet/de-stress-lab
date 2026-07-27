"""Model-fitting primitives with deterministic multistart behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy import optimize


@dataclass(frozen=True)
class FitResult:
    """A stable, serialization-friendly view of an optimizer result."""

    parameters: np.ndarray
    objective: float
    success: bool
    message: str


@dataclass(frozen=True)
class ModelComparison:
    """Nested or non-nested minimum-objective comparison."""

    null: FitResult
    alternative: FitResult

    @property
    def delta_chi2(self) -> float:
        return self.alternative.objective - self.null.objective

    @property
    def improvement(self) -> float:
        return self.null.objective - self.alternative.objective


def multistart_minimize(
    objective: Callable[[np.ndarray], float],
    start: Sequence[float],
    *,
    starts: int = 3,
    seed: int = 0,
    jitter: float = 0.02,
    method: str = "Nelder-Mead",
    options: dict | None = None,
) -> FitResult:
    """Minimize from deterministic jittered starts and retain the best result."""
    if starts < 1:
        raise ValueError("starts must be positive")
    initial = np.asarray(start, dtype=float)
    rng = np.random.default_rng(seed)
    candidates = [initial]
    candidates.extend(
        initial * (1.0 + jitter * rng.standard_normal(initial.size))
        for _ in range(starts - 1)
    )
    results = [
        optimize.minimize(objective, candidate, method=method, options=options)
        for candidate in candidates
    ]
    best = min(results, key=lambda result: float(result.fun))
    return FitResult(
        parameters=np.asarray(best.x, dtype=float),
        objective=float(best.fun),
        success=bool(best.success),
        message=str(best.message),
    )

