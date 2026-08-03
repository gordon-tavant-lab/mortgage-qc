// applicationStore.ts — 021-touchless-audit-run: minimal in-memory cache of applications
// pulled this session. The audit route (routes/audit.ts) needs to read "the already-pulled
// application payload" (contracts/audit-run.md) without calling Touchless again and without
// a request body carrying it — applications.ts's pull route was the only place that ever saw
// the payload, so it now also saves it here, keyed by applicationId. Server-process-lifetime
// only (matches this feature's scope — no persisted audit-trail storage, research.md Item 6);
// cleared on process restart, same as every other piece of this demo's fetched state.

export function saveApplication(applicationId: string, application: unknown): void {
  store.set(applicationId, application);
}

export function getApplication(applicationId: string): unknown | undefined {
  return store.get(applicationId);
}

export function clearApplication(applicationId: string): void {
  store.delete(applicationId);
}

const store = new Map<string, unknown>();
