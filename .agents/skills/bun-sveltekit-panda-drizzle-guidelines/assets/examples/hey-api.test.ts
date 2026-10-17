import { expect, test } from 'bun:test';
import { loadHealth } from './src/lib/health.ts';

test('generated SDK success, bodyless HTTP failure and network failure', async () => {
  let mode: 'ok' | 'http-error' | 'invalid-json' = 'ok';
  const server = Bun.serve({
    hostname: '127.0.0.1',
    port: 0,
    fetch: () =>
      mode === 'http-error'
        ? new Response(null, { status: 503 })
        : Response.json({ status: mode === 'invalid-json' ? 42 : 'ok' }),
  });
  try {
    expect(await loadHealth(server.url.toString(), fetch)).toEqual({
      ok: true,
      status: 'ok',
    });
    mode = 'invalid-json';
    expect((await loadHealth(server.url.toString(), fetch)).ok).toBe(false);
    mode = 'http-error';
    expect((await loadHealth(server.url.toString(), fetch)).ok).toBe(false);
    const offline: typeof fetch = Object.assign(
      async () => {
        throw new TypeError('offline');
      },
      { preconnect: fetch.preconnect },
    );
    expect((await loadHealth(server.url.toString(), offline)).ok).toBe(false);
  } finally {
    await server.stop(true);
  }
});
