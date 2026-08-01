// Data shapes mirror p0/qc_engine's real classes:
//   CheckResult   -> p0/qc_engine/engine.py:46
//   Check         -> p0/qc_engine/ruleset.py:49 (operator/threshold/ratio live HERE, not on CheckResult)
//   field catalog -> p0/qc_engine/field_catalog.json (385 real entries)
// Anything without a real backend counterpart today (e.g. reserve-months)
// is flagged inline as PLACEHOLDER — never silently presented as real.

export type Severity = "CRITICAL" | "WARNING" | "INFO";
export type CheckStatus = "PASS" | "FAIL" | "WARNING" | "FLAG" | "NEEDS_REVIEW" | "NOT_APPLICABLE";
export type LoanStatus = "PENDING" | "AUTO_CLEARED" | "EXCEPTION" | "RESOLVED";

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

// Stage-2 citation (rules compilation) fallback when no grounding applied --
// the raw AMQ workbook row locator. NOT populated in the real engine today:
// taxonomy.py's load_rows() discards openpyxl's row index/sheet name entirely
// (confirmed gap, see output/CITATION-AND-COMPILER-GAPS-2026-07-29.md).
export interface SourceLocator {
  workbook: string; // e.g. "PF and PC Sept 2025 AMQs - Retail.xlsx"
  sheet: string; // e.g. "Post-Closing"
  row: number; // e.g. 1142
}

// Mirrors ruleset.py's Check — the SIGNED artifact, distinct from a per-loan CheckResult
export interface Check {
  id: string;
  name: string;
  kind: "predicate" | "ratio_threshold" | "agree_numeric" | "agree_categorical" | "agree_doc_categorical";
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

export interface SourceAlignmentRow {
  fieldId: string;
  fieldName: string;
  docValue: string | null;
  losValue: string | null;
  mismoValue: string | null;
  aligned: boolean;
}

export interface Finding {
  id: string;
  loanId: string;
  checkName: string;
  severity: Severity;
  message: string;
  citation?: { doc: string; page: number; segment: string };
  mitigation: "UNRESOLVED" | "OVERRIDDEN" | "ESCALATED" | "SYSTEM_CORRECTED";
  notes?: string;
}
