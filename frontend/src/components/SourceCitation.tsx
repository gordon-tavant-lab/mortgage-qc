import { BookMarked } from "lucide-react";
import { PlaceholderBadge } from "./PlaceholderBadge";
import type { Check } from "../lib/types";

// Citation across the compile pipeline: grounding (a Guide-section citation
// attached at compile time) is the strongest, sourceLocator (raw AMQ
// row/sheet) is the fallback, and "no citation" is shown as a flagged gap --
// consistent with the mockup's discipline of never hiding what's missing.
// Reused by both the Guided Editor's Edit Check panel and Import & Sign's
// diff-and-sign review, since both surfaces need the same stage-2 citation
// story.
export function SourceCitation({ check, compact = false }: { check: Check; compact?: boolean }) {
  const hasGrounding = check.grounding && check.grounding.length > 0;
  const hasLocator = !!check.sourceLocator;

  return (
    <div className={compact ? "" : "rounded-lg border border-slate-150 bg-white p-3"}>
      {!compact && (
        <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
          <BookMarked className="h-3 w-3" /> Source Citation
        </div>
      )}
      {hasGrounding && (
        <div className="space-y-1.5">
          {check.grounding!.map((g, i) => (
            <div key={i} className="flex items-center gap-1.5 text-[11px] text-slate-700">
              <span className="rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-emerald-700">
                {g.sectionId}
              </span>
              <span>
                {g.source} — {g.title} ({g.revisionDate})
              </span>
            </div>
          ))}
        </div>
      )}
      {!hasGrounding && hasLocator && (
        <div className="flex items-center gap-1.5 text-[11px] text-slate-600">
          <BookMarked className="h-3 w-3 shrink-0 text-slate-400" />
          {check.sourceLocator!.workbook} — {check.sourceLocator!.sheet}, row {check.sourceLocator!.row}
        </div>
      )}
      {!hasGrounding && !hasLocator && (
        <div className="flex items-center gap-1.5">
          <PlaceholderBadge label="no citation captured at compile time" />
        </div>
      )}
    </div>
  );
}
