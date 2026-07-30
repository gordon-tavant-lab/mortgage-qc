# 013 — src/ PoC proceeds without SME sign-off gating progress

**Status:** Accepted 2026-07-29 (Gordon: "for this src/ poc, we don't [need] an expert
to agree")

## Decision
Inside `src/`, the triage classifications (GREEN/YELLOW/RED) and guide citations are
treated as good enough to keep building on *without* waiting for Kayla or another SME
to formally sign off each one. The `SME: ☐ agree ☐ correct` checkboxes in the review
packets stay — they're still the right mechanism for eventual validation — but they do
not block this PoC's own progress.

## Why
This is consistent with [[001]] (src/ is a low-risk sandbox) and with the project's
top-level Known Blocker 2 framing: SME validation is required before **production**
trust, not before **exploring** whether the architecture is viable at all. Gating a PoC
on an expert's calendar defeats the purpose of a fast sandbox.

## What does NOT change
- The packets are still generated in SME-reviewable form (source row citations, guide
  citations, plain rationale) — so when a real validation pass happens, no rework is
  needed.
- Nothing in `src/` claims production trust. Every run output, decision doc, and the
  journal say "pending SME review" / "proposal" — that language stays accurate even
  though no SME has reviewed yet.
- If/when this graduates out of `src/`, real SME sign-off becomes mandatory again
  (per [[001]]'s graduation clause).
