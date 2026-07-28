# Authoring Examples — Routes & Blocks (reference material)

> Source: Gordon, 2026-06-30. Two concrete examples of what a **route** and a
> **block** look like in the current YAML form. These illustrate the
> configuration model (routes → blocks → checks → field catalog) — AND surface
> two problems the product must solve:
>
> 1. **YAML is not non-technical-friendly.** The buyer is a BA/SME who must
>    configure this *without IT* (Constitution Principle VI). Hand-authoring this
>    YAML defeats the differentiator.
> 2. **The block below embeds a RUNTIME LLM agent** (`step_template.agent` with a
>    `system_prompt`, `model: sonnet`, `tools`, `max_tool_rounds`, `temperature`).
>    That is a *runtime-LLM-at-evaluation-time* design — which directly conflicts
>    with the determinism non-negotiable (Principle I) and the "compile, then run"
>    bet (Principle II). See the G3 bake-off: a runtime LLM reproducibly cleared a
>    98%-LTV loan. This example must be reconciled with the compiled-engine
>    architecture, not adopted as-is.

These are captured verbatim as the problem statement for the authoring-UX work.

---

## Example 1 — A Route (DAG of blocks)

```yaml
route_id: conventional-purchase-pc
name: "Conventional Purchase Post-Closing QC"
description: "Full QC audit for conventional purchase loans (Fannie Mae / Freddie Mac)"
version: 1
enabled: true
trigger:
  type: event
  source: qc.events
  event_type: loan.submitted_for_qc
settings:
  timeout_seconds: 300
  priority: normal
dag:
  nodes:
    - id: intake_classification
      block: loan-intake
      params:
        phase: "post-closing"
      authority: auto
    - id: fan_out_checks
      type: fan_out_joint
      outputs:
        - target: application_check
        - target: income_check
        - target: asset_check
        - target: credit_check
        - target: property_check
        - target: compliance_check
        - target: closing_docs_check
        - target: insurance_check
        - target: epd_check
        - target: underwriting_check
        - target: loan_documents_check
        - target: certification_check
        - target: data_validation_check
        - target: form_1033_check
        - target: product_specific_check
        - target: info_integrity_check
    - id: application_check
      block: application-verification
      authority: auto
    - id: income_check
      block: income-verification
      authority: auto
    - id: asset_check
      block: asset-verification
      authority: auto
    - id: credit_check
      block: credit-liabilities-review
      authority: auto
    - id: property_check
      block: property-appraisal-review
      authority: auto
    - id: compliance_check
      block: compliance-review
      authority: auto
    - id: closing_docs_check
      block: closing-documents-review
      authority: auto
    - id: insurance_check
      block: insurance-review
      authority: auto
    - id: epd_check
      block: epd-review
      authority: auto
    - id: underwriting_check
      block: underwriting-review
      authority: auto
    - id: loan_documents_check
      block: loan-documents-review
      authority: auto
    - id: certification_check
      block: certification-delivery
      authority: auto
    - id: data_validation_check
      block: data-validation-services
      authority: auto
    - id: form_1033_check
      block: appraisal-form-1033
      authority: auto
    - id: product_specific_check
      block: product-specific-check
      authority: auto
    - id: info_integrity_check
      block: information-integrity
      authority: auto
    - id: merge_checks
      type: fan_in_joint
      inputs:
        - source: step:application_check
          required: true
        - source: step:income_check
          required: true
        # ... (one required input per check block) ...
      merge_strategy: collect
    - id: generate_report
      block: qc-report-generator
      authority: auto
  edges:
    - from: intake_classification
      to: fan_out_checks
    - from: fan_out_checks
      to: [application_check, income_check, asset_check, credit_check, property_check,
           compliance_check, closing_docs_check, insurance_check, epd_check,
           underwriting_check, loan_documents_check, certification_check,
           data_validation_check, form_1033_check, product_specific_check,
           info_integrity_check]
    # ... each *_check edges to merge_checks ...
    - from: merge_checks
      to: generate_report
```

**What this shows:** a route is a **DAG** — intake → fan-out to ~16 category
blocks (one per AMQ category) → fan-in/merge → report. `authority: auto` per node.
Triggered by an event. This is the orchestration layer the SME must compose.

---

## Example 2 — A Block (group of checks, currently as a runtime LLM agent)

```yaml
block_id: certification-delivery
name: "Certification, Endorsement, and Delivery Review"
description: "Verifies loan certification requirements, endorsement documentation,
  delivery data accuracy, and investor delivery compliance for secondary market sale."
category: certification-delivery
version: 1
parameters:
  investor:
    type: string
    default: "fnm"
    description: "Investor code"
inputs:
  - name: loan_number
    type: string
    required: true
  - name: loan_data
    type: object
outputs:
  - name: exceptions
    type: array
  - name: passes
    type: array
  - name: not_applicable
    type: array
  - name: total_checks
    type: number
  - name: critical_count
    type: number
  - name: major_count
    type: number
step_template:
  agent:
    system_prompt: |
      You are a mortgage QC auditor specializing in Certification, Endorsement,
      and Delivery Review. You must systematically evaluate every question in the
      catalog below against the loan file data.
      ... [10-question catalog: each question has a CODE, TEXT, SIGNIFICANCE,
           AOR, and a set of RESPONSES. Each response maps to an EXCEPTION code +
           detail, or PASS, or NOT_APPLICABLE — and carries a CRITERIA field that
           is a SQL-like gate, e.g.:
             CRITERIA: SELECT DISTINCT Loans.LoanID FROM Loans
                       WHERE (Loans.QC_Policy = 'FHA')          ] ...
      OUTPUT FORMAT: Output ONLY raw JSON ... {exceptions[], passes[],
      not_applicable[], total_checks, critical_count, major_count}
    model: sonnet
    max_tokens: 8000
    temperature: 0.1
  tools:
    - get_loan_application
    - get_loan_summary
    - get_document_list
    - get_closing_documents
  max_tool_rounds: 15
  authority: auto
```

**What this shows — and the problem:**
- A **block** = a named group of **checks** (here 10 questions, codes like
  `O-FHA-15301`), each with a significance (Critical/Major), an AOR (area of
  responsibility — Closer/Underwriter/Processor), and responses that resolve to
  EXCEPTION / PASS / NOT_APPLICABLE.
- Each response carries a **SQL-like CRITERIA gate** (`WHERE QC_Policy = 'FHA'`) —
  this is exactly the machine-readable program gating the taxonomy run found (615
  rows; roadmap 010a).
- **The catch:** this block is implemented as a **runtime LLM agent** (`model:
  sonnet`, `temperature: 0.1`, `max_tool_rounds: 15`). The LLM reads the catalog
  and the loan at *evaluation time* and emits the verdicts. **This is the very
  runtime-LLM design the determinism non-negotiable rejects** — `temperature:
  0.1` is not even `0`, and tool-augmented multi-round agents are not bit-exact.
  Under the compiled architecture, this catalog (questions + responses + criteria
  + significance + AOR) is exactly the **authored data** that should be COMPILED
  into a signed, deterministic ruleset — the LLM's job is config-time
  interpretation, not runtime evaluation.

---

## The two problems for the authoring-UX work to solve

1. **Authoring surface:** non-technical SMEs cannot hand-write this YAML. What is
   the right authoring experience — natural-language intent (if dependable +
   accurate), a guided UI, import-from-spreadsheet, or a hybrid — that produces
   these artifacts without the SME touching YAML?
2. **The runtime-vs-compile reconciliation:** the block's question-catalog +
   criteria + significance is *authored data*; it must be compiled to a
   deterministic ruleset (Principle II), not executed by a runtime LLM agent. The
   authoring UX produces the *intent*; the compiler (002b) turns it into the
   signed artifact; the engine (003a/b/c) runs it deterministically.
```
