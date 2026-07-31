# Why does `src` report ~547 NO_DATA? — Root-Cause Analysis (2026-07-31)

**Question asked:** "Why do 547 checks in `src` end in NO_DATA? Are they all the same problem?
What stage causes it — the gold→SHACL conversion? Scenario inapplicability? Genuinely missing
data? A coding error?"

**Answer in one line:** They are **not** one problem — they are **three distinct root causes**
(440 + 87 + 21), and the dominant one is caused **upstream of both engines**, at the gold
compile stage, not by the SHACL conversion, and mostly not by "the data is missing."

*(Housekeeping first: the number is 548 in the raw `shacl_results.json` and 547 in the
comparison report — two gold cards, `PC::O-FNM-15438` and `PC::O-FNM-15410`, each contain two
defect options sharing one exception code, so two records collapse when joining on
`(card_id, exception_code)`. A gold-ruleset data quirk, not an engine bug.)*

---

## Method (how this was established, not guessed)

1. Every NO_DATA record was programmatically bucketed by its recorded reason → 3 buckets.
2. All **440 document checks** (bucket A) were individually classified by a guardrailed
   configuration-time review — 6 parallel reviewers over disjoint chunks, closed 54-type
   Touchless vocabulary, mandatory verbatim-evidence quoting, null-by-default — then
   machine-validated (4 evidence violations found and voided) and every wiring candidate
   hand-verified against the real loan payload. Artifacts:
   `src/shacl_pilot/bakeoff_gold_touchless_2026-07-31/nodata_research/doc_all_classified.json`.
3. All **87 cross-document checks** (bucket B) were individually analyzed for what data each
   comparison needs and whether the current payload carries it:
   `.../nodata_research/cross_doc_analysis.json`.
4. The **21 applicability-unknown checks** (bucket C) were traced to the exact payload field.

This is the same "LLM at configuration time, humans sign off, nothing unverified gets wired"
pattern Non-Negotiable #1 sanctions — the LLM work happened before the deterministic run, and
only hand-verified mappings entered the engines.

---

## The three root causes

### A — 440 document checks: the gold compile emits no machine-usable document reference

**Stage: gold rule compilation (upstream of BOTH engines). Not a SHACL-conversion bug.**

Gold cards carry the required document **only in English prose** (`question_text` /
defect description). There is no structured `required_document` field, no trigger-fact
field, no "is this machine-decidable" classification. So neither converter could wire these
checks to the loan's real 62-entry document inventory — the inventory data **is present**;
the *rule side* gives nothing safe to match against it.

Keyword matching cannot bridge this. Tested twice, empirically:
- A naive keyword sweep produced false matches (documented in the bake-off report Addendum).
- Even **exact** name matches are unsafe: of 36 checks whose prose literally contains a
  Touchless documentType, hand review rejected ~34 — they are content checks
  ("three-in-file merged report"), compound requirements ("paystub AND W-2s OR VOE"), or
  trigger-gated checks that merely mention the document.

The full guardrailed classification of all 440:

| Sub-category | Count | What it means | The real blocker |
|---|---|---|---|
| **TRIGGER_GATED** | **277 (63%)** | Check applies only if a loan condition holds (income type used for qualifying, DU relief received, POA used, gift of equity, RefiNow…) | The trigger facts live in LOS/AUS data the payload doesn't carry. **Data gap for the trigger, not the document.** Matches the project's standing rule: gate on the trigger first, or you can't tell "N/A" from "missing." |
| **PRESENCE_GATE** | 105 (24%) | A document is identifiable and absence would be a defect, but presence alone can't clear it (content/signature/completeness demanded) | Field-level extraction: only **1 of 62** documents in this payload is field-extracted. **Vendor/extraction-scope data gap.** |
| **NOT_DOC_DECIDABLE** | 37 (8%) | Labeled doc_presence by the gold compile, but really underwriter process/judgment | **Gold compile misclassification** — these should be `scripted_review`. A gold-QA finding in its own right. |
| **COMPOUND_DOCS** | 12 (3%) | Disjunctive/conjunctive multi-document requirements | Needs any-of/all-of document logic neither converter has — a real (small) conversion capability gap. |
| **PURE_PRESENCE** | 9 (2%) | Genuinely decidable by "is doc type X in file" | **3 wired this pass** (see below). 6 rejected with cause — see the verification trail. |

**Resolved now — 3 checks wired, symmetrically, into both engines:**

| Check | Mapping | Why it survived verification |
|---|---|---|
| `PC::ICPL / ICPL` | Closing Protection Letter | Bare-absence defect; ICPL names the same instrument |
| `PC::O-BP-14663 / O-BP-54652` | Borrowers Authorization | Bare-absence defect; verbatim instrument match |
| `PC::O-FNM-15436 / HOICoverage` | Hazard Insurance | Bare-absence defect ("HOI policy not in file") |

All three documents are present in this loan → both engines now independently verify each and
say **PASS** — 3 new cross-engine agreements.

**Rejected at verification, deliberately (this is the guardrail working):**
- *"appraisal" → Form 1004*: presence of a 1004 proves an appraisal exists, but absence
  doesn't prove none exists (condo/2-4-unit appraisals use different forms) → would
  false-FAIL other loans.
- *Escrow Waiver (O-FNM-50230)*: the defect is a **conjunction** ("escrow not set up AND
  waiver absent") — absence-→-FAIL wiring would false-FAIL every normal escrowed loan. It
  would have been right for this loan and wrong in general.
- *Credit report per applicant (O-FNM-00179)*: needs doc-level borrower tags; the real
  payload's Credit Report entry has `primaryBorrowerId: null`, and count-based logic is wrong
  for joint reports. Decidable for this single-borrower loan; not generally.
- 3 more name documents absent from Touchless's observed vocabulary entirely.

### B — 87 cross-document checks: 0 of 87 are runnable with today's data

**Stage: half converter honesty, half genuine data gap — and the data gap is total.**

The converter only ever built entity-existence probes here (already documented), so the
classifier honestly abstains. The new per-check analysis proves no real logic was being
suppressed: **not one** of the 87 comparisons has both sides machine-readable today:

| Blocking gap | Count | Detail |
|---|---|---|
| Doc exists in inventory but fields not extracted | 43 | Note, CD, Title Commitment, appraisal, bank statements… — only the URLA is field-extracted |
| Non-document system data missing | 28 | **10 share one root cause**: "amount submitted to DU per income category" is captured nowhere; rest need DU findings/EPIC/SFC/CU artifacts |
| Needed doc type absent from inventory | 16 | Form 1008, 1004D, ICPL-adjacent items, trust agreements, 4868… |
| Pure judgment, no data comparison | 0 | every check has a concrete underlying comparison |

### C — 21 checks: applicability cannot be decided (`Loans.Underwriting_Type` is null)

**Stage: genuine vendor data gap. Not a scenario-inapplicability false alarm, not a bug.**

`loanSummary.underwriting` exists in the payload and is **null**. Only 5 gold conditions gate
on it (all "Desktop Underwriter" variants) but they cascade over 21 checks. Derivation was
attempted and correctly refused: none of the 54 document types in the inventory is a DU/AUS
findings report, so under the closed-world inventory rule there is no legitimate basis to
infer DU vs. manual underwrite. UNKNOWN → NO_DATA is the honest verdict. **This belongs on
the Touchless vendor question list** (with the doc-level borrower-tag nulls from A, and the
1-of-62 extraction scope from A/B).

### Coding error?

Checked for, since two were already caught and fixed this session (SPARQL polarity inversion;
existence-probe false FAILs). This pass found **no new verdict-affecting code error** — but
did catch one *process* hazard: the p0 pipeline consumes a pre-generated fixture artifact
(`touchless_loan_fixture.json`) that is **not** auto-regenerated when the adapter changes; a
first rerun silently used the stale fixture (2 of 3 wired checks didn't flip until the
fixture was rebuilt). Recommendation: make the importer regenerate the fixture, or fail if
the fixture is older than the adapter.

---

## Before/after (joined 1,103-check universe)

| Verdict | p0 before | p0 after | src before | src after |
|---|---|---|---|---|
| PASS | 7 | **10** | 8 | **11** |
| FAIL | 427 | **424** | 0 | 0 |
| NO_DATA | — | — | 547 | **544** |
| NEEDS_REVIEW | 323 | 323 | 140 | 140 |
| NOT_APPLICABLE | 133 | 133 | 14 | 14 |
| NOT_COMPILED | 213 | 213 | 394 | 394 |
| **Both-committed agreements** | 7 | **10** | 7 | **10** |
| **Disagreements** | 0 | **0** | 0 | 0 |

Gates after the change: `pytest p0/` 445 passed / 3 skipped / 1 xfailed;
`run_full_ruleset_audit.py` unaffected (it loads `blocks/*.ttl` non-recursively — the gold
shapes live in `blocks/gold/` and are not in its path); `run_audit.py` 25/25 remains blocked
on the pre-existing missing `answer_keys/` ground-truth files (out of scope, needs Gordon's
call on reconstruction).

## What resolving the rest actually requires (ranked by leverage)

1. **Enrich the gold compile schema** — emit structured `required_documents[]` (with
   any-of/all-of), `trigger_facts[]`, and a decidability class per check, generated at
   compile time and SME-signed like every other compiled artifact. This single upstream fix
   unblocks the correct handling of all 440 bucket-A checks in *both* engines and would have
   caught the 37 misclassified ones. Without it, every downstream consumer is reduced to
   prose keyword-matching, which is demonstrably unsafe.
2. **Vendor (Touchless) asks** — add to the standing question list: (a) full documentType
   taxonomy (the 54 observed types are one loan's worth — needed for safe absence checks);
   (b) populate `loanSummary.underwriting` (unblocks all 21 of bucket C); (c) populate
   doc-level borrower IDs (unblocks per-applicant checks); (d) field-extraction scope beyond
   the URLA (unblocks the 105 PRESENCE_GATE + 43 of the cross_doc checks); (e) capture
   "submitted to AUS" income values (unblocks 10 cross_doc checks with one field).
3. **SME review of the classification artifact** — `doc_all_classified.json` is exactly the
   SME sign-off surface: 440 rows, each with category, proposed mapping, quoted evidence.
   The next curated-allowlist expansion should come from an SME pass over it, not from code.
4. **Small converter capability** — any-of/all-of document presence logic for the 12
   COMPOUND_DOCS checks (only worth building after #1 provides structured doc lists).

*Note: an AWS-Bedrock-based mapping pass (the `mapping/llm_doc_mapper.py` route) was
unavailable this session — SSO token expired. The classification was run with local
config-time reviewers under the same guardrail discipline instead; artifacts are committed
for audit.*
