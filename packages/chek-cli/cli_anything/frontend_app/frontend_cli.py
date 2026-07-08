"""Agent-first CLI harness for CHEK CLI."""

from __future__ import annotations

import json
import mimetypes
import sys
import urllib.parse
from pathlib import Path

import click

from . import __version__
from .ai_product import (
    AI_PRODUCT_CATEGORIES,
    AI_PRODUCT_INTEREST_RELATIONS,
    build_publish_payload,
    build_research_plan,
    build_review_payload,
    duplicate_check_payload,
    robot_config_version_edit_payload,
    validate_formal_submission,
    vehicle_sync_versions_edit_payload,
    product_from_inputs,
)
from .api_core import (
    ENV_ORIGINS,
    IDENTITY_CHOICES,
    check_scopes,
    clear_token,
    credential_status,
    delete_profile,
    export_profile,
    import_profile,
    load_config,
    login_with_password,
    parse_json_arg,
    profile_list,
    request_api,
    request_multipart_api,
    save_config,
    save_profile,
    save_profile_credential,
    save_token,
    sms_login,
    sms_send,
    token_summary,
    use_profile,
)
from .core import (
    CommandResult,
    HarnessError,
    doctor as doctor_data,
    find_repo_root,
    git_status,
    h5_url,
    http_smoke,
    package_json,
    read_logs,
    route_config,
    run_command,
    serve_status,
    start_h5_server,
    stop_h5_server,
    wait_for_http,
)
from .registry import REGISTRY, REGISTRY_META, find_method, get_schema, iter_methods, resolve_schema_ref


def emit(result: CommandResult, as_json: bool) -> None:
    payload = result.to_dict()
    if as_json:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    status = "OK" if payload["ok"] else "ERROR"
    click.echo(f"[{status}] {payload['command']}")
    data = payload.get("data")
    if isinstance(data, dict):
        for key, value in data.items():
            click.echo(f"{key}: {value}")
    elif isinstance(data, list):
        for item in data:
            click.echo(str(item))
    elif data:
        click.echo(str(data))
    for warning in payload.get("warnings", []):
        click.echo(f"warning: {warning}", err=True)
    for error in payload.get("errors", []):
        click.echo(f"error: {error}", err=True)


def fail(command: str, exc: Exception, as_json: bool) -> None:
    data = {}
    if isinstance(exc, HarnessError):
        data = exc.details
    emit(CommandResult(False, command, data=data, errors=[str(exc)]), as_json)
    raise SystemExit(1)


@click.group(invoke_without_command=True)
@click.option("--json", "as_json", is_flag=True, help="Alias for --format json.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "pretty"]),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.option("--as", "identity", type=click.Choice(IDENTITY_CHOICES), default=None, help="Identity type: auto | user | service | none.")
@click.option("--repo", type=click.Path(file_okay=False, path_type=Path), default=None, help="CHEK app repository root.")
@click.version_option(__version__)
@click.pass_context
def main(ctx: click.Context, as_json: bool, output_format: str, identity: str | None, repo: Path | None) -> None:
    """CHEK CLI agent-native interface for CHEK backend capabilities."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json or output_format == "json"
    ctx.obj["format"] = "json" if as_json else output_format
    ctx.obj["identity"] = identity
    ctx.obj["repo_arg"] = str(repo) if repo else None
    if ctx.invoked_subcommand is None:
        emit(
            CommandResult(
                True,
                "help",
                data={
                    "message": "Agent-first CHEK CLI. Start with: config show, auth status, schema, api, ai-product +research-plan.",
                    "layers": [
                        "shortcuts: ai-product +publish/+review, vehicle +search, discovery +feed, share +resolve",
                        "schema/API commands: schema, call service.resource.method, api METHOD PATH",
                        "auth identity: --as auto|user|service|none, config default-as",
                        "auxiliary dev commands: routes, serve, build, page, flow",
                    ],
                    "commands": [
                        "config show",
                        "auth status",
                        "schema",
                        "call vehicle.vehicles.batchSearch --data '{...}' --dry-run",
                        "api GET /api/backend-app/login/checkToken --dry-run",
                        "ai-product +research-plan --category 生产力工具 --product-name Kimi --software-version '2026 年 7 月网页版'",
                        "ai-product +publish --category 生产力工具 --product-name Kimi --software-version '2026 年 7 月网页版' --reason '值得测' --dry-run",
                        "ai-product +publish --formal --category 具身机器人 --product-name Unitree --hardware-model H1 --software-version 'unitree_sdk2 main@7740f8b' ...",
                        "media +upload-cover --file ./cover.png --source-url https://example.com/product --dry-run",
                        "ai-product +robot-version-edit --robot-id <robot_id> --product-name Unitree --hardware-model H1 --software-version 'unitree_sdk2 main@7740f8b'",
                        "ai-product +review --post-id <uuid> --stars 4 --comment '体验稳定' --dry-run",
                        "vehicle +search --query '小米 SU7' --dry-run",
                    ],
                },
            ),
            ctx.obj["json"],
        )


def repo_root(ctx: click.Context) -> Path:
    return find_repo_root(ctx.obj.get("repo_arg"))


def request_identity(ctx: click.Context) -> str | None:
    return ctx.obj.get("identity")


def emit_api(ctx: click.Context, command: str, result: dict) -> None:
    ok = bool(result.get("ok"))
    errors = []
    if not ok:
        error = result.get("error")
        if isinstance(error, dict):
            errors.append(str(error.get("message") or error.get("code") or "API request failed."))
        else:
            errors.append("API request failed.")
    emit(CommandResult(ok, command, data=result, errors=errors), ctx.obj["json"])
    if not ok:
        raise SystemExit(1)


def quote_path_value(value: str) -> str:
    return urllib.parse.quote(str(value), safe="")


def parse_key_value(raw: tuple[str, ...]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise HarnessError("Path arguments must use key=value syntax.", details={"value": item})
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise HarnessError("Path argument key cannot be empty.", details={"value": item})
        values[key] = value
    return values


def split_scope_args(raw: tuple[str, ...]) -> list[str]:
    scopes: list[str] = []
    for item in raw:
        scopes.extend(part.strip() for part in str(item).replace(",", " ").split() if part.strip())
    return sorted(set(scopes))


def render_registry_path(path_template: str, path_values: dict[str, str]) -> str:
    rendered = path_template
    missing = []
    for placeholder in sorted(set(part.split("}", 1)[0] for part in rendered.split("{")[1:])):
        if placeholder not in path_values:
            missing.append(placeholder)
            continue
        rendered = rendered.replace("{" + placeholder + "}", quote_path_value(path_values[placeholder]))
    if missing:
        raise HarnessError("Missing required path argument.", details={"missing": missing, "path": path_template})
    return rendered


def command_name(value: str) -> str:
    text = re_sub_non_word(str(value or ""))
    chars = []
    for index, char in enumerate(text):
        if char.isupper() and index > 0 and (text[index - 1].islower() or text[index - 1].isdigit()):
            chars.append("-")
        chars.append(char.lower())
    return "-".join(part for part in "".join(chars).replace("_", "-").split("-") if part)


def re_sub_non_word(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"_", "-"} else "-" for char in value)


def merge_params(raw_params: str | None, param_args: tuple[str, ...]) -> dict[str, str]:
    params = parse_json_arg(raw_params, stdin=sys.stdin, flag_name="--params") or {}
    if not isinstance(params, dict):
        raise HarnessError("--params must be a JSON object.")
    params.update(parse_key_value(param_args))
    return params


def call_registry_method(
    ctx: click.Context,
    *,
    command: str,
    schema_path: str,
    path_args: tuple[str, ...],
    auto_path_args: dict[str, str | None] | None,
    params: str | None,
    param_args: tuple[str, ...],
    body: str | None,
    no_auth: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    parts = schema_path.split(".")
    if len(parts) != 3:
        raise HarnessError("Schema path must be service.resource.method.", details={"schemaPath": schema_path})
    method_schema = find_method(parts[0], parts[1], parts[2])
    if not method_schema:
        raise HarnessError("Schema path not found.", details={"schemaPath": schema_path})
    path_values = parse_key_value(path_args)
    for key, value in (auto_path_args or {}).items():
        if value is not None and value != "":
            path_values[key] = value
    path = render_registry_path(str(method_schema["path"]), path_values)
    parsed_body = parse_json_arg(body, stdin=sys.stdin, flag_name="--data")
    emit_api(
        ctx,
        command,
        request_api(
            str(method_schema.get("httpMethod") or "GET"),
            path,
            params=merge_params(params, param_args),
            data=parsed_body,
            auth=not no_auth,
            identity=request_identity(ctx),
            timeout=timeout,
            dry_run=dry_run,
        ),
    )


def compact_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def redact_profile_payload(profile: dict[str, object]) -> dict[str, object]:
    redacted = dict(profile)
    token = redacted.pop("token", None)
    if isinstance(token, dict):
        redacted["token"] = token_summary(token)
    credentials = redacted.pop("credentials", None)
    if isinstance(credentials, dict):
        redacted["credentials"] = {
            str(identity): token_summary(credential)
            for identity, credential in credentials.items()
            if isinstance(credential, dict)
        }
    return redacted


def workflow_step(
    name: str,
    purpose: str,
    schema_path: str | None,
    method: str,
    path: str,
    *,
    params: dict[str, object] | None = None,
    data: object = None,
    auth: bool = True,
) -> dict[str, object]:
    return {
        "name": name,
        "purpose": purpose,
        "schemaPath": schema_path,
        "method": method,
        "path": path,
        "params": params or {},
        "data": data,
        "auth": auth,
    }


def execute_workflow(
    ctx: click.Context,
    *,
    command: str,
    objective: str,
    steps: list[dict[str, object]],
    dry_run: bool,
    timeout: int = 30,
) -> None:
    executed = []
    ok = True
    for step in steps:
        result = request_api(
            str(step["method"]),
            str(step["path"]),
            params=step.get("params") if isinstance(step.get("params"), dict) else None,
            data=step.get("data"),
            auth=bool(step.get("auth", True)),
            identity=request_identity(ctx),
            timeout=timeout,
            dry_run=dry_run,
        )
        executed.append(
            {
                "name": step["name"],
                "purpose": step["purpose"],
                "schemaPath": step.get("schemaPath"),
                "result": result,
            }
        )
        ok = ok and bool(result.get("ok"))
    report = agent_report(objective, executed, dry_run=dry_run)
    emit(
        CommandResult(
            ok,
            command,
            data={"objective": objective, "dryRun": dry_run, "stepCount": len(executed), "steps": executed, "agentReport": report},
            errors=[] if ok else ["One or more workflow steps failed."],
        ),
        ctx.obj["json"],
    )
    if not ok:
        raise SystemExit(1)


def agent_report(objective: str, executed: list[dict[str, object]], *, dry_run: bool) -> dict[str, object]:
    evidence = []
    for step in executed:
        result = step.get("result") if isinstance(step.get("result"), dict) else {}
        data = result.get("data") if isinstance(result, dict) else None
        evidence.append(
            {
                "step": step.get("name"),
                "schemaPath": step.get("schemaPath"),
                "ok": result.get("ok") if isinstance(result, dict) else False,
                "status": result.get("status") if isinstance(result, dict) else None,
                "summary": summarize_payload(data),
            }
        )
    if dry_run:
        recommendation = "Dry run only. Execute without --dry-run to collect evidence and produce grounded recommendations."
    else:
        recommendation = "Use the successful evidence steps as grounded inputs; inspect failed steps before making final recommendations."
    return {
        "objective": objective,
        "dryRun": dry_run,
        "evidence": evidence,
        "recommendation": recommendation,
        "nextActions": [
            "Use schemaPath to inspect exact parameter/response shape when a step needs refinement.",
            "Run with --as user or --as service when an endpoint requires authenticated evidence.",
            "Keep --dry-run for write/admin endpoints before executing mutations.",
        ],
    }


def summarize_payload(payload: object) -> dict[str, object]:
    if payload is None:
        return {"type": "null", "count": 0}
    if isinstance(payload, list):
        return {"type": "list", "count": len(payload), "items": [compact_entity(item) for item in payload[:5]]}
    if isinstance(payload, dict):
        list_keys = {key: len(value) for key, value in payload.items() if isinstance(value, list)}
        candidates = []
        for key in ("items", "records", "list", "data", "results", "vehicles", "robots"):
            value = payload.get(key)
            if isinstance(value, list):
                candidates = [compact_entity(item) for item in value[:5]]
                break
        return {"type": "object", "keys": sorted(payload.keys())[:24], "listKeys": list_keys, "candidates": candidates}
    return {"type": type(payload).__name__, "value": str(payload)[:240]}


def compact_entity(value: object) -> object:
    if not isinstance(value, dict):
        return value
    keep = {}
    for key in ("id", "vehicleId", "robotId", "name", "title", "brand", "model", "series", "score", "rank", "summary"):
        if key in value:
            keep[key] = value[key]
    return keep or {key: value[key] for key in list(value.keys())[:6]}


CURATED_EXAMPLES = [
    {
        "name": "vehicle.buying-plan",
        "domain": "vehicle",
        "positioning": ["买车 OpenClaw", "AI 版汽车之家"],
        "description": "Build an agent plan for car search, rankings, and evidence collection.",
        "command": "chek vehicle +buying-plan --query '小米 SU7' --scene urban --city 上海 --dry-run",
        "schemaPaths": [
            "vehicle.vehicles.batchSearch",
            "backend-saas.appVehicleMetrics.rankTop3",
            "backend-app.discovery.feed",
        ],
    },
    {
        "name": "vehicle.compare",
        "domain": "vehicle",
        "positioning": ["智能汽车数据库", "懂机帝"],
        "description": "Compare canonical vehicle details and optional raw parameter snapshots.",
        "command": "chek vehicle +compare --id veh_1 --id veh_2 --include-raw --dry-run",
        "schemaPaths": ["vehicle.vehicles.detail", "vehicle.vehicles.rawParams"],
    },
    {
        "name": "vehicle.rankings",
        "domain": "vehicle",
        "positioning": ["智能汽车数据库", "AI 版汽车之家"],
        "description": "Inspect intelligent vehicle ranking endpoints for a scene/window.",
        "command": "chek vehicle +rankings --scene urban --window latest --dry-run",
        "schemaPaths": ["backend-saas.appVehicleMetrics.rankTop3"],
    },
    {
        "name": "humanoid.search",
        "domain": "humanoid",
        "positioning": ["机器人数据库", "人形机器人配置数据"],
        "description": "Search humanoid robots by keyword, brand, category, and pagination.",
        "command": "chek humanoid +search --query 'Unitree' --page-size 10 --dry-run",
        "schemaPaths": ["humanoid.robots.list"],
    },
    {
        "name": "humanoid.compare",
        "domain": "humanoid",
        "positioning": ["机器人数据库", "人形机器人配置数据"],
        "description": "Compare humanoid robot details and configuration version snapshots.",
        "command": "chek humanoid +compare --id robot_1 --id robot_2 --include-configs --dry-run",
        "schemaPaths": ["humanoid.robots.detail", "humanoid.robots.configVersions"],
    },
    {
        "name": "ai-product.publish",
        "domain": "ai-product",
        "positioning": ["AI 产品提报", "公众提报产品", "版本化评测房间"],
        "description": "Research, duplicate-check, and publish an AI product review room.",
        "command": "chek ai-product +publish --formal --category 具身机器人 --product-name Unitree --hardware-model H1 --software-version 'unitree_sdk2 main@7740f8b' --source-url https://www.unitree.com/operate/h1/ --cover-image-url https://img.chekkk.com/app_project_pic/example.png --cover-source-url https://www.unitree.com/operate/h1/ --linked-entity 'targetType=humanoid_robot,targetId=<robot_id>,title=H1,tagTitle=H1,subtitle=宇树' --dry-run",
        "schemaPaths": ["backend-app.buddy.postsPost", "backend-app.buddy.posts"],
    },
    {
        "name": "media.upload-cover",
        "domain": "media",
        "positioning": ["AI 产品提报", "封面上传", "正式评审闭环"],
        "description": "Upload a researched AI product cover to CHEK media before formal room publication.",
        "command": "chek media +upload-cover --file ./cover.png --source-url https://www.unitree.com/operate/h1/ --dry-run",
        "schemaPaths": ["backend-app.media.images"],
    },
    {
        "name": "ai-product.robot-version-edit",
        "domain": "ai-product",
        "positioning": ["AI 产品提报", "机器人资料库", "版本化复评"],
        "description": "Submit the robot library config-version edit that corresponds to a formal AI product review room.",
        "command": "chek ai-product +robot-version-edit --robot-id <robot_id> --product-name Unitree --hardware-model H1 --software-version 'unitree_sdk2 main@7740f8b' --source-repo https://github.com/unitreerobotics/unitree_sdk2 --source-commit 7740f8b --post-id <room_uuid> --dry-run",
        "schemaPaths": ["humanoid.robots.editsPost", "humanoid.edits.detail"],
    },
    {
        "name": "ai-product.vehicle-version-edit",
        "domain": "ai-product",
        "positioning": ["AI 产品提报", "车型资料库", "版本化复评"],
        "description": "Submit the vehicle library hardware/software sync edit that corresponds to a formal AI product review room.",
        "command": "chek ai-product +vehicle-version-edit --vehicle-id <vehicle_id> --product-name '问界 M9' --hardware-model 'Max 智驾版' --software-version 'ADS 3.3.0' --dry-run",
        "schemaPaths": ["vehicle.vehicles.editsPost", "vehicle.vehicles.editsGet"],
    },
    {
        "name": "ai-product.review",
        "domain": "ai-product",
        "positioning": ["AI 产品评测", "追日靴评分", "证据化复评"],
        "description": "Submit a star rating and review evidence for an AI product room.",
        "command": "chek ai-product +review --post-id <uuid> --stars 4.5 --comment '长文本总结稳定' --evidence '附测试记录链接' --dry-run",
        "schemaPaths": ["backend-app.buddy.postsMessages", "backend-app.buddy.postsGet"],
    },
]


SAFE_READONLY_SMOKE = [
    ("auth", "auth.healthz.list", False),
    ("backend-app", "backend-app.discovery.feedFilters", False),
    ("crowd", "crowd.healthz.list", False),
    ("humanoid", "humanoid.healthz.list", False),
    ("vehicle", "vehicle.healthz.list", False),
    ("backend-saas", "backend-saas.options.scene", True),
]


WRITE_HINTS = {"admin", "approve", "reject", "revoke", "rollback", "delete", "update", "upload", "create", "post", "put", "patch"}


def safety_for_method(schema_path: str, method_schema: dict) -> dict[str, object]:
    http_method = str(method_schema.get("httpMethod") or "GET").upper()
    path = str(method_schema.get("path") or "")
    lowered = f"{schema_path} {path} {method_schema.get('summary') or ''} {method_schema.get('description') or ''}".lower()
    safe_read = http_method in {"GET", "HEAD", "OPTIONS"}
    mutating = http_method in {"POST", "PUT", "PATCH", "DELETE"} or any(hint in lowered for hint in WRITE_HINTS)
    admin = any(hint in lowered for hint in {"admin", "approve", "reject", "rollback", "delete", "modify", "update"})
    public = schema_path in {"backend-app.discovery.feed", "backend-app.discovery.feedFilters", "auth.share.resolve"} or path.endswith("/healthz")
    level = "public_read" if public and safe_read else "read" if safe_read and not admin else "admin_write" if admin else "write" if mutating else "unknown"
    return {
        "level": level,
        "httpMethod": http_method,
        "public": public,
        "mutating": mutating,
        "auth": "none" if public else "user_or_service",
        "dryRunRecommended": mutating or admin,
    }


def registry_operation_manifest(include_operations: bool, *, limit: int = 0) -> dict[str, object]:
    operations = []
    safety_counts: dict[str, int] = {}
    for service, resource, method, method_schema in iter_methods():
        schema_path = f"{service}.{resource}.{method}"
        safety = safety_for_method(schema_path, method_schema)
        safety_counts[str(safety["level"])] = safety_counts.get(str(safety["level"]), 0) + 1
        if include_operations:
            operations.append(
                {
                    "schemaPath": schema_path,
                    "command": f"chek {command_name(service)} {command_name(resource)} {command_name(method)}",
                    "httpMethod": method_schema.get("httpMethod"),
                    "path": method_schema.get("path"),
                    "summary": method_schema.get("summary") or method_schema.get("description"),
                    "safety": safety,
                }
            )
            if limit and len(operations) >= limit:
                include_operations = False
    return {
        "services": list(REGISTRY.keys()),
        "operationCount": REGISTRY_META.get("operationCount"),
        "safetyCounts": safety_counts,
        "operations": operations,
    }


def iter_schema_paths() -> list[str]:
    paths: list[str] = []
    for service_name, service in sorted(REGISTRY.items()):
        for resource_name, resource in sorted((service.get("resources") or {}).items()):
            for method_name in sorted((resource.get("methods") or {}).keys()):
                paths.append(f"{service_name}.{resource_name}.{method_name}")
    return paths


def parameter_placeholder(parameter: dict) -> str:
    schema = parameter.get("schema") if isinstance(parameter.get("schema"), dict) else {}
    param_type = str(schema.get("type") or "string")
    if param_type in {"integer", "number"}:
        return "1"
    if param_type == "boolean":
        return "true"
    return f"<{parameter.get('name') or 'value'}>"


def schema_example_value(service: str, schema: object, *, depth: int = 0) -> object:
    if depth > 8:
        return "<object>"
    if not isinstance(schema, dict):
        return "<value>"
    ref = schema.get("$ref")
    if ref:
        resolved = resolve_schema_ref(service, str(ref))
        if resolved:
            return schema_example_value(service, resolved, depth=depth + 1)
        return f"<{str(ref).split('/')[-1]}>"
    if "default" in schema:
        return schema["default"]
    for union_key in ("anyOf", "oneOf", "allOf"):
        variants = schema.get(union_key)
        if isinstance(variants, list) and variants:
            non_null = [item for item in variants if not (isinstance(item, dict) and item.get("type") == "null")]
            return schema_example_value(service, non_null[0] if non_null else variants[0], depth=depth + 1)
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return enum[0]
    schema_type = schema.get("type")
    if schema_type == "array":
        return [schema_example_value(service, schema.get("items"), depth=depth + 1)]
    if schema_type == "object" or isinstance(schema.get("properties"), dict):
        properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
        required = set(schema.get("required") or [])
        selected: dict[str, object] = {}
        for index, (name, child_schema) in enumerate(properties.items()):
            if index >= 16 and name not in required:
                continue
            selected[name] = schema_example_value(service, child_schema, depth=depth + 1)
        return selected or {}
    if schema_type in {"integer", "number"}:
        return 1
    if schema_type == "boolean":
        return True
    return "<string>"


def request_body_example(service: str, method_schema: dict) -> object:
    body = method_schema.get("requestBody")
    if not isinstance(body, dict):
        return None
    schemas = body.get("schema")
    if not isinstance(schemas, dict):
        return {}
    preferred = schemas.get("application/json") or next(iter(schemas.values()), {})
    return schema_example_value(service, preferred)


def generated_example(schema_path: str) -> dict[str, object]:
    parts = schema_path.split(".")
    if len(parts) != 3:
        raise HarnessError("Schema path must be service.resource.method.", details={"schemaPath": schema_path})
    method_schema = find_method(parts[0], parts[1], parts[2])
    if not method_schema:
        raise HarnessError("Schema path not found.", details={"schemaPath": schema_path})

    tree_parts = ["chek", *(command_name(part) for part in parts)]
    call_parts = ["chek", "call", schema_path]
    raw_parts = ["chek", "api", str(method_schema.get("httpMethod") or "GET"), str(method_schema["path"])]
    for param in method_schema.get("parameters") or []:
        if not isinstance(param, dict):
            continue
        name = str(param.get("name") or "")
        if not name:
            continue
        placeholder = parameter_placeholder(param)
        if param.get("location") == "path":
            tree_parts.extend([f"--{command_name(name)}", placeholder])
            call_parts.extend(["--path", f"{name}={placeholder}"])
        elif param.get("location") == "query" and (param.get("required") or len([part for part in tree_parts if part == "--param"]) < 3):
            tree_parts.extend(["--param", f"{name}={placeholder}"])
            call_parts.extend(["--param", f"{name}={placeholder}"])
    if method_schema.get("requestBody"):
        example_body = request_body_example(parts[0], method_schema)
        body = "'" + compact_json(example_body if isinstance(example_body, dict) else {"value": example_body}) + "'"
        tree_parts.extend(["--data", body])
        call_parts.extend(["--data", body])
        raw_parts.extend(["--data", body])
    tree_parts.append("--dry-run")
    call_parts.append("--dry-run")
    raw_parts.append("--dry-run")
    return {
        "schemaPath": schema_path,
        "summary": method_schema.get("summary") or method_schema.get("description") or schema_path,
        "httpMethod": method_schema.get("httpMethod"),
        "path": method_schema.get("path"),
        "commands": {
            "schema": f"chek schema {schema_path}",
            "tree": " ".join(tree_parts),
            "call": " ".join(call_parts),
            "raw": " ".join(raw_parts),
        },
        "requestBodyExample": request_body_example(parts[0], method_schema),
    }


@main.group()
def config() -> None:
    """Configure CHEK API target environment."""


@config.command("show")
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current CLI config."""
    as_json = ctx.obj["json"]
    try:
        emit(
            CommandResult(
                True,
                "config show",
                data={
                    **load_config(),
                    "availableEnvs": ENV_ORIGINS,
                },
            ),
            as_json,
        )
    except Exception as exc:
        fail("config show", exc, as_json)


@config.command("set-env")
@click.argument("env", type=click.Choice(sorted(ENV_ORIGINS)))
@click.pass_context
def config_set_env(ctx: click.Context, env: str) -> None:
    """Set the named CHEK API environment."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "config set-env", data=save_config({"env": env})), as_json)
    except Exception as exc:
        fail("config set-env", exc, as_json)


@config.command("set-origin")
@click.argument("origin")
@click.pass_context
def config_set_origin(ctx: click.Context, origin: str) -> None:
    """Set a custom API origin, e.g. http://localhost:3000."""
    as_json = ctx.obj["json"]
    try:
        cleaned = origin.rstrip("/")
        if not cleaned.startswith(("http://", "https://")):
            raise HarnessError("API origin must start with http:// or https://.", details={"origin": origin})
        emit(CommandResult(True, "config set-origin", data=save_config({"api_origin": cleaned})), as_json)
    except Exception as exc:
        fail("config set-origin", exc, as_json)


@config.command("default-as")
@click.argument("identity", required=False, type=click.Choice(IDENTITY_CHOICES))
@click.pass_context
def config_default_as(ctx: click.Context, identity: str | None) -> None:
    """View or set default identity, Lark-style: auto/user/service/none."""
    as_json = ctx.obj["json"]
    try:
        if identity:
            data = save_config({"default_as": identity})
        else:
            data = load_config()
        emit(CommandResult(True, "config default-as", data={"default_as": data.get("default_as"), "config": data}), as_json)
    except Exception as exc:
        fail("config default-as", exc, as_json)


@config.command("secret-store")
@click.argument("store", required=False, type=click.Choice(["file", "keyring", "auto"]))
@click.pass_context
def config_secret_store(ctx: click.Context, store: str | None) -> None:
    """View or set preferred credential storage mode."""
    as_json = ctx.obj["json"]
    try:
        if store:
            data = save_config({"secret_store": store})
        else:
            data = load_config()
        emit(
            CommandResult(
                True,
                "config secret-store",
                data={
                    "secret_store": data.get("secret_store"),
                    "note": "file stores 0600 JSON locally; keyring is reserved for hosts with a configured Python keyring backend.",
                    "config": data,
                },
            ),
            as_json,
        )
    except Exception as exc:
        fail("config secret-store", exc, as_json)


@main.group()
def auth() -> None:
    """Authenticate and manage API credentials."""


@auth.command("status")
@click.option("--check", is_flag=True, help="Call backend checkToken using the stored token.")
@click.pass_context
def auth_status(ctx: click.Context, check: bool) -> None:
    """Show stored token status."""
    as_json = ctx.obj["json"]
    try:
        data = credential_status(request_identity(ctx))
        if check:
            data["check"] = request_api("GET", "/api/backend-app/login/checkToken", auth=True, identity=request_identity(ctx))
        ok = not check or bool(data.get("check", {}).get("ok"))
        emit(CommandResult(ok, "auth status", data=data, errors=[] if ok else ["Stored token failed backend verification."]), as_json)
        if not ok:
            raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as exc:
        fail("auth status", exc, as_json)


@auth.command("set-token")
@click.option("--token", required=True, help="Access token to store locally.")
@click.option("--profile", "profile_name", default=None, help="Also save this token into a named auth profile.")
@click.option("--identity", type=click.Choice(["user", "service"]), default="user", show_default=True)
@click.option("--scope", "scopes", multiple=True, help="Known scope/permission attached to this credential. Repeatable or space-separated.")
@click.pass_context
def auth_set_token(ctx: click.Context, token: str, profile_name: str | None, identity: str, scopes: tuple[str, ...]) -> None:
    """Store an existing CHEK access token for agent use."""
    as_json = ctx.obj["json"]
    try:
        scope_list = split_scope_args(scopes)
        save_token(token, source="manual", identity=identity, scopes=scope_list)
        data = token_summary()
        if profile_name:
            save_profile_credential(profile_name, token, identity=identity, scopes=scope_list, activate=True)
            data["savedProfile"] = redact_profile_payload(save_profile(profile_name, include_token=True, set_active=True))
        emit(CommandResult(True, "auth set-token", data=data), as_json)
    except Exception as exc:
        fail("auth set-token", exc, as_json)


@auth.command("logout")
@click.pass_context
def auth_logout(ctx: click.Context) -> None:
    """Remove the stored token."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "auth logout", data={"removed": clear_token()}), as_json)
    except Exception as exc:
        fail("auth logout", exc, as_json)


@auth.group("profile")
def auth_profile() -> None:
    """Manage named environment/token profiles for repeatable agent sessions."""


@auth_profile.command("list")
@click.pass_context
def auth_profile_list(ctx: click.Context) -> None:
    """List saved auth profiles."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "auth profile list", data=profile_list()), as_json)
    except Exception as exc:
        fail("auth profile list", exc, as_json)


@auth_profile.command("save")
@click.argument("name")
@click.option("--no-token", is_flag=True, help="Save environment config only, without the active token.")
@click.option("--activate", is_flag=True, help="Mark the saved profile as active.")
@click.pass_context
def auth_profile_save(ctx: click.Context, name: str, no_token: bool, activate: bool) -> None:
    """Save the current config/token as a named profile."""
    as_json = ctx.obj["json"]
    try:
        emit(
            CommandResult(
                True,
                "auth profile save",
                data=redact_profile_payload(save_profile(name, include_token=not no_token, set_active=activate)),
            ),
            as_json,
        )
    except Exception as exc:
        fail("auth profile save", exc, as_json)


@auth_profile.command("use")
@click.argument("name")
@click.option("--as", "identity", type=click.Choice(IDENTITY_CHOICES), default=None, help="Override profile default identity.")
@click.pass_context
def auth_profile_use(ctx: click.Context, name: str, identity: str | None) -> None:
    """Switch the active config/token to a saved profile."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "auth profile use", data=use_profile(name, identity=identity)), as_json)
    except Exception as exc:
        fail("auth profile use", exc, as_json)


@auth_profile.command("delete")
@click.argument("name")
@click.pass_context
def auth_profile_delete(ctx: click.Context, name: str) -> None:
    """Delete a saved profile."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "auth profile delete", data=delete_profile(name)), as_json)
    except Exception as exc:
        fail("auth profile delete", exc, as_json)


@auth_profile.command("export")
@click.argument("name")
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Write profile JSON to a file.")
@click.option("--include-token", is_flag=True, help="Include the raw token. Use only for private handoff files.")
@click.pass_context
def auth_profile_export(ctx: click.Context, name: str, output: Path | None, include_token: bool) -> None:
    """Export a saved profile, redacting token material by default."""
    as_json = ctx.obj["json"]
    try:
        data = export_profile(name, include_token=include_token)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            data = {"profile": name, "output": str(output), "includeToken": include_token}
        emit(CommandResult(True, "auth profile export", data=data), as_json)
    except Exception as exc:
        fail("auth profile export", exc, as_json)


@auth_profile.command("import")
@click.argument("name")
@click.option("--file", "input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True)
@click.option("--activate", is_flag=True, help="Use the imported profile immediately.")
@click.pass_context
def auth_profile_import(ctx: click.Context, name: str, input_file: Path, activate: bool) -> None:
    """Import a profile JSON file."""
    as_json = ctx.obj["json"]
    try:
        data = json.loads(input_file.read_text(encoding="utf-8"))
        imported = import_profile(name, data, set_active=activate)
        if not activate and isinstance(imported, dict):
            imported = redact_profile_payload(imported)
        emit(CommandResult(True, "auth profile import", data=imported), as_json)
    except json.JSONDecodeError as exc:
        fail("auth profile import", HarnessError("Profile import file must be valid JSON.", details={"file": str(input_file)}), as_json)
    except Exception as exc:
        fail("auth profile import", exc, as_json)


@auth.command("check")
@click.option("--scope", "scopes", multiple=True, required=True, help="Scope/permission to check. Repeatable or space-separated.")
@click.option("--verify", is_flag=True, help="Also call userInfo to inspect server-side permissionCodeList when available.")
@click.pass_context
def auth_check(ctx: click.Context, scopes: tuple[str, ...], verify: bool) -> None:
    """Check local credential scopes and optionally verify against backend userInfo."""
    as_json = ctx.obj["json"]
    try:
        required = split_scope_args(scopes)
        data = check_scopes(required, identity=request_identity(ctx))
        if verify:
            server = request_api("GET", "/api/auth/v1/userInfo", auth=True, identity=request_identity(ctx))
            data["server"] = server
            permissions = []
            if isinstance(server.get("data"), dict):
                raw = server["data"].get("permissionCodeList") or server["data"].get("permissions") or []
                if isinstance(raw, list):
                    permissions = [str(item) for item in raw]
            data["serverPermissions"] = permissions
            missing = [scope for scope in required if scope not in permissions]
            data["serverMissing"] = missing
            data["ok"] = bool(server.get("ok")) and not missing
        ok = bool(data.get("ok"))
        emit(CommandResult(ok, "auth check", data=data, errors=[] if ok else ["Required scopes/permissions are missing or unknown."]), as_json)
        if not ok:
            raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as exc:
        fail("auth check", exc, as_json)


@auth.command("scopes")
@click.option("--from-server", is_flag=True, help="Call /api/auth/v1/userInfo and return permissionCodeList.")
@click.pass_context
def auth_scopes(ctx: click.Context, from_server: bool) -> None:
    """Show known scopes/permissions for the selected identity."""
    as_json = ctx.obj["json"]
    try:
        data = credential_status(request_identity(ctx))
        if from_server:
            data["server"] = request_api("GET", "/api/auth/v1/userInfo", auth=True, identity=request_identity(ctx))
        emit(CommandResult(True, "auth scopes", data=data), as_json)
    except Exception as exc:
        fail("auth scopes", exc, as_json)


@auth.group("credential")
def auth_credential() -> None:
    """Lark-style credential inspection helpers."""


@auth_credential.command("list")
@click.pass_context
def auth_credential_list(ctx: click.Context) -> None:
    """List selected identity and stored credential previews."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "auth credential list", data=credential_status(request_identity(ctx))), as_json)
    except Exception as exc:
        fail("auth credential list", exc, as_json)


@auth_credential.command("set")
@click.option("--token", required=True, help="Access token to store.")
@click.option("--profile", "profile_name", required=True, help="Named profile that owns the credential.")
@click.option("--identity", type=click.Choice(["user", "service"]), default="user", show_default=True)
@click.option("--scope", "scopes", multiple=True, help="Known scope/permission. Repeatable or space-separated.")
@click.option("--activate", is_flag=True, help="Use this profile/identity immediately.")
@click.pass_context
def auth_credential_set(ctx: click.Context, token: str, profile_name: str, identity: str, scopes: tuple[str, ...], activate: bool) -> None:
    """Store a user or service credential inside a named profile."""
    as_json = ctx.obj["json"]
    try:
        data = save_profile_credential(profile_name, token, identity=identity, scopes=split_scope_args(scopes), activate=activate)
        emit(CommandResult(True, "auth credential set", data=data), as_json)
    except Exception as exc:
        fail("auth credential set", exc, as_json)


@auth.command("login")
@click.option("--method", type=click.Choice(["sms", "password", "token"]), default="sms", show_default=True)
@click.option("--phone", default=None)
@click.option("--code", default=None, help="SMS code for --method sms.")
@click.option("--password", default=None, help="Password for --method password.")
@click.option("--token", default=None, help="Existing token for --method token.")
@click.option("--profile", "profile_name", default=None, help="Save and activate a named profile.")
@click.option("--identity", type=click.Choice(["user", "service"]), default="user", show_default=True)
@click.option("--scope", "scopes", multiple=True, help="Known scope/permission. Repeatable or space-separated.")
@click.pass_context
def auth_login(
    ctx: click.Context,
    method: str,
    phone: str | None,
    code: str | None,
    password: str | None,
    token: str | None,
    profile_name: str | None,
    identity: str,
    scopes: tuple[str, ...],
) -> None:
    """Unified login entry, shaped like Lark auth login but backed by CHEK auth methods."""
    as_json = ctx.obj["json"]
    try:
        if method == "token":
            if not token:
                raise HarnessError("--token is required for token login.")
            scope_list = split_scope_args(scopes)
            save_token(token, source="manual", identity=identity, scopes=scope_list)
            data = {"token": token_summary()}
            if profile_name:
                data["profile"] = save_profile_credential(profile_name, token, identity=identity, scopes=scope_list, activate=True)
            emit(CommandResult(True, "auth login", data=data), as_json)
            return
        if method == "sms":
            if not phone or not code:
                raise HarnessError("--phone and --code are required for sms login. Use auth sms-send first.")
            result = sms_login(phone, code)
            if profile_name and result.get("ok"):
                result["savedProfile"] = redact_profile_payload(save_profile(profile_name, include_token=True, set_active=True))
            emit_api(ctx, "auth login", result)
            return
        if method == "password":
            if not phone or not password:
                raise HarnessError("--phone and --password are required for password login.")
            result = login_with_password(phone, password)
            if profile_name and result.get("ok"):
                result["savedProfile"] = redact_profile_payload(save_profile(profile_name, include_token=True, set_active=True))
            emit_api(ctx, "auth login", result)
            return
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("auth login", exc, as_json)


@auth.command("sms-send")
@click.option("--phone", required=True, help="Mobile phone number.")
@click.option("--scene", default="login", show_default=True)
@click.pass_context
def auth_sms_send(ctx: click.Context, phone: str, scene: str) -> None:
    """Send a login SMS code."""
    try:
        emit_api(ctx, "auth sms-send", sms_send(phone, scene))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("auth sms-send", exc, ctx.obj["json"])


@auth.command("sms-login")
@click.option("--phone", required=True, help="Mobile phone number.")
@click.option("--code", required=True, help="SMS verification code.")
@click.pass_context
def auth_sms_login(ctx: click.Context, phone: str, code: str) -> None:
    """Login with SMS code and store the access token."""
    try:
        emit_api(ctx, "auth sms-login", sms_login(phone, code))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("auth sms-login", exc, ctx.obj["json"])


@auth.command("login-password")
@click.option("--phone", required=True, help="Mobile phone number.")
@click.option("--password", required=True, help="Password for CHEK account.")
@click.pass_context
def auth_login_password(ctx: click.Context, phone: str, password: str) -> None:
    """Login with phone/password and store the access token."""
    try:
        emit_api(ctx, "auth login-password", login_with_password(phone, password))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("auth login-password", exc, ctx.obj["json"])


@main.command("schema")
@click.argument("schema_path", required=False)
@click.pass_context
def schema_cmd(ctx: click.Context, schema_path: str | None) -> None:
    """Inspect known CHEK API service/resource/method schemas."""
    as_json = ctx.obj["json"]
    try:
        schema = get_schema(schema_path)
        if schema_path and not schema:
            raise HarnessError("Schema path not found.", details={"schemaPath": schema_path})
        emit(CommandResult(True, "schema", data={"schemaPath": schema_path, "schema": schema}), as_json)
    except Exception as exc:
        fail("schema", exc, as_json)


@main.group("registry")
def registry_group() -> None:
    """Inspect generated OpenAPI registry coverage."""


@registry_group.command("status")
@click.pass_context
def registry_status(ctx: click.Context) -> None:
    """Show OpenAPI source and operation coverage."""
    emit(CommandResult(True, "registry status", data=REGISTRY_META), ctx.obj["json"])


@main.command("manifest")
@click.option("--include-operations", is_flag=True, help="Include operation-level command/schema manifest.")
@click.option("--operation-limit", type=int, default=0, show_default=True, help="Limit returned operations; 0 means all.")
@click.pass_context
def manifest_cmd(ctx: click.Context, include_operations: bool, operation_limit: int) -> None:
    """Emit an agent-native capability manifest."""
    data = {
        "name": "CHEK CLI",
        "version": __version__,
        "defaultOutput": "json",
        "identityModel": {
            "pattern": "Lark-style --as identity switching",
            "choices": list(IDENTITY_CHOICES),
            "default": load_config().get("default_as"),
            "meaning": {
                "auto": "Use the selected profile/token if available.",
                "user": "Use a stored user credential.",
                "service": "Use a stored service/application credential.",
                "none": "Do not attach auth headers.",
            },
        },
        "commands": {
            "config": ["config show", "config set-env", "config set-origin", "config default-as", "config secret-store"],
            "auth": ["auth login", "auth status", "auth check", "auth scopes", "auth profile", "auth credential"],
            "api": ["schema", "call", "api", "examples", "smoke api"],
            "aiProduct": [
                "ai-product +research-plan",
                "ai-product +duplicate-check",
                "ai-product +publish",
                "ai-product +edit",
                "ai-product +robot-version-edit",
                "ai-product +vehicle-version-edit",
                "ai-product +review",
                "ai-product +list",
                "ai-product +detail",
            ],
            "media": ["media +upload-cover"],
            "workflows": [item["command"] for item in CURATED_EXAMPLES],
        },
        "registry": registry_operation_manifest(include_operations, limit=operation_limit),
        "examples": CURATED_EXAMPLES,
    }
    emit(CommandResult(True, "manifest", data=data), ctx.obj["json"])


@main.group("examples")
def examples_group() -> None:
    """Generate agent-friendly examples for shortcuts and registry operations."""


@examples_group.command("list")
@click.option("--domain", default=None, help="Filter curated examples by domain, e.g. vehicle/humanoid.")
@click.option("--limit", type=int, default=20, show_default=True)
@click.pass_context
def examples_list(ctx: click.Context, domain: str | None, limit: int) -> None:
    """List curated high-value agent examples."""
    examples = CURATED_EXAMPLES
    if domain:
        domain_l = domain.lower()
        examples = [
            item
            for item in examples
            if domain_l in str(item.get("domain", "")).lower()
            or any(domain_l in str(label).lower() for label in item.get("positioning", []))
        ]
    emit(CommandResult(True, "examples list", data={"examples": examples[: max(0, limit)], "count": len(examples)}), ctx.obj["json"])


@examples_group.command("show")
@click.argument("name_or_schema")
@click.pass_context
def examples_show(ctx: click.Context, name_or_schema: str) -> None:
    """Show a curated example or generated OpenAPI operation example."""
    as_json = ctx.obj["json"]
    try:
        curated = next((item for item in CURATED_EXAMPLES if item["name"] == name_or_schema), None)
        if curated:
            generated = [generated_example(path) for path in curated.get("schemaPaths", []) if find_method(*path.split("."))]
            emit(CommandResult(True, "examples show", data={"example": curated, "generated": generated}), as_json)
            return
        emit(CommandResult(True, "examples show", data=generated_example(name_or_schema)), as_json)
    except Exception as exc:
        fail("examples show", exc, as_json)


@examples_group.command("generate")
@click.option("--service", default=None, help="Filter registry operations by service.")
@click.option("--resource", default=None, help="Filter registry operations by resource.")
@click.option("--limit", type=int, default=50, show_default=True)
@click.pass_context
def examples_generate(ctx: click.Context, service: str | None, resource: str | None, limit: int) -> None:
    """Generate example commands from the OpenAPI registry."""
    as_json = ctx.obj["json"]
    try:
        paths = iter_schema_paths()
        if service:
            paths = [path for path in paths if path.startswith(service + ".")]
        if resource:
            paths = [path for path in paths if len(path.split(".")) == 3 and path.split(".")[1] == resource]
        selected = paths[: max(0, limit)]
        emit(
            CommandResult(
                True,
                "examples generate",
                data={"count": len(paths), "returned": len(selected), "examples": [generated_example(path) for path in selected]},
            ),
            as_json,
        )
    except Exception as exc:
        fail("examples generate", exc, as_json)


@main.group("smoke")
def smoke_group() -> None:
    """Run safe smoke checks for agent-facing backend capabilities."""


@smoke_group.command("api")
@click.option("--service", "services", multiple=True, help="Limit checks to one or more services.")
@click.option("--include-authenticated", is_flag=True, help="Include read-only checks that may require a token.")
@click.option("--include-auth-check", is_flag=True, help="Also call backend-app checkToken with the stored token.")
@click.option("--timeout", type=int, default=15, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def smoke_api(
    ctx: click.Context,
    services: tuple[str, ...],
    include_authenticated: bool,
    include_auth_check: bool,
    timeout: int,
    dry_run: bool,
) -> None:
    """Smoke-test safe read-only dev endpoints."""
    service_filter = set(services)
    steps: list[dict[str, object]] = []
    for service, schema_path, requires_auth in SAFE_READONLY_SMOKE:
        if service_filter and service not in service_filter:
            continue
        if requires_auth and not include_authenticated:
            continue
        parts = schema_path.split(".")
        method_schema = find_method(parts[0], parts[1], parts[2]) if len(parts) == 3 else None
        if not method_schema:
            continue
        steps.append(
            workflow_step(
                schema_path,
                "Safe read-only backend smoke check.",
                schema_path,
                str(method_schema.get("httpMethod") or "GET"),
                str(method_schema["path"]),
                auth=bool(requires_auth),
            )
        )
    if include_auth_check:
        steps.append(
            workflow_step(
                "backend-app.checkToken",
                "Verify the active auth token against backend-app.",
                None,
                "GET",
                "/api/backend-app/login/checkToken",
                auth=True,
            )
        )
    if not steps:
        fail("smoke api", HarnessError("No smoke checks selected.", details={"services": list(services)}), ctx.obj["json"])
    try:
        execute_workflow(
            ctx,
            command="smoke api",
            objective="Safe read-only API smoke checks for agent sessions.",
            steps=steps,
            dry_run=dry_run,
            timeout=timeout,
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("smoke api", exc, ctx.obj["json"])


@smoke_group.command("auth")
@click.option("--timeout", type=int, default=15, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def smoke_auth(ctx: click.Context, timeout: int, dry_run: bool) -> None:
    """Smoke-test authenticated identity, token, and user permission introspection."""
    steps = [
        workflow_step(
            "check-token",
            "Verify the selected credential against backend-app.",
            None,
            "GET",
            "/api/backend-app/login/checkToken",
            auth=True,
        ),
        workflow_step(
            "user-info",
            "Fetch user identity and permissionCodeList when supported by auth backend.",
            "auth.userInfo.list",
            "GET",
            "/api/auth/v1/userInfo",
            auth=True,
        ),
    ]
    try:
        execute_workflow(
            ctx,
            command="smoke auth",
            objective="Authenticated smoke checks for the selected CHEK identity.",
            steps=steps,
            dry_run=dry_run,
            timeout=timeout,
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("smoke auth", exc, ctx.obj["json"])


@main.group("ai-product")
def ai_product() -> None:
    """AI product publication, duplicate-check, and review shortcuts."""


def build_ai_product_from_options(
    *,
    from_file: Path | None,
    category: str | None,
    product_name: str | None,
    hardware_model: str | None,
    software_version: str | None,
    tags: tuple[str, ...],
) -> tuple[dict, dict]:
    raw_payload = parse_json_arg(from_file.read_text(encoding="utf-8"), flag_name="--from-file") if from_file else {}
    if raw_payload is None:
        raw_payload = {}
    if not isinstance(raw_payload, dict):
        raise HarnessError("--from-file must contain a JSON object.")
    product = product_from_inputs(
        category=category,
        product_name=product_name,
        hardware_model=hardware_model,
        software_version=software_version,
        tags=tags,
        payload=raw_payload,
    )
    return product, raw_payload


def emit_duplicate_block(
    ctx: click.Context,
    *,
    command: str,
    product: dict,
    duplicate_result: dict,
    publish_payload: dict | None = None,
) -> None:
    emit(
        CommandResult(
            False,
            command,
            data={
                "blockedByDuplicate": True,
                "product": product,
                "duplicateCheck": duplicate_result,
                "publishPayload": publish_payload,
                "agentGuidance": [
                    "进入 matchedPost/candidates 里的已有房间继续评测。",
                    "只有确认不是同一硬件型号 + 软件版本时，才改产品身份后重新发布。",
                    "确需重复发布时可显式使用 --duplicate-policy allow。",
                ],
            },
            errors=["Duplicate AI product review room found; publish was not executed."],
        ),
        ctx.obj["json"],
    )
    raise SystemExit(1)


@main.group()
def media() -> None:
    """CHEK media helpers for product covers and evidence assets."""


@media.command("+upload-cover")
@click.option("--file", "cover_file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, help="Local cover image file downloaded from a researched source.")
@click.option("--source-url", required=True, help="Original web page or image URL used to verify the cover.")
@click.option("--title", default="", help="Optional human-readable asset title.")
@click.option("--purpose", default="ai_product_cover", show_default=True)
@click.option("--media-kind", type=click.Choice(["image", "file"]), default="image", show_default=True)
@click.option("--field-name", default="file", show_default=True, help="Multipart field name expected by the media endpoint.")
@click.option("--content-type", default="", help="Override MIME type. Defaults to file extension detection.")
@click.option("--timeout", type=int, default=60, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def media_upload_cover(
    ctx: click.Context,
    cover_file: Path,
    source_url: str,
    title: str,
    purpose: str,
    media_kind: str,
    field_name: str,
    content_type: str,
    timeout: int,
    dry_run: bool,
) -> None:
    """Upload a researched cover image to CHEK media for formal AI product publication."""
    try:
        endpoint = "/api/backend-app/media/v1/images" if media_kind == "image" else "/api/backend-app/media/v1/files"
        resolved_type = content_type or mimetypes.guess_type(cover_file.name)[0] or "application/octet-stream"
        result = request_multipart_api(
            "POST",
            endpoint,
            files={field_name: (cover_file.name, cover_file.read_bytes(), resolved_type)},
            fields={
                "purpose": purpose,
                "sourceUrl": source_url,
                "source_url": source_url,
                "title": title or cover_file.stem,
            },
            auth=True,
            identity=request_identity(ctx),
            timeout=timeout,
            dry_run=dry_run,
        )
        if isinstance(result, dict):
            result = {
                **result,
                "coverSourceUrl": source_url,
                "agentGuidance": [
                    "Use the returned CHEK media URL as --cover-image-url.",
                    "Keep the original source URL as --cover-source-url.",
                    "Do not use dev media URLs for formal production review rooms.",
                ],
            }
        emit_api(ctx, "media +upload-cover", result)
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("media +upload-cover", exc, ctx.obj["json"])


@ai_product.command("+research-plan")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="JSON draft to enrich.")
@click.option("--category", type=click.Choice(AI_PRODUCT_CATEGORIES), default=None)
@click.option("--product-name", default=None)
@click.option("--hardware-model", default=None)
@click.option("--software-version", default=None)
@click.option("--tag", "tags", multiple=True, help="Product/entity tag. Repeatable or comma-separated.")
@click.pass_context
def ai_product_research_plan(
    ctx: click.Context,
    from_file: Path | None,
    category: str | None,
    product_name: str | None,
    hardware_model: str | None,
    software_version: str | None,
    tags: tuple[str, ...],
) -> None:
    """Build the web-search and duplicate-check plan an agent should run before publishing."""
    as_json = ctx.obj["json"]
    try:
        product, raw_payload = build_ai_product_from_options(
            from_file=from_file,
            category=category,
            product_name=product_name,
            hardware_model=hardware_model,
            software_version=software_version,
            tags=tags,
        )
        emit(
            CommandResult(
                True,
                "ai-product +research-plan",
                data={
                    "product": product,
                    "inputPayload": raw_payload,
                    "researchPlan": build_research_plan(product),
                    "nextCliCommands": [
                        "chek ai-product +duplicate-check ...",
                        "chek ai-product +publish --source-url <url> --reason <why> ...",
                        "chek ai-product +review --post-id <uuid> --stars <1-5> --evidence <text>",
                    ],
                },
            ),
            as_json,
        )
    except Exception as exc:
        fail("ai-product +research-plan", exc, as_json)


@ai_product.command("+duplicate-check")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--category", type=click.Choice(AI_PRODUCT_CATEGORIES), default=None)
@click.option("--product-name", default=None)
@click.option("--hardware-model", default=None)
@click.option("--software-version", default=None)
@click.option("--tag", "tags", multiple=True)
@click.option("--exclude-post-id", default=None, help="Exclude this post when checking an edit.")
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_duplicate_check(
    ctx: click.Context,
    from_file: Path | None,
    category: str | None,
    product_name: str | None,
    hardware_model: str | None,
    software_version: str | None,
    tags: tuple[str, ...],
    exclude_post_id: str | None,
    timeout: int,
    dry_run: bool,
) -> None:
    """Check whether an AI product version has already been submitted."""
    try:
        product, _ = build_ai_product_from_options(
            from_file=from_file,
            category=category,
            product_name=product_name,
            hardware_model=hardware_model,
            software_version=software_version,
            tags=tags,
        )
        result = request_api(
            "POST",
            "/api/backend-app/buddy/v1/posts/duplicate-check",
            data=duplicate_check_payload(product, exclude_post_id=exclude_post_id),
            auth=True,
            identity=request_identity(ctx),
            timeout=timeout,
            dry_run=dry_run,
        )
        emit_api(ctx, "ai-product +duplicate-check", result)
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +duplicate-check", exc, ctx.obj["json"])


@ai_product.command("+publish")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="JSON draft. CLI flags override matching fields.")
@click.option("--category", type=click.Choice(AI_PRODUCT_CATEGORIES), default=None)
@click.option("--product-name", default=None)
@click.option("--hardware-model", default=None, help="Optional for pure software products.")
@click.option("--software-version", default=None, help="Required; AI product scores are version-specific.")
@click.option("--tag", "tags", multiple=True)
@click.option("--reason", default="")
@click.option("--scenario", default="")
@click.option("--evidence", default="")
@click.option("--evidence-url", "evidence_urls", multiple=True)
@click.option("--source-url", "source_urls", multiple=True, help="Web source collected by the agent before publish.")
@click.option("--source-title", "source_titles", multiple=True)
@click.option("--interest-relation", type=click.Choice(AI_PRODUCT_INTEREST_RELATIONS), default="普通用户", show_default=True)
@click.option("--cover-image-url", default="")
@click.option("--cover-source-url", default="", help="Original web page or image URL used to verify the cover before upload.")
@click.option("--media-type", default="image", show_default=True)
@click.option("--media-url", default="")
@click.option(
    "--linked-entity",
    "linked_entities",
    multiple=True,
    help="Bound library entity as JSON or key=value pairs, e.g. targetType=humanoid_robot,targetId=...,title=Unitree H1.",
)
@click.option("--target-id", default="")
@click.option("--opening-message", default="")
@click.option("--duplicate-policy", type=click.Choice(["stop", "allow"]), default="stop", show_default=True)
@click.option("--check-duplicate/--no-check-duplicate", default=True, show_default=True)
@click.option("--require-source/--no-require-source", default=False, show_default=True)
@click.option("--formal/--draft", default=False, show_default=True, help="Enforce official submission requirements.")
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_publish(
    ctx: click.Context,
    from_file: Path | None,
    category: str | None,
    product_name: str | None,
    hardware_model: str | None,
    software_version: str | None,
    tags: tuple[str, ...],
    reason: str,
    scenario: str,
    evidence: str,
    evidence_urls: tuple[str, ...],
    source_urls: tuple[str, ...],
    source_titles: tuple[str, ...],
    interest_relation: str,
    cover_image_url: str,
    cover_source_url: str,
    media_type: str,
    media_url: str,
    linked_entities: tuple[str, ...],
    target_id: str,
    opening_message: str,
    duplicate_policy: str,
    check_duplicate: bool,
    require_source: bool,
    formal: bool,
    timeout: int,
    dry_run: bool,
) -> None:
    """Publish an AI product review room after research and duplicate-check."""
    try:
        product, raw_payload = build_ai_product_from_options(
            from_file=from_file,
            category=category,
            product_name=product_name,
            hardware_model=hardware_model,
            software_version=software_version,
            tags=tags,
        )
        if require_source and not any([source_urls, evidence_urls, evidence]):
            emit(
                CommandResult(
                    False,
                    "ai-product +publish",
                    data={"product": product, "researchPlan": build_research_plan(product)},
                    errors=["No source/evidence was provided; run the research plan first or pass --no-require-source."],
                ),
                ctx.obj["json"],
            )
            raise SystemExit(1)
        publish_payload = build_publish_payload(
            product=product,
            reason=reason,
            scenario=scenario,
            evidence=evidence,
            evidence_urls=evidence_urls,
            interest_relation=interest_relation,
            source_urls=source_urls,
            source_titles=source_titles,
            cover_image_url=cover_image_url,
            cover_source_url=cover_source_url,
            media_type=media_type,
            media_url=media_url,
            linked_entities=linked_entities,
            target_id=target_id,
            opening_message=opening_message,
            payload=raw_payload,
        )
        if formal:
            review_root = publish_payload.get("extras", {}).get("ai_product_review", {})
            formal_errors = validate_formal_submission(
                product=product,
                research_sources=review_root.get("research_sources") if isinstance(review_root, dict) else [],
                linked_entities=publish_payload.get("extras", {}).get("linkedEntities", []),
                cover_image_url=publish_payload.get("coverImageUrl", ""),
                cover_source_url=review_root.get("coverSourceUrl", "") if isinstance(review_root, dict) else "",
            )
            if formal_errors:
                emit(
                    CommandResult(
                        False,
                        "ai-product +publish",
                        data={"product": product, "researchPlan": build_research_plan(product), "publishPayload": publish_payload},
                        errors=formal_errors,
                    ),
                    ctx.obj["json"],
                )
                raise SystemExit(1)
        duplicate_result = None
        if check_duplicate:
            duplicate_result = request_api(
                "POST",
                "/api/backend-app/buddy/v1/posts/duplicate-check",
                data=duplicate_check_payload(product),
                auth=True,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            )
            duplicate_data = duplicate_result.get("data") if isinstance(duplicate_result, dict) else {}
            if (
                not dry_run
                and duplicate_policy == "stop"
                and bool(duplicate_result.get("ok"))
                and isinstance(duplicate_data, dict)
                and duplicate_data.get("duplicate")
            ):
                emit_duplicate_block(
                    ctx,
                    command="ai-product +publish",
                    product=product,
                    duplicate_result=duplicate_result,
                    publish_payload=publish_payload,
                )
        publish_result = request_api(
            "POST",
            "/api/backend-app/buddy/v1/posts",
            data=publish_payload,
            auth=True,
            identity=request_identity(ctx),
            timeout=timeout,
            dry_run=dry_run,
        )
        ok = bool(publish_result.get("ok")) and (not duplicate_result or bool(duplicate_result.get("ok")))
        emit(
            CommandResult(
                ok,
                "ai-product +publish",
                data={
                    "dryRun": dry_run,
                    "product": product,
                    "formal": formal,
                    "researchPlan": build_research_plan(product),
                    "duplicateCheck": duplicate_result,
                    "publish": publish_result,
                },
                errors=[] if ok else ["AI product publish failed."],
            ),
            ctx.obj["json"],
        )
        if not ok:
            raise SystemExit(1)
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +publish", exc, ctx.obj["json"])


@ai_product.command("+edit")
@click.option("--post-id", required=True)
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--category", type=click.Choice(AI_PRODUCT_CATEGORIES), default=None)
@click.option("--product-name", default=None)
@click.option("--hardware-model", default=None)
@click.option("--software-version", default=None)
@click.option("--tag", "tags", multiple=True)
@click.option("--reason", default="")
@click.option("--scenario", default="")
@click.option("--evidence", default="")
@click.option("--evidence-url", "evidence_urls", multiple=True)
@click.option("--source-url", "source_urls", multiple=True)
@click.option("--source-title", "source_titles", multiple=True)
@click.option("--interest-relation", type=click.Choice(AI_PRODUCT_INTEREST_RELATIONS), default="普通用户", show_default=True)
@click.option("--cover-image-url", default="")
@click.option("--cover-source-url", default="")
@click.option("--media-type", default="image", show_default=True)
@click.option("--media-url", default="")
@click.option("--linked-entity", "linked_entities", multiple=True)
@click.option("--target-id", default="")
@click.option("--opening-message", default="")
@click.option("--check-duplicate/--no-check-duplicate", default=True, show_default=True)
@click.option("--formal/--draft", default=False, show_default=True)
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_edit(
    ctx: click.Context,
    post_id: str,
    from_file: Path | None,
    category: str | None,
    product_name: str | None,
    hardware_model: str | None,
    software_version: str | None,
    tags: tuple[str, ...],
    reason: str,
    scenario: str,
    evidence: str,
    evidence_urls: tuple[str, ...],
    source_urls: tuple[str, ...],
    source_titles: tuple[str, ...],
    interest_relation: str,
    cover_image_url: str,
    cover_source_url: str,
    media_type: str,
    media_url: str,
    linked_entities: tuple[str, ...],
    target_id: str,
    opening_message: str,
    check_duplicate: bool,
    formal: bool,
    timeout: int,
    dry_run: bool,
) -> None:
    """Edit an AI product room. Changing product identity should create a new room instead."""
    try:
        product, raw_payload = build_ai_product_from_options(
            from_file=from_file,
            category=category,
            product_name=product_name,
            hardware_model=hardware_model,
            software_version=software_version,
            tags=tags,
        )
        publish_payload = build_publish_payload(
            product=product,
            reason=reason,
            scenario=scenario,
            evidence=evidence,
            evidence_urls=evidence_urls,
            interest_relation=interest_relation,
            source_urls=source_urls,
            source_titles=source_titles,
            cover_image_url=cover_image_url,
            cover_source_url=cover_source_url,
            media_type=media_type,
            media_url=media_url,
            linked_entities=linked_entities,
            target_id=target_id,
            opening_message=opening_message,
            payload=raw_payload,
        )
        if formal:
            review_root = publish_payload.get("extras", {}).get("ai_product_review", {})
            formal_errors = validate_formal_submission(
                product=product,
                research_sources=review_root.get("research_sources") if isinstance(review_root, dict) else [],
                linked_entities=publish_payload.get("extras", {}).get("linkedEntities", []),
                cover_image_url=publish_payload.get("coverImageUrl", ""),
                cover_source_url=review_root.get("coverSourceUrl", "") if isinstance(review_root, dict) else "",
            )
            if formal_errors:
                emit(
                    CommandResult(
                        False,
                        "ai-product +edit",
                        data={"product": product, "publishPayload": publish_payload},
                        errors=formal_errors,
                    ),
                    ctx.obj["json"],
                )
                raise SystemExit(1)
        duplicate_result = None
        if check_duplicate:
            duplicate_result = request_api(
                "POST",
                "/api/backend-app/buddy/v1/posts/duplicate-check",
                data=duplicate_check_payload(product, exclude_post_id=post_id),
                auth=True,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            )
        edit_result = request_api(
            "PATCH",
            f"/api/backend-app/buddy/v1/posts/{quote_path_value(post_id)}",
            data=publish_payload,
            auth=True,
            identity=request_identity(ctx),
            timeout=timeout,
            dry_run=dry_run,
        )
        ok = bool(edit_result.get("ok")) and (not duplicate_result or bool(duplicate_result.get("ok")))
        emit(
            CommandResult(
                ok,
                "ai-product +edit",
                data={
                    "dryRun": dry_run,
                    "product": product,
                    "identityChangePolicy": "Backend rejects product identity changes; create a new room for a new hardware/software version.",
                    "duplicateCheck": duplicate_result,
                    "edit": edit_result,
                },
                errors=[] if ok else ["AI product edit failed."],
            ),
            ctx.obj["json"],
        )
        if not ok:
            raise SystemExit(1)
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +edit", exc, ctx.obj["json"])


@ai_product.command("+robot-version-edit")
@click.option("--robot-id", required=True, help="Existing humanoid robot library id.")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--category", type=click.Choice(AI_PRODUCT_CATEGORIES), default="具身机器人", show_default=True)
@click.option("--product-name", default=None)
@click.option("--hardware-model", default=None)
@click.option("--software-version", default=None)
@click.option("--tag", "tags", multiple=True)
@click.option("--source-repo", default="")
@click.option("--source-commit", default="")
@click.option("--post-id", default="", help="AI product review room id to link back.")
@click.option("--checked-at", default="")
@click.option("--title", default="")
@click.option("--description", default="")
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_robot_version_edit(
    ctx: click.Context,
    robot_id: str,
    from_file: Path | None,
    category: str | None,
    product_name: str | None,
    hardware_model: str | None,
    software_version: str | None,
    tags: tuple[str, ...],
    source_repo: str,
    source_commit: str,
    post_id: str,
    checked_at: str,
    title: str,
    description: str,
    timeout: int,
    dry_run: bool,
) -> None:
    """Submit a robot config-version edit for a formal AI product review room."""
    try:
        product, _ = build_ai_product_from_options(
            from_file=from_file,
            category=category,
            product_name=product_name,
            hardware_model=hardware_model,
            software_version=software_version,
            tags=tags,
        )
        body = robot_config_version_edit_payload(
            product=product,
            source_repo=source_repo,
            source_commit=source_commit,
            buddy_post_id=post_id,
            checked_at=checked_at,
            title=title,
            description=description,
        )
        emit_api(
            ctx,
            "ai-product +robot-version-edit",
            request_api(
                "POST",
                f"/api/humanoid-chain/robots/{quote_path_value(robot_id)}/edits",
                data=body,
                auth=True,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            ),
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +robot-version-edit", exc, ctx.obj["json"])


@ai_product.command("+vehicle-version-edit")
@click.option("--vehicle-id", required=True, help="Existing vehicle library id.")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--category", type=click.Choice(AI_PRODUCT_CATEGORIES), default="智能汽车", show_default=True)
@click.option("--product-name", default=None)
@click.option("--hardware-model", default=None)
@click.option("--software-version", default=None)
@click.option("--tag", "tags", multiple=True)
@click.option("--title", default="")
@click.option("--description", default="")
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_vehicle_version_edit(
    ctx: click.Context,
    vehicle_id: str,
    from_file: Path | None,
    category: str | None,
    product_name: str | None,
    hardware_model: str | None,
    software_version: str | None,
    tags: tuple[str, ...],
    title: str,
    description: str,
    timeout: int,
    dry_run: bool,
) -> None:
    """Submit a vehicle hardware/software version edit for a formal AI product review room."""
    try:
        product, _ = build_ai_product_from_options(
            from_file=from_file,
            category=category,
            product_name=product_name,
            hardware_model=hardware_model,
            software_version=software_version,
            tags=tags,
        )
        body = vehicle_sync_versions_edit_payload(product=product, title=title, description=description)
        emit_api(
            ctx,
            "ai-product +vehicle-version-edit",
            request_api(
                "POST",
                f"/api/vms/api/vehicles/{quote_path_value(vehicle_id)}/edits",
                data=body,
                auth=True,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            ),
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +vehicle-version-edit", exc, ctx.obj["json"])


@ai_product.command("+review")
@click.option("--post-id", required=True)
@click.option("--rating", type=float, default=None, help="0-10 score. Mutually replaceable with --stars.")
@click.option("--stars", type=float, default=None, help="Douban-style 0.5-5 star score.")
@click.option("--comment", default="")
@click.option("--evidence", default="")
@click.option("--evidence-url", "evidence_urls", multiple=True)
@click.option("--interest-relation", type=click.Choice(AI_PRODUCT_INTEREST_RELATIONS), default="普通用户", show_default=True)
@click.option("--tested-version-confirmed/--version-not-confirmed", default=True, show_default=True)
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_review(
    ctx: click.Context,
    post_id: str,
    rating: float | None,
    stars: float | None,
    comment: str,
    evidence: str,
    evidence_urls: tuple[str, ...],
    interest_relation: str,
    tested_version_confirmed: bool,
    timeout: int,
    dry_run: bool,
) -> None:
    """Submit or update the current user's rating and review evidence."""
    try:
        body = build_review_payload(
            rating=rating,
            stars=stars,
            comment=comment,
            evidence_text=evidence,
            evidence_urls=evidence_urls,
            interest_relation=interest_relation,
            tested_version_confirmed=tested_version_confirmed,
        )
        emit_api(
            ctx,
            "ai-product +review",
            request_api(
                "POST",
                f"/api/backend-app/buddy/v1/posts/{quote_path_value(post_id)}/reviews",
                data=body,
                auth=True,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            ),
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +review", exc, ctx.obj["json"])


@ai_product.command("+list")
@click.option("--scope", type=click.Choice(["all", "mine", "joined"]), default="all", show_default=True)
@click.option("--target-id", default=None)
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_list(ctx: click.Context, scope: str, target_id: str | None, timeout: int, dry_run: bool) -> None:
    """List AI product review rooms."""
    try:
        emit_api(
            ctx,
            "ai-product +list",
            request_api(
                "GET",
                "/api/backend-app/buddy/v1/posts",
                params={
                    "scope": scope,
                    "postType": "ai_product_review",
                    "targetType": "ai_product",
                    "targetId": target_id,
                },
                auth=True,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            ),
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +list", exc, ctx.obj["json"])


@ai_product.command("+detail")
@click.option("--post-id", required=True)
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def ai_product_detail(ctx: click.Context, post_id: str, timeout: int, dry_run: bool) -> None:
    """Fetch an AI product review room by post id."""
    try:
        emit_api(
            ctx,
            "ai-product +detail",
            request_api(
                "GET",
                f"/api/backend-app/buddy/v1/posts/{quote_path_value(post_id)}",
                auth=True,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            ),
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("ai-product +detail", exc, ctx.obj["json"])


@main.command("call")
@click.argument("schema_path")
@click.option("--path", "path_args", multiple=True, help="Path argument as key=value. Repeatable.")
@click.option("--param", "param_args", multiple=True, help="Query parameter as key=value. Repeatable.")
@click.option("--params", default=None, help="JSON query params. Use '-' to read stdin.")
@click.option("--data", "body", default=None, help="JSON request body. Use '-' to read stdin.")
@click.option("--no-auth", is_flag=True, help="Do not attach the stored access token.")
@click.option("--dry-run", is_flag=True, help="Print request envelope without calling the backend.")
@click.option("--timeout", type=int, default=30, show_default=True)
@click.pass_context
def call_cmd(
    ctx: click.Context,
    schema_path: str,
    path_args: tuple[str, ...],
    param_args: tuple[str, ...],
    params: str | None,
    body: str | None,
    no_auth: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    """Call a known registry method by service.resource.method."""
    try:
        call_registry_method(
            ctx,
            command="call",
            schema_path=schema_path,
            path_args=path_args,
            auto_path_args={},
            params=params,
            param_args=param_args,
            body=body,
            no_auth=no_auth,
            dry_run=dry_run,
            timeout=timeout,
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("call", exc, ctx.obj["json"])


@main.command("api")
@click.argument("method")
@click.argument("path")
@click.option("--params", default=None, help="JSON query params. Use '-' to read stdin.")
@click.option("--data", "body", default=None, help="JSON request body. Use '-' to read stdin.")
@click.option("--no-auth", is_flag=True, help="Do not attach the stored access token.")
@click.option("--dry-run", is_flag=True, help="Print request envelope without calling the backend.")
@click.option("--timeout", type=int, default=30, show_default=True)
@click.pass_context
def api_cmd(ctx: click.Context, method: str, path: str, params: str | None, body: str | None, no_auth: bool, dry_run: bool, timeout: int) -> None:
    """Call any CHEK backend API path directly."""
    try:
        parsed_params = parse_json_arg(params, stdin=sys.stdin, flag_name="--params") or {}
        parsed_body = parse_json_arg(body, stdin=sys.stdin, flag_name="--data")
        emit_api(
            ctx,
            "api",
            request_api(
                method,
                path,
                params=parsed_params,
                data=parsed_body,
                auth=not no_auth,
                identity=request_identity(ctx),
                timeout=timeout,
                dry_run=dry_run,
            ),
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("api", exc, ctx.obj["json"])


@main.group()
def vehicle() -> None:
    """Vehicle metadata API shortcuts."""


@vehicle.command("+search")
@click.option("--query", "queries", multiple=True, required=True, help="Search query. Repeat for batch search.")
@click.option("--top-k", type=int, default=10, show_default=True)
@click.option("--include-details/--ids-only", default=True, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def vehicle_search(ctx: click.Context, queries: tuple[str, ...], top_k: int, include_details: bool, dry_run: bool) -> None:
    """Search vehicles using the same backend API as the app."""
    body = {
        "queries": [{"query": query, "topK": top_k} for query in queries],
        "options": {"includeDetails": include_details},
    }
    try:
        emit_api(ctx, "vehicle +search", request_api("POST", "/api/vms/api/vehicles:batchSearch", data=body, identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("vehicle +search", exc, ctx.obj["json"])


@vehicle.command("detail")
@click.option("--id", "vehicle_id", required=True, help="Vehicle ID.")
@click.option("--dry-run", is_flag=True)
@click.pass_context
def vehicle_detail(ctx: click.Context, vehicle_id: str, dry_run: bool) -> None:
    """Get vehicle detail."""
    try:
        emit_api(ctx, "vehicle detail", request_api("GET", f"/api/vms/api/vehicles/{quote_path_value(vehicle_id)}", identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("vehicle detail", exc, ctx.obj["json"])


@vehicle.command("raw-params")
@click.option("--id", "vehicle_id", required=True, help="Vehicle ID.")
@click.option("--dry-run", is_flag=True)
@click.pass_context
def vehicle_raw_params(ctx: click.Context, vehicle_id: str, dry_run: bool) -> None:
    """Get vehicle raw parameter snapshot."""
    try:
        emit_api(ctx, "vehicle raw-params", request_api("GET", f"/api/vms/api/vehicles/{quote_path_value(vehicle_id)}/raw-params", identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("vehicle raw-params", exc, ctx.obj["json"])


@vehicle.command("+buying-plan")
@click.option("--query", "queries", multiple=True, required=True, help="Vehicle, brand, or buying intent. Repeatable.")
@click.option("--scene", default="urban", show_default=True, help="Ranking scene, e.g. urban/highway.")
@click.option("--city", default=None, help="Optional city context.")
@click.option("--budget", default=None, help="Optional budget context, e.g. 20-30万.")
@click.option("--top-k", type=int, default=10, show_default=True)
@click.option("--include-feed/--no-feed", default=True, show_default=True)
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def vehicle_buying_plan(
    ctx: click.Context,
    queries: tuple[str, ...],
    scene: str,
    city: str | None,
    budget: str | None,
    top_k: int,
    include_feed: bool,
    timeout: int,
    dry_run: bool,
) -> None:
    """Run the car-buying OpenClaw workflow: search, rank, and collect evidence."""
    search_body = {
        "queries": [{"query": query, "topK": top_k} for query in queries],
        "options": {
            "includeDetails": True,
            "intent": "car-buying-openclaw",
            "scene": scene,
            "city": city,
            "budget": budget,
        },
    }
    joined_query = " ".join(queries)
    steps = [
        workflow_step(
            "vehicle-search",
            "Search the intelligent vehicle database for candidate models.",
            "vehicle.vehicles.batchSearch",
            "POST",
            "/api/vms/api/vehicles:batchSearch",
            data=search_body,
        ),
        workflow_step(
            "vehicle-rank-top3",
            "Fetch scene-aware intelligent driving rankings for recommendation evidence.",
            "backend-saas.appVehicleMetrics.rankTop3",
            "GET",
            "/api/backend-saas/v1/app-vehicle-metrics/rank/top3",
            params={"scene": scene, "city": city},
        ),
    ]
    if include_feed:
        steps.append(
            workflow_step(
                "discovery-evidence",
                "Collect discovery feed evidence related to the buying intent.",
                "backend-app.discovery.feed",
                "GET",
                "/api/backend-app/discovery/v1/feed",
                params={"q": joined_query, "page": 1, "pageSize": top_k},
                auth=False,
            )
        )
    try:
        execute_workflow(
            ctx,
            command="vehicle +buying-plan",
            objective="买车 OpenClaw / AI 版汽车之家 workflow for vehicle choice reasoning.",
            steps=steps,
            dry_run=dry_run,
            timeout=timeout,
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("vehicle +buying-plan", exc, ctx.obj["json"])


@vehicle.command("+compare")
@click.option("--id", "vehicle_ids", multiple=True, required=True, help="Vehicle ID. Repeat for comparison.")
@click.option("--include-raw/--no-raw", default=False, show_default=True, help="Include raw parameter snapshots.")
@click.option("--include-software/--no-software", default=False, show_default=True, help="Include hardware/software version mappings.")
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def vehicle_compare(
    ctx: click.Context,
    vehicle_ids: tuple[str, ...],
    include_raw: bool,
    include_software: bool,
    timeout: int,
    dry_run: bool,
) -> None:
    """Compare intelligent vehicle database records by stable vehicle IDs."""
    steps: list[dict[str, object]] = []
    for vehicle_id in vehicle_ids:
        encoded = quote_path_value(vehicle_id)
        steps.append(
            workflow_step(
                f"{vehicle_id}:detail",
                "Fetch canonical vehicle metadata and presentation fields.",
                "vehicle.vehicles.detail",
                "GET",
                f"/api/vms/api/vehicles/{encoded}",
            )
        )
        if include_raw:
            steps.append(
                workflow_step(
                    f"{vehicle_id}:raw-params",
                    "Fetch raw configuration parameters for deeper 懂机帝-style comparison.",
                    "vehicle.vehicles.rawParams",
                    "GET",
                    f"/api/vms/api/vehicles/{encoded}/raw-params",
                )
            )
        if include_software:
            steps.append(
                workflow_step(
                    f"{vehicle_id}:software",
                    "Fetch available hardware/software versions.",
                    "vehicle.vehicles.software",
                    "GET",
                    f"/api/vms/api/vehicles/{encoded}/software",
                )
            )
    try:
        execute_workflow(
            ctx,
            command="vehicle +compare",
            objective="智能汽车数据库 comparison workflow.",
            steps=steps,
            dry_run=dry_run,
            timeout=timeout,
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("vehicle +compare", exc, ctx.obj["json"])


@vehicle.command("+rankings")
@click.option("--scene", default=None, help="Scene filter, e.g. urban/highway.")
@click.option("--window", default=None, help="Ranking window.")
@click.option("--vehicle-id", default=None, help="Optional vehicle ID for model detail.")
@click.option("--model", default=None, help="Optional model name for model detail.")
@click.option("--hardware-config", default=None)
@click.option("--software-config", default=None)
@click.option("--debug", type=int, default=0, show_default=True)
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def vehicle_rankings(
    ctx: click.Context,
    scene: str | None,
    window: str | None,
    vehicle_id: str | None,
    model: str | None,
    hardware_config: str | None,
    software_config: str | None,
    debug: int,
    timeout: int,
    dry_run: bool,
) -> None:
    """Inspect intelligent vehicle ranking and model metric endpoints."""
    steps = [
        workflow_step(
            "rank-top3",
            "Fetch scene-aware top-three intelligent vehicle rankings.",
            "backend-saas.appVehicleMetrics.rankTop3",
            "GET",
            "/api/backend-saas/v1/app-vehicle-metrics/rank/top3",
            params={"scene": scene, "window": window},
        )
    ]
    if vehicle_id or model:
        steps.append(
            workflow_step(
                "model-detail",
                "Fetch model-level ranking detail and evidence features.",
                "backend-saas.appVehicleMetrics.modelDetail",
                "GET",
                "/api/backend-saas/v1/app-vehicle-metrics/model/detail",
                params={
                    "vehicleId": vehicle_id,
                    "model": model,
                    "hardwareConfig": hardware_config,
                    "softwareConfig": software_config,
                    "scene": scene,
                    "window": window,
                    "debug": debug,
                },
            )
        )
    try:
        execute_workflow(
            ctx,
            command="vehicle +rankings",
            objective="AI 版汽车之家 ranking workflow for explainable recommendations.",
            steps=steps,
            dry_run=dry_run,
            timeout=timeout,
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("vehicle +rankings", exc, ctx.obj["json"])


@main.group()
def humanoid() -> None:
    """Humanoid robot database shortcuts."""


@humanoid.command("+search")
@click.option("--query", "q", default=None, help="Robot or brand keyword.")
@click.option("--brand", default=None)
@click.option("--category", default=None)
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def humanoid_search(ctx: click.Context, q: str | None, brand: str | None, category: str | None, page: int, page_size: int, dry_run: bool) -> None:
    """Search humanoid robot database records."""
    params = {"q": q, "brand": brand, "category": category, "page": page, "pageSize": page_size}
    try:
        emit_api(ctx, "humanoid +search", request_api("GET", "/api/humanoid-chain/robots/", params=params, identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("humanoid +search", exc, ctx.obj["json"])


@humanoid.command("+compare")
@click.option("--id", "robot_ids", multiple=True, required=True, help="Robot ID. Repeat for comparison.")
@click.option("--include-configs/--no-configs", default=True, show_default=True)
@click.option("--timeout", type=int, default=30, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def humanoid_compare(ctx: click.Context, robot_ids: tuple[str, ...], include_configs: bool, timeout: int, dry_run: bool) -> None:
    """Compare humanoid robot records and configuration version data."""
    steps: list[dict[str, object]] = []
    for robot_id in robot_ids:
        encoded = quote_path_value(robot_id)
        steps.append(
            workflow_step(
                f"{robot_id}:detail",
                "Fetch robot product and market metadata.",
                "humanoid.robots.detail",
                "GET",
                f"/api/humanoid-chain/robots/{encoded}",
            )
        )
        if include_configs:
            steps.append(
                workflow_step(
                    f"{robot_id}:config-versions",
                    "Fetch humanoid robot configuration version snapshots.",
                    "humanoid.robots.configVersions",
                    "GET",
                    f"/api/humanoid-chain/robots/{encoded}/config-versions",
                )
            )
    try:
        execute_workflow(
            ctx,
            command="humanoid +compare",
            objective="机器人数据库 / 人形机器人配置数据 comparison workflow.",
            steps=steps,
            dry_run=dry_run,
            timeout=timeout,
        )
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("humanoid +compare", exc, ctx.obj["json"])


@humanoid.command("+config")
@click.option("--id", "robot_id", required=True, help="Robot ID.")
@click.option("--version-id", default=None, help="Optional config version ID.")
@click.option("--dry-run", is_flag=True)
@click.pass_context
def humanoid_config(ctx: click.Context, robot_id: str, version_id: str | None, dry_run: bool) -> None:
    """Fetch humanoid robot configuration versions or one version detail."""
    encoded = quote_path_value(robot_id)
    if version_id:
        path = f"/api/humanoid-chain/robots/{encoded}/config-versions/{quote_path_value(version_id)}"
        schema_path = "humanoid.robots.configVersionsGet"
    else:
        path = f"/api/humanoid-chain/robots/{encoded}/config-versions"
        schema_path = "humanoid.robots.configVersions"
    try:
        emit_api(ctx, "humanoid +config", request_api("GET", path, identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail(schema_path, exc, ctx.obj["json"])


@main.group()
def discovery() -> None:
    """Discovery feed API shortcuts."""


@discovery.command("+feed")
@click.option("--q", default=None, help="Search/filter query.")
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--batch", type=int, default=None)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.option("--include-types", default=None, help="Comma-separated feed item types.")
@click.option("--dry-run", is_flag=True)
@click.pass_context
def discovery_feed(ctx: click.Context, q: str | None, page: int, batch: int | None, page_size: int, include_types: str | None, dry_run: bool) -> None:
    """List public discovery feed items."""
    params = {"q": q, "page": page, "batch": batch, "pageSize": page_size, "includeTypes": include_types}
    try:
        emit_api(ctx, "discovery +feed", request_api("GET", "/api/backend-app/discovery/v1/feed", params=params, auth=False, dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("discovery +feed", exc, ctx.obj["json"])


@main.group()
def share() -> None:
    """Share-token API shortcuts."""


@share.command("+create")
@click.option("--resource-type", required=True)
@click.option("--resource-id", required=True)
@click.option("--scope", "scopes", multiple=True, help="Share scope. Repeatable.")
@click.option("--rotate/--no-rotate", default=None)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def share_create(ctx: click.Context, resource_type: str, resource_id: str, scopes: tuple[str, ...], rotate: bool | None, dry_run: bool) -> None:
    """Create a share token for a resource."""
    body = {
        "resourceType": resource_type,
        "resourceId": resource_id,
        "scopes": list(scopes) or ["read"],
        "rotate": rotate,
    }
    try:
        emit_api(ctx, "share +create", request_api("POST", "/api/auth/v1/share/token", data=body, identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("share +create", exc, ctx.obj["json"])


@share.command("+resolve")
@click.option("--share-id", required=True)
@click.option("--share-token", required=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def share_resolve(ctx: click.Context, share_id: str, share_token: str, dry_run: bool) -> None:
    """Resolve an anonymous share token."""
    body = {"shareId": share_id, "shareToken": share_token}
    try:
        emit_api(ctx, "share +resolve", request_api("POST", "/api/auth/v1/share/resolve", data=body, auth=False, dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("share +resolve", exc, ctx.obj["json"])


@share.command("+revoke")
@click.option("--share-id", required=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def share_revoke(ctx: click.Context, share_id: str, dry_run: bool) -> None:
    """Revoke a share token."""
    try:
        emit_api(ctx, "share +revoke", request_api("POST", "/api/auth/v1/share/revoke", data={"shareId": share_id}, identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("share +revoke", exc, ctx.obj["json"])


@main.group()
def micontrol() -> None:
    """MiControl run orchestration shortcuts."""


@micontrol.command("runs")
@click.option("--status", default=None)
@click.option("--limit", type=int, default=20, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def micontrol_runs(ctx: click.Context, status: str | None, limit: int, dry_run: bool) -> None:
    """List MiControl runs."""
    try:
        emit_api(ctx, "micontrol runs", request_api("GET", "/api/backend-app/micontrol/v2/runs", params={"status": status, "limit": limit}, identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("micontrol runs", exc, ctx.obj["json"])


@micontrol.command("detail")
@click.option("--run-id", required=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def micontrol_detail(ctx: click.Context, run_id: str, dry_run: bool) -> None:
    """Get MiControl run detail."""
    try:
        emit_api(ctx, "micontrol detail", request_api("GET", f"/api/backend-app/micontrol/v2/runs/{quote_path_value(run_id)}", identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("micontrol detail", exc, ctx.obj["json"])


@micontrol.command("create")
@click.option("--task", required=True)
@click.option("--context", default=None, help="JSON context object.")
@click.option("--input-payload", default=None, help="JSON payload object.")
@click.option("--dry-run", is_flag=True)
@click.pass_context
def micontrol_create(ctx: click.Context, task: str, context: str | None, input_payload: str | None, dry_run: bool) -> None:
    """Create a MiControl run."""
    try:
        body = {
            "task": task,
            "context": parse_json_arg(context, stdin=sys.stdin, flag_name="--context") or {},
            "inputPayload": parse_json_arg(input_payload, stdin=sys.stdin, flag_name="--input-payload") or {},
        }
        emit_api(ctx, "micontrol create", request_api("POST", "/api/backend-app/micontrol/v2/runs", data=body, identity=request_identity(ctx), dry_run=dry_run))
    except Exception as exc:
        if isinstance(exc, SystemExit):
            raise
        fail("micontrol create", exc, ctx.obj["json"])


@main.command()
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Check repository and toolchain readiness."""
    as_json = ctx.obj["json"]
    try:
        root = repo_root(ctx)
        data = doctor_data(root)
        warnings = data.pop("warnings", [])
        emit(CommandResult(True, "doctor", data=data, warnings=warnings), as_json)
    except Exception as exc:
        fail("doctor", exc, as_json)


@main.group()
def repo() -> None:
    """Repository inspection commands."""


@repo.command("status")
@click.pass_context
def repo_status(ctx: click.Context) -> None:
    """Show package and git status."""
    as_json = ctx.obj["json"]
    try:
        root = repo_root(ctx)
        pkg = package_json(root)
        emit(
            CommandResult(
                True,
                "repo status",
                data={
                    "repo": str(root),
                    "package": {
                        "name": pkg.get("name"),
                        "version": pkg.get("version"),
                        "private": pkg.get("private"),
                    },
                    "git": git_status(root),
                },
            ),
            as_json,
        )
    except Exception as exc:
        fail("repo status", exc, as_json)


@main.group()
def routes() -> None:
    """Route inspection commands."""


@routes.command("list")
@click.option("--limit", type=int, default=0, help="Limit route count; 0 means all.")
@click.pass_context
def routes_list(ctx: click.Context, limit: int) -> None:
    """List Taro routes from src/app.config.ts."""
    as_json = ctx.obj["json"]
    try:
        root = repo_root(ctx)
        config = route_config(root)
        pages = config["pages"][:limit] if limit and limit > 0 else config["pages"]
        emit(
            CommandResult(
                True,
                "routes list",
                data={
                    "entryPagePath": config["entryPagePath"],
                    "count": config["count"],
                    "returned": len(pages),
                    "pages": pages,
                    "source": config["source"],
                },
            ),
            as_json,
        )
    except Exception as exc:
        fail("routes list", exc, as_json)


@routes.command("find")
@click.argument("query")
@click.pass_context
def routes_find(ctx: click.Context, query: str) -> None:
    """Find routes containing a substring."""
    as_json = ctx.obj["json"]
    try:
        root = repo_root(ctx)
        config = route_config(root)
        query_lower = query.lower()
        matches = [page for page in config["pages"] if query_lower in page.lower()]
        emit(CommandResult(True, "routes find", data={"query": query, "matches": matches, "count": len(matches)}), as_json)
    except Exception as exc:
        fail("routes find", exc, as_json)


@main.group()
def serve() -> None:
    """H5 dev server lifecycle commands."""


@serve.command("h5")
@click.option("--port", type=int, default=10086, show_default=True)
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--wait-seconds", type=float, default=0.0, show_default=True, help="Wait for HTTP readiness after start.")
@click.argument("extra_args", nargs=-1)
@click.pass_context
def serve_h5(ctx: click.Context, port: int, host: str, wait_seconds: float, extra_args: tuple[str, ...]) -> None:
    """Start the H5 dev server in the background."""
    as_json = ctx.obj["json"]
    try:
        data = start_h5_server(repo_root(ctx), port=port, host=host, extra_args=extra_args)
        ok = True
        errors = []
        if wait_seconds > 0:
            data["readiness"] = wait_for_http(data["url"], timeout=wait_seconds, interval=1.5)
            ok = bool(data["readiness"].get("ok"))
            if not ok:
                errors.append("H5 server did not become HTTP-ready before the wait timeout.")
        emit(CommandResult(ok, "serve h5", data=data, errors=errors), as_json)
        if not ok:
            raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as exc:
        fail("serve h5", exc, as_json)


@serve.command("status")
@click.pass_context
def serve_status_cmd(ctx: click.Context) -> None:
    """Show tracked H5 server status."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "serve status", data=serve_status(repo_root(ctx))), as_json)
    except Exception as exc:
        fail("serve status", exc, as_json)


@serve.command("stop")
@click.pass_context
def serve_stop(ctx: click.Context) -> None:
    """Stop the tracked H5 dev server."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "serve stop", data=stop_h5_server(repo_root(ctx))), as_json)
    except Exception as exc:
        fail("serve stop", exc, as_json)


@serve.command("logs")
@click.option("--lines", type=int, default=80, show_default=True)
@click.pass_context
def serve_logs(ctx: click.Context, lines: int) -> None:
    """Read recent H5 dev server logs."""
    as_json = ctx.obj["json"]
    try:
        emit(CommandResult(True, "serve logs", data=read_logs(repo_root(ctx), lines)), as_json)
    except Exception as exc:
        fail("serve logs", exc, as_json)


@main.group()
def build() -> None:
    """Build commands."""


@build.command("h5")
@click.option("--timeout", type=int, default=600, show_default=True)
@click.option("--dry-run", is_flag=True, help="Return the command without executing it.")
@click.pass_context
def build_h5(ctx: click.Context, timeout: int, dry_run: bool) -> None:
    """Run pnpm build:h5."""
    as_json = ctx.obj["json"]
    args = ["pnpm", "build:h5"]
    try:
        root = repo_root(ctx)
        data = {"args": args, "cwd": str(root), "dryRun": True} if dry_run else run_command(args, root, timeout=timeout)
        ok = True if dry_run else data.get("returncode") == 0
        emit(CommandResult(ok, "build h5", data=data, errors=[] if ok else ["Build command failed."]), as_json)
        if not ok:
            raise SystemExit(data.get("returncode", 1))
    except SystemExit:
        raise
    except Exception as exc:
        fail("build h5", exc, as_json)


@build.command("target")
@click.argument("script")
@click.option("--timeout", type=int, default=600, show_default=True)
@click.option("--dry-run", is_flag=True)
@click.pass_context
def build_target(ctx: click.Context, script: str, timeout: int, dry_run: bool) -> None:
    """Run an existing package.json build script, e.g. build:weapp."""
    as_json = ctx.obj["json"]
    try:
        root = repo_root(ctx)
        scripts = package_json(root).get("scripts", {})
        if script not in scripts:
            raise HarnessError("Script not found in package.json.", details={"script": script, "available": sorted(scripts)})
        args = ["pnpm", script]
        data = {"args": args, "cwd": str(root), "dryRun": True} if dry_run else run_command(args, root, timeout=timeout)
        ok = True if dry_run else data.get("returncode") == 0
        emit(CommandResult(ok, "build target", data=data, errors=[] if ok else ["Build command failed."]), as_json)
        if not ok:
            raise SystemExit(data.get("returncode", 1))
    except SystemExit:
        raise
    except Exception as exc:
        fail("build target", exc, as_json)


@main.group()
def page() -> None:
    """Page URL and browser evidence commands."""


@page.command("url")
@click.argument("page_path")
@click.option("--base-url", default="http://localhost:10086", show_default=True)
@click.option("--query", default=None, help="Optional query string without hash routing.")
@click.pass_context
def page_url(ctx: click.Context, page_path: str, base_url: str, query: str | None) -> None:
    """Generate a Taro H5 URL for a page path."""
    as_json = ctx.obj["json"]
    emit(CommandResult(True, "page url", data={"url": h5_url(page_path, base_url, query), "pagePath": page_path}), as_json)


@page.command("snapshot")
@click.argument("page_path")
@click.option("--base-url", default="http://localhost:10086", show_default=True)
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path), default=None)
@click.option("--wait-ms", type=int, default=1500, show_default=True)
@click.pass_context
def page_snapshot(ctx: click.Context, page_path: str, base_url: str, output: Path | None, wait_ms: int) -> None:
    """Capture a screenshot for a Taro H5 route using Python Playwright."""
    as_json = ctx.obj["json"]
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        fail(
            "page snapshot",
            HarnessError("Python Playwright is not installed.", details={"install": "python -m pip install -e 'agent-harness/[browser]' && python -m playwright install chromium"}),
            as_json,
        )
        return

    try:
        root = repo_root(ctx)
        url = h5_url(page_path, base_url)
        output_path = output or root / ".agent-harness" / "artifacts" / f"{page_path.replace('/', '_')}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page_obj = browser.new_page(viewport={"width": 390, "height": 844})
            page_obj.goto(url, wait_until="domcontentloaded", timeout=30000)
            page_obj.wait_for_timeout(wait_ms)
            page_obj.screenshot(path=str(output_path), full_page=True)
            browser.close()
        emit(CommandResult(True, "page snapshot", data={"url": url, "screenshot": str(output_path)}), as_json)
    except Exception as exc:
        fail("page snapshot", exc, as_json)


@main.group()
def flow() -> None:
    """Agent smoke-flow commands."""


@flow.command("smoke")
@click.option("--url", default="http://localhost:10086", show_default=True)
@click.option("--timeout", type=float, default=10.0, show_default=True)
@click.option("--retries", type=int, default=1, show_default=True)
@click.option("--interval", type=float, default=1.0, show_default=True)
@click.pass_context
def flow_smoke(ctx: click.Context, url: str, timeout: float, retries: int, interval: float) -> None:
    """Check that a running frontend app responds over HTTP."""
    as_json = ctx.obj["json"]
    attempts = max(1, retries)
    result = {}
    for attempt in range(1, attempts + 1):
        result = http_smoke(url, timeout=timeout)
        result["attempt"] = attempt
        result["attempts"] = attempts
        if result.get("ok") or attempt == attempts:
            break
        import time

        time.sleep(interval)
    emit(CommandResult(bool(result.get("ok")), "flow smoke", data=result, errors=[] if result.get("ok") else ["HTTP smoke check failed."]), as_json)
    if not result.get("ok"):
        raise SystemExit(1)


def build_openapi_method_command(schema_path: str, method_schema: dict) -> click.Command:
    path_param_names = [str(name) for name in method_schema.get("pathParameters") or [] if name]
    help_text = method_schema.get("summary") or method_schema.get("description") or schema_path

    def generated_method(
        ctx: click.Context,
        path_args: tuple[str, ...],
        param_args: tuple[str, ...],
        params: str | None,
        body: str | None,
        no_auth: bool,
        dry_run: bool,
        timeout: int,
        **auto_path_args: str | None,
    ) -> None:
        try:
            call_registry_method(
                ctx,
                command=schema_path,
                schema_path=schema_path,
                path_args=path_args,
                auto_path_args=auto_path_args,
                params=params,
                param_args=param_args,
                body=body,
                no_auth=no_auth,
                dry_run=dry_run,
                timeout=timeout,
            )
        except Exception as exc:
            if isinstance(exc, SystemExit):
                raise
            fail(schema_path, exc, ctx.obj["json"])

    for path_name in reversed(path_param_names):
        option = "--" + command_name(path_name)
        generated_method = click.option(option, path_name, default=None, help=f"Path parameter: {path_name}")(generated_method)
    generated_method = click.pass_context(generated_method)
    generated_method = click.option("--timeout", type=int, default=30, show_default=True)(generated_method)
    generated_method = click.option("--dry-run", is_flag=True, help="Print request envelope without calling the backend.")(generated_method)
    generated_method = click.option("--no-auth", is_flag=True, help="Do not attach the stored access token.")(generated_method)
    generated_method = click.option("--data", "body", default=None, help="JSON request body. Use '-' to read stdin.")(generated_method)
    generated_method = click.option("--params", default=None, help="JSON query params. Use '-' to read stdin.")(generated_method)
    generated_method = click.option("--param", "param_args", multiple=True, help="Query parameter as key=value. Repeatable.")(generated_method)
    generated_method = click.option("--path", "path_args", multiple=True, help="Path argument as key=value. Repeatable.")(generated_method)
    generated_method = click.command(command_name(schema_path.split(".")[-1]), help=help_text)(generated_method)
    return generated_method


def mount_openapi_command_tree() -> None:
    for service_name, service in sorted(REGISTRY.items()):
        service_command_name = command_name(service_name)
        service_group = main.commands.get(service_command_name)
        if service_group is None:
            service_group = click.Group(name=service_command_name, help=service.get("title") or service_name)
            main.add_command(service_group, service_command_name)
        if not isinstance(service_group, click.Group):
            continue

        for resource_name, resource in sorted((service.get("resources") or {}).items()):
            resource_command_name = command_name(resource_name)
            resource_group = service_group.commands.get(resource_command_name)
            if resource_group is None:
                resource_group = click.Group(name=resource_command_name, help=f"{service_name}.{resource_name}")
                service_group.add_command(resource_group, resource_command_name)
            if not isinstance(resource_group, click.Group):
                continue

            for method_name, method_schema in sorted((resource.get("methods") or {}).items()):
                method_command = build_openapi_method_command(f"{service_name}.{resource_name}.{method_name}", method_schema)
                resource_group.add_command(method_command)


mount_openapi_command_tree()


if __name__ == "__main__":
    main(sys.argv[1:])
