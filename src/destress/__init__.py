"""Reusable statistical stress tests for scientific likelihood analyses."""

from .cosmology import CPLCosmology
from .data import AnisotropicBAO, BAODataset, IsotropicBAO
from .inference import FitResult, ModelComparison, multistart_minimize
from .stress import (
    DeletionInfluence,
    deletion_influence,
    empirical_tail,
    freeze_json,
    verify_frozen_json,
)

__all__ = [
    "AnisotropicBAO",
    "BAODataset",
    "CPLCosmology",
    "DeletionInfluence",
    "FitResult",
    "IsotropicBAO",
    "ModelComparison",
    "deletion_influence",
    "empirical_tail",
    "freeze_json",
    "multistart_minimize",
    "verify_frozen_json",
]

__version__ = "0.1.0"

