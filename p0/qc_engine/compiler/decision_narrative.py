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
  - `compile_llm._client()` / `compile_llm.MODEL_SONNET` (the same Bedrock
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

from qc_engine.compiler import compile_llm
from qc_engine.compiler import fact_vocabulary as FV
from qc_engine.compiler import knowledge_base as KB

# FR-008: past this many real exceptions/needs_review checks, the narrative
# must summarize by category and state the exact remaining count -- never
# enumerate all, never silently truncate without saying so.
OVER_LIMIT_THRESHOLD = 10

# "check <check_id>" -- every real check_id in this project's compiled
# rulesets is a hyphenated kebab-case token (verified: 5093/5093 checks in
# run_010's ruleset), so requiring a hyphen segment avoids mistaking ordinary
# prose ("every check passed") for a check-id reference.
_CHECK_ID_RE = re.compile(r"\bcheck\s+([A-Za-z][\w]*(?:-[\w]+)+)")
# "Fannie Mae Selling Guide <code>" -- code runs up to the first whitespace,
# comma, or parenthesis, matching every real guide_citations string this
# project's signed vocabulary carries (e.g. "... B3-4.3-04, Personal Gifts
# (02/04/2026)" and the simpler "... B3-3.1-01 (Employment History)").
_GUIDE_CITATION_RE = re.compile(r"Fannie Mae Selling Guide\s+([^\s,()]+)")


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
    real_check_ids = {r.check_id for r in run_result.results}
    referenced_check_ids: Set[str] = set()
    for m in _CHECK_ID_RE.finditer(narrative_text):
        token = m.group(1)
        if token not in real_check_ids:
            raise ValidationError(
                f"narrative references check_id {token!r}, which is not "
                f"present in this loan's real RunResult")
        referenced_check_ids.add(token)

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

    real_exception_ids = ([r.check_id for r in run_result.exceptions]
                          + [r.check_id for r in run_result.needs_review])
    if len(real_exception_ids) > OVER_LIMIT_THRESHOLD:
        named = referenced_check_ids & set(real_exception_ids)
        remainder = len(real_exception_ids) - len(named)
        if remainder > 0 and str(remainder) not in narrative_text:
            raise ValidationError(
                f"{len(real_exception_ids)} real exceptions/needs_review "
                f"checks exist but only {len(named)} are named, and the "
                f"explicit remainder count ({remainder}) is not stated "
                f"anywhere in the narrative (FR-008)")

    return referenced_check_ids, referenced_guide_citations


SYSTEM_PROMPT = """You are writing a DECISION NARRATIVE: a short, honest, human-readable \
explanation of why one mortgage loan's automated QC run produced the disposition it did. \
You are given that loan's already-computed, already-fixed result (disposition, \
review_reasons, every real exception/needs-review check with its citation) and a NARROWED \
lookup of the real Selling Guide section(s) attached to the specific facts this loan's own \
exceptions touch. You do not decide anything -- the verdict already happened. Your only job \
is to explain it faithfully.

Non-negotiable rules:
1. Ground every claim ONLY in the provided RunResult data and the provided guide-citation \
lookup. NEVER invent a check, a citation, a review reason, a Guide section, or a number not \
present in the input.
2. State the loan's disposition explicitly, in plain words.
3. If review_reasons has more than one tag, address EACH one separately and explicitly by \
name -- never collapse a multi-label disposition into language implying one simple cause.
4. When you name a specific check by its identifier, ALWAYS write it as the literal phrase \
"check <check_id>" (e.g. "check final-1003-complete-signed") -- exactly that check_id string, \
verbatim from the input, never paraphrased or abbreviated.
5. For each named exception, if the provided guide-citation lookup has an entry for that \
exception's underlying fact, cite it by writing the literal phrase "Fannie Mae Selling Guide \
<code>" using the EXACT code from the lookup (never invent a section number, date, or title). \
If the lookup has NO entry for that fact, say so honestly -- e.g. "no Guide section is \
attached to this fact yet" -- rather than omitting the point or inventing one to fill the gap.
6. If there are more than 10 real exceptions/needs-review checks, do NOT enumerate every one. \
Summarize by concern/category, name a small representative set of the highest-severity items, \
and STATE THE EXACT COUNT of the remaining checks as a plain number (e.g. "...and 23 more \
FAIL-status checks"). Never silently truncate without saying so.
7. A loan with zero exceptions and an AUTO_CLEARED disposition still gets a short, honest \
narrative ("cleared cleanly, no exceptions found") -- never skip it.
8. Plain prose. No markdown, no bullet points, no code fences. A few sentences to a short \
paragraph is enough.
"""


def _build_user_message(run_result: Any, facts: Dict[str, FV.CanonicalFact]) -> str:
    """The prompt payload: ONLY this loan's own RunResult content plus the
    narrowed guide-citation lookup (FR-001) -- never other loans, never the
    compiled ruleset's internals, never the full vocabulary."""

    def _result_row(r: Any) -> Dict[str, Any]:
        return {
            "check_id": r.check_id, "field_name": r.field_name,
            "status": r.status, "message": r.message,
            "citation": r.citation, "review_reason": r.review_reason,
        }

    real_exceptions = run_result.exceptions + run_result.needs_review
    payload = {
        "loan_id": run_result.loan_id,
        "disposition": run_result.disposition,
        "review_reasons": sorted(run_result.review_reasons),
        "total_checks_run": len(run_result.results),
        "total_real_exceptions_and_needs_review": len(real_exceptions),
        "exceptions_and_needs_review": [_result_row(r) for r in real_exceptions],
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
            max_retries: int = 2) -> DecisionNarrative:
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
    user_msg = _build_user_message(run_result, facts)

    attempts = 0
    for attempt in range(max_retries + 1):
        attempts = attempt + 1
        resp = client.converse(
            modelId=compile_llm.MODEL_SONNET,
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
            generated_at=_now_iso(), model=compile_llm.MODEL_SONNET,
            validation_attempts=attempts,
        )

    # Exhausted retries -- ship the structured result regardless (spec.md
    # Edge Cases): narrative_text=None, never raise.
    return DecisionNarrative(
        loan_id=run_result.loan_id, ruleset_sha256=run_result.ruleset_sha256,
        vocabulary_version=fact_vocabulary.version, disposition=run_result.disposition,
        review_reasons=sorted(run_result.review_reasons), narrative_text=None,
        referenced_check_ids=[], referenced_guide_citations=[],
        generated_at=_now_iso(), model=compile_llm.MODEL_SONNET,
        validation_attempts=attempts,
    )
