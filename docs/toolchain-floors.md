# Toolchain review before rule delivery

Dated inspection: 2026-09-12. Rule delivery changes guidance only; it must not
raise runtime/compiler floors or recreate lockfiles. Project requirements and
supported CI versions take precedence over generic examples in canonical rules.

- EasyHDR's inspected default branch pins Rust1.98.0.
- Obzorarr, Otpravkarr, Poyo Studio and Zondarr inspected root package manifests
  pin Bun1.4.2. This does not assert every transitive package/example is current.
- Wings-vpn declares Go1.26.0 and validates Go1.26.8/1.27.1. Its retained Go1.27
  guidance is not authorization to use features unavailable at its Go1.26 floor.
- Comradarr and Zimuarr are planning-stage projects. Do not invent an application,
  runtime data or dependency pins just to deliver rules.
- Arrsenal-of-scripts retains Python guidance; no root package manifest was found.

The prior inventory contained historical unreconciled floor warnings. Those are
not a current estate audit. Before any future prose/toolchain update, inspect the
specific consumer's actual supported versions and consult official documentation
for new package or language claims. Syntax/content CI and byte equality do not
prove such claims. Preserve the canonical rules during delivery migration and
review substantive rule improvements separately.

## SvelteKit 3 inspection

Dated inspection: 2026-10-02 (consumer manifests re-read on 2026-10-03 at the
SvelteKit 3 migration bases). `svelte5-sveltekit-app` now targets SvelteKit 3
with `@sveltejs/adapter-bun`; its floors, from the npm registry and the
SvelteKit 3 migration guide:

- Node 22.17 or newer (`@sveltejs/kit` 3.0.0 engines; the `sv` codemod wants
  22.18). Vitest and Playwright use whatever Node is on `PATH`.
- Bun 1.4.0 or newer (`@sveltejs/adapter-bun` 1.0.0 engines). The production
  build and server run on Bun.
- TypeScript `^6.0.0` is an optional Kit peer. Consumers stay on TypeScript 6
  or newer.
- Svelte 5.57.1 or newer, Vite `^8.0.12` and `@sveltejs/vite-plugin-svelte`
  `^7.0.0` (Kit peers).
- `@sveltejs/kit` 3.0.x and `@sveltejs/adapter-bun` 1.0.x. `sveltekit-superforms`
  3 is a prerelease (`3.0.0-next.N`, pinned exactly) until a stable 3.x exists.

Consumers inspected (root package manifests): Obzorarr, Otpravkarr, Poyo
Studio and Setun pin `packageManager` Bun1.4.2 (Poyo Studio also declares
`engines.bun` 1.4.2). Zondarr pins Bun1.4.2 at the root and in `frontend/`.
Setun is a new consumer of `svelte5-sveltekit-app` and `python-3_14-core`.

These floors take effect in each app's own SvelteKit 3 change. Delivering the
rule does not raise a consumer's floors or recreate its lockfile; each app's
change does that itself. Comradarr and Zimuarr remain planning-stage consumers
with no root package manifest: do not invent an application, runtime data or
dependency pins to deliver the rule.
