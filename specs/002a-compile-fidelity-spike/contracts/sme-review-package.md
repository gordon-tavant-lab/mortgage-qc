# Contract: SME (Kayla) Review Package

The handoff artifact between the compile step and the interpretation-fidelity review (User Story
2, FR-004). This is the "contract" GAP 1 (`output/FOUNDATION-READINESS.md`) calls for — pinned as a
schema here rather than left as prose, even though this is a throwaway spike, because the review
step is the one part of this feature with a human on the other side of the interface.

## Format

A single reviewable document (one row per sampled workbook row), with these columns:

| Column | Populated by | Description |
|---|---|---|
| `row_id` | compile step | links to source row and generated rule |
| `source_question` | compile step (verbatim from workbook) | the AMQ question text |
| `source_response` | compile step (verbatim from workbook) | the AMQ response / defect condition text — the actual thing being compiled |
| `plain_english_restatement` | LLM (compile step) | what the compiled rule says it does, in plain English |
| `constructed_label_score` | `p0/eval_synth` scorer | pass / fail — shown to Kayla for context, but must not be treated by her as the answer to "is the interpretation right" (FR-004) |
| `verdict` | **Kayla** | correct / incorrect / ambiguous |
| `correction` | **Kayla** | free text or corrected rule, if verdict != correct |
| `reviewer_note` | **Kayla**, optional | rationale |

## Why source text, not the generated rule's own logic, is the reference point

Kayla judges each row by reading `source_question` + `source_response` and asking "does the
`plain_english_restatement` capture what this response actually means?" — **not** by checking
whether the generated rule is internally consistent or whether it happened to pass the constructed-
label scorer. A rule can be self-consistent and still misread the row (the exact failure mode this
spike exists to catch, per `output/ROADMAP.md` §002a and Tension 6).

## Non-goals

- Not a live authoring UI — no such surface exists yet (roadmap feature `009` is unspecced and
  unbuilt). This is a static document handoff, consistent with `001a`'s assumption that field/rule
  authoring is currently hand-done and procedurally reviewed.
- Not a two-reviewer inter-rater-reliability protocol (`research.md` decision #3 — only one SME is
  available for this spike; noted as a future strengthening, not a requirement here).
