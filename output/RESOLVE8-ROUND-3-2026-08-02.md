# Resolve8 — round 3, a small honest yield (2026-08-02)

Gordon's ask: "can we further reduce NOT_COMPILED (849 → 599 → 439)?"

**Answer: yes, but only by 2 — 439 → 437 (p0), plus 3 parity fixes on the src/SHACL side
that were never about NOT_COMPILED at all. This round's real finding is that the big,
systematic gains are exhausted; what's left is either genuinely blocked (vendor/SME)
or was already reviewed and correctly rejected.**

## Where the 2 new checks came from

Round 2's trigger-gated analysis had already found 23 checks whose trigger is provably
**true** for this loan (not false — the opposite of what drove rounds 1–2), several of
which map to documents already present in the file. That work was captured in the
round-2 analysis artifact but never actually acted on. This round closed that out: read
the full, untruncated rule text for all 23, checked each against its check_type, and
applied one hard rule — **a document-presence check only auto-resolves to PASS when the
defect text is a pure absence statement** ("X is not in the file"). Anything compound —
"...or is unsigned", "...or did not meet all requirements", "...and/or all applicable
addenda", "...or any other method" — cannot be cleared by presence alone, no matter how
confidently the document maps to a real Touchless type.

| Verdict | Count | Why |
|---|---:|---|
| **Wired (PASS)** | **2** | Pure-absence defect, required doc confirmed present, card applicability universal (`QC_Policy=Fannie Mae` only) |
| Rejected — compound defect | 12 | Presence doesn't prove the second clause (signed status, form-requirement completeness, "all applicable addenda", coverage sufficiency) |
| Rejected — wildcard disjunction | 3 | Rule text says "...or any other method"/"other cash flow analysis form" — closed-world absence of one named document type can never disprove an open-ended alternative |
| Rejected — condo/PUD false-positive risk | 2 | Already flagged in round 2: fidelity/crime and GL insurance rules target condo/co-op projects; this loan is a detached PUD — wiring either would risk a fabricated finding, not just a missed PASS |
| Held — ambiguous applicability | 1 | CPA-letter requirement (no condition in the rule text for when one is required) |
| Held — likely misclassified | 1 | "W2s did not cover the years required" is check_type=`doc_presence` but is really a count/sufficiency question, not a presence question — flagged to the SME queue as a reclassification candidate, same pattern as the six rows fixed in round 1 |
| Not actioned (SME-held already) | 4 | The 2 `GATE_TRUE_DOC_PRESENT`/2 `GATE_TRUE_DOC_ABSENT` candidates from round 1's presence-gate analysis (final-URLA PASS, 2×ROV absence findings) — still correctly held for the same reasons stated then (documentType doesn't encode initial-vs-final; unconfirmed whether Touchless's taxonomy even has an ROV type) |

The 2 wired: `PC::O-FNM-15304/O-FNM-58198` (URLA Continuation Sheet — present) and
`PC::O-FNM-15444/O-FNM-50907` (Escrow Instructions — present). Both verified directly
against the payload's `documents[]` before wiring, both compile via the same
`CURATED_DOC_MATCHES` mechanism as every prior curated doc match.

## Cumulative (all 1,105 gold-ruleset checks, loan 12607601215)

| Status | Original audit | resolve6 | resolve7 | resolve8 |
|---|---|---|---|---|
| PASS | 121 | 130 | 131 | **133** |
| NEEDS_REVIEW | 92 | 92 | 92 | **92** |
| NOT_APPLICABLE | 43 | 284 | 443 | **443** |
| NOT_COMPILED | 849 | 599 | 439 | **437** |
| Evaluated | 256 (23%) | 506 (46%) | 666 (60%) | **668 (60%)** |

Per-check diff vs HEAD: exactly 2 × `NOT_COMPILED → PASS`, zero other changes.

## A side finding, fixed along the way (not a NOT_COMPILED reduction)

Auditing this bucket surfaced that `src/shacl_pilot`'s own `CURATED_DOC_MATCHES` was
missing an entry round 1 had already added to `p0` (the Occupancy Affidavit match) —
a parity gap, not a bug in either engine's verdicts, just an un-mirrored curated entry.
Ported all 3 (occupancy affidavit + the 2 new from this round) to keep the two engines
in lockstep. Result: src's PASS count moved 122→125, and jointly-evaluated agreement
moved 121→124 (still 0 disagreements). This is unrelated to NOT_COMPILED — src had its
own, separate NOT_COMPILED count throughout, driven by its own unsupported-check
tracking, not by p0's.

**Left as backlog, deliberately not attempted this round:** the 7 other curated facts
wired into p0 during resolve6/7 (CIP identity match, bank-account-holder match, 2
disjunctive presence facts, CLTV/HCLTV recompute, the ATR-QM threshold) have no SHACL
equivalent yet. Porting them needs new SPARQL/shape wiring in `ruleset_to_shacl.py`,
not a dict addition — real, scoped work, and it doesn't move any NOT_COMPILED count on
either side, so it stays flagged rather than folded into this round.

## Gates

`pytest p0/` 445 passed · `verify_against_defects.py` 25/25 · cross-engine 124 agree /
0 disagree (up from 121) · per-check diff vs HEAD shows only the 2 intended flips.
Deliverables refreshed (audit CSV + 3-sheet xlsx, both copies).

## Is there a round 4?

No — not on the same inputs. This round deliberately exhausted the last bucket of
"already-identified-but-unactioned" candidates from prior analysis, and it confirmed
the honest floor: 21 of 23 reviewed candidates were correctly rejected, most for
reasons this project's grounding discipline exists specifically to catch (compound
defects, wildcard disjunctions, a domain false-positive trap). The 437 remaining
NOT_COMPILED checks split the same way both prior reports already said: ~55
SME-answerable ambiguous rule text (the cheapest real unlock — a Kayla session),
~250 vendor-extraction blocked, ~65 by-design out of scope, ~31 demo exclusions, plus
the handful newly flagged here (1 misclassification candidate, 1 ambiguous-CPA-letter
condition) added to that same SME queue. Further reduction now requires new input from
outside this session, not more analysis of what's already in hand.
