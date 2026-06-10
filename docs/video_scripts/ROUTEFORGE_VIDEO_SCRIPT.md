# RouteForge — Demo Video Script (3:30)
**Track:** GitLab · **Accent:** #F97316 orange · **Tagline:** *"Your most important algorithm just changed. Did you test it?"*
**Live URLs:** Agent `https://routeforge-336382452417.us-central1.run.app` · Dashboard `https://routeforge-dashboard-336382452417.us-central1.run.app` · MCP proxy `https://routeforge-mcp-336382452417.us-central1.run.app/mcp`
**Verified against code 2026-06-11.**

---

## ⚠ ACCURACY GUARDRAILS (read before recording)
- ⚠ **There is NO `routeforge demo` CLI command** (CLI has only `init` + `status`). The demo is **server-side**: a startup auto-seed re-fires three demo merge requests (**iids 1, 2, 3**), and `POST /demo/seed` re-seeds on demand. Trigger the demo by hitting `/demo/seed` or just open the dashboard after a cold start. Show the dashboard, not a fake `demo` command.
- ⚠ **There is NO "MR !447", no "-200 penalty", no "31% vs 72%", no "confidence 94"** anywhere in code. The verdict and confidence are a **live Gemini output over the real diffs** of GitLab project 82762386 at run time. Do NOT put scripted numbers on screen — read whatever the live run shows.
- ✅ Real specialist order (verified): CommitWatcher → Critic injection-scan → PipelineObserver → ScenarioTester → CodeContextAnalyzer → RiskGate (Gemini) → Critic challenge → ChangelogWriter. **Critic runs twice.**
- ✅ **Thinking tokens are real:** RiskGate budget 8192, Critic 4096; `thinking_tokens` surfaced in the UI from `thoughts_token_count`. Show the thinking-token badge.
- ✅ **Gemini chain-of-thought text now shown (added 2026-06-11):** the verdict card has a "Gemini chain-of-thought" collapsible with RiskGate's actual thought text, AND a "Critic" section with the adversarial Critic's `challenge_reasoning` (previously computed but never surfaced). Expand the CoT on camera — it's the raw reasoning behind the BLOCK/PASS, not just a token count.
- ✅ Three real GitLab channels: **Webhook** (MR / pipeline / note events), **MCP** via self-hosted zereight proxy (`search_project_code`, `get_pipeline_job_output`, `create_merge_request_thread`, `resolve_merge_request_thread`, `create_issue`), **REST** (diffs, notes, approve, labels, discussions).
- ⚠ Say "GitLab MCP" carefully: it routes through a **self-hosted zereight/gitlab-mcp proxy**, not GitLab's native endpoint. "We run a GitLab MCP server" is accurate.
- ⚠ Injection is **detected and surfaced**, not halted — the pipeline continues to a verdict; the real backstop is the human approval gate. Don't claim it "blocks" the run.
- ✅ **Nothing is posted to GitLab until a human approves** — `POST /verdicts/{iid}/approve` posts the note and (for PASS) calls the Approvals API. This is the strongest, truest beat.

---

## SCRIPT

| Time | SCREEN | NARRATOR (V.O.) |
|---|---|---|
| 0:00–0:10 | Black. A GitLab merge-request card: *"perf: improve throughput +12%"*, pipeline **green ✓**, "Merged." Looks routine. | *(silence 2s)* "A merge request. Pipeline green. Twelve percent faster. Someone clicked merge. Nobody noticed the safety check that quietly disappeared in the diff." |
| 0:10–0:30 | Diff view scrolls; an `if "HORMUZ" in avoid_straits:` guard is deleted in red. CI stays green. | "Your routing engine is your most important algorithm. When it changes, your tests run — but your tests never simulated an *active crisis*. So the suite passed, CI went green, and a contributor removed the one line that keeps ships out of a blockaded strait. Green doesn't mean safe." |
| 0:30–0:55 | Six ShipSafe agents tile in; orange RouteForge highlights last. | *(shared 30s pitch)* "ShipSafe is a fleet of six AI agents… The machine recommends, the human decides, always. Today: RouteForge." |
| 0:55–1:15 | RouteForge dashboard: a live verdict feed of MRs. | "RouteForge intercepts every change to your algorithm and asks the question your CI can't: not 'do the tests pass' but 'is this still *safe*.' Gemini is the brain — it connects a code diff to a business consequence. It reads the changed function, runs the algorithm against a library of crisis scenarios, and reasons: 'this removed the crisis-avoidance guard; under an active Hormuz blockade this routes a tanker into the restricted zone. Block it.'" |
| **1:15–1:35** | `POST /demo/seed` fires; an MR appears in the feed. SSE pipeline log starts streaming `1/9 … 2/9`. | "Watch a live review. A merge request lands — RouteForge pulls the real diffs from GitLab over the REST API. Step one and two: who changed what." |
| **1:35–2:00** | Log streams 3/9 Critic injection scan → 4/9 PipelineObserver "CI passing" → 5/9 ScenarioTester "running crisis scenarios → blocked." | "Step three — before it trusts a word of that diff, the Critic scans it for prompt injection, because the diff is untrusted input. Step four: CI says passing. But step five — the scenario tester runs the *changed* algorithm against the Hormuz crisis fixtures… and it fails the ones that matter." |
| **2:00–2:25** | 6/9 CodeContextAnalyzer "search_project_code via MCP → K neighbors" → 7/9 RiskGate "Gemini evaluating… BLOCK · {live conf}% · {N} tok thinking". Thinking-token badge glows orange. | "Step six pulls the surrounding code through our GitLab MCP server, so Gemini judges the change *in context*. Step seven — the RiskGate. Gemini deliberates with a visible thinking budget and returns a structured verdict: block. Those thinking tokens are real — you're watching it reason." |
| **2:25–2:45** | 8/9 Critic "challenging verdict for false positives" → 9/9 ChangelogWriter "drafting comment." Verdict card renders. Then an inline diff thread on the exact deleted line. The **Approve** control sits unclicked. | "Step eight — a second adversarial Critic tries to overturn the block, because a false alarm wastes a developer's day. It holds. RouteForge drafts the comment, pins an inline thread on the exact line that was removed — and stops. It has *not* posted anything to GitLab. It's waiting for a human." |
| 2:45–3:05 | Click **Approve**. Now GitLab shows the posted verdict note + the MR moved to the blocked label; the inline thread is live. | "That's the integration depth. Three real GitLab channels: webhooks fire RouteForge on every MR and pipeline event; our MCP server does semantic code search, pulls failing job logs, and posts resolvable inline threads; the REST API handles diffs, notes, scoped labels and approvals. And it only writes to GitLab *after* you approve." |
| 3:05–3:20 | One slide: `crisis routing → payments fraud rules → insurance claims logic`. RouteForge ships fixtures for all three. | "RouteForge is demonstrated on routing safety. It works for any change to a high-stakes algorithm — a fraud rule, a claims model, a pricing engine. If the test suite never simulated the crisis, RouteForge will." |
| 3:20–3:30 | Dashboard verdict feed. End frame: RouteForge mark, tagline, GitLab + Google Cloud logos. | "Your most important algorithm just changed. RouteForge tested it — against the day that actually matters. One command to deploy." |

---

## Devpost description (≈145 words)
RouteForge is an AI reviewer for changes to your most critical algorithms. CI tells you the tests passed; it can't tell you a change is *unsafe*, because your test suite never simulated the crisis. RouteForge intercepts every merge request through GitLab webhooks, and uses Gemini on Vertex AI to run the *changed* algorithm against a library of crisis scenarios, reason about the business consequence, and return a structured BLOCK/PASS verdict with visible thinking tokens. It pulls surrounding code through a GitLab MCP server for context, treats every diff as untrusted input with a dedicated prompt-injection Critic, and pins an inline thread on the exact risky line. Critically, it never posts to GitLab until a human approves. Demonstrated on maritime routing safety; works for any high-stakes algorithm change — fraud rules, claims logic, pricing engines. The machine recommends. You decide.

## Social captions
1. Your CI is green. A contributor just deleted the one line that keeps ships out of a blockaded strait — and the test suite never simulated the blockade. RouteForge runs the *changed* algorithm against the crisis. Built on GitLab + Gemini. #GoogleCloud
2. RouteForge reads a diff, runs your algorithm against crisis scenarios, and blocks the unsafe merge — with visible Gemini thinking tokens. Then it waits for a human to approve before posting anything to GitLab. #AIagents
3. "The tests passed" is not "this is safe." RouteForge tests your most important algorithm against the day that actually matters. GitLab webhooks + MCP + Gemini on Vertex AI. #GoogleCloud #DevSecOps
