# Quickstart: Real-Engine Audit Run

## Prerequisites

- `backend/.env` has real Touchless QA credentials (already set up per `020`).
- `demo/touchless/` ported into this worktree (Phase 0 of this feature — see plan.md).
- `frontend/src/data/goldCatalog.json` present and current (from `019`).

## Run the demo end-to-end

```bash
# Terminal 1 — backend proxy (spec 020, extended by this feature)
cd backend && npm run dev   # http://localhost:4000

# Terminal 2 — frontend
cd frontend && npm run dev  # http://localhost:3000
```

1. Open the Loan Queue — confirm 20 loans total, 19 showing `PASS`, 1 showing its actual status.
2. Open the one real demo loan (`applicationId = 0eb57730-6d2e-4a6d-8db3-bc1217c77b90`).
3. Click "Pull Application." Confirm the loan populates from a real Touchless fetch (per `020`,
   unchanged by this feature).
4. Without any further click, confirm the loan's status shows `RUNNING`.
5. Within a few seconds, confirm the status resolves to `PASS`, `FAILED`, or `NEEDS_REVIEW` —
   never silently defaulted.
6. Open the Exceptions view and confirm the specific failing/flagged checks are listed, each
   traceable to a real gold rule.
6a. Click each exception's citation. Confirm a real document opens (via `020`'s
   `RetrievedDocumentViewer`, not the old placeholder "PDF page render placeholder" text) — and
   for any exception whose check spans multiple real documents (e.g. `URLA_1003_final`), confirm
   each matched document appears as its own separately clickable link (SC-008, FR-013).
7. Click "Restore to Gold." Confirm both the ruleset draft (if edited) and the fetched loan/verdict
   are cleared — the app matches a fresh load.
8. Open the Routes screen. Confirm 4 routes total: Conventional, FHA, VA, USDA — each with a
   non-zero check count shown identically to Conventional's real count.

## Verify the compiled ruleset independently (SC-002)

```bash
cd p0
python3 qc_engine/run_touchless_audit_for_demo.py \
  --loan ../demo/touchless/extracted/loan_application.json \
  --ruleset-out /tmp/audit021_ruleset.json
```

Compare the printed `loanStatus`/`runResult` against what the UI displayed in step 5 above — they
must match exactly (SC-002).

## Verify the queue-suppression rule (SC-006)

Force an error path (e.g. temporarily point `TOUCHLESS_BASE_URL` at an unreachable host, or kill
the backend mid-run) and confirm the Loan Queue grid renders with zero error badges, while the
loan detail view or an inline message at the fetch trigger does show the error.
