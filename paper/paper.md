---
title: 'de-stress-lab: Selection-aware stress tests and frozen prediction ledgers for scientific likelihoods'
tags:
  - Python
  - reproducibility
  - statistical diagnostics
  - likelihood
  - cosmology
authors:
  - name: Bobby Morong
    corresponding: true
    affiliation: 1
affiliations:
  - name: Independent researcher, United States
    index: 1
date: 27 July 2026
bibliography: paper.bib
---

# Summary

`de-stress-lab` is a Python package for testing how robust a scientific
likelihood result is to observation groups, model choices, and selection.
It provides explicit model and dataset interfaces, deterministic multistart
optimization, leave-group-out influence summaries, empirical null-tail
calibration, and cryptographically verifiable prediction ledgers. The package
ships with a cosmology example based on public DESI DR2 baryon acoustic
oscillation (BAO) summaries, while its statistical diagnostics operate on
general model-comparison outputs.
The versioned software archive and complete source are available with the
project release [@destress2026].

The project separates three claims that are often conflated: reproducing a
published likelihood result, locating which inputs affect it, and determining
whether a selected pattern is itself unusual under a null model. This
separation makes exploratory diagnostics useful without treating them as
additional confirmatory evidence.

# Statement of need

Research software commonly reports a global test statistic and a collection of
robustness checks. When an influential observation, subgroup, nuisance choice,
or parameterization is identified after inspecting the data, its apparent
extremeness is selected. A valid calibration must repeat that selection inside
each null realization. Otherwise the diagnostic can be mistaken for evidence
independent of the global result.

`de-stress-lab` gives researchers a small set of composable tools for this
workflow. A user can represent grouped measurements, calculate full and
deleted model comparisons, select the largest influence, and calibrate that
maximum using deterministic simulations. The same project can freeze future
predictions as JSON plus a SHA-256 digest so later adjudication cannot silently
rewrite the original forecast. The intended users are researchers, reviewers,
and computational auditors who need a transparent red-team layer around an
existing likelihood pipeline.

# State of the field

General inference frameworks such as `Cobaya` [@torrado2021] and sampling tools
such as `emcee` [@foremanmackey2013] provide broad model evaluation and
posterior computation. Scientific Python supplies the optimization and
numerical foundations [@virtanen2020]. Reproducibility systems package
environments and executions, but do not by themselves distinguish descriptive
influence from selection-calibrated evidence.

`de-stress-lab` is complementary to these tools. It does not replace a sampler,
Boltzmann solver, or domain likelihood. Its contribution is an auditable
control layer: grouped-deletion interfaces, model-comparison summaries,
empirical selected-tail calculations, frozen-ledger verification, and a
worked research-scale example. Domain-specific constants are kept outside the
generic statistical API.

# Software design

The package has four layers. `CPLCosmology` implements explicit flat
\(w_0w_a\)CDM late-time distances. Typed isotropic and anisotropic BAO blocks
retain covariance within tracers and expose residual and sampling operations.
Inference primitives return stable, serialization-friendly results from
deterministic multistart optimization. Stress-test functions consume ordinary
numbers and labels rather than cosmology objects, so other disciplines can use
them without adopting the example model.

The released scientific scripts remain frozen as the flagship provenance
record. Package-equivalence tests compare the reusable BAO implementation
against that analysis to near machine precision. Additional tests cover model
distances, covariance whitening, Gaussian simulation, group deletion,
empirical calibration, and ledger integrity. Continuous integration runs the
suite on multiple supported Python versions. Installation, examples,
contribution guidelines, support pathways, and an architectural decision
record are included in the repository.

# Research impact statement

The software grew from an independent stress test of the evolving-dark-energy
preference in public DESI DR2 compressed likelihoods [@desi2025]. That project
used the package's design pattern to reproduce headline likelihood
improvements, identify a high-influence redshift bin, and then calibrate the
maximum influence by repeating all tracer deletions inside every null
simulation. The flagship application demonstrates that a scientifically useful
localization can be real as a description while not constituting independent
evidence once selection and global signal strength are accounted for.

The repository also publishes a frozen 2027 prediction ledger. It defines
thresholds and adjudication rules for future DESI and Rubin-era observations,
providing a public example of converting interpretation into falsifiable,
time-stamped expectations.

Beyond the cosmology application, the model-agnostic functions accept any
sequence of full-data and deleted-group model-comparison statistics. This makes
the same workflow applicable to laboratory batches, clinical sites, survey
strata, instruments, or preprocessing variants. The package does not assign a
causal interpretation to an influential group. Instead, it reports influence
as a reproducible diagnostic and requires the user to simulate the complete
selection procedure before attaching an inferential tail probability.

# AI usage disclosure

OpenAI ChatGPT and OpenAI Codex (GPT-5-series systems) assisted with exploratory
implementation, refactoring, tests, documentation, and manuscript drafting.
Earlier exploratory work also used additional large-language-model assistants;
exact version metadata were not retained, which is recorded as a provenance
limitation. AI output was not accepted as scientific authority. Numerical
results were checked against independent optimizers, deterministic null
simulations, covariance checks, full-Boltzmann computations where applicable,
and package-equivalence tests. The human author reviewed the released content
and remains responsible for the software and paper.

# Acknowledgements

This project uses public data products from DESI, SDSS/eBOSS, Pantheon+,
the Dark Energy Survey, and Planck. No external financial support is declared.

# References
