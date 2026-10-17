# SvelteKit 3, Vite 8 and the Bun adapter

## Kit 3 configuration and imports

Pass Kit configuration to the `sveltekit` Vite plugin. Kit 3 rejects `svelte.config.js` and `svelte.config.ts`. Register Panda before Kit; Kit includes the Svelte Vite plugin, so adding a separate `svelte()` call double-registers it. Use the official scoped Bun adapter. These are version-specific setup rules, not merely formatting preferences. [Kit 3 migration](https://svelte.dev/docs/kit/migrating-to-sveltekit-3), [selected Kit Vite implementation](https://unpkg.com/@sveltejs/kit@3.1.0/src/exports/vite/index.js).

<!-- example: vite.config.ts -->
```ts
import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import adapter from '@sveltejs/adapter-bun';
import pandacss from '@pandacss/vite';

export default defineConfig({
  plugins: [
    pandacss(),
    sveltekit({
      adapter: adapter(),
      paths: { origin: process.env.APP_ORIGIN ?? 'http://127.0.0.1:3000' },
    }),
  ],
});
```

Set the public origin deliberately for production. The example defaults `paths.origin` to its direct HTTP URL, `http://127.0.0.1:3000`; build a deployment with `APP_ORIGIN=https://your-app.example bun run build`. `APP_ORIGIN` is read by Vite at build time; changing only the server startup environment does not change the compiled canonical origin. For this direct example, open the exact configured scheme/host/port: `localhost` differs from `127.0.0.1`, and changing PORT requires a matching origin and rebuild. The official adapter otherwise assumes HTTPS when deriving an origin, so a direct local HTTP form can fail its CSRF check even when its route/action is correct. Keep origin checking enabled. Behind a proxy, trust forwarded protocol/host headers only when the proxy strips untrusted incoming values. [Pinned adapter origin handling](https://unpkg.com/@sveltejs/adapter-bun@1.0.0/src/handler.js), [Kit CSRF origin handling](https://unpkg.com/@sveltejs/kit@3.1.0/src/runtime/server/csrf.js).

Use package.json `imports` mapping `#lib/*` to `./src/lib/*` and import actual module extensions. The implicit `$lib` alias is removed in this configuration. Extend `$app/tsconfig`; run `svelte-kit sync` before tooling consumes its generated files. Use `$app/env` for environment flags and `$app/state` for current route state, rather than copying older `$app/environment` or `$app/stores` examples. Leave experimental remote functions disabled unless the application explicitly opts into that feature. [Kit 3 API changes](https://svelte.dev/docs/kit/migrating-to-sveltekit-3).

## Route and server boundaries

Use filesystem routes: `+page.svelte` for a page, `+layout.svelte` for its shared shell, `+page.server.ts` for private page loading/actions, `+page.ts` for universal loading, and `+server.ts` for HTTP method handlers. Dynamic directories such as `[id]` produce `params.id`; parse and validate it before querying. Import route-specific types from `./$types` instead of hand-maintaining parameter and action-result interfaces. [Routing](https://svelte.dev/docs/kit/routing), [generated types](https://svelte.dev/docs/kit/types).

A universal load may execute in the browser; it must not import database code or secrets. Keep those in `.server.ts` modules or a `server/` directory and call them from server loads, hooks, actions or endpoints. Return serializable public data, not a database connection or a private configuration object. Server-only imports prevent an unsafe import graph; they do not sanitize the object you deliberately return. [Server-only modules](https://svelte.dev/docs/kit/server-only-modules).

Define explicit environment variables through `defineEnvVars` in `src/env.ts`. `public` defaults to false; `static` defaults to false and means startup-time reading, not a fresh read for every request. Import each named private value from `$app/env/private`. Missing values fail validation unless their schema explicitly accepts undefined; an omitted schema allows an empty string but still requires a value. Return a safe capability boolean when the UI only needs availability. [Environment variables](https://svelte.dev/docs/kit/environment-variables), [pinned environment contract](https://unpkg.com/@sveltejs/kit@3.1.0/src/exports/env/public.d.ts).

The example makes an optional private key explicit and returns only its availability; no value is serialized.

<!-- example: src/env.ts -->
```ts
import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
  API_KEY: { schema: (value: string | undefined) => value },
});
```
## Loads actions and errors

Use a server load for initial database-backed page data and the load event's `fetch` for application-aware requests. Return useful empty states. Do not write to the database inside a GET load merely to initialize a form; mutations belong to actions or explicit HTTP endpoints. [Loading data](https://svelte.dev/docs/kit/load).

For HTML forms export `actions` from `+page.server.ts`; validate `FormData` values as strings before trimming or parsing them. Return `fail(400, { message, ...safeFields })` for a correctable user input error. Use one default action or named actions such as `?/create`, not both on the same page. A normal POST form works without JavaScript; add `use:enhance` for progressive enhancement when useful. [Form actions](https://svelte.dev/docs/kit/form-actions).

Use `Response.json(...)` from a `+server.ts` handler for JSON responses (the older Kit `json` helper is deprecated), `error(404, ...)` for a missing resource, and a route `+error.svelte` for expected page-level failures. Do not catch and replace every thrown Kit error/redirect with a generic 500. Treat unexpected exceptions through the server error hook/logging policy and send a safe message to the browser. A UI error boundary does not catch an exception thrown later by an arbitrary event handler. [Pinned response helper contract](https://unpkg.com/@sveltejs/kit@3.1.0/types/index.d.ts), [Kit errors](https://svelte.dev/docs/kit/errors), [Svelte boundaries](https://svelte.dev/docs/svelte/svelte-boundary).

A complete typed loader/action file validates input before returning safe data. This example validates and echoes a title; persistence examples are separate. Its [page](../assets/examples/src/routes/+page.svelte) renders both fail and success results.

<!-- example: src/routes/+page.server.ts -->
```ts
import { fail } from '@sveltejs/kit';
import { API_KEY } from '$app/env/private';
import type { Actions, PageServerLoad } from './$types';

export const load = (() => ({
  configured: Boolean(API_KEY?.trim()),
})) satisfies PageServerLoad;

export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    const title = data.get('title');
    if (
      typeof title !== 'string' ||
      !title.trim() ||
      title.trim().length > 120
    ) {
      return fail(400, { message: 'Enter a title of 1–120 characters.' });
    }
    return { created: title.trim() };
  },
} satisfies Actions;
```

A [parameterized endpoint](../assets/examples/src/routes/api/notes/[id]/+server.ts) demonstrates 400/404 status handling; the [error component](../assets/examples/src/routes/+error.svelte) renders the route error without exposing a stack.
