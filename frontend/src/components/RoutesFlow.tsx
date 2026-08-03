import { useState, useEffect, useRef } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { MOCK_SIGNED_RULESET } from "../data/mockData";
import { GOLD_ROUTES, GOLD_BLOCKS, GOLD_CHECKS } from "../data/goldCatalog";
import { SignAndPinBar } from "./SignAndPinBar";
import { RouteList } from "./RouteList";
import { RouteDetail } from "./RouteDetail";
import { BlockDetail } from "./BlockDetail";
import { loadDraft, saveDraft, clearDraft, reconcileDraft, QuotaExceededError } from "../lib/rulesetStore";
import { useDataSource } from "../lib/dataSourceContext";
import type { Route, Block, Check } from "../lib/types";

type Level = { level: "list" } | { level: "route"; routeId: string } | { level: "block"; routeId: string; blockId: string };

let routeCounter = 0;

// Hydrate once at module scope so both the initial state AND the "was there
// a stale draft" report agree on the same reconciliation pass.
const initialDraft = loadDraft();
const initialHydration = initialDraft
  ? reconcileDraft(initialDraft.content, GOLD_CHECKS)
  : { content: { routes: GOLD_ROUTES, blocks: GOLD_BLOCKS, checks: GOLD_CHECKS }, missingCheckIds: [] as string[] };

export function RoutesFlow() {
  const { resetFetchedApplications } = useDataSource();
  const [routes, setRoutes] = useState<Route[]>(() => structuredClone(initialHydration.content.routes));
  const [blocks, setBlocks] = useState<Block[]>(() => structuredClone(initialHydration.content.blocks));
  const [checks, setChecks] = useState<Check[]>(() => structuredClone(initialHydration.content.checks));
  const [dirtyCount, setDirtyCount] = useState(0);
  const [justSigned, setJustSigned] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [missingCheckIds] = useState(initialHydration.missingCheckIds);
  const [lastSigned, setLastSigned] = useState({
    sha256: initialDraft?.sha256 ?? MOCK_SIGNED_RULESET.sha256,
    signedAt: initialDraft?.signoff_summary?.signedAt ?? MOCK_SIGNED_RULESET.signedAt,
    signedBy: initialDraft?.signoff_summary?.signedBy ?? MOCK_SIGNED_RULESET.signedBy,
  });
  const [nav, setNav] = useState<Level>({ level: "list" });
  const signedOnceRef = useRef(Boolean(initialDraft?.signoff_summary));
  const lastSignedRef = useRef(
    initialDraft?.signoff_summary ?? { signedBy: MOCK_SIGNED_RULESET.signedBy, signedAt: MOCK_SIGNED_RULESET.signedAt }
  );

  const bumpDirty = () => {
    setDirtyCount((n) => n + 1);
    setJustSigned(false);
  };

  const createRoute = (name: string, description: string) => {
    routeCounter += 1;
    setRoutes((prev) => [...prev, { id: `rt-custom-${routeCounter}`, name, description, blockIds: [] }]);
    bumpDirty();
  };

  const removeRoute = (routeId: string) => {
    setRoutes((prev) => prev.filter((r) => r.id !== routeId));
    bumpDirty();
  };

  const toggleBlockActive = (routeId: string, blockId: string) => {
    setRoutes((prev) =>
      prev.map((r) => {
        if (r.id !== routeId) return r;
        const isActive = r.blockIds.includes(blockId);
        return { ...r, blockIds: isActive ? r.blockIds.filter((id) => id !== blockId) : [...r.blockIds, blockId] };
      })
    );
    bumpDirty();
  };

  const toggleCheckActive = (blockId: string, checkId: string) => {
    setBlocks((prev) =>
      prev.map((b) => {
        if (b.id !== blockId) return b;
        const isActive = b.checkIds.includes(checkId);
        return { ...b, checkIds: isActive ? b.checkIds.filter((id) => id !== checkId) : [...b.checkIds, checkId] };
      })
    );
    bumpDirty();
  };

  const updateCheck = (checkId: string, updates: Partial<Check>) => {
    setChecks((prev) => prev.map((c) => (c.id === checkId ? { ...c, ...updates } : c)));
    bumpDirty();
  };

  // Auto-save (FR-013 / T024): persists on every real content change, decoupled
  // from Sign & Pin -- a refresh must not lose work even before the SME
  // formally signs. Carries forward the last real signoff (not the mockup's
  // placeholder) so a save between signs doesn't fabricate one.
  useEffect(() => {
    let cancelled = false;
    const signoff = signedOnceRef.current ? lastSignedRef.current : null;
    saveDraft({ routes, blocks, checks }, signoff)
      .then(() => {
        if (!cancelled) setSaveError(null);
      })
      .catch((err) => {
        if (cancelled) return;
        setSaveError(err instanceof QuotaExceededError ? err.message : "Could not save draft.");
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [routes, blocks, checks]);

  const signAndPin = async () => {
    const signedAt = new Date().toISOString();
    const signedBy = MOCK_SIGNED_RULESET.signedBy;
    const draft = await saveDraft({ routes, blocks, checks }, { signedBy, signedAt });
    signedOnceRef.current = true;
    lastSignedRef.current = { signedBy, signedAt };
    setLastSigned({ sha256: draft.sha256, signedAt, signedBy });
    setDirtyCount(0);
    setJustSigned(true);
  };

  const restoreToGold = () => {
    clearDraft();
    setRoutes(structuredClone(GOLD_ROUTES));
    setBlocks(structuredClone(GOLD_BLOCKS));
    setChecks(structuredClone(GOLD_CHECKS));
    setDirtyCount(0);
    setJustSigned(false);
    setSaveError(null);
    signedOnceRef.current = false;
    setLastSigned({
      sha256: MOCK_SIGNED_RULESET.sha256,
      signedAt: MOCK_SIGNED_RULESET.signedAt,
      signedBy: MOCK_SIGNED_RULESET.signedBy,
    });
    // spec021 US2 (T026): one reset button for the whole demo -- also clears whatever
    // fetched Touchless loan/audit-run state exists, not just the ruleset draft, so the
    // demo returns to a genuinely fresh starting state (SC-003).
    resetFetchedApplications();
  };

  const openRoute = (routeId: string) => setNav({ level: "route", routeId });
  const openBlock = (routeId: string, blockId: string) => setNav({ level: "block", routeId, blockId });
  const backToList = () => setNav({ level: "list" });
  const backToRoute = (routeId: string) => setNav({ level: "route", routeId });

  const activeRoute = nav.level !== "list" ? routes.find((r) => r.id === nav.routeId) : undefined;
  const activeBlock = nav.level === "block" ? blocks.find((b) => b.id === nav.blockId) : undefined;

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h2 className="font-display text-xl font-bold text-slate-900">Author — Routes</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          Catalog-constrained controls only — pick, wire, and edit from a pool of existing routes,
          blocks, and checks. This surface owns the criteria gate so free text never does (Tension
          8). No AI drafting in this view, by decision.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-0">
          <SignAndPinBar dirtyCount={dirtyCount} lastSigned={lastSigned} justSigned={justSigned} onSign={signAndPin} />
        </div>
        <button
          onClick={restoreToGold}
          className="flex shrink-0 items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-500 shadow-sm transition hover:border-rose-200 hover:text-rose-600"
          title="Discard local edits and reset to the original gold-sourced catalog"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Restore to Gold
        </button>
      </div>

      {saveError && (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-medium text-rose-700">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
          {saveError}
        </div>
      )}

      {missingCheckIds.length > 0 && (
        <div className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-800">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
          {missingCheckIds.length} check{missingCheckIds.length > 1 ? "s" : ""} from your saved draft no
          longer exist in the current catalog and {missingCheckIds.length > 1 ? "were" : "was"} removed.
        </div>
      )}

      {nav.level === "list" && (
        <RouteList
          routes={routes}
          blocks={blocks}
          onCreateRoute={createRoute}
          onRemoveRoute={removeRoute}
          onOpenRoute={openRoute}
        />
      )}

      {nav.level === "route" && activeRoute && (
        <RouteDetail
          route={activeRoute}
          blocks={blocks}
          allRoutes={routes}
          onToggleBlock={(blockId) => toggleBlockActive(activeRoute.id, blockId)}
          onOpenBlock={(blockId) => openBlock(activeRoute.id, blockId)}
          onBack={backToList}
        />
      )}

      {nav.level === "block" && activeRoute && activeBlock && (
        <BlockDetail
          block={activeBlock}
          routeName={activeRoute.name}
          checks={checks}
          allBlocks={blocks}
          onToggleCheck={(checkId) => toggleCheckActive(activeBlock.id, checkId)}
          onUpdateCheck={updateCheck}
          onBack={() => backToRoute(activeRoute.id)}
        />
      )}
    </div>
  );
}
