<script lang="ts">
  import { Dialog } from '@ark-ui/svelte/dialog';

  let { oncreate }: { oncreate: (title: string) => void } = $props();
  let open = $state(false);
  let title = $state('');
  let message = $state('');

  function submit() {
    const trimmed = title.trim();
    if (!trimmed) {
      message = 'Enter a title.';
      return;
    }
    oncreate(trimmed);
    title = '';
    message = '';
    open = false;
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger>Add local note</Dialog.Trigger>
  <Dialog.Backdrop />
  <Dialog.Positioner>
    <Dialog.Content>
      <Dialog.Title>Add a note</Dialog.Title>
      <Dialog.Description>The title is required.</Dialog.Description>
      <form
        onsubmit={(event) => {
          event.preventDefault();
          submit();
        }}
      >
        <label
          >Title <input
            bind:value={title}
            aria-invalid={Boolean(message)}
          /></label
        >
        <p role="status">{message}</p>
        <button type="submit">Create</button>
        <Dialog.CloseTrigger type="button">Cancel</Dialog.CloseTrigger>
      </form>
    </Dialog.Content>
  </Dialog.Positioner>
</Dialog.Root>
