import { ArrowLeft, ArrowRightCircle, ArrowLeftCircle, Layers, ChevronRight } from "lucide-react";
import type { Route, Block } from "../lib/types";

interface RouteDetailProps {
  route: Route;
  blocks: Block[];
  allRoutes: Route[];
  onToggleBlock: (blockId: string) => void;
  onOpenBlock: (blockId: string) => void;
  onBack: () => void;
}

export function RouteDetail({ route, blocks, allRoutes, onToggleBlock, onOpenBlock, onBack }: RouteDetailProps) {
  const available = blocks.filter((b) => !route.blockIds.includes(b.id));
  const active = blocks.filter((b) => route.blockIds.includes(b.id));

  const otherRoutesUsing = (blockId: string) =>
    allRoutes.filter((r) => r.id !== route.id && r.blockIds.includes(blockId)).length;

  return (
    <div className="space-y-5">
      <div>
        <button onClick={onBack} className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-700">
          <ArrowLeft className="h-3.5 w-3.5" />
          All Routes
        </button>
        <div className="mt-2">
          <h2 className="font-display text-lg font-bold text-slate-900">{route.name}</h2>
          <p className="mt-0.5 text-xs italic text-slate-500">"{route.description}"</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="mb-3 flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
              <Layers className="h-3.5 w-3.5" /> Available Blocks
            </span>
            <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-bold text-slate-600">
              {available.length}
            </span>
          </div>
          <div className="space-y-2">
            {available.map((block) => {
              const usedElsewhere = otherRoutesUsing(block.id);
              return (
                <div key={block.id} className="flex items-start gap-2.5 rounded-lg border border-slate-150 bg-slate-50/40 p-3">
                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-bold text-slate-900">{block.name}</div>
                    <p className="mt-0.5 text-[11px] leading-snug text-slate-500">{block.description}</p>
                    {usedElsewhere > 0 && (
                      <span className="mt-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-semibold text-blue-600">
                        also active in {usedElsewhere} other route{usedElsewhere > 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => onToggleBlock(block.id)}
                    className="shrink-0 rounded-lg p-1.5 text-blue-600 hover:bg-blue-50"
                    title="Activate this block on the route"
                  >
                    <ArrowRightCircle className="h-5 w-5" />
                  </button>
                </div>
              );
            })}
            {available.length === 0 && (
              <div className="py-6 text-center text-xs text-slate-400">All blocks are active on this route.</div>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-blue-200 bg-blue-50/20 p-4 shadow-[var(--shadow-panel)]">
          <div className="mb-3 flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-blue-700">
              <Layers className="h-3.5 w-3.5" /> Active Blocks
            </span>
            <span className="rounded bg-blue-100 px-2 py-0.5 font-mono text-[10px] font-bold text-blue-700">
              {active.length} wired
            </span>
          </div>
          <div className="space-y-2">
            {active.map((block) => (
              <div key={block.id} className="flex items-start gap-2.5 rounded-lg border border-blue-200 bg-white p-3">
                <button
                  onClick={() => onToggleBlock(block.id)}
                  className="shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-600"
                  title="Deactivate this block from the route"
                >
                  <ArrowLeftCircle className="h-5 w-5" />
                </button>
                <button onClick={() => onOpenBlock(block.id)} className="min-w-0 flex-1 text-left">
                  <div className="text-xs font-bold text-slate-900">{block.name}</div>
                  <p className="mt-0.5 text-[11px] leading-snug text-slate-500">{block.description}</p>
                  <span className="mt-1 inline-block font-mono text-[10px] text-slate-400">
                    {block.checkIds.length} compiled check{block.checkIds.length === 1 ? "" : "s"}
                  </span>
                </button>
                <button onClick={() => onOpenBlock(block.id)} className="shrink-0 text-slate-300 hover:text-slate-500">
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            ))}
            {active.length === 0 && (
              <div className="py-6 text-center text-xs text-blue-400/70">
                No blocks wired yet. Activate one from the pool on the left.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
