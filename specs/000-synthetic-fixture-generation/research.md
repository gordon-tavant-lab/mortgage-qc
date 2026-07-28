# Research: Synthetic Loan Fixture Generation

## Unknowns resolved

### 1. Extraction mechanism: deterministic text parsing, not the existing runtime-LLM pipeline

**Decision**: PDFs are parsed with `pdftotext -layout` (poppler-utils) plus per-document-type,
label-anchored regex patterns (data files, not per-doc Python code). MISMO XML reuses
`qc_engine/mismo.py` as-is, extended only in its field list. An LLM call is permitted only as a
last-resort fallback for a field the pattern set cannot resolve, and only offline at
`temperature=0`, still gated by the 25/25 defect check before use.

**Rationale**: A dedicated audit of `examples/mortgage-qc/agent-gateway/src/{extraction_handler,
pdf_processor,xml_extractor,cross_validator}.py` (Olav's real, deployed runtime-LLM mortgage QC
system) found: (a) its PDF path is Claude Vision at `temperature=0`, not Textract — reduces but does
not guarantee bit-identical output across runs; (b) its own issue log documents live extraction
inaccuracy (issue `006-loan-estimate-extraction-nulls.md`: fields return `null`/confidence-0.0 for
present data, unfixed; issue `010-gla-discrepancy-accuracy-mock-data.md`: a fixture silently
disagreeing with the real PDF); (c) confidence scores are frequently a hardcoded fallback (`0.8`/`0.5`
defaults), not a calibrated signal; (d) it is not runnable standalone — hardwired to AWS
Bedrock/S3/Redis/mock services, no CLI. Every PDF in `demo/syn/` is confirmed born-digital synthetic
text (verified by reading all 33 PDFs with `pdftotext -layout` directly — zero OCR noise, no scanned
images), which is strictly easier than what Olav's pipeline has to solve (real, sometimes-scanned
lender PDFs). A ground-truth artifact cannot be less reliable than the thing it's meant to validate.

**Alternatives considered**: Reusing Olav's pipeline wholesale — rejected on (a)-(d) above. A
pure-LLM extraction pipeline built fresh for this feature — rejected: introduces exactly the
non-determinism risk this feature exists to avoid, for documents that don't need it (clean text
layer, regular "Label — Value" structure).

### 2. MISMO parsing: extend the existing adapter, do not rewrite it

**Decision**: `qc_engine/mismo.py` (the existing, already-deterministic ElementTree-based MISMO 3.4
parser) is extended with additional field extractions; its parsing approach is unchanged.

**Rationale**: It already parses this project's exact MISMO file shape correctly (confirmed by
direct inspection) and carries no LLM dependency at all. Writing a second XML parser would duplicate
proven code for no benefit.

**Alternatives considered**: A new, separate XML extractor scoped to `demo/syn/` — rejected as
needless duplication of working, already-deterministic code.

### 3. Field catalog growth: grounded in the real rule taxonomy, not the 5 loans' convenience

**Decision**: Every new `field_catalog.json` entry is justified by a specific archetype/condition in
`p0/eval_synth/taxonomy.json` (itself derived from the real 7,398-condition AMQ workbook), not merely
by appearing in one of the 5 synthetic loans.

**Rationale**: The existing 7-field seed catalog covers none of the 25 embedded defects. Cross-
referencing against `taxonomy.json` found several **exact-text matches** to real rule conditions —
e.g. `title_vesting` matches *"the manner in which title is held on the 1003 does not match the title
commitment"* verbatim, and `arm_preloan_disclosure_present` matches *"No, the ARM pre-loan disclosure
is missing or was not provided timely"* verbatim — proving the new fields track real rules, not
convenience. This also surfaced the doc-vs-doc gap (decision #4).

**Alternatives considered**: Adding fields ad hoc, keyed only to what makes these 5 loans'
defects extractable — rejected: would pass this feature's own tests while adding catalog entries with
no grounding beyond this one batch, undermining `001a`'s "add a field without a code change" guarantee
being worth anything (a field nobody's real rule needs is dead weight in the vocabulary).

### 4. Doc-vs-doc comparisons: two independently-cited catalog fields, comparison mechanism deferred

**Decision**: Where a real defect is a document-vs-document mismatch (e.g., the 1003's employment
start date vs. the VOE's), model it as **two separate catalog fields**, each with its own `truth` and
`DocCitation` — not as one field with a `sources` entry. The actual comparison check-kind that reads
both fields is explicitly **not built by this feature** — deferred to whoever specifies `003c`
(reconcile checks).

**Rationale**: `001b`'s `SourceEnvelope` and its source-independence guard (FR-005 there) are built
for exactly one shape: `truth` (document side, singular) vs. `sources{}` (system side). Forcing a
second document-side value into `sources{}` to make a doc-vs-doc comparison "fit" would either get
rejected by that guard (correctly) or silently defeat its purpose. Keeping both sides as independent,
fully-cited catalog fields preserves `001b`'s guarantee (it only ever fires on genuine doc-vs-system
comparisons) while still making both values available, cited, and ready for whatever check-kind `003c`
eventually defines.

**Alternatives considered**: Relaxing `001b`'s guard to allow doc-vs-doc under `sources{}` — rejected;
that's a change to an already-implemented, zero-regression-gated feature's semantics, out of scope
here and not this feature's call to make. Silently coercing doc-vs-doc into doc-vs-system anyway —
rejected outright; it would misrepresent what the comparison actually is.

### 5. Accuracy verification: the 25 embedded DEFECT comments as a mechanical ground-truth gate

**Decision**: Every one of the 5 loans' MISMO XML files carries 5 `<!-- DEFECT ... -->` comments
(25 total) precisely describing an intentional discrepancy or absence (e.g., *"Undisclosed liability.
Ally Bank auto $412/mo NOT included in total; actual should be 1096.00"*). These are formalized as a
machine-readable manifest (`contracts/defect-verification-manifest.md`) and checked automatically:
every generated fixture must reproduce its loan's 5 documented defects exactly, 100%, before any
downstream use.

**Rationale**: This is `g-learn-ground-truth-by-construction`'s pattern applied one layer earlier than
usual — the defects were injected by construction when these synthetic loans were authored, so the
"right answer" is already known and requires no human adjudication. It converts "must be accurate" from
an aspiration into an executable, zero-tolerance test, matching the constitution's Safety gate
("zero false-auto-clears... a single false-clear blocks the change") applied to extraction instead of
to engine verdicts.

**Alternatives considered**: Manual/human spot-review of extracted values — rejected: doesn't scale,
isn't repeatable, and reintroduces exactly the eval-gap problem (Principle III / Blocker 2) this whole
project exists to solve at the engine layer; extraction deserves the same discipline.

### 6. Confidence scores must be honest, not a hardcoded fallback

**Decision**: `doc_confidence` reflects the actual extraction method's certainty — high/near-1.0 for
an unambiguous deterministic pattern match (no OCR, no ambiguity in a synthetic born-digital
document), lower and explicitly justified only for an LLM-fallback-resolved field. No blanket default
value.

**Rationale**: The audit in decision #1 found Olav's pipeline defaults to hardcoded `0.8`/`0.5`
confidence values regardless of actual extraction certainty — exactly the anti-pattern the
constitution's Confidence gate ("a PASS that relied on a sub-floor extraction is withheld") depends on
not existing, since a fabricated confidence value defeats that gate's entire purpose.

**Alternatives considered**: A single flat confidence value for all doc-sourced fields — rejected as
the same anti-pattern found in the audited system, just at a different fixed number.

## Technical context (no NEEDS CLARIFICATION remaining)

- **Language/Version**: Python 3.9-compatible (project-wide constraint).
- **Primary Dependencies**: `pdftotext` (poppler-utils, subprocess) for PDFs; stdlib
  `xml.etree.ElementTree` via the existing `qc_engine/mismo.py` for XML; stdlib `re`/`json`. No new
  third-party Python packages. LLM fallback (Bedrock, `temperature=0`) permitted only when
  deterministic patterns cannot resolve a field, never the primary path.
- **Storage**: Flat files only — source documents already in `demo/syn/`, output JSON fixtures under
  `p0/fixtures/from_docs/`. No database.
- **Testing**: `pytest`, extending `p0/tests/`; the 25/25 defect-verification script is itself an
  executable acceptance gate, not just documentation.
- **Target Platform**: Local/CI execution, one-time offline batch — no deployed service, no runtime
  network dependency on the primary path.
- **Project Type**: New subpackage (`p0/fixtures/from_docs/`) inside the existing `p0/` package, at
  the same architectural layer as `p0/eval_synth/` and `p0/fixtures/golden.py`.
- **Performance Goals**: N/A — correctness over speed for a fixed, small, one-time batch.
- **Constraints**: Byte-deterministic output; zero new third-party dependency on the primary
  extraction path; never described or wired as the Touchless production extractor.
- **Scale/Scope**: Fixed — 5 loans, 38 source files (33 PDFs + 5 MISMO exports), ~33 catalog fields,
  25 known defects. Not a
  general-purpose extractor for arbitrary lender documents.
