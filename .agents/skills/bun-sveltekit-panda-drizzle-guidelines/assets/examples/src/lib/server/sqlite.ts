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
