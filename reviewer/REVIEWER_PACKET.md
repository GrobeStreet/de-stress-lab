# DESI Evidence Review Packet
## Manuscript, reproduction, and verification guide

**Bobby Morong** · Independent researcher · Prepared 2026-08-09
*Draft package for independent review; no reviewer endorsement is claimed.*

---

## Review purpose

This packet supports independent evaluation of “Anatomy of a 2–3σ Hint,” an implementation and stress test of published DESI DR2 compressed likelihoods. The central question is whether the reported numerical results, statistical calibrations, and interpretation are internally correct and appropriately bounded.

The work is not a raw-data reanalysis, and an independent human clean-room execution remains pending. AI-assisted software and manuscript checks are disclosed but are not treated as scientific peer review.

## Requested review lanes

| Lane | Best-fit reviewer | Requested output |
|---|---|---|
| Numerical reproduction | Scientific software developer or computational cosmologist | Fresh-environment run record, hashes, mismatches, convergence notes |
| Statistical review | Statistician or cosmologist familiar with likelihood-ratio calibration | Assessment of null construction, selection conditioning, intervals, and interpretation |
| Domain review | BAO/CMB/SN cosmologist | Scope, data provenance, comparison framing, and missing native-likelihood checks |
| Manuscript review | Technical scientific editor or journal-experienced researcher | Errors, ambiguous claims, missing citations, and presentation recommendations |

## Headline evidence ledger

| Question | Released result | Interpretation boundary |
|---|---|---|
| Global CPL preference | Δχ² = −8.4575; 70/5,000 ΛCDM mocks, p = 0.0140 | A calibrated hint, not a discovery |
| Selected tracer influence | LRG2, M = 4.1249; 78/5,000, p = 0.0156 | Describes localization after selection |
| Conditional localization | 34/70, p = 0.486 | Localization is not independent extra evidence |
| Direct time variation | T = 7.8506; 30/5,000, p = 0.0060 | CPL-specific; not arbitrary time dependence |
| Direct test without LRG2 | T = 3.4263; 349/5,000, p = 0.0698 | Most strength is LRG2-sensitive |
| Held-out LRG2 | joint p = 0.0408; D_V p = 0.0204; D_M/D_H p = 0.3744 | Targeted diagnostic, not an independent discovery test |
| Full-CMB variant | Δχ² = −10.35 with LRG2; −3.76 without | PR3-native comparison stack, not DESI’s exact PR4/ACT stack |

## Reproduction sequence

1. Record the repository commit, platform, Python version, package versions, UTC start time, and clean Git status.
2. Follow `cleanroom/README.md` without reading expected result files.
3. Run the deterministic 20-mock smoke test twice and compare hashes.
4. Run the 5,000-mock flagship calibration and complete `cleanroom/VERIFIER_WORKSHEET.md` before opening the expected results.
5. Run the frontier package for the full/no-LRG2 direct tests and the held-out LRG2 diagnostic.
6. Report every mismatch, convergence failure, platform-dependent last-bit difference, changed input, or changed command.

## Files to inspect

| Item | Purpose |
|---|---|
| `preprint/manuscript.pdf` | Journal-style reading copy |
| `preprint/manuscript.tex` | REVTeX source |
| `paper/CLAIM_EVIDENCE_MATRIX.md` | Claim-to-artifact reconciliation |
| `RESULTS_MANIFEST.json` | Canonical completion states and hashes |
| `cleanroom/README.md` | Blind execution protocol |
| `cleanroom/VERIFIER_WORKSHEET.md` | Pre-comparison result record and attestation |
| `results/*.json` | Released numerical evidence |

## High-value review questions

- Is the global null generated and fitted consistently with the observed statistic?
- Is conditioning on global preference strength an appropriate way to prevent double-counting localization?
- Are the direct wCDM-versus-CPL mocks fitted at the correct observed constant-w null in each branch?
- Does the held-out LRG2 calculation propagate parameter uncertainty correctly, and is its targeted status stated strongly enough?
- Are the DES5Y offset results framed as degeneracy/sensitivity rather than diagnosis?
- Are PR3-native and compressed-CMB results clearly distinguished from DESI’s native PR4/ACT analysis?
- Are any manuscript claims stronger than the corresponding released artifact permits?

## Known limitations and deferred material

- No independent human clean-room execution has yet been received.
- The official/native LRG2 likelihood reconstruction is open.
- The scientific analysis implements published compressed likelihoods rather than raw catalog and survey-systematics pipelines.
- A later DDM manuscript expansion was removed from this package because its cited gate document, runner, outputs, and CLASS patch are absent from the repository and manifest.

## How to report

Please return a short signed record containing scope, environment, commit, commands, outputs/hashes, discrepancies, and an explicit statement of what was and was not independently checked. A successful rerun verifies execution of the released implementation; it does not by itself establish an independent clean-room reimplementation of the likelihood.
