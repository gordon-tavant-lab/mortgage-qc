// Data shapes mirror p0/qc_engine's real classes:
//   CheckResult   -> p0/qc_engine/engine.py:46
//   Check         -> p0/qc_engine/ruleset.py:49 (operator/threshold/ratio live HERE, not on CheckResult)
//   field catalog -> p0/qc_engine/field_catalog.json (385 real entries)
// Anything without a real backend counterpart today (e.g. reserve-months)
// is flagged inline as PLACEHOLDER — never silently presented as real.

export type Severity = "CRITICAL" | "WARNING" | "INFO";
// NOT_COMPILED added for spec019 (gold-ruleset rework, 2026-08-01): a check whose
// authoring-time compile state is not yet COMPILED (see Check.compileState) has no
// meaningful runtime CheckResult -- NOT_COMPILED is that "never ran" status, distinct
// from NOT_APPLICABLE (ran, gated out) and NEEDS_REVIEW (ran, ambiguous).
export type CheckStatus = "PASS" | "FAIL" | "WARNING" | "FLAG" | "NEEDS_REVIEW" | "NOT_APPLICABLE" | "NOT_COMPILED";
// Revised for spec021 (2026-08-02): trimmed from the original PENDING/AUTO_CLEARED/
// EXCEPTION/RESOLVED vocabulary to the real engine's severity-tiered outcome model
// (research.md Item 1) -- PASS (zero qc_failures) / FAILED (>=1 CRITICAL qc_failure) /
// NEEDS_REVIEW (qc_failures/needs_review present, none CRITICAL) / RESOLVED (only via
// manual mitigation of a NEEDS_REVIEW loan) / ERROR (the audit-run subprocess itself
// failed -- never a real engine verdict). RUNNING is NOT a member of this persisted
// union -- it's modeled as a separate, transient display state (see LoanDisplayState
// below), since a loan mid-run has no status of its own yet.
export type LoanStatus = "PASS" | "FAILED" | "NEEDS_REVIEW" | "RESOLVED" | "ERROR";

// A loan's *displayed* state, derived (not stored) -- see dataSourceContext.tsx's
// deriveLoanDisplayState(). The 19 cosmetic loans (no applicationId) are always
// "resolved" with their static mock status. The one real demo loan (applicationId
// present) starts "not_fetched" (honestly: no run has happened yet, never fabricated
// as if it had) until a pull+audit-run resolves it.
export type LoanDisplayState =
  | { kind: "not_fetched" }
  | { kind: "running" }
  | { kind: "resolved"; status: LoanStatus }
  | { kind: "error"; message: string };
// The false-clean-at-authoring-layer guard (spec019's core concept, re-platformed onto
// the gold ruleset in the 2026-08-01 rework -- see frontend/scripts/build_gold_catalog.py).
// COMPILABLE only when a real evidence field resolved; conservative by design.
export type Authorability = "COMPILABLE" | "NEEDS_FIELDS" | "NEEDS_SME" | "NOT_MECHANIZABLE";

export interface Loan {
  loanId: string;
  borrowerName: string;
  loanType: string;
  propertyAddress: string;
  routeId: string;
  status: LoanStatus;
  assignedAt: string;
  // Spec 020-touchless-api-integration: the Touchless `applicationId` this loan corresponds
  // to, if known. Optional -- only the demo loan wired to the live-verified Touchless sandbox
  // application carries one; `PullApplicationButton`/`LiveApplicationPanel` only render when
  // present (pull-only, requires a known id per spec Assumptions).
  applicationId?: string;
}

export interface FieldCatalogEntry {
  fieldId: string;
  fieldName: string;
  dataType: "string" | "number" | "decimal" | "boolean" | "date";
  expectedSources: ("doc" | "los" | "mismo")[];
  citationRequired: boolean;
  placeholder?: boolean; // true = not a real p0/qc_engine/field_catalog.json entry
}

// Stage-1 citation (guideline parsing): real and populated in the actual
// engine -- p0/qc_engine/compiler/knowledge_base.py's KBSection.citation,
// e.g. "Fannie Mae Selling Guide B3-4.3-04, Personal Gifts (02/04/2026)".
export interface GuidelineCitation {
  source: string; // e.g. "Fannie Mae Selling Guide"
  sectionId: string; // e.g. "B3-4.3-04"
  title: string; // e.g. "Personal Gifts"
  revisionDate: string; // e.g. "02/04/2026"
}

// Stage-2 citation (rules compilation) fallback when no grounding applied.
// Repurposed for spec019's gold-ruleset rework (2026-08-01): gold has no workbook
// sheet/row locator, but does have stable IDs -- ruleId (an atomic rule ID when the
// parent card was decomposed, else a synthesized `${cardId}#${index}`) and cardId
// (the parent gold card, always present). See build_gold_catalog.py.
export interface SourceLocator {
  ruleId: string; // e.g. "FNM-AST-0001" or "PC::CIP DATA POINTS#0"
  cardId: string; // e.g. "PC::CIP DATA POINTS"
}

// Mirrors ruleset.py's Check — the SIGNED artifact, distinct from a per-loan CheckResult
export interface Check {
  id: string;
  name: string;
  // agree_doc_numeric added 2026-08-01: was documented in the adjacent ratio.py comment
  // and implemented in the engine, but missing from this union -- pre-existing gap,
  // unrelated to the gold-ruleset rework, fixed while this file was already being touched.
  kind: "predicate" | "ratio_threshold" | "agree_numeric" | "agree_categorical" | "agree_doc_categorical" | "agree_doc_numeric";
  category: string; // AMQ "Question Category Name" -- scopes which block's available-checks pool this shows up in
  fieldId: string;
  predicate?: "is_true" | "is_present"; // for kind=predicate only
  compareFieldId?: string; // for kind=agree_doc_categorical/agree_doc_numeric only -- mirrors ruleset.py's compare_field_name
  normalizer?: string; // for kind=agree_categorical/agree_doc_categorical
  ratio?: "ltv" | "dti" | "field_value";
  operator: "<=" | ">=" | "==" | "!=" | "<" | ">";
  threshold: string;
  severity: Severity;
  description: string;
  messagePass?: string; // shown to the reviewer when this check clears -- mirrors ruleset.py's message_pass
  messageFail?: string; // shown to the reviewer when this check fires -- mirrors ruleset.py's message_fail
  appliesIf?: { fieldId: string; operator: string; value: string }[]; // precondition gate, mirrors ruleset.py's applies_if
  sourceCondition?: string; // the raw AMQ workbook row text, for diff-and-sign
  plainEnglish?: string; // SME-readable restatement
  // Grouping (stage-2 gap #1): sibling checks sharing one questionCode trace
  // back to the same AMQ Question Code -- multiple workbook rows, one shared
  // question. NOT populated in the real engine today (taxonomy.py reads this
  // per-row as `qcode` but compile_llm.py never persists it onto the Check).
  questionCode?: string;
  questionText?: string;
  // Citation (stage-2 gap #2): a GroundingRecord IS computed at compile time
  // in the real engine (compile_llm.py's grounding retrieval) but is silently
  // discarded before the ruleset is signed -- confirmed gap, not populated in
  // production today. `sourceLocator` is the fallback when no grounding
  // applied; also unpopulated in the real engine (see SourceLocator above).
  grounding?: GuidelineCitation[];
  sourceLocator?: SourceLocator;
  // The false-clean-at-authoring-layer guard (spec019, re-platformed onto the gold
  // ruleset 2026-08-01): whether this check can actually run today, and why not if
  // not. compileState is the coarse green/yellow signal shown on a row (never reuse
  // the verdict-badge color for this -- compile state and pass/fail are different
  // axes); authorability/authorabilityReason is the detail. Populated by
  // build_gold_catalog.py.
  authorability?: Authorability;
  authorabilityReason?: string;
  compileState?: "COMPILED" | "NOT_COMPILED";
  // Area(s) of Responsibility from the gold card's finding.aor (e.g. "Underwriter",
  // "Processor") -- added 2026-08-01 for the Phase 4 built-checks filter. Real gold
  // data, previously read but not threaded onto Check by build_gold_catalog.py.
  aor?: string[];
  placeholder?: boolean;
}

export interface Block {
  id: string;
  name: string; // one per AMQ "Question Category Name" — CLAUDE.md Non-Negotiable #4
  description: string;
  checkIds: string[];
}

export interface Route {
  id: string;
  name: string;
  description: string;
  blockIds: string[];
}

export interface SignedRuleset {
  id: string;
  name: string;
  version: string;
  sha256: string;
  signedBy: string;
  signedAt: string;
  editDistance: number;
  totalRules: number;
}

// Mirrors engine.py's CheckResult exactly (field-for-field)
export interface CheckResult {
  checkId: string;
  checkName: string;
  severity: Severity;
  status: CheckStatus;
  fieldId: string;
  fieldName: string;
  phase: "RECONCILE" | "QC";
  docValue?: string;
  systemValue?: string;
  comparedValue?: string;
  rounding?: string;
  citation?: { doc: string; page: number; segment: string };
  docConfidence?: number;
  message: string;
  reviewReason?: string;
  placeholder?: boolean;
}

export interface Reconciliation {
  fieldId: string;
  fieldName: string;
  docValue: string;
  docSource: string;
  systemValue: string;
  systemSource: string;
  status: "MATCH" | "MISMATCH_FLAG";
  note: string;
}

export interface LoanEvaluation {
  loanId: string;
  overallVerdict: "PASS" | "FAIL" | "NEEDS_REVIEW";
  passedCount: number;
  failedCount: number;
  needsReviewCount: number;
  executionHash: string;
  auditTrace: CheckResult[];
  reconciliations: Reconciliation[];
}

export interface Finding {
  id: string;
  loanId: string;
  checkName: string;
  severity: Severity;
  message: string;
  // documentIds (spec021 FR-013, research.md Item 8): real Touchless documentId(s) this
  // citation resolves to, for a real (engine-computed) exception -- absent for mock
  // findings, which keep their existing text-only placeholder citation-click behavior.
  // Plural because one check (e.g. URLA_1003_final) can span more than one real document.
  citation?: { doc: string; page: number; segment: string; documentIds?: string[] };
  mitigation: "UNRESOLVED" | "OVERRIDDEN" | "ESCALATED" | "SYSTEM_CORRECTED";
  notes?: string;
}
