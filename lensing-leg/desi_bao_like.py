"""DESI DR2 BAO likelihood for cobaya (values machine-extracted from arXiv:2503.14738,
identical to the main lab pipeline). yaml-settable option: drop_lrg2 (bool).
"""
import numpy as np
from cobaya.likelihood import Likelihood

C_KMS = 299792.458

BAO_DV = [(0.295, 7.942, 0.075)]
BAO_MH = [
    (0.510, 13.588, 0.167, 21.863, 0.425, -0.459),
    (0.706, 17.351, 0.177, 19.455, 0.330, -0.404),   # LRG2 — index 1
    (0.934, 21.576, 0.152, 17.641, 0.193, -0.416),
    (1.321, 27.601, 0.318, 14.176, 0.221, -0.434),
    (1.484, 30.512, 0.760, 12.817, 0.516, -0.500),
    (2.330, 38.988, 0.531,  8.632, 0.101, -0.431),
]
ZS = np.array(sorted({p[0] for p in BAO_DV} | {p[0] for p in BAO_MH}))


class DESIDR2BAO(Likelihood):
    drop_lrg2: bool = False

    def initialize(self):
        self.zidx = {z: i for i, z in enumerate(ZS)}

    def get_requirements(self):
        return {"angular_diameter_distance": {"z": ZS},
                "Hubble": {"z": ZS, "units": "km/s/Mpc"},
                "rdrag": None}

    def logp(self, **params_values):
        rd = self.provider.get_param("rdrag")
        DA = self.provider.get_angular_diameter_distance(ZS)
        Hz = self.provider.get_Hubble(ZS, units="km/s/Mpc")
        DM = DA * (1 + ZS)          # comoving transverse distance
        DH = C_KMS / Hz
        c2 = 0.0
        for z, dv, s in BAO_DV:
            i = self.zidx[z]
            c2 += (((z * DM[i] ** 2 * DH[i]) ** (1 / 3.0) / rd - dv) / s) ** 2
        for j, (z, dmv, sm, dhv, sh, r) in enumerate(BAO_MH):
            if self.drop_lrg2 and j == 1:
                continue
            i = self.zidx[z]
            a = DM[i] / rd - dmv
            b = DH[i] / rd - dhv
            det = (sm * sh) ** 2 * (1 - r * r)
            c2 += (a * a * sh * sh - 2 * r * a * b * sm * sh + b * b * sm * sm) / det
        return -0.5 * c2
