# Panda CSS 2 and Ark UI for Svelte

## Panda generation and presets

Configure `@pandacss/dev`, `@pandacss/vite`, `@pandacss/preset-base` and `@pandacss/preset-panda` together. Include both presets explicitly: base supplies utilities and conditions; the Panda preset supplies tokens. A stale README saying the base preset is automatic does not match this selected resolver. Put the framework-independent local preset after those defaults when extending the design system. [Panda 2 upgrade](https://panda-css.com/docs/get-started/upgrading-to-v2), [presets](https://panda-css.com/docs/customization/presets).

Run Kit sync, then `panda codegen`, before type-checking imports from styled-system. Import one application CSS file containing the Panda layer order `reset, base, tokens, recipes, utilities`; the Vite plugin processes that layer entry and watches relevant source. Do not add a second manual CSS watcher to the same pipeline. Generated runtime modules use `.js` here, paired with declarations; do not guess `.mjs`. [Vite setup](https://panda-css.com/docs/get-started/vite), [selected plugin](https://unpkg.com/@pandacss/vite@2.2.0/dist/index.js).

<!-- example: panda.config.ts -->
```ts
import { defineConfig } from '@pandacss/dev';
import base from '@pandacss/preset-base';
import panda from '@pandacss/preset-panda';
import local from './local.preset.ts';

export default defineConfig({
  presets: [base, panda, local],
  include: ['./src/**/*.{ts,svelte}'],
  outdir: 'styled-system',
  preflight: true,
});
```
<!-- example: src/app.css -->
```css
@layer reset, base, tokens, recipes, utilities;
```

## Tokens recipes and extraction

Use design tokens for repeated colors, spacing and typography. Put reusable system intent in semantic tokens, and extend the theme instead of replacing its defaults accidentally. Define local presets with `definePreset` from `@pandacss/dev`; they are plain styling configuration and should not import Svelte components or an application-only module. [Tokens](https://panda-css.com/docs/theming/tokens), [semantic tokens](https://panda-css.com/docs/theming/semantic-tokens).

Use `cva` for a component-local atomic recipe or `defineRecipe` in the theme for a generated recipe. Give variants finite named options, choose defaults, and expose their inferred variant types at component boundaries. Static extraction needs to see the possible style values: pass literal variants or map application input to known literals rather than constructing token names or class strings at runtime. For truly dynamic numeric or color values, use a constrained CSS custom property at the element and reference that variable from a static style. [Recipes](https://panda-css.com/docs/recipes/overview), [dynamic styling](https://panda-css.com/docs/guides/dynamic-styling).

This framework-independent preset defines the brand token and finite button variants; the [page](../assets/examples/src/routes/+page.svelte) calls the generated actionButton recipe using literal choices.

<!-- example: local.preset.ts -->
```ts
import { definePreset, defineRecipe } from '@pandacss/dev';

export default definePreset({
  name: 'guide',
  theme: {
    extend: {
      tokens: { colors: { brand: { value: '#0e7490' } } },
      recipes: {
        actionButton: defineRecipe({
          className: 'action-button',
          base: {
            borderRadius: 'md',
            fontWeight: 'semibold',
            _focusVisible: { outline: '2px solid', outlineOffset: '2px' },
          },
          variants: {
            appearance: {
              solid: { bg: 'brand', color: 'white' },
              subtle: { bg: 'gray.100', color: 'gray.900' },
            },
            size: { sm: { px: '2', py: '1' }, md: { px: '4', py: '2' } },
          },
          defaultVariants: { appearance: 'solid', size: 'md' },
        }),
      },
    },
  },
});
```

Keep every consuming source directory in `include`, including shared packages if they contain style calls. Verify recipe variants in a production build; a correct-looking development page does not prove its unvisited variants were extracted. Use `staticCss` only for a deliberate finite set that cannot be discovered from source, not as an unbounded replacement for extraction.

## Ark state and accessibility

Use the real Ark parts, including Dialog Trigger, Content, Title, Description and CloseTrigger. Keep an accessible name, use native buttons, label inputs, and preserve Ark keyboard/focus behavior. Ark is headless; styling a generic div to resemble a dialog does not supply its semantics. Target documented data attributes and Panda conditions such as open/disabled/focus-visible instead of replacing keyboard handlers. [Ark Dialog](https://ark-ui.com/docs/components/dialog), [styling](https://ark-ui.com/docs/guides/styling).

<!-- example: src/lib/EditDialog.svelte -->
```svelte
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
```

A controlled Dialog uses boolean `bind:open` or `onOpenChange(details)` with `details.open`; choose one source of truth. A Select uses a collection and `string[]` value even when single-select; `onValueChange` receives `details.value`, not `event.target.value`. Include its label, item text/indicator and hidden select when using native form integration. Do not invent a scalar value contract or mix a `defaultValue` expectation with controlled state. [Ark Select](https://ark-ui.com/docs/components/select), [pinned Svelte Select contract](https://unpkg.com/@ark-ui/svelte@5.24.3/dist/components/select/select-root.svelte).

Test opening, cancellation, Escape, focus containment/restoration and valid/invalid submission in a browser. Keep loading and disabled states exposed through the component's real props, and preserve visible focus styling.
