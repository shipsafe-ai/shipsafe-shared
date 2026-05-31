/**
 * TDD for secrets.ts — GCP Secret Manager helper.
 * All gcloud calls are mocked.
 */

import { describe, it, expect } from "vitest";
import {
  buildGetSecretArgs,
  buildSetSecretArgs,
  buildListSecretsArgs,
  parseSecretValue,
  parseSecretNames,
} from "../secrets.js";

const PROJECT = "shipsafe-hackathon";

describe("buildGetSecretArgs", () => {
  it("includes secret name and latest version", () => {
    const args = buildGetSecretArgs("PHOENIX_API_KEY", PROJECT);
    expect(args.join(" ")).toContain("PHOENIX_API_KEY");
    expect(args.join(" ")).toContain("latest");
  });

  it("includes project flag", () => {
    const args = buildGetSecretArgs("FOO", PROJECT);
    const pIdx = args.indexOf("--project");
    expect(pIdx).toBeGreaterThan(-1);
    expect(args[pIdx + 1]).toBe(PROJECT);
  });

  it("uses versions access-secrets subcommand", () => {
    const args = buildGetSecretArgs("FOO", PROJECT);
    expect(args).toContain("secrets");
    expect(args).toContain("versions");
    expect(args).toContain("access");
  });
});

describe("buildSetSecretArgs", () => {
  it("creates a new secret if it does not exist", () => {
    const { createArgs } = buildSetSecretArgs("MY_SECRET", "my-value", PROJECT);
    expect(createArgs.join(" ")).toContain("create");
    expect(createArgs.join(" ")).toContain("MY_SECRET");
  });

  it("project flag included in create args", () => {
    const { createArgs } = buildSetSecretArgs("MY_SECRET", "my-value", PROJECT);
    const pIdx = createArgs.indexOf("--project");
    expect(pIdx).toBeGreaterThan(-1);
    expect(createArgs[pIdx + 1]).toBe(PROJECT);
  });

  it("returns addVersionArgs for adding version", () => {
    const { addVersionArgs } = buildSetSecretArgs("MY_SECRET", "my-value", PROJECT);
    expect(addVersionArgs.join(" ")).toContain("versions");
    expect(addVersionArgs.join(" ")).toContain("add");
  });
});

describe("buildListSecretsArgs", () => {
  it("lists secrets in project", () => {
    const args = buildListSecretsArgs(PROJECT);
    expect(args).toContain("secrets");
    expect(args).toContain("list");
    const pIdx = args.indexOf("--project");
    expect(pIdx).toBeGreaterThan(-1);
  });

  it("includes filter when prefix provided", () => {
    const args = buildListSecretsArgs(PROJECT, "SHIPSAFE_");
    const fIdx = args.indexOf("--filter");
    expect(fIdx).toBeGreaterThan(-1);
    expect(args[fIdx + 1]).toContain("SHIPSAFE_");
  });
});

describe("parseSecretValue", () => {
  it("returns trimmed stdout", () => {
    expect(parseSecretValue("  my-secret-value\n")).toBe("my-secret-value");
  });

  it("returns empty string for empty stdout", () => {
    expect(parseSecretValue("")).toBe("");
  });
});

describe("parseSecretNames", () => {
  it("extracts secret names from gcloud list output", () => {
    const stdout = `NAME              CREATED              REPLICATION_POLICY
PHOENIX_API_KEY   2026-05-29T10:00:00  automatic
DT_OTLP_TOKEN     2026-05-29T10:01:00  automatic`;
    const names = parseSecretNames(stdout);
    expect(names).toContain("PHOENIX_API_KEY");
    expect(names).toContain("DT_OTLP_TOKEN");
  });

  it("returns empty array for empty output", () => {
    expect(parseSecretNames("")).toHaveLength(0);
  });

  it("skips the header line", () => {
    const stdout = "NAME\nMY_SECRET";
    const names = parseSecretNames(stdout);
    expect(names).not.toContain("NAME");
    expect(names).toContain("MY_SECRET");
  });
});
