import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET = (({ params }) => {
  if (!/^[1-9]\d*$/.test(params.id)) error(400, 'Invalid note ID');
  // This endpoint demonstrates the HTTP boundary; database examples are separate.
  if (params.id !== '1') error(404, 'Note not found');
  return Response.json({ id: 1, title: 'A typed route' });
}) satisfies RequestHandler;
