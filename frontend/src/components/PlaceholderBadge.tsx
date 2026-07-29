import { FlaskConical } from "lucide-react";

// Marks a specific field/check that has no real p0/qc_engine counterpart yet
// (e.g. reserve_months) -- distinct from SampleDataBanner, which marks the
// whole screen as mock data. This badge survives even in a "real" build.
export function PlaceholderBadge({ label = "not yet in engine" }: { label?: string }) {
  return (
    <span
      className="inline-flex items-center gap-1 rounded border border-purple-200 bg-purple-50 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-purple-700"
      title="This field/check has no real backend counterpart in p0/qc_engine yet."
    >
      <FlaskConical className="h-2.5 w-2.5" />
      {label}
    </span>
  );
}
