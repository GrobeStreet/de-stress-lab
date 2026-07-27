"""Typed BAO measurements and Gaussian likelihood evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .cosmology import CPLCosmology


@dataclass(frozen=True)
class IsotropicBAO:
    """An isotropic ``D_V/r_d`` measurement."""

    name: str
    redshift: float
    dv_over_rd: float
    sigma: float

    def residual(self, cosmology: CPLCosmology, sound_horizon: float) -> np.ndarray:
        prediction = cosmology.volume_distance(self.redshift) / sound_horizon
        return np.array([(prediction - self.dv_over_rd) / self.sigma])

    @property
    def observed(self) -> np.ndarray:
        return np.array([self.dv_over_rd])

    @property
    def covariance(self) -> np.ndarray:
        return np.array([[self.sigma**2]])


@dataclass(frozen=True)
class AnisotropicBAO:
    """A correlated ``(D_M/r_d, D_H/r_d)`` measurement."""

    name: str
    redshift: float
    dm_over_rd: float
    sigma_dm: float
    dh_over_rd: float
    sigma_dh: float
    correlation: float

    @property
    def covariance(self) -> np.ndarray:
        covariance = self.correlation * self.sigma_dm * self.sigma_dh
        return np.array(
            [
                [self.sigma_dm**2, covariance],
                [covariance, self.sigma_dh**2],
            ]
        )

    @property
    def observed(self) -> np.ndarray:
        return np.array([self.dm_over_rd, self.dh_over_rd])

    def residual(self, cosmology: CPLCosmology, sound_horizon: float) -> np.ndarray:
        prediction = np.array(
            [
                cosmology.transverse_distance(self.redshift) / sound_horizon,
                cosmology.hubble_distance(self.redshift) / sound_horizon,
            ]
        )
        return np.linalg.solve(
            np.linalg.cholesky(self.covariance), prediction - self.observed
        )


BAOMeasurement = IsotropicBAO | AnisotropicBAO


@dataclass(frozen=True)
class BAODataset:
    """A named sequence of independent BAO tracer blocks.

    Correlations inside an anisotropic tracer are retained.  The object assumes
    different tracer blocks are independent; use a custom likelihood when the
    supplied covariance contains correlations across blocks.
    """

    name: str
    measurements: tuple[BAOMeasurement, ...]

    @classmethod
    def from_measurements(
        cls, name: str, measurements: Iterable[BAOMeasurement]
    ) -> "BAODataset":
        values = tuple(measurements)
        if not values:
            raise ValueError("a BAO dataset requires at least one measurement")
        return cls(name=name, measurements=values)

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(measurement.name for measurement in self.measurements)

    def drop(self, index: int) -> "BAODataset":
        """Return a dataset with one tracer block removed."""
        if index < 0 or index >= len(self.measurements):
            raise IndexError(index)
        return BAODataset(
            name=f"{self.name} without {self.measurements[index].name}",
            measurements=self.measurements[:index] + self.measurements[index + 1 :],
        )

    def residuals(
        self, cosmology: CPLCosmology, sound_horizon: float
    ) -> np.ndarray:
        return np.concatenate(
            [
                measurement.residual(cosmology, sound_horizon)
                for measurement in self.measurements
            ]
        )

    def chi2(self, cosmology: CPLCosmology, sound_horizon: float) -> float:
        residuals = self.residuals(cosmology, sound_horizon)
        return float(residuals @ residuals)

    def sample(self, rng: np.random.Generator) -> "BAODataset":
        """Draw a Gaussian realization around the stored measurements."""
        sampled: list[BAOMeasurement] = []
        for measurement in self.measurements:
            draw = rng.multivariate_normal(measurement.observed, measurement.covariance)
            if isinstance(measurement, IsotropicBAO):
                sampled.append(
                    IsotropicBAO(
                        measurement.name,
                        measurement.redshift,
                        float(draw[0]),
                        measurement.sigma,
                    )
                )
            else:
                sampled.append(
                    AnisotropicBAO(
                        measurement.name,
                        measurement.redshift,
                        float(draw[0]),
                        measurement.sigma_dm,
                        float(draw[1]),
                        measurement.sigma_dh,
                        measurement.correlation,
                    )
                )
        return BAODataset.from_measurements(self.name, sampled)

