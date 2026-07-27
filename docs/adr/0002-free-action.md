# ADR-0002: Keep the free Action structural and transparent

**Status:** Accepted
**Date:** 2026-07-27
**Decider:** Bobby Morong

## Context

A free repository audit must be fast, safe on untrusted pull requests, useful
across research fields, and clear about what it does not establish. Executing
arbitrary scientific pipelines by default would introduce security, runtime,
and interpretation risks.

## Decision

The free GitHub Action performs deterministic file- and documentation-level
readiness checks. Every point is tied to visible evidence and a recommendation.
It writes JSON and Markdown, publishes a GitHub job summary, and can enforce a
configurable minimum score.

Claim execution and statistical red-teaming remain separate paid workflows with
explicit scope and data authorization.

## Options considered

### Execute every repository automatically

Broader assurance, but unsafe, unpredictable in cost, and impossible to
interpret consistently across languages and research fields.

### Opaque machine-learned score

Easy to market but difficult to contest, improve, or audit.

### Transparent structural score

Lower inferential ambition, but fast, explainable, inexpensive, and appropriate
as the top of the commercial funnel.

## Consequences

- Public repositories receive actionable value without sharing secrets.
- The badge represents a documented threshold, not scientific endorsement.
- Paid audits have a clear value boundary: execution and claim verification.
- Future checks can be added only with explicit weights and tests.
