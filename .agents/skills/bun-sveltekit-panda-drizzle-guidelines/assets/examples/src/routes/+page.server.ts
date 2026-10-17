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
