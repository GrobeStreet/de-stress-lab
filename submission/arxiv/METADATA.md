# arXiv submission metadata

Status: prepared, not submitted. Verified 2026-08-13 against the manuscript, repository, author identity, and current official arXiv guidance.

## Frozen fields

- Manuscript title: **Anatomy of a 2–3σ Hint**
- arXiv web-form title (ASCII/TeX): **Anatomy of a 2--3$\sigma$ Hint**
- Author: **Robert Morong**
- Affiliation in manuscript: **Independent researcher, San Diego, California, USA**
- Affiliation in arXiv account: **Unaffiliated**
- Contact email: **bobby@trainingties.com**
- Primary category: **astro-ph.CO**
- Cross-lists: **None recommended for v1**
- Journal reference: **Leave blank before acceptance**
- Article DOI: **Leave blank before assignment**. The Zenodo scientific-archive DOI is a related artifact, not an article DOI for this field.
- Report number: **None**
- Prepared license recommendation: **CC BY 4.0**; final selection remains an author decision and is irrevocable for that version once submitted.
- Comments: **REVTeX manuscript; code, released results, and verification materials: https://github.com/GrobeStreet/de-stress-lab; scientific archive: https://doi.org/10.5281/zenodo.21632602**
- Abstract: use the exact contents of `preprint/ABSTRACT.md`; it is below arXiv's 1,920-character limit.

## Author confirmation gates

- ORCID: **recommended, currently unlinked; not required for submission**. Link an existing ORCID or create one through the signed-in arXiv account if desired before submission so the record is connected unambiguously to the author.
- License: **CC BY 4.0 is the prepared recommendation, not an already-active choice**. Confirm compatibility with any intended journal/funder requirement before selecting it in arXiv; arXiv states the selected license cannot be changed for that version.
- Account category: **previously observed as available** with `astro-ph.CO` as the default category; re-confirm in the live account at submission time.
- Endorsement: **live-account decision required**. arXiv requires endorsement for a first submission or a new category; the submission workflow will display whether this account needs it.
- Submittal Agreement: **author acceptance required** in the live arXiv workflow.
- Final author preview: verify title, abstract, author spelling, category, processed PDF, and source-file list before pressing **Submit Article**.

## Upload and compiler note

Upload `submission/arxiv/arxiv-source.zip`. It contains the self-contained top-level `manuscript.tex`.

arXiv currently supports TeX Live 2025 (default) and TeX Live 2023. This manuscript loads REVTeX 4.2 and `array`; official arXiv guidance documents a possible TeX Live 2025 issue involving `array`. If the default arXiv build fails for that compatibility reason, retry with TeX Live 2023 rather than altering scientific content.

## Scope note

The manuscript is a compressed-likelihood implementation and robustness audit, not a raw-data or native-survey-likelihood reanalysis. Independent human clean-room execution remains pending. The prepared package must not be described as peer reviewed or independently verified until review records support those statements.

## Official guidance checked

- Submission overview: https://info.arxiv.org/help/submit/index.html
- Metadata fields: https://info.arxiv.org/help/prep.html
- Endorsement: https://info.arxiv.org/help/endorsement.html
- ORCID: https://info.arxiv.org/help/orcid.html
- Licenses: https://info.arxiv.org/help/license/index.html
- TeX Live: https://info.arxiv.org/help/faq/texlive.html
