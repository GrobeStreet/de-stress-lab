# Paid audit automation

## Production flow

1. Stripe sends a signed Checkout event to the Netlify Function.
2. The function verifies the untouched request body and signing secret.
3. It accepts only the configured Payment Link, $199 USD, and settled payment.
4. It extracts and normalizes the required public GitHub repository URL.
5. A site-scoped idempotency record prevents routine duplicate dispatches.
6. The function sends a minimal, non-customer payload to GitHub Actions.
7. An ephemeral runner clones the public repository without credentials,
   performs the static structural audit, and uploads a 30-day delivery artifact.
8. Execution, numerical reproduction, interpretation, and customer delivery
   remain behind the fulfillment safety gate.

Customer email, card, address, and payment details never enter GitHub Actions,
workflow logs, or public repository files.

## Required production configuration

The deployed function uses these encrypted environment variables:

- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PAYMENT_LINK_ID`
- `GITHUB_DISPATCH_TOKEN`
- `GITHUB_AUDIT_REPOSITORY`

The Stripe destination subscribes only to:

- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`
- `checkout.session.async_payment_failed`

The GitHub token should be restricted to this repository and the minimum
permission needed to create a repository dispatch.

## Failure handling

- Invalid signatures return an error and perform no action.
- Unrelated events, Payment Links, and unsettled payments are acknowledged and
  ignored.
- Invalid or inaccessible repository intake creates a minimal
  `paid-audit-needs-attention` workflow artifact.
- Failed GitHub dispatches return an error so Stripe retries delivery.
- The workflow never automatically installs or executes customer code.
