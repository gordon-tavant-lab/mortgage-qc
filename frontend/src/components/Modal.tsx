import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";

// spec024 T001: shared scrim+centered-panel component, extracted from the markup
// already duplicated in ExceptionReview.tsx's citation modal and
// RetrievedDocumentViewer.tsx -- a consolidation, not a new visual language. Escape
// and scrim-click both call onClose; the inner panel stops propagation so a click
// inside the dialog never bubbles up to the scrim's close handler.
interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
}

export function Modal({ open, onClose, title, children }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-slate-200 bg-white p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="mb-4 flex items-center justify-between border-b border-slate-100 pb-3">
          {title ? <h3 className="text-sm font-bold text-slate-900">{title}</h3> : <span />}
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-50 hover:text-slate-600"
            title="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
