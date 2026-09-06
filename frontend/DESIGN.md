# Cineverse dashboard — design plan

Subject: an AI studio backend for film producers — screenplay reasoning,
branching "what if" universes, budget/audience/red-team review, and a
final greenlight call. Audience: producers and hackathon judges deciding
whether to trust an AI studio's recommendation. The dashboard's job is to
make six very different workflows (write, simulate, critique, budget,
decide, monitor) feel like one coherent screening room, not six separate
tools bolted together.

## Color
- `#0B0D17` void — base background, the dark of a screening room
- `#141833` surface / `#1D2242` surface2 — panel layers
- `#C9A227` brass — the "greenlight" / film-reel metal accent, used for
  primary actions and anything that has been approved
- `#2E9E97` teal — the Simulate/Multiverse energy color, branch lines and
  running-simulation states
- `#C1443C` redteam — reserved only for Red Team severity and risk flags,
  never used decoratively
- `#EDE6D6` parchment — primary text, an aged title-card cream rather than
  a bright white, `#8B8FA3` muted for secondary text

## Type
- **Fraunces** (display serif, with its ink-trap detail) for module
  titles and the Cineverse wordmark — it reads like an old title card,
  not a SaaS dashboard.
- **Space Grotesk** for all UI text and body copy — a technical, slightly
  architectural grotesk that keeps long score/finding lists legible.
- **IBM Plex Mono** used narrowly and functionally — only for the actual
  numeric telemetry (scores, run IDs, timestamps in the Mission Control
  feed) where a fixed-width readout genuinely helps scanning, not as a
  generic label face.

## Layout
```
+------------------------------------------------------------+
| ⏺ CINEVERSE    [search projects, ideas...  ⌘K]  proj 🔔 ●  |
+---------+----------------------------------------------------+
| sprocket|  Hero: eyebrow / wordmark / tagline | gradient art |
|  Home   |  Pipeline stepper (1-6, numbered)                  |
|  CREATE |  6 module cards (image-zone + label, title, desc)  |
|   ...   |  Recent projects grid                              |
|  SIMUL. |                                          [Lumia]   |
|  ANALYZE|                                          [DNA]     |
|  PRODUCE|                                          [Activity]|
|  DECIDE |                                                    |
|  CONTROL|                                                    |
| [Lumia] |                                                    |
+---------+----------------------------------------------------+
```
Sidebar groups nav under CREATE / SIMULATE / ANALYZE / PRODUCE / DECIDE /
CONTROL headers, each with real sub-items (Screenplay, Visual Universe,
Shot Designer under CREATE; Audience, Characters under ANALYZE; etc.) —
clicking one navigates to the owning view and scrolls that section into
view. Two sub-items (Schedule, Crew) are marked "soon" rather than faked,
since there's no backend agent behind them yet.

## Principles
- One hero per session: the branching multiverse tree (Simulate) and the
  Home hero are the memorable visual moments; everywhere else stays a
  disciplined, data-dense panel.
- No fabricated media: card/hero "photography" is generative gradient
  art by default; a real photo only appears when the Visual Universe
  agent actually generates one. The avatar is an abstract mark, not a
  photo of a person.
- Every AI output is labeled with its source agent and, where relevant,
  whether it's mock or live — the interface never pretends simulated
  data is real audience research.
- Motion only on state change: a node entering the multiverse tree
  animates in; nothing fades/slides on scroll.
