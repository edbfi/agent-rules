# Development CI and publishing

Every PR/default-branch push validates the 12 canonical rule files and the public
manifest: opt-in publishing, unique public slugs, existing safe rule identifiers,
metadata/title and LF-terminated content. Bash parsing and ShellCheck cover the
sync tool. Three integration tests exercise the actual script using disposable
Git repositories: dry-run preservation, de-publishing before exclusion, pruning,
byte-identical copies, idempotence and restoration of chained hooks when opting in.
Run `python3 .github/scripts/check-content.py`, `shellcheck bin/sync` and
`python3 -m unittest discover -s tests -v` locally. No real consumer sync is needed.

The shared `ci / required` gate fails on missing, skipped, cancelled or failed
prerequisites and verifies explicit PR dispatch identities. Validation is
read-only; action references are full version tags. Renovate inherits the
versioned shared base preset. Rule prose and consumer runtime floors are not
silently updated by dependency maintenance.

The publisher now proposes consumer PRs using the existing SYNC_TOKEN, with
explicit default branches, a dedicated branch, only `.agents/rules` changes and
at most three concurrent targets. That token must have Contents and Pull requests
write access on the already-published target list. Unlike GITHUB_TOKEN-generated
PRs, these PRs start normal consumer workflows. Required checks block merging when
CI is missing or unsuccessful; the publisher never bypasses branch protection.
The local-only manifest remains outside this workflow, and no private targets
are added to public configuration. Existing rule files and public membership are
unchanged by this rollout.

Protect the default branch with strict up-to-date `ci / required` from GitHub
Actions, enforce administrators, disallow force pushes/deletions and require no
blanket reviews. Consumer merges still need toolchain-floor review when rules
change: syntax/content CI does not prove that prose accurately describes every
language version. Verify token scope and a real generated PR after the consumer
CI rollout. Automerge stays off until shared-policy readiness is confirmed.
