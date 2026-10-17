# Anti-patterns

| Wrong | Why | Right | Grep |
|---|---|---|---|
| Unpinned/ranged TypeScript | The compiler constraint is exact | Selected exact declaration and lockfile | `"typescript"\s*:\s*"[~^]` |
| Kit configuration in svelte.config.* | Kit 3 rejects that file | Configuration in the Vite sveltekit plugin | `svelte\.config\.[jt]s` |
| Implicit $lib, $app/stores or old environment module | The selected Kit APIs changed | #lib imports, $app/state, declared $app/env/private/public | `\$lib\|\$app/stores\|\$env/` |
| Plain local counter or one-time derived const | It does not track reactive changes | $state and $derived | `let count = [0-9]` |
| Mutating parent-owned component state | It obscures ownership and can cause runtime warnings | Callback props or an intentional bindable contract | `ownership_invalid_mutation` |
| Returning a private environment value from a server load | Returned page data reaches the browser | Return only the safe data/capability actually needed | `return.*(?:API_KEY\|SECRET\|TOKEN)` |
| Panda token/class assembled from runtime strings | Static extraction cannot reliably discover arbitrary runtime combinations | Finite literal recipe variants or constrained CSS variables | `css\(.*\x60` |
| Treating Ark Select value as a scalar DOM event | The Svelte API uses string[] and change details | Read details.value or bind the array | `onValueChange.*target\.value` |
| Drizzle schema option copied from stable 0.x examples | The selected RC uses relations configuration | defineRelations and relations, or plain query builder | `drizzle\(.*schema` |
| Async callback in synchronous SQLite transaction | An await does not preserve this driver's synchronous transaction | Keep callback synchronous; use PG async transactions separately | `transaction\(async` in SQLite modules |
| Read-then-insert to enforce uniqueness | Concurrent requests can both pass the read | Database unique constraint and atomic upsert | `onConflictDoUpdate` absence is review context, not proof |
| Generated SDK payload assumed to be the full call result | The default response is an envelope | Inspect status/error/data and handle bodyless errors | `await.*(?:get\|list).*\.map` |
| Hand-editing generated SDK/styling files | Regeneration discards the change | Edit schema/config/source and regenerate | `auto-generated` |
| Missing real lint/formatter configuration | Build success does not verify source rules or formatting | Install selected tools, configure them and run their actual commands | `eslint\.config` absence requires an inventory check |

These searches are review aids, not proof of a bug: inspect scope and the selected API. In particular, async transactions are correct for PostgreSQL, and the presence of an SDK method name or generated file is not itself a failure. Follow the focused references for the rationale and executable examples.
