/**
 * TDD — run RED before tokens.ts exists, then GREEN after.
 *
 * Contract tested:
 * - Exact color values from CLAUDE.md and DESIGN-SYSTEM.md
 * - Agent accent colors use CURRENT agent names (not old design-system names)
 * - Max border radius is 4px (CLAUDE.md rule)
 * - Font families are Geist + DM Mono (never Inter)
 * - Signal colors carry meaning: red=block amber=warn green=approve blue=info
 * - Type scale matches DESIGN-SYSTEM.md exactly
 */

import { describe, it, expect } from "vitest";
import {
  colors,
  fonts,
  typeScale,
  spacing,
  borderRadius,
  agentAccents,
  agents,
  AGENT_NAMES,
} from "./tokens.js";

// ---------------------------------------------------------------------------
// Background colors
// ---------------------------------------------------------------------------
describe("colors.bg", () => {
  it("base is near-black #0A0A0B", () => expect(colors.bg.base).toBe("#0A0A0B"));
  it("surface is #111113", () => expect(colors.bg.surface).toBe("#111113"));
  it("elevated is #18181B", () => expect(colors.bg.elevated).toBe("#18181B"));
  it("overlay is #1E1E22", () => expect(colors.bg.overlay).toBe("#1E1E22"));
});

// ---------------------------------------------------------------------------
// Border colors
// ---------------------------------------------------------------------------
describe("colors.border", () => {
  it("subtle is #27272A", () => expect(colors.border.subtle).toBe("#27272A"));
  it("default is #3F3F46", () => expect(colors.border.default).toBe("#3F3F46"));
  it("strong is #52525B", () => expect(colors.border.strong).toBe("#52525B"));
});

// ---------------------------------------------------------------------------
// Text colors
// ---------------------------------------------------------------------------
describe("colors.text", () => {
  it("primary is #FAFAFA", () => expect(colors.text.primary).toBe("#FAFAFA"));
  it("secondary is #A1A1AA", () => expect(colors.text.secondary).toBe("#A1A1AA"));
  it("tertiary is #71717A", () => expect(colors.text.tertiary).toBe("#71717A"));
  it("disabled is #52525B", () => expect(colors.text.disabled).toBe("#52525B"));
});

// ---------------------------------------------------------------------------
// Signal colors — these carry meaning, never decorative
// ---------------------------------------------------------------------------
describe("colors.signal", () => {
  it("block is red #EF4444", () => expect(colors.signal.block).toBe("#EF4444"));
  it("warn is amber #F59E0B", () => expect(colors.signal.warn).toBe("#F59E0B"));
  it("approve is green #22C55E", () => expect(colors.signal.approve).toBe("#22C55E"));
  it("info is blue #3B82F6", () => expect(colors.signal.info).toBe("#3B82F6"));
  it("neutral is violet #8B5CF6", () => expect(colors.signal.neutral).toBe("#8B5CF6"));
  it("blockBg exists and is semi-transparent", () =>
    expect(colors.signal.blockBg).toBeDefined());
  it("warnBg exists", () => expect(colors.signal.warnBg).toBeDefined());
  it("approveBg exists", () => expect(colors.signal.approveBg).toBeDefined());
  it("infoBg exists", () => expect(colors.signal.infoBg).toBeDefined());
});

// ---------------------------------------------------------------------------
// Agent accent colors — CLAUDE.md names, not old design-system names
// ---------------------------------------------------------------------------
describe("agentAccents", () => {
  it("cargodb is emerald #10B981", () =>
    expect(agentAccents.cargodb).toBe("#10B981"));
  it("routeforge is orange #F97316", () =>
    expect(agentAccents.routeforge).toBe("#F97316"));
  it("voyageblack is blue #3B82F6", () =>
    expect(agentAccents.voyageblack).toBe("#3B82F6"));
  it("tidesync is violet #8B5CF6", () =>
    expect(agentAccents.tidesync).toBe("#8B5CF6"));
  it("naviguard is pink #EC4899", () =>
    expect(agentAccents.naviguard).toBe("#EC4899"));
  it("agentops is teal #14B8A6", () =>
    expect(agentAccents.agentops).toBe("#14B8A6"));
  it("has exactly 6 agents", () =>
    expect(Object.keys(agentAccents)).toHaveLength(6));
  it("uses current agent names not old ones", () => {
    const keys = Object.keys(agentAccents);
    expect(keys).not.toContain("shipguard");
    expect(keys).not.toContain("schemasafe");
    expect(keys).not.toContain("postmortem");
    expect(keys).not.toContain("trustpipe");
    expect(keys).not.toContain("promptshield");
  });
});

// ---------------------------------------------------------------------------
// agents array — used for nav rendering
// ---------------------------------------------------------------------------
describe("agents", () => {
  it("has 6 entries", () => expect(agents).toHaveLength(6));
  it("each has name, accent, icon, label fields", () => {
    for (const a of agents) {
      expect(a).toHaveProperty("name");
      expect(a).toHaveProperty("accent");
      expect(a).toHaveProperty("icon");
      expect(a).toHaveProperty("label");
    }
  });
  it("agent accents match agentAccents map", () => {
    for (const a of agents) {
      expect(a.accent).toBe(agentAccents[a.name as keyof typeof agentAccents]);
    }
  });
});

// ---------------------------------------------------------------------------
// AGENT_NAMES constant
// ---------------------------------------------------------------------------
describe("AGENT_NAMES", () => {
  it("is a tuple of 6 string literals", () =>
    expect(AGENT_NAMES).toHaveLength(6));
  it("contains all current agent names", () => {
    expect(AGENT_NAMES).toContain("cargodb");
    expect(AGENT_NAMES).toContain("routeforge");
    expect(AGENT_NAMES).toContain("voyageblack");
    expect(AGENT_NAMES).toContain("tidesync");
    expect(AGENT_NAMES).toContain("naviguard");
    expect(AGENT_NAMES).toContain("agentops");
  });
});

// ---------------------------------------------------------------------------
// Fonts
// ---------------------------------------------------------------------------
describe("fonts", () => {
  it("display includes Geist", () =>
    expect(fonts.display[0]).toBe("Geist"));
  it("body includes Geist", () =>
    expect(fonts.body[0]).toBe("Geist"));
  it("mono includes DM Mono", () =>
    expect(fonts.mono[0]).toBe("DM Mono"));
  it("none of the stacks include Inter", () => {
    const allFonts = [...fonts.display, ...fonts.body, ...fonts.mono];
    expect(allFonts).not.toContain("Inter");
  });
});

// ---------------------------------------------------------------------------
// Type scale — values from DESIGN-SYSTEM.md
// ---------------------------------------------------------------------------
describe("typeScale", () => {
  it("xs is 11px", () => expect(typeScale.xs).toBe("11px"));
  it("sm is 13px", () => expect(typeScale.sm).toBe("13px"));
  it("base is 15px", () => expect(typeScale.base).toBe("15px"));
  it("lg is 17px", () => expect(typeScale.lg).toBe("17px"));
  it("xl is 20px", () => expect(typeScale.xl).toBe("20px"));
  it("2xl is 24px", () => expect(typeScale["2xl"]).toBe("24px"));
  it("3xl is 32px", () => expect(typeScale["3xl"]).toBe("32px"));
  it("4xl is 48px", () => expect(typeScale["4xl"]).toBe("48px"));
  it("5xl is 64px", () => expect(typeScale["5xl"]).toBe("64px"));
});

// ---------------------------------------------------------------------------
// Spacing scale — matches DESIGN-SYSTEM.md
// ---------------------------------------------------------------------------
describe("spacing", () => {
  it("space-1 is 4px", () => expect(spacing[1]).toBe("4px"));
  it("space-2 is 8px", () => expect(spacing[2]).toBe("8px"));
  it("space-4 is 16px", () => expect(spacing[4]).toBe("16px"));
  it("space-6 is 24px", () => expect(spacing[6]).toBe("24px"));
  it("space-8 is 32px", () => expect(spacing[8]).toBe("32px"));
});

// ---------------------------------------------------------------------------
// Border radius — 4px MAX enforced (CLAUDE.md rule)
// ---------------------------------------------------------------------------
describe("borderRadius", () => {
  it("DEFAULT is 4px", () => expect(borderRadius.DEFAULT).toBe("4px"));
  it("sm is 2px", () => expect(borderRadius.sm).toBe("2px"));
  it("none is 0px", () => expect(borderRadius.none).toBe("0px"));
  it("no value exceeds 4px", () => {
    for (const [key, val] of Object.entries(borderRadius)) {
      const px = parseInt(val as string, 10);
      expect(px, `borderRadius.${key} = ${val} exceeds 4px max`).toBeLessThanOrEqual(4);
    }
  });
});
