/**
 * Post-deploy health check helper.
 * Polls the deployed Cloud Run service until it responds healthy or times out.
 * Uses native fetch (Node 18+) — no extra dependencies.
 */

export interface HealthCheckOptions {
  url: string;
  timeout?: number;   // ms, default 180_000 (3 min — Cloud Run cold-start budget)
  interval?: number;  // ms between polls, default 5_000
  path?: string;      // health endpoint, default "/health"
}

export interface HealthResult {
  healthy: boolean;
  url: string;
  latencyMs: number;
  statusCode?: number;
  error?: string;
}

// ---------------------------------------------------------------------------
// Pure helpers (exported for unit tests)
// ---------------------------------------------------------------------------

export function buildHealthUrl(baseUrl: string, path = "/health"): string {
  const trimmed = baseUrl.replace(/\/$/, "");
  const safePath = path.startsWith("/") ? path : `/${path}`;
  return `${trimmed}${safePath}`;
}

export function parseHealthResponse(
  statusCode: number,
  latencyMs: number
): HealthResult {
  const url = "";
  const healthy = statusCode >= 200 && statusCode < 300;
  return {
    healthy,
    url,
    latencyMs,
    statusCode,
    ...(healthy ? {} : { error: `HTTP ${statusCode}` }),
  };
}

export function isRetryableStatus(statusCode: number): boolean {
  // Cloud Run service starting up returns 404/502/503 transiently
  return [404, 502, 503, 504].includes(statusCode);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function checkHealth(
  url: string,
  path = "/health"
): Promise<HealthResult> {
  const healthUrl = buildHealthUrl(url, path);
  const t0 = Date.now();
  try {
    const res = await fetch(healthUrl, { method: "GET" });
    const latencyMs = Date.now() - t0;
    const result = parseHealthResponse(res.status, latencyMs);
    return { ...result, url: healthUrl };
  } catch (err) {
    return {
      healthy: false,
      url: healthUrl,
      latencyMs: Date.now() - t0,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

export async function waitForHealthy(
  opts: HealthCheckOptions
): Promise<HealthResult> {
  const {
    url,
    timeout = 180_000,
    interval = 5_000,
    path = "/health",
  } = opts;

  const deadline = Date.now() + timeout;

  while (Date.now() < deadline) {
    const result = await checkHealth(url, path);
    if (result.healthy) return result;
    if (
      result.statusCode !== undefined &&
      !isRetryableStatus(result.statusCode)
    ) {
      // Non-transient error — fail fast
      return result;
    }
    const remaining = deadline - Date.now();
    if (remaining <= 0) break;
    await new Promise((r) => setTimeout(r, Math.min(interval, remaining)));
  }

  return {
    healthy: false,
    url: buildHealthUrl(url, path),
    latencyMs: timeout,
    error: `Timed out after ${timeout}ms waiting for ${url} to become healthy`,
  };
}
