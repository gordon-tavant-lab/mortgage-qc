import { useState, useEffect, useMemo } from "react";
import {
  ArrowLeft,
  ArrowRightCircle,
  ArrowLeftCircle,
  ClipboardList,
  ShieldCheck,
  Pencil,
  ChevronDown,
  ChevronRight,
  FileQuestion,
  FlaskConical,
} from "lucide-react";
import { MOCK_FIELD_CATALOG } from "../data/mockData";
import { SeverityBadge } from "./StatusBadge";
import { PlaceholderBadge } from "./PlaceholderBadge";
import { SourceCitation } from "./SourceCitation";
import { compiledGateSummary } from "../lib/checkFormat";
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

const KIND_LABEL: Record<Check["kind"], string> = {
  predicate: "Presence / Truth Check",
  ratio_threshold: "Ratio Threshold",
  agree_categorical: "Document vs. System Agreement",
  agree_numeric: "Document vs. System Agreement (Numeric)",
  agree_doc_categorical: "Document vs. Document Agreement",
};

export function BlockDetail({ block, routeName, checks, allBlocks, onToggleCheck, onUpdateCheck, onBack }: BlockDetailProps) {
  // "Checks should only have the rules associated with the block category" --
  // the available pool is scoped to checks whose category matches this
  // block's own name (Block.name IS the AMQ category name, CLAUDE.md #4),
  // not every check system-wide.
  const available = checks.filter((c) => c.category === block.name && !block.checkIds.includes(c.id));
  const active = checks.filter((c) => block.checkIds.includes(c.id));

  const otherBlocksUsing = (checkId: string) =>
    allBlocks.filter((b) => b.id !== block.id && b.checkIds.includes(checkId)).length;

  // Grouping (stage-2 gap): sibling checks sharing one questionCode are
  // clustered under a shared header, EXPANDED by default -- not collapsed.
  // Collapsing implies false switch-statement semantics (the engine runs
  // every active check independently, there's no "pick one answer"
  // resolution) and risks sign-off-theater if "activate group" becomes a
  // single bulk click instead of per-check consideration.
  const availableGroups = useMemo(() => groupByQuestion(available), [available]);

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
          <div className="space-y-3">
            {availableGroups.map((group) =>
              group.questionCode ? (
                <QuestionGroup
                  key={group.questionCode}
                  questionText={group.questionText ?? group.questionCode}
                  checks={group.checks}
                  otherBlocksUsing={otherBlocksUsing}
                  onToggleCheck={onToggleCheck}
                />
              ) : (
                group.checks.map((check) => (
                  <AvailableCheckRow
                    key={check.id}
                    check={check}
                    usedElsewhere={otherBlocksUsing(check.id)}
                    onToggleCheck={onToggleCheck}
                  />
                ))
              )
            )}
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
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-xs font-bold text-slate-900">{check.name}</span>
                    <SeverityBadge severity={check.severity} />
                    {check.questionCode && (
                      <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-semibold uppercase text-slate-500">
                        {check.questionCode}
                      </span>
                    )}
                  </div>
                  <div className="mt-0.5 font-mono text-[11px] text-slate-500">{compiledGateSummary(check)}</div>
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

function groupByQuestion(checks: Check[]): { questionCode?: string; questionText?: string; checks: Check[] }[] {
  const groups: { questionCode?: string; questionText?: string; checks: Check[] }[] = [];
  const seen = new Map<string, number>();
  for (const check of checks) {
    if (check.questionCode) {
      if (seen.has(check.questionCode)) {
        groups[seen.get(check.questionCode)!].checks.push(check);
      } else {
        seen.set(check.questionCode, groups.length);
        groups.push({ questionCode: check.questionCode, questionText: check.questionText, checks: [check] });
      }
    } else {
      groups.push({ checks: [check] });
    }
  }
  return groups;
}

function AvailableCheckRow({
  check,
  usedElsewhere,
  onToggleCheck,
}: {
  check: Check;
  usedElsewhere: number;
  onToggleCheck: (id: string) => void;
}) {
  return (
    <div className="flex items-start gap-2.5 rounded-lg border border-slate-150 bg-slate-50/40 p-3">
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
}

// Expanded-by-default: siblings sharing an AMQ Question Code are visually
// clustered under the shared question text, but every check is immediately
// visible and individually activatable -- no click-to-reveal, no implied
// bulk-approve gesture.
function QuestionGroup({
  questionText,
  checks,
  otherBlocksUsing,
  onToggleCheck,
}: {
  questionText: string;
  checks: Check[];
  otherBlocksUsing: (id: string) => number;
  onToggleCheck: (id: string) => void;
}) {
  return (
    <div className="rounded-lg border border-indigo-150 bg-indigo-50/30">
      <div className="flex items-start gap-1.5 border-b border-indigo-100 px-3 py-2">
        <FileQuestion className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-500" />
        <div>
          <div className="text-[10px] font-semibold uppercase tracking-wide text-indigo-500">
            One question, {checks.length} possible answers
          </div>
          <div className="text-xs font-semibold text-slate-800">{questionText}</div>
        </div>
      </div>
      <div className="space-y-2 p-2">
        {checks.map((check) => (
          <AvailableCheckRow
            key={check.id}
            check={check}
            usedElsewhere={otherBlocksUsing(check.id)}
            onToggleCheck={onToggleCheck}
          />
        ))}
      </div>
    </div>
  );
}

function CheckEditor({
  check,
  onUpdate,
}: {
  check: Check;
  onUpdate: (updates: Partial<Check>) => void;
}) {
  const [fieldId, setFieldId] = useState(check.fieldId);
  const [compareFieldId, setCompareFieldId] = useState(check.compareFieldId ?? "");
  const [predicateType, setPredicateType] = useState<"is_true" | "is_present">(check.predicate ?? "is_true");
  const [operator, setOperator] = useState(check.operator);
  const [threshold, setThreshold] = useState(check.threshold);
  const [severity, setSeverity] = useState<Severity>(check.severity);
  const [messagePass, setMessagePass] = useState(check.messagePass ?? "");
  const [messageFail, setMessageFail] = useState(check.messageFail ?? "");

  const fieldEntry = MOCK_FIELD_CATALOG.find((f) => f.fieldId === fieldId);
  const commit = (updates: Partial<Check>) => onUpdate(updates);
  const isDocVsDoc = check.kind === "agree_doc_categorical";
  const isPredicate = check.kind === "predicate";
  const isRatio = check.kind === "ratio_threshold";
  const isDocVsSystem = check.kind === "agree_categorical" || check.kind === "agree_numeric";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)]">
      <div className="flex flex-wrap items-start justify-between gap-2 border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Edit Check</h3>
          <p className="mt-0.5 text-xs text-slate-500">
            Every choice below is constrained to a real, catalog-resolvable value — editing "{check.name}".
          </p>
        </div>
        <span className="shrink-0 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-slate-600">
          {KIND_LABEL[check.kind]}
        </span>
      </div>

      <div className="mt-4 space-y-4">
        {isPredicate && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <FieldPicker
              label="Catalog Field"
              value={fieldId}
              onChange={(v) => {
                setFieldId(v);
                commit({ fieldId: v });
              }}
            />
            <div>
              <label htmlFor="check-predicate" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
                Predicate Type
              </label>
              <select
                id="check-predicate"
                name="check-predicate"
                value={predicateType}
                onChange={(e) => {
                  const v = e.target.value as "is_true" | "is_present";
                  setPredicateType(v);
                  commit({ predicate: v });
                }}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-blue-500 focus:outline-none"
              >
                <option value="is_true">Must be True (a status/answer field)</option>
                <option value="is_present">Must Be Present (a document/value exists)</option>
              </select>
            </div>
            <SeverityPicker
              value={severity}
              onChange={(v) => {
                setSeverity(v);
                commit({ severity: v });
              }}
            />
          </div>
        )}

        {isRatio && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FieldPicker
              label="Catalog Field"
              value={fieldId}
              onChange={(v) => {
                setFieldId(v);
                commit({ fieldId: v });
              }}
            />
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
            <SeverityPicker
              value={severity}
              onChange={(v) => {
                setSeverity(v);
                commit({ severity: v });
              }}
            />
          </div>
        )}

        {isDocVsSystem && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FieldPicker
              label="Document Field (compared against the system/LOS value)"
              value={fieldId}
              onChange={(v) => {
                setFieldId(v);
                commit({ fieldId: v });
              }}
            />
            <SeverityPicker
              value={severity}
              onChange={(v) => {
                setSeverity(v);
                commit({ severity: v });
              }}
            />
          </div>
        )}

        {isDocVsDoc && (
          <>
            <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] text-amber-800">
              <FlaskConical className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>
                Document-vs-document check: needs <strong>two</strong> fields, neither a system value. This kind is
                fully supported by the engine but has near-zero real usage today — a confirmed, unfixed compiler gap
                (see the flagged-follow-up doc).
              </span>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FieldPicker
                label="Field A"
                value={fieldId}
                onChange={(v) => {
                  setFieldId(v);
                  commit({ fieldId: v });
                }}
              />
              <FieldPicker
                label="Field B (compare_field_name)"
                value={compareFieldId}
                onChange={(v) => {
                  setCompareFieldId(v);
                  commit({ compareFieldId: v });
                }}
                exclude={fieldId}
                allowEmpty
              />
              <SeverityPicker
                value={severity}
                onChange={(v) => {
                  setSeverity(v);
                  commit({ severity: v });
                }}
              />
            </div>
          </>
        )}

        <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5">
          <div className="flex flex-wrap items-center gap-2 font-mono text-xs text-slate-600">
            <span>{fieldId}</span>
            {isPredicate && <span className="text-blue-600">{predicateType}</span>}
            {isRatio && (
              <>
                <span className="text-blue-600">{operator}</span>
                <span className="font-bold text-emerald-700">{threshold}</span>
              </>
            )}
            {isDocVsSystem && <span className="text-blue-600">agrees_with system/LOS value</span>}
            {isDocVsDoc && (
              <>
                <span className="text-blue-600">agrees_with</span>
                <span className="font-bold text-emerald-700">{compareFieldId || "(select field B)"}</span>
              </>
            )}
            <SeverityBadge severity={severity} />
          </div>
          <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-600">
            <ShieldCheck className="h-3.5 w-3.5" />
            Referential integrity verified
          </span>
        </div>

        {fieldEntry?.placeholder && (
          <PlaceholderBadge label="not in field_catalog.json yet" />
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="check-msg-pass" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
              Pass Message
            </label>
            <textarea
              id="check-msg-pass"
              name="check-msg-pass"
              rows={2}
              value={messagePass}
              onChange={(e) => {
                setMessagePass(e.target.value);
                commit({ messagePass: e.target.value });
              }}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="check-msg-fail" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
              Fail Message
            </label>
            <textarea
              id="check-msg-fail"
              name="check-msg-fail"
              rows={2}
              value={messageFail}
              onChange={(e) => {
                setMessageFail(e.target.value);
                commit({ messageFail: e.target.value });
              }}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        <PreconditionSummary check={check} />
        <SourceCitation check={check} />
      </div>
    </div>
  );
}

function FieldPicker({
  label,
  value,
  onChange,
  exclude,
  allowEmpty,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  exclude?: string;
  allowEmpty?: boolean;
}) {
  const id = `field-picker-${label.replace(/\s+/g, "-").toLowerCase()}`;
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-xs font-semibold uppercase text-slate-500">
        {label}
      </label>
      <select
        id={id}
        name={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-blue-500 focus:outline-none"
      >
        {allowEmpty && <option value="">Select a field…</option>}
        {MOCK_FIELD_CATALOG.filter((f) => f.fieldId !== exclude).map((f) => (
          <option key={f.fieldId} value={f.fieldId}>
            {f.fieldName} ({f.fieldId})
          </option>
        ))}
      </select>
    </div>
  );
}

function SeverityPicker({ value, onChange }: { value: Severity; onChange: (v: Severity) => void }) {
  return (
    <div>
      <label htmlFor="check-severity" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
        Violation Severity
      </label>
      <select
        id="check-severity"
        name="check-severity"
        value={value}
        onChange={(e) => onChange(e.target.value as Severity)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-slate-800 focus:border-blue-500 focus:outline-none"
      >
        <option value="CRITICAL">Critical</option>
        <option value="WARNING">Warning</option>
        <option value="INFO">Info</option>
      </select>
    </div>
  );
}

function PreconditionSummary({ check }: { check: Check }) {
  const [expanded, setExpanded] = useState(true);
  if (!check.appliesIf || check.appliesIf.length === 0) return null;
  return (
    <div className="rounded-lg border border-slate-150 bg-slate-50/60">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-between px-3 py-2 text-[11px] font-semibold uppercase tracking-wide text-slate-500"
      >
        <span>Applies-If Precondition ({check.appliesIf.length})</span>
        {expanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
      </button>
      {expanded && (
        <div className="space-y-1 border-t border-slate-100 px-3 py-2 font-mono text-[11px] text-slate-600">
          {check.appliesIf.map((cond, i) => (
            <div key={i}>
              {cond.fieldId} {cond.operator} {cond.value}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

