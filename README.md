# agent-rules

The previous canonical Markdown rules and connected repository list have been
cleared. `manifest.toml` has no targets or accepted rule hashes, and publishing
remains disabled.

## Local skill

The `coding-guidelines-builder` skill is installed in
`.agents/skills/coding-guidelines-builder/` from
[edbfi/skills](https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/SKILL.md).
Its source is recorded in `skills-lock.json`.

Install or refresh it locally with:

```sh
bunx skills add https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/SKILL.md --skill coding-guidelines-builder --agent codex --yes
```

## Development

Run `prek run --all-files --hook-stage manual` for the same checks as CI.
Run `python3 scripts/check-rules.py` to validate rule and manifest shape alone;
an empty rule collection is supported.

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
