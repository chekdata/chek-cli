import {
  CONFIG_JSON_SCHEMA,
  CONFIG_UI_HINTS,
  parseConfig,
} from "./config.js";
import {
  registerChekCliProgram,
  registerChekCliCommands,
} from "./commands.js";
import type { OpenClawPluginApi } from "./openclaw-types.js";
import { ChekCliController } from "./service.js";

const chekCliPlugin = {
  id: "chek-cli",
  name: "CHEK CLI",
  description:
    "Agent-native CHEK CLI and OpenClaw helpers for review rooms, AI product publication, and mention handling.",
  configSchema: {
    parse: parseConfig,
    jsonSchema: CONFIG_JSON_SCHEMA,
    uiHints: CONFIG_UI_HINTS,
  },
  register(api: OpenClawPluginApi) {
    const config = parseConfig(api.pluginConfig);
    const controller = new ChekCliController({
      config,
      logger: api.logger,
      runtimeConfig: api.runtime.config,
    });

    registerChekCliCommands(api, controller);
    api.registerCli(({ program }) => {
      registerChekCliProgram(program, api, controller);
    }, { commands: ["chek"] });

    api.registerService({
      id: "chek-cli",
      start: async ({ stateDir }) => {
        controller.attachStateDir(stateDir);
        await controller.start();
      },
      stop: async () => {
        await controller.stop();
      },
    });
  },
};

export default chekCliPlugin;
