# ShipSafe · Cross-Repo Architecture

This document is the authoritative cross-repo reference. Before touching
any inter-repo dependency, cross-submission communication pattern, or
shared infrastructure component, read this document.

---

## Repository map

```
github.com/shipsafe-ai/
│
├── shipsafe-shared              ← Foundation (this concept starts here)
│   ├── shipsafe_shared/         Python package
│   │   ├── instrumentation/     OTel + OpenInference — shared by all six
│   │   ├── demo_data/           Hormuz Crisis fixtures — shared by all six
│   │   └── critic/              Base Critic class — subclassed by all six
│   ├── cli_core/                Node CLI helpers — imported by all six CLIs
│   └── design/                  Tailwind preset — extended by all six dashboards
│
├── shipsafe-routeforge          GitLab track submission
├── shipsafe-agentops            Dynatrace track submission
├── shipsafe-cargodb             MongoDB track submission
├── shipsafe-voyageblack         Elastic track submission
├── shipsafe-tidesync            Fivetran track submission
└── shipsafe-naviguard           Arize track submission
```

---

## Dependency arrows

### Python dependency (pip)

All six submission repos declare `shipsafe-shared` as a Python dependency.
In production they pin to a git tag; in local dev they use an editable
install from the sibling directory:

```
shipsafe-routeforge/pyproject.toml
  └── depends on → shipsafe-shared @ git+https://...@v0.1.0

(local dev)
shipsafe-routeforge/
  └── pip install -e ../shipsafe-shared
```

This gives each submission access to:
- `shipsafe_shared.instrumentation.init_telemetry()` — OTel setup
- `shipsafe_shared.demo_data.*` — Hormuz Crisis fixtures
- `shipsafe_shared.critic.base.CriticBase` — Critic parent class

### Node dependency (npm)

Each submission's CLI package depends on `cli_core`:

```
shipsafe-routeforge/cli/package.json
  └── "@shipsafe/cli-core": "github:shipsafe-ai/shipsafe-shared#v0.1.0"
```

Each submission's dashboard depends on the design tokens:

```
shipsafe-routeforge/dashboard/tailwind.config.ts
  └── presets: [require("@shipsafe/design/tailwind.preset.cjs")]
```

### What does NOT cross between submissions

**There are NO runtime HTTP calls between the six submission repos.**
This is CLAUDE.md Rule 8 — Cross-Submission Isolation.

Each submission must run completely independently for its partner judge
without any other submission's infrastructure being live. The competing-
services clause (hackathon rules Section 7.B) and the "substantially
different submission" requirement both favour clean independence.

The one exception: AgentOps reads telemetry from all six agents — but
it does this through the shared Dynatrace OTel stream (observation of
telemetry) not through direct HTTP calls to other submissions' Cloud
Run endpoints.

---

## The runtime architecture

Each of the six submissions has the same internal shape:

```
                    ┌────────────────────────────┐
   External event   │  Submission (Cloud Run)     │
   ─────────────►  │  ┌────────────────────────┐ │
   (webhook, API,  │  │  Orchestrator (ADK)     │ │
    schedule, CLI) │  │  ┌───────────────────┐  │ │
                   │  │  │  Specialist 1     │  │ │
                   │  │  │  Specialist 2     │  │ │
                   │  │  │  Specialist 3     │  │ │
                   │  │  │  Specialist 4     │  │ │
                   │  │  │  Specialist 5     │  │ │
                   │  │  │  Critic           │  │ │
                   │  │  └───────────────────┘  │ │
                   │  └────────────────────────┘ │
                   │                              │
                   │  Dashboard (Next.js)         │
                   └──────────┬───────────────────┘
                              │
              ┌───────────────┼───────────────────┐
              │               │                   │
              ▼               ▼                   ▼
       Partner MCP      GCP Secret           OTel stream
       (their stack)    Manager              (OTLP push)
                                                 │
                                    ┌────────────┴──────────┐
                                    │                       │
                                    ▼                       ▼
                             Phoenix Cloud           Dynatrace
                             (NaviGuard              (AgentOps
                              reads this)             reads this)
```

---

## The shared OTel stream — the Option C backbone

The instrumentation layer is what makes AgentOps possible without
cross-submission HTTP calls:

```
shipsafe_shared.instrumentation.init_telemetry()
         │
         │  same call
         │
         ├── If PHOENIX_API_KEY set:
         │       phoenix.otel.register(auto_instrument=True)
         │       → sends OpenInference spans to Phoenix Cloud
         │       → NaviGuard's Phoenix MCP can query these
         │
         └── If DT_ENVIRONMENT + DT_OTLP_TOKEN set:
                 OTLPExporter → Dynatrace
                 Protocol:    http/protobuf  ← MUST be this, not gRPC
                 Endpoint:    {DT_ENVIRONMENT}/api/v2/otlp  ← no signal suffix
                 Token scope: openTelemetryTrace.ingest
                 Metrics:     delta temporality
                 → AgentOps' Dynatrace MCP can DQL query these
```

All six agents call `init_telemetry()` at startup. Both Phoenix and
Dynatrace receive the full trace stream from all six agents.

---

## Per-submission partner architecture

### CargoDB → MongoDB

```
Event → Orchestrator → Specialists → MongoDB MCP Server
                                         │
                              ┌──────────┴────────────┐
                              │     Atlas cluster      │
                              │  cargodb_memory.       │
                              │  decisions             │
                              │  + Vector Search index │
                              │  + Voyage AI embeddings│
                              └───────────────────────┘
```

Memory layer: MongoDB Atlas Vector Search. Atlas is both the data
store AND the semantic recall engine. No external vector DB needed.

### RouteForge → GitLab

```
MR event → GitLab webhook → Orchestrator → Three channels:
                                    │
                    ┌───────────────┼──────────────────┐
                    │               │                  │
              Webhook auth    MCP OAuth         REST API PAT
              (entry point)   (AI-aware tools:  (workhorse reads
                              semantic_code_    and writes)
                              search, etc.)
```

Three-channel architecture. MCP for the AI-native capabilities;
REST for the reliable workhorse; webhook for the trigger.

### VoyageBlack → Elastic

```
Incident → Orchestrator → ES|QL tools (via MCP) → Elasticsearch
                                                       │
                                           ┌──────────┴───────────┐
                                           │  logs-* index         │
                                           │  postmortems-* index  │
                                           │  semantic_text fields │
                                           │  ELSER auto-embeds    │
                                           └──────────────────────┘
```

Elasticsearch is the memory layer (past postmortems), the search
engine (ELSER semantic recall), and the MCP server — one product,
three roles.

### TideSync → Fivetran

```
Sync event → Orchestrator → Two independent sources:
                    │
            ┌───────┴────────────────┐
            │                        │
     Fivetran MCP            BigQuery direct
     (pipeline status)       (data freshness)
            │                        │
            └──────────┬─────────────┘
                       │
                ImpactMapper (Gemini)
                "sync OK but data stale"
                       │
                  CONTRADICTION → alert
```

The contradiction between what Fivetran's control plane reports
and what the destination data actually contains IS the product.

### NaviGuard → Arize

```
Traces → Phoenix Cloud → Phoenix MCP → Orchestrator → Self-improvement loop:
                                            │
                        ┌───────────────────┼───────────────────────┐
                        │                   │                       │
                ModelMonitor        DatasetBuilder          ExperimentRunner
                (detect drift)      (capture failures)      (propose retrain)
                        │                   │                       │
                        └───────────────────┴───────────────────────┘
                                            │
                                    Human approval
                                            │
                                   Retrain experiment
                                   started in Phoenix
```

NaviGuard is the only submission that reads its partner's data
AND writes back to it (creating datasets and experiments in
Phoenix). The self-improvement loop is Arize's rubric centerpiece.

### AgentOps → Dynatrace

```
All 6 agents' OTel stream → Dynatrace Grail storage
                                        │
                              Dynatrace MCP (DQL)
                                        │
                              AgentOps Orchestrator
                              ┌─────────┴──────────┐
                              │                    │
                         FleetWatcher        CascadeTracer
                         TokenAccountant     AnomalyScout
                         IncidentNarrator    Critic
```

AgentOps is the capstone — the agent that watches the other agents.
Its partner integration is read-only observation of the shared OTel
stream. No HTTP calls to other submissions.

---

## CLAUDE.md per-repo strategy

Each repo has its own CLAUDE.md at the root. Claude Code reads the
local one. The canonical cross-cutting rules live in
`shipsafe-shared/CLAUDE.md`. Per-submission CLAUDE.md files re-state
the 9 rules verbatim and add submission-specific rules.

When the canonical rules change, update all seven files. The sync
script at `shipsafe-shared/scripts/sync_claude_md.sh` can automate
the cross-cutting section sync.

---

## Trial account timing

Trial clocks are staggered to avoid expiry during the judging
window (Jun 22 – Jul 7):

| Account | Clock trigger | Expires |
|---|---|---|
| MongoDB Atlas | none (free tier) | never |
| Voyage AI | none (free tier) | never |
| Phoenix Cloud | none (free tier) | never |
| GitLab Ultimate | Day 3 signup | ~Jul 1 ✅ |
| Dynatrace | Day 4 signup | ~Jun 19 ⚠️ video demo is primary |
| Elastic Cloud | Day 6 signup | ~Jun 20 ⚠️ video demo is primary |
| Fivetran | First sync Day 7 | ~Jun 21 ⚠️ video demo is primary |

For trials that expire before the judging window ends, the video
demo is the primary evidence. The README instructs judges to clone
and run locally with their own credentials if they want a live check.

---

## Cross-cutting rules summary

Full rules with rationale are in `CLAUDE.md`. Summary for quick reference:

1. Gemini via Vertex AI for ALL LLM calls — including evaluator judges
2. Python ADK for all agent brains — no low-code Agent Builder
3. Deep MCP integration per partner — not surface-level tool calls
4. Cloud Run only deployments — no Kubernetes, no Lambda, no VMs
5. GCP Secret Manager for ALL credentials — nothing in .env files
6. TDD always — test file exists and fails before implementation code
7. Gemini model from config, never hardcoded
8. Cross-submission isolation — no runtime HTTP between submissions
9. Prompt-injection defense — human approval gate on all external actions

---

## Local directory convention

```
~/dev/shipsafe/
├── shipsafe-shared/      ← clone this first
├── shipsafe-routeforge/
├── shipsafe-agentops/
├── shipsafe-cargodb/
├── shipsafe-voyageblack/
├── shipsafe-tidesync/
└── shipsafe-naviguard/
```

Siblings under one parent so `pip install -e ../shipsafe-shared`
works from any submission repo during local development.
