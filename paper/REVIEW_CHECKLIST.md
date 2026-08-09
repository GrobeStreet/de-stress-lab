# JOSS pre-submission checklist

Last audited against the current JOSS submission requirements and review
checklist on **2026-08-09**. This is a self-audit, not editorial approval.

## Pre-review gates

| Gate | Status | Evidence or required action |
|---|---|---|
| Public development history longer than six months | **Blocked until 2027-01-22** | Public history begins 2026-07-21. Continue real maintenance and do not manufacture activity. |
| Demonstrated research impact | **Partial** | The package architecture is used by the public DESI DR2 flagship analysis. Record any additional real research use or integration before submission. |
| Good open-source practice | **Ready** | Public issues and pull requests, tagged releases, `CHANGELOG.md`, tests and CI, documentation, `CONTRIBUTING.md`, `SUPPORT.md`, and `GOVERNANCE.md`. |
| Iterative development over time | **In progress** | Preserve meaningful maintenance, feedback, and releases across the eligibility interval. |
| Independent installation | **Requested** | A non-author report is requested in issue #21 or through the independent-install issue form. |

## Reviewer checklist mapping

| Review item | Status | Repository evidence |
|---|---|---|
| Source and issue tracker public | Ready | Repository and GitHub issues are public. |
| OSI-approved license | Ready | `LICENSE` (MIT). |
| Appropriate authorship | Author confirmation needed | Confirm final display name, affiliation, ORCID choice, and any additional contributors before submission. |
| Installation | Author-verified; independent check pending | `README.md`, `docs/QUICKSTART.md`, PyPI release, tests, issue #21. |
| Functionality and tests | Ready | `tests/`, `.github/workflows/tests.yml`, reproducibility audit, package-equivalence tests. |
| Statement of need | Ready | `paper/paper.md` and `README.md`. |
| Example usage | Ready | `docs/QUICKSTART.md`, CLI demo, and domain-neutral deletion-influence example. |
| API documentation | Ready | `docs/API.md`. |
| Contribution, support, conduct, governance | Ready | `CONTRIBUTING.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`. |
| Paper summary | Ready | Required section in `paper/paper.md`. |
| State of the field | Ready | Required section with related-software citations. |
| Software design | Ready | Required section describing boundaries and trade-offs. |
| Research impact statement | Partial | Flagship use is documented; stronger external-use evidence remains desirable. |
| AI usage disclosure | Ready | Required section names tools, scope, validation, and human responsibility. |
| References and paper length | Ready | `paper/paper.bib`; manuscript body is within JOSS's 750-1750 word range. |
| Conflict of interest and funding statements | Author confirmation needed | Confirm at submission; the current paper declares no external financial support. |

## Submission-day sequence

1. Re-run this checklist against the current JOSS documentation.
2. Confirm the repository has more than six months of distributed public
   development and credible research-use evidence.
3. Obtain and link at least one independent installation record.
4. Confirm author name, affiliation, ORCID choice, authorship, funding, and
   conflicts of interest.
5. Run the full test suite and `destress demo` from a clean environment.
6. Build `paper/paper.md` with the JOSS draft workflow and inspect the PDF.
7. Submit the repository URL and paper path through the JOSS form.
8. Do not use generative AI for conversations with JOSS editors or reviewers;
   the author must handle those interactions directly under the current policy.
