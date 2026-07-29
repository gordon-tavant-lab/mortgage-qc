import {
  ShieldCheck,
  ListChecks,
  ScanEye,
  PlayCircle,
  FileSpreadsheet,
  Sliders,
  ClipboardCheck,
  CheckCircle2,
} from "lucide-react";
import type { ViewId } from "../lib/nav";

const NAV_ITEMS: { id: ViewId; label: string; icon: typeof ListChecks; group: string }[] = [
  { id: "queue", label: "Loan Queue", icon: ListChecks, group: "" },
  { id: "inspect", label: "Inspect Sources", icon: ScanEye, group: "" },
  { id: "apply", label: "Apply", icon: PlayCircle, group: "" },
  { id: "author-import", label: "Import & Sign", icon: FileSpreadsheet, group: "Author" },
  { id: "author-guided", label: "Guided Editor", icon: Sliders, group: "Author" },
  { id: "review", label: "Exception Review", icon: ClipboardCheck, group: "" },
];

interface NavbarProps {
  activeView: ViewId;
  onSelectView: (v: ViewId) => void;
  exceptionCount: number;
}

export function Navbar({ activeView, onSelectView, exceptionCount }: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-900">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-between gap-3 px-4 py-2.5">
        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-blue-500/30 bg-blue-500/15 p-2 text-blue-400">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display text-base font-bold tracking-tight text-white">
                Mortgage QA/QC Engine
              </h1>
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
                <CheckCircle2 className="h-3 w-3" />
                Pure Deterministic
              </span>
            </div>
            <p className="hidden text-xs text-slate-400 sm:block">
              Exact Decimal Math · Non-IT Authoring · Bit-Exact Harness
            </p>
          </div>
        </div>

        <nav className="flex flex-wrap items-center gap-1 rounded-xl border border-slate-800 bg-slate-800/60 p-1">
          {NAV_ITEMS.map((item) => {
            const isActive = activeView === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onSelectView(item.id)}
                className={`relative flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-400 hover:bg-slate-700/60 hover:text-white"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{item.label}</span>
                {item.id === "review" && exceptionCount > 0 && (
                  <span className="ml-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white">
                    {exceptionCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
