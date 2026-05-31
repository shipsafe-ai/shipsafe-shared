/**
 * ShipSafe design tokens — single source of truth for all 6 agent dashboards.
 *
 * Source of truth: CLAUDE.md (agent names + accents) + DESIGN-SYSTEM.md (all other values).
 * Rule: border-radius 4px max. No gradients. No glassmorphism. Dark only.
 */

// ---------------------------------------------------------------------------
// Colors
// ---------------------------------------------------------------------------

export const colors = {
  bg: {
    base:     "#0A0A0B",
    surface:  "#111113",
    elevated: "#18181B",
    overlay:  "#1E1E22",
  },

  border: {
    subtle:  "#27272A",
    default: "#3F3F46",
    strong:  "#52525B",
  },

  text: {
    primary:   "#FAFAFA",
    secondary:  "#A1A1AA",
    tertiary:   "#71717A",
    disabled:   "#52525B",
  },

  signal: {
    block:   "#EF4444",
    warn:    "#F59E0B",
    approve: "#22C55E",
    info:    "#3B82F6",
    neutral: "#8B5CF6",
    // Muted backgrounds for cards/badges
    blockBg:   "#7F1D1D33",
    warnBg:    "#78350F33",
    approveBg: "#14532D33",
    infoBg:    "#1E3A5F33",
  },
} as const;

// ---------------------------------------------------------------------------
// Agent accent colors (CLAUDE.md canonical names)
// ---------------------------------------------------------------------------

export const agentAccents = {
  cargodb:     "#10B981",  // emerald
  routeforge:  "#F97316",  // orange
  voyageblack: "#3B82F6",  // blue
  tidesync:    "#8B5CF6",  // violet
  naviguard:   "#EC4899",  // pink
  agentops:    "#14B8A6",  // teal
} as const;

export type AgentName = keyof typeof agentAccents;

export const AGENT_NAMES = [
  "cargodb",
  "routeforge",
  "voyageblack",
  "tidesync",
  "naviguard",
  "agentops",
] as const satisfies AgentName[];

// Per-agent metadata used for nav, activity feed labels, etc.
export const agents: Array<{
  name: AgentName;
  label: string;
  accent: string;
  icon: string;
}> = [
  { name: "cargodb",     label: "CargoDB",     accent: agentAccents.cargodb,     icon: "◎" },
  { name: "routeforge",  label: "RouteForge",  accent: agentAccents.routeforge,  icon: "⬡" },
  { name: "voyageblack", label: "VoyageBlack", accent: agentAccents.voyageblack, icon: "⊡" },
  { name: "tidesync",    label: "TideSync",    accent: agentAccents.tidesync,    icon: "⋈" },
  { name: "naviguard",   label: "NaviGuard",   accent: agentAccents.naviguard,   icon: "⊛" },
  { name: "agentops",    label: "AgentOps",    accent: agentAccents.agentops,    icon: "⊕" },
];

// ---------------------------------------------------------------------------
// Typography
// ---------------------------------------------------------------------------

export const fonts = {
  display: ["Geist", "-apple-system", "sans-serif"],
  body:    ["Geist", "-apple-system", "sans-serif"],
  mono:    ["DM Mono", "Fira Code", "monospace"],
} as const;

export const typeScale = {
  xs:    "11px",
  sm:    "13px",
  base:  "15px",
  lg:    "17px",
  xl:    "20px",
  "2xl": "24px",
  "3xl": "32px",
  "4xl": "48px",
  "5xl": "64px",
} as const;

export const lineHeight = {
  tight:  "1.2",
  normal: "1.5",
  loose:  "1.75",
} as const;

export const letterSpacing = {
  tight:   "-0.02em",
  normal:   "0em",
  wide:     "0.06em",
  widest:   "0.12em",  // for ALL CAPS labels
} as const;

// ---------------------------------------------------------------------------
// Spacing (4px base unit)
// ---------------------------------------------------------------------------

export const spacing: Record<number, string> = {
  1:  "4px",
  2:  "8px",
  3:  "12px",
  4:  "16px",
  5:  "20px",
  6:  "24px",
  8:  "32px",
  10: "40px",
  12: "48px",
  16: "64px",
  20: "80px",
  24: "96px",
};

// ---------------------------------------------------------------------------
// Border radius — 4px max (CLAUDE.md: "sharp, precision instrument")
// ---------------------------------------------------------------------------

export const borderRadius = {
  none:    "0px",
  sm:      "2px",
  DEFAULT: "4px",
} as const;

// ---------------------------------------------------------------------------
// Animation durations
// ---------------------------------------------------------------------------

export const duration = {
  fast:   "150ms",
  normal: "200ms",
  slow:   "800ms",
} as const;
