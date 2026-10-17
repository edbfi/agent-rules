#!/bin/sh
# Portable stack gates. Run after coding in the selected, provisioned environment.
# Exit 1 = ordinary project failure; exit 78 = runner/toolchain infrastructure failure.
set -u
if [ "$#" -ne 1 ]; then
  echo 'INFRASTRUCTURE: usage: check.sh PROJECT_DIRECTORY' >&2
  exit 78
fi
cd "$1" || exit 78
command -v bun >/dev/null 2>&1 || { echo 'INFRASTRUCTURE: Bun unavailable' >&2; exit 78; }
[ "$(bun --version)" = '1.4.3' ] || { echo 'INFRASTRUCTURE: expected Bun 1.4.3' >&2; exit 78; }
status=0
run_gate() {
  label=$1
  shift
  echo "GATE_BEGIN: $label"
  "$@"
  result=$?
  echo "GATE_END: $label exit=$result"
  if [ "$result" -ne 0 ]; then status=1; fi
}
run_gate dependencies bun -e '
const fs = require("node:fs");
const expected = {"bun":"1.4.3","typescript":"6.0.3","svelte":"5.57.2","@sveltejs/kit":"3.1.0","@sveltejs/vite-plugin-svelte":"7.3.1","vite":"8.3.4","@sveltejs/adapter-bun":"1.0.0","@pandacss/dev":"2.2.0","@pandacss/vite":"2.2.0","@pandacss/preset-base":"2.2.0","@pandacss/preset-panda":"2.2.0","@ark-ui/svelte":"5.24.3","drizzle-orm":"1.0.0-rc.5-5935859","drizzle-kit":"1.0.0-rc.5-5935859","@hey-api/openapi-ts":"0.99.0","svelte-check":"4.7.7","eslint":"10.13.0","typescript-eslint":"8.71.2","eslint-plugin-svelte":"3.23.1","prettier":"3.9.10","prettier-plugin-svelte":"4.1.1","@eslint/js":"10.0.1","@types/bun":"1.4.3","playwright":"1.64.1"};
if (!fs.existsSync("package.json")) { console.error("project package.json is missing"); process.exit(1); }
const p = JSON.parse(fs.readFileSync("package.json", "utf8"));
const direct = {...p.dependencies, ...p.devDependencies};
let failed = false;
for (const [name, version] of Object.entries(expected)) {
  if (name === "bun" || !(name in direct)) continue;
  let installed;
  try { installed = JSON.parse(fs.readFileSync(`node_modules/${name}/package.json`, "utf8")).version; }
  catch { console.error(`${name}: direct dependency unavailable`); failed=true; continue; }
  if (installed !== version) { console.error(`${name}: installed ${installed}; selected compatible version ${version}`); failed=true; }
  if (name === "typescript" && direct[name] !== version) { console.error("typescript declaration must be exactly 6.0.3"); failed=true; }
}
if (!("typescript" in direct)) { console.error("exact TypeScript dependency missing"); failed=true; }
process.exit(failed ? 1 : 0);
'
# Application builds use their declared production build; small library/database
# projects may instead expose tsconfig.json and use the compiler without emitting.
if bun -e 'process.exit(require("./package.json").scripts?.build ? 0 : 1)' 2>/dev/null; then
  run_gate build bun run build
elif [ -f tsconfig.json ]; then
  run_gate build bun node_modules/typescript/bin/tsc --noEmit
elif [ -d src ]; then
  # Component-only requests need not be wrapped in an unrelated application.
  run_gate build bun node_modules/svelte-check/bin/svelte-check --no-tsconfig --fail-on-warnings
else
  run_gate build bun node_modules/typescript/bin/tsc --noEmit
fi
# Running the actual tools prevents a no-op project script from passing a gate.
run_gate lint bun node_modules/eslint/bin/eslint.js . --max-warnings 0
run_gate format bun node_modules/prettier/bin/prettier.cjs . --check
# Verification is not an invitation to demand unrequested test suites. The
# task/controller sets this only if the task explicitly asks for tests.
if [ "${EVAL_REQUIRE_TESTS:-0}" = 1 ]; then
  run_gate tests bun -e '
const fs = require("node:fs");
const p = require("./package.json");
const walk = d => fs.readdirSync(d,{withFileTypes:true}).some(e => {
 if (["node_modules",".git",".svelte-kit","build","dist","styled-system"].includes(e.name)) return false;
 const path = `${d}/${e.name}`;
 return e.isDirectory() ? walk(path) : /(?:test|spec)\.[cm]?[jt]sx?$/.test(e.name);
});
if (!p.scripts?.test || !walk(".")) { console.error("requested test suite is missing"); process.exit(1); }
const r = Bun.spawnSync(["bun","run","test"],{stdout:"inherit",stderr:"inherit"}); process.exit(r.exitCode);
'
fi
exit "$status"
