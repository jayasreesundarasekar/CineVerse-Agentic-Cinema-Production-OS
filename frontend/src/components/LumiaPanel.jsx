/**
 * Lumia — the AI Co-Director. Quick actions call real specialized
 * agents directly; the chat input calls the conversational Lumia
 * agent. Nothing here is scripted copy — every reply comes from a
 * live POST to the FastAPI backend.
 */
import React, { useState } from "react";
import { Sparkles, Send } from "lucide-react";
import { api } from "../lib/api.js";
import { Spinner } from "./ui.jsx";

const QUICK_ACTIONS = [
  { label: "Summarize my screenplay", prompt: "Summarize the current screenplay and its structural strengths." },
  { label: "Suggest shot ideas", prompt: "Suggest a few striking shot ideas for the current scene." },
  { label: "Analyze my story", prompt: "What should I look at first when analyzing this story's structure?" },
  { label: "Help with production planning", prompt: "Where should I start with production planning and budget?" },
];

export default function LumiaPanel({ projectId, onExploreVisuals }) {
  const [messages, setMessages] = useState([
    { role: "lumia", content: "Hey — I'm Lumia, your AI co-director. Ask me anything about this project, or try a quick action below.", cta: "visuals" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(text) {
    const message = text || input;
    if (!message.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setLoading(true);
    try {
      const history = messages.slice(-6).map((m) => ({ role: m.role === "lumia" ? "assistant" : "user", content: m.content }));
      const res = await api.lumiaChat({ project_id: projectId, message, history });
      setMessages((prev) => [...prev, { role: "lumia", content: res.reply }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "lumia", content: `I hit an error reaching the backend: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-surface border border-hair rounded-lg flex flex-col h-full">
      <div className="px-4 py-3.5 border-b border-hair flex items-center gap-3">
        <span className="w-9 h-9 rounded-full bg-cine-gradient flex items-center justify-center text-void">
          <Sparkles size={16} />
        </span>
        <div>
          <p className="text-sm font-medium text-parchment flex items-center gap-1.5">
            Lumia <span className="w-1.5 h-1.5 rounded-full bg-teal inline-block" />
          </p>
          <p className="text-[11px] text-muted">Production intelligence, online</p>
        </div>
      </div>

      <div className="flex-1 overflow-auto scrollbar-thin px-4 py-3 space-y-3 max-h-72">
        {messages.map((m, i) => (
          <div key={i} className={`text-sm ${m.role === "user" ? "text-parchment/80 pl-4" : "text-parchment"}`}>
            {m.content}
            {m.cta === "visuals" && onExploreVisuals && (
              <button
                onClick={onExploreVisuals}
                className="mt-2 block text-xs font-medium bg-cine-gradient text-void rounded-full px-3 py-1.5 hover:opacity-90 transition-opacity"
              >
                Explore visuals
              </button>
            )}
          </div>
        ))}
        {loading && <Spinner className="text-muted" />}
      </div>

      <div className="px-4 pb-3 flex flex-wrap gap-1.5">
        {QUICK_ACTIONS.map((qa) => (
          <button
            key={qa.label}
            onClick={() => send(qa.prompt)}
            disabled={loading}
            className="text-[11px] px-2.5 py-1 rounded-full border border-hair text-muted hover:text-parchment hover:border-violet/50 transition-colors disabled:opacity-40"
          >
            {qa.label}
          </button>
        ))}
      </div>

      <form
        className="p-3 border-t border-hair flex gap-2"
        onSubmit={(e) => { e.preventDefault(); send(); }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Lumia anything..."
          className="flex-1 bg-void border border-hair rounded-md px-3 py-2 text-sm text-parchment placeholder:text-muted/60 focus:border-violet"
        />
        <button type="submit" disabled={loading} className="w-9 h-9 rounded-md bg-cine-gradient text-void flex items-center justify-center disabled:opacity-50">
          <Send size={14} />
        </button>
      </form>
    </div>
  );
}
