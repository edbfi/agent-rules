import { SQL } from 'bun';
import { expect, test } from 'bun:test';
import { randomUUID } from 'node:crypto';
import { eq, sql } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/bun-sql';
import { migrate } from 'drizzle-orm/bun-sql/migrator';
import { counters } from './src/lib/server/pg-schema.ts';

const url = process.env.TEST_DATABASE_URL;
if (process.env.REQUIRE_POSTGRES === '1' && !url) {
  throw new Error('TEST_DATABASE_URL is required');
}

test.skipIf(!url)(
  'PostgreSQL migration, atomic concurrent updates and rollback',
  async () => {
    if (!url) throw new Error('TEST_DATABASE_URL is required');
    const client = new SQL(url);
    const db = drizzle({ client });
    const key = randomUUID();
    try {
      await migrate(db, { migrationsFolder: './migrations/postgresql' });
      await migrate(db, { migrationsFolder: './migrations/postgresql' });
      await db.insert(counters).values({ key, value: 0 });
      await Promise.all(
        Array.from({ length: 5 }, () =>
          db.transaction(async (tx) => {
            await tx
              .update(counters)
              .set({ value: sql`${counters.value} + 1` })
              .where(eq(counters.key, key));
          }),
        ),
      );
      await expect(
        db.transaction(async (tx) => {
          await tx
            .update(counters)
            .set({ value: 99 })
            .where(eq(counters.key, key));
          throw new Error('abort transaction');
        }),
      ).rejects.toThrow('abort transaction');
      const [result] = await db
        .select()
        .from(counters)
        .where(eq(counters.key, key));
      expect(result?.value).toBe(5);
    } finally {
      try {
        await db.delete(counters).where(eq(counters.key, key));
      } finally {
        await client.close();
      }
    }
  },
);
