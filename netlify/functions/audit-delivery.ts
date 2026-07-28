import { getStore } from "@netlify/blobs";
import type { Config } from "@netlify/functions";

import {
  bearerToken,
  deliveryEmail,
  parseDeliveryRequest,
  tokensMatch,
} from "./_shared/audit-delivery.js";

declare const Netlify: {
  env: {
    get(name: string): string | undefined;
  };
};

type OrderRecord = {
  customerEmail?: string;
  deliveredAt?: string;
  emailMessageId?: string;
  orderReference: string;
  repositoryUrl?: string;
  state:
    | "accepted"
    | "dispatched"
    | "delivered"
    | "needs_attention"
    | "dispatch_failed";
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

export default async (request: Request): Promise<Response> => {
  if (request.method !== "POST") {
    return json({ error: "method_not_allowed" }, 405);
  }

  if (
    !tokensMatch(
      bearerToken(request),
      requiredEnvironment("AUDIT_DELIVERY_TOKEN"),
    )
  ) {
    return json({ error: "unauthorized" }, 401);
  }

  let value: unknown;
  try {
    value = await request.json();
  } catch {
    return json({ error: "invalid_json" }, 400);
  }
  const delivery = parseDeliveryRequest(value);
  if (!delivery) {
    return json({ error: "invalid_delivery" }, 400);
  }

  const store = getStore({ name: "paid-audit-orders", consistency: "strong" });
  const key = `orders/${delivery.order_reference}.json`;
  const record = (await store.get(key, { type: "json" })) as OrderRecord | null;
  if (!record) {
    return json({ error: "order_not_found" }, 404);
  }
  if (record.state === "delivered") {
    return json({ delivered: true, action: "duplicate" });
  }
  if (
    record.state !== "dispatched" ||
    record.repositoryUrl !== delivery.repository_url ||
    !record.customerEmail
  ) {
    return json({ error: "order_not_deliverable" }, 409);
  }

  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${requiredEnvironment("RESEND_API_KEY")}`,
      "Content-Type": "application/json",
      "Idempotency-Key": `audit-delivery-${delivery.order_reference}`,
      "User-Agent": "de-stress-audit-delivery",
    },
    body: JSON.stringify(
      deliveryEmail(
        delivery,
        record.customerEmail,
        requiredEnvironment("AUDIT_FROM_EMAIL"),
        Netlify.env.get("AUDIT_REPLY_TO_EMAIL"),
      ),
    ),
  });
  const result = (await response.json().catch(() => ({}))) as {
    id?: string;
    message?: string;
  };
  if (!response.ok || !result.id) {
    throw new Error(
      `Email delivery rejected (${response.status}): ${result.message ?? "unknown error"}`,
    );
  }

  const { customerEmail: _customerEmail, ...privacySafeRecord } = record;
  const now = new Date().toISOString();
  await store.setJSON(key, {
    ...privacySafeRecord,
    deliveredAt: now,
    emailMessageId: result.id,
    state: "delivered",
    updatedAt: now,
  } satisfies OrderRecord);

  return json({ delivered: true, action: "sent" });
};

export const config: Config = {
  path: "/api/audit/delivery",
  method: ["POST"],
};
