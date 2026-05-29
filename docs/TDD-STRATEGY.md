# ShipSafe · TDD Strategy & Test Plan

## Philosophy

Tests are not a chore. In this project, tests ARE the specification.
Write the test first. Watch it fail. Then write the minimum code to make it pass.
If you can't write a test for it, you don't understand it well enough to build it.

---

## Test layers

### Layer 1 — Unit tests (fastest, most numerous)

Each agent function tested in complete isolation. All external dependencies mocked.

**Rule:** A unit test must run in under 50ms. If it takes longer, you're not mocking enough.

**Coverage target:** 90% per agent package.

**Location:** `src/**/*.test.ts`

```typescript
// Example: watcher.agent.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { WatcherAgent } from './watcher.agent'
import { createMockGitLabMCP } from '@shipsafe/shared/test-utils'

describe('WatcherAgent', () => {
  let agent: WatcherAgent
  let mockGitLab: ReturnType<typeof createMockGitLabMCP>

  beforeEach(() => {
    mockGitLab = createMockGitLabMCP()
    agent = new WatcherAgent({ gitlab: mockGitLab })
  })

  describe('trigger detection', () => {
    it('triggers when pipeline status changes to failed', async () => {
      mockGitLab.getPipelineStatus.mockResolvedValue('failed')
      const result = await agent.check({ projectId: '123', pipelineId: '456' })
      expect(result.shouldTrigger).toBe(true)
    })

    it('does not trigger when pipeline is pending', async () => {
      mockGitLab.getPipelineStatus.mockResolvedValue('pending')
      const result = await agent.check({ projectId: '123', pipelineId: '456' })
      expect(result.shouldTrigger).toBe(false)
    })

    it('does not trigger when pipeline passed', async () => {
      mockGitLab.getPipelineStatus.mockResolvedValue('passed')
      const result = await agent.check({ projectId: '123', pipelineId: '456' })
      expect(result.shouldTrigger).toBe(false)
    })
  })

  describe('payload construction', () => {
    it('includes pipeline ID in trigger payload', async () => {
      mockGitLab.getPipelineStatus.mockResolvedValue('failed')
      mockGitLab.getPipelineDetails.mockResolvedValue({
        id: '456',
        ref: 'feature/checkout-v2',
        sha: 'abc123'
      })
      const result = await agent.check({ projectId: '123', pipelineId: '456' })
      expect(result.payload?.pipelineId).toBe('456')
    })

    it('includes branch name in trigger payload', async () => {
      mockGitLab.getPipelineStatus.mockResolvedValue('failed')
      mockGitLab.getPipelineDetails.mockResolvedValue({
        id: '456',
        ref: 'feature/checkout-v2',
        sha: 'abc123'
      })
      const result = await agent.check({ projectId: '123', pipelineId: '456' })
      expect(result.payload?.branch).toBe('feature/checkout-v2')
    })
  })

  describe('error handling', () => {
    it('returns retryable error when GitLab MCP times out', async () => {
      mockGitLab.getPipelineStatus.mockRejectedValue(new Error('timeout'))
      const result = await agent.check({ projectId: '123', pipelineId: '456' })
      expect(result.error?.code).toBe('GITLAB_MCP_TIMEOUT')
      expect(result.error?.retryable).toBe(true)
    })

    it('returns non-retryable error when project not found', async () => {
      mockGitLab.getPipelineStatus.mockRejectedValue(
        Object.assign(new Error('not found'), { status: 404 })
      )
      const result = await agent.check({ projectId: 'invalid', pipelineId: '456' })
      expect(result.error?.retryable).toBe(false)
    })
  })
})
```

---

### Layer 2 — Integration tests (medium speed)

Tests that verify two or more agents work together correctly.
External APIs still mocked, but internal agent communication is real.

**Rule:** An integration test must run in under 500ms.

**Coverage target:** All agent handoff points covered.

**Location:** `src/integration/*.test.ts`

```typescript
// Example: watcher-to-investigator.test.ts
describe('WatcherAgent → InvestigatorAgent handoff', () => {
  it('passes pipeline ID from watcher output to investigator input', async () => {
    const watcher = new WatcherAgent({ gitlab: mockGitLab })
    const investigator = new InvestigatorAgent({ gitlab: mockGitLab, gemini: mockGemini })

    mockGitLab.getPipelineStatus.mockResolvedValue('failed')
    const watcherOutput = await watcher.check({ projectId: '123', pipelineId: '456' })

    expect(watcherOutput.shouldTrigger).toBe(true)

    const investigatorOutput = await investigator.analyze(watcherOutput.payload!)
    expect(investigatorOutput.changedFiles).toBeDefined()
    expect(mockGitLab.getMRDiff).toHaveBeenCalledWith(
      expect.objectContaining({ pipelineId: '456' })
    )
  })
})
```

---

### Layer 3 — E2E tests (slowest, most important)

Tests that verify the entire demo flow works end-to-end against real services.
Run against real GCP, real partner services, real NexCart.

**Rule:** E2E tests are the demo script. If E2E passes, the demo works.

**Coverage target:** All 6 demo flows covered exactly as scripted.

**Location:** `e2e/*.e2e.test.ts`

**When to run:** Before every deployment. Not during local development.

```typescript
// Example: shipguard.e2e.test.ts
import { describe, it, expect, beforeAll } from 'vitest'
import { ShipGuardOrchestrator } from '../src/orchestrator'
import { GitLabMCPClient } from '../src/tools/gitlab-mcp.tool'

describe('ShipGuard E2E — demo flow', () => {
  let orchestrator: ShipGuardOrchestrator

  beforeAll(async () => {
    // Uses real environment variables from .env.test
    orchestrator = new ShipGuardOrchestrator({
      gitlab: new GitLabMCPClient(process.env.SHIPGUARD_GITLAB_TOKEN!),
      gemini: realGeminiClient,
    })
  })

  it('blocks the checkout-v2 MR with HOLD verdict', async () => {
    // This MR is pre-seeded in NexCart's GitLab repo
    const result = await orchestrator.analyze({
      mrId: parseInt(process.env.NEXCART_DEMO_MR_ID!),
      projectId: parseInt(process.env.NEXCART_GITLAB_PROJECT_ID!),
    })

    expect(result.decision?.verdict).toBe('hold')
    expect(result.decision?.confidence).toBeGreaterThan(75)
    expect(result.decision?.reasoning).toContain('payment')
  }, 30_000) // 30 second timeout for real API calls

  it('posts a comment on the GitLab MR', async () => {
    const comments = await gitlabClient.getMRComments({
      projectId: parseInt(process.env.NEXCART_GITLAB_PROJECT_ID!),
      mrId: parseInt(process.env.NEXCART_DEMO_MR_ID!),
    })

    const shipguardComment = comments.find(c => c.body.includes('ShipGuard'))
    expect(shipguardComment).toBeDefined()
    expect(shipguardComment?.body).toContain('HOLD')
    expect(shipguardComment?.body).toContain('confidence')
  }, 10_000)

  it('includes business impact in the decision', async () => {
    const result = await orchestrator.analyze({
      mrId: parseInt(process.env.NEXCART_DEMO_MR_ID!),
      projectId: parseInt(process.env.NEXCART_GITLAB_PROJECT_ID!),
    })

    const hasBusinessImpact = result.decision?.evidence.some(
      e => e.business && e.business.length > 0
    )
    expect(hasBusinessImpact).toBe(true)
  }, 30_000)
})
```

---

## Mock factories

The `@shipsafe/shared/test-utils` package provides mock factories for all external services. Always use these — never create mocks inline.

```typescript
// packages/shared/src/test-utils/index.ts

export function createMockGitLabMCP() {
  return {
    getPipelineStatus: vi.fn(),
    getPipelineDetails: vi.fn(),
    getMRDiff: vi.fn(),
    getMRDetails: vi.fn(),
    createMRComment: vi.fn(),
    createMR: vi.fn(),
    triggerPipeline: vi.fn(),
  }
}

export function createMockMongoDBMCP() {
  return {
    listCollections: vi.fn(),
    getCollectionSchema: vi.fn(),
    getIndexes: vi.fn(),
    sampleDocuments: vi.fn(),
    runQuery: vi.fn(),
  }
}

export function createMockElasticMCP() {
  return {
    searchLogs: vi.fn(),
    searchTraces: vi.fn(),
    searchMetrics: vi.fn(),
    getDeployEvents: vi.fn(),
  }
}

export function createMockFivetranMCP() {
  return {
    listConnectors: vi.fn(),
    getConnectorStatus: vi.fn(),
    getSyncHistory: vi.fn(),
    triggerSync: vi.fn(),
  }
}

export function createMockArizeClient() {
  return {
    getTraces: vi.fn(),
    getModelMetrics: vi.fn(),
    runEvaluation: vi.fn(),
  }
}

export function createMockDynatraceClient() {
  return {
    getTraces: vi.fn(),
    getMetrics: vi.fn(),
    getLogs: vi.fn(),
    getProblems: vi.fn(),
  }
}

export function createMockGeminiClient() {
  return {
    generate: vi.fn().mockResolvedValue({
      text: 'Mock Gemini response',
      tokensUsed: 100,
    }),
    generateStructured: vi.fn(),
  }
}
```

---

## Test data fixtures

All test data lives in `packages/shared/src/test-utils/fixtures/`.

```
fixtures/
├── gitlab/
│   ├── mr-checkout-v2.json      → the demo MR payload
│   ├── pipeline-failed.json     → failed pipeline response
│   └── pipeline-passed.json     → passed pipeline response
├── mongodb/
│   ├── nexcart-schema.json      → NexCart database schema
│   ├── migration-rename.json    → the demo migration script
│   └── query-samples.json       → sample queries that reference fields
├── elastic/
│   ├── incident-window.json     → logs from the demo incident
│   ├── deploy-events.json       → deploy event timeline
│   └── error-spike.json         → Redis timeout error logs
├── fivetran/
│   ├── sync-failed.json         → failed sync connector status
│   └── connector-list.json      → list of NexCart connectors
├── arize/
│   ├── production-traces.json   → 500 real query traces
│   ├── baseline-scores.json     → current prompt quality scores
│   └── challenger-scores.json   → new prompt quality scores
└── dynatrace/
    ├── agent-telemetry.json     → sample agent traces
    └── latency-spike.json       → the demo latency spike event
```

---

## Vitest configuration

```typescript
// vitest.config.ts (root — shared by all packages via extend)
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 85,
        functions: 85,
        branches: 80,
        statements: 85,
      },
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.e2e.test.ts',
        '**/test-utils/**',
      ],
    },
    exclude: ['**/*.e2e.test.ts'],  // E2E runs separately
    testTimeout: 5000,
    hookTimeout: 10000,
  },
})
```

---

## CI test pipeline

```yaml
# .gitlab-ci.yml (NexCart repo — dogfooding ShipGuard)
stages:
  - test
  - coverage
  - e2e
  - deploy

unit-tests:
  stage: test
  script:
    - pnpm install
    - pnpm test
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'

coverage-check:
  stage: coverage
  script:
    - pnpm test:coverage
    - echo "Coverage check passed"

e2e-tests:
  stage: e2e
  script:
    - pnpm test:e2e
  environment: staging
  only:
    - main
    - /^release\/.*/

# PromptShield quality gate
promptshield-gate:
  stage: deploy
  script:
    - curl -X POST $PROMPTSHIELD_URL/api/gate
      -H "Authorization: Bearer $PROMPTSHIELD_TOKEN"
      -d '{"version": "$CI_COMMIT_SHA"}'
  allow_failure: false
```

---

## TDD daily workflow

```
Morning:
1. Pick the next agent from the phase checklist
2. Read its interface in packages/shared/src/types/index.ts
3. Write ALL unit tests for that agent (expect them all to fail)
4. Run: pnpm test --watch
5. Write the minimum implementation to make each test pass
6. Refactor until code is clean
7. Run: pnpm test:coverage — must be above 85%
8. Commit

Before end of day:
1. Run full test suite: pnpm test
2. If anything is red, fix it before stopping
3. Never end the day with failing tests
```

---

*Tests are the spec. The spec is the product. Build the spec first.*
