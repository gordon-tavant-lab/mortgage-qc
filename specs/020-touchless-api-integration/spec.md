# Feature Specification: Touchless API Integration (Pull Application + Document Citation Retrieval)

**Feature Branch**: `020-touchless-api-integration`
**Created**: 2026-08-01
**Status**: Draft
**Input**: User description: "we should start a new spec to document to implement this api, we will
need to extract a loan applicationID=0eb57730-6d2e-4a6d-8db3-bc1217c77b90 and its subsequent
documents (documentId). a button will trigger the transmission of the application. and citation
links or buttons will retrieve the exact documents from the api by documentId." Refined through an
interactive grilling session (2026-07-31 → 2026-08-01) that resolved scope, security, and a
technical risk via a live API test — see Assumptions and `output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pull a known loan application from Touchless on demand (Priority: P1)

A reviewer or demo operator, viewing a loan they already know the `applicationId` for, clicks a
button to fetch that application's current data directly from Touchless — replacing today's
static-fixture-only view with a real, on-demand pull, routed through a backend proxy so vendor
credentials never reach the browser.

**Why this priority**: This is the core value of the whole feature — proving the real API
integration works end-to-end for a known loan, independent of any citation or toggle behavior.
Every other story depends on this one existing first.

**Independent Test**: Trigger the pull for `applicationId = 0eb57730-6d2e-4a6d-8db3-bc1217c77b90`
and confirm the loan detail view populates from a genuine network call to Touchless (observable via
the proxy), not from `demo/touchless/extracted/loan_application.json` — deliverable and
demonstrable with no citation-retrieval or toggle work built yet.

**Acceptance Scenarios**:

1. **Given** a known `applicationId` and no data pulled yet this session, **When** the reviewer
   clicks the pull button, **Then** the loan detail view populates with that application's current
   Touchless data, fetched through the backend proxy.
2. **Given** an application has already been pulled once this session, **When** the reviewer
   navigates away and back to the same loan, **Then** the previously pulled data is shown without a
   new network call (no silent re-fetch).
3. **Given** the pull fails (network error, expired auth, unknown `applicationId`), **When** the
   reviewer clicks the pull button, **Then** a clear error is shown and no stale or fixture data is
   silently substituted in its place.

---

### User Story 2 - Retrieve the exact source document behind a citation (Priority: P2)

A reviewer looking at a cited value (e.g., a field pulled from a Credit Report) clicks a citation
link/button tied to that document's `documentId` and sees the *actual* document Touchless returns —
the real PDF and/or its real extracted-field data — rather than today's themed, simulated document
viewer.

**Why this priority**: This closes the traceability loop that citations exist for — a citation
pointing at hardcoded mock content isn't a real citation. It depends on User Story 1 existing (a
pulled application supplies the `documentId`s to click), so it's second.

**Independent Test**: With an application already pulled (or its known `documents[]` list
available), click a citation tied to a specific `documentId` and confirm the real document content
(PDF bytes and/or OCR field data) is fetched and displayed, distinguishable from the existing
simulated viewer's placeholder content.

**Acceptance Scenarios**:

1. **Given** a document's `documentId` from a loan's document list, **When** the reviewer clicks its
   citation, **Then** the system fetches and displays that document's real content from Touchless.
2. **Given** the same `documentId` is clicked twice, **When** the second click occurs, **Then** the
   system MAY reuse the already-fetched content rather than re-fetching (consistent with
   fetch-once-per-session behavior).
3. **Given** a `documentId` that the API rejects or returns unexpected content for, **When** the
   reviewer clicks its citation, **Then** a clear error is shown rather than blank or incorrect
   content silently standing in.

---

### User Story 3 - Toggle between stored and live data for demo/testing (Priority: P3)

A demo operator (Gordon) can flip a single, session-wide switch — tucked a few clicks deep in the
main navigation, not on the loan detail screen itself — between "Stored" (the existing static
fixture) and "Live" (real Touchless API) as the active data source, so a demo or test session can
deliberately choose predictable fixture data or real live behavior without needing two separate
builds.

**Why this priority**: Valuable for control over demo/testing but not required for the other two
stories to deliver value on their own — hence lowest priority.

**Independent Test**: Flip the toggle to Live, pull an application, confirm the loan detail view
reflects live data; flip back to Stored and confirm it reverts to the static fixture — testable
independently of the citation-retrieval work in User Story 2.

**Acceptance Scenarios**:

1. **Given** the toggle is set to "Stored", **When** a loan is viewed, **Then** it shows the static
   fixture data exactly as today.
2. **Given** the toggle is flipped to "Live", **When** a loan is viewed and pulled, **Then** it shows
   data fetched from Touchless instead.
3. **Given** a toggle choice has been made, **When** the browser session ends and a new one begins,
   **Then** the choice resets to the default (Stored) rather than persisting.

### Edge Cases

- What happens when a live pull (application or document) fails partway — network timeout, expired
  bearer token, or an unknown/rejected ID? The system must show a clear error, not a blank screen or
  a silent fallback to stored data.
- What happens when the reviewer switches the toggle to "Live" but hasn't pulled anything yet this
  session? The view should prompt for an explicit pull rather than showing empty or stale content.
- What happens when a citation's `documentId` returns a content type or shape the viewer doesn't
  expect (e.g., not a PDF, or an OCR response with zero fields)? Shown as a distinct error state, not
  treated as a successful empty result.
- What happens when the assumption that `documentId` works directly as the API's document-lookup key
  (verified for one document type, see Assumptions) doesn't hold for some other document type? The
  failure must be visible and attributable to that specific document, not silently swallowed.
- What happens if the vendor's OAuth token expires mid-session? The proxy must detect and surface an
  auth failure distinctly from a "document not found" failure, so the reviewer knows to retry rather
  than assume the document doesn't exist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a user to trigger, via a button, an on-demand pull of a loan
  application's data from Touchless for a known `applicationId`, routed through a backend proxy —
  the browser MUST NOT call Touchless directly.
- **FR-002**: The backend proxy MUST hold Touchless authentication credentials server-side only;
  they MUST NOT appear in any browser-delivered code, bundle, or client-visible network request.
- **FR-003**: System MUST provide a single, session-wide control — placed in the main navigation
  behind a few clicks rather than on the loan detail screen — to toggle the active data source
  between "Stored" (existing static fixture) and "Live" (Touchless API).
- **FR-004**: The data-source toggle's chosen state MUST persist only for the current browser
  session; it MUST reset to "Stored" on a new session and MUST NOT be encoded in a shareable URL.
- **FR-005**: When in "Live" mode, pulling a given `applicationId` MUST fetch once and hold the
  result for the remainder of the session; refreshing it requires an explicit, separate re-pull
  action — no automatic or silent re-fetching.
- **FR-006**: System MUST allow retrieval of a specific document's content given its `documentId`,
  via a citation link/button, routed through the same backend proxy.
- **FR-007**: Document retrieval MUST use the `documentId` already present on a loan's document list
  as the lookup key against Touchless's document-read endpoint, without requiring a separate
  ID-mapping step (see Assumptions — verified live for one document/type).
- **FR-008**: System MUST display the actual retrieved document content (the real fetched bytes)
  to the reviewer, visibly distinct from today's simulated/themed document viewer content.
- **FR-009**: System MUST also make the retrieved extracted-field data (name, value, confidence)
  available alongside the document view, to support the citation's context.
- **FR-010**: Data pulled or retrieved by this feature MUST NOT feed the deterministic QC engine's
  check evaluation in this pass — it is display-and-citation-only (see Assumptions for why, and what
  would need to be true before that changes).
- **FR-011**: Wherever pulled data is shown, the system MUST clearly indicate which data source
  (Stored vs. Live) is currently active, extending the existing "this is sample data" banner pattern
  rather than introducing an unrelated new indicator.
- **FR-012**: The system MUST surface a clear, non-crashing error whenever a live pull (application
  or document) fails, and MUST NOT silently substitute stored/fixture data in place of a failed live
  request.
- **FR-013**: This feature MUST NOT introduce any new persistent storage of pulled data beyond
  in-session memory — no new database, and no new on-disk retention beyond what already exists in
  this codebase today.

### Key Entities

- **Pulled Application**: A Touchless application payload fetched on demand for a known
  `applicationId`, held in session memory, tagged with which data source (Stored/Live) it came from
  and when it was fetched.
- **Document Reference**: An entry in a loan's document list (its `documentId`, document type,
  source, etc.) — the same shape the existing static fixture already provides.
- **Retrieved Document**: The actual content fetched for one `documentId` — its real bytes/content
  and, where available, its extracted-field data — shown in the citation viewer in place of
  simulated content.
- **Data Source Mode**: The session-scoped choice (Stored or Live) controlling which application
  data feeds the loan detail view.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can pull a known loan's live application data and see it reflected in the loan
  detail view within 5 seconds of clicking the pull button.
- **SC-002**: A user can view the real document behind any citation in a single action, with content
  that is visibly and verifiably distinct from placeholder/simulated content.
- **SC-003**: Switching the active data source between Stored and Live takes no more than 3
  actions from the main screen, and the control is not visible in the primary navigation.
- **SC-004**: 100% of failed live-data requests (application-level or document-level) surface a
  visible, distinguishable error to the user — none silently show blank or stale content.
- **SC-005**: Zero instances of Touchless credentials appearing in any browser-visible network
  request or client bundle, verifiable by direct inspection.

## Assumptions

- **Pull-only, no push.** This spec covers fetching data FROM Touchless only. It does not add any
  capability to upload or submit documents/applications TO Touchless — that remains Touchless's own
  extraction pipeline, untouched by this project (Non-Negotiable #2).
- **Display/citation-only, not wired into the QC engine.** Pulled application and document data in
  this pass feeds the loan detail view and the citation viewer only — it does not become input to
  any deterministic check evaluation. The sample data available today reads like a live, mutable,
  mid-underwriting record rather than a guaranteed immutable post-closing snapshot, and several
  vendor questions about that (`output/TOUCHLESS-API-QUESTIONS-2026-07-30.md`, Tier-1 Qs A/B/D)
  remain open. Wiring pulled data into real verdicts is explicitly deferred to a follow-on spec once
  those are answered, to avoid violating Non-Negotiable #1 (same loan → same verdict, every time).
- **`documentId` doubles as the API's document lookup key.** Verified live on 2026-08-01 for one
  Credit Report document on `applicationId 0eb57730-6d2e-4a6d-8db3-bc1217c77b90` — both the raw
  document and its extracted-field data were retrieved successfully using the `documentId` already
  present in the loan's document list, with no separate ID-mapping call required (see
  `output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md`). Treated as the default behavior for all document
  types; not yet spot-checked beyond this one case, so a graceful, visible failure path is required
  per FR-012/Edge Cases rather than assuming universal success.
- **Existing QA/test credentials are sufficient for this build.** The credentials already committed
  in this repo (`docs/architecture/api/TLP-QA-QC-Creds.postman_environment`) are QA-tier and were
  used to verify the above. Production credential provisioning, rotation, and any related compliance
  handling are out of scope for this spec.
- **The toggle needs no dev-only gating.** It's a demo/testing convenience, tucked a few clicks deep
  in the nav for visual tidiness, not a security boundary — it may ship in any build.
- **Document rendering fidelity is a planning-stage decision, not fixed here.** The retrieved
  document must be shown as genuine sourced content rather than the existing simulated content;
  whether that means full in-browser PDF paging/highlighting or a simpler native embed is left to
  the implementation plan, with a bias toward the simplest option that still shows real content in
  this first pass.
- **No new persistent storage.** Pulled data lives in browser/session memory; the backend proxy is
  effectively stateless per request (aside from short-lived token handling), consistent with this
  project's existing flat-files-only constraint.
- **Three-source reconciliation is unaffected.** This spec adds a new way to fetch the same kind of
  data the static fixture already represents (application + document data); it does not add MISMO
  XML retrieval or change how the three sources (document/LOS/MISMO) are reconciled against each
  other (Non-Negotiable #3).
