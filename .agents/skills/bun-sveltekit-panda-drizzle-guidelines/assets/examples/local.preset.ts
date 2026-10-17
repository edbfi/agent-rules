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
