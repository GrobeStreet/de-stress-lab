"""Model-fitting primitives with deterministic multistart behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy import optimize


@dataclass(frozen=True)
class FitResult:
    """Stable, serialization-friendly view of an optimizer result.

    Parameters
    ----------
    parameters
        Best-fit parameter vector.
    objective
        Objective-function value at the retained optimum.
    success
        Whether the underlying optimizer reported success.
    message
        Optimizer status message.
    """

    parameters: np.ndarray
    objective: float
    success: bool
    message: str


@dataclass(frozen=True)
class ModelComparison:
    """Compare the best objective values of two fitted models.

    Parameters
    ----------
    null
        Fit result for the reference/null model.
    alternative
        Fit result for the alternative model.

    Notes
    -----
    ``delta_chi2`` is defined as alternative minus null objective. Therefore a
    negative value favors the alternative when the objective is chi-squared.
    """

    null: FitResult
    alternative: FitResult

    @property
    def delta_chi2(self) -> float:
        """Return alternative minus null objective value."""
        return self.alternative.objective - self.null.objective

    @property
    def improvement(self) -> float:
        """Return null minus alternative objective value."""
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
    """Minimize an objective from deterministic jittered starting points.

    Parameters
    ----------
    objective
        Callable accepting a one-dimensional NumPy parameter vector and
        returning a scalar objective value.
    start
        Base starting parameter vector.
    starts
        Number of optimization starts, including the unjittered base start.
    seed
        Seed for the NumPy random generator used to create jittered starts.
    jitter
        Fractional Gaussian jitter applied elementwise to additional starts.
    method
        Optimization method passed to :func:`scipy.optimize.minimize`.
    options
        Optional dictionary passed to :func:`scipy.optimize.minimize`.

    Returns
    -------
    FitResult
        The candidate with the smallest objective value.

    Raises
    ------
    ValueError
        If ``starts`` is less than one.

    Examples
    --------
    >>> result = multistart_minimize(lambda x: float((x[0] - 2.0) ** 2), [0.0])
    >>> round(result.parameters[0], 3)
    2.0
    """
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
