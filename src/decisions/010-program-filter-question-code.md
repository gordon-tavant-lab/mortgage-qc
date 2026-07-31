# 010 — Program applicability is filtered by Question Code agency prefix

**Status:** Accepted 2026-07-29 (Gordon)

## Decision
Each loan's program/agency is read from its own documents (1003 "Loan Program" line,
MISMO MortgageType as fallback): Fannie Mae → `O-FNM`, FHA → `O-FHA`, VA → `O-VA`,
Freddie Mac → `O-FRD`, USDA → `O-RHS`. A loan runs:

- rules whose Question Code starts with its own agency prefix, PLUS
- all GENERIC rules — codes with no agency prefix (`O-CFPB-*`, `O-CNTL-*`, `O-BP-*`,
  `O-EPD-*`, DVS/URLA/portfolio codes, etc.)

and EXCLUDES the other four agencies' rules. Example: a VA loan runs `O-VA-*` +
generic (689 rules) and excludes `O-FNM-*`, `O-FHA-*`, `O-FRD-*`, `O-RHS-*` (3,478).

## Applicable rule counts (compiled ruleset v. sha 2816f114)
| Program | agency rules | + generic | = runs |
|---|---|---|---|
| Fannie Mae (O-FNM) | 1,108 | 244 | 1,352 |
| Freddie Mac (O-FRD) | 1,141 | 244 | 1,385 |
| FHA (O-FHA) | 716 | 244 | 960 |
| USDA (O-RHS) | 513 | 244 | 757 |
| VA (O-VA) | 445 | 244 | 689 |

## Why prefix, not the SQL criteria column
The workbook's `Question Criteria` SQL (`WHERE Loans.QC_Policy = 'FHA'`) encodes the
same fact; the code prefix is the cleaner deterministic key and matches how Gordon
reads the sheet. The criteria column stays available for a Layer-2 compile pass to
extract finer preconditions (occupancy, purpose, product) later.
