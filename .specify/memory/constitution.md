# Mortgage QA/QC Tool Constitution

> The invariants every spec, plan, and task in this project must honor. These are
> not style preferences — they are the bets the product is built on. A change that
> violates a principle is not "a different approach"; it is off-product. Challenge
> it or surface the tension; do not silently diverge.
>
> Source of truth: `CLAUDE.md` (the four non-negotiables), `output/THESIS.md`, and
> the empirical record in `p0/` (the determinism proof, the G3 bake-off, the
> synthetic eval) plus independent corroboration from a real deployed system
> (`output/PRIOR-ART-OLAV-MORTGAGE-QC.md`). Where this constitution and a
> marketing claim disagree, the empirical record wins.

## Core Principles

### I. Determinism of the *correct* computation (the defining bet) — NON-NEGOTIABLE
Same loan → **same pass/fail, every time, on every machine.** The engine is a pure
function of `(signed_ruleset, loan)` — no network, no model, no wall-clock at
runtime. Money/ratio math is **Decimal** with a pinned rounding policy
(`ROUND_HALF_EVEN`), never IEEE-754 float, because float drift flips pass/fail at
tolerance boundaries.

The **G3 bake-off (2026-06-28)** refined *why* this matters, on evidence:
reproducibility alone is **not** the discriminator (at temp=0 both Haiku 4.5 and
Sonnet 4.6 were byte-identical). The load-bearing reasons to compile are
**(a) guaranteed-correct arithmetic on boundary cases** — a runtime LLM can be
reproducibly *wrong* (Haiku cleared a 98%-LTV loan) — and **(b) auditability**: the
engine can show the exact Decimal value and rounding policy a regulator re-derives.
A runtime-LLM design is permitted **only** for cases where no deterministic
algorithm exists; everywhere an algorithm exists, demand determinism.

**Independently corroborated (2026-07-01):** a real, deployed runtime-LLM mortgage
QC system (not this project's) logged the same failure in production — identical
loans producing 2 to 13 findings across runs (`output/PRIOR-ART-OLAV-MORTGAGE-QC.md`).

### II. Compile, then run — the LLM never freelances at runtime — NON-NEGOTIABLE
The LLM works at **configuration time**: it interprets the SME's rule intent and
**generates an intermediate ruleset**. The SME validates, corrects, and **signs**
that artifact *before* it runs. The engine then executes the **same signed
artifact** (loaded by hash) deterministically against every loan. On any rule
change: back through the pipeline → regenerate → re-validate → re-sign → run.

Sign-off binds to the **human-corrected** artifact, and SME edit-distance is
**measured** — zero edits across many rules is the sign-off-theater smell, surfaced
loudly, not a win. Reconciliation/normalization logic lives **inside** the signed
artifact as authored data referenced by name, never as hand-code outside it.

### III. Eval is foundational — ground truth before trust — NON-NEGOTIABLE
"AI is only as good as the method to evaluate it." No rules work is trustworthy
without labeled cases with **known** outcomes to test against. Because expert-
labeled real loans may be the last thing we get, we **decompose** the ground-truth
gap into three questions and solve what we can now:
1. **Engine correctness** (given the data, is the verdict right per spec?) →
   proven *by construction*: we inject the defect, so the label is exact
   (`p0/eval_synth/`). Mandatory metric: **zero false-auto-clears** at scale.
2. **Interpretation correctness** (did we read the check as the lender means it?) →
   an SME **rules review** of the mutation→verdict mapping, decoupled from loans.
3. **Defect distribution + extraction/OCR realism** → the honest residual; it is
   the only piece that genuinely needs real files. Label it loudly; never fold it
   silently into a correctness claim.
The synthetic eval is the regression floor; real loans, when they arrive, become
the distribution check with **no harness rework**.

### IV. Build the core, assume the periphery (scope discipline) — NON-NEGOTIABLE
The product is the **rules engine + config workbench + result set**. Do **not**
build document extraction (upstream contract with Touchless returns extracted
fields + classification) or LOS integration (reuse the existing connector). The
extraction contract may **widen** over time — track that as an *interface*, not a
build. Do not boil the ocean: a feature outside Apply / Author / Output is
out-of-scope until the core earns the right to it.

### V. Source independence — reconcile, don't self-validate
Comparison data must come from genuinely independent origins. The closing
**document is the source of truth**; the lender **system** (LOS / MISMO-as-system)
is what we check against it. Never derive the comparison value from the same source
as the value being checked — that collapses the audit into self-validation. In test
data, the document path and the system path must be independent (synthetic data
earns this by *construction*; LOS-only data makes the comparison trivially
identical and untestable). Reconcile mismatches **FLAG** (informational); they do
**not** fail QC — pass/fail lives solely in the QC rules.

**Independently corroborated:** a real deployed system's mock sources disagreed with
extracted truth data, producing false positives prompt engineering could not reliably
fix — the eventual fix was structural, not a better prompt
(`output/PRIOR-ART-OLAV-MORTGAGE-QC.md`).

### VI. Configurable by non-technical users (the philosophy that won the room)
**Routes → Blocks → Checks**, wired by hand by a BA/SME **without going back to
IT** — simple or complex, their call. This self-service capability is what caught
the client's imagination; protect it. Effort goes into perfecting the three
surfaces — **Apply** (the deterministic engine), **Author** (no-IT config),
**Output** (auto-clear the obvious, surface only true human-judgment exceptions,
clear fast) — and nowhere else.

### VII. Configuration is authored data, across all layers
Everything the SME configures is **authored data interpreted by version-pinned
code** — never hand-written logic outside the signed artifact. This is one model at
four layers: the **field catalog** (the vocabulary — which data elements exist, each
with type, expected sources, citation/confidence requirements), **checks**
(assertions over fields), **blocks** (groupings of checks), and **routes**
(compositions of blocks + applicability gating). All four share the same mechanics:
**authored → SME-corrected & signed → identified by SHA-256 → executed by a
version-pinned interpreter.** Adding a field, check, block, or route is an authoring
act, not a code change — this is what makes the system scale to 800+ checks and new
data sources maintainably.

Two boundaries hold the model together: **(a) what stays fluid vs. fixed** — the
field *set* and source *list* are data-driven (add a settlement-agent feed by
authoring, not coding), but the per-field *envelope* (`value, source_origin,
citation, confidence`) is a stable typed shape, because canonical hashing
(determinism + audit) and the confidence gate depend on it. **(b) referential
integrity** — fields are vocabulary, checks/blocks/routes are logic over it; the
dependency is one-way, and **every check's field reference must resolve to a catalog
entry** (an unresolved reference is a silent no-op = a false-clear vector, caught by
the SAFE gate). Unify the mechanics; keep the layers distinct.

## Quality Gates

- **Determinism gate:** any engine change must keep the bit-exact harness green
  (golden set, byte-identical result hash across repeated runs).
- **Safety gate (catastrophic):** **zero false-auto-clears** — the engine must
  never mark a loan cleared where a known defect exists. A single false-clear
  blocks the change. Includes **referential integrity**: a check whose field
  reference does not resolve to a catalog entry is a silent no-op (a false-clear
  vector) and must fail validation.
- **Eval gate:** new check kinds or rule changes require labeled cases (synthetic-
  by-construction at minimum) and must pass the constructed-label scorer plus the
  label-free metamorphic invariants.
- **Audit gate:** every doc-sourced value is traceable (doc name + page +
  segment); every verdict carries field-level intermediates (the three inputs, the
  normalized/derived value, the rounding, the rule version) — not an opaque trace.
- **Confidence gate:** a PASS that relied on a sub-floor extraction is withheld to
  NEEDS_REVIEW, never auto-cleared.

## Development Workflow

This project follows the **prototype → validate → hand off** flywheel: Gordon
prototypes fast, validates with Kayla/client, and hands the validated prototype to
Monish's team for industrial build-out (observability, security, guardrails) on the
Touchless platform. Specs are spec-driven (GitHub Spec Kit): constitution → specify
→ (clarify) → plan → tasks → implement. Spec directories use a numbered `NNN-`
prefix for dependency ordering. The full feature roadmap is specified before any
one feature is built, so the dependency picture is complete first. Python is
**3.9-compatible** (`Optional[...]`, not `X | None`). Decisions that touch a
non-negotiable are checked against this constitution before code is written; a real
tension is surfaced, not silently resolved.

## Governance

This constitution supersedes ad-hoc practice. Any spec, plan, or task that
conflicts with a NON-NEGOTIABLE principle must either be revised or must explicitly
document the tension and its justification for human decision before proceeding.
Amendments require: a stated rationale, an update to the affected downstream
artifacts (`CLAUDE.md`, `THESIS.md`, specs), and a version bump per the policy
below. The empirical record in `p0/` is the tie-breaker when a principle's
*rationale* is challenged — principles are refined by evidence (as Principle I was
by the G3 bake-off), not by assertion.

**Versioning policy** (semantic): **MAJOR** = a principle removed or redefined in a
backward-incompatible way; **MINOR** = a new principle or materially expanded
guidance; **PATCH** = clarifications and wording.

**Version**: 1.1.1 | **Ratified**: 2026-06-28 | **Last Amended**: 2026-07-01
<!-- v1.1.1 (PATCH): cited independent real-world corroboration (Olav's deployed
runtime-LLM system, output/PRIOR-ART-OLAV-MORTGAGE-QC.md) for Principles I and V.
No principle redefined. -->
<!-- v1.1.0 (MINOR): added Principle VII (Configuration is authored data, across
all layers) + referential-integrity clause in the Safety gate, unifying the field
catalog with Routes→Blocks→Checks as one authored, signed, hashed model. -->
<!-- v1.0.0: initial ratification (6 principles, 4 NON-NEGOTIABLE). -->

