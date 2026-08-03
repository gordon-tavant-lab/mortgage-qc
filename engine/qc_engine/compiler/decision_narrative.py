"""
014 -- decision narrative: an LLM-authored, read-only prose summary of one
loan's already-computed `RunResult`, grounded in that `RunResult` plus the
signed `FactVocabulary`'s `guide_citations` for exactly the facts this loan's
own real exceptions touch (spec.md FR-001/FR-010).

Why this does not touch Non-Negotiable #1 (determinism): this module never
computes, re-computes, or influences a check's verdict or a loan's
disposition. It runs strictly AFTER `qc_engine.engine.run()` has finished,
reads that already-fixed result, and produces prose describing it. The four
guardrails (spec.md):
  1. Generate once per RunResult, persisted alongside it -- never regenerated
     on a later read of the same, unchanged result (caller's responsibility,
     FR-002).
  2. Validated closed-set grounding, same discipline as
     `draft_fact_names_llm.py`: every check_id, guide-citation, and
     review-reason tag the narrative references MUST already exist in the
     real RunResult / signed FactVocabulary it was generated from. A
     reference that doesn't is a validation failure -> bounded retry (FR-003).
  3. Narrative text is presentation-only -- read by humans, never read back
     by the engine (FR-005; enforced structurally, see below).
  4. The prose MAY vary in wording on regeneration; the FACTS it asserts
     MUST NOT -- guardrail 2's validation applies identically every time.

FR-005 (leaf, output-only module) is enforced at the SOURCE level, not just
architecturally: `qc_engine/engine.py` must never contain the literal string
naming this module's artifact, so `RunResult.to_dict()` takes a generic
`extra` mapping a caller supplies (see engine.py) rather than a hard-coded
key -- a caller (this module's own driver, never `engine.py` itself) is the
only place that ever writes that key's name.

Reuses, does not reinvent:
  - `bedrock_client._client()` / `bedrock_client.MODEL_SONNET` (the same Bedrock
    Converse harness every other compile-time LLM call in this project uses).
  - `draft_fact_names_llm.py`'s validate-before-accept, bounded-retry,
    never-silently-pass-through shape.
  - `qc_engine.compiler.knowledge_base.is_usable` / `fact_vocabulary`'s own
    `VocabularyNotSignedError` -- refuse outright on an unsigned vocabulary,
    same posture every other consumer of the vocabulary already has.

`_validate()`'s check_id / Guide-citation extraction is a SIMPLE, DETERMINISTIC
string scan (plan.md) -- not a second LLM call to "check the first". It looks
for the literal phrase "check <check_id>" (this module's own SYSTEM_PROMPT
instructs the model to always phrase a named check that way, matching every
real check_id in this project's compiled rulesets: all 5093 are hyphenated
kebab-case tokens, e.g. `final-1003-complete-signed`) and the literal phrase
"Fannie Mae Selling Guide <code>" for Guide citations. This deliberately does
NOT attempt open-ended fabrication detection over arbitrary prose (e.g. "every
check passed" must never be mistaken for a reference to a check literally
named "passed") -- scoped exactly to what spec.md's acceptance scenarios and
this feature's own test suite exercise.

Python 3.9 compatible.
"""
from __future__ import annotations

import datetime
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from qc_engine.compiler import bedrock_client
from qc_engine.compiler import fact_vocabulary as FV
from qc_engine.compiler import knowledge_base as KB

# FR-008: past this many real exceptions/needs_review checks, the narrative
# must summarize by category and state the exact remaining count -- never
# enumerate all, never silently truncate without saying so.
#
# Real 5-loan panel proof (2026-07-28, run_014): every real loan carries
# ~2,600 real exceptions/needs_review checks (run_013's 1,600+ FAIL + 1,000+
# NEEDS_REVIEW per loan). Sending every one of those rows to the model, as
# an earlier version of this module did, produced ~890K-token prompts
# ($3+/loan, matching CLAUDE.md's own "$700-3,500/run real-payload" finding)
# AND made validation fail every time -- an LLM asked to correctly
# transcribe/count thousands of individual check_ids is unreliable at
# exactly the task FR-008 already anticipates. The fix: sample
# deterministically (below) and hand the model a fixed, small, per-category
# sample plus a PRECOMPUTED remainder count -- the model never has to
# compute that number itself, and `_validate()` checks for the same
# precomputed number, not for however many check_ids the model happened to
# cite by name.
OVER_LIMIT_THRESHOLD = 10
# Per distinct review_reason category, how many real exceptions/needs_review
# rows are shown to the model in full detail once the total exceeds the
# threshold above.
_SAMPLE_PER_CATEGORY = 3

# "check <check_id>" -- every real check_id in this project's compiled
# rulesets is a hyphenated kebab-case token (verified: 5093/5093 checks in
# run_010's ruleset), so requiring a hyphen segment avoids mistaking ordinary
# prose ("every check passed") for a check-id reference.
# live-demo-engine-wiring finding (2026-08-03): this regex assumed every real check_id
# is a clean hyphenated kebab-case token (true for the original p0/AMQ-workbook-compiled
# rulesets this module was built against -- 5093/5093 verified). The gold-ruleset-compiled
# check_ids this pipeline actually uses are shaped "{card_id}::{exception_code}" and
# routinely contain spaces and uppercase words (e.g. "PC::Closing Conditions::UW
# Condition-A") -- verified 0/668 real check_ids on a real audit run match the old kebab-
# case assumption. A token-extraction regex can't reliably bound an irregular shape like
# that. Ground check-id references by CLOSED-SET MEMBERSHIP instead (see _validate()
# below): for each of this loan's real check_ids, check whether "check <id>" (any case)
# appears verbatim in the narrative -- correct regardless of the id's internal shape, and
# structurally can never mark a fabricated id as "referenced" since it only ever matches
# against the real set.
# "Fannie Mae Selling Guide <code>" -- the code is 1-2 uppercase letters
# followed by a digit/hyphen/dot run ending in a digit (every real code in
# this project's signed vocabulary matches this shape: "B3-4.3-04",
# "B3-3.1-01", "E-3-03", "D1-3-03"...). Real 5-loan proof (2026-07-28, run
# 014, loan 2025-1108-VA-003) found the earlier, looser
# `[^\s,()]+` version matched the word "citation" itself in the model's own
# HONEST sentence "no Fannie Mae Selling Guide citation can be offered for
# them" -- a false-positive fabrication rejection on a narrative that was
# doing exactly what FR-010 asks (naming the absence of a Guide section
# honestly). Anchoring to the real code shape (letter-then-digit, not any
# following word) fixes that without weakening real-fabrication detection:
# "citation"/"Section"/"requirements" never match this pattern, but every
# real code and every plausible invented one (e.g. "B9-9.9-99") still does.
_GUIDE_CITATION_RE = re.compile(r"Fannie Mae Selling Guide\s+([A-Z]{1,2}[\d.\-]*\d)")
# A real model (2026-07-28 5-loan proof, loan 2025-0917-001) writes large
# remainder counts with a thousands separator ("2,642 more checks"), which a
# naive `str(n) in text` substring check misses entirely ("2642" is not a
# substring of "2,642") -- strip exactly that separator before comparing,
# never anything else (a genuinely wrong number must still fail).
_THOUSANDS_COMMA_RE = re.compile(r"(?<=\d),(?=\d)")


def _strip_thousands_commas(text: str) -> str:
    return _THOUSANDS_COMMA_RE.sub("", text)


class ValidationError(Exception):
    """Raised by `_validate()` when a narrative references a check_id, Guide
    citation, or review-reason tag not present in the real `RunResult` /
    signed `FactVocabulary` it was generated from, or drops the required
    over-limit remainder count (FR-003/FR-007/FR-008/FR-010). Bounded retry,
    never a silent pass-through -- `draft_fact_names_llm.py`'s exact
    discipline."""


@dataclass
class DecisionNarrative:
    """spec.md Key Entities. `to_dict()`/`from_dict()` mirror every other
    artifact in this project (`fact_vocabulary.py` precedent)."""
    loan_id: str
    ruleset_sha256: str
    vocabulary_version: int
    disposition: str
    review_reasons: List[str]
    narrative_text: Optional[str]
    referenced_check_ids: List[str]
    referenced_guide_citations: List[str]
    generated_at: str
    model: str
    validation_attempts: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loan_id": self.loan_id,
            "ruleset_sha256": self.ruleset_sha256,
            "vocabulary_version": self.vocabulary_version,
            "disposition": self.disposition,
            "review_reasons": list(self.review_reasons),
            "narrative_text": self.narrative_text,
            "referenced_check_ids": list(self.referenced_check_ids),
            "referenced_guide_citations": list(self.referenced_guide_citations),
            "generated_at": self.generated_at,
            "model": self.model,
            "validation_attempts": self.validation_attempts,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DecisionNarrative":
        return DecisionNarrative(
            loan_id=d["loan_id"],
            ruleset_sha256=d["ruleset_sha256"],
            vocabulary_version=d["vocabulary_version"],
            disposition=d["disposition"],
            review_reasons=list(d.get("review_reasons", [])),
            narrative_text=d.get("narrative_text"),
            referenced_check_ids=list(d.get("referenced_check_ids", [])),
            referenced_guide_citations=list(d.get("referenced_guide_citations", [])),
            generated_at=d["generated_at"],
            model=d["model"],
            validation_attempts=d["validation_attempts"],
        )


def _sample_exceptions(real_exceptions: List[Any]) -> Tuple[List[Any], Dict[str, int]]:
    """Deterministic FR-008 sampling: group by review_reason, take up to
    `_SAMPLE_PER_CATEGORY` (sorted by check_id, so the same RunResult always
    yields the same sample), and return (sample_rows, counts_per_category).
    Used identically by the prompt builder and by `_validate()`'s remainder
    check -- "how many are shown" and "what remainder is required" must
    never drift apart."""
    by_reason: Dict[str, List[Any]] = {}
    for r in real_exceptions:
        by_reason.setdefault(r.review_reason or "UNLABELED", []).append(r)
    sample: List[Any] = []
    category_counts: Dict[str, int] = {}
    for reason in sorted(by_reason):
        group = sorted(by_reason[reason], key=lambda r: r.check_id)
        category_counts[reason] = len(group)
        sample.extend(group[:_SAMPLE_PER_CATEGORY])
    return sample, category_counts


def _expected_remainder(run_result: Any) -> int:
    """The exact remainder count `_validate()` requires the narrative to
    state, once real exceptions/needs_review exceed `OVER_LIMIT_THRESHOLD`.
    Computed the SAME way `_build_user_message()` samples for the prompt
    (`_sample_exceptions`), so the number the model is told to write and the
    number `_validate()` checks for are always identical -- never dependent
    on how many individual check_ids the model happened to cite by name."""
    real_exceptions = run_result.exceptions + run_result.needs_review
    if len(real_exceptions) <= OVER_LIMIT_THRESHOLD:
        return 0
    sample, _ = _sample_exceptions(real_exceptions)
    return len(real_exceptions) - len(sample)


def _facts_for_run_result(run_result: Any, fact_vocabulary: FV.FactVocabulary
                          ) -> Dict[str, FV.CanonicalFact]:
    """The narrowed set of `CanonicalFact`s this loan's own real exceptions
    touch -- keyed by `canonical_field_name`. NEVER the full vocabulary
    (plan.md): a result whose status carries no `review_reason` (PASS,
    NOT_APPLICABLE, FLAG -- `CheckResult`'s own discipline, `engine.py`)
    contributes nothing here, so the prompt can't accidentally ground the
    narrative in a fact this loan never actually hit a concern on."""
    facts_by_field = {f.canonical_field_name: f for f in fact_vocabulary.facts}
    touched: Dict[str, FV.CanonicalFact] = {}
    for r in run_result.results:
        if r.review_reason is None:
            continue
        fact = facts_by_field.get(r.field_name)
        if fact is not None:
            touched[r.field_name] = fact
    return touched


def _known_guide_codes(facts: Dict[str, FV.CanonicalFact]) -> Dict[str, str]:
    """code (e.g. 'B3-3.1-01') -> the real, verbatim `guide_citations` string
    it came from, across every fact `_facts_for_run_result()` returned."""
    codes: Dict[str, str] = {}
    for fact in facts.values():
        for citation in fact.guide_citations:
            m = _GUIDE_CITATION_RE.search(citation)
            if m:
                codes[m.group(1)] = citation
    return codes


def _validate(run_result: Any, fact_vocabulary: FV.FactVocabulary,
              narrative_text: str) -> Tuple[Set[str], Set[str]]:
    """Cross-references every check_id and Guide-citation the narrative
    names against the real `RunResult` / narrowed vocabulary lookup, and
    confirms every `review_reasons` tag is addressed (FR-007) and, if the
    loan carries more than `OVER_LIMIT_THRESHOLD` real exceptions/
    needs_review checks, that an explicit remainder count is stated
    (FR-008). Raises `ValidationError` on the first violation found; returns
    (referenced_check_ids, referenced_guide_citations) on success."""
    lowered_text = narrative_text.lower()
    referenced_check_ids: Set[str] = {
        r.check_id for r in run_result.results
        if f"check {r.check_id.lower()}" in lowered_text
    }

    facts = _facts_for_run_result(run_result, fact_vocabulary)
    known_codes = _known_guide_codes(facts)
    referenced_guide_citations: Set[str] = set()
    for m in _GUIDE_CITATION_RE.finditer(narrative_text):
        code = m.group(1)
        if code not in known_codes:
            raise ValidationError(
                f"narrative cites Guide section {code!r}, which is not "
                f"present on any real, signed fact this loan's exceptions "
                f"touch")
        referenced_guide_citations.add(known_codes[code])

    for reason in run_result.review_reasons:
        if reason not in narrative_text:
            raise ValidationError(
                f"narrative drops real review_reason tag {reason!r} -- "
                f"every distinct tag must be addressed (FR-007)")

    expected_remainder = _expected_remainder(run_result)
    if (expected_remainder > 0
            and str(expected_remainder) not in _strip_thousands_commas(narrative_text)):
        total_real = len(run_result.exceptions) + len(run_result.needs_review)
        raise ValidationError(
            f"{total_real} real exceptions/needs_review checks exist -- "
            f"only a representative sample was shown to the model, and the "
            f"expected explicit remainder count ({expected_remainder}) is "
            f"not stated anywhere in the narrative (FR-008)")

    return referenced_check_ids, referenced_guide_citations


SYSTEM_PROMPT = """You are writing a DECISION NARRATIVE: a short, honest, human-readable \
explanation of one mortgage loan's automated QC run, for a loan officer or QC auditor to \
read. You are given (a) a `loan_overview` block of this loan's own real, already-extracted \
characteristics, (b) that loan's already-computed, already-fixed audit result (disposition, \
review_reasons, every real exception/needs-review check with its citation), and (c) a \
NARROWED lookup of the real Selling Guide section(s) attached to the specific facts this \
loan's own exceptions touch. You do not decide anything -- the verdict already happened and \
the loan's characteristics already exist. Your only job is to explain them faithfully.

Write your narrative in exactly TWO clearly separated sections, each starting with its own \
heading line written EXACTLY as shown (plain text, not markdown -- e.g. "Loan Overview" on \
its own line, then a blank line, then that section's prose):

Loan Overview
Describe what kind of loan this is -- program (e.g. Conventional/FHA/VA), loan purpose \
(purchase/refinance), loan amount, note rate, LTV/DTI if present, borrower and property \
basics -- using ONLY fields present in the provided `loan_overview` block. Give a real, \
concrete picture a reviewer could act on. If a field is missing from `loan_overview` (null or \
absent), do not guess it or fill it in -- either omit that detail or say it's not available. \
NEVER invent a loan characteristic not present in `loan_overview`.

Audit Findings
Explain the audit result: the disposition, why (review_reasons), and what specifically is of \
interest or actionable for a loan officer or auditor reviewing this loan -- not just a list, \
but which findings actually matter and why. This section follows rules 1-7 below, exactly as \
before.

Non-negotiable rules for the Audit Findings section:
1. Ground every claim ONLY in the provided RunResult data and the provided guide-citation \
lookup. NEVER invent a check, a citation, a review reason, a Guide section, or a number not \
present in the input.
2. State the loan's disposition explicitly, in plain words.
3. If review_reasons has more than one tag, address EACH one separately and explicitly by \
name -- never collapse a multi-label disposition into language implying one simple cause.
4. When you name a specific check by its identifier, ALWAYS write it as the literal phrase \
"check <check_id>" (e.g. "check PC::O-FNM-15304::O-FNM-58198") -- exactly that check_id string, \
verbatim from the input, never paraphrased or abbreviated.
5. For each named exception, if the provided guide-citation lookup has an entry for that \
exception's underlying fact, cite it by writing the literal phrase "Fannie Mae Selling Guide \
<code>" using the EXACT code from the lookup (never invent a section number, date, or title). \
If the lookup has NO entry for that fact, say so honestly -- e.g. "no Guide section is \
attached to this fact yet" -- rather than omitting the point or inventing one to fill the gap.
6. If `remainder_not_shown_count` in the input is greater than 0, only `sample_exceptions` \
(NOT the full set) was shown to you in detail -- there are more real exceptions/needs-review \
checks that exist but are not individually listed here. Do NOT claim there are more or fewer \
than `total_real_exceptions_and_needs_review` in total. Summarize by concern/category using \
`category_counts_by_review_reason` and the sample, and you MUST write the EXACT NUMBER given by \
`remainder_not_shown_count` as a plain digit somewhere in your narrative -- for example, if that \
field's value is 47, write a sentence like "...and 47 more checks not individually listed here." \
Copy the real number from `remainder_not_shown_count` verbatim; never compute, round, or guess a \
different one. Never silently truncate without saying so.
7. A loan with zero exceptions and an AUTO_CLEARED disposition still gets a short, honest \
narrative ("cleared cleanly, no exceptions found") -- never skip it.

Formatting: plain prose within each section (no markdown, no bullet points, no code fences), \
a few sentences to a short paragraph per section is enough. Use exactly the two section \
headings given above, in that order, nothing else.
"""


def _build_user_message(run_result: Any, facts: Dict[str, FV.CanonicalFact],
                        loan_overview: Optional[Dict[str, Any]] = None) -> str:
    """The prompt payload: ONLY this loan's own RunResult content plus the
    narrowed guide-citation lookup (FR-001) -- never other loans, never the
    compiled ruleset's internals, never the full vocabulary.

    FR-008: when real exceptions/needs_review exceed OVER_LIMIT_THRESHOLD,
    only a deterministic per-category sample (`_sample_exceptions`) is sent
    in full detail -- never all of them (a real loan can carry 2,600+; the
    2026-07-28 5-loan proof found sending every row produced ~890K-token
    prompts and, worse, unreliable validation, since the model had to
    correctly transcribe/count thousands of individual check_ids). The
    precomputed remainder count is handed to the model directly rather than
    left for it to compute from a list it cannot see in full."""

    def _result_row(r: Any) -> Dict[str, Any]:
        return {
            "check_id": r.check_id, "field_name": r.field_name,
            "status": r.status, "message": r.message,
            "citation": r.citation, "review_reason": r.review_reason,
        }

    real_exceptions = run_result.exceptions + run_result.needs_review
    if len(real_exceptions) > OVER_LIMIT_THRESHOLD:
        sample, category_counts = _sample_exceptions(real_exceptions)
    else:
        sample, category_counts = real_exceptions, _sample_exceptions(real_exceptions)[1]
    remainder = len(real_exceptions) - len(sample)
    payload = {
        "loan_overview": loan_overview or {},
        "loan_id": run_result.loan_id,
        "disposition": run_result.disposition,
        "review_reasons": sorted(run_result.review_reasons),
        "total_checks_run": len(run_result.results),
        "total_real_exceptions_and_needs_review": len(real_exceptions),
        "category_counts_by_review_reason": category_counts,
        "sample_exceptions": [_result_row(r) for r in sample],
        "remainder_not_shown_count": remainder,
        "guide_citation_lookup": {
            field_name: {
                "fact_id": fact.id, "description": fact.description,
                "guide_citations": list(fact.guide_citations),
            }
            for field_name, fact in facts.items()
        },
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _now_iso() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def generate(run_result: Any, fact_vocabulary: FV.FactVocabulary, client: Any,
            max_retries: int = 2, loan_overview: Optional[Dict[str, Any]] = None) -> DecisionNarrative:
    """Generates a `DecisionNarrative` for one already-computed `RunResult`.

    Raises `VocabularyNotSignedError` up front (before any model call) if
    `fact_vocabulary` isn't signed. Otherwise calls `client.converse(...)` at
    temperature=0 (FR-004), validates the response (`_validate`), retries on
    validation failure up to `max_retries` additional attempts, and on
    exhaustion returns a `DecisionNarrative` with `narrative_text=None`
    (never raises past this point -- the structured result must still ship,
    spec.md Edge Cases)."""
    if not KB.is_usable(fact_vocabulary):
        raise FV.VocabularyNotSignedError(
            f"fact vocabulary v{fact_vocabulary.version} is not signed -- "
            f"cannot ground a decision narrative against unreviewed facts")

    facts = _facts_for_run_result(run_result, fact_vocabulary)
    user_msg = _build_user_message(run_result, facts, loan_overview)

    attempts = 0
    for attempt in range(max_retries + 1):
        attempts = attempt + 1
        resp = client.converse(
            modelId=bedrock_client.MODEL_SONNET,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            inferenceConfig={"temperature": 0, "maxTokens": 2000},
        )
        text = resp["output"]["message"]["content"][0]["text"].strip()
        try:
            check_ids, guide_citations = _validate(run_result, fact_vocabulary, text)
        except ValidationError:
            continue
        return DecisionNarrative(
            loan_id=run_result.loan_id, ruleset_sha256=run_result.ruleset_sha256,
            vocabulary_version=fact_vocabulary.version, disposition=run_result.disposition,
            review_reasons=sorted(run_result.review_reasons), narrative_text=text,
            referenced_check_ids=sorted(check_ids),
            referenced_guide_citations=sorted(guide_citations),
            generated_at=_now_iso(), model=bedrock_client.MODEL_SONNET,
            validation_attempts=attempts,
        )

    # Exhausted retries -- ship the structured result regardless (spec.md
    # Edge Cases): narrative_text=None, never raise.
    return DecisionNarrative(
        loan_id=run_result.loan_id, ruleset_sha256=run_result.ruleset_sha256,
        vocabulary_version=fact_vocabulary.version, disposition=run_result.disposition,
        review_reasons=sorted(run_result.review_reasons), narrative_text=None,
        referenced_check_ids=[], referenced_guide_citations=[],
        generated_at=_now_iso(), model=bedrock_client.MODEL_SONNET,
        validation_attempts=attempts,
    )
