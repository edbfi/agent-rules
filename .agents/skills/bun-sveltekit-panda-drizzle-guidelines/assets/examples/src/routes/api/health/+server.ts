import type { RequestHandler } from './$types';

export const GET = (() =>
  Response.json({ status: 'ok' })) satisfies RequestHandler;
