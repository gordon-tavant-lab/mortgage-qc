import { useState } from "react";
import { MOCK_ROUTES, MOCK_BLOCKS, MOCK_CHECKS, MOCK_SIGNED_RULESET } from "../data/mockData";
import { SampleDataBanner } from "./SampleDataBanner";
import { SignAndPinBar } from "./SignAndPinBar";
import { RouteList } from "./RouteList";
import { RouteDetail } from "./RouteDetail";
import { BlockDetail } from "./BlockDetail";
import type { Route, Block, Check } from "../lib/types";

type Level = { level: "list" } | { level: "route"; routeId: string } | { level: "block"; routeId: string; blockId: string };

let routeCounter = 0;
let signCounter = 0;

function fakeHash(seed: number): string {
  // Not a real digest -- just a distinct-looking hex string per sign, so the
  // mockup visibly changes on each Sign & Pin without depending on
  // Math.random()/Date.now() for anything that matters.
  const base = (seed * 2654435761) % 0xffffffff;
  return base.toString(16).padStart(8, "0").repeat(8).slice(0, 64);
}

export function RoutesFlow() {
  const [routes, setRoutes] = useState<Route[]>(() => structuredClone(MOCK_ROUTES));
  const [blocks, setBlocks] = useState<Block[]>(() => structuredClone(MOCK_BLOCKS));
  const [checks, setChecks] = useState<Check[]>(() => structuredClone(MOCK_CHECKS));
  const [dirtyCount, setDirtyCount] = useState(0);
  const [justSigned, setJustSigned] = useState(false);
  const [lastSigned, setLastSigned] = useState({
    sha256: MOCK_SIGNED_RULESET.sha256,
    signedAt: MOCK_SIGNED_RULESET.signedAt,
    signedBy: MOCK_SIGNED_RULESET.signedBy,
  });
  const [nav, setNav] = useState<Level>({ level: "list" });

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

  const signAndPin = () => {
    signCounter += 1;
    setLastSigned({
      sha256: fakeHash(signCounter),
      signedAt: new Date().toISOString(),
      signedBy: MOCK_SIGNED_RULESET.signedBy,
    });
    setDirtyCount(0);
    setJustSigned(true);
  };

  const openRoute = (routeId: string) => setNav({ level: "route", routeId });
  const openBlock = (routeId: string, blockId: string) => setNav({ level: "block", routeId, blockId });
  const backToList = () => setNav({ level: "list" });
  const backToRoute = (routeId: string) => setNav({ level: "route", routeId });

  const activeRoute = nav.level !== "list" ? routes.find((r) => r.id === nav.routeId) : undefined;
  const activeBlock = nav.level === "block" ? blocks.find((b) => b.id === nav.blockId) : undefined;

  return (
    <div className="space-y-6 pb-12">
      <SampleDataBanner />

      <div>
        <h2 className="font-display text-xl font-bold text-slate-900">Author — Routes</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          Catalog-constrained controls only — pick, wire, and edit from a pool of existing routes,
          blocks, and checks. This surface owns the criteria gate so free text never does (Tension
          8). No AI drafting in this view, by decision.
        </p>
      </div>

      <SignAndPinBar dirtyCount={dirtyCount} lastSigned={lastSigned} justSigned={justSigned} onSign={signAndPin} />

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
