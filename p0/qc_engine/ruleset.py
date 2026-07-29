"""
The signed ruleset artifact — the thing the regulator actually audits.

The judge's CRITICAL ruling #2: "compile once + SME sign-off" only works if the
signature binds to the HUMAN-CORRECTED artifact, not the raw LLM draft, and if
we MEASURE how much the human actually changed. Zero edits across thousands of
rules is a red flag (sign-off theater), not a win.

A ruleset is:
  - a set of checks (each: a deterministic comparison spec) and reconciliation
    transforms (normalizer + tolerance) — both authored data, no code,
  - per-rule provenance: the LLM draft, the signed (corrected) version, who
    signed it, and the edit-distance between them,
  - a canonical SHA-256 over the signed content + a pinned engine version.

The runtime loads a ruleset BY HASH. Same hash -> same rules -> same verdicts.

Python 3.9 compatible.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

ENGINE_VERSION = "p0-1.0.0"  # pinned; part of the determinism contract


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein distance — the SME-correction metric (ruling #2)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1]


@dataclass
class Check:
    """A single deterministic assertion over the canonical loan.

    phase (the product's two-step):
      - "RECONCILE": compare the closing document (truth) vs the system data and
        surface discrepancies (kinds: agree_categorical, agree_numeric).
      - "QC": run a policy/compliance rule against the data, regardless of
        source agreement (kinds: predicate, ratio_threshold, agree_doc_categorical,
        agree_doc_numeric).

    kind:
      - "agree_categorical": doc vs system agree under `normalizer`  [RECONCILE]
      - "agree_numeric": doc vs system agree within `tolerance`       [RECONCILE]
      - "predicate": a named boolean policy predicate (e.g. signed)   [QC]
      - "ratio_threshold": a derived ratio (ltv/dti) vs `threshold`   [QC]
      - "agree_doc_categorical": field_name's doc value vs
        compare_field_name's doc value agree under `normalizer`       [QC]
        (003d -- two independently-extracted DOCUMENT values, neither
        a system source; never reads sources{} on either side, unlike
        agree_categorical. QC phase, not RECONCILE: a mismatch here is
        a genuine defect in the closing package itself, not "the
        system hasn't caught up yet" -- so it resolves FAIL, not the
        informational FLAG agree_categorical produces on disagreement.)
      - "agree_doc_numeric": same as agree_doc_categorical but numeric,
        within `tolerance`                                            [QC]
    """
    id: str
    name: str
    field_name: str
    kind: str
    severity: str  # CRITICAL | WARNING | INFO
    phase: str = ""  # "RECONCILE" | "QC"; defaults inferred from kind if blank
    sources: List[str] = field(default_factory=list)
    normalizer: str = "identity"
    tolerance: str = "0"          # Decimal string, authored
    predicate: str = ""           # for kind=predicate
    ratio: str = ""               # "ltv" | "dti" | "field_value" for kind=ratio_threshold
    threshold: str = ""           # Decimal string percent, authored
    operator: str = "<="          # comparison for ratio_threshold
    message_pass: str = ""
    message_fail: str = ""
    compare_field_name: Optional[str] = None  # 003d: second field, for
    # kind=agree_doc_categorical|agree_doc_numeric only. None for every
    # other kind.
    # 002e: an AND-combined list of loan-fact preconditions gating whether
    # this check applies at all, evaluated before kind-dispatch. Each
    # condition: {"field_name": ..., "operator": "=="|"!="|"<="|">="|"<"|">"
    # |"in"|"between", "value": <string; "|"-delimited for in/between>}.
    # None (the default) is unconditional -- today's universal behavior,
    # unchanged for every check that doesn't set this.
    applies_if: Optional[List[Dict[str, str]]] = None
    # AMQ "Question Code" (row.get("qcode")) this check was compiled from --
    # audit/traceability metadata only, never read by the engine at
    # evaluation time. None for checks compiled before this field existed,
    # or for any check not sourced from an AMQ row.
    question_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuleProvenance:
    """Per-rule audit of the compile->correct->sign loop (ruling #2)."""
    check_id: str
    llm_draft: str            # what the LLM compiled
    signed_text: str          # what the human approved (possibly corrected)
    signed_by: str
    signed_at: str            # ISO; injected, never wall-clock inside engine
    edit_distance: int = 0

    def __post_init__(self) -> None:
        self.edit_distance = _edit_distance(self.llm_draft, self.signed_text)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuleIntentRecord:
    """The permanent (source text -> extracted intent) leg of the compile audit
    triple (002b FR-011). The third leg -- the deterministic logic -- is the
    Check itself (Ruleset.checks), not duplicated here.

    Retained for the life of the signed artifact; never read by the engine at
    evaluation time (Principle II is unchanged -- this is an audit-record
    field, not a second execution path)."""
    check_id: str
    source_text: str
    extracted_intent: str
    # Where source_text came from in the real AMQ workbook, formatted as
    # "<source_file>:<sheet>:<source_row>" -- a plain string, not a nested
    # object, matching this dataclass's existing style. None when the row
    # didn't carry a locator (e.g. synthetic/test rows, or compiled before
    # this field existed).
    source_locator: Optional[str] = None
    # 002c grounding provenance, carried onto the signed artifact (previously
    # computed per-check in compile_row() but dropped before assembly).
    kb_program: Optional[str] = None
    kb_version: Optional[int] = None
    section_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Ruleset:
    ruleset_id: str
    version: int
    checks: List[Check] = field(default_factory=list)
    provenance: List[RuleProvenance] = field(default_factory=list)
    intent_records: List[RuleIntentRecord] = field(default_factory=list)
    engine_version: str = ENGINE_VERSION

    def intent_for(self, check_id: str) -> Optional[RuleIntentRecord]:
        return next((r for r in self.intent_records if r.check_id == check_id), None)

    # --- the canonical, hashable content -----------------------------------
    def canonical_content(self) -> Dict[str, Any]:
        """The exact bytes the signature covers. Sorted, stable JSON."""
        return {
            "ruleset_id": self.ruleset_id,
            "version": self.version,
            "engine_version": self.engine_version,
            "checks": [c.to_dict() for c in self.checks],
        }

    def sha256(self) -> str:
        blob = json.dumps(self.canonical_content(), sort_keys=True,
                          separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    # --- sign-off integrity (ruling #2) ------------------------------------
    def unedited_rules(self) -> List[str]:
        """Rules the SME signed WITHOUT changing the LLM draft at all.

        Surfaced loudly: a high count is the sign-off-theater smell the judge
        warned about. The demo shows this on screen.
        """
        return [p.check_id for p in self.provenance if p.edit_distance == 0]

    def signoff_summary(self) -> Dict[str, Any]:
        total = len(self.provenance)
        edited = sum(1 for p in self.provenance if p.edit_distance > 0)
        return {
            "rules_total": total,
            "rules_edited_by_sme": edited,
            "rules_unedited": total - edited,
            "mean_edit_distance": (
                round(sum(p.edit_distance for p in self.provenance) / total, 2)
                if total else 0
            ),
        }

    def to_json(self) -> str:
        return json.dumps({
            "content": self.canonical_content(),
            "sha256": self.sha256(),
            "provenance": [p.to_dict() for p in self.provenance],
            "intent_records": [r.to_dict() for r in self.intent_records],
            "signoff_summary": self.signoff_summary(),
        }, indent=2, sort_keys=True)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Ruleset":
        content = d["content"]
        rs = Ruleset(
            ruleset_id=content["ruleset_id"],
            version=content["version"],
            engine_version=content.get("engine_version", ENGINE_VERSION),
            checks=[Check(**c) for c in content["checks"]],
            provenance=[RuleProvenance(
                check_id=p["check_id"], llm_draft=p["llm_draft"],
                signed_text=p["signed_text"], signed_by=p["signed_by"],
                signed_at=p["signed_at"],
            ) for p in d.get("provenance", [])],
            intent_records=[RuleIntentRecord(
                check_id=r["check_id"], source_text=r["source_text"],
                extracted_intent=r["extracted_intent"],
                source_locator=r.get("source_locator"),
                kb_program=r.get("kb_program"),
                kb_version=r.get("kb_version"),
                section_ids=r.get("section_ids"),
            ) for r in d.get("intent_records", [])],
        )
        return rs
