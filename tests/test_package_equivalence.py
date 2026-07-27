import sys
from pathlib import Path

import pytest

from destress.cosmology import CPLCosmology
from destress.datasets import DESI_DR2_BAO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fit_w0wa as legacy


@pytest.mark.parametrize(
    "omega_m,h,w0,wa,rd",
    [
        (0.2973, 0.68, -1.0, 0.0, 101.55 / 0.68),
        (0.352, 0.636, -0.44, -1.68, 147.0),
    ],
)
def test_packaged_bao_matches_frozen_flagship(omega_m, h, w0, wa, rd):
    cosmology = CPLCosmology(omega_m=omega_m, h=h, w0=w0, wa=wa)
    packaged = DESI_DR2_BAO.chi2(cosmology, rd)
    frozen = legacy.chi2_bao(omega_m, h, w0, wa, rd)
    assert packaged == pytest.approx(frozen, rel=2e-12, abs=2e-12)

