# Contract: Audit Run Endpoint

New route, same backend as `020`'s existing proxy — added to `server.ts`'s route mounting
alongside `applicationsRouter`/`documentsRouter`.

## `POST /api/audit/:applicationId/run`

Triggers a real deterministic-engine evaluation of an already-pulled application. Reuses `020`'s
existing `isValidUuid()` guard and error-envelope shape (`ErrorCode`/`ErrorEnvelope` from
`backend/src/errors.ts`) rather than inventing a parallel error format.

### Request

- Path param `applicationId`: must be a valid UUID (same guard as `020`'s
  `applications/:applicationId/pull`), and must correspond to an application already pulled this
  session (the route reads the already-fetched application payload; it does not itself call
  Touchless again).
- No request body.

### Response — 200 OK

```json
{
  "applicationId": "0eb57730-6d2e-4a6d-8db3-bc1217c77b90",
  "evaluatedAt": "2026-08-02T10:15:00Z",
  "loanStatus": "PASS" | "FAILED" | "NEEDS_REVIEW",
  "compiledCheckCount": 11,
  "excludedCheckCount": 197,
  "runResult": {
    "...": "RunResult.to_dict() shape, passed through unmodified",
    "results": [
      {
        "...": "CheckResult fields, unmodified",
        "citation": {
          "docName": "Bank Statement",
          "pageNum": 0,
          "segmentSnippet": "Touchless documents[] presence check",
          "documentIds": ["632a9c26-d636-4564-b89d-256a5dfe70d4"]
        }
      }
    ]
  }
}
```

`compiledCheckCount`/`excludedCheckCount` surface the honest scoping from research.md Item 2 —
the frontend is not required to display these, but they must be present so a reviewer (or a
future spec) can verify the run wasn't silently claiming full 208-check coverage.

`citation.documentIds` (FR-013, research.md Item 8) is the real Touchless `documentId`(s) this
check's evidence resolved against — one entry for most checks, up to 4 for `URLA_1003_final`.
Absent/empty only when a check's evidence field genuinely couldn't be matched to a real document
(should not arise for anything actually compiled in, per Item 2's filtering, but the frontend must
render this honestly rather than assume it never happens). The frontend passes each id straight to
`020`'s existing `GET /api/touchless/documents/:documentId` route via `RetrievedDocumentViewer` —
no new document-fetch endpoint is added by this feature.

### Response — error (reuses `020`'s `ErrorEnvelope` shape)

| Code | When | HTTP status | Retryable |
|---|---|---|---|
| `NOT_FOUND` | `applicationId` was never pulled this session | 404 | false |
| `PROXY_ERROR` | the Python subprocess exited non-zero, timed out, or produced unparseable stdout | 500 | false |
| `INVALID_INPUT` | `applicationId` fails UUID validation | 400 | false |

A `PROXY_ERROR` here is what the frontend maps to the `ERROR` loan-status display state (FR-006a)
— never silently defaulted to `PASS`/`FAILED`/`NEEDS_REVIEW`.

### Non-functional

- Server-side only: the Python subprocess (compiler + adapter + engine) runs on the backend host;
  no engine/vendor logic executes in the browser (Assumption, spec.md).
- Synchronous request/response — the demo's single loan evaluates in well under a second (938
  lines of pure-Python dataclass logic over ~10 checks), so no polling/webhook design is needed for
  this scope. If a future spec needs this for a larger check count or slower path, that's a new
  design point, not assumed here.
