# Versions

| Component | Target | Mode or compatibility constraint |
|---|---|---|
| Bun / bundled SQLite | 1.4.3 / 3.53.4 | Official adapter requires Bun >=1.4.0; SQLite is verified from that runtime |
| TypeScript / Bun types | 6.0.3 exactly / 1.4.3 | Kit mode: target/module esnext, moduleResolution bundler, verbatimModuleSyntax, isolatedModules; no additional browser/OS minimum |
| Svelte / Kit / Svelte Vite plugin / Vite / official Bun adapter | 5.57.2 / 3.1.0 / 7.3.1 / 8.3.4 / 1.0.0 | Kit peers: Svelte ^5.57.1, TS ^6, plugin ^7, Vite ^8.0.12 |
| Panda dev / Vite / base / panda presets | 2.2.0, all four | Panda Vite requires Vite >=6 |
| Ark UI for Svelte | 5.24.3 | Svelte >=5.20 |
| Drizzle ORM / Kit | 1.0.0-rc.5-5935859, both | Latest matched published RC; canonical rc tag still points at rc.4; sole prerelease exception |
| PostgreSQL | 18.6 stable | Isolated service; PostgreSQL 19 RC is outside stable policy |
| Hey API openapi-ts | 0.99.0 | Selected stable release |
| ESLint / @eslint/js / typescript-eslint / eslint-plugin-svelte | 10.13.0 / 10.0.1 / 8.71.2 / 3.23.1 | TS parser >=4.8.4 <6.1.0; Svelte plugin accepts ESLint 10 and Svelte 5 |
| Prettier / prettier-plugin-svelte | 3.9.10 / 4.1.1 | Svelte plugin requires Prettier 3 and Svelte 5 |
| svelte-check / Playwright | 4.7.7 / 1.64.1 | Verification tools; browser fixture uses paired Chromium |

- **Research date:** 2026-10-16
