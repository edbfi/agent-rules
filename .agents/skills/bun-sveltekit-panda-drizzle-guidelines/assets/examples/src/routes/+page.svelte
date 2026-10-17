<script lang="ts">
  import Counter from '#lib/Counter.svelte';
  import EditDialog from '#lib/EditDialog.svelte';
  import { css } from '../../styled-system/css/index.js';
  import { actionButton } from '../../styled-system/recipes/index.js';
  import type { PageProps } from './$types';

  let { data, form }: PageProps = $props();
  let titles: string[] = $state([]);
</script>

<svelte:head><title>Stack examples</title></svelte:head>
<main class={css({ p: '4', maxWidth: '48rem', marginInline: 'auto' })}>
  <h1>Stack examples</h1>
  <p>Private service configured: {data.configured ? 'yes' : 'no'}</p>
  <Counter step={2}>
    {#snippet children(count)}<p>Current count: {count}</p>{/snippet}
  </Counter>
  <EditDialog oncreate={(title) => titles.push(title)} />
  <ul>
    {#each titles as title, index (index)}<li>{title}</li>{/each}
  </ul>
  <form method="POST">
    <label>Server title <input name="title" /></label>
    <button class={actionButton({ appearance: 'solid', size: 'md' })}
      >Validate on server</button
    >
    {#if form?.message}<p role="alert">{form.message}</p>{/if}
    {#if form?.created}<p>Validated: {form.created}</p>{/if}
  </form>
  <button class={actionButton({ appearance: 'subtle', size: 'sm' })}
    >Secondary action</button
  >
</main>
