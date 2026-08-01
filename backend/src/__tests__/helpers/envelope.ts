// helpers/envelope.ts — shared assertions for the plan.md §2.5 error envelope contract:
//   { error: { code, message, upstreamStatus, retryable, requestId, timestamp } }
// Used by every route/unit test that expects an error response, so the exact shape is
// checked consistently rather than re-typed ad hoc in every test file.
import { expect } from "vitest";

export const ERROR_ENVELOPE_KEYS = [
  "code",
  "message",
  "upstreamStatus",
  "retryable",
  "requestId",
  "timestamp",
] as const;

/**
 * Asserts `body` is a well-formed plan.md §2.5 error envelope, optionally pinned to a
 * specific `error.code`. Fails loudly (rather than silently passing) if `body.error` is
 * missing entirely — e.g. because the current Phase-4 scaffold's generic 500 handler still
 * matches the shape today, this only enforces the *fields*, not the code, unless asked.
 */
export function expectValidErrorEnvelope(body: unknown, expectedCode?: string): void {
  expect(body).toBeTypeOf("object");
  expect(body).not.toBeNull();
  expect(body).toHaveProperty("error");

  const err = (body as { error: Record<string, unknown> }).error;
  for (const key of ERROR_ENVELOPE_KEYS) {
    expect(err, `error envelope missing key "${key}"`).toHaveProperty(key);
  }

  expect(typeof err.code).toBe("string");
  expect(typeof err.message).toBe("string");
  expect((err.message as string).length).toBeGreaterThan(0);
  expect(typeof err.retryable).toBe("boolean");
  expect(typeof err.requestId).toBe("string");
  expect((err.requestId as string).length).toBeGreaterThan(0);
  expect(err.upstreamStatus === null || typeof err.upstreamStatus === "number").toBe(true);

  // timestamp must be a real, parseable instant (ISO-8601-ish per plan.md's example).
  expect(Number.isNaN(Date.parse(err.timestamp as string))).toBe(false);

  if (expectedCode !== undefined) {
    expect(err.code).toBe(expectedCode);
  }
}

/**
 * Structural groundedness check (CLAUDE.md LLM-guardrail-adjacent discipline, applied here to
 * the proxy's own error messages per plan.md §2.5: "never the raw Touchless response body,
 * never a stack trace. PII never appears in this field."):
 *
 * - `message` must not contain any of the caller-supplied `forbiddenSubstrings` verbatim
 *   (e.g. a raw vendor response body, a borrower name planted in a mocked upstream payload).
 * - `message` must not contain an SSN-shaped substring, as a generic PII tripwire independent
 *   of whatever specific fixture data a given test happens to use.
 */
export function expectMessageIsSafe(body: unknown, forbiddenSubstrings: string[] = []): void {
  const message = (body as { error: { message: string } }).error.message;
  for (const forbidden of forbiddenSubstrings) {
    expect(message).not.toContain(forbidden);
  }
  expect(message).not.toMatch(/\d{3}-\d{2}-\d{4}/); // SSN-shaped
  expect(message).not.toMatch(/^[[{]/); // not a raw dumped JSON/array body
}
