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
}

export interface FieldCatalogEntry {
  fieldId: string;
  fieldName: string;
  dataType: "string" | "number" | "decimal" | "boolean" | "date";
  expectedSources: ("doc" | "los" | "mismo")[];
  citationRequired: boolean;
  placeholder?: boolean; // true = not a real p0/qc_engine/field_catalog.json entry
}

// Mirrors ruleset.py's Check — the SIGNED artifact, distinct from a per-loan CheckResult
export interface Check {
  id: string;
  name: string;
  kind: "predicate" | "ratio_threshold" | "agree_numeric" | "agree_categorical" | "agree_doc_categorical";
  fieldId: string;
  ratio?: "ltv" | "dti" | "field_value";
  operator: "<=" | ">=" | "==" | "!=" | "<" | ">";
  threshold: string;
  severity: Severity;
  description: string;
  sourceCondition?: string; // the raw AMQ workbook row text, for diff-and-sign
  plainEnglish?: string; // SME-readable restatement
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
