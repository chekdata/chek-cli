# Robot Database Maintenance

## Maintenance Goal

Keep the CHEK robot database useful for long-term AI product reviews and leaderboards. The database should answer:

- what robot exists;
- which hardware/software/config version was tested;
- what evidence supports sales, price, open-source, and capability claims;
- which review rooms and community activity support heat/open-source signals;
- what changed since the last review.

## Main Data Areas

Use governed edit submissions whenever possible.

Robot detail and versions:

```bash
chek humanoid robots list --param q=Unitree
chek humanoid robots detail --id <robot_id>
chek humanoid robots config-versions --id <robot_id>
chek humanoid robots config-versions-get --id <robot_id> --version-id <version_id>
```

Robot edit submission:

```bash
chek humanoid robots edits-post --id <robot_id> --data '<SubmitEditRequest JSON>'
```

Known useful robot edit ops:

- `put_robot_fields`
- `put_robot_profile`
- `put_config_version_fields`
- `put_robot_version_spec_fields`
- `create_config_version`
- `upsert_sales_fact_monthly`
- `upsert_price_fact_monthly`
- `upsert_open_source_resource`

## Version Maintenance

Create a config version when a review room targets a new real hardware/software tuple:

```json
{
  "type": "create_config_version",
  "body": {
    "versionName": "Unitree H1 / unitree_sdk2 main@7740f8b",
    "versionType": "community_review",
    "releaseDateText": "2026-07-09",
    "isLatest": false,
    "baseInfo": "CHEK AI 产品评审版本：Unitree H1，unitree_sdk2 main@7740f8b。",
    "configSummary": "硬件型号 H1；软件/系统版本 unitree_sdk2 main@7740f8b。用于社区评审、复评和榜单追溯。",
    "rawSnapshot": {
      "source": "CHEK CLI AI product review submission",
      "sourceRepo": "https://github.com/unitreerobotics/unitree_sdk2",
      "sourceCommit": "7740f8b",
      "buddyPostId": "<room_uuid>",
      "checkedAt": "2026-07-09"
    }
  }
}
```

Do not overwrite an old version when the product has materially changed. Add a new version or a dated re-review package.

## Duplicate And Entity-Type Gate

Search canonical name, owner/brand, normalized model code, and aliases before a create and again immediately before approval. Read plausible matches and their version lists.

- Update the existing main entity for the same real product and generation.
- Use a config version/variant for a distinct SKU, generation, SDK, firmware, or experimental hardware scope when the schema supports it.
- Keep same-name products from different owners separate.
- Store an independently evaluated model/method as `benchmark_method`, not as physical hardware. It may be presented as a leaderboard subject but must retain its method identity.
- Do not create a new physical robot for a delivery milestone, showcase, SDK, foundation-model release, or component unless it is independently modeled by the schema.

## Cover Completion Gate

A new main entry is not complete without a verified cover or an explicit blocked reason.

- Prefer official product heroes, official release images, official conference exhibit images, or reputable original reporting. For `benchmark_method`, use the paper/project visual rather than an unrelated robot photo.
- Visually verify the exact model and generation. Reject ambiguous group shots, wrong variants, logo-only placeholders, watermarks, and generated substitutes for real products.
- Upload through CHEK media, preserve the original source URL, and store the returned CHEK media URL through governed edits.
- Read back the robot and poll the media URL until it returns HTTP 200. A successful upload response alone is not completion because object storage may propagate asynchronously.

## Capability Leaderboard Admission

Do not expose every stored evaluation definition as a formal capability leaderboard. Maintain candidate, governed-definition, and formal-published states.

Formal publication requires all of the following:

- at least 10 distinct comparable subjects from at least 5 independent organizations in the same protocol partition;
- a public stable protocol/version, task or dataset definition, environment and embodiment scope, aggregation rule, required trials, and evidence requirements;
- exact subject/config identity, metric, unit, ranking direction, source, and trial/sample basis for every ranked result;
- a common primary metric and no cross-benchmark aggregate score;
- independently checkable official or paper evidence; fixtures and illustrative demos are excluded;
- separate partitions for simulation versus real world, seen versus unseen, and materially different hardware scopes.

Sub-threshold or paper-specific real-robot evaluations may remain in the evaluation library and appear as evidence on an entity detail page, but must not be promoted as a public cross-subject rank. Never infer trial counts from percentages.

## Sales Facts

Sales leaderboard support should come from `salesFacts` and `leaderboardMetrics.sales`, not from vague popularity claims.

For each sales fact, capture:

- robot id;
- month or date range;
- units;
- geography or channel if known;
- fact type: monthly delivery, cumulative delivery, preorder, shipment, official claim, channel estimate;
- confidence: high/medium/low;
- source title and URL;
- note explaining limitations.

Use official sales/delivery announcements first. Use media/channel estimates only with lower confidence and clear notes. Do not convert "hot discussion" into sales units.

## Open-Source Resources

Open-source leaderboard support should come from structured resources, not just room text.

For each resource, capture:

- resource type: repo, dataset, model, doc, tutorial, CAD, paper, benchmark;
- platform: GitHub, official docs, paper site, Zhihu, media, etc.;
- URL and title;
- repo name, stars, forks, last updated date when available;
- version linkage;
- confidence;
- note explaining why it supports the robot entry.

Zhihu Developer search is useful for discovering Chinese discussion and evaluation material, but final open-source facts should prefer GitHub, official docs, paper pages, or project sites.

## Heat Ranking Inputs

Heat is driven by 30-day CHEK community behavior: favorites, review rooms, participation, messages, discovery actions, and similar activity. Do not fabricate heat metrics through database writes.

To improve heat quality:

- publish real version-specific review rooms;
- route duplicates into existing rooms;
- post concise evidence messages;
- invite users with actual usage or borrow/test access to rate;
- keep room tags and linked entities correct.

## Maintenance Cadence

Weekly:

- scan new robot product releases, SDK updates, firmware updates, GitHub activity, and review rooms;
- dedupe by product + hardware + software version;
- submit missing config versions for active review rooms;
- update obvious open-source resources and source freshness.

Monthly:

- review sales and delivery facts for the prior month;
- mark stale facts and confidence;
- check leaderboard anomalies where ranking changed but supporting facts are weak;
- prepare re-review candidates for major firmware/SDK/model updates.

Quarterly:

- audit top robots by sales, heat, and open-source rank;
- reconcile robot names, aliases, tags, linked entities, and duplicate main entries;
- review old pending edits and rejected edits for rework.

## Quality Gates

Before submitting an edit:

- Confirm the robot main entry exists and is the right canonical entity.
- Confirm the source is current and reachable.
- Confirm the fact belongs to the robot and version, not just the brand.
- Use source-backed uncertainty instead of overclaiming.
- Keep notes concise and audit-friendly.
- Confirm a new entry has a verified cover plan and no unresolved duplicate match.

Before approving an edit:

- Read detail and compare before/after snapshot.
- Confirm no product/version identity mismatch.
- Confirm no DEV room/media/source URL is referenced.
- Confirm the submitted evidence is production-safe and user-readable.
- Confirm the saved cover uses a production CHEK media URL, the original source is retained, and the asset returns HTTP 200.

## Reporting Format

When maintenance work is done, report:

- robot ids touched;
- edit submission ids and statuses;
- facts inserted/updated by type;
- review rooms linked;
- leaderboard support impact: sales, heat, open-source;
- unresolved missing sources, missing main entries, or pending approvals.
