# de-stress-lab
### Reusable scientific stress testing, reproducibility utilities, and tamper-evident result ledgers

[![Reproducibility audit](https://github.com/GrobeStreet/de-stress-lab/actions/workflows/reproducibility-audit.yml/badge.svg)](https://github.com/GrobeStreet/de-stress-lab/actions/workflows/reproducibility-audit.yml)
[![Tests](https://github.com/GrobeStreet/de-stress-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/GrobeStreet/de-stress-lab/actions/workflows/tests.yml)
[![Software DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21633731.svg)](https://doi.org/10.5281/zenodo.21633731)
[![Scientific archive DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21632602.svg)](https://doi.org/10.5281/zenodo.21632602)

`de-stress-lab` is a Python package for asking a general scientific question:

> When a quantitative result looks interesting, which observation or assumption is carrying it, and does that apparent localization remain surprising after accounting for selection?

The reusable package provides tools for:

- leave-one-group-out influence analysis;
- empirical null calibration;
- deterministic multistart optimization;
- model-comparison diagnostics;
- frozen JSON result ledgers with SHA-256 verification;
- reproducible command-line workflows for checking released artifacts.

The repository includes a DESI DR2 cosmology analysis as a **flagship application of the software**, but the package is not limited to cosmology and pyOpenSci review is sought for the reusable software, packaging, tests, documentation, and maintainability—not as validation of a dark-energy claim.

## Install

For normal use:

```bash
python -m pip install de-stress-lab
```

Quick smoke test:

```bash
destress demo
```

For development:

```bash
git clone https://github.com/GrobeStreet/de-stress-lab.git
cd de-stress-lab
python -m pip install -e ".[test]"
pytest
```

See [`docs/QUICKSTART.md`](docs/QUICKSTART.md), [`docs/API.md`](docs/API.md), and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Minimal API example

```python
from destress import deletion_influence, empirical_tail

result = deletion_influence(
    full_delta=-8.4,
    deleted_delta=[-7.9, -3.4, -8.0],
    labels=["tracer-a", "tracer-b", "tracer-c"],
)
print(result.selected_label, result.maximum)

null_maxima = [0.5, 1.0, 2.1, 0.8]
print(empirical_tail(null_maxima, result.maximum))
```

Frozen ledgers can be written and checked with:

```python
from destress import freeze_json, verify_frozen_json

freeze_json({"metric": 1.23}, "result.json")
verify_frozen_json("result.json")
```

## Why this package

Scientific analyses often report a global fit statistic but provide less reusable infrastructure for diagnosing which data block drives that fit, calibrating the selected maximum influence under a null model, and freezing the resulting evidence trail so later reruns can be compared against an immutable artifact.

`de-stress-lab` packages those steps into small composable utilities rather than a one-off notebook. It complements general scientific Python tools such as NumPy and SciPy by focusing on influence localization, empirical-tail calibration, reproducibility checks, and frozen ledgers rather than replacing general optimization, statistics, or domain-specific likelihood packages.

## Flagship application: DESI DR2

The repository independently reimplements the **published compressed likelihoods** behind the DESI DR2 evolving-dark-energy preference and applies the package's stress-testing workflow.

- In DESI DR2 BAO + compressed CMB, a direct constant-w vs CPL calibration gives **T = 7.8506**, with **30/5,000** fitted-null mocks as large: **p = 0.0060 (2.75σ)**.
- Remove **LRG2 (z = 0.706)** and the same test falls to **T = 3.4263**, **349/5,000**, **p = 0.0698 (1.81σ)**.
- The maximum leave-one-tracer influence is LRG2, but among null mocks with a global preference at least as strong as observed, **34/70** have an equal-or-larger selected maximum: **p_cond = 0.486**.

**Interpretation:** LRG2 is load-bearing for the observed fit, but its being the most influential tracer is not additional independent evidence once the global fluctuation and selection step are conditioned on.

This is a localized **2–3σ likelihood-level hint**, not a discovery claim.

### Scientific evidence ladder

| Test | Result | What it supports |
|---|---:|---|
| Compressed DESI+CMB CPL vs ΛCDM | Δχ² = −8.4575 | Reproduces the compressed-likelihood preference |
| Direct constant-w vs CPL | 30/5,000, p = **0.0060** | Within CPL, time variation is preferred over constant-w at 2.75σ |
| Direct test without LRG2 | 349/5,000, p = **0.0698** | Most direct significance is LRG2-sensitive |
| Selected maximum influence | 78/5,000, p = **0.0156** | LRG2 is unusually influential unconditionally |
| Selected influence conditional on global strength | 34/70, p = **0.486** | Localization is not extra evidence beyond the global fluctuation |
| Held-out LRG2 prediction | 204/5,000, p = **0.0408** | LRG2 is a modest held-out discrepancy |
| Full-CMB PR3-native variant | 2.77σ → **1.43σ** without LRG2 | Lensing information does not remove the LRG2 sensitivity in this comparison stack |

The full-CMB check uses a **Planck PR3-native comparison stack**, not DESI's exact PR4/ACT likelihood generation. It is a qualitative robustness leg, not an exact reproduction of the published PR4 full-CMB headline.

## Scope — what the DESI application is and is not

**It is:**

- an independent implementation of published compressed likelihoods;
- a selection-aware influence audit;
- a fitted-null Monte Carlo calibration;
- a direct constant-w vs CPL test;
- a held-out LRG2 diagnostic;
- a worked example of the reusable Python package.

**It is not:**

- a raw DESI data reanalysis;
- a reconstruction of the native survey likelihood;
- an exact reproduction of DESI's PR4/ACT full-CMB pipeline;
- proof of evolving dark energy;
- independent human scientific verification yet.

## Proof / receipts

- **Installable software:** [PyPI `de-stress-lab`](https://pypi.org/project/de-stress-lab/)
- **Reusable software archive:** [DOI 10.5281/zenodo.21633731](https://doi.org/10.5281/zenodo.21633731)
- **Frozen scientific reproduction archive:** [DOI 10.5281/zenodo.21632602](https://doi.org/10.5281/zenodo.21632602)
- **Machine-readable result ledger:** [`RESULTS_MANIFEST.json`](RESULTS_MANIFEST.json)
- **Independent-reproduction venue:** [ReproHack Paper #108](https://www.reprohack.org/paper/108/)
- **Human verifier entry point:** [`VERIFY.md`](VERIFY.md) · [Issue #21](https://github.com/GrobeStreet/de-stress-lab/issues/21)
- **Prepared arXiv package:** [`submission/arxiv/`](submission/arxiv/)
- **Frozen prediction ledger:** [`predictions/2027-ledger.md`](predictions/2027-ledger.md)
- **Green automation:** [tests](https://github.com/GrobeStreet/de-stress-lab/actions/workflows/tests.yml) · [reproducibility audit](https://github.com/GrobeStreet/de-stress-lab/actions/workflows/reproducibility-audit.yml)

**Verification status:** analysis, tests, manifests, archived artifacts, clean-room protocol, and arXiv source package are complete. **Independent human clean-room execution remains pending and is actively being sought.**

> **Independent verifier wanted.** You do not need to endorse the cosmology. A clean clone/install/test run is useful evidence; the blinded 5,000-mock rerun is optional. Start at [`VERIFY.md`](VERIFY.md). Failures and deviations are welcome.

## Reproduce the repository software path

```bash
python -m pip install -e ".[test]"
destress demo
pytest
destress verify-ledger predictions/2027-ledger.json
```

See the [quick start](docs/QUICKSTART.md) and [GitHub Action guide](docs/GITHUB_ACTION.md).

## Documentation and project policy

- [`docs/API.md`](docs/API.md) — public API guide
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) — first-use walkthrough
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — development and contribution workflow
- [`GOVERNANCE.md`](GOVERNANCE.md) — maintenance, releases, continuity, and credit
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) — community expectations
- [`AI_USE.md`](AI_USE.md) — generative-AI use and human-review disclosure
- [`ERRATA.md`](ERRATA.md) — historical corrections and clarifications

## Generative AI disclosure

Generative AI tools assisted portions of implementation, testing, auditing, and documentation. Those outputs were subject to maintainer review and automated or numerical checks as appropriate. AI-assisted checks are **not** substitutes for unrelated human scientific verification. See [`AI_USE.md`](AI_USE.md) for the explicit disclosure.

## Why two DOIs?

Use **[10.5281/zenodo.21633731](https://doi.org/10.5281/zenodo.21633731)** when citing the reusable software package, CLI, API, or ledger tooling.

Use **[10.5281/zenodo.21632602](https://doi.org/10.5281/zenodo.21632602)** when citing the immutable v1.0 scientific reproduction and its archived artifacts.

## Repository map

```text
src/             reusable `destress` Python package
scripts/         scientific reproduction and stress-test analyses
results/         versioned numerical outputs
cleanroom/       blinded second-person reproduction protocol
submission/arxiv prepared, validated arXiv source and metadata
predictions/     frozen prediction ledger and hashes
paper/           software-paper / scholarly-readiness materials
docs/            quick start, API, build, and architecture documentation
tests/           numerical equivalence, metadata, and determinism checks
```

## Working rule

**Reproduce → localize → calibrate selection → test the kill condition → publish the result even when it weakens the story.**

Canonical numbers, completion states, and artifact hashes live in [`RESULTS_MANIFEST.json`](RESULTS_MANIFEST.json). Historical corrections and clarifications live in [`ERRATA.md`](ERRATA.md).

— Robert “Bobby” Morong, independent researcher
