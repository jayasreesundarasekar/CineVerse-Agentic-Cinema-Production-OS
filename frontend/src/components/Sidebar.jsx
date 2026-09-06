import React from "react";
import { Home, Sparkles } from "lucide-react";
import Logo from "./Logo.jsx";
import { NAV_GROUPS } from "../lib/nav.js";

export default function Sidebar({ active, activeAnchor, onSelect }) {
  return (
    <nav className="w-64 shrink-0 bg-rail border-r border-hair flex flex-col">
      <div className="sprocket-rail h-6" />
      <div className="px-5 py-5 flex items-center gap-3">
        <Logo size={34} />
        <div>
          <p className="font-display text-xl tracking-wide text-parchment leading-none">CINEVERSE</p>
          <p className="text-[11px] text-muted mt-1">Agentic Cinema OS</p>
        </div>
      </div>

      <div className="px-3 mb-2">
        <NavButton
          icon={Home}
          label="Mission Control"
          sub="Your cinematic universe"
          active={active === "home"}
          onClick={() => onSelect("home", null)}
        />
      </div>

      <div className="flex-1 overflow-auto scrollbar-thin px-3 space-y-4 pb-4">
        {NAV_GROUPS.map((g) => (
          <div key={g.group}>
            <p className="flex items-center gap-1.5 text-[11px] tracking-wider text-muted px-2 mb-1">
              <g.icon size={12} /> {g.group}
            </p>
            <div className="space-y-0.5">
              {g.items.map((item) => (
                <NavButton
                  key={item.label}
                  label={item.label}
                  sub={item.sub}
                  comingSoon={item.comingSoon}
                  active={active === item.view && (!item.anchor || activeAnchor === item.anchor)}
                  onClick={() => onSelect(item.view, item.anchor)}
                  indent
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-hair">
        <button
          onClick={() => onSelect("home", null)}
          className="w-full flex items-center gap-2.5 rounded-lg border border-violet/30 bg-cine-gradient-soft px-3 py-2.5 hover:border-violet/60 transition-colors"
        >
          <span className="w-8 h-8 rounded-full bg-cine-gradient flex items-center justify-center text-void shrink-0">
            <Sparkles size={14} />
          </span>
          <span className="text-left">
            <span className="block text-sm text-parchment leading-tight">Lumia</span>
            <span className="block text-[11px] text-muted leading-tight">Your AI Co-Director</span>
          </span>
        </button>
      </div>
    </nav>
  );
}

function NavButton({ icon: Icon, label, sub, active, onClick, indent, comingSoon }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-md flex items-start gap-2.5 transition-colors ${indent ? "px-3 py-2" : "px-3 py-2.5"} ${
        active ? "bg-surface2 text-parchment" : "text-muted hover:text-parchment hover:bg-surface/60"
      }`}
    >
      {Icon && <Icon size={17} className={`mt-0.5 shrink-0 ${active ? "text-violet" : ""}`} />}
      <span className="min-w-0">
        <span className="flex items-center gap-1.5 text-sm font-medium truncate">
          {label}
          {comingSoon && <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-hair text-muted shrink-0">soon</span>}
        </span>
        <span className="block text-[11px] text-muted/80 truncate">{sub}</span>
      </span>
    </button>
  );
}
