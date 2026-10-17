"""End-to-end tests for scripts/sync.py against throwaway git repositories (offline)."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import cast

REPO = Path(__file__).resolve().parents[1]
SYNC = REPO / "scripts" / "sync.py"
BUILDER = REPO / ".agents" / "skills" / "coding-guidelines-builder"


def builder_fixtures() -> tuple[Callable[..., Path], Callable[..., Path]]:
    """The builder's own valid-pack generators (tests/test_packs.py of the installed builder)."""
    spec = importlib.util.spec_from_file_location("builder_test_packs", BUILDER / "tests" / "test_packs.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["builder_test_packs"] = module  # dataclasses resolve string annotations through sys.modules
    spec.loader.exec_module(module)
    return cast("Callable[..., Path]", module.build_component), cast("Callable[..., Path]", module.build_stack)


build_component, build_stack = builder_fixtures()
GIT_ENV = {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com", "GIT_COMMITTER_NAME": "Test",
           "GIT_COMMITTER_EMAIL": "test@example.com", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
RULE = '---\ntype: "agent_requested"\ndescription: "Commit conventions"\n---\n# Commit conventions\n\nUse Conventional Commits.\n'
GH_STUB = """#!/bin/sh
echo "$@" >> "$GH_LOG"
case "$1 $2" in
  "pr list") cat "$GH_OPEN" 2>/dev/null || true ;;
  "pr create") echo "https://github.com/edbfi/demo/pull/1"; echo "https://github.com/edbfi/demo/pull/1" > "$GH_OPEN" ;;
esac
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(content, encoding="utf-8")


class SyncFixture(unittest.TestCase):
    # Fixtures are built in __init__ rather than setUp: the repo types under Python 3.11, which
    # has no typing.override, and basedpyright recommended mode flags an unmarked setUp override.
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base: Path = Path(temp.name)
        self.env: dict[str, str] = {**os.environ, **GIT_ENV}
        self.root: Path = self.base / "agent-rules"
        self.consumer: Path = self.base / "checkouts" / "edbfi" / "demo"
        self.other: Path = self.base / "other-clone"
        stub = self.base / "bin" / "gh"
        write(stub, GH_STUB)
        stub.chmod(0o755)
        self.env.update({"PATH": f"{stub.parent}{os.pathsep}{self.env['PATH']}", "GH_LOG": str(self.base / "gh.log"),
                         "GH_OPEN": str(self.base / "gh-open"), "AGENT_RULES_ROOT": str(self.root)})
        self.make_source()
        self.make_consumer()

    # --- helpers ---

    def git(self, cwd: Path, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=self.env, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout.strip()

    def bare(self, name: str) -> Path:
        path = self.base / "remotes" / "edbfi" / f"{name}.git"
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = self.git(path.parent, "init", "--quiet", "--bare", "--initial-branch=main", path.name)
        return path

    def manifest(self, guidelines: list[str], rules: list[str]) -> None:
        listed = ", ".join(json.dumps(g) for g in guidelines)
        names = ", ".join(json.dumps(r) for r in rules)
        write(self.root / "manifest.toml", "schema = 2\n\n[defaults]\npublish = false\n\n[[repo]]\n"
              + f'slug = "edbfi/demo"\npublish = true\nguidelines = [{listed}]\nrules = [{names}]\n')

    def publish_source(self, message: str) -> None:
        index = subprocess.run([sys.executable, "-B", str(BUILDER / "scripts" / "packs.py"), "index", str(self.root / "guidelines")],
                               capture_output=True, text=True, check=False)
        self.assertEqual(0, index.returncode, index.stdout + index.stderr)
        _ = self.git(self.root, "add", "-A")
        _ = self.git(self.root, "commit", "--quiet", "-m", message)
        _ = self.git(self.root, "push", "--quiet", "origin", "HEAD:main")

    def make_source(self) -> None:
        origin = self.bare("agent-rules")
        self.root.mkdir()
        _ = self.git(self.root, "init", "--quiet", "--initial-branch=main")
        _ = self.git(self.root, "remote", "add", "origin", str(origin))
        (self.root / ".agents" / "skills").mkdir(parents=True)
        (self.root / ".agents" / "skills" / "coding-guidelines-builder").symlink_to(BUILDER)
        _ = build_component(self.root / "guidelines")
        _ = build_stack(self.root / "guidelines")
        write(self.root / "rules" / "commit.md", RULE)
        write(self.root / "scripts" / "legacy-rules.json", json.dumps({"rules": {}}))
        self.manifest(["stacks/bun-zod"], ["commit"])
        self.publish_source("source")

    def make_consumer(self) -> None:
        origin = self.bare("demo")
        seed = self.base / "seed"
        _ = self.git(self.base, "clone", "--quiet", str(origin), str(seed))
        write(seed / "README.md", "# Demo\n")
        _ = self.git(seed, "add", "-A")
        _ = self.git(seed, "commit", "--quiet", "-m", "init")
        _ = self.git(seed, "push", "--quiet", "origin", "HEAD:main")
        self.consumer.parent.mkdir(parents=True)
        _ = self.git(self.base, "clone", "--quiet", str(origin), str(self.consumer))
        _ = self.git(self.base, "clone", "--quiet", str(origin), str(self.other))

    def sync(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(SYNC), *args, "--repo", "edbfi/demo", "--checkout", str(self.consumer)],
                              capture_output=True, text=True, env=self.env, check=False)

    def assert_exit(self, code: int, result: subprocess.CompletedProcess[str]) -> str:
        self.assertEqual(code, result.returncode, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def branch(self) -> str:
        """The sync branch prepared for the current agent-rules commit."""
        source = self.git(self.root, "rev-parse", "--short=7", "HEAD")
        names = self.git(self.consumer, "branch", "--list", f"chore/sync-agent-guidelines-{source}-*", "--format=%(refname:short)")
        self.assertEqual(1, len(names.splitlines()), f"expected one sync branch for {source}, found {names!r}")
        return names

    def show(self, branch: str, path: str) -> str:
        return self.git(self.consumer, "show", f"{branch}:{path}")

    def merge(self, branch: str) -> None:
        """Land a prepared sync branch on the consumer's main, as merging its PR would."""
        _ = self.git(self.consumer, "push", "--quiet", "origin", f"{branch}:main")
        _ = self.git(self.other, "pull", "--quiet", "--ff-only", "origin", "main")

    def consumer_commit(self, path: str, content: str | None) -> None:
        target = self.other / path
        if content is None:
            target.unlink()
        else:
            write(target, content)
        _ = self.git(self.other, "add", "-A")
        _ = self.git(self.other, "commit", "--quiet", "-m", f"edit {path}")
        _ = self.git(self.other, "push", "--quiet", "origin", "HEAD:main")


class Delivery(SyncFixture):
    def test_plan_writes_nothing_and_apply_prepares_a_branch(self) -> None:
        out = self.assert_exit(0, self.sync("plan"))
        self.assertIn("deliver stacks/bun-zod:", out)
        self.assertEqual("", self.git(self.consumer, "status", "--porcelain"))
        self.assertEqual("", self.git(self.consumer, "branch", "--list", "chore/*"))
        out = self.assert_exit(0, self.sync("apply"))
        self.assertIn("prepared branch", out)
        branch = self.branch()
        files = self.git(self.consumer, "ls-tree", "-r", "--name-only", branch).splitlines()
        self.assertIn(".agents/guidelines/stacks/bun-zod/README.md", files)
        self.assertIn(".agents/guidelines/components/zod-4/practices/core-api.md", files)
        self.assertIn(".agents/rules/commit.md", files)
        self.assertIn(".agents/guidelines/INDEX.md", files)
        self.assertFalse([f for f in files if "/examples/" in f])
        pointer = self.show(branch, ".agents/rules/guidelines-stacks-bun-zod.md")
        self.assertIn('description: "Bun and Zod coding guidelines (researched 2026-10-17)"', pointer)
        self.assertIn("| Zod | 4.1.0 | `.agents/guidelines/components/zod-4/README.md` |", pointer)
        lock = cast("dict[str, dict[str, object]]", json.loads(self.show(branch, ".agents/guidelines/guidelines-lock.json")))
        self.assertEqual(self.git(self.root, "rev-parse", "HEAD"), lock["source"]["commit"])
        self.assertIn(".agents/rules/commit.md", lock["files"])
        message = self.git(self.consumer, "log", "-1", "--format=%B", branch)
        self.assertTrue(message.startswith("chore(agents): sync coding guidelines from agent-rules@"))
        self.assertIn("Signed-off-by: Test <test@example.com>", message)
        self.assertEqual("", self.git(self.consumer, "status", "--porcelain"))
        self.assertEqual("main", self.git(self.consumer, "branch", "--show-current"))

    def test_merged_delivery_is_up_to_date_and_updates_flow(self) -> None:
        _ = self.assert_exit(0, self.sync("apply"))
        self.merge(self.branch())
        self.assertIn("up to date", self.assert_exit(0, self.sync("apply")))
        practices = self.root / "guidelines/components/zod-4/practices/core-api.md"
        _ = practices.write_text(practices.read_text(encoding="utf-8").replace("It is the current", "It is the documented"), encoding="utf-8")
        self.publish_source("update zod")
        out = self.assert_exit(0, self.sync("apply"))
        self.assertIn("1 update", out)
        self.assertIn("It is the documented", self.show(self.branch(), ".agents/guidelines/components/zod-4/practices/core-api.md"))

    def test_apply_fetches_before_planning(self) -> None:
        self.consumer_commit("NOTES.md", "new upstream file\n")
        _ = self.assert_exit(0, self.sync("apply"))
        self.assertIn("NOTES.md", self.git(self.consumer, "ls-tree", "--name-only", self.branch()))

    def test_retire_removes_unmodified_files(self) -> None:
        _ = self.assert_exit(0, self.sync("apply"))
        self.merge(self.branch())
        self.manifest([], [])
        self.publish_source("retire")
        _ = self.assert_exit(0, self.sync("apply"))
        files = self.git(self.consumer, "ls-tree", "-r", "--name-only", self.branch())
        self.assertNotIn(".agents/", files)


class Conflicts(SyncFixture):
    def test_local_edit_holds_back_its_set_and_sets_sharing_a_changed_component(self) -> None:
        self.manifest(["stacks/bun-zod", "components/zod-4"], ["commit"])
        self.publish_source("both")
        _ = self.assert_exit(0, self.sync("apply"))
        self.merge(self.branch())
        self.consumer_commit(".agents/guidelines/stacks/bun-zod/decisions.md", "# Decisions\n\nOur own.\n")
        practices = self.root / "guidelines/components/zod-4/practices/core-api.md"
        _ = practices.write_text(practices.read_text(encoding="utf-8").replace("It is the current", "It is the documented"), encoding="utf-8")
        write(self.root / "rules/commit.md", RULE.replace("Use Conventional", "Always use Conventional"))
        self.publish_source("change component and rule")
        out = self.assert_exit(1, self.sync("apply"))
        self.assertIn("CONFLICT stacks/bun-zod", out)
        self.assertIn("decisions.md edited or removed locally", out)
        self.assertIn("CONFLICT components/zod-4", out)
        self.assertIn("shares a component pack with a held-back set", out)
        branch = self.branch()
        self.assertIn("Always use", self.show(branch, ".agents/rules/commit.md"))
        self.assertIn("It is the current", self.show(branch, ".agents/guidelines/components/zod-4/practices/core-api.md"))
        self.assertEqual("# Decisions\n\nOur own.", self.show(branch, ".agents/guidelines/stacks/bun-zod/decisions.md"))

    def test_conflict_only_run_exits_1(self) -> None:
        self.consumer_commit(".agents/rules/commit.md", "# Mine\n")
        self.manifest([], ["commit"])
        self.publish_source("rule only")
        out = self.assert_exit(1, self.sync("apply"))
        self.assertIn("already exists and is not managed by sync", out)
        self.assertIn("nothing to apply", out)

    def test_foreign_index_and_unmanaged_files(self) -> None:
        self.consumer_commit(".agents/guidelines/INDEX.md", "# Our index\n")
        out = self.assert_exit(1, self.sync("plan"))
        self.assertIn("INDEX.md was edited locally or is not managed by sync", out)
        self.consumer_commit(".agents/guidelines/INDEX.md", None)
        _ = self.assert_exit(0, self.sync("apply"))
        self.merge(self.branch())
        self.consumer_commit(".agents/guidelines/stacks/bun-zod/notes.md", "# Notes\n")
        self.assertIn("unmanaged (kept): .agents/guidelines/stacks/bun-zod/notes.md", self.assert_exit(0, self.sync("plan")))

    def test_invalid_lock_and_unsafe_paths_stop(self) -> None:
        self.consumer_commit(".agents/guidelines/guidelines-lock.json", '{"schema": 9}\n')
        self.assertIn("is not a schema 1 lock", self.assert_exit(2, self.sync("plan")))
        lock = {"schema": 1, "source": {"repo": "edbfi/agent-rules", "commit": "x"}, "entries": {},
                "files": {"../outside.md": {"source_sha256": "a", "installed_sha256": "b"}}}
        self.consumer_commit(".agents/guidelines/guidelines-lock.json", json.dumps(lock) + "\n")
        self.assertIn("refusing managed path", self.assert_exit(2, self.sync("plan")))
        self.consumer_commit(".agents/guidelines/guidelines-lock.json", None)
        outside = self.base / "outside"
        outside.mkdir()
        shutil.rmtree(self.other / ".agents/guidelines", ignore_errors=True)
        (self.other / ".agents/guidelines").symlink_to(outside)
        _ = self.git(self.other, "add", "-A")
        _ = self.git(self.other, "commit", "--quiet", "-m", "symlink")
        _ = self.git(self.other, "push", "--quiet", "origin", "HEAD:main")
        self.assertIn("refusing to follow a symlink", self.assert_exit(2, self.sync("apply")))
        self.assertEqual([], list(outside.iterdir()))


class Legacy(SyncFixture):
    def legacy(self, content: str, replaced_by: str | None) -> None:
        digest = subprocess.run(["sha256sum"], input=RULE, capture_output=True, text=True, check=True).stdout.split()[0]
        write(self.root / "scripts/legacy-rules.json", json.dumps({"rules": {"old.md": {"sha256": [digest], "replaced_by": replaced_by}}}))
        self.publish_source("legacy table")
        self.consumer_commit(".agents/rules/old.md", content)

    def test_known_legacy_rule_is_replaced(self) -> None:
        self.legacy(RULE, "stacks/bun-zod")
        out = self.assert_exit(0, self.sync("apply"))
        self.assertIn("legacy: remove .agents/rules/old.md", out)
        self.assertNotIn(".agents/rules/old.md", self.git(self.consumer, "ls-tree", "-r", "--name-only", self.branch()))

    def test_modified_or_unreplaced_legacy_rules_are_kept(self) -> None:
        self.legacy(RULE + "local edit\n", "stacks/bun-zod")
        self.assertIn("modified legacy rule", self.assert_exit(1, self.sync("plan")))
        self.legacy(RULE, None)
        self.assertIn("no replacement delivered yet", self.assert_exit(0, self.sync("plan")))


class Environment(SyncFixture):
    def test_prettier_consumers_get_an_ignore_line(self) -> None:
        self.consumer_commit(".prettierrc", "{}\n")
        _ = self.assert_exit(0, self.sync("apply"))
        self.assertEqual(".agents/guidelines/", self.show(self.branch(), ".prettierignore"))

    def test_identity_local_state_and_source_guards(self) -> None:
        _ = self.git(self.consumer, "remote", "set-url", "--push", "origin", "git@github.com:edbfi/elsewhere.git")
        self.assertIn("is not edbfi/demo", self.assert_exit(2, self.sync("plan")))
        _ = self.git(self.consumer, "remote", "set-url", "--push", "origin", self.git(self.consumer, "remote", "get-url", "origin"))
        hook = self.consumer / ".git" / "hooks" / "pre-commit"
        write(hook, "#!/bin/sh\n# agent-rules-leak-guard\n")
        self.assertIn("retired agent-rules leak guard", self.assert_exit(2, self.sync("plan")))
        hook.unlink()
        write(self.consumer / ".git" / "info" / "exclude", ".agents/rules/\n")
        self.assertIn("still excludes .agents/rules/", self.assert_exit(2, self.sync("plan")))
        write(self.consumer / ".git" / "info" / "exclude", "")
        write(self.root / "scratch.txt", "dirty\n")
        self.assertIn("uncommitted changes", self.assert_exit(2, self.sync("apply")))
        (self.root / "scratch.txt").unlink()
        _ = self.git(self.root, "commit", "--quiet", "--allow-empty", "-m", "unpublished")
        self.assertIn("not on origin/main", self.assert_exit(2, self.sync("apply")))

    def test_prepared_branch_is_resumable_and_published_once(self) -> None:
        _ = self.assert_exit(0, self.sync("apply"))
        branch = self.branch()
        self.assertIn("already prepared", self.assert_exit(0, self.sync("apply")))
        out = self.assert_exit(0, self.sync("apply", "--pr"))
        self.assertIn(f"pushed {branch}", out)
        self.assertIn("opened https://github.com/edbfi/demo/pull/1", out)
        self.assertIn("pull request already open", self.assert_exit(0, self.sync("apply", "--pr")))
        log = (self.base / "gh.log").read_text(encoding="utf-8")
        self.assertEqual(1, log.count("pr create"))
        self.assertIn("--repo edbfi/demo", log)
        _ = self.git(self.consumer, "branch", "-D", branch)
        _ = self.git(self.consumer, "push", "--quiet", "origin", f":{branch}")
        _ = self.git(self.consumer, "branch", branch, "main")
        self.assertIn("already exists with different content", self.assert_exit(1, self.sync("apply")))

    def test_usage_errors(self) -> None:
        result = subprocess.run([sys.executable, "-B", str(SYNC), "plan"], capture_output=True, text=True, env=self.env, check=False)
        self.assertEqual(2, result.returncode)
        result = subprocess.run([sys.executable, "-B", str(SYNC), "plan", "--repo", "edbfi/unknown"],
                                capture_output=True, text=True, env=self.env, check=False)
        self.assertIn("not an opted-in target", result.stderr)
        _ = self.assert_exit(2, self.sync("plan", "--pr"))


if shutil.which("git") is None:  # pragma: no cover - the repository's own tooling requires git
    raise unittest.SkipTest("git is not available")

if __name__ == "__main__":
    _ = unittest.main()
