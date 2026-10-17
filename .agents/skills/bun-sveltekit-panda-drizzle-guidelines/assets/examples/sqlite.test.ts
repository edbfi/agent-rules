import { expect, test } from 'bun:test';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { migrate } from 'drizzle-orm/bun-sqlite/migrator';
import { openNotes } from './src/lib/server/sqlite.ts';
import { notebooks, notes } from './src/lib/server/sqlite-schema.ts';

test('SQLite migration, rollback, foreign keys and reopened file persistence', () => {
  const directory = mkdtempSync(join(tmpdir(), 'guide-notes-'));
  const path = join(directory, 'notes.sqlite');
  let store = openNotes(path);
  try {
    migrate(store.db, { migrationsFolder: './migrations/sqlite' });
    migrate(store.db, { migrationsFolder: './migrations/sqlite' });
    const [book] = store.db
      .insert(notebooks)
      .values({ title: 'Work' })
      .returning()
      .all();
    if (!book) throw new Error('Insert returned no notebook');
    store.db
      .insert(notes)
      .values({ notebookId: book.id, title: 'Keep this' })
      .run();
    expect(() =>
      store.db.transaction((tx) => {
        tx.insert(notes)
          .values({ notebookId: book.id, title: 'Rollback this' })
          .run();
        throw new Error('abort transaction');
      }),
    ).toThrow('abort transaction');
    expect(() =>
      store.db
        .insert(notes)
        .values({ notebookId: -1, title: 'Invalid parent' })
        .run(),
    ).toThrow();
    store.client.close();
    store = openNotes(path);
    expect(
      store.db
        .select()
        .from(notes)
        .all()
        .map((note) => note.title),
    ).toEqual(['Keep this']);
  } finally {
    store.client.close();
    rmSync(directory, { recursive: true, force: true });
  }
});
