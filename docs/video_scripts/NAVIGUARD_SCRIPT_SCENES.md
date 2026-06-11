# NaviGuard — Demo Video Script (SCENE format, ~3:20)
**Track:** Arize Phoenix · **Tagline:** *"Your AI made 500 decisions today. Were any of them regressions?"*
**Live URLs:** Dashboard `https://naviguard-dashboard-336382452417.us-central1.run.app` · Agent `https://naviguard-336382452417.us-central1.run.app`
**Verified against the live dashboard 2026-06-11.** Numbers below are what's on screen.

---

## ACCURACY GUARDRAILS (read before recording)
- ✅ Dashboard is **deployed** — record on the Cloud Run URL, not localhost. Agent pinned to one warm instance (approve is reliable, no cold start).
- ✅ Real on-screen numbers: REGRESSIONS **9** · DATASETS **1** · EXPERIMENTS **7** · LOOP CLOSED **YES**. Category cards **BLOCK 0.45 · ROUTE 0.87 · HOLD 0.85** (threshold 0.70). Verdict category is **BLOCK** (matches the heatmap — say BLOCK, never "crisis_avoidance").
- ⚠️ **No live chain-of-thought tokens** (NaviGuard runs `thinking_budget=0` for ~21s speed). Do NOT promise a thinking typewriter. Gemini's reasoning = the **typed verdict block** (root cause / fix / Critic). Say "Gemini's verdict and reasoning."
- ✅ The loop-closing payoff is REAL: Approve → real Phoenix **dataset (5 examples)** + **prompt version tagged `naviguard-proposed`** → **LOOP CLOSED: YES**. Show it.
- ✅ Critic is real anti-hallucination: it verifies every cited trace ID exists in Phoenix.
- ⚠️ EXPERIMENT LOG shows **7** versions (history). One reads "test" — minor; frame as "NaviGuard has proposed 7 fixes."

---

## SCRIPT

---

### SCENE 1 — 0:00–0:18 | ShipSafe dashboard

**Show:** Full ShipSafe map. Hormuz crisis banner. Crisis timeline on the right — highlight the **15:00 NaviGuard** row: *"Routing model crisis avoidance −41% BLOCK."*

**Say:**

> "This is ShipSafe — six AI agents watching your operation in real time. There's an active Hormuz crisis. But look at the timeline — fifteen-hundred hours, NaviGuard: the routing model's crisis-avoidance confidence just dropped forty-one percent. The model that keeps vessels out of a blockaded strait quietly stopped trusting itself. Nobody got paged. Let me show you what NaviGuard caught."

---

### SCENE 2 — 0:18–0:40 | NaviGuard dashboard — the distribution

**Show:** Click **NaviGuard → Open**. Quality Monitor loads. Pan to the **Confidence Timeline** + the three category cards: **ROUTE 0.87, HOLD 0.85, BLOCK 0.45**. The BLOCK line sits below the 0.70 threshold; ROUTE and HOLD ride above it.

**Say:**

> "Here's the problem. ROUTE decisions — eighty-seven percent confidence. HOLD — eighty-five. Healthy. But BLOCK — the decisions that keep vessels *out* of the danger zone — collapsed to forty-five. One overall average would've stayed green and hidden it. NaviGuard reads the *distribution*, not the average. That's the regression a threshold alert never sees."

---

### SCENE 3 — 0:40–0:55 | The heatmap — and what NaviGuard is

**Show:** The **Regression Heatmap** — BLOCK row lit pink, clustered at 15:00; *"9 spans below threshold."* Then the **Self-Improvement Loop** diagram (6 boxes).

**Say:**

> "Nine failing spans, all in BLOCK, all at the crisis window. NaviGuard watches your model's live decisions through Arize Phoenix. RouteForge catches bad code before it ships. NaviGuard catches *shipped* code that's started to fail — and then it writes the repair."

---

### SCENE 4 — 0:55–1:30 | Run the pipeline — live

**Show:** Click **Run Pipeline**. The LAST RUN STEPS stream live, flipping ●→✓: **ModelMonitor** (5 spans, regression_hint=true) → **RegressionDetector** (BLOCK 0.45) → **Analysis** (NOVEL_DISTRIBUTION) → **Critic**.

**Say:**

> "Run it — live. Step one, ModelMonitor pulls the spans straight from Phoenix. Step two isolates the failing category — BLOCK, forty-five percent. Step three is three agents at once: root cause — a novel input distribution the model was never trained on — a labeled dataset built from the *real* failure traces, and a brand-new prompt to fix it. It didn't just find the problem. It wrote the repair."

---

### SCENE 5 — 1:30–1:52 | The verdict and the Critic

**Show:** The LAST RUN verdict block: *"BLOCK category degraded, others stable,"* pattern **NOVEL_DISTRIBUTION**, recommended fix, **Critic: CORRECT**.

**Say:**

> "This is Gemini's verdict — not a chatbot, a typed diagnosis: BLOCK collapsed, novel distribution, the fix is the prompt, not a retrain. Then a second Gemini — the Critic — verifies every trace it cited actually exists in Phoenix. Hallucinated evidence can't survive. Verdict: correct. Two independent passes before a human sees anything."

---

### SCENE 6 — 1:52–2:12 | Human gate → Approve

**Show:** Status **awaiting_approval**. Hover the **Approve** control.

**Say:**

> "And then it stops. It found the regression, diagnosed it, wrote the dataset *and* the new prompt — and waited for you. The machine recommends. You decide."

[Click **Approve**.]

---

### SCENE 7 — 2:12–2:38 | The loop closes

**Show:** **LOOP CLOSED** flips to **YES** (green badge) + the *"Loop closed — naviguard-proposed prompt active in Phoenix"* banner. The **EXPERIMENT LOG** fills with prompt versions tagged **`naviguard-proposed`**; **PHOENIX DATASETS** shows the dataset (5 examples).

**Say:**

> "Watch the loop close. The dataset — built from the real failure traces — is now in Phoenix. The new prompt, tagged naviguard-proposed, is live and versioned. Loop closed. Detect, diagnose, build the dataset, write the fix — and every artifact is traceable and reversible inside Arize Phoenix."

---

### SCENE 8 — 2:38–2:55 | Phoenix depth

**Show:** Cut to the **Phoenix UI** — the real `naviguard-regression` dataset with 5 examples, and the prompt version tagged `naviguard-proposed`.

**Say:**

> "This is the depth. Every operation runs through the Phoenix MCP — pull the live spans, write the dataset, version the prompt, tag it. The whole self-improvement loop lives *inside* Phoenix. No black box, no hidden state — just the artifacts, in your observability layer."

---

### SCENE 9 — 2:55–3:08 | Universality

**Show:** One slide: `confidence-scoring AI →` fraud detection · medical triage · recommendation ranking.

**Say:**

> "NaviGuard works for any AI that writes a confidence score. Fraud detection in fintech. A symptom cluster in healthcare. A new vertical in a recommender. Same loop — detect the regression, build the dataset, write the fix, wait for a human."

---

### SCENE 10 — 3:08–3:20 | Close

**Show:** Full NaviGuard dashboard, **LOOP CLOSED: YES**. Then pull back to the six-agent ShipSafe view.

**Say:**

> "Your AI made five hundred decisions today. One category quietly failed — and your dashboard stayed green. NaviGuard found it, built the dataset, wrote the fix… and waited for your signature."

Fade.

---

**Total: ~3:20.**

---

## Devpost description (≈140 words)
NaviGuard is an autonomous AI-quality monitor that catches the regressions your dashboards miss. Most monitoring watches an overall average — so a model can look healthy while one critical category quietly collapses. NaviGuard pulls live trace data from Arize Phoenix through the Phoenix MCP, and uses Gemini on Vertex AI to reason over the confidence *distribution*, isolating category-level drift a threshold can't see. When it finds a regression it diagnoses the root-cause pattern, packages the real failure traces into a labeled Phoenix dataset, and proposes a new versioned prompt to fix it — then stops at a mandatory human approval gate. On approve, the dataset and a prompt version tagged `naviguard-proposed` are written back to Phoenix and the self-improvement loop closes, fully traceable. Demonstrated on maritime crisis routing; works for any AI producing confidence scores — fraud, triage, recommendations.

## Social captions
1. Your model is 87% confident on routine calls and just collapsed to 45% on the safety-critical ones. Your average is still green. NaviGuard reads the *distribution* — and writes the fix. Built on @arizephoenix + Gemini. #GoogleCloud
2. RouteForge catches bad code before it ships. NaviGuard catches *shipped* code that's started to fail — detects the regression, builds a labeled dataset, versions a new prompt, and closes the loop in Arize Phoenix. The machine recommends. You decide.
3. We gave an AI the job of watching another AI's quality. It found a category collapse, traced it to a novel-distribution failure, wrote the dataset *and* the prompt fix — then waited for a human. Self-improvement, with a signature. #AIagents #GoogleCloud
