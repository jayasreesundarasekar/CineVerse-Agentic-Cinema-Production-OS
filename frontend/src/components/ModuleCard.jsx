import React from "react";
import { ArrowRight } from "lucide-react";

const TONE_GRADIENTS = {
  violet: "radial-gradient(circle at 30% 20%, rgba(124,92,252,0.55), transparent 60%), radial-gradient(circle at 80% 80%, rgba(76,201,240,0.35), transparent 55%), #171b3a",
  sky: "radial-gradient(circle at 70% 20%, rgba(76,201,240,0.5), transparent 60%), radial-gradient(circle at 20% 85%, rgba(124,92,252,0.35), transparent 55%), #12203a",
  magenta: "radial-gradient(circle at 25% 25%, rgba(233,75,176,0.5), transparent 60%), radial-gradient(circle at 80% 75%, rgba(124,92,252,0.3), transparent 55%), #221530",
  brass: "radial-gradient(circle at 30% 25%, rgba(201,162,39,0.45), transparent 60%), radial-gradient(circle at 80% 80%, rgba(233,75,176,0.25), transparent 55%), #241d12",
  teal: "radial-gradient(circle at 30% 20%, rgba(46,158,151,0.5), transparent 60%), radial-gradient(circle at 80% 80%, rgba(76,201,240,0.3), transparent 55%), #12211f",
  red: "radial-gradient(circle at 70% 25%, rgba(193,68,60,0.5), transparent 60%), radial-gradient(circle at 20% 80%, rgba(233,75,176,0.25), transparent 55%), #221414",
};

export default function ModuleCard({ icon: Icon, title, tag, description, tone = "violet", onClick }) {
  return (
    <button
      onClick={onClick}
      className="text-left bg-surface border border-hair rounded-lg overflow-hidden hover:border-violet/50 transition-colors group flex flex-col"
    >
      <div className="h-28 relative flex items-end p-3" style={{ background: TONE_GRADIENTS[tone] }}>
        <span className="flex items-center gap-1.5 text-xs font-semibold tracking-wide text-parchment bg-void/40 backdrop-blur-sm rounded-full px-2.5 py-1">
          <Icon size={13} /> {tag}
        </span>
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <p className="text-sm text-parchment mb-1 leading-snug">{title}</p>
        <p className="text-xs text-muted mb-3 leading-snug flex-1">{description}</p>
        <span className="inline-flex items-center gap-1.5 text-xs text-muted group-hover:text-parchment transition-colors self-end">
          <ArrowRight size={13} className="group-hover:translate-x-0.5 transition-transform" />
        </span>
      </div>
    </button>
  );
}
