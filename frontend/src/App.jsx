import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import TopBar from "./components/TopBar.jsx";
import HomeView from "./views/HomeView.jsx";
import CreateView from "./views/CreateView.jsx";
import SimulateView from "./views/SimulateView.jsx";
import AnalyzeView from "./views/AnalyzeView.jsx";
import ProduceView from "./views/ProduceView.jsx";
import DecideView from "./views/DecideView.jsx";
import ControlView from "./views/ControlView.jsx";
import { api, useMissionControlSocket } from "./lib/api.js";

export default function App() {
  const [active, setActive] = useState("home");
  const [anchor, setAnchor] = useState(null);
  const [projectId, setProjectId] = useState("thriller-01");
  const [mockMode, setMockMode] = useState(undefined);
  const [backendError, setBackendError] = useState(false);
  const [lastDna, setLastDna] = useState(null);

  // One shared Mission Control connection for the whole app.
  const { events, connected } = useMissionControlSocket(80);

  useEffect(() => {
    api.health()
      .then((h) => setMockMode(h.mock_mode))
      .catch(() => setBackendError(true));
  }, []);

  function navigate(view, anchorId) {
    setActive(view);
    setAnchor(anchorId || null);
  }

  const views = {
    home: <HomeView projectId={projectId} onNavigate={navigate} onChangeProject={setProjectId} events={events} lastDna={lastDna} />,
    create: <CreateView projectId={projectId} onDnaExtracted={setLastDna} anchor={anchor} />,
    simulate: <SimulateView projectId={projectId} />,
    analyze: <AnalyzeView projectId={projectId} anchor={anchor} />,
    produce: <ProduceView projectId={projectId} />,
    decide: <DecideView projectId={projectId} />,
    control: <ControlView projectId={projectId} events={events} connected={connected} />,
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar active={active} activeAnchor={anchor} onSelect={navigate} />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar projectId={projectId} onChangeProject={setProjectId} onNavigate={navigate} events={events} mockMode={mockMode} />
        <main className="flex-1 overflow-auto p-6 scrollbar-thin">
          {backendError && (
            <div className="mb-4 text-xs text-redteam border border-redteam/30 rounded-md px-3 py-2 bg-redteam/10">
              Can't reach the backend at {import.meta.env.VITE_API_URL || "http://localhost:8000"} — make sure `uvicorn app.main:app` is running.
            </div>
          )}
          {views[active]}
        </main>
      </div>
    </div>
  );
}
