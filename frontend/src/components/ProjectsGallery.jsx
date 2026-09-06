import React from "react";
import { MoreVertical } from "lucide-react";
import { relativeTime } from "../lib/projects.js";
import { EmptyState } from "./ui.jsx";

const TONE_CYCLE = [
  "radial-gradient(circle at 30% 30%, rgba(124,92,252,0.5), transparent 60%), #171b3a",
  "radial-gradient(circle at 70% 30%, rgba(76,201,240,0.5), transparent 60%), #12203a",
  "radial-gradient(circle at 40% 70%, rgba(233,75,176,0.5), transparent 60%), #221530",
  "radial-gradient(circle at 60% 40%, rgba(201,162,39,0.45), transparent 60%), #241d12",
];

export default function ProjectsGallery({ projects, onOpen }) {
  if (!projects.length) {
    return <EmptyState title="No recent projects" hint="Set a project ID in the top bar to start one." />;
  }
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {projects.slice(0, 8).map((p, i) => (
        <div
          key={p.id}
          onClick={() => onOpen(p.id)}
          className="cursor-pointer bg-surface border border-hair rounded-lg overflow-hidden hover:border-violet/50 transition-colors"
        >
          <div className="h-20 relative" style={{ background: TONE_CYCLE[i % TONE_CYCLE.length] }} />
          <div className="p-3">
            <div className="flex items-start justify-between gap-1">
              <p className="text-sm text-parchment truncate">{p.title || p.id}</p>
              <MoreVertical size={13} className="text-muted shrink-0 mt-0.5" />
            </div>
            {p.tags?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1">
                {p.tags.map((t) => (
                  <span key={t} className="text-[10px] text-muted border border-hair rounded-full px-1.5 py-0.5">{t}</span>
                ))}
              </div>
            )}
            <p className="text-[11px] text-muted mt-1.5">Last edited {relativeTime(p.lastOpened)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
