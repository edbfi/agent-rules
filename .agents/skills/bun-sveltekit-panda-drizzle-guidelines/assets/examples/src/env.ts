import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
  API_KEY: { schema: (value: string | undefined) => value },
});
