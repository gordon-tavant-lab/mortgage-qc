import { useState } from "react";
import { Layers, GitFork, ToggleLeft, ToggleRight, ShieldCheck, PlusCircle } from "lucide-react";
import { MOCK_CHECKS, MOCK_BLOCKS, MOCK_ROUTES, MOCK_FIELD_CATALOG } from "../data/mockData";
import { SampleDataBanner } from "./SampleDataBanner";
import { PlaceholderBadge } from "./PlaceholderBadge";
import { SeverityBadge } from "./StatusBadge";
import type { Severity } from "../lib/types";

export function GuidedEditorView() {
  const [selectedRouteId, setSelectedRouteId] = useState(MOCK_ROUTES[0].id);
  const [selectedCheckId, setSelectedCheckId] = useState(MOCK_CHECKS[0].id);
  const route = MOCK_ROUTES.find((r) => r.id === selectedRouteId)!;
  const check = MOCK_CHECKS.find((c) => c.id === selectedCheckId)!;
  const [fieldId, setFieldId] = useState(check.fieldId);
  const [operator, setOperator] = useState(check.operator);
  const [threshold, setThreshold] = useState(check.threshold);
  const [severity, setSeverity] = useState<Severity>(check.severity);

  const selectCheck = (id: string) => {
    const c = MOCK_CHECKS.find((x) => x.id === id)!;
    setSelectedCheckId(id);
    setFieldId(c.fieldId);
    setOperator(c.operator);
    setThreshold(c.threshold);
    setSeverity(c.severity);
  };

  // Referential integrity by construction: fieldId can only ever be a value
  // picked from the real catalog dropdown below — there is no way to type an
  // unresolved reference into this control (009b's SAFE-gate-by-construction).
  const fieldEntry = MOCK_FIELD_CATALOG.find((f) => f.fieldId === fieldId);

  return (
    <div className="space-y-6 pb-12">
      <SampleDataBanner />

      <div>
        <h2 className="font-display text-xl font-bold text-slate-900">Author — Guided Editor</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          Catalog-constrained controls only — pick the field, pick the operator, pick the value.
          This surface owns the criteria gate so free text never does (Tension 8). No AI drafting
          in this view, by decision.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="space-y-6 lg:col-span-4">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
            <div className="mb-3 flex items-center justify-between">
              <label htmlFor="route-select" className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
                <GitFork className="h-3.5 w-3.5" /> Route
              </label>
            </div>
            <select
              id="route-select"
              name="route-select"
              value={selectedRouteId}
              onChange={(e) => setSelectedRouteId(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-800 focus:border-blue-500 focus:outline-none"
            >
              {MOCK_ROUTES.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
            <p className="mt-2 text-xs italic text-slate-500">"{route.description}"</p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
            <div className="mb-3 flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
                <Layers className="h-3.5 w-3.5" /> Blocks
              </span>
              <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-bold text-slate-600">
                {route.blockIds.length} wired
              </span>
            </div>
            <div className="space-y-2">
              {MOCK_BLOCKS.map((block) => {
                const isWired = route.blockIds.includes(block.id);
                return (
                  <div
                    key={block.id}
                    className={`flex items-start gap-2.5 rounded-lg border p-3 ${
                      isWired ? "border-blue-200 bg-blue-50/30" : "border-slate-150 bg-slate-50/30 text-slate-400"
                    }`}
                  >
                    <div className="flex-1">
                      <div className="text-xs font-bold text-slate-900">{block.name}</div>
                      <p className="mt-0.5 text-[11px] leading-snug text-slate-500">{block.description}</p>
                    </div>
                    {isWired ? (
                      <ToggleRight className="h-5 w-8 shrink-0 text-blue-600" />
                    ) : (
                      <ToggleLeft className="h-5 w-8 shrink-0 text-slate-400" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)] lg:col-span-8">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Edit Check</h3>
              <p className="mt-0.5 text-xs text-slate-500">Every choice below is constrained to a real, catalog-resolvable value.</p>
            </div>
            <label htmlFor="check-select" className="sr-only">Select check to edit</label>
            <select
              id="check-select"
              name="check-select"
              value={selectedCheckId}
              onChange={(e) => selectCheck(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 focus:border-blue-500 focus:outline-none"
            >
              {MOCK_CHECKS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="check-field" className="mb-1 block text-xs font-semibold uppercase text-slate-500">Catalog Field</label>
                <select
                  id="check-field"
                  name="check-field"
                  value={fieldId}
                  onChange={(e) => setFieldId(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-blue-500 focus:outline-none"
                >
                  {MOCK_FIELD_CATALOG.map((f) => (
                    <option key={f.fieldId} value={f.fieldId}>
                      {f.fieldName} ({f.fieldId})
                    </option>
                  ))}
                </select>
                {fieldEntry?.placeholder && (
                  <div className="mt-1.5">
                    <PlaceholderBadge label="not in field_catalog.json yet" />
                  </div>
                )}
              </div>

              <div>
                <label htmlFor="check-operator" className="mb-1 block text-xs font-semibold uppercase text-slate-500">Operator</label>
                <select
                  id="check-operator"
                  name="check-operator"
                  value={operator}
                  onChange={(e) => setOperator(e.target.value as typeof operator)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-mono text-xs font-bold text-slate-800 focus:border-blue-500 focus:outline-none"
                >
                  <option value="<=">&le; (less than or equal)</option>
                  <option value=">=">&ge; (greater than or equal)</option>
                  <option value="==">== (exact equal)</option>
                  <option value="!=">!= (not equal)</option>
                  <option value="<">&lt; (less than)</option>
                  <option value=">">&gt; (greater than)</option>
                </select>
              </div>

              <div>
                <label htmlFor="check-threshold" className="mb-1 block text-xs font-semibold uppercase text-slate-500">Target Threshold</label>
                <input
                  id="check-threshold"
                  name="check-threshold"
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-mono text-xs font-bold text-emerald-700 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="check-severity" className="mb-1 block text-xs font-semibold uppercase text-slate-500">Violation Severity</label>
                <select
                  id="check-severity"
                  name="check-severity"
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value as Severity)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-slate-800 focus:border-blue-500 focus:outline-none"
                >
                  <option value="CRITICAL">Critical</option>
                  <option value="WARNING">Warning</option>
                  <option value="INFO">Info</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5">
              <div className="flex items-center gap-2 font-mono text-xs text-slate-600">
                <span>{fieldId}</span>
                <span className="text-blue-600">{operator}</span>
                <span className="font-bold text-emerald-700">{threshold}</span>
                <SeverityBadge severity={severity} />
              </div>
              <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-600">
                <ShieldCheck className="h-3.5 w-3.5" />
                Referential integrity verified
              </span>
            </div>

            <button className="flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700">
              <PlusCircle className="h-3.5 w-3.5" />
              Add another check to this block
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
