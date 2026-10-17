# Provenance

Research snapshot: 2026-10-16. Coding model: gpt-6.1-sol, high; Codex
CLI/app-server 0.163.0, explicit/on_demand instruction loading. Automatic native
discovery and description optimization were not measured. The model's knowledge
cutoff is unknown; no cutoff-specific or contradicted-probe admissions are claimed.

This is a compact public export of the nonoperative audit record. The nine
operative files (SKILL.md, references, assets and check script) are byte-identical
to the evaluated skill. This provenance file omits private workspace paths,
transcripts and duplicated release extracts; its tree hash therefore differs
from the original audit bundle. It is not referenced by loaded skill instructions.
Detailed evaluation artifacts remain outside this repository. The
[public validation report](../../../docs/validation/bun-sveltekit-panda-drizzle-guidelines.md)
records the method, complete planned coverage, results and limits without claiming
that raw transcripts are bundled here.

## Evidence

| file | section | evidence | reference |
|---|---|---|---|
| SKILL.md | Decisions | structure | Required fixed-layout section; concrete choices supported by the records below |
| SKILL.md | Decisions | decision | Requested stack, selected release policy, verified tooling choices and exact assets |
| SKILL.md | Top mistakes | structure | Required empty heading after measured removal of redundant guidance |
| SKILL.md | Check | structure | Required fixed-layout section |
| SKILL.md | Check | decision | Unchanged evaluated check script; tests required only when the task requests them |
| SKILL.md | Routing | structure | Routes only to retained admitted release/compatibility guidance |
| references/integration.md | * | decision | Required empty scaffold after individual and joint pruning; no operative integration claims remain |
| references/anti-patterns.md | * | decision | Required empty lookup-table scaffold after pruning; no anti-pattern rows remain |
| references/versions.md | * | decision | Requested floors, TypeScript exact pin, stable-compatible selection and Drizzle-only RC exception |
| references/versions.md | * | compat | Pinned package metadata/peer ranges, Bun runtime SQLite query and full-stack integration checks |
| assets/package.json | * | decision | Exact selected dependency declarations extracted from the verified example project; merge only needed dependencies |
| assets/eslint.config.js | * | baseline | m-01: missing local TypeScript/Svelte lint gate/configuration across all eight initial development submissions |
| assets/eslint.config.js | * | compat | ESLint/TypeScript/Svelte flat config passed the pinned SvelteKit 3 production and lint gates |
| assets/.prettierrc.json | * | baseline | m-02: missing executable formatting gate in seven initial development submissions; task 4 passed formatting |
| assets/.prettierrc.json | * | compat | Prettier 3/Svelte-plugin 4 configuration passed the pinned formatting gate |
| assets/.prettierignore | * | decision | Verified generated-output defaults; consuming projects must adjust generated paths |
| scripts/check.sh | * | decision | Same generic gate used during evaluation; SHA256 cf6568a0a58403ff42b51422a113ec25568328817b3e967d9acd608680b4e02e |

## Admission and verification records

The requested stack was Bun 1+, TypeScript exactly 6.0.3, Svelte 5+/Kit 3+, Svelte
Vite plugin 7+/Vite 8+, official Bun adapter 1+, Panda development/Vite/presets 2+,
Ark UI for Svelte 5+, Drizzle ORM/Kit 1+ (matched latest RC allowed), Bun-bundled
SQLite 3+, PostgreSQL 18+ and Hey API 0+. Other packages follow the latest stable
mutually compatible releases in the dated research snapshot. SQLite was queried
from the selected Bun runtime rather than selected independently.

Initial baseline admissions, eight development tasks with one repeat each:

- **m-01:** every submitted project lacked either its local ESLint command/
  dependency or the required flat configuration; retained lint assets address it.
- **m-02:** seven projects lacked an executable Prettier/Svelte formatting gate;
  task 4 was the measured passing exception. Retained formatter assets address
  this seven-of-eight failure.
- **m-03:** tasks 6/7 failed the separate exact TypeScript 6.0.3 dependency-declaration
  assertion: task 6 supplied only a repaired component, and task 7 declared ^6.0.0.
  Temporary/shared or locked 6.0.3 execution did not satisfy that declaration gate.
  The retained dependency asset and version table address this two-of-eight failure.

These lint/format/version requirements were generic frozen evaluation defaults;
the individual task prompts did not all explicitly request them. The initial
baseline was 58/77 scored assertions and 75.2778% mean task rate. Final controls
also failed the lint/format defaults, so measured gains must not be presented as
proof that unguided functional behavior was generally incorrect.

The example project passed the common gate with requested tests enabled:
production SSR/client build, zero-warning Svelte checking, ESLint, Prettier,
SQLite tests, isolated PostgreSQL 18.6 migration/CRUD and production Chromium
interaction. Configuration assets are unchanged copies; the dependency asset
selects entries from that verified manifest. No instructional code blocks remain
after pruning; executable assets and the common check remain verified material.

Three independent section removals each preserved 231/231 assertions across 24
valid runs per condition. The jointly pruned candidate then passed 77/77 in eight
fresh development runs. Required empty scaffolds remain; unsupported/redundant
guidance was not retained merely to fill them. No holdout finding informed a
candidate revision. The final comparison used 72 fresh valid calls, all 12 tasks,
both conditions and three repeats, with independent grading and no unverifiable
assertions. Detailed results and the retained E10 assertion overconstraint are
in the public report. No post-freeze score-driven assertion or candidate changes
were made.

## Primary release and compatibility sources

Exact selected pins and mode constraints are retained in
[references/versions.md](references/versions.md). Sources below identify fixed
published releases; mutable documentation was corroborated against their shipped
source and actual integration/runtime checks.

| Component | Primary source |
|---|---|
| Bun 1.4.3 / bundled SQLite | [Release metadata](https://registry.npmjs.org/bun/1.4.3), [versioned SQLite docs](https://raw.githubusercontent.com/oven-sh/bun/bun-v1.4.3/docs/runtime/sqlite.mdx); runtime query observed SQLite 3.53.4 |
| TypeScript 6.0.3 / Bun types 1.4.3 | [TypeScript](https://registry.npmjs.org/typescript/6.0.3), [Bun types](https://registry.npmjs.org/@types/bun/1.4.3) |
| Svelte 5.57.2 / Kit 3.1.0 | [Svelte](https://registry.npmjs.org/svelte/5.57.2), [Kit](https://registry.npmjs.org/@sveltejs/kit/3.1.0) |
| Svelte Vite plugin 7.3.1 / Vite 8.3.4 / adapter-bun 1.0.0 | [Plugin](https://registry.npmjs.org/@sveltejs/vite-plugin-svelte/7.3.1), [Vite](https://registry.npmjs.org/vite/8.3.4), [official adapter](https://registry.npmjs.org/@sveltejs/adapter-bun/1.0.0) |
| Panda 2.2.0 | [Development](https://registry.npmjs.org/@pandacss/dev/2.2.0), [Vite](https://registry.npmjs.org/@pandacss/vite/2.2.0), [base](https://registry.npmjs.org/@pandacss/preset-base/2.2.0), [Panda preset](https://registry.npmjs.org/@pandacss/preset-panda/2.2.0) |
| Ark Svelte 5.24.3 | [Release metadata](https://registry.npmjs.org/@ark-ui/svelte/5.24.3) |
| Drizzle 1.0.0-rc.5-5935859, matched pair | [ORM](https://registry.npmjs.org/drizzle-orm/1.0.0-rc.5-5935859), [Kit](https://registry.npmjs.org/drizzle-kit/1.0.0-rc.5-5935859); latest published matched RC in the snapshot, ahead of the older rc.4 tag |
| PostgreSQL 18.6 | [Official release matrix/policy](https://www.postgresql.org/support/versioning/); isolated 18.6 migration/CRUD/race verification |
| Hey API 0.99.0 | [Generator metadata](https://registry.npmjs.org/@hey-api/openapi-ts/0.99.0) |
| ESLint 10.13.0 / @eslint/js 10.0.1 | [ESLint](https://registry.npmjs.org/eslint/10.13.0), [JS rules](https://registry.npmjs.org/@eslint/js/10.0.1) |
| typescript-eslint 8.71.2 / eslint-plugin-svelte 3.23.1 | [TS rules/parser](https://registry.npmjs.org/typescript-eslint/8.71.2), [Svelte plugin](https://registry.npmjs.org/eslint-plugin-svelte/3.23.1) |
| Prettier 3.9.10 / prettier-plugin-svelte 4.1.1 | [Prettier](https://registry.npmjs.org/prettier/3.9.10), [Svelte formatter](https://registry.npmjs.org/prettier-plugin-svelte/4.1.1) |
| svelte-check 4.7.7 / Playwright 1.64.1 | [Svelte check](https://registry.npmjs.org/svelte-check/4.7.7), [Playwright](https://registry.npmjs.org/playwright/1.64.1) |

Compatibility checks covered 20 declared peer/runtime-engine ranges and actual
full-stack SSR/browser/database execution. Shipped Panda 2.2.0 config resolution
requires explicit presets despite older README wording; shipped Kit 3 rejects
svelte.config.js, so lint parser configuration follows verified Kit 3 behavior
rather than that older plugin README example. The recorded package sources and
integration checks take precedence over unversioned examples.

## Limits

Explicit on-demand loading measures the effect of instruction content, not native
activation. Provider dollar cost is unknown. The finite development/holdout
sample is descriptive. One guided final E10 assertion overconstrains the original
prompt; its frozen 9/10 score is retained without claiming a sorting defect or
Integrity penalty. Five earlier ablation capture failures were invalid/ungraded,
diagnosed and replaced with fresh attempts; they were never converted to scores.
Public export changes only this audit record and adds the external report;
operative instructions, release choices, assets and check script are unchanged.
