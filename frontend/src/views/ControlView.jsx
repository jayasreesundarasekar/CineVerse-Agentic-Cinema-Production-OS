import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";
import { Panel } from "../components/ui.jsx";
import ActivityFeed from "../components/ActivityFeed.jsx";

/** Receives the shared Mission Control socket state from App.jsx rather
 * than opening its own connection — one live socket for the whole app. */
export default function ControlView({ projectId, events, connected }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    api.backendStatus().then(setStatus).catch(() => setStatus(null));
  }, []);

  const filtered = events.filter((e) => !projectId || e.payload?.project_id === projectId || !e.payload?.project_id);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
      <Panel eyebrow="Mission Control" title="Backend status" className="xl:col-span-1">
        <Row label="WebSocket" value={connected ? "connected" : "reconnecting…"} tone={connected ? "teal" : "red"} />
        <Row
          label="ClickHouse"
          value={status?.clickhouse_connected ? "connected" : "in-memory (mock)"}
          tone={status?.clickhouse_connected ? "teal" : "brass"}
        />
      </Panel>

      <Panel eyebrow="Live agent activity" title="Real-time feed" className="xl:col-span-2">
        <ActivityFeed events={filtered} />
      </Panel>
    </div>
  );
}

function Row({ label, value, tone }) {
  const dot = { teal: "bg-teal", red: "bg-redteam", brass: "bg-brass" }[tone] || "bg-muted";
  return (
    <div className="flex items-center justify-between py-2 border-b border-hair last:border-0">
      <span className="text-sm text-muted">{label}</span>
      <span className="flex items-center gap-2 text-sm">
        <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
        {value}
      </span>
    </div>
  );
}
