import type { Route, Block, Check } from "./types";

// Spec019 Phase 5 (storage/save/restore). This module is pure client-side --
// it has zero filesystem access, which is what actually enforces the
// gold-isolation guard (FR-013): a browser can write to localStorage, never
// to storage/rules/gold/ or anywhere else on disk. There is nothing here that
// *could* touch gold even by accident -- the isolation is structural, not a
// runtime check.

const STORAGE_KEY = "mortgage-qc-ruleset-draft-v1";

export interface RulesetDraftContent {
  routes: Route[];
  blocks: Block[];
  checks: Check[];
}

export interface RulesetDraft {
  content: RulesetDraftContent;
  sha256: string;
  provenance: { source: "goldCatalog.json"; savedAt: string };
  intent_records: [];
  signoff_summary: { signedBy: string; signedAt: string } | null;
}

export class QuotaExceededError extends Error {
  constructor() {
    super("localStorage quota exceeded -- this draft could not be saved.");
    this.name = "QuotaExceededError";
  }
}

// Real digest (SHA-256 via the Web Crypto API) -- replaces the mockup's
// fakeHash(). Async because SubtleCrypto is async; every caller already
// awaits this.
export async function computeDigest(content: RulesetDraftContent): Promise<string> {
  const bytes = new TextEncoder().encode(JSON.stringify(content));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export async function saveDraft(
  content: RulesetDraftContent,
  signoff: { signedBy: string; signedAt: string } | null
): Promise<RulesetDraft> {
  const sha256 = await computeDigest(content);
  const draft: RulesetDraft = {
    content,
    sha256,
    provenance: { source: "goldCatalog.json", savedAt: new Date().toISOString() },
    intent_records: [],
    signoff_summary: signoff,
  };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
  } catch (err) {
    if (err instanceof DOMException && (err.name === "QuotaExceededError" || err.code === 22)) {
      throw new QuotaExceededError();
    }
    throw err;
  }
  return draft;
}

export function loadDraft(): RulesetDraft | null {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as RulesetDraft;
  } catch {
    // Corrupt draft -- treat as absent rather than throwing on load.
    return null;
  }
}

export function clearDraft(): void {
  localStorage.removeItem(STORAGE_KEY);
}

// Reconciliation (FR-013 / T025): a saved draft's checks may no longer exist
// in the current catalog (e.g. goldCatalog.json was regenerated). Report
// what's missing rather than silently dropping it or crashing.
export function reconcileDraft(
  draft: RulesetDraftContent,
  currentChecks: Check[]
): { content: RulesetDraftContent; missingCheckIds: string[] } {
  const currentIds = new Set(currentChecks.map((c) => c.id));
  const missingCheckIds = new Set<string>();

  const blocks = draft.blocks.map((b) => {
    const validCheckIds = b.checkIds.filter((id) => {
      const ok = currentIds.has(id);
      if (!ok) missingCheckIds.add(id);
      return ok;
    });
    return { ...b, checkIds: validCheckIds };
  });
  const checks = draft.checks.filter((c) => currentIds.has(c.id));

  return {
    content: { routes: draft.routes, blocks, checks },
    missingCheckIds: Array.from(missingCheckIds),
  };
}
