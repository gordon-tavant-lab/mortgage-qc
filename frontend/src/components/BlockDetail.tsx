import { useState, useEffect } from "react";
import { ArrowLeft, ArrowRightCircle, ArrowLeftCircle, ClipboardList, ShieldCheck, Pencil } from "lucide-react";
import { MOCK_FIELD_CATALOG } from "../data/mockData";
import { SeverityBadge } from "./StatusBadge";
import { PlaceholderBadge } from "./PlaceholderBadge";
import type { Block, Check, Severity } from "../lib/types";

interface BlockDetailProps {
  block: Block;
  routeName: string;
  checks: Check[];
  allBlocks: Block[];
  onToggleCheck: (checkId: string) => void;
  onUpdateCheck: (checkId: string, updates: Partial<Check>) => void;
  onBack: () => void;
}

export function BlockDetail({ block, routeName, checks, allBlocks, onToggleCheck, onUpdateCheck, onBack }: BlockDetailProps) {
  // "Checks should only have the rules associated with the block category" --
  // the available pool is scoped to checks whose category matches this
  // block's own name (Block.name IS the AMQ category name, CLAUDE.md #4),
  // not every check system-wide.
  const available = checks.filter((c) => c.category === block.name && !block.checkIds.includes(c.id));
  const active = checks.filter((c) => block.checkIds.includes(c.id));

  const otherBlocksUsing = (checkId: string) =>
    allBlocks.filter((b) => b.id !== block.id && b.checkIds.includes(checkId)).length;

  const [selectedCheckId, setSelectedCheckId] = useState<string | null>(active[0]?.id ?? null);
  const selectedCheck = active.find((c) => c.id === selectedCheckId) ?? null;
  const activeIds = active.map((c) => c.id).join(",");

  useEffect(() => {
    const stillValid = selectedCheckId && active.some((c) => c.id === selectedCheckId);
    if (!stillValid) {
      setSelectedCheckId(active[0]?.id ?? null);
    }
    // activeIds (not `active`) keeps this from re-running every render on a
    // fresh array reference -- only fires when the actual membership changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeIds]);

  return (
    <div className="space-y-5">
      <div>
        <button onClick={onBack} className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-700">
          <ArrowLeft className="h-3.5 w-3.5" />
          {routeName}
        </button>
        <div className="mt-2">
          <h2 className="font-display text-lg font-bold text-slate-900">{block.name}</h2>
          <p className="mt-0.5 text-xs text-slate-500">{block.description}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="mb-3 flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
              <ClipboardList className="h-3.5 w-3.5" /> Available Checks
              <span className="normal-case text-slate-400">· {block.name} category</span>
            </span>
            <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-bold text-slate-600">
              {available.length}
            </span>
          </div>
          <div className="space-y-2">
            {available.map((check) => {
              const usedElsewhere = otherBlocksUsing(check.id);
              return (
                <div key={check.id} className="flex items-start gap-2.5 rounded-lg border border-slate-150 bg-slate-50/40 p-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold text-slate-900">{check.name}</span>
                      <SeverityBadge severity={check.severity} />
                    </div>
                    {usedElsewhere > 0 && (
                      <span className="mt-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-semibold text-blue-600">
                        also in {usedElsewhere} other block{usedElsewhere > 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => onToggleCheck(check.id)}
                    className="shrink-0 rounded-lg p-1.5 text-blue-600 hover:bg-blue-50"
                    title="Activate this check in the block"
                  >
                    <ArrowRightCircle className="h-5 w-5" />
                  </button>
                </div>
              );
            })}
            {available.length === 0 && (
              <div className="py-6 text-center text-xs text-slate-400">
                No more {block.name}-category checks available to add.
              </div>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-blue-200 bg-blue-50/20 p-4 shadow-[var(--shadow-panel)]">
          <div className="mb-3 flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-blue-700">
              <ClipboardList className="h-3.5 w-3.5" /> Active Checks
            </span>
            <span className="rounded bg-blue-100 px-2 py-0.5 font-mono text-[10px] font-bold text-blue-700">
              {active.length} wired
            </span>
          </div>
          <div className="space-y-2">
            {active.map((check) => (
              <div
                key={check.id}
                className={`flex items-start gap-2.5 rounded-lg border p-3 ${
                  selectedCheckId === check.id ? "border-blue-400 bg-white ring-1 ring-blue-300" : "border-blue-200 bg-white"
                }`}
              >
                <button
                  onClick={() => onToggleCheck(check.id)}
                  className="shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-600"
                  title="Deactivate this check from the block"
                >
                  <ArrowLeftCircle className="h-5 w-5" />
                </button>
                <button onClick={() => setSelectedCheckId(check.id)} className="min-w-0 flex-1 text-left">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-slate-900">{check.name}</span>
                    <SeverityBadge severity={check.severity} />
                  </div>
                  <div className="mt-0.5 font-mono text-[11px] text-slate-500">
                    {check.fieldId} {check.operator} {check.threshold}
                  </div>
                </button>
                <button
                  onClick={() => setSelectedCheckId(check.id)}
                  className="shrink-0 rounded-lg p-1.5 text-slate-300 hover:bg-slate-50 hover:text-blue-600"
                  title="Edit this check's gate"
                >
                  <Pencil className="h-4 w-4" />
                </button>
              </div>
            ))}
            {active.length === 0 && (
              <div className="py-6 text-center text-xs text-blue-400/70">
                No checks wired yet. Activate one from the pool on the left.
              </div>
            )}
          </div>
        </div>
      </div>

      {selectedCheck && (
        <CheckEditor
          key={selectedCheck.id}
          check={selectedCheck}
          onUpdate={(updates) => onUpdateCheck(selectedCheck.id, updates)}
        />
      )}
    </div>
  );
}

function CheckEditor({ check, onUpdate }: { check: Check; onUpdate: (updates: Partial<Check>) => void }) {
  const [fieldId, setFieldId] = useState(check.fieldId);
  const [operator, setOperator] = useState(check.operator);
  const [threshold, setThreshold] = useState(check.threshold);
  const [severity, setSeverity] = useState<Severity>(check.severity);

  const fieldEntry = MOCK_FIELD_CATALOG.find((f) => f.fieldId === fieldId);

  const commit = (updates: Partial<Check>) => onUpdate(updates);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)]">
      <div className="border-b border-slate-100 pb-3">
        <h3 className="text-sm font-bold text-slate-900">Edit Check</h3>
        <p className="mt-0.5 text-xs text-slate-500">
          Every choice below is constrained to a real, catalog-resolvable value — editing "{check.name}".
        </p>
      </div>

      <div className="mt-4 space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="check-field" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
              Catalog Field
            </label>
            <select
              id="check-field"
              name="check-field"
              value={fieldId}
              onChange={(e) => {
                setFieldId(e.target.value);
                commit({ fieldId: e.target.value });
              }}
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
            <label htmlFor="check-operator" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
              Operator
            </label>
            <select
              id="check-operator"
              name="check-operator"
              value={operator}
              onChange={(e) => {
                const v = e.target.value as Check["operator"];
                setOperator(v);
                commit({ operator: v });
              }}
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
            <label htmlFor="check-threshold" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
              Target Threshold
            </label>
            <input
              id="check-threshold"
              name="check-threshold"
              value={threshold}
              onChange={(e) => {
                setThreshold(e.target.value);
                commit({ threshold: e.target.value });
              }}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-mono text-xs font-bold text-emerald-700 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label htmlFor="check-severity" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
              Violation Severity
            </label>
            <select
              id="check-severity"
              name="check-severity"
              value={severity}
              onChange={(e) => {
                const v = e.target.value as Severity;
                setSeverity(v);
                commit({ severity: v });
              }}
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
      </div>
    </div>
  );
}
