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

Before approving an edit:

- Read detail and compare before/after snapshot.
- Confirm no product/version identity mismatch.
- Confirm no DEV room/media/source URL is referenced.
- Confirm the submitted evidence is production-safe and user-readable.

## Reporting Format

When maintenance work is done, report:

- robot ids touched;
- edit submission ids and statuses;
- facts inserted/updated by type;
- review rooms linked;
- leaderboard support impact: sales, heat, open-source;
- unresolved missing sources, missing main entries, or pending approvals.
