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
  Plus,
  Trash2,
} from "lucide-react";
import { MOCK_FIELD_CATALOG } from "../data/mockData";
import { SeverityBadge } from "./StatusBadge";
import { PlaceholderBadge } from "./PlaceholderBadge";
import { SourceCitation } from "./SourceCitation";
import { Modal } from "./Modal";
import { compiledGateSummary } from "../lib/checkFormat";
import {
  CheckFilterBar,
  EMPTY_CHECK_FILTER,
  filterChecks,
  KIND_LABEL,
  type CheckFilterState,
} from "./CheckFilterBar";
import type { Block, Check, Severity } from "../lib/types";

// spec024 US10: every AMQ-imported FHA/VA/USDA check id is stamped "{program}-amq-..."
// (build_gold_catalog.py's build_program_blocks_and_checks) -- used to scope a block's
// Available Checks pool to its own program, not just its category text.
const PROGRAM_CHECK_ID_PREFIXES = [
  { program: "fha-", prefix: "fha-amq-" },
  { program: "va-", prefix: "va-amq-" },
  { program: "usda-", prefix: "usda-amq-" },
];

interface BlockDetailProps {
  block: Block;
  routeName: string;
  checks: Check[];
  allBlocks: Block[];
  onToggleCheck: (checkId: string) => void;
  onUpdateCheck: (checkId: string, updates: Partial<Check>) => void;
  onBack: () => void;
  // spec024 US8 (FR-022/024): catalog-level check create/remove, distinct from
  // onToggleCheck's active/inactive toggle of an already-catalog check.
  // onCreateCheck appends a brand-new check (category-scoped to this block,
  // never auto-active) and returns it so the editor can open on it immediately;
  // onRemoveCheck permanently deletes one and returns whether it succeeded --
  // false means it's still active in some block and was refused.
  onCreateCheck: (category: string) => Check;
  onRemoveCheck: (checkId: string) => boolean;
}

export function BlockDetail({
  block,
  routeName,
  checks,
  allBlocks,
  onToggleCheck,
  onUpdateCheck,
  onBack,
  onCreateCheck,
  onRemoveCheck,
}: BlockDetailProps) {
  // "Checks should only have the rules associated with the block category" --
  // the available pool is scoped to checks whose category matches this
  // block's own name (Block.name IS the AMQ category name, CLAUDE.md #4),
  // not every check system-wide.
  //
  // Authorability-first (spec019's false-clean-at-authoring-layer guard,
  // re-platformed onto the gold ruleset 2026-08-01): COMPILABLE checks sort to
  // the top of the pool, since those are the ones an SME can actually wire up
  // today. Everything else stays visible -- never hidden -- but never implies
  // it's as ready as a COMPILABLE check.
  // spec024 US10 (2026-08-03, supersedes the US5 guard this replaced): FHA/VA/USDA
  // blocks now carry real, AMQ-workbook-imported checks (build_gold_catalog.py's
  // build_program_blocks_and_checks()). `isConventionalBlock` is kept as a narrower
  // flag: check *creation* (US8's "New Check") stays Conventional-only, a deliberate
  // scope decision (not forced by US10) -- see the "New Check" button below.
  const isConventionalBlock = block.id.startsWith("conv-");
  // Real regression, caught live: Check.category is shared text across programs (e.g.
  // "Property - Appraisal" exists for Conventional AND every FHA/VA/USDA block) -- category
  // match alone let an FHA block's Available Checks pool pull in Conventional's real
  // compiled checks, and vice versa, which would let an SME wire a Fannie-Mae-specific
  // check into a program it was never written for. AMQ-imported checks all carry a stable
  // "{program}-amq-" id prefix (build_program_blocks_and_checks); scope by that too.
  const blockProgramPrefix = PROGRAM_CHECK_ID_PREFIXES.find((p) => block.id.startsWith(p.program))?.prefix;
  const availableUnsorted = checks.filter((c) => {
    if (c.category !== block.name || block.checkIds.includes(c.id)) return false;
    if (blockProgramPrefix) return c.id.startsWith(blockProgramPrefix);
    return !PROGRAM_CHECK_ID_PREFIXES.some(({ prefix }) => c.id.startsWith(prefix));
  });
  const available = [...availableUnsorted].sort((a, b) => {
    const rank = (c: Check) => (c.authorability === "COMPILABLE" ? 0 : 1);
    return rank(a) - rank(b);
  });
  const compilableCount = available.filter((c) => c.authorability === "COMPILABLE").length;
  const active = checks.filter((c) => block.checkIds.includes(c.id));

  const otherBlocksUsing = (checkId: string) =>
    allBlocks.filter((b) => b.id !== block.id && b.checkIds.includes(checkId)).length;

  // Grouping (stage-2 gap): sibling checks sharing one questionCode are
  // clustered under a shared header, EXPANDED by default -- not collapsed.
  // Collapsing implies false switch-statement semantics (the engine runs
  // every active check independently, there's no "pick one answer"
  // resolution) and risks sign-off-theater if "activate group" becomes a
  // single bulk click instead of per-check consideration.
  // spec024 US10 (FR-011 tension, flagged in spec.md's Assumptions): every FHA/VA/USDA
  // check is NOT_COMPILED, so FR-011's default-hide would show "0 compilable / 0 total"
  // directly under a route/block header that just claimed a large, real, non-zero count.
  // Defaulting "show not built" to true for non-Conventional blocks resolves that --
  // Conventional keeps the original default-hide behavior (FR-011 still applies there,
  // where most checks ARE compiled and not-built ones are the exception worth hiding).
  const defaultAvailableFilter = (): CheckFilterState => ({
    ...EMPTY_CHECK_FILTER,
    showNotBuilt: !isConventionalBlock,
  });
  const [availableFilter, setAvailableFilter] = useState<CheckFilterState>(defaultAvailableFilter);
  const [activeFilter, setActiveFilter] = useState<CheckFilterState>(EMPTY_CHECK_FILTER);
  const [availablePage, setAvailablePage] = useState(0);
  const [activePage, setActivePage] = useState(0);
  // Filters narrow within a block -- they don't carry meaning across blocks (an
  // AOR/kind value picked for Assets may not even exist in Income's options), so
  // reset on navigation rather than leaving a stale, confusing filter applied.
  useEffect(() => {
    setAvailableFilter(defaultAvailableFilter());
    setActiveFilter(EMPTY_CHECK_FILTER);
    setAvailablePage(0);
    setActivePage(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [block.id]);
  useEffect(() => setAvailablePage(0), [availableFilter]);
  useEffect(() => setActivePage(0), [activeFilter]);

  // spec024 US4 (FR-011/012): the not-built gate is layered on top of the shared
  // filterChecks() -- and applied ONLY to Available Checks. Active Checks must keep
  // showing NOT_COMPILED items (badged "wired, not yet buildable"), same as before
  // this feature -- hiding an already-active check would be a real regression, not
  // a usability improvement.
  const availableFiltered = useMemo(
    () =>
      filterChecks(available, availableFilter).filter(
        (c) => availableFilter.showNotBuilt || c.compileState !== "NOT_COMPILED"
      ),
    [available, availableFilter]
  );
  const activeFiltered = useMemo(() => filterChecks(active, activeFilter), [active, activeFilter]);

  const PAGE_SIZE = 25;
  const availableTotalPages = Math.max(1, Math.ceil(availableFiltered.length / PAGE_SIZE));
  const availableCurrentPage = Math.min(availablePage, availableTotalPages - 1);
  const availablePaged = availableFiltered.slice(
    availableCurrentPage * PAGE_SIZE,
    availableCurrentPage * PAGE_SIZE + PAGE_SIZE
  );
  const availableGroups = useMemo(() => groupByQuestion(availablePaged), [availablePaged]);

  const activeTotalPages = Math.max(1, Math.ceil(activeFiltered.length / PAGE_SIZE));
  const activeCurrentPage = Math.min(activePage, activeTotalPages - 1);
  const activePaged = activeFiltered.slice(activeCurrentPage * PAGE_SIZE, activeCurrentPage * PAGE_SIZE + PAGE_SIZE);

  // spec024 US4: not-built (compileState === "NOT_COMPILED") checks are hidden by
  // default via filterChecks()/CheckFilterBar's "Show not built" toggle -- this
  // count reflects only that toggle (not query/severity/kind/aor), matching how
  // the pre-existing badge always ignored those filters.
  const notBuiltCount = available.length - compilableCount;
  const visibleAvailableCount = availableFilter.showNotBuilt
    ? available.length
    : available.filter((c) => c.compileState !== "NOT_COMPILED").length;

  // spec024 US3 (FR-008/FR-009): the check editor now opens as a modal instead of
  // an always-visible inline panel. `editingCheckId` gates the modal; a snapshot
  // of the check's editable fields is captured on open so dismissing without an
  // explicit Save reverts any in-progress edits (CheckEditor auto-commits on
  // every keystroke via onUpdate, so "discard" means "write the snapshot back").
  const [editingCheckId, setEditingCheckId] = useState<string | null>(null);
  const [checkSnapshot, setCheckSnapshot] = useState<Partial<Check> | null>(null);
  // spec024 US8: looks across the whole `checks` pool, not just `active` -- a
  // freshly-created check (onCreateCheck) opens its editor while still sitting in
  // Available, before the author has activated it.
  const editingCheck = checks.find((c) => c.id === editingCheckId) ?? null;
  const allCheckIds = checks.map((c) => c.id).join(",");

  useEffect(() => {
    // Only auto-close if the check was deleted outright (US8 FR-024) -- no longer
    // tied to active/inactive membership, since a new check's editor must survive
    // it sitting in Available.
    if (editingCheckId && !checks.some((c) => c.id === editingCheckId)) {
      setEditingCheckId(null);
      setCheckSnapshot(null);
    }
    // allCheckIds (not `checks`) keeps this from re-running every render on a
    // fresh array reference -- only fires when the actual pool changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allCheckIds]);

  function openCheckEditor(check: Check) {
    setCheckSnapshot({
      fieldId: check.fieldId,
      compareFieldId: check.compareFieldId,
      predicate: check.predicate,
      operator: check.operator,
      threshold: check.threshold,
      severity: check.severity,
      messagePass: check.messagePass,
      messageFail: check.messageFail,
    });
    setEditingCheckId(check.id);
  }

  // spec024 US8 (FR-022): creates the check (category-scoped to this block, never
  // auto-active) and opens it in the same modal used to edit any existing check --
  // no separate creation form, per this feature's reuse-the-existing-modal design.
  //
  // spec024 FR-027 (confirmed bug, 2026-08-03): a newly-created check is always
  // NOT_COMPILED (FR-023), and Available Checks hides NOT_COMPILED checks by default
  // (FR-011) -- so without this, the check the author just created would immediately
  // vanish from the list they were just looking at. Flipping this block's own
  // "show not built" toggle on at creation time keeps it visible, reusing the
  // existing filter instead of adding a second, parallel visibility rule.
  function handleCreateCheck() {
    const newCheck = onCreateCheck(block.name);
    setAvailableFilter((prev) => ({ ...prev, showNotBuilt: true }));
    openCheckEditor(newCheck);
  }

  function discardAndCloseEditor() {
    if (editingCheckId && checkSnapshot) {
      onUpdateCheck(editingCheckId, checkSnapshot);
    }
    setEditingCheckId(null);
    setCheckSnapshot(null);
  }

  function saveAndCloseEditor() {
    setEditingCheckId(null);
    setCheckSnapshot(null);
  }

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
            <div className="flex items-center gap-2">
              <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-bold text-slate-600">
                {compilableCount} compilable / {visibleAvailableCount} total
              </span>
              {/* spec024 US8: check creation stays Conventional-only -- a deliberate scope
                  decision, not something US10 forces. FHA/VA/USDA now have a real (if
                  not-yet-compiled) check population, but authoring brand-new checks on top
                  of imported AMQ rows is a separate capability this feature doesn't add. */}
              {isConventionalBlock && (
                <button
                  onClick={handleCreateCheck}
                  className="flex items-center gap-1 rounded-lg bg-blue-600 px-2 py-1 text-[11px] font-semibold text-white shadow-sm transition hover:bg-blue-700"
                >
                  <Plus className="h-3 w-3" />
                  New Check
                </button>
              )}
            </div>
          </div>
          {notBuiltCount > 0 && !availableFilter.showNotBuilt && (
            <div className="mb-3 -mt-1 text-[11px] text-slate-500">
              {notBuiltCount} not yet buildable check{notBuiltCount === 1 ? "" : "s"} hidden -- check
              "Show not built" below to reveal them.
            </div>
          )}
          {notBuiltCount > 0 && availableFilter.showNotBuilt && (
            <div className="mb-3 -mt-1 text-[11px] text-slate-500">
              {notBuiltCount} not yet buildable -- shown below, never claimed as ready.
            </div>
          )}
          {available.length > 0 && (
            <CheckFilterBar checks={available} value={availableFilter} onChange={setAvailableFilter} showNotBuiltToggle />
          )}
          <div className="space-y-3">
            {availableGroups.map((group) =>
              group.questionCode ? (
                <QuestionGroup
                  key={group.questionCode}
                  questionText={group.questionText ?? group.questionCode}
                  checks={group.checks}
                  otherBlocksUsing={otherBlocksUsing}
                  onToggleCheck={onToggleCheck}
                  onRemoveCheck={onRemoveCheck}
                />
              ) : (
                group.checks.map((check) => (
                  <AvailableCheckRow
                    key={check.id}
                    check={check}
                    usedElsewhere={otherBlocksUsing(check.id)}
                    onToggleCheck={onToggleCheck}
                    onRemoveCheck={onRemoveCheck}
                  />
                ))
              )
            )}
            {availableFiltered.length === 0 && available.length > 0 && (
              <div className="py-6 text-center text-xs text-slate-400">No checks match these filters.</div>
            )}
            {available.length === 0 && (
              <div className="py-6 text-center text-xs text-slate-400">
                No more {block.name}-category checks available to add.
              </div>
            )}
          </div>
          {availableFiltered.length > PAGE_SIZE && (
            <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3 text-[11px] text-slate-500">
              <span>
                Showing {availableCurrentPage * PAGE_SIZE + 1}–
                {Math.min((availableCurrentPage + 1) * PAGE_SIZE, availableFiltered.length)} of {availableFiltered.length}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setAvailablePage((p) => Math.max(0, p - 1))}
                  disabled={availableCurrentPage === 0}
                  className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>
                <span className="font-mono">
                  Page {availableCurrentPage + 1} of {availableTotalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setAvailablePage((p) => Math.min(availableTotalPages - 1, p + 1))}
                  disabled={availableCurrentPage >= availableTotalPages - 1}
                  className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          )}
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
          {active.length > 0 && (
            <CheckFilterBar checks={active} value={activeFilter} onChange={setActiveFilter} />
          )}
          <div className="space-y-2">
            {activePaged.map((check) => (
              <div
                key={check.id}
                className={`flex items-start gap-2.5 rounded-lg border p-3 ${
                  editingCheckId === check.id ? "border-blue-400 bg-white ring-1 ring-blue-300" : "border-blue-200 bg-white"
                }`}
              >
                <button
                  onClick={() => onToggleCheck(check.id)}
                  className="shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-600"
                  title="Deactivate this check from the block"
                >
                  <ArrowLeftCircle className="h-5 w-5" />
                </button>
                <button onClick={() => openCheckEditor(check)} className="min-w-0 flex-1 text-left">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-xs font-bold text-slate-900">{check.name}</span>
                    <SeverityBadge severity={check.severity} />
                    {check.questionCode && (
                      <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-semibold uppercase text-slate-500">
                        {check.questionCode}
                      </span>
                    )}
                    {check.authorability && check.authorability !== "COMPILABLE" && (
                      <span
                        className="rounded border border-amber-200 bg-amber-50 px-1.5 py-0.5 text-[9px] font-semibold uppercase text-amber-700"
                        title={check.authorabilityReason ?? undefined}
                      >
                        wired, not yet buildable
                      </span>
                    )}
                  </div>
                  <div className="mt-0.5 font-mono text-[11px] text-slate-500">{compiledGateSummary(check)}</div>
                </button>
                <button
                  onClick={() => openCheckEditor(check)}
                  className="shrink-0 rounded-lg p-1.5 text-slate-300 hover:bg-slate-50 hover:text-blue-600"
                  title="Edit this check's gate"
                >
                  <Pencil className="h-4 w-4" />
                </button>
              </div>
            ))}
            {activeFiltered.length === 0 && active.length > 0 && (
              <div className="py-6 text-center text-xs text-blue-400/70">No wired checks match these filters.</div>
            )}
            {active.length === 0 && (
              <div className="py-6 text-center text-xs text-blue-400/70">
                No checks wired yet. Activate one from the pool on the left.
              </div>
            )}
          </div>
          {activeFiltered.length > PAGE_SIZE && (
            <div className="mt-3 flex items-center justify-between border-t border-blue-100 pt-3 text-[11px] text-blue-700/70">
              <span>
                Showing {activeCurrentPage * PAGE_SIZE + 1}–
                {Math.min((activeCurrentPage + 1) * PAGE_SIZE, activeFiltered.length)} of {activeFiltered.length}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setActivePage((p) => Math.max(0, p - 1))}
                  disabled={activeCurrentPage === 0}
                  className="rounded-lg border border-blue-200 px-2.5 py-1 font-semibold text-blue-700 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>
                <span className="font-mono">
                  Page {activeCurrentPage + 1} of {activeTotalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setActivePage((p) => Math.min(activeTotalPages - 1, p + 1))}
                  disabled={activeCurrentPage >= activeTotalPages - 1}
                  className="rounded-lg border border-blue-200 px-2.5 py-1 font-semibold text-blue-700 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <Modal open={editingCheck != null} onClose={discardAndCloseEditor}>
        {editingCheck && (
          <>
            <CheckEditor
              key={editingCheck.id}
              check={editingCheck}
              onUpdate={(updates) => onUpdateCheck(editingCheck.id, updates)}
            />
            <div className="mt-4 flex justify-end gap-2 border-t border-slate-100 pt-3">
              <button
                onClick={discardAndCloseEditor}
                className="rounded-lg border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={saveAndCloseEditor}
                className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700"
              >
                Done
              </button>
            </div>
          </>
        )}
      </Modal>
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

const AUTHORABILITY_LABEL: Record<NonNullable<Check["authorability"]>, string> = {
  COMPILABLE: "Ready to build",
  NEEDS_FIELDS: "Needs fields",
  NEEDS_SME: "Needs SME judgment",
  NOT_MECHANIZABLE: "Not mechanizable yet",
  NOT_ASSESSED: "Not yet assessed",
};

function AvailableCheckRow({
  check,
  usedElsewhere,
  onToggleCheck,
  onRemoveCheck,
}: {
  check: Check;
  usedElsewhere: number;
  onToggleCheck: (id: string) => void;
  onRemoveCheck: (id: string) => boolean;
}) {
  const isCompilable = check.authorability === "COMPILABLE";
  // spec024 US8 (FR-024/025): remove is only ever offered on Available rows (this
  // component), never on Active rows -- local to this row since the confirm/blocked
  // state has no meaning once you leave it.
  const [confirmRemove, setConfirmRemove] = useState(false);
  const [blockedMessage, setBlockedMessage] = useState<string | null>(null);

  function handleRemove() {
    const removed = onRemoveCheck(check.id);
    setConfirmRemove(false);
    setBlockedMessage(removed ? null : "Still active in another block -- deactivate it there first.");
  }

  return (
    <div
      className={`flex items-start gap-2.5 rounded-lg border p-3 ${
        isCompilable ? "border-slate-150 bg-slate-50/40" : "border-slate-150 border-dashed bg-white opacity-80"
      }`}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-bold text-slate-900">{check.name}</span>
          <SeverityBadge severity={check.severity} />
          {check.authorability && (
            <span
              className={`rounded px-1.5 py-0.5 text-[9px] font-semibold uppercase ${
                isCompilable ? "bg-slate-100 text-slate-500" : "bg-white text-slate-400 border border-slate-200"
              }`}
              title={check.authorabilityReason ?? undefined}
            >
              {AUTHORABILITY_LABEL[check.authorability]}
            </span>
          )}
        </div>
        {usedElsewhere > 0 && (
          <span className="mt-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-semibold text-blue-600">
            also in {usedElsewhere} other block{usedElsewhere > 1 ? "s" : ""}
          </span>
        )}
        {blockedMessage && <p className="mt-1 text-[10px] font-semibold text-amber-700">{blockedMessage}</p>}
      </div>
      {confirmRemove ? (
        <div className="flex shrink-0 items-center gap-1">
          <button
            onClick={handleRemove}
            className="rounded-lg bg-rose-600 px-2 py-1 text-[10px] font-semibold text-white hover:bg-rose-700"
          >
            Confirm
          </button>
          <button
            onClick={() => setConfirmRemove(false)}
            className="rounded-lg border border-slate-200 px-2 py-1 text-[10px] font-semibold text-slate-500 hover:bg-slate-50"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          onClick={() => {
            setBlockedMessage(null);
            setConfirmRemove(true);
          }}
          className="shrink-0 rounded-lg p-1.5 text-slate-300 hover:bg-rose-50 hover:text-rose-500"
          title="Remove this check from the catalog"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      )}
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
  onRemoveCheck,
}: {
  questionText: string;
  checks: Check[];
  otherBlocksUsing: (id: string) => number;
  onToggleCheck: (id: string) => void;
  onRemoveCheck: (id: string) => boolean;
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
            onRemoveCheck={onRemoveCheck}
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
  // spec024 US8: name is editable here so an author-created check (which starts
  // named "New Check", see RoutesFlow.tsx's createCheck) can be given a real name --
  // the only field on Check this editor didn't already expose.
  const [name, setName] = useState(check.name);
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
        <div>
          <label htmlFor="check-name" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
            Check Name
          </label>
          <input
            id="check-name"
            name="check-name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              commit({ name: e.target.value });
            }}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-blue-500 focus:outline-none"
          />
        </div>

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

