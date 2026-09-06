/**
 * Thin fetch wrapper for the Cineverse FastAPI backend, plus a small
 * WebSocket hook for the /ws/mission-control live feed.
 */
import { useEffect, useRef, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/mission-control";

async function request(path, { method = "GET", body, params } = {}) {
  let url = `${API_URL}${path}`;
  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
    ).toString();
    if (qs) url += `?${qs}`;
  }
  const res = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${method} ${path} failed (${res.status}): ${text.slice(0, 300)}`);
  }
  return res.json();
}

export const api = {
  get: (path, params) => request(path, { method: "GET", params }),
  post: (path, body) => request(path, { method: "POST", body }),

  health: () => request("/health"),
  agentsList: () => request("/agents/"),

  // CREATE
  analyzeScreenplay: (payload) => request("/agents/screenplay/analyze", { method: "POST", body: payload }),
  extractVisualDna: (payload) => request("/create/visual-universe/extract-dna", { method: "POST", body: payload }),
  generateVisuals: (payload) => request("/create/visual-universe/generate", { method: "POST", body: payload }),
  visualHistory: (project_id) => request("/create/visual-universe/history", { method: "GET", params: { project_id } }),
  createScenePackage: (payload) => request("/create/scene-package", { method: "POST", body: payload }),
  createCharacterTwin: (payload) => request("/create/character-twin", { method: "POST", body: payload }),
  checkCharacterTwin: (payload) => request("/create/character-twin/check", { method: "POST", body: payload }),
  listCharacters: (project_id) => request("/create/characters", { method: "GET", params: { project_id } }),
  createStoryboard: (payload) => request("/create/storyboard", { method: "POST", body: payload }),

  // SIMULATE
  runSimulation: (payload) => request("/agents/simulation/run", { method: "POST", body: payload }),
  runScenarioLab: (payload) => request("/simulate/scenario-lab", { method: "POST", body: payload }),
  multiverseTree: (project_id) => request("/simulate/multiverse", { method: "GET", params: { project_id } }),
  listUniverses: (project_id) => request("/simulate/universes", { method: "GET", params: { project_id } }),

  // ANALYZE
  runResearch: (payload) => request("/agents/research/run", { method: "POST", body: payload }),
  runForensics: (payload) => request("/agents/forensics/run", { method: "POST", body: payload }),
  runAudience: (payload) => request("/analyze/audience", { method: "POST", body: payload }),
  audienceProjections: (project_id) => request("/analyze/audience-projections", { method: "GET", params: { project_id } }),
  runRedTeam: (payload) => request("/analyze/red-team", { method: "POST", body: payload }),
  redTeamFindings: (project_id) => request("/analyze/red-team/findings", { method: "GET", params: { project_id } }),

  // PRODUCE
  runBudget: (payload) => request("/produce/budget", { method: "POST", body: payload }),
  listBudgets: (project_id) => request("/produce/budgets", { method: "GET", params: { project_id } }),

  // DECIDE
  runGreenlight: (payload) => request("/decide/greenlight", { method: "POST", body: payload }),
  listDecisions: (project_id) => request("/decide/decisions", { method: "GET", params: { project_id } }),

  // Lumia (AI Co-Director)
  lumiaChat: (payload) => request("/lumia/chat", { method: "POST", body: payload }),

  // Analytics (CONTROL)
  simulationRuns: (project_id) => request("/analytics/simulation-runs", { method: "GET", params: { project_id } }),
  missionControlEvents: (project_id) => request("/analytics/mission-control-events", { method: "GET", params: { project_id } }),
  backendStatus: () => request("/analytics/backend-status"),
};

/** Live Mission Control feed. Auto-reconnects with backoff; never throws. */
export function useMissionControlSocket(maxEvents = 60) {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const retryRef = useRef(1000);

  useEffect(() => {
    let socket;
    let closedByEffect = false;
    let timer;

    function connect() {
      try {
        socket = new WebSocket(WS_URL);
      } catch {
        scheduleRetry();
        return;
      }
      socket.onopen = () => {
        setConnected(true);
        retryRef.current = 1000;
      };
      socket.onmessage = (msg) => {
        try {
          const parsed = JSON.parse(msg.data);
          setEvents((prev) => [{ ...parsed, receivedAt: Date.now() }, ...prev].slice(0, maxEvents));
        } catch {
          /* ignore malformed frames */
        }
      };
      socket.onclose = () => {
        setConnected(false);
        if (!closedByEffect) scheduleRetry();
      };
      socket.onerror = () => socket.close();
    }

    function scheduleRetry() {
      timer = setTimeout(connect, retryRef.current);
      retryRef.current = Math.min(retryRef.current * 1.6, 15000);
    }

    connect();
    return () => {
      closedByEffect = true;
      clearTimeout(timer);
      socket && socket.close();
    };
  }, [maxEvents]);

  return { events, connected };
}
