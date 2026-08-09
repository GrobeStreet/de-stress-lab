# Prepared arXiv package

This directory contains a validated source archive and submission metadata. It does not represent an arXiv submission.

Build and validate from the repository root:

```bash
python3 scripts/audit_manuscript_claims.py
python3 scripts/build_preprint.py
python3 scripts/build_arxiv_package.py
```

`arxiv-source.zip` contains only the self-contained top-level `manuscript.tex`. The packaging script rejects unsupported file names, compiles the isolated source in a temporary directory, checks the archive membership, and writes `SHA256SUMS`.

Before upload, the author must resolve the ORCID, license, and endorsement gates in `METADATA.md`. After arXiv compiles the upload, compare its processed PDF with `preprint/manuscript.pdf` and inspect every page before submission.
