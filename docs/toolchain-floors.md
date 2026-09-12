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
