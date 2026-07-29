import { Zap, Hash, FileCheck2, ArrowRightLeft, ShieldCheck, CheckCircle, XCircle, Clock } from "lucide-react";
import { MOCK_EVALUATION, MOCK_SIGNED_RULESET, MOCK_CHECKS } from "../data/mockData";
import { PlaceholderBadge } from "./PlaceholderBadge";
import { CheckStatusBadge } from "./StatusBadge";

const VERDICT_STYLES = {
  PASS: "bg-emerald-50 border-emerald-200 text-emerald-700",
  FAIL: "bg-rose-50 border-rose-200 text-rose-700",
  NEEDS_REVIEW: "bg-amber-50 border-amber-200 text-amber-700",
};

export function ApplyView() {
  const evaluation = MOCK_EVALUATION;

  // The real Op/Target join: CheckResult.checkId -> the matching Check in
  // the SIGNED RULESET, not a field on CheckResult itself (engine.py's
  // CheckResult carries no operator/threshold -- ruleset.py's Check does).
  const checkById = (id: string) => MOCK_CHECKS.find((c) => c.id === id);

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
          <span
            className="flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700"
            title="No manual trigger needed — the engine re-runs automatically whenever this loan's sources or signed ruleset change."
          >
            <Zap className="h-3.5 w-3.5" />
            Auto-run on load · a few seconds ago
          </span>
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
              {MOCK_SIGNED_RULESET.sha256.slice(0, 12)}...
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div className={`flex flex-col justify-between rounded-2xl border p-4 shadow-[var(--shadow-panel)] ${VERDICT_STYLES[evaluation.overallVerdict]}`}>
          <div className="text-xs font-semibold uppercase tracking-wider opacity-80">Overall Loan Verdict</div>
          <div className="my-2 flex items-center gap-2">
            {evaluation.overallVerdict === "PASS" && <CheckCircle className="h-6 w-6" />}
            {evaluation.overallVerdict === "FAIL" && <XCircle className="h-6 w-6" />}
            {evaluation.overallVerdict === "NEEDS_REVIEW" && <Clock className="h-6 w-6" />}
            <span className="text-xl font-bold tracking-tight">{evaluation.overallVerdict}</span>
          </div>
          <div className="text-[11px] opacity-80">
            {evaluation.overallVerdict === "FAIL" ? "Hard rule assertion failure." : "—"}
          </div>
        </div>
        <StatCard label="Passed Assertions" value={evaluation.passedCount} color="text-emerald-600" sub="Verified high confidence" />
        <StatCard label="Failed Defective" value={evaluation.failedCount} color="text-rose-600" sub="Zero false-clear gate" />
        <StatCard label="Needs Review" value={evaluation.needsReviewCount} color="text-amber-600" sub="Sub-floor confidence or review" />
        <div className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="flex items-center gap-1 text-xs font-medium text-slate-500">
            <Hash className="h-3.5 w-3.5 text-blue-600" />
            Execution Hash
          </div>
          <div className="my-1 truncate font-mono text-xs font-bold text-slate-900" title={evaluation.executionHash}>
            {evaluation.executionHash.slice(0, 14)}...
          </div>
          <div className="text-[10px] font-semibold text-emerald-600">✓ Byte-exact reproducible</div>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[var(--shadow-panel)]">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 bg-slate-50/60 p-4">
          <div>
            <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900">
              <FileCheck2 className="h-4 w-4 text-blue-600" />
              Deterministic Audit Trace &amp; Field-Level Intermediates
            </h3>
            <p className="text-xs text-slate-500">
              Every verdict displays the exact Decimal value, source citation, extraction confidence, and rounding policy.
            </p>
          </div>
          <span className="rounded-lg border border-slate-200 bg-white px-2.5 py-1 font-mono text-xs text-slate-600">
            Policy: ROUND_HALF_EVEN
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-500">
                <th className="px-4 py-3">QC Check Assertion</th>
                <th className="px-4 py-3">Field ID</th>
                <th className="px-4 py-3">Extracted Value</th>
                <th className="px-4 py-3">Op / Target</th>
                <th className="px-4 py-3">Rounded Decimal</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Source Citation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {evaluation.auditTrace.map((step) => {
                const check = checkById(step.checkId);
                const isGated = (step.docConfidence ?? 1) < 0.85;
                return (
                  <tr key={step.checkId} className="hover:bg-slate-50/60">
                    <td className="max-w-xs px-4 py-3 font-semibold text-slate-900">
                      <div className="flex items-center gap-1.5">
                        {step.checkName}
                        {step.placeholder && <PlaceholderBadge />}
                      </div>
                      <div className="mt-0.5 text-[11px] font-normal text-slate-500">{step.message}</div>
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-500">{step.fieldName}</td>
                    <td className="px-4 py-3 font-mono font-bold text-slate-900">{step.docValue}</td>
                    <td className="px-4 py-3 font-mono text-blue-600">
                      {/* joined from ruleset.py's Check, not CheckResult -- see checkById() above */}
                      {check ? `${check.operator} ${check.threshold}` : "—"}
                    </td>
                    <td className="px-4 py-3 font-mono font-semibold text-emerald-600">{step.comparedValue}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <span className={`font-mono font-semibold ${isGated ? "font-bold text-amber-600" : "text-emerald-600"}`}>
                          {((step.docConfidence ?? 0) * 100).toFixed(0)}%
                        </span>
                        {isGated && (
                          <span
                            className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-700"
                            title="review_reason: LOW_CONFIDENCE -- withheld from auto-clear (spec 006)"
                          >
                            Gate
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <CheckStatusBadge status={step.status} />
                    </td>
                    <td className="max-w-xs truncate px-4 py-3 text-[11px] text-slate-500">
                      {step.citation ? `${step.citation.doc}, Page ${step.citation.page}${step.citation.segment ? `, ${step.citation.segment}` : ""}` : "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {evaluation.reconciliations.length > 0 && (
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
                {evaluation.reconciliations.map((rec) => (
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
    </div>
  );
}

function StatCard({ label, value, color, sub }: { label: string; value: number; color: string; sub: string }) {
  return (
    <div className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
      <div className="text-xs font-medium text-slate-500">{label}</div>
      <div className={`my-1 font-mono text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-[11px] text-slate-500">{sub}</div>
    </div>
  );
}
