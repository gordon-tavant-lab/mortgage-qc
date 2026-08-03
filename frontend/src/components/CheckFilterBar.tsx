import { useMemo } from "react";
import type { Check } from "../lib/types";

// Extracted from BlockDetail.tsx (spec019 Phase 4) so ApplyView.tsx's per-loan check
// list (spec021, live demo walkthrough finding) can reuse the exact same filter UX
// instead of a second, divergent implementation.

export const ALL = "ALL";

export interface CheckFilterState {
  query: string;
  severity: string;
  kind: string;
  aor: string;
}

export const EMPTY_CHECK_FILTER: CheckFilterState = { query: "", severity: ALL, kind: ALL, aor: ALL };

export const KIND_LABEL: Record<Check["kind"], string> = {
  predicate: "Presence / Truth Check",
  ratio_threshold: "Ratio Threshold",
  agree_categorical: "Document vs. System Agreement",
  agree_numeric: "Document vs. System Agreement (Numeric)",
  agree_doc_categorical: "Document vs. Document Agreement",
  agree_doc_numeric: "Document vs. Document Agreement (Numeric)",
};

export function filterChecks(checks: Check[], f: CheckFilterState): Check[] {
  const q = f.query.trim().toLowerCase();
  return checks.filter(
    (c) =>
      (f.severity === ALL || c.severity === f.severity) &&
      (f.kind === ALL || c.kind === f.kind) &&
      (f.aor === ALL || (c.aor ?? []).includes(f.aor)) &&
      (q === "" || c.name.toLowerCase().includes(q) || c.description.toLowerCase().includes(q))
  );
}

// Options are derived from whichever check list this bar is filtering, not a static
// enum -- a dropdown never offers a value that would produce zero results in its own list.
export function CheckFilterBar({
  checks,
  value,
  onChange,
}: {
  checks: Check[];
  value: CheckFilterState;
  onChange: (v: CheckFilterState) => void;
}) {
  const severities = useMemo(() => Array.from(new Set(checks.map((c) => c.severity))).sort(), [checks]);
  const kinds = useMemo(() => Array.from(new Set(checks.map((c) => c.kind))).sort(), [checks]);
  const aors = useMemo(() => Array.from(new Set(checks.flatMap((c) => c.aor ?? []))).sort(), [checks]);

  return (
    <div className="mb-3 flex flex-wrap items-center gap-1.5">
      <input
        type="search"
        value={value.query}
        onChange={(e) => onChange({ ...value, query: e.target.value })}
        placeholder="Search name or description…"
        className="w-full min-w-[140px] flex-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-[11px] text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
      />
      <FilterSelect
        label="Severity"
        value={value.severity}
        onChange={(v) => onChange({ ...value, severity: v })}
        options={severities}
      />
      <FilterSelect
        label="Kind"
        value={value.kind}
        onChange={(v) => onChange({ ...value, kind: v })}
        options={kinds}
        labelMap={KIND_LABEL}
        widthClassName="w-20"
      />
      <FilterSelect label="AOR" value={value.aor} onChange={(v) => onChange({ ...value, aor: v })} options={aors} />
    </div>
  );
}

function FilterSelect({
  label,
  value,
  onChange,
  options,
  labelMap,
  widthClassName = "w-24",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
  labelMap?: Record<string, string>;
  widthClassName?: string;
}) {
  const id = `check-filter-${label.toLowerCase()}`;
  return (
    <div className="flex items-center gap-1.5">
      <label htmlFor={id} className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </label>
      <select
        id={id}
        name={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        title={value === ALL ? undefined : labelMap?.[value] ?? value}
        className={`truncate rounded-lg border border-slate-200 bg-white px-2 py-1 text-[11px] font-medium text-slate-700 focus:border-blue-500 focus:outline-none ${widthClassName}`}
      >
        <option value={ALL}>All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {labelMap?.[o] ?? o}
          </option>
        ))}
      </select>
    </div>
  );
}
