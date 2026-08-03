import { AlertTriangle, ClipboardList, FileSearch, FileText, Loader2, Sparkles } from "lucide-react";
import { useDataSource } from "../lib/dataSourceContext";

// The model is instructed (decision_narrative.py's SYSTEM_PROMPT) to write exactly these
// two heading lines verbatim, each on its own line. Split on them for display -- falls back
// to one plain block if the model's real output doesn't match exactly (never crashes on an
// unexpected shape).
function splitNarrativeSections(text: string): { overview: string; findings: string } | null {
  const overviewIdx = text.indexOf("Loan Overview");
  const findingsIdx = text.indexOf("Audit Findings");
  if (overviewIdx === -1 || findingsIdx === -1 || findingsIdx <= overviewIdx) return null;
  return {
    overview: text.slice(overviewIdx + "Loan Overview".length, findingsIdx).trim(),
    findings: text.slice(findingsIdx + "Audit Findings".length).trim(),
  };
}

// DecisionNarrativePanel — spec014 ("we also need a decision narrative at the end of the
// results"), wired into this demo's live engine/ pipeline. An LLM-authored, read-only prose
// explanation of an already-computed RunResult -- generated on demand only (a real, billed
// Bedrock call: engine/qc_engine/run_decision_narrative_for_demo.py), never automatically
// alongside the deterministic audit run itself. Every check_id and Guide citation the
// narrative names is validated against this loan's real RunResult and the gold ruleset's
// own real Selling Guide citations before being shown (decision_narrative.py's _validate())
// -- if generation fails validation after retries, the backend still returns a structured
// result with narrativeText: null, shown honestly here, never silently hidden.
interface DecisionNarrativePanelProps {
  applicationId: string;
}

export function DecisionNarrativePanel({ applicationId }: DecisionNarrativePanelProps) {
  const { auditRuns, narratives, generateNarrative } = useDataSource();
  const audit = auditRuns.get(applicationId);
  const narrative = narratives.get(applicationId);

  if (audit?.status !== "resolved") {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-4 text-xs text-slate-400">
        Run the real audit first (see the Apply tab) to generate a decision narrative — this
        explains an already-computed result, it never decides one.
      </div>
    );
  }

  const generating = narrative?.status === "generating";

  return (
    <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
          <FileText className="h-3.5 w-3.5" />
          QC Audit Decision Narrative
        </div>
        <button
          type="button"
          onClick={() => void generateNarrative(applicationId)}
          disabled={generating}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-all ${
            generating
              ? "cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400"
              : "border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100"
          }`}
        >
          {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
          {generating ? "Generating…" : narrative?.status === "resolved" ? "Regenerate" : "Generate Decision Narrative"}
        </button>
      </div>

      {narrative?.status === "error" && (
        <div className="flex items-start gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          {narrative.message}
        </div>
      )}

      {narrative?.status === "resolved" && (
        narrative.result.narrativeText ? (
          <div className="space-y-3">
            {(() => {
              const sections = splitNarrativeSections(narrative.result.narrativeText!);
              if (!sections) {
                return <p className="text-sm leading-relaxed text-slate-700">{narrative.result.narrativeText}</p>;
              }
              return (
                <>
                  <div>
                    <div className="mb-1 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wide text-blue-700">
                      <FileSearch className="h-3.5 w-3.5" />
                      Loan Overview
                    </div>
                    <p className="text-sm leading-relaxed text-slate-700">{sections.overview}</p>
                  </div>
                  <div>
                    <div className="mb-1 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wide text-blue-700">
                      <ClipboardList className="h-3.5 w-3.5" />
                      Audit Findings
                    </div>
                    <p className="text-sm leading-relaxed text-slate-700">{sections.findings}</p>
                  </div>
                </>
              );
            })()}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-slate-100 pt-2 text-[11px] text-slate-400">
              <span>{narrative.result.referencedCheckIds.length} real check(s) cited</span>
              <span>{narrative.result.referencedGuideCitations.length} real Guide citation(s) cited</span>
              <span>{narrative.result.model}</span>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-1.5 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            The model could not produce a narrative that passed grounding validation after
            retries — shown honestly as unavailable, never a guessed summary.
          </div>
        )
      )}

      {!narrative && !generating && (
        <p className="text-xs text-slate-400">
          Not yet generated — click above for a plain-language explanation of this loan's real
          disposition, grounded in its actual checks and the gold ruleset's own Selling Guide
          citations.
        </p>
      )}
    </div>
  );
}
