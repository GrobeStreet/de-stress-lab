# Frozen 2027 prediction ledger

**Version:** 1.0  
**Frozen:** 2026-07-27  
**Scoring cutoff:** 2027-12-31  
**Release tag:** `prediction-ledger-2027-v1`

This ledger converts the report's narrative expectations into tests fixed before
the relevant 2027 results are known. It is a forecast, not new evidence. The
original file is immutable. Clarifications or corrections must be published as
separately hashed amendments without replacing this version.

## Baseline

The frozen DR2 analysis found:

- held-out LRG2 joint \(p=0.0408\);
- isotropic \(D_V/r_d\) residual \(p=0.0204\), \(|z|=2.319\);
- Alcock–Paczynski ratio residual \(p=0.3744\), \(|z|=0.884\);
- direct constant-\(w\) versus CPL test \(2.75\sigma\);
- the same direct test without LRG2 \(1.81\sigma\);
- a fitted DES5Y external-low-redshift intercept of about \(+0.036\) mag.

## Predictions

### P2027-01 — the redshift-0.7 distance-scale residual regresses

In the final public DESI BAO release, fit flat ΛCDM to all public DESI BAO
tracers except the tracer whose effective redshift is nearest 0.706, together
with the collaboration's baseline early-universe anchor. Propagate fit
uncertainty and score the held-out isotropic \(D_V/r_d\) residual.

**Prediction:** \(|z_{D_V}| < 2.0\).  
**Forecast probability:** 0.65.

### P2027-02 — the redshift-0.7 shape ratio remains ordinary

Using the same held-out fit, score the ratio \(D_M/D_H\).

**Prediction:** \(|z_{\rm AP}| < 1.5\).  
**Forecast probability:** 0.80.

### P2027-03 — final DESI alone does not cross 3σ for direct time variation

For final public DESI BAO plus the collaboration's baseline CMB combination,
compare constant-\(w\) CDM with CPL \(w_0w_a\)CDM using the collaboration's
priors. Prefer a collaboration-reported calibrated significance; otherwise run
the public null-calibrated procedure in this repository.

**Prediction:** the direct time-variation preference is below \(3.0\sigma\).  
**Forecast probability:** 0.75.

### P2027-04 — no final-release tracer is as load-bearing as DR2 LRG2

Repeat the direct constant-\(w\) versus CPL comparison after deleting each final
DESI tracer in turn. Compare the equivalent significance before and after each
deletion.

**Prediction:** no single deletion reduces the equivalent significance by
\(0.75\sigma\) or more.  
**Forecast probability:** 0.60.

### P2027-05 — survey-aware supernova calibration reduces the low-z seam

Use the first public Rubin-era supernova cosmology analysis released by the
cutoff that supplies a survey-aware low-redshift cross-calibration model.
Measure the fitted relative low-z magnitude offset and the change in the
CPL-versus-ΛCDM improvement when that calibration freedom is introduced.

**Prediction:** \(|D| < 0.020\) mag and the calibration freedom changes
\(|\Delta\chi^2|\) by less than 4.  
**Forecast probability:** 0.60.

If no qualifying public Rubin-era analysis exists by the cutoff, this prediction
is marked **unscored**, not false.

### P2027-06 — no discovery-grade independent confirmation by the cutoff

**Prediction:** no final DESI BAO analysis and no Rubin-era supernova analysis,
considered separately, reports a look-elsewhere-aware \(5\sigma\) rejection of
constant-\(w\) dark energy in favor of time variation by 2027-12-31.  
**Forecast probability:** 0.90.

## Adjudication

The source hierarchy is:

1. final collaboration paper and its public likelihood;
2. collaboration data release and documented baseline configuration;
3. an independently reproducible calculation using the released package.

A prediction receives 1 for true, 0 for false, and is excluded if its stated
qualifying data do not exist by the cutoff. Mixed conjunctive thresholds are
true only if all stated conditions hold. The adjudication must cite sources,
record code and data versions, and publish a new checksum; it must not alter
this ledger.

## Integrity

The machine-readable record is `2027-ledger.json`. Its SHA-256 digest is stored
in `2027-ledger.json.sha256`. The annotated Git tag and GitHub release named
above bind those files to a public commit and timestamp.

