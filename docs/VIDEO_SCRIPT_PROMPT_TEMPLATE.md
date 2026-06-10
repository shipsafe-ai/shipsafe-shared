# NaviGuard Demo Video Script — Master Prompt for Claude Session

> Copy this entire file into a new Claude session for each agent.
> Fill in the [AGENT-SPECIFIC VARIABLES] section at the top before pasting.
> The session will produce a complete, ready-to-record video script.

---

## [AGENT-SPECIFIC VARIABLES — fill these in before pasting]

```
AGENT_NAME:          NaviGuard
AGENT_TAGLINE:       "Your AI made 500 decisions today. Were any of them regressions?"
AGENT_PACKAGE:       @shipsafe/naviguard
PARTNER_NAME:        Arize Phoenix
PARTNER_ROLE:        AI observability and trace storage
PARTNER_MCP_TOOLS:   list-traces, get-spans, list-datasets, add-dataset-examples, upsert-prompt, list-experiments
PARTNER_MCP_DEPTH:   NaviGuard uses Phoenix MCP to (1) pull live trace data — real span confidence scores from production — (2) create a labeled dataset from failure traces upon human approval, and (3) version a new prompt in Phoenix that addresses the root cause. The self-improvement loop closes inside Phoenix: regression → dataset → prompt version → tagged naviguard-proposed — all traceable in Phoenix UI.
AGENT_COLOR:         #EC4899 (pink)
STANDALONE_PROBLEM:  AI quality regressions are invisible. Your model made 500 routing decisions today. One category quietly dropped from 72% confidence to 31%. No alert fired. No dashboard showed it. You only discover it when a ship routes into a restricted zone.
WHAT_IT_DOES:        NaviGuard monitors AI model confidence via Arize Phoenix traces, detects category-level regressions Gemini couldn't catch with an alert threshold alone, runs root cause analysis, packages failure traces into a retraining dataset, proposes a new prompt version — and waits for human approval before touching anything in production.
GEMINI_REASONING:    Gemini is the reasoning engine, not just a classifier. It looks at confidence drift ACROSS categories — not just overall accuracy. A model can have 80% overall accuracy while one critical sub-category has collapsed to 31%. Gemini finds that. Then it patterns the failure: NOVEL_DISTRIBUTION, PROMPT_DRIFT, EDGE_CASE_CLUSTER. Then it writes the new prompt that addresses that specific failure mode. Code can't do this. SQL can't do this.
CRISIS_MOMENT:       15:00:17 — naviguard service log: "Crisis avoidance confidence: 31% (baseline 72%). Delta: -41%. Category: BLOCK. Trace: trace-9f3a2b1c." This is the Hormuz routing model collapsing mid-crisis. Ships are rerouting. The algorithm that was just merged — MR !447 — introduced the regression. NaviGuard catches it 17 seconds after it appears in Phoenix traces.
DEMO_STEPS:          (1) npx @shipsafe/naviguard demo → (2) ModelMonitor fetches Phoenix traces in parallel → (3) RegressionDetector: REGRESSION detected, crisis_avoidance 0.31 vs 0.70 baseline → (4) RootCauseAnalyzer: NOVEL_DISTRIBUTION pattern, Gemini reasoning visible → (5) DatasetBuilder: 5 failure traces packaged, awaiting approval → (6) ExperimentRunner: new prompt proposed, expected improvement +15% → (7) Critic: CORRECT verdict, approved_for_dataset_creation=true → (8) Human approval gate → (9) Phoenix dataset created + prompt version tagged naviguard-proposed
UNIQUE_DIFFERENTIATOR: The self-improvement loop. NaviGuard doesn't just alert — it closes the loop. Regression found → root cause analyzed → dataset built from real failure traces → new prompt version created in Phoenix — all traceable, all reversible, all requiring human approval. No other tool does this end-to-end in one command.
UNIVERSALITY:        NaviGuard works for any AI model producing confidence scores. Swap "crisis_avoidance" for "fraud_detection" in fintech. Swap the routing model for a recommendation engine in e-commerce. Swap Phoenix traces for your existing observability layer. Same pipeline, same loop, same command.
```

---

## YOUR TASK

Write a complete, ready-to-record **demo video script** for **[AGENT_NAME]** using the variables above and the full ShipSafe context below.

The video is **3 minutes 30 seconds maximum**. It will be submitted to the Google Cloud Rapid Agent Hackathon as the demo video for the **[PARTNER_NAME] track**.

---

## FULL SHIPSAFE CONTEXT (do not summarize — use this as written)

### What ShipSafe Is

ShipSafe is a fleet of 6 AI agents built for enterprise operations intelligence. The demo domain is maritime logistics. The product works for any domain.

**The one-sentence pitch for ShipSafe overall:**
*"Enterprise-grade AI operations has always existed — but only for companies with full engineering teams. ShipSafe makes the same capability available to any team, deployable in 3 minutes with one command."*

**The 6 agents:**
| Agent | Partner | One-sentence pitch |
|---|---|---|
| CargoDB | MongoDB | "Your data from different sources is quietly lying to you." |
| RouteForge | GitLab | "Your most important algorithm just changed. Did you test it?" |
| VoyageBlack | Elastic | "Your worst incident took 3 weeks to document. This takes 90 seconds." |
| TideSync | Fivetran | "Your pipeline succeeded. Your data is still wrong." |
| NaviGuard | Arize Phoenix | "Your AI made 500 decisions today. Were any of them regressions?" |
| AgentOps | Dynatrace | "You built agents to watch your systems. Who watches the agents?" |

**The Hormuz Crisis scenario** (this is the demo thread running through ALL 6 agents):
- 14:55 — UKMTO advisory: Strait of Hormuz restricted
- 14:56 — CargoDB: 23 vessel position conflicts detected
- 14:57 — VoyageBlack: incident window opened, logs ingested
- 14:58 — RouteForge: routing MR !447 intercepted — scenario tests bypassed in merge
- 14:59 — TideSync: Jebel Ali port feed stale by 4h26m, SLA breached
- 15:00 — NaviGuard: routing model crisis avoidance dropped from 72% → 31%, BLOCK verdict
- 15:01 — AgentOps: CargoDB 8.8× latency spike traced as cascade root cause
- 15:02 — Human sees: one screen, one decision, full audit trail

**The universal CLI requirement:**
Every agent deploys in one command: `npx @shipsafe/[agent] init`
Three minutes from that command to a running dashboard. No manual steps.

**The architecture pattern** (identical across all 6 agents):
```
Raw Data (from partner MCP)
    ↓
Structured Context (your code formats it)
    ↓
Gemini on Vertex AI (reasons, produces structured output)
    ↓
Typed Decision (verdict + confidence + reasoning + evidence)
    ↓
Chain-of-Thought (streamed live to UI)
    ↓
Human Approval Gate (operator approves or overrides)
```

**The 5+1 agent structure** (every submission has this):
- 4 specialist agents (each owns one reasoning task)
- 1 Critic agent (adversarial — challenges the other agents' conclusions)
- 1 Orchestrator (chains them, manages context isolation)
- Human approval gate before any external action

**Why Gemini is the brain, not just a classifier:**
Gemini does semantic reasoning that code cannot: understanding field equivalence across formats, connecting code changes to business consequences, synthesizing events into causal narratives, diagnosing why an AI system degraded, tracing cascade failures. The Critic agent — mandatory in every submission — specifically challenges whether the other agents' conclusions are correct. This adversarial architecture is what separates NaviGuard (and every ShipSafe agent) from a simple alerting tool.

**Prompt injection defense** (mention this — it's sophisticated):
Any agent that reads user-controlled content treats it as DATA, never as instructions. Structured-output constrained generation. Critic explicitly checks: "did the input content try to manipulate the verdict?" Verdicts never auto-execute — human approval gate is mandatory.

---

## VIDEO SCRIPT REQUIREMENTS

### Tone
- Mission control. Precision instrument. Not a SaaS product demo.
- Business decision-making language, not engineering language.
- Urgency without panic. Confidence without hype.
- Every sentence earns its place or it's cut.

### Structure (strict timing)

**[0:00–0:12] — THE CRISIS HOOK**
Open on the crisis moment from CRISIS_MOMENT above. This is happening RIGHT NOW on screen. No narrator yet. Let the log speak. The number that makes you stop: the delta, the dollar figure, the vessel count.

**[0:12–0:35] — THE PROBLEM**
Narrator: describe STANDALONE_PROBLEM. Make the pain visceral. This is a problem every company with AI in production has had. Name the cost: delayed discovery, wrong decisions, cascading failures.

**[0:35–1:05] — SHIPSAFE 30-SECOND OVERVIEW**
"ShipSafe is a fleet of 6 AI agents for operations intelligence. Maritime logistics is the demo. Enterprise operations is the product."
Show all 6 agents on screen briefly. "Each agent deploys with one command. Each agent has one job it does better than any human can — at machine speed."
Land on THIS agent: "Today: [AGENT_NAME]."

**[1:05–1:30] — THIS AGENT'S PROMISE**
State WHAT_IT_DOES clearly. Then: "Gemini is the brain."
State GEMINI_REASONING — why Gemini, not a threshold alert, not a SQL query. What semantic reasoning capability is being used here that code literally cannot do.

**[1:30–2:30] — LIVE DEMO**
Walk through DEMO_STEPS. Show the actual terminal + dashboard.
Key moments to highlight:
- The Gemini chain-of-thought streaming live (show the reasoning, not just the verdict)
- The confidence number vs baseline (0.31 vs 0.70 — this lands visually)
- The Critic agent challenging the analysis (this is the adversarial architecture moment)
- The human approval gate appearing — "it found it, proposed the fix, and then it waited. It did not act without you."
- The Phoenix dataset being created / prompt version appearing in Phoenix UI after approval

**[2:30–2:55] — PARTNER MCP DEPTH**
Do NOT say "we integrate with [Partner]." Show HOW.
Use PARTNER_MCP_DEPTH verbatim or adapted. Show the actual MCP tool call in code or in terminal output. Name the specific tools from PARTNER_MCP_TOOLS. Make the judge feel: "they actually built this, not just wired it up."

**[2:55–3:15] — UNIVERSALITY**
Read UNIVERSALITY. Show one slide/screen with domain swap examples. End on: "[AGENT_NAME] is demonstrated on maritime logistics. It works for any domain where [core capability applies]."

**[3:15–3:30] — CALL TO ACTION**
Show terminal: `npx @shipsafe/[AGENT_PACKAGE] demo`
"One command. Three minutes. Production-ready AI quality monitoring."
Final frame: agent name + tagline + partner logo + Google Cloud logo.

---

## WHAT TO INCLUDE IN THE SCRIPT

For each section, write:
1. **NARRATOR (V.O.)** — exact spoken words
2. **SCREEN** — what is visible on screen at that moment
3. **EMPHASIS** — what visual or spoken element the viewer should NOT miss

Write the script so a non-technical product manager could record it and a developer watching it would still nod and say "yes, that's actually how it works."

---

## WHAT TO AVOID

- Do NOT say "leveraging" or "utilizing" — say "using" or "calling"
- Do NOT say "seamlessly" — show it
- Do NOT explain what JSON is
- Do NOT show more than 3 terminal commands before showing a result
- Do NOT end on "and that's NaviGuard!" — end on the universality + CTA
- Do NOT skip the Critic agent — it is the differentiator that proves this isn't just a wrapper
- Do NOT make the human approval gate sound like a limitation — it IS the feature ("the machine recommends, the human decides — always")

---

## JUDGING CRITERIA TO OPTIMIZE FOR

This is Google Cloud Rapid Agent Hackathon. Judges evaluate:
1. **Technical implementation depth** — did they actually build it or just demo a prototype?
2. **Partner integration quality** — surface-level API call vs deep MCP tool usage
3. **Business value clarity** — does a non-technical judge understand why this matters?
4. **Google Cloud integration** — Gemini on Vertex AI, Cloud Run deployment, Secret Manager
5. **Innovation** — is there something here no one has done before?

**The answer to #5 for every ShipSafe agent:**
The self-improvement loop architecture (detect → analyze → package fix → human approve → execute → trace in partner platform) is new. The Critic agent pattern is new. The "one command to production" requirement is new. Make sure these come through.

---

## OUTPUT FORMAT

Produce the complete script in this format:

```
[SECTION NAME — TIMING]
SCREEN: [what viewer sees]
NARRATOR: [exact spoken words]
EMPHASIS: [the moment that must land]
---
```

After the full script, produce:
1. **30-second ShipSafe pitch** (standalone, for use in other contexts)
2. **3 social media captions** (Twitter/X-style, under 280 chars each)
3. **One-paragraph Devpost description** for this agent (under 150 words, universality-first)
