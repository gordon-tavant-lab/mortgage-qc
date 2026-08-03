import { FileText, Database, FileCode, Info } from "lucide-react";

export function InspectSources() {
  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">
        Before a run, the loan's document data is retrieved from Touchless through three
        sequential calls — confirmed on the 2026-08-01 Touchless call, not an assumed contract.
      </p>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {[
          { icon: FileText, label: "1. Application Results", sub: "GET the application's results — status and summary metadata for the whole application" },
          { icon: Database, label: "2. Indexed Documents", sub: "GET the list of documents Touchless has indexed for that application" },
          { icon: FileCode, label: "3. Extracted Data", sub: "GET the structured fields Touchless extracted from each indexed document" },
        ].map((s) => (
          <div key={s.label} className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
            <div className="rounded-lg border border-blue-100 bg-blue-50 p-2 text-blue-600">
              <s.icon className="h-4 w-4" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-900">{s.label}</div>
              <div className="mt-0.5 text-xs text-slate-500">{s.sub}</div>
            </div>
          </div>
        ))}
      </div>

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
    </div>
  );
}
