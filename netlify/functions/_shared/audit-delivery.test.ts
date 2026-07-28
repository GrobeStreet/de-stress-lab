import assert from "node:assert/strict";
import test from "node:test";

import {
  bearerToken,
  deliveryEmail,
  parseDeliveryRequest,
  tokensMatch,
} from "./audit-delivery.js";

const orderReference = "0123456789abcdefabcd";

function file(name: string, value = "test") {
  return {
    content_base64: Buffer.from(value).toString("base64"),
    content_type: name.endsWith(".json") ? "application/json" : "text/markdown",
    name,
  };
}

function requestValue() {
  return {
    files: [
      file("delivery-manifest.json", "{}"),
      file("execution.md"),
      file("scope.md"),
      file("audit.md"),
    ],
    order_reference: orderReference,
    repository_url: "https://github.com/example/research-code",
  };
}

test("accepts a bounded delivery package", () => {
  assert.deepEqual(parseDeliveryRequest(requestValue()), requestValue());
});

test("rejects traversal, duplicate, and malformed files", () => {
  assert.equal(
    parseDeliveryRequest({
      ...requestValue(),
      files: [file("../audit.md"), file("execution.md"), file("scope.md")],
    }),
    null,
  );
  assert.equal(
    parseDeliveryRequest({
      ...requestValue(),
      files: [
        file("delivery-manifest.json"),
        file("execution.md"),
        file("execution.md"),
        file("scope.md"),
      ],
    }),
    null,
  );
  assert.equal(
    parseDeliveryRequest({
      ...requestValue(),
      files: [
        file("delivery-manifest.json"),
        file("execution.md"),
        file("scope.md"),
        { ...file("audit.md"), content_base64: "not base64!" },
      ],
    }),
    null,
  );
});

test("authenticates a fixed-length bearer token safely", () => {
  const request = new Request("https://example.test", {
    headers: { Authorization: "Bearer shared-secret" },
  });
  assert.equal(bearerToken(request), "shared-secret");
  assert.equal(tokensMatch("shared-secret", "shared-secret"), true);
  assert.equal(tokensMatch("other", "shared-secret"), false);
  assert.equal(tokensMatch(null, "shared-secret"), false);
});

test("builds an attachment-only customer email", () => {
  const request = parseDeliveryRequest(requestValue());
  assert.ok(request);
  const message = deliveryEmail(
    request,
    "researcher@example.edu",
    "Audit Lab <audit@example.com>",
    "support@example.com",
  );
  assert.deepEqual(message.to, ["researcher@example.edu"]);
  assert.equal(message.reply_to, "support@example.com");
  assert.equal((message.attachments as unknown[]).length, 4);
  assert.ok(String(message.text).includes("does not certify scientific correctness"));
});
