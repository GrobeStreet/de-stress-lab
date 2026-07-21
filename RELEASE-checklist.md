# Release Checklist — Dark-Energy Stress Lab

## 1. Repo (30 min, do first)
- [ ] Create public GitHub repo `de-stress-lab` (your account).
- [ ] Copy in: `REPORT.md`, `README.md`, `scripts/`, `results/`, `RELEASE-checklist.md` (this file, optional).
- [ ] Do NOT commit `data/` raw files (Pantheon+ cov is 33MB; DES npz 6MB) — instead add `data/DOWNLOAD.md` with the curl commands (they're in the scripts' headers and session history). Keeps the repo light and forces provenance.
- [ ] Do NOT commit `venv/`. Add `.gitignore`: `venv/`, `data/*.cov`, `data/*.npz`, `data/*.html`, `data/*.dat`, `data/*.csv`.
- [ ] Add `LICENSE` (MIT for code) and note data licenses belong to the surveys.
- [ ] Tag `v1.0`.

## 2. Sanity pass before sharing (1 evening)
- [ ] Re-run `fit_w0wa.py` and `lrg2_audit.py` from a fresh clone following your own DOWNLOAD.md — the reproduce-from-scratch test.
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
- Never claim more than "reproducible, sharply localized 2–3σ hint."
- If someone shows an error: fix, credit, update the repo, say so publicly. The audit trail IS the credibility.
- The report pre-commits to updating against the 2027 outcomes — calendar it.

## While it circulates → Expedition 2
Full-CMB lensing leg (Planck PR4 + lensing via cobaya on the Mac): the "does 3.1σ survive without LRG2" run — the question this release will make people want answered.
