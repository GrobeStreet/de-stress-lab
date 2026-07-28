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
  deliveryStartedAt?: string;
  orderReference: string;
  repositoryUrl?: string;
  state:
    | "accepted"
    | "delivery_pending"
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
  if (record.state === "delivery_pending") {
    return json({ delivered: false, action: "pending" }, 202);
  }
  if (
    record.state !== "dispatched" ||
    record.repositoryUrl !== delivery.repository_url ||
    !record.customerEmail
  ) {
    return json({ error: "order_not_deliverable" }, 409);
  }

  const deliveryStartedAt = new Date().toISOString();
  await store.setJSON(key, {
    ...record,
    deliveryStartedAt,
    state: "delivery_pending",
    updatedAt: deliveryStartedAt,
  } satisfies OrderRecord);

  let messageId: string;
  try {
    const response = await fetch("https://api.sendgrid.com/v3/mail/send", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${requiredEnvironment("SENDGRID_API_KEY")}`,
        "Content-Type": "application/json",
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
    if (response.status !== 202) {
      const result = (await response.json().catch(() => ({}))) as {
        errors?: Array<{ message?: string }>;
      };
      throw new Error(
        `Email delivery rejected (${response.status}): ${result.errors?.[0]?.message ?? "unknown error"}`,
      );
    }
    messageId =
      response.headers.get("x-message-id") ??
      `sendgrid-accepted-${delivery.order_reference}`;
  } catch (error) {
    const failedAt = new Date().toISOString();
    await store.setJSON(key, {
      ...record,
      reason: error instanceof Error ? error.message : "SendGrid delivery failed",
      state: "dispatched",
      updatedAt: failedAt,
    } satisfies OrderRecord);
    throw error;
  }

  const { customerEmail: _customerEmail, ...privacySafeRecord } = record;
  const now = new Date().toISOString();
  await store.setJSON(key, {
    ...privacySafeRecord,
    deliveredAt: now,
    deliveryStartedAt,
    emailMessageId: messageId,
    state: "delivered",
    updatedAt: now,
  } satisfies OrderRecord);

  return json({ delivered: true, action: "sent" });
};

export const config: Config = {
  path: "/api/audit/delivery",
  method: ["POST"],
};
