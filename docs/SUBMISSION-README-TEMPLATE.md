# [AgentName] · [One-line value proposition]

<!--
INSTRUCTIONS FOR USING THIS TEMPLATE
=====================================
Replace every [PLACEHOLDER] with real content.
Delete this comment block before publishing.

Rules for the first three sections (judge reads these first):
  - NO mention of shipping, maritime, or Hormuz
  - Lead with the universal problem, not the demo scenario
  - The agent name and problem must make sense for any industry

The Hormuz Crisis demo appears in section 4 only.
The ShipSafe ecosystem appears in the footer only.
-->

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Gemini-orange.svg)](https://google.com/adk)
[![Powered by [Partner]](https://img.shields.io/badge/powered%20by-[Partner]-[color].svg)]([partner-url])

> [Two-sentence description of the problem this agent solves and for whom.
> Must be industry-agnostic. Example: "Your data pipeline reports a successful
> sync. Your data is silently three hours stale. TideSync catches the
> contradiction — before your team makes decisions on bad data."]

---

## Deploy in 3 minutes

```bash
npx @shipsafe/[agent-name] init
```

That is the entire getting-started guide. The CLI handles everything else:
GCP project, [Partner] connection, Cloud Run deploy, health check.

---

## See it working now

```bash
npx @shipsafe/[agent-name] demo
```

Runs a pre-built crisis scenario against demo data. No credentials required
from you. Works in under 60 seconds from a clean machine with Node 20+.

---

## What it does

<!-- Three bullets. Each = one concrete action the agent takes, not a feature name.
     Format: "Detects [specific thing] and [consequence prevented]"
     Bad:  "- Real-time monitoring with AI-powered insights"
     Good: "- Detects when your pipeline reports success but data is stale,
              and alerts before downstream decisions use bad data" -->

- [Detects X and prevents Y]
- [Translates technical findings into plain-English business impact]
- [Posts results directly into your existing workflow — Slack / [Partner] / email]

---

## How it works

<!-- One ASCII architecture diagram, then 3 sentences max explaining the flow.
     Focus on the data flow: what comes in, what the agent does, what comes out. -->

```
[External event] → [AgentName] → [Partner MCP] → [Action]
                       │
                  [Specialist 1]    [Specialist 4]
                  [Specialist 2]    [Specialist 5]
                  [Specialist 3]    [Critic      ]
                       │
                  Human approval gate → [Output to workflow]
```

[Sentence 1: What triggers the agent and what data it reads.]
[Sentence 2: What the multi-agent pipeline does with that data — the key reasoning step.]
[Sentence 3: What comes out — the concrete output delivered to the human or system.]

For the full architecture, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Requirements

- Google Cloud project (free tier works for the demo)
- [[Partner] account]([partner-free-tier-link]) (free tier works)
- Node.js 20+
- 3 minutes

---

## Connect to your own [data source / platform / account]

```bash
npx @shipsafe/[agent-name] connect --[uri/token/key] [your-value]
```

Replaces the demo data with your real [data source]. The agent then monitors
YOUR [pipelines / algorithms / models / fleet] rather than the demo scenario.

---

## Demo scenario: Hormuz Crisis

The built-in demo simulates a geopolitical incident closing the Strait of Hormuz
to commercial shipping. [One sentence on what this specific agent does during
the crisis — its particular slice of the response.]

The demo uses real IMO vessel numbers, UN/LOCODE port codes, and ISO 6346
container manifests. It is fully self-contained — no external credentials needed.

---

## Limitations and roadmap

<!-- Being honest here builds trust. 2-3 concrete limitations + what v2 would fix. -->

- **[Limitation 1]**: [what it doesn't handle yet] — v2 will add [specific improvement]
- **[Limitation 2]**: [scope boundary] — out of scope by design; handled by [[sibling agent]]([link])
- **[Limitation 3]**: [known constraint] — workaround: [one-liner]

---

## Part of the ShipSafe ecosystem

[AgentName] is one of six independent agents in the ShipSafe AI reliability
platform. Each solves a different failure mode. All deploy the same way.

| Agent | Failure mode it prevents | Partner |
|---|---|---|
| [CargoDB](https://github.com/shipsafe-ai/shipsafe-cargodb) | Agent memory loss — decisions with no history | MongoDB |
| [RouteForge](https://github.com/shipsafe-ai/shipsafe-routeforge) | Unsafe algorithm changes reaching production | GitLab |
| [VoyageBlack](https://github.com/shipsafe-ai/shipsafe-voyageblack) | Incidents with no documented postmortem | Elastic |
| [TideSync](https://github.com/shipsafe-ai/shipsafe-tidesync) | Silent data staleness in pipelines | Fivetran |
| [NaviGuard](https://github.com/shipsafe-ai/shipsafe-naviguard) | AI quality regressions going undetected | Arize |
| [AgentOps](https://github.com/shipsafe-ai/shipsafe-agentops) | AI agent fleets running without observability | Dynatrace |

Each agent is independently useful. You can deploy one, or all six.

---

## License

MIT — fork it, deploy it, build on it. See [LICENSE](LICENSE).
