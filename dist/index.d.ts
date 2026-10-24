import { parseConfig } from "./config.js";
import type { OpenClawPluginApi } from "./openclaw-types.js";
declare const chekCliPlugin: {
    id: string;
    name: string;
    description: string;
    configSchema: {
        parse: typeof parseConfig;
        jsonSchema: {
            readonly type: "object";
            readonly additionalProperties: false;
            readonly properties: {
                readonly enabled: {
                    readonly type: "boolean";
                };
                readonly backendAppBaseUrl: {
                    readonly type: "string";
                    readonly minLength: 1;
                };
                readonly accessToken: {
                    readonly type: "string";
                };
                readonly pollIntervalMs: {
                    readonly type: "integer";
                    readonly minimum: 2000;
                    readonly maximum: 60000;
                };
                readonly sessionKey: {
                    readonly type: "string";
                    readonly minLength: 1;
                };
                readonly installId: {
                    readonly type: "string";
                };
                readonly deviceId: {
                    readonly type: "string";
                };
                readonly authSessionId: {
                    readonly type: "string";
                };
                readonly deviceCode: {
                    readonly type: "string";
                };
                readonly authorizationStatus: {
                    readonly type: "string";
                };
                readonly authorizationUrl: {
                    readonly type: "string";
                };
                readonly authorizedUserOneId: {
                    readonly type: "string";
                };
                readonly authorizedDisplayName: {
                    readonly type: "string";
                };
                readonly lastAuthorizedAt: {
                    readonly type: "string";
                };
            };
        };
        uiHints: {
            readonly enabled: {
                readonly label: "Enabled";
            };
            readonly backendAppBaseUrl: {
                readonly label: "CHEK Backend URL";
                readonly placeholder: "https://api-dev.chekkk.com/api/backend-app";
            };
            readonly sessionKey: {
                readonly label: "Legacy Session Key (unused)";
            };
        };
    };
    register(api: OpenClawPluginApi): void;
};
export default chekCliPlugin;
