import { promises as fs } from "node:fs";
import path from "node:path";

import {
  isConfigured,
  parseConfig,
  resolveAccessToken,
  withConfigPatch,
} from "./config.js";
import type {
  ControllerSnapshot,
  BrowserAuthSession,
  ChekCliConfig,
} from "./types.js";
import type { OpenClawPluginApi } from "./openclaw-types.js";

type Logger = {
  debug?: (message: string) => void;
  info: (message: string) => void;
  warn: (message: string) => void;
  error: (message: string) => void;
};

const PLUGIN_CONFIG_KEY = "chek-cli";
const LEGACY_PLUGIN_CONFIG_KEY = "memor-upload";
const STATUS_FILE_NAME = "chek-cli-status.json";
const RETIRED_BRIDGE_MESSAGE =
  "站内 Agent 执行、专用授权和房间自动回复已退役；请使用 Python CHEK CLI 连接自己的 Agent 工具。";

function nowIso(): string {
  return new Date().toISOString();
}

function summarizeError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export class ChekCliController {
  private config: ChekCliConfig;
  private readonly runtimeConfig: OpenClawPluginApi["runtime"]["config"];
  private readonly snapshot: ControllerSnapshot;
  private stateDir: string | null = null;

  constructor(params: {
    config: ChekCliConfig;
    logger: Logger;
    runtimeConfig: OpenClawPluginApi["runtime"]["config"];
  }) {
    this.config = params.config;
    this.runtimeConfig = params.runtimeConfig;
    this.snapshot = {
      running: false,
      configured: isConfigured(params.config),
      backendAppBaseUrl: params.config.backendAppBaseUrl,
      pollIntervalMs: params.config.pollIntervalMs,
      sessionKey: params.config.sessionKey,
      accessTokenConfigured: Boolean(resolveAccessToken(params.config)),
      installId: params.config.installId,
      deviceId: params.config.deviceId,
      authSessionId: params.config.authSessionId || null,
      authorizationStatus: params.config.authorizationStatus || "",
      authorizationUrl: params.config.authorizationUrl || null,
      authorizedUserOneId: params.config.authorizedUserOneId || null,
      authorizedDisplayName: params.config.authorizedDisplayName || null,
      lastAuthorizedAt: params.config.lastAuthorizedAt || null,
      lastPollAt: null,
      lastSuccessAt: null,
      lastTaskAt: null,
      lastTaskId: null,
      lastError: null,
    };
  }

  attachStateDir(stateDir: string): void {
    this.stateDir = stateDir;
  }

  getSnapshot(): ControllerSnapshot {
    return { ...this.snapshot };
  }

  getConfig(): ChekCliConfig {
    return { ...this.config };
  }

  async start(): Promise<void> {
    // The root TypeScript package remains as a migration shim. It must never
    // poll the retired hosted Agent endpoints or create a browser-auth session.
    this.snapshot.running = false;
    this.snapshot.lastError = RETIRED_BRIDGE_MESSAGE;
    await this.persistSnapshot();
  }

  async stop(): Promise<void> {
    this.snapshot.running = false;
    await this.persistSnapshot();
  }

  async updateConfig(config: ChekCliConfig): Promise<void> {
    this.config = config;
    this.snapshot.configured = isConfigured(config);
    this.snapshot.backendAppBaseUrl = config.backendAppBaseUrl;
    this.snapshot.pollIntervalMs = config.pollIntervalMs;
    this.snapshot.sessionKey = config.sessionKey;
    this.snapshot.accessTokenConfigured = Boolean(resolveAccessToken(config));
    this.snapshot.installId = config.installId;
    this.snapshot.deviceId = config.deviceId;
    this.snapshot.authSessionId = config.authSessionId || null;
    this.snapshot.authorizationStatus = config.authorizationStatus || "";
    this.snapshot.authorizationUrl = config.authorizationUrl || null;
    this.snapshot.authorizedUserOneId = config.authorizedUserOneId || null;
    this.snapshot.authorizedDisplayName = config.authorizedDisplayName || null;
    this.snapshot.lastAuthorizedAt = config.lastAuthorizedAt || null;
    this.snapshot.lastError = null;
    await this.persistSnapshot();
  }

  async persistConfigPatch(patch: Partial<ChekCliConfig>): Promise<ChekCliConfig> {
    const currentConfig = this.runtimeConfig.loadConfig();
    const plugins = (currentConfig.plugins ?? {}) as Record<string, unknown>;
    const entries =
      plugins.entries && typeof plugins.entries === "object" && !Array.isArray(plugins.entries)
        ? ({ ...(plugins.entries as Record<string, unknown>) } as Record<string, unknown>)
        : {};
    const existingEntry =
      entries[PLUGIN_CONFIG_KEY] && typeof entries[PLUGIN_CONFIG_KEY] === "object"
        ? (entries[PLUGIN_CONFIG_KEY] as Record<string, unknown>)
        : entries[LEGACY_PLUGIN_CONFIG_KEY] && typeof entries[LEGACY_PLUGIN_CONFIG_KEY] === "object"
          ? (entries[LEGACY_PLUGIN_CONFIG_KEY] as Record<string, unknown>)
        : {};
    const existingPluginConfig = parseConfig(existingEntry.config);
    const nextPluginConfig = withConfigPatch(existingPluginConfig, patch);

    entries[PLUGIN_CONFIG_KEY] = {
      ...existingEntry,
      enabled: nextPluginConfig.enabled,
      config: nextPluginConfig,
    };

    await this.runtimeConfig.writeConfigFile({
      ...currentConfig,
      plugins: {
        ...plugins,
        entries,
      },
    });
    await this.updateConfig(nextPluginConfig);
    return nextPluginConfig;
  }

  async syncAuthorizationSession(): Promise<BrowserAuthSession | null> {
    this.snapshot.lastError = RETIRED_BRIDGE_MESSAGE;
    await this.persistSnapshot();
    return null;
  }

  async runHealthCheck(): Promise<{ backend: string; gateway: string }> {
    return {
      backend: "retired",
      gateway: "use-python-cli",
    };
  }

  private async persistSnapshot(): Promise<void> {
    if (!this.stateDir) {
      return;
    }
    const targetPath = path.join(this.stateDir, STATUS_FILE_NAME);
    await fs.mkdir(this.stateDir, { recursive: true });
    await fs.writeFile(targetPath, `${JSON.stringify(this.snapshot, null, 2)}\n`, "utf-8");
  }
}
