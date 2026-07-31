# Architecture: Blocks

| | |
|---|---|
| **Date** | 2026-07-30 |
| **Covers** | the `block` / `category` fields on every rule in `src/shacl_pilot/compiled/ruleset.json` · `CATEGORY_TO_BLOCK` in `src/shacl_pilot/amq_compiler.py` · `catalog_blocks` in `src/shacl_pilot/routes.json` |
| **Why this exists** | A **Block** is the middle tier of **Route → Block → Check**, and it is the unit an SME actually groups checks into (`CLAUDE.md` Non-Negotiable #4: *"Block = one named grouping of checks per raw AMQ Question Category Name"*). This is the definitive list, with real counts. Written from the artifacts, not the specs; §8 gives the command to reproduce every figure. |
| **Companion** | `../README.md` (the five routes) · `specs/019-workbook-first-rule-authoring/spec.md` |
| **Data version** | `ruleset_sha256` `6fa9840dc020` |

---

## 1. What a Block is, in one sentence

A **Block** is one named grouping of checks, mapping **1:1 to a raw AMQ "Question Category Name"** —
so the lender's own 16 categories become the 16 blocks, with **no manual re-organization of 3,369
checks required**.

The 1:1 mapping is verified: every one of the 16 block ids resolves to exactly one AMQ category, and
vice versa. `CATEGORY_TO_BLOCK` in `amq_compiler.py` does nothing but rename (`Assets` →
`asset-verification`); it never splits or merges a category.

---

## 2. The 16 blocks

Sorted by size. **Green** = checks compiled into executable SHACL today. **Affirm.** = affirmative
"Yes / Not Applicable" questionnaire rows, which are *not* checks (§5).

| # | Block id | AMQ Question Category | Checks | Green | Affirm. |
|---|---|---|---:|---:|---:|
| 1 | `product-specific-check` | Product Specific | 589 | 0 | 115 |
| 2 | `property-appraisal-review` | Property - Appraisal | 584 | 0 | 130 |
| 3 | `income-verification` | Income | 516 | **2** | 100 |
| 4 | `underwriting-review` | Underwriting | 374 | 0 | 92 |
| 5 | `credit-liabilities-review` | Credit - Liabilities | 302 | 0 | 84 |
| 6 | `asset-verification` | Assets | 229 | **4** | 75 |
| 7 | `data-validation-services` | Data Validation Svc-DVS | 137 | 0 | 20 |
| 8 | `insurance-review` | Insurance | 133 | 0 | 28 |
| 9 | `closing-documents-review` | Closing | 125 | 0 | 34 |
| 10 | `loan-documents-review` | Loan Documents | 109 | 0 | 31 |
| 11 | `information-integrity` | Information Integrity | 84 | 0 | 14 |
| 12 | `application-verification` | Application | 61 | **6** | 19 |
| 13 | `certification-delivery` | Certification, Endorsement, and Delivery | 48 | 0 | 10 |
| 14 | `epd-review` | EPD | 34 | 0 | 9 |
| 15 | `appraisal-form-1033` | Fannie Mae Form 1033 | 30 | 0 | 30 |
| 16 | `compliance-review` | ATR-QM | 14 | 0 | 6 |
| | **TOTAL** | | **3,369** | **12** | **797** |

---

## 3. Distribution — the shape an authoring UI must survive

- **The top 3 blocks hold 50%** of all checks (1,689 of 3,369). The top 6 hold **77%**.
- **The largest single block is 589 checks** — against 27 in today's mock data, a **22× jump**. A flat
  scrollable list is not viable; question-code grouping collapses `property-appraisal-review`'s 584
  into ~131 groups.
- **The smallest is 14** (`compliance-review`). So one UI must work at both 14 and 589 — hence spec
  019's rule that grouping collapses only above ~50 checks per block.

---

## 4. Compile coverage: 12 of 3,369, in 3 of 16 blocks

**13 of 16 blocks have zero compiled checks.** The 12 that exist:

| Block | Exception Code | SHACL shape | Severity |
|---|---|---|---|
| `application-verification` | `O-FHA-54281` | `CoBorrowerSectionCompleteShape` | Critical |
| `application-verification` | `O-FHA-58072` | `CoBorrowerSectionCompleteShape` | Critical |
| `application-verification` | `O-FNM-58197` | `CoBorrowerSectionCompleteShape` | Major |
| `application-verification` | `O-FRD-58201` | `CoBorrowerSectionCompleteShape` | Major |
| `application-verification` | `O-RHS-58247` | `CoBorrowerSectionCompleteShape` | Major |
| `application-verification` | `O-VA-58305` | `CoBorrowerSectionCompleteShape` | Critical |
| `asset-verification` | `O-FHA-50677-1` | `LargeDepositShape` | Critical |
| `asset-verification` | `O-FNM-00215` | `LargeDepositShape` | Critical |
| `asset-verification` | `O-FRD-50451` | `LargeDepositShape` | Critical |
| `asset-verification` | `O-RHS-02772` | `GiftEvidenceShape` | Critical |
| `income-verification` | `O-FHA-02293` | `SelfEmployedDocsShape` | Critical |
| `income-verification` | `O-VA-00364` | `SelfEmployedDocsShape` | Critical |

Two facts worth stating plainly:

1. **The 12 rules are only 4 distinct shapes.** `CoBorrowerSectionCompleteShape` covers 6 rules (the
   same defect across all five agencies), `LargeDepositShape` 3, `SelfEmployedDocsShape` 2,
   `GiftEvidenceShape` 1. Coverage is narrower than "12" suggests.
2. **Coverage is inverse to block size.** `application-verification` is the 12th-largest block (61
   checks) but holds half the compiled rules. The two largest blocks — Product Specific (589) and
   Property-Appraisal (584), together **35% of all checks** — have **zero**. Today's coverage reflects
   where the pilot started, not where the volume is.

> **Separately:** 28 shapes are authored in `src/shacl_pilot/blocks/*.ttl`, but only **4** are reachable
> from a rule via `eval_target`. So 24 authored shapes have no rule pointing at them. "Compiled" means
> *logic exists and a rule points at it* — not *wired end-to-end*.

---

## 5. Affirmative rows are not checks

Every block carries some rows with a **blank** Exception Code, severity, and description — 797 in
total. Reading their `Question Response`: 488 say "Not Applicable", the rest "Yes, all credit report
requirements were met" and similar. **769 of 797** begin "Yes…" or "Not Applicable".

These are the questionnaire's **compliant branch** — the answer a reviewer picks when nothing is wrong.
They assert no defect condition, so they are not checks and must not appear in an authoring pool as
gateless rows. Count them per block and exclude them.

`appraisal-form-1033` is the extreme case: **30 checks, 30 affirmative rows** — a 1:1 split, the
highest ratio of any block.

---

## 6. Severity mix per block

AMQ's `Default Significance`. Note the four non-standard values, which any severity enum must handle:

| Block | Critical | Major | Minor | Other |
|---|---:|---:|---:|---|
| `product-specific-check` | 558 | 29 | 1 | Note 1 |
| `property-appraisal-review` | 474 | 110 | — | — |
| `income-verification` | 483 | 32 | 1 | — |
| `underwriting-review` | 344 | 29 | 1 | — |
| `credit-liabilities-review` | 278 | 24 | — | — |
| `asset-verification` | 210 | 19 | — | — |
| `data-validation-services` | 136 | 1 | — | — |
| `insurance-review` | 120 | 8 | 5 | — |
| `closing-documents-review` | 99 | 25 | — | Material 1 |
| `loan-documents-review` | 104 | 5 | — | — |
| `information-integrity` | 77 | 1 | — | Critical-Pending SI 6 |
| `application-verification` | 24 | 33 | 4 | — |
| `certification-delivery` | 35 | 11 | 2 | — |
| `epd-review` | 31 | — | — | Note 3 |
| `appraisal-form-1033` | 30 | — | — | — |
| `compliance-review` | 14 | — | — | — |

**~90% of all checks are Critical**, so severity is a weak sort key — it barely discriminates.
`application-verification` is the one block where Major (33) outnumbers Critical (24).

The four non-standard values (`Material` 1, `Note` 4, `Critical-Pending SI` 6, and blank 797) are why
spec 019's FR-006 normalizes to `Critical`/`Major`/`Minor` while retaining `severityRaw`.

---

## 7. Which blocks appear in which routes

14 of 16 blocks appear in all five routes. Two do not:

- **`appraisal-form-1033`** — Fannie only (all 30 checks). Correct: a Fannie-specific form.
- **`data-validation-services`** — Fannie (46) and Freddie (91) only. Correct: DVS is a GSE service.

Full per-route matrix: `../README.md` §5.

Two further blocks are declared in `routes.json` as agency `extra_blocks` but hold **zero** rules —
`fha-compliance-check` and `va-eligibility-check`. See `../README.md` §6; do not render them as silent
blanks.

---

## 8. Reproducing every number here

```bash
cd /Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod
python3 - <<'PY'
import json, collections
r = json.load(open('src/shacl_pilot/compiled/ruleset.json'))['rules']
chk = [x for x in r if str(x.get('exception_code','')).strip()]
aff = [x for x in r if not str(x.get('exception_code','')).strip()]
bc, ac = collections.Counter(x['block'] for x in chk), collections.Counter(x['block'] for x in aff)
gc = collections.Counter(x['block'] for x in chk if x['eval_class'] == 'mapped')
cat = {x['block']: x['category'] for x in r}
for b, n in bc.most_common():
    print(f'{b:<28}{cat[b]:<42}{n:>5}{gc.get(b,0):>5}{ac.get(b,0):>6}')
print(f'{"TOTAL":<70}{sum(bc.values()):>5}{sum(gc.values()):>5}{sum(ac.values()):>6}')
PY
```

---

## 9. Caveats

- **Counts are the 3,369 defect checks**, not all 4,166 compiled rules (797 affirmative + 379
  `Discarded` make up the difference; a direct workbook read counts 3,370 because
  `amq_compiler.py:301` excludes one external-lookup rule).
- **`Discarded` is the 17th AMQ category** (379 rows, workbook-retired) and is excluded by design — so
  "17 categories" and "16 blocks" are both true statements about different sets.
- **A block's check count is not its coverage.** 13 of 16 blocks execute nothing today.
- **Post-Closing only.** Pre-Funding's 4,825 workbook rows have never been ingested.
- **Block ids are a third naming scheme.** `.ttl` files use short names (`application`),
  `ruleset.json`/`routes.json` use the long ids (`application-verification`), and the UI's
  `Block.name` is the AMQ category (`Application`). All three refer to the same thing; the mismatch is
  a known reconciliation item in spec 019.
