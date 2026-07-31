# 016 — Bucket C: discard the NMLS-registry-lookup rule from PoC/demo scope

**Status:** Accepted 2026-07-29 (Gordon — "discard this rule from the PoC/demo scope
entirely", re: rules needing a data source outside any loan document)

## Decision
1 of the 16 YELLOW groups — **group 45** — is explicitly **removed from active PoC/demo
scope**: not compiled, not tracked as YELLOW or RED, excluded from this exercise's
headline triage percentages. It is the only one of the 16 whose blocker is a **live
external system lookup**, not a document the loan file could ever contain.

## The rule
Group 45, source row 68, condition: "The loan originator identified on the URLA was not
the actual licensed loan originator for the loan" (`O-FHA-15141`). The CSV's exception
description (row 68) reads: "The loan application did not contain the loan originator's
name, Nationwide Mortgage Licensing System and Registry (NMLS) identification number,
telephone number, and signature." Verified this is genuinely an NMLS-registry check, not
a document-presence check in disguise: the **condition** (question response text) asks
whether the *identified* originator was the *actual licensed* originator — i.e. whether
the NMLS ID on the URLA is valid and truly belongs to the person who originated this loan.
That is a claim about an external registry's state (is this ID currently licensed, does
it match this individual), not a fact the loan document alone can settle by rereading its
own text — no loan file, however complete, can self-certify that its own originator ID
is authentic. Confirmed no such lookup capability, cached registry snapshot, or NMLS data
file exists anywhere in `src/` or `demo/syn/`.

## Why this is out of scope (not RED, not YELLOW)
- **RED** means a human reviewer resolves it using judgment about the *existing* file.
  There is no judgment call here a human reviewer could make from the file alone either —
  they'd have to go look the ID up in the same external registry.
- **YELLOW** (as originally triaged) implied "deterministic once the external data
  source is wired" — true, but "wiring an external data source" is a fundamentally
  different kind of work than document extraction: it's a live third-party system
  integration (NMLS Consumer Access / registry API), with its own auth, rate limits,
  data-freshness, and uptime dependencies — outside this pilot's "document extraction +
  cross-source reconciliation" mandate (see top-level CLAUDE.md non-negotiable #3: three
  *document/system-of-record* sources, reconciled — not a fourth, live regulatory
  registry).
- Discarding it prevents the headline "16 YELLOW groups, X automatable" count from
  quietly implying this pilot can do NMLS verification when it categorically cannot yet.

## What we will do
- Group 45 is dropped from the active triage count for this bucket-resolution exercise:
  the corrected total is **12 Bucket A + 3 Bucket B = 15 actionable-or-deferred groups**,
  with group 45 called out separately as **out of scope**, not silently folded into
  either bucket's denominator.
- Not compiled into `ruleset.json`/`triage_application_verification.json` by this
  decision (no `.json`/`.py` edits performed here — that remains for the human
  follow-on).
- Revisit as a **distinct future integration decision** if/when this project takes on
  live external-system lookups as a category (NMLS registry, CAIVRS/LDP-GSA/GSA
  exclusion lists already exist as static per-loan documents in `demo/syn/loan 02`'s
  `05_CAIVRS_LDP_GSA.pdf` and are handled as ordinary document presence — group 45 is
  different in kind because it needs a live, current-as-of-today lookup, not a
  point-in-time screenshot document).

## Cross-links
[[009]] (full-workbook compile — this is one applicable rule being explicitly excluded,
not silently left `unmapped`), [[014]] (sibling Bucket A decision), [[015]] (sibling
Bucket B decision).
