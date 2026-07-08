# Zhihu Developer Search Reference

Use this reference when a sourcing run can benefit from Zhihu on-site evidence for Chinese user discussions, expert posts, experience reports, and missed candidates.

## Manual Verification

The public documentation at `https://developer.zhihu.com/docs?key=zhihu_search` exposes the Zhihu search API.

Observed behavior:

- Unauthenticated calls return JSON with `Code: 20001`, `Message: Authorization failed`, and HTTP status `200`.
- Treat `Code != 0` as failure even when HTTP status is `200`.
- The in-browser profile route may redirect to Zhihu login when no developer login session exists.

## Authentication

Use a user-provided or environment-provided Access Secret. Never hard-code or print it.

Preferred environment variable:

```bash
ZHIHU_DEVELOPER_ACCESS_SECRET
```

Optional fallback when a user's environment already uses it:

```bash
ZHIHU_ACCESS_SECRET
```

Required headers:

```text
Authorization: Bearer <your_access_secret>
X-Request-Timestamp: <seconds-level Unix timestamp>
Content-Type: application/json
```

## Zhihu Search API

Endpoint:

```text
GET https://developer.zhihu.com/api/v1/content/zhihu_search
```

Query parameters:

- `Query` string, required.
- `Count` integer, optional, default `10`, maximum `10`.

Response fields to preserve in evidence notes:

- `Title`
- `ContentType`
- `ContentID`
- `ContentText`
- `Url`
- `CommentCount`
- `VoteUpCount`
- `AuthorName`
- `AuthorBadgeText`
- `EditTime`
- `AuthorityLevel`
- `RankingScore`

Minimal curl pattern:

```bash
ACCESS_SECRET="${ZHIHU_DEVELOPER_ACCESS_SECRET:-${ZHIHU_ACCESS_SECRET:-}}"
curl -sS -G 'https://developer.zhihu.com/api/v1/content/zhihu_search' \
  --data-urlencode 'Query=上汽大众 ID. ERA 9X 体验 评测' \
  -d 'Count=5' \
  -H "Authorization: Bearer ${ACCESS_SECRET}" \
  -H "X-Request-Timestamp: $(date +%s)" \
  -H 'Content-Type: application/json'
```

If `ACCESS_SECRET` is empty, skip the API call and use public web search or ask the user for a configured credential.

## Query Strategy

Use Zhihu search to enrich the evidence pool, not to replace official verification.

General query modifiers:

- `体验`
- `评测`
- `实测`
- `问题`
- `值得买吗`
- `对比`
- `发布`
- `版本`
- `更新`

Category examples:

- 智能汽车: `<产品名> <硬件型号> 智驾 城市NOA OTA 版本 体验`, plus supplier names such as `Momenta`, `文远知行`, `地平线`, `乾崑`, `ADS`, `世界模型`.
- 具身机器人: `<产品名> <型号> 实测 开箱 固件 SDK 稳定性 任务`, plus `家庭服务机器人`, `人形机器人`, `陪伴机器人`.
- 生产力工具: `<产品名> AI 版本 网页版 App 评测 对比`, plus task terms such as `搜索`, `办公`, `代码`, `文档`, `浏览器`.
- AI 健康应用: `<产品名> AI 健康 隐私 免责声明 医生 问诊 症状自查 报告解读`.
- 其他消费级 AI 产品: `<产品名> AI 眼镜 录音卡 硬件 固件 App 隐私 体验`.

## Evidence Use

For each useful Zhihu result:

- Record the result URL in `证据来源`.
- Summarize the evidence conclusion in one sentence, including uncertainty.
- Prefer high-authority or high-engagement results, but do not overfit to votes alone.
- Convert `EditTime` timestamps to a human date when using them to justify a release/update window.
- Verify final product facts through official pages, app stores, manufacturer announcements, stores, or reputable media before setting `建议提报`.

Use Zhihu results especially for:

- discovering missed candidates and aliases;
- checking whether a domestic audience can access, test, buy, borrow, or discuss the product;
- collecting user pain points and review angles;
- finding version-specific field clues that official pages omit.
