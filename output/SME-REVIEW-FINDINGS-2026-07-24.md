# SME Review Findings — Conditional-Applicability Gap + Operator-Inversion Bug

| | |
|---|---|
| **Date** | 2026-07-24 |
| **Source** | Kayla (SME) + Gordon, live review call of loan 01's QC output (`loan01_with_provenance.json`) against the known answer key |
| **Status** | **Consensus reached on problem space. No plan or code change committed by this document.** |
| **Governs** | Precedes any spec/plan work on this gap. Cross-references `output/ROADMAP.md` features `010a`/`010b`. |

> This document exists because the user's explicit instruction was: surface every fundamental
> technical gap the call raised, get agreement on what "the" systemic issue is, and document that
> agreement — **before** any implementation plan is drafted. Nothing below is a build decision.

---

## 1. The systemic issue (consensus)

**The engine has no mechanism for conditional-applicability gating based on loan-specific facts.**

`p0/qc_engine/compiler/program_gating.py` gates checks by *program* (Fannie/Freddie/VA/USDA/SONYMA,
via `010a`) — a coarse, loan-type-level gate. It does **not** gate by loan-specific *facts*: does
this loan have a gift letter, is it a condo, is there a co-borrower, etc. In the real world, an AMQ
reviewer only ever answers the subset of the ~800 rules that a given loan's facts actually trigger
("they might start with 10 questions... and let's say it had a gift letter, then it may open up two
or three more questions" — Kayla). Today, every gift-related check in the compiled ruleset fires
against every loan regardless of whether a gift exists.

**Concretely, on loan 01 (no gift used):** the tool surfaced gift-fund-related checks (e.g. "gift
assets used to qualify — source documentation not confirmed") as some flavor of unresolved
gap/exception. Kayla's read, after checking the actual 1003/closing package: *"we would want on
this particular loan... a result of an NA, not applicable, because there is no gift letter... it's
just truly not applicable. There are going to be a lot of these things that are just not applicable
to each loan situation."* The correct behavior is `NOT_APPLICABLE`, cleanly — not a surfaced
exception, not a `SOURCE_INCOMPLETE` review flag.

**Root cause: the dependency graph exists in the source workbook but is undecodable.** The AMQ
sheet carries a "Question ID" / "Question Criteria by Questions" column (column M in the sheet
Kayla and Gordon inspected live) that appears to cross-reference other questions — the branching
logic that would say "only ask this if that other question's answer was X." Neither Gordon nor
Kayla could resolve what the ID values mean or match them to any other column: *"we don't have a...
we can't find a question number to match that... we would need to have them sit down and show us to
be able to do anything additional with that."* Kayla's own hypothesis is that this ties into the
client's internal QC software (ACES) via an opaque question-ID branching key that only the client
holds. **This is not a new discovery** — `output/ROADMAP.md`'s `010a` entry already lists this exact
column in its out-of-scope note ("the unrelated `Question Criteria by Questions` column
(questionnaire branching logic, not program gating)"), and `010b`'s out-of-scope note already flags
"pulling Fannie/Freddie selling guides beyond the client spreadsheet" as an **open question to
resolve with Kayla, don't block.** This call is that resolution conversation — it confirms the gap
is real and adds Kayla's hard constraint on how to close it (next paragraph).

**Kayla's hard constraint on any fix:** domain knowledge (e.g., a Fannie/Freddie Selling Guide) may
be used **only** to decide *whether an existing rule applies* — it must never cause additional
rules/questions to fire, and must never originate new rule content. Verbatim: *"I always think
having knowledge of things is great, but is it going to force other rules to run because of it? If
so, then we're not delivering what the client asks... if it's not going to interject and cause other
rules to run or questions to run, then we're fine... it's just truly systemic information."* Both
agreed to **abandon using the Selling Guide as a source of new rule content or re-underwriting
logic** — Gordon: *"if we bring in all of Fannie and Freddie guides in, then we're basically
re-underwriting the file... we'd be looking at so much more than we have to."* The attached
`docs/Selling-Guide_06-03-2026_highlighted.pdf` (Fannie Mae, 1,188 pages) is offered as the
candidate knowledge source for this narrower, gating-only use — not yet opened or scoped for use.

This is a **distinct capability** from the existing citation-grounding discipline already governing
`compile_llm.py`/`knowledge_base.py` (`002c`, hardened 2026-07-22): that discipline governs *how a
single check's own condition/threshold is worded*; this gap is about *whether the check should be
evaluated on this loan at all*. Same non-negotiable spirit (grounding adds context, never new rule
content), applied to a different decision point.

---

## 2. Separate finding: operator-inversion bug in `ratio_threshold` checks

**Not systemic — a straightforward, already-diagnosed compiler defect, distinct from the gating
gap above.** Found because Kayla manually re-derived loan 01's LTV by hand and caught the tool
disagreeing with its own stated rule intent.

**Mechanism:** `engine.py`'s `ratio_threshold` evaluation treats `operator` as the literal
PASS-condition expression (`ok = value > thr` when `operator=">"`, etc. — PASS iff `ok`). The
compiler's `SYSTEM_PROMPT` (`p0/qc_engine/compiler/compile_llm.py`) never states this convention, so
where a source row's `defect_text` describes a *FAIL-trigger* comparison ("if LTV **exceeds** 80%..."),
the compiler transcribes that comparison word literally into `operator` instead of inverting it to
express the PASS condition the engine actually needs.

**Confirmed concretely on loan 01** (`loan_amount=340,000.00`, `property_value=425,000.00` → LTV
exactly 80.0%): both `fnm-ltv-mi-required` and `ltv-exceeds-80-without-mi` compile as
`operator=">", threshold=80`, while their own `message_pass` text states *"LTV is at or below 80%;
MI not required..."* — i.e., PASS should require `<=80`. With the engine's actual logic, `80.0 > 80`
is `False`, so the check returns **FAIL** at exactly the boundary the rule's own text says should
PASS. This is a real false positive at the load-bearing LTV/MI boundary — the same boundary-math
risk class the G3 bake-off flagged (`p0/experiment_g3/RESULTS.md`).

**Scope, re-verified today** (script + output persisted, not just re-stated from memory):
`output/operator_inversion_suspects_2026-07-24.json` — **45 of 495** unique `ratio_threshold` checks
in `post_closing_only_ruleset.json` carry the same signature (an operator whose direction contradicts
its own `message_pass` text). Both loan-01-confirmed checks are in this set. 45/495 is a heuristic
lower bound (keyed on 7 specific PASS-condition phrasings) — the true count of inverted checks may
be higher; anything not matching those phrasings wouldn't be caught by this scan.

**Consequence already in the wild:** `output/LOAN-01-QC-RESULT-WITH-PROVENANCE-2026-07-24.pdf`
(already sent to Gordon's colleague) lists `fnm-ltv-mi-required` and `ltv-exceeds-80-without-mi` as
confirmed real defects for loan 01. They are false positives caused by this bug. **This needs
correcting once the fix lands** — tracked as a follow-up, not done in this document.

---

## 3. Already resolved on the call — not open questions

- **The Question-ID/ACES branching column**: explicitly agreed to leave out of scope entirely —
  *"I would leave that off for running this, to be honest with you... it has no relevance to what
  we're trying to do."* Decoding it needs the client to sit down and explain their key, which is not
  something either party can produce today.
- **Private Bank / Private Equity sheet scope**: confirmed on the call — Private Equity is fully
  excluded (*"we're not using the private equity one... perfect"*), Private Bank is PC-only
  (*"just PC, but their private bank... I don't know anything about private equity"*). This matches
  what the existing `run_010_post_closing_only` recompile already scopes to (the "Post Closing Oct
  2025" sheet of the Private Bank workbook) — **no scope change needed**, this was a real ambiguity
  going into the call and is now closed.
- **Fannie vs. Freddie program ambiguity**: re-raised on the call (*"are these Fannie or Freddie
  loans... it didn't specify"*) but this is the pre-existing, already-partially-handled `AMBIGUOUS`
  sentinel in `program_gating.py` (`010a`) — not a new gap, just re-confirmed as still real and
  still unresolved at the loan-type level for loans that don't name a specific GSE.

---

## 4. What this document does NOT decide

No design for closing the conditional-applicability gap is proposed here — not the shape of a
dependency-gating mechanism, not how (or whether) the Selling Guide gets consumed, not a spec
number, not a phasing plan. Per the explicit instruction this review was run under, that comes
next, as a separate planning step, once this problem statement is confirmed.

**Immediate housekeeping this finding implies** (not a design decision, just correcting a known-bad
already-shipped artifact once the bug above is fixed): re-run loan 01 and regenerate
`LOAN-01-QC-RESULT-WITH-PROVENANCE-2026-07-24.pdf` / `loan01_with_provenance.json` so the two
false-positive LTV/MI findings no longer read as confirmed defects.
