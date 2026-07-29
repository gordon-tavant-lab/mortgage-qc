import { useState } from "react";
import { Navbar } from "./components/Navbar";
import { LoanQueue } from "./components/LoanQueue";
import { InspectSources } from "./components/InspectSources";
import { ApplyView } from "./components/ApplyView";
import { ImportAndSignView } from "./components/ImportAndSignView";
import { GuidedEditorView } from "./components/GuidedEditorView";
import { ExceptionReview } from "./components/ExceptionReview";
import { MOCK_FINDINGS } from "./data/mockData";
import type { ViewId } from "./lib/nav";

function App() {
  const [activeView, setActiveView] = useState<ViewId>("queue");
  const exceptionCount = MOCK_FINDINGS.filter((f) => f.mitigation === "UNRESOLVED").length;

  return (
    <div className="min-h-screen bg-[var(--color-canvas)]">
      <Navbar activeView={activeView} onSelectView={setActiveView} exceptionCount={exceptionCount} />
      <main className="mx-auto max-w-[1400px] px-4 pb-16 pt-6">
        {activeView === "queue" && <LoanQueue onOpenLoan={setActiveView} />}
        {activeView === "inspect" && <InspectSources />}
        {activeView === "apply" && <ApplyView />}
        {activeView === "author-import" && <ImportAndSignView />}
        {activeView === "author-guided" && <GuidedEditorView />}
        {activeView === "review" && <ExceptionReview />}
      </main>
    </div>
  );
}

export default App;
