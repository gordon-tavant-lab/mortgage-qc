import { useEffect, useRef, useState } from "react";
import { Settings } from "lucide-react";
import { DataSourceToggle } from "./DataSourceToggle";
import { ActivateLiveDemoButton } from "./ActivateLiveDemoButton";

// SettingsMenu — a small gear-icon dropdown tucked in the Navbar (NOT a 4th main nav tab)
// so the data-source toggle satisfies SC-003 ("the control is not visible in the primary
// navigation"). Room to add more demo/testing-only controls here later without growing the
// primary nav.
export function SettingsMenu() {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handlePointerDown(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, [open]);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Settings"
        aria-expanded={open}
        className="flex items-center justify-center rounded-lg border border-slate-700 bg-slate-800/60 p-2 text-slate-400 transition-colors hover:bg-slate-700/60 hover:text-white"
      >
        <Settings className="h-4 w-4" />
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-64 rounded-xl border border-slate-200 bg-white p-3 shadow-[var(--shadow-panel)]">
          <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            Demo / Testing Settings
          </div>
          <DataSourceToggle />
          <ActivateLiveDemoButton onActivated={() => setOpen(false)} />
        </div>
      )}
    </div>
  );
}
