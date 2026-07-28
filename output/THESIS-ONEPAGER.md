# Mortgage QA/QC Tool — One-Page Thesis

**Build a configurable, deterministic QA/QC engine** that lets a non-technical mortgage SME wire up 800+ closed-loan checks (routes → blocks → checks), run them on demand against three data sources, **auto-clear** everything the machine can decide, and surface only the true human-judgment exceptions. This is a **seed to productize**, not a one-off prototype.

---

### 1 · Build the core, assume the periphery
Build the **rules engine + config workbench + result set**. **Don't build** document extraction (→ Touchless team returns data + classification) or LOS integration (→ reuse existing connector). *"Solve the core first: 800 checks, 3 sources — apply them correctly, return a good result set."*

### 2 · Three data sources, reconciled
**(a)** Closed-loan PDFs — the source of truth, unpacked by Touchless. **(b)** MISMO 3.4 XML — from title company or LOS. **(c)** LOS 3.4 export — via connector. The value is **cross-comparing** all three, not checking one in isolation. *Test data must keep the document and system paths independent — LOS-only data can't validate the comparison.*

### 3 · Determinism above all (the defining bet)
Same loan → **same pass/fail, every time.** Design: the **LLM compiles an intermediate ruleset at config time**; the SME validates it; the engine then runs it deterministically. **Proven, not asserted (G3 bake-off, 2026-06-28):** at temp=0, runtime LLMs *were* reproducible — so variance isn't the discriminator. The real ones are **(a) correctness on boundary math** — Haiku 4.5 *reproducibly* cleared a 98%-LTV loan (a buyback); Sonnet 4.6 caught it, but you can't know which behavior you have in advance or hand a regulator the derivation — and **(b) cost**: the engine is **$0 at any scale**, while a strong runtime model on real full-extraction payloads runs **~$700–$3,500 per run, every re-run.** *Runtime-LLM stays a live option for the no-algorithm cases (autonomy), not the deterministic core.*

### 4 · The philosophy that won the room
**Routes → Blocks → Checks**, configured by a **non-technical BA/SME without IT** — simple or complex, run on demand. This is what caught the client's imagination and what David reiterated. **Protect it.** Perfect three surfaces: **apply** (deterministic engine), **author** (no-IT config), **output** (human clears exceptions fast).

### 5 · Known blockers (with mitigations)
| Blocker | Mitigation |
|---|---|
| **Extraction accuracy** poisons QC | Don't rebuild; use Touchless / Kayla's Cloud-processed files |
| **No labeled test data** — can't tell right from wrong | Kayla provides expert-validated loans with known outcomes + validates the 800 check interpretations *(this is the eval gap)* |
| **Rule-to-program mapping unknown** — which rules fire for which product? | Kayla to get client detail; for now assume all rules apply, gate later |

---

**Next step:** Write the PRD (input → tool → output, every open question) with Gordon + team + Kayla, ~1 month → hand validated prototype to Monish for production build-out.
**Bigger picture:** QA/QC = the *determinism* story (HousingWire format: theory → live tool → proof). October Mortgage AI keynote = the *autonomy* story to build Jul–Sep. Agentic AI belongs **only** where no deterministic algorithm exists; everywhere else, utter determinism — because the regulator audits the math.
