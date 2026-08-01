# SME Review Queue

Items requiring Kayla's mortgage-domain sign-off before production use (per
CLAUDE.md Known Blocker #2). Everything here is safe for demo/bake-off use
today under the individual-hand-verification bar already applied — this
queue is what still needs an actual SME's judgment before it can be trusted
unsupervised in production.

## check_type reclassifications (A0)

| card_id | exception_code | original check_type | proposed check_type | rationale |
|---|---|---|---|---|
| `PC::CIP DATA POINTS` | `CIP data points` | `doc_presence` | `cross_doc_consistency` | The question is presence-framed ("Are the 4 CIP data points provided in file?") but the actual defect ("have not been provided **or are inconsistent**") is checking whether name/address/DOB/SSN agree consistently across every document in the file that carries them — not whether any single document exists. See `output/NODATA-ROOT-CAUSE-ANALYSIS-2026-07-31.md` and `storage/rules/gold/data/compiled/application.json`'s updated `notes` field for full detail. |

## PURE_PRESENCE document-check wiring (from `A` sidecar, when built)

*(Empty for now — today's 3 wired checks (ICPL, Borrowers Authorization,
Hazard Insurance policy) were reviewed and confirmed correct by Gordon
directly during the 2026-07-31 session; logged here for visibility, not as
open items needing further action.)*

| card_id | exception_code | wired field | status |
|---|---|---|---|
| `PC::ICPL` | `ICPL` | `doc_present_closing_protection_letter` | wired, hand-verified 2026-07-31 |
| `PC::O-BP-14663` | `O-BP-54652` | `doc_present_borrowers_authorization` | wired, hand-verified 2026-07-31 |
| `PC::O-FNM-15436` | `HOICoverage` | `doc_present_hazard_insurance` | wired, hand-verified 2026-07-31 |

## Scope decisions NOT requiring SME review

For completeness — these are Gordon's deployment-scope calls, not mortgage-
domain judgments, so they do not need Kayla's sign-off, only documentation
of the reason (see `demo_exclusions.json` and `autopass_no_system_access.json`):
- 21 checks excluded from this demo build (`demo_exclusions.json`) — either
  require a system this project has no connection to (eMortgage tamper-
  evident security), or are Gordon's direct "not needed for this demo" calls.
- 66 checks auto-passed for this demo build because they require DU, EPIC,
  or Loan Delivery system access this project has no connection to
  (`autopass_no_system_access.json`) — output is indistinguishable from a
  real PASS, a deliberate, documented departure from this project's
  "never show a false clean" discipline, scoped to this demo only.
