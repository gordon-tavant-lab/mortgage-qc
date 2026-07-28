# Foundation Readiness Audit — Before Speccing

| | |
|---|---|
| **Run via** | `g-dev-build` → Phase 0 (IDEATE) + Intent Lock Checkpoint, applied to the whole foundation |
| **Date** | 2026-06-30 (re-verified same day, second pass) |
| **Question** | Is the foundation solid enough to start speccing features (`/speckit-specify`)? |
| **Verdict** | **READY.** GAP 3 (hygiene) is now closed. GAP 1 (contracts) and GAP 2 (criteria) remain — both are spec-time deliverables, not pre-spec blockers. One new minor finding (provenance of a cost figure) added below. |

## Addendum — second-pass re-verification (same day)

A second, independent pass: full re-read of `THESIS.md` (214 lines) and `ROADMAP.md`
(366 lines) end-to-end, a directory survey of the whole project, and — critically —
**re-running the code instead of re-reading the claims about it**:

| Check | Re-run result |
|---|---|
| `p0/tests/test_p0.py` | **19 passed** (fresh run) |
| `p0/eval_synth/test_properties.py` | **7 passed** (fresh run) |
| `p0/eval_synth/eval.py 3000` | **24,000/24,000 exact, 0 false-auto-clears, PASSED** (fresh run, new artifact `synth_eval_audit_verify.json`) — confirms the figure cited below, not just in this doc |
| `p0/harness.py` (1000-run bit-exact) | **byte-identical digest across 1000 runs**, confirmed; precision=1.0 recall=1.0 on golden set; sign-off integrity reported (8 rules, 3 edited, mean edit-distance 3.38) |
| `taxonomy.json` cross-check | confirmed **7,398** total conditions, **4,192** classified (56.7%), **615** SQL gating rows excluded — matches the roadmap's cited numbers exactly, traceable to the real AMQ workbooks in `demo/rules/*.xlsx` |
| `.specify/specs/` | still does not exist — confirms no feature has been specced yet |
| GAP 3 (stray Gordon-OS files) | **closed** — `PORTFOLIO.md`/`goal-weights.yaml` removed from project root, `demo/`, `p0/`, `p0/experiment_g3/` (2 of 7 were tracked, removed via `git rm`). Note: a SessionStart hook auto-regenerates the root-level template files on next session start — this is workspace-level automation outside this project's control; harmless but will need re-clearing or a `.gitignore` entry if it recurs. |

### New minor finding — a cost figure's precision outruns its source
THESIS.md (Point 3, "Empirical update") cites a specific extrapolated range —
**"Sonnet realistically $700–$3,500/10k-run"** for real-extraction-scale payloads —
attributed to the G3 bake-off. Checked `p0/experiment_g3/RESULTS.md` and
`PRE-REGISTRATION.md` directly: the **measured** figures there are $27–$70/10k-run
on the ~1.1K-token synthetic payload (Bedrock-verified, real). The **10–50× real-
extraction multiplier** that produces $700–$3,500 is **not computed or cited
anywhere in the experiment files** — it's a reasoned but unverified back-of-envelope
applied only in THESIS.md. Not a fabrication (the logic — real Touchless payloads
carry far more tokens than a synthetic 1.1K-token test — is sound), but a specific-
looking number that isn't yet load-bearing evidence. **Low severity, doesn't block
001a/002a**, but: don't cite "$700–$3,500" as measured in client-facing material:
say "directionally, real payloads likely cost an order of magnitude more — the
real number is unmeasured until 002a runs against the actual AMQ workbook."

> Scope note: this is a *foundation-readiness audit*, not a feature build. Running the full
> 12-phase team-lead lifecycle here would itself violate Principle IV. So `g-dev-build` routed to
> Phase 0 + the Intent Lock Checkpoint — verify the foundation, name the gaps, sequence the specs.

---

## What was verified (not assumed)

The roadmap cites P0 + synthetic eval as **DONE foundation**. A foundation is only valid if it
*actually passes today* — so it was re-run, not trusted:

| Check | Result |
|---|---|
| P0 determinism harness (1000-run bit-exact + labeled eval + sign-off) | **PASSED ✓** |
| P0 unit tests (`tests/test_p0.py`) | **19 passed** |
| eval_synth property/metamorphic tests | **7 passed** |
| Synthetic eval gate (3,000 loans) | **24,000/24,000 exact, 0 false-auto-clears ✓** |
| Spec Kit mechanism (scripts executable, 6 templates present) | **intact** |
| Constitution v1.1.0 (7 principles, 4 NON-NEGOTIABLE) | **present, internally consistent** |
| Source material (`docs/transcript.md`, `summary.md`, `authoring-examples.md`) | **present** |
| Governing docs (THESIS, PRD, ROADMAP v0.5, AUTHORING-UX-DECISION) | **present, cross-referenced** |

**Conclusion:** the "DONE" claims are real, green, and reproducible. The proof-driven foundation
(determinism + eval-by-construction + the G3 architecture decision) is the strongest possible base
to spec against — most projects spec on assumptions; this one specs on a proven engine.

---

## Intent Lock Checkpoint — the gaps

The lifecycle's Intent Lock Checkpoint requires three artifacts before *any* feature implementation:
**spec, contract, criteria.** Against the foundation as a whole:

| Artifact | State | Gap |
|---|---|---|
| **Spec** | constitution + roadmap + PRD + authoring decision all exist | ✅ richer than most projects ever get |
| **Contract** | no `contracts/` dir; the **Touchless inbound contract** + **LOS/MISMO contract** + **field-catalog schema** are described in prose (001a/001b) but not pinned as schemas | ⚠️ **GAP 1** |
| **Criteria** | no `criteria.md`; executable pass/fail gates exist *in code* for the foundation (harness.py, eval.py) but are not yet expressed as per-feature acceptance assertions | ⚠️ **GAP 2** |

Plus one hygiene gap found in the scan:

- ✅ **GAP 3 — stray workspace artifacts in the project. CLOSED.** 7 Gordon-OS bootstrap template files (`PORTFOLIO.md` / `goal-weights.yaml` at project root, `demo/`, `p0/`, `p0/experiment_g3/`) removed. 2 were tracked in git (`p0/experiment_g3/`'s copies) and staged for removal via `git rm`; not yet committed.

### None of these block `001a`. All three should be closed before a clean full-arc run.

- **GAP 1 (contracts)** matters most for **001b** (the inbound contracts) and **002b** (what the
  compiler emits) — not for 001a (the field catalog is internal). Close it as part of speccing
  001a/001b, where `/speckit-plan` produces the schemas into a `contracts/` dir.
- **GAP 2 (criteria)** is partly already solved: the **zero-false-auto-clear gate** and the
  **bit-exact harness** are reusable, executable criteria the foundation already ships. Each
  feature spec should reference them and add its archetype-specific assertions. This is a
  per-spec activity, not a pre-spec blocker.
- **GAP 3 (hygiene)** is a 2-minute cleanup, do it now.

---

## Readiness scorecard

| Dimension | Score | Note |
|---|---|---|
| Proven foundation | ★★★★★ | green, reproducible, not aspirational |
| Governing docs (constitution/thesis/roadmap) | ★★★★★ | unusually complete; survived adversarial review |
| Dependency-ordered arc | ★★★★★ | 19 features, no cycles, numbering = order |
| Tensions surfaced | ★★★★★ | 8 named, RED/AMBER tagged, owners implied |
| Spec mechanism (Spec Kit) | ★★★★★ | initialized, scripts + templates intact |
| Contracts pinned as schemas | ★★☆☆☆ | **GAP 1** — prose, not schemas yet |
| Executable per-feature criteria | ★★★☆☆ | **GAP 2** — foundation gates exist; per-feature TBD |
| Project hygiene | ★★★★★ | **GAP 3 closed** — stray workspace templates removed |

---

## Recommended spec sequence (the foundation's payoff)

The arc already encodes this; stated as an execution order for `/speckit-specify`:

1. **`001a-field-catalog`** — START HERE. Zero open tensions, the engine's true prerequisite, scope
   validated by the adversarial review. The cleanest possible first spec.
2. **`002a-compile-fidelity-spike`** — in parallel or right after. It is the **highest-risk
   irreversible item** (Tension 6) and uses the already-built `eval_synth` scorer — so it can be
   specced and run early to de-risk the whole compile bet *before* 002b is committed.
3. **`001b`** → **`002b`** → **`003a/b/c`** → **`004`** → **`005`** … per the roadmap's dependency
   order. Contracts (GAP 1) get pinned during 001b/002b planning.

**Gate before speccing:** close GAP 3 (hygiene) now; carry GAP 1 + GAP 2 into the 001a/002a specs
(they are spec-time deliverables, not pre-spec blockers).

---

## The one-line verdict

> **Spec it.** The foundation is proven — twice now, having been re-run independently rather than
> trusted — the constitution is sound, the arc is dependency-clean, and the tensions are named.
> Hygiene is clean. Start with `001a` + `002a`, let `/speckit-plan` pin the contracts and criteria
> as each feature is specced, and when citing 002a's economic case, say "directionally an order of
> magnitude more, unmeasured until the real workbook runs through it" rather than the specific
> $700–$3,500 figure. This is a stronger starting position than the vast majority of projects ever
> reach.
