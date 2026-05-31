/**
 * GCP Secret Manager helper.
 * Wraps `gcloud secrets` — no Google Cloud SDK dependency required.
 */

import { exec } from "node:child_process";
import { promisify } from "node:util";

const execPromise = promisify(exec);

export async function _execAsync(
  cmd: string
): Promise<{ stdout: string; stderr: string }> {
  return execPromise(cmd);
}

// ---------------------------------------------------------------------------
// Argument builders (pure — exported for unit tests)
// ---------------------------------------------------------------------------

export function buildGetSecretArgs(name: string, project: string): string[] {
  return [
    "secrets", "versions", "access", "latest",
    "--secret",  name,
    "--project", project,
  ];
}

export function buildSetSecretArgs(
  name: string,
  _value: string,
  project: string
): { createArgs: string[]; addVersionArgs: string[] } {
  return {
    createArgs: [
      "secrets", "create", name,
      "--project",      project,
      "--replication-policy", "automatic",
    ],
    addVersionArgs: [
      "secrets", "versions", "add", name,
      "--project", project,
      "--data-file", "-",  // reads value from stdin
    ],
  };
}

export function buildListSecretsArgs(
  project: string,
  prefix?: string
): string[] {
  const args = [
    "secrets", "list",
    "--project", project,
    "--format",  "table(name)",
  ];
  if (prefix) {
    args.push("--filter", `name:${prefix}`);
  }
  return args;
}

// ---------------------------------------------------------------------------
// Output parsers (pure)
// ---------------------------------------------------------------------------

export function parseSecretValue(stdout: string): string {
  return stdout.trim();
}

export function parseSecretNames(stdout: string): string[] {
  const lines = stdout.trim().split("\n");
  if (lines.length <= 1) return [];
  // First line is the header (NAME ...), skip it
  return lines
    .slice(1)
    .map((l) => l.trim().split(/\s+/)[0])
    .filter(Boolean);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function getSecret(
  name: string,
  project: string
): Promise<string> {
  const args = buildGetSecretArgs(name, project);
  const { stdout } = await _execAsync(`gcloud ${args.join(" ")}`);
  return parseSecretValue(stdout);
}

export async function setSecret(
  name: string,
  value: string,
  project: string
): Promise<void> {
  const { createArgs, addVersionArgs } = buildSetSecretArgs(name, value, project);
  // Create secret if it doesn't exist (ignore error if already exists)
  try {
    await _execAsync(`gcloud ${createArgs.join(" ")}`);
  } catch {
    // Secret already exists — proceed to add version
  }
  // Pipe value via stdin to avoid shell quoting issues with token values
  const addCmd = `echo -n '${value.replace(/'/g, "'\\''")}' | gcloud ${addVersionArgs.join(" ")}`;
  await _execAsync(addCmd);
}

export async function secretExists(
  name: string,
  project: string
): Promise<boolean> {
  try {
    await _execAsync(
      `gcloud secrets describe ${name} --project ${project} --quiet`
    );
    return true;
  } catch {
    return false;
  }
}

export async function listSecrets(
  project: string,
  prefix?: string
): Promise<string[]> {
  const args = buildListSecretsArgs(project, prefix);
  const { stdout } = await _execAsync(`gcloud ${args.join(" ")}`);
  return parseSecretNames(stdout);
}
