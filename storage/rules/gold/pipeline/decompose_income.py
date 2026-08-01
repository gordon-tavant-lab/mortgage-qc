"""Atomic decomposition of the Income category (flagship depth).

Every defect_option already carries a verified check_type (compile) and the parent card's
citations were adversarially verified (verify pass, both PASS "minor_issues" with no
citation_errors of substance beyond the 2 bundle cards' known under-coverage). Decomposition
here means: promote each defect_option to a standalone atomic_rule, and where a defect_option's
true topic is narrower than the card's shared citation set, give it its OWN precise citation
instead of inheriting the whole card's list. The precise mappings below are NOT freshly guessed
-- they were already established during compile (card.compile.nuance / card.notes, which named
the exact governing section per named sub-topic) and during verify (which caught one
compile-time miscategorization: 'Income - Other' on O-FNM-15330 is SSI-specific -> B3-3.4-15,
not the generic umbrella it was filed under).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
income = json.load(open(ROOT / 'data' / 'compiled' / 'income.json'))
index = {e['section_id']: e for e in json.load(open(ROOT / 'guide' / 'index.json'))}

# exception_code -> single precise section_id, only where narrower than the card's citation set.
PRECISE_CITATION = {
    # O-FNM-15330 "other income" bundle -- 8 named sub-topics + umbrella
    'O-FNM-00432': 'B3-3.4-04',   # Boarder
    'O-FNM-55664': 'B3-3.4-04',   # Personal-assistant boarder rental income (grouped w/ Boarder)
    'O-FNM-00431': 'B3-3.4-07',   # Foster care
    'O-FNM-00427': 'B3-3.4-08',   # Interest & dividend
    'O-FNM-00429': 'B3-3.3-06',   # Mortgage differential / employer subsidy
    'O-FNM-00428': 'B3-3.4-11',   # Notes receivable
    'O-FNM-00424': 'B3-3.4-12',   # Public assistance
    'O-FNM-00425': 'B3-3.3-09',   # Temporary leave
    'O-FNM-00430': 'B3-3.4-18',   # VA benefits
    # verify-caught correction: 'Income - Other' response text is SSI-gross-up specific
    'Income - Other': 'B3-3.4-15',

    # O-FNM-15331 "additional other income" bundle -- 8 named sub-topics + umbrella
    'O-FNM-00436': 'B3-3.4-05',   # Capital gains
    'O-FNM-51012': 'B3-3.4-06',   # Employment-related assets, LTV threshold
    'O-FNM-54028': 'B3-3.4-06',   # Employment-related assets, monthly-amount calc
    'O-FNM-55665': 'B3-3.2-02',   # Foreign income, tax returns
    'O-FNM-55666': 'B3-3.2-02',   # Foreign income, USD translation
    'O-FNM-55677': 'B3-3.1-01',   # Virtual currency as asset-based income
    'O-FNM-00438': 'B3-3.1-01',   # Non-occupant borrower income
    'O-FNM-00435': 'B3-3.4-10',   # Mortgage credit certificate
    'O-FNM-00437': 'B3-3.4-13',   # Royalty
    'O-FNM-02572': 'B3-3.4-19',   # Schedule K-1 < 25% ownership

    # O-FNM-16379 trust income: one option is really an employment-related-assets rule
    'O-FNM-57140': 'B3-3.4-06',
}

EVIDENCE_KEYWORDS = [
    (r'\bpaystub', 'paystub'), (r'\bw-?2', 'W2'), (r'\btax return', 'tax_return'),
    (r'\btax transcript|4506-?c', 'irs_tax_transcript_4506c'),
    (r'\bvoe\b|form 1005', 'VOE_form_1005'), (r'\bvvoe\b|verbal verification', 'VVOE_record'),
    (r'\b1003\b|urla', 'URLA_1003_final'), (r'\b1008\b|transmittal', 'form_1008'),
    (r'\baus\b', 'AUS_findings'), (r'\bdu\b|desktop underwriter', 'DU_findings'),
    (r'\bform 1007|form 1025', 'appraisal_rental_schedule'),
    (r'\bschedule e\b|form 8825', 'tax_return_schedule_e'),
    (r'\blease\b', 'lease_agreement'), (r'\bbank statement|account statement', 'bank_statement'),
    (r'\baward letter|ssa-1099|social security administration', 'ssa_award_letter'),
    (r'\btrust agreement|trustee', 'trust_agreement'),
    (r'\bw-?2s? covering|distribution', 'brokerage_rsu_statement'),
    (r'\bemail exchange|employer email', 'employer_email_verification'),
    (r'\bincome calculator', 'income_calculator_findings_report'),
    (r'\bk-1|1065|1120s', 'schedule_k1'),
    (r'\bles\b|leave and earnings', 'military_LES'),
]


def infer_evidence(text):
    t = text.lower()
    for pat, name in EVIDENCE_KEYWORDS:
        if re.search(pat, t):
            return {'kind': 'document', 'name': name}
    return {'kind': 'document', 'name': 'loan_file_documentation'}


def build_logic(check_type, description):
    d = description.rstrip('.')
    templates = {
        'doc_presence': f'Confirm the file contains: {d}. Fail if absent.',
        'doc_completeness': f'Extract the relevant document and verify it satisfies: {d}. Fail if the document exists but this content/field requirement is unmet.',
        'computation': f'Recompute the value per Selling Guide formula and compare to the file: {d}. Fail on mismatch beyond any stated tolerance.',
        'threshold_eligibility': f'Extract the governing attribute and compare against the Guide-stated bound/enumeration: {d}. Fail if the loan falls outside the eligible set.',
        'date_window': f'Compute the interval between the two referenced dates and compare to the required window: {d}. Fail if outside the window.',
        'cross_doc_consistency': f'Extract the value from each source document and compare for consistency: {d}. Fail on mismatch.',
        'scripted_review': f'Evaluate against the criteria checklist derived from the cited section: {d}. If evidence is insufficient to decide, emit REQUIRES_HUMAN_REVIEW instead of a finding.',
    }
    return templates.get(check_type, f'Evaluate: {d}.')


def citation_obj(section_id):
    e = index[section_id]
    return {'section_id': section_id, 'title': e['title'], 'effective_date': e['effective_date'],
            'guide_version': '2026-06-03'}


rules = []
seq = 0
for card in income:
    card_citations = card['citations']
    for opt in card['defect_options']:
        seq += 1
        code = opt['finding']['exception_code']
        override = PRECISE_CITATION.get(code)
        citations = [citation_obj(override)] if override else list(card_citations)
        rule = {
            'rule_id': f'FNM-INC-{seq:04d}',
            'status': 'draft',
            'version': 1,
            'check_type': opt['check_type'],
            'statement': opt['finding']['description'],
            'applicability': card['applicability'],
            'evidence': [infer_evidence(opt['finding']['description'] + ' ' + opt['response'])],
            'logic': {'procedure': build_logic(opt['check_type'], opt['finding']['description'])},
            'finding': opt['finding'],
            'citations': citations,
            'provenance': {
                'parent_card_id': card['card_id'],
                'source_defect_option': opt['response'],
                'compiled_by': 'Fable 5, direct in-context decomposition, 2026-07-31',
            },
            'compile': {'status': 'compiled'},
        }
        if override:
            rule['notes'] = 'Citation precision-assigned during decomposition (narrower than parent card\'s shared citation set) -- see pipeline/decompose_income.py PRECISE_CITATION.'
        rules.append(rule)

out = {'schema_version': '1.0.0', 'generated': 'decompose_income.py', 'guide_version': '2026-06-03',
       'category': 'Income', 'parent_cards': len(income), 'atomic_rules': rules}
(ROOT / 'data' / 'atomic' / 'income.json').write_text(json.dumps(out, indent=1))
print(f'parent cards: {len(income)}  atomic rules: {len(rules)}')
