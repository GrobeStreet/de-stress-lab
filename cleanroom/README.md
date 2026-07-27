# Independent verifier rerun

This package is for a human verifier working in a fresh clone and a fresh Python
environment. It reproduces the selection-calibrated influence test and the three
frontier diagnostics without external data downloads: the seven published DESI DR2
BAO summaries and compressed-CMB mean/covariance are versioned in
`scripts/fit_w0wa.py`.

This is an independent **execution and numerical verification** of the released code.
It is not a clean-room reimplementation of the likelihood from the papers. A stronger
verification would independently transcribe the published inputs and write a separate
implementation.

## Blind protocol

1. Obtain the repository URL and commit identifier from the author, but do not read
   `RESULTS_MANIFEST.json`, the manuscript results paragraphs, or `results/max_influence_mocks.json`.
2. Clone that exact commit into a new directory on a machine or user account not used
   for development.
3. Record the commit, platform, Python version, and UTC start time in
   `VERIFIER_WORKSHEET.md`.
4. Create the environment:

   ```bash
   python3 -m venv .venv-cleanroom
   .venv-cleanroom/bin/python -m pip install --upgrade pip
   .venv-cleanroom/bin/python -m pip install -r cleanroom/requirements.txt
   ```

5. Run a 20-mock smoke test:

   ```bash
   cleanroom/run_flagship.sh 20 1 cleanroom/smoke-output.json
   ```

   Confirm that all fits report convergence and that rerunning the same command produces
   a byte-for-byte identical JSON file.

6. Run the registered 5,000-mock calibration. Replace `8` with a suitable worker count:

   ```bash
   cleanroom/run_flagship.sh 5000 8 cleanroom/verification-output.json
   ```

7. Before viewing the project's expected result, copy the following fields from
   `cleanroom/verification-output.json` into the worksheet:

   - `observed.dchi2_full`
   - all seven values in `observed.dchi2_deleted`
   - `observed.selected_tracer`
   - `observed.max_influence`
   - `summary.exceedances_ge_observed`
   - `summary.empirical_tail_probability`
   - `summary.clopper_pearson_95`
   - `summary.failed_optimizer_records`

8. Hash the output and sign/date the worksheet:

   ```bash
   shasum -a 256 cleanroom/verification-output.json
   ```

9. Only then compare against `RESULTS_MANIFEST.json` and
   `results/max_influence_mocks.json`. Report every numerical mismatch, convergence
   failure, code change, or environmental deviation; do not silently repair the run.

## Frontier diagnostics

After completing and recording the flagship result, run the direct time-variation
and held-out LRG2 tests:

```bash
cleanroom/run_frontier.sh 20 1 cleanroom/frontier-smoke
cleanroom/run_frontier.sh 5000 8 cleanroom/frontier-verification
```

The runner first executes the unit tests, then produces:

- `time-variation.json`: one-extra-parameter likelihood-ratio calibration of
  constant-w CDM against CPL w₀wₐCDM;
- `time-variation-no-lrg2.json`: the same calibrated test after omitting LRG2;
- `lrg2-posterior-predictive.json`: a ΛCDM fit excluding LRG2 followed by a
  held-out joint, Alcock–Paczynski-ratio, and isotropic-distance check.

Record the requested fields in `VERIFIER_WORKSHEET.md` before viewing the expected
values. The time-variation mocks are generated at the observed best-fit constant-w
null separately for the full and no-LRG2 datasets. The LRG2 diagnostic is targeted
after inspection; it must be interpreted together with the selection-calibrated
maximum-influence result, not as an independent discovery test.

## Optional broader reproduction

To reproduce the compressed-likelihood ladder and the published leave-one-out table,
download the public supernova files with `data/DOWNLOAD.md`, then run:

```bash
.venv-cleanroom/bin/python scripts/fit_w0wa.py data
.venv-cleanroom/bin/python scripts/influence.py data loo
```

Those commands overwrite their result JSONs in the verifier's clone. Preserve the
original clone state or use a disposable checkout.

## Acceptance criteria

The flagship rerun passes if:

- all 5,000 mock records and the observed record report optimizer convergence;
- the selected observed tracer and all eight observed Δχ² values match the manifest
  within `1e-3`;
- the exceedance count matches exactly for deterministic seeds 10000–14999;
- a repeated run with the same software versions produces the same output hash.

The frontier rerun passes if:

- all unit tests pass;
- all three outputs contain 5,000 mock records with zero optimizer failures;
- the observed statistics match within `1e-6`, and the exceedance counts match
  `RESULTS_MANIFEST.json`;
- the full-data and no-LRG2 time-variation tests use their own recorded constant-w
  null fits and report no fit at the prior boundary.

Record all hashes. Exact byte-level hash agreement is expected on a repeated run in
the same pinned environment; across platforms, last-bit floating-point differences
may change the JSON hash without changing the numerical result.

If only the final JSON is compared, this verifies deterministic re-execution. For
scientific independence, the verifier should additionally audit the statistic definition,
mock generator, likelihood inputs, bounds, and optimizer behavior against the cited
primary sources.

## Optional optimizer cross-check

The production run uses bounded least-squares on the exact whitened Gaussian residual
vector. To compare it with the original scalar-χ² Nelder–Mead pipeline on matched seeds:

```bash
.venv-cleanroom/bin/python scripts/max_influence_mocks.py \
  --mocks 200 --workers 8 --solver least-squares --fresh \
  --output cleanroom/least-squares-output.json
.venv-cleanroom/bin/python scripts/max_influence_mocks.py \
  --mocks 200 --workers 8 --solver nelder-mead --fresh \
  --output cleanroom/nelder-mead-output.json
.venv-cleanroom/bin/python scripts/compare_max_influence_runs.py \
  cleanroom/nelder-mead-output.json cleanroom/least-squares-output.json
```

The released validation summary is
`results/max_influence_solver_validation.json`.
