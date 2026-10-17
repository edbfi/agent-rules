# Provenance

Research snapshot: 2026-10-16; expanded-guide revision: 2026-10-17. This revision
contains source-backed idiomatic coding guidance across the requested stack.
Admission does not require a measured baseline mistake: correct framework,
runtime, database and API practices belong in the guide even when the coding
model already knew them. This follows the explicit request for a full researched
guide and supersedes the earlier mistake-only pruning scope.

The initial evaluated version retained mostly dependency/lint/format tooling.
Its 72-run comparison is historical evidence for that minimal version only; it
does not validate this expanded guide or prove that the removed coding knowledge
was unnecessary. No new model benchmark is claimed for this expansion. Current
source/example verification is documented in the
[validation report](../../../docs/validation/bun-sveltekit-panda-drizzle-guidelines.md).

This public record preserves primary citations, evidence admissions and limits
without private workspace paths or raw transcripts. The earlier frozen/delivered
artifact remains unchanged as history; the repository guide now has different
operative content and must not claim its old fingerprint.

## Evidence

| file | section | evidence | reference |
|---|---|---|---|
| SKILL.md | Decisions | structure | Fixed layout; technical guidance supported by selected primary sources |
| SKILL.md | Decisions | decision | Explicit request for full source-backed coding guidelines, including idioms already known by the baseline |
| SKILL.md | Top mistakes | structure | Fixed required section; concrete pitfalls supported by references and source APIs |
| SKILL.md | Top mistakes | decision | Known incompatible/deprecated patterns and runtime boundaries in the selected releases |
| SKILL.md | Check | structure | Fixed required section |
| SKILL.md | Check | decision | Reusable project gate plus the committed example validation described in the public report |
| SKILL.md | Routing | structure | Routes to substantive component/integration references |
| references/bun-typescript.md | Runtime and dependency discipline | decision | Bun 1.4.3 lockfile/runtime documentation and selected package metadata |
| references/bun-typescript.md | Strict TypeScript boundaries | decision | TypeScript 6.0.3 declarations, official narrowing guidance and Kit 3 generated compiler options |
| references/bun-typescript.md | Resource ownership | decision | Bun SQLite/SQL lifecycle and transaction APIs; checked example resource cleanup |
| references/svelte.md | Reactive state and derived values | decision | Svelte 5.57.2 compiler/runtime declarations; official runes documentation |
| references/svelte.md | Component contracts and events | decision | Svelte 5 Snippet/render/callback contracts in shipped type declarations |
| references/svelte.md | Effects and server rendering | decision | Svelte 5 effect/lifecycle documentation and example compiler/SSR checks |
| references/sveltekit.md | Kit 3 configuration and imports | decision | Kit 3.1.0 plugin/config resolver and migration documentation |
| references/sveltekit.md | Route and server boundaries | decision | Kit 3 server modules, environment exports and request-scoped server data APIs |
| references/sveltekit.md | Loads actions and errors | decision | Official load/form-action documentation and selected Kit 3 action/error signatures |
| references/panda-ark.md | Panda generation and presets | decision | Panda 2.2.0 config resolver and Vite plugin generation/CSS-layer handling |
| references/panda-ark.md | Tokens recipes and extraction | decision | Panda 2.2.0 recipe/token/static-extraction APIs and checked example styles |
| references/panda-ark.md | Ark state and accessibility | decision | Ark Svelte 5.24.3 Dialog/Select declarations and official component documentation |
| references/drizzle.md | Choose the driver and schema | decision | Drizzle ORM rc5 bun-sqlite/bun-sql drivers, dialect builders and relation signatures |
| references/drizzle.md | Migrations are deployment artifacts | decision | Drizzle Kit rc5 defineConfig and matching runtime migrator signatures |
| references/drizzle.md | Transactions constraints and concurrency | decision | Selected Drizzle/Bun transaction APIs and database constraint/concurrency semantics; concrete sample tests |
| references/hey-api.md | Generate the contract | decision | Hey API 0.99.0 generator/config/plugin declarations |
| references/hey-api.md | Request scoped clients and envelopes | decision | Selected client-fetch/SDK request options and response envelope signatures |
| references/hey-api.md | Validation and failures | decision | Separate runtime validator hooks versus generated TypeScript declarations |
| references/integration.md | Build and generate in dependency order | decision | Verified Kit/Panda/Hey API dependency ordering and pinned example project |
| references/integration.md | Isolated database verification | decision | Bun bundled SQLite and isolated PostgreSQL 18.6 migration/runtime tests |
| references/integration.md | Browser and validation gates | decision | Common check script, actual sample execution and explicit browser checks where recorded |
| references/anti-patterns.md | * | decision | Source-backed wrong/why/right/grep rules for selected APIs and real project boundaries |
| references/versions.md | * | decision | Requested floors, TypeScript exact pin, dated stable-compatible selection and Drizzle RC exception |
| references/versions.md | * | compat | Selected release metadata, peer/runtime-engine ranges and observed integration/runtime versions |
| assets/package.json | * | decision | Selected dependency asset; consuming projects merge only needed entries |
| assets/eslint.config.js | * | baseline | Historical m-01: missing local lint gate/configuration in 8/8 initial submissions |
| assets/.prettierrc.json | * | baseline | Historical m-02: missing executable formatter in 7/8; task 4 was the passing exception |
| assets/.prettierignore | * | decision | Generated-output defaults are adapted to the consuming project |
| assets/examples | * | decision | Committed source project is the source of truth for instructional code blocks; checks recorded separately |
| scripts/check.sh | * | decision | Reusable dependency/build/lint/format/test gate; no per-task solution checks |

## Source-backed guidance basis

| Topic | Primary API documentation or fixed shipped source |
|---|---|
| Bun ownership, lockfiles and SQLite | [Versioned lockfile docs](https://raw.githubusercontent.com/oven-sh/bun/bun-v1.4.3/docs/pm/lockfile.mdx), [SQLite docs](https://raw.githubusercontent.com/oven-sh/bun/bun-v1.4.3/docs/runtime/sqlite.mdx), [SQL docs](https://raw.githubusercontent.com/oven-sh/bun/bun-v1.4.3/docs/runtime/sql.mdx) |
| TypeScript boundaries | [Official narrowing handbook](https://www.typescriptlang.org/docs/handbook/2/narrowing.html), [selected compiler package](https://registry.npmjs.org/typescript/6.0.3) |
| Svelte state, components and lifecycle | [Runes](https://svelte.dev/docs/svelte/what-are-runes), [fixed 5.57.2 source/types](https://registry.npmjs.org/svelte/-/svelte-5.57.2.tgz) |
| Kit configuration, routes, loads and forms | [Kit 3 migration](https://svelte.dev/docs/kit/migrating-to-sveltekit-3), [load](https://svelte.dev/docs/kit/load), [form actions](https://svelte.dev/docs/kit/form-actions), [fixed 3.1.0 source/types](https://registry.npmjs.org/@sveltejs/kit/-/kit-3.1.0.tgz) |
| Panda presets, generation and extraction | [Vite integration](https://panda-css.com/docs/get-started/vite), [v2 migration](https://panda-css.com/docs/get-started/upgrading-to-v2), [fixed 2.2.0 development package](https://registry.npmjs.org/@pandacss/dev/-/dev-2.2.0.tgz) |
| Ark controlled state and accessible parts | [Dialog documentation](https://ark-ui.com/docs/components/dialog), [fixed 5.24.3 Svelte component source](https://registry.npmjs.org/@ark-ui/svelte/-/svelte-5.24.3.tgz) |
| Drizzle drivers, schemas and transactions | [Fixed matched ORM rc5 source/types](https://registry.npmjs.org/drizzle-orm/-/drizzle-orm-1.0.0-rc.5-5935859.tgz), [matching Kit source/types](https://registry.npmjs.org/drizzle-kit/-/drizzle-kit-1.0.0-rc.5-5935859.tgz) |
| Generated clients and runtime validation | [Fetch client documentation](https://heyapi.dev/docs/openapi/typescript/clients/fetch), [fixed 0.99.0 generator/plugin declarations](https://registry.npmjs.org/@hey-api/openapi-ts/-/openapi-ts-0.99.0.tgz) |

Unversioned official documentation is corroborating material. Selected release
source/signatures and concrete example checks control version-sensitive claims.
A runtime check supports the exercised behavior only, not every prose statement
or every alternate driver/deployment mode. Code blocks are tied to committed
example files and verified for exact source agreement.

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

## Expanded example verification

The expanded example passed Kit/Panda/Hey API generation, separate SQLite and
PostgreSQL migration generation, strict Svelte/TypeScript checking (0 errors,
0 warnings), production build, ESLint with zero warnings and Prettier checking.
Three Bun tests passed with nine expectations, including the required isolated
PostgreSQL test; no PostgreSQL skip was counted as coverage. Production Chromium
checked the concrete UI/form/API/private-HTML paths listed in the
[validation report](../../../docs/validation/bun-sveltekit-panda-drizzle-guidelines.md).

Actual execution caught a dialog event annotation/lint issue and the adapter's
HTTPS-origin default for local HTTP forms. The corrected sample infers the DOM
event type and explicitly configures its canonical origin while retaining CSRF
checks. These source/runtime checks validate exercised example paths; they are
not a replacement for an expanded-guide model benchmark.

## Historical tooling experiment

The initial baseline admissions remain relevant to the retained tooling assets:
m-01 was an absent executable local lint gate/config in 8/8 development tasks;
m-02 was an absent formatter gate in 7/8, with task 4 passing; m-03 was a separate
exact TypeScript 6.0.3 dependency-declaration failure in tasks 6/7. These were generic
frozen defaults, not requirements explicitly repeated in every task prompt.
The old initial baseline scored 58/77 assertions; the first guided version 77/77.

The later 72 fresh calls scored 350/351 guided versus 261/351 control assertions.
That minimal tooling-oriented version had already been over-pruned. The score
does not measure the expanded reference content now present. Five earlier host
capture failures stayed invalid/ungraded and were replaced only by fresh calls.
The unchanged primary score retained one E10 assertion overconstraint at 9/10,
without an Integrity penalty or claim that its ORDER BY behavior was defective.

## Limits

No expanded-guide coding-model benchmark was run. Automatic native activation is
untested. Historical experiments used explicit/on_demand developer instructions;
provider dollar costs are unknown. Frozen historical results and expanded sample
validation must be reported separately. Source-backed prose is reviewed against
primary APIs; only the concrete executions listed in the validation report are
claimed as tested. Private raw experiment artifacts are not bundled here.
