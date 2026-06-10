import { useState } from "react";
import { GenerationsPage } from "./pages/GenerationsPage";
import { MachinePage } from "./pages/MachinePage";
import { ProfilesPage } from "./pages/ProfilesPage";
import { RunPage } from "./pages/RunPage";

type Page = "profiles" | "run" | "generations" | "machine";

const TABS: { id: Page; label: string }[] = [
  { id: "profiles", label: "Profiles" },
  { id: "run", label: "Run" },
  { id: "generations", label: "Generations" },
  { id: "machine", label: "Machine" },
];

export default function App() {
  const [page, setPage] = useState<Page>("profiles");
  const [generationId, setGenerationId] = useState<number | null>(null);

  const openGeneration = (id: number) => {
    setGenerationId(id);
    setPage("generations");
  };

  return (
    <div className="app">
      <div className="topbar">
        <h1>sheetcut</h1>
        <nav>
          {TABS.map((t) => (
            <button
              key={t.id}
              className={page === t.id ? "active" : ""}
              onClick={() => setPage(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>
      {page === "profiles" && <ProfilesPage />}
      {page === "run" && <RunPage onOpenGeneration={openGeneration} />}
      {page === "generations" && (
        <GenerationsPage selectedId={generationId} onSelect={setGenerationId} />
      )}
      {page === "machine" && <MachinePage />}
    </div>
  );
}
