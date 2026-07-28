# Authoring UX — Decision Memo

| | |
|---|---|
| **Decision** | What is the right authoring experience for non-technical SMEs to create routes, blocks, checks, and field-catalog entries? |
| **Owner** | Product Manager |
| **Date** | 2026-06-30 |
| **Status** | RECOMMENDATION — for human decision (gates G4, Tension 1, Tension 7) |
| **Governs** | Constitution v1.1.0 (Principles I, II, VI, VII). Inputs: `docs/authoring-examples.md`, `output/ROADMAP.md`, `p0/experiment_g3/RESULTS.md`. |
| **Reshapes** | Roadmap feature **009-no-it-authoring-workbench**. |

> **TL;DR.** Authoring is not one task — it is four, and they have opposite UX needs. The
> bulk path is **import** (the AMQ workbook already *is* a structured authoring source — 7,398
> conditions, 615 machine-readable gating clauses, already parsed by the taxonomy/compiler).
> Natural language is **safe and valuable for the prose layer** (titles, descriptions, intent
> drafts) but **must not be the sole authority on the criteria gate** — that is where a
> plausible-but-wrong artifact gets rubber-stamped. A **guided structured UI** owns the gate,
> the significance, and the route DAG. The recommendation is a **Hybrid: Import-first +
> Guided-UI for the dense logic + NL as a drafting assistant inside the guided UI**, with the
> LLM working **only at config time** and every artifact flowing the compile-then-sign loop
> (002b) before it can run. The runtime-LLM block in Example 2 is **reframed as authored data**,
> not adopted. This rescopes 009 from "a workbench" into a three-tier authoring system whose
> hardest dependency is the **diff-and-sign review surface**, not the input method.

---

## 1. The real problem: "authoring" is four tasks, not one

The roadmap's Authored Configuration Model (constitution Principle VII) already names four
layers. The mistake the brief warns against is treating them as one UX. They are not — they sit
on opposite ends of *density* and *risk*:

| Layer | What the SME authors | Density | If the LLM gets it wrong, the failure is… | Right input metaphor |
|---|---|---|---|---|
| **Route** | a DAG of blocks: intake → fan-out → fan-in → report, with `authority` per node, applicability gating | low (structural, repetitive — see Example 1's 16-way fan-out) | a block doesn't run, or runs out of order → **visible, loud** (a whole category missing) | **visual DAG / wiring**, not prose |
| **Block** | a named grouping of checks (one per AMQ category) | low (it's a label + a membership list) | wrong checks grouped → re-organizable, **low stakes** | **list / grouping UI** |
| **Check** | the question + responses + significance (Critical/Major) + AOR + **the CRITERIA gate** | **HIGH — this is the dense, dangerous part** | a wrong criteria gate **silently fires the wrong check or skips a check that should fire** → a **false-clear vector** (constitution SAFE gate) | **mixed: prose for the question, structured for the gate** |
| **Field catalog** | which data elements exist, each with type, expected sources, citation/confidence requirements | medium (typed, finite vocabulary) | an unresolved field reference = a silent no-op = **false-clear vector** (Principle VII referential integrity) | **structured form, validated against the catalog** |

The 10-question catalog in Example 2 is the hard case, and within it the **CRITERIA field**
(`WHERE QC_Policy = 'FHA'`) is the hard *part*. Everything else in that block — the question
text, the significance, the AOR, the response→exception mapping — is comparatively safe to draft
in prose. **The criteria gate is the one place where a wrong-but-plausible artifact survives a
casual human review and silently breaks QC.** Any authoring decision has to be made *about that
specific field*, not about "authoring" in the abstract.

A second, separable problem rides inside Example 2: that block is implemented as a **runtime LLM
agent** (`model: sonnet`, `temperature: 0.1`, `max_tool_rounds: 15`). That is not an authoring
question at all — it is an architecture violation (Principle I/II). It is resolved in §6: the
catalog is *authored data*, compiled once into a signed deterministic ruleset; the agent
disappears.

---

## 2. The option space, with honest trade-offs

Four options, scored on the four axes that matter: non-technical-friendliness, dependability/
accuracy, fit with compile-then-run determinism, and the dominant failure mode.

### Option A — Natural-language authoring (SME describes intent → LLM drafts artifact at config time → SME signs)
The prototype already gestures at this (`useLlmAssistant` / "LLM Draft Assistant" in
`RulesWorkbench.tsx`).

- **Non-technical-friendly:** Highest. "Closing costs must be under 3% of principal" is exactly
  how an SME thinks.
- **Dependability/accuracy:** **Bifurcated, and this is the crux.** For *prose* (question text,
  description, significance suggestion) — high, and errors are cosmetic/caught on read. For the
  *criteria gate* — **this is the same class of task G3 showed an LLM can get reproducibly
  wrong** (boundary interpretation, `≤` vs `<`, which policy the WHERE clause gates to). The
  difference from G3 is *when* the error occurs (§3) — but the accuracy of the underlying act is
  no better than G3 measured.
- **Fit with determinism:** Compatible **if and only if** the LLM is confined to config time and
  the output is signed + compiled. NL → intent → compiler → signed ruleset honors Principle II
  exactly. NL → runs directly does not exist in this design and is rejected.
- **Failure mode:** **Sign-off theater on the gate.** The LLM emits a criteria clause that *looks
  right*, the SME — not a SQL reader — rubber-stamps it, and a check now silently mis-fires. The
  constitution already names this smell (Principle II: "zero edits across many rules is the
  sign-off-theater smell") and already has the instrument (measured edit-distance). NL authoring
  *increases* this risk precisely because prose-in feels effortless.

### Option B — Guided structured UI (forms / wizards / visual DAG builder; no free-text-to-logic)
- **Non-technical-friendly:** High for routes/blocks/fields (pick from lists, wire boxes, fill
  typed forms). **Medium-to-low for the criteria gate** — a non-technical SME still has to express
  "FHA loans only, LTV over 95%" through *some* structured control. But a guided control
  (dropdown: field = `QC_Policy`, op = `equals`, value = `FHA` [picked from the catalog's known
  values]) is far safer than free text, because **every choice is constrained to valid,
  catalog-resolvable values** — referential integrity is enforced *by construction* at author
  time, not caught later by the SAFE gate.
- **Dependability/accuracy:** **Highest.** No interpretation step to be wrong. What the SME picks
  is what compiles. The artifact is auditable as a direct trace of human choices.
- **Fit with determinism:** Native. The structured form *is* the intent; the compiler's job
  shrinks to near-trivial.
- **Failure mode:** **Author friction / abandonment.** Wiring 7,398 conditions through forms by
  hand is not viable — the SME goes back to IT, killing the differentiator. Guided UI is the right
  tool for *editing and net-new authoring*, the wrong tool for *bulk*.

### Option C — Import from spreadsheet (the AMQ workbook is already a structured authoring source)
This is the option the brief flags and the roadmap already half-banks on. The AMQ workbooks carry
**7,398 conditions** and **615 machine-readable SQL gating rows**; `taxonomy.py` already parses
and classifies them; the compile-fidelity spike (002a) tests turning them into signed rules.

- **Non-technical-friendly:** **Highest for bulk** — the SME already lives in the spreadsheet.
  "Author" becomes "import what you already maintain," not "re-enter 7,398 rows."
- **Dependability/accuracy:** **High for what the sheet encodes explicitly** (the 615 SQL gates
  are machine-readable — no interpretation needed, just parse). **Gated by 002a for the rest** —
  where intent is implicit in prose cells, the compiler must interpret, and that is exactly the
  config-time interpretation risk 002a is built to measure. Import does not *eliminate* the
  interpretation risk; it *concentrates it into one auditable batch* the SME reviews once.
- **Fit with determinism:** Excellent. Import → compile → SME diff-review → sign. This *is* the
  compile-then-run loop applied to the bulk path.
- **Failure mode:** **Batch sign-off theater** — 7,398 rows is far too many to review honestly one
  by one, so the SME signs the batch. Mitigated only by (a) the edit-distance / sign-off-theater
  instrument and (b) the eval gate (005) catching defects construction can catch. Residual: the
  interpretation errors eval *can't* catch (Principle III "Question 2"), which is why 002a
  requires Kayla's rules review, not just runnability.

### Option D — Hybrid (RECOMMENDED): Import-first + Guided-UI for the dense logic + NL as a drafting assistant
- **Import (C)** is the **bulk path** — get the 7,398 conditions in once, honor the 615 gates the
  sheet already encodes.
- **Guided UI (B)** owns the **route DAG, the block grouping, the field catalog, and the criteria
  gate** — the structured, safety-critical surfaces, with catalog-constrained controls so
  referential integrity holds by construction.
- **NL (A)** is a **drafting assistant *inside* the guided UI** — it pre-fills the prose fields
  (question text, description, suggested significance) and *proposes* a structured gate that lands
  in the guided control **for the SME to confirm field-by-field**, never as free text that bypasses
  the structured surface.

This is the only option that is non-technical-friendly *and* dependable *and* determinism-native,
because it assigns each task to the input method whose failure mode is survivable for that task.

| Option | Non-technical | Dependable | Determinism fit | Dominant failure mode |
|---|---|---|---|---|
| A · NL only | ★★★ | ★ (gate) / ★★★ (prose) | OK if config-time + signed | **gate sign-off theater** |
| B · Guided UI only | ★★ | ★★★ | native | **bulk abandonment → back to IT** |
| C · Import only | ★★★ (bulk) | ★★ (gated on 002a) | excellent | **batch sign-off theater** |
| **D · Hybrid** | **★★★** | **★★★** (each task on its safe method) | **native** | mixed, but each is the *survivable* one |

---

## 3. The dependability question, head-on

The user gated NL authoring on *"if it is dependable and accurate."* G3 is the binding evidence:
a runtime LLM (Haiku) **reproducibly produced a wrong verdict** — it cleared a 98%-LTV loan
against a 95% max, identically every time, and that stable-wrong answer survives a "show me the
same number twice" audit. So: is NL authoring safe?

**The decisive distinction is *when the error occurs and where it gets caught*.**

| | G3 runtime-LLM error | NL **authoring**-LLM error |
|---|---|---|
| **When** | evaluation time, on every loan, forever | config time, once, on the draft |
| **What runs in production** | the LLM's verdict, directly | a **signed, compiled, deterministic** ruleset — the LLM's *output is never what runs* |
| **Catch points before it ships** | **none** — the wrong verdict *is* the product output | (1) SME **sign-off** on the diff; (2) the **eval gate** (005, zero-false-auto-clear); (3) the **002a interpretation-fidelity review** |
| **Detectability** | **silent and reproducible** — worst case | a wrong gate is a *static artifact* a human and a scorer can inspect *before* it ever touches a loan |

So the calculus genuinely changes: **an authoring-time LLM error is not the G3 failure.** G3's
horror is a *silent runtime* error with no catch point. Authoring-time errors face three catch
points before production. That is why NL-as-config-time-drafting is *permissible* where
NL-at-runtime is not.

**But be rigorous about where it can still slip through.** The catch points are not equally
strong, and one task defeats all three:

1. **The SME sign-off catches prose errors well and gate errors poorly.** An SME reading
   "ensure closing costs are under 3% of principal" can verify the *sentence*. The same SME
   reading `WHERE QC_Policy = 'FHA' AND LTV > 95` is reviewing *code they cannot fluently read* —
   this is the sign-off-theater hole, and it is **deepest exactly on the criteria gate**, the one
   field that is a false-clear vector.
2. **The eval gate (005) catches what construction can label** — a gate that produces a wrong
   verdict on a synthetic case with a known answer gets caught. It does **not** catch a gate that
   is *interpreted wrong but consistently* (reads "FHA" where the lender meant "FHA + VA") if no
   constructed case exercises that distinction. This is Principle III's "Question 2"
   (interpretation correctness), which the constitution says construction *cannot* answer.
3. **002a's SME rules-review** is the only catch point aimed squarely at interpretation fidelity —
   and it is a *spike sample*, not a per-rule guarantee.

**Conclusion on dependability (precise, per the brief's instruction to say exactly which part):**

- ✅ **NL is dependable enough to author the PROSE layer** — question text, descriptions,
  significance/AOR suggestions. Errors here are visible-on-read and cosmetic. Use it freely.
- ⚠️ **NL is NOT dependable enough to be the sole authority on the CRITERIA GATE.** It may
  *propose* a gate, but the proposal must land in a **structured, catalog-constrained control**
  that the SME confirms value-by-value — converting an un-reviewable SQL string into a set of
  discrete, human-checkable choices. This is the single most important design constraint in this
  memo.
- ✅ **The compile-then-run architecture is what makes even the proposal safe** — because the
  proposal is never what runs. The signed, compiled artifact is.

The honest residual that no authoring UX removes: **batch/gate sign-off theater on the dense
checks.** The mitigations are not new — they are the constitution's own instruments: measured
edit-distance with sign-off-theater surfaced loudly (Principle II), the zero-false-auto-clear eval
gate (005), referential integrity enforced at author time (Principle VII), and 002a's
interpretation review. The authoring UX's job is to *feed* those instruments, not to claim it has
solved a problem they exist to police.

---

## 4. Recommendation + phased path

**Recommend Option D (Hybrid), phased so the MVP earns the right to the v2 magic.** This honors
Tension 7 (trust-ordering): we do not ship a seductive author-first surface over an unproven
engine.

### MVP authoring experience (for the pilot) — "Import + Diff-and-Sign + Guided Edit"
The pilot does **not** need free-form NL authoring. It needs the SME to get their existing rules
in, see exactly what the compiler made of them, and sign — plus edit the handful that matter.

1. **Import** the AMQ workbook (the bulk path, Option C). Honor the 615 SQL gates the sheet already
   encodes (roadmap 010a). This is "authoring" the SME already did, in the tool they already use.
2. **The diff-and-sign review surface** (the real centerpiece — see §5). For each compiled rule:
   show the source condition ↔ the compiled gate ↔ the plain-English restatement, side by side.
   The SME signs the artifact (Principle II), and **edit-distance is measured and surfaced** — a
   batch signed with zero edits is flagged, not celebrated.
3. **Guided UI for net-new and edits** (Option B) — a structured, catalog-constrained editor for a
   single check's gate/significance/AOR, the block grouping, and the route DAG (a visual builder
   over Example 1's structure). Referential integrity holds by construction.

This is hardened directly from the existing prototype: `RulesWorkbench.tsx` (routes/blocks/checks
toggling, the Add-Check modal) and `RuleCompilerVisualizer.tsx` (the verification gate), keeping
the design language (Inter/Space Grotesk/JetBrains Mono, slate canvas, blue accent).

> **Honesty note on the prototype:** `RuleCompilerVisualizer.tsx` currently *simulates* compilation
> with theatrical log lines (`[OPTIMIZER] Bypassing O(n) security gaps…`, "Ruleset is 100%
> deterministic"). For demo that's fine; for the product the diff-and-sign surface must show the
> *real* compiled artifact and *real* edit-distance, not a progress animation. The prototype is the
> design language, not the behavior contract.

### v2 vision — "NL drafting assistant inside the guided UI"
Once the engine + eval + audit are load-bearing (the trust order), turn on NL as a **drafting
assistant**: the SME types intent in prose; the LLM (config time) pre-fills the prose fields and
**proposes a structured gate into the guided control**; the SME confirms field-by-field. NL never
emits free-text logic that bypasses the structured surface. This is the magic that won the room —
delivered on top of an engine that has earned the trust to host it.

**The reconciliation with compile-then-run, stated once, plainly:**

> **Authoring produces INTENT → the compiler (002b) produces the signed, hashed, deterministic
> ruleset → the engine (003a/b/c) runs it.** The LLM lives only in the INTENT→draft step, at
> config time. The artifact the SME signs is the artifact that runs (loaded by SHA-256). No
> authoring path — import, guided, or NL — ever puts a model on the runtime path.

---

## 5. Proposed rescope of feature 009

**009 today** ("harden the prototype's `RulesWorkbench` + `RuleCompilerVisualizer` into the no-IT
config surface") is under-specified for what the analysis reveals: it treats authoring as one
surface and is silent on the import path, the diff-and-sign centerpiece, and the gate-safety
constraint.

### Rescoped 009 — split into three sub-features by the tasks' divergent UX/risk

| New ID | Name | Scope | Why split |
|---|---|---|---|
| **009a-import-and-diff-sign** | Import + the compiled-artifact review/sign surface | Ingest the AMQ workbook; render source-condition ↔ compiled-gate ↔ plain-English diff per rule; capture SME sign-off bound to the human-corrected artifact (SHA-256); **measure + surface edit-distance and the zero-edit sign-off-theater smell.** | This is the **MVP authoring experience** and the real engineering risk. The bulk path + the trust anchor. Depends on the compiler, not on a UI vision. |
| **009b-guided-structured-editor** | Catalog-constrained editor for checks, blocks, field catalog, and the route DAG | Net-new + edit a single check (gate via catalog-constrained controls, significance, AOR), group checks into blocks, declare field-catalog entries (typed, sources, confidence), wire the route DAG visually. Referential integrity enforced **at author time**. | The safe surface for the dense logic. Owns the criteria gate so NL never does. |
| **009c-nl-drafting-assistant** *(v2)* | NL intent → config-time draft into the guided UI | SME prose → LLM (config time) pre-fills prose fields + **proposes a structured gate into 009b's control** for field-by-field confirmation. Never free-text logic to runtime. | The magic — gated behind a trusted engine (Tension 7) and behind 002a proving config-time interpretation fidelity. |

### New dependencies

- **009a** depends on **002b** (the production compiler) and **010a** (honoring the 615 SQL gates
  on import) and **005** (no imported rule runs without passing the eval gate). It is the *first*
  authoring feature and the one that proves the compile-then-sign loop is usable by an SME.
- **009b** depends on **001a** (the field catalog it edits and constrains against) and **002b**.
- **009c** depends on **009b** (it writes *into* the guided control) and on **002a's go-decision**
  — if 002a finds config-time interpretation fidelity is poor or needs near-total SME rewriting,
  **009c does not ship**; the product stays import + guided. NL authoring is *conditional on 002a*,
  exactly as the user conditioned it on "dependable and accurate."

### Interaction with the G4 tension (Tension 1: customer-authored model vs Tavant-internal pipeline)
The analysis sharpens G4 into a phased answer instead of a binary:

- **MVP (009a + 009b) is customer-facing but Tavant-shaped.** The customer authors via *their own
  spreadsheet* (import) and edits via a *guided UI* — they never touch YAML or the compiler. The
  compile pipeline stays Tavant-internal; the customer's surface is import + diff-sign + guided
  edit. This satisfies Principle VI ("without going back to IT") **without** committing to the
  expensive full customer-authored DSL.
- **The expensive, hard-to-reverse commitment (a full customer-authored authoring model) is
  deferred to 009c/v2** and gated on 002a. **G4 must be locked before 009c, not before 009a.**
  This *unblocks the MVP authoring work* — which previously sat behind an unresolved G4 — by
  showing the MVP needs only the cheap, reversible half of the decision.

---

## 6. Reframing the runtime-LLM block (Example 2)

The `certification-delivery` block embeds a runtime agent (`temperature: 0.1`,
`max_tool_rounds: 15`). Under this recommendation it is **authored data, not a runtime agent**:

- The **10-question catalog** (codes, question text, responses→exception mapping, significance,
  AOR) is exactly the **check-and-block authored data** of Principle VII — imported (009a) or
  authored in the guided UI (009b).
- Each response's **SQL-like CRITERIA gate** is the program gating honored by **010a** (it is one
  of the 615 machine-readable rows) and executed deterministically by **003a/b/c**.
- The agent's `system_prompt` + `tools` + `temperature` **disappear**. The catalog is **compiled
  once** (002b) into a signed deterministic ruleset; the engine evaluates it with no model at
  runtime. This is the §4 reconciliation applied to the exact artifact in the brief.

This is the second problem `docs/authoring-examples.md` flagged, resolved: the block is *intent
the authoring UX captures and the compiler turns into a signed artifact* — never a runtime
evaluator.

---

## 7. New tension surfaced

**Tension 8 — NL-on-the-gate vs the sign-off-theater hole (AMBER → RED on the criteria layer).**
The feature most likely to *delight* (type-it-in-English authoring, 009c) targets the exact field
(the criteria gate) where a wrong-but-plausible artifact most easily survives SME sign-off, because
the SME cannot fluently read the gate they are signing. The constitution's instruments
(edit-distance, eval gate, referential integrity, 002a review) *police* this but do not *eliminate*
it. **Decision owed:** does NL ever emit the gate, or is it permanently confined to proposing into a
catalog-constrained control that the SME confirms value-by-value? **This memo recommends the
latter, hard** — but it constrains the v2 "magic" and should be an explicit, signed-off product
boundary before 009c is specced, not discovered in build. This is distinct from Tension 1 (which is
about *whether* the authoring model is customer-facing) and Tension 7 (the *ordering* of the Author
surface) — Tension 8 is about *how much authority the LLM gets over the one safety-critical field*.

---

*Decision memo — for human sign-off on the recommendation, the 009a/b/c rescope, and Tension 8.
The architect translates the in-scope items (009a, 009b) into EARS technical criteria and the
diff-and-sign + guided-editor designs once the gates are green. Constitution v1.1.0 governs.*
