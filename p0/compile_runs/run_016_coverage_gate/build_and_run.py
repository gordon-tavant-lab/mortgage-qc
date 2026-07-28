"""
run_016 -- the Field & Precondition Coverage Gate (spec 015 Phase 0, T001-T005).

Why this exists: a demo-prep QC run for loan 01 (run_015) surfaced two real
gaps by ACCIDENT -- a screenshot of loan 01's own 1003 form -- because this
project has two systems (document extraction: doc_patterns/*.json +
field_catalog.json; and the precondition-ontology pipeline: p0/ontology_
extraction/, spec 002f) that were never reconciled against each other. A gap
in the second category is invisible to every other review mechanism this
project runs. This script is the durable, re-runnable fix for that blind
spot: it asks, systematically, "does every field this project's ontology
pipeline / compiled ruleset / FIBO-aligned vocabulary depends on actually
have (a) a catalog entry, (b) a real extraction-or-derivation path, and
(c) a non-null value somewhere in the 5 real loans?" -- and reports every
field that fails any one of those three, in full, not a sample.

Three independent nets, each producing its own section of the report:

1. ontology_dependency_coverage -- every REAL canonical fact
   `p0.ontology_extraction.pipeline.run_layers()`'s Layer-0 proposals
   resolve to via the signed fact vocabulary (storage/fact_vocabulary/,
   `qc_engine.compiler.fact_vocabulary.resolve_layer0`) -- the same
   resolution step `run_013_comprehensive_e2e_v6` and 002g's own
   `compile_llm.attach_preconditions` already use in production. Proposals
   that fail to resolve (unmapped question/answer pairs -- the "FLAGGED"
   case) are reported too, honestly, as proposals the vocabulary itself
   cannot yet back -- not filtered out, because those are exactly the ones
   most likely to be gating on a fact with no real backing.
2. ruleset_field_coverage -- the broader net (T002): every distinct
   `Check.field_name` / `Check.compare_field_name` across the currently-
   vetted `comprehensive_e2e_v6_ruleset.json` (3,203 checks), the same
   3-part check. This catches non-gating extraction gaps too, not just
   precondition-fact gaps.
3. fibo_alignment -- a SMALL, CURATED (not a full ontology import) list of
   FIBO LOAN/RealEstateLoans concepts this project's own gating dimensions
   map onto (loan program/investor type, occupancy, property type, income
   type), each with the field name(s) this session's own investigation
   found SHOULD represent that concept. This is the section that surfaces
   `loan_program_1003` and `income_type_used_for_qualification` by name --
   fields nothing in the current repo references yet at all, discoverable
   only because this curated list encodes the manual-investigation finding
   as a checkable fact, not because any existing pipeline output happens to
   name them (the whole point: it stops being an accident). Per plan.md
   this cross-check is independent/informational relative to sections 1-2
   (it never blocks a hard gate on its own) -- but a concept whose proposed
   field is entirely absent (no catalog entry, no extraction path, never
   populated) is still reported as a real, named gap, not softened away.

Honest scoping notes:
- Zero LLM calls anywhere in this script -- purely structural JSON/AST-free
  analysis (field-name set arithmetic + dict lookups). Logged as such via
  `qc_engine.eval_log.EvalLog`'s cost line (CLAUDE.md Cost Transparency).
- `run_layers()` is invoked Layer-0-only (no `layer1_client`/`layer2_client`),
  matching `run_013`'s own invocation and this project's confirmed current
  state (spec 015 background: only the free Layer-0 structural pass has
  ever actually run against this rulebook) -- Phase C's Layer-1 go/no-go is
  explicitly out of this script's scope.
- The FIBO concept list is hand-curated from FIBO's public LOAN /
  RealEstateLoans schema (no OWL/RDF file is parsed or imported) -- see the
  `FIBO_CONCEPT_ALIGNMENT` constant below for the exact concepts and the
  one-line provenance note on each.
- This script never mutates any fixture, profile, catalog, or ruleset file
  -- read-only analysis, safe to re-run at any time, before or after a fix
  lands (User Story 2 Acceptance Scenario 2: re-running this gate is the
  required step before signing off a newly compiled ruleset or demo run).

Inputs:
  p0/fixtures/ontology_extraction/retail_post_closing_rows.json (the same
    rows run_013 loads)
  p0/qc_engine/field_catalog.json
  p0/fixtures/from_docs/doc_patterns/*.json
  p0/fixtures/from_docs/loan_0{1..5}.json (the 5 real, doc-extracted fixtures)
  storage/fact_vocabulary/ (latest signed version, via FV.load_latest)
  result/rules/comprehensive_e2e_v6_ruleset.json (the currently-vetted ruleset)
  qc_engine/build_loan_profiles_v3.py (imported directly -- DERIVATIONS +
    build_profile(), run fresh against the 5 real fixtures rather than
    trusting possibly-stale storage/loan_profiles/v3/*.json artifacts)

Outputs:
  result/qc_results/run_016_coverage_gate_results.json
  storage/logs/run_016_coverage_gate.jsonl

Run: python3 p0/compile_runs/run_016_coverage_gate/build_and_run.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
for _p in (_P0, _FROM_DOCS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fixture_loader import load_canonical_loan  # noqa: E402
from ontology_extraction import pipeline as ontology_pipeline  # noqa: E402
from qc_engine.build_loan_profiles_v3 import build_profile  # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.eval_log import EvalLog  # noqa: E402

RUN_ID = "run_016_coverage_gate"

ROWS_PATH = os.path.join(_P0, "fixtures", "ontology_extraction",
                         "retail_post_closing_rows.json")
CATALOG_PATH = os.path.join(_P0, "qc_engine", "field_catalog.json")
DOC_PATTERNS_DIR = os.path.join(_FROM_DOCS, "doc_patterns")
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules",
                            "comprehensive_e2e_v6_ruleset.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "{}_results.json".format(RUN_ID))
LOAN_NUMBERS = ("01", "02", "03", "04", "05")

# The two fields this session found by hand (spec 015 background) -- SC-006's
# explicit acceptance bar for this gate.
SC_006_EXPECTED_GAPS = ("loan_program_1003", "income_type_used_for_qualification")


# --- A small, curated FIBO LOAN/RealEstateLoans concept list (T003) ----------
# Hand-curated from FIBO's public schema (spec.fibo-loan.org, FND "Loans and
# Leases" / "RealEstateLoans" modules) -- NOT a full ontology import, per
# plan.md's explicit scoping. Each concept names the field(s) this project's
# own gating dimensions should map onto it, informed directly by this
# session's investigation (spec 015 background) -- the curated knowledge that
# makes automated detection of `loan_program_1003` / `income_type_used_for_
# qualification` possible at all, since neither string appears anywhere else
# in the pre-fix repo for sections 1/2 above to discover on their own.
FIBO_CONCEPT_ALIGNMENT: List[Dict[str, Any]] = [
    {
        "concept": "fibo-loan:LoanProgramType",
        "fibo_schema_note": (
            "FIBO FND 'Loans and Leases' / RealEstateLoans module -- "
            "classifies a loan by its origination program/agency "
            "(Conventional, FHA, VA, USDA; conventional loans further "
            "resolve to the GSE, Fannie Mae or Freddie Mac)."
        ),
        "expected_fields": ["loan_program", "loan_program_1003"],
        "session_note": (
            "`loan_program` (the DERIVED fact) already has a catalog entry "
            "and a derivation path (build_loan_profiles_v3.derive_loan_"
            "program), but is honestly `underivable` for loans 01/04 -- no "
            "raw, citable field distinguishes Fannie Mae vs. Freddie Mac "
            "when loan_type_cd only reads 'Conventional'. `loan_program_"
            "1003` (a direct extraction of the 1003's own 'Loan Program' "
            "line) is the missing raw field spec 015 Phase A Issue 1 adds."
        ),
    },
    {
        "concept": "fibo-loan:MortgageInvestorType",
        "fibo_schema_note": (
            "FIBO's Investor/InvestorType concepts, specialized in "
            "mortgage-servicing/secondary-market contexts to the GSE or "
            "agency that ultimately holds or insures a closed loan."
        ),
        "expected_fields": ["loan_program"],
        "session_note": (
            "no field distinctly models 'investor type' apart from "
            "loan_program today -- currently conflated into one fact. "
            "Informational only: this concept is not itself a hard, named "
            "gap the way loan_program_1003 is."
        ),
    },
    {
        "concept": "fibo-loan:OccupancyType",
        "fibo_schema_note": (
            "FIBO RealEstateLoans occupancy classification for the subject "
            "property (owner-occupied / second home / investment)."
        ),
        "expected_fields": ["occupancy_1003", "occupancy_type"],
        "session_note": (
            "fully covered -- both the raw 1003 field and the derived "
            "canonical fact exist (010b). Included for completeness / as "
            "a passing control case, not because it's a gap."
        ),
    },
    {
        "concept": "fibo-loan:RealEstatePropertyType",
        "fibo_schema_note": (
            "FIBO's real-estate collateral property-type classification "
            "(single-family, condo, 2-4 unit, manufactured, etc.) for the "
            "subject property."
        ),
        "expected_fields": ["property_type"],
        "session_note": (
            "no field of this name (or a recognizable synonym) exists in "
            "the catalog at all -- a genuine, independent gap surfaced "
            "only by this FIBO cross-check, not by sections 1 or 2 above "
            "(nothing in ontology_extraction's proposals or the compiled "
            "ruleset currently depends on a field named this way)."
        ),
    },
    {
        "concept": "fibo-loan:IncomeType",
        "fibo_schema_note": (
            "FIBO's income-type classification (W-2 / self-employed / "
            "other) as used to qualify a borrower for a loan."
        ),
        "expected_fields": ["income_type_used_for_qualification"],
        "session_note": (
            "spec 015 Phase B Step 6: self-employment-gated checks need "
            "this field to resolve NOT_APPLICABLE for W-2 borrowers instead "
            "of APPLICABILITY_UNKNOWN. Notably, `storage/fact_vocabulary`'s "
            "own v7 already names `income_type_used_for_qualification` as a "
            "canonical fact with 14 signed question bindings (479 real "
            "Layer-0 proposals resolve to it -- see "
            "ontology_dependency_coverage below) -- the vocabulary already "
            "expects this fact to exist; nothing produces or catalogs it."
        ),
    },
]


# --- section-agnostic 3-part field check -------------------------------------

def check_field_coverage(
    field_name: str,
    catalog_names: Set[str],
    doc_pattern_fields: Set[str],
    derivation_fact_names: Set[str],
    fixtures_fields: Dict[str, Dict[str, Any]],
    profiles: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """The one check reused by all three sections (plan.md's 3-part test):
    (a) catalog entry exists, (b) something (a doc_pattern regex or a
    build_loan_profiles_v3 derivation) actually produces it, (c) it is
    non-None in at least one of the 5 real fixtures OR non-underivable in
    at least one of the 5 real profiles."""
    has_catalog = field_name in catalog_names
    has_extraction_path = (field_name in doc_pattern_fields
                           or field_name in derivation_fact_names)
    populated_in: List[str] = []
    for loan_id, fields in fixtures_fields.items():
        entry = fields.get(field_name)
        if entry is not None and entry.get("truth") is not None:
            populated_in.append("fixture:loan_{}".format(loan_id))
    for loan_id, profile in profiles.items():
        if field_name in profile.get("derived_facts", {}):
            populated_in.append("profile:loan_{}".format(loan_id))
    ever_populated = bool(populated_in)

    failing_checks = []
    if not has_catalog:
        failing_checks.append("no_catalog_entry")
    if not has_extraction_path:
        failing_checks.append("no_extraction_or_derivation_path")
    if not ever_populated:
        failing_checks.append("never_populated")

    return {
        "field_name": field_name,
        "has_catalog_entry": has_catalog,
        "has_extraction_or_derivation_path": has_extraction_path,
        "ever_populated": ever_populated,
        "populated_in": populated_in,
        "failing_checks": failing_checks,
        "is_gap": bool(failing_checks),
    }


def _bucket_by_failure(checked: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Categorize gaps by WHICH check failed (task step 5) -- full lists,
    never a sample or a truncated top-N."""
    buckets: Dict[str, List[str]] = {
        "no_catalog_entry": [],
        "no_extraction_or_derivation_path": [],
        "never_populated": [],
    }
    for c in checked:
        for reason in c["failing_checks"]:
            buckets[reason].append(c["field_name"])
    for k in buckets:
        buckets[k] = sorted(set(buckets[k]))
    return buckets


# --- shared loaders -----------------------------------------------------------

def _load_catalog_field_names() -> Set[str]:
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)
    return {e["field_name"] for e in catalog["entries"]}


def _load_doc_pattern_field_names() -> Set[str]:
    names: Set[str] = set()
    for fname in sorted(os.listdir(DOC_PATTERNS_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(DOC_PATTERNS_DIR, fname)) as f:
            pattern = json.load(f)
        names.update(pattern.get("fields", {}).keys())
    return names


def _load_fixtures_and_profiles():
    """Loads the 5 real fixtures' raw `fields` dicts (for the raw-extraction
    populated check) AND builds fresh v3-shaped profiles by calling
    build_loan_profiles_v3.build_profile() directly against each real
    CanonicalLoan -- never trusting a possibly-stale committed
    storage/loan_profiles/v3/*.json artifact, and, as a side effect, giving
    us the exact set of fact names every derivation function ATTEMPTS to
    produce (the union of derived_facts.keys() | underivable.keys() across
    all 5 loans -- a fact only ever lands in one or the other, never
    neither, per build_profile()'s own per-derivation-function contract)."""
    fixtures_fields: Dict[str, Dict[str, Any]] = {}
    profiles: Dict[str, Dict[str, Any]] = {}
    derivation_fact_names: Set[str] = set()
    for n in LOAN_NUMBERS:
        fixture_path = os.path.join(_FROM_DOCS, "loan_{}.json".format(n))
        with open(fixture_path) as f:
            raw = json.load(f)
        fixtures_fields[n] = raw.get("fields", {})

        loan = load_canonical_loan(fixture_path)
        profile = build_profile(loan)
        profiles[n] = profile
        derivation_fact_names.update(profile.get("derived_facts", {}).keys())
        derivation_fact_names.update(profile.get("underivable", {}).keys())
    return fixtures_fields, profiles, derivation_fact_names


def _git_head() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT,
            stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return None


# --- Section 1: ontology_extraction dependency coverage (T001) --------------

def _ontology_dependency_coverage(
    log: EvalLog, catalog_names, doc_pattern_fields, derivation_fact_names,
    fixtures_fields, profiles,
) -> Dict[str, Any]:
    with open(ROWS_PATH) as f:
        rows = json.load(f)
    # Layer-0-only (no layer1_client/layer2_client): zero-LLM, matching
    # run_013's own invocation and this project's confirmed current state
    # (CLAUDE.md: only the free Layer-0 pass has ever run against this
    # rulebook -- Layer 1's go/no-go is Phase C, out of this script's scope).
    result = ontology_pipeline.run_layers(rows)

    by_trust_tier: Dict[str, int] = {}
    for p in result.proposals:
        by_trust_tier[p.trust_tier] = by_trust_tier.get(p.trust_tier, 0) + 1
    raw_field_names = sorted({
        p.condition.field_name for p in result.proposals if p.condition is not None
    })

    vocab = FV.load_latest(VOCAB_DIR)
    resolved_field_names: Set[str] = set()
    resolved_counts: Dict[str, int] = {}
    unresolved: List[Dict[str, Any]] = []
    for p in result.proposals:
        if p.condition is None:
            unresolved.append({
                "row_id": p.row_id, "source_layer": p.source_layer,
                "reason": "no condition (parse_failed={})".format(p.parse_failed),
            })
            continue
        res = FV.resolve_layer0(vocab, p)
        if res.status == "resolved":
            fname = res.condition["field_name"]
            resolved_field_names.add(fname)
            resolved_counts[fname] = resolved_counts.get(fname, 0) + 1
        else:
            unresolved.append({
                "row_id": p.row_id, "source_layer": p.source_layer,
                "reason": res.reason,
            })

    checked = [
        check_field_coverage(name, catalog_names, doc_pattern_fields,
                             derivation_fact_names, fixtures_fields, profiles)
        for name in sorted(resolved_field_names)
    ]
    for c in checked:
        c["proposals_resolving_to_this_fact"] = resolved_counts[c["field_name"]]
    gaps = [c for c in checked if c["is_gap"]]

    log.log("ontology_dependency_coverage", "summary",
            total_proposals=len(result.proposals), by_trust_tier=by_trust_tier,
            distinct_raw_layer0_keys=len(raw_field_names),
            distinct_resolved_facts=len(resolved_field_names),
            unresolved_proposals=len(unresolved),
            resolved_fact_gaps=len(gaps))

    return {
        "note": (
            "PreconditionProposal.condition.field_name is a raw, opaque "
            "Layer-0 question key (e.g. 'question_570606') until resolved "
            "through the signed fact vocabulary (qc_engine.compiler."
            "fact_vocabulary.resolve_layer0) -- the same resolution step "
            "run_013 and 002g's compile_llm.attach_preconditions already "
            "use in production. Checking those raw keys against the field "
            "catalog directly would trivially and uninformatively fail "
            "every one of them by construction, so this section reports "
            "the 3-part coverage check against the REAL underlying "
            "canonical fact names each proposal resolves to -- and keeps "
            "the raw counts + every unresolved ('FLAGGED') proposal "
            "visible below, since those are exactly the ones most likely "
            "to be gating on a fact with no real backing."
        ),
        "total_proposals": len(result.proposals),
        "proposals_by_trust_tier": by_trust_tier,
        "distinct_raw_layer0_dependency_keys": len(raw_field_names),
        "vocabulary_version": vocab.version,
        "resolved_fact_names_checked": checked,
        "resolved_fact_gaps": gaps,
        "resolved_fact_gap_buckets": _bucket_by_failure(gaps),
        "unresolved_proposals_total": len(unresolved),
        "unresolved_proposals": unresolved,
    }


# --- Section 2: ruleset field coverage -- the broader net (T002) -----------

def _ruleset_field_coverage(
    log: EvalLog, catalog_names, doc_pattern_fields, derivation_fact_names,
    fixtures_fields, profiles,
) -> Dict[str, Any]:
    with open(RULESET_PATH) as f:
        wrapper = json.load(f)
    checks = wrapper["content"]["checks"]
    names: Set[str] = set()
    for c in checks:
        if c.get("field_name"):
            names.add(c["field_name"])
        if c.get("compare_field_name"):
            names.add(c["compare_field_name"])

    checked = [
        check_field_coverage(name, catalog_names, doc_pattern_fields,
                             derivation_fact_names, fixtures_fields, profiles)
        for name in sorted(names)
    ]
    gaps = [c for c in checked if c["is_gap"]]

    log.log("ruleset_field_coverage", "summary",
            ruleset=wrapper["content"]["ruleset_id"], total_checks=len(checks),
            distinct_field_names=len(names), gaps=len(gaps))

    return {
        "note": (
            "The broader net (spec.md/plan.md T002): every distinct "
            "Check.field_name/compare_field_name across the currently-"
            "vetted comprehensive_e2e_v6_ruleset.json, same 3-part check -- "
            "catches non-gating extraction gaps too, not just precondition-"
            "fact gaps from section 1."
        ),
        "ruleset_id": wrapper["content"]["ruleset_id"],
        "total_checks": len(checks),
        "distinct_field_names_referenced": len(names),
        "fields_checked": checked,
        "gaps": gaps,
        "gap_buckets": _bucket_by_failure(gaps),
    }


# --- Section 3: FIBO curated concept alignment (T003) ------------------------

def _fibo_alignment(
    log: EvalLog, catalog_names, doc_pattern_fields, derivation_fact_names,
    fixtures_fields, profiles,
) -> Dict[str, Any]:
    concepts_out = []
    for concept in FIBO_CONCEPT_ALIGNMENT:
        field_checks = [
            check_field_coverage(name, catalog_names, doc_pattern_fields,
                                 derivation_fact_names, fixtures_fields, profiles)
            for name in concept["expected_fields"]
        ]
        fully_covered = any(not fc["is_gap"] for fc in field_checks)
        concepts_out.append({
            "concept": concept["concept"],
            "fibo_schema_note": concept["fibo_schema_note"],
            "session_note": concept["session_note"],
            "expected_fields_checked": field_checks,
            "at_least_one_expected_field_fully_covered": fully_covered,
            "concept_flagged": not fully_covered,
        })

    flagged = [c for c in concepts_out if c["concept_flagged"]]
    # Every individual expected field that's a real, named gap -- flattened,
    # full list (a concept can be "flagged" via more than one missing field).
    named_field_gaps = sorted({
        fc["field_name"]
        for c in concepts_out for fc in c["expected_fields_checked"]
        if fc["is_gap"]
    })

    log.log("fibo_alignment", "summary", concepts_checked=len(concepts_out),
            concepts_flagged=len(flagged), named_field_gaps=named_field_gaps)

    return {
        "note": (
            "Informational, independent third validation signal (plan.md "
            "step 4) -- never a hard gate on its own the way sections 1/2 "
            "are, but individually-named expected fields that are entirely "
            "absent (no catalog entry, no extraction path, never "
            "populated) are still reported here as real, actionable gaps, "
            "not softened away."
        ),
        "concepts": concepts_out,
        "concepts_flagged": len(flagged),
        "named_field_gaps": named_field_gaps,
    }


def main() -> None:
    log = EvalLog(RUN_ID)
    git_head = _git_head()
    log.log("setup", "run_started", git_head=git_head, rows_path=ROWS_PATH,
            catalog_path=CATALOG_PATH, ruleset_path=RULESET_PATH)

    catalog_names = _load_catalog_field_names()
    doc_pattern_fields = _load_doc_pattern_field_names()
    fixtures_fields, profiles, derivation_fact_names = _load_fixtures_and_profiles()
    log.log("setup", "loaders_ready", catalog_entries=len(catalog_names),
            doc_pattern_fields=len(doc_pattern_fields),
            derivation_fact_names=sorted(derivation_fact_names))

    ontology_section = _ontology_dependency_coverage(
        log, catalog_names, doc_pattern_fields, derivation_fact_names,
        fixtures_fields, profiles)
    ruleset_section = _ruleset_field_coverage(
        log, catalog_names, doc_pattern_fields, derivation_fact_names,
        fixtures_fields, profiles)
    fibo_section = _fibo_alignment(
        log, catalog_names, doc_pattern_fields, derivation_fact_names,
        fixtures_fields, profiles)

    # -- SC-006: the gate must reproduce, by name, the two gaps this session
    # found by hand -- this is the entire acceptance bar for Phase 0.
    all_named_gaps = set(fibo_section["named_field_gaps"])
    all_named_gaps.update(g["field_name"] for g in ontology_section["resolved_fact_gaps"])
    all_named_gaps.update(g["field_name"] for g in ruleset_section["gaps"])
    sc_006_detail = {
        name: (name in all_named_gaps) for name in SC_006_EXPECTED_GAPS
    }
    sc_006_pass = all(sc_006_detail.values())
    for name in SC_006_EXPECTED_GAPS:
        log.log_evidence_chain(
            entity_id=name, input_={"expected": "reported as a gap"},
            method="run_016_coverage_gate.sc_006_check",
            verdict="GAP_REPORTED" if sc_006_detail[name] else "NOT_REPORTED",
            stage="sc_006_check")
    log.log("sc_006_check", "result", detail=sc_006_detail, pass_=sc_006_pass)

    log.log_cost(
        llm_calls=0, cost_usd=0.0, deterministic_resolution_rate=1.0,
        note=("purely structural JSON/field-name-set analysis -- zero LLM "
              "calls anywhere in this script; the only network-independent "
              "cost is the human time this gate is designed to save by "
              "catching this class of gap automatically instead of by "
              "screenshot accident."))

    out = {
        "run": RUN_ID,
        "purpose": (
            "Field & Precondition Coverage Gate (spec 015 Phase 0) -- a "
            "required, re-runnable pass before signing off any newly "
            "compiled ruleset or demo/production run, same standing as "
            "verify_against_defects.py's 25/25 gate (see CLAUDE.md)."
        ),
        "git_head": git_head,
        "ontology_dependency_coverage": ontology_section,
        "ruleset_field_coverage": ruleset_section,
        "fibo_alignment": fibo_section,
        "summary": {
            "catalog_entries_total": len(catalog_names),
            "doc_pattern_extractable_fields_total": len(doc_pattern_fields),
            "derivation_fact_names_total": len(derivation_fact_names),
            "ontology_resolved_fact_gaps": len(ontology_section["resolved_fact_gaps"]),
            "ruleset_field_gaps": len(ruleset_section["gaps"]),
            "fibo_concepts_flagged": fibo_section["concepts_flagged"],
        },
        "sc_006_check": {
            "expected_gaps": list(SC_006_EXPECTED_GAPS),
            "detail": sc_006_detail,
            "pass": sc_006_pass,
        },
        "eval_log": log.path,
        "cost": {"llm_calls": 0, "cost_usd": 0.0, "deterministic_resolution_rate": 1.0},
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)

    log.log("setup", "run_finished", results_path=RESULTS_OUT)

    print("ontology_dependency_coverage: {} proposals, {} distinct resolved "
          "facts, {} gap(s), {} unresolved".format(
              ontology_section["total_proposals"],
              len(ontology_section["resolved_fact_names_checked"]),
              len(ontology_section["resolved_fact_gaps"]),
              ontology_section["unresolved_proposals_total"]))
    print("ruleset_field_coverage: {} checks, {} distinct field names, "
          "{} gap(s)".format(
              ruleset_section["total_checks"],
              ruleset_section["distinct_field_names_referenced"],
              len(ruleset_section["gaps"])))
    print("fibo_alignment: {} concepts checked, {} flagged, named gaps: {}".format(
        len(fibo_section["concepts"]), fibo_section["concepts_flagged"],
        fibo_section["named_field_gaps"]))
    print("SC-006 check ({}): {}".format(
        "PASS" if sc_006_pass else "FAIL", sc_006_detail))
    print("wrote {}".format(RESULTS_OUT))
    print("eval log: {}".format(log.path))

    if not sc_006_pass:
        raise SystemExit(
            "SC-006 FAILED: the coverage gate did not reproduce {} as real "
            "gaps against the pre-fix repo state -- this gate has a bug, "
            "per spec 015 plan.md's Phase 0 verification requirement."
            .format([n for n, ok in sc_006_detail.items() if not ok]))


if __name__ == "__main__":
    main()
