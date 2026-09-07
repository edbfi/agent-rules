"""Exercise sync against disposable Git repositories, never real consumers."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.canonical = self.root / "canonical"
        (self.canonical / "bin").mkdir(parents=True)
        (self.canonical / "rules").mkdir()
        shutil.copy2(SOURCE / "bin/sync", self.canonical / "bin/sync")
        (self.canonical / "rules/example.md").write_text("# Fixture guidance\n")
        self.consumer = self.root / "checkouts/directory-unrelated-to-slug"
        self.consumer.mkdir(parents=True)
        self.git("init", "-q")
        self.git("remote", "add", "origin", "git@github.com-fixture:fixture/consumer.git")
        self.rules = self.consumer / ".agents/rules"
        self.rules.mkdir(parents=True)
        (self.rules / "legacy.md").write_text("# Legacy fixture\n")
        self.git("add", ".agents/rules")
        self.git("-c", "user.name=CI Fixture", "-c", "user.email=ci@example.invalid",
                 "commit", "-q", "-s", "-m", "test: seed synthetic consumer")
        self.environment = os.environ.copy()
        self.environment.update(AGENT_RULES_ROOT=str(self.root / "checkouts"),
                                XDG_CONFIG_HOME=str(self.root / "config"),
                                AGENT_RULES_LOCAL_MANIFEST=str(self.root / "absent.toml"))

    def git(self, *arguments):
        return subprocess.check_output(["git", *arguments], cwd=self.consumer, text=True)

    def sync(self, *, publish=False, apply=False):
        (self.canonical / "manifest.toml").write_text(
            '[defaults]\npublish = false\nexclude_via = "info"\n'
            '[[repo]]\nslug = "fixture/consumer"\nrules = ["example"]\n'
            f'publish = {str(publish).lower()}\n')
        subprocess.run(["bash", str(self.canonical / "bin/sync"),
                        *(["--apply"] if apply else []), "fixture/consumer"],
                       env=self.environment, check=True, capture_output=True, text=True)

    def test_dry_run_does_not_write(self):
        before = self.git("status", "--porcelain")
        self.sync()
        self.assertEqual(self.git("status", "--porcelain"), before)
        self.assertTrue((self.rules / "legacy.md").is_file())
        self.assertFalse((self.rules / "example.md").exists())

    def test_local_only_sync_depublishes_prunes_excludes_and_verifies(self):
        self.sync(apply=True)
        self.assertFalse((self.rules / "legacy.md").exists())
        self.assertEqual((self.rules / "example.md").read_bytes(),
                         (self.canonical / "rules/example.md").read_bytes())
        self.assertIn("D\t.agents/rules/legacy.md", self.git("diff", "--cached", "--name-status"))
        self.assertEqual(self.git("check-ignore", ".agents/rules/example.md").strip(),
                         ".agents/rules/example.md")
        guard = self.consumer / ".git/hooks/pre-commit"
        self.assertIn("agent-rules-leak-guard", guard.read_text())
        before = self.git("status", "--porcelain")
        self.sync(apply=True)
        self.assertEqual(self.git("status", "--porcelain"), before)

    def test_publishing_restores_chained_hook_and_stages_only_rules(self):
        hook = self.consumer / ".git/hooks/pre-commit"
        original = "#!/bin/sh\nexit 0\n"
        hook.write_text(original)
        hook.chmod(0o755)
        self.sync(apply=True)
        self.sync(publish=True, apply=True)
        self.assertEqual(hook.read_text(), original)
        self.assertIn(".agents/rules/example.md", self.git("ls-files"))
        self.assertNotIn(".agents/rules/", (self.consumer / ".git/info/exclude").read_text())
        staged = self.git("diff", "--cached", "--name-only").splitlines()
        self.assertTrue(all(name.startswith(".agents/rules/") for name in staged))
