# Generative AI Use Disclosure

This project has used generative AI tools as part of its development workflow. This disclosure is intended to make that use explicit for reviewers, contributors, and downstream users.

## Where AI assistance was used

Generative AI assisted portions of:

- implementation and refactoring suggestions;
- test and edge-case generation;
- documentation drafting and editing;
- repository auditing and reproducibility checklists;
- scientific-writing structure and wording review.

AI output was not treated as evidence of scientific correctness, successful reproduction, or independent verification.

## Scale and attribution

AI assistance occurred throughout the active development period rather than in one isolated commit. Exact line-by-line historical attribution is not fully reconstructable. Some routines, tests, and documentation began from AI-generated or AI-edited drafts and were then reviewed, changed, tested, or rejected by the maintainer.

Where a future contribution contains substantial AI-generated code, contributors should disclose that fact in the pull request when practical.

## Human review and responsibility

The maintainer is responsible for the submitted package and its maintenance. AI-generated suggestions are accepted only after human review appropriate to the change. Depending on the component, review includes one or more of:

- reading and editing the implementation;
- running the automated test suite;
- numerical equivalence or regression checks;
- comparing generated results with frozen artifacts and checksums;
- documenting limitations and failed checks;
- preserving reported, regenerated, and independently verified states as distinct evidence levels.

The repository explicitly states when independent human clean-room execution has not yet occurred. Automated or AI-assisted checks are not presented as substitutes for unrelated external verification.

## Data and privacy

The reusable package does not require users to submit private data to an AI service. Core package execution is local Python code. Contributors should not paste confidential, restricted, or personally identifying data into external generative-AI tools as part of project development.

## Policy for review

For pyOpenSci review, this file should be read together with the README, test suite, provenance records, and release artifacts. Reviewers should treat this disclosure as context, not as a request to relax normal software-quality expectations.
