import { ArrowLeftCircle, ArrowRightCircle } from "lucide-react";
import type { Block } from "../lib/types";

// spec024 US1 (T003): renders inside <Modal> (RouteDetail.tsx). Wraps the ALREADY
// working activation logic (RoutesFlow.tsx's toggleBlockActive, passed down as
// onToggleBlock) with an explicit confirm step -- this component adds no new
// activation logic of its own (FR-001 already worked as a one-click list-row button;
// this is FR-002's popup-modal presentation of that same action).
interface BlockMembershipModalProps {
  block: Block;
  isActive: boolean;
  usedElsewhere: number;
  onConfirm: () => void;
}

export function BlockMembershipModal({ block, isActive, usedElsewhere, onConfirm }: BlockMembershipModalProps) {
  return (
    <div className="space-y-4">
      <div>
        <div className="text-sm font-bold text-slate-900">{block.name}</div>
        <p className="mt-1 text-xs leading-relaxed text-slate-500">{block.description}</p>
        {usedElsewhere > 0 && (
          <span className="mt-2 inline-block rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-semibold text-blue-600">
            also active in {usedElsewhere} other route{usedElsewhere > 1 ? "s" : ""}
          </span>
        )}
      </div>
      <div className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-xs text-slate-500">
        {isActive
          ? `${block.checkIds.length} check${block.checkIds.length === 1 ? "" : "s"} in this block will stop contributing to this route's audit once deactivated.`
          : `${block.checkIds.length} check${block.checkIds.length === 1 ? "" : "s"} in this block will start contributing to this route's audit once activated.`}
      </div>
      <button
        onClick={onConfirm}
        className={`flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-xs font-semibold shadow-sm transition ${
          isActive
            ? "border border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100"
            : "bg-blue-600 text-white hover:bg-blue-700"
        }`}
      >
        {isActive ? (
          <>
            <ArrowLeftCircle className="h-4 w-4" />
            Deactivate on this route
          </>
        ) : (
          <>
            <ArrowRightCircle className="h-4 w-4" />
            Activate on this route
          </>
        )}
      </button>
    </div>
  );
}
