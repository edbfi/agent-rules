import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  dialect: 'sqlite',
  schema: './src/lib/server/sqlite-schema.ts',
  out: './migrations/sqlite',
  dbCredentials: { url: './example.sqlite' },
});
