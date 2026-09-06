import React from "react";
import { Badge, EmptyState } from "./ui.jsx";

/** Shared Mission Control feed renderer — used on Home (compact) and
 * the Control view (full). Renders real WebSocket events, nothing staged. */
export default function ActivityFeed({ events, compact = false }) {
  if (!events.length) {
    return <EmptyState title="No activity yet" hint="Trigger any agent — it streams here live." />;
  }
  const shown = compact ? events.slice(0, 6) : events;
  return (
    <div className={`space-y-1.5 ${compact ? "" : "max-h-[36rem] overflow-auto scrollbar-thin"} font-mono text-xs`}>
      {shown.map((e, i) => (
        <div key={i} className="flex items-start gap-3 border-b border-hair/60 pb-1.5">
          <span className="text-muted shrink-0">{new Date(e.receivedAt).toLocaleTimeString()}</span>
          <Badge tone={e.type === "agent_completed" ? "teal" : e.type === "agent_started" ? "brass" : "muted"}>
            {e.type}
          </Badge>
          <span className="text-parchment">{e.payload?.agent}</span>
          {!compact && <span className="text-muted truncate">{e.payload?.task}</span>}
        </div>
      ))}
    </div>
  );
}
