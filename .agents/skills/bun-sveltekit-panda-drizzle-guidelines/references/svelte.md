# Svelte 5 components

## Reactive state and derived values

Use `$state` for values that change and affect rendering. Plain local variables are ordinary JavaScript; a computed expression evaluated once does not follow later updates. Use `$derived(expression)` or `$derived.by(() => ...)` for synchronous pure computations. Reading state creates dependencies; destructuring a state proxy into ordinary locals creates snapshots of those properties. Keep the proxy access or derive the value you need. [State](https://svelte.dev/docs/svelte/$state), [derived values](https://svelte.dev/docs/svelte/$derived).

Objects and arrays created with `$state` are deeply reactive where Svelte can proxy them; mutating a class instance, Map or Date is not the same contract. Prefer immutable replacement or the appropriate Svelte reactive wrapper for such objects. Do not use an effect to copy one piece of state into a computed second value; that adds ordering and synchronization problems that a derived value avoids. [Svelte reactivity utilities](https://svelte.dev/docs/svelte/svelte-reactivity).

The component below derives from both local count and the current `step` prop. It does not snapshot `step` during initialization.

<!-- example: src/lib/Counter.svelte -->
```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    step = 1,
    onchange,
    children,
  }: {
    step?: number;
    onchange?: (count: number) => void;
    children?: Snippet<[number]>;
  } = $props();
  let count = $state(0);
  const scaled = $derived(count * step);

  function increment() {
    count += 1;
    onchange?.(count);
  }
</script>

<button onclick={increment}>Count {count}; scaled {scaled}</button>
{@render children?.(count)}
```

## Component contracts and events

Destructure typed props with `$props()`, including defaults. For editable local state seeded by a prop, explicitly choose creation-time state versus continued synchronization; do not accidentally promise both. Avoid mutating an object owned by a parent. Report changes with a callback prop, or expose two-way binding deliberately with `$bindable()` when the component contract calls for it. [Props and ownership](https://svelte.dev/docs/svelte/$props), [bindable props](https://svelte.dev/docs/svelte/$bindable).

Use DOM event properties such as `onclick` and `onsubmit`; call `event.preventDefault()` in the handler when needed. New component APIs use typed callback props rather than `createEventDispatcher`. Accept child content as a typed `Snippet`, render it with `{@render children?.(...)}`, and use keyed each blocks for lists with stable identities. Do not use array positions as identities for editable/reorderable records. [Svelte 5 event and snippet APIs](https://svelte.dev/docs/svelte/v5-migration-guide).

## Effects and server rendering

Use `$effect` to synchronize an external browser system, such as a subscription, with reactive values. Return a cleanup function that removes listeners, cancels work or destroys the subscription. Effects run in the browser, so they cannot populate data required for server-rendered HTML; use a Kit load function for that. Avoid an effect that updates a dependency it reads, and do not start asynchronous request races without cancellation or a stale-result guard. [Effects](https://svelte.dev/docs/svelte/$effect).

Access `window`, `document` and browser-only libraries inside a browser lifecycle boundary. Keep per-user mutable state out of module scope on the server because a module instance may serve multiple requests. A component runtime boundary does not replace server HTTP error handling; route failures belong to Kit's load/action/endpoint boundary. [Kit state management](https://svelte.dev/docs/kit/state-management).
