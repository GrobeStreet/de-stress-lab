# Free GitHub Action

The free action performs a transparent structural scan of a research
repository. It scores ten controls totaling 100 points:

| Control | Points |
|---|---:|
| Reader-facing README | 10 |
| Explicit software license | 10 |
| Machine-readable environment | 15 |
| Automated tests | 15 |
| Continuous integration | 10 |
| Citation metadata | 5 |
| Data-availability statement | 10 |
| Code-availability statement | 10 |
| Contribution and support path | 5 |
| Frozen evidence or result manifest | 10 |

This score measures readiness to reproduce, not scientific correctness.

## Add it to a repository

Create `.github/workflows/reproducibility-audit.yml`:

```yaml
name: Reproducibility audit

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - id: audit
        uses: GrobeStreet/de-stress-lab@action-v1
        with:
          minimum-score: "70"
      - uses: actions/upload-artifact@v7
        with:
          name: reproducibility-audit
          path: |
            destress-audit.json
            destress-audit.md
```

The job summary contains the score, evidence for every check, and prioritized
next actions. The Action also exposes:

- `score`
- `grade`
- `score-badge-url`
- `status-badge-markdown`

## Public badge

After the workflow runs, place this in the repository README:

```markdown
[![Reproducibility audit](https://github.com/OWNER/REPOSITORY/actions/workflows/reproducibility-audit.yml/badge.svg)](https://github.com/OWNER/REPOSITORY/actions/workflows/reproducibility-audit.yml)
```

The badge is green only when the workflow succeeds, including the configured
minimum score.

## Boundaries

The free scan does not execute headline scientific claims, judge statistical
validity, inspect private data, or certify a result. Claim-level reproduction,
null simulations, influence analysis, and correction pull requests belong to
the paid audit tier.

## Go beyond the badge

The fixed-scope
[Automated Reproducibility Audit](PAID_AUDIT.md) adds code, build, test,
provenance, and safe execution-path review for one authorized repository. It
produces Markdown and JSON findings with prioritized remediation for a one-time
$199 payment.
