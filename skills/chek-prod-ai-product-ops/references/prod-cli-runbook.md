# Prod CLI Runbook

## Prod Preflight

Use a prod profile only:

```bash
chek config set-env prod
chek config default-as user
chek config show
chek auth status --check
```

Stop if any output points to DEV, staging, `api-dev.chekkk.com`, or a DEV-only CLI home. Do not reuse DEV login homes such as `/tmp/chek-cli-dev-login-sidechat`.

Recommended prod isolation when the user wants a temporary session:

```bash
export CHEK_CLI_HOME=/tmp/chek-cli-prod-ops
chek config set-env prod
chek config default-as user
chek auth login --method sms --phone "<phone>" --code "<code>" --profile prod-ops
```

Never print tokens or full Authorization headers.

## Formal AI Product Publish

Research first:

```bash
chek ai-product +research-plan \
  --category 具身机器人 \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b"
```

Duplicate check:

```bash
chek ai-product +duplicate-check \
  --category 具身机器人 \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b"
```

If duplicate is true, enter the matched room and post review/evidence there. Do not publish a second room for the same product/hardware/software tuple.

Formal publish:

```bash
chek ai-product +publish \
  --category 具身机器人 \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b" \
  --tag 宇树 \
  --tag UnitreeH1 \
  --reason "H1 是成熟度和可见度都很高的人形平台，适合检验厂商 SDK 对真实开发者是否友好。" \
  --scenario "SDK 文档是否清楚；控制接口是否稳定易用；社区资料能否补足官方文档" \
  --source-url "https://www.unitree.com/operate/h1/" \
  --source-url "https://github.com/unitreerobotics/unitree_sdk2" \
  --cover-image-url "<CHEK_MEDIA_URL>" \
  --cover-source-url "https://www.unitree.com/operate/h1/" \
  --linked-entity "targetType=humanoid_robot,targetId=<robot_id>,title=H1,tagTitle=H1,subtitle=宇树" \
  --formal
```

Use `--dry-run` before live mutation when the user did not already explicitly say to submit/publish.

## Cover Search And Upload

Search the web for the cover before upload. Prefer:

- official product page or manufacturer media;
- official announcement/news image;
- app store image for software products;
- GitHub/social preview image for open-source products when official product imagery is unavailable;
- reputable media only when official imagery is unsuitable.

Upload to CHEK prod media. If the generated `backend-app media images` command cannot handle multipart upload, use the prod media endpoint with a redacted-token curl command or the repository's existing media helper. Preserve:

- original cover source URL;
- local downloaded file path until upload verification;
- CHEK media URL returned by prod.

Do not use DEV media URLs for prod room covers.

## Robot And Vehicle Version Sync

Robot config-version edit:

```bash
chek ai-product +robot-version-edit \
  --robot-id <robot_id> \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b" \
  --source-repo "https://github.com/unitreerobotics/unitree_sdk2" \
  --source-commit 7740f8b \
  --post-id <room_uuid> \
  --checked-at "$(date +%F)"
```

Vehicle hardware/software edit:

```bash
chek ai-product +vehicle-version-edit \
  --vehicle-id <vehicle_id> \
  --product-name "问界 M9" \
  --hardware-model "Max 智驾版" \
  --software-version "ADS 3.3.0"
```

If the main robot or vehicle entity is missing, do not publish an unbound room. Record a missing-main-entry task with source evidence and ask for the governed creation path.

## Reviews And Evidence Posts

Submit rating:

```bash
chek ai-product +review \
  --post-id <room_uuid> \
  --stars 4.5 \
  --comment "版本确认后体验稳定" \
  --evidence "附测试记录、截图或视频说明" \
  --evidence-url "https://example.com/evidence"
```

For high-quality evidence content that should appear in a room, post a concise message with:

- what was tested;
- exact version;
- method or scenario;
- result;
- evidence URL.

Avoid publishing a raw list of search results.

## Approval Guardrails

For prod approvals:

1. Read edit detail first.
2. Confirm the before/after snapshot and source URLs match the intended entity/version.
3. Approve only when the user explicitly requested approval or the workflow instruction clearly includes approval.
4. Use an empty JSON body when the endpoint requires a body:

```bash
chek humanoid edits detail --submission-id <id>
chek humanoid edits approve --submission-id <id> --data '{}'

chek vehicle vehicles edits-get --edit-id <id>
chek vehicle vehicles edits-approve --edit-id <id> --data '{}'
```

Report approved, pending, rejected, or blocked status explicitly.

## Validation

After publishing or editing a room:

```bash
chek backend-app buddy posts-get --post-id <room_uuid>
```

Check:

- `targetType` is `ai_product`;
- `postType` is `ai_product_review`;
- title is clean;
- product tuple is correct;
- `linkedEntities` exists for vehicles/robots;
- `coverImageUrl` is a CHEK prod media URL;
- `ai_product_review.coverSourceUrl` exists;
- `extras.readerBrief` exists and is readable;
- `reviewStats.threshold` is present when scoring is enabled.

After robot/vehicle version edits, read edit detail and record status.
