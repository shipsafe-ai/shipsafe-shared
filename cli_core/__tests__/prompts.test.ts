/**
 * TDD for prompts.ts — interactive setup helpers.
 * Tests the pure/synchronous parts (formatters, validators).
 * Readline-dependent functions (promptGcpConfig etc.) are integration-tested
 * separately since they require a TTY.
 */

import { describe, it, expect } from "vitest";

import {
  formatStep,
  formatSuccess,
  formatError,
  formatWarning,
  validateGcpProject,
  validateGcpRegion,
  maskSecret,
  buildSecretMountSpec,
} from "../prompts.js";

describe("formatStep", () => {
  it("formats step counter as [n/total]", () => {
    expect(formatStep(1, 5, "Installing deps")).toContain("[1/5]");
  });

  it("includes the message", () => {
    expect(formatStep(2, 4, "Deploying to Cloud Run")).toContain(
      "Deploying to Cloud Run"
    );
  });
});

describe("formatSuccess", () => {
  it("returns a non-empty string", () => {
    expect(formatSuccess("Deployed successfully").length).toBeGreaterThan(0);
  });

  it("includes the message", () => {
    expect(formatSuccess("Agent is live")).toContain("Agent is live");
  });
});

describe("formatError", () => {
  it("includes the error message", () => {
    expect(formatError("Secret not found")).toContain("Secret not found");
  });
});

describe("formatWarning", () => {
  it("includes the warning message", () => {
    expect(formatWarning("Token may be expired")).toContain(
      "Token may be expired"
    );
  });
});

describe("validateGcpProject", () => {
  it("accepts valid project IDs", () => {
    expect(validateGcpProject("shipsafe-hackathon")).toBeNull();
    expect(validateGcpProject("my-project-123")).toBeNull();
  });

  it("rejects empty string", () => {
    expect(validateGcpProject("")).not.toBeNull();
  });

  it("rejects IDs with uppercase", () => {
    expect(validateGcpProject("MyProject")).not.toBeNull();
  });

  it("rejects IDs with spaces", () => {
    expect(validateGcpProject("my project")).not.toBeNull();
  });

  it("rejects IDs that start with a number", () => {
    expect(validateGcpProject("1badproject")).not.toBeNull();
  });
});

describe("validateGcpRegion", () => {
  it("accepts known GCP regions", () => {
    expect(validateGcpRegion("us-central1")).toBeNull();
    expect(validateGcpRegion("europe-west1")).toBeNull();
    expect(validateGcpRegion("asia-east1")).toBeNull();
  });

  it("rejects empty string", () => {
    expect(validateGcpRegion("")).not.toBeNull();
  });

  it("rejects nonsense strings", () => {
    expect(validateGcpRegion("not-a-region")).not.toBeNull();
  });
});

describe("maskSecret", () => {
  it("shows only last 4 chars", () => {
    const masked = maskSecret("supersecretvalue1234");
    expect(masked).toContain("1234");
    expect(masked).not.toContain("supersecretvalue");
  });

  it("masks short secrets entirely", () => {
    const masked = maskSecret("abc");
    expect(masked).not.toContain("abc");
  });

  it("returns placeholder for empty string", () => {
    expect(maskSecret("")).toBe("(empty)");
  });
});

describe("buildSecretMountSpec", () => {
  it("formats secret as ENV_VAR=secret-name:latest", () => {
    const spec = buildSecretMountSpec("DT_OTLP_TOKEN");
    expect(spec).toBe("DT_OTLP_TOKEN=DT_OTLP_TOKEN:latest");
  });

  it("handles multiple secrets as comma-separated string", () => {
    const spec = ["PHOENIX_API_KEY", "DT_OTLP_TOKEN"]
      .map(buildSecretMountSpec)
      .join(",");
    expect(spec).toContain("PHOENIX_API_KEY=PHOENIX_API_KEY:latest");
    expect(spec).toContain("DT_OTLP_TOKEN=DT_OTLP_TOKEN:latest");
  });
});
