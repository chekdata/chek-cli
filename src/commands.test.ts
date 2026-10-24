import { describe, expect, it } from "vitest";

import { registerChekCliCommands } from "./commands.js";
import { parseConfig } from "./config.js";
import { ChekCliController } from "./service.js";
import type { OpenClawPluginApi, PluginCommandContext, ReplyPayload } from "./openclaw-types.js";

function createLogger() {
  return {
    info: () => undefined,
    warn: () => undefined,
    error: () => undefined,
    debug: () => undefined,
  };
}

describe("migration commands", () => {
  it("preserves an ordinary CHEK token while clearing retired auth state", async () => {
    let runtimeConfig: Record<string, unknown> = {
      plugins: {
        entries: {
          "memor-upload": {
            config: {
              accessToken: "ordinary-token",
              authSessionId: "retired-session",
              deviceCode: "retired-device",
            },
          },
        },
      },
    };
    let setupHandler:
      | ((ctx: PluginCommandContext) => ReplyPayload | Promise<ReplyPayload>)
      | undefined;
    const api = {
      logger: createLogger(),
      runtime: {
        config: {
          loadConfig: () => runtimeConfig,
          writeConfigFile: async (next: Record<string, unknown>) => {
            runtimeConfig = next;
          },
        },
      },
      registerCommand: (definition: Parameters<OpenClawPluginApi["registerCommand"]>[0]) => {
        if (definition.name === "chek-setup") setupHandler = definition.handler;
      },
      registerCli: () => undefined,
      registerService: () => undefined,
    } satisfies OpenClawPluginApi;
    const controller = new ChekCliController({
      config: parseConfig({ accessToken: "ordinary-token", authSessionId: "retired-session" }),
      logger: createLogger(),
      runtimeConfig: api.runtime.config,
    });

    registerChekCliCommands(api, controller);
    expect(setupHandler).toBeDefined();
    await setupHandler?.({
      channel: "test",
      isAuthorizedSender: true,
      commandBody: "/chek-setup",
      config: {},
    });

    const entries = (runtimeConfig.plugins as { entries: Record<string, { config: Record<string, unknown> }> }).entries;
    expect(entries["chek-cli"].config.accessToken).toBe("ordinary-token");
    expect(entries["chek-cli"].config.authSessionId).toBe("");
    expect(entries["chek-cli"].config.deviceCode).toBe("");
  });
});
