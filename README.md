# agent-rules

Twelve canonical, flat Markdown rule files for explicitly opted-in edbfi projects.
Source files are the artifact; no application build or local hydration is needed.

## Delivery

Delivery runs only through manually dispatched GitHub workflows. It reads the
public manifest and isolated GitHub repository trees. It never discovers local
checkouts, reads local manifests, edits hooks/excludes or touches developer files.

1. Review and merge canonical changes, then wait for the exact final `ci` run.
2. Dispatch **preview rules** on the default branch with its full commit SHA and
   one opted-in `edbfi/repository` slug.
3. Download `rules-plan`. Review `changes.diff`, every path and old/new hash in
   `plan.json`, the consumer base, and project toolchain requirements. Record the
   preview run ID and SHA256 of the exact `plan.json` bytes.
4. Dispatch **sync rules** with the same source/target, preview run and plan hash.
   This writer remains disabled until its credential and initial pilot are ready.
   It rejects stale source/base, altered artifacts, unexpected consumer edits and
   unsafe paths. A matching tree produces no PR.
5. Review the generated PR's exact head/base, full diff, author/sign-off, every
   expected CI job and relevant artifacts. Merge manually with the maintainer's
   reviewed `ghmerge` procedure, then verify final CI. Automerge is off; no branch
   protections or rulesets are part of this process. Preserve consumer prek files.

The writer creates a new `chore/agent-rules-<source SHA prefix>` branch. It never
force-pushes or writes a default branch. An identical open PR is reported; a
conflicting branch or closed PR is preserved and stops delivery. Repository
changes can still occur after a final API read: the PR's recorded base and normal
manual review remain authoritative; this is not an atomic lock on GitHub.

## Manifest and conflict handling

`publish` defaults to false. Every public target is an explicit opt-in in
`manifest.toml`; other owners and excluded projects are rejected. Canonical rule
changes do not add consumers automatically. Keep the manifest public-only.

`accepted` records the SHA256 of reviewed previous rule bytes. Existing consumers
must match either the desired bytes or an accepted previous version. Add a prior
canonical hash deliberately when updating a rule; never bless a custom consumer
edit merely to get a green run. Files absent in a consumer may be added.

Unrelated/custom rule files are preserved. To rename a managed rule, include an
explicit `[repo.remove]` old filename and its reviewed SHA256 in that target's
entry. The replacement and removal travel in one PR. Nothing else is pruned.

## Credentials

Read-only validation/preview uses the automatic GitHub job token. Only the writer
uses `RULES_SYNC_TOKEN`: a fresh fine-grained token named `edbfi-agent-rules-sync`,
owned by edbfi, scoped to the manifest targets with Contents and Pull requests
read/write (Metadata read is implicit). No Workflows, Administration or Packages
permission is needed. The user selects no expiry and generates/captures the value.
Never commit or log it. Old tokens are not reused or revoked by this migration.
The source repository is public and need not be in the PAT's selected targets.

## Development

Run `python3 .github/scripts/check-content.py`,
`python3 -m unittest discover -s tests -v` and `actionlint`.
Tests use disposable local fixtures and a stub GitHub API; they never sync real
consumers. See [CI.md](CI.md) and [toolchain notes](docs/toolchain-floors.md).
The old local synchronizer remains recoverable in repository history.

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
