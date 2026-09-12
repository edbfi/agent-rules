# Validation and manual delivery

The `ci` workflow runs on PRs, default-branch pushes and explicit repair or checked-merge dispatch.
Expected jobs: `guard`, `content`, `ci / required`. Versioned edbfi shared guards
check dispatch identity and reject missing/skipped/failed prerequisites.

Content checks validate canonical Markdown shape, the edbfi-only opt-in manifest,
unique safe identifiers, and accepted previous hashes. Python compilation and
isolated planner/writer tests cover actual diff generation, no-op behavior,
conflicts, explicit rename removal, preservation of custom files, unsafe paths,
source/base drift, failed final CI, altered plans, and branch/PR idempotence.
No real consumer is touched by these tests. Workflow syntax is checked locally
with actionlint before PR review. Rule prose and dependency accuracy require
review before delivery; content CI does not execute the example toolchains.
Existing canonical bytes are preserved in this activation.

`preview rules` and `sync rules` are manual workflows on the canonical default
branch only. Both pin the checkout and verify successful exact-source final CI from a push
or explicit dispatch; a newer pending or failed final run blocks delivery.
Preview uploads the exact plan, unified diff and SHA256 receipt. Publishing verifies
preview provenance, the maintainer-supplied hash, target identity, current source
and consumer base; it regenerates and compares the entire plan before creating
GitHub blobs/tree/signed-off commit/new branch and proposing a PR. It never changes
an existing ref. Branch collisions remain intact. API objects created before a
later guard fails may remain unreachable; no default branch is changed.

The source job token is read-only. RULES_SYNC_TOKEN is confined to the writer
step and required for real PRs to trigger ordinary consumer CI. The writer stays
disabled until the newly generated token and a real reviewed pilot are ready.
Schedules and automatic fan-out are not enabled. Initial unchanged consumers must
report no-op; never manufacture changes solely to test permissions.

Renovate updates, including major rule-file pins and shared-policy versions,
merge unattended after all three required jobs pass on the current revision.
The checked action verifies genuine author sign-offs and dispatches exact-commit
final CI. No dashboard approval, branch protections or rulesets are configured;
native GitHub automerge stays disabled. Other changes and rule delivery retain
full manual review and the maintainer's ghmerge process. Preserve prek.
