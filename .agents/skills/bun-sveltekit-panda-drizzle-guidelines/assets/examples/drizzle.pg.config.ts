import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  dialect: 'postgresql',
  schema: './src/lib/server/pg-schema.ts',
  out: './migrations/postgresql',
  dbCredentials: {
    url:
      process.env.TEST_DATABASE_URL ??
      'postgres://guide:guide@postgres:5432/guide',
  },
});
