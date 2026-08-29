"""Selection-aware stress tests and immutable prediction-ledger helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np


@dataclass(frozen=True)
class DeletionInfluence:
    """Result of a leave-one-group-out model-comparison scan.

    Parameters
    ----------
    full_delta
        Model-comparison statistic for the full dataset.
    deleted_delta
        Statistic recomputed after deleting each candidate group.
    influences
        ``deleted_delta - full_delta`` for each candidate group.
    selected_index
        Index of the largest influence value.
    selected_label
        Human-readable label corresponding to ``selected_index``.
    """

    full_delta: float
    deleted_delta: tuple[float, ...]
    influences: tuple[float, ...]
    selected_index: int
    selected_label: str

    @property
    def maximum(self) -> float:
        """Return the largest selected influence value."""
        return self.influences[self.selected_index]


def deletion_influence(
    full_delta: float,
    deleted_delta: Iterable[float],
    labels: Iterable[str],
) -> DeletionInfluence:
    """Compute and select leave-one-group-out influence values.

    Parameters
    ----------
    full_delta
        Model-comparison statistic for the full dataset.
    deleted_delta
        Statistics after deleting each candidate group.
    labels
        Labels corresponding one-to-one with ``deleted_delta``.

    Returns
    -------
    DeletionInfluence
        Full deletion scan and the index/label of the largest influence.

    Raises
    ------
    ValueError
        If ``deleted_delta`` and ``labels`` differ in length or are empty.

    Notes
    -----
    ``delta`` is conventionally ``chi2_alternative - chi2_null``. A positive
    influence therefore means deletion weakens the alternative.

    Examples
    --------
    >>> result = deletion_influence(-8.0, [-7.5, -3.0], ["A", "B"])
    >>> result.selected_label
    'B'
    >>> result.maximum
    5.0
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
    """Estimate an empirical one-sided tail probability.

    Parameters
    ----------
    samples
        Null or reference statistics.
    threshold
        Observed statistic against which the tail is counted.
    side
        ``"greater"`` counts values greater than or equal to ``threshold``;
        ``"less"`` counts values less than or equal to it.

    Returns
    -------
    dict
        Trial count, exceedance count, empirical tail probability, and
        plus-one corrected probability.

    Raises
    ------
    ValueError
        If ``samples`` is empty or ``side`` is not ``"greater"``/``"less"``.

    Examples
    --------
    >>> empirical_tail([0.1, 0.5, 1.2], 1.0)["exceedances"]
    1
    """
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
    """Return the canonical UTF-8 JSON representation used by frozen ledgers.

    Parameters
    ----------
    payload
        JSON-serializable mapping.

    Returns
    -------
    bytes
        Sorted, compact UTF-8 JSON with a trailing newline.
    """
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def freeze_json(payload: Mapping, destination: str | Path) -> str:
    """Write canonical JSON and a neighboring SHA-256 checksum file.

    Parameters
    ----------
    payload
        JSON-serializable mapping to freeze.
    destination
        Output JSON path.

    Returns
    -------
    str
        SHA-256 digest of the exact bytes written.

    Examples
    --------
    >>> from pathlib import Path
    >>> path = Path("result.json")
    >>> digest = freeze_json({"value": 1}, path)
    >>> len(digest)
    64
    """
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
    """Verify a frozen JSON file against its neighboring SHA-256 record.

    Parameters
    ----------
    destination
        Path to the JSON file. A sibling ``.sha256`` file must exist.

    Returns
    -------
    str
        Verified SHA-256 digest.

    Raises
    ------
    ValueError
        If the JSON is invalid or the checksum differs from the recorded value.
    FileNotFoundError
        If either required file is missing.
    """
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
