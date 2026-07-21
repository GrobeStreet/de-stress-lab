# Dark-Energy Stress Lab
### Project B v2 — an independent compressed-likelihood implementation and stress test of the DESI evolving-dark-energy claim

**Scope statement (audit-reconciled):** this lab independently *reimplements the published compressed likelihoods* (DESI DR2 BAO summaries, Pantheon+/DES5Y distances, the DR2 compressed early-CMB prior) and reproduces their maximum-likelihood w0wa improvements. It is NOT a raw-data reanalysis, does not reproduce the full-CMB 3.1sigma or the 3.8-4.2sigma SN headline rows, and reproduces best fits, not posteriors. Externally reviewed by four independent AI systems (software/statistics/manuscript checks, not independent scientific peer review); one re-ran the pipeline and matched all chi2 values to 4 decimals. A clean-room human rerun is the outstanding verification step.

**Status (2026-07-19): reproduction phase complete; diagnostics complete; verdict below.**

| Run | This pipeline | Published | Source |
|---|---|---|---|
| DESI DR2 BAO alone, flat ΛCDM | Ωm = 0.2973 ± 0.0083 | Ωm = 0.2975 ± 0.0086 | arXiv:2503.14738 |
| " | h·rd = 101.55 ± 0.72 Mpc | 101.54 ± 0.73 Mpc | " |
| Pantheon+ SNe alone (z>0.01, no calibrators, full STAT+SYS cov) | Ωm = 0.3326 ± 0.0180 | Ωm = 0.334 ± 0.018 | arXiv:2202.04077 |

**The physics already visible:** BAO prefers Ωm ≈ 0.297; supernovae prefer Ωm ≈ 0.333. Within ΛCDM these should agree. That ~2σ mismatch between expansion-history probes is a seed of the w₀wₐ preference — the "evolving dark energy" fit is, in part, the model bending to reconcile these two numbers. Whether that reconciliation reflects physics or calibration is what this lab exists to test.

## Provenance rules (non-negotiable)
1. No number enters the pipeline from memory. BAO values were machine-extracted from the arXiv HTML of the DR2 paper; SN data downloaded from the official PantheonPlusSH0ES release.
2. No interpretation until reproduction matches published results (PASSED for BAO-alone, SN-alone, and the w₀wₐ ladder rows −4.7/−4.9/−8.0; NOT attempted for full-CMB rows — out of scope).
3. Both the baseline analysis and published critiques get implemented as switchable pipeline options.
4. Results publish regardless of which way they point.

## Layout
```
data/      pantheon_plus.dat + cov, des_dovekie_hd.csv + npz (official releases), desi_dr2.html (BAO/CMB source)
scripts/   fit_lcdm.py (wk1 reproductions) · fit_w0wa.py (w0wa + calibrated-surrogate CMB, validation gates)
           influence.py (LOO/pulls/SN cuts) · fit_des5y.py (DES5Y + intercept test)
           ccmb_ext.py (anchored intercept + w(z) swap) · null_mocks.py (parametric bootstrap)
           camb_check.py (exact-Boltzmann swap — REQUIRES local CAMB; sandbox CPU unsupported)
results/   *.json per analysis
```

## Documented simplifications (v0)
- Gaussian likelihood on published BAO summary values (this mirrors the official compressed likelihood; full-shape comes later).
- (superseded — later scripts include radiation in E(z); early-universe module is a *calibrated surrogate*, see fit_w0wa.py header)
- SN target value (0.334 ± 0.018) taken from Brout et al. abstract; re-verify exact cut definitions against their §4 before treating small differences as meaningful.

## Week 2–4 results: the w₀wₐ preference REPRODUCED (2026-07-19)

Compressed-CMB likelihood implemented from the DR2 paper's own eqs. 35–36 (Gaussian in θ*, ωb, ωbc; CamSpec-based). Validation gates: G1 — pivot-calibrated sound-horizon integral matches the paper's rd formula to 0.17% across a parameter grid; G2 — ΛCDM DESI+BBN+θ* reproduces the published Ωm=0.2967±0.0045, H0=68.45±0.47 (we get 0.2976, 68.37). Two bugs were caught **by the gates** before any dark-energy fit ran (an ωbc bookkeeping error and a recombination-calibration offset) — the stop/go protocol working as designed.

| Fit (w₀wₐCDM vs ΛCDM) | Δχ² (this lab) | Δχ² (published) | σ (this lab / published) |
|---|---|---|---|
| DESI BAO alone | **−4.7** | −4.7 | 1.7 / 1.7 |
| DESI + Pantheon+ | **−5.1** | −4.9 | 1.8 / 1.7 |
| DESI + compressed CMB | **−8.5** | −8.0 | 2.4 / 2.4 |

Best-fit parameters also land on the published values: DESI+SN w₀=−0.886 (pub −0.888), DESI+cCMB w₀=−0.44, Ωm=0.352, H0=63.6 (pub −0.42/−0.43, 0.353, 63.6). Run: `python3 scripts/fit_w0wa.py data` (~7 s).

**What this means:** the DR2 evolving-dark-energy preference is independently reproduced from primary-source inputs on a laptop — for the BAO, BAO+SN, and BAO+compressed-CMB legs. The paper's own table shows the climb to 3.1σ requires full CMB information (mostly lensing), and to 3.8–4.2σ requires Union3/DESY5 supernovae — neither yet in this pipeline.

## Week 4–6 results: INFLUENCE DIAGNOSTICS (2026-07-19) — the novel analysis

**Probe 1 — leave-one-tracer-out (DESI+cCMB, 2.4σ baseline):**

| Dropped tracer | Δχ² | σ | |
|---|---|---|---|
| none (full) | −8.5 | 2.4 | |
| BGS z=0.295 | −9.0 | 2.5 | signal strengthens |
| LRG1 z=0.510 | −7.9 | 2.3 | |
| **LRG2 z=0.706** | **−4.3** | **1.6** | **preference collapses** |
| LRG3+ELG1 z=0.934 | −8.3 | 2.4 | |
| ELG2 z=1.321 | −8.1 | 2.4 | |
| QSO z=1.484 | −8.5 | 2.4 | |
| Lya z=2.330 | −9.6 | 2.6 | signal strengthens |

**Probe 2 — χ² improvement decomposition (w₀wₐ vs ΛCDM at respective best fits):** LRG2 −4.1, CMB anchor −3.9, LRG1 −1.2, all others ≈ 0, Lyα **+1.0** (fits *worse* under evolving dark energy).

**Probe 3 — SN low-z cut sweep (DESI+Pantheon+):** σ falls monotonically 1.8 → 1.6 → 1.4 → 1.3 as z_min goes 0.01 → 0.025 → 0.05 → 0.10, while w₀ stays pinned at ≈ −0.89 throughout. The *crossing* component (wₐ) is what the nearby supernovae supply.

**Reading (calibrated, not triumphant):** in this pipeline the evolving-dark-energy preference concentrates in three places — one BAO measurement (LRG2, z=0.706), the lowest-redshift supernovae, and the CMB geometric anchor's mild Ωm tension with BAO. This is *consistent with both* interpretations: genuine late-time dark-energy dynamics would look like this, and so would one ~2σ-fluctuating data point plus low-z SN calibration effects. Caveats: dropping the most influential point of any ~2–3σ signal deflates it by construction (look-elsewhere applies); DESI's own robustness checks found no instrumental issue with LRG2; and this pipeline lacks full-CMB lensing and DESY5/Union3, which supply the climb above 3σ. What the diagnostics establish is the signal's *concentration*, which is exactly what decides how much one should believe it before the 2027 data.

## Week 6 results: DES5Y + THE EFSTATHIOU TEST (2026-07-19)

Data: official DES-SN5YR repo, 2025 **Dovekie-recalibrated** release (N=1820; inverse covariance unpacked per the repo's own likelihood code; external low-z sample identified by IDSURVEY≠10, N=197, z≤0.087).

| Test (DESI BAO + DES5Y, no CMB) | Δχ²(w₀wₐ−Λ) | σ | w₀ / wₐ |
|---|---|---|---|
| A. Baseline | −7.3 | 2.2 | −0.84 / −0.54 |
| B. + free low-z intercept D (1 nuisance) | **−0.4** | **0.2** | −0.99 / +0.12 |
| C. Drop external sample entirely (z>0.1) | −0.6 | 0.3 | −0.99 / +0.20 |

Published no-CMB row (2024 release): Δχ² = −13.6, 3.3σ. Two findings:

**F1 — The Dovekie recalibration itself appears to have weakened the DES5Y evidence** (−13.6 → −7.3 in this pipeline; machinery validated on Pantheon+ at −5.1 vs published −4.9). Part of the gap could be pipeline simplifications, but the SN-leg machinery is the same one that reproduced Pantheon+.

**F2 — The intercept test reproduces Efstathiou's critique on the newer data:** freeing ONE magnitude offset on the 197 external low-z SNe returns a fitted D ≈ **+0.037 mag** under ΛCDM — nearly identical to the ~0.04 mag Efstathiou inferred — and the evolving-dark-energy preference collapses to 0.2σ with w₀ = −0.99: ΛCDM restored to within noise. One calibration nuisance parameter explains the DES5Y contribution as effectively as two dark-energy parameters.

**Counter-arguments, documented:** the DES team maintains cross-survey calibration systematics are already in the covariance (freeing D may double-count); the offset test is a post-hoc choice motivated by a critic; and this combo omits the CMB leg (published 4.2σ row includes full CMB).

## Week 7 results: CMB-ANCHORED INTERCEPT + PARAMETERIZATION SWAP (2026-07-19)

**Anchored intercept test (DESI + cCMB + DES5Y):** baseline Δχ² = −10.9 (**2.9σ** — our compressed-CMB analog of the published 4.2σ row). Adding the single low-z intercept: Δχ² = −3.2 (**1.3σ**), fitted D = +0.0355 mag. Even with the CMB anchor, the calibration nuisance strips out the supernova contribution; the surviving ~1.3σ is the BAO+CMB geometry piece (which our LOO showed is itself concentrated in LRG2).

**w(z) parameterization swap** (all families reduce to Λ at w₀=−1, wₐ=0):

| Combo | CPL | JBP | LOG | wCDM (1 dof) |
|---|---|---|---|---|
| DESI+cCMB | 2.4σ | 2.1σ | 2.4σ | **0.8σ** |
| DESI+cCMB+DES5Y | 2.9σ | 2.6σ | 2.9σ | **1.2σ** |

Two conclusions cut opposite ways. *For* the DESI claim: the preference is **not** a CPL artifact — all two-parameter evolving families find it at nearly equal strength. *Against* over-interpretation: constant-w captures almost none of it — the evidence lives entirely in the second degree of freedom (time variation/crossing), best-fit parameters are family-unstable (JBP wants w₀=+0.09, wₐ=−5.4), and that crossing is precisely the component our diagnostics localized to LRG2 and the low-z supernova calibration seam.

**Consolidated lab verdict (honest form):** a real, parameterization-robust ~2–3σ preference for *late-time evolution* exists in the anchored data; its observational support is concentrated in one BAO tracer and the low-z SN calibration; one ~0.036 mag calibration offset — matching both Efstathiou's inference and the direction of the Dovekie recalibration — reduces it to noise-compatible levels. Probability mass should sit between "small real dynamical effect" and "two stacked systematics," with the 2027 DESI final likelihood and Rubin-calibrated SNe as the decider.

## Next
Public write-up (notebook + report), per the publish-regardless rule.


---

## FINAL SECTION — External audits, bootstrap, and consolidated verdict (2026-07-19)

**Cross-AI verification.** Three independent AI systems audited this lab. One re-executed the pipeline and confirmed every χ² to 4 decimals, verified the minima against differential evolution and varied starts (not a local-minimum accident), confirmed distance-grid accuracy at 3×10⁻⁷, and verified the covariance is positive definite. Its corrections are adopted: the early-universe module is labeled a **calibrated surrogate** (rd correction 2.32%, θ* anchor 0.125%; G2 partially circular), the "independent reproduction" claim is narrowed to "independent compressed-likelihood implementation," and DESI's early-matter condition (w₀+wₐ<0; satisfied by all reported best fits) is documented.

**Anchor-uncertainty propagation:** varying the surrogate's θ* anchor by ±1σ of the *published* anchor uncertainty (H₀ = 67.14 ± 0.47) moves the baseline between Δχ² = −6.1 and −11.1 → the surrogate pins significance to **2.4σ ± ~0.5σ**. Exact CLASS/CAMB required to do better (`camb_check.py` ready; blocked in this sandbox by CPU instruction set — run locally).

**Parametric bootstrap (75 ΛCDM mocks through the full pipeline):** empirical P(Δχ² ≤ −8.46 | ΛCDM) = 0.013 vs Wilks 0.0146 — **the 2.45σ label is honest; no pipeline significance inflation.** One mock ΛCDM universe exceeded the real data's preference.

**Cross-AI extensions adopted into the record:** LRG2's leverage is primarily its *radial* D_H/r_d measurement (Δχ² −6.5 with radial only vs −4.9 transverse only vs −4.3 neither); LRG2 sits ~2.36σ from the joint ΛCDM prediction (unusual, not outrageous); shifting LRG2 halfway to ΛCDM (a 1.18σ move in its own covariance) drops the preference below 2σ; error-inflation degrades the signal smoothly (not a numerical pathology).

**Literature balance (added per audit):** DES's rebuttal ([Vincenzi et al., arXiv:2501.06664](https://arxiv.org/abs/2501.06664)) reproduces the Efstathiou offset but attributes much of it to improved intrinsic-scatter/host modeling — reverting assumptions lowers their result 3.9σ→3.3σ rather than eliminating it. [Cortês & Liddle (arXiv:2504.15336)](https://arxiv.org/abs/2504.15336): overlapping SN significances must not be averaged; DESI+CMB 3.1σ is the safest single summary. [Afroz & Mukherjee (PRD, arXiv:2504.16868)](https://arxiv.org/abs/2504.16868): a redshift-dependent Pantheon+–DESI inconsistency; ΛCDM-compatible once modeled.

**Consolidated verdict (three AI systems, one human, convergent):** a real, reproducible, parameterization-robust likelihood-level tension exists (~2.4σ compressed / 3.1σ full-CMB per DESI); it is sharply localized (LRG2 radial BAO + CMB anchor + low-z SN calibration); the Efstathiou intercept (D≈+0.036 mag) neutralizes the SN contribution even CMB-anchored, while DES's rebuttal keeps that contested; the constant-w model captures none of it (evidence is specifically for *time variation*); and the honest status is **a reproducible, sharply localized 2–3σ hint — not proof**. Calibrated odds that the ultimate explanation is genuinely new physics rather than calibration/systematics: ~25–40% for signal survival, <~30% for new physics. Deciders: official LRG2 likelihood-level audit, exact-Boltzmann full-CMB decomposition (lensing leg), DESI 2027 final likelihood, Rubin-calibrated SNe.

**Remaining evidentiary gates (in order):** LRG2 official-likelihood audit → CLASS/CAMB swap (script ready) → posterior sampling with DESI priors + DIC → full-CMB with lensing decomposition → official Union3/DES5Y likelihoods (never averaging overlapping SN significances) → growth/lensing (RSD, fσ8, E_G) to separate dark energy from modified gravity at matched H(z).


---

## GATE 1 RESULT — THE LRG2 AUDIT, public-data version (2026-07-19)

The z≈0.7 BAO measurement across three analyses, tested in the DESI+cCMB frame (all values primary-sourced: eBOSS from the official SDSS DR16 consensus files in the cobaya bao_data release; DR1 from arXiv:2404.03002; DR2 from arXiv:2503.14738):

**T1 — distance from the ΛCDM best-fit prediction:**

| Measurement | joint | D_M pull | D_H pull |
|---|---|---|---|
| eBOSS DR16 (z=0.698, independent) | **0.83σ** | +1.28σ | −0.70σ |
| DESI DR1 (z=0.706) | 1.40σ | **−1.78σ** | +0.13σ |
| DESI DR2 (z=0.706) | 1.51σ | −0.39σ | **−1.66σ** |

The z≈0.7 deviation has **changed observable between DESI's own releases** — DR1's pull was transverse (D_M low), DR2's is radial (D_H low) — and the independent eBOSS measurement shows neither (slightly ΛCDM-high in D_M, if anything).

**T2/T3 — swap test (DESI+cCMB, the z≈0.7 slot filled by each):**

| z≈0.7 slot | Δχ² | σ |
|---|---|---|
| DESI DR2 (baseline) | −8.5 | 2.4 |
| **eBOSS DR16 (independent)** | **−4.3** | **1.6** |
| DESI DR1 | −5.9 | 1.9 |
| dropped entirely | −4.3 | 1.6 |

**Finding:** substituting the independent eBOSS measurement yields *exactly* the same preference as having no z≈0.7 measurement at all — eBOSS's deviation pattern has essentially zero projection onto the w₀wₐ direction. The entire lift from 1.6σ to 2.4σ is supplied by DR2's LRG2 specifically.

**Balanced reading:** DR2's LRG2 is by far the most precise of the three (±0.177 vs ±0.30/±0.32 on D_M) — more data can legitimately resolve what noisier data could not, DESI's blinded internal-consistency checks passed, and eBOSS's weaker precision means it *couldn't* strongly confirm the signal even if real. But the audit establishes two facts the discovery narrative must carry: the z≈0.7 anomaly's observable signature is unstable across DESI's own releases (transverse → radial), and the only independent experiment at this redshift is ΛCDM-consistent. The official-likelihood-level LRG2 reproduction (Gate 1's full form) remains the decisive test — this is the strongest public-data evidence available for prioritizing it.


---

## GATE 2 RESULT — EXACT BOLTZMANN PHYSICS (CAMB, run on Bobby's Mac, 2026-07-20)

The calibrated surrogate's two empirical constants — the audits' primary criticism — are now replaced with CAMB (full RECFAST recombination, exact r_drag/θ*, w0wa-PPF background), executed on local hardware (homebrew Python 3.13 venv; sandbox CPU could not run CAMB's binary).

| Fit (DESI+cCMB) | Δχ² exact-CAMB | Δχ² surrogate | σ exact / surrogate |
|---|---|---|---|
| w₀wₐ vs ΛCDM, baseline | **−8.28** | −8.46 | 2.41 / 2.45 |
| w₀wₐ vs ΛCDM, without LRG2 | **−4.14** | −4.33 | 1.53 / 1.58 |

Best-fit parameters agree to the third decimal (exact: w₀=−0.447, wₐ=−1.64, Ωm=0.351, H0=63.7; surrogate: −0.44, −1.68, 0.352, 63.6). CAMB-vs-surrogate at the best fits: rd differs by 0.12%, θ* by 0.035% — and the fits absorb these into slightly shifted (h, ωb), leaving Δχ² essentially unchanged.

**Conclusions.** (1) The calibrated surrogate was accurate: every headline number of this lab survives exact early-universe physics to within ~0.2 in Δχ² (~0.03σ). (2) **The LRG2 localization is confirmed at the Boltzmann level**: removing LRG2 still collapses the exact-physics preference from 2.4σ to 1.5σ. (3) The audits' surrogate objection is resolved empirically, not rhetorically. Remaining ladder: posterior sampling with DESI priors (+DIC), full-CMB lensing leg, official likelihoods — then the write-up.


---

## GATE 3 RESULT — POSTERIOR INFERENCE + DIC (emcee on Bobby's Mac, 2026-07-20)

Full MCMC under DESI's official priors (w₀∈U[−3,1], wₐ∈U[−3,2], w₀+wₐ<0, verbatim from the paper), 80k samples, CAMB-validated surrogate likelihood.

| Quantity | This lab (posterior) | Published (DESI+CMB) |
|---|---|---|
| w₀ | −0.45 +0.24/−0.23 | −0.42 ± 0.21 |
| wₐ | −1.66 +0.65/−0.71 | −1.75 ± 0.58 |
| w₀–wₐ correlation | **−0.978** | −0.975 (paper eq. 21) |
| ΔDIC (MAP plug-in) | **−4.96** (pD = 4.75/3.0 — sane) | −4.4 |
| ΛCDM Ωm, H0 | 0.3013 ± 0.0036, 68.25 | 0.2967–0.3005 band |
| Posterior mass near w₀+wₐ boundary | 0.000 | (paper notes prior cutoff for BAO-alone; none here) |

DIC convention note: naive plug-in at the posterior *mean* gives ΔDIC = −8.99 — an artifact of the strongly curved w₀–wₐ ridge (mean sits off-ridge). With the standard MAP plug-in, effective parameter counts come out exactly right (4.75 for 5 params, 3.0 for 3) and ΔDIC = −4.96, matching the published −4.4 to the same offset as our Δχ². **The audit's "best fits, not posteriors" objection is now closed**: intervals, contours (chain released), correlation structure, and information criteria all reproduce.

**Ladder status:** reproduction ✓ · diagnostics ✓ · calibration tests ✓ · parameterization ✓ · bootstrap ✓ · LRG2 audit ✓ · exact physics ✓ · posteriors+DIC ✓. Remaining beyond current resources: full-CMB lensing leg and official uncompressed likelihoods. → REPORT-draft.md is the write-up.


---

## AUDIT 4 ADOPTED (2026-07-20) — eight corrections, all accepted

A fourth external review (13-page document) was received and adopted in full: (1) eBOSS reframed as a partially correlated comparator, not an independent non-confirmation (DESI/SDSS sample+footprint overlap); (2) the 75-mock bootstrap relabeled as a consistency check (1/75 ⇒ 95% CI 0.03–7.2%) — a 5,000-mock calibration run is queued; (3) the two LRG2 sigmas (global preference vs single-measurement deviation) now explicitly defined with reference fit; (4) "exact CAMB"→"full CAMB Boltzmann," "independent hardware"→"separate execution environment," AI reviews relabeled as software/manuscript checks with a clean-room human rerun as the outstanding verification; (5) Dovekie framed as a multi-element release change, attribution unestablished (cf. arXiv:2511.07517); (6) the low-z intercept explicitly labeled a sensitivity test that cannot distinguish calibration from cosmology; (7) full-CMB claims kept outside the report boundary until the in-progress lensing-leg run completes (PR3-native likelihoods; comparison caveat pre-documented); (8) repository freeze with one-command reproduction confirmed as release step 1. The audit's bottom-line framing is adopted as the project's: **lead with the influence/fragility map — where the DESI preference lives and how fragile it is — not with "evolving dark energy."**


---

## EXPEDITION 2 RESULT — THE FULL-CMB LENSING LEG (2026-07-20)

Cobaya + CAMB on local hardware: Planck 2018 native likelihoods (low-ℓ TT, low-ℓ EE, plik-lite TTTEEE, **lensing**) + DESI DR2 BAO, MAP minimization (BOBYQA, dual runs converged), DESI official w(z) priors. Comparison caveat pre-registered: DESI DR2 used PR4 CamSpec + PR4/ACT lensing; this uses the 2018 (PR3) native equivalents — expect the same qualitative lensing lift, not identical numbers. Prior-volume constants (2·log 20) removed to convert posterior minima to likelihood Δχ².

| Full CMB (incl. lensing) + DESI BAO | Δχ²(w₀wₐ−Λ) | σ (2-dof Wilks) |
|---|---|---|
| with LRG2 | **-10.35** | **2.77** |
| without LRG2 | **-3.76** | **1.43** |

Published full-CMB row (PR4): −12.5, 3.1σ — our −10.4 / 2.8σ with the PR3-native stack is in the expected range given the likelihood-generation difference.

**THE ANSWER TO THE PROJECT'S CENTRAL OPEN QUESTION: the CMB-lensing information does not rescue the preference from LRG2 removal.** With full CMB including lensing, dropping the single z=0.706 measurement collapses the evolving-dark-energy preference from ~2.8σ to ~1.4σ — the sharpest form of the localization result, now demonstrated at the full-likelihood level rather than the compressed level. Caveats: PR3-native vs PR4 likelihoods; MAP (not posterior) comparison; single-pipeline result awaiting the clean-room rerun; LRG2 removal carries the usual look-elsewhere qualifier.


---

## H-X CROSS-PROBE TEST RESULT + 5000-MOCK CALIBRATION (2026-07-20)

**Mock calibration (audit item 2 CLOSED):** 5,000 ΛCDM mocks through the full pipeline: P(Δχ² ≤ −8.46) = 0.0150 [95% CI 0.0119–0.0187] vs Wilks 0.0146. The significance labels are now *calibrated*, not merely consistent. Distribution extreme: one mock at Δχ² = −17.5 (~3.7σ-equivalent) — pure-ΛCDM universes do occasionally produce stronger "evolving dark energy" than the real data.

**H-X (pre-registered cross-probe w(z) consistency): verdict INTERMEDIATE, per kill conditions.** BAO–Pantheon+ shift 1.44σ, BAO–DES5Y 1.35σ, Pantheon+–DES5Y 0.24σ. Crossing redshifts: BAO z× = 0.49 ± 0.07; both SN legs z× ≈ 0.29–0.30. Neither the consistency nor the inconsistency threshold was met; reported without promotion. Notable texture (not promoted): the two supernova datasets agree with each other almost exactly and both point at a *different* turning point than the BAO leg, despite a shared CMB anchor pulling all legs together. Registered follow-up: P1-without-LRG2 z× test. Full record: HYPOTHESIS-cross-probe.md, results/hx_tension.json, results/probe_posteriors.json.


**H-X registered follow-up (2026-07-20):** P1 without LRG2 gives z× = 0.478 [0.384–0.564] — the BAO leg's crossing-location preference does NOT dissolve when LRG2 is removed (registered condition not met). LRG2 carries the *significance* of the BAO preference, but the crossing *location* is a distributed property of BAO+CMB geometry. Reported per registration; overall H-X verdict remains INTERMEDIATE.


**H-Y RESULT (2026-07-20):** registered kill condition MET. DES5Y+cCMB with the low-z intercept marginalized: wₐ = +0.50 [−0.33, +1.03] (includes 0, sign flips), w₀ → −1.17 (straddles Λ). The SN crossing feature is fully degenerate with the calibration seam. Registered caveat carried: degeneracy established, cause not — the intercept can absorb real cosmology. Chain complete: HYPOTHESIS-cross-probe.md holds the full registered record.
