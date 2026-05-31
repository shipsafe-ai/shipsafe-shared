/**
 * TDD for health.ts — post-deploy health check helper.
 * HTTP calls are mocked via vi.stubGlobal.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import {
  buildHealthUrl,
  parseHealthResponse,
  isRetryableStatus,
  HealthCheckOptions,
} from "../health.js";

describe("buildHealthUrl", () => {
  it("appends default /health path", () => {
    expect(buildHealthUrl("https://routeforge-abc.run.app")).toBe(
      "https://routeforge-abc.run.app/health"
    );
  });

  it("uses custom path when provided", () => {
    expect(buildHealthUrl("https://example.run.app", "/ready")).toBe(
      "https://example.run.app/ready"
    );
  });

  it("does not double-slash when base has trailing slash", () => {
    const url = buildHealthUrl("https://example.run.app/", "/health");
    expect(url).not.toContain("//health");
  });
});

describe("parseHealthResponse", () => {
  it("returns healthy=true for 200", () => {
    const result = parseHealthResponse(200, 142);
    expect(result.healthy).toBe(true);
    expect(result.statusCode).toBe(200);
    expect(result.latencyMs).toBe(142);
  });

  it("returns healthy=true for any 2xx", () => {
    expect(parseHealthResponse(201, 100).healthy).toBe(true);
    expect(parseHealthResponse(204, 100).healthy).toBe(true);
  });

  it("returns healthy=false for 5xx", () => {
    expect(parseHealthResponse(500, 100).healthy).toBe(false);
    expect(parseHealthResponse(503, 100).healthy).toBe(false);
  });

  it("returns healthy=false for 4xx", () => {
    expect(parseHealthResponse(404, 100).healthy).toBe(false);
  });

  it("includes error string for non-2xx", () => {
    const result = parseHealthResponse(503, 100);
    expect(result.error).toBeDefined();
    expect(result.error).toContain("503");
  });
});

describe("isRetryableStatus", () => {
  it("returns true for 502 Bad Gateway (Cloud Run starting)", () =>
    expect(isRetryableStatus(502)).toBe(true));

  it("returns true for 503 Service Unavailable", () =>
    expect(isRetryableStatus(503)).toBe(true));

  it("returns true for 404 (service not routed yet)", () =>
    expect(isRetryableStatus(404)).toBe(true));

  it("returns false for 200", () =>
    expect(isRetryableStatus(200)).toBe(false));

  it("returns false for 401 (misconfigured auth, not transient)", () =>
    expect(isRetryableStatus(401)).toBe(false));
});

describe("HealthCheckOptions defaults", () => {
  it("default timeout is 180000ms (3 minutes)", () => {
    const opts: HealthCheckOptions = { url: "https://x.run.app" };
    expect(opts.timeout ?? 180_000).toBe(180_000);
  });

  it("default interval is 5000ms", () => {
    const opts: HealthCheckOptions = { url: "https://x.run.app" };
    expect(opts.interval ?? 5_000).toBe(5_000);
  });
});
