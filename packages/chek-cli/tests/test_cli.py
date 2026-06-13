from click.testing import CliRunner
import pytest

from cli_anything.frontend_app.frontend_cli import main
from cli_anything.frontend_app.registry import REGISTRY_META


@pytest.fixture(autouse=True)
def isolated_cli_home(tmp_path, monkeypatch):
    monkeypatch.setenv("CHEK_CLI_HOME", str(tmp_path / "chek-cli-home"))


def write_fake_frontend_repo(root):
    (root / "src").mkdir()
    (root / "package.json").write_text('{"scripts":{"build:h5":"taro build --type h5"}}', encoding="utf-8")
    (root / "src" / "app.config.ts").write_text(
        """
export default defineAppConfig({
  entryPagePath: 'pages/discovery/index',
  pages: [
    'pages/discovery/index',
    'pages/vehicles/index/index',
  ],
})
""",
        encoding="utf-8",
    )


def test_routes_list_json(tmp_path):
    write_fake_frontend_repo(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "--repo", str(tmp_path), "routes", "list", "--limit", "2"])
    assert result.exit_code == 0
    assert '"ok": true' in result.output
    assert '"routes list"' in result.output


def test_build_h5_dry_run_json(tmp_path):
    write_fake_frontend_repo(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "--repo", str(tmp_path), "build", "h5", "--dry-run"])
    assert result.exit_code == 0
    assert '"dryRun": true' in result.output


def test_schema_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "schema", "vehicle.vehicles.batchSearch"])
    assert result.exit_code == 0
    assert '"command": "schema"' in result.output
    assert "/api/vms/api/vehicles:batchSearch" in result.output


def test_openapi_registry_coverage():
    assert REGISTRY_META["serviceCount"] == 6
    assert REGISTRY_META["operationCount"] >= 490
    assert REGISTRY_META["failedSources"] == []
    assert set(REGISTRY_META["sources"]) == {"auth", "backend-app", "backend-saas", "crowd", "humanoid", "vehicle"}


def test_raw_api_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "api", "GET", "/api/backend-app/login/checkToken", "--dry-run"])
    assert result.exit_code == 0
    assert '"dryRun": true' in result.output
    assert "https://api-dev.chekkk.com/api/backend-app/login/checkToken" in result.output


def test_vehicle_search_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "vehicle", "+search", "--query", "小米 SU7", "--dry-run"])
    assert result.exit_code == 0
    assert '"command": "vehicle +search"' in result.output
    assert "/api/vms/api/vehicles:batchSearch" in result.output


def test_vehicle_buying_plan_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--json", "vehicle", "+buying-plan", "--query", "小米 SU7", "--scene", "urban", "--city", "上海", "--dry-run"],
    )
    assert result.exit_code == 0
    assert '"command": "vehicle +buying-plan"' in result.output
    assert "/api/vms/api/vehicles:batchSearch" in result.output
    assert "/api/backend-saas/v1/app-vehicle-metrics/rank/top3" in result.output
    assert '"agentReport"' in result.output


def test_ai_product_research_plan_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--json",
            "ai-product",
            "+research-plan",
            "--category",
            "生产力工具",
            "--product-name",
            "Kimi",
            "--software-version",
            "2026 年 7 月网页版",
            "--tag",
            "长文本",
        ],
    )
    assert result.exit_code == 0
    assert '"command": "ai-product +research-plan"' in result.output
    assert "Kimi 2026 年 7 月网页版 评测 体验" in result.output
    assert '"duplicateCheck"' in result.output


def test_ai_product_research_plan_accepts_top_level_json_file(tmp_path):
    draft = tmp_path / "product.json"
    draft.write_text(
        '{"category":"生产力工具","product_name":"豆包","software_version":"网页版 2026-07","tags":["多模态"]}',
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "ai-product", "+research-plan", "--from-file", str(draft)])
    assert result.exit_code == 0
    assert '"product_name": "豆包"' in result.output
    assert "豆包 网页版 2026-07 评测 体验" in result.output


def test_ai_product_duplicate_check_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--json",
            "ai-product",
            "+duplicate-check",
            "--category",
            "具身机器人",
            "--product-name",
            "Unitree G1",
            "--hardware-model",
            "EDU",
            "--software-version",
            "v1.2.4",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert '"dryRun": true' in result.output
    assert "/api/backend-app/buddy/v1/posts/duplicate-check" in result.output
    assert '"software_version": "v1.2.4"' in result.output


def test_ai_product_publish_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--json",
            "ai-product",
            "+publish",
            "--category",
            "AI 健康",
            "--product-name",
            "某 AI 健康 App",
            "--software-version",
            "iOS v3.6.1",
            "--reason",
            "值得复评康养问诊体验",
            "--source-url",
            "https://example.com/review",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert '"command": "ai-product +publish"' in result.output
    assert "/api/backend-app/buddy/v1/posts/duplicate-check" in result.output
    assert "/api/backend-app/buddy/v1/posts" in result.output
    assert '"post_type": "ai_product_review"' in result.output
    assert '"hardware_model": ""' in result.output


def test_ai_product_review_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--json",
            "ai-product",
            "+review",
            "--post-id",
            "00000000-0000-0000-0000-000000000001",
            "--stars",
            "4.5",
            "--comment",
            "版本确认后体验稳定",
            "--evidence-url",
            "https://example.com/evidence",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert '"command": "ai-product +review"' in result.output
    assert "/api/backend-app/buddy/v1/posts/00000000-0000-0000-0000-000000000001/reviews" in result.output
    assert '"rating": 9.0' in result.output


def test_humanoid_compare_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "humanoid", "+compare", "--id", "robot_1", "--id", "robot_2", "--dry-run"])
    assert result.exit_code == 0
    assert '"command": "humanoid +compare"' in result.output
    assert "/api/humanoid-chain/robots/robot_1/config-versions" in result.output


def test_registry_call_dry_run_with_path_arg():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "call", "vehicle.vehicles.detail", "--path", "id=veh_123", "--dry-run"])
    assert result.exit_code == 0
    assert '"command": "call"' in result.output
    assert "/api/vms/api/vehicles/veh_123" in result.output


def test_dynamic_openapi_command_tree_vehicle():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--json", "vehicle", "vehicles", "batch-search", "--data", '{"queries":[{"query":"小米 SU7"}]}', "--dry-run"],
    )
    assert result.exit_code == 0
    assert '"command": "vehicle.vehicles.batchSearch"' in result.output
    assert "/api/vms/api/vehicles:batchSearch" in result.output


def test_dynamic_openapi_command_tree_path_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "humanoid", "robots", "config-versions", "--id", "robot_123", "--dry-run"])
    assert result.exit_code == 0
    assert "/api/humanoid-chain/robots/robot_123/config-versions" in result.output


def test_auth_profile_roundtrip_uses_isolated_home(tmp_path):
    runner = CliRunner()
    env = {"CHEK_CLI_HOME": str(tmp_path)}
    token = "Bearer secret-token-123456"
    result = runner.invoke(main, ["--json", "auth", "set-token", "--token", token, "--profile", "dev-agent"], env=env)
    assert result.exit_code == 0
    assert "secret-token-123456" not in result.output
    assert '"savedProfile"' in result.output

    result = runner.invoke(main, ["--json", "auth", "profile", "list"], env=env)
    assert result.exit_code == 0
    assert '"name": "dev-agent"' in result.output

    result = runner.invoke(main, ["--json", "config", "set-env", "prod"], env=env)
    assert result.exit_code == 0

    result = runner.invoke(main, ["--json", "auth", "profile", "use", "dev-agent"], env=env)
    assert result.exit_code == 0
    assert '"active": "dev-agent"' in result.output
    assert "https://api-dev.chekkk.com" in result.output


def test_lark_style_identity_and_credentials(tmp_path):
    runner = CliRunner()
    env = {"CHEK_CLI_HOME": str(tmp_path)}
    token = "Bearer service-token-123456"

    result = runner.invoke(main, ["--json", "config", "default-as", "service"], env=env)
    assert result.exit_code == 0
    assert '"default_as": "service"' in result.output

    result = runner.invoke(
        main,
        [
            "--json",
            "auth",
            "credential",
            "set",
            "--profile",
            "dev-agent",
            "--identity",
            "service",
            "--scope",
            "vehicle:read",
            "--token",
            token,
            "--activate",
        ],
        env=env,
    )
    assert result.exit_code == 0
    assert "service-token-123456" not in result.output
    assert '"resolvedIdentity": "service"' in result.output

    result = runner.invoke(main, ["--json", "--as", "service", "auth", "check", "--scope", "vehicle:read"], env=env)
    assert result.exit_code == 0
    assert '"ok": true' in result.output

    result = runner.invoke(main, ["--json", "--as", "service", "api", "GET", "/api/vms/healthz", "--dry-run"], env=env)
    assert result.exit_code == 0
    assert '"identity": "service"' in result.output


def test_examples_and_smoke_dry_run_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "examples", "show", "vehicle.buying-plan"])
    assert result.exit_code == 0
    assert "买车 OpenClaw" in result.output
    assert "vehicle.vehicles.batchSearch" in result.output

    result = runner.invoke(main, ["--json", "examples", "generate", "--service", "vehicle", "--resource", "vehicles", "--limit", "1"])
    assert result.exit_code == 0
    assert '"returned": 1' in result.output
    assert '"requestBodyExample"' in result.output

    result = runner.invoke(main, ["--json", "smoke", "api", "--dry-run"])
    assert result.exit_code == 0
    assert '"command": "smoke api"' in result.output
    assert "/api/vms/healthz" in result.output

    result = runner.invoke(main, ["--json", "smoke", "auth", "--dry-run"])
    assert result.exit_code == 0
    assert '"command": "smoke auth"' in result.output


def test_manifest_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--json", "manifest", "--include-operations", "--operation-limit", "3"])
    assert result.exit_code == 0
    assert '"identityModel"' in result.output
    assert '"operations"' in result.output
