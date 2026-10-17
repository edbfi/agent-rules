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
