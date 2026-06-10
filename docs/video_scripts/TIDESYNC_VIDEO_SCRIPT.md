# TideSync — Demo Video Script (3:30)
**Track:** Fivetran · **Accent:** #8B5CF6 violet · **Tagline:** *"Your pipeline succeeded. Your data is still wrong."*
**Live URL:** `https://tidesync-336382452417.us-central1.run.app` (agent + dashboard, same Cloud Run service)
**Verified against code 2026-06-11.**

---

## ⚠ ACCURACY GUARDRAILS (read before recording)
- ✅ **REAL Fivetran MCP integration (added 2026-06-11).** TideSync now spawns the official `fivetran/fivetran-mcp` server over stdio and routes control-plane reads (`list_connections`, `get_connection_details`) through it, with direct-REST fallback so the demo never breaks. **Verified live:** `GET /mcp/tools` returns `connected:true` and **77 Fivetran MCP tools**. The dashboard "Fivetran MCP" panel label is now accurate. The V.O. CAN say "Fivetran MCP."
  - Great on-camera shot: hit `GET /mcp/tools` in a browser/terminal → the live list of 77 tools from the MCP server. Proves deep MCP integration in one frame.
  - `USE_FIVETRAN_MCP=false` disables the MCP path (REST-only) if ever needed.
- ✅ The PRODUCT thesis is the differentiator: **control plane (Fivetran MCP says "sync succeeded") vs data truth (BigQuery `MAX(_fivetran_synced)` proves it's stale).** Both planes are real; the contradiction is the whole demo.
- ✅ Real BigQuery query: `SELECT MAX(_fivetran_synced), COUNT(*), TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_fivetran_synced), SECOND) AS lag_seconds`. Stale when `lag_seconds > 3600`.
- ✅ Specialist order: SyncSentinel → DataDoctor → regex injection pre-screen → ImpactMapper (Gemini) → **Gemini adversarial Critic** → BriefingAgent (background).
- ✅ **Two-layer Critic (upgraded 2026-06-11):** Layer 1 = deterministic regex injection pre-screen; **Layer 2 = a real Gemini adversarial critic** (`challenge_verdict`) that challenges the staleness verdict and returns reasoning. **Verified live:** `UPHOLD` + reasoning ("lag of 260745s far exceeds the 3600s threshold… Fivetran reports recent success"). The dashboard shows an "Adversarial Critic · Gemini" panel with the reasoning. You CAN call it Gemini-powered now.
- ⚠ **The "thinking" steps in the UI are cosmetic frontend timers** (fixed `setTimeout` text swaps), NOT streamed backend progress. There is **no SSE endpoint**. Don't claim "live token streaming" or "watch it think in real time." You can still show the step text — just describe it as a progress indicator, not live model output.
- ⚠ The ContradictionPanel "SLA breach in ~Xm" sub-line has a flat-vs-nested field bug and **likely doesn't render** — verify on screen before scripting that number.
- ✅ Human gate is real and two-layer: writes gated by `FIVETRAN_ALLOW_WRITES`, AND `/run` returns `status:"awaiting_approval"` + token; resync only fires after `POST /approve/{token}`. RecoveryAgent never auto-executes.
- ⚠ Command: **`npx shipsafe-tidesync demo`** (not `@shipsafe/tidesync`). It POSTs to `/run` (body ignored; runs against live Fivetran+BigQuery).

---

## SCRIPT

| Time | SCREEN | NARRATOR (V.O.) |
|---|---|---|
| 0:00–0:10 | Black. A Fivetran connector tile, big green **"Sync succeeded · 2m ago ✓"**. Looks perfect. | *(silence 2s)* "Your data pipeline says it succeeded. Green check, two minutes ago. Everything's fine." *(beat)* "Everything is not fine." |
| 0:10–0:30 | Beside the green tile, a BigQuery query result: `MAX(_fivetran_synced) = 04:33` while now is `08:59`. The report built on top reads "current." | "The sync ran. The connector is healthy. But the actual data in your warehouse is four and a half hours stale — because the source stopped feeding it and the pipeline happily synced *nothing*, successfully. Your dashboards are green. Your reports are wrong. And nobody knows, because status and truth are two different questions." |
| 0:30–0:55 | Six ShipSafe agents tile in; violet TideSync highlights last. | *(shared 30s pitch)* "ShipSafe is a fleet of six AI agents… the human decides, always. Today: TideSync." |
| 0:55–1:15 | TideSync dashboard, the split Contradiction panel. | "TideSync catches the lie that pipeline monitoring can't: *sync succeeded, data still wrong.* It checks two independent sources of truth — the Fivetran control plane for sync status, and BigQuery directly for actual freshness — and uses Gemini to reason about the gap between them and what it costs the business." |
| 1:08–1:15 | Quick cut: browser on `GET /mcp/tools` → JSON `"connected": true, "tool_count": 77`, list of Fivetran MCP tools. | "Under the hood, TideSync runs the official Fivetran MCP server — seventy-seven tools, live." |
| **1:15–1:35** | Click **Run**. Progress indicator steps through "Querying Fivetran MCP connectors → Checking BigQuery freshness → Gemini contradiction analysis." | "Run it. SyncSentinel pulls connector status through the Fivetran MCP server. Then DataDoctor goes straight to the warehouse — not the pipeline — and asks BigQuery the only question that matters: when was this data actually last updated." |
| **1:35–2:05** | The **Contradiction panel** renders side by side: **LEFT** "sync succeeded 08:57 · status connected ✓ (green)"; **RIGHT** "BigQuery MAX(_fivetran_synced) = 04:33 · lag 4h 26m". Header flips red: **"CONTRADICTION DETECTED."** | "And there it is. On the left, the control plane: connected, succeeded, green. On the right, the data truth from BigQuery: last real record, four hours twenty-six minutes ago. Same connector. Two completely different stories. The lag blew past the one-hour SLA — TideSync flags it stale." |
| **2:05–2:25** | **ImpactMapper (Gemini)** verdict card: `is_stale`, `lag_display`, `breach_confidence`, business `recommendation`. | "This is where Gemini reasons. ImpactMapper takes both reports and judges: is this data still trustworthy, how confident are we it's a real breach, and what's the business impact — which downstream reports are now built on stale numbers. The verdict is structured, not prose." |
| **2:25–2:42** | **Adversarial Critic · Gemini** panel: `UPHOLD`/`CHALLENGE` + reasoning. Two-layer defense — a regex injection pre-screen ran upstream; this is the Gemini layer challenging the verdict. | "Then a second Gemini turns adversarial. The Critic *challenges* the staleness verdict — is it actually justified by the BigQuery lag, or did something in the data try to manipulate the call? Here it upholds: 'lag of two hundred sixty thousand seconds far exceeds the threshold while Fivetran reports success.' Real reasoning, on screen — not a rubber stamp." |
| **2:42–2:55** | `status: awaiting_approval` + **"Approve Resync"** button. Click it → `POST /approve/{token}` → RecoveryAgent runs Fivetran setup tests, then triggers a sync. | "And it does not fix it behind your back. Every write to Fivetran is gated — it returns 'awaiting approval' with a token. The operator approves; only then does RecoveryAgent run the setup tests and trigger the sync. The machine recommends. You decide." |
| 2:55–3:08 | One slide: `port feed → finance close → ML feature store → patient records`. | "TideSync is demonstrated on a stale shipping feed. The pattern is universal: a finance close built on yesterday's numbers, an ML feature store quietly frozen, a patient record that didn't update. Anywhere a pipeline can succeed while the data goes stale, TideSync is the cross-check." |
| 3:08–3:20 | Dashboard, contradiction resolved after sync. | "Pipeline status tells you the truck arrived. TideSync checks whether anything was actually *in* it." |
| 3:20–3:30 | End frame: TideSync mark, tagline, Fivetran + Google Cloud logos. | "Your pipeline succeeded. Your data was still wrong. Now you'll know. One command. Three minutes. TideSync." |

---

## Devpost description (≈150 words)
TideSync catches the failure pipeline monitoring is blind to: the sync succeeded, but the data is still stale. A connector can report "connected, succeeded, green" while the source quietly stopped feeding it — so your warehouse freezes and every downstream report silently goes wrong. TideSync checks two independent sources of truth: the Fivetran control plane (via the official Fivetran MCP server — 77 tools over stdio) for sync status, and BigQuery directly for actual data freshness (`MAX(_fivetran_synced)` and real lag in seconds). When they contradict — status healthy, data stale past SLA — Gemini on Vertex AI reasons about whether the data is trustworthy, how confident the breach is, and which downstream reports are now compromised. Recovery is proposed, never auto-executed: every re-sync passes a human approval gate. Demonstrated on a stale maritime port feed; works for any pipeline — finance closes, ML feature stores, clinical records.

## Social captions
1. "Sync succeeded ✓" is not "the data is correct." TideSync checks the Fivetran control plane AND queries BigQuery directly — and catches the contradiction when your pipeline is green but your data is 4 hours stale. #GoogleCloud
2. Your pipeline can succeed while syncing nothing. TideSync asks BigQuery the question status can't answer — *when was this data actually last updated* — then lets Gemini reason about the business impact. #Fivetran #dataquality
3. Status tells you the truck arrived. TideSync checks whether anything was in it. Stale-data detection with a human approval gate before any re-sync. #GoogleCloud #AIagents
