import { useState } from "react";
import { Navbar } from "./components/Navbar";
import { LoanQueue } from "./components/LoanQueue";
import { LoanDetail } from "./components/LoanDetail";
import { ImportAndSignView } from "./components/ImportAndSignView";
import { RoutesFlow } from "./components/RoutesFlow";
import { MOCK_LOANS } from "./data/mockData";
import { DataSourceProvider } from "./lib/dataSourceContext";
import type { ViewId, LoanDetailTab } from "./lib/nav";

function App() {
  const [activeView, setActiveView] = useState<ViewId>("queue");
  const [selectedLoanId, setSelectedLoanId] = useState<string>(MOCK_LOANS[0].loanId);
  const [loanDetailTab, setLoanDetailTab] = useState<LoanDetailTab>("apply");

  const openLoan = (loanId: string, tab: LoanDetailTab = "apply") => {
    setSelectedLoanId(loanId);
    setLoanDetailTab(tab);
    setActiveView("loan-detail");
  };

  return (
    <DataSourceProvider>
      <div className="min-h-screen bg-[var(--color-canvas)]">
        <Navbar activeView={activeView} onSelectView={setActiveView} />
        <main className="mx-auto max-w-[1400px] px-4 pb-16 pt-6">
          {activeView === "queue" && <LoanQueue onOpenLoan={openLoan} />}
          {activeView === "loan-detail" && (
            <LoanDetail loanId={selectedLoanId} initialTab={loanDetailTab} onBack={() => setActiveView("queue")} />
          )}
          {activeView === "author-import" && <ImportAndSignView />}
          {activeView === "routes" && <RoutesFlow />}
        </main>
      </div>
    </DataSourceProvider>
  );
}

export default App;
