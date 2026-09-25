# Validation and manual delivery

The `ci` workflow runs on PRs, default-branch pushes and manual dispatch.
Expected jobs: `content`, `ci / required`. The versioned edbfi shared gate
rejects missing/skipped/failed prerequisites.

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

Shared actions, workflows and presets use immutable `v4.0.0` references.
Renovate is the sole ongoing dependency merge owner. Through the shared
`automerge.json` preset it arms GitHub auto-merge with the rebase strategy, and
GitHub merges only after every required CI and policy check passes on the
current head. Shared Renovate policy updates remain manual;
release-age rules, holds and repository-specific updater ownership still apply.
The legacy Actions merger and its comment commands are retired.

The separate PR policy workflow verifies Conventional Commit titles, genuine
matching author sign-offs, Renovate provenance, holds, outstanding review requests
and unresolved changes requests. After a pass, policy re-runs the other event's
older failed verdict for the same head (`actions: write`), so a withdrawn
objection clears without a manual re-run. Require its actual emitted policy context alongside
all existing application/content checks, pinned to GitHub Actions, with strict
up-to-date branch protection. Preserve stronger review requirements. Explicit CI
dispatches do not substitute for a missing metadata policy result. Review exact
head/base, full diffs and all required results before a bootstrap merge, then
verify resulting default-branch CI. Repository-specific updater ownership and
manual publication or delivery controls remain unchanged.
