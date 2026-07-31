# Architecture: Routes

| | |
|---|---|
| **Date** | 2026-07-30 |
| **Covers** | `src/shacl_pilot/routes.json` · the `agency` field on every rule in `src/shacl_pilot/compiled/ruleset.json` |
| **Why this exists** | Routes are the top of the **Route → Block → Check** hierarchy that the whole authoring surface is built on (`CLAUDE.md` Non-Negotiable #4), but there was no single document stating what the routes actually are, how a loan gets assigned one, or how many rules each one runs. Written directly from the artifacts, not from the specs — every number below was measured, and the commands to reproduce them are given. |
| **Companion** | `../block/README.md` (the 16 blocks) · `specs/019-workbook-first-rule-authoring/spec.md` (the authoring surface these feed) |
| **Data version** | `ruleset_sha256` `6fa9840dc020`, compiled from `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` |

---

## 1. What a Route is, in one sentence

A **Route** is the set of Blocks that run against one loan, selected **deterministically** from the
loan's agency/program — so a Fannie Mae conventional loan and an FHA loan get different, correct sets
of checks without anyone choosing by hand.

---

## 2. The five routes

`routes.json` defines five, one per agency program:

| Route id | Title | Agency token | Checks that run |
|---|---|---|---:|
| `frd-post-closing-qc` | Freddie Mac Post-Closing QC | `O-FRD` | **1,122** |
| `fnm-post-closing-qc` | Conventional (Fannie Mae) Post-Closing QC | `O-FNM` | **1,086** |
| `fha-post-closing-qc` | FHA Post-Closing QC | `O-FHA` | **727** |
| `rhs-post-closing-qc` | USDA/RHS Post-Closing QC | `O-RHS` | **609** |
| `va-post-closing-qc` | VA Post-Closing QC | `O-VA` | **545** |

Each count = that agency's own rules **plus 180 generic rules** that run in every route (see §4).

---

## 3. How a loan gets its route

Deterministic lookup — no model call, no human choice:

```
loan documents  →  agency detected  →  routes.json: selection_by_agency  →  one route
```

```json
"selection_by_agency": {
  "O-FNM": "fnm-post-closing-qc",
  "O-FHA": "fha-post-closing-qc",
  "O-VA":  "va-post-closing-qc",
  "O-FRD": "frd-post-closing-qc",
  "O-RHS": "rhs-post-closing-qc"
}
```

The agency itself is detected from the loan's own documents (decision 010) and recorded on every run,
so the route choice is auditable after the fact.

---

## 4. Route is **derived**, not stored — and it is one-to-many

**There is no `route` field on any rule.** Confirmed: the 17 keys on a compiled rule are `agency`,
`aor`, `block`, `category`, `demo_in_scope`, `eval_class`, `eval_target`, `exception_code`,
`exception_description`, `exception_name`, `question_code`, `question_text`, `response_text`,
`severity`, `source_rows`, `yellow_blocker_type`, `yellow_category`. Route is computed from `agency`
via the table above.

That matters for the UI, because the relationship is **not** one rule → one route:

| `agency` | Checks | Route |
|---|---:|---|
| `O-FRD` | 942 | `frd-post-closing-qc` |
| `O-FNM` | 906 | `fnm-post-closing-qc` |
| `O-FHA` | 547 | `fha-post-closing-qc` |
| `O-RHS` | 429 | `rhs-post-closing-qc` |
| `O-VA` | 365 | `va-post-closing-qc` |
| `GENERIC` | **180** | **all five** |

The 180 generic rules are regulatory, not program-specific, so they belong to every route:
`O-FED-` 36 · `O-EPD-` 34 · `O-BP-` 6 · `O-CFPB-` 4 · `O-IRS-` 2 · `O-UDAAP-` 1 · and **97 with no
`O-` prefix at all**. This matches the existing finding that only the five agency tokens carry a
program (`docs/AMQ-PROGRAM-TAXONOMY.md`).

> **UI consequence.** Route must be a **filter**, not a per-row column. "Show me the FHA route" → 727
> rules. A per-row route label would need five values in one cell for every generic rule, which reads
> as noise. This is recorded as a design constraint in spec 019.

---

## 5. Blocks per route

All five routes draw from the same 16-block catalog, but not every block has rules in every route:

| Block | FNM | FHA | VA | FRD | RHS |
|---|---:|---:|---:|---:|---:|
| `product-specific-check` | 228 | 120 | 121 | 229 | 99 |
| `property-appraisal-review` | 178 | 93 | 63 | 176 | 94 |
| `income-verification` | 139 | 78 | 53 | 163 | 83 |
| `underwriting-review` | 92 | 101 | 90 | 92 | 107 |
| `credit-liabilities-review` | 62 | 81 | 44 | 85 | 46 |
| `asset-verification` | 78 | 48 | 18 | 67 | 26 |
| `insurance-review` | 53 | 32 | 23 | 47 | 26 |
| `loan-documents-review` | 51 | 23 | 19 | 26 | 14 |
| `data-validation-services` | 46 | — | — | 91 | — |
| `epd-review` | 34 | 34 | 34 | 34 | 34 |
| `closing-documents-review` | 22 | 33 | 31 | 54 | 33 |
| `appraisal-form-1033` | 30 | — | — | — | — |
| `information-integrity` | 30 | 19 | 9 | 17 | 13 |
| `application-verification` | 15 | 25 | 21 | 19 | 17 |
| `certification-delivery` | 14 | 26 | 5 | 8 | 3 |
| `compliance-review` | 14 | 14 | 14 | 14 | 14 |
| **Total** | **1,086** | **727** | **545** | **1,122** | **609** |

Two blocks are **not universal**:

- **`appraisal-form-1033`** (Fannie Mae Form 1033) — Fannie only, all 30 checks. Correct: it is a
  Fannie-specific form.
- **`data-validation-services`** (DVS) — Fannie (46) and Freddie (91) only. Correct: DVS is a GSE
  service, not an FHA/VA/USDA one.

Two blocks are **identical across all five** because they are entirely generic: `compliance-review`
(ATR-QM, 14) and `epd-review` (EPD, 34).

---

## 6. Known gap: two declared blocks have no rules

`routes.json` declares agency-specific `extra_blocks`, and **neither has a single rule mapped to it**:

| Route | `extra_blocks` | Rules |
|---|---|---:|
| `fha-post-closing-qc` | `fha-compliance-check` | **0** |
| `va-post-closing-qc` | `va-eligibility-check` | **0** |

They are placeholders that never received rule content. Harmless to the engine, but a Route screen
that renders `catalog_blocks + extra_blocks` will show two permanently empty blocks with no
explanation. **Either label them explicitly as declared-but-unpopulated, or omit them** — do not
render a silent blank.

This also means "how many blocks are there?" has three defensible answers: **16** (blocks with rules),
**18** (including the two empty `extra_blocks`), or **19** (including the excluded `Discarded`
category). Any surface that shows a block count must state its basis.

---

## 7. Reproducing every number here

```bash
cd /Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod
python3 - <<'PY'
import json, collections
rs = json.load(open('src/shacl_pilot/compiled/ruleset.json'))
rt = json.load(open('src/shacl_pilot/routes.json'))
chk = [x for x in rs['rules'] if str(x.get('exception_code','')).strip()]
gen = [x for x in chk if x['agency'] == 'GENERIC']
print('defect checks:', len(chk), '| generic:', len(gen))
for agency, route in rt['selection_by_agency'].items():
    sub = [x for x in chk if x['agency'] == agency] + gen
    print(f'{route:<24}{len(sub):>6}')
PY
```

---

## 8. Caveats

- **Counts are over the 3,369 defect checks**, not all 4,166 compiled rules. The other 797 are
  affirmative "Yes / Not Applicable" questionnaire branches with no Exception Code — not checks.
  (A direct workbook read counts 3,370; `amq_compiler.py:301` excludes one external-lookup rule.)
- **A route running N checks does not mean N checks execute.** Only **12** rules ruleset-wide are
  compiled into SHACL today — see `../block/README.md` §4. The rest have no executable logic yet.
- **Pre-Funding is not covered.** These routes are Post-Closing only (5,520 of the workbook's 10,345
  rows). Pre-Funding's 4,825 rows have never been ingested.
- **`extra_blocks` are empty** (§6) — the block-per-route table above reflects rules that exist, not
  every block a route declares.
