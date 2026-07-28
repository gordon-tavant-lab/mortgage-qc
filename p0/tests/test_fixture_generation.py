"""
Tests for p0/fixtures/from_docs/ — document-derived synthetic loan fixtures.
Covers extract_pdf, extract_xml, build_fixtures, and the 25/25 verify_against_defects gate.
Run from repo root:  python3 -m pytest p0/tests/test_fixture_generation.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FROM_DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fixtures", "from_docs")
FROM_DOCS_DIR = os.path.normpath(FROM_DOCS_DIR)
DEMO_SYN_DIR = os.path.join(REPO_ROOT, "demo", "syn")

sys.path.insert(0, FROM_DOCS_DIR)
# eval_synth/test_properties.py imports its sibling `generator` module as a
# bare top-level import, so eval_synth/ itself (not just p0/) must be on
# sys.path — matching how pytest's own rootdir insertion resolves it when
# p0/eval_synth/test_properties.py is collected directly.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eval_synth"))

from build_fixtures import (                                        # noqa: E402
    build_all_fixtures, LOAN_PACKAGES, DERIVED_FIELD_NAMES)
from fixture_loader import load_canonical_loan                      # noqa: E402
from extract_pdf import extract_pdf_fields                          # noqa: E402
import verify_against_defects as VAD                                # noqa: E402

from qc_engine.model import CanonicalLoan                           # noqa: E402
from qc_engine import run, load_catalog, validate_referential_integrity  # noqa: E402
from fixtures.ruleset_defects import defects_ruleset, defects_ruleset_for  # noqa: E402
from test_properties import score                                   # noqa: E402


# --- US1: fixtures load cleanly, no cross-loan leakage ----------------------

def test_build_fixtures_produces_exactly_five_files_matching_loan_ids():
    written = build_all_fixtures()
    assert len(written) == 5

    expected_loan_ids = {
        "loan 01": "2025-0917-001",
        "loan 02": "2025-1004-FHA-002",
        "loan 03": "2025-1108-VA-003",
        "loan 04": "2025-1215-FRD-004",
        "loan 05": "2025-1122-USDA-005",
    }
    for folder_name, path in written.items():
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["loan_id"] == expected_loan_ids[folder_name]


def test_every_real_loan_document_is_matched_by_a_doc_pattern():
    """2026-07-16: audited whether extraction actually touches every PDF, not
    just the ones convenient for the 25 known defects. Every real loan document
    must be matched by some doc_patterns/*.json entry -- the only PDF allowed
    to go unmatched is the synthetic generator's own answer key (00_*), since
    extracting "ground truth" from the ground-truth file would be circular."""
    from extract_pdf import _load_doc_patterns, _match_doc_type
    patterns = _load_doc_patterns()
    unmatched = []
    for folder_name in LOAN_PACKAGES:
        folder = os.path.join(DEMO_SYN_DIR, folder_name)
        for f in sorted(os.listdir(folder)):
            if not f.lower().endswith(".pdf"):
                continue
            if f.startswith("00_"):
                continue  # the answer key -- deliberately excluded, not a loan document
            if _match_doc_type(f, patterns) is None:
                unmatched.append((folder_name, f))
    assert not unmatched, "real loan documents with zero extraction coverage: {0}".format(unmatched)


def test_no_cross_loan_data_leakage():
    """Every populated field's citation (where present) must name only a
    document from that loan's own demo/syn/loan 0N/ folder."""
    build_all_fixtures()
    for folder_name in LOAN_PACKAGES:
        loan_num = folder_name.split(" ")[1]
        fixture_path = os.path.join(FROM_DOCS_DIR, "loan_{0}.json".format(loan_num))
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        own_folder = os.path.join(DEMO_SYN_DIR, folder_name)
        own_pdf_names = set(
            f for f in os.listdir(own_folder) if f.lower().endswith(".pdf")
        )
        for field_name, entry in data["fields"].items():
            citation = entry.get("citation")
            if citation:
                assert citation["doc_name"] in own_pdf_names, (
                    "{0}.{1} cites {2}, not in {3}'s own folder"
                    .format(data["loan_id"], field_name, citation["doc_name"], folder_name)
                )


def test_fixtures_load_into_canonical_loan_and_score_with_zero_changes():
    """Zero code changes to model.py or eval_synth's scorer (FR-008,
    spec.md Acceptance Scenario 2)."""
    build_all_fixtures()
    for loan_num in ("01", "02", "03", "04", "05"):
        path = os.path.join(FROM_DOCS_DIR, "loan_{0}.json".format(loan_num))
        loan = load_canonical_loan(path)
        assert isinstance(loan, CanonicalLoan)

        # score() takes List[LabeledLoan] = (CanonicalLoan, expected_verdicts, provenance)
        result = score([(loan, {}, {"mutations": []})])
        assert result["loans"] == 1
        assert result["exact_match_rate"] == 1.0  # no checks target these new
        # fields yet (that's the 003-series' job) — zero applicable checks is
        # a valid, non-error scoring result, proving the scorer runs unmodified.


def test_credit_inquiry_table_extracted():
    """2026-07-16: the credit report's Inquiries (last 120 days) table --
    2 rows, both real: the borrower's own mortgage application inquiry and
    the Ally Bank auto inquiry (the undisclosed liability's own paper trail,
    per defect #4 -- this inquiry is *why* the auto loan shows up on the
    credit report at all)."""
    build_all_fixtures()
    loan01 = json.load(open(os.path.join(FROM_DOCS_DIR, "loan_01.json"), encoding="utf-8"))
    fields = loan01["fields"]
    rows = set(k.split("_")[2] for k in fields if k.startswith("credit_inquiry_"))
    assert len(rows) == 2
    assert fields["credit_inquiry_01_requesting_party"]["truth"] == "Prospective Client Bank (mortgage)"
    assert fields["credit_inquiry_02_requesting_party"]["truth"] == "Ally Bank (auto)"


def test_round4_tables_have_correct_row_counts_and_no_page_break_collisions():
    """2026-07-16 follow-up: checking loans 02-05 for untapped tables found
    5 more (1003 assets/liabilities on loan 01, FHA appraisal MPR items on
    loan 02, mortgage payment history + self-employed doc checklist on loan
    04). Caught a real bug while verifying: _extract_simple_table reset its
    row counter every page, so a table straddling a page break (loan 01's
    1003 Assets table: "Checking" ends page 1, "Savings"/"401(k)" start page
    2) silently collided row numbers and overwrote "Checking" with "Savings"
    under the same field name. Fixed by persisting the counter across pages;
    this test locks in both the fix and the expected row counts."""
    build_all_fixtures()
    loan01 = json.load(open(os.path.join(FROM_DOCS_DIR, "loan_01.json"), encoding="utf-8"))
    loan02 = json.load(open(os.path.join(FROM_DOCS_DIR, "loan_02.json"), encoding="utf-8"))
    loan04 = json.load(open(os.path.join(FROM_DOCS_DIR, "loan_04.json"), encoding="utf-8"))

    def row_indices(fields, prefix):
        return set(k[len(prefix):].split("_")[0] for k in fields if k.startswith(prefix))

    assert len(row_indices(loan01["fields"], "asset_")) == 3, "expected 3 asset rows (Checking/Savings/401k)"
    assert loan01["fields"]["asset_01_account_type"]["truth"] == "Checking", (
        "asset_01 should be Checking (the page-1 row) -- a page-break collision "
        "would show Savings or 401(k) here instead"
    )
    assert len(row_indices(loan01["fields"], "liability_1003_")) == 3
    assert len(row_indices(loan02["fields"], "mpr_item_")) == 3
    assert len(row_indices(loan04["fields"], "mortgage_payment_")) == 12
    assert len(row_indices(loan04["fields"], "se_income_doc_")) == 8

    # independent sanity check: the 1003's own liabilities (excluding the
    # undisclosed Ally Bank one, by design) should sum to a plausible total
    # distinct from, and lower than, the credit report's 4-liability total
    liab_1003_total = sum(
        float(v["truth"]) for k, v in loan01["fields"].items()
        if k.startswith("liability_1003_") and k.endswith("_monthly_payment")
    )
    assert abs(liab_1003_total - 684.00) < 0.01, (
        "1003 liabilities monthly payments should sum to $684.00 (85+389+210), got {0}"
        .format(liab_1003_total)
    )


def test_bank_ledger_reconciles_to_the_penny():
    """2026-07-16 bulk-data round: the strongest possible correctness proof
    for the 16-row bank transaction ledger isn't spot-checking values, it's
    an independent arithmetic identity the extraction never targets directly:
    beginning_balance + sum(credits) - sum(debits) must equal ending_balance
    exactly. If even one transaction were missed or misclassified
    credit-vs-debit (the one genuinely ambiguous part of this extraction),
    this would not balance to the penny."""
    build_all_fixtures()
    path = os.path.join(FROM_DOCS_DIR, "loan_01.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    fields = data["fields"]
    credits = sum(float(v["truth"]) for k, v in fields.items()
                  if k.startswith("bank_txn_") and k.endswith("_credit_amount"))
    debits = sum(float(v["truth"]) for k, v in fields.items()
                 if k.startswith("bank_txn_") and k.endswith("_debit_amount"))
    beginning = float(fields["beginning_balance"]["truth"])
    ending = float(fields["ending_balance"]["truth"])
    assert abs((beginning + credits - debits) - ending) < 0.005, (
        "bank ledger doesn't reconcile: {0} + {1} - {2} = {3}, expected {4}"
        .format(beginning, credits, debits, beginning + credits - debits, ending)
    )
    # and the row count itself, independently: 16 dated rows in the source PDF
    txn_numbers = set(k.split("_")[2] for k in fields if k.startswith("bank_txn_"))
    assert len(txn_numbers) == 16, "expected 16 transaction rows, found {0}".format(len(txn_numbers))


def test_property_value_gets_doc_side_truth_and_facts_are_derived():
    """2026-07-16 follow-up: property_value had the exact same gap as
    property_address (mismo-only truth), and chk-ltv-max reads loan.facts,
    a wholly separate path from loan.fields that build_fixtures.py had always
    left empty regardless of how complete fields{} was. Both fixed together."""
    build_all_fixtures()
    for loan_num in ("01", "02", "03", "04", "05"):
        path = os.path.join(FROM_DOCS_DIR, "loan_{0}.json".format(loan_num))
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["fields"]["property_value"]["truth"] is not None, (
            "{0}: property_value still mismo-only".format(data["loan_id"])
        )
        facts = data["facts"]
        assert facts.get("loan_amount"), "{0}: facts missing loan_amount".format(data["loan_id"])
        assert facts.get("property_value"), "{0}: facts missing property_value".format(data["loan_id"])

    # loan 01's own answer key states "LTV 80%" -- an independent sanity check
    # the derived facts are actually correct, not just non-null
    loan01 = json.load(open(os.path.join(FROM_DOCS_DIR, "loan_01.json"), encoding="utf-8"))
    ltv = float(loan01["facts"]["loan_amount"]) / float(loan01["facts"]["property_value"])
    assert abs(ltv - 0.80) < 0.001, "loan 01 LTV = {0}, expected 0.80 per its own answer key".format(ltv)


def test_original_seed_fields_get_doc_side_truth_not_just_mismo():
    """2026-07-16: Gordon noticed property_address's truth was null despite a
    clear address in sources.mismo. Root cause: extract_pdf.py never wrote a
    pattern for the 5 reconcilable original seed fields themselves. This
    proves the fix and guards the specific bug caught while making it: a bare
    label alternative (e.g. "Borrower") matching the tail of an unrelated
    phrase ("Cash-Out to Borrower  $78,600" in loan 04) instead of the real
    label line."""
    build_all_fixtures()
    expected_names = {
        "01": "John A. Smith", "02": "Maria E. Sanchez", "03": "Marcus D. Johnson",
        "04": "Anika R. Patel", "05": "Derrick T. Williams",
    }
    for loan_num, expected_name in expected_names.items():
        path = os.path.join(FROM_DOCS_DIR, "loan_{0}.json".format(loan_num))
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for seed_field in ("property_address", "note_rate", "loan_amount",
                           "borrower_name", "borrower_ssn"):
            truth = data["fields"][seed_field]["truth"]
            assert truth is not None, "{0}.{1}: still null".format(data["loan_id"], seed_field)
        borrower_name = data["fields"]["borrower_name"]["truth"]
        assert borrower_name == expected_name, (
            "{0}: borrower_name = {1!r}, expected {2!r} (a regression here likely means "
            "a bare label alternative matched an unrelated phrase again)"
            .format(data["loan_id"], borrower_name, expected_name)
        )
        assert "$" not in borrower_name and not borrower_name[0].isdigit()


# --- US2: 25/25 known-defect verification gate ------------------------------

def test_verify_against_defects_reports_25_of_25_on_real_fixtures():
    build_all_fixtures()
    matched, total, results = VAD.run_verification(FROM_DOCS_DIR)
    assert total == 25
    failing = [r for r in results if not r["matched"]]
    assert matched == 25, "not 25/25: {0}".format(failing)


def test_verify_against_defects_reports_24_of_25_when_one_defect_broken():
    """No partial-credit path: patch one loan's fixture so a defect no longer
    reproduces, and confirm the gate reports exactly 24/25, not a pass
    (spec.md Edge Cases)."""
    build_all_fixtures()
    loan01_path = os.path.join(FROM_DOCS_DIR, "loan_01.json")
    with open(loan01_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    original = copy.deepcopy(data)

    # Silently "fix" defect #2 (title vesting mismatch) so both sides agree —
    # simulating a broken extractor that fails to reproduce a known defect.
    data["fields"]["title_vesting_commitment"]["truth"] = \
        data["fields"]["title_vesting_1003"]["truth"]
    with open(loan01_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    try:
        matched, total, results = VAD.run_verification(FROM_DOCS_DIR)
        assert total == 25
        assert matched == 24, "expected exactly 24/25, got {0}/{1}".format(matched, total)
        broken = [r for r in results if not r["matched"]]
        assert len(broken) == 1
        assert broken[0]["field_name"] == "title_vesting_1003"
    finally:
        with open(loan01_path, "w", encoding="utf-8") as f:
            json.dump(original, f)


# --- US3: catalog grounded in real taxonomy ----------------------------------
# Every new field belongs to one of three legitimate, distinct categories, and
# every entry must self-identify which one justifies its existence -- never a
# blank/generic description (spec.md FR-004 for the rule-grounded 26; the
# 2026-07-15 comprehensive-coverage expansion for the rest, modeled explicitly
# on examples/mortgage-qc's extraction schemas, not a taxonomy.json archetype;
# the 2026-07-28/specs/010b-derive-remaining-gating-dimensions third category
# for a computed derived fact -- a canonical value the engine derives from
# other, already-catalog-grounded fields, rather than either a directly
# document-extracted value tied to a specific defect archetype or a
# comprehensive-coverage extraction field. A derived fact is grounded by
# naming its own deriving function and owning spec, not a taxonomy.json
# citation it would be dishonest to claim -- see build_loan_profiles_v3.py's
# derive_occupancy_type/derive_loan_program and their field_catalog.json
# descriptions).

def test_every_new_catalog_field_has_taxonomy_grounding_citation():
    catalog_path = os.path.join(REPO_ROOT, "p0", "qc_engine", "field_catalog.json")
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    seed_fields = {
        "borrower_name", "borrower_ssn", "note_rate", "loan_amount",
        "property_address", "flood_zone", "note_signed",
    }
    taxonomy_path = os.path.join(REPO_ROOT, "p0", "eval_synth", "taxonomy.json")
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)
    archetype_ids = {a["id"] for a in taxonomy["archetypes"]}

    new_entries = [e for e in catalog["entries"] if e["field_name"] not in seed_fields]
    assert len(new_entries) > 0
    for entry in new_entries:
        desc = entry["description"]
        is_rule_grounded = "taxonomy.json archetype" in desc and any(
            "archetype {0}".format(a) in desc for a in archetype_ids)
        is_comprehensive_coverage = (
            desc.startswith("Comprehensive-coverage field")
            and "examples/mortgage-qc" in desc
        )
        is_derived_fact_grounded = (
            "computed derived fact, not a directly-extracted field" in desc
            and ".py's derive_" in desc
            and "specs/" in desc
        )
        assert is_rule_grounded or is_comprehensive_coverage or is_derived_fact_grounded, (
            "{0}: description is neither a real taxonomy.json archetype citation, "
            "a labeled comprehensive-coverage grounding, nor a labeled derived-fact "
            "grounding -- every catalog field must self-identify which category "
            "justifies it".format(entry["field_name"])
        )


def test_comprehensive_coverage_fields_do_not_masquerade_as_rule_grounded():
    """The two grounding categories must stay honestly distinct -- a
    comprehensive-coverage field claiming a fake taxonomy citation (or vice
    versa) would be worse than having no citation at all."""
    catalog_path = os.path.join(REPO_ROOT, "p0", "qc_engine", "field_catalog.json")
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    for entry in catalog["entries"]:
        desc = entry["description"]
        if desc.startswith("Comprehensive-coverage field"):
            assert "taxonomy.json archetype" not in desc, (
                "{0}: comprehensive-coverage field must not also claim a "
                "taxonomy.json archetype citation".format(entry["field_name"]))


# --- US4: every extracted value traceable ------------------------------------

def test_every_document_sourced_field_has_non_empty_citation():
    build_all_fixtures()
    for loan_num in ("01", "02", "03", "04", "05"):
        path = os.path.join(FROM_DOCS_DIR, "loan_{0}.json".format(loan_num))
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for field_name, entry in data["fields"].items():
            if field_name in DERIVED_FIELD_NAMES:
                continue  # computed from 2 docs -- no single citation applies
            if entry.get("truth") is not None:
                citation = entry.get("citation")
                assert citation is not None, (
                    "{0}.{1} has a truth value but no citation"
                    .format(data["loan_id"], field_name)
                )
                assert citation["doc_name"]
                assert citation["page_num"] and citation["page_num"] > 0
                assert citation["segment_snippet"]


def test_citation_carries_document_title_section_and_field_label():
    """2026-07-15 addition: page_num alone is nearly useless when every source
    document is a single page. Every document-sourced citation must also carry
    document_title (always), and the mechanism must genuinely work across the
    dataset for section/field_label (not just exist as always-null keys)."""
    build_all_fixtures()
    any_section = False
    any_field_label = False
    for loan_num in ("01", "02", "03", "04", "05"):
        path = os.path.join(FROM_DOCS_DIR, "loan_{0}.json".format(loan_num))
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for field_name, entry in data["fields"].items():
            if field_name in DERIVED_FIELD_NAMES:
                continue  # computed from 2 docs -- no single citation applies
            if entry.get("truth") is None:
                continue
            citation = entry["citation"]
            assert citation.get("document_title"), (
                "{0}.{1}: citation missing document_title"
                .format(data["loan_id"], field_name)
            )
            if citation.get("section"):
                any_section = True
                # must never just re-echo the document's own title (that's
                # what document_title is for -- a distinct section or none)
                assert citation["section"] != citation["document_title"]
            if citation.get("field_label"):
                any_field_label = True
                label = citation["field_label"]
                # no dangling punctuation a regex left behind (e.g. a "$"
                # matched outside the value's own capture group), and no
                # embedded newline (a DOTALL-flag field whose value sits on a
                # different line than its label, e.g. household_income_usda --
                # a fix for one of these two must not silently reintroduce
                # the other; 2026-07-16 caught exactly this trade-off)
                assert not label.endswith(("$", ":", "—", "-")), label
                assert "\n" not in label, label
                assert label == label.strip(), label
    assert any_section, "no fixture field resolved a non-null section anywhere"
    assert any_field_label, "no fixture field resolved a non-null field_label anywhere"


def test_system_sourced_field_uses_mismo_slot_not_fabricated_citation():
    """fha_case_number_1003's system side (the FHA Connection portal's case
    number) is carried under sources['mismo'] with no page/doc citation
    fabricated for it — the doc-side citation covers only the 1003's own
    stated value (research.md decision #4)."""
    build_all_fixtures()
    loan02_path = os.path.join(FROM_DOCS_DIR, "loan_02.json")
    with open(loan02_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    entry = data["fields"]["fha_case_number_1003"]
    assert entry["sources"].get("mismo") == "381-9927614"
    # the citation present belongs to the doc (1003) side only, never a
    # fabricated page reference for the system-side value
    assert entry["citation"]["doc_name"] == "01_Final_1003_URLA.pdf"


# --- Wiring fields into real checks (fixtures/ruleset_defects.py) -----------

def test_defect_ruleset_passes_referential_integrity():
    """Every check in defects_ruleset() must resolve to a real field_catalog
    entry -- the same load-time gate the real engine runs (catalog.py's
    validate_referential_integrity, FR-004)."""
    catalog_path = os.path.join(REPO_ROOT, "p0", "qc_engine", "field_catalog.json")
    catalog = load_catalog(catalog_path)
    validate_referential_integrity(defects_ruleset(), catalog)  # must not raise


def test_wired_checks_catch_all_25_known_defects():
    """Runs the 5 document-derived fixtures through defects_ruleset() and
    confirms every one of the 25 known defects actually resolves its correct
    status, on the exact loan defect_manifest.json names. 20 use the engine's
    predicate/ratio_threshold/agree_categorical kinds; the remaining 5
    (Bucket F, spec 003d) are genuine doc-vs-doc mismatches using the new
    agree_doc_categorical/agree_doc_numeric kinds -- previously unwirable
    (this test asserted only 20/25 before 003d shipped the capability)."""
    manifest_path = os.path.join(FROM_DOCS_DIR, "defect_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # manifest field_name -> check_id, for every defect this ruleset wires.
    # (piti_ratio/dti_ratio are one manifest entry naming two independently
    # checkable fields; dti_ratio is verified separately below since the
    # manifest's own field_name key only names piti_ratio.)
    field_to_check_id = {
        "large_deposit_source_documented": "chk-def-large-deposit",
        "hud92900a_certification_signed": "chk-def-hud92900a-signed",
        "gift_funds_source_documented": "chk-def-gift-funds-documented",
        "lead_paint_completion_cert_present": "chk-def-lead-paint-cert",
        "fha_amendatory_clause_present": "chk-def-fha-amendatory-clause",
        "arm_preloan_disclosure_present": "chk-def-arm-preloan-disclosure",
        "termite_inspection_present": "chk-def-termite-inspection",
        "lead_paint_disclosure_present": "chk-def-lead-paint-disclosure",
        "va_residual_income_documented": "chk-def-va-residual-income",
        "self_employed_pl_balance_sheet_present": "chk-def-self-employed-pl-bs",
        "usda_property_eligibility_documented": "chk-def-usda-property-eligibility",
        "well_septic_test_documented": "chk-def-well-septic-test",
        "site_value_justification_documented": "chk-def-site-value-justification",
        "appraisal_comp_distance_miles": "chk-def-appraisal-comp-distance",
        "mortgage_late_payment_count_12mo": "chk-def-mortgage-late-payments",
        "household_income_usda": "chk-def-usda-household-income",
        "piti_ratio": "chk-def-usda-piti-ratio",
        "notice_of_value_date": "chk-def-nov-date-order",
        "appraisal_effective_date": "chk-def-appraisal-staleness",
        "fha_case_number_1003": "chk-def-fha-case-number",
        # Bucket F (003d) -- doc-vs-doc, previously unwirable:
        "employment_start_date_1003": "chk-def-employment-dates-agree",
        "title_vesting_1003": "chk-def-title-vesting-agree",
        "loan_purpose_1003": "chk-def-loan-purpose-agree",
        "liability_disclosed_on_1003": "chk-def-liability-disclosed-agree",
        "cd_payoff_amount": "chk-def-cd-payoff-agree",
    }
    assert len(field_to_check_id) == 25

    loans_by_id = {}
    for loan_folder, path in build_all_fixtures().items():
        loan = load_canonical_loan(path)
        loans_by_id[loan.loan_id] = loan

    wired_defects = [d for d in manifest["defects"]
                     if d["field_name"] in field_to_check_id]
    assert len(wired_defects) == 25

    # chk-def-liability-disclosed-agree is the one Bucket F case where the
    # manifest's own defect_values show doc_1003=None -- one side genuinely
    # absent, so the correct, honest verdict is NEEDS_REVIEW (SOURCE_
    # INCOMPLETE), not a special-cased FAIL. Every other Bucket F check has
    # both sides populated with genuinely differing values -> FAIL.
    #
    # spec 015 Issue 2 (2026-07-28): these 5 are is_true predicate checks
    # whose manifest-labeled defect is a genuinely missing document (the
    # field's real fixture value is None, not an explicit False) --
    # engine.py's is_true+None fix now correctly reports NEEDS_REVIEW /
    # APPLICABILITY_UNKNOWN instead of a blind FAIL. Still "caught" (never
    # silently auto-cleared), just honest about what the engine can and
    # can't determine from a missing document, per CLAUDE.md's auto-clear-
    # vs-escalate philosophy. Verified directly against each field's real
    # fixture value -- the other 8 of the 13 predicate-kind defects in this
    # manifest have an explicit False value (the file affirmatively states
    # "not documented"), untouched by this fix, and stay FAIL below.
    NEEDS_REVIEW_CHECKS = {
        "chk-def-liability-disclosed-agree",
        "chk-def-fha-amendatory-clause",
        "chk-def-arm-preloan-disclosure",
        "chk-def-lead-paint-disclosure",
        "chk-def-va-residual-income",
        "chk-def-site-value-justification",
    }

    for defect in wired_defects:
        loan = loans_by_id[defect["loan_id"]]
        check_id = field_to_check_id[defect["field_name"]]
        result = run(loan, defects_ruleset_for(loan))
        by_id = {r.check_id: r for r in result.results}
        assert check_id in by_id, (defect["loan_id"], check_id)
        # chk-def-fha-case-number is a RECONCILE-phase agree_categorical
        # check: doc-vs-system disagreement is informational (FLAG), not a
        # QC failure -- the closing doc is truth regardless of the lender's
        # system data (engine.py's own design, not a gap to fix here).
        if check_id == "chk-def-fha-case-number":
            expected_status = "FLAG"
        elif check_id in NEEDS_REVIEW_CHECKS:
            expected_status = "NEEDS_REVIEW"
        else:
            expected_status = "FAIL"
        assert by_id[check_id].status == expected_status, (
            f"defect #{defect['defect_number']} on {defect['loan_id']} "
            f"({defect['description']}) expected check '{check_id}' to "
            f"{expected_status}, got {by_id[check_id].status}")

    # USDA PITI/DTI: one manifest entry, two independently checkable fields --
    # dti_ratio's own check isn't in field_to_check_id (the manifest names
    # only piti_ratio for this entry), so verify it explicitly here.
    usda_loan = loans_by_id["2025-1122-USDA-005"]
    result = run(usda_loan, defects_ruleset_for(usda_loan))
    by_id = {r.check_id: r for r in result.results}
    assert by_id["chk-def-usda-dti-ratio"].status == "FAIL"


def test_wired_threshold_checks_are_not_applicable_on_other_loans():
    """The single-field and derived-date-diff ratio_threshold checks must not
    false-positive on loans where the field simply doesn't apply to that
    program -- every loan the defect manifest does NOT name for a given check
    must resolve NOT_APPLICABLE, never a spurious FAIL (or a spurious PASS
    that would misleadingly auto-clear)."""
    rs = defects_ruleset()
    loans_by_id = {}
    for loan_folder, path in build_all_fixtures().items():
        loan = load_canonical_loan(path)
        loans_by_id[loan.loan_id] = loan

    single_owner_checks = {
        "chk-def-appraisal-comp-distance": "2025-0917-001",
        "chk-def-mortgage-late-payments": "2025-1215-FRD-004",
        "chk-def-usda-household-income": "2025-1122-USDA-005",
        "chk-def-usda-piti-ratio": "2025-1122-USDA-005",
        "chk-def-usda-dti-ratio": "2025-1122-USDA-005",
        "chk-def-nov-date-order": "2025-1108-VA-003",
        "chk-def-fha-case-number": "2025-1004-FHA-002",
    }
    for check_id, owner_loan_id in single_owner_checks.items():
        for loan_id, loan in loans_by_id.items():
            result = run(loan, rs)
            by_id = {r.check_id: r for r in result.results}
            status = by_id[check_id].status
            if loan_id == owner_loan_id:
                # chk-def-fha-case-number is RECONCILE-phase agree_categorical:
                # doc-vs-system disagreement is informational (FLAG), not FAIL.
                expected = "FLAG" if check_id == "chk-def-fha-case-number" else "FAIL"
                assert status == expected, (check_id, loan_id, status)
            else:
                assert status == "NOT_APPLICABLE", (check_id, loan_id, status)

    # appraisal_staleness_days is the one partial exception: loan01 ALSO has
    # both source dates (a real 25-day gap, well under the 120-day limit) --
    # a genuine PASS, not NOT_APPLICABLE. Only loan04 breaches (207 days).
    result_01 = run(loans_by_id["2025-0917-001"], rs)
    assert {r.check_id: r for r in result_01.results}[
        "chk-def-appraisal-staleness"].status == "PASS"
    result_04 = run(loans_by_id["2025-1215-FRD-004"], rs)
    assert {r.check_id: r for r in result_04.results}[
        "chk-def-appraisal-staleness"].status == "FAIL"


def test_predicate_checks_are_gated_by_applicability_not_universal():
    """The 13 predicate ("missing document") checks used to run unconditionally
    against every loan -- so e.g. loan 01 (Conventional) showed FAIL on
    "HUD-92900-A signed," "USDA property eligibility documented," etc., checks
    for programs it isn't. defects_ruleset_for(loan) now gates each of the 13
    by document-presence, property-age, or program (ruleset_defects.py's own
    applicability-gating comment explains why 3 different gates, not 1).

    This test locks in the CURRENT, understood behavior -- including its one
    honest residual: lead-paint's property-age gate defaults to "applies"
    when year_built_appraisal is unknown (conservative: don't silently clear
    a compliance check for lack of contrary evidence), so loans 02/04/05 (no
    year data at all) show FAIL on BOTH lead-paint checks, not just their own
    labeled defect. That's deliberate, not a bug -- documented here so a
    future change to the default doesn't silently drift without deciding to."""
    loans_by_id = {}
    for loan_folder, path in build_all_fixtures().items():
        loan = load_canonical_loan(path)
        loans_by_id[loan.loan_id] = loan

    all_predicate_check_ids = {
        "chk-def-large-deposit", "chk-def-hud92900a-signed",
        "chk-def-gift-funds-documented", "chk-def-lead-paint-cert",
        "chk-def-fha-amendatory-clause", "chk-def-arm-preloan-disclosure",
        "chk-def-termite-inspection", "chk-def-lead-paint-disclosure",
        "chk-def-va-residual-income", "chk-def-self-employed-pl-bs",
        "chk-def-usda-property-eligibility", "chk-def-well-septic-test",
        "chk-def-site-value-justification",
    }
    # loan_id -> the predicate checks that apply to it. Historically all
    # expected FAIL; spec 015 Issue 2 (2026-07-28) changed that for the
    # subset whose real fixture value is None (genuinely missing document,
    # not an explicit False) -- those now correctly resolve NEEDS_REVIEW /
    # APPLICABILITY_UNKNOWN instead. This is genuinely per-(loan, check),
    # not per-check-id: e.g. chk-def-lead-paint-cert is an explicit False
    # for FHA-002 (stays FAIL) but None for VA-003/FRD-004/USDA-005 (becomes
    # NEEDS_REVIEW) -- verified directly against each loan's real fixture
    # value below, see NEEDS_REVIEW_PAIRS.
    expected_applicable = {
        "2025-0917-001": {"chk-def-large-deposit"},
        "2025-1004-FHA-002": {
            "chk-def-fha-amendatory-clause", "chk-def-gift-funds-documented",
            "chk-def-hud92900a-signed", "chk-def-lead-paint-cert",
            "chk-def-lead-paint-disclosure",  # residual: year unknown, conservative gate-in
        },
        "2025-1108-VA-003": {
            "chk-def-arm-preloan-disclosure", "chk-def-lead-paint-cert",
            "chk-def-lead-paint-disclosure",  # genuine: year_built_appraisal=1962
            "chk-def-termite-inspection", "chk-def-va-residual-income",
        },
        "2025-1215-FRD-004": {
            "chk-def-lead-paint-cert", "chk-def-lead-paint-disclosure",  # residual
            "chk-def-self-employed-pl-bs",
        },
        "2025-1122-USDA-005": {
            "chk-def-lead-paint-cert", "chk-def-lead-paint-disclosure",  # residual
            "chk-def-site-value-justification",
            "chk-def-usda-property-eligibility", "chk-def-well-septic-test",
        },
    }

    # spec 015 Issue 2 (2026-07-28): (loan_id, check_id) pairs whose real
    # fixture value is None (genuinely missing document) rather than an
    # explicit False -- these now correctly resolve NEEDS_REVIEW /
    # APPLICABILITY_UNKNOWN, not FAIL. Confirmed directly against
    # loan.get(field_name).doc for every pair in expected_applicable above;
    # every pair NOT listed here has an explicit False and stays FAIL.
    NEEDS_REVIEW_PAIRS = {
        ("2025-1004-FHA-002", "chk-def-fha-amendatory-clause"),
        ("2025-1004-FHA-002", "chk-def-lead-paint-disclosure"),
        ("2025-1108-VA-003", "chk-def-arm-preloan-disclosure"),
        ("2025-1108-VA-003", "chk-def-lead-paint-disclosure"),
        ("2025-1108-VA-003", "chk-def-va-residual-income"),
        ("2025-1108-VA-003", "chk-def-lead-paint-cert"),
        ("2025-1215-FRD-004", "chk-def-lead-paint-cert"),
        ("2025-1215-FRD-004", "chk-def-lead-paint-disclosure"),
        ("2025-1122-USDA-005", "chk-def-site-value-justification"),
        ("2025-1122-USDA-005", "chk-def-lead-paint-disclosure"),
        ("2025-1122-USDA-005", "chk-def-lead-paint-cert"),
    }

    for loan_id, loan in loans_by_id.items():
        rs = defects_ruleset_for(loan)
        present_ids = {c.id for c in rs.checks} & all_predicate_check_ids
        assert present_ids == expected_applicable[loan_id], (
            loan_id, present_ids, expected_applicable[loan_id])

        result = run(loan, rs)
        by_id = {r.check_id: r for r in result.results}
        for check_id in present_ids:
            expected = ("NEEDS_REVIEW" if (loan_id, check_id) in NEEDS_REVIEW_PAIRS
                        else "FAIL")
            assert by_id[check_id].status == expected, (
                loan_id, check_id, by_id[check_id].status, "expected", expected)
