# ShipSafe Shared

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![Node 20+](https://img.shields.io/badge/node-20%2B-brightgreen.svg)](https://nodejs.org)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Gemini-orange.svg)](https://google.com/adk)

> Shared instrumentation, design tokens, demo data, and CLI scaffolding for the ShipSafe AI reliability platform.

---

## The ShipSafe Platform

ShipSafe is six independent AI agents that compose into a complete AI reliability
operating system for teams running AI in production. Each agent solves a specific
failure mode that destroys trust in autonomous systems.

| Agent | Problem it solves | Partner | Deploy |
|---|---|---|---|
| [CargoDB](https://github.com/shipsafe-ai/shipsafe-cargodb) | Agent decisions with no memory — "have we seen this before?" has no answer | MongoDB Atlas | `npx @shipsafe/cargodb init` |
| [RouteForge](https://github.com/shipsafe-ai/shipsafe-routeforge) | Algorithm changes that look fine in review but fail under real-world conditions | GitLab | `npx @shipsafe/routeforge init` |
| [VoyageBlack](https://github.com/shipsafe-ai/shipsafe-voyageblack) | Incidents that take 47 minutes of analyst time just to understand | Elastic | `npx @shipsafe/voyageblack init` |
| [TideSync](https://github.com/shipsafe-ai/shipsafe-tidesync) | Pipelines that report green while the data is silently stale | Fivetran | `npx @shipsafe/tidesync init` |
| [NaviGuard](https://github.com/shipsafe-ai/shipsafe-naviguard) | AI models drifting away from accuracy as the world changes | Arize Phoenix | `npx @shipsafe/naviguard init` |
| [AgentOps](https://github.com/shipsafe-ai/shipsafe-agentops) | AI agent fleets running invisibly until something goes wrong | Dynatrace | `npx @shipsafe/agentops init` |

Each agent stands alone as a complete product. Together they cover the full
spectrum of AI reliability: deployment safety, data trust, incident response,
institutional memory, model quality, and fleet observability.

---

## What's in this repo

`shipsafe-shared` is the foundation that all six agents depend on.
It is not a product you deploy directly — it is the library every agent imports.

### Python package — `shipsafe_shared`

```
shipsafe_shared/
├── instrumentation/     # OTel + OpenInference layer
│   └── telemetry.py     # init_telemetry() — one call, two destinations
├── demo_data/           # Hormuz Crisis fixtures (vessels, ports, scenario)
│   ├── vessels.json
│   ├── ports.json
│   └── hormuz_crisis.py
└── critic/              # Shared Critic base class all six agents subclass
    └── base.py
```

The `instrumentation` layer is the most critical piece. One call fans out to
both Phoenix Cloud (for NaviGuard's self-improvement loop) and Dynatrace
(for AgentOps' fleet observability):

```python
from shipsafe_shared.instrumentation import init_telemetry

init_telemetry(project_name="shipsafe-routeforge")
# → emits OpenInference OTel spans to Phoenix Cloud
# → emits OTel OTLP traces to Dynatrace
# Same code path, same trace stream, two observers
```

### Node CLI core — `cli_core/`

Shared deploy helpers, Secret Manager client, health check utilities, and
interactive prompts. Every `npx @shipsafe/<agent>` CLI imports from here.

### Design tokens — `design/`

Tailwind preset and TypeScript tokens. All six dashboards extend the same
`tailwind.preset.cjs` — dark mission-control aesthetic, consistent accent
colours per agent, shared typography and spacing across the fleet.

### Canonical docs — `docs/`

The source of truth for platform architecture and build plan:

| Doc | What's in it |
|---|---|
| `PARTNER-INTEGRATION.md` | Deep integration spec for all 6 partners — verified against official partner docs |
| `PHASES.md` | 13-day build plan with daily checklists |
| `ARCHITECTURE.md` | Cross-repo dependency diagram and runtime flow |
| `DESIGN-SYSTEM.md` | Visual language, component rules, and aesthetic direction |
| `UNIVERSAL-CLI.md` | CLI spec all six agents follow |
| `TDD-STRATEGY.md` | Testing philosophy and per-layer guidance |
| `GETTING-STARTED.md` | Dev environment setup from scratch |

---

## Install

### As a Python dependency (for agent repos)

Production (pinned to a tag):

```bash
pip install "shipsafe-shared @ git+https://github.com/shipsafe-ai/shipsafe-shared.git@v0.1.0"
```

Local development (editable, with both repos checked out side by side):

```bash
cd ~/dev/shipsafe/shipsafe-routeforge
pip install -e ../shipsafe-shared
```

### For development on this repo

```bash
git clone https://github.com/shipsafe-ai/shipsafe-shared.git
cd shipsafe-shared
pip install -e ".[dev]"
```

Requires Python 3.12+, Node 20+, and pnpm.

---

## The demo scenario

All six agents ship with a pre-built demo: the **Hormuz Crisis**. A geopolitical
incident closes the Strait of Hormuz to commercial shipping. Fourteen vessels
are in transit. Six AI agents respond simultaneously — each from its own angle,
each using its own partner's stack, each independently valuable.

Demo fixtures (real IMO vessel numbers, UN/LOCODE port codes, ISO 6346
container manifests) live in `shipsafe_shared/demo_data/`.

Run any agent's demo:

```bash
npx @shipsafe/<agent> demo
# Loads fixtures, triggers the crisis scenario, opens the dashboard
```

---

## Architecture

Each submission stands alone — no HTTP calls between agents at runtime.
Each uses its own partner's stack as its memory and compute layer. The fleet
narrative is conveyed through AgentOps reading the shared OTel telemetry
stream: observation only, never code dependency.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full cross-repo
dependency diagram and runtime flow.

---

## Requirements

| Dependency | Min version | Purpose |
|---|---|---|
| Python | 3.12 | Agent brains (all six) |
| Node.js | 20 LTS | CLI and dashboards |
| pnpm | 9.x | Node package management |
| Google Cloud SDK | latest | Auth, Cloud Run, Secret Manager |
| Docker Desktop | 27+ | Local container builds |

---

## License

MIT — fork it, deploy it, build on it. See [LICENSE](LICENSE).
