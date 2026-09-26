# agent-rules

Twelve canonical, flat Markdown rule files for explicitly opted-in edbfi projects.
Source files are the artifact; no application build or local hydration is needed.

## Delivery

Workflow-based delivery is disabled. Review and copy canonical rule changes manually into explicitly opted-in repositories. Preserve consumer-specific rules and local hooks.

## Manifest and conflict handling

`publish` defaults to false. Every public target is an explicit opt-in in
`manifest.toml`; other owners and excluded projects are never targets. Canonical rule
changes do not add consumers automatically. Keep the manifest public-only.

`accepted` records the SHA256 of reviewed previous rule bytes. Existing consumers
must match either the desired bytes or an accepted previous version. Add a prior
canonical hash deliberately when updating a rule; never bless a custom consumer
edit merely to make it pass. Files absent in a consumer may be added.

Unrelated/custom rule files are preserved. To rename a managed rule, include an
explicit `[repo.remove]` old filename and its reviewed SHA256 in that target's
entry. The replacement and removal travel in one PR. Nothing else is pruned.

## Development

There are no scripts or tests; rule changes are reviewed and copied manually.
See the [toolchain notes](docs/toolchain-floors.md).
The old local synchronizer and the retired CI delivery scripts remain recoverable
in repository history.

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
