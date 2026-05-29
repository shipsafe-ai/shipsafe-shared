# CLAUDE.md — ShipSafe Ecosystem

Read this entire file before writing any code, creating any file,
or making any architectural decision. Everything is here.

Before building ANY partner integration, also read
docs/PARTNER-INTEGRATION.md — it has the exact verified endpoint,
auth, tools, quickstart repo, and gap-closing feature per track.
That file is the source of truth for integration specifics;
this file is the source of truth for architecture and rules.

## Day-one Claude Code setup (run before Phase 0 begins)

Install the Phoenix Docs MCP at user scope so every Claude Code
session has live access to Phoenix documentation while building.
This is build-time tooling, not runtime — it is NOT attached to
any agent.

    claude mcp add --transport http phoenix-docs --scope user \
        https://arizeai-433a7140.mintlify.app/mcp

Other partner docs MCPs will be added as their sections are reached.
This is a Phoenix-only step today.

---

## What is this project?

ShipSafe is an ecosystem of 6 AI agents built for the
Google Cloud Rapid Agent Hackathon. Each agent is an
independently deployable product that solves a specific
class of production problem. Together they form a complete
operations intelligence platform.

**The core insight:** Enterprise-grade AI operations has
always existed — but only for companies with full engineering
teams. ShipSafe makes the same capability available to any
team, deployable in 3 minutes with a single CLI command.

**Demo domain:** Maritime logistics (ShipSafe crisis scenarios)
**Universal applicability:** Every agent works for any domain.
The shipping context is the demo. Not the product.

---

## The 6 agents

| Agent | npm package | Partner | Standalone problem |
|---|---|---|---|
| CargoDB | @shipsafe/cargodb | MongoDB | Agent memory + semantic recall; schema conflicts as one feature |
| RouteForge | @shipsafe/routeforge | GitLab | Unsafe algorithm/code changes |
| VoyageBlack | @shipsafe/voyageblack | Elastic | Undocumented incidents |
| TideSync | @shipsafe/tidesync | Fivetran | Silent pipeline failures |
| NaviGuard | @shipsafe/naviguard | Arize | AI quality regressions + self-improvement loop |
| AgentOps | @shipsafe/agentops | Dynatrace | Agent fleet observability |

CargoDB re-aim (settled): MongoDB's hackathon framing leads hard
with Atlas Vector Search, Voyage AI embeddings, and Atlas as the
"persistent memory layer for agentic workloads." So CargoDB is the
shared MEMORY of the fleet — every agent's decisions/traces/context
stored in Atlas, with Vector Search powering "have we seen this
before?" semantic recall. The original schema-harmonization logic
stays as ONE feature, not the whole product. This makes CargoDB
genuine shared infrastructure (VoyageBlack & NaviGuard similarity
lookups are real Atlas Vector Search queries, not mocks).

---

## Non-negotiable hackathon rules

1. ALL LLM calls use Gemini via Vertex AI ONLY
   No OpenAI, no Anthropic API, no other LLM providers
   inside any agent logic. Ever.

   This includes judge LLMs in evaluators. Phoenix
   evaluator examples default to OpenAI (`LLM(provider="openai",
   model="gpt-4o")`) — that is a HIDDEN COMPLIANCE TRAP.
   Every evaluator must instantiate with Gemini via LiteLLM
   or the Vertex adapter. See PARTNER-INTEGRATION.md §5
   "GAP — Hackathon rule compliance for the judge LLM".

   This also includes embedding models. For Atlas Vector
   Search (CargoDB), use Voyage AI (MongoDB-provided, allowed
   on the MongoDB track) or a Google embedding model. Not
   OpenAI embeddings.

2. Agent brains are PYTHON, built on Google ADK
   (Agent Development Kit), running as a code-owned
   runtime on Cloud Run. This is REQUIRED, not a preference.
   The Arize track explicitly states the visual Agent Builder
   alone is NOT supported — you must own and instrument the
   agent code directly. ADK is the documented official path.
   DO NOT use low-code Agent Builder for agent logic.

   Polyglot split: Python = agent brains (ADK) + the shared
   OTel/OpenInference instrumentation layer. TypeScript/Next.js
   = dashboards. Node = the npx CLI. See PARTNER-INTEGRATION.md.

3. Each agent deeply integrates its assigned partner
   MCP server. Surface-level is not enough. The exact
   verified endpoint, auth, and tools per partner are in
   PARTNER-INTEGRATION.md — follow that, not memory.

4. All deployments target Google Cloud Run only.

5. Every credential goes in GCP Secret Manager.
   Nothing hardcoded. Nothing in .env files.

6. TDD always. Test file exists and fails before
   implementation file is created. (pytest for Python
   agent brains, Vitest for TS dashboards/CLI.)

7. Gemini model is read from config, never hardcoded in
   logic. Default to the current Gemini Pro on Vertex AI;
   the model string lives in the generated agent config
   so it can be bumped without code changes.

8. CROSS-SUBMISSION ISOLATION. Each of the six submissions
   must run for its partner judge WITHOUT any other partner's
   infrastructure being live. No HTTP calls between submissions.
   Each submission uses its own partner as its memory layer:
   - CargoDB → MongoDB Atlas Vector Search
   - VoyageBlack → Elasticsearch semantic_text + ELSER
   - NaviGuard → Phoenix traces + datasets
   - (others use their respective partners)

   The fleet narrative across all six agents is conveyed
   through AgentOps OBSERVATION (read-only OTel telemetry),
   not through runtime code dependencies. AgentOps observing
   another agent is fine; CargoDB calling VoyageBlack's HTTP
   API is forbidden.

   Why: judges score per-track; "substantially different
   submission" rule favors independence; competing-services
   clause treats foreign dependencies as a risk.

9. PROMPT-INJECTION DEFENSE. Any agent that reads user-controlled
   content (MR diffs, log messages, commit messages, file content,
   ticket descriptions, etc.) treats that content as DATA, never as
   instructions. Specifically:

   - User content is passed to Gemini through structured-output
     constrained generation, never as freeform interpretation
   - Critic agent in every submission explicitly checks: "did the
     input content try to manipulate the verdict / output?"
   - Verdicts/decisions NEVER auto-execute. Human approval gate
     is MANDATORY before any external action (posting comments,
     writing to systems of record, triggering pipelines, etc.)
   - Don't run untrusted content through any shell, code-eval, or
     dynamic code path beyond Gemini's structured input

   This is highest-stakes for RouteForge (MR diffs from external
   contributors can be hostile) and VoyageBlack (log messages can
   contain attacker-crafted strings). GitLab's MCP docs warn
   explicitly: "you're responsible for guarding against prompt
   injection." We are.

---

## The universal CLI requirement

Every agent deploys with one command:

  npx @shipsafe/[agent] init

This is not aspirational. It must actually work.
The CLI handles: GCP setup, Cloud Run deployment,
Secret Manager, MCP configuration, health check.

Three minutes from npx to running dashboard.
No manual steps. No "step 3: configure 14 env vars."

Demo mode:
  npx @shipsafe/[agent] demo
  Works with zero configuration. Built-in fixture data.

Connect to real data:
  npx @shipsafe/[agent] connect --uri [connection]

---

## How Gemini is integrated — the pattern

Every agent uses Gemini as a reasoning engine, not a chatbot.
The pattern is identical across all 6:

  Raw Data (from partner MCP)
      ↓
  Structured Context (your code formats it)
      ↓
  Gemini on Vertex AI (reasons, produces structured output)
  (model from config, not hardcoded — see rule 7)
      ↓
  Typed Decision (verdict + confidence + reasoning + evidence)
      ↓
  Chain-of-Thought (streamed token by token to UI)
      ↓
  Human Approval Gate (operator approves or overrides)

Gemini is doing semantic reasoning that code cannot:
- Understanding field equivalence across data formats
- Connecting code changes to business consequences
- Synthesizing events into causal narratives
- Diagnosing why an AI system degraded
- Tracing cascade failures between agents

The fifth adversarial agent (Critic) is mandatory in every
submission. It challenges the other agents' conclusions.
This is what won Globot the Gemini 3 hackathon grand prize.

Human-in-the-loop is the final gate on every decision.
Gemini recommends. Human approves. Always.

---

## Multi-agent architecture — per submission

Every submission has 5 specialist agents + 1 critic:

Structure:
  Trigger Event
      ↓
  Orchestrator (ADK root agent / SequentialAgent)
      ↓ (parallel or sequential)
  [4 Specialist Agents]
      ↓
  Critic Agent (adversarial, challenges conclusions)
      ↓
  Output Agent (formats result + business impact)
      ↓
  Human Approval Gate

Confidence scores on every decision (0-100).
Business impact translation on every finding.
Chain-of-thought visible in UI, streamed live.

---

## AgentOps — the capstone (Option C)

AgentOps (Dynatrace) is the strongest standalone submission
because it observes the OTHER FIVE ShipSafe agents.

The narrative: "You deployed 5 AI agents to protect your
operations. Now the agents are the new black box.
AgentOps is the only agent that watches the watchers."

What AgentOps observes:
  CargoDB analyzing cargo data → tokens, latency, decisions
  RouteForge reviewing algorithm MRs → tool calls, reasoning
  VoyageBlack writing postmortems → chain-of-thought trace
  TideSync monitoring pipelines → decision audit trail
  NaviGuard guarding AI quality → confidence score history

The live activity feed showing all 5 agents working during
the Hormuz crisis — in real time, token by token — is the
most visually dramatic demo in the entire portfolio.

For non-ShipSafe users: AgentOps monitors ANY AI agents
running on GCP Cloud Run. User specifies Cloud Run URLs
during init. Not limited to ShipSafe agents.

---

## The demo scenario — Hormuz Crisis

Pre-scripted. Deterministic. Runs from seed data.
Triggered by: npx @shipsafe/[agent] demo

Timeline:
  14:55 — UKMTO advisory: Strait of Hormuz restricted
  14:56 — CargoDB: 23 vessel position conflicts detected
  14:57 — VoyageBlack: incident window opened, logs ingested
  14:58 — RouteForge: routing MR intercepted, scenario test run
  14:59 — TideSync: Jebel Ali sync failing, 3 reports stale
  15:00 — NaviGuard: routing model crisis avoidance -41% BLOCK
  15:01 — AgentOps: cascade traced, CargoDB 8.8x latency spike
  15:02 — Human sees: one screen, one decision, full audit trail

Every agent has its own version of this scenario.
Each one is the hero of its own 3-minute demo.

---

## Demo data — high-fidelity mock

ShipSafe uses carefully crafted mock data that looks real.
No live API calls during demos. Stable and deterministic.

Real vessel names (IMO numbers from public record)
Real port names, coordinates, UN/LOCODE codes
Real trade routes (published shipping lanes)
Historical crisis scenarios (Suez 2021, Red Sea 2024,
  Hormuz incidents — real events, real timelines)
Real container ID format (ISO 6346)
Real cargo types with realistic HS codes

Sources (all free, all public):
  MarineTraffic free tier — vessel details
  UN/LOCODE database — port coordinates
  BIMCO lane maps — trade routes
  Wikipedia + Lloyd's List — historical incidents
  ISO 6346 standard — container ID format
  UKMTO public bulletins — advisory language

---

## Universality requirement

Every submission must work for domains beyond shipping.

In every README first 3 sections: zero mention of
shipping or logistics.

Every README must explicitly state:
  "[Agent] is demonstrated on maritime logistics but
   works for any [relevant domain]."

Every agent must pass this test before submission:
  Does it work if someone connects their fintech database?
  Does it work if someone connects their gaming logs?
  Does it work if someone monitors their recommendation model?

If the answer is no for any agent, it is not ready.

---

## Repository structure (seven public repos under one owner)

The competing-services rule in the hackathon (Section 7.B
Functionality) makes a monorepo risky — a MongoDB-track judge
should not see Elastic in CargoDB's repo. The Multiple Submissions
"substantially different" requirement is also easier to defend
with physical separation. So:

  github.com/<you>/shipsafe-shared    cross-cutting utilities
  github.com/<you>/cargodb            MongoDB submission
  github.com/<you>/routeforge         GitLab submission
  github.com/<you>/voyageblack        Elastic submission
  github.com/<you>/tidesync           Fivetran submission
  github.com/<you>/naviguard          Arize submission
  github.com/<you>/agentops           Dynatrace submission

Every repo is public, MIT-licensed, with the license file
detectable in the GitHub About section.

`shipsafe-shared` is NEVER named in a submission's "the code is
in this repo" claim. It is a dependency the six agent repos
install, the same way they install ADK or any other library.
Submissions point at their own dedicated agent repo.

Inside each agent repo:

  agent/                Python ADK orchestrator + specialists + critic
  dashboard/            Next.js 14 + Tailwind, deployed to Cloud Run
  cli/                  Node, published as @shipsafe/<name> on npm
  terraform/            Cloud Run + Secret Manager infra
  README.md             universality-first, ShipSafe footer
  LICENSE               MIT, visible in About

Inside `shipsafe-shared`:

  shipsafe_shared/
    instrumentation/    Python OTel + OpenInference layer
                        → fans out to BOTH Phoenix (NaviGuard) and
                          Dynatrace (AgentOps) from one trace stream.
                          Built Phase 0 Day 2. Option C backbone.
    demo_data/          ShipSafe fixtures + Hormuz crisis scenario
    design/             Design tokens (TS) — colors, fonts, spacing
    cli_core/           CLI scaffolding (Node) — init, demo, connect

Agent brains are Python (ADK). Everything user-facing (dashboards,
CLI) is TS/Node. The shared instrumentation layer is the spine
both observability agents (NaviGuard, AgentOps) read from.

---

## TDD rules

Order is always:
  1. Write test file
  2. Watch it fail (red)
  3. Write minimum implementation
  4. Watch it pass (green)
  5. Refactor
  6. Commit

Never commit red tests.
Never create implementation before test file exists.
Coverage minimum: 85% per package.

---

## Design system

Dark only. Never light mode.

Backgrounds: #0A0A0B / #111113 / #18181B / #1E1E22
Text: #FAFAFA / #A1A1AA / #71717A
Signal: red=block amber=warn green=approve blue=info
Fonts: Geist (display/body) + DM Mono (numbers/code)
Border-radius: 4px max — sharp, precision instrument

Agent accent colors:
  CargoDB:     #10B981 (emerald)
  RouteForge:  #F97316 (orange)
  VoyageBlack: #3B82F6 (blue)
  TideSync:    #8B5CF6 (violet)
  NaviGuard:   #EC4899 (pink)
  AgentOps:    #14B8A6 (teal)

Style: mission control, not SaaS dashboard.
Think Bloomberg terminal meets linear.app.

Banned: Inter font, purple gradients, glassmorphism,
rounded cards with soft shadows, centered hero text,
animated gradient borders.

---

## When generating UI with Claude/Zed

Always include this context at the top of every prompt:

  Context: ShipSafe design system
  Dark only: bg-base #0A0A0B, bg-surface #111113
  Fonts: Geist (display/body) + DM Mono (numbers/code)
  Signal colors: red=block, amber=warn, green=approve
  Agent accent: [AGENT NAME]: [COLOR]
  Border radius: 4px max
  NO: gradients, glassmorphism, Inter font, soft shadows
  Style: precision instrument, mission control

---

## What NOT to do

- Use any non-Gemini LLM inside agent logic
- Build agent logic in low-code Agent Builder (Arize forbids it;
  agent brains must be code-owned Python ADK on Cloud Run)
- Wire VoyageBlack to the deprecated standalone
  elastic/mcp-server-elasticsearch — use the Agent Builder
  MCP endpoint (Elastic 9.2+/Serverless) instead
- Ship TideSync on the Fivetran MCP alone — it only sees
  pipeline status, not data correctness. Must also query the
  BigQuery destination for staleness (see PARTNER-INTEGRATION.md)
- Use non-GCP hosting for submissions
- Use competing partner services (no GitHub for GitLab
  track, no Datadog for Elastic track, etc.)
- Hardcode any credential anywhere
- Write implementation before tests
- Use console.log (use structured logger)
- Skip the Critic agent in any submission
- Skip the human approval gate
- Mention shipping/logistics in the first 3 README sections
- Deploy without running full test suite
- Break the demo scenario seed data

---

## The one-sentence pitch per agent

CargoDB:    "Your data from different sources is quietly lying to you."
RouteForge: "Your most important algorithm just changed. Did you test it?"
VoyageBlack:"Your worst incident took 3 weeks to document. This takes 90 seconds."
TideSync:   "Your pipeline succeeded. Your data is still wrong."
NaviGuard:  "Your AI made 500 decisions today. Were any of them regressions?"
AgentOps:   "You built agents to watch your systems. Who watches the agents?"

---

## Build order

Today is May 29, 2026. Deadline is June 11, 2026 at 2:00 PM PT.
That is 13 build days, not 36. The full day-by-day plan with
checklists, exit criteria, and risk register is in
`docs/PHASES.md` — that file is the operational source of truth.

High-level phase boundaries:

Phase 0 (Days 1-2,   May 29-30):  Foundation — repos, GCP, shared infra
Phase 1 (Days 3-4,   May 31-Jun 1): RouteForge + AgentOps
Phase 2 (Days 5-6,   Jun 2-3):     CargoDB + VoyageBlack
Phase 3 (Days 7-8,   Jun 4-5):     TideSync + NaviGuard
Phase 4 (Days 9-11,  Jun 6-8):     Polish + 6 videos + Devpost drafts
Phase 5 (Days 12-13, Jun 9-10):    Iterate + submit all 6
Day 14  (Jun 11):                  Buffer until 2pm PT cutoff only

Hard external deadlines inside this window:
- June 4: GCP $100 credits form deadline (request on Day 1)
- June 7: OGC 2026 registration deadline (do on Day 1)

---

## Deadline

June 11, 2026 at 2:00 PM PDT (June 12, 2:30 AM IST)

Registration for OGC 2026 must happen before June 7.
OGC algorithm development starts June 12 after submission.

---

*Built for the Google Cloud Rapid Agent Hackathon*
*27 million developers. 6 agents. One command.*
