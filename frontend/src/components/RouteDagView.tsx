import { ArrowRight, Boxes, Radio } from "lucide-react";
import type { Block, Route } from "../lib/types";

// spec024 US2 (T007): live, read-only DAG of a route's currently-active blocks --
// mirrors QcAuditProcessFlow.tsx's existing flexbox-row + ArrowRight-connector
// pattern exactly (same visual language already shipping in this app), rather than
// pulling in a general graph-layout library the requirement doesn't call for (FR-006:
// a connected, directed sequence, not an unordered set).
//
// A pure function of route.blockIds -- no local state, no fetch. Any state update to
// `route` (e.g. RoutesFlow.tsx's toggleBlockActive) re-renders this with zero extra
// wiring, which is what makes FR-005's "no reload" requirement true for free.
interface RouteDagViewProps {
  route: Route;
  blocks: Block[];
}

export function RouteDagView({ route, blocks }: RouteDagViewProps) {
  const activeBlocks = route.blockIds
    .map((id) => blocks.find((b) => b.id === id))
    .filter((b): b is Block => Boolean(b));

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)]">
      <div className="mb-3 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
        <Boxes className="h-3.5 w-3.5" />
        Active Block Sequence
      </div>
      {activeBlocks.length === 0 ? (
        <div className="py-6 text-center text-xs text-slate-400">
          No blocks are active on this route yet. Activate one below to see it appear here.
        </div>
      ) : (
        <div className="flex min-w-max items-center">
          <div className="flex items-center">
            <div className="flex w-36 shrink-0 flex-col items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <div className="rounded-lg bg-slate-200 p-2 text-slate-600">
                <Radio className="h-4 w-4" />
              </div>
              <div className="text-xs font-bold text-slate-900">{route.name}</div>
              <div className="text-[11px] leading-snug text-slate-500">Route entry</div>
            </div>
          </div>
          {activeBlocks.map((block) => (
            <div key={block.id} className="flex items-center">
              <ArrowRight className="mx-1 h-4 w-4 shrink-0 text-blue-300 sm:mx-2" />
              <div className="flex w-40 shrink-0 flex-col items-center gap-1.5 rounded-xl border border-blue-200 bg-blue-50/60 p-3 text-center sm:w-44">
                <div className="rounded-lg bg-blue-100 p-2 text-blue-700">
                  <Boxes className="h-4 w-4" />
                </div>
                <div className="text-xs font-bold text-slate-900">{block.name}</div>
                <div className="text-[11px] leading-snug text-slate-500">
                  {block.checkIds.length} check{block.checkIds.length === 1 ? "" : "s"}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
