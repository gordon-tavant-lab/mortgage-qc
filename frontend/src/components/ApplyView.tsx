import { useEffect, useMemo, useState } from "react";
import {
  Zap,
  Hash,
  FileCheck2,
  ArrowRightLeft,
  ShieldCheck,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  FileText,
  ChevronRight,
  Loader2,
} from "lucide-react";
import { MOCK_EVALUATION, MOCK_SIGNED_RULESET, MOCK_LOANS } from "../data/mockData";
import { GOLD_ROUTES, GOLD_BLOCKS, GOLD_CHECKS } from "../data/goldCatalog";
import { CheckStatusBadge } from "./StatusBadge";
import { RetrievedDocumentViewer } from "./RetrievedDocumentViewer";
import { CheckFilterBar, EMPTY_CHECK_FILTER, filterChecks, type CheckFilterState } from "./CheckFilterBar";
import { useDataSource } from "../lib/dataSourceContext";
import type { Check, CheckStatus, Severity } from "../lib/types";

// Live-demo-walkthrough finding (2026-08-02): this view previously always rendered
// MOCK_EVALUATION regardless of which loan was open -- every loan looked identical
// ("OVERALL LOAN VERDICT: FAIL", same 3 fake defects), directly contradicting the real
// per-loan status shown one click away. Rebuilt to be loanId-aware: the 19 cosmetic
// PASS loans (FR-006b, no real evaluation capability behind them) show their mapped
// route's real gold checks, honestly framed as passed, never fabricating execution
// details that never happened; the one real demo loan shows its ACTUAL RunResult once
// evaluated, and an honest "not yet evaluated"/"running"/"error" state otherwise --
// never a canned verdict.

const VERDICT_STYLES: Record<"PASS" | "FAILED" | "NEEDS_REVIEW", string> = {
  PASS: "bg-emerald-50 border-emerald-200 text-emerald-700",
  FAILED: "bg-rose-50 border-rose-200 text-rose-700",
  NEEDS_REVIEW: "bg-amber-50 border-amber-200 text-amber-700",
};

type Bucket = "passed" | "failed" | "needsReview";

interface ApplyRow {
  id: string;
  name: string;
  category: string;
  kind: Check["kind"];
  severity: Severity;
  aor?: string[];
  status: CheckStatus;
  message?: string;
  citation?: { doc: string; page: number; segment: string; documentIds?: string[] };
  isReal: boolean;
}

function routeIdForLoanType(loanType: string): string {
  const key = loanType.trim().toUpperCase();
  if (key === "FHA") return "fha";
  if (key === "VA") return "va";
  if (key === "USDA") return "usda";
  return "conventional";
}

// Cosmetic loans have no real evaluation behind them -- their "passed" list is the
// real gold-derived checks for their mapped route (spec021 US3), just never actually
// executed. Never fabricates a status other than PASS for these.
function cosmeticRowsForRoute(routeId: string): ApplyRow[] {
  const route = GOLD_ROUTES.find((r) => r.id === routeId);
  if (!route) return [];
  const blockIds = new Set(route.blockIds);
  const checkIds = new Set(GOLD_BLOCKS.filter((b) => blockIds.has(b.id)).flatMap((b) => b.checkIds));
  return GOLD_CHECKS.filter((c) => checkIds.has(c.id)).map((c) => ({
    id: c.id,
    name: c.name,
    category: c.category,
    kind: c.kind,
    severity: c.severity,
    aor: c.aor,
    status: "PASS" as CheckStatus,
    isReal: false,
  }));
}

// Mirrors p0/qc_engine/engine.py's CheckResult.to_dict() shape exactly (same convention
// as auditFindings.ts). check_id matches goldCatalog.json's own id scheme 1:1 (both the
// frontend and backend compilers slugify() the same gold rule_id), so category/kind/aor
// can be enriched from GOLD_CHECKS without the backend needing to resend them.
interface RealCheckResultJson {
  check_id: string;
  check_name: string;
  severity: Severity;
  status: CheckStatus;
  phase: string;
  message: string;
  citation: { docName: string; pageNum: number; segmentSnippet: string; documentIds?: string[] } | null;
}

function realRowsFromRunResult(runResult: unknown): ApplyRow[] {
  if (typeof runResult !== "object" || runResult === null) return [];
  const results = (runResult as { results?: RealCheckResultJson[] }).results;
  if (!Array.isArray(results)) return [];
  return results.map((r) => {
    const meta = GOLD_CHECKS.find((c) => c.id === r.check_id);
    return {
      id: r.check_id,
      name: r.check_name,
      category: meta?.category ?? "—",
      kind: meta?.kind ?? "predicate",
      severity: r.severity,
      aor: meta?.aor,
      status: r.status,
      message: r.message,
      citation: r.citation
        ? {
            doc: r.citation.docName,
            page: r.citation.pageNum,
            segment: r.citation.segmentSnippet,
            documentIds: r.citation.documentIds,
          }
        : undefined,
      isReal: true,
    };
  });
}

// Buckets by the check's ACTUAL status, not severity -- the earlier severity-based
// version mis-bucketed any non-PASS CRITICAL check as "failed" even when its real status
// was NOT_APPLICABLE (precondition not met -- the check never ran, not a defect) or
// NEEDS_REVIEW, inflating "Failed Defective" with checks that never actually failed
// (live-demo finding 2026-08-02: 506 "Failed Defective" on a run with zero real FAILs).
// NOT_APPLICABLE returns null -- Gordon's explicit call for the demo: a gated-out check
// is neither a pass nor a failure and should not appear in any bucket or the table at all.
function bucketFor(row: ApplyRow): Bucket | null {
  if (row.status === "NOT_APPLICABLE") return null;
  if (row.status === "PASS") return "passed";
  if (row.status === "FAIL") return "failed";
  return "needsReview"; // NEEDS_REVIEW, WARNING, or any other non-terminal real status
}

function rowsToChecks(rows: ApplyRow[]): Check[] {
  return rows.map((r) => ({
    id: r.id,
    name: r.name,
    kind: r.kind,
    category: r.category,
    fieldId: r.id,
    operator: "<=",
    threshold: "",
    severity: r.severity,
    description: r.message ?? r.name,
    aor: r.aor,
  }));
}

interface ApplyViewProps {
  loanId: string;
}

export function ApplyView({ loanId }: ApplyViewProps) {
  const { auditRuns } = useDataSource();
  const loan = MOCK_LOANS.find((l) => l.loanId === loanId);
  const audit = loan?.applicationId ? auditRuns.get(loan.applicationId) : undefined;

  let rows: ApplyRow[] = [];
  let overallVerdict: "PASS" | "FAILED" | "NEEDS_REVIEW" | null = null;
  let executionHash = MOCK_SIGNED_RULESET.sha256;
  let statusNote: { kind: "running" | "error" | "not_fetched"; message: string } | null = null;

  if (!loan?.applicationId) {
    rows = cosmeticRowsForRoute(routeIdForLoanType(loan?.loanType ?? "Conventional"));
    overallVerdict = "PASS";
  } else if (audit?.status === "resolved") {
    rows = realRowsFromRunResult(audit.result.runResult);
    overallVerdict = audit.result.loanStatus;
    const runResultHash = (audit.result.runResult as { ruleset_sha256?: string } | undefined)?.ruleset_sha256;
    if (runResultHash) executionHash = runResultHash;
  } else if (audit?.status === "running") {
    statusNote = { kind: "running", message: "Evaluation in progress — the engine is running now." };
  } else if (audit?.status === "error") {
    statusNote = { kind: "error", message: `Evaluation could not complete: ${audit.message}` };
  } else {
    statusNote = {
      kind: "not_fetched",
      message: 'This loan has not been evaluated yet — click "Pull Live Application" above to fetch it and run a real audit.',
    };
  }

  const buckets = useMemo(() => {
    const b: Record<Bucket, ApplyRow[]> = { passed: [], failed: [], needsReview: [] };
    for (const row of rows) {
      const bucket = bucketFor(row);
      if (bucket) b[bucket].push(row);
    }
    return b;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rows]);

  const defaultBucket: Bucket = overallVerdict === "FAILED" ? "failed" : overallVerdict === "NEEDS_REVIEW" ? "needsReview" : "passed";
  const [selectedBucket, setSelectedBucket] = useState<Bucket>(defaultBucket);
  const [filter, setFilter] = useState<CheckFilterState>(EMPTY_CHECK_FILTER);
  const [viewingDocumentId, setViewingDocumentId] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 25;

  // Reset the selected bucket + filter whenever the loan changes, or once this loan's
  // audit run transitions to a new state (e.g. running -> resolved) -- otherwise a stale
  // filter/bucket choice from a previous loan or evaluation stage would silently carry
  // forward (same discipline as BlockDetail.tsx's own reset-on-navigation).
  useEffect(() => {
    setSelectedBucket(defaultBucket);
    setFilter(EMPTY_CHECK_FILTER);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loanId, audit?.status]);

  // Live-demo finding (2026-08-02): a route can carry 220+ checks -- paginate rather
  // than render them all at once. Resets to page 1 whenever the bucket/filter/loan
  // changes so a stale page index never silently shows an empty or wrong-context page.
  useEffect(() => {
    setPage(0);
  }, [selectedBucket, filter, loanId]);

  const filteredIds = useMemo(
    () => new Set(filterChecks(rowsToChecks(buckets[selectedBucket]), filter).map((c) => c.id)),
    [buckets, selectedBucket, filter],
  );
  // Live-demo finding (2026-08-03): DU-related auto-pass rows (this project has no live
  // connection to Desktop Underwriter -- autopass_no_system_access.json's demo-scoped
  // decision) were interleaved with genuinely-evaluated PASS rows in whatever order the
  // engine returned them, so the very first page often opened on an "auto-pass" caveat
  // instead of a real "Predicate satisfied." result. Stable-sort them to the end within
  // whichever bucket is being viewed -- never reordered out of existence, just deprioritized
  // so the real evaluations lead.
  const visibleRows = buckets[selectedBucket]
    .filter((r) => filteredIds.has(r.id))
    .map((r, i) => ({ r, i, isAutoPass: (r.message ?? "").startsWith("auto-pass:") }))
    .sort((a, b) => (Number(a.isAutoPass) - Number(b.isAutoPass)) || (a.i - b.i))
    .map(({ r }) => r);
  const totalPages = Math.max(1, Math.ceil(visibleRows.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages - 1);
  const pagedRows = visibleRows.slice(currentPage * PAGE_SIZE, currentPage * PAGE_SIZE + PAGE_SIZE);

  if (!loan) return null;

  return (
    <div className="space-y-6">
      <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider text-blue-600">
                Core Principle I &amp; II
              </span>
              <h2 className="font-display text-lg font-bold text-slate-900">Deterministic QC Execution Engine</h2>
            </div>
            <p className="mt-0.5 text-xs text-slate-500">
              Pure function of <code className="text-blue-600">(signed_ruleset, loan)</code>. Zero LLM
              freelancing at runtime. Pinned Banker's Rounding.
            </p>
          </div>
          {audit?.status === "resolved" ? (
            <span className="flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">
              <Zap className="h-3.5 w-3.5" />
              Real engine run · {audit.result.evaluatedAt ? new Date(audit.result.evaluatedAt).toLocaleTimeString() : "just now"}
            </span>
          ) : loan.applicationId ? (
            <span className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-500">
              <Clock className="h-3.5 w-3.5" />
              No real run yet
            </span>
          ) : (
            <span
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-500"
              title="This is one of the 19 cosmetic demo loans -- no real evaluation capability behind it."
            >
              Cosmetic demo loan
            </span>
          )}
        </div>

        <div className="border-t border-slate-100 pt-4">
          <div className="text-xs font-semibold text-slate-600">Active Signed Ruleset Artifact:</div>
          <div className="mt-1.5 flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs">
            <div>
              <div className="flex items-center gap-1.5 font-semibold text-slate-800">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                {MOCK_SIGNED_RULESET.name} ({MOCK_SIGNED_RULESET.version})
              </div>
              <div className="mt-0.5 text-[10px] text-slate-400">
                Signed by {MOCK_SIGNED_RULESET.signedBy} · SME Edits: {MOCK_SIGNED_RULESET.editDistance}
              </div>
            </div>
            <span className="rounded border border-slate-700 bg-slate-800 px-2 py-1 font-mono text-[10px] text-slate-200">
              {executionHash.slice(0, 12)}...
            </span>
          </div>
        </div>
      </div>

      {statusNote ? (
        <div
          className={`flex items-center gap-2 rounded-xl border p-4 text-sm ${
            statusNote.kind === "error"
              ? "border-rose-200 bg-rose-50 text-rose-700"
              : statusNote.kind === "running"
                ? "border-blue-200 bg-blue-50 text-blue-700"
                : "border-slate-200 bg-slate-50 text-slate-600"
          }`}
        >
          {statusNote.kind === "running" ? (
            <Loader2 className="h-4 w-4 shrink-0 animate-spin" />
          ) : (
            <AlertCircle className="h-4 w-4 shrink-0" />
          )}
          {statusNote.message}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <div
              className={`flex flex-col justify-between rounded-2xl border p-4 shadow-[var(--shadow-panel)] ${VERDICT_STYLES[overallVerdict ?? "PASS"]}`}
            >
              <div className="text-xs font-semibold uppercase tracking-wider opacity-80">Overall Loan Verdict</div>
              <div className="my-2 flex items-center gap-2">
                {overallVerdict === "PASS" && <CheckCircle className="h-6 w-6" />}
                {overallVerdict === "FAILED" && <XCircle className="h-6 w-6" />}
                {overallVerdict === "NEEDS_REVIEW" && <Clock className="h-6 w-6" />}
                <span className="text-xl font-bold tracking-tight">{overallVerdict}</span>
              </div>
              <div className="text-[11px] opacity-80">
                {overallVerdict === "FAILED" ? "Hard rule assertion failure." : "—"}
              </div>
            </div>
            <BucketCard
              label="Passed Assertions"
              value={buckets.passed.length}
              color="text-emerald-600"
              sub="Verified high confidence"
              active={selectedBucket === "passed"}
              onClick={() => setSelectedBucket("passed")}
            />
            <BucketCard
              label="Failed Defective"
              value={buckets.failed.length}
              color="text-rose-600"
              sub="Zero false-clear gate"
              active={selectedBucket === "failed"}
              onClick={() => setSelectedBucket("failed")}
            />
            <BucketCard
              label="Needs Review"
              value={buckets.needsReview.length}
              color="text-amber-600"
              sub="Non-critical failure"
              active={selectedBucket === "needsReview"}
              onClick={() => setSelectedBucket("needsReview")}
            />
            <div className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
              <div className="flex items-center gap-1 text-xs font-medium text-slate-500">
                <Hash className="h-3.5 w-3.5 text-blue-600" />
                Execution Hash
              </div>
              <div className="my-1 truncate font-mono text-xs font-bold text-slate-900" title={executionHash}>
                {executionHash.slice(0, 14)}...
              </div>
              <div className="text-[10px] font-semibold text-emerald-600">✓ Byte-exact reproducible</div>
            </div>
          </div>

          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[var(--shadow-panel)]">
            <div className="border-b border-slate-100 bg-slate-50/60 p-4">
              <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900">
                <FileCheck2 className="h-4 w-4 text-blue-600" />
                {selectedBucket === "passed" && "Passed Assertions"}
                {selectedBucket === "failed" && "Failed Defective Assertions"}
                {selectedBucket === "needsReview" && "Needs-Review Assertions"}
              </h3>
              <p className="text-xs text-slate-500">
                {loan.applicationId
                  ? "Every check reflects the real, deterministic engine run against this loan."
                  : selectedBucket === "passed"
                    ? "Cosmetic demo loan -- these are this route's real gold-ruleset checks, shown as passed; not independently executed."
                    : "Cosmetic demo loan -- every check is shown as passed (FR-006b); this bucket is expected to be empty."}
              </p>
              <div className="mt-3">
                <CheckFilterBar checks={rowsToChecks(buckets[selectedBucket])} value={filter} onChange={setFilter} />
              </div>
            </div>

            {visibleRows.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No checks match the current filter.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-500">
                      <th className="px-4 py-3">QC Check Assertion</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Severity</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Evidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {pagedRows.map((row) => (
                      <tr key={row.id} className="hover:bg-slate-50/60">
                        <td className="max-w-xs px-4 py-3 font-semibold text-slate-900">
                          {row.name}
                          {row.message && <div className="mt-0.5 text-[11px] font-normal text-slate-500">{row.message}</div>}
                        </td>
                        <td className="px-4 py-3 text-[11px] text-slate-600">{row.category}</td>
                        <td className="px-4 py-3 text-[11px] text-slate-600">{row.severity}</td>
                        <td className="px-4 py-3">
                          <CheckStatusBadge status={row.status} />
                        </td>
                        <td className="max-w-xs px-4 py-3 text-[11px]">
                          {!row.isReal ? (
                            <span className="italic text-slate-400">Cosmetic loan — not independently executed</span>
                          ) : row.citation?.documentIds && row.citation.documentIds.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {row.citation.documentIds.map((docId) => (
                                <button
                                  key={docId}
                                  onClick={() => setViewingDocumentId(docId)}
                                  className="flex items-center gap-1 rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-slate-700 transition hover:border-blue-300 hover:bg-blue-50/50"
                                >
                                  <FileText className="h-3 w-3 text-blue-600" />
                                  {row.citation!.doc}
                                  <ChevronRight className="h-3 w-3 text-slate-400" />
                                </button>
                              ))}
                            </div>
                          ) : row.citation ? (
                            <span className="text-slate-400">No source document identified</span>
                          ) : (
                            <span className="text-slate-300">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {visibleRows.length > PAGE_SIZE && (
              <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-[11px] text-slate-500">
                <span>
                  Showing {currentPage * PAGE_SIZE + 1}–{Math.min((currentPage + 1) * PAGE_SIZE, visibleRows.length)} of{" "}
                  {visibleRows.length}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                    disabled={currentPage === 0}
                    className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Previous
                  </button>
                  <span className="font-mono">
                    Page {currentPage + 1} of {totalPages}
                  </span>
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                    disabled={currentPage >= totalPages - 1}
                    className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {MOCK_EVALUATION.reconciliations.length > 0 && (
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[var(--shadow-panel)]">
          <div className="border-b border-slate-100 bg-slate-50/60 p-4">
            <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900">
              <ArrowRightLeft className="h-4 w-4 text-amber-500" />
              Core Principle V: Independent Source Origin Reconciliation
            </h3>
            <p className="text-xs text-slate-500">
              Compares Document-Extracted truth vs LOS System origin. Mismatches generate informational flags without failing QC directly.
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-500">
                  <th className="px-4 py-3">Field Name</th>
                  <th className="px-4 py-3">Closing Doc Value</th>
                  <th className="px-4 py-3">LOS System Value</th>
                  <th className="px-4 py-3">Reconciliation Status</th>
                  <th className="px-4 py-3">Audit Note</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {MOCK_EVALUATION.reconciliations.map((rec) => (
                  <tr key={rec.fieldId} className="hover:bg-slate-50/60">
                    <td className="px-4 py-3 font-semibold text-slate-900">{rec.fieldName}</td>
                    <td className="px-4 py-3 font-mono font-bold text-slate-900">
                      {rec.docValue} <span className="text-[10px] text-slate-400">({rec.docSource})</span>
                    </td>
                    <td className="px-4 py-3 font-mono font-bold text-slate-900">
                      {rec.systemValue} <span className="text-[10px] text-slate-400">({rec.systemSource})</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[11px] font-bold text-amber-700">
                        {rec.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-[11px] text-slate-500">{rec.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {viewingDocumentId && (
        <RetrievedDocumentViewer documentId={viewingDocumentId} onClose={() => setViewingDocumentId(null)} />
      )}
    </div>
  );
}

function BucketCard({
  label,
  value,
  color,
  sub,
  active,
  onClick,
}: {
  label: string;
  value: number;
  color: string;
  sub: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex flex-col justify-between rounded-2xl border p-4 text-left shadow-[var(--shadow-panel)] transition ${
        active ? "border-blue-400 ring-2 ring-blue-100" : "border-slate-200 bg-white hover:border-slate-300"
      }`}
    >
      <div className="text-xs font-medium text-slate-500">{label}</div>
      <div className={`my-1 font-mono text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-[11px] text-slate-500">{sub}</div>
    </button>
  );
}
