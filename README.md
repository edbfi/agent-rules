# agent-rules

The canonical coding-guidelines library for edbfi projects, and the tool that delivers it.

Guidelines are researched, sourced and example-verified Markdown packs produced by
[`coding-guidelines-builder`](https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/SKILL.md).
They live in [`guidelines/`](guidelines/INDEX.md); `scripts/sync.py` delivers the packs each opted-in
repository needs as a reviewed pull request, together with one short pointer rule per entry in
that repository's `.agents/rules/`.

## Layout

```text
guidelines/
  INDEX.md              generated catalog of every pack
  components/<id>/      one pack per component and version line (typescript, python-3_14, ...)
  stacks/<id>/          one pack per combination; routes to its component packs
rules/                  optional hand-written flat rules (created with the first one)
manifest.toml           which repositories receive which entries
scripts/check-library.py, scripts/sync.py, scripts/legacy-rules.json
.agents/skills/coding-guidelines-builder/   the installed builder (skills-lock.json)
```

The pack format is the builder's
[`references/pack-format.md`](https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/references/pack-format.md).

## Building or refreshing packs

From this repository, ask an agent to use the installed `coding-guidelines-builder` with the stack
(for example "TypeScript", or "Bun, SvelteKit 3, Drizzle with PostgreSQL") and the library root
`guidelines/`. To refresh, name the pack: `refresh: guidelines/components/typescript`. Commit the
packs and the regenerated `guidelines/INDEX.md` in one PR.

Install or update the builder with:

```sh
bunx skills add https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/SKILL.md --skill coding-guidelines-builder --agent codex --yes
```

## Opting a repository in

Add a target to `manifest.toml`:

```toml
[[repo]]
slug = "edbfi/comradarr"
publish = true
guidelines = ["stacks/bun-sveltekit-panda-drizzle", "components/python-3_14"]
rules = []
```

A stack entry also delivers the component packs it declares. Empty `guidelines` and `rules` retire a
target: the next sync removes every unmodified delivered file, after which the entry can go. Rule
names starting with `guidelines-` are reserved for the generated pointers. With no targets at all,
the manifest keeps `repo = []` above `[defaults]`.

## Syncing

```sh
python3 scripts/sync.py plan  --repo edbfi/comradarr        # what would change; writes nothing
python3 scripts/sync.py apply --repo edbfi/comradarr        # prepare a local branch
python3 scripts/sync.py apply --repo edbfi/comradarr --pr   # push it and open a pull request
python3 scripts/sync.py plan  --all                         # every target
```

The checkout defaults to `~/github/<owner>/<repo>` (`--checkout PATH` or `--checkouts ROOT` to
change it). Sync works in a temporary worktree from the consumer's freshly fetched default branch,
so the checkout's own working tree and branches are never touched, and it only delivers content
that is merged to `origin/main` here.

In the consumer, packs land in `.agents/guidelines/` (without their `examples/`), pointers and rules
in `.agents/rules/`, and `.agents/guidelines/guidelines-lock.json` records every delivered file. A
file edited in the consumer is never overwritten: its delivery set, and any set sharing a component
pack that would change, is held back and reported as a conflict (exit 1) until it is reconciled.
Flat rules delivered before the library are removed only once their replacement arrives and only if
unmodified (`scripts/legacy-rules.json`).

## Development

Run `prek run --all-files --hook-stage manual` for the same checks as CI. `python3 scripts/check-library.py`
validates the manifest, rules and every pack with the installed builder's checks;
`python3 scripts/check-library.py --stale` lists packs past their refresh date, which the weekly CI
run turns into a failure. `python3 -m unittest discover -s tests` runs the sync and check tests.

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
