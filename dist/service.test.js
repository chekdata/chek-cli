import { afterEach, describe, expect, it, vi } from "vitest";
import { parseConfig } from "./config.js";
import { ChekCliController } from "./service.js";
function createRuntimeConfig(initialConfig) {
    let currentConfig = {
        plugins: {
            entries: {
                "memor-upload": {
                    enabled: true,
                    config: initialConfig,
                },
            },
        },
    };
    return {
        loadConfig: () => currentConfig,
        writeConfigFile: async (next) => {
            currentConfig = next;
        },
    };
}
function createLogger() {
    return {
        info: vi.fn(),
        warn: vi.fn(),
        error: vi.fn(),
        debug: vi.fn(),
    };
}
describe("ChekCliController", () => {
    afterEach(() => {
        vi.unstubAllGlobals();
        vi.clearAllMocks();
    });
    it("does not contact retired browser authorization endpoints", async () => {
        const runtimeConfig = createRuntimeConfig({
            backendAppBaseUrl: "https://api-dev.chekkk.com/api/backend-app",
            authSessionId: "auth-session-1",
            deviceCode: "ck-12345678",
        });
        const fetchMock = vi.fn();
        vi.stubGlobal("fetch", fetchMock);
        const controller = new ChekCliController({
            config: parseConfig({
                backendAppBaseUrl: "https://api-dev.chekkk.com/api/backend-app",
                authSessionId: "auth-session-1",
                deviceCode: "ck-12345678",
            }),
            logger: createLogger(),
            runtimeConfig,
        });
        const session = await controller.syncAuthorizationSession();
        expect(session).toBeNull();
        expect(controller.getConfig().accessToken).toBe("");
        expect(controller.getSnapshot().lastError).toContain("已退役");
        expect(fetchMock).not.toHaveBeenCalled();
    });
});
it.each([
    { accessToken: "ckmu_test_token" },
    { authSessionId: "old-session", deviceCode: "old-code" },
])("does not start legacy polling (%j)", async (credentials) => {
    const config = { backendAppBaseUrl: "https://api-dev.chekkk.com/api/backend-app", ...credentials };
    const controller = new ChekCliController({ config: parseConfig(config), logger: createLogger(), runtimeConfig: createRuntimeConfig(config) });
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    try {
        await controller.start();
        expect(controller.getSnapshot().running).toBe(false);
        expect(controller.getSnapshot().lastError).toContain("已退役");
        expect(fetchMock).not.toHaveBeenCalled();
    }
    finally {
        await controller.stop();
        vi.unstubAllGlobals();
    }
});
