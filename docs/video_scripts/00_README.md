# ShipSafe Demo Video Scripts — 6 Agents

Six recording-ready 3:30 demo video scripts, one per hackathon submission.
**Every fact in these scripts was verified against the actual code on 2026-06-11** —
not memory, not CLAUDE.md aspirations. Where the built product diverges from the
original narrative, the script follows the BUILT product so narration matches the screen.

## Files
- `NAVIGUARD_VIDEO_SCRIPT.md` — Arize Phoenix track
- `ROUTEFORGE_VIDEO_SCRIPT.md` — GitLab track
- `CARGODB_VIDEO_SCRIPT.md` — MongoDB track
- `VOYAGEBLACK_VIDEO_SCRIPT.md` — Elastic track
- `TIDESYNC_VIDEO_SCRIPT.md` — Fivetran track
- `AGENTOPS_VIDEO_SCRIPT.md` — Dynatrace track

## How to use each file
1. Read the **⚠ ACCURACY GUARDRAILS** block first — it lists what NOT to say/show so you don't claim something the code doesn't do.
2. Record to the timed **SCRIPT** table. NARRATOR = exact V.O. SCREEN = what to capture. EMPHASIS = the one beat that must land.
3. Grab the **Devpost description** + **social captions** at the bottom.

## Shared timing skeleton (3:30 / 210s) — REVISED: ShipSafe first, plain-language problem
| Beat | Time | Purpose |
|---|---|---|
| **ShipSafe intro** | 0:00–0:12 | **Open on the master ShipSafe dashboard.** What the platform is, one breath, plain words |
| **This agent's problem** | 0:12–0:35 | The specific pain this agent solves — simple language, no jargon. Use the agent's node on the crisis timeline |
| **How this agent solves it** | 0:35–0:55 | Plain-language solution, then drill into the agent's own dashboard |
| Why Gemini / demo setup | 0:55–1:15 | The reasoning code can't do |
| **LIVE DEMO** | **1:15–2:45** | **The 90s that judges weight hardest** |
| Partner depth | 2:45–3:05 | Show the real tool calls, not "we integrate with X" |
| Universality | 3:05–3:20 | Same agent, different domain |
| CTA | 3:20–3:30 | One command. Three minutes. |

## Two dashboards — use both
- **Master ShipSafe dashboard** (`SHIPSAFE · AI OPERATIONS INTELLIGENCE · 6 AGENTS · 1 COMMAND`): the fleet + the Hormuz crisis cascade timeline (UKMTO → CargoDB → VoyageBlack → RouteForge → TideSync → NaviGuard → AgentOps → operator reroute). **Open every video here** — it establishes what ShipSafe is and where this agent fits.
- **Per-agent dashboard**: the agent's own live demo. Drill in via the agent's `Open →` tile.

## Problem-beat visuals (0:12–0:35) — don't fake a screen
The agent's **own dashboard appears from 0:35 onward**, not in the problem beat. For the problem beat use ONLY: (a) the **master ShipSafe timeline node** for that agent, (b) a **real external tool screen** (GitLab MR/diff, BigQuery console, Kibana logs, a Dynatrace/Fivetran view), or (c) a **clearly-labeled explainer title-card / b-roll graphic**. Never show a tile/number as if it's the agent's product screen when the product doesn't render it — e.g. NaviGuard's "80% vs 0.31" only appears LIVE in the demo (step 2), so in the problem beat it's a title-card, not a dashboard tile.

## Fixture vs live — is the scripted timeline a drawback? No.
The master crisis timeline is a **deterministic, pre-scripted scenario** — exactly what the hackathon asks for (stable mock data, no live API calls during a demo). Labels like "23 conflicts" / "8.8×" are the *stage*, not live computations. **What must be live is the agent's own run** — and it is: drill into the agent and its verdict/reasoning IS computed at run time (real Gemini, real MCP / DQL / `$vectorSearch`). Narrate the master timeline as "the scenario playing out," the agent's run as "watch it compute this now." Never call a static label live-computed — that's the only way it becomes a drawback.

## The shared 30-second ShipSafe pitch (use verbatim in the overview beat)
> "ShipSafe is a fleet of six AI agents for operations intelligence. Maritime logistics is the demo — enterprise operations is the product. Each agent deploys in one command and does one job better than a human can at machine speed. Every agent runs on Gemini, deeply integrates one partner platform, and ends every decision at a human approval gate. The machine recommends. The human decides. Always."
