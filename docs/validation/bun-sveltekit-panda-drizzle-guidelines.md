# Bun/SvelteKit/Panda/Drizzle guide validation

The [current guide](../../.agents/skills/bun-sveltekit-panda-drizzle-guidelines/SKILL.md)
contains researched coding guidance and a concrete source project, beyond the
initial dependency/lint/format toolkit. Research snapshot: 2026-10-16; expansion
revision: 2026-10-17. Exact selected releases and mode constraints remain in the
[version table](../../.agents/skills/bun-sveltekit-panda-drizzle-guidelines/references/versions.md).
Primary API sources and admission records are in
[provenance](../../.agents/skills/bun-sveltekit-panda-drizzle-guidelines/PROVENANCE.md).

## Current source-backed coverage

| Area | Coding guidance |
|---|---|
| Bun and TypeScript | Runtime/dependency discipline, strict external boundaries, resource ownership and cleanup |
| Svelte 5 | Reactive and derived state, component/snippet/callback contracts, effects and SSR boundaries |
| SvelteKit 3 | Vite configuration/import migration, server/private boundaries, request-scoped loads, actions and errors |
| Panda 2 and Ark Svelte | Code generation and CSS layers, tokens/recipes/static extraction, controlled state and accessible composition |
| Drizzle and databases | Dialect-specific schemas/drivers, version-matched migration artifacts, transactions, constraints and concurrency |
| Hey API | Generated contract/SDK discipline, request-scoped clients and response envelopes, runtime validation and failures |
| Integration and review | Dependency-ordered builds, isolated database verification, browser checks and actionable anti-patterns |

Known-correct idioms remain useful reference material even when a baseline model
already implements them. The current scope therefore admits primary-source-backed
coding guidance without requiring a measured baseline failure. It does not use
an absence of benchmark regression as a reason to remove whole subject areas.

## Current validation

The committed example project under `assets/examples/` is the source of truth for
instructional code blocks. Block/source matching, type/build/runtime execution
and source review support the expanded guide. No new controlled coding-model
benchmark has been run for this expansion. The earlier 72-run scores below must
not be attributed to the current reference content.

The following checks passed on the expanded example source with the exact pins
in its package manifest, using Bun 1.4.3, bundled SQLite 3.53.4 and Chromium
156.0.8078.4 (Playwright 1.64.1). PostgreSQL used a fresh isolated 18.6 service;
`REQUIRE_POSTGRES=1` and `TEST_DATABASE_URL` ensured its test actually ran.

| Command | Observed result |
|---|---|
| `bun run generate` | Kit types, Panda output and the actual Hey API SDK generated successfully |
| `bun run db:generate` | Separate SQLite and PostgreSQL rc5 migration artifacts generated |
| `bun run build` | Strict Svelte/TypeScript check: 0 errors, 0 warnings; production SSR/client build and official Bun adapter output passed |
| `bun run lint` | ESLint passed with `--max-warnings 0` |
| `bun run format:check` | Prettier passed on handwritten source |
| `REQUIRE_POSTGRES=1 TEST_DATABASE_URL=… bun test` | 3 tests passed, 0 failed, 9 expectations, no PostgreSQL skip |
| `bun run test:browser` | Production hydration, dialog validation/Escape/focus restoration, Panda computed padding, server-form failure/success, API 400/404/health responses and private sentinel absence from SSR/page HTML passed |

The SQLite test applies migrations twice, checks foreign-key enforcement and
rollback, then closes/reopens its temporary file to check persistence. The
PostgreSQL test applies migrations twice, runs five concurrent atomic increments
and verifies rollback. The SDK test uses generated code for success, malformed
payload, bodyless HTTP failure and network failure. These are concrete paths,
not a claim that every database operation or deployment mode is covered.

The initial validation setup used a shared dependency symlink that misplaced
Kit's generated compiler configuration; a private copy of the same pinned
dependencies fixed it without changing source imports or weakening type checks.
Execution also exposed and fixed a dialog event typing/lint issue and the Bun
adapter's HTTPS-origin default during local HTTP form POSTs. The example now sets
an explicit canonical origin and keeps CSRF checks enabled. Production builds
must configure their actual public origin as documented in the guide.

Browser coverage does not include focus containment, navigation data or a scan
of every served client asset. The sentinel assertion checks SSR/page HTML only.
No-op scripts, successful compilation or a source review alone were not counted
as runtime verification.

All 15 marked instructional blocks match the committed example sources exactly,
with no unresolved or unmarked code blocks. Provenance, token-budget and isolated
skill-creator validation pass. Repository manual hooks pass for tracked and new
files; local links resolve and the public export has no private workspace paths.

## Historical experiment: initial tooling-only version

The original PR revision retained mostly selected dependency declarations,
ESLint/Prettier assets and a common check script after over-pruning the actual
coding guidance. The following comparison evaluated that minimal version only.
It is retained as history, not validation of the expanded guide.

All 12 tasks used without-skill and with-instructions conditions, with three fresh
valid repeats each: 72 calls, zero invalid/reused final runs and zero unverifiable
assertions. Primary rates average each task's repeats, then weight tasks equally.
Pooled assertion counts are secondary. Differences are instructions minus control.

| Scope | With instructions | Without skill | Mean task difference | Pooled passed/scored |
|---|---:|---:|---:|---|
| Development, 8 tasks | 100.0000% | 74.3981% | +25.6019 points | 231/231 vs 172/231 |
| Held out, 4 tasks | 99.1667% | 74.2929% | +24.8737 points | 119/120 vs 89/120 |
| Overall, 12 tasks | 99.7222% | 74.3631% | +25.3591 points | 350/351 vs 261/351 |

The runner was gpt-6.1-sol/high via Codex app-server 0.163.0. Conditions shared exact
prompts, fixtures, frozen assertions, toolchain, permissions and limits, with
fresh isolated non-root workspaces/databases, 1,800s coding/600s postcheck limits,
and explicit on-demand developer instructions. Independent graders excluded
injected guidance/read bodies. Automatic native activation was not measured.

Generic lint/format/version gates were frozen defaults even where task prompts
did not explicitly request them. All 36 controls failed lint and format, and 18
selected-version assertions failed. Thus the gains primarily demonstrate meeting
that tooling contract. They do not show that the expanded coding advice improves
model performance or that unguided functional behavior was generally wrong.

E10 guided repeat 1 retained its unchanged primary 9/10 score for an overconstrained
API-ordering assertion. Its append-only API did not accept caller-selected
positions; a second SQLite connection correctly demonstrated ORDER BY and stable
records. The prompt did not expressly require positions/reordering. No Integrity
penalty or sorting-defect claim is made, and no assertion was rewritten to change
the score. Three repeats and four holdout tasks are descriptive, not a general
correctness guarantee.

The old initial baseline was 58/77 assertions; its first guided iteration 77/77.
Each of three independent removals (Top mistakes, integration, anti-patterns)
preserved 231/231 over 24 runs per condition, and the jointly pruned sample passed
77/77 in eight fresh development runs. Those tests could not measure the value of
reference knowledge that the tasks/model did not need to consult. The user asked
for that substantive researched knowledge to be restored.

Five earlier host capture failures stayed invalid/ungraded: four dangling-link
copy failures and one literal-U+0085 JSONL framing failure. Fresh retries supplied
missing slots after a host-only capture fix. No invalid was converted to a score.
The final 72 calls reported 58,409,548 provider tokens; all 198 historical coding
attempts reported 164,032,182 tokens with reuse deduplicated. Costs for other
contexts are outside that ledger, and provider dollar cost is unknown.

## Artifact and validation limits

The historical frozen/delivered skill is preserved unchanged outside the
repository. The expanded guide now has different operative content and example
assets; neither its old full-tree nor its nine-file fingerprint describes this
revision. Public provenance omits private paths/transcripts but retains primary
citations, admissions and the distinction between old measurements and current
checks. No .skill archive helper was available for the historical delivery.

Native automatic activation and expanded-guide model-effectiveness are untested.
The reported current checks cover only their concrete source/examples and paths;
unexecuted deployment modes or alternate database drivers are not silently
claimed verified. Future release changes require source/compatibility rechecks.
