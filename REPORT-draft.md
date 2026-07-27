# SUPERSEDED DRAFT — DO NOT CITE

This outline predates the completed 5,000-mock calibration, full-CMB lensing
variant, registered H-X/H-Y results, and selection-calibrated influence test.
The canonical manuscript is `whitepaper.md`; canonical machine-readable results
and completion states are in `RESULTS_MANIFEST.json`.

# Anatomy of a 2–3σ Hint: An Independent Stress Test of the DESI DR2 Evolving-Dark-Energy Preference
### Draft v0.9 — public write-up of the Dark-Energy Stress Lab · July 2026

*Independent researcher (Bobby M.), with AI-assisted implementation. All data public; all code released; every input primary-sourced. This report publishes regardless of direction, per pre-committed protocol.*

## Abstract
We independently reimplement the compressed likelihoods behind the DESI DR2 preference for evolving dark energy (w₀wₐCDM over ΛCDM) and subject the result to influence diagnostics, calibration stress tests, parameterization swaps, a parametric bootstrap, an independent-measurement swap test, and an exact-Boltzmann (CAMB) verification. We reproduce the published Δχ²_MAP ladder (−4.7 / −4.9 / −8.0 published vs −4.7 / −5.1 / −8.5 here) and best-fit parameters to the third decimal. We then find the preference is sharply *localized*: (1) removing the single LRG2 (z=0.706) BAO measurement collapses the compressed-CMB preference from 2.4σ to 1.6σ (confirmed with exact CAMB physics: 2.41σ → 1.53σ); (2) substituting the independent eBOSS DR16 measurement at the same redshift yields a preference identical to having no measurement there at all; (3) the z≈0.7 anomaly changed observable between DESI's own data releases (transverse in DR1, radial in DR2); (4) a single free magnitude offset on the DES5Y external low-z supernova sample fits at +0.036 mag — matching Efstathiou's published estimate — and reduces the DESI+DES5Y preference from 2.2σ to 0.2σ (1.3σ with the CMB anchor); (5) the preference is robust across CPL/JBP/logarithmic parameterizations (2.4–2.9σ) but absent for constant w (0.8–1.2σ): the evidence is specifically for *time variation*; (6) a 75-mock parametric bootstrap confirms the Wilks-based significance labels are honest (empirical false-positive rate 1.3% vs 1.5% expected). Posterior sampling under DESI's official priors yields [POSTERIOR RESULTS — see below]. We conclude the claim is a real, reproducible likelihood-level tension whose observational support is concentrated in one radial BAO measurement and one contested supernova calibration seam — a hint that current evidence cannot promote to a discovery, and that DESI's 2027 final likelihood and independently calibrated supernovae will decide.

## 1. Motivation and scope
[From README scope statement: independent compressed-likelihood implementation, not raw-data reanalysis; audit-reconciled claims.]

## 2. Data and provenance
[Provenance table: DESI DR2 BAO summary values (arXiv:2503.14738, machine-extracted); Pantheon+ official release (1,701 SNe, full STAT+SYS covariance); DES-SN5YR Dovekie release (N=1820, official inverse covariance); compressed CMB prior (DR2 eqs. 35–36); BBN and θ* priors (DR2 eqs. 14, 16); eBOSS DR16 consensus (cobaya bao_data); DESI DR1 (arXiv:2404.03002). Provenance rule: no number from memory.]

## 3. Methods
[Likelihoods; validation gates G1/G2 and the two bugs they caught; calibrated surrogate + its empirical vindication by CAMB; optimizer; significance conventions; official priors w₀∈U[−3,1], wₐ∈U[−3,2], w₀+wₐ<0.]

## 4. Reproduction results
[Ladder table; parameter agreement; cross-AI verification note (χ² matched to 4 decimals by an independent re-run).]

## 5. Influence diagnostics
[LOO table; pull decomposition; SN low-z cut sweeps; LRG2 D_M/D_H split (radial carries the leverage); shift and error-inflation tests.]

## 6. The z≈0.7 measurement across experiments
[eBOSS/DR1/DR2 comparison; observable instability (transverse→radial); swap test: eBOSS ≡ no measurement; balanced caveats (precision asymmetry, footprint overlap, DESI internal consistency).]

## 7. Supernova calibration tests
[Efstathiou intercept test on Dovekie DES5Y: D=+0.036–0.037 mag, preference → 0.2σ (no CMB) / 1.3σ (cCMB); Dovekie recalibration itself −13.6→−7.3; DES rebuttal (Vincenzi et al.) documented; Cortês & Liddle averaging warning; Afroz & Mukherjee.]

## 8. Robustness of the statistical framework
[Parameterization swap (CPL/JBP/LOG vs wCDM); parametric bootstrap (75 mocks); anchor-uncertainty propagation (±0.5σ surrogate bound); exact-CAMB verification on independent hardware.]

## 9. Posterior inference
Full MCMC (emcee, 80k samples) under DESI's official priors (w₀∈U[−3,1], wₐ∈U[−3,2], w₀+wₐ<0) over the CAMB-validated likelihood, run on local hardware. Marginalized 68% intervals: **w₀ = −0.45 +0.24/−0.23, wₐ = −1.66 +0.65/−0.71** (published DESI+CMB: −0.42±0.21, −1.75±0.58). Posterior w₀–wₐ correlation **−0.978** vs the paper's quoted −0.975. ΛCDM: Ωm = 0.3013±0.0036, H0 = 68.25±0.28. **ΔDIC = −4.96** with MAP plug-in (effective parameters 4.75/3.0, as expected) vs published −4.4 — matching to the same offset as Δχ²; the naive mean-plug-in convention gives −8.99, an artifact of the curved w₀–wₐ ridge, documented as a convention sensitivity. Zero posterior mass within 0.05 of the w₀+wₐ<0 prior boundary in this data combination. Thinned chain released (results/w0wa_chain.npz).

## 10. What this does and does not establish
Established: the published compressed likelihoods contain the reported preference; it is not a coding, optimizer, or Wilks artifact; it is specifically evidence for time variation; it is sharply localized. Not established: that dark energy evolves; that LRG2 is wrong; that the calibration explanation is correct (DES rebuttal stands); anything about the full-CMB lensing contribution (out of scope). Verdict: **a reproducible, sharply localized 2–3σ hint — not proof.**

## 11. Falsifiable expectations
If the signal is real physics: DESI final likelihood (2027) should retain the radial-BAO departure at z≈0.7 with higher precision; independently calibrated Rubin SNe should reproduce the low-z crossing without a magnitude offset; growth/lensing data should co-vary as dynamical dark energy predicts. If it is systematics: the LRG2 radial deviation should regress; the SN preference should track calibration choices; ΛCDM residuals should decorrelate across probes.

## Appendices
A. Full results JSONs. B. Reproduction instructions (env, commands, runtimes). C. Audit trail (three external AI audits and adopted corrections). D. Known limitations (posteriors from surrogate likelihood; no full-CMB lensing; no Union3; look-elsewhere in LOO; intercept test post-hoc).
