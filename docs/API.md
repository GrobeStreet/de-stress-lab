# API guide

## Scientific model

`destress.CPLCosmology` evaluates flat CPL late-time expansion and the
distances `comoving_distance`, `transverse_distance`, `hubble_distance`, and
`volume_distance`. Radiation is included. The grid extent and resolution are
explicit constructor parameters.

The class deliberately does not calculate a sound horizon. Pass the
domain-appropriate sound horizon into a dataset likelihood.

## Grouped BAO data

`IsotropicBAO` represents one Gaussian `D_V/r_d` measurement.
`AnisotropicBAO` represents a correlated `(D_M/r_d, D_H/r_d)` pair.
`BAODataset` combines independent tracer blocks and supports:

- `residuals(cosmology, sound_horizon)`
- `chi2(cosmology, sound_horizon)`
- `drop(index)`
- `sample(rng)`

For cross-tracer covariance, implement a custom likelihood rather than
pretending the blocks are independent.

## Inference

`multistart_minimize` wraps deterministic, jittered optimization and returns a
stable `FitResult`. `ModelComparison` exposes the objective difference and
improvement. Domain priors and invalid regions belong in the supplied objective.

## Statistical stress tests

`deletion_influence(full_delta, deleted_delta, labels)` calculates

```text
influence[j] = deleted_delta[j] - full_delta
```

and selects the maximum. When `delta` is alternative minus null chi-squared, a
positive value means deletion weakens the alternative.

`empirical_tail(samples, threshold, side)` reports both the empirical fraction
and the plus-one estimate. To account for selection, every null sample must
repeat the same group scan and supply its selected maximum—not a preselected
group statistic.

## Frozen ledgers

`freeze_json(payload, path)` writes canonical JSON and a neighboring SHA-256
file. `verify_frozen_json(path)` verifies an existing pair. A published ledger
should additionally be bound to a signed or annotated Git tag and release.

