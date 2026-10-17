# Bun/SvelteKit/Panda/Drizzle guidelines validation

The [skill](../../.agents/skills/bun-sveltekit-panda-drizzle-guidelines/SKILL.md)
provides selected dependency declarations, TypeScript/Svelte lint and formatting
configuration, and a reusable verification script for the requested stack.
Research snapshot: 2026-10-16; final evaluation completed 2026-10-17. Exact pins,
compatibility modes and primary source citations are in its
[version table](../../.agents/skills/bun-sveltekit-panda-drizzle-guidelines/references/versions.md)
and [provenance](../../.agents/skills/bun-sveltekit-panda-drizzle-guidelines/PROVENANCE.md).

## Final comparison

All 12 tasks used both without-skill and with-instructions conditions, with three
fresh valid runs per task/condition: 72 coding calls, zero invalid/reused final
runs, zero unverifiable assertions. Primary rates average each task's three
repeats, then weight each task equally. Pooled assertion counts are secondary.
All differences below are with instructions minus without skill.

| Scope | With instructions | Without skill | Mean task difference | Pooled passed/scored |
|---|---:|---:|---:|---|
| Development, 8 tasks | 100.0000% | 74.3981% | +25.6019 points | 231/231 vs 172/231 |
| Held out, 4 tasks | 99.1667% | 74.2929% | +24.8737 points | 119/120 vs 89/120 |
| Overall, 12 tasks | 99.7222% | 74.3631% | +25.3591 points | 350/351 vs 261/351 |

The coding runner used gpt-6.1-sol/high through Codex app-server 0.163.0. Conditions
shared exact task prompt bytes, declared fixtures, frozen assertions, pinned
toolchain, permissions and limits; only selected guidance differed. Each call
had a fresh isolated non-root Docker workspace, isolated database state, 1,800s
coding timeout and 600s postcheck timeout. Guidance loaded explicitly on demand
through developer instructions; checks were exposed only after coding exited.
Independent graders excluded injected guidance/read bodies from their context.

Generic lint, format and selected-version gates were frozen evaluation defaults,
even when individual task prompts did not explicitly ask for them. All 36 control
runs failed lint and format assertions; 18 selected-version assertions also
failed. Thus these results primarily demonstrate meeting the measured tooling
contract, not general failure of unguided functional code.

The single guided failure is E10 repeat 1's sealed API-ordering clause. Its
append-only API does not accept caller-selected out-of-order positions, while a
second SQLite connection in its test correctly demonstrates ORDER BY and stable
records. The prompt did not explicitly require caller-selected positions or a
reorder API. This assertion overconstraint remains in the primary 9/10 score;
there is no Integrity penalty or claim of a sorting defect. Neither assertions
nor the candidate were changed after final freeze. Three repeats per task and
four held-out tasks provide descriptive evidence, not a correctness guarantee.

## Development and pruning

The initial eight-task baseline scored 58/77 assertions, 75.2778% mean task rate;
the first guided iteration scored 77/77. Each of three independent removals
(Top mistakes, integration, anti-patterns) preserved 231/231 assertions over 24
valid runs per condition. Shared full-candidate runs were reused without extra
coding calls. The jointly pruned candidate then passed 77/77 in eight fresh
development runs before final freeze. Required empty scaffolds remain.

Five earlier ablation attempts failed host artifact capture, not task grading:
four dereferenced dangling PostgreSQL documentation symlinks, and one misframed
literal U+0085 inside valid JSON-RPC strings. Raw evidence was preserved, the
host-only capture revision was tested, and missing slots were filled by fresh
calls. No invalid attempt was retrospectively assigned a score.

## Export identity and checks

The nine operative files are byte-identical to the evaluated delivery, including
dotfiles and executable check-script mode. Only nonoperative PROVENANCE.md is a
compact public adaptation, omitting private absolute paths and transcripts while
preserving evidence admissions, sources and limits. The full public-export tree
is therefore not claimed to equal the original audit-bundle hash. Raw evaluation
artifacts and the verified example project are retained outside this repository.

Operative-file fingerprint:
`2b8a61c85d76b1d484da9265ba78223f2745644a992b0fe0bba99ff5b3232214`.
Algorithm: SHA256 of compact JSON sorted
`[[relative POSIX path, SHA256(file bytes)], ...]`, excluding PROVENANCE.md.

Delivered-copy checks passed: token budget (490 entrypoint/864 loaded estimated
tokens), provenance coverage, example verification and creator quick validation.
Executable assets also passed the pinned example's production SSR/client build,
Svelte checks, lint, formatting, tests, SQLite/PostgreSQL migration/CRUD and
Chromium interaction before export. No instructional code blocks remain after
pruning. Repository checks and the same skill validators are run for this export.

Native automatic discovery/activation remains untested; the evaluation used
explicit loading. Dollar cost is unreported. The final 72 calls reported
58,409,548 provider tokens. All 198 coding attempts across development, ablations,
invalids and final evaluation reported 164,032,182 tokens, counting reused copies
once; cached/reasoning token subsets were not added again. Other agent-context
usage is outside that coding ledger. No optional .skill archive helper was
available; this repository publishes the folder.
