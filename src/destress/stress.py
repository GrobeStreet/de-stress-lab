"""Selection-aware stress tests and immutable prediction-ledger helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping

import numpy as np


@dataclass(frozen=True)
class DeletionInfluence:
    """Result of a leave-one-group-out model-comparison scan."""

    full_delta: float
    deleted_delta: tuple[float, ...]
    influences: tuple[float, ...]
    selected_index: int
    selected_label: str

    @property
    def maximum(self) -> float:
        return self.influences[self.selected_index]


def deletion_influence(
    full_delta: float,
    deleted_delta: Iterable[float],
    labels: Iterable[str],
) -> DeletionInfluence:
    """Select the largest loss of alternative-model preference after deletion.

    ``delta`` is conventionally ``chi2_alternative - chi2_null``.  Therefore
    a positive influence means that deleting the group weakens the alternative.
    """
    deleted = tuple(float(value) for value in deleted_delta)
    names = tuple(labels)
    if len(deleted) != len(names) or not deleted:
        raise ValueError("deleted_delta and labels must have the same nonzero length")
    influences = tuple(value - float(full_delta) for value in deleted)
    selected = int(np.argmax(influences))
    return DeletionInfluence(
        full_delta=float(full_delta),
        deleted_delta=deleted,
        influences=influences,
        selected_index=selected,
        selected_label=names[selected],
    )


def empirical_tail(
    samples: Iterable[float],
    threshold: float,
    *,
    side: str = "greater",
) -> dict[str, float | int]:
    """Return empirical and plus-one tail probabilities."""
    values = np.asarray(tuple(samples), dtype=float)
    if values.size == 0:
        raise ValueError("samples cannot be empty")
    if side == "greater":
        exceedances = int(np.count_nonzero(values >= threshold))
    elif side == "less":
        exceedances = int(np.count_nonzero(values <= threshold))
    else:
        raise ValueError("side must be 'greater' or 'less'")
    return {
        "trials": int(values.size),
        "exceedances": exceedances,
        "empirical_p": exceedances / int(values.size),
        "plus_one_p": (exceedances + 1) / (int(values.size) + 1),
    }


def canonical_json_bytes(payload: Mapping) -> bytes:
    """Canonical UTF-8 JSON representation used by frozen ledgers."""
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def freeze_json(payload: Mapping, destination: str | Path) -> str:
    """Write canonical JSON and a neighboring SHA-256 checksum file."""
    path = Path(destination)
    encoded = canonical_json_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{digest}  {path.name}\n", encoding="utf-8"
    )
    return digest


def verify_frozen_json(destination: str | Path) -> str:
    """Verify valid JSON and its neighboring SHA-256 checksum."""
    path = Path(destination)
    encoded = path.read_bytes()
    json.loads(encoded.decode("utf-8"))
    expected = path.with_suffix(path.suffix + ".sha256").read_text(
        encoding="utf-8"
    ).split()[0]
    actual = hashlib.sha256(encoded).hexdigest()
    if actual != expected:
        raise ValueError(f"checksum mismatch: expected {expected}, got {actual}")
    return actual
