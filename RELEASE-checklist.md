# Release Checklist — Dark-Energy Stress Lab

## 1. Repo (30 min, do first)
- [ ] Create public GitHub repo `de-stress-lab` (your account).
- [ ] Copy in: `whitepaper.md`, `README.md`, `RESULTS_MANIFEST.json`, `scripts/`, `results/`, `tests/`, `cleanroom/`, and `RELEASE-checklist.md`.
- [ ] Do NOT commit `data/` raw files (Pantheon+ cov is 33MB; DES npz 6MB) — instead add `data/DOWNLOAD.md` with the curl commands (they're in the scripts' headers and session history). Keeps the repo light and forces provenance.
- [ ] Do NOT commit `venv/`. Add `.gitignore`: `venv/`, `data/*.cov`, `data/*.npz`, `data/*.html`, `data/*.dat`, `data/*.csv`.
- [ ] Add `LICENSE` (MIT for code) and note data licenses belong to the surveys.
- [ ] Tag `v1.0`.

## 2. Sanity pass before sharing (1 evening)
- [ ] Give the exact commit to an independent human verifier and have them complete `cleanroom/VERIFIER_WORKSHEET.md` before opening expected results.
- [ ] Re-run `fit_w0wa.py` and `lrg2_audit.py` from a fresh clone following `data/DOWNLOAD.md`.
- [x] Run 5,000 ΛCDM mocks with all seven tracer deletions selected inside every mock; reconcile the manuscript and manifest.
- [ ] Read REPORT.md once aloud. Fix anything you can't defend in your own words — you will be asked.
- [ ] Optional but high-value: have one more external AI adversarial pass on REPORT.md specifically.

## 3. Share (in this order)
1. **Blog/long-form post** linking the repo (Substack/personal site). Title suggestion: "I reproduced the biggest claim in cosmology on a laptop. Then I tried to break it." Lead with the eBOSS swap test.
2. **CosmoCoffee** (cosmocoffee.info) — the professional cosmology forum; post in arXiv discussions referencing the DR2 paper. Frame: independent reproduction + influence diagnostics, seeking criticism.
3. **r/cosmology + r/Physics** — link post; expect and welcome skepticism.
4. **Direct emails (3–5, short, specific):** authors whose results you engaged — e.g., an Efstathiou-side and a DES-side author, and a DESI BAO member. One paragraph: what you did, the eBOSS swap number, link, "corrections welcome." These are also your future arXiv endorsers.
5. **X/Bluesky** thread only after 1–4 (the technical audience there follows the forums).

## 4. arXiv (when ready, not urgent)
- [ ] Target: astro-ph.CO. Needs endorsement — ask a responsive contact from step 3.4 after they've engaged with the work.
- [ ] Convert REPORT.md → LaTeX (AI does this in one pass) with proper citations (all arXiv IDs already inline).

## 5. Rules of engagement (pin this)
- Every critique gets logged in the README audit trail, answered or adopted.
- Never claim more than "reproducible, localized 2–3σ hint"; the selected-null result shows localization is not independent evidence beyond the global fluctuation.
- If someone shows an error: fix, credit, update the repo, say so publicly. The audit trail IS the credibility.
- The report pre-commits to updating against the 2027 outcomes — calendar it.

## Completed after the original checklist

- [x] Full-CMB lensing-inclusive variant (PR3-native comparison stack).
- [x] 5,000-mock global significance calibration.
- [x] Selection-calibrated maximum-influence analysis.
- [x] Clean-room verifier package and pinned execution instructions.

## Still outstanding

- [ ] Human clean-room execution and signed worksheet.
- [ ] Official-likelihood LRG2 reconstruction.
- [ ] Regenerate PDF/DOCX release artifacts from the reconciled `whitepaper.md`.
