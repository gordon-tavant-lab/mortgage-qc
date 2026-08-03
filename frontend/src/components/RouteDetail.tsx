import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRightCircle, ArrowLeftCircle, Layers, ChevronRight, Plus, Trash2 } from "lucide-react";
import { Modal } from "./Modal";
import { BlockMembershipModal } from "./BlockMembershipModal";
import { RouteDagView } from "./RouteDagView";
import type { Route, Block } from "../lib/types";

interface RouteDetailProps {
  route: Route;
  blocks: Block[];
  allRoutes: Route[];
  onToggleBlock: (blockId: string) => void;
  onOpenBlock: (blockId: string) => void;
  onBack: () => void;
  // spec024 US7 (FR-020/021): catalog-level block create/remove, distinct from
  // onToggleBlock's route-membership toggle of an already-catalog block.
  // onCreateBlock appends a brand-new block to the catalog (not active on any
  // route); onRemoveBlock permanently deletes one and returns whether it
  // succeeded -- false means it's still active somewhere and was refused.
  onCreateBlock: (name: string, description: string) => void;
  onRemoveBlock: (blockId: string) => boolean;
}

const PAGE_SIZE = 25;

// The gold-ruleset rework (2026-08-01, superseded 2026-08-02 by spec021 US3's
// four-route split) gives every route its own block pool per AMQ category (ids
// prefixed "conv-"/"fha-"/"va-"/"usda-") so each can carry a different check
// population -- Conventional real, FHA/VA/USDA genuinely empty (spec024 US5; see
// BlockDetail.tsx's isRealCoverageBlock guard and build_gold_catalog.py). Without
// this scoping, every route's "available blocks" list would show every OTHER
// route's same-category block as if it were an unused option to add (e.g. "Assets
// (FHA)" appearing as addable to the Conventional route) -- confusing duplicates,
// not a real choice. Custom SME-created routes (no recognized prefix) keep the
// original shared-pool behavior -- any block is fair game.
export const ROUTE_BLOCK_PREFIX: Record<string, string> = {
  conventional: "conv-",
  fha: "fha-",
  va: "va-",
  usda: "usda-",
};

export function RouteDetail({
  route,
  blocks,
  allRoutes,
  onToggleBlock,
  onOpenBlock,
  onBack,
  onCreateBlock,
  onRemoveBlock,
}: RouteDetailProps) {
  const prefix = ROUTE_BLOCK_PREFIX[route.id];
  const relevantBlocks = prefix ? blocks.filter((b) => b.id.startsWith(prefix)) : blocks;
  const available = relevantBlocks.filter((b) => !route.blockIds.includes(b.id));
  const active = relevantBlocks.filter((b) => route.blockIds.includes(b.id));

  const otherRoutesUsing = (blockId: string) =>
    allRoutes.filter((r) => r.id !== route.id && r.blockIds.includes(blockId)).length;

  const [availablePage, setAvailablePage] = useState(0);
  const [activePage, setActivePage] = useState(0);
  useEffect(() => setAvailablePage(0), [route.id]);
  useEffect(() => setActivePage(0), [route.id]);

  const availableTotalPages = Math.max(1, Math.ceil(available.length / PAGE_SIZE));
  const availableCurrentPage = Math.min(availablePage, availableTotalPages - 1);
  const pagedAvailable = available.slice(
    availableCurrentPage * PAGE_SIZE,
    availableCurrentPage * PAGE_SIZE + PAGE_SIZE
  );

  const activeTotalPages = Math.max(1, Math.ceil(active.length / PAGE_SIZE));
  const activeCurrentPage = Math.min(activePage, activeTotalPages - 1);
  const pagedActive = active.slice(activeCurrentPage * PAGE_SIZE, activeCurrentPage * PAGE_SIZE + PAGE_SIZE);

  // spec024 US1 (FR-002): activation/deactivation opens as a confirm modal instead
  // of the previous direct one-click toggle. `membershipBlockId` tracks which
  // block's modal is open; the modal itself is the only thing that calls
  // onToggleBlock, so dismissing (Escape / outside-click / no action) never mutates
  // anything (FR-009).
  const [membershipBlockId, setMembershipBlockId] = useState<string | null>(null);
  const membershipBlock = relevantBlocks.find((b) => b.id === membershipBlockId) ?? null;

  // spec024 US6 (FR-017/018/019): the route page opens DAG-only; the Available/Active
  // Blocks list boxes only appear once the rule author explicitly clicks Edit.
  const [editModalOpen, setEditModalOpen] = useState(false);

  // spec024 US7 (FR-020/021): catalog-level block create/remove -- a new block appears
  // in Available Blocks (never auto-active); remove is only offered here, on Available
  // rows, and is refused (message shown, nothing deleted) if the block is still active
  // on any route (onRemoveBlock's own guard, checked before this component ever sees the
  // result).
  const [showNewBlockForm, setShowNewBlockForm] = useState(false);
  const [newBlockName, setNewBlockName] = useState("");
  const [newBlockDescription, setNewBlockDescription] = useState("");
  const [confirmRemoveBlockId, setConfirmRemoveBlockId] = useState<string | null>(null);
  const [removeBlockedMessage, setRemoveBlockedMessage] = useState<string | null>(null);

  function handleCreateBlock() {
    if (!newBlockName.trim()) return;
    onCreateBlock(newBlockName.trim(), newBlockDescription.trim());
    setNewBlockName("");
    setNewBlockDescription("");
    setShowNewBlockForm(false);
  }

  function handleRemoveBlock(blockId: string, blockName: string) {
    const removed = onRemoveBlock(blockId);
    setConfirmRemoveBlockId(null);
    setRemoveBlockedMessage(
      removed ? null : `"${blockName}" is still active on another route -- deactivate it there first.`
    );
  }

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

      <RouteDagView route={route} blocks={blocks} onEdit={() => setEditModalOpen(true)} />

      <Modal open={editModalOpen} onClose={() => setEditModalOpen(false)} title="Edit Blocks" widthClassName="max-w-5xl">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
          <div className="mb-3 flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
              <Layers className="h-3.5 w-3.5" /> Available Blocks
            </span>
            <div className="flex items-center gap-2">
              <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-bold text-slate-600">
                {available.length}
              </span>
              <button
                onClick={() => setShowNewBlockForm((v) => !v)}
                className="flex items-center gap-1 rounded-lg bg-blue-600 px-2 py-1 text-[11px] font-semibold text-white shadow-sm transition hover:bg-blue-700"
              >
                <Plus className="h-3 w-3" />
                New Block
              </button>
            </div>
          </div>
          {showNewBlockForm && (
            <div className="mb-3 space-y-2 rounded-lg border border-blue-200 bg-blue-50/40 p-3">
              <div>
                <label htmlFor="new-block-name" className="mb-1 block text-[10px] font-semibold uppercase text-slate-500">
                  Block Name
                </label>
                <input
                  id="new-block-name"
                  name="new-block-name"
                  value={newBlockName}
                  onChange={(e) => setNewBlockName(e.target.value)}
                  placeholder="e.g., Custom Escrow Review"
                  className="w-full rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-800 focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label htmlFor="new-block-desc" className="mb-1 block text-[10px] font-semibold uppercase text-slate-500">
                  Description
                </label>
                <input
                  id="new-block-desc"
                  name="new-block-desc"
                  value={newBlockDescription}
                  onChange={(e) => setNewBlockDescription(e.target.value)}
                  placeholder="Summarize what this block covers"
                  className="w-full rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowNewBlockForm(false)}
                  className="rounded-lg border border-slate-200 px-2.5 py-1 text-[11px] font-semibold text-slate-500 hover:bg-white"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateBlock}
                  disabled={!newBlockName.trim()}
                  className="rounded-lg bg-blue-600 px-2.5 py-1 text-[11px] font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Create Block
                </button>
              </div>
            </div>
          )}
          {removeBlockedMessage && (
            <div className="mb-3 rounded-lg border border-amber-200 bg-amber-50 px-2.5 py-1.5 text-[11px] text-amber-800">
              {removeBlockedMessage}
            </div>
          )}
          <div className="space-y-2">
            {pagedAvailable.map((block) => {
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
                  {confirmRemoveBlockId === block.id ? (
                    <div className="flex shrink-0 items-center gap-1">
                      <button
                        onClick={() => handleRemoveBlock(block.id, block.name)}
                        className="rounded-lg bg-rose-600 px-2 py-1 text-[10px] font-semibold text-white hover:bg-rose-700"
                      >
                        Confirm
                      </button>
                      <button
                        onClick={() => setConfirmRemoveBlockId(null)}
                        className="rounded-lg border border-slate-200 px-2 py-1 text-[10px] font-semibold text-slate-500 hover:bg-slate-50"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => {
                        setRemoveBlockedMessage(null);
                        setConfirmRemoveBlockId(block.id);
                      }}
                      className="shrink-0 rounded-lg p-1.5 text-slate-300 hover:bg-rose-50 hover:text-rose-500"
                      title="Remove this block from the catalog"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={() => setMembershipBlockId(block.id)}
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
          {available.length > PAGE_SIZE && (
            <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3 text-[11px] text-slate-500">
              <span>
                Showing {availableCurrentPage * PAGE_SIZE + 1}–
                {Math.min((availableCurrentPage + 1) * PAGE_SIZE, available.length)} of {available.length}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setAvailablePage((p) => Math.max(0, p - 1))}
                  disabled={availableCurrentPage === 0}
                  className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>
                <span className="font-mono">
                  Page {availableCurrentPage + 1} of {availableTotalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setAvailablePage((p) => Math.min(availableTotalPages - 1, p + 1))}
                  disabled={availableCurrentPage >= availableTotalPages - 1}
                  className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          )}
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
            {pagedActive.map((block) => (
              <div key={block.id} className="flex items-start gap-2.5 rounded-lg border border-blue-200 bg-white p-3">
                <button
                  onClick={() => setMembershipBlockId(block.id)}
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
          {active.length > PAGE_SIZE && (
            <div className="mt-3 flex items-center justify-between border-t border-blue-100 pt-3 text-[11px] text-blue-700/70">
              <span>
                Showing {activeCurrentPage * PAGE_SIZE + 1}–
                {Math.min((activeCurrentPage + 1) * PAGE_SIZE, active.length)} of {active.length}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setActivePage((p) => Math.max(0, p - 1))}
                  disabled={activeCurrentPage === 0}
                  className="rounded-lg border border-blue-200 px-2.5 py-1 font-semibold text-blue-700 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>
                <span className="font-mono">
                  Page {activeCurrentPage + 1} of {activeTotalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setActivePage((p) => Math.min(activeTotalPages - 1, p + 1))}
                  disabled={activeCurrentPage >= activeTotalPages - 1}
                  className="rounded-lg border border-blue-200 px-2.5 py-1 font-semibold text-blue-700 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      </Modal>

      <Modal open={membershipBlock != null} onClose={() => setMembershipBlockId(null)} title="Edit block membership">
        {membershipBlock && (
          <BlockMembershipModal
            block={membershipBlock}
            isActive={route.blockIds.includes(membershipBlock.id)}
            usedElsewhere={otherRoutesUsing(membershipBlock.id)}
            onConfirm={() => {
              onToggleBlock(membershipBlock.id);
              setMembershipBlockId(null);
            }}
          />
        )}
      </Modal>
    </div>
  );
}
