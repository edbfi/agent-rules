# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What ships

- `rules/*.md` is the product. Each rule is copied byte-for-byte into opted-in consumer repos at `.agents/rules/<name>.md`. The rules describe consumer stacks (Svelte, Go, Swift, ...), not how to work in this repo. They are 25–40 KB each, so open only the one you are editing.
- `.github/scripts/delivery.py` holds all manifest validation plus the preview planner and PR writer. `check-content.py` imports `manifest()` from it, so put new manifest checks in `delivery.py`.
- There is no build step and no `package.json`. The npm pins inside rule files are the repo's dependency surface, and Renovate edits them in place through a regex manager (`renovate.json`).

## Commands

Stdlib-only Python (3.11+ for `tomllib`); nothing to install. These mirror the `content` job in `.github/workflows/ci.yml`:

```bash
python3 .github/scripts/check-content.py        # rule shape + manifest validation
python3 -m py_compile .github/scripts/*.py
python3 -m unittest discover -s tests -v
python3 -m unittest tests.test_delivery -v                                 # one file
python3 -m unittest tests.test_delivery.Delivery.test_noop_never_writes    # one case
actionlint                                       # workflows; local only, CI does not run it
```

CI also fails if the checks leave the tree dirty (`git diff --exit-code HEAD`).

## Rule files

- Shape enforced by `check-content.py`: starts with `---` frontmatter containing `type:` (convention: `type: "agent_requested"` plus `description:`), has a `# ` title, LF endings, trailing newline.
- Keep one flat file per stack directly in `rules/`. The identifier is the filename stem, `[a-z0-9_-]+`, with version dots written as `_` (`python-3_14-core`). Symlinked rules and subdirectories are rejected; use a regular file.
- Don't hand-edit pinned versions for dependency bumps; Renovate owns them. `typescript` in `rules/wxt-svelte5-extension.md` is capped `<7` in `renovate.json` on purpose.
- Before changing a rule's toolchain claims, read `docs/toolchain-floors.md`: consumer floors win over the rule's examples.

## Accepted hashes (the main footgun)

Delivery treats a consumer's managed file as an "unreviewed edit" and aborts unless its bytes equal the new canonical bytes or appear in `[accepted]."<rule>"` in `manifest.toml`.

When you change a rule that some `[[repo]]` target lists:

1. Hash the prior canonical bytes: `git show HEAD:rules/<name>.md | shasum -a 256`.
2. Make sure that hash is in `[accepted]."<name>"`. Append; never replace, because consumers can be on any earlier version.
3. Never add the hash of a consumer's custom edit to get a green run.

Every rule listed by any target needs at least one accepted hash, or `manifest()` fails with "Missing accepted hashes". Renovate's pin bumps don't update `[accepted]`. Today only `wxt-svelte5-extension` has matching pins, and no target lists it.

## Manifest (`manifest.toml`)

- `[defaults]` must stay exactly `publish = false`. Each target is an explicit `[[repo]]` with `slug = "edbfi/<name>"`, `publish = true` and `rules = [...]`. Slugs in `EXCLUDED` in `delivery.py` are rejected, and so are private or archived repos at plan time.
- Opting a repo in is a manifest-only change (see commit `3e39eb1`). It delivers nothing until someone dispatches the workflows by hand.
- To rename a managed rule, add `[repo.remove]` `"old-name.md" = "<sha256 of reviewed old bytes>"` under that target. Nothing else is ever pruned from consumers.
- Only `manifest.toml` is read. `manifest.local.toml`, `.sync-cache/` and similar entries in `.gitignore` belong to a retired local synchronizer. Don't recreate local manifests or checkout discovery.

## Delivery code and tests

- `delivery.py main()` refuses to run outside `workflow_dispatch` CI in `edbfi/agent-rules`. Exercise it by calling `build_plan()` / `publish()` with a fake `request`, not by running the CLI or `gh api`.
- Tests are offline. Add cases to `tests/test_delivery.py` using its `GitHub` stub and temp-dir `write_manifest()`, for example:

  ```python
  gh = GitHub({".agents/rules/core.md": b"old\n", ".agents/rules/custom.md": b"custom\n"})
  self.publish(self.plan(gh), gh)
  tree = next(v for e, v in gh.writes if e.endswith("/git/trees"))
  ```

- The writer must never force-push, update an existing ref or write a default branch. The tests assert this; keep them passing rather than loosening them.

## Process

- Commits and PR titles use Conventional Commits with a `Signed-off-by` trailer (`git commit -s`). The PR policy workflow enforces both.
- The delivery runbook (preview, then review `plan.json`/`changes.diff`, then sync with the plan SHA256) is in `README.md` under "Delivery". Read it before touching `preview.yml`, `sync.yml` or the plan format.
- CI job names and the Renovate merge policy are described in `CI.md`. Read it before renaming jobs in `ci.yml`, because the shared gate and required checks depend on those names.
