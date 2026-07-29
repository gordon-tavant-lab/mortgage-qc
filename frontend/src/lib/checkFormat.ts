import type { Check } from "./types";

// Kind-aware compiled-gate summary -- a ratio_threshold's operator/threshold
// doesn't mean anything for a predicate or doc-vs-doc check, so this must
// branch on kind rather than always rendering `${operator} ${threshold}`.
export function compiledGateSummary(check: Check): string {
  switch (check.kind) {
    case "predicate":
      return `${check.fieldId} ${check.predicate ?? "is_true"}`;
    case "ratio_threshold":
      return `${check.fieldId} ${check.operator} ${check.threshold}`;
    case "agree_doc_categorical":
      return `${check.fieldId} agrees_with ${check.compareFieldId ?? "(unset)"}`;
    default:
      return `${check.fieldId} agrees_with system/LOS value`;
  }
}
