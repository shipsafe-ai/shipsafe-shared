# PHASES.md — ShipSafe Build Plan

13 days. 6 submissions. Go hard or go home.

This document supersedes every previous PHASES.md. Anything that
mentions NexCart, DevSafe, ShipGuard, SchemaSafe, PostMortem AI,
TrustPipe, PromptShield, or FleetWatch is the old plan and should
be ignored. This is the only build plan.

---

## The hard math

| Item | Value |
|---|---|
| Today | Thursday, May 29, 2026 |
| Deadline | Thursday, June 11, 2026 at 2:00 PM PT |
| Time until deadline (IST) | June 12, 2026 at 2:30 AM IST |
| Build days available | 13 (May 29 → June 10) |
| Day 14 (June 11) | Buffer until 2pm PT cutoff, no new work |
| Submissions required | 6 (one per partner track) |
| Days per submission | 2 (one pair every two days) |
| Polish + video days | 3 (Phase 4) |
| Iterate + submit days | 2 (Phase 5) |

Reality check: the original PHASES.md assumed a 36-day build from
May 7. Time has been spent on strategy and research, which the next
13 days will rely on heavily. We are not behind — we are running
to a compressed plan from a stronger starting position than most
entrants who began coding immediately.

---

## Architecture summary (read before any phase)

- **Domain**: ShipSafe maritime operations intelligence platform.
  Demo scenario is the Hormuz Crisis (scripted, deterministic,
  high-fidelity mock data). Every submission's universality
  claim must hold for other domains — World Cup logistics,
  financial services, retail — but the demo is maritime.

- **Six agents, six repos**: each submission is its own public
  GitHub repo with MIT license. A seventh `shipsafe-shared` repo
  holds cross-cutting utilities (instrumentation, demo data,
  design tokens, CLI core) installed as dependencies by the six.
  Never share a submission's repo URL across tracks.

- **Agent brains**: Python, Google ADK, deployed to Cloud Run.
  Same shape for all six. The ADK orchestrator runs 5 specialist
  agents + 1 Critic agent + human approval gate.

- **Dashboards**: Next.js 14, TypeScript, Tailwind, deployed to
  Cloud Run alongside the agent. Dark-only, mission-control style.

- **CLI**: Node, published as `@shipsafe/<agent>` to npm. One
  command (`npx @shipsafe/<agent> init`) deploys a working
  instance in under 3 minutes.

- **Shared instrumentation**: a single Python OTel + OpenInference
  layer in `shipsafe-shared`. Emits one trace stream that fans
  out to BOTH Phoenix Cloud (for NaviGuard) and Dynatrace (for
  AgentOps). Built once on Day 2, used by all six agents.

- **Rules compliance**: Gemini only (including judge LLMs in
  evaluators — Phoenix defaults to OpenAI, must be swapped). No
  competing partner services in any one submission's repo. All
  credentials in GCP Secret Manager. See CLAUDE.md rules and
  PARTNER-INTEGRATION.md per-partner specifics.

For per-partner technical details, see
`docs/PARTNER-INTEGRATION.md`. This file is operational; that
file is technical.

---

## Phase 0 — Foundation (Days 1–2, May 29–30)

Everything else depends on this. No agent work begins until
Phase 0 exits clean.

### Day 1 — Thursday, May 29 — Accounts, repos, credits

The credit and trial clocks start here. Several have hard
deadlines or take days to approve.

#### Immediate (do first)
- [ ] Submit $100 GCP credits form
      `forms.gle/xfv9vQzfRfNCCVbG7` (hard deadline June 4,
      approval takes 1–5 business days, do TODAY)
- [ ] Register for OGC 2026 at optichallenge.com
      (5 minutes, before June 7)
- [ ] Install Phoenix Docs MCP in Claude Code at user scope
      (command in CLAUDE.md "Day-one Claude Code setup")

#### GitHub setup
- [ ] Create public repo: `github.com/<you>/cargodb` + MIT license
- [ ] Create public repo: `github.com/<you>/routeforge` + MIT license
- [ ] Create public repo: `github.com/<you>/voyageblack` + MIT license
- [ ] Create public repo: `github.com/<you>/tidesync` + MIT license
- [ ] Create public repo: `github.com/<you>/naviguard` + MIT license
- [ ] Create public repo: `github.com/<you>/agentops` + MIT license
- [ ] Create public repo: `github.com/<you>/shipsafe-shared` + MIT license
- [ ] Every repo's About section shows MIT license visible (rule req)

#### GCP setup
- [ ] Create GCP project: `shipsafe-hackathon`
- [ ] Enable APIs: Vertex AI, Cloud Run, Secret Manager,
      Cloud Build, Artifact Registry, IAM
- [ ] Configure `gcloud` CLI locally, `gcloud auth login`
- [ ] Verify Vertex AI works: send one Gemini call from local Python

#### Partner accounts (no clocks yet — sign up but don't start trials)
- [ ] MongoDB Atlas free tier (no clock; create cluster now)
- [ ] Voyage AI account at `docs.voyageai.com`, generate API key,
      store as `VOYAGE_API_KEY` in Secret Manager (free tier; no clock)
- [ ] Phoenix Cloud free tier at app.phoenix.arize.com (no clock)
- [ ] Fivetran account at `fivetran.com/signup`
      **CRITICAL: do NOT trigger any incremental sync yet.**
      The 14-day clock starts on first sync, not signup. Configure
      the account, generate API key + secret, but leave any connector
      paused/unconfigured until Day 7.
- [ ] Generate Fivetran API key + secret from
      `fivetran.com/dashboard/user/api-config`, store in Secret Manager
- [ ] Create a Google Sheet "ShipSafe – Hormuz Port Arrivals" with
      ~50 rows of mock arrival timestamps. We will OAuth this as
      the Fivetran source on Day 7. Leave the most recent timestamp
      cells editable for the demo's freeze-the-source beat.
- [ ] Devpost account verified (will use for submissions)

#### Local dev environment
- [ ] Python 3.12 verified (`python --version`)
- [ ] Node 20+ verified, pnpm 9+ installed
- [ ] `gcloud`, `terraform`, `docker` installed
- [ ] Editor (Zed or Claude Code) opened on shipsafe-shared

### Day 1 exit criteria

- All 7 repos exist, public, MIT-licensed
- GCP project provisioned, Gemini call works
- GCP credits requested
- OGC 2026 registered
- Phoenix Docs MCP live in Claude Code

### Day 2 — Friday, May 30 — Shared infrastructure

The `shipsafe-shared` repo becomes the spine of the build. Every
agent depends on it. Build once, install everywhere.

#### Shared instrumentation layer (Python)
- [ ] `shipsafe_shared/instrumentation/__init__.py` with one
      `init_telemetry(project_name)` function
- [ ] Installs `openinference-instrumentation-google-adk`,
      `arize-phoenix-otel`, OTLP exporter for Dynatrace
- [ ] Calls `phoenix.otel.register(auto_instrument=True)` if
      `PHOENIX_API_KEY` env is set
- [ ] Configures OTLP exporter to Dynatrace if
      `DT_ENVIRONMENT` env is set, using the four required env vars:
      - `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf` (NOT gRPC default)
      - `OTEL_EXPORTER_OTLP_ENDPOINT=<DT_ENVIRONMENT>/api/v2/otlp`
        (base URL, no signal suffix — SDK appends `/v1/traces` etc.)
      - `OTEL_EXPORTER_OTLP_HEADERS=Authorization=Api-Token <token>`
        (token must have `openTelemetryTrace.ingest` scope)
      - `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=delta`
        (Dynatrace requires delta; OTel default is cumulative)
- [ ] Both Phoenix and Dynatrace exporters fire from one OTel span
      stream — same code path, two destinations
- [ ] Smoke test: hello-world ADK agent emits traces. Verify in
      BOTH UIs that traces appear within 30s. **If only Phoenix
      sees the trace, one of the four Dynatrace gotchas is hitting
      — check protocol, endpoint, token scope, temporality in order.**

#### Shared demo data
- [ ] `shipsafe_shared/demo_data/vessels.json` — 5+ real vessels
      (IMO numbers from public record, e.g. MSC Gülsün, Ever Given,
      HMM Algeciras, Maersk Mc-Kinney Møller, Cosco Shipping Universe)
- [ ] `shipsafe_shared/demo_data/ports.json` — 6+ real ports with
      UN/LOCODE (Rotterdam, Shanghai, Jebel Ali, Singapore, Hamburg, Busan)
- [ ] `shipsafe_shared/demo_data/hormuz_crisis.py` — scripted
      scenario with timeline (14:55 advisory → 15:02 operator decision)
- [ ] Per-agent fixture loaders that draw from the same dataset

#### Shared design tokens (TypeScript)
- [ ] `shipsafe_shared/design/tokens.ts` — colors, spacing, fonts
- [ ] Six agent accent colors locked (per CLAUDE.md design system)
- [ ] Tailwind config preset all six dashboards extend

#### Shared CLI core (Node)
- [ ] `shipsafe_shared/cli_core/` — scaffolding for `init`,
      `demo`, `connect`, `status`, `logs`, `destroy` commands
- [ ] Cloud Run deployment helper (one function each agent calls)
- [ ] Secret Manager helper (read/write/list)
- [ ] Health check helper (wait for deployed service to respond)

#### Publish shared utilities
- [ ] Tag `v0.1.0` on shipsafe-shared
- [ ] Six agent repos pin to that tag as a git dependency
      (Python: `git+https://github.com/.../shipsafe-shared.git@v0.1.0`)
- [ ] Node side: published to npm OR same git-dep pattern

### Day 2 exit criteria

- shipsafe-shared at v0.1.0, public, importable from a fresh repo
- Hello-world ADK agent successfully emits traces to BOTH Phoenix
  Cloud and Dynatrace at the same time, verified in both UIs
- Demo data loads in a smoke test
- Six agent repos cloned locally, each with shipsafe-shared
  installed and verified by a one-line import test

If Day 2 doesn't exit clean by midnight, stop and fix it before
starting Phase 1. The shared layer is the multiplier for every
phase after. Broken foundation breaks all six builds.

---

## Phase 1 — RouteForge + AgentOps (Days 3–4, May 31–Jun 1)

The strongest pair, built first. RouteForge stands alone as the
GitLab submission. AgentOps observes RouteForge initially, then
the other four as they come online. Building these two first means
AgentOps gets the longest observation window across the fleet.

### Day 3 — Saturday, May 31 — RouteForge

Refer to PARTNER-INTEGRATION.md §2 for verified GitLab specifics.

#### GitLab-side setup (morning)
- [ ] Start GitLab Ultimate 30-day trial (clock starts now; 30 days
      past the hackathon deadline gives full buffer)
- [ ] Turn on GitLab Duo + beta/experimental features in trial
- [ ] Create demo project: `shipsafe-routing-engine`
- [ ] Seed it with a "routing algorithm" Python file
- [ ] Set default Duo namespace in profile preferences to the
      demo project's top-level group (required for MCP external tools)

#### Three credential channels (the verified pattern)
- [ ] Generate Project Access Token, scope `api` + `write_repository`,
      14-day expiration. Store as `GITLAB_PAT` in Secret Manager
      (REST API workhorse)
- [ ] Generate webhook shared secret (random 32-char), store as
      `GITLAB_WEBHOOK_SECRET` in Secret Manager
- [ ] OAuth setup-time flow during `init` will generate
      `GITLAB_MCP_OAUTH_TOKEN` (Day 4 work — needs Cloud Run URL first)
- [ ] Configure project webhook (placeholder URL for now):
      MR events only, secret token attached, SSL verification on

#### Verify integrations work
- [ ] REST API: `curl -H "PRIVATE-TOKEN: $GITLAB_PAT" https://gitlab.com/api/v4/projects/<id>/merge_requests`
- [ ] MCP via Claude Code from local terminal:
      `claude mcp add --transport http GitLab https://gitlab.com/api/v4/mcp`
      then verify `get_mcp_server_version` works through OAuth flow

#### Agent build
- [ ] `agent/orchestrator.py` — ADK SequentialAgent
- [ ] `agent/specialists/commit_watcher.py` (parses webhook payload,
      calls `get_merge_request` + `get_merge_request_commits`)
- [ ] `agent/specialists/scenario_tester.py` (runs Hormuz crisis
      scenarios against the changed algorithm)
- [ ] `agent/specialists/code_context_analyzer.py` (calls
      `semantic_code_search` via MCP — the AI-aware differentiator)
- [ ] `agent/specialists/risk_gate.py` (pass/block verdict + confidence)
- [ ] `agent/specialists/changelog_writer.py` (verdict comment body)
- [ ] `agent/critic.py` — challenges verdict AND checks for
      prompt injection patterns in the diff
- [ ] HTTP endpoint `/webhooks/gitlab` with `X-Gitlab-Token` verification
- [ ] Human approval gate — verdict NEVER auto-posts to MR

#### Dashboard
- [ ] Next.js 14 app on Cloud Run
- [ ] MR view with diff and verdict panel
- [ ] Live chain-of-thought stream from agent
- [ ] Scenario test results table
- [ ] Semantic-code-search results panel ("similar patterns
      elsewhere in this project")
- [ ] Verdict approval button → calls `create_workitem_note` via
      MCP (or REST API) to post the verdict comment on the MR

#### Deploy + package
- [ ] Cloud Run deployed
- [ ] Update GitLab webhook URL to the now-known Cloud Run URL
- [ ] Run OAuth setup flow to populate `GITLAB_MCP_OAUTH_TOKEN`
- [ ] README + universality (works for any GitLab project with
      critical business logic, regardless of domain)
- [ ] `npx @shipsafe/routeforge init` works end-to-end
- [ ] Test: open a real MR, see RouteForge run, see verdict
      comment land after human approval

### Day 4 — Sunday, Jun 1 — AgentOps

Refer to PARTNER-INTEGRATION.md §6 for verified Dynatrace specifics.

#### Trial + Dynatrace-side setup (morning)
- [ ] Start Dynatrace free trial at `dynatrace.com/signup`
      (clock starts now; ~15 days past hackathon deadline)
- [ ] Pick GCP region for the Dynatrace environment
- [ ] Note the environment URL pattern: `https://<env-id>.live.dynatrace.com`
      and apps URL: `https://<env-id>.apps.dynatrace.com`

#### Two credentials (Secret Manager)
- [ ] Generate API token with `openTelemetryTrace.ingest` scope.
      Store as `DT_OTLP_TOKEN`. This is the shared push token —
      all 6 agents use it
- [ ] Generate Platform Token (different from API tokens; created
      in the apps console). Store as `DT_PLATFORM_TOKEN`. This is
      AgentOps-only, used for DQL queries via the MCP
- [ ] Store environment URL as `DT_ENVIRONMENT`

#### Verify the four push-side gotchas (CRITICAL)
- [ ] Re-confirm `shipsafe-shared/instrumentation` from Day 2 sets
      all four env vars correctly (protocol, endpoint, headers, temporality)
- [ ] Verify RouteForge spans from yesterday's build are landing
      in Dynatrace UI. If only Phoenix sees them, diagnose by:
      1. Check `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`
      2. Check endpoint has no signal suffix
      3. Check token scope (must be `openTelemetryTrace.ingest`)
      4. Check `delta` temperature for metrics

#### Dynatrace MCP setup (the query side)
- [ ] Add `@dynatrace-oss/dynatrace-mcp-server@latest` via npx
      configuration in agent's MCP config
- [ ] Pass `DT_ENVIRONMENT` and `DT_PLATFORM_TOKEN` as MCP env vars
- [ ] Smoke test: agent queries DQL via MCP, gets recent spans
      from RouteForge (already running)

#### Agent build (the capstone specialists)
- [ ] `agent/orchestrator.py` — observes other ShipSafe agents
- [ ] `agent/specialists/fleet_watcher.py` — live health from DQL
      queries; reads spans from all 6 agents
- [ ] `agent/specialists/cascade_tracer.py` — DQL over distributed
      traces; identifies cross-agent failure propagation
- [ ] `agent/specialists/token_accountant.py` — DQL over span
      attributes for cost + token spend per agent/model
- [ ] `agent/specialists/anomaly_scout.py` — DQL + Gemini reasoning
      for "this latency spike is unusual"
- [ ] `agent/specialists/incident_narrator.py` — Gemini synthesis
      across fleet for postmortem-style narratives
- [ ] `agent/critic.py` — challenges + prompt-injection check

#### Dashboard (the showcase dashboard)
- [ ] Live activity feed showing all 6 ShipSafe agents
      (RouteForge for now, others added as they ship)
- [ ] Token-by-token streaming view per agent
- [ ] Cascade-failure trace visualization
- [ ] Token cost + latency tiles per agent
- [ ] Per-agent decision audit log
- [ ] DQL query caching (last 5 minutes) to avoid repeating
      Grail queries that may incur cost on production users' envs
- [ ] This is the most visually dramatic dashboard — invest in it

#### Deploy + package
- [ ] Cloud Run deployed
- [ ] README + universality (monitors ANY OTel-instrumented agent fleet)
- [ ] `npx @shipsafe/agentops init` works

### Phase 1 exit criteria

- RouteForge live, blocks/approves a real GitLab MR with
  visible chain-of-thought
- AgentOps live, observes RouteForge and itself in real time
- Both dashboards accessible by URL
- Both repos pushed, public, with MIT and ShipSafe footer

---

## Phase 2 — CargoDB + VoyageBlack (Days 5–6, Jun 2–3)

The data-layer pair. Each agent uses its own partner as its
memory layer — CargoDB uses Atlas Vector Search, VoyageBlack uses
Elasticsearch semantic_text + ELSER. No cross-submission HTTP
calls. Build order is CargoDB then VoyageBlack only because
CargoDB's design is more constrained by hackathon rules (Vector
Search demonstrated for the MongoDB judge).

### Day 5 — Monday, Jun 2 — CargoDB

Refer to PARTNER-INTEGRATION.md §1 for verified MongoDB specifics.

#### Atlas setup (verify, mostly done from Day 1)
- [ ] Atlas cluster from Day 1 still running
- [ ] Network access list includes Cloud Run egress range
- [ ] Database user with `readWrite` on `cargodb_memory`
- [ ] SRV URI stored as `MONGODB_ATLAS_URI` in Secret Manager

#### Voyage AI + MCP setup (THE preview-flag trap lives here)
- [ ] Voyage AI API key stored as `VOYAGE_API_KEY` in Secret Manager
- [ ] **Set `MDB_MCP_PREVIEW_FEATURES=search`** in MCP server env —
      WITHOUT THIS the vector search tools don't load; silent fail
- [ ] Choose embedding model: `voyage-3.5-lite` (1024-dim, cheap, fast)
- [ ] Smoke test from Claude Code: connect to MCP, ask
      "create a vector search index" — if MCP refuses, the preview
      flag isn't set

#### Vector Search index creation (one-time)
- [ ] Database `cargodb_memory`, collection `decisions`
- [ ] Vector search index `decisions_vector_idx` on `embedding` field,
      1024 dims, cosine similarity
- [ ] Filter fields: `decision_type`, `timestamp` (for hybrid queries)
- [ ] Verify via MCP `collection-indexes` tool

#### Optional sanity warm-up (recommended)
- [ ] Load `sample_mflix` dataset via Atlas UI
- [ ] Run a `$vectorSearch` against `sample_mflix.embedded_movies`
      via MCP `aggregate` to confirm wiring works
- [ ] Once Mflix recall works, drop and move to Hormuz fixtures

#### Agent build
- [ ] `agent/orchestrator.py` — ADK SequentialAgent
- [ ] `agent/specialists/memory_writer.py` — calls MCP `insert-many`
      with text fields; MCP server auto-embeds via Voyage API key
      (NO embedding code in CargoDB's repo)
- [ ] `agent/specialists/memory_recall.py` — calls MCP `aggregate`
      with `$vectorSearch` pipeline; MCP server auto-embeds queryText
- [ ] `agent/specialists/schema_harmonizer.py` — calls MCP
      `collection-schema` (the schema-drift capability, now ONE feature)
- [ ] `agent/specialists/manifest_auditor.py` — MCP `find` + `aggregate`
- [ ] `agent/specialists/migration_guardian.py` — MCP `explain` for
      index-impact safety
- [ ] `agent/critic.py` — challenges the above + prompt-injection check

No HTTP endpoint serving cross-submission memory (Rule 8). CargoDB's
Atlas Vector Search is demonstrated within CargoDB's own demo,
which is what the MongoDB judge needs to see.

#### Dashboard
- [ ] Schema drift visualization (panel for the "one feature")
- [ ] Vector similarity search UI (live, over CargoDB's own history)
- [ ] Memory browser — every decision CargoDB has written
- [ ] Migration safety panel
- [ ] Atlas Performance Advisor panel — calls
      `atlas-get-performance-advisor` via MCP, surfaces actionable
      index suggestions, one-click apply with operator approval

#### Deploy + package
- [ ] Cloud Run deployed
- [ ] Update Atlas network access to Cloud Run egress IP range
- [ ] README + universality (works for any team's MongoDB Atlas cluster)
- [ ] `npx @shipsafe/cargodb init` works

### Day 6 — Tuesday, Jun 3 — VoyageBlack

Refer to PARTNER-INTEGRATION.md §3 for verified Elastic specifics.
Before starting, fetch the 3 Phase 2 prep docs flagged in §3:
Agent Builder Get Started, Tools documentation, MCP server doc.

#### Trial + Elastic Cloud setup
- [ ] Start Elastic Cloud trial on Serverless project, GCP region
      (DO NOT use the deprecated standalone MCP server)
- [ ] Enable Agent Builder in Kibana UI
- [ ] Create API key with `feature_agentBuilder.read` + `feature_actions.read`
      Kibana application privileges (without these → 403 Forbidden)
- [ ] Store Elastic Cloud URL + API key in Secret Manager

#### Data ingest — semantic_text + ELSER (the key pattern)
- [ ] Create index `logs-hormuz-*` with `semantic_text` field
      using `copy_to` from message + service fields
- [ ] Create index `postmortems-shipsafe` for past postmortems
      (also with semantic_text — this is VoyageBlack's memory)
- [ ] Load Hormuz crisis log fixtures via bulk API
- [ ] Verify ELSER auto-embeds on ingest (no separate pipeline code)

#### Tools defined in Agent Builder UI
- [ ] `incident_logs_timewindow` — ES|QL tool, time-bounded
- [ ] `incident_logs_semantic` — semantic search tool
- [ ] `service_error_correlation` — ES|QL aggregations
- [ ] `similar_past_incident` — semantic search over postmortems index
- [ ] `write_postmortem` — index/upsert finalized postmortem
- [ ] Copy MCP Server URL from "Manage MCP" dropdown

#### Agent build
- [ ] `agent/orchestrator.py`
- [ ] `agent/specialists/timeline_builder.py` (calls timewindow + semantic)
- [ ] `agent/specialists/correlation_engine.py` (calls correlation tool)
- [ ] `agent/specialists/impact_calculator.py`
- [ ] `agent/specialists/root_cause_analyzer.py` (Gemini reasoning)
- [ ] `agent/specialists/report_writer.py` (calls similar_past_incident
      + write_postmortem — VoyageBlack's OWN memory loop)
- [ ] `agent/critic.py`

Translate Elastic's reference architecture (LangChain/LangGraph/OpenAI)
to ADK/Gemini on the fly. Same data wiring, compliant orchestration.

#### Dashboard
- [ ] Incident window selector
- [ ] Live timeline reconstruction
- [ ] Postmortem document generation
- [ ] Similar-incidents panel (powered by VoyageBlack's own
      postmortems index via semantic_text, NOT by CargoDB)

#### Deploy + package
- [ ] Cloud Run deployed
- [ ] README + universality (works for any Elastic cluster)
- [ ] `npx @shipsafe/voyageblack init` works

### Phase 2 exit criteria

- CargoDB live, Atlas Vector Search demonstrated over its own
  decision history (no HTTP memory service exposed)
- VoyageBlack live, producing real postmortems from real ES|QL
  queries, with semantic_text similarity recall over its own
  postmortems index (no dependency on CargoDB)
- Both submissions independently testable; either one running
  alone proves its own value to its judge
- AgentOps now observes 4 agents (auto, since they share the
  instrumentation layer)

---

## Phase 3 — TideSync + NaviGuard (Days 7–8, Jun 4–5)

Day 7 is Wednesday June 4 — **GCP credits hard deadline** for new
applicants. The request was filed Day 1; the approval window is
1–5 business days, so it should already be active. Verify before
the day starts.

### Day 7 — Wednesday, Jun 4 — TideSync

Refer to PARTNER-INTEGRATION.md §4 for verified Fivetran specifics.
**GCP credits hard deadline today** — verify approval landed.
Fivetran account is already created from Day 1 (clock hasn't
started — we did not trigger any sync yet).

#### Fivetran-side setup (the longest step today)
- [ ] In Fivetran dashboard: add destination → BigQuery (SaaS deployment)
- [ ] Copy the auto-generated Fivetran service account email
- [ ] In GCP IAM: grant that service account `BigQuery Data Owner`
      on the target dataset and `Storage Object Admin` on the
      staging bucket
- [ ] Add source connector: Google Sheets → OAuth to the
      "ShipSafe – Hormuz Port Arrivals" sheet prepared on Day 1
- [ ] Start the first incremental sync — **trial clock starts now,
      14-day window begins**
- [ ] Verify rows land in BigQuery `shipsafe_hormuz` dataset

#### GCP side — TideSync's own BigQuery read access
- [ ] Grant TideSync's Cloud Run service account `BigQuery Data Viewer`
      and `BigQuery Job User` on the `shipsafe_hormuz` dataset
- [ ] Smoke test from local Python: query `SELECT MAX(timestamp) FROM ...`
      using the Cloud Run service account's ADC

#### Fivetran MCP setup
- [ ] Fork `github.com/fivetran/fivetran-mcp` to your GitHub
      (one of the seven repos — depends on shipsafe-shared)
- [ ] Configure with FIVETRAN_APIKEY + FIVETRAN_APISECRET from
      Secret Manager (set FIVETRAN_ALLOW_WRITES=false initially)
- [ ] Smoke test: `list_connections` should return the Google Sheets connector

#### Agent build (specialists map to the two-source architecture)
- [ ] `agent/orchestrator.py`
- [ ] `agent/specialists/sync_sentinel.py` — calls Fivetran MCP for
      pipeline status, sync history
- [ ] `agent/specialists/data_doctor.py` — direct BigQuery queries
      for `MAX(timestamp)`, row counts, null-rate drift on
      `shipsafe_hormuz` tables
- [ ] `agent/specialists/impact_mapper.py` — Gemini reasoning over
      BOTH sources; detects "sync OK but data stale" contradiction
- [ ] `agent/specialists/recovery_agent.py` — calls Fivetran MCP
      `resync_connection` / `run_connection_setup_tests`
- [ ] `agent/specialists/briefing_agent.py` — morning briefing synthesis
- [ ] `agent/critic.py`
- [ ] Webhook receiver endpoint (`/webhooks/fivetran`) that triggers
      an immediate BigQuery freshness query on sync-complete events
- [ ] Register the webhook via Fivetran MCP `create_account_webhook`

#### Dashboard
- [ ] Connector health overview (from Fivetran MCP)
- [ ] Per-connector staleness indicators (from BigQuery queries)
- [ ] Two-source contradiction panel — the demo moment
- [ ] Predictive SLA breach panel — trendline projection
- [ ] Morning briefing preview

#### Demo prep
- [ ] Practice the freeze-the-source beat: edit the Google Sheet
      to stop adding new rows during a demo run, watch TideSync
      catch the staleness within seconds of the webhook firing

#### Deploy + package
- [ ] Cloud Run deployed
- [ ] README + universality (works for any Fivetran + BigQuery
      pipeline, regardless of domain)
- [ ] `npx @shipsafe/tidesync init` works

### Day 8 — Thursday, Jun 5 — NaviGuard

This is the rubric-critical submission. Arize published their
scoring criteria, and the self-improvement loop is the bonus-points
item. Spend this day well.

Before starting, fetch the 3 Phase 3 prep docs flagged in
PARTNER-INTEGRATION.md §5: Customize Your LLM Endpoint, Datasets
& Experiments how-to, Agent-Assisted Tracing.

#### Setup
- [ ] Phoenix Cloud account from Day 1 still active
- [ ] Phoenix API key + collector endpoint in Secret Manager
- [ ] Clone `Arize-ai/gemini-hackathon` repo as NaviGuard's spine
- [ ] Wire `@arizeai/phoenix-mcp` as an ADK toolset on the agent
      (not as a Gemini CLI sidecar — must close loop inside agent)

#### Agent build
- [ ] `agent/orchestrator.py`
- [ ] `agent/specialists/trace_harvester.py` — pulls own traces
      via Phoenix MCP at decision time
- [ ] `agent/specialists/baseline_profiler.py`
- [ ] `agent/specialists/challenger_evaluator.py`
- [ ] `agent/specialists/regression_hunter.py`
- [ ] `agent/specialists/quality_gate.py`
- [ ] `agent/critic.py`

#### The self-improvement loop (the rubric centerpiece)
- [ ] Custom `ClassificationEvaluator` with NaviGuard verdict
      template (CORRECT/INCORRECT rubric)
- [ ] Judge LLM = Gemini (NOT OpenAI — every Phoenix example
      defaults to OpenAI; this is the compliance trap)
- [ ] Evaluator runs on NaviGuard's own recent verdicts
- [ ] When drift detected: NaviGuard updates its own prompt
      as a Phoenix prompt artifact via Phoenix MCP
- [ ] Demo shows the loop closing visibly

#### Dashboard
- [ ] Regression heatmap by category
- [ ] Confidence drift over time
- [ ] Self-improvement visualization — show the loop running
- [ ] Prompt version history (read from Phoenix)

#### Deploy + package
- [ ] Cloud Run deployed
- [ ] README + universality (works for any Phoenix-traced model)
- [ ] `npx @shipsafe/naviguard init` works

### Phase 3 exit criteria

- All 6 agents deployed and accessible
- AgentOps observes all 5 other agents simultaneously
- The Hormuz Crisis demo can be run end-to-end across the fleet
- Every repo public with MIT license + ShipSafe footer

---

## Phase 4 — Polish, videos, drafts (Days 9–11, Jun 6–8)

Build is done. Now make six submissions actually look like
production-grade products. Rules allow updating submissions any
time before the deadline — file drafts early on Day 9 so the
automated Stage One screening can give signal as we iterate.

### Day 9 — Friday, Jun 6 — Devpost drafts + universality QA

#### Devpost draft for each of 6 submissions
- [ ] Create draft submission on Devpost for each track
- [ ] Title, tagline, technologies-used filled in
- [ ] Hosted URL pasted in (the Cloud Run dashboard URL)
- [ ] Repo URL pasted in (each agent's dedicated repo)
- [ ] Track selected from dropdown
- [ ] Saved as draft — no video yet, that's tomorrow

#### Universality QA (rules requirement)
- [ ] For each agent, write the README's non-shipping example
      in the first 3 sections (no maritime mentions)
- [ ] Pick from Devpost's suggested challenges: 2026 World Cup,
      Financial Services, Brick-and-Mortar Retail
- [ ] Each agent README references one of those concretely
- [ ] Run a manual smoke test: does it work if you connect a
      non-shipping data source? Document the result.

#### Repo compliance audit
- [ ] MIT license visible in About section of every repo
- [ ] No competing partner service in any repo's source
      (e.g. no Elastic refs in CargoDB repo, no MongoDB refs
      in VoyageBlack repo — competing services clause)
- [ ] No OpenAI/Anthropic refs anywhere in agent logic
- [ ] No hardcoded credentials anywhere; everything via
      Secret Manager

### Day 10 — Saturday, Jun 7 — Demo videos

**Reminder**: OGC 2026 registration deadline is today (June 7).
Confirm registration is complete.

#### Per agent (6 videos)
- [ ] Record a 3-minute crisis scenario demo, agent-specific
- [ ] Open with the universal problem (no shipping)
- [ ] Cut to the Hormuz Crisis as the concrete scenario
- [ ] Show the agent's chain-of-thought streaming live
- [ ] Show the human approval gate
- [ ] Close with the universality claim
- [ ] Upload to YouTube as unlisted
- [ ] Paste YouTube URL into the Devpost draft

#### Polish
- [ ] Dashboard visual review — fonts, colors, spacing
- [ ] Fix any broken hot reloads or 404s
- [ ] Verify every `npx @shipsafe/<agent> init` runs clean from
      a fresh shell

### Day 11 — Sunday, Jun 8 — Devpost descriptions

#### Per Devpost submission
- [ ] Write the description (features, technologies, what learned)
- [ ] Include the ShipSafe ecosystem footer subtly at the end
- [ ] Use the rubric language verbatim where applicable
      (especially for NaviGuard: "self-improvement loop")
- [ ] Image uploads if available (dashboard screenshots)
- [ ] Save submission (not yet submitted — still iterating)

### Phase 4 exit criteria

- 6 Devpost drafts saved with all fields filled
- 6 YouTube videos uploaded as unlisted, linked in drafts
- Repo compliance audit passed for all 6
- Universality QA passed for all 6

---

## Phase 5 — Iterate and submit (Days 12–13, Jun 9–10)

Two days to fix what's weakest and submit.

### Day 12 — Monday, Jun 9 — End-to-end QA

- [ ] Fresh-shell test: `npx @shipsafe/<agent> init` for all 6
- [ ] Demo videos play correctly on YouTube
- [ ] Every Devpost field complete on all 6 drafts
- [ ] Every repo accessible (public, MIT visible)
- [ ] Every hosted URL accessible to anonymous users (judges
      have no creds — they may judge based only on the video
      and description per rules, but the hosted URL must work
      if they try it)
- [ ] Identify weakest of the 6 — spend remaining day on it

### Day 13 — Tuesday, Jun 10 — Final fixes + submit

- [ ] Final iteration on the weakest submission from Day 12
- [ ] Re-record any video that doesn't show the agent functioning
- [ ] Click "Submit" on all 6 Devpost drafts by end of day
- [ ] Rules allow further updates until 2pm PT June 11, but the
      goal is to be submitted by end of Day 13 with Day 14 as
      pure safety margin

### Phase 5 exit criteria

- All 6 submissions submitted (not draft) on Devpost
- Confirmation emails received from Devpost for each

---

## Day 14 — Wednesday, June 11 — Buffer until 2pm PT

No new work. Only emergency fixes if something is broken.
Hard cutoff: **2:00 PM PT (2:30 AM IST June 12).**

- [ ] At 1:55pm PT, confirm all 6 submissions still show
      "submitted" status
- [ ] At 2:00pm PT, the Devpost window closes. Done.

After the deadline: shift to OGC 2026 algorithm development
(June 15 preliminary round opens).

---

## Risk register — what can go wrong, and what to do

| Risk | Likelihood | Mitigation |
|---|---|---|
| GCP credits not approved by Day 7 | Medium | Filed Day 1; pay out-of-pocket if needed for the small amounts hackathon use generates |
| One agent doesn't work end-to-end by Phase 4 | Medium-high | Phase 5 (Days 12–13) is buffered for exactly this; weakest submission gets the iteration time |
| Demo video fails to upload to YouTube | Low | Vimeo is allowed by rules as alternative |
| Phoenix evaluator wired with OpenAI judge by mistake | High | Flagged everywhere; PARTNER-INTEGRATION.md §5 GAP; CLAUDE.md Rule 1 |
| Elastic deprecated MCP used by mistake | Medium | PARTNER-INTEGRATION.md §3 flags Agent Builder MCP as the only correct endpoint |
| Fivetran MCP shows pipeline-OK but TideSync misses data staleness | High (this IS the demo) | PARTNER-INTEGRATION.md §4 mandates BigQuery as second source |
| Six-repo discipline breaks; competing partner deps leak between repos | Medium | Phase 4 Day 9 explicit audit step |
| OGC June 7 registration missed | Low | Day 1 task; Day 10 reminder |
| Time runs out, one submission is incomplete | Medium | Submit anything that runs — partial submission > no submission; rules allow updates until deadline |

---

## What this plan does NOT include (and why)

- **Marketing site / landing page**: judges don't see it. Time
  budget says no.
- **Custom branding videos**: rules require the demo show the
  agent functioning. A polished agent-functioning video beats a
  cinematic agent-not-functioning video.
- **Comprehensive test coverage**: TDD on the 3 specialists per
  agent that matter most. Don't aim for 85% coverage everywhere
  on this timeline — aim for working demos that don't break.
- **Beautiful CSS animations**: dark mission-control aesthetic
  comes from the design tokens already in shipsafe-shared.
  Don't hand-roll animations.
- **OGC 2026 work**: starts June 15, after the hackathon.
  Register before June 7, then put it down until June 12.

---

## Daily standup format (suggested, optional)

Each morning, before opening any code:

1. What does the checklist say I'm building today?
2. What's blocking me from starting? (Trial not activated?
   Credential missing? Doc not read?)
3. What's the smallest version of today's deliverable I can
   ship by end of day? (Floor, not ceiling.)
4. What's already on fire from yesterday that I should fix
   before adding new work?

13 days, 6 agents, one operator. The plan above is the plan.
Execute it.
