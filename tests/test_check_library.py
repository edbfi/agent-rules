"""Tests for scripts/check-library.py against throwaway library roots (offline)."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import cast

REPO = Path(__file__).resolve().parents[1]
CHECK = REPO / "scripts" / "check-library.py"
BUILDER = REPO / ".agents" / "skills" / "coding-guidelines-builder"
RULE = '---\ntype: "agent_requested"\ndescription: "Commit conventions"\n---\n# Commit conventions\n\nUse Conventional Commits.\n'


def builder_fixtures() -> tuple[Callable[..., Path], Callable[..., Path]]:
    """The builder's own valid-pack generators (tests/test_packs.py of the installed builder)."""
    spec = importlib.util.spec_from_file_location("builder_test_packs", BUILDER / "tests" / "test_packs.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["builder_test_packs"] = module  # dataclasses resolve string annotations through sys.modules
    spec.loader.exec_module(module)
    return cast("Callable[..., Path]", module.build_component), cast("Callable[..., Path]", module.build_stack)


build_component, build_stack = builder_fixtures()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(content, encoding="utf-8")


class CheckLibrary(unittest.TestCase):
    # Fixtures are built in __init__ rather than setUp: the repo types under Python 3.11, which
    # has no typing.override, and basedpyright recommended mode flags an unmarked setUp override.
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root: Path = Path(temp.name)
        (self.root / ".agents" / "skills").mkdir(parents=True)
        (self.root / ".agents" / "skills" / "coding-guidelines-builder").symlink_to(BUILDER)
        (self.root / "guidelines").mkdir()
        self.manifest("repo = []\n")
        self.index()

    def manifest(self, repos: str) -> None:
        # A bare `repo = []` must precede [defaults]; after it, TOML would nest it inside that table.
        if repos.startswith("repo ="):
            write(self.root / "manifest.toml", f"schema = 2\n{repos}\n[defaults]\npublish = false\n")
        else:
            write(self.root / "manifest.toml", f"schema = 2\n\n[defaults]\npublish = false\n\n{repos}")

    def target(self, guidelines: list[str], rules: list[str], slug: str = "edbfi/demo") -> str:
        return (f'[[repo]]\nslug = "{slug}"\npublish = true\nguidelines = {json.dumps(guidelines)}\n'
                + f"rules = {json.dumps(rules)}\n")

    def index(self) -> None:
        result = subprocess.run([sys.executable, "-B", str(BUILDER / "scripts" / "packs.py"), "index", str(self.root / "guidelines")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def check(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(CHECK), *args], capture_output=True, text=True,
                              env={**os.environ, "AGENT_RULES_ROOT": str(self.root)}, check=False)

    def assert_problem(self, needle: str, *args: str) -> None:
        result = self.check(*args)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(needle, result.stdout + result.stderr)

    def test_empty_library_passes(self) -> None:
        result = self.check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Validated 0 rules, 0 packs", result.stdout)

    def test_valid_library_rules_and_targets_pass(self) -> None:
        _ = build_component(self.root / "guidelines")
        _ = build_stack(self.root / "guidelines")
        write(self.root / "rules" / "commit.md", RULE)
        self.manifest(self.target(["stacks/bun-zod"], ["commit"]) + "\n" + self.target([], [], "edbfi/retired"))
        self.index()
        result = self.check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Validated 1 rules, 2 packs", result.stdout)

    def test_manifest_rules(self) -> None:
        write(self.root / "rules" / "commit.md", RULE)
        cases = [
            ("repo = []\n[accepted]\n", "top-level keys must be schema, defaults and repo"),
            (self.target(["stacks/missing"], []), "unknown guidelines entry 'stacks/missing'"),
            (self.target([], ["absent"]), "unknown rule 'absent'"),
            (self.target([], [], "someone/else"), "slug must be edbfi/<repo>"),
            (self.target([], ["commit", "commit"]), "rules must be a list of distinct strings"),
            (self.target([], []) + self.target([], []), "duplicate slug"),
            (self.target([], []).replace("publish = true", "publish = false"), "publish must be true"),
        ]
        for repos, needle in cases:
            with self.subTest(needle=needle):
                self.manifest(repos)
                self.assert_problem(needle)
        write(self.root / "manifest.toml", "schema = 1\nrepo = []\n\n[defaults]\npublish = false\n")
        self.assert_problem("schema must be 2")

    def test_rule_shape_and_reserved_prefix(self) -> None:
        write(self.root / "rules" / "guidelines-x.md", RULE)
        self.assert_problem("reserved for generated pointer rules")
        (self.root / "rules" / "guidelines-x.md").unlink()
        write(self.root / "rules" / "bad.md", RULE.replace('type: "agent_requested"', 'type: "always"'))
        self.assert_problem("type must be one of")
        (self.root / "rules" / "bad.md").unlink()
        write(self.root / "rules" / ".gitkeep", "")
        self.assert_problem("filename must be lowercase <name>.md")

    def test_library_problems_fail(self) -> None:
        component = build_component(self.root / "guidelines")
        self.assert_problem("is out of date")
        self.index()
        self.assertEqual(0, self.check().returncode)
        write(component / "SKILL.md", "# No\n")
        self.assert_problem("a SKILL.md does not belong in the library")
        (component / "SKILL.md").unlink()
        write(component / "examples" / "src" / "good.ts", "export const ok = 2;\n")
        self.assert_problem("does not match examples/")

    def test_stale_packs(self) -> None:
        component = build_component(self.root / "guidelines")
        self.assertEqual(0, self.check("--stale").returncode)
        meta = cast("dict[str, object]", json.loads((component / "pack.json").read_text(encoding="utf-8")))
        meta["refresh_after"] = "2026-01-01"
        _ = (component / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        result = self.check("--stale")
        self.assertEqual(1, result.returncode)
        self.assertIn("stale: components/zod-4", result.stdout)
        self.assertEqual(2, self.check("--bogus").returncode)

    def test_missing_builder(self) -> None:
        (self.root / ".agents" / "skills" / "coding-guidelines-builder").unlink()
        self.assert_problem("coding-guidelines-builder is not installed; run: bunx skills add")


if __name__ == "__main__":
    _ = unittest.main()
