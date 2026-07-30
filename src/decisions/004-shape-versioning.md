# 004 — SHACL shapes are versioned by content hash

**Status:** Accepted 2026-07-29 (Gordon)

## Decision
Every block shapes file is content-hashed (sha256). A `shapes_manifest.json` records
per-file hash + combined ruleset hash. Every audit run stamps the manifest hash it ran
under into its output. If an SME edits a shape, the hash changes, the manifest is
regenerated as a new version, and any two runs can be compared knowing exactly which
ruleset version produced each — the SHACL analog of the prod design's
`compiledRulesetSnippet` audit trail and the compile→validate→sign-off loop.

## Workflow when an SME changes a rule
1. Edit the block `.ttl` (later: via the friendly editor, see 006).
2. Regenerate manifest (`python3 shape_manifest.py update`) → new version entry with
   timestamp + per-block hash diff.
3. Re-run the gauge loan (loan 01) — accuracy must stay at baseline before the new
   version is used on real loans.
4. Runs record the manifest version, so results are always traceable to the exact
   shapes that produced them.

## Evidence
- `src/shacl_pilot/shape_manifest.py` — `update` / `verify` commands, per-file sha256 + combined ruleset hash.
- `src/shacl_pilot/shapes_manifest.json` — 5 recorded versions; v1→v2 shows an SME edit to `blocks/closing.ttl` (only that file's hash changed), v3 is the revert with a combined hash **identical to v1** (`f1924ddee30d…`), demonstrating content-addressing round-trip.
- `src/shacl_pilot/shapes_manifest.json` v4 (routes.json change, decision 011) and v5 (`blocks/assets.ttl` guide-citation edit, decision 012, combined hash `696832b1efad…`).
- `src/shacl_pilot/run_audit.py` — run output stamps "Ruleset sha … + shapes version N (hash…) recorded for audit trail."
