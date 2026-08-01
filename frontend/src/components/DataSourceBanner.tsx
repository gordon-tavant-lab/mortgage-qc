import { FlaskConical, Radio } from "lucide-react";
import { useDataSource } from "../lib/dataSourceContext";

// DataSourceBanner (formerly SampleDataBanner) — FR-011. Extends the existing "sim badge"
// honesty pattern (CLAUDE.md/output/DEMO-UX-LESSONS.md §5) rather than introducing a new,
// unrelated indicator: Stored keeps the original amber/purple "sample data" treatment;
// Live gets a visually distinct blue/green treatment so the two can never be mistaken for
// one another.
export function DataSourceBanner() {
  const { mode, pulledApplications } = useDataSource();

  if (mode === "stored") {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-purple-200 bg-purple-50 px-3 py-2 text-xs font-medium text-purple-800">
        <FlaskConical className="h-3.5 w-3.5 shrink-0" />
        <span>
          Stored (sample data) — every number on this screen is sample data, not a live engine run.
        </span>
      </div>
    );
  }

  const mostRecentPull = [...pulledApplications.values()].sort(
    (a, b) => new Date(b.fetchedAt).getTime() - new Date(a.fetchedAt).getTime(),
  )[0];

  return (
    <div className="flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-medium text-blue-800">
      <Radio className="h-3.5 w-3.5 shrink-0" />
      <span>
        {mostRecentPull
          ? `Live — pulled at ${new Date(mostRecentPull.fetchedAt).toLocaleTimeString()}`
          : "Live — no application pulled yet this session. Use Pull Live Application below."}
      </span>
    </div>
  );
}
