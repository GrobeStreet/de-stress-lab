# Quick start

Install the package from a checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
destress demo
pytest
```

The API separates a scientific model from a dataset:

```python
from destress import CPLCosmology
from destress.datasets import DESI_DR2_BAO

cosmology = CPLCosmology(omega_m=0.30, h=0.70)
chi2 = DESI_DR2_BAO.chi2(cosmology, sound_horizon=147.0)
```

Selection-aware deletion influence is independent of cosmology:

```python
from destress import deletion_influence

scan = deletion_influence(
    full_delta=-12.4,
    deleted_delta=[-11.8, -8.1, -12.0],
    labels=["batch-A", "batch-B", "batch-C"],
)
print(scan.selected_label, scan.maximum)
```

This domain-neutral example asks which laboratory batch most weakens an
alternative model when deleted. If the batch is chosen because it maximizes
the observed influence, each null simulation must repeat the complete deletion
scan before an empirical tail probability is interpreted.

Verify the frozen prediction ledger:

```bash
destress verify-ledger predictions/2027-ledger.json
```

The full flagship rerun requires the public inputs described in
[`data/DOWNLOAD.md`](../data/DOWNLOAD.md). It intentionally remains separate
from the lightweight package example.

See the [API guide](API.md) for the stable public interfaces and assumptions.
