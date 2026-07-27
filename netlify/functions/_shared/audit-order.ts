import { createHash } from "node:crypto";

import type Stripe from "stripe";

export const EXPECTED_AMOUNT = 19_900;
export const EXPECTED_CURRENCY = "usd";

export type IntakeDecision =
  | { kind: "ignore"; reason: string }
  | { kind: "needs_attention"; orderReference: string; reason: string }
  | {
      kind: "dispatch";
      orderReference: string;
      repositoryUrl: string;
    };

function paymentLinkId(
  paymentLink: string | Stripe.PaymentLink | null,
): string | null {
  if (typeof paymentLink === "string") {
    return paymentLink;
  }
  return paymentLink?.id ?? null;
}

export function normalizeGitHubRepositoryUrl(value: string): string | null {
  let parsed: URL;
  try {
    parsed = new URL(value.trim());
  } catch {
    return null;
  }

  if (
    parsed.protocol !== "https:" ||
    parsed.hostname.toLowerCase() !== "github.com" ||
    parsed.username ||
    parsed.password ||
    parsed.search ||
    parsed.hash
  ) {
    return null;
  }

  const parts = parsed.pathname.split("/").filter(Boolean);
  if (parts.length !== 2) {
    return null;
  }

  const owner = parts[0];
  const repository = parts[1].replace(/\.git$/i, "");
  const ownerPattern = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/;
  const repositoryPattern = /^[A-Za-z0-9_.-]{1,100}$/;
  if (
    !ownerPattern.test(owner) ||
    owner.endsWith("-") ||
    !repositoryPattern.test(repository) ||
    repository === "." ||
    repository === ".."
  ) {
    return null;
  }

  return `https://github.com/${owner}/${repository}`;
}

export function extractRepositoryUrl(
  customFields: Stripe.Checkout.Session.CustomField[] | null,
): string | null {
  for (const field of customFields ?? []) {
    let value: string | null = null;
    if (field.type === "text") {
      value = field.text?.value ?? null;
    } else if (field.type === "numeric") {
      value = field.numeric?.value ?? null;
    }
    if (!value) {
      continue;
    }
    const repositoryUrl = normalizeGitHubRepositoryUrl(value);
    if (repositoryUrl) {
      return repositoryUrl;
    }
  }
  return null;
}

export function orderReference(sessionId: string): string {
  return createHash("sha256").update(sessionId).digest("hex").slice(0, 20);
}

export function decideIntake(
  eventType: string,
  session: Stripe.Checkout.Session,
  expectedPaymentLink: string,
): IntakeDecision {
  if (
    eventType !== "checkout.session.completed" &&
    eventType !== "checkout.session.async_payment_succeeded"
  ) {
    return { kind: "ignore", reason: "event_not_fulfillable" };
  }

  if (paymentLinkId(session.payment_link) !== expectedPaymentLink) {
    return { kind: "ignore", reason: "different_payment_link" };
  }

  if (
    session.amount_total !== EXPECTED_AMOUNT ||
    session.currency?.toLowerCase() !== EXPECTED_CURRENCY
  ) {
    return {
      kind: "needs_attention",
      orderReference: orderReference(session.id),
      reason: "unexpected_amount_or_currency",
    };
  }

  if (session.payment_status !== "paid") {
    return { kind: "ignore", reason: "payment_not_settled" };
  }

  const repositoryUrl = extractRepositoryUrl(session.custom_fields);
  if (!repositoryUrl) {
    return {
      kind: "needs_attention",
      orderReference: orderReference(session.id),
      reason: "missing_or_invalid_repository_url",
    };
  }

  return {
    kind: "dispatch",
    orderReference: orderReference(session.id),
    repositoryUrl,
  };
}
