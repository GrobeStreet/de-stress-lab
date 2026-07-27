# Anatomy of a 2–3σ Hint
## An Independent Stress Test of the DESI DR2 Evolving-Dark-Energy Preference

**Bobby Morong** (independent researcher), with AI-assisted implementation · July 2026
*All data public · all code released with this report · every input primary-sourced · published under a pre-committed publish-regardless protocol*

---

## Abstract

We independently reimplement the compressed likelihoods behind the DESI DR2 preference for evolving dark energy (w₀wₐCDM over ΛCDM) and subject the result to influence diagnostics, calibration stress tests, parameterization swaps, parametric bootstraps, a comparator-measurement swap test, full-Boltzmann (CAMB) verification, and posterior sampling under the collaboration's own priors. We reproduce the published Δχ²_MAP ladder (−4.7/−4.9/−8.0 published vs −4.7/−5.1/−8.5 here), marginalized posteriors (w₀ = −0.45 +0.24/−0.23, wₐ = −1.66 +0.65/−0.71 vs published −0.42 ± 0.21, −1.75 ± 0.58), the w₀–wₐ posterior correlation (−0.978 vs −0.975), and ΔDIC (−4.96 vs −4.4). We then find the preference is sharply localized. Removing the single LRG2 (z = 0.706) BAO measurement collapses the compressed-CMB preference from 2.4σ to 1.6σ (full CAMB: 2.41σ → 1.53σ). Substituting the earlier eBOSS DR16 measurement at the same redshift — a lower-precision, partially sample- and footprint-correlated comparator, not an independent experiment — yields a preference identical to having no measurement there. The z ≈ 0.7 anomaly changed observable between DESI's releases — transverse (D_M) in DR1, radial (D_H) in DR2. A selection-calibrated test repeats all seven tracer deletions inside each of 5,000 ΛCDM mocks. The observed maximum loss of preference is M = 4.125 in Δχ², at LRG2; 78/5,000 null mocks have an equal-or-larger selected maximum, p = 0.0156 [0.0124, 0.0194]. However, among the 70 null mocks whose global w₀wₐ preference is at least as strong as observed, 34 have an equal-or-larger maximum, p_cond = 0.486 [0.364, 0.608]. LRG2 is therefore descriptively load-bearing, but the concentration is not exceptional conditional on a global fluctuation of this strength. On the supernova side, a single free magnitude offset on the DES5Y external low-z sample fits at +0.036 mag and reduces the DESI+DES5Y preference from 2.2σ to 0.2σ (1.3σ with the CMB anchor); this is a degeneracy test, not a calibration diagnosis. The preference is robust across CPL, JBP, and logarithmic w(z) parameterizations (2.4–2.9σ) but nearly absent for constant w (0.8–1.2σ). A 5,000-mock global parametric bootstrap gives P(Δχ² ≤ −8.457 | ΛCDM) = 0.0140 [0.0109, 0.0177], consistent with the Wilks expectation 0.0146. A pre-registered cross-probe consistency test (see §8a) returned an INTERMEDIATE verdict. Finally, a full-CMB variant including lensing (PR3-native likelihoods; see §8b) gives Δχ² = −10.35 (2.77σ) with LRG2 and −3.76 (1.43σ) without it: lensing information does not restore the preference. We conclude the claim is a real, reproducible likelihood-level tension whose support is localized but whose degree of localization is ordinary among equally strong ΛCDM fluctuations. A hint, precisely mapped; not a discovery.

## 1. Motivation and scope

The DESI DR2 BAO analysis (arXiv:2503.14738) reports a preference for a time-varying dark-energy equation of state reaching 3.1σ with full CMB data and 2.8–4.2σ with supernova compilations — the most significant challenge to ΛCDM in a generation, if it holds. Claims of this magnitude attract two failure modes: uncritical amplification and uncritical dismissal. This project attempts a third path: full independent reimplementation followed by systematic attempts to break the result, with every finding published regardless of direction.

Scope, stated precisely: this is an independent implementation of the *published compressed likelihoods* — DESI DR2 BAO summary values, Pantheon+ and DES-SN5YR distance moduli with full covariances, and the DR2 paper's own compressed early-CMB prior (its eqs. 35–36). It is not a raw-data reanalysis. In addition to the compressed branch, a full-CMB variant (Planck 2018 native low-ℓ TT/EE + plik-lite TTTEEE + lensing, via cobaya+CAMB) is included; DESI's own analysis uses PR4 CamSpec and PR4/ACT lensing, so this variant tests the lensing-inclusive structure of the result, not its exact published numbers. Four AI systems performed software, statistics, or manuscript checks during development; these are not independent scientific peer review. One re-executed the pipeline and matched all χ² values to four decimals. A clean-room human rerun remains the outstanding verification step.

## 2. Data and provenance

All inputs are public and primary-sourced under a fixed rule: no number enters the pipeline from memory. DESI DR2 BAO values (7 tracers, correlated D_M/D_H pairs plus BGS D_V) and the compressed CMB prior were machine-extracted from the arXiv HTML of the DR2 paper. Pantheon+ (1,701 light curves; 1,580 after standard cuts; full STAT+SYS covariance) from the official PantheonPlusSH0ES release. DES-SN5YR from the official repository's 2025 Dovekie-recalibrated release (N = 1,820; inverse covariance unpacked per the repository's own likelihood code; external low-z sample identified by IDSURVEY). eBOSS DR16 LRG consensus values from the official SDSS files in the cobaya bao_data release. DESI DR1 values from arXiv:2404.03002. BBN and θ* priors from DR2 eqs. 14 and 16; w(z) priors (w₀ ∈ U[−3,1], wₐ ∈ U[−3,2], w₀+wₐ < 0) verbatim from the paper.

## 3. Methods

Likelihoods are Gaussian in the published summary statistics (mirroring the official compressed treatment), with supernova magnitude offsets marginalized analytically and, where used, subsample calibration offsets marginalized jointly. Late-time distances use a validated fast integrator (relative error < 3×10⁻⁷, verified by external audit). Early-universe quantities (r_drag, θ*) use, in the production pipeline, a calibrated surrogate — standard fitting formulas pinned to the paper's own r_d formula and CMB column, a labeling adopted after audit — and, decisively, full CAMB Boltzmann computations (RECFAST recombination, PPF dark energy) for verification. Two validation gates preceded all dark-energy fits and caught two real implementation bugs before any result existed. Significance follows DESI's two-degree-of-freedom Wilks convention, and is checked against an empirical 5,000-mock null distribution (§8).

## 4. Reproduction

| Quantity | This work | Published |
|---|---|---|
| BAO-alone ΛCDM | Ωm = 0.2973 ± 0.0083, h·r_d = 101.55 ± 0.72 | 0.2975 ± 0.0086, 101.54 ± 0.73 |
| Pantheon+-alone ΛCDM | Ωm = 0.3326 ± 0.0180 (N=1580) | 0.334 ± 0.018 |
| Δχ²: DESI / +Pantheon+ / +cCMB | −4.7 / −5.1 / −8.5 | −4.7 / −4.9 / −8.0 |
| w₀, wₐ (DESI+cCMB, MAP) | −0.44, −1.68 (H0 = 63.6) | −0.42, −1.75 (63.6) |
| w₀, wₐ (posterior 68%) | −0.45 +0.24/−0.23, −1.66 +0.65/−0.71 | −0.42 ± 0.21, −1.75 ± 0.58 |
| w₀–wₐ posterior correlation | −0.978 | −0.975 |
| ΔDIC (DESI+cCMB) | −4.96 (MAP plug-in; p_D = 4.75/3.0) | −4.4 |

An AI software audit re-ran this pipeline and confirmed all χ² values to four decimals, verified the minima against differential evolution, and confirmed covariance positive-definiteness. This is a software check, not independent scientific review.

## 5. Influence diagnostics: where the preference lives

Leave-one-tracer-out refits of DESI+cCMB show the preference is not distributed: dropping any of six tracers leaves 2.3–2.6σ (removing BGS or Lyα *strengthens* it), while dropping LRG2 (z = 0.706) collapses it to 1.6σ. The χ² decomposition attributes the w₀wₐ improvement to LRG2 (−4.1) and the CMB geometric anchor (−3.9), with LRG1 contributing −1.2, all others ≈ 0, and Lyα opposing at +1.0. Within LRG2, the radial measurement dominates: retaining only D_H/r_d gives Δχ² = −6.5, only D_M/r_d gives −4.9, neither −4.3. The selection-calibrated statistic I_j = Δχ²_−j − Δχ²_full and M = max_j I_j gives M_obs = 4.125 at LRG2. Repeating the full fit and all seven deletion fits inside each of 5,000 ΛCDM mocks yields an unconditional selected tail of 78/5,000, p = 0.0156 [0.0124, 0.0194]. Conditioning on a global preference at least as strong as observed leaves 70 mocks, of which 34 meet or exceed M_obs: p_cond = 0.486 [0.364, 0.608]. Thus LRG2's leverage is a valid description of where the observed fit changes, but it is not an additional anomaly beyond the rarity of the global fit. Shifting LRG2 halfway toward the ΛCDM prediction (a 1.18σ move within its own covariance) lowers the global preference below 2σ; inflating only its errors degrades the signal smoothly, indicating genuine statistical leverage rather than numerical pathology. On the supernova side, the significance of DESI+Pantheon+ falls monotonically from 1.8σ to 1.3σ as low-z cuts rise from z > 0.01 to z > 0.1, with w₀ pinned near −0.89 throughout: the *crossing* component is a low-redshift phenomenon.

## 6. The z ≈ 0.7 measurement across experiments

Three analyses have measured BAO at this redshift. Against the ΛCDM best-fit prediction: eBOSS DR16 (z = 0.698; partially correlated with DESI in sample and footprint) deviates jointly by 0.83σ, with D_M *high* if anything; DESI DR1 by 1.40σ, driven by low D_M; DESI DR2 by 1.51σ, driven by low D_H. The anomaly changed observable between DESI's own releases. The swap test quantifies the consequence: with DR2's LRG2 the preference is 2.4σ; with DR1's, 1.9σ; with eBOSS's, 1.6σ — numerically identical to having no z ≈ 0.7 measurement at all. Balanced reading: DR2's measurement is 1.7–1.8× more precise than either comparator and may be resolving what noisier data could not; DESI's blinded internal-consistency checks passed; eBOSS could not strongly confirm a real signal at its precision, and the footprints partially overlap. But a discovery narrative must carry both facts: the signature is unstable across releases, and the earlier partially overlapping measurement at this redshift is ΛCDM-consistent (the swap is a comparator test, not an independent non-confirmation). Reproducing LRG2 from its official likelihood surface is the single most decisive open test.

## 7. Supernova calibration

On the Dovekie-recalibrated DES5Y release, DESI+DES5Y (no CMB) prefers w₀wₐ at 2.2σ (Δχ² = −7.3) — against −13.6 (3.3σ) published with the 2024 release. The updated Dovekie release changed cross-calibration, SALT training, scatter modeling, bias simulations, and sample treatment together; the smaller preference coincides with the new release, but attribution among those changes is not established (the same machinery reproduces Pantheon+ at −5.1 vs −4.9). As a sensitivity test (not a diagnosis — a free offset can absorb calibration, selection, population evolution, survey differences, or genuine cosmological curvature alike), freeing one magnitude offset on the 197 external low-z supernovae returns D = +0.037 mag under ΛCDM — matching Efstathiou's ~0.04 mag estimate from Pantheon+/DES5Y cross-matching — and the preference collapses to 0.2σ, with w₀ = −0.99. With the CMB anchor attached, the intercept still reduces 2.9σ to 1.3σ (D = +0.036). Counter-arguments are part of the record: the DES team reproduces the offset but attributes much of it to improved intrinsic-scatter and host-galaxy modeling (reverting those assumptions moves their result 3.9σ → 3.3σ, not to zero); the intercept is a post-hoc test motivated by a critic and may double-count covariance systematics; and per Cortês & Liddle, the overlapping supernova compilations must never be averaged.

## 8. Robustness of the statistical framework

The preference is not an artifact of the CPL parameterization: JBP and logarithmic w(z) families find it at 2.1–2.9σ across combinations. It is, however, entirely a statement about *time variation*: constant-w captures almost nothing (0.8–1.2σ, w ≈ −1.0), and best-fit (w₀, wₐ) values are strongly family-dependent — the data constrain "the expansion history bends at late times," not a specific trajectory. The completed 5,000-mock global calibration yields 70 exceedances of the unrounded observed Δχ² = −8.4575: p = 0.0140 [0.0109, 0.0177], versus the Wilks expectation 0.0146. This supersedes the earlier 75-mock consistency check and the previously reported 1.50% value derived from the rounded legacy output. The selection-calibrated maximum-influence result is reported in §5; its conditional result shows that localization should not be counted as independent evidence against ΛCDM. The calibrated surrogate's uncertainty, propagated from the published anchor precision, bounds its significance to ±0.5σ — resolved by full CAMB Boltzmann computation (separate execution environment; not scientific independence), which confirms the baseline (2.41σ vs 2.45σ) and the LRG2 collapse (1.53σ vs 1.58σ) with best-fit parameters agreeing to the third decimal. Posterior sampling under the official priors shows no pileup at the w₀+wₐ < 0 boundary; the naive mean-plug-in DIC convention (−8.99) is documented as an artifact of the curved w₀–wₐ ridge, with the standard MAP plug-in giving −4.96 and textbook effective-parameter counts.

## 8a. Pre-registered cross-probe consistency test (H-X)

With hypotheses and kill conditions registered before execution (HYPOTHESIS-cross-probe.md), per-probe w₀wₐ posteriors were sampled for P1 = DESI BAO+cCMB, P2 = Pantheon+ +cCMB+BBN, P3 = DES5Y+cCMB+BBN. Pairwise 2D parameter-shift tensions: P1–P2 = 1.44σ, P1–P3 = 1.35σ, P2–P3 = 0.24σ. Phantom-crossing redshifts: P1 z× = 0.487 [0.418–0.553]; P2 0.292 [0.187–0.502]; P3 0.296 [0.244–0.403]. Verdict against the registered conditions: INTERMEDIATE — neither the consistency (<1σ all pairs) nor inconsistency (>2σ any pair) threshold met; reported without promotion. The registered follow-up is complete: P1 without LRG2 gives z× = 0.478 [0.384–0.564], so LRG2 controls much of the preference's strength but not the surviving BAO posterior's crossing location. Caveats: Gaussian shift metric on curved posteriors; surrogate likelihood (CAMB-validated); shared-anchor correlation.

## 8b. The full-CMB lensing variant

Using cobaya with CAMB and the clik-free native Planck 2018 likelihoods (low-ℓ TT, low-ℓ EE, plik-lite TTTEEE, lensing) plus the DESI BAO likelihood, MAP minimization (BOBYQA, dual converged runs) under DESI's official w(z) priors gives, after removing the uniform-prior volume constant: with LRG2, Δχ² = −10.35 (2.77σ); without LRG2, Δχ² = −3.76 (1.43σ). The with-LRG2 value sits below the published PR4-based −12.5 (3.1σ) by an amount consistent with the PR3-vs-PR4 likelihood difference (pre-registered caveat). The central finding stands at the full-likelihood level: **CMB lensing does not substitute for LRG2** — the preference collapses from ~2.8σ to ~1.4σ on removal of one measurement. Caveats: PR3-native likelihoods; MAP not posterior comparison; single pipeline pending clean-room rerun; the selected-null calibration and its conditional limit are in §5.

## 9. What this establishes — and what it does not

Established: the published compressed likelihoods genuinely contain the reported preference; it survives independent reimplementation, optimizer attack, full Boltzmann physics, parameterization changes, and bootstrap calibration; it is specifically evidence for late-time evolution; and its observed fit sensitivity is sharply localized. The new selected-null calibration adds an essential limit: among ΛCDM mocks with a global preference this strong, a maximum deletion influence at least as large as observed occurs about half the time. Not established: that dark energy evolves; that LRG2 is wrong (its precision is real and DESI's checks passed); that localization is an independent anomaly; that the supernova calibration explanation is correct; or that the PR3-native full-CMB variant numerically reproduces DESI's PR4/ACT likelihood stack. The honest status is **a reproducible, localized 2–3σ hint — not proof.**

## 10. Falsifiable expectations

If the signal is physics: DESI's final likelihood (2027) retains the radial z ≈ 0.7 departure at higher precision; Rubin-calibrated supernovae reproduce the low-z crossing with no magnitude offset required; growth and lensing co-vary as dynamical dark energy predicts. If it is systematics: the LRG2 radial deviation regresses; the supernova preference tracks calibration choices across compilations; residuals decorrelate across probes. We pre-commit to updating this document against those outcomes.

## Reproduction

Everything runs from the released directory. The flagship correction is `python3 scripts/max_influence_mocks.py --mocks 5000 --workers 8 --fresh` (about 8 minutes on the development machine). The original ladder is `python3 scripts/fit_w0wa.py data`; other diagnostics are in `influence.py`, `fit_des5y.py`, `ccmb_ext.py`, `lrg2_audit.py`, `camb_check.py`, and `posterior.py`. Results ship as JSON in `results/`; canonical values and completion states are in `RESULTS_MANIFEST.json`. A blind human-verifier protocol and one-command runner are in `cleanroom/`.

## Acknowledgments and provenance of assistance

Implementation, literature triage, and drafting were AI-assisted (multiple systems, adversarially cross-checked); four AI software/statistics/manuscript audits are incorporated with attribution in the README, but these are not independent scientific replication. A human clean-room rerun remains pending. Errors are the author's. Data credits: DESI, SDSS/eBOSS, Pantheon+/SH0ES, DES, Planck, and the cobaya project's data releases.


## Appendix A. Complete test ledger

| # | Test | Result | Verdict |
|---|---|---|---|
| 1 | ΛCDM reproduction (BAO-alone, SN-alone) | Ωm to ±0.0002 / ±0.0014 of published | PASS |
| 2 | w₀wₐ Δχ² ladder reproduction | −4.7/−5.1/−8.5 vs published −4.7/−4.9/−8.0 | PASS |
| 3 | Best-fit parameter reproduction | w₀, wₐ, Ωm, H0 to ≤0.01 | PASS |
| 4 | Posterior reproduction (emcee, official priors) | intervals match; correlation −0.978 vs −0.975; ΔDIC −4.96 vs −4.4 | PASS |
| 5 | External re-execution (independent AI) | all χ² to 4 decimals; minima verified vs differential evolution | PASS (software check) |
| 6 | Leave-one-tracer-out (7 BAO tracers) | only LRG2 matters: 2.4σ → 1.6σ; others 2.3–2.6σ | **LOCALIZED** |
| 7 | χ² pull decomposition | LRG2 −4.1, CMB anchor −3.9, LRG1 −1.2, Lyα +1.0 (opposes) | LOCALIZED |
| 8 | LRG2 D_M/D_H split (external contribution, verified) | radial D_H carries the leverage (−6.5 vs −4.9) | LOCALIZED |
| 9 | eBOSS swap (partially correlated comparator) | eBOSS in the z≈0.7 slot ≡ no measurement at all (1.6σ) | NOT CORROBORATED |
| 10 | DR1 vs DR2 z≈0.7 comparison | anomaly changed observable: transverse (DR1) → radial (DR2); eBOSS sees neither | UNSTABLE SIGNATURE |
| 11 | Efstathiou intercept test (DES5Y) | fitted offset +0.036–0.037 mag (matches his ~0.04); 2.2σ→0.2σ no-CMB, 2.9σ→1.3σ with cCMB | SN LEG ABSORBABLE (sensitivity test; DES rebuttal stands) |
| 12 | SN low-z cut sweeps (both compilations) | significance decays monotonically as low-z SNe removed; crossing is a low-z phenomenon | LOCALIZED (SN side) |
| 13 | Dovekie-release comparison | DES5Y contribution −13.6 → −7.3 across releases (multi-element change; attribution open) | RELEASE-DEPENDENT |
| 14 | w(z) parameterization swap (CPL/JBP/LOG/wCDM) | evolving families all 2.1–2.9σ; constant-w 0.8–1.2σ | ROBUST to form; evidence is specifically TIME VARIATION |
| 15 | Parametric bootstrap, 5,000 ΛCDM mocks (unrounded reconciled runner) | P(false pos.) = 1.40% [1.09–1.77%] vs Wilks 1.46% | STATISTICS CALIBRATED |
| 16 | Anchor-uncertainty propagation | surrogate pins significance to 2.4σ ± 0.5σ | BOUNDED, then superseded by #17 |
| 17 | Full CAMB Boltzmann verification | baseline 2.41σ vs surrogate 2.45σ; no-LRG2 1.53σ vs 1.58σ | SURROGATE VINDICATED |
| 18 | Full-CMB + lensing variant (PR3-native, cobaya) | 2.77σ with LRG2 (pub. PR4: 3.1σ); **1.43σ without LRG2** | LENSING DOES NOT RESCUE |
| 19 | H-X pre-registered cross-probe consistency | BAO–SN shifts 1.44σ/1.35σ; SN–SN 0.24σ; z×: BAO 0.49±0.07, SNe ≈0.30 | **INTERMEDIATE** (per kill conditions) |
| 20 | H-X registered follow-up: BAO z× without LRG2 | z× = 0.478 [0.384–0.564] — unchanged | CROSSING LOCATION IS DISTRIBUTED, not an LRG2 artifact |
| 21 | H-Y registered: SN crossing vs intercept degeneracy | with intercept marginalized: wₐ = +0.50 [−0.33, +1.03] (includes 0, flips sign); w₀ → −1.17 | **KILL CONDITION MET: SN crossing degenerate with calibration seam** |
| 22 | Selection-calibrated maximum influence, 5,000 ΛCDM mocks | M_obs = 4.125 at LRG2; unconditional 78/5,000, p=0.0156; conditional on equally strong global preference 34/70, p=0.486 | **LOCALIZED, BUT NOT EXCEPTIONALLY SO CONDITIONAL ON SIGNAL STRENGTH** |

## Appendix B. Availability

Code, data-download instructions, results, chains, and the pre-registered hypothesis chain: https://github.com/GrobeStreet/de-stress-lab (v1.0, MIT). Archived with DOI via Zenodo.
