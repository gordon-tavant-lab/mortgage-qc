import { AlertTriangle, ArrowRight, Download, Loader2, RefreshCw } from "lucide-react";
import { useDataSource } from "../lib/dataSourceContext";

// PullApplicationButton — FR-001/SC-001. Triggers an on-demand pull of a known
// applicationId's live Touchless data. Disabled when the session-wide data source is
// "stored" — pulling only makes sense in "live" mode. "Stored" stays the deliberate
// session default (spec020 FR: resets every fresh session so a demo never silently hits
// the real Touchless API) -- but 021's own live-audit demo depends on this exact button
// being the primary trigger, so a hover-only tooltip explaining why it's disabled isn't
// enough (a live screenshot walkthrough found this as real friction: not discoverable
// without hovering). Added a visible inline hint + a one-click "Switch to Live" action
// right here, so there's no need to separately hunt down the Settings-menu toggle.
interface PullApplicationButtonProps {
  applicationId: string;
}

export function PullApplicationButton({ applicationId }: PullApplicationButtonProps) {
  const { mode, setMode, pullApplication, isPullingApplication, pulledApplications, applicationError } =
    useDataSource();

  const pulling = isPullingApplication(applicationId);
  const cached = pulledApplications.has(applicationId);
  const error = applicationError(applicationId);
  const disabled = mode === "stored" || pulling;

  const handleClick = () => {
    if (mode === "stored" || pulling) return;
    if (cached) {
      void pullApplication(applicationId, { force: true });
    } else {
      void pullApplication(applicationId);
    }
  };

  let label = "Pull Live Application";
  let Icon = Download;
  if (pulling) {
    label = "Pulling…";
    Icon = Loader2;
  } else if (cached) {
    label = "Re-pull Application";
    Icon = RefreshCw;
  }

  return (
    <div className="flex flex-col items-start gap-1.5">
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        title={
          mode === "stored"
            ? "Switch the data source to Live (Settings menu) to pull a live application"
            : undefined
        }
        className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-all ${
          disabled
            ? "cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400"
            : "border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100"
        }`}
      >
        <Icon className={`h-3.5 w-3.5 ${pulling ? "animate-spin" : ""}`} />
        {label}
      </button>
      {mode === "stored" && (
        <button
          type="button"
          onClick={() => setMode("live")}
          className="flex items-center gap-1 text-[11px] font-medium text-blue-600 hover:text-blue-700 hover:underline"
        >
          Data source is Stored — switch to Live to pull a real application
          <ArrowRight className="h-3 w-3" />
        </button>
      )}
      {error && (
        <div className="flex items-center gap-1.5 text-[11px] font-medium text-rose-700">
          <AlertTriangle className="h-3 w-3 shrink-0" />
          {error.message}
        </div>
      )}
    </div>
  );
}
