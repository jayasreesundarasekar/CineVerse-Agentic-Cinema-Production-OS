import React from "react";
import { EmptyState } from "./ui.jsx";

/** Shows the last extracted Visual DNA for this session. Real data lifted
 * from the Create module's last extraction call — no placeholder values. */
export default function CinematicDnaCard({ dna }) {
  if (!dna) {
    return <EmptyState title="No Cinematic DNA yet" hint="Extract it from the Create tab to see it here." />;
  }
  const rows = Object.entries(dna).filter(([k]) => k !== "suggested_prompt");
  return (
    <div className="space-y-2">
      {rows.map(([key, value]) => (
        <div key={key} className="flex justify-between text-sm border-b border-hair/60 pb-1.5 last:border-0">
          <span className="text-muted capitalize">{key.replace(/_/g, " ")}</span>
          <span className="text-parchment text-right max-w-[60%] truncate" title={Array.isArray(value) ? value.join(", ") : String(value)}>
            {Array.isArray(value) ? value.slice(0, 2).join(", ") : String(value)}
          </span>
        </div>
      ))}
    </div>
  );
}
