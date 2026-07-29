import { FlaskConical } from "lucide-react";

export function SampleDataBanner() {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-purple-200 bg-purple-50 px-3 py-2 text-xs font-medium text-purple-800">
      <FlaskConical className="h-3.5 w-3.5 shrink-0" />
      <span>
        Design-review mockup — every number on this screen is sample data, not a live engine run.
      </span>
    </div>
  );
}
