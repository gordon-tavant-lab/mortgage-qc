#!/usr/bin/env bash
# verify-no-leaks.sh — spec 020 (Touchless API Integration), T037.
#
# Automates two checks that were previously only ever run once, by hand, during the Phase 8
# review (see specs/020-touchless-api-integration/security-review.md "Phase 8 Re-Verification"
# and tasks.md T019/T037):
#
#   1. Credential-leak sweep (SC-005): no Touchless credential string, and no VITE_-prefixed
#      Touchless reference, may appear anywhere in frontend/src or a built dist/ bundle.
#   2. FR-010 zero-regression sweep: this feature's diff must never touch p0/qc_engine,
#      CheckResult, or LoanEvaluation — pulled/retrieved Touchless data is display/citation-only.
#
# Exits non-zero (and prints exactly what matched) on any hit, so this is safe to wire into CI
# or run before a demo, rather than relying on someone remembering to re-run a manual grep.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi
cd "$REPO_ROOT"

fail=0

echo "== [1/2] Credential-leak sweep (SC-005) =="

# Pull the real credential values out of backend/.env so this check verifies against whatever
# secret is ACTUALLY configured locally, not a value hardcoded into this script.
CLIENT_ID=""
CLIENT_SECRET=""
if [ -f backend/.env ]; then
  CLIENT_ID="$(grep -E '^TOUCHLESS_CLIENT_ID=' backend/.env | cut -d= -f2- || true)"
  CLIENT_SECRET="$(grep -E '^TOUCHLESS_CLIENT_SECRET=' backend/.env | cut -d= -f2- || true)"
fi

SCAN_PATHS=(frontend/src)
[ -d frontend/dist ] && SCAN_PATHS+=(frontend/dist)
[ -d backend/dist ] && SCAN_PATHS+=(backend/dist)

if grep -rn "VITE_" "${SCAN_PATHS[@]}" 2>/dev/null | grep -iE "touchless|client_secret|client_id|bearer"; then
  echo "FAIL: found a VITE_-prefixed Touchless/credential reference above — must not exist client-side."
  fail=1
fi

if [ -n "$CLIENT_SECRET" ] && grep -rn -- "$CLIENT_SECRET" "${SCAN_PATHS[@]}" 2>/dev/null; then
  echo "FAIL: the real TOUCHLESS_CLIENT_SECRET value was found in a client-facing path above."
  fail=1
fi

if [ -n "$CLIENT_ID" ] && grep -rn -- "$CLIENT_ID" "${SCAN_PATHS[@]}" 2>/dev/null; then
  echo "FAIL: the real TOUCHLESS_CLIENT_ID value was found in a client-facing path above."
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "PASS: no credential/VITE_ leak found in ${SCAN_PATHS[*]}."
fi

echo
echo "== [2/2] FR-010 zero-regression sweep (no QC-engine wiring) =="
echo "   Scoped to this feature's actual changes (git-tracked, not the whole pre-existing"
echo "   codebase, which already legitimately mirrors p0/qc_engine's types -- e.g."
echo "   frontend/src/lib/types.ts, ApplyView.tsx, mockData.ts predate spec 020)."

engine_hit=0
ENGINE_PATTERN="p0/qc_engine|CheckResult|LoanEvaluation"

# New, untracked files this feature added (backend/ entirely, plus the new frontend/src
# files) get a full-content check -- there is no legitimate pre-existing reference to
# exempt, since none of this content existed before spec 020.
# Scoped to actual application source (backend/src, frontend/src) -- deliberately excludes
# backend/README.md and this script's own comments, which discuss the FR-010 constraint in
# prose without violating it (a pure grep can't tell "describes the rule" from "breaks it").
UNTRACKED_FILES=()
while IFS= read -r f; do
  UNTRACKED_FILES+=("$f")
done < <(git ls-files --others --exclude-standard -- backend/src frontend/src 2>/dev/null || true)

if [ "${#UNTRACKED_FILES[@]}" -gt 0 ]; then
  if grep -nE "$ENGINE_PATTERN" "${UNTRACKED_FILES[@]}" 2>/dev/null; then
    echo "FAIL: a new file this feature added references the QC engine (above)."
    engine_hit=1
  fi
fi

# Pre-existing, git-tracked files this feature MODIFIED only get checked on their ADDED
# lines (the diff), since the file itself may already legitimately reference the engine
# from before spec 020 existed.
if git diff --unified=0 -- frontend/src backend/src 2>/dev/null | grep -E "^\+[^+]" | grep -E "$ENGINE_PATTERN"; then
  echo "FAIL: a line added to an existing file references the QC engine (above)."
  engine_hit=1
fi

if [ "$engine_hit" -eq 0 ]; then
  echo "PASS: no new or newly-added reference to p0/qc_engine, CheckResult, or LoanEvaluation."
else
  echo "This feature must stay display/citation-only per spec 020 FR-010 / CLAUDE.md Non-Negotiable #1."
  fail=1
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "verify-no-leaks: FAILED — see above."
  exit 1
fi
echo "verify-no-leaks: all checks passed."
