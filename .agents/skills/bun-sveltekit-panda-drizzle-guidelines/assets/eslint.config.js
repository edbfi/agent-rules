import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';

export default [
  {
    ignores: [
      'build/**',
      '.svelte-kit/**',
      'styled-system/**',
      'src/lib/api/**',
      'migrations/**',
    ],
  },
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs['flat/recommended'],
  {
    files: ['**/*.svelte'],
    languageOptions: { parserOptions: { parser: ts.parser } },
  },
  {
    languageOptions: {
      globals: { process: 'readonly', console: 'readonly', Bun: 'readonly' },
    },
  },
];
