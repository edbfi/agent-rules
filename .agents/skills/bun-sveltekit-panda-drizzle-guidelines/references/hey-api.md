# Hey API typed clients

## Generate the contract

Keep the OpenAPI document and generator configuration as inputs, and run `openapi-ts` to recreate output. Give operations stable `operationId` values so generated call names are intentional. Treat generated files as derived code: change the schema or generator options, regenerate, and review the diff. Do not fix a generated result type by hand because regeneration will discard the fix. [Generator configuration](https://heyapi.dev/docs/openapi/typescript/get-started), [pinned package](https://unpkg.com/@hey-api/openapi-ts@0.99.0/README.md).

The generator's default type/SDK plugins do not mean that every application has a configured transport. Configure `@hey-api/client-fetch` explicitly when the generated SDK needs Fetch, together with `@hey-api/typescript` and `@hey-api/sdk`. Run Kit sync first when this project extends a generated Kit tsconfig. [Fetch client](https://heyapi.dev/docs/openapi/typescript/clients/fetch), [pinned plugin definitions](https://unpkg.com/@hey-api/openapi-ts@0.99.0/dist/index.d.mts).

The runnable generator configuration is explicit about the fetch transport.

<!-- example: openapi-ts.config.ts -->
```ts
import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './openapi.json',
  output: './src/lib/api',
  plugins: ['@hey-api/typescript', '@hey-api/client-fetch', '@hey-api/sdk'],
});
```

## Request scoped clients and envelopes

In a server load or endpoint, create a client with its base URL, request-aware fetch and permitted request-specific headers, then pass that client to the SDK call. Do not mutate a process-wide generated client with one user's Authorization header; concurrent requests share the module. Forward credentials only to the intended origin. Browser-visible configuration contains no private API key. [Client configuration](https://heyapi.dev/docs/openapi/typescript/clients/fetch).

Keep the generated envelope and the payload distinct. In the normal non-throwing object response style, inspect `response`, `error` and `data` before using the payload. Handle HTTP status even when an error response has no JSON body; an undefined error payload is not evidence of a successful request. Network/abort failures may lack a Response. If choosing `throwOnError`, use a coherent catch policy instead of mixing throwing and envelope assumptions in the same helper. [Fetch error handling and response styles](https://heyapi.dev/docs/openapi/typescript/clients/fetch).

Provide useful separate empty and unavailable states: a successful empty array is not an upstream outage. If the UI can render partial data, return a safe status with the remaining data; otherwise use the appropriate Kit error status. Do not leak a private upstream URL or stack trace into page data.

## Validation and failures

Generated TypeScript types describe the contract at compile time. They do not prove that JSON received at runtime follows it. Validate untrusted responses at the boundary when correctness depends on their shape, using an explicit validator plugin or the client's request/response validator hooks; keep validation failure distinct from an HTTP or network failure. Do not cast arbitrary JSON into the generated type as a substitute. [Runtime validation](https://heyapi.dev/docs/openapi/typescript/validators).

Test the actual generated SDK against a local fixture: success data, empty data, non-2xx with and without a body, and request cancellation/network rejection where the application relies on it. Regenerate twice and compare output when reproducibility matters. The compact example's generated directory is ignored and recreated from its checked-in schema/config; it is not a hand-maintained library.

The boundary helper below passes its own client to the generated operation, handles a bodyless 503, and explicitly narrows the actual payload before returning it. The [fixture test](../assets/examples/hey-api.test.ts) exercises success, malformed payload, HTTP failure and network rejection.

<!-- example: src/lib/health.ts -->
```ts
import { createClient } from './api/client/index.ts';
import { getHealth } from './api/sdk.gen.ts';
import type { Health } from './api/types.gen.ts';

export type HealthResult =
  { ok: true; status: string } | { ok: false; message: string };

function isHealth(value: unknown): value is Health {
  return (
    typeof value === 'object' &&
    value !== null &&
    'status' in value &&
    typeof value.status === 'string'
  );
}

export async function loadHealth(
  baseUrl: string,
  fetcher: typeof fetch,
): Promise<HealthResult> {
  const client = createClient({ baseUrl, fetch: fetcher });
  try {
    const result = await getHealth({ client, throwOnError: false });
    if (!result.response?.ok || result.error || !isHealth(result.data)) {
      return { ok: false, message: 'The health service is unavailable.' };
    }
    return { ok: true, status: result.data.status };
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return { ok: false, message: 'The request was cancelled.' };
    }
    return { ok: false, message: 'The health service could not be reached.' };
  }
}
```
