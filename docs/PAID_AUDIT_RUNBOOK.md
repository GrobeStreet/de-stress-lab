# Paid audit fulfillment runbook

## Purpose

Use this procedure after Stripe reports a successful payment for the
**Automated Reproducibility Audit**. It converts a purchase into a consistent,
safe delivery without expanding the fixed $199 scope.

## Preconditions

- Stripe payment status is successful.
- The line item is `Automated Reproducibility Audit` at the current one-time
  price.
- The required GitHub repository URL is present.
- The purchaser controls the repository or is authorized to request the audit.
- No credentials or confidential data were placed in the checkout field.

The live Payment Link ID is `plink_1Txqm0CXiKgGyE2b6TfI1OUZ`. Treat customer
email addresses and payment records as private. Never copy them into a public
issue, report, commit, or workflow log.

## Intake

1. Confirm the payment in Stripe; do not rely on an email alone. The production
   webhook performs this check automatically for supported Payment Link orders.
2. Use the non-customer order reference and repository URL from the generated
   GitHub Actions artifact. Do not copy payment or contact data into GitHub.
3. Check that the repository is accessible and the requested work fits one
   repository and one primary build path.
4. If access or authorization is unclear, pause before cloning or analysis and
   request clarification privately.
5. Record the intake time and set a two-business-day delivery target.

The automated stage validates the Stripe signature, Payment Link, settled
status, amount, currency, and public GitHub repository URL. It is idempotent by
Checkout Session and produces only a static audit. Customer code is never
executed by the webhook.

## Safety gate

Treat every purchased repository as untrusted code.

- Do not execute it on the operator's normal workstation.
- Do not expose API keys, SSH agents, cloud credentials, browser sessions, or
  customer data to the repository.
- Prefer static inspection first.
- Execute installation or tests only in an isolated disposable environment
  with no secrets, minimal filesystem access, bounded CPU/time, and network
  access disabled unless a documented dependency retrieval step requires it.
- Do not open an issue, pull request, or public report without explicit
  customer permission.

If an isolated execution environment is unavailable, complete the static audit
and state that execution was not attempted.

## Audit procedure

1. Freeze the repository commit SHA and record the default branch.
2. Run the structural scanner:

   ```bash
   destress audit-repo REPOSITORY_PATH \
     --json-output audit.json \
     --markdown-output audit.md
   ```

3. Inspect the documented installation path, dependency bounds or lockfiles,
   test organization, CI permissions, release metadata, citation metadata,
   data provenance, deterministic seeds, and frozen-result evidence.
4. Check whether the README's claimed commands match the configured package and
   workflow entry points.
5. When the safety gate passes, run only the documented minimal installation
   and test commands in the disposable environment. Preserve the exact command,
   environment, exit status, duration, and bounded output.
6. Rank findings by reproducibility impact:
   - **Blocker:** prevents an independent run or makes the result ambiguous.
   - **High:** can materially change or invalidate a reported result.
   - **Medium:** weakens provenance, testing, or environment control.
   - **Low:** maintainability or documentation improvement.

For automated orders, the structural scanner has already run on an ephemeral
GitHub-hosted runner. Download the `paid-audit-*` artifact, verify its recorded
commit, and continue from the safety gate before attempting installation or
tests.

## Delivery package

Deliver:

- `audit.md` — executive result, evidence table, and prioritized actions;
- `audit.json` — machine-readable readiness findings;
- `execution.md` — attempted commands, environment, outputs, and blockers;
- `scope.md` — frozen repository SHA, exclusions, and boundary statement.

Start from the
[delivery template](PAID_AUDIT_DELIVERY_TEMPLATE.md) so every customer receives
the same evidence structure. Keep the working copy outside the public
repository unless the customer explicitly authorizes publication.

The executive result must distinguish:

1. repository readiness;
2. successful or blocked execution;
3. numerical reproduction;
4. scientific interpretation.

Never imply that passing the first two establishes the last two.

## Customer handoff

1. Send the files to the email recorded by Stripe.
2. State the audited commit SHA and every unattempted check.
3. Invite one clarification round limited to factual errors or missing
   repository instructions.
4. Offer separately scoped work only when the requested next step exceeds the
   fixed-price boundary.
5. Mark the order delivered without publishing customer information.

## Exceptions and escalation

- **Repository inaccessible:** request a corrected URL or separately arranged
  access; do not request credentials through public channels.
- **Unsafe or unusually large build:** deliver the static review and execution
  blocker rather than weakening isolation.
- **Regulated, personal, or confidential data appears:** stop and request a
  private rescoping decision.
- **Customer requests endorsement or predetermined findings:** decline and
  preserve the publish-regardless standard.
- **Payment dispute or refund request:** handle in Stripe and preserve the
  audit record; do not continue work after a full refund.
