---
name: bun-sveltekit-panda-drizzle-guidelines
description: Use for writing, extending, reviewing, fixing, or setting up a Bun, TypeScript, SvelteKit, Panda CSS, Ark UI, Drizzle and Hey API application. Covers current APIs, reactive components, server boundaries, styling, accessible UI, typed API clients, database transactions and migrations, and executable verification. Apply to coding tasks in this stack even when the request does not name a framework; excludes non-coding questions and unrelated single-component projects.
---

# Bun SvelteKit Panda Drizzle coding guidelines

Build a server-rendered, typed application with explicit boundaries: Svelte owns component state, Kit owns HTTP and server data, Panda generates styles, Ark owns interaction semantics, and the database owns persistence constraints. Keep secrets and database clients on the server. Generate types and CSS from their real inputs, then test the resulting application and database behavior.

This guide includes practical current API rules and runnable examples for the entire stack. Read the relevant focused reference before changing that part of an application. The compact [example project](assets/examples/package.json) supplies real imports and configuration; regenerate its ignored SDK/styling output before running it.

## Decisions

- Use Bun for installation, scripts, tests and the production server. Keep the selected exact dependency declarations in [assets/package.json](assets/package.json); TypeScript is **6.0.3 exactly**. The release matrix and peer/runtime constraints are in [versions](references/versions.md).
- Kit 3 configuration belongs in `sveltekit({ adapter: adapter() })` inside Vite config, using official `@sveltejs/adapter-bun`. Kit installs its Svelte Vite plugin; do not register another copy. Use package `imports` such as `#lib/*`, and extend `$app/tsconfig`. [Kit 3 configuration](https://svelte.dev/docs/kit/migrating-to-sveltekit-3).
- Use Svelte 5 runes, callback props and snippets for new components. Mutable local state uses `$state`; computed state uses `$derived`; `$effect` is for synchronization with external systems, with cleanup. [Runes](https://svelte.dev/docs/svelte/what-are-runes).
- Configure Panda development tools, Vite plugin and both base/theme presets together. Prefer tokens and finite recipe variants; keep values visible to static extraction. Use Ark components for focus, keyboard interaction and ARIA semantics, and Panda for presentation. [Panda Vite](https://panda-css.com/docs/get-started/vite), [Ark styling](https://ark-ui.com/docs/guides/styling).
- Use `drizzle-orm/bun-sqlite` with `bun:sqlite` for SQLite and `drizzle-orm/bun-sql` with Bun `SQL` for PostgreSQL. Keep dialect schemas and migration histories separate. Drizzle is the only permitted prerelease in the selected combination. [Bun SQLite](https://bun.sh/docs/api/sqlite), [Drizzle Bun SQL](https://orm.drizzle.team/docs/connect-bun-sql).
- Generate Hey API types and SDK from the checked-in OpenAPI contract; pass a request-specific client on the server. Generated TypeScript does not validate untrusted runtime data. [Hey API fetch client](https://heyapi.dev/docs/openapi/typescript/clients/fetch).

## Top mistakes

- Plain `let` and a one-time `const doubled = count * 2` do not make reactive Svelte state; use `$state` and `$derived`.
- A server load's returned object reaches the browser. Returning a private environment value or database client breaks the server boundary even when its import is in a server file.
- Kit 2 examples with `svelte.config.*`, implicit `$lib`, old `$env/*` or `$app/stores` need the Kit 3 APIs described in the routing reference.
- Panda's base/theme presets are explicit in this setup. Runtime string construction such as a color token assembled from input is not a reliable CSS extraction strategy; map input to literal variants.
- Ark value-change callbacks receive detail objects, not DOM events. A Select value is `string[]`; a Dialog open value is boolean.
- Synchronous Bun SQLite transactions cannot span `await`. Use the transaction handle for every operation; throw to roll back. PostgreSQL transactions are asynchronous and reserve one connection through the driver.
- Do not pass the old Drizzle `schema` configuration to this RC's relational API; use `defineRelations` and the `relations` option. Generating migrations and applying them are separate operations.
- Do not treat the generated SDK envelope as the payload or assume every HTTP error has a JSON body. Check the response and error path before using data.

## Check

Use the actual tools: install with Bun, sync Kit types before generators, run Panda/Hey API generation, type-check with warnings rejected, build, lint and check formatting. [Integration](references/integration.md) gives runnable commands and isolated database/browser checks. The reusable [check script](scripts/check.sh) takes a project directory; it checks the selected pins and real tools, and `EVAL_REQUIRE_TESTS=1` also requires and runs the requested test suite.

## Routing

| Work being done | Read |
|---|---|
| Runtime scripts, strict TypeScript, unknown inputs, resource ownership | [Bun and TypeScript](references/bun-typescript.md) |
| Reactive state, component props, events, snippets, effects | [Svelte 5](references/svelte.md) |
| Vite/Kit setup, routes, server loads, forms, API handlers, secrets and errors | [SvelteKit 3](references/sveltekit.md) |
| Tokens, presets, recipes, static extraction, accessible controlled UI | [Panda and Ark](references/panda-ark.md) |
| SQLite/PostgreSQL schemas, queries, migrations, transactions and concurrency | [Drizzle](references/drizzle.md) |
| OpenAPI generation, typed SDK calls and API failures | [Hey API](references/hey-api.md) |
| End-to-end wiring, database isolation, build and validation commands | [Integration and testing](references/integration.md) |
| Reviewing a change for stale or unsafe patterns | [Anti-patterns](references/anti-patterns.md) |
| Exact releases, language mode and compatibility floors | [Versions](references/versions.md) |
