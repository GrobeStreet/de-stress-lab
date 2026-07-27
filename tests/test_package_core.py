import json
from pathlib import Path

import numpy as np
import pytest

from destress import (
    AnisotropicBAO,
    BAODataset,
    CPLCosmology,
    IsotropicBAO,
    deletion_influence,
    empirical_tail,
    verify_frozen_json,
)
from destress.datasets import DESI_DR2_BAO


def test_lcdm_distances_are_positive_and_ordered():
    cosmology = CPLCosmology(omega_m=0.3, h=0.7)
    distances = cosmology.comoving_distance(np.array([0.1, 0.5, 1.0]))
    assert np.all(distances > 0)
    assert np.all(np.diff(distances) > 0)
    assert cosmology.hubble_distance(1.0) > 0
    assert cosmology.volume_distance(0.5) > 0


def test_bao_chi2_is_zero_at_constructed_prediction():
    cosmology = CPLCosmology(omega_m=0.3, h=0.7)
    rd = 147.0
    z = 0.5
    dataset = BAODataset.from_measurements(
        "synthetic",
        [
            IsotropicBAO("iso", z, cosmology.volume_distance(z) / rd, 0.1),
            AnisotropicBAO(
                "aniso",
                z,
                cosmology.transverse_distance(z) / rd,
                0.2,
                cosmology.hubble_distance(z) / rd,
                0.3,
                -0.4,
            ),
        ],
    )
    assert dataset.chi2(cosmology, rd) == pytest.approx(0.0, abs=1e-20)


def test_drop_and_gaussian_sample_preserve_structure():
    reduced = DESI_DR2_BAO.drop(2)
    assert len(reduced.measurements) == 6
    assert "LRG2" not in reduced.labels
    sampled = DESI_DR2_BAO.sample(np.random.default_rng(7))
    assert sampled.labels == DESI_DR2_BAO.labels
    assert len(sampled.residuals(CPLCosmology(0.3, 0.7), 147.0)) == 13


def test_selection_influence_and_empirical_calibration():
    result = deletion_influence(
        -8.5,
        [-9.0, -7.9, -4.3, -8.3],
        ["BGS", "LRG1", "LRG2", "LRG3"],
    )
    assert result.selected_label == "LRG2"
    assert result.maximum == pytest.approx(4.2)
    tail = empirical_tail([0.2, 1.0, 2.0, 3.0], 2.0)
    assert tail == {
        "trials": 4,
        "exceedances": 2,
        "empirical_p": 0.5,
        "plus_one_p": 0.6,
    }


def test_frozen_ledger_verifies():
    root = Path(__file__).resolve().parents[1]
    digest = verify_frozen_json(root / "predictions" / "2027-ledger.json")
    assert len(digest) == 64

