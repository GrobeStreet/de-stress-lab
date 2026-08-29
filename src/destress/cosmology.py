"""Small, explicit FLRW distance models used by the stress-test examples."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import integrate

C_KMS = 299_792.458
OMEGA_GAMMA_H2 = 2.4729e-5
NEFF = 3.044
OMEGA_R_H2 = OMEGA_GAMMA_H2 * (
    1.0 + 7.0 / 8.0 * (4.0 / 11.0) ** (4.0 / 3.0) * NEFF
)


@dataclass(frozen=True)
class CPLCosmology:
    """Flat CPL ``w0-wa`` cosmology with radiation in the expansion rate.

    Parameters
    ----------
    omega_m
        Present-day matter density fraction.
    h
        Dimensionless Hubble parameter such that ``H0 = 100 h`` km/s/Mpc.
    w0
        Present-day CPL dark-energy equation-of-state parameter.
    wa
        CPL time-variation parameter.
    omega_r_h2
        Physical radiation density ``Omega_r h^2``.
    grid_max_redshift
        Maximum redshift supported by the interpolation grid.
    grid_size
        Number of points used for the comoving-distance integration grid.

    Notes
    -----
    The class intentionally supplies late-time distances only. Users may provide
    any domain-appropriate sound-horizon calculation or calibration separately.
    """

    omega_m: float
    h: float
    w0: float = -1.0
    wa: float = 0.0
    omega_r_h2: float = OMEGA_R_H2
    grid_max_redshift: float = 3.0
    grid_size: int = 3000

    def e2(self, redshift):
        """Return the dimensionless squared expansion rate ``E(z)^2``.

        Parameters
        ----------
        redshift
            Scalar or array-like redshift.

        Returns
        -------
        float or numpy.ndarray
            ``H(z)^2 / H0^2`` evaluated at the supplied redshift(s).
        """
        z = np.asarray(redshift)
        omega_r = self.omega_r_h2 / self.h**2
        omega_de = 1.0 - self.omega_m - omega_r
        dark_energy = (1.0 + z) ** (3.0 * (1.0 + self.w0 + self.wa))
        dark_energy *= np.exp(-3.0 * self.wa * z / (1.0 + z))
        return (
            omega_r * (1.0 + z) ** 4
            + self.omega_m * (1.0 + z) ** 3
            + omega_de * dark_energy
        )

    def _grid(self):
        redshift = np.linspace(0.0, self.grid_max_redshift, self.grid_size)
        distance = integrate.cumulative_trapezoid(
            1.0 / np.sqrt(self.e2(redshift)), redshift, initial=0.0
        )
        return redshift, distance

    def comoving_distance(self, redshift):
        """Return line-of-sight comoving distance in Mpc.

        Parameters
        ----------
        redshift
            Scalar or array-like redshift within the configured grid range.

        Returns
        -------
        float or numpy.ndarray
            Comoving distance in Mpc.

        Raises
        ------
        ValueError
            If any redshift lies outside ``[0, grid_max_redshift]``.
        """
        z = np.asarray(redshift)
        if np.any(z < 0.0) or np.any(z > self.grid_max_redshift):
            raise ValueError(
                f"redshift must lie in [0, {self.grid_max_redshift}] for this grid"
            )
        grid_z, grid_distance = self._grid()
        value = np.interp(z, grid_z, grid_distance) * C_KMS / (100.0 * self.h)
        return float(value) if value.ndim == 0 else value

    def transverse_distance(self, redshift):
        """Return transverse comoving distance ``D_M`` in Mpc.

        Parameters
        ----------
        redshift
            Scalar or array-like redshift.

        Returns
        -------
        float or numpy.ndarray
            Transverse comoving distance. In this flat model it equals the
            line-of-sight comoving distance.
        """
        return self.comoving_distance(redshift)

    def hubble_distance(self, redshift):
        """Return Hubble distance ``D_H = c/H(z)`` in Mpc.

        Parameters
        ----------
        redshift
            Scalar or array-like redshift.

        Returns
        -------
        float or numpy.ndarray
            Hubble distance in Mpc.
        """
        value = C_KMS / (100.0 * self.h * np.sqrt(self.e2(redshift)))
        return float(value) if np.ndim(value) == 0 else value

    def volume_distance(self, redshift):
        """Return spherically averaged BAO distance ``D_V`` in Mpc.

        Parameters
        ----------
        redshift
            Scalar or array-like redshift.

        Returns
        -------
        float or numpy.ndarray
            ``(z D_M^2 D_H)^(1/3)`` in Mpc.
        """
        z = np.asarray(redshift)
        dm = np.asarray(self.transverse_distance(z))
        dh = np.asarray(self.hubble_distance(z))
        value = (z * dm * dm * dh) ** (1.0 / 3.0)
        return float(value) if value.ndim == 0 else value
