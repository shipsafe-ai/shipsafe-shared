# NaviGuard — Demo Video Script (3:30)
**Track:** Arize Phoenix · **Accent:** #EC4899 pink · **Tagline:** *"Your AI made 500 decisions today. Were any of them regressions?"*
**Live URLs:** Backend `https://naviguard-o34wppiwiq-uc.a.run.app` · Dashboard `https://naviguard-dashboard-336382452417.us-central1.run.app`
**Verified against code 2026-06-11. Pipeline runtime measured: ~21s for the Hormuz demo.**

---

## ⚠ ACCURACY GUARDRAILS (read before recording)
- ✅ **This agent's SSE step-streaming is REAL** — `/run/stream` streams 4 step events live; the dashboard shows ✓/●/○ per step. This is the one ShipSafe agent with genuine live progress. Show it.
- ✅ Real numbers from a live run you can reproduce: `crisis_avoidance` confidence **0.31 vs 0.70 baseline (delta −0.39)**, pattern **NOVEL_DISTRIBUTION**, Critic verdict **CORRECT**, status **awaiting_approval**.
- ✅ Demo trigger that works: dashboard **"Run Hormuz Demo"** button (calls `/run/stream` with `scenario:"hormuz"`). It loads fixture spans — say "fixture/demo data," don't imply these are live production traces.
- ✅ Gemini here is doing real reasoning across 4 steps (monitor → detect → root-cause+dataset+experiment in parallel → critic). Steps 3a/3b/3c run in parallel via `asyncio.gather` — fine to say "in parallel."
- ⚠ The dataset + prompt version are created in Phoenix **only after you click Approve** (human gate). Don't show them appearing before approval.
- ⚠ Confirm the npm command name before showing a terminal — the dashboard button is the safe, verified trigger. Prefer it on camera.

---

## SCRIPT

| Time | SCREEN | NARRATOR (V.O.) |
|---|---|---|
| 0:00–0:10 | Black. A single log line types out in DM Mono: `15:00:17 naviguard │ crisis_avoidance confidence 0.31 (baseline 0.70) · Δ −0.39 · BLOCK`. Cursor blinks. | *(silence — let it land 2s)* "At three minutes past three, an AI routing model quietly stopped trusting itself. No alarm fired." |
| 0:10–0:30 | Split screen: a green "Overall accuracy: 80% ✓" dashboard on the left, the collapsed `crisis_avoidance` category on the right. | "Your AI made five hundred decisions today. Overall accuracy looked fine — eighty percent, green. But one category — crisis avoidance — collapsed from seventy-two percent confidence to thirty-one. A threshold monitor never saw it. You'd find out when a vessel routed into a restricted zone." |
| 0:30–0:55 | The six ShipSafe agents tile in, pink NaviGuard highlights last. | *(use the shared 30s pitch — see 00_README)* "ShipSafe is a fleet of six AI agents for operations intelligence… The machine recommends, the human decides, always. Today: NaviGuard." |
| 0:55–1:15 | Dashboard loads. Pink "Run Hormuz Demo" button. | "NaviGuard watches AI quality through Arize Phoenix. And here's why Gemini is the brain, not a threshold: Gemini reads the confidence *distribution* the way a senior ML engineer would — 'overall is fine, but crisis avoidance dropped thirty-nine points and nothing else moved. That's not general decay. That's a novel-distribution problem, and the fix is the prompt, not a retrain.' Code can't make that inference. A threshold can't tell category collapse from drift." |
| **1:15–1:35** | Click **Run Hormuz Demo**. Step 1 row flips ○→● then ✓: *"Analyzed 5 spans — regression_hint=True."* | "Watch it think — live. Step one: NaviGuard pulls the spans from Phoenix and computes the confidence stats. Five spans. Regression hint: true." |
| **1:35–1:55** | Step 2 ●→✓: *"REGRESSION — crisis_avoidance 0.31 vs 0.70, delta −0.39."* The two category bars render: standard_route healthy green, crisis_avoidance deep pink below the line. | "Step two — the regression detector. It isolates the failing category. Crisis avoidance, thirty-one percent, thirty-nine points under baseline. Standard routing is *fine* — that's the tell." |
| **1:55–2:20** | Step 3 ●: *"RootCause + DatasetBuilder + ExperimentRunner running in parallel."* Then ✓: *"Pattern: NOVEL_DISTRIBUTION."* Three sub-cards pop: root cause, a 5-example dataset spec, a proposed new prompt (+15%). | "Step three — three specialists at once. Root cause: novel distribution — the model hasn't seen enough crisis scenarios. A retraining dataset, built from the five real failure traces. And a brand-new prompt version that adds explicit crisis-avoidance criteria. It didn't just find the problem. It wrote the fix." |
| **2:20–2:45** | Step 4 ●→✓: *"Verdict: CORRECT — trace-9f3a2b1c verified, no hallucination, approved_for_dataset_creation=true."* Then the pink **Human Approval** gate slides up. | "Step four — the Critic. An adversarial agent that verifies the evidence actually exists in Phoenix and checks for hallucination. Verdict: correct. And then" — *(beat)* — "it stops. It found the regression, diagnosed it, wrote the dataset and the new prompt… and waited for you. It did not touch production." |
| 2:45–3:05 | Click **Approve**. Cut to Phoenix UI: a new dataset `naviguard-regression-…` and a prompt version tagged `naviguard-proposed`. | "This is the depth. NaviGuard uses the Phoenix MCP for four real operations: pull live spans, write a labeled dataset from the failure traces, version a new prompt, and tag it. The whole self-improvement loop is *inside* Phoenix — detection, dataset, prompt diff, version tag — every step traceable and reversible." |
| 3:05–3:20 | One slide, three rows: `crisis_avoidance → fraud_detection`, `→ diagnostic_confidence`, `→ recommendation_confidence`. | "NaviGuard works for any AI writing confidence scores to an observability layer. Fraud detection in fintech. A symptom cluster in healthcare. A new vertical in a recommender. Same agent. Same loop." |
| 3:20–3:30 | Terminal + dashboard. End frame: NaviGuard mark, tagline, Arize + Google Cloud logos. | "One command. Three minutes. Production-grade AI quality monitoring that doesn't just alert you — it hands you the fix and waits for your signature. NaviGuard." |

---

## Devpost description (≈140 words)
NaviGuard is an autonomous AI-quality monitor that catches the regressions your dashboards miss. Most monitoring watches overall accuracy — so a model can look healthy at 80% while one critical category quietly collapses. NaviGuard pulls live trace data from Arize Phoenix, and uses Gemini on Vertex AI to reason over the confidence *distribution*, isolating category-level drift a threshold alert can't see. When it finds a regression it diagnoses the root-cause pattern, packages the real failure traces into a labeled Phoenix dataset, and proposes a new versioned prompt to fix it — then stops at a mandatory human approval gate. Nothing touches production without a human signature. The entire self-improvement loop lives inside Phoenix and is fully traceable. Demonstrated on maritime crisis routing; works for any AI system producing confidence scores — fraud detection, medical triage, recommendations.

## Social captions
1. Your model is 80% accurate and one category just collapsed to 31%. Your threshold monitor is still green. NaviGuard reads the *distribution*, not the average — and writes the fix. Built on @arizephoenix + Gemini. #GoogleCloud
2. Most AI monitors alert you to a problem. NaviGuard hands you the solution: root cause, a labeled retraining dataset, and a new prompt version — then waits for your approval. The machine recommends. You decide.
3. We gave an AI agent the job of watching another AI's quality. It found a 39-point regression in 21 seconds, traced it to a novel-distribution failure, and proposed the prompt fix — all inside Arize Phoenix. #AIagents #GoogleCloud
