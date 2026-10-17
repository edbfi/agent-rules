# Drizzle 1 RC with Bun SQLite and PostgreSQL 18

## Choose the driver and schema

Use `Database` from `bun:sqlite` with `drizzle({ client })` from `drizzle-orm/bun-sqlite` for the synchronous SQLite connection. Use `SQL` from `bun` with `drizzle({ client })` from `drizzle-orm/bun-sql` for PostgreSQL. These are different drivers with different transaction execution contracts; do not interchange imports because both run on Bun. [Drizzle Bun SQLite](https://orm.drizzle.team/docs/connect-bun-sqlite), [Bun SQL](https://orm.drizzle.team/docs/connect-bun-sql).

Define SQLite tables with `sqliteTable` and SQLite columns; define PostgreSQL tables with `pgTable` and PostgreSQL columns. Keep uniqueness, foreign keys, non-null requirements and checks in the schema/migration, not only in a request validator. Use a composite unique key for a business rule such as one registration per event/email, then target that key in an upsert. A `select` followed by an unconditional `insert` is a race. [Drizzle constraints](https://orm.drizzle.team/docs/indexes-constraints), [upserts](https://orm.drizzle.team/docs/guides/upsert).

Use inferred insert/select types instead of duplicating schema interfaces. Handle no returned row explicitly. Build predicates with `eq`, `and` and bound values; interpolate data through the SQL tag rather than concatenating it into a raw SQL string. Never omit a mutation's intended `where` clause. [Select](https://orm.drizzle.team/docs/select), [update](https://orm.drizzle.team/docs/update).

This RC's relational configuration uses `defineRelations(...)` and `drizzle({ client, relations })`; the old `schema` option is not part of this version's DrizzleConfig. The basic query builder works without relational configuration. Verify relation examples against the selected RC declarations rather than stable 0.x documentation. [Pinned relation API](https://unpkg.com/drizzle-orm@1.0.0-rc.5-5935859/relations.d.ts), [pinned DrizzleConfig](https://unpkg.com/drizzle-orm@1.0.0-rc.5-5935859/utils.d.ts).

A concrete SQLite schema makes nullability and referential integrity part of storage, and exports types inferred from those definitions.

<!-- example: src/lib/server/sqlite-schema.ts -->
```ts
import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';

export const notebooks = sqliteTable('notebooks', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
});

export const notes = sqliteTable('notes', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  notebookId: integer('notebook_id')
    .notNull()
    .references(() => notebooks.id),
  title: text('title').notNull(),
});

export type Note = typeof notes.$inferSelect;
export type NewNote = typeof notes.$inferInsert;
```

The SQLite [schema](../assets/examples/src/lib/server/sqlite-schema.ts) defines the actual foreign key; its connection factory configures enforcement before any work and returns explicit client ownership.

<!-- example: src/lib/server/sqlite.ts -->
```ts
import { Database } from 'bun:sqlite';
import { drizzle } from 'drizzle-orm/bun-sqlite';

export function openNotes(path: string) {
  const client = new Database(path, { create: true, strict: true });
  try {
    client.run('PRAGMA foreign_keys = ON');
    client.run('PRAGMA journal_mode = WAL');
    client.run('PRAGMA busy_timeout = 2500');
    return { client, db: drizzle({ client }) };
  } catch (error) {
    client.close();
    throw error;
  }
}
```

## Migrations are deployment artifacts

Keep ORM and Kit on the matched selected RC, not an older `rc` dist-tag. A Kit config uses `dialect: 'sqlite'` or `'postgresql'`, schema path, output directory and connection URL. `driver: 'bun-sqlite'` is not the dialect selection. Generate and review SQL with `drizzle-kit generate`; apply generated migrations through the matching runtime migrator or the deployment command. Keep independent directories/configs for the two dialects. This RC uses timestamped migration subdirectories containing `migration.sql`; its runtime reader rejects the older `meta/_journal.json` layout. Keep generator output together rather than borrowing a 0.x migration history. [Kit generate](https://orm.drizzle.team/docs/drizzle-kit-generate), [pinned config union](https://unpkg.com/drizzle-kit@1.0.0-rc.5-5935859/index.d.ts).

A dialect-specific Kit configuration generates the reviewed migration history; the PostgreSQL companion changes both the dialect and schema/output paths.

<!-- example: drizzle.sqlite.config.ts -->
```ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  dialect: 'sqlite',
  schema: './src/lib/server/sqlite-schema.ts',
  out: './migrations/sqlite',
  dbCredentials: { url: './example.sqlite' },
});
```

The runtime migrators are `drizzle-orm/bun-sqlite/migrator` and `drizzle-orm/bun-sql/migrator`; `migrationsFolder` is their option. Do not generate migrations at request time. Treat a successful second application as an idempotency test, then verify behavior against the migrated schema. Avoid replacing deployment history with ad hoc CREATE TABLE statements or pushing schema changes directly into a shared production database. [Runtime migrations](https://orm.drizzle.team/docs/migrations), [pinned RC migration reader](https://unpkg.com/drizzle-orm@1.0.0-rc.5-5935859/migrator.js).

## Transactions constraints and concurrency

For `bun:sqlite`, configure foreign-key enforcement on every connection before transactions. For a file-backed application database, WAL can improve reader/writer coexistence, but it still has a single writer; it does not remove lock contention. Keep write transactions short, configure a bounded busy timeout if appropriate, and do network work before entering the transaction. Never use an async callback with this synchronous driver's transaction API. Exceptions roll back; a caught error followed by a normal return can commit partial work. [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html), [WAL](https://www.sqlite.org/wal.html), [Bun SQLite transactions](https://bun.sh/docs/api/sqlite).

For PostgreSQL use `await db.transaction(async (tx) => ...)`, and issue every operation through `tx`, not the outer pool. Throw to roll back; close the test pool in a finally block. Use database constraints and atomic updates such as increment/decrement expressions to avoid lost updates. Use row locks or serializable isolation when a business invariant spans multiple rows; handle/retry serialization failures at the entire transaction boundary with a bounded policy. A transaction at the default isolation level is not a universal cure for read-modify-write races. [Drizzle transactions](https://orm.drizzle.team/docs/transactions), [PostgreSQL isolation](https://www.postgresql.org/docs/18/transaction-iso.html).

Test both success and rollback with actual drivers. SQLite tests should verify migrated data after reopening a file, foreign-key failure, and atomic rollback. PostgreSQL tests need a fresh owned database/service, repeated migration application, concurrent updates and rollback. In-memory SQLite is useful for unit tests but cannot prove file persistence or PostgreSQL behavior.

The [SQLite migration config](../assets/examples/drizzle.sqlite.config.ts) and [PostgreSQL migration config](../assets/examples/drizzle.pg.config.ts) use separate schemas/output. Run `bun run db:generate` to generate their local example migrations (review and commit migration history when adopting this as an application). The complete [SQLite test](../assets/examples/sqlite.test.ts) verifies migration, rollback, invalid foreign key and reopening; the [PostgreSQL test](../assets/examples/postgres.test.ts) verifies atomic concurrent increments and rollback using an isolated service. Their transaction callbacks use the correct driver handle.

This complete PostgreSQL test is executable with the owned-service invocation in [integration](integration.md). It demonstrates the asynchronous driver, runtime migrator, atomic update expressions and exception rollback together; an omitted service URL is an explicit skip, not a pass.

<!-- example: postgres.test.ts -->
```ts
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
```
