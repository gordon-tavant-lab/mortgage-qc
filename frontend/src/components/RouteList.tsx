import { useState } from "react";
import { Plus, GitFork, ChevronRight, Trash2, Layers, ClipboardList } from "lucide-react";
import type { Route, Block } from "../lib/types";

interface RouteListProps {
  routes: Route[];
  blocks: Block[];
  onCreateRoute: (name: string, description: string) => void;
  onRemoveRoute: (routeId: string) => void;
  onOpenRoute: (routeId: string) => void;
}

export function RouteList({ routes, blocks, onCreateRoute, onRemoveRoute, onOpenRoute }: RouteListProps) {
  const [showNewForm, setShowNewForm] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [confirmRemoveId, setConfirmRemoveId] = useState<string | null>(null);

  const checkCountFor = (route: Route) =>
    route.blockIds.reduce((sum, blockId) => {
      const block = blocks.find((b) => b.id === blockId);
      return sum + (block?.checkIds.length ?? 0);
    }, 0);

  const handleCreate = () => {
    if (!newName.trim()) return;
    onCreateRoute(newName.trim(), newDescription.trim() || "Custom configured SME mortgage review route");
    setNewName("");
    setNewDescription("");
    setShowNewForm(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Configured Routes</h3>
          <p className="mt-0.5 text-xs text-slate-500">
            Point a route at a target set of loans. Drill into a route to wire its blocks.
          </p>
        </div>
        <button
          onClick={() => setShowNewForm((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700"
        >
          <Plus className="h-3.5 w-3.5" />
          New Route
        </button>
      </div>

      {showNewForm && (
        <div className="space-y-3 rounded-xl border border-blue-200 bg-blue-50/40 p-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <label htmlFor="new-route-name" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
                Route Name
              </label>
              <input
                id="new-route-name"
                name="new-route-name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g., Freddie Mac Standard Purchase Route"
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="new-route-desc" className="mb-1 block text-xs font-semibold uppercase text-slate-500">
                Description
              </label>
              <input
                id="new-route-desc"
                name="new-route-desc"
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Summarize target loans and program"
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700 focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowNewForm(false)}
              className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-500 hover:bg-white"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={!newName.trim()}
              className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Create Route
            </button>
          </div>
        </div>
      )}

      <div className="divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-[var(--shadow-panel)]">
        {routes.map((route) => (
          <div
            key={route.id}
            className="group flex items-center gap-3 px-4 py-3.5 transition hover:bg-slate-50/70"
          >
            <div className="rounded-lg border border-blue-100 bg-blue-50 p-2 text-blue-600">
              <GitFork className="h-4 w-4" />
            </div>
            <button onClick={() => onOpenRoute(route.id)} className="min-w-0 flex-1 text-left">
              <div className="text-sm font-bold text-slate-900">{route.name}</div>
              <p className="mt-0.5 truncate text-xs italic text-slate-500">"{route.description}"</p>
            </button>
            <div className="hidden items-center gap-4 text-xs text-slate-500 sm:flex">
              <span className="flex items-center gap-1">
                <Layers className="h-3.5 w-3.5 text-slate-400" />
                {route.blockIds.length} block{route.blockIds.length === 1 ? "" : "s"}
              </span>
              <span className="flex items-center gap-1">
                <ClipboardList className="h-3.5 w-3.5 text-slate-400" />
                {checkCountFor(route)} checks
              </span>
            </div>

            {confirmRemoveId === route.id ? (
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => {
                    onRemoveRoute(route.id);
                    setConfirmRemoveId(null);
                  }}
                  className="rounded-lg bg-rose-600 px-2.5 py-1.5 text-[11px] font-semibold text-white hover:bg-rose-700"
                >
                  Confirm Remove
                </button>
                <button
                  onClick={() => setConfirmRemoveId(null)}
                  className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-[11px] font-semibold text-slate-500 hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setConfirmRemoveId(route.id)}
                className="rounded-lg p-2 text-slate-300 opacity-0 transition hover:bg-rose-50 hover:text-rose-500 group-hover:opacity-100"
                title="Remove route"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}

            <button onClick={() => onOpenRoute(route.id)} className="text-slate-300 hover:text-slate-500">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        ))}

        {routes.length === 0 && (
          <div className="px-4 py-10 text-center text-xs text-slate-400">
            No routes configured yet. Click "New Route" to create one.
          </div>
        )}
      </div>
    </div>
  );
}
