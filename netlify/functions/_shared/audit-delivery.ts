import { timingSafeEqual } from "node:crypto";

export const ALLOWED_DELIVERY_FILES = new Set([
  "audit.json",
  "audit.md",
  "delivery-manifest.json",
  "execution.md",
  "scope.md",
]);
export const MAX_DELIVERY_BYTES = 5_000_000;

export type DeliveryFile = {
  content_base64: string;
  content_type: string;
  name: string;
};

export type DeliveryRequest = {
  files: DeliveryFile[];
  order_reference: string;
  repository_url: string;
};

export function bearerToken(request: Request): string | null {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) {
    return null;
  }
  return authorization.slice("Bearer ".length);
}

export function tokensMatch(actual: string | null, expected: string): boolean {
  if (!actual) {
    return false;
  }
  const actualBytes = Buffer.from(actual);
  const expectedBytes = Buffer.from(expected);
  return (
    actualBytes.length === expectedBytes.length &&
    timingSafeEqual(actualBytes, expectedBytes)
  );
}

export function parseDeliveryRequest(value: unknown): DeliveryRequest | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<DeliveryRequest>;
  if (
    !/^[a-f0-9]{20}$/.test(candidate.order_reference ?? "") ||
    typeof candidate.repository_url !== "string" ||
    !Array.isArray(candidate.files) ||
    candidate.files.length < 3 ||
    candidate.files.length > ALLOWED_DELIVERY_FILES.size
  ) {
    return null;
  }

  const names = new Set<string>();
  let totalBytes = 0;
  for (const file of candidate.files) {
    if (
      !file ||
      typeof file.name !== "string" ||
      !ALLOWED_DELIVERY_FILES.has(file.name) ||
      names.has(file.name) ||
      typeof file.content_type !== "string" ||
      !/^[a-z0-9.+-]+\/[a-z0-9.+-]+$/i.test(file.content_type) ||
      typeof file.content_base64 !== "string" ||
      !/^[A-Za-z0-9+/]*={0,2}$/.test(file.content_base64)
    ) {
      return null;
    }
    const bytes = Buffer.from(file.content_base64, "base64");
    if (bytes.toString("base64") !== file.content_base64) {
      return null;
    }
    totalBytes += bytes.length;
    names.add(file.name);
  }

  if (
    totalBytes > MAX_DELIVERY_BYTES ||
    !names.has("delivery-manifest.json") ||
    !names.has("execution.md") ||
    !names.has("scope.md")
  ) {
    return null;
  }

  return candidate as DeliveryRequest;
}

export function deliveryEmail(
  request: DeliveryRequest,
  customerEmail: string,
  from: string,
  replyTo?: string,
): Record<string, unknown> {
  return {
    from,
    to: [customerEmail],
    ...(replyTo ? { reply_to: replyTo } : {}),
    subject: `Your reproducibility audit is ready (${request.order_reference})`,
    text: [
      "Your automated reproducibility audit is attached.",
      "",
      `Repository: ${request.repository_url}`,
      `Order reference: ${request.order_reference}`,
      "",
      "This automated stage is a structural repository review. It does not certify scientific correctness, reproduce numerical claims, or constitute peer review.",
      "",
      "Reply to this email within seven days for one clarification round covering factual errors or missing repository instructions.",
    ].join("\n"),
    attachments: request.files.map((file) => ({
      content: file.content_base64,
      filename: file.name,
    })),
    tags: [
      { name: "service", value: "reproducibility-audit" },
      { name: "order_reference", value: request.order_reference },
    ],
  };
}
