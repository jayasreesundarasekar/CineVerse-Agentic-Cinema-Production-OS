# Cineverse — Multi-Agent Screenplay & Production Intelligence Platform

A FastAPI backend orchestrating specialized AI agents for screenplay
reasoning, narrative simulation, factual research, movie forensics,
and media intelligence — with real-time Mission Control monitoring
and ClickHouse-backed "multiverse" analytics.

## Architecture

```
React dashboard (frontend/)  <-- CORS -->  FastAPI (app/main.py)
                                             ├─ /storage/*        -> Google Cloud Storage (uploads/artifacts)
                                             ├─ /agents/*, /create|simulate|analyze|produce|decide/* -> AgentOrchestrator
                                             ├─ /analytics/*      -> ClickHouse (runs, scores, events)
                                             └─ /ws/mission-control -> WebSocket real-time agent feed
                                                                        (also visualized via Grafana)
```

### Agents (app/agents/)
| Agent | File | Role |
|---|---|---|
| Screenplay Agent | `screenplay_agent.py` | Structure, arcs, pacing, dialogue, theme scoring |
| Simulation Agent | `simulation_agent.py` | "What-if" narrative simulations, scored & logged to ClickHouse |
| Research Agent | `research_agent.py` | Fact-checks script claims via Parallel API/MCP |
| Forensics Agent | `forensics_agent.py` | Compares script to TMDB/OMDb metadata for originality |
| Media Intelligence Agent | `media_intelligence_agent.py` | YouTube-based buzz/marketing analysis |

All agents inherit `BaseAgent`, call Gemini through `GeminiClient`, and
broadcast progress to Mission Control via the shared `ConnectionManager`.
`AgentOrchestrator` (`app/agents/orchestrator.py`) routes single-agent
calls and chains a full pipeline (`/agents/pipeline/full`). Its interface
mirrors what a deployed Google Cloud Agent Builder / Agent Engine
reasoning engine would expose, so swapping in real Agent Engine
endpoints later (via `AGENT_ENGINE_ID`) is a drop-in change.

## Frontend — Cineverse dashboard

A full React dashboard lives in `frontend/`, with a Home landing page
(hero, pipeline stepper, module cards, Recent Projects, and the Lumia
AI Co-Director panel) plus all six modules (CREATE, SIMULATE, ANALYZE,
PRODUCE, DECIDE, CONTROL). The Cinema Multiverse branching tree is the
one hero visual; Lumia's quick actions and chat call real backend
agents (`POST /lumia/chat`), not scripted copy. See `frontend/DESIGN.md`
for the full design rationale (palette, type, layout).

```bash
cd frontend
cp .env.example .env      # points at your running FastAPI backend
npm install
npm run dev                # http://localhost:5173
```

Run the backend (`uvicorn app.main:app --reload`) alongside it — CORS is
already open (`allow_origins=["*"]`) so the dashboard can call it directly.

## Gemini SDK (important if you set up this project before ~mid-2026)

Cineverse uses the current **`google-genai`** SDK (`from google import
genai`), not the old `google-generativeai` package — Google fully
retired that package and it receives no more fixes. Model defaults are
also current: `gemini-3.5-flash` for text/reasoning and
`gemini-3.1-flash-image` for image generation, since the `gemini-2.0-*`
family (including the old image-preview model) was shut down June 1,
2026. Check `app/config.py` if newer models have since shipped.

Two related fixes worth knowing about if you're debugging this locally:
- **`.env` is now resolved relative to the project root**, not the
  process's working directory — so starting `uvicorn` from a different
  folder (an IDE run config, a systemd unit, etc.) no longer silently
  reads `gemini_api_key` as empty.
- **A failing live Gemini call surfaces the real error** in the
  response's mock `note` field (e.g. `"Gemini API error: 401
  Unauthorized"`) instead of falling back to the exact same message as
  "no key configured" — the fallback behavior is unchanged, but you can
  now tell a bad/expired key or a retired model ID apart from a genuinely
  unconfigured one just by reading the response.

## Extended product modules (CREATE / SIMULATE / ANALYZE / PRODUCE / DECIDE / CONTROL)

Beyond the original 5 core agents, the platform is organized into 6 modules
via `app/api/routes_studio.py`, backed by new agents in `app/agents/`:

| Module | Endpoint(s) | Agent | What it does |
|---|---|---|---|
| 🎭 CREATE | `POST /create/storyboard` | `storyboard_agent.py` (AI Shot Designer) | Scene -> shot list: shot type, **lens (mm)**, **camera movement**, camera angle, duration, location, cast, props, VFX, lighting — saved to GCS |
| 🎭 CREATE | `POST /create/visual-universe/extract-dna` | `visual_universe_agent.py` | **Visual Universe Generator**, step 1 — extracts locations, time period, weather, architecture, mood, color/lighting direction, genre, visual motifs, props, environmental details, and a ready-to-use image prompt |
| 🎭 CREATE | `POST /create/visual-universe/generate` | `visual_universe_agent.py` | **GENERATE VISUALS**, step 2 — 1-4 images for a chosen category (📍location / 🎭character / 🎬scene / 🎨moodboard / 🏙️world / 🎞️shot), each a distinct variant (e.g. establishing shot, night version, interior version), saved to GCS. Uses Gemini's own image-output mode — no extra image API added |
| 🎭 CREATE | `POST /create/scene-package` | orchestrator `run_scene_to_shots_pipeline` | The full **Story → Scene → Visuals → Shots** pipeline in one call: extracts visual DNA, generates reference visuals, then feeds both into the AI Shot Designer |
| 🎭 CREATE | `POST /create/character-twin`, `POST /create/character-twin/check` | `character_twin_agent.py` | Persistent character profile (goals/fears/values/arc); checks if a decision is in-character |
| 🌌 SIMULATE | `POST /simulate/scenario-lab` | `scenario_lab_agent.py` | Generalized "WHAT IF...?" engine (budget cuts, actor loss, ending/genre/runtime changes); can register a new node in the... |
| 🌌 SIMULATE | `GET /simulate/multiverse` | `app/core/multiverse.py` | ...**Cinema Multiverse** — the branching universe tree (ORIGINAL → Universe A/B → ... → GREENLIGHT) |
| 🔍 ANALYZE | `POST /analyze/audience` | `audience_agent.py` | Simulated audience-segment appeal scores (18-24, genre fans, international, etc.) — explicitly labeled as AI projections |
| 🔍 ANALYZE | `POST /analyze/red-team` | `red_team_agent.py` | Adversarial critic hunting plot holes, inconsistencies, cost/audience risk before greenlight |
| 🎥 PRODUCE | `POST /produce/budget` | `budget_agent.py` | Line-item budget simulator: recalculates cost/risk/quality/audience-impact deltas for a "what if" change |
| 🏢 DECIDE | `POST /decide/greenlight` | `executive_agent.py` (chains audience+budget+red_team) | Full Greenlight Engine pipeline with a **Decision Provenance** trace |
| 🏢 DECIDE | `POST /decide/executive`, `GET /decide/decisions` | `executive_agent.py` | Direct executive call, and the decision log (verdict + reasoning + source run IDs) |
| 📡 CONTROL | `WS /ws/mission-control` | — | Real-time feed of all of the above (unchanged from the core build) |

**Note on the shared analytics singleton:** every agent and route imports
`analytics` from `app.core.clickhouse_client` (a module-level singleton)
rather than instantiating `ClickHouseAnalytics()` itself. In mock/in-memory
mode (no ClickHouse configured) each instance would otherwise get its own
isolated store, so e.g. a Scenario Lab universe wouldn't be visible to the
Multiverse tree endpoint. Keep using the shared `analytics` import if you
add new agents/routes.

## APIs used (as specified)

- **Google Gemini API** — `app/core/gemini_client.py` (core reasoning for every agent)
- **Google Cloud Agent Builder / Agent Engine** — orchestration pattern in `app/agents/orchestrator.py`
- **Google Cloud Storage** — `app/core/gcs_storage.py`
- **ClickHouse** — `app/core/clickhouse_client.py`, schema in `clickhouse/init.sql`
- **Grafana** — dashboard + datasource provisioning in `grafana/`
- **Parallel API/MCP** — `app/integrations/parallel_client.py` (Research Agent)
- **YouTube Data API** — `app/integrations/youtube_client.py` (Media Intelligence Agent)
- **TMDB API** — `app/integrations/tmdb_client.py` (Forensics Agent)
- **OMDb API** — `app/integrations/omdb_client.py` (Forensics Agent)
- **FastAPI** — `app/main.py` and `app/api/*`
- **WebSocket** — `app/core/websocket_manager.py`, `/ws/mission-control`

## Mock mode

Every external client (Gemini, GCS, ClickHouse, TMDB, OMDb, YouTube,
Parallel) gracefully falls back to a clearly-labeled simulated response
when its API key/credentials are missing. This means the full pipeline
runs end-to-end out of the box — fill in `.env` keys incrementally to
switch each piece over to live data.

## Setup

```bash
cp .env.example .env        # then fill in your API keys
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Or just run `./scripts/run_dev.sh`.

### With ClickHouse + Grafana (Docker)

```bash
docker compose up --build
```

- API: http://localhost:8000 (docs at `/docs`)
- Grafana: http://localhost:3000 (default admin/admin) — import
  `grafana/dashboards/mission_control_dashboard.json`
- ClickHouse HTTP: http://localhost:8123

### Google Cloud setup (for live GCS / Gemini / Agent Engine)

1. Create a GCP project and enable: Vertex AI API, Cloud Storage API.
2. Create a service account with Storage Object Admin + Vertex AI User,
   download its JSON key, and set `GOOGLE_APPLICATION_CREDENTIALS`.
3. Create a GCS bucket matching `GCS_BUCKET_NAME`.
4. Get a Gemini API key (Google AI Studio) and set `GEMINI_API_KEY`.
5. (Optional) Deploy agents to Agent Engine and set `AGENT_ENGINE_ID`
   to point `AgentOrchestrator` at the remote endpoints instead.

## API quick reference

- `POST /storage/upload` — upload a script/production doc
- `GET  /agents/` — list available agents
- `POST /agents/screenplay/analyze` — structural analysis
- `POST /agents/simulation/run` — run a narrative simulation
- `POST /agents/research/run` — fact-check via research agent
- `POST /agents/forensics/run` — compare against comparable titles
- `POST /agents/media-intelligence/run` — YouTube buzz analysis
- `POST /agents/pipeline/full` — chained end-to-end pipeline
- `GET  /analytics/simulation-runs` / `/screenplay-scores` / `/mission-control-events`
- `WS   /ws/mission-control` — real-time agent activity stream

## Tests

```bash
pytest app/tests -v
```
