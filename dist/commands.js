import { maskToken, resolveAccessToken } from "./config.js";
import { buildBootstrapMessage } from "./render.js";
function formatStatus(controller) {
    const snapshot = controller.getSnapshot();
    return [
        "CHEK CLI 状态",
        `- running: ${snapshot.running ? "yes" : "no (migration shim)"}`,
        `- configured: ${snapshot.configured ? "yes" : "no"}`,
        `- backend: ${snapshot.backendAppBaseUrl}`,
        `- session: ${snapshot.sessionKey}`,
        `- installId: ${snapshot.installId || "-"}`,
        `- deviceId: ${snapshot.deviceId || "-"}`,
        `- pollIntervalMs: ${snapshot.pollIntervalMs}`,
        `- accessToken: ${snapshot.accessTokenConfigured ? "configured" : "missing"}`,
        `- authorizationStatus: ${snapshot.authorizationStatus || "-"}`,
        `- authSessionId: ${snapshot.authSessionId || "-"}`,
        `- authorizationUrl: ${snapshot.authorizationUrl || "-"}`,
        `- authorizedUser: ${snapshot.authorizedDisplayName || snapshot.authorizedUserOneId || "-"}`,
        `- lastAuthorizedAt: ${snapshot.lastAuthorizedAt || "-"}`,
        `- lastPollAt: ${snapshot.lastPollAt || "-"}`,
        `- lastSuccessAt: ${snapshot.lastSuccessAt || "-"}`,
        `- lastTaskAt: ${snapshot.lastTaskAt || "-"}`,
        `- lastTaskId: ${snapshot.lastTaskId || "-"}`,
        `- lastError: ${snapshot.lastError || "-"}`,
    ].join("\n");
}
function formatSetupUsage() {
    return [
        "用法：",
        "/chek-setup",
        "",
        "站内 Agent 执行、专用授权和房间自动回复已退役。这个兼容命令不会创建授权会话或轮询旧接口。",
        "",
        "请在自己的 Agent 工具里使用 Python CHEK CLI：",
        "git clone https://github.com/chekdata/chek-cli.git",
        "cd chek-cli/packages/chek-cli && python -m pip install -e \".[dev]\"",
        "chek config set-env dev && chek registry status",
        "",
        "Cursor、Codex、Claude Code 等可执行本地命令的工具可以直接运行；聊天模式工具先生成草稿。",
    ].join("\n");
}
function summarizeSavedConfig(config) {
    return [
        "CHEK CLI 已保存。",
        `- backend: ${config.backendAppBaseUrl}`,
        `- session: ${config.sessionKey}`,
        `- installId: ${config.installId || "-"}`,
        `- deviceId: ${config.deviceId || "-"}`,
        `- interval: ${config.pollIntervalMs}ms`,
        `- token: ${maskToken(resolveAccessToken(config))}`,
        `- auth: ${config.authorizationStatus || "-"}`,
    ].join("\n");
}
async function ensureBaseSetup(controller, patch) {
    const baseConfig = controller.getConfig();
    return await controller.persistConfigPatch({
        ...patch,
    });
}
async function runSetup(controller, patch) {
    // Keep a disabled entry for older hosts, but never save or use an old
    // browser-auth token/session. Authentication belongs to the Python CLI.
    const savedConfig = await ensureBaseSetup(controller, {
        ...patch,
        enabled: false,
        accessToken: "",
        authSessionId: "",
        deviceCode: "",
        authorizationStatus: "retired",
        authorizationUrl: "",
        authorizedUserOneId: "",
        authorizedDisplayName: "",
        lastAuthorizedAt: "",
    });
    return `${summarizeSavedConfig(savedConfig)}\n- bridge: retired (no browser authorization, polling, or automatic room replies)\n\n${formatSetupUsage()}`;
}
export function registerChekCliCommands(api, controller) {
    api.registerCommand({
        name: "chek-setup",
        description: "Show the migration path to the Python CHEK CLI.",
        acceptsArgs: true,
        handler: async (ctx) => {
            const rawArgs = ctx.args?.trim() ?? "";
            if (rawArgs === "help" || rawArgs === "--help") {
                return {
                    text: `${formatSetupUsage()}\n\n${formatStatus(controller)}`,
                };
            }
            const text = await runSetup(controller, {});
            return {
                text,
            };
        },
    });
    api.registerCommand({
        name: "chek-status",
        description: "Show migration-shim status.",
        handler: async () => ({
            text: formatStatus(controller),
        }),
    });
    api.registerCommand({
        name: "chek-bootstrap",
        description: "Print the Python CHEK CLI migration guide.",
        handler: async () => ({
            text: buildBootstrapMessage(),
        }),
    });
}
export function registerChekCliProgram(program, api, controller) {
    void api;
    const chek = program.command("chek").description("CHEK CLI helpers for CHEK");
    chek
        .command("setup")
        .description("Print the Python CHEK CLI migration guide")
        .action(async (options) => {
        void options;
        const output = await runSetup(controller, {});
        console.log(output);
    });
    chek
        .command("status")
        .description("Print current CHEK CLI runtime status")
        .action(() => {
        console.log(formatStatus(controller));
    });
    chek
        .command("bootstrap")
        .description("Print the canonical bootstrap message")
        .action(() => {
        console.log(buildBootstrapMessage());
    });
}
