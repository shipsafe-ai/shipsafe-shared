# VoyageBlack — Demo Video Script (3:30)
**Track:** Elastic · **Accent:** #3B82F6 blue · **Tagline:** *"Your worst incident took 3 weeks to document. This takes 90 seconds."*
**Live URLs:** Agent `https://voyageblack-agent-o34wppiwiq-uc.a.run.app` · Dashboard + es-mcp-server deployed (URLs via terraform, not hardcoded)
**Verified against code 2026-06-11.**

---

## ⚠ ACCURACY GUARDRAILS (read before recording)
- ✅ Two real MCP servers — show both badges: **Agent Builder MCP** (5 custom ES|QL/ELSER tools: `incident_logs_timewindow`, `incident_logs_semantic`, `service_error_correlation`, `similar_past_incident`, `write_postmortem`) and the **standalone Elasticsearch MCP** (`docker.elastic.co/mcp/elasticsearch`: `list_indices`, `search`, `esql`).
- ⚠ **`write_postmortem` is listed but NEVER invoked.** The actual write is a **direct Elasticsearch REST `httpx.put`** to `postmortems-shipsafe/_doc/{id}` in `report_writer.write()`. Don't say "approval triggers the write_postmortem MCP tool." Say "writes the postmortem back to Elasticsearch" (true) — or "via Elasticsearch" generically.
- ✅ Real specialist order: TimelineBuilder → CorrelationEngine → ImpactCalculator (the one on the standalone ES MCP) → RootCauseAnalyzer (pure Gemini, no tools) → ReportWriter → Critic (always last).
- ✅ **ELSER semantic search is the star.** `similar_past_incident` runs ELSER over the `postmortems-shipsafe` index; mappings use `semantic_text` with inference `.elser-2-elasticsearch`. The demo seeds one prior postmortem (Red Sea 2024) so the FIRST run already returns a real semantic match. Show the % match.
- ✅ Recommendations are **Gemini-generated from evidence** (each must cite a service/pattern/event_id) — not hardcoded. RootCauseAnalyzer receives only structured fields, never raw log text (injection isolation).
- ✅ Demo command: **`voyageblack demo`** (`npx @shipsafe/voyageblack demo`) — Hormuz path, window 14:57→15:02Z. Dashboard also has a **"Load Auth Outage Demo"** button (non-maritime, 11-event auth→payment→notification cascade) — great universality shot.
- ⚠ **Don't assert an exact on-screen event count** ("9 events"). The window (14:57→15:02) excludes the first 3 fixture events, and the window-filtering ES|QL lives in Kibana, not the repo. Read whatever `entry_count` the live run shows.
- ✅ Human gate: `/run` only ever returns a **draft**; writing happens only via `POST /approve/{id}` ("Approve & Write to Elastic"). The Approve button is **disabled when injection is detected**. Critic has a deterministic regex layer + a Gemini semantic layer that fails closed.

---

## SCRIPT

| Time | SCREEN | NARRATOR (V.O.) |
|---|---|---|
| 0:00–0:10 | Black. A wall of raw log lines scrolls fast — ERROR, CRITICAL, timeouts — unreadable. Caption: *"3 weeks to write the postmortem."* | *(silence 2s)* "Your worst outage is over. Now comes the part everyone dreads: three weeks of scrolling logs to reconstruct what actually happened — while the details fade." |
| 0:10–0:30 | The scroll freezes. Highlighted scattered events: a routing failure, an SLA breach, an unsafe merge, a stale feed — clearly related, pages apart. | "The story is *in* the logs — a routing failure here, a cargo SLA breach there, an unsafe merge, a stale data feed. All connected. All buried across thousands of lines and a dozen services. Humans are slow at this and bad at it, and the postmortem ships too late to prevent the next one." |
| 0:30–0:55 | Six ShipSafe agents tile in; blue VoyageBlack highlights last. | *(shared 30s pitch)* "ShipSafe is a fleet of six AI agents… the human decides, always. Today: VoyageBlack." |
| 0:55–1:15 | Dashboard: "Load Hormuz Demo" + "Generate Postmortem". | "VoyageBlack turns raw incident logs into a finished postmortem in about ninety seconds. The engine is Elastic — ELSER semantic search plus ES|QL — and Gemini is the brain that does what search can't: synthesize scattered events into a single causal narrative, and write recommendations grounded in the actual evidence." |
| **1:15–1:35** | Click **Generate Postmortem**. Stage 1 **TimelineBuilder** (badge *Agent Builder*) streams live Gemini "thinking" then ✓ `{entry_count, services}`. | "Watch ninety seconds of incident response. Stage one — TimelineBuilder queries Elastic over the incident window and Gemini reconstructs the ordered timeline. You're seeing it think, live." |
| **1:35–2:00** | Stage 2 **CorrelationEngine** (*Agent Builder*) ✓ `{service_count, max_cascade_depth}`. Stage 3 **ImpactCalculator** (badge *ES MCP*) ✓ `{total_errors, services_affected, duration}`. | "Stage two correlates errors across services and finds the cascade depth — what triggered what. Stage three switches to the standalone Elasticsearch MCP server and runs raw ES|QL to compute the blast radius: how many services, how many errors, how long." |
| **2:00–2:25** | Stage 4 **RootCauseAnalyzer** (no badge — pure Gemini) ✓ `{confidence %, primary_cause}`. Recommendations render, each citing a service/event_id. | "Stage four is pure reasoning — no tools. Gemini receives only the structured facts, never the raw log text, and diagnoses the root cause with a confidence score and recommendations that each cite a specific service and failure mode. Grounded, not generic — and isolated from anything an attacker could hide in a log line." |
| **2:25–2:45** | Stage 5 **ReportWriter** (*Agent Builder*) ✓ `{similar_count, top_similarity %}` — surfaces **Red Sea 2024** as a semantic match. Stage 6 **Critic** ✓ `{approved, injection_detected, risk_level}`. | "Stage five is the part I love: ELSER semantic search finds a *similar past incident* — Red Sea 2024 — and pulls its lessons forward. Stage six, the Critic, scans every log line for prompt injection and reviews the draft for hallucination. Then it routes to a human." |
| 2:45–3:05 | Redirect to `/postmortem/{id}`: full timeline, blast radius, root cause, similar incidents, recommendations, then the **"Human Review Required"** gate. Click **Approve & Write to Elastic**. | "Ninety seconds in, a complete postmortem — and a gate. Nothing is written until a human approves. On approve, it's written back to Elasticsearch with ELSER semantic indexing — so this incident becomes findable for the *next* one. That's the flywheel: every postmortem you approve makes the next investigation faster." |
| 3:05–3:20 | Click **"Load Auth Outage Demo"** → a non-maritime auth→payment→notification cascade runs the identical pipeline. | "And it isn't about ships. Here's a SaaS auth outage — authentication, payments, notifications — same pipeline, same ninety seconds. VoyageBlack works for any incident in any system that writes logs to Elastic." |
| 3:20–3:30 | Dashboard. End frame: VoyageBlack mark, tagline, Elastic + Google Cloud logos. | "Your worst incident took three weeks to document. This takes ninety seconds — and remembers it forever. VoyageBlack." |

---

## Devpost description (≈145 words)
VoyageBlack turns raw incident logs into a complete, citable postmortem in about ninety seconds. After an outage, the story is buried across thousands of log lines and a dozen services — and reconstructing it by hand takes weeks. VoyageBlack uses Elastic — ELSER semantic search and ES|QL across two MCP servers — to rebuild the timeline, correlate the cross-service cascade, and compute the blast radius. Gemini on Vertex AI then synthesizes the causal narrative and writes recommendations grounded in specific evidence, isolated from raw log text so attacker-crafted log lines can't manipulate it. ELSER surfaces similar past incidents to pull lessons forward, an adversarial Critic checks for injection and hallucination, and a mandatory human approval gate guards every write. Approved postmortems are re-indexed semantically, so each one accelerates the next. Demonstrated on maritime crisis and a SaaS auth outage; works for any logged system.

## Social captions
1. Your worst outage took 3 weeks to write up. VoyageBlack does it in 90 seconds — timeline, cascade, blast radius, root cause — using Elastic ELSER + ES|QL and Gemini. Then ELSER remembers it for the next one. #GoogleCloud
2. The postmortem story is already in your logs; humans are just slow at reading 10,000 lines across 12 services. VoyageBlack reads it in 90s, cites the evidence, and waits for human approval before writing. #Elastic #AIagents
3. Every postmortem you approve makes the next investigation faster — VoyageBlack re-indexes it with ELSER semantic search so similar incidents surface instantly. A memory flywheel for incident response. #GoogleCloud
