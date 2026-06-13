import type { Command } from "commander";
import type { OpenClawPluginApi } from "./openclaw-types.js";
import { ChekCliController } from "./service.js";
export declare function registerChekCliCommands(api: OpenClawPluginApi, controller: ChekCliController): void;
export declare function registerChekCliProgram(program: Command, api: OpenClawPluginApi, controller: ChekCliController): void;
