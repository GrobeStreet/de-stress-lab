import { getStore } from "@netlify/blobs";
import type { Config } from "@netlify/functions";
import Stripe from "stripe";

import { decideIntake } from "./_shared/audit-order.js";

declare const Netlify: {
  env: {
    get(name: string): string | undefined;
  };
};

const stripe = new Stripe("sk_not_used_for_signature_verification");

type OrderRecord = {
  orderReference: string;
  repositoryUrl?: string;
  state: "accepted" | "dispatched" | "needs_attention" | "dispatch_failed";
  reason?: string;
  updatedAt: string;
};

function json(body: object, status = 200): Response {
  return Response.json(body, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "Content-Type": "application/json",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function requiredEnvironment(name: string): string {
  const value = Netlify.env.get(name);
  if (!value) {
    throw new Error(`Missing server configuration: ${name}`);
  }
  return value;
}

async function dispatchGitHub(
  eventType: "paid-audit-purchased" | "paid-audit-needs-attention",
  clientPayload: Record<string, string>,
): Promise<void> {
  const repository = requiredEnvironment("GITHUB_AUDIT_REPOSITORY");
  const token = requiredEnvironment("GITHUB_DISPATCH_TOKEN");
  const response = await fetch(
    `https://api.github.com/repos/${repository}/dispatches`,
    {
      method: "POST",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        "User-Agent": "de-stress-audit-intake",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({
        event_type: eventType,
        client_payload: clientPayload,
      }),
    },
  );
  if (!response.ok) {
    throw new Error(`GitHub dispatch rejected with status ${response.status}`);
  }
}

async function isPublicGitHubRepository(repositoryUrl: string): Promise<boolean> {
  const repository = new URL(repositoryUrl).pathname.replace(/^\//, "");
  const response = await fetch(`https://api.github.com/repos/${repository}`, {
    headers: {
      Accept: "application/vnd.github+json",
      "User-Agent": "de-stress-audit-intake",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (response.status === 404) {
    return false;
  }
  if (!response.ok) {
    throw new Error(`GitHub repository validation failed (${response.status})`);
  }
  const record = (await response.json()) as { private?: boolean };
  return record.private === false;
}

export default async (request: Request): Promise<Response> => {
  if (request.method === "GET") {
    return json({ service: "de-stress-audit-intake", status: "ready" });
  }
  if (request.method !== "POST") {
    return json({ error: "method_not_allowed" }, 405);
  }

  const signature = request.headers.get("stripe-signature");
  if (!signature) {
    return json({ error: "missing_signature" }, 400);
  }

  let event: Stripe.Event;
  try {
    event = await stripe.webhooks.constructEventAsync(
      await request.text(),
      signature,
      requiredEnvironment("STRIPE_WEBHOOK_SECRET"),
    );
  } catch {
    return json({ error: "invalid_signature" }, 400);
  }

  if (
    event.type === "checkout.session.async_payment_failed" ||
    !(
      event.type === "checkout.session.completed" ||
      event.type === "checkout.session.async_payment_succeeded"
    )
  ) {
    return json({ received: true, action: "ignored" });
  }

  const decision = decideIntake(
    event.type,
    event.data.object,
    requiredEnvironment("STRIPE_PAYMENT_LINK_ID"),
  );
  if (decision.kind === "ignore") {
    return json({ received: true, action: "ignored", reason: decision.reason });
  }

  const store = getStore({ name: "paid-audit-orders", consistency: "strong" });
  const key = `orders/${decision.orderReference}.json`;
  const previous = await store.get(key, { type: "json" });
  if (previous) {
    const record = previous as OrderRecord;
    if (record.state === "dispatched" || record.state === "needs_attention") {
      return json({ received: true, action: "duplicate" });
    }
  }

  if (decision.kind === "needs_attention") {
    const record: OrderRecord = {
      orderReference: decision.orderReference,
      state: "needs_attention",
      reason: decision.reason,
      updatedAt: new Date().toISOString(),
    };
    await store.setJSON(key, record);
    await dispatchGitHub("paid-audit-needs-attention", {
      order_reference: decision.orderReference,
      reason: decision.reason,
    });
    return json({ received: true, action: "needs_attention" });
  }

  if (!(await isPublicGitHubRepository(decision.repositoryUrl))) {
    const reason = "repository_not_publicly_accessible";
    const record: OrderRecord = {
      orderReference: decision.orderReference,
      repositoryUrl: decision.repositoryUrl,
      state: "needs_attention",
      reason,
      updatedAt: new Date().toISOString(),
    };
    await store.setJSON(key, record);
    await dispatchGitHub("paid-audit-needs-attention", {
      order_reference: decision.orderReference,
      reason,
    });
    return json({ received: true, action: "needs_attention" });
  }

  const accepted: OrderRecord = {
    orderReference: decision.orderReference,
    repositoryUrl: decision.repositoryUrl,
    state: "accepted",
    updatedAt: new Date().toISOString(),
  };
  await store.setJSON(key, accepted);

  try {
    await dispatchGitHub("paid-audit-purchased", {
      order_reference: decision.orderReference,
      repository_url: decision.repositoryUrl,
    });
  } catch (error) {
    await store.setJSON(key, {
      ...accepted,
      state: "dispatch_failed",
      reason: error instanceof Error ? error.message : "dispatch_failed",
      updatedAt: new Date().toISOString(),
    } satisfies OrderRecord);
    throw error;
  }

  await store.setJSON(key, {
    ...accepted,
    state: "dispatched",
    updatedAt: new Date().toISOString(),
  } satisfies OrderRecord);
  return json({ received: true, action: "dispatched" });
};

export const config: Config = {
  path: "/api/stripe/audit-webhook",
  method: ["GET", "POST"],
};
