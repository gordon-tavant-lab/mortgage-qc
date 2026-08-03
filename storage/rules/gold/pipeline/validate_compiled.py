"""Deterministic post-compile gate. No LLM. Exit code 1 on any hard failure.

Checks:
  1. Every category file present; per-category card count == source count.
  2. JSON Schema validation of every compiled card ($defs.card).
  3. Every citation section_id exists in guide/index.json (citation-drift gate).
  4. Exception-code round-trip: every source defect option's exception_code appears in the
     compiled card (minus documented dedups); no invented codes; severities byte-identical.
  5. Every card has >=1 citation OR lender_specific_no_guide_basis flag.
Merges everything into data/rules_compiled.json with a summary block.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
schema = json.load(open(ROOT / 'schema' / 'rule.schema.json'))
index = {e['section_id'] for e in json.load(open(ROOT / 'guide' / 'index.json'))}
card_validator = jsonschema.Draft202012Validator(
    {'$defs': schema['$defs'], '$ref': '#/$defs/card'})

hard, soft = [], []
all_cards = []
by_cat_dir = ROOT / 'data' / 'by_category'
compiled_dir = ROOT / 'data' / 'compiled'

for src_file in sorted(by_cat_dir.glob('*.json')):
    cat = src_file.stem
    src = json.load(open(src_file))
    # Large categories may be split into batches: <cat>.b1.json, <cat>.b2.json, ...
    # instead of a single <cat>.json. Merge whichever exists.
    single = compiled_dir / f'{cat}.json'
    batches = sorted(compiled_dir.glob(f'{cat}.b*.json'))
    if single.exists():
        comp = json.load(open(single))
    elif batches:
        comp = []
        for bf in batches:
            comp.extend(json.load(open(bf)))
    else:
        hard.append(f'{cat}: compiled file MISSING (checked {cat}.json and {cat}.b*.json)')
        continue
    if len(comp) != len(src):
        hard.append(f'{cat}: card count {len(comp)} != source {len(src)}')
    src_by_id = {c['card_id']: c for c in src}
    for card in comp:
        cid = card.get('card_id', '?')
        for err in card_validator.iter_errors(card):
            hard.append(f'{cid}: schema: {err.message[:140]} @ {"/".join(map(str, err.path))}')
        for cit in card.get('citations', []):
            if cit.get('section_id') not in index:
                hard.append(f'{cid}: citation {cit.get("section_id")} not in guide index')
        if not card.get('citations'):
            fc = (card.get('compile') or {}).get('failure_category')
            st = (card.get('compile') or {}).get('status')
            if fc != 'lender_specific_no_guide_basis' and card.get('dominant_type') != 'routing_context' and st != 'failed':
                hard.append(f'{cid}: zero citations without lender_specific/failed flag')
        s = src_by_id.get(cid)
        if s is None:
            hard.append(f'{cid}: not in source category file')
            continue
        src_codes = Counter((o['exception_code'], o['significance'])
                            for o in s['answer_options'] if o['exception_code'])
        out_codes = Counter((d['finding']['exception_code'], d['finding'].get('severity'))
                            for d in card.get('defect_options', []))
        missing = set(src_codes) - set(out_codes)
        invented = set(out_codes) - set(src_codes)
        if missing:
            hard.append(f'{cid}: dropped codes {sorted(missing)[:4]}')
        if invented:
            hard.append(f'{cid}: invented/mutated codes {sorted(invented)[:4]}')
        n_src_defects = sum(src_codes.values())
        n_out = sum(out_codes.values())
        if n_out < len(src_codes):
            hard.append(f'{cid}: defect option count {n_out} < distinct source {len(src_codes)}')
        elif n_out < n_src_defects and 'dedup' not in (card.get('notes') or '').lower():
            soft.append(f'{cid}: {n_src_defects - n_out} options deduped without a dedup note')
        all_cards.append(card)

types = Counter(c.get('dominant_type') for c in all_cards)
statuses = Counter((c.get('compile') or {}).get('status') for c in all_cards)
atomic_types = Counter(d['check_type'] for c in all_cards for d in c.get('defect_options', []))
summary = {
    'cards': len(all_cards),
    'defect_options': sum(len(c.get('defect_options', [])) for c in all_cards),
    'compile_status': dict(statuses),
    'dominant_types': dict(types.most_common()),
    'atomic_option_types': dict(atomic_types.most_common()),
    'decomposition_pending': sum(1 for c in all_cards
                                 if (c.get('decomposition') or {}).get('status') == 'pending'),
    'hard_failures': len(hard),
    'soft_warnings': len(soft),
}
out = {'schema_version': '1.0.0', 'generated': 'validate_compiled', 'guide_version': '2026-06-03',
       'cards': all_cards, 'validation_summary': summary}
(ROOT / 'data' / 'rules_compiled.json').write_text(json.dumps(out, indent=1))
(ROOT / 'data' / 'validation_report.json').write_text(
    json.dumps({'summary': summary, 'hard': hard, 'soft': soft}, indent=1))
print(json.dumps(summary, indent=2))
if hard:
    print(f'\nHARD FAILURES ({len(hard)}):', *hard[:40], sep='\n  ')
    sys.exit(1)
print('\nGATE PASS' + (f' ({len(soft)} soft warnings)' if soft else ''))
