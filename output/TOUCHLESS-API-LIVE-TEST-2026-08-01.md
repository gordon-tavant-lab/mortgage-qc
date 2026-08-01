# Touchless API — Live Test: `documentId` vs `indexedDocId`

**Date:** 2026-08-01
**Purpose:** Resolve Tier-1 Question C from `output/TOUCHLESS-API-QUESTIONS-2026-07-30.md` before
committing to the citation-retrieval design in the new Touchless-API-integration spec: does the
`documentId` already present in `loan_application.json`'s `documents[]` array work directly against
the API's `indexedDocId`-keyed document-read endpoints, or is a separate ID-mapping/lookup step
required?

**Method:** Live call against the QA environment using the credentials already committed at
`docs/architecture/api/TLP-QA-QC-Creds.postman_environment` (`QAGateway =
https://qa-touchless.tavant.com`, `client_id` redacted here — see `backend/.env`). These are
QA/test-tier credentials, not production secrets.

- `applicationId` under test: `0eb57730-6d2e-4a6d-8db3-bc1217c77b90` (the same loan as
  `demo/touchless/extracted/loan_application.json`)
- `documentId` under test: `632a9c26-d636-4564-b89d-256a5dfe70d4` (first entry in that file's
  `documents[]` array — `documentType: "Credit Report"`, `documentSource: "LOS"`)

---

## Finding 1 — The undefined `BaseURL` gap is resolved: it equals `QAGateway`

`docs/architecture/api/TLP-QA.postman_collection.json`'s OAuth Login request references
`{{BaseURL}}`, which has no value in the paired environment file (only `QAGateway` is defined). Live
test:

```
POST https://qa-touchless.tavant.com/userservice/oauth/token?grant_type=client_credentials
Authorization: Basic (client_id:client_secret)
```

**Result: `200 OK`.**
```json
{"access_token":"a071c8c9-4196-486d-901e-6fb703e7196a","token_type":"bearer","expires_in":59999,"scope":"write"}
```

`BaseURL` and `QAGateway` are the same host in the QA environment — the OAuth endpoint lives on the
same gateway as everything else. No separate host is needed. (Not yet confirmed whether this holds
in a production environment, where OAuth is sometimes split to a dedicated auth host — worth a
one-line confirmation from the vendor before assuming this generalizes.)

## Finding 2 — `documentId == indexedDocId`, confirmed for this document

```
GET https://qa-touchless.tavant.com/store/documents/read/632a9c26-d636-4564-b89d-256a5dfe70d4
Authorization: Bearer <token>
```

**Result: `200 OK`**, `content-type: application/pdf`, `content-length: 93587`. Body starts with a
valid `%PDF-1.7` header and contains real embedded content (CoreLogic Credco order-lookup links) —
this is a genuine, retrievable PDF, not an error page or empty stub.

```
GET https://qa-touchless.tavant.com/store/documents/read/632a9c26-d636-4564-b89d-256a5dfe70d4/ocr
Authorization: Bearer <token>
```

**Result: `200 OK`**, `content-type: text/plain` (JSON body), `content-length: 7715`, **110 extracted
fields**. The extracted borrower (`Borrower_First_Name: "ANDY"`, `Borrower_Last_Name: "AMERICA"`,
`Borrower_SSN: "999-60-3333"`) matches the same synthetic borrower already in
`loan_application.json` — confirming this document is genuinely linked to the loan we already have,
not a coincidentally-valid but unrelated ID.

**Conclusion: the `documentId` field already present on every `documents[]` entry can be passed
directly as `indexedDocId` to both the raw-document and OCR endpoints — no separate lookup/mapping
call is required.** This directly unblocks the citation-retrieval design: a citation button can call
`GET /store/documents/read/{documentId}` (or `/ocr`) using the `documentId` already on hand, with no
intermediate resolution step.

**Caveat — tested on one document only.** This confirms the mapping for one `Credit Report` PDF on
one loan. It has not been spot-checked across other `documentType`s (Note, Appraisal, Closing
Disclosure, etc.) or another `applicationId`. Treat "documentId == indexedDocId, universally" as
strongly supported, not proven, until 2-3 more documents are spot-checked — cheap to do once the
spec's proxy layer exists.

## Finding 3 — The live response reproduces the exact confidence-scale problem already flagged

Distribution across the 110 returned fields:

| Confidence | Field count |
|---|---|
| 0.0 | 78 |
| 10.0 | 1 |
| 80.0 | 1 |
| 100.0 | 26 |
| **102.0** | **4** |

This is a live reproduction of Tier-2 Q E from the vendor-questions doc (confidence values above
100, no documented scale) — not a one-off in the sample file we were handed. The four `102.0` fields
here are `Borrower_Address_City`, `Borrower_Address_State`, `Borrower_Address_Zip`, all populated and
plausible-looking, so `102` does not obviously correlate with an error condition. Also notable:
`CoBorrower_First_Name` returned `"CoreLogic"` and `CoBorrower_Last_Name` returned `"(TUC"` — clearly
mis-extracted (bled over from a report-header disclaimer, not an actual co-borrower name) — but
correctly flagged at `confidence: 0.0`. That's a reassuring data point: at least in this sample, junk
extractions *did* get a low score, even though the scale's upper bound is still unexplained.

## Implication for the spec

- The citation-retrieval feature (Q5 in the interview) can be scoped as originally intended:
  `documentId` from the loan's `documents[]` list is sufficient input, with **no ID-mapping
  dependency** blocking the design. Remove that as an open blocker; keep the confidence-scale
  question as a separate, already-tracked open item (Tier-2 Q E) — unaffected by this test.
- OAuth against the QA tier works with `BaseURL = QAGateway`; the backend proxy (per the "small
  backend proxy" decision) can hardcode this for QA and just needs the equivalent value confirmed
  for whatever environment is used at demo time.
