# 005 — Shapes organized as routes → blocks → checks

**Status:** Accepted 2026-07-29 (Gordon)

## Decision
Mirror the project's routes → blocks → checks model (and the block inventory observed in
`docs/research/olav-demo-rules-authoring-architecture.md`) in the SHACL pilot:

- **Check** = one SHACL NodeShape (one rule, one exception code, one severity).
- **Block** = one `.ttl` file per AMQ "Question Category Name" grouping
  (`blocks/application.ttl`, `blocks/assets.ttl`, `blocks/property_appraisal.ttl`, …).
- **Route** = an entry in `routes.json`: a named, ordered list of blocks plus a
  **compiled applicability key** (mortgage type + loan purpose from MISMO).

## Route selection is a lookup table, NOT inference
Per the olav-demo doc's takeaway #4 (its `loan-intake` block re-decides block selection
with an LLM on every loan): here, route selection is a deterministic lookup —
`(mismo_mortgage_type, mismo_loan_purpose) → route_id` — recorded in the audit output
with the matched key, so the audit trail shows which branch fired and why.

## Difference from Olav's blocks
Olav's block payload is an LLM system prompt evaluated at runtime; here a block is a
set of signed-off SHACL constraints executed by a standard validator. The route/block
*organization* is reused; the runtime is not.

## Evidence
- `src/shacl_pilot/blocks/` — 9 block `.ttl` files, 25 `sh:NodeShape` checks total (application 7, property_appraisal 7, assets 2, credit_liabilities 2, product_specific 2, underwriting 2, certification_delivery 1, closing 1, income 1).
- `src/shacl_pilot/routes.json` — per-program routes with deterministic `selection_by_agency` lookup table (current v2 form, evolved by decisions 010/011).
- `src/shacl_pilot/run_audit.py` — detects the agency from the loan's own documents and records the matched route in the run output.
- `docs/research/olav-demo-rules-authoring-architecture.md` — the block-inventory reference this organization mirrors.
