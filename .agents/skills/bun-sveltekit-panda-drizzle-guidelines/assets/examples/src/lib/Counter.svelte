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
