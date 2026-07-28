"""
The map step (002b, research.md Decision 1): one Bedrock call per real AMQ
workbook row, compiling it into a CompiledCheckDraft -- the same `Check`
schema `p0/qc_engine/ruleset.py` already defines (no new fields), plus the
retained intent triple (FR-011) and, when needed, a proposed new field-catalog
entry (research.md Decision 2).

Generalizes `p0/experiment_002a/compile_llm.py`'s proven Bedrock harness
(Sonnet 4.6, temperature=0, one row per call) into a reusable, production
function -- not an extension of that throwaway spike's scripts (spec.md Edge
Cases; `002a`'s own FR-008 disclaims exactly this).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_QC_ENGINE = os.path.dirname(_HERE)
_REPO_ROOT = os.path.dirname(os.path.dirname(_QC_ENGINE))
if _QC_ENGINE not in sys.path:
    sys.path.insert(0, os.path.dirname(_QC_ENGINE))

from qc_engine.ruleset import Check, Ruleset, RuleProvenance, RuleIntentRecord  # noqa: E402
from qc_engine.catalog import FieldCatalog, FieldCatalogEntry  # noqa: E402
from qc_engine.compiler import program_gating  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.compiler import knowledge_base_store as store  # noqa: E402

os.environ.setdefault("AWS_CA_BUNDLE", "")
REGION = "us-east-1"
PROFILE = "gordon-chan"
MODEL_SONNET = "us.anthropic.claude-sonnet-4-6"

# The check-schema fields that only make sense for one `kind` each -- used to
# strip stray keys the LLM may echo back for the wrong kind.
_KIND_ONLY_FIELDS = {
    "predicate": ("predicate",),
    "ratio_threshold": ("ratio", "threshold", "operator"),
    "agree_categorical": ("normalizer",),
    "agree_numeric": ("tolerance",),
    # 003d: the doc-vs-doc pair also carries compare_field_name.
    "agree_doc_categorical": ("normalizer", "compare_field_name"),
    "agree_doc_numeric": ("tolerance", "compare_field_name"),
}

SYSTEM_PROMPT = """You are compiling a mortgage post-closing QA/QC rule from a real \
lender AMQ (Audit Management Questionnaire) workbook row into a deterministic, \
executable check specification.

You will be given:
- question_text: the AMQ question category
- defect_text: the RESPONSE TEXT describing the defect condition (this is the \
thing you must compile into a rule -- a check that FAILS/FLAGS when this \
condition is true)
- engine_kind: which check FAMILY this MUST be (predicate | ratio_threshold | \
agree_categorical | agree_numeric) -- determined upstream by classification. \
For predicate/ratio_threshold, kind MUST exactly equal engine_kind. For the \
agree_* family (a two-source agreement check), engine_kind names the \
comparison shape (categorical vs numeric agreement) but NOT which of the two \
comparison kinds to emit -- see the "doc-vs-system vs doc-vs-doc" constraint \
below, where YOU decide between agree_categorical/agree_numeric (doc vs a \
system of record) and agree_doc_categorical/agree_doc_numeric (doc vs a \
second, independent document) based on defect_text and existing_catalog_fields.
- significance: the severity tag from the sheet
- existing_catalog_fields: field names (with type AND expected_sources) \
already in the field catalog -- REUSE one of these if the check genuinely \
reads that same real-world data element; only propose a brand-new field if \
none of these fit. expected_sources is the load-bearing signal for the \
doc-vs-system/doc-vs-doc decision below: a field whose expected_sources is \
exactly ["doc"] (no "los"/"mismo") has NO system side -- it can only ever be \
compared against another document field, never against a system value.
- grounding_context: retrieved excerpts from a signed, SME-reviewed regulatory/guide \
knowledge base relevant to this row (may be empty). When present, use it to correctly \
interpret ambiguous defect_text -- it reflects real regulatory/guide requirements, not \
your own general knowledge. Never contradict grounding_context if it directly addresses \
the condition described.

Output ONLY a JSON object (no markdown fences, no prose) with this exact shape:
{
  "check": {
    "id": "<short-slug-id>",
    "name": "<short human name>",
    "field_name": "<canonical snake_case field name this check reads -- reuse \
an existing_catalog_fields entry when it genuinely matches, else invent one>",
    "kind": "<must equal engine_kind for predicate/ratio_threshold; for the \
agree_* family, YOU choose exactly one of agree_categorical | agree_numeric | \
agree_doc_categorical | agree_doc_numeric per the constraint below>",
    "severity": "CRITICAL | WARNING | INFO",
    "phase": "QC | RECONCILE",
    "predicate": "is_true | is_present (ONLY if kind=predicate, else omit)",
    "ratio": "ltv | dti | field_value (ONLY if kind=ratio_threshold, else omit)",
    "threshold": "<Decimal string -- percent for ltv/dti, else the field's own \
unit (years, days, months, count, dollars, etc.) for field_value. ONLY if \
kind=ratio_threshold>",
    "operator": "<= | < | >= | > -- MUST always express the condition under \
which the loan PASSES, never the FAIL-trigger condition literally transcribed \
from defect_text (see the PASS-condition convention below). ONLY if \
kind=ratio_threshold",
    "normalizer": "identity (ONLY if kind=agree_categorical or \
agree_doc_categorical, else omit)",
    "tolerance": "<Decimal string, ONLY if kind=agree_numeric or \
agree_doc_numeric, else omit>",
    "compare_field_name": "<the SECOND field being compared -- reuse an \
existing_catalog_fields entry the same way field_name does. ONLY if \
kind=agree_doc_categorical or agree_doc_numeric, else omit entirely>",
    "message_pass": "<short pass message>",
    "message_fail": "<short fail/flag message>"
  },
  "plain_english_restatement": "<one sentence restating, in your own words, \
what this check does and when it fails/flags -- THIS IS RETAINED PERMANENTLY \
as the audit record of what we understood this rule to mean, alongside the \
source text and the compiled logic. Be precise about WHAT is being checked.>",
  "proposed_field_entry": {
    "field_name": "<MUST equal check.field_name>",
    "data_type": "string | decimal | date | boolean | enum",
    "expected_sources": ["doc", "los"],
    "citation_required": true or false,
    "confidence_required": true or false,
    "description": "<one sentence>",
    "enum_values": "<REQUIRED, non-empty list of strings, ONLY if data_type=enum; omit entirely otherwise>"
  }
}

Constraints (hard):
- For engine_kind=predicate or engine_kind=ratio_threshold, kind MUST exactly \
equal engine_kind. Do not substitute a different kind.
- For engine_kind=agree_categorical or engine_kind=agree_numeric (the agree_* \
family), YOU decide the actual kind between the doc-vs-system pair \
(agree_categorical/agree_numeric) and the doc-vs-doc pair \
(agree_doc_categorical/agree_doc_numeric) -- engine_kind only fixes whether \
the comparison is categorical or numeric, not which of the two sources it is:
    - Use agree_categorical/agree_numeric (doc-vs-system, UNCHANGED existing \
behavior, field_name only, no compare_field_name) when defect_text names the \
lender's system of record, LOS, MISMO, or an automated-underwriting-system \
finding (DU, LPA, AUS) as one side of the comparison -- AUS/DU/LPA output IS \
system-side (it is the same lender data in another format), not a document.
    - Use agree_doc_categorical/agree_doc_numeric (doc-vs-doc, field_name AND \
compare_field_name both set) when defect_text names TWO independent DOCUMENTS \
(e.g. the 1003, a VOE, a Title Commitment, a Closing Disclosure, a credit \
report, a payoff statement, an appraisal) with no system/LOS/MISMO/AUS entity \
named on either side. Confirm with existing_catalog_fields' expected_sources \
when the candidate fields already exist: expected_sources == ["doc"] (no \
"los"/"mismo") on BOTH sides is a strong signal this is doc-vs-doc, not \
doc-vs-system -- there is no system value to compare against.
    - When genuinely ambiguous from defect_text alone, default to \
agree_categorical/agree_numeric (the existing, proven doc-vs-system path) \
rather than guessing doc-vs-doc -- do not invent a compare_field_name/second \
document that defect_text does not itself name (same NEVER-INVENT discipline \
as thresholds, below).
- If kind=ratio_threshold, ratio MUST be exactly one of "ltv" | "dti" | \
"field_value" -- the engine supports all three, do not force-fit into the \
wrong one:
    - "ltv": ONLY when the check genuinely computes loan-to-value from \
loan_amount/property_value (the row is actually about LTV).
    - "dti": ONLY when the check genuinely computes debt-to-income from \
monthly_debts/monthly_income (the row is actually about DTI).
    - "field_value": every other numeric/count/date-diff floor-or-ceiling on a \
SPECIFIC named field -- e.g. a minimum credit score, a years-of-history \
requirement, a day-count staleness window, a late-payment count, a dollar \
amount, a percentage that is itself the field's own value (not a computed \
LTV/DTI). This compares field_name's own extracted value directly against \
threshold -- no ratio is computed. This is the correct/default choice \
whenever the row is not literally about LTV or DTI. Never mislabel a \
field_value condition as "ltv" or "dti" just because they are the only \
ratios you might otherwise recall -- that produces a check which silently \
computes the WRONG value at evaluation time (this has happened before and \
is a serious defect, not a harmless approximation).
- PASS-CONDITION CONVENTION (002d, hard rule for ratio_threshold): `operator`/ \
`threshold` MUST always express the condition under which the loan PASSES -- \
the engine evaluates `ok = (value <operator> threshold)` and reports PASS when \
`ok` is true. defect_text is almost always phrased as a FAIL-trigger \
condition ("if LTV exceeds 80%...", "...balance is $2,500 or more...") -- when \
it is, you MUST INVERT the comparison word into its PASS-condition opposite, \
never transcribe the FAIL-trigger word literally. Two worked examples:
    - defect_text: "MI is required if LTV exceeds 80%." -> the FAIL trigger is \
"exceeds 80%" (operator ">" would be the literal transcription -- WRONG). The \
PASS condition is "LTV is at or below 80%" -> emit `operator: "<="`, \
`threshold: "80"`, `message_pass: "LTV is at or below 80%; MI not required."`
    - defect_text: "Defect if lender cash-like incentive is $2,500 or more." -> \
the FAIL trigger is "$2,500 or more" (operator ">=" would be the literal \
transcription -- WRONG). The PASS condition is "incentive is less than $2,500" \
-> emit `operator: "<"`, `threshold: "2500"`, `message_pass: "Lender incentive \
is under $2,500."`
  Before finalizing, re-read your own `message_pass` text: it must describe \
the SAME direction as the `operator`/`threshold` you emitted -- if \
`message_pass` says "does not exceed X" / "is at or below X" / "X or less", \
`operator` MUST be "<=" or "<"; if `message_pass` says "is at least X" / "X or \
more" / "X or greater", `operator` MUST be ">=" or ">". A self-contradiction \
between your own `operator` and your own `message_pass` is exactly the defect \
this convention exists to prevent.
- If kind=predicate, predicate MUST be "is_true" or "is_present" -- no other value.
- OMIT "proposed_field_entry" entirely (do not include the key) if field_name \
already matches an existing_catalog_fields entry.
- If proposed_field_entry.data_type is "enum", enum_values is REQUIRED and MUST be \
a non-empty list of strings -- when unsure of the exact allowed values, prefer \
data_type "string" instead of guessing at an enum's members.
- Never invent a runtime LLM call or free-text logic; this is a static, \
deterministic specification only.
- NEVER INVENT A NUMBER, DATE, OR CONDITION. Every threshold, tolerance, \
operator, and rule condition in your output MUST be traceable to defect_text \
itself or to a quoted grounding_context excerpt -- never to your own general/ \
training knowledge of "typical" industry guidelines, even when that knowledge \
is accurate. If defect_text implies a limit/threshold exists but does not state \
its exact value, and grounding_context does not supply it either, DO NOT fill \
in a plausible-sounding number. Instead set threshold/tolerance to the literal \
string "UNSPECIFIED" and say so explicitly in plain_english_restatement (e.g. \
"defect_text references a distance/ratio limit but does not state the exact \
value; grounding_context does not supply it either -- threshold left unspecified, \
needs SME input"). A wrong-but-confident number is worse than an honest gap: \
the SME reviewing this compile must be able to tell "the source stated this" \
from "the model guessed this" on sight.
- IMPORTANT -- this is NOT the same thing as an informally-worded but still \
EXPLICIT number. defect_text stating "less than 2 yrs", "at least 30 days", \
"no more than 5%", "within 12 months", etc. IS an explicit, extractable \
threshold -- extract the literal number (2, 30, 5, 12) into threshold, even \
though it is phrased in prose rather than as a bare figure. UNSPECIFIED is \
reserved ONLY for when defect_text references a limit/requirement conceptually \
but states NO number for it anywhere (e.g. "exceeds the maximum allowable \
distance" with no distance given). Before writing threshold as UNSPECIFIED, \
check the message_pass/message_fail text you are about to write: if those \
messages would themselves state a specific number (because you understood the \
row well enough to phrase it that way), that same number belongs in the \
structured threshold field too -- it is a self-contradiction to write "2-year \
requirement" in message_pass while leaving threshold as UNSPECIFIED.
- grounding_context may be used ONLY to interpret/clarify what defect_text \
already says (e.g. resolving an ambiguous term, supplying the real citation for \
a condition the text already describes). It must NEVER be used to introduce a \
condition, threshold, or requirement that defect_text does not itself reference \
-- grounding adds context to an existing rule, it never adds a new rule.
"""


@dataclass
class CompiledCheckDraft:
    """The map step's output unit (data-model.md #1)."""
    row_id: str
    check: Optional[Check]
    source_text: str
    extracted_intent: str
    proposed_field_entry: Optional[FieldCatalogEntry] = None
    parse_error: Optional[str] = None
    # 010a: parsed from the source row's own Exception Code + (if present)
    # SQL gating clause -- the automated generalization of
    # ruleset_defects.py's hand-derived program gating. None means this row
    # carried no exception_code at all (distinct from an Applicability whose
    # program field is itself None, which means "no program prefix found,
    # fails open" -- see program_gating.py).
    applicability: Optional[program_gating.Applicability] = None
    # 002c: which signed knowledge-base version/sections (if any) grounded
    # this compile -- None when no signed KB exists yet for this row's
    # program (FR-006's fallback), never a live search result.
    grounding: Optional["GroundingRecord"] = None
    # 002d FR-003/FR-004: set when `operator_consistency_check()` finds the
    # compiled operator's direction contradicts this check's own message_pass
    # text. A non-None flag here excludes the check from `assemble_ruleset`'s
    # signed set (same treatment as `parse_error`) while keeping it present in
    # the batch output for SME review -- never silently signed.
    operator_consistency_flag: Optional[str] = None
    # 002g: where an attached `applies_if` came from (layer + fact id +
    # ontology key) -- draft-level metadata only, never serialized into the
    # Check, so no digest impact. `applies_if_review` is set when a
    # precondition proposal exists but was NOT auto-attached: unresolved
    # vocabulary mapping, or a MEDIUM/MANDATORY trust tier (Layer 1/2 --
    # human path, never auto-attached regardless of resolvability).
    applies_if_provenance: Optional[str] = None
    applies_if_review: Optional[str] = None


@dataclass
class GroundingRecord:
    """002c: the exact KB version/sections a compiled check was grounded
    against -- version-anchored (spec.md US2/FR-004) so a later KB update
    never retroactively changes what an already-compiled check's grounding
    meant."""
    kb_program: str
    kb_version: int
    section_ids: List[str]


# Central storage for this project's generated/derived stores (databases,
# ingested corpora, etc.) -- lives at the repo root, not buried inside
# p0/qc_engine/compiler/, so it's one place to find "that kind of thing"
# regardless of which module produced it.
_KB_DIR = os.path.join(_REPO_ROOT, "storage", "knowledge_base")


def _load_signed_kb_for_program(program: Optional[str]) -> Optional[KB.KnowledgeBaseCorpus]:
    """Loads the highest-version SIGNED corpus for a program from the
    SQLite-backed store (`knowledge_base_store.py`), or None if no usable
    corpus exists yet (FR-006: grounding is additive, never a hard blocker
    on compilation). Falls back to the legacy per-program JSON-file layout
    (`storage/knowledge_base/{program}/v{n}.json`) if the SQLite DB has
    nothing for this program -- a hand-authored test corpus predating the
    real Fannie Selling Guide ingestion may still only exist in that form.

    The db path is derived from `_KB_DIR` on every call (not cached at
    import time) so tests that monkeypatch `_KB_DIR` to an isolated tmpdir
    correctly redirect BOTH the SQLite lookup and the JSON fallback --
    otherwise a real corpus already on disk for the same program name could
    leak into a test that expects isolation."""
    if not program:
        return None
    kb_db_path = os.path.join(_KB_DIR, "kb.sqlite3")
    if os.path.exists(kb_db_path):
        for version in store.list_versions(kb_db_path, program):
            corpus = store.load_from_db(kb_db_path, program, version=version)
            if corpus is not None and KB.is_usable(corpus):
                return corpus
    program_dir = os.path.join(_KB_DIR, program)
    if not os.path.isdir(program_dir):
        return None
    versions = sorted(
        (f for f in os.listdir(program_dir) if f.startswith("v") and f.endswith(".json")),
        key=lambda f: int(f[1:-5]), reverse=True,
    )
    for fname in versions:
        corpus = KB.load(os.path.join(program_dir, fname))
        if KB.is_usable(corpus):
            return corpus
    return None


def _client():
    import boto3
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    return session.client("bedrock-runtime")


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"No JSON object found in LLM output: {text[:200]}")
    return json.loads(m.group(0))


def _existing_catalog_fields(catalog: FieldCatalog) -> List[Dict[str, Any]]:
    # 003d: expected_sources is the load-bearing signal the compiler needs to
    # tell doc-vs-system from doc-vs-doc -- previously omitted, so the
    # compiler had no reliable way to know "no system value exists for this
    # field" short of guessing from defect_text phrasing alone.
    return [{"field_name": e.field_name, "data_type": e.data_type,
             "expected_sources": e.expected_sources}
            for e in catalog.entries]


def _clean_check_kwargs(kind: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    """Strip fields the LLM echoed back for the wrong kind (e.g. `ratio` on a
    predicate check) -- keeps Check() construction from failing on stray keys
    a permissive LLM output might include."""
    allowed_extra = set(_KIND_ONLY_FIELDS.get(kind, ()))
    all_extra_fields = {f for fields in _KIND_ONLY_FIELDS.values() for f in fields}
    return {k: v for k, v in raw.items()
            if k not in (all_extra_fields - allowed_extra)}


def compile_row(client, row: Dict[str, Any], catalog: FieldCatalog) -> CompiledCheckDraft:
    """Compile one real workbook row via one Bedrock call (temperature=0,
    Sonnet 4.6 -- the model 002a validated for interpretation fidelity).

    002c: if a signed knowledge base exists for this row's program, ground
    the compile with the top-matching retrieved sections -- a pure,
    in-memory lookup (knowledge_base.retrieve()), never a live search call
    (FR-005/FR-006: additive when present, silent no-op fallback when not)."""
    program = program_gating.parse_exception_code_prefix(row.get("exception_code"))
    signed_kb = _load_signed_kb_for_program(program)
    grounding_record: Optional[GroundingRecord] = None
    grounding_text = ""
    if signed_kb is not None:
        retrieved = KB.retrieve(signed_kb, row["defect_text"])
        if retrieved:
            grounding_text = "\n".join(f"- ({s.source_document}) {s.content}" for s in retrieved)
            grounding_record = GroundingRecord(
                kb_program=signed_kb.program, kb_version=signed_kb.version,
                section_ids=[s.id for s in retrieved],
            )

    user_msg = json.dumps({
        "question_text": row.get("qcode") or row.get("category") or "",
        "defect_text": row["defect_text"],
        "engine_kind": row["engine_kind"],
        "significance": row.get("significance"),
        "existing_catalog_fields": _existing_catalog_fields(catalog),
        "grounding_context": grounding_text,
    }, indent=2)

    resp = client.converse(
        modelId=MODEL_SONNET,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": user_msg}]}],
        inferenceConfig={"temperature": 0, "maxTokens": 700},
    )
    raw_text = resp["output"]["message"]["content"][0]["text"]

    try:
        parsed = _extract_json(raw_text)
        # 003d: clean by the LLM's OWN chosen kind, not the upstream
        # engine_kind -- for the agree_* family the two now legitimately
        # differ (the compiler may choose agree_doc_categorical/_numeric
        # over the input engine_kind=agree_categorical/_numeric). Cleaning
        # by engine_kind here would silently strip compare_field_name off
        # every doc-vs-doc check the moment the compiler correctly chose to
        # emit one -- a bug that would defeat this entire feature invisibly.
        check_kwargs = _clean_check_kwargs(parsed["check"].get("kind", row["engine_kind"]), parsed["check"])
        check = Check(**check_kwargs)
    except Exception as e:  # noqa: BLE001 -- record, don't crash the batch
        return CompiledCheckDraft(
            row_id=row["row_id"], check=None, source_text=row["defect_text"],
            extracted_intent="", parse_error=f"{type(e).__name__}: {e}",
            grounding=grounding_record,
        )

    # A malformed proposed_field_entry must NOT discard an otherwise-valid
    # compiled check -- it degrades to no proposal (the referential-integrity
    # screen then correctly reports this check as BLOCKED, not silently lost,
    # per User Story 3). Found via a real 30-row production batch run: 3
    # agree_categorical rows had the LLM emit data_type="enum" with no
    # enum_values, which crashed the WHOLE row under the original single-try
    # implementation -- discarding 3 valid Check compiles along with the bad
    # proposals.
    proposed_entry: Optional[FieldCatalogEntry] = None
    proposal_error: Optional[str] = None
    proposed = parsed.get("proposed_field_entry")
    if proposed:
        try:
            proposed_entry = FieldCatalogEntry(**proposed)
        except Exception as e:  # noqa: BLE001
            proposal_error = f"proposed_field_entry rejected: {type(e).__name__}: {e}"

    # 010a: parse the row's own program signal -- Exception Code prefix
    # (primary) plus its own SQL gating clause (secondary, if present) --
    # never an LLM call, both parsed directly from the row's real workbook
    # text the same way _extract_json above parsed the LLM's.
    applicability = program_gating.Applicability(
        program=program_gating.parse_exception_code_prefix(row.get("exception_code")),
        sql_filters=program_gating.parse_sql_gating_clause(row.get("sql_criteria", "")),
    )

    # 002d FR-003: run automatically as part of the compile step itself, not a
    # separate scan a human must remember to invoke.
    operator_flag = (
        operator_consistency_check(check) if check.kind == "ratio_threshold" else None
    )

    return CompiledCheckDraft(
        row_id=row["row_id"], check=check,
        source_text=row["defect_text"],
        extracted_intent=parsed.get("plain_english_restatement", ""),
        proposed_field_entry=proposed_entry,
        parse_error=proposal_error,
        applicability=applicability,
        grounding=grounding_record,
        operator_consistency_flag=operator_flag,
    )



# 002d: the PASS-condition phrase table -- formalizes the manual scan that
# found 45/495 operator-direction suspects in `post_closing_only_ruleset.json`
# (output/operator_inversion_suspects_2026-07-24.json) into permanent,
# deterministic (no LLM) code. Validated against that real ruleset: catches
# all 45 known suspects plus a small number of additional checks sharing the
# exact same contradiction pattern (Acceptance Scenario 3 -- "the gate may
# reasonably catch additional phrasings the manual heuristic didn't"), zero
# false positives against the ~450 checks NOT in the suspect set once the two
# demographic/verb-collision traps below were excluded.
_UPPER_BOUND_PHRASES = (
    "does not exceed", "no more than", "at or below", "or less",
    "or lower", "or lesser", "is below",
)
_LOWER_BOUND_PHRASES = (
    "at least", "or more", "or greater", "meets or exceeds",
    "equals or exceeds", "or higher",
)
# "under 20%" is a real upper-bound signal; "DU-underwritten"/"re-underwritten"
# are not -- require a digit immediately after the word.
_UNDER_WITH_NUMBER = re.compile(r"\bunder\s+\$?\d")
# "$2,500" is not a clause boundary -- a thousands separator, not two clauses.
_THOUSANDS_COMMA = re.compile(r"(?<=\d),(?=\d{3}\b)")
# "borrower is at least 62 years old" is a demographic qualifier, not a signal
# about the field being compared -- strip it before phrase-matching so its
# "at least" doesn't collide with the check's own comparison direction.
_AGE_CLAUSE = re.compile(r"(?:at least\s+)?\d+\+?\s*years?\s*old")


def _normalize_for_phrase_match(text: str) -> str:
    text = _THOUSANDS_COMMA.sub("", text)
    text = _AGE_CLAUSE.sub("", text)
    return text.lower()


def operator_consistency_check(check: Check) -> Optional[str]:
    """FR-002: deterministic (no LLM call), given a compiled `ratio_threshold`
    Check's own `operator`/`message_pass`, returns a reason string if the
    operator's direction contradicts the natural-language PASS-condition
    phrasing already present in `message_pass`, or `None` if consistent or
    unmeasurable (no recognized phrase found -- Edge Cases: absence of a
    contradiction signal is not evidence of a contradiction, so this is NOT a
    general correctness proof of every check, only detection of this one
    named failure pattern).

    Not restricted to `kind == "ratio_threshold"` by an early return -- callers
    should only invoke this for that kind (the only kind with an `operator`
    field); passing another kind's Check simply won't find phrase signal
    against a meaningless comparison and returns None."""
    if not check.operator or not check.message_pass:
        return None
    text = _normalize_for_phrase_match(check.message_pass)
    upper_hit = any(p in text for p in _UPPER_BOUND_PHRASES) or bool(_UNDER_WITH_NUMBER.search(text))
    lower_hit = any(p in text for p in _LOWER_BOUND_PHRASES)
    if upper_hit and check.operator not in ("<=", "<"):
        return "PASS-text implies <= / < but operator is %s" % check.operator
    if lower_hit and check.operator not in (">=", ">"):
        return "PASS-text implies >= / > but operator is %s" % check.operator
    return None


def compile_batch(rows: List[Dict[str, Any]], catalog: FieldCatalog) -> List[CompiledCheckDraft]:
    """Map step over a whole batch -- one row per call (research.md Decision 1),
    the shape `002a` already proved at n=24."""
    client = _client()
    return [compile_row(client, row, catalog) for row in rows]


# --- 002g: compile-time precondition wiring ----------------------------------

@dataclass
class PreconditionAttachReport:
    """Honest coverage accounting for one attach pass (002g SC-004, mirroring
    002f FR-012's coverage-report discipline): what was attempted, what each
    layer proposed, what actually attached, what needs a human, and which
    novel facts surfaced for vocabulary review (never auto-added)."""
    rows_attempted: int = 0
    proposals_by_layer: Optional[Dict[int, int]] = None
    attached: int = 0
    flagged_for_review: int = 0
    novel_fact_candidates: Optional[List[str]] = None
    layer0_coverage: Optional[Any] = None


def attach_preconditions(
    drafts: List[CompiledCheckDraft],
    rows: List[Dict[str, Any]],
    vocabulary: Any,
    layer1_client: Any = None,
    layer2_client: Any = None,
    corpus_lookup: Any = None,
) -> PreconditionAttachReport:
    """002g FR-001/FR-002: run `002f`'s pipeline once over the batch, resolve
    each proposal against the SIGNED canonical-fact vocabulary, and set
    `applies_if` on the matching draft's compiled Check.

    Attach policy (trust tiers, 002f's discipline):
    - Layer 0 (HIGH_AUTO_ELIGIBLE) + resolved  -> `applies_if` attached, with
      provenance recorded on the draft.
    - Layer 0 + unresolved (unmapped answer / spans two facts) -> NO
      `applies_if` (a check gates on a vocabularied fact or not at all);
      draft flagged via `applies_if_review`.
    - Layer 1/2 (MEDIUM/MANDATORY tiers) -> NEVER auto-attached, resolvable
      or not; flagged for the human path. Layer-1 field names are still
      resolved so novel names surface as vocabulary candidates (US2).

    Default is Layer-0-only (`layer1_client=None`) -- zero LLM calls, zero
    cost (FR-007/FR-009); passing real clients is a separate, explicit spend
    decision by the caller. Mutates the drafts' checks in place (the same
    batch-annotation shape `operator_consistency_check` wiring uses) and
    returns the report."""
    from ontology_extraction import pipeline as ontology_pipeline  # noqa: E402
    from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402

    result = ontology_pipeline.run_layers(
        rows, layer1_client=layer1_client, layer2_client=layer2_client,
        corpus_lookup=corpus_lookup,
    )
    drafts_by_row = {d.row_id: d for d in drafts}
    by_layer: Dict[int, int] = {}
    report = PreconditionAttachReport(
        rows_attempted=len(rows), proposals_by_layer=by_layer,
        novel_fact_candidates=[], layer0_coverage=result.coverage,
    )
    for proposal in result.proposals:
        by_layer[proposal.source_layer] = by_layer.get(proposal.source_layer, 0) + 1
        draft = drafts_by_row.get(proposal.row_id)
        if draft is None or draft.check is None:
            continue
        if proposal.source_layer == 0:
            resolution = FV.resolve_layer0(vocabulary, proposal)
            if resolution.status == "resolved":
                existing = draft.check.applies_if or []
                draft.check.applies_if = existing + [resolution.condition]
                draft.applies_if_provenance = (
                    f"layer0 {proposal.provenance} -> fact {resolution.fact_id}")
                report.attached += 1
            else:
                draft.applies_if_review = f"layer0 unresolved: {resolution.reason}"
                report.flagged_for_review += 1
        else:
            # MEDIUM/MANDATORY tier: human path, never auto-attached.
            draft.applies_if_review = (
                f"layer{proposal.source_layer} ({proposal.trust_tier}) "
                "requires human review before gating")
            report.flagged_for_review += 1
            cond = proposal.condition
            if cond is not None:
                name_res = FV.resolve_field_name(vocabulary, cond.field_name)
                if name_res.status == "novel_candidate":
                    if cond.field_name not in report.novel_fact_candidates:
                        report.novel_fact_candidates.append(cond.field_name)
    return report


def assemble_ruleset(
    drafts: List[CompiledCheckDraft], ruleset_id: str, version: int,
    signed_by: str, signed_at: str,
    corrections: Optional[Dict[str, str]] = None,
) -> Ruleset:
    """Batch assembly (US1 Scenario 2, US5): drafts -> a signed Ruleset,
    reusing RuleProvenance/Ruleset unmodified. Drafts with a parse_error (no
    compiled Check) are excluded -- they never reach sign-off. Drafts flagged
    by `operator_consistency_check()` (002d FR-004) are excluded the same
    way -- present in the batch output for SME review, never silently signed.

    `corrections`: check_id -> SME-corrected text, when the SME edited the
    LLM's draft during sign-off (RuleProvenance's edit-distance mechanism,
    FR-004/FR-006). Defaults to signing the LLM draft unedited when absent
    (the sign-off-theater case US2 exists to flag)."""
    corrections = corrections or {}
    checks: List[Check] = []
    provenance: List[RuleProvenance] = []
    intent_records: List[RuleIntentRecord] = []
    for d in drafts:
        if d.check is None:
            continue
        if d.operator_consistency_flag is not None:
            continue
        checks.append(d.check)
        llm_draft_text = json.dumps(d.check.to_dict(), sort_keys=True)
        signed_text = corrections.get(d.check.id, llm_draft_text)
        provenance.append(RuleProvenance(
            check_id=d.check.id, llm_draft=llm_draft_text,
            signed_text=signed_text, signed_by=signed_by, signed_at=signed_at,
        ))
        intent_records.append(RuleIntentRecord(
            check_id=d.check.id, source_text=d.source_text,
            extracted_intent=d.extracted_intent,
        ))
    return Ruleset(
        ruleset_id=ruleset_id, version=version, checks=checks,
        provenance=provenance, intent_records=intent_records,
    )
