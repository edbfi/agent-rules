import { integer, pgTable, text } from 'drizzle-orm/pg-core';

export const counters = pgTable('counters', {
  key: text('key').primaryKey(),
  value: integer('value').notNull().default(0),
});
