## COMPLIANCE REVIEW — Touchless API Integration (020-touchless-api-integration)

**Reviewed artifact:** `specs/020-touchless-api-integration/spec.md` (Draft, quality-checklist passed).
**Plan status:** `specs/020-touchless-api-integration/plan.md` does **not exist yet** — the
architect's plan has not landed. This review is therefore a **spec-level MVP compliance pass**,
not a plan-level one. Item 4 below (credential handling) is flagged against the repo's *current
working-tree state*, which is independent of the plan and needs no plan to evaluate. All other
findings should be re-checked once the plan lands, specifically against the conditions listed
under BLOCKING/RISK ACCEPTED below — this document does not need to be re-run from scratch, just
re-verified against those specific points.

### Regulatory Applicability

- **Applicable:**
  - **GLBA Safeguards Rule** — this pathway carries nonpublic personal information (NPI) once
    "Live" mode is used against real applications: SSN, DOB, address, income/liability detail.
    Applies regardless of today's fixture being synthetic (`999-60-3333` / "Andy America"),
    because the architecture itself is what's in scope for this review, and it will carry real
    NPI unchanged the day a real `applicationId` is used.
  - **General data-minimization principle** (the spirit underlying GLBA, CCPA/CPRA, and this
    project's own flat-files-only posture) — relevant to the "no new persistent storage" design
    choice (FR-013).
  - **CCPA/CPRA** — light applicability if any California consumer's data transits this pathway;
    the in-memory/session-only design is directly aligned with data-minimization/no-unnecessary-
    retention principles CCPA cares about, so this is a point in the design's favor, not a gap.
- **Not applicable (with justification):**
  - **ECOA/Reg B, FCRA** — no credit decisioning, adverse-action output, or scoring is produced by
    this feature; it is a read-only display/citation pathway (FR-010).
  - **SR 11-7 (Model Risk Management)** — no model is introduced. This proxy adds zero new LLM/AI
    calls, confirmed by inspecting the spec's Requirements and Assumptions; the LLM guardrail
    policy in `CLAUDE.md` / `docs/LLM-GUARDRAIL-POLICY.md` does not newly apply.
  - **PCI-DSS** — no cardholder data is in scope for this pathway.
  - **HMDA/TILA/RESPA** — no disclosure generation or HMDA-reportable field production occurs here;
    this feature only displays data the LOS/Touchless side already owns.
  - **BSA/AML, SOX** — no transaction monitoring or financial-controls surface is touched.

### BLOCKING (cannot ship without resolution)

1. **A live, plaintext vendor secret is sitting in the working tree, uncovered by `.gitignore`, one `git add` away from permanent git history.**
   `docs/architecture/api/TLP-QA-QC-Creds.postman_environment` contains `client_id: <REDACTED-QA-CLIENT-ID>` and
   `client_secret: <REDACTED-QA-SECRET>` in cleartext. It currently shows as untracked (`?? docs/architecture/api/`)
   in `git status` and is **not** matched by any pattern in `.gitignore` — the existing
   `*credentials*` glob does not match a file named `*Creds*`. `git log --all -- docs/architecture/api/`
   confirms it has not yet been committed, so this is still fully preventable. Once committed,
   purging a secret from git history requires a history rewrite (and, properly, credential
   rotation) — treat this as materially harder to fix later than now.
   Required action: before any implementation work lands, either (a) add a `.gitignore` rule that
   actually matches this file (e.g. `*.postman_environment` or the literal path under
   `docs/architecture/api/`), or (b) relocate the file to a path already covered by an existing
   ignore rule, or (c) remove the live secret value from the committed reference (replace with a
   placeholder and document out-of-band where the real QA secret lives — e.g., a local-only file
   or secrets manager). This is independent of whether the plan has landed and should be fixed
   immediately regardless of this feature's implementation timeline.
   Required action (secondary, lower urgency since QA-tier): consider rotating `<REDACTED-QA-SECRET>` once
   the file is no longer floating uncommitted in a shared workspace, since it has already been
   visible in a working tree without git protection. Not a hard blocker given QA-tier scope, but
   flag to whoever owns the Touchless relationship.

2. **Session-memory implementation must not silently become durable client-side storage.**
   FR-004 requires the data-source toggle to reset to "Stored" on a new browser session and never
   persist across sessions; the Assumptions describe pulled data as living in "browser/session
   memory." `sessionStorage` and in-process JS state satisfy this (both clear on tab/browser
   close); `localStorage` does **not** — it survives browser restarts and would silently convert
   this feature's "no new retention" design into an actual new client-side retention point holding
   NPI (SSN, DOB, address) once Live mode pulls a real loan. This is exactly the kind of gap this
   review exists to catch: the spec's *intent* is airtight, but the implementation choice that
   satisfies FR-004/FR-013 vs. quietly violates them is a single API call's difference.
   Required action: when the plan lands, confirm explicitly which browser storage mechanism is
   used for pulled application/document data and the toggle state. Anything other than in-memory
   JS state or `sessionStorage` must be treated as a new retention obligation and escalated back to
   this review before shipping.

3. **Server-side proxy logging must not become an undocumented retention channel.**
   The spec correctly scopes "no new persistent storage" to databases and on-disk retention
   (FR-013), but does not yet say anything about the backend proxy's own request/access/error
   logs. A common real-world gap: a proxy that logs full request/response bodies (or stack traces
   that embed a response body) at the application or web-server layer creates NPI retention that
   was never designed for, reviewed, or retention-scheduled — and would sit completely outside
   this spec's stated scope boundary while still being a real GLBA safeguarding concern.
   Required action: when the plan lands, confirm the proxy's logging strategy explicitly excludes
   full request/response bodies for the loan-application and document-content endpoints (structured
   metadata only — e.g., `applicationId`, status code, latency — never SSN/DOB/address/document
   bytes). If any logging framework used by default logs bodies (common in some HTTP middleware
   stacks), it must be explicitly disabled or redacted for these three routes.

### RISK ACCEPTED (document and proceed)

1. **Production credential provisioning is deferred by design.**
   Residual risk: this spec explicitly scopes only QA-tier credentials
   (`docs/architecture/api/TLP-QA-QC-Creds.postman_environment`, `client_id=<REDACTED-QA-CLIENT-ID>`); production
   credential issuance, rotation policy, and any related vendor-side compliance handling
   (encryption of credentials at rest in a secrets manager, least-privilege scoping, rotation
   cadence) are not addressed here.
   Mitigation: the spec's own Assumptions state this boundary plainly, and Finding BLOCKING-1 above
   closes the immediate exposure of the QA secret itself. Before this pathway is ever pointed at
   production Touchless credentials, a follow-on spec or a dedicated secrets-management review must
   gate that change — this should not happen as an incidental config swap inside an unrelated
   future feature.
   Accepted by: engineering lead / whoever owns the Touchless vendor relationship, to confirm before
   any production-credential cutover spec is opened.

2. **Real NPI will flow through this pathway once "Live" mode is used against a real loan, with no new masking/redaction control introduced by this spec.**
   Residual risk: today's fixture (`applicationId 0eb57730-…`) is synthetic ("Andy America",
   `999-60-3333`), so no real NPI is at risk yet, but the architecture this spec builds is the same
   architecture that will carry real SSN/DOB/address the first time a real `applicationId` is
   used in Live mode. No masking, partial-display (e.g., last-4-of-SSN), or role-based access
   control is introduced by this spec to gate who can see a full SSN once real data flows.
   Mitigation: this is consistent with the spec's own stated scope (display/citation-only, MVP),
   and the existing app has presumably already made this same call for however it displays the
   static Touchless fixture today (this review did not re-audit that existing display path — flag
   for a human check if it hasn't been reviewed before). No new masking control is being requested
   as a blocking condition for *this* spec, since it neither improves nor worsens the pre-existing
   NPI-display posture of the loan detail view — but this should be revisited explicitly the moment
   this feature is used against real (non-synthetic) loan data, not left as an implicit assumption.
   Accepted by: product owner (Gordon), to confirm this is genuinely unchanged risk vs. today's
   fixture-only display, not a new exposure this feature introduces.

### COMPLIANT (no issues found)

- **No new persistent PII storage, as scoped (FR-013, Assumption "No new persistent storage").**
  The spec is explicit that pulled data lives in browser/session memory only and the proxy is
  stateless aside from short-lived token handling — this is a proportionate, correctly-scoped MVP
  design that does not create a new data-retention obligation, *contingent on* BLOCKING items 2
  and 3 above being confirmed once the plan lands (both are implementation-detail risks to the
  spec's own stated intent, not disagreements with the intent itself).
- **Audit-trail consistency with the constitution's Audit gate.**
  The constitution requires every doc-sourced value be traceable (doc name + page + segment). This
  feature's citation-retrieval design — fetching the *actual* PDF/OCR content by `documentId`
  rather than today's simulated viewer — is directly in service of that same traceability
  principle, not a competing one. Because FR-010 keeps this data out of the deterministic engine's
  evaluation path, it never produces a `CheckResult`/`LoanEvaluation`, so there is no risk of this
  feature's output being *mistaken for* an audited verdict at the data-model level. The one thing
  that must hold at the **UI** level (not re-litigating FR-010's boundary, just confirming its
  presentation is airtight): the citation viewer and pulled application view must not adopt any
  visual language (e.g., a pass/fail badge, a checkmark, a "cleared" label) that a reviewer could
  mistake for a QC verdict — it is source content, not a determination. This is a presentation
  concern to keep in mind during design review (`design:design-critique`, per `CLAUDE.md`'s
  design-skill guidance), not a blocking finding, since the spec's stated intent is already correct.
- **Data-source transparency, FR-011.**
  Explicitly extending the existing `SampleDataBanner.tsx` pattern (`frontend/src/components/SampleDataBanner.tsx`)
  rather than inventing a new indicator is the right call — it reuses a pattern reviewers already
  recognize, satisfying a reasonable "know what you're looking at" governance bar: a reviewer must
  never mistake demo/fixture data for a real live pull, or vice versa. No gap found in the spec's
  requirement language (FR-011, FR-003/FR-004 session-scoping); implementation fidelity to this
  requirement should be re-checked once the plan lands, but the *requirement* itself is sound.
- **No push/write capability introduced (Assumption "Pull-only, no push").**
  Consistent with Non-Negotiable #2 (build the core, assume the periphery) — this feature does not
  expand this project's footprint into Touchless's own extraction/write pipeline.
- **Error handling avoids silent fallback (FR-012, SC-004).**
  Requiring a visible, distinguishable error rather than a silent substitution of stale/fixture
  data is the correct posture for a regulated-industry tool — a silently-wrong data source shown to
  a reviewer as if it were current is a worse failure mode than a visible error, and the spec
  already treats it that way.
- **Credentials-in-transit.** The QA gateway endpoint is HTTPS
  (`https://qa-touchless.tavant.com`), and the backend-proxy architecture (FR-001/FR-002) correctly
  keeps the vendor bearer token and OAuth client secret out of the browser entirely — no
  browser-visible network request will carry the credential. This satisfies SC-005 as scoped, once
  BLOCKING-1 (the repo-level secret exposure, a separate issue from the *runtime* architecture) is
  resolved.

---

### Overall Verdict: **PASS-WITH-CONDITIONS**

The spec's design intent is sound and proportionate for an MVP: no new LLM/AI surface, no new
persistent storage, a stateless proxy, credentials held server-side, display-only scope correctly
walled off from the deterministic engine, and a transparency mechanism reusing an already-approved
UI pattern. Nothing here requires re-litigating scope or blocking the feature from proceeding to
implementation.

However, ship this MVP feature only once the following are resolved:

1. Fix the credential-file `.gitignore` gap (BLOCKING-1) — **before any further work touches this
   repo**, independent of this feature's own timeline, since the exposure exists today regardless
   of whether Touchless integration code is ever written.
2. When the plan lands, confirm the client-side storage mechanism for pulled data and toggle state
   is in-memory or `sessionStorage`, never `localStorage` or any other durable client store
   (BLOCKING-2).
3. When the plan lands, confirm the proxy's logging configuration excludes full request/response
   bodies for the three Touchless-backed routes (BLOCKING-3).
4. Before real (non-synthetic) loan data is ever pulled through this pathway, revisit RISK-ACCEPTED-2
   with the product owner explicitly, rather than letting it happen as an implicit side effect of
   flipping the Live toggle on a real `applicationId`.
5. Treat production credential provisioning (RISK-ACCEPTED-1) as requiring its own gate — a
   follow-on spec or a dedicated secrets-management review — never a silent config swap.

Everything else reviewed (audit-trail framing, data-source transparency, no-push scope, error
handling posture) is compliant as specified and needs no further compliance action beyond normal
implementation fidelity checks once the plan and code land.

---

## Phase 8 Re-Verification (2026-08-01, against shipped code)

Performed directly against the actual implementation (the automated compliance re-verification
sub-agent failed 3 times on a repeated infrastructure connection error; this was done by reading
the shipped code directly instead of retrying further).

- **BLOCKING-2 (storage mechanism) — RESOLVED, confirmed.** Read `frontend/src/lib/dataSourceContext.tsx`
  directly: pulled applications, retrieved documents, the active mode, and all error state live in
  React `useState`/`Map`/`Set` — no `localStorage`, no `sessionStorage`, no persistence of any kind.
  A page reload discards everything, exactly the "no durable client store" requirement.
- **BLOCKING-3 (logging excludes full bodies) — RESOLVED, confirmed.** Read `backend/src/middleware/requestLogger.ts`
  directly: logs are metadata-only (method, route template, status, latency, correlation id) — no
  request or response body is ever passed to `console.log`, on any of the three Touchless-backed
  routes.
- **BLOCKING-1 (credential-file `.gitignore` gap) — RESOLVED, confirmed.** Already covered under
  the security re-verification above; the same fix satisfies this compliance item.
- **RISK-ACCEPTED-2 (real loan data via the Live toggle)** — unchanged from Phase 3: this remains a
  standing product-owner decision point, not something Phase 8 code review can close on its own.
  Flagging again here so it isn't lost: the toggle and proxy are built to work identically whether
  `applicationId` belongs to synthetic or real data — nothing in the code distinguishes them. That
  is correct given the spec's scope, but it means the human decision to actually point this at a
  real loan is the only remaining control.
- **FR-013 (no new persistent storage)** re-confirmed by the same in-memory-only finding above —
  the backend proxy itself is also stateless per-request (aside from the in-memory OAuth token
  cache, which holds no PII, only a vendor bearer token).

**Compliance re-verification verdict: PASS**, both BLOCKING-2 and BLOCKING-3 resolved. No new
compliance finding surfaced by the implementation beyond what Phase 3 already flagged.
