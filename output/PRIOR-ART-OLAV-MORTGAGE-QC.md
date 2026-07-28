# Prior Art Audit: Olav's `mortgage-qc` (Runtime-LLM POC)

| | |
|---|---|
| **Run via** | `/g-os-metacognition` — contrarian-led ("what am I not seeing?"), two Explore agents |
| **Date** | 2026-07-01 |
| **Subject** | `examples/mortgage-qc/` — confirmed real, deployed, GitLab-hosted system (`gitlab.tavant.com:gordon.chan/mortgage-qc.git`), production commit history through 2026-06 |
| **Provenance** | Originated as **Olav's LLM-at-runtime POC** — the exact counterpoint architecture THESIS.md and `.specify/memory/constitution.md` Principle I/II are written against — but `git shortlog` confirms Gordon authored 77 of the repo's 79 commits (2 are Olav's original seed). This is Gordon's own forked/extended build, deployed live at `mortgage-qc.loopinhuman.com` (corrected 2026-07-15, see [[project_mortgage_qc_prod]]) — not a third-party artifact under passive review. Not a toy either way — it has a working `agent-gateway`, 9 mock system services, a cockpit UI, 11 spec-kit specs, and 14 logged production issues. |
| **Question** | What's already proven here that this project (`mortgage-qc-prod`) can reuse, and does that change any of the 3 specs already written (`001a`, `001b`, `002a`)? |

> **Scope note**: nothing here contradicts anything already built. This audit adds *evidence and prior art*, not corrections. Treat this as strengthening, not revising.

---

## The single most valuable finding: prompts cannot fix structural data conflicts

Issue `013-appraisal-false-positives-human-review.md` and spec `010-qc-accuracy-fixes` document a real,
repeated production failure: Olav's mock system services (appraisal, credit, etc.) returned data that
conflicted with the actual extracted PDF (e.g. mock GLA = 2,400 sf vs. extracted PDF = 3,639 sf). The
LLM correctly detected the mismatch and flagged it — but the mismatch was **fake**, an artifact of two
data sources that should have been the same thing but weren't. The team tried to fix this with prompt
engineering (tell the agent which source to trust) and it **failed** — LLM non-determinism meant the
same loan produced different, sometimes-wrong findings across runs. The team's own conclusion,
verbatim from the investigation: prompting cannot reliably fix this; the fix has to be structural
(eliminate the conflict at the data layer, not paper over it at inference time).

**This is independent, real-world corroboration of `mortgage-qc-prod`'s Principle V (source
independence) and of `001b`'s research.md decision #2** (source independence is a test-construction
discipline because production data doesn't have this problem — genuinely different systems are
independent by construction; the risk lives in how test/mock data is built). Olav's mocks are exactly
the failure mode that decision predicts: badly-constructed "independent" sources that quietly aren't.

**This is also a second, independent empirical data point for Principle I** (determinism), alongside the
G3 bake-off. Issue `011-finding-count-inflation-regression.md` shows the same loan producing 2 → 5 → 8 →
13 findings across identical runs — a lived instance of exactly the "same loan, different verdict" risk
Principle I exists to eliminate, from a different team's real deployment, not a controlled experiment.

**Recommendation**: THESIS.md and `constitution.md` currently cite only the G3 bake-off as evidence.
Worth considering a citation to this issue log as a second, independent corroboration — a real
production system hitting exactly the failure modes the thesis predicts, not a controlled comparison.
This is a call for Gordon, not something to amend unilaterally (constitution amendments need a stated
rationale + version bump per its own governance section).

---

## Second most valuable finding: silent schema violations cause catastrophic data loss

Issue `012-property-check-output-not-parsed-by-merge.md` (marked CRITICAL): a block returned
unstructured prose (`{"response": "..."}`) instead of the required `{"exceptions": [...]}` schema, and
the merge step **silently dropped every property finding** — no error, no warning, just missing data.
Combined with issue `014` (citations always pointed at the same 2 pages until the block was made to
emit `evidence.page_references` directly, rather than reconstructing citations after the fact), the
pattern is: **anything not enforced as a schema at the point of emission gets silently lost or
wrong** — never caught until a human notices the output looks off.

This directly validates `001a-field-catalog`'s central design bet: the SAFE gate (referential integrity
validated at load time, failing loudly) exists for exactly this failure class. Olav's system had no
equivalent gate at the block-output layer, and paid for it in lost findings. Worth citing as evidence
for *why* 001a's "never a silent no-op" design (already implemented) was the right call — not a design
change, a confirmation.

---

## Reusable prior art, by roadmap feature

| Feature | Status | What to take from Olav's system |
|---|---|---|
| **`001a-field-catalog`** | implemented | `config/qc_questions.json` + `config/block_questions.json` are a real, lender-curated question/exception-code vocabulary derived from the **same AMQ workbooks** `taxonomy.py` parses (`PF and PC Sept 2025 AMQs - Retail.xlsx`, `Private Bank Oct 2025...`). Not a reason to change what's built (the 7-field seed catalog is still correct) — but a candidate **additional grounding source** when scaling the catalog toward the full 800+ checks, alongside `taxonomy.json`'s archetype classification (which serves a different purpose: synthetic eval generation, not the real vocabulary itself). |
| **`001b-source-envelope-and-inbound-contracts`** | planned | Issue 013's "prompts can't fix structural conflicts" finding is direct corroborating evidence for research.md decision #2 (added as a citation, see below). The `systems/*` mock adapters (appraisal, credit, docvault, employment, flood, investor, los, title) show a real, working "loan_number → {source data}" envelope shape — a decent reference for what real inbound sources look like, though these are mocks, not a production connector pattern to copy wholesale. |
| **`002a-compile-fidelity-spike`** | specced+planned, pending Kayla's review | `qc_questions.json`/`block_questions.json` are a curated, per-block-organized question set — a stronger candidate compile-input than raw workbook rows for a *future* round or for `002b`'s eventual design (structured input reduces the LLM's parsing burden vs. raw spreadsheet text). Does not change this spike's already-locked pre-registration or its 24-row result. |
| **`004-loan-disposition`** (unspecced) | — | Issues 008 (duplicate exception codes) and 009 (phantom findings for absent documents) are concrete precondition rules a disposition layer should enforce: dedup by exception_code before composing a verdict; validate the cited document actually exists in the extracted set before a finding counts. |
| **`006-confidence-gated-auto-clear`** (unspecced) | — | Issue 012 is the cautionary case: enforce output schema at the point of generation (e.g. Bedrock's structured-output constraints), never parse-and-hope after the fact. |
| **`007-audit-trail-and-citation-of-record`** (unspecced) | — | Issue 014 (now fixed in Olav's system): citations must be emitted by the check/block itself at finding-generation time (`evidence.page_references`), never reconstructed afterward via heuristic section-to-document mapping. Design `007`'s per-finding audit record to require this field from the start. |
| **`008-exception-queue-and-clear-next`** (unspecced) | — | Olav's `specs/005-review-center-ux` is real, validated UX for this exact surface: severity-grouped findings (Critical → Major → Minor → Passed, each collapsed by default), collapsible extraction-sources section (don't push findings below the fold with a long document list), and — notably — showing **passed** checks alongside exceptions for audit-trail completeness. **Plus a working implementation**: `cockpit/frontend/src/components/ConfirmationCard.jsx` — a real, deployed human-in-the-loop review component (briefing text, proposed-actions list, impact summary, recommendation, Approve/Reject buttons, expandable technical details). See "Reusable Implementation Assets" below for the reuse caveat (design-language mismatch). |
| **`009a/009b` (authoring UI, unspecced)** | — | The routes/blocks/checks YAML schema (`routes/*.route.yaml`, `blocks/*.block.yaml`) is production-validated: routes define a DAG of block executions (fan-out/fan-in), blocks carry question→response→exception-code tables with a `CRITERIA` field for SQL-style gating. Strong template for what the authoring surface should let an SME configure, once `009` is specced — the *shape* is proven even though Olav's *execution* (LLM-at-runtime per block) is the opposite bet from this project's compiled engine. |
| **`010a-program-applicability-gating`** (renamed from `010a-honor-encoded-sql-gating`; unspecced) | — | Olav's blocks' `CRITERIA: SELECT ... WHERE (Loans.QC_Policy = 'Freddie Mac')` fields are very likely the same underlying SQL gating clauses `taxonomy.json` already extracts and excludes (615 rows). Independent confirmation that "honor the sheet's existing SQL gates rather than re-deriving them" is a pattern someone else already validated works in production — **but per `output/RULE-PROGRAM-GATING-FINDINGS.md` (2026-07-20), this SQL-clause pattern is 010a's *secondary* mechanism, not its primary one; the Exception Code prefix (`O-FHA-`/`O-VA-`/`O-RHS-`/`O-FRD-`/`O-FNM-`, 79% of real rows) is the primary program signal and has no known analog in Olav's system.** |

---

## Reusable Implementation Assets (concrete files, not just lessons)

A second investigation pass (2026-07-01) looked specifically for files that could be copied or lightly
adapted, not just patterns to learn from. Two categories stand out:

### Deploy infrastructure — highest-confidence reuse; this project has no deploy setup yet at all

| Asset | Path | Verdict |
|---|---|---|
| Sablier scale-to-zero (Caddy + Sablier) | `deploy/Caddyfile.sablier`, `deploy/docker-compose.sablier.yml` | **Directly reusable.** Confirmed genuine, working: Caddy reverse-proxies, Sablier stops/wakes the container group on a 30m idle timeout with a loading page while it wakes. This is the same pattern already used elsewhere in the workspace — copy the syntax, swap the group name/ports/service name. |
| 6-point post-deploy healthcheck | `deploy/healthcheck.sh` | **Directly reusable.** Generic verification pattern: containers up + not restarting, app-level `/health`, import integrity, public API end-to-end 200s, expected data actually loaded, no stale-upstream-IP errors in logs. Swap container name prefixes and the module/endpoint list. |
| S3 → SSM → EC2 deploy workflow | `deploy/deploy.sh` | **Reusable, adapt the specifics.** Tar to S3, `aws ssm send-command` to the target instance, unpack + `docker-compose up` + healthcheck. Change instance ID, bucket, profile, env path. |
| OOM safety via `mem_limit` | `deploy/docker-compose.prod.yml` (gateway service, 2G cap) | **Copy the pattern.** A large-PDF extraction fan-out crashing the host is exactly the failure class `mem_limit` guards against — relevant the moment this project's engine runs behind any long-lived service. |
| Operational runbook conventions | `deploy/RUNBOOK.md` | **Reusable structure.** "Healthcheck gates every deploy" and "frontend restart is mandatory after backend redeploy (stale upstream DNS)" are both concrete, hard-won rules worth adopting verbatim as house rules once this project deploys anything. |

### Frontend — one real component, one real design-language conflict to flag

`cockpit/frontend/src/components/ConfirmationCard.jsx` is a real, deployed HITL review component:
briefing text, a proposed-actions list, an impact-summary bar, a recommendation line, Approve/Reject
buttons, and an expandable raw-JSON technical-detail view. Its **data model** (briefing, proposed
actions with `details`/`affected_items`, impact summary, recommendation) is a strong, validated shape
for `008`'s exception-review card.

**The catch, worth flagging rather than silently resolving:** this cockpit uses React 18 + Vite 5 +
inline styles (a dark slate/blue terminal aesthetic) — a **different** stack and visual language from
`examples/mortgage-qa_qc-tool/`, the AI-Studio prototype `CLAUDE.md` already designates as this
project's front-end design-language reference (React 19, Vite 6, Tailwind v4, Inter/Space
Grotesk/JetBrains Mono, slate-50 canvas). **Recommendation, not yet a decision:** when `008` is
specced, reuse ConfirmationCard's *interaction/data model* (what fields a review card needs, the
approve/reject/expand-details flow) and rebuild it in the AI-Studio prototype's actual design system —
don't port the JSX/styling verbatim, since `CLAUDE.md`'s existing convention should govern the look.

Session-scoped WebSocket routing (`cockpit/backend/src/main.py`, query-param session scoping + Redis
loan→session bindings, plus rehydration-on-reconnect so a refresh doesn't show a blank UI mid-extraction)
is a generic, reusable pattern **if and when** `008`'s eventual architecture needs live updates over a
socket — not required by anything currently specced, but worth knowing exists.

## What is explicitly NOT reusable

The `agent-gateway` (`agent-gateway/src/agent_invoker.py`) is a confirmed runtime-LLM evaluator —
every block step calls Bedrock at evaluation time, tool-use loops to a decision. This is the literal
architecture Principle I/II exist to reject for the deterministic core. Its retry/semaphore/throttling
handling (issue 006) is a real operational lesson worth knowing about *if* `002b`'s config-time compiler
ever needs its own Bedrock resilience — but the architecture itself is not something to adopt.

## Bottom line

**PROCEED-WITH-GUARDRAILS.** Two distinct kinds of value here, both purely additive: **evidence**
(Olav's team already ran the experiment this project's thesis predicts — prompt-only fixes fail on
structural data conflicts — and hit the wall empirically; independent corroboration, cited in `001b`)
and **implementation assets** (a genuine Sablier scale-to-zero deploy stack, a 6-point healthcheck
script, and a real HITL review component this project has nothing equivalent to yet). Nothing requires
reopening `001a` (already implemented, zero regression) or `002a` (pre-registration stays locked). The
highest-leverage unclaimed value is in features not yet specced (`004`, `006`, `007`, `008`, `009a/b`,
`010a`) and in deploy infrastructure this project hasn't built at all — each now has a concrete,
production-tested reference point instead of a blank page.
