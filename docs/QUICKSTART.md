# Quick start

Install the published package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install de-stress-lab==0.1.0
destress demo
```

For development from a checkout, use
`python -m pip install -e ".[test]"` and run `pytest`.

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
    full_delta=-8.5,
    deleted_delta=[-9.0, -7.9, -4.3],
    labels=["BGS", "LRG1", "LRG2"],
)
print(scan.selected_label, scan.maximum)
```

Verify the frozen prediction ledger:

```bash
destress verify-ledger predictions/2027-ledger.json
```

The full flagship rerun requires the public inputs described in
[`data/DOWNLOAD.md`](../data/DOWNLOAD.md). It intentionally remains separate
from the lightweight package example.

See the [API guide](API.md) for the stable public interfaces and assumptions.
