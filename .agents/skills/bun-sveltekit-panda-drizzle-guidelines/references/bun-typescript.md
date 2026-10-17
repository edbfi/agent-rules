# Bun and TypeScript

## Runtime and dependency discipline

Use `bun install` to resolve dependencies and keep `bun.lock` with an application. CI uses `bun install --frozen-lockfile` so an accidental manifest change fails instead of silently updating the dependency graph. The compact example is a source template and generates its ignored lock locally; remove that ignore and retain `bun.lock` when adopting it as an application. Keep TypeScript pinned exactly; a matching installed version behind `^6.0.0` still permits a later compiler. Native addons and Node API compatibility must be checked on Bun itself, rather than inferred from a package's Node engine range. [Bun lockfiles](https://bun.sh/docs/pm/lockfile), [Bun compatibility](https://bun.sh/docs/runtime/nodejs-compat).

Run application commands through package scripts with `bun run build`, `bun run check` and `bun test`. Build with the official Bun adapter and start the generated output using `bun ./build`; Vite's preview server is a development inspection tool, not the selected production entrypoint. The adapter requires Bun at least 1.4. [Official adapter source](https://github.com/sveltejs/kit/tree/main/packages/adapter-bun).

## Strict TypeScript boundaries

Set `strict: true`, keep Kit's inherited module/bundler settings and generated route types, and import types with `import type`. Preserve `$app/types` when adding Bun ambient types; replacing the inherited list with only `bun` loses generated app declarations. Use the selected Bun types rather than declaring runtime globals yourself. [TypeScript strict mode](https://www.typescriptlang.org/tsconfig/strict.html), [Kit TypeScript](https://svelte.dev/docs/kit/types).

<!-- example: tsconfig.json -->
```json
{
  "extends": "$app/tsconfig",
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    "types": ["$app/types", "bun"]
  },
  "include": ["src/**/*.ts", "src/**/*.svelte", "*.ts", "*.js"],
  "exclude": ["node_modules", "build", ".svelte-kit", "styled-system"]
}
```

Use `unknown` at HTTP/JSON/storage boundaries and narrow it before reading fields. A type assertion or `satisfies` checks your static description; neither parses or validates an incoming object. Prefer a discriminated result such as a success/data branch and a failure/message branch to an object whose fields are all optional. Handle nullable database lookups and empty arrays explicitly. Narrow a caught error with `instanceof Error` before reading `.message`. [TypeScript narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html).

Use `satisfies` on route loaders, actions and literal configuration where retaining inference matters. Avoid exported `any`, non-null assertions for required environment values, and unchecked casts of `request.json()`. Validate configuration at startup and request values at the request boundary. Type-safe SQL result shapes still depend on correct migrations and actual stored data.

## Resource ownership

The code that creates an isolated database, server or client owns its cleanup. Use `try/finally` for SQLite `close()`, await a Bun SQL pool's `close()`, and stop test HTTP servers after the assertion. A process-wide database pool is appropriate for a long-running server; do not create an unbounded pool per request or close a shared pool after one request. Keep request-specific credentials out of mutable global clients. [Bun SQLite lifetime](https://bun.sh/docs/api/sqlite), [Bun SQL pooling](https://bun.sh/docs/api/sql).

Use parameter bindings or Drizzle predicates for data. Do not interpolate user strings into raw SQL, filesystem paths or shell commands. Tests should create their own temporary directory and delete the entire directory after connections close, including SQLite WAL sidecars.
