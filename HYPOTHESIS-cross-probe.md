# Registered Hypothesis — Cross-Probe Consistency of the Preferred w(z)
**Registered 2026-07-20, BEFORE any test was run. Results bind to this document.**

## Hypothesis
**H-X:** If the late-time expansion-history bend is physical, the three data legs (DESI BAO, Pantheon+, DES5Y — each anchored by the same compressed CMB) must prefer *statistically consistent* regions of the (w₀, wₐ) plane and consistent phantom-crossing redshifts. If the preference is a coincidence of unrelated systematics (LRG2 fluctuation + SN calibration seam), the legs should prefer *mutually inconsistent or disjoint* evolutions, with the joint fit a compromise that no single leg favors.

## Pre-specified tests
1. Posterior sampling (emcee, official DESI priors incl. w₀+wₐ<0) of w₀wₐCDM for three probe combinations:
   P1 = DESI BAO + cCMB (chain exists) · P2 = Pantheon+ + cCMB + BBN · P3 = DES5Y + cCMB + BBN.
2. Pairwise 2D parameter-shift tension in (w₀, wₐ): Δμᵀ(C₁+C₂)⁻¹Δμ → σ-equivalent (Gaussian approximation; documented limitation given banana-shaped posteriors — also report overlap of 68% regions).
3. Phantom-crossing redshift z× (where w(z)=−1) computed per posterior sample; compare distributions across probes.

## Pre-committed interpretations (kill conditions)
- **Consistent** (all pairwise shifts <1σ and z× distributions overlapping at 68%): supports a common physical origin; weakens the "two unrelated systematics" reading; must be reported as evidence FOR the DESI interpretation.
- **Inconsistent** (any pairwise shift >2σ or disjoint z× at 95%): the joint preference averages incompatible signals; strengthens the systematics reading.
- **Intermediate:** report as inconclusive; no narrative promotion either way.
- Known confound, stated now: all three probes share the cCMB anchor, which correlates them toward agreement; a null result (consistency) is therefore WEAKER evidence than an inconsistency result is. Low SN-leg constraining power may also render the test inconclusive rather than confirmatory.

## Status
- [x] P2, P3 chains run · [x] tension computed · [x] z× computed · [x] conclusions appended below.

## RESULT (2026-07-20) — verdict against the pre-registered kill conditions: **INTERMEDIATE**

Pairwise 2D parameter-shift tensions: P1(BAO)–P2(Pantheon+) = 1.44σ; P1–P3(DES5Y) = 1.35σ; P2–P3 = **0.24σ**. Crossing-redshift 68% intervals: BAO z× = 0.487 [0.418–0.553]; Pantheon+ 0.292 [0.187–0.502]; DES5Y 0.296 [0.244–0.403].

Against the registered conditions: NOT "consistent" (two pairwise shifts exceed 1σ; BAO and DES5Y z× intervals are disjoint at 68%), and NOT "inconsistent" (no shift exceeds 2σ; z× not shown disjoint at 95%). **Per pre-commitment, this is reported as inconclusive with no narrative promotion in either direction.**

Texture, reported without promotion: the two supernova legs agree with each other almost perfectly (0.24σ) and both prefer a milder evolution crossing at z× ≈ 0.29–0.30; the BAO leg prefers a sharper evolution crossing at z× ≈ 0.49. Each BAO–SN comparison sits at ~1.4σ despite the shared CMB anchor biasing the legs toward agreement (a bias noted in the registration). Interpretations compatible with this pattern include: (a) one real evolution imperfectly measured by all legs; (b) a shared mild SN feature (physical or calibration-driven) plus an unrelated BAO feature; (c) noise. Method caveats: Gaussian shift metric on curved posteriors; percentile-based z× overlap; surrogate likelihood (CAMB-validated).

Follow-up test that would sharpen this: repeat P1 without LRG2 — if the BAO leg's z× preference dissolves without LRG2 while the SN legs' z× ≈ 0.3 persists, the "two separate signals" reading gains; registered here before running.


## REGISTERED FOLLOW-UP RESULT (2026-07-20): P1 without LRG2

w₀ = −0.59 [−0.84, −0.31], wₐ = −1.27 [−2.07, −0.55]; **z× = 0.478 [0.384–0.564]** (defined in 97% of samples), vs z× = 0.487 [0.418–0.553] with LRG2.

**The registered condition ("BAO z× preference dissolves without LRG2") did NOT occur.** The crossing-location preference is essentially unchanged — only slightly broadened — when LRG2 is removed. Faithful reading: LRG2 supplies the *strength* of the BAO-leg preference (2.4σ → 1.6σ on removal), but the preferred *location* of the crossing (z ≈ 0.48) is a distributed property of the remaining BAO+CMB geometry, not an LRG2 artifact. This point counts AGAINST the "two unrelated systematics" reading for the crossing location, while leaving the strength localization intact. Meanwhile the BAO-vs-SN location split (0.48 vs 0.30) persists at low significance. Net: the overall H-X verdict remains INTERMEDIATE; within it, this follow-up moves the needle modestly toward "a common weak feature in BAO geometry + a separate mild SN feature" and away from "everything is LRG2."


---

## REGISTERED HYPOTHESIS H-Y (2026-07-20, registered BEFORE running)

**H-Y:** If the supernova legs' shared z× ≈ 0.30 crossing feature is driven by the low-z calibration seam, then marginalizing the Efstathiou intercept (free magnitude offset on the DES5Y external low-z sample) should destroy or radically broaden the DES5Y crossing preference. If the crossing survives intercept marginalization at z× ≈ 0.30, the SN feature is NOT the low-z seam.

**Test:** P3' = DES5Y + cCMB + BBN posterior with BOTH the global offset M and the low-z intercept D analytically marginalized. Compare z× distribution and wₐ to P3.

**Kill conditions (pre-committed):**
- z× fraction-defined drops below ~50% or the wₐ 68% interval includes 0 → the SN crossing is degenerate with the calibration seam → **systematics reading gains materially** (the SN leg's "agreement" with Pantheon+ would then be suspect as a shared low-z calibration artifact).
- z× ≈ 0.30 persists (68% interval overlapping [0.24, 0.40]) with wₐ excluding 0 at 68% → the SN feature survives its leading systematic explanation → **physics reading gains materially**.
- Otherwise → intermediate, reported without promotion.
Caveat registered: Pantheon+ and DES5Y share low-z SNe and calibration heritage, so even a surviving feature could reflect a deeper shared systematic; and the intercept absorbs real cosmology too, biasing toward the "dissolves" outcome.


## H-Y RESULT (2026-07-20) — registered kill condition (a) MET: **the SN crossing is degenerate with the calibration seam**

DES5Y + cCMB + BBN with the low-z intercept marginalized: w₀ = −1.165 [−1.317, −0.949] (now straddling the cosmological constant), **wₐ = +0.50 [−0.33, +1.03] — the 68% interval includes 0**, and the median even flips sign (from −0.80 to +0.50). The z× ≈ 0.30 crossing preference does not survive; what remains is direction-ambiguous wobble.

Verdict per pre-commitment: **the systematics reading gains materially.** The DES5Y evolution feature — and by the registered implication, the suspicious near-perfect DES5Y–Pantheon+ agreement at z× ≈ 0.30 — is fully degenerate with a single low-z calibration offset, and the two compilations share low-z supernovae and calibration heritage, making a common artifact plausible.

Registered caveat, carried in full: the intercept can absorb real cosmology as well as calibration error, so this test establishes *degeneracy*, not *cause*. What it proves is precise and damning enough: the supernova leg of the evolving-dark-energy case cannot distinguish "the universe bent at z ≈ 0.3" from "two telescope samples are mis-stitched by 3.6%." Only externally calibrated supernovae (Rubin) break the degeneracy.

## FINAL STATE OF THE REGISTERED CHAIN
H-X: INTERMEDIATE → follow-up: BAO crossing location is distributed (not LRG2's artifact) → H-Y: SN crossing is calibration-degenerate. Net anatomy: one weak-but-distributed BAO-geometry feature (z× ≈ 0.48, ~1.4–1.6σ on its own), amplified by one uncorroborated measurement (LRG2), joined to one calibration-degenerate supernova feature. All three layers now have registered, quantified status.
