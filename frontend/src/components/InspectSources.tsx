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

      {applicationId && <DecisionNarrativePanel applicationId={applicationId} />}
    </div>
  );
}
