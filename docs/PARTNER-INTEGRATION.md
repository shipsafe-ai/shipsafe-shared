# PARTNER-INTEGRATION.md — Verified integration paths per track

This is the source of truth for HOW each agent connects to its
partner. Every path below was verified against the partner's actual
documentation and source repos (not memory). Where a partner's
primary tool is deprecated, or where the obvious integration won't
deliver the agent's value proposition, it is flagged as a GAP with
the fix. Read the relevant section before building that agent.

Last verified: 2026-05-28 against the live partner docs.

---

## Conventions used below

- **Endpoint**: the exact MCP server / API the agent connects to.
- **Auth**: credentials needed and where they go (always Secret Manager).
- **Tools**: the operations the agent actually gets.
- **Runtime**: confirmed code-owned Python ADK on Cloud Run for all six.
- **GAP**: a place the naive integration fails; with the fix.
- **Feature**: the high-impact addition the docs unlock.

All agent brains are Python (ADK). All instrumentation is the shared
Python OTel/OpenInference layer in packages/instrumentation. Dashboards
and CLI are TS/Node. Gemini model comes from config, never hardcoded.

---

## The cross-cutting backbone: one instrumentation layer, two readers

Arize and Dynatrace want the SAME thing in different destinations:
instrument the agents with OpenTelemetry, export traces, then query
them back via an MCP server.

  Arize:     OpenInference (OTel-compatible) → Phoenix → Phoenix MCP
  Dynatrace: OpenTelemetry                   → Dynatrace → Dynatrace MCP

So packages/instrumentation is built ONCE in Phase 0 and emits an OTel
span stream that fans out to both Phoenix and Dynatrace. NaviGuard reads
Phoenix for AI-quality introspection; AgentOps reads Dynatrace for
operational health. Same telemetry, two angles. This is the technical
backbone of the Option C "watches the watchers" capstone — and it is a
strong technical-implementation story for two judges at once.

Build order implication: the instrumentation layer is a Phase 0
deliverable, before RouteForge/AgentOps in Phase 1.

---

## 1. CargoDB → MongoDB Atlas Vector Search

### Quickstart spine

Three official docs, read end-to-end before building:

1. `mongodb.com/docs/mcp-server/get-started/` — MCP server install + config
2. `mongodb.com/docs/mcp-server/tools/` — exact tool catalog (verified below)
3. `mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/` — index syntax + `$vectorSearch` stage

Optional warm-up dataset: `sample_mflix.embedded_movies` ships
with pre-built embeddings — useful for sanity-checking the
Vector Search wiring without burning Voyage AI credits. Load via
Atlas UI → "Load Sample Dataset". Once CargoDB's own pipeline
works against Mflix, swap to the Hormuz fixtures.

### Trial accounts

Atlas free tier (M0) shared cluster — sufficient for the hackathon
demo, no clock, no credit card required. Sign up Day 1; cluster
provisioning takes ~3 minutes.

Voyage AI API key obtained separately from `docs.voyageai.com`
(MongoDB acquired Voyage AI; the key is now MongoDB-provided AI
per hackathon rules). Free tier gives plenty of embedding calls
for the demo.

### Architecture (verified)

```
   ┌──────────────────────────────────────────┐
   │           CargoDB ADK agent              │
   │  (Cloud Run, Python, Gemini via Vertex)  │
   └─────────────────┬────────────────────────┘
                     │ MCP (stdio or HTTP)
                     ▼
   ┌──────────────────────────────────────────┐
   │       MongoDB MCP Server                 │
   │  - Auto-embed via Voyage AI (server-side)│
   │  - Wraps Atlas Data API + Admin API      │
   └─────────────────┬────────────────────────┘
                     │ Atlas SRV URI
                     ▼
   ┌──────────────────────────────────────────┐
   │  MongoDB Atlas (M0 free tier)            │
   │  - cargodb_memory database               │
   │  - decisions collection                  │
   │  - Vector Search index on `embedding`    │
   └──────────────────────────────────────────┘
```

### Layer 1 — Atlas cluster setup

- [ ] Atlas account at `cloud.mongodb.com/cloud/atlas/register`
- [ ] M0 free shared cluster, GCP region (closest to your Cloud Run
      region for latency, matching submission story)
- [ ] Database `cargodb_memory`, collection `decisions`
- [ ] Database user with `readWrite` on cargodb_memory
- [ ] Network access: temporarily 0.0.0.0/0 during dev,
      tighten to Cloud Run egress IP range for deploy
- [ ] SRV URI looks like: `mongodb+srv://<user>:<pass>@<cluster>.mongodb.net`

### Layer 2 — Voyage AI embedding setup

The MongoDB MCP Server auto-generates embeddings client-side when
configured with a Voyage AI API key. This means CargoDB never writes
embedding code — just calls `insert-many` with text and MCP handles
the embedding generation.

- [ ] Voyage AI account, API key
- [ ] Choose model — `voyage-3.5-lite` is the right default for
      operational decision text (fast, cheap, accurate enough for
      similarity recall). Use `voyage-3-large` only if quality
      becomes a bottleneck.

**Auth (Secret Manager):**
- `MONGODB_ATLAS_URI` — SRV URI
- `VOYAGE_API_KEY` — for the MCP server's auto-embedding
- `MDB_MCP_PREVIEW_FEATURES=search` — REQUIRED FLAG for vector search

The full list of Voyage models the MCP supports:
`voyage-3-large`, `voyage-3.5`, `voyage-3.5-lite`, `voyage-code-3`

### GAP — Vector Search is a preview feature

The MCP Server's vector search support is PREVIEW. Without the
`MDB_MCP_PREVIEW_FEATURES=search` env var (or the `previewFeatures`
config flag), the vector search tools simply aren't exposed. This
is a silent failure mode — the MCP starts fine, just without the
tools we depend on.

Verify the flag is set early. Quickest sanity check: run a
`create-index` natural-language prompt against the MCP from Claude
Code, ask for a vector search index. If MCP refuses, the flag isn't
set. (See "MongoDB Automated Embedding" below for the alternative
server-side path — but it requires Community Edition v8.2+ and is
also preview, so MCP client-side via Voyage is the cleaner path.)

### Layer 3 — Vector Search index (the one-time setup)

Created via the MCP `create-index` tool with a natural-language
prompt to Gemini, but the underlying JSON is worth knowing:

```json
{
  "name": "decisions_vector_idx",
  "type": "vectorSearch",
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1024,
      "similarity": "cosine"
    },
    { "type": "filter", "path": "decision_type" },
    { "type": "filter", "path": "timestamp" }
  ]
}
```

`voyage-3.5-lite` produces 1024-dim vectors. Filter fields enable
hybrid queries ("similar decisions, last 30 days, decision_type =
routing"). Create once during `init`; CargoDB then writes documents
and queries through the MCP without further index work.

### Layer 4 — The MCP tool catalog (verified, exhaustive)

The MongoDB MCP Server exposes THREE tool categories. CargoDB uses
subsets of all three.

**Database tools (the workhorse):**
| Tool | CargoDB usage |
|---|---|
| `connect` | One-time at agent startup |
| `find` | Exact-match recall by ID/timestamp |
| **`aggregate`** | **Runs `$vectorSearch` pipelines — the semantic recall** |
| `count` | Dashboard metrics |
| **`insert-many`** | **Writes new decisions; AUTO-EMBEDS with Voyage AI key** |
| `create-index` | One-time vector index creation |
| `update-one` / `update-many` | Update decision outcomes |
| `delete-many` | Cleanup test data |
| `collection-indexes` | Verify vector index exists |
| `collection-schema` | Schema-drift detection (the "one feature") |
| `list-databases` / `list-collections` | Inventory |
| `export` | Demo data export to file |

**Atlas tools (admin):**
| Tool | CargoDB usage |
|---|---|
| `atlas-inspect-cluster` | Health check, demo storytelling |
| `atlas-get-performance-advisor` | Real performance recommendations |
| `atlas-list-alerts` | Surface Atlas alerts in dashboard |

`atlas-connect-cluster`, `atlas-create-db-user`, `atlas-create-access-list`
exist but require Atlas API credentials (separate from SRV URI).
For hackathon scope, the simpler SRV-URI-only path covers everything.

**Local Atlas tools**: Docker-based local deployments. Skip — we
use cloud Atlas for the demo.

### Layer 5 — The semantic recall query (the demo's heart)

A `$vectorSearch` pipeline run via the MCP `aggregate` tool. When
the MCP server has a Voyage AI key configured, it auto-embeds the
`queryText`:

```python
# CargoDB calls MCP aggregate with this pipeline.
# MCP server embeds queryText automatically.
pipeline = [
    {
        "$vectorSearch": {
            "index": "decisions_vector_idx",
            "path": "embedding",
            "queryText": "vessel rerouted due to security incident in Hormuz",
            "numCandidates": 50,
            "limit": 3,
            "filter": {"decision_type": "routing"}
        }
    },
    {
        "$project": {
            "decision": 1,
            "outcome": 1,
            "timestamp": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]
```

Returns the top-3 most similar past decisions with a similarity
score. "This matches the 2024 Red Sea incident, 89% similar" is
this query's output, rendered to the dashboard.

### Layer 6 — CargoDB agent specialists

| Specialist | Calls | Job |
|---|---|---|
| MemoryWriter | MCP `insert-many` | Persists every decision; MCP auto-embeds |
| MemoryRecall | MCP `aggregate` with `$vectorSearch` | The "have we seen this?" query |
| SchemaHarmonizer | MCP `collection-schema` + Gemini | Original schema-drift cap (ONE feature) |
| ManifestAuditor | MCP `find` + `aggregate` | Cargo manifest validation |
| MigrationGuardian | MCP `collection-indexes` + `explain` | Index-impact safety check |
| Critic | challenges the others + prompt-injection check | Adversarial review |

### GAP — Atlas Search vs Atlas Vector Search are different products

Both are listed on MongoDB's resources page; they solve different
problems:

- **Atlas Search** — Lucene-based keyword + relevance search.
  Use for "find decisions mentioning Hormuz" with BM25 scoring.
- **Atlas Vector Search** — semantic similarity via embeddings.
  Use for "find decisions semantically similar to this situation."

CargoDB uses Vector Search as the spine (the AI-aware capability).
Atlas Search could augment as a stretch feature (hybrid retrieval:
keyword + vector), but only if Phase 4 has slack. Default: Vector
Search alone is enough for the MongoDB judge's bonus on "memory
layer for agentic workloads."

### Feature (high impact) — three things to demo

**1. Auto-embedding via MCP.** CargoDB writes decisions with
plain text via `insert-many`; the MCP server transparently
generates Voyage AI embeddings and stores them with the document.
NO embedding code in CargoDB's repo. Shows deep integration with
MongoDB's full stack (MCP + Atlas + Voyage AI as one product).

**2. Semantic recall during the Hormuz demo.** As the crisis
unfolds, CargoDB writes its current decisions to Atlas. On the
next decision, MemoryRecall hits Vector Search and surfaces
"this resembles the 2024 Red Sea incident — 89% similar.
Outcome then: reroute via Cape of Good Hope, +18% transit time."
Real Vector Search, not a mocked string.

**3. Performance Advisor integration.** CargoDB surfaces Atlas's
own performance recommendations (`atlas-get-performance-advisor`)
in its dashboard — "Your decisions collection would benefit from
an index on decision_type. Apply now?" — and on operator approval,
applies the index via `create-index`. Real Atlas admin via MCP,
not just data plane.

### Standalone story (non-shipping)

Connect any team's MongoDB Atlas cluster; CargoDB gives the
connected agent semantic memory + recall over its own decision
history. Works for fraud agents ("have we seen this pattern?"),
recommendation agents ("similar past suggestions"), customer-
support agents ("did this customer hit this issue before?") —
anywhere an agent benefits from "have I seen this before?"

### Rule-compliance notes (explicit MongoDB partner directive)

The MongoDB Devpost resources page is unusually direct:
"You can also bring your own embedding model and dataset, as long
as the embedding model is one of MongoDB-provided or
Google-provided models." This is a binding instruction:

- **Allowed**: Voyage AI (MongoDB-provided), Google Vertex AI
  embeddings (text-embedding-005, etc.)
- **Forbidden**: OpenAI embeddings, Cohere, any other provider —
  even if the rest of the agent uses Gemini

Default for CargoDB: Voyage AI via the MCP's built-in auto-embed.
Alternative: Google embeddings via Vertex AI, called directly from
the agent code (bypasses the MCP's auto-embed path, more boilerplate).

Voyage AI is allowed on the MongoDB track because MongoDB acquired
Voyage AI. Do NOT use Voyage AI in any other submission's repo —
the other submissions are not on the MongoDB track, so Voyage AI
is not a partner-provided AI for them. They must use Google
embeddings or their own partner's embedding (ELSER for VoyageBlack).

### Design decision — each submission stands alone

The earlier plan had VoyageBlack and NaviGuard calling CargoDB's
`/memory/similar` HTTP endpoint for cross-fleet similarity recall.
That is REVERSED (see CLAUDE.md Rule 8 — Cross-Submission Isolation).
Each submission uses its own partner as its memory layer:

- CargoDB → MongoDB Atlas Vector Search (this section)
- VoyageBlack → Elasticsearch semantic_text + ELSER (see §3)
- NaviGuard → Phoenix traces + datasets (see §5)

The cross-fleet narrative is conveyed through AgentOps OBSERVATION
of all six agents, not through HTTP dependencies between
submissions.

### Phase 2 prep — three things to do before CargoDB build starts

Not blocking other work; do before Day 5:

1. **Sign up for Voyage AI** at `docs.voyageai.com` and generate
   API key (free tier is plenty for the demo)
2. **Load Sample Mflix** into the Atlas cluster as a sanity-check
   warm-up dataset — confirms Vector Search works before you write
   any agent code
3. **Read the `$vectorSearch` aggregation stage docs** —
   `mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/`
   — to internalize numCandidates vs limit, filter syntax, score
   projection. Most live-build debugging on Day 5 will be here.



---

## 2. RouteForge → GitLab MCP server

### Quickstart spine

There is no single reference repo for "code-owned external agent
consuming GitLab MCP" — most GitLab MCP docs assume an interactive
AI client (Cursor, Claude Desktop, Gemini CLI). Our use case (a
Cloud Run service-side agent reacting to MR webhooks) is novel
enough that we are the reference architecture. Read these three
docs end-to-end before building:

1. `docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/` — MCP server config + OAuth
2. `docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server_tools/` — exact tool catalog
3. `docs.gitlab.com/user/duo_agent_platform/agents/custom/` — to know what NOT to use (see GAP below)

### Trial accounts

30-day GitLab Ultimate trial at `about.gitlab.com/free-trial/`, no
access code required. Includes Duo Agent Platform with 24 credits
per user. The 30-day clock starts on signup, so don't sign up
until Phase 1 Day 3 — that puts the clock end past the hackathon
deadline and into early OGC time.

The MCP server requires Premium or Ultimate tier (Ultimate trial
satisfies this), and you must turn on GitLab Duo plus "beta and
experimental features" in the trial instance after signup.

### GAP — Custom Agents are NOT what we want

GitLab's "Custom Agents" (GA, in the Duo Agent Platform) are
configured via the GitLab UI (system prompt + tool dropdown), run
on Duo's infrastructure with Duo's LLM, and are accessed via Duo
Chat. They consume the 24 trial credits.

**This contradicts every hackathon rule we have**: Gemini-only
LLM, code-owned runtime, Cloud Run deployment, shared
instrumentation layer. If you build RouteForge as a Custom Agent
you forfeit Vertex AI, lose your Phoenix/Dynatrace tracing, and
the Arize track gets disqualified.

Same reasoning excludes Custom Flows (Beta) — they are GitLab-side
multi-step orchestrations using Duo's LLM.

**Correct architecture**: RouteForge is an EXTERNAL agent. Python
ADK on Cloud Run, Gemini via Vertex AI, instrumented through our
shared OTel layer. It connects to GitLab MCP as a CLIENT. GitLab's
trial gives us the MCP endpoint and tools; we provide everything else.

### Architecture (verified)

```
   GitLab project
     ┌──────────────┐
     │   MR event   │
     └──────┬───────┘
            │ webhook (shared secret auth)
            ▼
   ┌──────────────────────┐
   │  RouteForge Cloud Run│
   │  (Python ADK agent)  │
   └──────────────────────┘
       │              │
       │ MCP (OAuth)  │ REST API (PAT)
       ▼              ▼
   ┌──────────────────────┐
   │  GitLab MCP server   │
   │  api/v4/mcp          │
   │  + GitLab REST API   │
   └──────────────────────┘
```

Three distinct GitLab integration channels, each with its own
auth model:

| Channel | Direction | Auth | Used for |
|---|---|---|---|
| Webhook | GitLab → RouteForge | Shared secret | Trigger on MR events |
| MCP (OAuth) | RouteForge → GitLab | OAuth Dynamic Client Reg | AI-aware tools (semantic_code_search, etc.) |
| REST API | RouteForge → GitLab | PAT/Project Access Token | Workhorse reads/writes |

This dual MCP+REST design is deliberate. The MCP server is in Beta
and currently designed for interactive AI tools — the OAuth flow
is awkward for a server-side daemon. REST API with a Project Access
Token is the reliable workhorse. MCP is used WHERE IT UNIQUELY MATTERS
(semantic code search, instance-wide search) so we score on "deep
partner integration" without depending on MCP for everything.

### Layer 1 — MCP server endpoint

```
HTTP transport (recommended):
https://gitlab.com/api/v4/mcp

stdio transport (alternative, if HTTP blocked):
npx mcp-remote https://gitlab.com/api/v4/mcp
```

ADK supports HTTP-transport MCP toolsets directly. Use HTTP.

### Layer 2 — OAuth flow at setup time (the one-time dance)

The MCP server uses OAuth 2.0 Dynamic Client Registration. This
is designed for interactive clients with browsers — not Cloud Run
services. Pattern that works:

1. During `npx @shipsafe/routeforge init`, CLI prints an
   authorization URL and opens the browser
2. User authorizes the RouteForge OAuth client in GitLab
3. CLI receives the OAuth access token on a local callback
4. CLI stores the token in GCP Secret Manager as
   `GITLAB_MCP_OAUTH_TOKEN`
5. Cloud Run agent reads token from Secret Manager at startup,
   uses it as bearer auth for MCP calls

This is a one-time setup cost. Subsequent MR events use the stored
token, no re-auth. Same pattern that Cursor / Claude Code use,
adapted for a server deployment.

If the OAuth flow proves too brittle in time-boxed hackathon
conditions, fall back to REST-API-only for the demo. The MCP path
is a scoring bonus, not a hard requirement — the rules require
"deep MCP integration with the assigned partner" which we satisfy
via the workhorse paths and the unique MCP-only tools.

### Layer 3 — REST API auth (the reliable workhorse)

Project Access Token (PAT) from the demo project — scope `api` +
`write_repository`, expiration ~14 days. Store as `GITLAB_PAT` in
Secret Manager.

```python
import httpx
client = httpx.Client(
    base_url="https://gitlab.com/api/v4",
    headers={"PRIVATE-TOKEN": gitlab_pat},
)
```

PAT auth covers: read MR diffs, list commits, get pipeline status,
post MR comments, read project files. All the workhorse operations
RouteForge needs to actually do its job.

### Layer 4 — Webhook trigger (the entry point)

In the demo GitLab project, configure a webhook:
- URL: `https://routeforge-<hash>-uc.a.run.app/webhooks/gitlab`
- Trigger: Merge request events only
- Secret token: shared with RouteForge via Secret Manager as
  `GITLAB_WEBHOOK_SECRET`
- SSL verification: enabled

RouteForge verifies the `X-Gitlab-Token` header on every webhook,
rejects anything that doesn't match. This is the entry point — no
OAuth, no PAT, just a shared secret.

### Layer 5 — The MCP tool catalog (verified, exhaustive)

These are ALL the tools the GitLab MCP server exposes (as of GitLab
18.10). RouteForge uses a subset; the catalog is small enough to know
end-to-end:

| Tool | RouteForge usage |
|---|---|
| `get_mcp_server_version` | sanity check during init |
| `get_merge_request` | full MR metadata for context |
| `get_merge_request_diffs` | the actual code change — the core input |
| `get_merge_request_commits` | what changed and when |
| `get_merge_request_pipelines` | CI/CD status before verdict |
| `get_pipeline_jobs` | which jobs passed/failed |
| `manage_pipeline` | retry failed jobs after fix recommendation |
| `create_workitem_note` | POST THE VERDICT COMMENT (workhorse) |
| `get_workitem_notes` | check for prior reviewer comments |
| `search` | "have we seen similar MRs before?" — instance-wide |
| `search_labels` | match severity labels by project conventions |
| **`semantic_code_search`** | **the differentiator — vector search over code** |
| `create_issue` / `get_issue` | follow-up issue creation on block verdict |
| `create_merge_request` | not used by RouteForge |

The standout is `semantic_code_search`. It's GitLab's built-in
vector search over a project's code (powered by their own
embeddings, allowed under partner-provided AI rule). When
RouteForge sees a routing-algorithm MR, semantic_code_search can
find: "where else is this function called?", "what other code
follows this pattern?", "are there past incidents related to
similar changes?". This is the AI-native capability you can't get
from REST API alone — it's the reason MCP integration matters.

### Layer 6 — Agent specialists

| Specialist | Calls | Job |
|---|---|---|
| CommitWatcher | webhook + `get_merge_request` + `get_merge_request_commits` | Parse MR context |
| ScenarioTester | code execution sandbox + Hormuz fixtures | Run crisis scenarios against the changed algorithm |
| CodeContextAnalyzer | `semantic_code_search` + `get_merge_request_diffs` | "Where else does this matter?" |
| RiskGate | Gemini reasoning over above | Pass/Block verdict + confidence |
| ChangelogWriter | Gemini synthesis | Verdict comment body |
| Critic | challenges the above + prompt-injection check | Adversarial review |

Output flow: human approval gate → `create_workitem_note` posts
the verdict comment on the MR. NEVER auto-post.

### GAP — Prompt injection from MR diffs

GitLab's MCP docs warn explicitly, on every page: "You're
responsible for guarding against prompt injection when you use
these tools. Exercise extreme caution or use MCP tools only on
GitLab objects you trust."

This is real for RouteForge. An attacker who can open a merge
request can inject prompts into the diff to manipulate the
verdict. Mitigations:

- All diff content passed to Gemini as data, not as instructions
  (use Vertex AI structured output, never freeform interpretation)
- Critic agent specifically checks: "Did this diff contain
  prompt-injection patterns? Does the verdict appear influenced
  by content suspiciously aimed at the reviewing agent?"
- Hard rule in the agent: verdict comment NEVER auto-posts. Human
  approval gate is mandatory. The CLI/dashboard shows the verdict,
  human clicks "post" or "override".
- Don't run untrusted diff content through any shell or code path
  beyond Gemini's structured input.

### Default Duo namespace (the resources-page footnote)

The Devpost resources page noted: "external tools using MCP must
set a default Duo namespace." This is a per-user GitLab UI
preference (Profile → Preferences → set default Duo namespace).
For RouteForge:

- The user setting up RouteForge must set their default Duo
  namespace to the demo project's top-level group
- This is verified during `npx @shipsafe/routeforge init` — the
  CLI checks the user's namespace setting via the REST API and
  warns if unset

### Feature (high impact) — three things to demo

**1. Real MR-triggered verdict.** Demo opens with an actual MR
on a routing-algorithm file. Webhook fires, RouteForge runs, the
dashboard shows live chain-of-thought, operator approves verdict,
comment lands on the actual MR. Native to the dev workflow.

**2. Semantic code search for context.** RouteForge doesn't just
read the diff — it asks "where else does this pattern appear?"
via semantic_code_search and synthesizes "this change affects
three other call sites that I checked." Shows the AI-aware
capability that's unique to MCP.

**3. Crisis scenario testing.** ScenarioTester runs the changed
algorithm against the Hormuz Crisis fixtures from shipsafe-shared.
Demo line: "The change improves throughput by 12% — but blocks
all routing through the Strait during Hormuz Crisis. Block."

### Standalone story (non-shipping)

Any GitLab project with critical business logic — fraud detection
algorithms, ranking models, pricing engines, claims-routing
logic. RouteForge gates changes to that logic against scenario
tests before they reach production. Financial Services: trade-
execution algorithm changes. Retail: dynamic-pricing logic.
Healthcare: claims-routing rules.

### Rule-compliance notes

- GitLab Duo's built-in AI features (semantic_code_search) are
  partner-provided AI → allowed on the GitLab track
- Do NOT use GitHub anywhere in RouteForge's repo (competing
  service)
- Do NOT use Duo Chat / Custom Agents (would force Duo's LLM
  which is not Gemini)
- The 24 Duo credits are NOT consumed by MCP server calls — those
  go through the OAuth-authenticated API, not the Duo Chat path

### Phase 1 prep — three things to do before RouteForge build starts

Not blocking other work; do before Day 3:

1. **Start GitLab Ultimate trial** at `about.gitlab.com/free-trial/`
   on Day 3 morning (clock starts on signup; 30 days = past
   submission deadline + buffer)
2. **Turn on GitLab Duo + beta features** in trial instance
3. **Create demo GitLab project** with a placeholder "routing
   algorithm" file, configure the webhook with placeholder URL
   (will be replaced with RouteForge's Cloud Run URL after deploy)



---

## 3. VoyageBlack → Elastic (Agent Builder MCP endpoint)

### Quickstart spine

Two reference repos worth cloning patterns from, neither perfectly
applicable to us:

- `elastic/elasticsearch-labs` — official notebooks including the
  agentic reference architecture, Gemini vector search, Gemini QA.
- The Agent Builder reference architecture blog post — uses
  LangChain + LangGraph + OpenAI GPT-5.2. **Do not follow the LLM
  or orchestration choice** (rules violation — see GAP below) but
  the data + MCP wiring pattern is exactly what we need.

### Trial accounts

Elastic Cloud free trial at `cloud.elastic.co/registration`,
**Serverless project, region selectable on Google Cloud**. Trial
duration is finite — start in Phase 2 Day 6, not Day 1. Elastic
on Google Cloud Marketplace is the same product through a
different billing path.

### GAP — Use Agent Builder MCP endpoint, NOT the deprecated standalone

The standalone `elastic/mcp-server-elasticsearch` server is
DEPRECATED (critical security fixes only). It has been superseded
by the Agent Builder MCP endpoint, which is the recommended path
for Elasticsearch 9.2+ deployments and Serverless projects, offering
full access to built-in and custom tools. Do NOT build on the old
server. Most search results and tutorials reference it — they're
out of date.

### Architecture (verified from official reference architecture)

Elasticsearch is the spine of VoyageBlack's stack: it stores the
log/trace data AND serves as the agent's own memory layer for
past postmortems AND exposes the MCP server. One product, three
roles.

```
                    ┌─────────────────────┐
   Ingest ─────────▶│  Elasticsearch      │
   (Hormuz fixtures)│  - Logs indices     │
                    │  - Postmortem index │
                    │  - ELSER embeddings │◀──┐
                    │  - MCP server       │   │ semantic_text
                    └──────────┬──────────┘   │ auto-embedding
                               │              │
                    Tools defined in          │
                    Agent Builder UI ─────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  MCP endpoint       │◀── VoyageBlack ADK
                    └─────────────────────┘    agent connects here
```

### Layer 1 — Elastic Cloud + Agent Builder setup

- [ ] Elastic Cloud Serverless project on GCP region
- [ ] Enable Agent Builder in Kibana UI
      (`elastic.co/docs/solutions/search/agent-builder/get-started`)
- [ ] Built-in tools available immediately; no extra config needed
      for first MCP connection

### Layer 2 — Data ingest with auto-embeddings (the ELSER pattern)

The reference architecture's key pattern is `semantic_text` field
type with `copy_to` from the fields you want searchable. ELSER
(Elastic's built-in semantic model) auto-generates embeddings on
ingest — no separate embedding pipeline.

Hormuz crisis log fixtures get loaded once:

```python
# Index mapping (the pattern, not exact code)
mappings = {
    "properties": {
        "timestamp": {"type": "date"},
        "message": {"type": "text", "copy_to": "semantic_field"},
        "service": {"type": "keyword", "copy_to": "semantic_field"},
        "level": {"type": "keyword"},
        "semantic_field": {"type": "semantic_text"},
    }
}
```

Now `semantic_field` is searchable with natural language — ELSER
embeddings happen automatically on ingest, no model code in the
agent. This is what makes Elastic-as-memory work for VoyageBlack
without us building an embedding pipeline.

### Layer 3 — Tools defined in Agent Builder UI

Tools are defined via the Kibana Agent Builder UI (or the tools
API). Two tool types:

- **ES|QL tools** — wrap an ES|QL query; agent calls with parameters.
- **Semantic search tools** — wrap a semantic_text search; agent
  passes natural-language queries.

Tools you'll define for VoyageBlack:

| Tool name | Type | Purpose |
|---|---|---|
| `incident_logs_timewindow` | ES|QL | Logs in time window with filters |
| `incident_logs_semantic` | Semantic | "Anything about Hormuz" |
| `service_error_correlation` | ES|QL | Aggregations across services |
| `similar_past_incident` | Semantic | Search past postmortems index |
| `write_postmortem` | ES|QL/index | Store finalized postmortem |

Best practices: `elastic.co/docs/solutions/search/agent-builder/tools`.

### Layer 4 — MCP server endpoint exposure

In Kibana → Agent Builder → Tools → click "Manage MCP" dropdown →
"Copy MCP Server URL". This is the URL VoyageBlack's ADK agent
imports as an MCP toolset client.

**Auth (Secret Manager):**
- `ELASTIC_CLOUD_URL` — the project URL
- `ELASTIC_MCP_URL` — the MCP server URL from Manage MCP
- `ELASTIC_API_KEY` — must include `feature_agentBuilder.read`
  Kibana application privilege or the agent gets 403 Forbidden

The API key role descriptor pattern:

```json
POST /_security/api_key
{
  "name": "voyageblack-mcp",
  "expiration": "30d",
  "role_descriptors": {
    "mcp-access": {
      "cluster": ["monitor_inference"],
      "indices": [
        { "names": ["logs-*", "postmortems-*"],
          "privileges": ["read", "view_index_metadata"] }
      ],
      "applications": [
        { "application": "kibana-.kibana",
          "privileges": ["feature_agentBuilder.read", "feature_actions.read"],
          "resources": ["*"] }
      ]
    }
  }
}
```

Principle of least privilege — only the indices VoyageBlack needs.

### GAP — Rule-compliant orchestration (the reference architecture violates rules)

Elastic's reference architecture uses LangChain MCP client +
LangGraph orchestration + OpenAI GPT-5.2. ALL THREE are wrong for
this hackathon:

| Reference architecture | What we use |
|---|---|
| LangChain MCP client | ADK native MCPToolset |
| LangGraph orchestration | ADK SequentialAgent / orchestrator |
| OpenAI GPT-5.2 | Gemini on Vertex AI |

The data + MCP wiring (semantic_text, ELSER, tools-via-UI, MCP
endpoint) carries over verbatim. The agent code does not. Translate
on the fly; do not let "the reference architecture uses X" drift
into our codebase.

### Layer 5 — VoyageBlack agent specialists (workflow pattern)

The reference architecture's workflow translates to ADK orchestrator
+ five specialists + critic:

| Reference function | VoyageBlack specialist | Tool(s) called |
|---|---|---|
| `call_agent_builder_semantic_search` | TimelineBuilder | `incident_logs_timewindow`, `incident_logs_semantic` |
| (correlation across sources) | CorrelationEngine | `service_error_correlation` |
| (severity assessment) | ImpactCalculator | ES|QL aggregations |
| `generate_response` | RootCauseAnalyzer | Gemini reasoning over above |
| (similarity recall + storage) | ReportWriter | `similar_past_incident`, `write_postmortem` |
| critic agent | Critic | challenges the others |

The `similar_past_incident` tool is what makes Elastic the memory
layer for VoyageBlack — it queries past postmortems stored in
Elasticsearch with semantic_text. No cross-submission HTTP call to
CargoDB; each submission stands on its own partner's stack.

### A2A protocol is ALSO available (do not use)

The same MCP server URL can be transformed for A2A protocol — same
URL with `/a2a` instead of `/mcp` ending. A2A (Agent-to-Agent) is
an alternative protocol for orchestrating multiple agents. **We do
not use A2A** — MCP is the hackathon-required protocol per the
rules and our other submissions. Stay on MCP.

### ELSER and Elastic Inference Service are rule-compliant

Hackathon rules permit "built-in AI-powered features within the
specific Partner's products relevant to your chosen track." ELSER
(Elastic's semantic model) and Elastic Inference Service (model
catalog) are Elastic's built-in AI — allowed on the Elastic track
specifically. Do NOT use them in any other submission's repo
(CargoDB/RouteForge/etc.) — competing-services clause.

### Feature (high impact) — Elastic-as-memory for VoyageBlack alone

The earlier design had VoyageBlack calling CargoDB's
`/memory/similar` HTTP endpoint for past-incident recall. That is
NOT what we do. Each submission stands alone with its partner's
stack:

- VoyageBlack stores past postmortems in its own Elasticsearch
  `postmortems-*` index with `semantic_text` field
- "This resembles the 2024 Red Sea incident, 89% match" is a
  semantic search over THAT index, not an HTTP call to CargoDB
- Cross-submission narrative (the full fleet) is conveyed via
  AgentOps observation, not via inter-submission code dependencies

Why: the Elastic judge should see VoyageBlack's submission run
without ANY non-Elastic infrastructure being live. Code dependency
on CargoDB (which uses MongoDB) is a competing-services risk and a
substantially-different-submission risk.

### Standalone story (non-shipping)

Any Elasticsearch cluster, any application's logs/traces.
VoyageBlack turns a raw incident window into a written postmortem,
correlates it to past similar incidents, and stores its own outputs
back to Elasticsearch as enriched memory. Works for any team that
ingests logs to Elastic — Financial Services fraud incidents,
World Cup logistics incidents, retail outage postmortems.

### Phase 2 prep — three docs to fetch before VoyageBlack build starts

Not blocking other work; read before Day 6:

1. **Agent Builder Get Started** —
   `elastic.co/docs/solutions/search/agent-builder/get-started`
   How to enable Agent Builder in a Serverless project.
2. **Tools documentation** —
   `elastic.co/docs/solutions/search/agent-builder/tools`
   Tool-definition best practices, ES|QL vs semantic search trade-offs.
3. **MCP server doc** —
   `elastic.co/docs/solutions/search/agent-builder/mcp-server`
   API key application privileges (the 403 trap), MCP client
   configuration examples.



---

## 4. TideSync → Fivetran

### Quickstart spine

`github.com/fivetran/fivetran-mcp` — official Python MCP server,
50+ tools, MIT licensed. Fork and extend it as the official docs
suggest. The README is the source of truth on tool list and env
vars; do not assume tools from memory.

Also reference for REST-API code patterns:
- `github.com/fivetran/api_framework` — official Python examples
- See the `atlas(method, endpoint, payload)` helper pattern for
  flat REST calls when MCP is overkill

### Trial accounts and the clock trick

Fivetran free trial is **14 days**, but the clock starts **on
first incremental sync, not on signup**. This is significant:
sign up Day 1, configure connection during Phase 0, and only
trigger the first incremental sync on Day 7 when TideSync's build
begins. That puts the full hackathon (and a multi-day post-
submission buffer) inside the 14-day window. Don't trigger
"sync now" on the demo connector before Day 7.

Trial mechanics:
- Unlimited connections per source during the trial
- One 14-day trial per connection
- Unlimited destinations during the trial

### Layer 1 — Auth (verified pattern)

API key + secret pair from `fivetran.com/dashboard/user/api-config`.
Two valid auth formats, identical behavior:

```python
# Bearer pattern
headers = {"Authorization": f"Bearer {api_key}:{api_secret}"}

# HTTPBasicAuth pattern
auth = HTTPBasicAuth(api_key, api_secret)
```

**Auth (Secret Manager):**
- `FIVETRAN_APIKEY` — from the dashboard
- `FIVETRAN_APISECRET` — from the dashboard
- `FIVETRAN_ALLOW_WRITES` — keep `false` unless a demo step
  needs a write (the MCP gates mutations behind this flag)

Same credentials work for BOTH the MCP server and direct REST
calls. Mix freely.

### Layer 2 — The Fivetran MCP server (control plane)

Tools available (50+; representative subset that matters to TideSync):

| Category | Tools | Used by |
|---|---|---|
| Connection inventory | `list_connections`, `get_connection_details` | Sync Sentinel |
| Sync triggers | `sync_connection`, `resync_connection` | Recovery Agent |
| Health checks | `run_connection_setup_tests` | Sync Sentinel |
| Schema config | `get_connection_schema_config`, `modify_connection_table_config` | Data Doctor |
| Webhooks | `list_webhooks`, `create_account_webhook`, `test_webhook` | reactive freshness check |
| Transformations | `list_transformations`, `run_transformation` | Recovery Agent |

ALL operate at PIPELINE level (control plane). None can answer
"is the data in the destination actually fresh and correct?"

### Layer 3 — BigQuery as the destination + second source (the demo's heart)

The Fivetran MCP cannot tell you data is stale because that lives
in the destination. TideSync queries BigQuery directly as a
second source. Gemini reasons across both:

```
Fivetran MCP says:    "Sync succeeded at 09:14, 1.2M rows"
BigQuery query says:  "Newest record timestamp = 04:33,
                      max_lag = 4h 41m vs SLA 1h"
Gemini concludes:     "Silent staleness — connector reports
                      healthy but source feed is frozen"
```

That contradiction IS the demo. Without source B, TideSync only
restates what Fivetran's UI already shows.

### Layer 4 — BigQuery setup (verified two-service-account model)

Service accounts are separated:

1. **Fivetran's service account** writes data to BigQuery
   - Auto-generated by Fivetran during destination setup (SaaS deployment)
   - Granted: `BigQuery Data Owner` on the dataset, `Storage Object Admin` on staging bucket
   - We never touch this — Fivetran manages it

2. **TideSync's GCP service account** reads from BigQuery
   - Our own service account (same one running the Cloud Run agent)
   - Granted: `BigQuery Data Viewer` + `BigQuery Job User` on the dataset
   - This is what the Python agent uses to run staleness queries
   - Same GCP project, simple IAM, no cross-project complexity

Deployment model: **SaaS** (not Hybrid). Hybrid requires
Enterprise/Business Critical plan. SaaS works on the trial.

GCP-side advantage: Fivetran's network is configured with
Private Google Access, so Fivetran→BigQuery traffic is private
when both are on GCP. Mention this in the demo for a clean
"native GCP integration" beat.

### Layer 5 — TideSync agent specialists

Maps the five-specialist + Critic pattern onto the two-source
data flow:

| Specialist | Calls | Job |
|---|---|---|
| SyncSentinel | Fivetran MCP `list_connections`, `get_connection_details` | Pipeline health roll-up |
| DataDoctor | BigQuery direct queries (max timestamp, row count, null-rate) | Destination freshness |
| ImpactMapper | Gemini reasoning over both | Detects sync-OK-but-stale |
| RecoveryAgent | Fivetran MCP `resync_connection`, `run_connection_setup_tests` | Triggers remediation |
| BriefingAgent | Gemini synthesis | Morning briefing email |
| Critic | challenges the above | adversarial review |

### Feature (high impact) — Three things the two-source pattern unlocks

**Predictive SLA breach**: Sync Sentinel pulls past sync history
from Fivetran MCP, Data Doctor pulls past staleness timestamps
from BigQuery. Gemini projects a trendline: "at current degradation
rate, this connector breaches its 1h SLA in approximately 2h 15m."
Warning BEFORE breach, not after.

**Reactive webhook freshness check**: Fivetran can push webhook
events on sync completion. TideSync exposes a webhook receiver,
the receiver triggers an immediate BigQuery freshness query, and
if stale → posts the alert WITHIN SECONDS of sync completion.
Demo beat: "sync finished 12 seconds ago. Data already stale."

**Cost-aware sync recommendations**: Combining BigQuery query
patterns (which tables are read often) with Fivetran sync history
(which tables are synced often), Gemini recommends "table X is
synced hourly but read weekly — switch to daily, save $Y/month."

### Demo connector choice

For the hackathon demo, the cleanest source connector is **Google
Sheets** because:
- Setup is two clicks (OAuth to a Google account)
- We control the source — we can freeze it mid-demo to simulate
  staleness deliberately
- No external API rate-limit or auth complexity
- Demo narrative: "ShipSafe's Hormuz port arrival sheet stops
  updating during the crisis; TideSync catches it instantly"

Alternatives: Google Drive (similar), a simple file source. NOT
a database connector — too much setup for hackathon time budget.

### Standalone story (non-shipping)

Any Fivetran account with any BigQuery destination. TideSync
catches the silent staleness failure that any analytics team
fears. Financial Services trade-data freshness, Retail inventory
sync correctness, World Cup ticket-sales pipeline trust — all
demo-able with the same agent against a different connector.

### Rule-compliance notes

- BigQuery is GCP — no competing-services risk
- Voyage AI, Gemini for any embedding or LLM call — never OpenAI
- Fivetran's "built-in transformations" (dbt models) are
  Fivetran-provided AI features → allowed on the Fivetran track
  but skip for hackathon scope; adds setup time without unique value

### Phase 3 prep — three things to do before TideSync build starts

Not blocking other work; do before Day 7:

1. **Fork `fivetran-mcp` to your GitHub** — gives you control to
   extend tools if needed. Don't extend until needed; the default
   tool set is enough for the demo.
2. **Set up the Google Sheet "Hormuz port arrivals"** as the
   demo source with timestamps you control — pre-populate with
   ~50 rows, leave the most recent timestamp manipulable for
   the demo's "freeze the source" beat.
3. **Read `fivetran.com/docs/destinations/bigquery/setup-guide`**
   end-to-end — Fivetran service account creation, IAM grants,
   destination configuration. The clock for Fivetran-side setup
   is the longest single setup step on Day 7.



---

## 5. NaviGuard → Arize Phoenix

**This track published its rubric. Build to it directly.**
Scored on: technical implementation, meaningful use of tracing and MCP,
quality of the agent's self-improvement loop, and overall impact.
Bonus points: agents that use their own observability data to improve
over time.

### Quickstart spine

Clone `github.com/Arize-ai/gemini-hackathon` as the starting skeleton. It
is a working Google ADK agent using `uv`, with OpenInference auto-
instrumentation, `phoenix.otel.register(auto_instrument=True)` shipping
traces to Phoenix Cloud, and `.gemini/settings.json` wiring
`@arizeai/phoenix-mcp`. Layout: `agent/main.py`, `agent/instrumentation.py`,
`agent/<demo>/` (root_agent, prompt, tools). Replace the shopping demo
with NaviGuard's logic.

### Trial accounts

Phoenix Cloud free tier at `app.phoenix.arize.com` — no clock, sign up
anytime. Self-host option is fully open source at
`github.com/Arize-ai/phoenix` if needed.

### Layer 1 — Instrumentation (Python, PyPI)

Three packages. Installed once into the shared
`packages/instrumentation` Python module, used by every agent so the
same OTel stream feeds both Phoenix (NaviGuard) and Dynatrace
(AgentOps):

```
pip install openinference-instrumentation-google-adk \
            google-adk \
            arize-phoenix-otel
```

Additional instrumentors when relevant:
- `openinference-instrumentation-vertexai` — for direct Vertex/Gemini
  calls outside ADK (e.g. evaluator judge LLM)
- `openinference-instrumentation-google-genai` — for the unified
  `google-genai` SDK

These are Python-only. Confirms agent brains MUST be Python.

**Setup call (the only line you write):**

```python
from phoenix.otel import register

tracer_provider = register(
    project_name="naviguard",
    auto_instrument=True,  # auto-detects every installed OI package
)
```

That's it. On Cloud Run, this works as-is. (If we ever switch to Vertex
AI Agent Engine, additional flags are needed — see "Cloud Run vs Agent
Engine" gap below.)

### Layer 2 — Trace destination

Phoenix Cloud, at the user's project. Traces stream in real time,
organized by `project_name`.

**Auth (Secret Manager):**
- `PHOENIX_API_KEY` — issued at `app.phoenix.arize.com`
- `PHOENIX_COLLECTOR_ENDPOINT` — the workspace's collector URL,
  shaped like `https://app.phoenix.arize.com/s/<handle>/v1/traces`
- `GOOGLE_API_KEY` or Vertex ADC — for Gemini access

### Layer 3 — Introspection via the Phoenix MCP server

`@arizeai/phoenix-mcp` is the runtime MCP server, invoked via npx:

```bash
npx -y @arizeai/phoenix-mcp@latest \
    --baseUrl https://app.phoenix.arize.com \
    --apiKey $PHOENIX_API_KEY
```

The Node-based server is launched by ADK as an MCP subprocess. The
agent attaches it as a TOOLSET. The full tool surface — straight from
the docs — gives the agent runtime access to:

- **Projects, Traces, and Spans** — explore recent traces, inspect
  spans, analyze annotations
- **Sessions** — review conversation flows and session annotations
- **Annotation Configs** — inspect labeling/scoring configs
- **Prompts Management** — create, list, update, iterate on prompts
- **Datasets** — explore datasets and synthesize new examples
- **Experiments** — pull experiment results and visualize them

Crucial: the agent can CREATE new prompts in Phoenix, not just read.
This is what closes the self-improvement loop — NaviGuard detects a
drift pattern and updates its own decision prompt as a versioned
Phoenix artifact.

### Layer 4 — Evaluation (the self-improvement loop)

Phoenix evals run via `phoenix.evals.ClassificationEvaluator`. The
agent exports its own recent spans, scores them with a custom
evaluator, reads the results back via Phoenix MCP, and adjusts its
next decision.

**Pattern (exact API):**

```python
from phoenix.client import Client
from phoenix.evals import ClassificationEvaluator, bind_evaluator
from phoenix.evals.llm import LLM

# 1. Export NaviGuard's own spans from the last window
client = Client()
spans_df = client.spans.get_spans_dataframe(project_identifier="naviguard")
verdict_spans = spans_df[spans_df['span_kind'] == 'AGENT']

# 2. Define a custom evaluator with NaviGuard-specific rubric
# (see "Custom evaluator template" below)
custom_evaluator = ClassificationEvaluator(
    name="verdict_correctness",
    llm=judge_llm,  # MUST be Gemini — see compliance gap below
    prompt_template=NAVIGUARD_VERDICT_TEMPLATE,
    choices={"correct": 1, "incorrect": 0},
)

# 3. Bind span attributes to evaluator inputs
bound = bind_evaluator(
    evaluator=custom_evaluator,
    input_mapping={
        "input": "attributes.input.value",
        "output": "attributes.output.value",
    },
)

# 4. Run; results land back in Phoenix as evaluator traces
# (meta-tracing — evals are themselves OTel-traced, queryable via MCP)
```

Evaluators are model-agnostic via adapters (OpenAI, LiteLLM, LangChain,
AI SDK). Rate-limit handling, retries, concurrency, and explanations
are built in — no need to write that infrastructure.

### Custom evaluator template (the rigid pattern that wins)

Phoenix's template structure is non-negotiable: judge role + explicit
CORRECT/INCORRECT rubric + `[BEGIN DATA] / [END DATA]` block + closing
question. Skeleton for NaviGuard's verdict evaluator:

```
You are an expert evaluator judging whether NaviGuard correctly
identified an AI quality regression. NaviGuard's job is to detect
when an AI model's outputs degrade compared to a baseline.

CORRECT - the verdict:
- Correctly flags confidence drops below the configured threshold
- Detects category-specific drift even when overall accuracy is stable
- Provides evidence (specific trace IDs, confidence deltas) the
  operator can verify
- Distinguishes genuine regression from baseline drift
- Confidence score reflects actual evidence strength

INCORRECT - the verdict contains any of:
- Missing category-specific regressions visible in the trace data
- Hallucinated evidence (referenced trace IDs that don't exist)
- Confidence score that contradicts the evidence presented
- Generic conclusions not tied to the specific spans analyzed
- Approves a model that the trace data shows is regressing

[BEGIN DATA]
[Recent trace summary]: {{input}}
[NaviGuard verdict]: {{output}}
[END DATA]

Is the verdict correct or incorrect?
```

### GAP — Hackathon rule compliance for the judge LLM

Every Phoenix evaluator example in the docs uses OpenAI:
`LLM(provider="openai", model="gpt-4o")`. Hackathon rules say "All
other artificial intelligence tools are not permitted" beyond Gemini
and partner-provided AI. **Using OpenAI as a judge LLM violates the
rules.**

**Fix**: every evaluator instantiates with Gemini as judge. Phoenix is
"model agnostic via adapters" — Gemini is reachable via LiteLLM or a
Vertex adapter. Exact configuration is in the "Customize Your LLM
Endpoint" tutorial (unfetched, see "Phase 3 prep" below). Treat the
OpenAI defaults in every Phoenix example as a trap to swap, not as
guidance to follow.

### GAP — Cloud Run vs Agent Engine

When deploying to Vertex AI Agent Engine, Vertex aggressively manages
the OTel global state and will shut down the Phoenix exporter mid-
deployment if you use the default global tracer provider.

We deploy to Cloud Run, so this does NOT apply. But if Phase 4 ever
upgrades NaviGuard to Agent Engine, switch to:
- `register(..., set_global_tracer_provider=False, batch=False)`
- Instrumentation lives in the agent module, not the main app
- `GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)`
  called explicitly

This confirms Cloud Run is the simpler instrumentation target.

### Phoenix Docs MCP — for BUILD time, not runtime

Arize publishes a SECOND MCP server: Phoenix Docs MCP, an HTTP
transport server that searches Phoenix documentation in real time.

Server URL: `https://arizeai-433a7140.mintlify.app/mcp`

Install once in Claude Code on day one:

```bash
claude mcp add --transport http phoenix-docs --scope user \
    https://arizeai-433a7140.mintlify.app/mcp
```

This is build-time only — NOT attached to NaviGuard at runtime. The
purpose is that when Claude Code is writing NaviGuard's code and hits
a Phoenix API question, it queries live docs instead of reasoning from
training data. Eliminates a class of mid-build errors.

### The closed-loop architecture, in three concrete artifacts

This is what gets scored under "quality of the self-improvement loop":

1. **At decision time** — NaviGuard calls Phoenix MCP to fetch recent
   similar verdicts and their evaluator scores. Context for the next
   decision comes from prior performance.

2. **Continuously** — a custom `ClassificationEvaluator` runs over
   NaviGuard's recent verdicts and flags categories where its
   confidence is miscalibrated.

3. **When drift is detected** — NaviGuard reads the eval findings via
   Phoenix MCP and updates its own decision prompt — a versioned
   Phoenix prompt artifact, queryable via MCP, modifiable via MCP.

Loop closes inside one Phoenix space. The phrase "self-improvement
loop" appears in the rubric verbatim — use the same words in the
Devpost description.

### Standalone story (non-shipping)

Any Arize/Phoenix-traced model. NaviGuard is an AI quality gate that
learns from its own trace history — works for any ADK or Vertex-based
agent regardless of domain.

### Contact and community

- Technical questions: **Richard Young, ryoung@arize.com**
- Hackathon Discord: `discord.gg/7Dqk5ebCD4`

### Phase 3 prep — three docs to fetch before NaviGuard build starts

Not blocking other work, but read before Phase 3 begins:

1. **Customize Your LLM Endpoint** — `arize.com/docs/phoenix/evaluation/tutorials/customize-your-llm-endpoint` —
   the exact Gemini-as-judge configuration (rule-compliance critical).
2. **Datasets & Experiments how-to** — `arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments` —
   programmatic experiment creation, so NaviGuard can run an
   experiment when it detects drift (strongest demo material).
3. **Agent-Assisted Tracing** — Arize ships a coding agent that adds
   tracing automatically; validates NaviGuard's instrumentation is
   complete.



---

## 6. AgentOps → Dynatrace

### Quickstart spine

**The reference repo is gold and almost copy-paste-ready**:
`github.com/dynatrace-oss/dynatrace-ai-agent-instrumentation-examples` —
official OTel exporter configs, sample dashboards, ready-to-run
patterns. Each subfolder is a different AI tool. The `claude-code`
subfolder has the exact env-var pattern Dynatrace expects; copy
that into our shared instrumentation layer.

For the MCP-side (query-back), two implementations exist:
- **Official**: `@dynatrace-oss/dynatrace-mcp-server` (npm, npx-runnable)
- **Community**: `@theharithsa/dynatrace-mcp-server` (npm, npx-runnable,
  has additional features like Davis CoPilot AI integration)

Use the official one. It's actively maintained (1.7.3+ as of fetch),
supports stdio and HTTP transport, and works with our ADK agent
via npx.

### Trial accounts

Dynatrace free trial at `dynatrace.com/signup`. Standard ~15-day
trial; start Day 4 morning (with AgentOps build) — clock ends past
the hackathon deadline.

Alternative path: one-click deployment from GCP Marketplace —
"Dynatrace for Gemini Enterprise" — which provisions a Dynatrace
environment tied to your GCP project. Faster than trial signup
but only relevant if we want the Gemini-Enterprise-specific
dashboards (we don't; we use raw Gemini via Vertex AI).

### Architecture (verified — the dual-channel design)

```
       ┌─────────────────────────────────────────┐
       │  All 6 agents (Cloud Run, Python ADK)   │
       │  ↓ shared/instrumentation                │
       └────────────────┬────────────────────────┘
                        │ OTel push (OTLP HTTP/protobuf)
                        │
              ┌─────────┼─────────────┐
              │         │             │
              ▼         ▼             ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ Phoenix  │ │Dynatrace │ │ Console  │
       │ Cloud    │ │ OTLP     │ │ (dev)    │
       │ (Arize)  │ │ ingest   │ │          │
       └──────────┘ └────┬─────┘ └──────────┘
                         │
                         │ Stored in Dynatrace Grail
                         │
                         │ DQL queries via MCP
                         ▼
                  ┌──────────────────┐
                  │ AgentOps ADK     │ ← capstone agent
                  │ agent on Cloud   │   queries fleet
                  │ Run (the 6th)    │   health & cascades
                  └──────────────────┘
```

This is the technical backbone of the Option C "watches the
watchers" capstone:
- **Push side**: every agent emits OTel telemetry. Same trace
  stream fans out to Phoenix (NaviGuard's domain) and Dynatrace
  (AgentOps' domain).
- **Pull side**: AgentOps queries Dynatrace via the Dynatrace MCP
  using DQL, reads its fleet's operational telemetry, generates
  insights and incident timelines.

### Layer 1 — OTel exporter env vars (verified, must be exact)

```bash
# Protocol — Dynatrace requires HTTP/protobuf, NOT gRPC (the OTel default)
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# Endpoint — base URL, no signal suffix
export OTEL_EXPORTER_OTLP_ENDPOINT=https://<env-id>.live.dynatrace.com/api/v2/otlp

# Auth — API token with openTelemetryTrace.ingest scope
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Api-Token <token>"

# Metrics — Dynatrace requires DELTA temporality (OTel default is cumulative)
export OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=delta
```

### GAP — Four configuration traps that fail silently

The OTLP push side has FOUR specific traps that all fail without
useful errors. Verify each one in `shipsafe-shared/instrumentation`:

1. **gRPC vs HTTP/protobuf**: OTel SDK defaults to gRPC. Dynatrace
   accepts only HTTP/protobuf. Symptom: exports succeed locally
   but never appear in Dynatrace.

2. **Endpoint suffix**: the env var should be the base URL
   `/api/v2/otlp` WITHOUT a signal suffix like `/v1/traces`. The
   SDK appends the suffix per signal. Including it manually → 404.

3. **API token scope**: must have `openTelemetryTrace.ingest`. The
   trial UI doesn't make this scope obvious. Without it, ingest
   returns 401 silently for traces (depends on token type).

4. **Delta temporality**: OTel defaults to cumulative. Dynatrace
   accepts cumulative but its dashboards expect delta. Without
   the env var, metrics ingest but counters look weird.

### GAP — Fifth trap: Phoenix's add_span_processor overwrites default

Phoenix's `_TracerProvider.add_span_processor()` shuts down its
existing processor before adding the new one. Adding Dynatrace's
`BatchSpanProcessor` via the default call path destroys Phoenix's
processor and adds DT to an already-shutdown multi-processor.
`force_flush()` returns True trivially but exports nothing.

Fix (in shipsafe_shared/instrumentation/telemetry.py): pass
`replace_default_processor=False` to Phoenix's `add_span_processor`.
This adds DT alongside Phoenix without shutdown. Falls back to plain
`add_span_processor()` via try/except TypeError for non-Phoenix providers.

### GAP — Dynatrace free trial does NOT include Grail trace storage

The free trial exposes the OTLP ingest endpoint and returns HTTP 200,
but trace data requires a licensed plan ("Custom Traces Classic" or
"FullStack" coverage). `fetch spans` DQL returns 0 records on trial.

Verified: HTTP 200, correct payload, correct token scopes.
Workaround for dev: accept HTTP 200 as smoke test pass.
For production/hackathon submission: use a cloud marketplace
Dynatrace deployment or request an extended trial with trace coverage.

### Layer 2 — Authentication (Secret Manager keys)

| Variable | Scope | Used by |
|---|---|---|
| `DT_ENVIRONMENT` | Environment URL | Push + MCP |
| `DT_OTLP_TOKEN` | `openTelemetryTrace.ingest` | OTel push (all 6 agents) |
| `DT_PLATFORM_TOKEN` | Platform token (DQL execute) | AgentOps MCP query side |

Two tokens because the scopes are different and you want least-
privilege. The OTel token is shared across all six agents (they
push to the same Dynatrace env). The platform token is AgentOps-
only (it does the queries).

### Layer 3 — Dynatrace MCP server (the query side)

Configuration:

```json
{
  "mcpServers": {
    "dynatrace": {
      "command": "npx",
      "args": ["-y", "@dynatrace-oss/dynatrace-mcp-server@latest"],
      "env": {
        "DT_ENVIRONMENT": "https://<env-id>.apps.dynatrace.com",
        "DT_PLATFORM_TOKEN": "<from-secret-manager>"
      },
      "timeout": 30000,
      "trust": false
    }
  }
}
```

Capabilities exposed via MCP:
- Execute DQL (Dynatrace Query Language) over Grail storage
- Retrieve logs, events, spans, metrics
- Query dashboards
- (Read about specific tools at the GitHub repo before Day 4 build)

### GAP — Grail query costs

The official Dynatrace MCP README warns: "using certain
capabilities to access data in Dynatrace Grail may incur
additional costs based on your Dynatrace consumption model.
This affects execute_dql tool and other capabilities that query
Dynatrace Grail storage, and costs depend on the volume (GB
scanned)."

Trial usage during the hackathon is unlikely to hit cost
ceilings — the data volume from 6 demo agents is small. But for
the universality story, document this so users connecting their
own production Dynatrace know about it. Suggest: AgentOps caches
common DQL queries (last 5 minutes) to reduce re-query volume.

### Layer 4 — Semantic conventions (OpenInference + OpenLLMetry)

Phoenix prefers OpenInference attributes; Dynatrace prefers
OpenLLMetry (now aligning with official OTel GenAI conventions).
Both are OTel-spec extensions — Dynatrace accepts any valid OTel
span, just with less-rich AI dashboards if attributes don't match
its expectations.

Strategy: shared instrumentation uses `openinference-instrumentation-google-adk`
(Arize's library) which emits OpenInference-spec spans. Dynatrace
ingests them as standard OTel and stores them in Grail; AgentOps
queries via DQL using OpenInference attribute names.

For polish: optionally emit dual conventions — add `gen_ai.*`
attributes (official OTel GenAI) alongside `openinference.*`
attributes. This makes Dynatrace's AI Observability dashboards
fully populate without sacrificing Phoenix integration. Stretch
item — not Day 4 blocker.

### Layer 5 — AgentOps agent specialists

| Specialist | Calls | Job |
|---|---|---|
| FleetWatcher | Dynatrace MCP `execute_dql` | Live health of all 6 agents |
| CascadeTracer | DQL over distributed traces | Identify cross-agent failure propagation |
| TokenAccountant | DQL over span attributes | Cost & token spend per agent/model/user |
| AnomalyScout | DQL + Gemini reasoning | "This latency spike is unusual" |
| IncidentNarrator | Gemini synthesis | Postmortem-style narrative across the fleet |
| Critic | challenges the above + prompt-injection check | Adversarial review |

### Feature (high impact) — three things to demo

**1. Live fleet observability during Hormuz crisis.** As the demo
unfolds, AgentOps shows live token-by-token activity of all five
other agents — what they're each doing right now, who's slow,
who's spending tokens. This is the single most visually dramatic
view in the portfolio: five agents working a crisis, observed in
real time by the sixth.

**2. Cascade-failure tracing.** When ScenarioTester (in RouteForge)
slows down, downstream agents that depend on its output (in the
demo, MemoryRecall in CargoDB queries while ScenarioTester
finishes) see latency spikes. AgentOps traces the cascade from
root cause to user impact in a single timeline view. Real
distributed tracing across submission boundaries.

**3. Cost & token accountability.** "RouteForge spent $0.23 on
this MR review; the semantic_code_search call was 47% of that
cost." Real attribution to specific agent decisions. This is what
makes the universality story credible to ops/finance audiences,
not just developers.

### Cross-submission isolation reminder (Rule 8 applies here too)

AgentOps is the ONE submission that legitimately observes the
others — but only through Dynatrace's OTel ingest (read-only
telemetry), never through HTTP calls to other submissions'
endpoints. The fleet narrative is conveyed through observation
of the shared OTel stream, not through code dependencies.

If AgentOps' submission runs in isolation (the other five
submissions are not deployed), it observes itself — and any
other AI agents the user has instrumented with the shared
instrumentation. The universality holds.

### Standalone story (non-shipping)

Monitors ANY AI agents on GCP Cloud Run, instrumented with
OpenTelemetry. The shared instrumentation package is open source;
any team can pip-install it, set the four env vars, and get
their agent fleet observed in Dynatrace. AgentOps' analysis
agents (FleetWatcher, CascadeTracer, etc.) work against any OTel
trace stream with AI-aware attributes.

Stretch universal angle: Dynatrace natively instruments Claude
Code, Gemini CLI, and Codex CLI with zero code changes (env vars
only). For non-shipping users, AgentOps credibly extends to
"monitor the coding agents that built your application" — real,
demonstrable. The reference repo shows the exact config; we
mention this in the AgentOps README without building it into the
demo.

### Rule-compliance notes

- Dynatrace OTLP ingest is partner-provided AI/observability →
  allowed on the Dynatrace track
- Davis CoPilot AI (Dynatrace's own AI) is allowed if used, but
  NOT used in our build — we use Gemini for all reasoning
- The shared instrumentation package can be reused across all 6
  submissions because it doesn't bring any non-partner AI — it's
  just OTel SDK + OpenInference attributes. Each submission's
  partner ingests its own copy of the stream.

### Phase 1 prep — three things to do before AgentOps build starts

Not blocking other work; do before Day 4:

1. **Sign up for Dynatrace trial** at `dynatrace.com/signup` Day 4
   morning (clock starts Day 4; ends past deadline). Pick a GCP
   region for the environment.
2. **Generate two API tokens** — one with `openTelemetryTrace.ingest`
   for the shared push, one platform token for AgentOps' DQL queries
3. **Clone reference repo** `dynatrace-oss/dynatrace-ai-agent-
   instrumentation-examples` and read the Claude Code subfolder
   end-to-end — its setup.sh becomes the template for our shared
   instrumentation env-var config



---

## Quick-reference matrix

| Agent | Partner | Connect via | Primary auth | The one gap to remember |
|---|---|---|---|---|
| CargoDB | MongoDB | Atlas MCP server + Voyage AI auto-embed | SRV URI + Voyage API key + `MDB_MCP_PREVIEW_FEATURES=search` | Vector Search is PREVIEW — silent fail without the flag; auto-embed eliminates embedding code |
| RouteForge | GitLab | MCP server (OAuth) + REST API (PAT) + Webhook (secret) | Three channels, three credentials | Custom Agents are NOT what we want; OAuth flow needs setup-time dance |
| VoyageBlack | Elastic | Agent Builder MCP endpoint (9.2+) | Cloud URL + API key with feature_agentBuilder.read | Each submission stands alone — Elastic IS the memory, no cross-call to CargoDB |
| TideSync | Fivetran | Fork fivetran-mcp + BigQuery direct queries | API key + secret + GCP svc acct | MCP = pipeline only; BigQuery for data truth; trial clock starts on first sync (not signup) |
| NaviGuard | Arize | OpenInference + Phoenix + Phoenix MCP (npx) | Phoenix API key + collector endpoint | Phoenix MCP as ADK toolset; judge LLM MUST be Gemini not OpenAI |
| AgentOps | Dynatrace | OTel push + Dynatrace MCP (DQL) | Env URL + 2 API tokens (ingest scope + platform token) | Four silent-fail traps: gRPC vs HTTP/protobuf, endpoint suffix, token scope, delta temporality |

---

## Trial-account staggering (don't start short clocks early)

| Account | Clock | When to create |
|---|---|---|
| GCP ($100 credits) | approval 1–5 days | TODAY (request immediately) |
| MongoDB Atlas | none (free tier) | anytime |
| Phoenix Cloud | none (free tier) | Phase 0/3 |
| Dynatrace | ~15-day trial | Day 4 morning (with AgentOps) |
| GitLab Ultimate | 30 days | Day 3 morning (clock past deadline) |
| Fivetran | 14 days, **clock starts on first sync** | Sign up Day 1; first incremental sync on Day 7 |
| Elastic Cloud | trial | Phase 2 (with VoyageBlack) |

---

## What changed from the pre-research plan (so nothing regresses)

**Status (as of this update): ALL SIX PARTNERS DEEP-RESEARCH VERIFIED.**
Every section is backed by a direct fetch of the partner's official
docs or repo. Refer to PARTNER-INTEGRATION.md as the single source of
truth for partner integration; do not pattern-match from memory.

- Agent brains are Python ADK, confirmed by Arize+Dynatrace Python-only
  instrumentation. Low-code Agent Builder is forbidden for agent logic.
- packages/instrumentation is a Phase 0 shared layer feeding Phoenix AND
  Dynatrace from one OTel stream.
- CargoDB re-aimed to MongoDB-as-memory + Vector Search; MCP
  auto-embeds via Voyage AI (zero embedding code in CargoDB repo).
- NaviGuard reframed around the self-improvement loop (rubric-driven),
  with Phoenix MCP as an ADK toolset.
- TideSync is a two-source agent (Fivetran MCP + BigQuery), not MCP alone.
  Trial clock starts on first incremental sync, not signup — sign up
  Day 1, start clock Day 7.
- VoyageBlack targets the Agent Builder MCP endpoint, not the deprecated
  standalone server.
- VoyageBlack uses Elasticsearch as its OWN memory layer (semantic_text +
  ELSER), confirmed by Elastic's reference architecture and the Devpost
  resources page now published.
- RouteForge is an EXTERNAL agent (Custom Agents are a trap — Duo's LLM
  forfeits Vertex AI Gemini). Three-channel auth: webhook + MCP OAuth +
  REST PAT.
- AgentOps push-side has FOUR silent-fail gotchas (gRPC vs HTTP/protobuf,
  endpoint suffix, token scope, delta temporality) — all flagged in
  shared instrumentation Day 2.
- AgentOps pull-side uses official `@dynatrace-oss/dynatrace-mcp-server`,
  NOT a community fork; queries Dynatrace Grail via DQL with cost
  awareness (5-min query cache).
- **Each submission stands alone — no cross-submission HTTP dependencies.**
  Earlier plan had VoyageBlack/NaviGuard calling CargoDB's /memory/similar
  endpoint. That is REVERSED. Every submission uses its own partner's
  memory layer. The fleet narrative is conveyed via AgentOps observation,
  not via inter-submission code dependencies.
- Reference architectures from partners often use non-compliant stacks
  (Elastic uses LangChain+LangGraph+OpenAI GPT-5.2; Phoenix examples
  default to OpenAI judge). Translate the data/MCP wiring; replace the
  orchestration and LLM with ADK+Gemini every time.
- Embedding model constraints are PER-TRACK. Voyage AI on CargoDB only
  (MongoDB-provided); ELSER on VoyageBlack only (Elastic-provided);
  semantic_code_search on RouteForge only (GitLab-provided); Google
  Vertex AI embeddings on tracks without a partner-provided embedding
  (TideSync). NEVER OpenAI/Cohere/etc. on any track.

