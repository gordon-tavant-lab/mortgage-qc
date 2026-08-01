"""Deterministic gate for atomic (decomposed) rules. No LLM. Exit 1 on hard failure.

Checks: schema conformance, citation section_ids resolve against guide/index.json, the
business rule the schema comment promises (compile.status='compiled' requires >=1 citation
unless failure_category='lender_specific_no_guide_basis'), and exception_code/severity
round-trip fidelity against the parent compiled card.
"""
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
schema = json.load(open(ROOT / 'schema' / 'rule.schema.json'))
index = {e['section_id'] for e in json.load(open(ROOT / 'guide' / 'index.json'))}
validator = jsonschema.Draft202012Validator({'$defs': schema['$defs'], '$ref': '#/$defs/atomicRule'})

hard = []
all_rules = []
by_cat = {}

for path in sorted((ROOT / 'data' / 'atomic').glob('*.json')):
    d = json.load(open(path))
    cat = d['category']
    rules = d['atomic_rules']
    src = json.load(open(ROOT / 'data' / 'compiled' / f'{cat.lower().replace(" ", "-")}.json'))
    src_codes = sorted((c['card_id'], o['finding']['exception_code'], o['finding'].get('severity'))
                       for c in src for o in c['defect_options'])
    out_codes = sorted((r['provenance']['parent_card_id'], r['finding']['exception_code'], r['finding'].get('severity'))
                       for r in rules)
    if src_codes != out_codes:
        hard.append(f'{cat}: exception_code/severity round-trip mismatch vs source '
                    f'({len(src_codes)} source options, {len(out_codes)} atomic rules)')

    for r in rules:
        for e in validator.iter_errors(r):
            hard.append(f"{r['rule_id']}: schema: {e.message[:140]} @ {'/'.join(map(str, e.path))}")
        for c in r.get('citations', []):
            if c.get('section_id') not in index:
                hard.append(f"{r['rule_id']}: citation {c.get('section_id')} not in guide index")
        status = r.get('compile', {}).get('status')
        flag = r.get('compile', {}).get('failure_category')
        if status == 'compiled' and not r.get('citations') and flag != 'lender_specific_no_guide_basis':
            hard.append(f"{r['rule_id']}: compiled with zero citations and no lender_specific_no_guide_basis flag")
        all_rules.append(r)
    by_cat[cat] = len(rules)

summary = {
    'atomic_rules': len(all_rules),
    'by_category': by_cat,
    'hard_failures': len(hard),
}
(ROOT / 'data' / 'rules_atomic.json').write_text(
    json.dumps({'schema_version': '1.0.0', 'atomic_rules': all_rules, 'validation_summary': summary}, indent=1))
print(json.dumps(summary, indent=2))
if hard:
    print(f'\nHARD FAILURES ({len(hard)}):', *hard[:40], sep='\n  ')
    sys.exit(1)
print('\nGATE PASS')
