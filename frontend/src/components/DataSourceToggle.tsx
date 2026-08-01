import { useDataSource, type DataSourceMode } from "../lib/dataSourceContext";

// DataSourceToggle — FR-003/FR-004. Lives inside SettingsMenu, not the primary nav (SC-003).
// Session-scoped only: flipping this never touches the URL and never survives a reload
// (plan.md §2.3 — in-memory React state only).
const OPTIONS: { id: DataSourceMode; label: string }[] = [
  { id: "stored", label: "Stored" },
  { id: "live", label: "Live" },
];

export function DataSourceToggle() {
  const { mode, setMode } = useDataSource();

  return (
    <div className="space-y-1.5">
      <div className="text-xs font-medium text-slate-600">Data Source</div>
      <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
        {OPTIONS.map((option) => (
          <button
            key={option.id}
            type="button"
            onClick={() => setMode(option.id)}
            className={`flex-1 rounded-md px-2.5 py-1 text-xs font-semibold transition-all ${
              mode === option.id ? "bg-blue-600 text-white shadow-sm" : "text-slate-500 hover:bg-slate-100"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
      <p className="text-[11px] leading-snug text-slate-400">
        Demo/testing only — resets to Stored on a new browser session, never persists.
      </p>
    </div>
  );
}
