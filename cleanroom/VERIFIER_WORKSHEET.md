# DESI maximum-influence verification worksheet

Complete this before opening `RESULTS_MANIFEST.json` or the canonical result JSON.

## Environment

- Verifier:
- UTC date/time:
- Repository URL:
- Commit:
- `git status --short` before run:
- Operating system / architecture:
- Python:
- NumPy:
- SciPy:
- Worker count:
- Wall-clock runtime:

## Observed seven-tracer analysis

- Full-data Δχ²:
- Delete BGS Δχ²:
- Delete LRG1 Δχ²:
- Delete LRG2 Δχ²:
- Delete LRG3+ELG1 Δχ²:
- Delete ELG2 Δχ²:
- Delete QSO Δχ²:
- Delete Lyα Δχ²:
- Selected tracer:
- Selected maximum influence:

## Selection-calibrated null result

- Number of mocks:
- Seed range:
- Exceedances at or above observed maximum:
- Empirical tail probability:
- Plus-one tail probability:
- Exact 95% interval:
- Optimizer failures:
- Output SHA-256:

## Audit notes

- Did the smoke test reproduce byte-for-byte?
- Were any commands, inputs, bounds, tolerances, or source files changed?
- Were the likelihood constants independently checked against primary sources?
- Were a sample of minima checked with a second optimizer or starting point?
- Differences from the released result:

## Direct time-variation calibration

### Full DESI+cCMB

- Observed wCDM χ² and best-fit w:
- Observed w₀wₐCDM χ², w₀, and wₐ:
- T = χ²(wCDM) − χ²(w₀wₐCDM):
- Number of mocks and seed range:
- Exceedances:
- Empirical tail probability and exact 95% interval:
- Gaussian-equivalent significance:
- Prior-boundary records / optimizer failures:
- Output SHA-256:

### Without LRG2

- Observed wCDM χ² and best-fit w:
- Observed w₀wₐCDM χ², w₀, and wₐ:
- T = χ²(wCDM) − χ²(w₀wₐCDM):
- Number of mocks and seed range:
- Exceedances:
- Empirical tail probability and exact 95% interval:
- Gaussian-equivalent significance:
- Prior-boundary records / optimizer failures:
- Output SHA-256:

## Held-out LRG2 diagnostic

- No-LRG2 ΛCDM best-fit parameters:
- Predicted and observed `(D_M/r_d, D_H/r_d)`:
- Joint χ²:
- Joint bootstrap exceedances, p, and exact 95% interval:
- `F_AP` observed/predicted, |z|, and bootstrap p:
- `D_V/r_d` observed/predicted, |z|, and bootstrap p:
- Prior-boundary records / optimizer failures:
- Output SHA-256:

## Attestation

I recorded the fields above before viewing the expected values in the results manifest.

- Name:
- Signature or cryptographic identity:
- UTC date:
