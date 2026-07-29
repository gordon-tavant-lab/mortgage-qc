import { ShieldCheck, CheckCircle2 } from "lucide-react";

interface SignedInfo {
  sha256: string;
  signedAt: string;
  signedBy: string;
}

interface SignAndPinBarProps {
  dirtyCount: number;
  lastSigned: SignedInfo;
  justSigned: boolean;
  onSign: () => void;
}

// Persistent across all three Route/Block/Check screens by design: edits at
// any level accumulate into ONE shared draft rather than three independent
// sign-off ceremonies -- per the constitution's own warning that busywork
// signing (Principle II's "sign-off theater") dilutes the signal.
export function SignAndPinBar({ dirtyCount, lastSigned, justSigned, onSign }: SignAndPinBarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-[var(--shadow-panel)]">
      <div className="flex items-center gap-3 text-xs">
        {dirtyCount > 0 ? (
          <span className="flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
            {dirtyCount} unsaved change{dirtyCount > 1 ? "s" : ""}
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-slate-500">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
            Up to date — signed by {lastSigned.signedBy}
          </span>
        )}
        <span className="hidden font-mono text-[10px] text-slate-400 sm:inline">
          {lastSigned.sha256.slice(0, 12)}...
        </span>
      </div>

      {justSigned ? (
        <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
          <CheckCircle2 className="h-4 w-4" />
          Signed &amp; pinned
        </span>
      ) : (
        <button
          onClick={onSign}
          disabled={dirtyCount === 0}
          className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ShieldCheck className="h-4 w-4" />
          Sign &amp; Pin Version
        </button>
      )}
    </div>
  );
}
