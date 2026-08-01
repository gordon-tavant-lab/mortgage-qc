// errors.test.ts — T009 unit tests for errors.ts's toErrorEnvelope() serializer: every
// TouchlessProxyError must map to the exact plan.md §2.5 envelope shape, with the correct
// `retryable` flag per the table, and `message` must never leak PII or a raw vendor body.
//
// RED (expected, Phase 5): toErrorEnvelope() currently throws "not implemented — Phase 6".
import { describe, expect, it } from "vitest";
import { ErrorCode, TouchlessProxyError, toErrorEnvelope } from "../errors";
import { expectMessageIsSafe, expectValidErrorEnvelope } from "./helpers/envelope";

// Per plan.md §2.5's table: retryable=true for AUTH_FAILURE, TIMEOUT, UPSTREAM_ERROR;
// retryable=false for NOT_FOUND, INVALID_INPUT.
const RETRYABLE_BY_CODE: Partial<Record<ErrorCode, boolean>> = {
  [ErrorCode.AUTH_FAILURE]: true,
  [ErrorCode.NOT_FOUND]: false,
  [ErrorCode.TIMEOUT]: true,
  [ErrorCode.UPSTREAM_ERROR]: true,
  [ErrorCode.INVALID_INPUT]: false,
};

describe("errors.toErrorEnvelope", () => {
  it.each(Object.entries(RETRYABLE_BY_CODE) as [ErrorCode, boolean][])(
    "maps %s to the plan.md §2.5 envelope with retryable=%s",
    (code, expectedRetryable) => {
      const err = new TouchlessProxyError(code, "a generic categorized message", 401);
      const envelope = toErrorEnvelope(err, "req-123");

      expectValidErrorEnvelope(envelope, code);
      expect(envelope.error.retryable).toBe(expectedRetryable);
      expect(envelope.error.requestId).toBe("req-123");
    },
  );

  it("never includes the raw vendor response body or PII in the message field", () => {
    const rawVendorBody = JSON.stringify({
      status: 404,
      detail: "no application found",
      borrowerSsn: "123-45-6789",
      borrowerName: "Jane Q. Borrower",
    });
    const err = new TouchlessProxyError(ErrorCode.NOT_FOUND, rawVendorBody, 404);

    const envelope = toErrorEnvelope(err, "req-456");

    expectValidErrorEnvelope(envelope, ErrorCode.NOT_FOUND);
    expectMessageIsSafe(envelope, [rawVendorBody, "123-45-6789", "Jane Q. Borrower"]);
  });

  it("falls back to a PROXY_ERROR envelope for an unrecognized/non-TouchlessProxyError error", () => {
    const envelope = toErrorEnvelope(new Error("some unexpected internal exception"), "req-789");

    expectValidErrorEnvelope(envelope, ErrorCode.PROXY_ERROR);
    expect(envelope.error.retryable).toBe(false);
  });

  it("produces a parseable ISO-8601 timestamp close to now", () => {
    const before = Date.now();
    const envelope = toErrorEnvelope(
      new TouchlessProxyError(ErrorCode.TIMEOUT, "upstream call exceeded its deadline", null),
      "req-ts",
    );
    const after = Date.now();

    const parsed = Date.parse(envelope.error.timestamp);
    expect(parsed).toBeGreaterThanOrEqual(before);
    expect(parsed).toBeLessThanOrEqual(after);
  });
});
