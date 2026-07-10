# Vehicle Database Maintenance

## Maintenance Goal

Keep the CHEK vehicle database useful for intelligent-vehicle reviews, rankings, and version-specific AI product rooms. The database should answer:

- what vehicle, trim, and model year exists;
- which hardware configuration and software/OTA version was tested;
- what source supports price, delivery, intelligent-driving capability, sensor, battery, and release claims;
- which review rooms and user evidence support a version;
- what changed since the last review or ranking snapshot.

## Main Data Areas

Prefer governed edit submissions and high-level CHEK CLI shortcuts. Use direct generated API commands only after checking schemas and running `--dry-run` where supported.

Vehicle search and readback:

```bash
chek vehicle +search --query "问界 M9" --top-k 10 --dry-run
chek vehicle detail --id <vehicle_id> --dry-run
chek vehicle raw-params --id <vehicle_id> --dry-run
chek vehicle +compare --id <vehicle_1> --id <vehicle_2> --include-raw --include-software --dry-run
chek vehicle +rankings --scene urban --window latest --dry-run
```

Schema discovery before lower-level writes:

```bash
chek schema vehicle.vehicles.batchSearch
chek routes find vehicle vehicles software
chek routes find vehicle vehicles raw-params
chek routes find vehicle vehicles repo-docs
```

Version edit for AI product review linkage:

```bash
chek ai-product +vehicle-version-edit \
  --vehicle-id <vehicle_id> \
  --product-name "问界 M9" \
  --hardware-model "Max 智驾版" \
  --software-version "ADS 3.3.0" \
  --post-id <room_uuid>
```

## Field Extraction From User Materials

When the user gives spec sheets, screenshots, brochures, release notes, app screenshots, OTA pages, test reports, or recordings/transcripts, extract:

- canonical vehicle name, brand, series, trim, model year, and aliases;
- hardware version: trim, ADAS package, sensor suite, chip/domain controller, battery/motor where relevant;
- software version: OTA name, intelligent-driving system version, app version, cockpit OS version, map/data version when stated;
- release or availability event: launch, preorder, delivery, OTA rollout, public beta, or regional availability;
- capability facts: city NOA, highway NOA, parking, AEB, end-to-end model, world model, voice/cockpit AI, assisted-driving limits;
- evidence: source title, source URL or file path, page/timestamp, capture date, and confidence.

Do not merge brand-level marketing claims into a trim/version fact unless the source explicitly links them to that trim/version.

## Version Maintenance

Create or update a version record when a room or ranking refers to a new real hardware/software pair:

- Treat `产品名 + 硬件型号 + 软件版本` as the review identity.
- Do not overwrite an older hardware/software pair when an OTA, trim, or model-year update materially changes capabilities.
- Link the version edit to the CHEK AI product review room when available.
- Read back vehicle detail, software options, and raw parameters after the edit is approved or applied.

If the main vehicle entity is missing, do not publish an unbound formal AI product room. Create a missing-main-entry task with source evidence and ask for the governed creation path.

## Evidence Standards

Use official and high-confidence sources first:

- manufacturer product pages, press releases, OTA/release notes, manuals, app store notes, and official spec sheets;
- MIIT filings, regulatory announcements, insurance/new-car catalog references where relevant;
- app screenshots or in-car screenshots supplied by the user, with private data redacted;
- reputable media reviews and owner/test logs as supporting evidence, not the only authority for official fields.

For user-submitted files, keep a trace from each extracted field back to the file, page, screenshot, timestamp, or transcript segment.

## Maintenance Cadence

Weekly:

- scan new vehicle releases, OTA updates, trim changes, delivery announcements, and ranking-relevant capability changes;
- dedupe by vehicle + trim/hardware + software version;
- prepare version edits for active review rooms;
- update obvious source freshness and missing evidence notes.

Monthly:

- review delivery/sales facts and ranking evidence for the prior month;
- mark stale facts or low-confidence estimates;
- reconcile ranking anomalies where public claims and database facts diverge.

Quarterly:

- audit top vehicles by urban/highway NOA, heat, and community review activity;
- reconcile aliases, trims, tags, linked entities, and duplicate vehicle records;
- review old pending/rejected edits for rework.

## Quality Gates

Before submitting an edit:

- Confirm the canonical vehicle entry exists and matches the brand/model/trim.
- Confirm the field belongs to the specific trim/hardware/software version, not only the brand.
- Confirm the source is current and reachable.
- Preserve uncertainty with confidence notes instead of guessing.
- Redact personal data, license plates, VINs, phone numbers, exact home/work locations, and private account information from user materials.

Before approving an edit:

- Read edit detail and compare before/after.
- Confirm no DEV room/media/source URL is referenced.
- Confirm the source supports every changed field.
- Confirm the change improves version-specific review or ranking traceability.

## Reporting Format

When vehicle maintenance work is done, report:

- vehicle ids touched;
- edit submission ids and statuses;
- fields inserted/updated by type;
- review rooms linked;
- ranking support impact: intelligent-driving, sales/delivery, heat, or evidence freshness;
- unresolved missing sources, missing main entries, or pending approvals.
