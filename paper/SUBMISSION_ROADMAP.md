# Scholarly submission roadmap

This project has two distinct scholarly products. They should support one
another, but must not be represented as the same review.

## 1. Scientific manuscript

The scientific manuscript concerns the DESI DR2 reproduction, influence
diagnostics, selected-null calibration, and frozen predictions.

Target sequence:

1. Complete one independent human clean-room execution and preserve the signed
   verifier worksheet.
2. Resolve or explicitly delimit the official-likelihood LRG2 reconstruction.
3. Reconcile every manuscript number with `RESULTS_MANIFEST.json`.
4. Convert the canonical manuscript to REVTeX and build a submission PDF.
5. Post a versioned preprint when endorsement and author metadata are ready.
6. Submit to an appropriate scientific journal, with Physical Review D as the
   current primary target.

The journal submission must describe the work as an independent implementation
of published compressed likelihoods, not a raw-data reanalysis. It must retain
the selection caveat, AI-use disclosure, data credits, and clean-room status.

External scientific readers are being asked to find errors, reproduce the
workflow, or assess presentation. They are not being asked to validate the
mathematics by status or authority.

## 2. JOSS software paper

The JOSS paper concerns the reusable `de-stress-lab` software—not the truth of
the flagship cosmology interpretation.

JOSS's current public screening rules require more than six months of public
development, distributed activity, demonstrated research use, and healthy
open-source practice. The repository became public on 2026-07-21, so the
earliest conservative screening date is 2027-01-22.

Before that date:

- preserve a versioned software DOI;
- obtain an independent installation record;
- document at least one use beyond the original flagship analysis;
- maintain meaningful issues, pull requests, tests, releases, and changelog
  entries over time;
- record external feedback and how it changed the software;
- confirm author name, affiliation, ORCID choice, conflicts, and AI disclosure.

Do not manufacture activity to satisfy the timeline. Every public change should
reflect actual maintenance, feedback, adoption, or research use.

## Evidence register

Record each event in a dated issue or release:

| Evidence | Minimum record |
|---|---|
| Independent install | Exact release, platform, commands, outcome, verifier |
| External use | Research question, repository/release, user confirmation |
| Feedback | Public issue and linked change or reason for no change |
| Release | Changelog, tag, archive, checksum, DOI relationship |
| Manuscript review | Reviewer role, scope, dated response, credited corrections |

Official references:

- JOSS submission requirements: https://joss.readthedocs.io/en/latest/submitting.html
- JOSS review checklist: https://joss.readthedocs.io/en/latest/review_checklist.html
- APS manuscript submission: https://publish.aps.org/
