# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What ships

- `rules/*.md` is the product. Each rule is copied byte-for-byte into opted-in consumer repos at `.agents/rules/<name>.md`. The rules describe consumer stacks (Svelte, Go, Swift, ...), not how to work in this repo. They are 25–40 KB each, so open only the one you are editing.
- `manifest.toml` lists the opted-in consumer repos and the rules each one receives. Nothing reads it automatically; it is the record used when copying rules by hand.

## Rule files

- Required shape: starts with `---` frontmatter containing `type:` (convention: `type: "agent_requested"` plus `description:`), has a `# ` title, LF endings, trailing newline.
- Keep one flat file per stack directly in `rules/`. The identifier is the filename stem, `[a-z0-9_-]+`, with version dots written as `_` (`python-3_14-core`). Don't use symlinked rules or subdirectories; use a regular file.
- Before changing a rule's toolchain claims, read `docs/toolchain-floors.md`: consumer floors win over the rule's examples.

## Accepted hashes (the main footgun)

A consumer's managed file is an "unreviewed edit" unless its bytes equal the new canonical bytes or appear in `[accepted]."<rule>"` in `manifest.toml`. Don't overwrite an unreviewed edit when copying a rule.

When you change a rule that some `[[repo]]` target lists:

1. Hash the prior canonical bytes: `git show HEAD:rules/<name>.md | shasum -a 256`.
2. Make sure that hash is in `[accepted]."<name>"`. Append; never replace, because consumers can be on any earlier version.
3. Never add the hash of a consumer's custom edit to make it pass.

## Manifest (`manifest.toml`)

- `[defaults]` must stay exactly `publish = false`. Each target is an explicit `[[repo]]` with `slug = "edbfi/<name>"`, `publish = true` and `rules = [...]`. Never target private or archived repos, or these excluded repos: `cccp-ps`, `afisharr`, `cdiag.link`, `claude-atoll-web`, `claude-diag`, `tgraph-bot-source`, `autoscan`.
- Opting a repo in is a manifest change (see commit `3e39eb1`); its rules are then copied manually.
- To rename a managed rule, add `[repo.remove]` `"old-name.md" = "<sha256 of reviewed old bytes>"` under that target. Nothing else is ever pruned from consumers.
- Only `manifest.toml` is used. `manifest.local.toml`, `.sync-cache/` and similar entries in `.gitignore` belong to a retired local synchronizer. Don't recreate local manifests or checkout discovery.

## Process

- Commits and PR titles use Conventional Commits with a `Signed-off-by` trailer (`git commit -s`).
- There is no delivery automation; review rule changes and copy them manually.
