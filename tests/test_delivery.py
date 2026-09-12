"""Offline GitHub fixtures: never contact or modify real consumers."""
import base64
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("delivery", ROOT / ".github/scripts/delivery.py")
d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(d)
SHA = "a" * 40
BASE = "b" * 40


class GitHub:
    def __init__(self, files=None):
        self.files = files or {}
        self.writes = []
        self.base = BASE
        self.branch = []
        self.prs = []
        self.commit = None
        self.source_sha = SHA
        self.ci = "success"
        self.ci_runs = None
        self.mode = "100644"
        self.truncated = False

    def __call__(self, endpoint, payload=None, source=False):
        if endpoint == "user":
            return {"id": 326875205}
        if source:
            if "/branches/" in endpoint:
                return {"commit": {"sha": self.source_sha}}
            if "/actions/" in endpoint:
                return {"workflow_runs": self.ci_runs if self.ci_runs is not None else [
                    {"head_sha": SHA, "head_branch": "main", "event": "push",
                     "status": "completed", "conclusion": self.ci}]}
            return {"id": 1343246959, "default_branch": "main"}
        if payload is not None:
            self.writes.append((endpoint, payload))
            if endpoint.endswith("/git/commits"):
                self.commit = copy.deepcopy(payload)
                return {"sha": "head"}
            if endpoint.endswith("/git/refs"):
                self.branch = [{"ref": payload["ref"], "object": {"sha": "head"}}]
                return {}
            if endpoint.endswith("/pulls"):
                return {"html_url": "https://github.com/edbfi/example/pull/1"}
            return {"sha": "new-tree" if endpoint.endswith("/git/trees") else "new-blob"}
        if "/branches/" in endpoint:
            return {"commit": {"sha": self.base}}
        if "/git/commits/head" in endpoint:
            return {**self.commit, "tree": {"sha": self.commit["tree"]},
                    "parents": [{"sha": p} for p in self.commit["parents"]],
                    "message": self.commit["message"].rstrip("\n")}
        if "/git/commits/" in endpoint:
            return {"tree": {"sha": "base-tree"}}
        if "/git/trees/" in endpoint:
            return {"truncated": self.truncated, "tree": [
                {"path": p, "mode": self.mode, "type": "blob", "sha": p}
                for p in self.files]}
        if "/git/blobs/" in endpoint:
            return {"encoding": "base64", "content": base64.b64encode(
                self.files[endpoint.split("/git/blobs/", 1)[1]]).decode()}
        if "/git/matching-refs/" in endpoint:
            return self.branch
        if "/pulls?" in endpoint:
            return self.prs
        return {"id": 7, "full_name": "edbfi/example", "default_branch": "main", "archived": False, "private": False}


class Delivery(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "rules").mkdir()
        (self.root / "rules/core.md").write_bytes(b"new\n")
        self.write_manifest()

    def write_manifest(self, slug="edbfi/example", extra="", rules='["core"]'):
        (self.root / "manifest.toml").write_text(
            '[defaults]\npublish = false\n[[repo]]\nslug = "' + slug
            + '"\npublish = true\nrules = ' + rules + '\n' + extra
            + '\n[accepted]\ncore = ["' + d.digest(b"old\n") + '"]\n')

    def plan(self, gh):
        return d.build_plan("edbfi/example", SHA, self.root, gh)[0]

    def publish(self, plan, gh):
        with patch.object(d, "canonical_sha", return_value=SHA):
            return d.publish(plan, self.root, gh)

    def test_noop_never_writes(self):
        gh = GitHub({".agents/rules/core.md": b"new\n"})
        self.assertEqual(self.publish(self.plan(gh), gh)["result"], "no-op")
        self.assertEqual(gh.writes, [])

    def test_add_generates_signed_pr_without_force_or_default_write(self):
        gh = GitHub()
        plan, diff = d.build_plan("edbfi/example", SHA, self.root, gh)
        self.assertIn("+new", diff)
        self.assertEqual(self.publish(plan, gh)["result"], "created")
        refs = [v for e, v in gh.writes if e.endswith("/git/refs")]
        self.assertEqual(refs[0]["ref"], "refs/heads/chore/agent-rules-" + SHA[:12])
        self.assertIn("Signed-off-by: edbfi", gh.commit["message"])
        self.assertEqual(gh.commit["author"], d.IDENTITY)
        self.assertFalse(any("force" in v for _, v in gh.writes))

    def test_update_preserves_custom_files(self):
        gh = GitHub({".agents/rules/core.md": b"old\n", ".agents/rules/custom.md": b"custom\n"})
        self.publish(self.plan(gh), gh)
        tree = next(v for e, v in gh.writes if e.endswith("/git/trees"))
        self.assertEqual(tree["base_tree"], "base-tree")
        self.assertEqual([e["path"] for e in tree["tree"]], [".agents/rules/core.md"])

    def test_explicit_rename_removes_only_matching_obsolete_bytes(self):
        self.write_manifest(extra='[repo.remove]\n"old-core.md" = "' + d.digest(b"old\n") + '"\n')
        gh = GitHub({".agents/rules/old-core.md": b"old\n"})
        plan = self.plan(gh)
        self.assertEqual(len(plan["changes"]), 2)
        self.assertIsNone(plan["changes"][1]["content"])
        gh.files[".agents/rules/old-core.md"] = b"custom\n"
        with self.assertRaisesRegex(ValueError, "unreviewed edits"):
            self.plan(gh)

    def test_consumer_edits_rejected(self):
        with self.assertRaisesRegex(ValueError, "unreviewed edits"):
            self.plan(GitHub({".agents/rules/core.md": b"custom\n"}))

    def test_owner_and_excluded_targets(self):
        for slug in ["other/example", "edbfi/cccp-ps", "edbfi/autoscan", "edbfi/../example"]:
            with self.subTest(slug=slug):
                self.write_manifest(slug)
                with self.assertRaises(ValueError):
                    self.plan(GitHub())

    def test_invalid_and_duplicate_rules(self):
        for rules in ['["../core"]', '["core", "core"]']:
            self.write_manifest(rules=rules)
            with self.assertRaises(ValueError):
                self.plan(GitHub())

    def test_duplicate_targets(self):
        f = self.root / "manifest.toml"
        f.write_text(f.read_text() + '\n[[repo]]\nslug="edbfi/example"\npublish=true\nrules=["core"]\n')
        with self.assertRaisesRegex(ValueError, "Duplicate target"):
            self.plan(GitHub())

    def test_symlink_and_truncated_tree(self):
        gh = GitHub({".agents/rules/core.md": b"new\n"})
        gh.mode = "120000"
        with self.assertRaisesRegex(ValueError, "Unsafe managed"):
            self.plan(gh)
        gh.truncated = True
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.plan(gh)
        f = self.root / "rules/core.md"
        f.unlink()
        f.symlink_to(self.root / "manifest.toml")
        with self.assertRaisesRegex(ValueError, "unsafe rule"):
            self.plan(GitHub())

    def test_stale_base_source_ci_and_tampered_plan(self):
        for mutation in ["base", "source", "ci", "plan"]:
            gh = GitHub()
            plan = self.plan(gh)
            if mutation == "base":
                gh.base = "c" * 40
            elif mutation == "source":
                gh.source_sha = "c" * 40
            elif mutation == "ci":
                gh.ci = "failure"
            else:
                plan["changes"][0]["path"] = "prek.toml"
            with self.assertRaises(ValueError):
                self.publish(plan, gh)
            self.assertEqual(gh.writes, [])

    def test_final_ci_accepts_push_and_dispatch_but_rejects_ineligible_runs(self):
        good = {"head_sha": SHA, "head_branch": "main", "event": "push",
                "status": "completed", "conclusion": "success"}
        for event in ["push", "workflow_dispatch"]:
            with self.subTest(event=event):
                gh = GitHub()
                gh.ci_runs = [{**good, "event": event}]
                d.source_ready(SHA, gh)
        bad_rows = [[], [{**good, "event": "pull_request"}],
                    [{**good, "head_sha": BASE}], [{**good, "head_branch": "feature"}],
                    [{**good, "status": "in_progress", "conclusion": None}, good],
                    [{**good, "conclusion": "failure"}, good],
                    [{**good, "conclusion": "cancelled"}, good],
                    [{**good, "conclusion": "skipped"}, good]]
        for rows in bad_rows:
            with self.subTest(rows=rows):
                gh = GitHub()
                gh.ci_runs = rows
                with self.assertRaisesRegex(ValueError, "Exact final CI"):
                    self.publish(self.plan(gh), gh)
                self.assertEqual(gh.writes, [])

    def test_existing_matching_branch_and_pr_are_idempotent(self):
        gh = GitHub()
        plan = self.plan(gh)
        self.publish(plan, gh)
        gh.prs = [{"state": "open", "head": {"sha": "head"}, "base": {"ref": "main"}, "html_url": "url"}]
        gh.writes.clear()
        self.assertEqual(self.publish(plan, gh)["result"], "existing")
        self.assertFalse(any(e.endswith(("/git/refs", "/pulls", "/git/commits")) for e, _ in gh.writes))
        gh.commit["tree"] = "different-tree"
        with self.assertRaisesRegex(ValueError, "Existing branch differs"):
            self.publish(plan, gh)

    def test_dirty_canonical_checkout_rejected(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        with self.assertRaisesRegex(ValueError, "dirty"):
            d.canonical_sha(self.root)

    def test_wrong_writer_identity_and_directory_symlink(self):
        gh = GitHub()
        plan = self.plan(gh)
        def wrong_user(endpoint, payload=None, source=False):
            if endpoint == "user":
                return {"id": 1}
            return gh(endpoint, payload, source)
        with self.assertRaisesRegex(ValueError, "belong to edbfi"):
            self.publish(plan, wrong_user)
        self.assertEqual(gh.writes, [])
        with self.assertRaisesRegex(ValueError, "Unsafe consumer directory"):
            self.plan(GitHub({".agents": b"elsewhere"}))

    def test_second_base_check_stops_before_ref_write(self):
        gh = GitHub()
        plan = self.plan(gh)
        def moved(endpoint, payload=None, source=False):
            result = gh(endpoint, payload, source)
            if payload is not None and endpoint.endswith("/git/commits"):
                gh.base = "c" * 40
            return result
        with self.assertRaisesRegex(ValueError, "before branch creation"):
            self.publish(plan, moved)
        self.assertFalse(any(e.endswith(("/git/refs", "/pulls")) for e, _ in gh.writes))

    def test_cli_artifact_provenance_hash_and_target(self):
        output = self.root / "artifact"
        output.mkdir()
        plan = self.plan(GitHub())
        raw = d.encoded(plan)
        (output / "plan.json").write_bytes(raw)
        argv = ["delivery", "publish", "--target", "edbfi/example", "--source-sha", SHA,
                "--output", str(output), "--preview-run", "123", "--plan-sha256", d.digest(raw)]
        env = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": d.SOURCE, "GITHUB_EVENT_NAME": "workflow_dispatch"}
        good_run = {"path": ".github/workflows/preview.yml", "event": "workflow_dispatch",
                    "head_sha": SHA, "conclusion": "success"}
        for field, value in [("path", "other.yml"), ("event", "pull_request"),
                             ("head_sha", BASE), ("conclusion", "failure"), ("hash", "bad"), ("target", "edbfi/other")]:
            args = argv.copy()
            run = good_run.copy()
            if field == "hash":
                args[-1] = value
            elif field == "target":
                args[3] = value
            else:
                run[field] = value
            with patch.dict(os.environ, env), patch("sys.argv", args), \
                    patch.object(d, "canonical_sha", return_value=SHA), \
                    patch.object(d, "source_ready"), patch.object(d, "api", return_value=run), \
                    patch.object(d, "publish") as publish:
                with self.assertRaises(ValueError):
                    d.main()
                publish.assert_not_called()

    def test_cli_rejects_local_and_pr_execution(self):
        argv = ["delivery", "preview", "--target", "edbfi/example", "--source-sha", SHA,
                "--output", str(self.root / "artifact")]
        for event in ["", "pull_request"]:
            with patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": d.SOURCE,
                                        "GITHUB_EVENT_NAME": event}), patch("sys.argv", argv):
                with self.assertRaisesRegex(ValueError, "Manual dispatch"):
                    d.main()


if __name__ == "__main__":
    unittest.main()
