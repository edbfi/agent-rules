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
