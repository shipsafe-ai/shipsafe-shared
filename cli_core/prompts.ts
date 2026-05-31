/**
 * Interactive setup helpers for the ShipSafe agent CLIs.
 *
 * Pure output formatters and validators are synchronous and testable.
 * readline-dependent functions (promptGcpConfig, promptSecrets, promptConfirm)
 * are thin wrappers — tested via integration tests, not unit tests.
 */

import * as readline from "node:readline";

// ---------------------------------------------------------------------------
// Pure formatters (exported for unit tests)
// ---------------------------------------------------------------------------

export function formatStep(
  step: number,
  total: number,
  message: string
): string {
  return `[${step}/${total}] ${message}`;
}

export function formatSuccess(message: string): string {
  return `✓ ${message}`;
}

export function formatError(message: string): string {
  return `✗ ${message}`;
}

export function formatWarning(message: string): string {
  return `⚠ ${message}`;
}

// ---------------------------------------------------------------------------
// Pure validators — return null on success, error string on failure
// ---------------------------------------------------------------------------

const GCP_PROJECT_RE = /^[a-z][a-z0-9\-]{4,28}[a-z0-9]$/;

export function validateGcpProject(value: string): string | null {
  if (!value) return "Project ID is required";
  if (!GCP_PROJECT_RE.test(value))
    return "Invalid GCP project ID (lowercase letters, digits, hyphens; must start with a letter)";
  return null;
}

const KNOWN_REGIONS = new Set([
  "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3",
  "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
  "europe-north1",
  "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2",
  "asia-northeast3", "asia-south1", "asia-southeast1", "asia-southeast2",
  "australia-southeast1", "southamerica-east1",
]);

export function validateGcpRegion(value: string): string | null {
  if (!value) return "Region is required";
  if (!KNOWN_REGIONS.has(value))
    return `Unknown region "${value}". Example valid regions: us-central1, europe-west1, asia-east1`;
  return null;
}

// ---------------------------------------------------------------------------
// Secret masking
// ---------------------------------------------------------------------------

export function maskSecret(value: string): string {
  if (!value) return "(empty)";
  if (value.length <= 4) return "****";
  return `${"*".repeat(value.length - 4)}${value.slice(-4)}`;
}

/**
 * Build the --set-secrets mount spec for a single secret.
 * Format Cloud Run expects: ENV_VAR=secret-name:version
 */
export function buildSecretMountSpec(secretName: string): string {
  return `${secretName}=${secretName}:latest`;
}

// ---------------------------------------------------------------------------
// Interactive prompts (readline-dependent, not unit tested)
// ---------------------------------------------------------------------------

export interface GcpConfig {
  project: string;
  region: string;
}

function question(rl: readline.Interface, prompt: string): Promise<string> {
  return new Promise((resolve) => rl.question(prompt, resolve));
}

export async function promptGcpConfig(): Promise<GcpConfig> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  try {
    let project = "";
    while (true) {
      project = (await question(rl, "GCP project ID: ")).trim();
      const err = validateGcpProject(project);
      if (!err) break;
      console.error(formatError(err));
    }

    let region = "";
    while (true) {
      region = (
        await question(rl, "GCP region [us-central1]: ")
      ).trim() || "us-central1";
      const err = validateGcpRegion(region);
      if (!err) break;
      console.error(formatError(err));
    }

    return { project, region };
  } finally {
    rl.close();
  }
}

export async function promptSecrets(
  required: string[]
): Promise<Record<string, string>> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const result: Record<string, string> = {};
  try {
    for (const name of required) {
      let value = "";
      while (!value) {
        value = (await question(rl, `${name}: `)).trim();
        if (!value) console.error(formatError("Value is required"));
      }
      result[name] = value;
      console.log(formatSuccess(`${name} = ${maskSecret(value)}`));
    }
  } finally {
    rl.close();
  }
  return result;
}

export async function promptConfirm(message: string): Promise<boolean> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  try {
    const answer = (await question(rl, `${message} [y/N]: `)).trim().toLowerCase();
    return answer === "y" || answer === "yes";
  } finally {
    rl.close();
  }
}

export function printStep(step: number, total: number, message: string): void {
  console.log(formatStep(step, total, message));
}

export function printSuccess(message: string): void {
  console.log(formatSuccess(message));
}

export function printError(message: string): void {
  console.error(formatError(message));
}

export function printWarning(message: string): void {
  console.warn(formatWarning(message));
}
