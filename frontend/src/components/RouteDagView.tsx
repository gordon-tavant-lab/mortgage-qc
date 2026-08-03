import { Boxes, FileCheck, GitFork, Merge, Radio } from "lucide-react";
import type { Block, Route } from "../lib/types";

// spec024 US2 (T007), reworked per Gordon's follow-up (2026-08-03): the engine
// actually evaluates a route's active blocks independently, then aggregates every
// block's checks into one verdict -- a fan-out/fan-in shape, not a linear chain.
// This mirrors that: Route entry -> fan-out joint -> N block nodes IN PARALLEL
// (elbow-connected off two shared vertical trunks, CSS-only, no measurement/refs
// needed since every row is a fixed height) -> fan-in joint -> QC Report Generator.
// Still a pure function of route.blockIds -- no local state, no fetch -- so any
// state update to `route` (RoutesFlow.tsx's toggleBlockActive) re-renders this with
// zero extra wiring (FR-005's "no reload" requirement holds for free).
interface RouteDagViewProps {
  route: Route;
  blocks: Block[];
}

const ROW_HEIGHT = 72; // px -- fixed so the trunk lines can be positioned in pure CSS
const ROW_GAP = 8; // px

function EndpointNode({
  icon: Icon,
  title,
  subtitle,
  tone,
}: {
  icon: typeof Radio;
  title: string;
  subtitle: string;
  tone: "source" | "joint" | "sink";
}) {
  const toneClasses =
    tone === "sink"
      ? "border-blue-300 bg-blue-50 ring-1 ring-blue-200"
      : tone === "joint"
        ? "border-slate-200 bg-slate-50"
        : "border-slate-200 bg-slate-50";
  const iconClasses = tone === "sink" ? "bg-blue-100 text-blue-700" : "bg-slate-200 text-slate-600";
  return (
    <div className={`flex w-36 shrink-0 flex-col items-center gap-1.5 rounded-xl border p-3 text-center ${toneClasses}`}>
      <div className={`rounded-lg p-2 ${iconClasses}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="text-xs font-bold text-slate-900">{title}</div>
      <div className="text-[10px] uppercase tracking-wide text-slate-400">{subtitle}</div>
    </div>
  );
}

function HLine() {
  return <div className="h-px w-6 shrink-0 self-center bg-slate-400" />;
}

function ParallelBlockLane({ blocks }: { blocks: Block[] }) {
  const n = blocks.length;
  const totalHeight = n * ROW_HEIGHT + (n - 1) * ROW_GAP;
  const trunkOffset = ROW_HEIGHT / 2;

  const Trunk = ({ align }: { align: "left" | "right" }) => (
    <div className="relative w-6 shrink-0" style={{ height: totalHeight }}>
      {n > 1 && (
        <div
          className={`absolute w-px bg-slate-400 ${align === "left" ? "left-0" : "right-0"}`}
          style={{ top: trunkOffset, height: totalHeight - ROW_HEIGHT }}
        />
      )}
      {blocks.map((b, i) => (
        <div
          key={b.id}
          className={`absolute h-px w-6 bg-slate-400 ${align === "left" ? "left-0" : "right-0"}`}
          style={{ top: i * (ROW_HEIGHT + ROW_GAP) + trunkOffset }}
        />
      ))}
    </div>
  );

  return (
    <div className="flex items-center">
      <Trunk align="left" />
      <div className="flex flex-col" style={{ gap: ROW_GAP }}>
        {blocks.map((b) => (
          <div
            key={b.id}
            className="flex w-48 items-center gap-2 rounded-xl border border-blue-200 bg-blue-50/60 px-3"
            style={{ height: ROW_HEIGHT }}
          >
            <div className="shrink-0 rounded-lg bg-blue-100 p-1.5 text-blue-700">
              <Boxes className="h-3.5 w-3.5" />
            </div>
            <div className="min-w-0">
              <div className="line-clamp-2 text-[11px] font-bold leading-tight text-slate-900">{b.name}</div>
              <div className="mt-0.5 text-[10px] text-slate-500">
                {b.checkIds.length} check{b.checkIds.length === 1 ? "" : "s"}
              </div>
            </div>
          </div>
        ))}
      </div>
      <Trunk align="right" />
    </div>
  );
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
          <EndpointNode icon={Radio} title={route.name} subtitle="Route entry" tone="source" />
          <HLine />
          <EndpointNode icon={GitFork} title="Fan-Out" subtitle="Fan out joint" tone="joint" />
          <ParallelBlockLane blocks={activeBlocks} />
          <EndpointNode icon={Merge} title="Fan-In" subtitle="Fan in joint" tone="joint" />
          <HLine />
          <EndpointNode icon={FileCheck} title="QC Report Generator" subtitle="Reporting" tone="sink" />
        </div>
      )}
    </div>
  );
}
