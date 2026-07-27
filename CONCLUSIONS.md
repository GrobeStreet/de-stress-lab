# CONCLUSIONS — The Dark-Energy Stress Lab
### The complete findings, testing record, and conclusions of the investigation · July 2026
*Companion to REPORT.md (the formal paper), README.md (the chronological lab record), and HYPOTHESIS-cross-probe.md (the pre-registered test chain). This document is the synthesis.*

---

## I. The investigation at a glance

**Question:** Is the DESI DR2 evidence for evolving dark energy — the strongest challenge to the standard cosmological model in a generation — a robust, distributed signal, or a fragile, localized one?

**Method:** Independent reimplementation of the published compressed likelihoods from primary sources, followed by systematic adversarial testing: influence diagnostics, calibration stress tests, parameterization swaps, empirical significance calibration, full-Boltzmann verification, posterior inference, and pre-registered cross-probe hypothesis tests. Four external adversarial reviews absorbed; all corrections adopted; two internal bugs caught by validation gates before any result existed; every finding published regardless of direction.

**Answer, in one sentence:** Within the compressed CPL analysis, time variation is directly preferred at a calibrated 2.75σ, but the result falls to 1.81σ without LRG2, whose held-out residual is modest and mostly an isotropic-distance discrepancy; this is a sharpened hint, not a discovery.

## II. The complete test ledger

Every test run by this lab, its result, and its verdict. Reproduction targets from DESI DR2 (arXiv:2503.14738) unless noted.

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
| 14 | w(z) parameterization swap (CPL/JBP/LOG/wCDM) | evolving families all 2.1–2.9σ; constant-w 0.8–1.2σ | EVOLVING FLEXIBILITY REWARDED; DIRECT TEST IN #23 |
| 15 | Parametric bootstrap, 5,000 ΛCDM mocks (unrounded reconciled runner) | P(false pos.) = 1.40% [1.09–1.77%] vs Wilks 1.46% | STATISTICS CALIBRATED |
| 16 | Anchor-uncertainty propagation | surrogate pins significance to 2.4σ ± 0.5σ | BOUNDED, then superseded by #17 |
| 17 | Full CAMB Boltzmann verification | baseline 2.41σ vs surrogate 2.45σ; no-LRG2 1.53σ vs 1.58σ | SURROGATE VINDICATED |
| 18 | Full-CMB + lensing variant (PR3-native, cobaya) | 2.77σ with LRG2 (pub. PR4: 3.1σ); **1.43σ without LRG2** | LENSING DOES NOT RESCUE |
| 19 | H-X pre-registered cross-probe consistency | BAO–SN shifts 1.44σ/1.35σ; SN–SN 0.24σ; z×: BAO 0.49±0.07, SNe ≈0.30 | **INTERMEDIATE** (per kill conditions) |
| 20 | H-X registered follow-up: BAO z× without LRG2 | z× = 0.478 [0.384–0.564] — unchanged | CROSSING LOCATION IS DISTRIBUTED, not an LRG2 artifact |
| 21 | H-Y registered: SN crossing vs intercept degeneracy | with intercept marginalized: wₐ = +0.50 [−0.33, +1.03] (includes 0, flips sign); w₀ → −1.17 | **KILL CONDITION MET: SN crossing degenerate with calibration seam** |
| 22 | Selection-calibrated maximum influence, 5,000 ΛCDM mocks | M_obs = 4.125 at LRG2; unconditional 78/5,000, p=0.0156; conditional on equally strong global preference 34/70, p=0.486 | **LOCALIZED, BUT NOT EXCEPTIONALLY SO CONDITIONAL ON SIGNAL STRENGTH** |
| 23 | Direct time-variation calibration: wCDM vs CPL | T=7.851; 30/5,000 best-fit constant-w mocks; p=0.0060 [0.0041–0.0086], 2.75σ | **DIRECT CPL TIME-VARIATION HINT** |
| 24 | Direct time-variation calibration without LRG2 | T=3.426; 349/5,000; p=0.0698 [0.0629–0.0772], 1.81σ | **MOST STRENGTH IS LRG2-SENSITIVE** |
| 25 | Held-out LRG2 ΛCDM prediction | joint p=0.0408 (2.05σ); isotropic D_V p=0.0204; AP ratio p=0.374 | **MODEST SCALE DISCREPANCY; SHAPE ORDINARY; TARGETED TEST** |

## III. The three-layer picture (current best model of the evidence)

Everything above coheres into a three-layer anatomy that neither pure narrative — "dark energy is evolving" nor "it's all systematics" — survives contact with:

**Layer 1 — A weak, distributed BAO-geometry feature.** Even with LRG2 removed, the BAO+CMB data retain a ~1.4–1.6σ ΛCDM-versus-w₀wₐ preference and a 1.81σ direct wCDM-versus-CPL preference, with a stable CPL turning point at z ≈ 0.48 (tests #20 and #24). This is not one data point, but it is too weak to support a physical claim alone.

**Layer 2 — The LRG2 amplifier.** LRG2 at z = 0.706 supplies much of the *model-preference strength*: compressed (2.4σ→1.6σ), full-Boltzmann (2.41σ→1.53σ), full-CMB-with-lensing (2.77σ→1.43σ), and direct CPL time variation (2.75σ→1.81σ). The earlier component split shows greater radial leverage, but the new held-out prediction identifies a joint 2.05σ discrepancy driven mainly by low isotropic D_V/r_d (p=0.0204), not an unusual AP ratio (p=0.374). Test #22 calibrates the selection: M_obs = 4.125 is rare unconditionally (p=0.0156) but ordinary conditional on a global fluctuation this strong (34/70, p=0.486). “Load-bearing” is descriptive; the targeted p-values are not additional discovery evidence.

**Layer 3 — The supernova seam.** Both SN compilations share a mild evolution feature (they agree with each other at 0.24σ) with a turning point at z ≈ 0.30 — a *different* location than the BAO layer prefers. The DES5Y version of this feature can be absorbed by a single +0.036 mag low-z calibration offset (matching Efstathiou's independent estimate; contested by DES), decays under low-z cuts, and shrank between DES data releases. Test #21 (registered, completed): the crossing does NOT survive the calibration nuisance — wₐ becomes consistent with zero and flips sign. Layer 3 is fully degenerate with the seam; cause (calibration vs cosmology) remains formally open but the leading systematic explanation is sufficient.

The published 3.1–4.2σ headline is the sum of these three layers plus the CMB anchor — layers that, on our evidence, do not obviously agree on what they are measuring (z× = 0.48 vs 0.30, at ~1.4σ each despite a shared anchor pulling them together).

## IV. Conclusions

**Established (would defend against any audience):**
1. The published compressed likelihoods genuinely contain the reported evolving-dark-energy preference; it is not a software, optimizer, prior-boundary, or Wilks artifact (tests 1–5, 15).
2. Within CPL and the compressed DESI+cCMB likelihood, the direct extra parameter for time variation is preferred at 2.75σ against a best-fit constant-w null (test 23); this is not a model-independent detection of arbitrary time dependence.
3. The preference is highly sensitive to LRG2 at every level tested, including direct time variation and CMB lensing (tests 6–8, 17, 18, 24), but that maximum influence is typical conditional on an equally strong global ΛCDM fluctuation (test 22).
4. The z ≈ 0.7 anomaly is uncorroborated and release-unstable (tests 9, 10).
5. The DES5Y supernova contribution is absorbable by one calibration parameter of exactly the magnitude independently predicted (test 11) — a sensitivity result, not a diagnosis.
6. The BAO leg's preferred crossing location is distributed, not an LRG2 artifact (test 20) — a point against the maximal-systematics reading, found by our own registered test and reported per pre-commitment.
7. The look-elsewhere concern in naming LRG2 is now calibrated directly: localization remains a valid influence map, not additional evidence against ΛCDM (test 22).
8. A held-out ΛCDM prediction finds LRG2 modestly discrepant jointly, but the discrepancy is a distance-scale shift rather than an unusual AP anisotropy (test 25).

**Refuted or resolved (within this lab's scope):**
- "The lensing information independently supports evolving dark energy" — no (test 18).
- "The significance labels are inflated" — no; empirically calibrated (test 15).
- "The result is an artifact of the CPL parameterization" — no (test 14).
- "Everything is LRG2" — no; the crossing location survives without it (test 20).
- "The LRG2 issue is specifically an anomalous radial/transverse shape" — no; the held-out AP ratio is ordinary even though D_H has more model leverage (test 25).

**Undecided (honestly):**
- Whether the three layers reflect one true physical evolution imperfectly measured, or a coincidence of a BAO-geometry fluctuation and an SN calibration seam. The pre-registered cross-probe test returned INTERMEDIATE (test 19); the z× split (0.48 vs 0.30) is suggestive of two signals but below every pre-committed threshold.
- Whether LRG2's precision is measuring reality or fluctuating — only DESI's final likelihood (2027) and an official-likelihood-level audit decide.
- Whether the SN seam is calibration or cosmology: test #21 established full *degeneracy* — the SN data cannot distinguish a z≈0.3 bend from a 3.6% cross-sample mis-stitch (cause remains open; Rubin-calibrated SNe break the degeneracy).

No numerical probability is assigned to signal survival or “new physics”: this analysis does not derive such odds. If the effect is physical, the map still supplies a falsifiable expectation — a late-time bend with BAO geometry favoring z× ≈ 0.5 — for future data.

## V. What decides it (in order of arrival)
1. ~~Test #21~~ DONE: the SN crossing does NOT survive the intercept (kill condition met) — Layer 3 is calibration-degenerate.
2. **Official-likelihood LRG2 audit** (requires DESI likelihood files): the decisive check on Layer 2.
3. **DESI final likelihood, 47M galaxies (2027):** does the z≈0.7 distance-scale departure sharpen or regress; does the distributed z×≈0.48 feature persist.
4. **Rubin-calibrated supernovae (2027+):** does the z×≈0.30 SN feature appear with no calibration dial available.
5. **Growth and lensing co-variance (RSD, fσ8, E_G):** the physics-vs-systematics discriminator no background test can provide.

## VI. Provenance of this investigation
Built by an independent researcher with AI-assisted implementation; all data public; every input primary-sourced under a no-numbers-from-memory rule; two implementation bugs caught by pre-set validation gates; four AI software/statistics/manuscript reviews logged; registered tests reported against pre-committed conditions; and the post-selection correction in test 22 incorporated even though it limits the strongest localization narrative. A blind human-verifier package is complete; independent human execution remains pending.
