# Preprint package

`manuscript.tex` and `manuscript.pdf` are generated from the evidence-reconciled `whitepaper.md` by:

```bash
python3 scripts/audit_manuscript_claims.py
python3 scripts/build_preprint.py
```

The source uses REVTeX 4.2 with the APS/Physical Review D preprint options. The package is prepared for review and arXiv upload, but it has not been submitted. Before public submission the author must confirm affiliation wording, ORCID choice, category/endorsement, license, and metadata.

The DDM expansion from the 2026-07-28 historical manuscript is intentionally excluded because its supporting public artifacts are not present in this repository or the results manifest.
