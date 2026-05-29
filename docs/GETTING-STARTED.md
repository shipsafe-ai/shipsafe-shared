# ShipSafe · Getting Started

This is the dev environment setup guide for working on the ShipSafe
agent ecosystem. Read this once on Day 1; refer back during Phase
0 deliverables.

For the 13-day build plan, see PHASES.md. For partner-specific
integration, see PARTNER-INTEGRATION.md. For visual standards, see
DESIGN-SYSTEM.md. For CLI behavior, see UNIVERSAL-CLI.md. For
testing discipline, see TDD-STRATEGY.md.

---

## What you're building

Six independent AI agents that compose into one platform. Each
agent ships as its own GitHub repository, deploys to its own
Cloud Run service, and connects to its own partner stack. They
share a foundation: one Python package + one Node CLI scaffolding
package, both living in `shipsafe-shared`.

```
shipsafe-ai (GitHub org)
│
├── shipsafe-shared          ← foundation: instrumentation, demo data, CLI core, design tokens
│
├── shipsafe-routeforge      ← GitLab track
├── shipsafe-agentops        ← Dynatrace track
├── shipsafe-cargodb         ← MongoDB track
├── shipsafe-voyageblack     ← Elastic track
├── shipsafe-tidesync        ← Fivetran track
└── shipsafe-naviguard       ← Arize track
```

Each submission repo depends on `shipsafe-shared` as a Python
package (via git dep) for instrumentation, demo data, and the
shared Critic base class. Submission dashboards depend on
`shipsafe-shared/design/` for visual tokens. Submission CLIs
depend on `shipsafe-shared/cli_core/` for deploy and secrets
helpers.

---

## Local working directory

Pick one parent directory where all seven repos live as siblings.
The convention used throughout these docs:

```
~/dev/shipsafe/
├── shipsafe-shared/
├── shipsafe-routeforge/
├── shipsafe-agentops/
├── shipsafe-cargodb/
├── shipsafe-voyageblack/
├── shipsafe-tidesync/
└── shipsafe-naviguard/
```

This matters: when a submission's `pyproject.toml` declares
`shipsafe-shared` as a dev dependency, the relative path
`../shipsafe-shared` is what makes local editing work.

---

## Tools required on your Mac

Install these before Day 1's work starts:

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Agent brains, all six |
| Node.js | 20 LTS+ | CLI scaffolding, dashboards |
| pnpm | latest | Node package manager (faster than npm) |
| gcloud CLI | latest | GCP authentication and deploys |
| Docker Desktop | latest | Local container builds for Cloud Run |
| git | 2.40+ | Multi-repo workflow |
| Claude Code | latest | The primary build interface |

Quick install (macOS, Homebrew):

```bash
brew install python@3.12 node pnpm google-cloud-sdk docker git
```

Claude Code is installed separately per Anthropic's instructions.
Follow https://docs.claude.com for the current install command.

Verify versions:

```bash
python3.12 --version    # → 3.12.x
node --version          # → v20.x or later
pnpm --version          # → 9.x or later
gcloud --version        # → 500+
docker --version        # → 27+
git --version           # → 2.40+
```

---

## GCP authentication

Authenticate once on Day 1. The same credentials are used by all
six agent builds across the next 13 days.

```bash
gcloud auth login                          # browser-based login
gcloud auth application-default login      # for SDK use
gcloud config set project <your-gcp-project-id>
```

The `<your-gcp-project-id>` is the project where all six Cloud Run
services will deploy. Use one project for the whole hackathon —
keeps IAM, Secret Manager, and BigQuery simple.

---

## Day 1 setup sequence

Refer to PHASES.md Day 1 for the full deliverables. The setup
order:

1. **Create the GitHub org `shipsafe-ai`** (or your chosen org name)
2. **Create the seven repos** under the org, all public, all MIT
   licensed (see PHASES.md Day 1 for the exact repo names)
3. **Clone `shipsafe-shared` to `~/dev/shipsafe/shipsafe-shared/`**
4. **Build the project structure** (see "Repo structure" below)
5. **Copy the canonical docs** into the right locations
6. **Sign up for partner accounts** that have no trial clock
   (MongoDB Atlas free tier, Voyage AI, Phoenix Cloud, Fivetran —
   but DO NOT trigger Fivetran's first sync, that starts the clock)
7. **Request GCP credits** (Jun 4 hard deadline — do this on Day 1)
8. **Register OGC 2026** (deadline Jun 7 — do this on Day 1)
9. **Install Phoenix Docs MCP in Claude Code** (one-liner —
   see Phase 0 Day 1 in PHASES.md)

The six submission repos sit empty until Day 3+. Day 1 + Day 2
are entirely about `shipsafe-shared` and partner accounts.

---

## Repo structure — shipsafe-shared

This is the Phase 0 Day 1-2 deliverable. The skeleton:

```
shipsafe-shared/
├── README.md                          # public-facing
├── LICENSE                            # MIT
├── CLAUDE.md                          # canonical cross-cutting rules
├── pyproject.toml                     # Python package metadata
├── docs/
│   ├── PARTNER-INTEGRATION.md
│   ├── PHASES.md
│   ├── DESIGN-SYSTEM.md
│   ├── UNIVERSAL-CLI.md
│   ├── TDD-STRATEGY.md
│   ├── GETTING-STARTED.md             # this file
│   └── ARCHITECTURE.md
├── shipsafe_shared/                   # Python package (note underscore)
│   ├── __init__.py
│   ├── instrumentation/
│   │   ├── __init__.py
│   │   └── telemetry.py              # init_telemetry() entry point
│   ├── demo_data/
│   │   ├── __init__.py
│   │   ├── vessels.json
│   │   ├── ports.json
│   │   ├── hormuz_crisis.py
│   │   ├── seed.py
│   │   └── fixtures/
│   └── critic/
│       ├── __init__.py
│       └── base.py                    # shared Critic base class
├── cli_core/                          # Node CLI scaffolding (separate npm pkg)
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── deploy.ts                  # Cloud Run helper
│       ├── secrets.ts                 # Secret Manager helper
│       ├── health.ts                  # post-deploy health check
│       └── prompts.ts                 # interactive setup prompts
├── design/                            # Frontend design tokens (Tailwind preset)
│   ├── package.json
│   ├── tokens.ts
│   └── tailwind.preset.cjs
├── tests/
│   ├── test_instrumentation.py
│   └── test_demo_data.py
└── .github/
    └── workflows/
        ├── python-ci.yml
        └── node-ci.yml
```

Naming convention: the repo and the PyPI/npm package names are
hyphenated (`shipsafe-shared`), but the Python import path uses
underscore (`shipsafe_shared`) per Python convention. The Node
CLI core is its own npm package — separate from the Python so
agent repos can depend on the Python without needing Node, and
dashboard repos can depend on the Node without needing Python.

---

## Repo structure — each submission

The six submission repos follow an identical template. Example
for RouteForge:

```
shipsafe-routeforge/
├── README.md                          # public face (universal framing)
├── LICENSE                            # MIT
├── CLAUDE.md                          # RouteForge-specific local guidance
├── pyproject.toml                     # depends on shipsafe-shared via git
├── docs/
│   ├── ARCHITECTURE.md                # this submission's specifics
│   └── DEMO.md                        # how to run the demo
├── agent/                             # Python ADK agent brain
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── critic.py                      # subclasses shipsafe_shared.critic
│   ├── specialists/
│   │   ├── __init__.py
│   │   ├── commit_watcher.py
│   │   ├── scenario_tester.py
│   │   ├── code_context_analyzer.py
│   │   ├── risk_gate.py
│   │   └── changelog_writer.py
│   ├── webhooks.py                    # GitLab webhook handler
│   └── config.py
├── dashboard/                         # Next.js 14
│   ├── package.json
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── components/
│   └── tailwind.config.ts             # extends shipsafe-shared/design preset
├── cli/                               # npx @shipsafe/routeforge entry
│   ├── package.json
│   └── src/
│       ├── index.ts
│       ├── init.ts                    # uses shipsafe-shared/cli_core
│       ├── demo.ts
│       └── connect.ts
├── terraform/                         # Cloud Run deployment
│   ├── main.tf
│   └── variables.tf
├── tests/
│   ├── test_orchestrator.py
│   ├── test_specialists/
│   └── fixtures/
└── .github/
    └── workflows/
        └── ci.yml
```

The six submission repos are NOT created on Day 1. They exist as
empty GitHub repos but the code/structure gets built per the
PHASES.md schedule (RouteForge Day 3, AgentOps Day 4, etc.).

---

## Python package configuration

Inside `shipsafe-shared/`, the `pyproject.toml` declares the
package:

```toml
[project]
name = "shipsafe-shared"
version = "0.1.0a1"
description = "Shared instrumentation, demo data, and Critic primitives for the ShipSafe agent ecosystem"
license = { text = "MIT" }
requires-python = ">=3.12"
authors = [{ name = "ShipSafe", email = "shipsafe@example.com" }]

dependencies = [
    "google-adk>=0.1.0",
    "openinference-instrumentation-google-adk",
    "arize-phoenix-otel",
    "opentelemetry-exporter-otlp-proto-http",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio",
    "ruff",
    "mypy",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["shipsafe_shared"]
```

After this exists, in a fresh terminal inside `shipsafe-shared/`:

```bash
pip install -e ".[dev]"
```

That installs the package in editable mode, so changes to
`shipsafe_shared/` are immediately visible to anything importing
it.

---

## How submission repos depend on shipsafe-shared

Each submission's `pyproject.toml` declares the dependency via
git, pinned to a tag:

```toml
dependencies = [
    "shipsafe-shared @ git+https://github.com/shipsafe-ai/shipsafe-shared.git@v0.1.0",
    "google-adk>=0.1.0",
    # ... other deps
]
```

For local development with both repos checked out, use editable
install pointing at the local clone:

```bash
cd ~/dev/shipsafe/shipsafe-routeforge
pip install -e ../shipsafe-shared
pip install -e ".[dev]"
```

This makes RouteForge see changes to `shipsafe-shared` immediately
without re-publishing.

---

## Day 2 smoke test (the critical one)

After Day 2's build of `shipsafe_shared.instrumentation`, the
smoke test that gates Phase 1 start:

```python
# scripts/smoke_test_instrumentation.py
from shipsafe_shared.instrumentation import init_telemetry
from google.adk.agents import LlmAgent

# Init telemetry — fans out to both Phoenix and Dynatrace
init_telemetry(project_name="smoke-test")

# Hello-world ADK agent
agent = LlmAgent(name="smoke", model="gemini-1.5-pro")
result = agent.run("What is 2+2?")
print(result)
```

Run it with both `PHOENIX_API_KEY` and `DT_ENVIRONMENT` set as
env vars (plus the Dynatrace OTLP token). Then verify within 30
seconds:

- Open Phoenix Cloud → "smoke-test" project → see the trace
- Open Dynatrace → recent traces → see the same trace

If only Phoenix sees the trace, one of the four Dynatrace silent
fails is hitting. Diagnostic order (see PARTNER-INTEGRATION.md §6
for full details):

1. `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf` (NOT gRPC default)
2. Endpoint has no signal suffix (`/api/v2/otlp`, not `/v1/traces`)
3. Token scope is `openTelemetryTrace.ingest`
4. `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=delta`

Do NOT start Phase 1 (RouteForge build on Day 3) until this smoke
test passes cleanly. The instrumentation is load-bearing for every
submission.

---

## Working with Claude Code across multiple repos

Each of the seven repos has its own `CLAUDE.md` at the root.
Claude Code reads the local one. When you start Claude Code,
`cd` into the specific repo first:

```bash
cd ~/dev/shipsafe/shipsafe-routeforge
claude              # starts Claude Code with shipsafe-routeforge/CLAUDE.md as context
```

Don't run Claude Code from `~/dev/shipsafe/` (the parent
directory) — it will be confused about which repo's rules apply.

The canonical CLAUDE.md lives in `shipsafe-shared/`. Per-repo
CLAUDE.md files re-state the 9 cross-cutting rules verbatim
(so Claude Code in each repo sees them without external fetch)
and add submission-specific rules and the specialist roster.

When the canonical rules change (rarely after Phase 0), update
all seven files. A simple bash script in `shipsafe-shared/scripts/`
can sync the cross-cutting section if you set one up.

---

## Secret Manager setup

All credentials go in GCP Secret Manager (CLAUDE.md Rule 5).
Never in `.env` files, never in code, never in the agent config.
The setup pattern, done once per credential during the partner
account creation steps:

```bash
# Example for MongoDB Atlas URI
echo -n "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true" | \
    gcloud secrets create MONGODB_ATLAS_URI \
        --data-file=- \
        --replication-policy=automatic

# Verify
gcloud secrets versions access latest --secret=MONGODB_ATLAS_URI
```

Each agent's Cloud Run service is granted `roles/secretmanager.
secretAccessor` on the specific secrets it needs. The grant
happens via Terraform during the agent's deploy.

The credentials needed across the 13 days, in approximate creation
order (PHASES.md tracks the exact day each is created):

| Secret | Used by | Created |
|---|---|---|
| `MONGODB_ATLAS_URI` | CargoDB | Day 1 |
| `VOYAGE_API_KEY` | CargoDB (MCP auto-embed) | Day 1 |
| `PHOENIX_API_KEY` | All 6 (shared instrumentation) | Day 1 |
| `FIVETRAN_APIKEY` + `FIVETRAN_APISECRET` | TideSync | Day 1 (no sync yet!) |
| `GCP_PROJECT_ID` | All 6 (Cloud Run deploys) | Day 1 |
| `GITLAB_PAT` | RouteForge (REST API) | Day 3 |
| `GITLAB_WEBHOOK_SECRET` | RouteForge (webhook auth) | Day 3 |
| `GITLAB_MCP_OAUTH_TOKEN` | RouteForge (MCP) | Day 3 (after OAuth setup) |
| `DT_ENVIRONMENT` + `DT_OTLP_TOKEN` | All 6 (shared instrumentation) | Day 4 |
| `DT_PLATFORM_TOKEN` | AgentOps (DQL queries) | Day 4 |
| `ELASTIC_CLOUD_URL` + `ELASTIC_API_KEY` | VoyageBlack | Day 6 |
| `ELASTIC_MCP_URL` | VoyageBlack | Day 6 |
| `ARIZE_API_KEY` + `ARIZE_SPACE_KEY` | NaviGuard | Day 8 |

---

## Common dev commands

Inside any submission repo:

```bash
# Run tests
pytest                                 # all tests
pytest tests/test_orchestrator.py      # specific file
pytest -k "memory_recall"              # by name pattern

# Type check
mypy agent/

# Lint
ruff check agent/
ruff format agent/

# Run the agent locally (against demo data)
python -m agent.orchestrator

# Run the dashboard locally
cd dashboard && pnpm dev

# Run the CLI locally (without npm publish)
cd cli && pnpm dev init
```

Inside `shipsafe-shared/`:

```bash
# Run shared layer tests
pytest

# Smoke test instrumentation (the critical Day 2 gate)
python scripts/smoke_test_instrumentation.py

# Sync canonical CLAUDE.md across all 7 repos (after rule changes)
bash scripts/sync_claude_md.sh
```

---

## When something goes wrong

A reverse-engineered troubleshooting tree for the most common
Phase 0-1 failure modes:

**"My agent's traces don't appear in Dynatrace."**
→ Run the Day 2 smoke test diagnostic order above. 90% of the
time it's one of the four silent fails.

**"My ADK agent calls Gemini but I get an auth error."**
→ `gcloud auth application-default login` again. The credentials
expire periodically.

**"shipsafe-shared isn't importable in my submission repo."**
→ Check that you ran `pip install -e ../shipsafe-shared` from
inside the submission repo. The relative path is required.

**"Vector Search index creation fails silently in CargoDB."**
→ The `MDB_MCP_PREVIEW_FEATURES=search` env var isn't set on the
MCP server. See PARTNER-INTEGRATION.md §1 GAP.

**"RouteForge's MCP OAuth flow hangs during `init`."**
→ Browser callback URL isn't reachable. Fall back to the REST-only
path documented in PARTNER-INTEGRATION.md §2.

**"My Cloud Run deploy succeeded but the service returns 503."**
→ Cold start; wait 10s and retry. If persistent, check the service
logs: `gcloud run services logs read <service-name> --region=us-central1`.

For partner-specific gotchas not listed here, see
PARTNER-INTEGRATION.md — each section has a "GAP" subsection
documenting the known failure modes.

---

## What "done" looks like on Day 2

You're ready to start Phase 1 (Day 3 RouteForge build) when:

- [ ] `shipsafe-shared` repo has the full structure populated
- [ ] All 7 canonical docs are committed and pushed
- [ ] `pip install -e .` succeeds from inside `shipsafe-shared/`
- [ ] `shipsafe_shared.instrumentation.init_telemetry()` runs without error
- [ ] Hello-world ADK agent emits traces to BOTH Phoenix Cloud AND Dynatrace
- [ ] Both UIs (Phoenix and Dynatrace) show the trace within 30 seconds
- [ ] All 7 GitHub repos have CLAUDE.md at the root
- [ ] All 6 partner accounts that have no trial clock are created
- [ ] GCP credits requested
- [ ] OGC 2026 registered
- [ ] `shipsafe-shared` tagged as `v0.1.0-alpha`

If any of these is incomplete by midnight Day 2, fix it before
starting Day 3. The shared layer is a multiplier for every phase
after; a broken foundation breaks all six builds.
