# PRD — Mortgage Post-Closing QA/QC System

| | |
|---|---|
| **Version** | 0.1 |
| **Date** | 2026-06-26 |
| **Author** | Product (via grilled decisions) |
| **Status** | DRAFT for review |
| **Reviewers** | Architect (next handoff), Eval owner (TBD), VP/CCO sponsor (TBD), Kayla (SME) |

> **What this doc owns:** the problem, the users, the positioning, the scope, the
> metrics, and the sequencing. It does **not** specify data models, APIs, or EARS
> technical acceptance criteria — those are the architect's. Where a claim is
> already demonstrated, it is cited as **[P0]** (the working determinism proof in
> `p0/`).

---

## 1. Problem & Opportunity

### The job-to-be-done
A QC analyst at a mortgage lender needs to **prove that every closed loan was QC'd
correctly and defensibly** — auto-clearing the obvious, isolating the real
exceptions — so the lender **shrinks its loan-buyback exposure and survives a
regulatory or investor audit.**

Today this is manual: a funded, closed loan comes back from the title company as a
blob of hundreds of signed, dated PDFs (the **source of truth**). An analyst opens
it next to the lender's loan data and does stare-and-compare against 800+ checks on
a spreadsheet. It is slow, judgment-heavy, inconsistent analyst-to-analyst, and —
critically — **not provable to a regulator.**

### Why this is worth funding (the two business hires)
The product is hired for two distinct outcomes. Both must be true; one without the
other is not a product:

1. **Throughput** — auto-clear the loans the machine can decide so analysts spend
   their time only on true human-judgment exceptions. *"I'm done with this loan.
   Next one, next one, next one."*
2. **Defensibility** — every decision is deterministic, cited to a document page,
   and replayable. *"If they don't understand how you calculated that number, you
   buy back the loan."*

### The buyback / audit pain (the money)
- A repurchased loan costs the lender **~$32K on average** (Stratmor/Reggora,
  2023–24; repurchase rate ~0.49%), with **total economic loss exceeding $100K**
  on some loans. Use **~$32K as the defensible anchor**, $100K+ as the upside —
  *not* a bare "$40K+." Validate against the design partner's own buyback data.
- A confidently-wrong auto-clear is the single most expensive failure mode: it puts
  a defective loan on the books and is invisible until the investor or regulator
  finds it. This is why **false-auto-clear rate is the hard gate** (§6).

### Market context & why now
- **Primary competitor is manual review** (spreadsheet + stare-and-compare), not
  software. We win on speed *and* trust, not on feature breadth.
- **Secondary competitors are established QC platforms** (ACES, LoanLogics/ICE,
  Indecomm). Characterize them accurately: **ACES** is workflow / sampling /
  defect-tracking / GSE reporting. **LoanLogics (IDEA + LoanHD) and Indecomm
  (IDXGenius + AuditGenius) genuinely do document extraction *and* automated
  defect detection / QC** — they are closer to our core than ACES. Our wedge is
  **not** "they don't automate QC"; it is **deterministic, byte-identical,
  audit-replayable doc-vs-system reconciliation bound to a signed, SME-validated
  ruleset** — a thing none of them ship today (§3).
- **Why now:** AI can finally read a closing document well enough to QC against it
  (via the upstream extraction partner), and regulators/investors are tightening
  audit expectations. The opening is to be the engine that is *both* AI-fast *and*
  audit-defensible — which an LLM-at-runtime tool cannot credibly claim.

---

## 2. Target Users & Buyer

Dual-persona. We sell to the **buyer** on risk and budget; we win the **user's**
heart with UX. Both must be served or the deal stalls.

### Economic buyer — "the VP"
| | |
|---|---|
| **Title** | VP of QC / Chief Compliance Officer |
| **Owns** | Buyback risk, audit defensibility, the QC budget |
| **Wins when** | Repurchase exposure drops and they can hand an examiner a clean, replayable trail |
| **Fears** | A confidently-wrong auto-clear; an examiner asking "show me the math" and getting an opaque AI shrug |
| **Buys on** | Repurchase-risk reduction + audit defensibility — *not* on UI elegance |

### User / champion — "Kayla" (QC Analyst / SME)
| | |
|---|---|
| **Title** | Senior QC Analyst / subject-matter expert |
| **Owns** | The 800-check interpretation; the loan-by-loan disposition |
| **Wins when** | She clears the obvious in seconds and spends her judgment only on real exceptions |
| **Fears** | A tool that buries her in false exceptions, or that she can't trust without re-checking |
| **Loves** | Self-service: configure simple or complex checks and run on demand, *without going back to IT* (the reaction that won the room) |

### Ideal Customer Profile (wedge ICP)
A lender that simultaneously has:
1. **Enough closed-loan volume** to feel buyback *and* throughput pain;
2. **Multiple LOSs / recent M&A or multi-channel origination** — so there is no
   single QC source of truth (independence becomes a felt need, §3);
3. **A recent audit finding or repurchase scare** — an active, funded wound.

> **Assumption:** the first design partner fits this ICP. Identity TBD (§11).

---

## 3. Positioning & Differentiation

### Headline
> **"The independent QC engine that audits every closed loan — no matter which LOS
> originated it — and proves the math to a regulator."**

Pitch order (per the determinism repositioning): **accuracy first, determinism
second.**
> *"Accurate, defensible, independent QC for every closed loan."* Accuracy is the
> promise (proven by eval, §7); **determinism is the mechanism** (compile-then-run)
> that turns "accurate" into "auditable and repeatable."

### The stance: a layer, not a platform
We are the **deterministic decision-engine layer**, not a QC-workflow-platform
replacement. We do the part legacy tools *don't*: we **eliminate the review and
prove the math**, deterministically. We deliberately do **not** rebuild workflow,
sampling, defect-tracking, or GSE reporting (§5 build/buy/partner).

### Independence is a feature, not an integration detail
The product is **system-of-record-agnostic** — it is not tied to the origination
app. It integrates with whatever LOS(s) the lender runs, often **multiple**
(M&A / multi-channel lenders have no single QC truth). Its value is precisely in
**catching errors the originating system introduced** — an independent referee, not
a system grading its own homework. In the doc-vs-system comparison, "system" =
*whatever system-of-record holds the loan.* **[P0: `model.py` resolves the system
value from LOS, with MISMO/DU as a fallback format of the same lender data; it is
never compared against its own re-serialization.]**

### Objection-handlers
| Competitor | Their claim | Our handler |
|---|---|---|
| **ACES** | "We run your QC — workflow, sampling, defect tracking, GSE reporting." | *"That's the workflow layer, and we don't replace it. We're the engine underneath that decides the loan deterministically and proves the math — feed us, or sit beside ACES."* |
| **LoanLogics / Indecomm** (extraction + automated QC) | "We already do automated extraction and automated defect detection." | *"Correct — and that's the part we don't rebuild (we consume extraction). The gap is provability: can you reproduce a given verdict byte-for-byte years later and show an examiner the exact math? That's our wedge — deterministic, audit-replayable decisions bound to a signed ruleset."* **[honest: do NOT claim they don't automate QC — they do.]** |
| **Olav's runtime-LLM POC** | "The LLM can read the rules and decide at runtime; you don't need a compiled ruleset." | *"His POC proves AI can **read** rules. Ours proves AI can be **trusted to decide** — same loan, same verdict, byte-identical, every time, provable to an examiner."* **[P0: bit-exact across 1000 runs. NOTE: the per-file cost/determinism bake-off vs governed-runtime-LLM is still owed (see §11 / G3) — do not over-claim cost superiority until run.]** |
| **Manual review (the real incumbent)** | "Our analysts already do this." | *"At your volume, manually, you can neither clear fast enough nor prove the math when audited. We do both."* |

---

## 4. The Product — What It Does

Grounded in the **working P0** (`p0/`). The P0 is the determinism proof; the MVP
hardens it into a usable product on real loans.

### The two-step model (this is the actual product)
A loan is processed in two phases, and **only one of them is pass/fail.** **[P0:
`engine.py`, `RunResult.flags` vs `qc_failures`.]**

| Step | Name | What it does | Verdict semantics |
|---|---|---|---|
| **1** | **Reconcile (informational)** | Compare the closing document (truth) vs the system-of-record value; flag every difference ("document says X, system says Y — fix your system of record"). | A **FLAG** is INFO. It does **not** fail QC. A loan can be `AUTO-CLEARED (with N data-sync flags)`. |
| **2** | **QC rules (the only pass/fail)** | Run policy/compliance checks (e.g. LTV ≤ 95%, note signed) against the **truth** values. | **PASS / FAIL.** This is where a loan passes or fails and where exceptions are born. |

**Proof fixtures [P0]:** `LN-95301` — note rate doc 6.125 vs system 6.250 →
**FLAG only → still AUTO-CLEARED**. `LN-QCFAIL` — doc and system match perfectly,
but LTV 98% > 95% → **QC FAIL → EXCEPTION**. The separation is real, not asserted.

### The three surfaces

1. **Apply (the deterministic engine)** — runs a **signed ruleset by hash** against
   a canonical loan. Pure function of (ruleset, loan): no network, no model, no
   wall-clock. All money/ratio math is **Decimal with pinned ROUND_HALF_EVEN**, so
   the result is byte-identical on every run and machine. **[P0: `money.py`,
   `engine.py`; bit-exact across 1000 runs.]**
2. **Output (the exception queue)** — presents the result set so a human mitigates
   fast: **flags vs QC failures shown separately**, every doc-sourced value carries
   a **citation** (doc name + page + snippet), and a **clear-&-next-loan** flow.
   Auto-cleared loans require Step 2 to pass *and* nothing needing review. **[P0:
   `RunResult` exposes `flags`, `qc_failures`, `needs_review`, `auto_cleared`;
   `model.py` `DocCitation`.]**
3. **Author (DEFERRED to v2)** — the no-IT configuration surface (routes → blocks →
   checks). In the MVP, **Tavant hand-authors rulesets with the SME** via the
   LLM-compile + sign-off loop. Author is shown as a **clickable demo** to carry the
   vision, not as production functionality (§5).

### Compile-then-run, with binding sign-off
The LLM works at **configuration time**: it drafts a ruleset from the SME's intent;
the SME **corrects and signs** it; the engine then runs the **same signed artifact**
deterministically forever. The signature binds to the **human-corrected** text, and
we **measure SME edit-distance per rule** — zero edits across many rules is surfaced
loudly as sign-off-theater risk. The ruleset is identified **by SHA-256**; same hash
→ same rules → same verdicts. **[P0: `ruleset.py` provenance, edit-distance,
`unedited_rules()`, `sha256()`.]**

### Auto-clear logic and the confidence gate
Auto-clear is **gated on per-field extraction confidence.** A PASS that relied on a
low-confidence extracted truth value is **withheld → NEEDS_REVIEW**, never
auto-cleared. A confident-but-wrong extraction must not silently clear a bad loan.
**[P0: `engine.py` `DEFAULT_CONFIDENCE_FLOOR = 0.80`.]**

### Audit trail (system of record for the decision)
Every decision lands in a **hash-chained, tamper-evident audit log** — each record
hashes the prior plus the full per-check field intermediates (the 3 inputs, the
normalized/derived value, the rounding applied, the rule version + hash, the
verdict, the citation). Tampering with any historical record breaks every
subsequent hash. **[P0: `audit.py` `verify_chain()`; `engine.py` field-level
`CheckResult`.]**

---

## 5. MVP Scope & Explicit Non-Goals

### MVP = the Apply + Output loop on REAL labeled loans
**In scope (v1):**
- Deterministic engine: Step 1 reconcile (doc-vs-system flags) + Step 2 QC
  pass/fail. **[P0 proves the mechanism; MVP runs it on real loans.]**
- Output: cited exception queue, flags-vs-QC-fails separation, clear-&-next.
- Signed ruleset + hash-chained audit trail.
- Confidence-gated auto-clear.
- Runs against **genuinely independent** doc and system paths (not LOS-only).

**Deferred:**
| Item | Defer to | Why |
|---|---|---|
| **Author surface** (no-IT routes/blocks/checks UI) | **v2** | Tavant hand-authors with SME in v1; prove the engine earns trust first. Shown as clickable demo only. |
| **Product/program rule gating** (which of 800 fire for which loan) | **v2** | Blocker 3; assume all rules apply for now (§11). |
| **Self-service multi-LOS onboarding** | **v3** | MVP integrates the design partner's LOS(s) via reused connector. |
| **Document extraction** | **Never (partner)** | Touchless owns it (§contract). |
| **LOS integration build** | **Never (reuse)** | Reuse existing connector. |
| **Workflow / sampling / defect-tracking / GSE reporting** | **Partner/defer** | Legacy platforms' turf; we are the engine layer (§3). |

### Build / Buy / Partner
| Capability | Decision | Rationale |
|---|---|---|
| Deterministic reconcile + compile-then-run QC engine + cited audit | **BUILD** | This is the product and the moat-adjacent core. **[P0]** |
| Document extraction + classification | **BUY / PARTNER (Touchless)** | Don't rebuild; extraction accuracy is Blocker 1. |
| LOS data access | **REUSE** | Existing connector. |
| Workflow, defect tracking, sampling, GSE reporting | **PARTNER / DEFER** | Not our layer; would dilute focus. |

### Data-contract interfaces (track as interfaces, not builds)
- **From Touchless (upstream):** for a document blob → return **extracted fields +
  document classification + per-field citation + per-field confidence.** The
  confidence field is load-bearing for the auto-clear gate. *The contract may widen
  over time as more data elements are reviewed — track as an interface.*
- **From the LOS connector:** the lender's system-of-record loan data (LOS export;
  MISMO 3.4 / ULAD-DU accepted as a same-data fallback format). **[P0: `mismo.py`
  validated against all 3 demo loans.]**
- **Future truth-side widening:** an independent title/settlement feed (UCD /
  Closing Disclosure) would become a *second* truth-side source — not present today
  (§11).

---

## 6. Success Metrics

Three tiers. **Trust gates Value:** we never trade a higher auto-clear rate for a
worse false-auto-clear rate.

### Tier 1 — VALUE (the business outcome)
| Metric | Baseline | Target | How measured |
|---|---|---|---|
| Auto-clear rate | unknown — instrument first | **60–70%** | % of loans dispositioned with no human touch, against the volume eval set |
| Analyst time per loan | unknown — instrument first (assume current manual baseline) | **3–5× reduction** | timed analyst sessions, before vs after |

### Tier 2 — TRUST (gates Value — non-negotiable)
| Metric | Baseline | Target | How measured |
|---|---|---|---|
| **False-auto-clear rate** | unknown — instrument first | **≈ 0 (HARD GATE)** | auto-cleared loans that the labeled set says were defective. **This is the buyback number. It blocks ship.** |
| Exception precision / recall | unknown | high (set with SME at pilot) | engine exceptions vs labeled defects on the golden set |
| Determinism | — | **byte-identical (binary pass/fail)** | bit-exact harness over the golden set **[P0: passes 1000×]** |

### Tier 3 — ADOPTION (leading indicators)
| Metric | Baseline | Target | How measured |
|---|---|---|---|
| Time to author + sign a ruleset | unknown | trend down release-over-release | wall-clock of the compile→correct→sign loop |
| Analyst override rate | unknown | low + falling (churn leading indicator) | % of engine dispositions an analyst reverses |

### Pilot exit criteria (contractual)
1. **Passes a mock regulatory audit** — an examiner-style reviewer can trace any
   number to its inputs, rounding, rule version, and document citation, and confirm
   the audit chain is intact. **(Explicit contractual exit criterion.)**
2. **False-auto-clear rate ≈ 0** on the labeled set.
3. **Auto-clear rate** within the 60–70% target band on the volume set.
4. **Determinism** byte-identical on re-run. **[P0 already proves this property.]**
5. **Independence demonstrated** — the engine catches a defect the originating
   system introduced (doc-vs-system), on a loan with genuinely independent paths.

---

## 7. Eval & Ground-Truth Strategy

**Eval is a first-class workstream with a named owner and milestones. Blocker 2
(no labeled test data) is the #1 program risk** — the tool is only as trustworthy as
the ground truth it is measured against.

### Tiered data sets
| Tier | Size | Labeling | Role |
|---|---|---|---|
| **GOLDEN** | ~20–50 | Deeply, expertly labeled (Kayla) with known outcomes | **Regression gate on every ruleset promotion.** No promotion if golden regresses. |
| **COVERAGE** | moderate | Labeled for **defect-type diversity** (rate mismatch, flood conflict, unsigned note, address disparity, …) | Ensures we exercise the full defect surface, not just the easy path. **[P0 golden fixtures carry exactly these labeled defect types.]** |
| **VOLUME** | larger | Lightly labeled | Estimates real-world **auto-clear rate** at honest confidence. |

### The label-confirmation flywheel (instrument from day 1)
The engine's **cited** outputs become **draft labels** the SME confirms or corrects.
Each confirmed loan grows the labeled corpus, which sharpens the eval, which earns
more trust, which feeds the moat (§9). This is the compounding asset — wire it in
from the first pilot loan.

### Non-negotiables
- **Keep the doc path independent of the LOS.** LOS-only test data makes doc-vs-
  system trivially identical and untestable. **[P0 authors the doc path separately
  from the system path with labeled defects.]**
- **Report at honest confidence.** Synthetic data proves the plumbing; the real eval
  depends on Kayla's expert-labeled loans. We do not pretend otherwise.

### SME dependency (the critical path)
Kayla must (a) provide expert-validated loans with known outcomes, and (b) validate
the **800 check interpretations themselves** — did the team read each check
correctly? Both are on the critical path; treat SME availability as a tracked
dependency, not an assumption.

---

## 8. Pricing & Packaging

### Model: flat per-loan, every loan, re-runs free
- **Bill per LOAN dispositioned, not per run.** The engine reviews 100% of loans;
  catching an exception is as valuable as auto-clearing. **Re-runs of an updated
  ruleset (vN+1) are FREE** — determinism gives near-zero marginal cost, so price
  scales with value while cost stays flat.
- **NOT outcome-tiered** (no "pay only for exceptions"); **NEVER per-seat.**
- **Guardrails:** volume-declining per-loan rates + annual committed-volume bands.
- **Plus a ruleset-authoring services fee** (the compile→correct→sign engagement;
  Author surface is deferred, so this is delivered by Tavant + SME in v1).

### Anti-objection framing
- **Anchor:** *"$X per loan vs ~$32K per repurchased loan (avg; $100K+ all-in)."*
  (sourced Stratmor/Reggora; validate against the partner's own data, §1).
- **Weaponize the competitor's weakness — but only after G3 is run:** a runtime-LLM
  design is *harder* to quote a stable per-loan price for, and the thesis's
  illustrative "$10K/run on 10,000 files" assumes ~$1/file. **This is unverified
  2024-era arithmetic; 2026 caching/batch/small-model routing may cut it to cents.**
  Our compiled-once engine has a predictable, near-zero marginal compute cost — but
  **do not lead with cost superiority until the per-file bake-off (§11 G3) is run.**
  Until then, lead on *defensibility* (audit-replayable), not price.

---

## 9. Moat & Defensibility

> **Determinism tech is table-stakes, not the moat.** A competent team can build a
> deterministic engine. What compounds is the data and the trust.

### Primary moat — the eval / labeled-outcome flywheel + signed-ruleset library
Every pilot and every confirmed label grows an expert-adjudicated corpus and a
library of **signed rulesets per investor/program.** Over time and volume this
compounds via expert adjudication into something a new entrant cannot quickly
replicate. **Instrument the flywheel from day 1.**

### Supporting moats
- **Signed ruleset packs per investor/program** — switching cost; the lender's
  trusted, audited rules live with us.
- **Audit system-of-record lock-in** — once we hold the tamper-evident decision
  history examiners rely on, we are hard to remove. **[P0: hash-chained audit.]**
- **Tavant distribution** — access to lenders and the prototype→productize flywheel.

### Critical dependency
We need a **contractual right to learn from anonymized, cross-customer eval
outcomes.** Without it, the primary moat does not compound across the customer base.
Secure this in the first pilot contract (§11 open question).

---

## 10. GTM & Roadmap

### GTM motion
1. **Paid, time-boxed, fixed-scope "Determinism Pilot"** — proves all three:
   accuracy + defensibility + independence; passes a mock audit (§6).
2. **Reference + asset deposit** — a named reference and a deposit of reusable IP
   (signed-ruleset packs + eval harness).
3. **In-account expansion** — more programs, more LOSs, Author v2.
4. **Productized accelerator starter-kit** — signed-ruleset packs + eval harness so
   the *next* pilot is ~60% pre-built.

> **Anti-services-trap rule:** every engagement must **deposit reusable IP** (a
> ruleset pack, an eval set, a connector). If an engagement produces only a
> deliverable and no reusable asset, it is mispriced or misscoped.

### Roadmap (mapped to the three surfaces)
| Phase | Surfaces | Status / Scope |
|---|---|---|
| **P0 — Determinism proof** | Apply (core math + audit) | ✅ **DONE.** Decimal+pinned rounding, bit-exact ×1000, signed ruleset + edit-distance, hash-chain audit, doc-vs-system reconcile, two-step model, confidence gate, 19 tests green. |
| **MVP (v1)** | **Apply + Output** on real labeled loans | Engine on real loans; cited exception queue; flags-vs-QC-fails; clear-&-next; reuse LOS connector; consume Touchless contract; eval flywheel wired. Author shown as clickable demo only. |
| **v2** | **+ Author** | No-IT routes→blocks→checks authoring; product/program rule gating (Blocker 3). |
| **v3** | **Scale** | Self-service multi-LOS onboarding; productized accelerator + ruleset-pack library; cross-customer eval (subject to data rights). |

---

## 11. Risks & Open Questions

| # | Risk / Question | Severity | Mitigation / Owner |
|---|---|---|---|
| **B1** | **Extraction accuracy** (input quality poisons QC) | High | Don't rebuild; lean on Touchless / Kayla's Cloud-processed files. The **confidence gate** routes low-confidence extractions to humans **[P0]**. Scope determinism honestly as *"deterministic given the extracted inputs."* |
| **B2** | **No labeled test data** (the eval gap) | **#1 program risk** | First-class eval workstream (§7); tiered sets; SME-confirmation flywheel; tracked SME dependency. |
| **B3** | **Rule-to-program mapping unknown** (which of 800 fire for which product?) | Medium | Assume all rules apply for now; build product/program gating in v2. Don't block the build. Open: do we need the Fannie/Freddie selling guides beyond the client spreadsheet? |
| **Q1** | **Determinism vs governed-AI** — empirical question | Medium | Can a runtime-LLM design *prove* identical results every time? Burden of proof is on that side; compiled ruleset is the default **[P0]**. PRD/pilot exists partly to settle this. |
| **Q2** | **Cross-customer data rights** | High (moat-blocking) | Secure contractual right to learn from anonymized cross-customer eval outcomes in the first pilot (§9). |
| **Q3** | **First design partner** | High (GTM-blocking) | TBD. Must fit the wedge ICP (§2): volume + multi-LOS/M&A + recent audit/repurchase scare. |
| **A1** | **Repurchase-cost anchor** | — | Use **~$32K avg (Stratmor/Reggora 2023–24)**, $100K+ all-in as upside. Validate against the partner's own buyback data. *(Corrected from a bare "$40K+".)* |
| **A2** | **Per-loan price point $X** | — | **Assumption.** Set against validated repurchase cost + token-cost comparison (G3). |
| **A3** | **Independent truth-side feed (UCD/CD)** | — | Not present today; would widen the truth side. Track as future interface, not a build. |

### Go/No-Go gates before committing the full enterprise architecture
*(From the pre-architecture metacognition review, 2026-06-26. Architecture is hard to reverse; these upstream foundations must be green first. Today 4 of 6 are red.)*

| Gate | Must be true | Status | Why it gates architecture |
|---|---|---|---|
| **G1 · Labeled ground truth** | ≥20 expert-labeled loans (Kayla), independent doc/system paths | 🔴 RED | Can't measure the false-auto-clear ≈ 0 gate (§6) without it. |
| **G2 · Extraction accuracy quantified** | Measured field accuracy + *calibrated* confidence from Touchless on real docs | 🔴 RED | The 0.80 confidence floor is a magic number until calibrated; it can't catch *confidently-wrong* extractions. |
| **G3 · Runtime-LLM cost/determinism bake-off** | A real per-file cost number for the governed-LLM path (the thesis demanded this) | 🔴 RED | Can't claim determinism is a *cost/architecture* win — or rebut Olav — without it. Cheap to run; not yet run. |
| **G4 · Author: in the model or not** | Explicit call — is customer self-service authoring in the *data model* (UI may ship v2) or are we a service? | 🟡 AMBER | The thesis says self-service authoring "won the room." A customer-authored routes/blocks/checks model differs radically from a Tavant-internal compile pipeline. Locking the wrong one is the expensive reversal. |
| **G5 · Single- vs multi-LOS scope honesty** | Pilot is single-LOS OR multi-LOS is funded into the MVP estimate now | 🟡 AMBER | §3 leads with "any LOS" but §10 defers multi-LOS onboarding to v3 — can't "assume the periphery" (NN2) and headline multi-LOS at once. N-connector reconciliation is a load-bearing architectural axis. |
| **G6 · Design partner + data rights** | Named ICP-fit partner with the cross-customer-learning clause (Q2) agreed | 🔴 RED | The moat (§9) is contingent on a contract term lenders structurally resist. If they refuse, the moat changes. |

**Minimum green set to architect the *product*:** G1, G2, G3, G4. If leadership wants motion now, the only defensible move is **architect the single-LOS, Tavant-authored, design-partner-specific *services accelerator*** — and stop the positioning writing checks (multi-LOS, self-service, cross-customer moat) the MVP can't cash.

---

## 12. Appendix — Traceability

### Requirements → the four non-negotiables
| Requirement | NN1 Determinism | NN2 Build core / assume periphery | NN3 Three sources reconciled | NN4 Configurable by non-tech |
|---|---|---|---|---|
| Compile-then-run signed ruleset (§4) | ✅ | | | (Author v2) |
| Decimal + pinned rounding, bit-exact (§4,6) | ✅ | | | |
| Doc-vs-system reconcile = flag; QC = pass/fail (§4) | ✅ | | ✅ | |
| Confidence-gated auto-clear (§4) | ✅ | ✅ (B1 boundary) | | |
| Hash-chained audit trail (§4) | ✅ | | | |
| Buy/partner extraction; reuse LOS (§5) | | ✅ | ✅ | |
| Independence / multi-LOS (§3,5) | | ✅ | ✅ | |
| Author surface deferred to v2 (§4,5,10) | | ✅ | | ✅ |
| Eval flywheel + tiered sets (§7) | ✅ (regression gate) | | ✅ (independent paths) | |

### Requirements → P0 evidence (what is already proven)
| Claim | P0 evidence |
|---|---|
| Same loan → same verdict, byte-identical | `harness.py` — bit-exact across 1000 runs |
| No float drift flips pass/fail | `money.py` — Decimal + pinned ROUND_HALF_EVEN, fixed scales |
| Sign-off binds to human-corrected text; theater is visible | `ruleset.py` — provenance + Levenshtein edit-distance + `unedited_rules()` |
| Ruleset identified by hash | `ruleset.py` — `sha256()` over canonical content |
| Field-level "show me the math" audit | `engine.py` — `CheckResult` records inputs, normalized, rounding, rule version, citation |
| Tamper-evident decision history | `audit.py` — hash chain + `verify_chain()` |
| Step 1 flag ≠ QC fail | `engine.py` — `flags` vs `qc_failures`; `LN-95301` flagged-but-cleared, `LN-QCFAIL` failed |
| Confident-but-wrong won't auto-clear | `engine.py` — confidence floor 0.80 → NEEDS_REVIEW |
| Real MISMO parses | `mismo.py` — validated against all 3 demo loans |
| Independent doc/system test paths | `fixtures/golden.py` — doc path authored separately from system path, labeled defects |

---

*End of PRD v0.1 (DRAFT). Next handoff: architect translates §4–§7 product
acceptance criteria into EARS technical criteria and the data-contract interface
specs for Touchless and the LOS connector.*
