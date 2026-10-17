---
name: bun-sveltekit-panda-drizzle-guidelines
description: Use when writing, extending, reviewing, fixing, or setting up code in a Bun, TypeScript, SvelteKit, Panda CSS, Ark UI, Drizzle and Hey API project. Apply to any coding task in this stack, including component-only repairs and database work, even when the request does not name a framework. Covers the selected toolchain, exact dependency choices, and executable lint/format verification; excludes non-coding questions and unrelated projects using only one component.
---

# Bun SvelteKit Panda Drizzle guidelines

Deliver the working behavior together with its local validation tools and selected dependency declarations. Small component repairs and database projects still need the lint, formatting and exact TypeScript dependency gates.

## Decisions

Use Bun, the official `@sveltejs/adapter-bun`, Panda development/Vite/base/theme packages, Ark UI for Svelte, Drizzle ORM/Kit, Bun's bundled SQLite, PostgreSQL and Hey API. The selected releases and compatibility floors are in `references/versions.md`; merge only dependencies the project needs from `assets/package.json`.

Use ESLint with TypeScript/Svelte rules and Prettier with its Svelte plugin. Biome is outside this verified Svelte tooling setup. `assets/eslint.config.js`, `assets/.prettierrc.json` and `assets/.prettierignore` are reusable defaults; merge them into existing configuration and adjust generated-output paths to the project.

## Top mistakes

## Check

Run `sh scripts/check.sh PROJECT_DIRECTORY` before finishing, using this skill's script path. It runs the same dependency, build, warnings-as-errors lint and formatter gates used to verify these guidelines. Set `EVAL_REQUIRE_TESTS=1` when the task asks for tests, so the gate also verifies and runs that suite.

## Routing

| When the task involves | Read |
|---|---|
| Choosing package releases, TypeScript mode or database/runtime versions | `references/versions.md` |
