# ADR-0001: Separate reusable diagnostics from the flagship analysis

**Status:** Accepted  
**Date:** 2026-07-27  
**Decider:** Bobby Morong

## Context

The original Dark-Energy Stress Lab was a reproducible, one-project analysis.
Its scripts combine cosmological distance calculations, DESI-specific summary
data, optimization, null simulation, and report generation. That layout is
auditable for the original result but makes the statistical methods difficult
to reuse on another experiment.

## Decision

Create an installable `destress` Python package with four stable layers:

1. explicit scientific models;
2. typed datasets and likelihood blocks;
3. deterministic inference primitives;
4. selection-aware stress tests and frozen-ledger verification.

Dataset-specific constants live in a separate registry. Existing scripts and
results remain frozen as the flagship validation case. Package-equivalence
tests compare the new API against those scripts instead of rewriting the
historical record.

## Options considered

### Rewrite every script around one framework

This would remove duplication, but it would also alter the exact implementation
that generated the released results and weaken the audit trail.

### Publish the scripts unchanged

This preserves provenance but does not provide a maintainable or reusable API.

### Add a package beside the frozen scripts

This retains the released analysis and provides a stable migration path. It
requires temporary duplication, controlled by numerical-equivalence tests.

## Consequences

- Other projects can supply their own likelihood or grouped observations.
- The DESI example remains available without making it the package abstraction.
- Frozen results do not silently change as the API evolves.
- Future work should migrate shared code only after equivalence tests cover it.

