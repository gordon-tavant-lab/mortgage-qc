import { CheckCircle2, Loader2, Radio } from "lucide-react";
import { useDataSource } from "../lib/dataSourceContext";
import { MOCK_LOANS } from "../data/mockData";

// live-demo-engine-wiring: the one-click entry point for the live-demo story. Lives in
// SettingsMenu (not the primary nav, same SC-003 rationale as DataSourceToggle) since
// LoanQueue now hides the real Touchless-backed loan entirely until a pull happens
// (LoanQueue.tsx) -- there is no other way to trigger the FIRST pull once that loan is
// off the queue, so this button switches the data source to Live AND fires the pull in
// one action, then closes the settings panel so the queue's real-time RUNNING -> resolved
// transition is the very next thing the user sees.
//
// The one real Touchless-backed loan is a fixed, known applicationId (mockData.ts) -- not
// user-selectable, matching every other single-loan assumption already made throughout
// this feature (run_touchless_audit_for_demo.py's own DEFAULT_EXTRACTED_DATA_PATH, etc.).
const LIVE_APPLICATION_ID = MOCK_LOANS.find((loan) => loan.applicationId)?.applicationId;

interface ActivateLiveDemoButtonProps {
  onActivated?: () => void;
}

export function ActivateLiveDemoButton({ onActivated }: ActivateLiveDemoButtonProps) {
  const { setMode, pullApplication, isPullingApplication, pulledApplications, auditRuns } =
    useDataSource();

  if (!LIVE_APPLICATION_ID) return null;

  const pulling = isPullingApplication(LIVE_APPLICATION_ID);
  const activated = pulledApplications.has(LIVE_APPLICATION_ID);
  const audit = auditRuns.get(LIVE_APPLICATION_ID);
  const running = audit?.status === "running";

  const handleClick = () => {
    if (activated || pulling) return;
    setMode("live");
    void pullApplication(LIVE_APPLICATION_ID);
    onActivated?.();
  };

  let label = "Activate Live Demo";
  let Icon = Radio;
  if (pulling) {
    label = "Fetching real loan…";
    Icon = Loader2;
  } else if (running) {
    label = "Audit running…";
    Icon = Loader2;
  } else if (activated) {
    label = "Live Demo Active";
    Icon = CheckCircle2;
  }

  const disabled = activated || pulling;

  return (
    <div className="space-y-1.5 border-t border-slate-100 pt-2.5">
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        className={`flex w-full items-center justify-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold transition-all ${
          activated
            ? "cursor-default border border-emerald-200 bg-emerald-50 text-emerald-700"
            : disabled
              ? "cursor-not-allowed border border-slate-200 bg-slate-100 text-slate-400"
              : "border border-blue-600 bg-blue-600 text-white hover:bg-blue-700"
        }`}
      >
        <Icon className={`h-3.5 w-3.5 ${pulling || running ? "animate-spin" : ""}`} />
        {label}
      </button>
      <p className="text-[11px] leading-snug text-slate-400">
        Pulls the one real Touchless-backed loan and runs the real audit engine against it —
        watch it appear in the Loan Queue and go Running → a real verdict.
      </p>
    </div>
  );
}
