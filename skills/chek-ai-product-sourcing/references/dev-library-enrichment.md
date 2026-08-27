# CHEK DEV Library Enrichment

## Scope And Environment

Use this workflow only when the user explicitly asks to enrich the CHEK DEV robot, vehicle, model/method, version, cover, or capability-evaluation database.

Before any read or write:

```bash
chek --json config show
chek auth status --check
```

Require `env=dev` and `api_origin=https://api-dev.chekkk.com`. Stop if the target is production or ambiguous. Never print access tokens, cookies, Authorization headers, or used SMS codes.

## Evidence Package

For every proposed create or update, capture:

- canonical name, brand/owner, category, entry type, and aliases;
- event and date, with the change classified as main entity, hardware/config version, SDK/model/firmware version, delivery/production fact, or onsite showcase;
- exact source-backed facts and precise missing evidence;
- official product, release, paper, repository, or conference URLs;
- domestic access status and confidence;
- official cover page/image candidates;
- suggested action: `create`, `update`, `create_version`, `link_method`, `pending`, or `skip`.

Use discovery sites only to find leads. Resolve final fields and cover provenance to official pages, papers, conference organizers, regulatory sources, or reputable original reporting. Do not expose an intermediary discovery site as the factual source when primary evidence is available.

## Mandatory Duplicate Resolution

Before creating anything, query DEV by canonical name, normalized punctuation/case, brand, model code, and every known alias. Inspect the detail and version list of plausible matches.

Use this decision order:

1. Same real product and same generation: update the existing main entity.
2. Same product family but a distinct SKU, hardware generation, or experimental configuration: create or update a version/variant under the existing main entity when the schema supports it.
3. Same string but a different owner, embodiment, or method: keep separate entities and record disambiguating aliases/owner.
4. SDK, firmware, foundation model, delivery milestone, or showcase only: update the related entity/version/fact; do not create a physical robot.
5. Benchmark model/method with independent evaluation identity: use `entryType=benchmark_method`. It may appear as a robot-like leaderboard subject in the product UI, but must not be mislabeled as physical hardware.

Record the matched entity ID for every update and the negative search evidence for every create. Re-run the duplicate lookup immediately before submission.

## Main Entry And Version Completeness

For a physical robot or vehicle, separate stable identity from versioned configuration:

- Main entry: canonical name, aliases, brand, category, description, market status, official URL, cover.
- Version/config: hardware SKU, dimensions/specs, controller/compute, firmware, SDK, model version, release date, source snapshot.
- Market changes: production, delivery, preorder, or sales facts with exact scope; never assign company-wide totals to one model without evidence.
- Onsite appearance: store as an event/evidence fact unless the event is the actual first public release.

Enrich an existing record when new evidence fills previously empty parameters. Do not limit a run to creating missing entries.

## Cover Completion Gate

Every newly created main entry must finish with a verified cover. Existing entries with external-only or dead covers should be migrated when they are in scope.

1. Prefer an official product hero, official announcement image, official conference exhibit image, paper/project visual for a benchmark method, or reputable original reporting when no official usable image exists.
2. Visually confirm the exact model. Reject wrong-generation images, generic brand photos, group shots where the subject is unclear, unrelated robots, logos alone, watermarks, and synthetic replacements for a real product.
3. Upload the local image with `chek media +upload-cover`, preserving the original source URL and a readable asset title.
4. Store the returned `https://img.chekkk.com/...` URL through a governed edit. Keep the original source URL in the media metadata and edit description/evidence.
5. Approve only when the user authorized approval. Read back the entity and verify the saved cover uses the CHEK media domain.
6. Poll the media URL until it returns HTTP 200. Object storage may briefly return 404 after a successful upload; do not declare failure or success from the first request alone. If it never becomes available, re-upload and replace the edit.

## Capability Evaluation Admission

Do not put every discovered standard into the public capability leaderboard. Keep three states: candidate registry, governed definition, and formally published leaderboard.

A definition may enter the governed library when it has a public protocol, stable version, task/dataset description, metric and ranking direction, environment/embodiment scope, aggregation rule, required trials, and evidence requirements.

A definition may enter the formal capability leaderboard only when all of these gates pass:

- at least 10 distinct comparable subjects from at least 5 independent organizations under the same protocol partition;
- every ranked result identifies the exact method/robot configuration, protocol version, environment, metric, and source;
- trial count or the protocol's required sample basis is present; do not infer counts from percentages;
- one common primary metric with an explicit ascending/descending direction; no cross-project total score;
- reproducible official, paper, or independently verifiable evidence, with fixtures and illustrative demos excluded;
- no mixture of simulation and real-world results, seen and unseen settings, or materially different hardware scopes in one rank partition.

Definitions below this threshold remain visible only in the evaluation library or candidate queue. Paper-specific real-robot protocols may be stored and shown on entity details as evidence without becoming a public cross-subject leaderboard.

## Governed Write And Readback

Prefer edit submissions over direct writes. Use CLI schema/route discovery and `--dry-run` before unfamiliar mutations. For each batch:

1. submit the smallest entity/version/fact/cover diff;
2. record submission IDs and status;
3. approve only with explicit authority and after reading before/after snapshots;
4. read back entity detail and versions;
5. verify source URLs, cover HTTP status, entry type, identity, and changed fields;
6. re-run duplicate search and report zero unintended duplicates.

Final reporting must distinguish created main entries, created versions, enriched existing entries, pending evidence, skipped duplicates, covers completed, approvals performed, and failed readbacks.
