"""
build_loan_profiles_v4.py -- adds one more derivation on top of v3's 6
(occupancy_type, loan_program, income_type_used_for_qualification,
gift_funds_used, loan_transaction_type, appraisal_in_file), writing
storage/loan_profiles/v4/ (v1/v2/v3 stay untouched -- one file per version,
same precedent that made each prior version a NEW script rather than an edit
to the one before it: a prior version's generator behavior is pinned by
committed tests and artifacts).

Track F (2026-07-28): `applies_if` gating (qc_engine/engine.py's
_eval_applies_if) reads loan.get(field_name).doc, i.e. loan.fields only --
never loan.facts. `doc_present_*` facts (both the 7 that predate this feature
and the 43 Track F adds) live only in loan.facts
(build_fixtures.py::_derive_document_presence_facts), so none of them are
usable in any applies_if condition today. Rather than touch engine.py/model.py
(this project's stated "zero engine changes" ethos for exactly this class of
gap -- see p0/fixtures/from_docs/README.md's Round 7), this reuses the same
profile-promotion mechanism v1-v3 already established: a profile's
derived_facts get merged into loan.fields at load time by both
run_018_guideline_to_loan01_e2e/build_and_run.py and
test_loan01_defects_vs_comprehensive_ruleset.py.

derive_document_presence_passthrough() below is a single generic function,
not one per document type (there are 50 doc_present_* facts total) -- it
copies every loan.facts key starting with "doc_present_" straight into
derived_facts unchanged. This differs from every other derivation in v1-v3
(each of which computes a NEW, semantically-renamed fact from a source field,
e.g. gift_funds_used <- doc_present_gift_letter): a doc_present_* fact's own
name already IS the gating token the compiled ruleset's applies_if conditions
reference directly, so a straight copy is the correct, minimal shape -- there
is nothing to rename or reinterpret.

Run: python3 p0/qc_engine/build_loan_profiles_v4.py
Python 3.9 compatible. Deterministic -- no network, no LLM calls (FR-009).
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
_REPO_ROOT = os.path.dirname(_P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
for _p in (_P0, _FROM_DOCS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fixture_loader import load_canonical_loan  # noqa: E402
from qc_engine.build_loan_profiles_v3 import DERIVATIONS as V3_DERIVATIONS  # noqa: E402
from qc_engine.model import CanonicalLoan  # noqa: E402

LOAN_NUMBERS = ("01", "02", "03", "04", "05")
FIXTURE_DIR = os.path.join(_P0, "fixtures", "from_docs")
PROFILE_VERSION = 4
OUT_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v{}".format(PROFILE_VERSION))

DOC_PRESENCE_PREFIX = "doc_present_"


def derive_document_presence_passthrough(loan: CanonicalLoan) -> Dict[str, Any]:
    """Every loan.facts key starting with "doc_present_" -> an identical
    derived_facts entry (same "true"/"false" string value, no reinterpretation).
    Always returns a derived_facts payload (never underivable) for every
    doc_present_* fact build_fixtures.py computed for this loan -- there is no
    "missing" case here, since build_fixtures.py always writes every key in
    its _DOCUMENT_PRESENCE_SUBSTRINGS dict for every loan."""
    derived_facts: Dict[str, Any] = {}
    for fact_name, value in loan.facts.items():
        if not fact_name.startswith(DOC_PRESENCE_PREFIX):
            continue
        derived_facts[fact_name] = {
            "value": value,
            "derived_from": {"fact": fact_name, "value": value},
            "derivation_rule": (
                "straight passthrough of a doc_present_* routing/gating fact "
                "already computed by build_fixtures.py's "
                "_derive_document_presence_facts -- the fact's own name is "
                "already the canonical applies_if gating token, so no "
                "renaming or reinterpretation applies (Track F, 2026-07-28)"
            ),
            "derivation_kind": "computed",
        }
    return {"derived_facts": derived_facts}


DERIVATIONS = tuple(V3_DERIVATIONS) + (derive_document_presence_passthrough,)


def build_profile(loan: CanonicalLoan) -> Dict[str, Any]:
    """Same per-fact both/either shape v2/v3 introduced: a v4 profile can
    carry BOTH derived_facts and underivable simultaneously, per-fact."""
    profile: Dict[str, Any] = {"loan_id": loan.loan_id, "profile_version": PROFILE_VERSION}
    derived_facts: Dict[str, Any] = {}
    underivable: Dict[str, Any] = {}
    for derive_fn in DERIVATIONS:
        result = derive_fn(loan)
        derived_facts.update(result.get("derived_facts", {}))
        underivable.update(result.get("underivable", {}))
    if derived_facts:
        profile["derived_facts"] = derived_facts
    if underivable:
        profile["underivable"] = underivable
    return profile


def build_all_profiles() -> List[str]:
    os.makedirs(OUT_DIR, exist_ok=True)
    written = []
    for n in LOAN_NUMBERS:
        fixture_path = os.path.join(FIXTURE_DIR, "loan_{}.json".format(n))
        if not os.path.isfile(fixture_path):
            raise SystemExit(
                "missing fixture {} -- refusing to write a loan profile not "
                "derived from real data".format(fixture_path))
        loan = load_canonical_loan(fixture_path)
        profile = build_profile(loan)
        out_path = os.path.join(OUT_DIR, "loan_{}.json".format(n))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, sort_keys=True)
            f.write("\n")
        written.append(out_path)
    return written


def main() -> None:
    written = build_all_profiles()
    print("wrote {} loan profile(s) to {}".format(len(written), OUT_DIR))
    for path in written:
        with open(path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        loan_id = profile["loan_id"]
        derived = profile.get("derived_facts", {})
        underivable = profile.get("underivable", {})
        doc_presence_true = [k for k, v in derived.items()
                              if k.startswith(DOC_PRESENCE_PREFIX) and v["value"] == "true"]
        non_doc_presence = {k: v["value"] for k, v in sorted(derived.items())
                             if not k.startswith(DOC_PRESENCE_PREFIX)}
        parts = ["{}={}".format(k, v) for k, v in non_doc_presence.items()]
        parts += ["{}=UNDERIVABLE".format(k) for k in sorted(underivable)]
        parts.append("doc_present_* true-for-this-loan: {}".format(sorted(doc_presence_true) or "none"))
        print("  {} ({}): {}".format(os.path.basename(path), loan_id, ", ".join(parts)))


if __name__ == "__main__":
    main()
