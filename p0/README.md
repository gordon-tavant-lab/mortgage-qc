# P0 — The Determinism Proof

> The minimum credible proof that a Mortgage QA/QC engine can be **deterministic
> and auditable** — the bet that separates this product from an LLM-at-runtime POC.
> Pure Python, zero cloud, zero network, zero model calls. Runs in seconds.

This P0 was built to the **judge's ruling** after a proposer → contrarian → judge
review of the enterprise architecture. It exists to prove the three things the
judge said must be true *before* the determinism claim is defensible in a client
room or an audit.

## What it proves

| # | Judge ruling | How this P0 answers it |
|---|---|---|
| **1** | "No LLM at runtime" ≠ deterministic. Float drift on money/ratio math flips pass/fail at tolerance boundaries. | All money/ratio math is **Decimal** with a pinned **ROUND_HALF_EVEN** policy and fixed scale (`qc_engine/money.py`). The **bit-exact harness** runs the golden set 1000× and asserts a **byte-identical** result hash (`harness.py`). |
| **2** | Sign-off must bind to the **human-corrected** artifact; measure SME edit-distance (sign-off theater is the risk). | The signed ruleset carries **per-rule provenance** — LLM draft vs signed text — and computes **edit-distance** per rule. `unedited rules` is surfaced loudly (`qc_engine/ruleset.py`). |
| **3** | Reconciliation/normalization must live **inside** the signed/authored artifact, not hand-code. | Normalizers + tolerances are **authored data referenced by name** from the signed ruleset; the Python is a fixed, version-pinned interpreter with no per-field judgment (`qc_engine/reconcile.py`). |
| **4** | The audit record must contain **field-level intermediates**, not an opaque debug trace. | Every `CheckResult` records the 3 inputs, the normalized/derived value, the rounding applied, the rule version, the verdict, and the doc citation (`qc_engine/engine.py`). |
| **8** | Confident-but-wrong extraction must not silently auto-clear. | Auto-clear is **gated on per-field extraction confidence**; below the floor → `NEEDS_REVIEW`, never an auto-clear. |
| **9** | S3 Object Lock is WORM but not verifiable history. | A **hash-chained** audit log (each record hashes the prior) detects any tampering; verified in SQLite here, anchored in Object Lock in prod (`qc_engine/audit.py`). |

## The two-step that is the actual product

A loan is processed in **two phases**:

1. **STEP 1 · Reconcile (informational)** — compare the closing document
   (**truth**) vs the system data and **FLAG** every difference ("document says
   X but system says Y — fix your system of record"). A flag is **INFO**; it
   does **NOT** fail QC. The loan docs are the source of truth, so QC simply
   runs against the doc values.
2. **STEP 2 · QC rules (the only pass/fail)** — run the policy/compliance checks
   (LTV ≤ 95%, note signed, etc.) against the truth values. **This** is where a
   loan passes or fails.

**Auto-clear requires Step 2 to pass** (and nothing needing human review).
Flags do not block auto-clear — a loan can be `AUTO-CLEARED (with N data-sync
flags)`. Two fixtures prove the separation:
- `LN-95301` (Marcus): note rate doc 6.125 vs system 6.250 → **FLAG only** →
  still **AUTO-CLEARED**.
- `LN-QCFAIL` (Dana): doc and system match perfectly, but LTV 98% > 95% →
  **QC FAIL** → **EXCEPTION**.

Each check is tagged `phase = RECONCILE | QC`; `RunResult` exposes `flags`
(informational) and `qc_failures` (the exceptions) separately.

## The non-negotiables, embodied
- **Determinism** — Decimal + pinned rounding + bit-exact harness.
- **DOC (truth) vs SYSTEM** — the closing documents from the title company are
  the **source of truth**; the engine checks whether the lender's **system**
  data matches and flags any mismatch ("document says X but system says Y").
  A MISMO/DU export is just the same system data in another file format
  (`system_value()` uses it as a fallback) — it is never compared against the
  system's own re-serialization (that proves nothing). If the truth document is
  missing, the check is `NEEDS_REVIEW`, never an auto-clear. (A genuinely
  independent title feed — the **UCD / Closing-Disclosure** — would become a
  second truth-side source the contract widens to; not present today.) Real
  MISMO 3.4 XML parses via `qc_engine/mismo.py` (validated against all 3 demo loans).
- **Independent test paths** — golden fixtures author the doc path **separately**
  from the system path with **labeled defects** (rate mismatch, flood conflict,
  unsigned note, address disparity). *Synthetic data proves the plumbing; the real
  eval still depends on Kayla's expert-labeled loans — we do not pretend otherwise.*

## Run it

```bash
cd p0
python3 tests/test_p0.py        # 19/19 — unit + integration
python3 harness.py 1000         # bit-exact determinism + precision/recall=1.0
python3 prove.py                # the 90-second LTV-boundary money moment
python3 run_demo.py             # E2E: 5 loans → result set + verified audit chain
```

## What this is NOT (deferred to P1/P2 per the roadmap)
No AWS (Fargate/Aurora/Cognito/Object Lock), no GoRules ZEN embedding, no
authoring UI, no Touchless/LOS connectors. Those are the industrial build. This is
the **determinism proof** — the thing that de-risks everything downstream and is
the demo artifact for the HousingWire determinism story.

## Files
```
qc_engine/
  money.py       Decimal money/ratio math + pinned rounding (determinism core)
  model.py       CanonicalLoan + per-field {doc,los,mismo} + citation + confidence
  reconcile.py   named normalizers/tolerances (authored, signed — not hand-code)
  ruleset.py     signed artifact: SHA-256, provenance, SME edit-distance
  engine.py      pure deterministic evaluator + field-level audit record
  audit.py       hash-chained immutable audit log (tamper-evident)
  mismo.py       real MISMO 3.4 / ULAD-DU XML adapter (system-side source)
fixtures/
  golden.py      labeled loans, independent doc/system paths, known outcomes
  ruleset_demo.py the compile→correct→sign loop with real SME corrections
harness.py       bit-exact determinism gate + eval vs labels
prove.py         LTV-boundary Decimal-vs-float demo
run_demo.py      end-to-end result set + audit chain verification
tests/test_p0.py 19 tests
```
