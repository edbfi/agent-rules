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
