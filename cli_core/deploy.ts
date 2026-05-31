/**
 * Cloud Run deployment helper.
 * Wraps `gcloud run deploy` — all heavy lifting stays in the gcloud CLI,
 * no GCP SDK dependency required in agent repos.
 */

import { exec } from "node:child_process";
import { promisify } from "node:util";

const execPromise = promisify(exec);

// Exported for mocking in tests only — not part of the public API.
export async function _execAsync(
  cmd: string
): Promise<{ stdout: string; stderr: string }> {
  return execPromise(cmd);
}

export interface DeployOptions {
  service: string;
  image: string;
  region: string;
  project: string;
  envVars?: Record<string, string>;
  secrets?: string[];
  memory?: string;
  cpu?: string;
}

export interface DeployResult {
  url: string;
  service: string;
  region: string;
}

/**
 * Build the gcloud run deploy argument list from options.
 * Pure function — exported for unit testing without spawning gcloud.
 */
export function buildCloudRunArgs(opts: DeployOptions): string[] {
  const args: string[] = [
    "run", "deploy", opts.service,
    "--image",   opts.image,
    "--region",  opts.region,
    "--project", opts.project,
    "--platform", "managed",
    "--allow-unauthenticated",
    "--quiet",
  ];

  if (opts.envVars && Object.keys(opts.envVars).length > 0) {
    const pairs = Object.entries(opts.envVars)
      .map(([k, v]) => `${k}=${v}`)
      .join(",");
    args.push("--set-env-vars", pairs);
  }

  if (opts.secrets && opts.secrets.length > 0) {
    const mounts = opts.secrets
      .map((name) => `${name}=${name}:latest`)
      .join(",");
    args.push("--set-secrets", mounts);
  }

  if (opts.memory) {
    args.push("--memory", opts.memory);
  }

  if (opts.cpu) {
    args.push("--cpu", opts.cpu);
  }

  return args;
}

/**
 * Extract the Service URL from `gcloud run deploy` stdout.
 * Returns null if the line is not present (parse-safe — caller retries/errors).
 */
export function parseServiceUrl(stdout: string): string | null {
  for (const line of stdout.split("\n")) {
    if (line.startsWith("Service URL:")) {
      return line.replace("Service URL:", "").trim();
    }
  }
  return null;
}

/**
 * Deploy an image to Cloud Run and return the service URL.
 */
export async function deployToCloudRun(
  opts: DeployOptions
): Promise<DeployResult> {
  const args = buildCloudRunArgs(opts);
  const cmd = `gcloud ${args.join(" ")}`;
  const { stdout } = await _execAsync(cmd);
  const url = parseServiceUrl(stdout);
  if (!url) {
    throw new Error(
      `Could not parse Service URL from gcloud output:\n${stdout}`
    );
  }
  return { url, service: opts.service, region: opts.region };
}

/**
 * Build and push a Docker image to Artifact Registry.
 * Returns the full image URI.
 */
export async function buildAndPush(
  imageName: string,
  contextPath: string
): Promise<string> {
  await _execAsync(`docker build -t ${imageName} ${contextPath}`);
  await _execAsync(`docker push ${imageName}`);
  return imageName;
}

/**
 * Delete a Cloud Run service.
 */
export async function destroyService(
  service: string,
  region: string,
  project: string
): Promise<void> {
  await _execAsync(
    `gcloud run services delete ${service} --region ${region} --project ${project} --quiet`
  );
}
