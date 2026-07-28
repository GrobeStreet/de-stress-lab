import assert from "node:assert/strict";
import test from "node:test";

import type Stripe from "stripe";

import {
  decideIntake,
  normalizeCustomerEmail,
  normalizeGitHubRepositoryUrl,
  orderReference,
} from "./audit-order.js";

function session(
  overrides: Partial<Stripe.Checkout.Session> = {},
): Stripe.Checkout.Session {
  return {
    id: "cs_live_example",
    object: "checkout.session",
    amount_total: 19_900,
    currency: "usd",
    customer_details: {
      address: null,
      email: "Researcher@Example.edu",
      name: null,
      phone: null,
      tax_exempt: "none",
      tax_ids: [],
    },
    payment_link: "plink_expected",
    payment_status: "paid",
    custom_fields: [
      {
        key: "repository",
        label: { custom: "GitHub repository URL", type: "custom" },
        optional: false,
        type: "text",
        text: { value: "https://github.com/example/research-code" },
      },
    ],
    ...overrides,
  } as Stripe.Checkout.Session;
}

test("normalizes only repository-root GitHub URLs", () => {
  assert.equal(
    normalizeGitHubRepositoryUrl("https://github.com/example/research-code.git"),
    "https://github.com/example/research-code",
  );
  assert.equal(
    normalizeGitHubRepositoryUrl("https://github.com/example/research-code/issues"),
    null,
  );
  assert.equal(
    normalizeGitHubRepositoryUrl("https://github.com.evil.test/example/repo"),
    null,
  );
  assert.equal(normalizeGitHubRepositoryUrl("git@github.com:example/repo.git"), null);
});

test("dispatches a settled matching audit purchase", () => {
  assert.deepEqual(
    decideIntake("checkout.session.completed", session(), "plink_expected"),
    {
      kind: "dispatch",
      customerEmail: "researcher@example.edu",
      orderReference: orderReference("cs_live_example"),
      repositoryUrl: "https://github.com/example/research-code",
    },
  );
});

test("does not fulfill an unsettled or unrelated checkout", () => {
  assert.deepEqual(
    decideIntake(
      "checkout.session.completed",
      session({ payment_status: "unpaid" }),
      "plink_expected",
    ),
    { kind: "ignore", reason: "payment_not_settled" },
  );
  assert.deepEqual(
    decideIntake("checkout.session.completed", session(), "plink_other"),
    { kind: "ignore", reason: "different_payment_link" },
  );
});

test("normalizes a deliverable customer email", () => {
  assert.equal(
    normalizeCustomerEmail("  Researcher@Example.edu "),
    "researcher@example.edu",
  );
  assert.equal(normalizeCustomerEmail("not-an-email"), null);
  assert.equal(normalizeCustomerEmail("header@example.edu\nBcc: bad@example.net"), null);
});

test("routes invalid intake for private review without exposing customer data", () => {
  const result = decideIntake(
    "checkout.session.async_payment_succeeded",
    session({ custom_fields: [] }),
    "plink_expected",
  );
  assert.equal(result.kind, "needs_attention");
  assert.equal(
    result.kind === "needs_attention" ? result.reason : "",
    "missing_or_invalid_repository_url",
  );
});

test("routes a missing customer email for private review", () => {
  const result = decideIntake(
    "checkout.session.completed",
    session({ customer_details: null, customer_email: null }),
    "plink_expected",
  );
  assert.deepEqual(result, {
    kind: "needs_attention",
    orderReference: orderReference("cs_live_example"),
    reason: "missing_or_invalid_customer_email",
  });
});
