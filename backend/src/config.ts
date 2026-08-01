// config.ts — loads required env vars from process.env via dotenv and fails fast (throws
// before the server binds) if any are missing. See plan.md §3.

import * as dotenv from "dotenv";

dotenv.config();

export interface Config {
  touchlessClientId: string;
  touchlessClientSecret: string;
  touchlessBaseUrl: string;
  port: number;
  requestTimeoutMs: number;
}

const REQUIRED_ENV_VARS = [
  "TOUCHLESS_CLIENT_ID",
  "TOUCHLESS_CLIENT_SECRET",
  "TOUCHLESS_BASE_URL",
  "PORT",
  "REQUEST_TIMEOUT_MS",
] as const;

function loadConfig(): Config {
  const missing = REQUIRED_ENV_VARS.filter((name) => !process.env[name]);
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variable(s): ${missing.join(", ")}. ` +
        "Copy backend/.env.example to backend/.env and fill in real values.",
    );
  }

  return {
    touchlessClientId: process.env.TOUCHLESS_CLIENT_ID as string,
    touchlessClientSecret: process.env.TOUCHLESS_CLIENT_SECRET as string,
    touchlessBaseUrl: process.env.TOUCHLESS_BASE_URL as string,
    port: Number(process.env.PORT),
    requestTimeoutMs: Number(process.env.REQUEST_TIMEOUT_MS),
  };
}

export const config: Config = loadConfig();
