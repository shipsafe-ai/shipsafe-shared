/**
 * TDD for deploy.ts — Cloud Run deployment helper.
 * Shells out to `gcloud` CLI. All exec calls are mocked.
 */

import { describe, it, expect } from "vitest";
import { buildCloudRunArgs, parseServiceUrl, DeployOptions } from "../deploy.js";

describe("buildCloudRunArgs", () => {
  const baseOpts: DeployOptions = {
    service: "routeforge",
    image: "us-central1-docker.pkg.dev/shipsafe/agents/routeforge:latest",
    region: "us-central1",
    project: "shipsafe-hackathon",
  };

  it("returns an array of gcloud args", () => {
    const args = buildCloudRunArgs(baseOpts);
    expect(Array.isArray(args)).toBe(true);
    expect(args.length).toBeGreaterThan(0);
  });

  it("includes service name", () => {
    const args = buildCloudRunArgs(baseOpts);
    expect(args).toContain("routeforge");
  });

  it("includes image flag", () => {
    const args = buildCloudRunArgs(baseOpts);
    const imgIdx = args.indexOf("--image");
    expect(imgIdx).toBeGreaterThan(-1);
    expect(args[imgIdx + 1]).toBe(baseOpts.image);
  });

  it("includes region flag", () => {
    const args = buildCloudRunArgs(baseOpts);
    const rIdx = args.indexOf("--region");
    expect(rIdx).toBeGreaterThan(-1);
    expect(args[rIdx + 1]).toBe("us-central1");
  });

  it("includes project flag", () => {
    const args = buildCloudRunArgs(baseOpts);
    const pIdx = args.indexOf("--project");
    expect(pIdx).toBeGreaterThan(-1);
    expect(args[pIdx + 1]).toBe("shipsafe-hackathon");
  });

  it("includes --allow-unauthenticated by default", () => {
    const args = buildCloudRunArgs(baseOpts);
    expect(args).toContain("--allow-unauthenticated");
  });

  it("includes --set-env-vars when envVars provided", () => {
    const args = buildCloudRunArgs({
      ...baseOpts,
      envVars: { FOO: "bar", BAZ: "qux" },
    });
    const evIdx = args.indexOf("--set-env-vars");
    expect(evIdx).toBeGreaterThan(-1);
    const evVal = args[evIdx + 1];
    expect(evVal).toContain("FOO=bar");
    expect(evVal).toContain("BAZ=qux");
  });

  it("includes --set-secrets when secrets provided", () => {
    const args = buildCloudRunArgs({
      ...baseOpts,
      secrets: ["DT_OTLP_TOKEN", "PHOENIX_API_KEY"],
    });
    const sIdx = args.indexOf("--set-secrets");
    expect(sIdx).toBeGreaterThan(-1);
    const sVal = args[sIdx + 1];
    expect(sVal).toContain("DT_OTLP_TOKEN");
    expect(sVal).toContain("PHOENIX_API_KEY");
  });

  it("includes --memory when provided", () => {
    const args = buildCloudRunArgs({ ...baseOpts, memory: "1Gi" });
    const mIdx = args.indexOf("--memory");
    expect(mIdx).toBeGreaterThan(-1);
    expect(args[mIdx + 1]).toBe("1Gi");
  });

  it("omits --memory when not provided", () => {
    const args = buildCloudRunArgs(baseOpts);
    expect(args).not.toContain("--memory");
  });
});

describe("parseServiceUrl", () => {
  it("extracts URL from gcloud deploy stdout", () => {
    const stdout = `Deploying container to Cloud Run service [routeforge] in project [shipsafe-hackathon]...
Service [routeforge] revision [routeforge-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://routeforge-abc123-uc.a.run.app`;
    expect(parseServiceUrl(stdout)).toBe(
      "https://routeforge-abc123-uc.a.run.app"
    );
  });

  it("returns null when no Service URL line present", () => {
    expect(parseServiceUrl("Deploying...")).toBeNull();
  });

  it("handles trailing whitespace", () => {
    const stdout = "Service URL: https://example.run.app  \n";
    expect(parseServiceUrl(stdout)).toBe("https://example.run.app");
  });
});
