"""Reusable statistical stress tests for scientific likelihood analyses."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

_EXPORT_MODULES = {
    "CPLCosmology": ".cosmology",
    "AnisotropicBAO": ".data",
    "BAODataset": ".data",
    "IsotropicBAO": ".data",
    "FitResult": ".inference",
    "ModelComparison": ".inference",
    "multistart_minimize": ".inference",
    "DeletionInfluence": ".stress",
    "deletion_influence": ".stress",
    "empirical_tail": ".stress",
    "freeze_json": ".stress",
    "verify_frozen_json": ".stress",
}


def __getattr__(name: str):
    """Load scientific dependencies only when their public objects are used."""
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name, __name__), name)
    globals()[name] = value
    return value
