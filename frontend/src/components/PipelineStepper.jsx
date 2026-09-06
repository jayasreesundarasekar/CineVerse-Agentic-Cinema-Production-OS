/**
 * The Cineverse pipeline, in order — a real sequence (script to
 * greenlight), so numbered circles-on-a-line are structurally honest
 * here, not decorative.
 */
import React from "react";
import { FileText, Palette, Image, Clapperboard, Sparkles, Gavel } from "lucide-react";

const STEPS = [
  { view: "create", anchor: "screenplay", label: "Screenplay", sub: "Structure & flow", icon: FileText, tone: "#4CC9F0" },
  { view: "create", anchor: "visual-universe", label: "Cinematic DNA", sub: "Style & mood", icon: Palette, tone: "#7C5CFC" },
  { view: "create", anchor: "visual-universe", label: "Visuals", sub: "World & characters", icon: Image, tone: "#7C5CFC" },
  { view: "create", anchor: "shot-designer", label: "Shots", sub: "Scene planning", icon: Clapperboard, tone: "#E94BB0" },
  { view: "simulate", anchor: null, label: "Simulation", sub: "Explore & outcode", icon: Sparkles, tone: "#2E9E97" },
  { view: "decide", anchor: null, label: "Greenlight", sub: "Bring it to life", icon: Gavel, tone: "#C9A227" },
];

export default function PipelineStepper({ onSelect }) {
  return (
    <div className="relative overflow-x-auto scrollbar-thin py-1">
      <div className="flex items-center min-w-max">
        {STEPS.map((step, i) => {
          const Icon = step.icon;
          return (
            <React.Fragment key={step.label}>
              <button
                onClick={() => onSelect(step.view, step.anchor)}
                className="flex items-center gap-2.5 px-2 py-2 rounded-md hover:bg-surface2 transition-colors shrink-0"
              >
                <span
                  className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
                  style={{ background: `${step.tone}22`, border: `1.5px solid ${step.tone}66`, color: step.tone }}
                >
                  <Icon size={14} />
                </span>
                <span className="text-left">
                  <span className="block text-xs text-parchment leading-tight">{i + 1}. {step.label}</span>
                  <span className="block text-[10px] text-muted leading-tight">{step.sub}</span>
                </span>
              </button>
              {i < STEPS.length - 1 && <span className="w-6 h-px bg-hair shrink-0" />}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
