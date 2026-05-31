/**
 * ShipSafe Tailwind CSS preset (CommonJS — compatible with all Tailwind v3/v4 configs).
 *
 * Usage in any agent dashboard's tailwind.config.ts:
 *   import preset from '@shipsafe/design/tailwind'
 *   export default { presets: [preset], content: ['./src/**\/*.{ts,tsx}'] }
 *
 * Rules enforced:
 * - Dark only — no light-mode variants
 * - Border-radius max 4px (CLAUDE.md)
 * - No gradients, no glassmorphism
 * - Agent accent colors use current names (CLAUDE.md), not old design-system names
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",

  theme: {
    // --- Colors (extends so Tailwind defaults remain available) ---
    extend: {
      colors: {
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
        },
        // Per-agent accents — current agent names only
        agent: {
          cargodb:     "#10B981",
          routeforge:  "#F97316",
          voyageblack: "#3B82F6",
          tidesync:    "#8B5CF6",
          naviguard:   "#EC4899",
          agentops:    "#14B8A6",
        },
      },

      fontFamily: {
        display: ["Geist", "-apple-system", "sans-serif"],
        body:    ["Geist", "-apple-system", "sans-serif"],
        mono:    ["DM Mono", "Fira Code", "monospace"],
      },

      // Type scale from DESIGN-SYSTEM.md (overrides Tailwind defaults)
      fontSize: {
        xs:    ["11px", { lineHeight: "1.5" }],
        sm:    ["13px", { lineHeight: "1.5" }],
        base:  ["15px", { lineHeight: "1.6" }],
        lg:    ["17px", { lineHeight: "1.5" }],
        xl:    ["20px", { lineHeight: "1.4" }],
        "2xl": ["24px", { lineHeight: "1.3" }],
        "3xl": ["32px", { lineHeight: "1.2" }],
        "4xl": ["48px", { lineHeight: "1.1" }],
        "5xl": ["64px", { lineHeight: "1.0" }],
      },

      // Spacing extras (4px base unit; Tailwind's default scale remains)
      spacing: {
        18: "72px",
        22: "88px",
      },

      // Border-radius — 4px max (CLAUDE.md hard rule)
      // md/lg/xl are intentionally absent — they exceed 4px
      borderRadius: {
        none:    "0px",
        sm:      "2px",
        DEFAULT: "4px",
      },

      // Letter spacing for ALL CAPS labels and tight headlines
      letterSpacing: {
        tightest: "-0.02em",
        wide:      "0.06em",
        widest:    "0.12em",
      },

      // Animations that carry information (no decorative motion)
      animation: {
        "pulse-border": "pulseBorder 2s ease-in-out infinite",
        "slide-in":     "slideIn 150ms ease",
        "fade-in":      "fadeIn 200ms ease",
        shimmer:        "shimmer 1.5s infinite",
      },

      keyframes: {
        pulseBorder: {
          "0%, 100%": { opacity: "1" },
          "50%":       { opacity: "0.4" },
        },
        slideIn: {
          from: { transform: "translateY(-8px)", opacity: "0" },
          to:   { transform: "translateY(0)",    opacity: "1" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to:   { opacity: "1" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition:  "200% 0" },
        },
      },

      // Max width for main content
      maxWidth: {
        content: "1400px",
      },

      // Nav height constant
      height: {
        nav: "48px",
      },
    },
  },

  plugins: [],
};
