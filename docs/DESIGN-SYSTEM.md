# ShipSafe · Design System

## The aesthetic direction

ShipSafe is a **precision instrument for engineers under pressure.**

The design language reflects this: dark, dense, data-forward, with sharp typographic hierarchy and purposeful color signals. Think mission control, not SaaS dashboard. Think Bloomberg terminal meets linear.app — information-dense but never cluttered, serious but not cold.

**The one thing someone must remember:** *"It felt like a real tool, not a demo."*

---

## What we are NOT building

Read this before touching any UI code. These are the AI-generated aesthetics we explicitly reject:

❌ Purple-to-blue gradients on white backgrounds
❌ Rounded cards with soft drop shadows everywhere
❌ Inter or Space Grotesk as the primary font
❌ Gradient hero sections with centered text
❌ Generic "AI product" blues and teals
❌ Glassmorphism for its own sake
❌ Animated gradient borders as a style statement
❌ Lottie animations for empty states
❌ Every section having its own background color
❌ "Built with ❤️" footers
❌ Unnecessary motion that doesn't carry information

---

## Color system

### Base palette

```css
:root {
  /* Backgrounds — near black, not pure black */
  --bg-base: #0A0A0B;
  --bg-surface: #111113;
  --bg-elevated: #18181B;
  --bg-overlay: #1E1E22;

  /* Borders — subtle, not invisible */
  --border-subtle: #27272A;
  --border-default: #3F3F46;
  --border-strong: #52525B;

  /* Text — high contrast hierarchy */
  --text-primary: #FAFAFA;
  --text-secondary: #A1A1AA;
  --text-tertiary: #71717A;
  --text-disabled: #52525B;

  /* Signal colors — carry meaning, use sparingly */
  --signal-block:   #EF4444;   /* critical — red */
  --signal-warn:    #F59E0B;   /* warning — amber */
  --signal-approve: #22C55E;   /* safe — green */
  --signal-info:    #3B82F6;   /* informational — blue */
  --signal-neutral: #8B5CF6;   /* agent thinking — violet */

  /* Signal backgrounds — muted versions for cards/badges */
  --signal-block-bg:   #7F1D1D33;
  --signal-warn-bg:    #78350F33;
  --signal-approve-bg: #14532D33;
  --signal-info-bg:    #1E3A5F33;
  --signal-neutral-bg: #2E1065433;

  /* Per-agent accent colors — one per agent, used sparingly */
  --agent-shipguard:    #F97316;   /* orange */
  --agent-schemasafe:   #10B981;   /* emerald */
  --agent-postmortem:   #3B82F6;   /* blue */
  --agent-trustpipe:    #8B5CF6;   /* violet */
  --agent-promptshield: #EC4899;   /* pink */
  --agent-agentops:     #14B8A6;   /* teal */
}
```

### Color rules

1. **Never use agent accent colors as backgrounds** — only for borders, icons, and text accents
2. **Signal colors are sacred** — red means block, amber means warn, green means approve. Don't use them decoratively
3. **Backgrounds stay near-black** — only 4 levels of elevation, never lighter than `--bg-overlay`
4. **Text hierarchy is strict** — primary for main content, secondary for metadata, tertiary for labels, disabled for inactive

---

## Typography

### Font stack

```css
/* Display — headlines, verdicts, big numbers */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Geist:wght@400;500;600;700;800;900&display=swap');

:root {
  --font-display: 'Geist', -apple-system, sans-serif;
  --font-mono:    'DM Mono', 'Fira Code', monospace;
  --font-body:    'Geist', -apple-system, sans-serif;
}
```

**Why Geist + DM Mono:**
- Geist is sharp and engineered — designed by Vercel for developer tools. Not overused yet.
- DM Mono has personality. The italics are beautiful. Monospace signals precision.
- Together they feel like an IDE, not a marketing site.

### Type scale

```css
:root {
  /* Scale */
  --text-xs:   11px;  /* metadata, timestamps, labels */
  --text-sm:   13px;  /* secondary content, table cells */
  --text-base: 15px;  /* body text */
  --text-lg:   17px;  /* card titles, section headers */
  --text-xl:   20px;  /* page sections */
  --text-2xl:  24px;  /* page titles */
  --text-3xl:  32px;  /* verdict displays, big numbers */
  --text-4xl:  48px;  /* hero numbers (confidence score) */
  --text-5xl:  64px;  /* dashboard hero stats */

  /* Line heights */
  --leading-tight:  1.2;
  --leading-normal: 1.5;
  --leading-loose:  1.75;

  /* Letter spacing */
  --tracking-tight:  -0.02em;
  --tracking-normal:  0em;
  --tracking-wide:    0.06em;
  --tracking-widest:  0.12em;  /* for ALL CAPS labels */
}
```

### Typography rules

1. **Big numbers are monospace** — confidence scores, token counts, latency values always use `--font-mono`
2. **Labels are uppercase + tracked** — `HOLD`, `SEV2`, `BLOCKED` use `--tracking-widest`
3. **Headlines are tight** — `--tracking-tight` on anything above `--text-xl`
4. **Never center-align body text** — left-aligned always, center only for isolated stat displays
5. **Code and technical values are always monospace** — field names, error codes, SHA hashes

---

## Component patterns

### Verdict badge

The most important component in ShipSafe. Used everywhere.

```tsx
// verdict-badge.tsx
interface VerdictBadgeProps {
  verdict: 'approve' | 'hold' | 'block' | 'warn'
  confidence?: number
  size?: 'sm' | 'md' | 'lg'
}

// Approved:  green border, green text, --signal-approve-bg
// Hold:      amber border, amber text, --signal-warn-bg
// Block:     red border, red text, --signal-block-bg
// Warn:      amber border, amber text, --signal-warn-bg
```

Design rules for verdict badge:
- Square corners (border-radius: 3px max) — these are signals, not friendly bubbles
- Monospace font for the verdict text
- Confidence shown as `(87%)` in a lighter weight
- Never use gradient fill — solid flat background

### Agent step card

Shows one agent's work in the pipeline visualization.

```tsx
// States: pending (dim) → running (pulsing) → complete (solid) → error (red)
// Running state: left border pulses in agent accent color
// Complete: checkmark appears, duration shown in mono
// Error: red border, error code visible
```

### Confidence ring

Large circular visualization for the main confidence score.

```tsx
// SVG ring, NOT a CSS border-radius hack
// The ring color maps to the verdict:
//   >80%: --signal-approve
//   60-80%: --signal-warn
//   <60%: --signal-block
// Center shows the number in --font-mono --text-4xl
// Below shows the verdict label in --tracking-widest uppercase
```

### Data table

Used for evidence lists, schema comparisons, pipeline statuses.

```tsx
// Rules:
// - No rounded corners on the table itself
// - Alternating row backgrounds: transparent / --bg-elevated
// - Severity column uses colored dots, not text badges
// - Monospace for all numeric columns
// - Sticky header with --bg-surface background
// - Hover state: --bg-overlay
// - No horizontal rules between rows — use spacing only
```

### Live activity feed

Used in AgentOps. Real-time stream of agent actions.

```tsx
// Inspired by terminal output but cleaner
// Monospace font throughout
// Timestamp: --text-tertiary --text-xs
// Agent name: agent accent color
// Operation: --text-secondary
// Status indicator: colored dot (green/amber/red)
// New items slide in from bottom with subtle fade
// Max visible: 50 items, older items fade out
```

---

## Layout system

### Spacing scale

```css
:root {
  --space-1:   4px;
  --space-2:   8px;
  --space-3:   12px;
  --space-4:   16px;
  --space-5:   20px;
  --space-6:   24px;
  --space-8:   32px;
  --space-10:  40px;
  --space-12:  48px;
  --space-16:  64px;
  --space-20:  80px;
  --space-24:  96px;
}
```

### Page structure

Every agent dashboard follows this exact layout:

```
┌─────────────────────────────────────────────────────┐
│ ShipSafe nav (48px, --bg-surface, border-bottom)      │
├─────────────────────────────────────────────────────┤
│ Agent header (agent name, status, last run)          │
├───────────────┬─────────────────────────────────────┤
│               │                                      │
│  Left panel   │  Main content area                   │
│  (280px)      │  (flex-1)                            │
│               │                                      │
│  Agent        │  Primary visualization               │
│  pipeline     │  (verdict, confidence, timeline)     │
│  steps        │                                      │
│               ├─────────────────────────────────────┤
│               │  Evidence / details panel            │
│               │  (scrollable)                        │
│               │                                      │
└───────────────┴─────────────────────────────────────┘
```

### Grid rules

- Main content max-width: 1400px, centered
- Content padding: `--space-6` on all sides
- Card gaps: `--space-4`
- Section gaps: `--space-8`
- Never nest cards more than 2 levels deep

---

## Motion principles

Motion carries information. If it doesn't, remove it.

### Allowed motion

```css
/* Agent step transitions — conveys state change */
.agent-step {
  transition: border-color 200ms ease, opacity 200ms ease;
}

/* Running state pulse — conveys activity */
@keyframes pulse-border {
  0%, 100% { border-color: var(--agent-color); opacity: 1; }
  50%       { border-color: var(--agent-color); opacity: 0.4; }
}

/* New items in activity feed — conveys recency */
@keyframes slide-in {
  from { transform: translateY(-8px); opacity: 0; }
  to   { transform: translateY(0);    opacity: 1; }
}
.feed-item { animation: slide-in 150ms ease; }

/* Confidence ring fill — conveys calculation */
.confidence-ring {
  stroke-dashoffset: ...;
  transition: stroke-dashoffset 800ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Number counting up — conveys live data */
/* Use a simple JS counter, not CSS */

/* Page load stagger — conveys structure */
.card:nth-child(1) { animation-delay: 0ms; }
.card:nth-child(2) { animation-delay: 60ms; }
.card:nth-child(3) { animation-delay: 120ms; }
```

### Forbidden motion

❌ Hover animations that delay information access
❌ Spinning loaders — use skeleton screens instead
❌ Page transition animations — instant feels faster
❌ Parallax scrolling
❌ Any animation over 400ms for UI state changes
❌ Bounce/spring on anything data-critical

---

## The ShipSafe navbar

Shared across all 6 agents. Identical on every page.

```
┌─────────────────────────────────────────────────────┐
│ ◈ ShipSafe    ShipGuard · SchemaSafe · PostMortem     │
│              TrustPipe · PromptShield · AgentOps  ≡  │
└─────────────────────────────────────────────────────┘
```

- Height: 48px
- Background: `--bg-surface` with bottom border `--border-subtle`
- Logo: `◈ ShipSafe` in Geist 600 weight — the ◈ symbol is the brand mark
- Active agent: highlighted with its accent color underline
- All agents always visible — no hamburger menu on desktop
- Mobile: horizontal scroll on nav items, no collapse

---

## Per-agent visual identity

Each agent has one accent color and one icon. These are fixed. Never change them.

| Agent | Color | CSS var | Icon | Usage |
|---|---|---|---|---|
| ShipGuard | Orange `#F97316` | `--agent-shipguard` | `⬡` | Left border on active card |
| SchemaSafe | Emerald `#10B981` | `--agent-schemasafe` | `◎` | Left border on active card |
| PostMortem AI | Blue `#3B82F6` | `--agent-postmortem` | `⊡` | Left border on active card |
| TrustPipe | Violet `#8B5CF6` | `--agent-trustpipe` | `⋈` | Left border on active card |
| PromptShield | Pink `#EC4899` | `--agent-promptshield` | `⊛` | Left border on active card |
| AgentOps | Teal `#14B8A6` | `--agent-agentops` | `⊕` | Left border on active card |

The accent color appears ONLY on:
- Active nav item underline
- Left border of the current agent's primary card
- Agent name text in the activity feed
- The confidence ring stroke color
- Active state on pipeline step

---

## Skeleton screens

Never use spinners. Always use skeleton screens.

```tsx
// Skeleton rules:
// - Same dimensions as the real content
// - Background: --bg-elevated
// - Shimmer animation: left-to-right gradient sweep
// - No border-radius > 4px
// - Duration: 1.5s infinite

@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-elevated) 25%,
    var(--bg-overlay)  50%,
    var(--bg-elevated) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

---

## Dark mode only

ShipSafe is dark mode only. There is no light mode. This is intentional.

Engineers use dark mode. The dense data visualizations look better on dark backgrounds. The signal colors (red/amber/green) pop on dark. Don't add a light mode toggle — it would dilute the design intent and double the CSS maintenance burden during a hackathon.

---

## Tailwind configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

export default {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          base:     '#0A0A0B',
          surface:  '#111113',
          elevated: '#18181B',
          overlay:  '#1E1E22',
        },
        border: {
          subtle:  '#27272A',
          default: '#3F3F46',
          strong:  '#52525B',
        },
        signal: {
          block:   '#EF4444',
          warn:    '#F59E0B',
          approve: '#22C55E',
          info:    '#3B82F6',
          neutral: '#8B5CF6',
        },
        agent: {
          shipguard:    '#F97316',
          schemasafe:   '#10B981',
          postmortem:   '#3B82F6',
          trustpipe:    '#8B5CF6',
          promptshield: '#EC4899',
          agentops:     '#14B8A6',
        },
      },
      fontFamily: {
        display: ['Geist', '-apple-system', 'sans-serif'],
        mono:    ['DM Mono', 'Fira Code', 'monospace'],
        body:    ['Geist', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'xs':   ['11px', { lineHeight: '1.5' }],
        'sm':   ['13px', { lineHeight: '1.5' }],
        'base': ['15px', { lineHeight: '1.6' }],
        'lg':   ['17px', { lineHeight: '1.5' }],
        'xl':   ['20px', { lineHeight: '1.4' }],
        '2xl':  ['24px', { lineHeight: '1.3' }],
        '3xl':  ['32px', { lineHeight: '1.2' }],
        '4xl':  ['48px', { lineHeight: '1.1' }],
        '5xl':  ['64px', { lineHeight: '1.0' }],
      },
      spacing: {
        '18': '72px',
        '22': '88px',
      },
      borderRadius: {
        DEFAULT: '4px',
        'sm':    '2px',
        'md':    '6px',
        'lg':    '8px',
        'none':  '0px',
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer':    'shimmer 1.5s infinite',
        'slide-in':   'slideIn 150ms ease',
        'fade-in':    'fadeIn 200ms ease',
      },
      keyframes: {
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition:  '200% 0' },
        },
        slideIn: {
          from: { transform: 'translateY(-8px)', opacity: '0' },
          to:   { transform: 'translateY(0)',    opacity: '1' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config
```

---

## When asking Claude to generate UI

When you prompt Claude (via Zed or otherwise) to generate UI components for ShipSafe, always include this context block at the top of your prompt:

```
Context: ShipSafe design system
- Dark only: bg-base #0A0A0B, bg-surface #111113, bg-elevated #18181B
- Fonts: Geist (display/body) + DM Mono (numbers, code, labels)
- Signal colors: red=block, amber=warn, green=approve — never decorative
- Agent accent for [AGENT NAME]: [COLOR]
- Border radius: 4px max — sharp corners, not friendly bubbles
- Labels: uppercase + wide tracking
- Numbers: monospace always
- NO: gradients, glassmorphism, Inter font, centered hero text, 
      purple/blue gradients, soft shadows everywhere
- Style: precision instrument, mission control, not SaaS dashboard
```

This prevents Claude from defaulting to generic AI aesthetics and keeps every generated component consistent with the system.

---

## Reference components to build first

Build these 8 components before starting any agent-specific UI. Every agent uses all of them.

1. `<VerdictBadge>` — approve/hold/block/warn with confidence
2. `<AgentStepCard>` — pipeline step with pending/running/complete/error states
3. `<ConfidenceRing>` — SVG ring visualization
4. `<EvidenceCard>` — technical finding + business impact
5. `<DataTable>` — sortable, with severity dots
6. `<LiveFeed>` — real-time activity stream
7. `<SkeletonLine>` — loading state primitive
8. `<ShipSafeNav>` — shared navigation with all 6 agents

These 8 components make up ~80% of every agent dashboard.

---

*Design is not decoration. Every pixel should make Alex's job easier under pressure.*
