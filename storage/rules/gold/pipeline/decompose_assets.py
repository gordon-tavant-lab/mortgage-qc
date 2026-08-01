"""Atomic decomposition of the Assets category (flagship depth).

Unlike Income, no Assets card was flagged decomposition.required=true -- every card already
maps to one narrowly-scoped asset sub-type (reserves, IPCs, VOD, retirement, gift funds, EMD,
etc.), so decomposition here is a straightforward 1:1 promotion of each defect_option to an
atomic rule inheriting the parent card's citations. Two exceptions, both already identified
during compile (recorded in compile.nuance, just omitted from the card-level citation array
by the 4-citation cap): O-FNM-56339 (real estate commission credit) governs specifically under
B3-4.3-21, and O-FNM-50259 (pooled savings) under B3-4.2-04.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
assets = json.load(open(ROOT / 'data' / 'compiled' / 'assets.json'))
index = {e['section_id']: e for e in json.load(open(ROOT / 'guide' / 'index.json'))}

PRECISE_CITATION = {
    'O-FNM-56339': 'B3-4.3-21',   # Borrower's Earned Real Estate Commission
    'O-FNM-50259': 'B3-4.2-04',   # Pooled Savings (Community Savings Funds)
}

EVIDENCE_KEYWORDS = [
    (r'\bbank statement|account statement|voa\b|voice of deposit|\bvod\b', 'bank_statement'),
    (r'\bgift letter|gift of equity', 'gift_letter'),
    (r'\bretirement (?:statement|account)|401\(k\)|ira\b', 'retirement_account_statement'),
    (r'\bearnest money|emd\b', 'earnest_money_deposit_record'),
    (r'\bsettlement statement|closing (?:disclosure|statement)', 'settlement_statement'),
    (r'\bpurchase (?:contract|agreement)|sales contract', 'sales_contract'),
    (r'\btrust account|trust manager|trustee', 'trust_account_statement'),
    (r'\bvirtual currency', 'virtual_currency_exchange_record'),
    (r'\bforeign asset', 'foreign_asset_documentation'),
    (r'\bdu\b|desktop underwriter', 'DU_findings'),
    (r'\baus\b', 'AUS_findings'),
    (r'\bcredit card', 'credit_card_statement'),
    (r'\blife insurance', 'life_insurance_cash_value_statement'),
    (r'\bnote\b.*(?:secured|collateral)', 'promissory_note'),
    (r'\bemployer', 'employer_documentation'),
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
        'routing_context': f'Record context flag from selected answer: {d}.',
    }
    return templates.get(check_type, f'Evaluate: {d}.')


def citation_obj(section_id):
    e = index[section_id]
    return {'section_id': section_id, 'title': e['title'], 'effective_date': e['effective_date'],
            'guide_version': '2026-06-03'}


rules = []
seq = 0
skipped_zero_defect = []
for card in assets:
    if not card['defect_options']:
        skipped_zero_defect.append(card['card_id'])
        continue
    card_citations = card['citations']
    for opt in card['defect_options']:
        seq += 1
        code = opt['finding']['exception_code']
        override = PRECISE_CITATION.get(code)
        citations = [citation_obj(override)] if override else list(card_citations)
        if not citations:
            # PC::Custodial Acct: card itself has 0 citations (lender_specific_no_guide_basis,
            # confirmed exhaustive zero-hit grep at compile time) -- atomic rule inherits that.
            citations = []
        rule = {
            'rule_id': f'FNM-AST-{seq:04d}',
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
            'compile': ({'status': 'compiled_with_flags', 'failure_category': 'lender_specific_no_guide_basis',
                         'nuance': 'Inherited from parent card PC::Custodial Acct: exhaustive zero-hit grep across all 390 guide sections at compile time.'}
                        if not citations else {'status': 'compiled'}),
        }
        if override:
            rule['notes'] = 'Citation precision-assigned during decomposition (named in parent card.compile.nuance but omitted from the card-level citation array by the 4-citation cap) -- see pipeline/decompose_assets.py PRECISE_CITATION.'
        rules.append(rule)

out = {'schema_version': '1.0.0', 'generated': 'decompose_assets.py', 'guide_version': '2026-06-03',
       'category': 'Assets', 'parent_cards': len(assets), 'atomic_rules': rules,
       'routing_context_cards_excluded': skipped_zero_defect}
(ROOT / 'data' / 'atomic' / 'assets.json').write_text(json.dumps(out, indent=1))
print(f'parent cards: {len(assets)}  atomic rules: {len(rules)}  excluded (0 defects): {skipped_zero_defect}')
