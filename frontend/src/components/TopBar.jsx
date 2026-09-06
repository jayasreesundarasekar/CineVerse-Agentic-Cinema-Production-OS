import React, { useEffect, useMemo, useRef, useState } from "react";
import { Search, Bell, FolderOpen, Sparkles } from "lucide-react";
import { FLAT_NAV } from "../lib/nav.js";
import ActivityFeed from "./ActivityFeed.jsx";

export default function TopBar({ projectId, onChangeProject, onNavigate, events, mockMode }) {
  const [query, setQuery] = useState("");
  const [showResults, setShowResults] = useState(false);
  const [showBell, setShowBell] = useState(false);
  const [editingProject, setEditingProject] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    function handleKey(e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape") setShowResults(false);
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  const results = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();
    return FLAT_NAV.filter((item) => item.label.toLowerCase().includes(q) || item.group.toLowerCase().includes(q)).slice(0, 6);
  }, [query]);

  function go(item) {
    onNavigate(item.view, item.anchor);
    setQuery("");
    setShowResults(false);
  }

  return (
    <header className="h-16 shrink-0 border-b border-hair flex items-center gap-4 px-6 bg-void/60 relative z-20">
      <div className="relative flex-1 max-w-md">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => { setQuery(e.target.value); setShowResults(true); }}
          onFocus={() => setShowResults(true)}
          onBlur={() => setTimeout(() => setShowResults(false), 150)}
          onKeyDown={(e) => { if (e.key === "Enter" && results[0]) go(results[0]); }}
          placeholder="Search projects, ideas, or anything..."
          className="w-full bg-surface border border-hair rounded-lg pl-9 pr-14 py-2 text-sm text-parchment placeholder:text-muted/60 focus:border-violet transition-colors"
        />
        <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-muted border border-hair rounded px-1.5 py-0.5">⌘K</kbd>

        {showResults && results.length > 0 && (
          <div className="absolute mt-1.5 w-full bg-surface border border-hair rounded-lg shadow-xl overflow-hidden">
            {results.map((item) => (
              <button
                key={item.label}
                onMouseDown={() => go(item)}
                className="w-full text-left px-3.5 py-2.5 hover:bg-surface2 transition-colors flex items-center justify-between"
              >
                <span className="text-sm text-parchment">{item.label}</span>
                <span className="text-[11px] text-muted">{item.group}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex-1" />

      {mockMode !== undefined && (
        <span className="flex items-center gap-1.5 text-[11px] text-muted">
          <span className={`w-1.5 h-1.5 rounded-full ${mockMode ? "bg-brass" : "bg-teal"}`} />
          {mockMode ? "mock mode" : "live APIs"}
        </span>
      )}

      <div className="relative">
        {editingProject ? (
          <input
            autoFocus
            defaultValue={projectId}
            onBlur={(e) => { onChangeProject(e.target.value || "default"); setEditingProject(false); }}
            onKeyDown={(e) => { if (e.key === "Enter") e.target.blur(); }}
            className="bg-surface border border-violet/50 rounded-md px-3 py-1.5 text-sm text-parchment w-40"
          />
        ) : (
          <button
            onClick={() => setEditingProject(true)}
            className="flex items-center gap-1.5 text-xs text-muted hover:text-parchment border border-hair rounded-md px-3 py-1.5 transition-colors"
          >
            <FolderOpen size={13} /> {projectId}
          </button>
        )}
      </div>

      <div className="relative">
        <button
          onClick={() => setShowBell((v) => !v)}
          className="w-9 h-9 rounded-full border border-hair flex items-center justify-center text-muted hover:text-parchment hover:border-violet/50 transition-colors relative"
        >
          <Bell size={16} />
          {events.length > 0 && <span className="absolute top-1.5 right-2 w-1.5 h-1.5 rounded-full bg-magenta" />}
        </button>
        {showBell && (
          <div className="absolute right-0 mt-2 w-80 bg-surface border border-hair rounded-lg shadow-xl p-3 z-30">
            <p className="text-xs text-muted mb-2">Recent activity</p>
            <ActivityFeed events={events} compact />
          </div>
        )}
      </div>

      <div className="w-9 h-9 rounded-full bg-cine-gradient flex items-center justify-center text-void shrink-0" title="Filmmaker">
        <Sparkles size={15} />
      </div>
    </header>
  );
}
