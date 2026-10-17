# agent-rules

The previous canonical Markdown rules and connected repository list have been
cleared. `manifest.toml` has no targets or accepted rule hashes, and publishing
remains disabled.

## Local skills

The `coding-guidelines-builder` skill is installed in
`.agents/skills/coding-guidelines-builder/` from
[edbfi/skills](https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/SKILL.md).
Its source is recorded in `skills-lock.json`.

Install or refresh it locally with:

```sh
bunx skills add https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/SKILL.md --skill coding-guidelines-builder --agent codex --yes
```

The generated [Bun/SvelteKit/Panda/Drizzle guidelines](.agents/skills/bun-sveltekit-panda-drizzle-guidelines/SKILL.md)
cover the selected stack and include reusable dependency, lint, formatting and
verification tools. Their [validation report](docs/validation/bun-sveltekit-panda-drizzle-guidelines.md)
records the evaluated release pins, measured results and limitations.

## Development

Run `prek run --all-files --hook-stage manual` for the same checks as CI.
Run `python3 scripts/check-rules.py` to validate rule and manifest shape alone;
an empty rule collection is supported.

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
