import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import adapter from '@sveltejs/adapter-bun';
import pandacss from '@pandacss/vite';

export default defineConfig({
  plugins: [
    pandacss(),
    sveltekit({
      adapter: adapter(),
      paths: { origin: process.env.APP_ORIGIN ?? 'http://127.0.0.1:3000' },
    }),
  ],
});
