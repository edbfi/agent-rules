# agent-rules — working notes

Twelve flat canonical Markdown rules, a public opt-in manifest, and CI-only
preview/PR delivery. No local hydration or checkout discovery is supported.

- Preserve canonical rule bytes during delivery maintenance. Keep one flat file
  per stack; no concatenation or generated reference hierarchy.
- Publish defaults to false. Only explicit edbfi targets may receive PRs. Never
  add private/local manifests or excluded projects to public configuration.
- Preserve unrelated consumer files, prek configurations and local state.
  Remove only explicitly named, hash-matched obsolete rules in the same PR as
  their replacement. Unexpected managed-file edits are conflicts.
- Compare exact hashes and source/base revisions. Never force-push, merge
  delivery PRs automatically. Preserve required-check protection and the
  Renovate-owned dependency policy in CI.md; rule delivery stays manual.
- Test through `python3 -m unittest discover -s tests -v`; fixtures must not
  contact real consumers. Delivery CLI execution is restricted to manual CI.
- Reconcile project toolchain requirements before reviewing a rule update.
  Existing project minimum versions take precedence over examples in generic
  guidance. Verify official registries/release documentation when changing pins;
  content-shape validation alone does not prove rule prose correct.

See README.md, CI.md and docs/toolchain-floors.md for the delivery contract.
