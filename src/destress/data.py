"""Typed BAO measurements and Gaussian likelihood evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .cosmology import CPLCosmology


@dataclass(frozen=True)
class IsotropicBAO:
    """Represent an isotropic ``D_V/r_d`` measurement.

    Parameters
    ----------
    name
        Human-readable tracer or measurement label.
    redshift
        Effective redshift of the measurement.
    dv_over_rd
        Observed ``D_V/r_d`` value.
    sigma
        One-sigma uncertainty on ``D_V/r_d``.
    """

    name: str
    redshift: float
    dv_over_rd: float
    sigma: float

    def residual(self, cosmology: CPLCosmology, sound_horizon: float) -> np.ndarray:
        """Return the standardized model residual.

        Parameters
        ----------
        cosmology
            Cosmology used to predict ``D_V``.
        sound_horizon
            Sound horizon ``r_d`` in the same distance units as the cosmology.

        Returns
        -------
        numpy.ndarray
            Length-one standardized residual vector.
        """
        prediction = cosmology.volume_distance(self.redshift) / sound_horizon
        return np.array([(prediction - self.dv_over_rd) / self.sigma])

    @property
    def observed(self) -> np.ndarray:
        """Return the observed value as a one-element vector."""
        return np.array([self.dv_over_rd])

    @property
    def covariance(self) -> np.ndarray:
        """Return the 1x1 covariance matrix."""
        return np.array([[self.sigma**2]])


@dataclass(frozen=True)
class AnisotropicBAO:
    """Represent a correlated ``(D_M/r_d, D_H/r_d)`` measurement.

    Parameters
    ----------
    name
        Human-readable tracer or measurement label.
    redshift
        Effective redshift of the measurement.
    dm_over_rd, dh_over_rd
        Observed transverse and radial BAO distance ratios.
    sigma_dm, sigma_dh
        One-sigma uncertainties for the two ratios.
    correlation
        Correlation coefficient between the two measurements.
    """

    name: str
    redshift: float
    dm_over_rd: float
    sigma_dm: float
    dh_over_rd: float
    sigma_dh: float
    correlation: float

    @property
    def covariance(self) -> np.ndarray:
        """Return the 2x2 covariance matrix."""
        covariance = self.correlation * self.sigma_dm * self.sigma_dh
        return np.array(
            [[self.sigma_dm**2, covariance], [covariance, self.sigma_dh**2]]
        )

    @property
    def observed(self) -> np.ndarray:
        """Return ``(D_M/r_d, D_H/r_d)`` as a vector."""
        return np.array([self.dm_over_rd, self.dh_over_rd])

    def residual(self, cosmology: CPLCosmology, sound_horizon: float) -> np.ndarray:
        """Return the covariance-whitened model residual.

        Parameters
        ----------
        cosmology
            Cosmology used to predict ``D_M`` and ``D_H``.
        sound_horizon
            Sound horizon ``r_d`` in matching distance units.

        Returns
        -------
        numpy.ndarray
            Two-element whitened residual vector.
        """
        prediction = np.array(
            [
                cosmology.transverse_distance(self.redshift) / sound_horizon,
                cosmology.hubble_distance(self.redshift) / sound_horizon,
            ]
        )
        return np.linalg.solve(np.linalg.cholesky(self.covariance), prediction - self.observed)


BAOMeasurement = IsotropicBAO | AnisotropicBAO


@dataclass(frozen=True)
class BAODataset:
    """Named sequence of independent BAO tracer blocks.

    Parameters
    ----------
    name
        Dataset label.
    measurements
        Ordered tuple of isotropic and/or anisotropic BAO measurements.

    Notes
    -----
    Correlations inside an anisotropic tracer are retained. Different tracer
    blocks are assumed independent; use a custom likelihood if the supplied
    covariance includes cross-tracer correlations.
    """

    name: str
    measurements: tuple[BAOMeasurement, ...]

    @classmethod
    def from_measurements(cls, name: str, measurements: Iterable[BAOMeasurement]) -> "BAODataset":
        """Construct a dataset from an iterable of measurements.

        Parameters
        ----------
        name
            Dataset label.
        measurements
            Non-empty iterable of BAO measurements.

        Returns
        -------
        BAODataset
            Immutable dataset containing the supplied measurements.

        Raises
        ------
        ValueError
            If no measurements are supplied.
        """
        values = tuple(measurements)
        if not values:
            raise ValueError("a BAO dataset requires at least one measurement")
        return cls(name=name, measurements=values)

    @property
    def labels(self) -> tuple[str, ...]:
        """Return measurement labels in stored order."""
        return tuple(measurement.name for measurement in self.measurements)

    def drop(self, index: int) -> "BAODataset":
        """Return a copy with one tracer block removed.

        Parameters
        ----------
        index
            Zero-based measurement index to remove.

        Returns
        -------
        BAODataset
            New dataset without the selected measurement.

        Raises
        ------
        IndexError
            If ``index`` is outside the stored measurement range.
        """
        if index < 0 or index >= len(self.measurements):
            raise IndexError(index)
        return BAODataset(
            name=f"{self.name} without {self.measurements[index].name}",
            measurements=self.measurements[:index] + self.measurements[index + 1 :],
        )

    def residuals(self, cosmology: CPLCosmology, sound_horizon: float) -> np.ndarray:
        """Concatenate standardized/whitened residuals for all blocks.

        Parameters
        ----------
        cosmology
            Cosmology used for distance predictions.
        sound_horizon
            Sound horizon ``r_d``.

        Returns
        -------
        numpy.ndarray
            Concatenated residual vector.
        """
        return np.concatenate(
            [measurement.residual(cosmology, sound_horizon) for measurement in self.measurements]
        )

    def chi2(self, cosmology: CPLCosmology, sound_horizon: float) -> float:
        """Return the Gaussian chi-squared value for the dataset.

        Parameters
        ----------
        cosmology
            Cosmology used for distance predictions.
        sound_horizon
            Sound horizon ``r_d``.

        Returns
        -------
        float
            Sum of squared whitened residuals.
        """
        residuals = self.residuals(cosmology, sound_horizon)
        return float(residuals @ residuals)

    def sample(self, rng: np.random.Generator) -> "BAODataset":
        """Draw a Gaussian realization around the stored measurements.

        Parameters
        ----------
        rng
            NumPy random generator controlling the draw.

        Returns
        -------
        BAODataset
            New dataset with the same labels, redshifts, and covariance but
            newly sampled observed values.
        """
        sampled: list[BAOMeasurement] = []
        for measurement in self.measurements:
            draw = rng.multivariate_normal(measurement.observed, measurement.covariance)
            if isinstance(measurement, IsotropicBAO):
                sampled.append(IsotropicBAO(measurement.name, measurement.redshift, float(draw[0]), measurement.sigma))
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
