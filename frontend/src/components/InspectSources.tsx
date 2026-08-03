import { Info } from "lucide-react";
import { DecisionNarrativePanel } from "./DecisionNarrativePanel";
import { QcAuditProcessFlow } from "./QcAuditProcessFlow";

interface InspectSourcesProps {
  applicationId?: string;
}

export function InspectSources({ applicationId }: InspectSourcesProps) {
  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">
        Before a run, the loan's document data is retrieved from Touchless through three
        sequential calls — confirmed on the 2026-08-01 Touchless call, not an assumed contract.
      </p>

      <QcAuditProcessFlow />

      <div className="flex items-start gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-500">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        <span>
          Not yet confirmed: whether Touchless's extraction output can identify a value's exact
          in-page location (e.g. character offset or bounding box) inside a document. Treat this as
          an open question, not something already solved.
        </span>
      </div>

      <div className="flex items-start gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-500">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        <span>
          This demo's live pull has one real data source — Touchless's own extracted
          document data (see the "Live Touchless Application" panel above for the actual
          fetched loan's real fields). No separate LOS export or MISMO 3.4 XML feed is
          wired into this demo, so a genuine cross-source reconciliation isn't performed
          here — showing one wouldn't be a real comparison.
        </span>
      </div>

      {applicationId && <DecisionNarrativePanel applicationId={applicationId} />}
    </div>
  );
}
