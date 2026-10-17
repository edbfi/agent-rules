"""Deliver guideline packs and rules from this repository to opted-in consumer repositories.

Usage:
  sync.py plan  (--repo edbfi/<name> [--checkout PATH] | --all [--checkouts ROOT])
  sync.py apply (--repo edbfi/<name> [--checkout PATH] | --all [--checkouts ROOT]) [--pr]

`plan` prints what a sync would change and writes nothing. `apply` prepares the change on a
new branch in the consumer checkout without touching its working tree or existing branches; with
--pr it pushes that branch and opens a pull request. The default checkout is
~/github/<owner>/<repo>; --checkouts ROOT uses ROOT/<owner>/<repo>.

A consumer receives, per manifest entry, the pack (every file except examples/), for a stack also
the component packs it declares, and one pointer rule in .agents/rules/; listed hand-written rules
are copied to .agents/rules/. .agents/guidelines/guidelines-lock.json records every delivered
file's canonical and installed hash, so local edits are detected and never overwritten: a conflict
holds back its whole delivery set and every set that shares a component it would change.
Exit status: 0 done or nothing to do, 1 conflicts, 2 usage or environment errors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import cast

ROOT = Path(os.environ.get("AGENT_RULES_ROOT") or Path(__file__).resolve().parents[1])
BUILDER = ROOT / ".agents" / "skills" / "coding-guidelines-builder" / "scripts"
LIBRARY = ROOT / "guidelines"
SOURCE_REPO = "edbfi/agent-rules"
GUIDELINES = ".agents/guidelines"
RULES = ".agents/rules"
LOCK = f"{GUIDELINES}/guidelines-lock.json"
INDEX = f"{GUIDELINES}/INDEX.md"
PRETTIER_IGNORE = ".prettierignore"
PRETTIER_LINE = f"{GUIDELINES}/"
PRETTIER_CONFIGS = (".prettierrc", ".prettierrc.json", ".prettierrc.json5", ".prettierrc.yaml", ".prettierrc.yml",
                    ".prettierrc.toml", ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.mjs", ".prettierrc.ts",
                    "prettier.config.js", "prettier.config.cjs", "prettier.config.mjs", "prettier.config.ts")
LEAK_GUARD = "agent-rules-leak-guard"


class SyncError(Exception):
    """An environment or input problem that stops the run (exit 2)."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(*args: str | Path, cwd: Path, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True, check=False, env=env)
    if check and result.returncode != 0:
        raise SyncError(f"{' '.join(str(a) for a in args)} failed in {cwd}:\n{(result.stdout + result.stderr).strip()}")
    return result


def git(cwd: Path, *args: str | Path, check: bool = True) -> str:
    return run("git", *args, cwd=cwd, check=check).stdout.strip()


# --- manifest and library ---

@dataclass(frozen=True)
class Target:
    slug: str
    guidelines: tuple[str, ...]
    rules: tuple[str, ...]


def load_targets() -> dict[str, Target]:
    try:
        data = tomllib.loads((ROOT / "manifest.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise SyncError(f"manifest.toml unreadable: {error}") from error
    raw = cast("object", data.get("repo", []))
    targets: dict[str, Target] = {}
    for item in cast("list[object]", raw) if isinstance(raw, list) else []:
        entry = cast("dict[str, object]", item) if isinstance(item, dict) else {}
        slug = entry.get("slug")
        if not isinstance(slug, str) or entry.get("publish") is not True:
            continue
        lists = [cast("list[object]", entry.get(k)) if isinstance(entry.get(k), list) else [] for k in ("guidelines", "rules")]
        guidelines, rules = ([v for v in values if isinstance(v, str)] for values in lists)
        targets[slug.lower()] = Target(slug, tuple(guidelines), tuple(rules))
    return targets


def load_json(path: Path) -> dict[str, object]:
    value = cast("object", json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise SyncError(f"{path} must hold a JSON object")
    return cast("dict[str, object]", value)


def text_field(data: dict[str, object], key: str, default: str = "") -> str:
    value = data.get(key)
    return value if isinstance(value, str) else default


def pack_meta(key: str) -> dict[str, object]:
    path = LIBRARY / key / "pack.json"
    if not path.is_file():
        raise SyncError(f"guidelines/{key} has no pack.json; run check-library.py")
    return load_json(path)


def stack_components(key: str) -> list[str]:
    raw = pack_meta(key).get("components")
    edges = cast("list[object]", raw) if isinstance(raw, list) else []
    return [f"components/{text_field(cast('dict[str, object]', e), 'id')}" for e in edges if isinstance(e, dict)]


def pack_files(key: str) -> dict[str, bytes]:
    base = LIBRARY / key
    files: dict[str, bytes] = {}
    for path in sorted(base.rglob("*")):
        rel = path.relative_to(base)
        if rel.parts[0] == "examples" or not path.is_file():
            continue
        files[f"{GUIDELINES}/{key}/{rel.as_posix()}"] = path.read_bytes()
    return files


def pointer_path(key: str) -> str:
    return f"{RULES}/guidelines-{key.replace('/', '-')}.md"


def quoted(value: str) -> str:
    return re.sub(r'["\\\n]', "'", value)


def pointer(key: str) -> bytes:
    meta = pack_meta(key)
    name = text_field(meta, "name", key)
    researched = text_field(meta, "researched", "unknown")
    load_when = text_field(meta, "load_when", "working on this project")
    rows = [(name, text_field(meta, "resolved"), key)] if key.startswith("components/") else [
        (text_field(pack_meta(c), "name", c), text_field(pack_meta(c), "resolved"), c) for c in stack_components(key)]
    raw_targets = meta.get("targets")
    targets = cast("dict[str, object]", raw_targets) if isinstance(raw_targets, dict) else {}
    target_text = ", ".join(f"{k} {v}" for k, v in sorted(targets.items())) or "none declared"
    lines = [
        "---",
        'type: "agent_requested"',
        f'description: "{quoted(name)} coding guidelines (researched {quoted(researched)})"',
        "---",
        f"# {name} coding guidelines",
        "",
        f"Before {load_when[:1].lower() + load_when[1:]}, read `{GUIDELINES}/{key}/README.md`, then the topic",
        "files its \"Where to look\" table names for the task. Check `changes.md` in each component pack",
        "before relying on remembered APIs.",
        "",
        "| Component | Version | Guidelines |",
        "|---|---|---|",
        *(f"| {n} | {v} | `{GUIDELINES}/{c}/README.md` |" for n, v, c in rows),
        "",
        f"Targets: {target_text}. If this project's lockfile resolves different versions, say so before",
        "applying version-specific advice.",
    ]
    return ("\n".join(lines) + "\n").encode()


def desired_sets(target: Target) -> dict[str, dict[str, bytes]]:
    """Delivery sets: entry key -> consumer path -> canonical bytes."""
    sets: dict[str, dict[str, bytes]] = {}
    for key in target.guidelines:
        files = pack_files(key)
        if key.startswith("stacks/"):
            for component in stack_components(key):
                files.update(pack_files(component))
        files[pointer_path(key)] = pointer(key)
        sets[key] = files
    for name in target.rules:
        source = ROOT / "rules" / f"{name}.md"
        if not source.is_file():
            raise SyncError(f"rules/{name}.md does not exist; run check-library.py")
        sets[f"rules/{name}"] = {f"{RULES}/{name}.md": source.read_bytes()}
    return sets


def pack_of(path: str) -> str | None:
    """The pack key a consumer path belongs to, or None for pointers and rules."""
    parts = PurePosixPath(path).parts
    if len(parts) >= 4 and parts[:2] == (".agents", "guidelines") and parts[2] in ("components", "stacks"):
        return f"{parts[2]}/{parts[3]}"
    return None


# --- consumer state ---

def safe(worktree: Path, rel: str) -> Path:
    """Resolve a managed path, refusing traversal, foreign locations and symlinks."""
    pure = PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts or not (rel.startswith(f"{GUIDELINES}/") or rel.startswith(f"{RULES}/")):
        raise SyncError(f"refusing managed path outside {GUIDELINES}/ and {RULES}/: {rel!r}")
    current = worktree
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise SyncError(f"refusing to follow a symlink at {current.relative_to(worktree).as_posix()}")
    if current.exists() and not current.is_file():
        raise SyncError(f"{rel} exists and is not a regular file")
    return current


def current_hash(worktree: Path, rel: str) -> str | None:
    path = safe(worktree, rel)
    return sha(path.read_bytes()) if path.is_file() else None


@dataclass
class Lock:
    commit: str = ""
    entries: dict[str, list[str]] = field(default_factory=dict)
    files: dict[str, tuple[str, str]] = field(default_factory=dict)  # path -> (source, installed)
    managed_lines: list[str] = field(default_factory=list)
    legacy_removed: list[str] = field(default_factory=list)


def read_lock(worktree: Path) -> Lock:
    path = safe(worktree, LOCK)
    if not path.is_file():
        return Lock()
    try:
        data = load_json(path)
    except ValueError as error:
        raise SyncError(f"{LOCK} does not parse: {error}") from error
    source = data.get("source")
    source_map = cast("dict[str, object]", source) if isinstance(source, dict) else {}
    if data.get("schema") != 1 or source_map.get("repo") != SOURCE_REPO:
        raise SyncError(f"{LOCK} is not a schema 1 lock from {SOURCE_REPO}; inspect it before syncing")
    lock = Lock(commit=text_field(source_map, "commit"))
    raw_entries = data.get("entries")
    for key, value in (cast("dict[str, object]", raw_entries) if isinstance(raw_entries, dict) else {}).items():
        files = cast("dict[str, object]", value).get("files") if isinstance(value, dict) else None
        lock.entries[key] = [f for f in cast("list[object]", files) if isinstance(f, str)] if isinstance(files, list) else []
    raw_files = data.get("files")
    for rel, value in (cast("dict[str, object]", raw_files) if isinstance(raw_files, dict) else {}).items():
        hashes = cast("dict[str, object]", value) if isinstance(value, dict) else {}
        _ = safe(worktree, rel)
        lock.files[rel] = (text_field(hashes, "source_sha256"), text_field(hashes, "installed_sha256"))
    for rel in (f for files in lock.entries.values() for f in files):
        _ = safe(worktree, rel)
    raw_lines = data.get("managed_lines")
    lines_map = cast("dict[str, object]", raw_lines) if isinstance(raw_lines, dict) else {}
    prettier = lines_map.get(PRETTIER_IGNORE)
    lock.managed_lines = [v for v in cast("list[object]", prettier) if isinstance(v, str)] if isinstance(prettier, list) else []
    removed = data.get("legacy_removed")
    lock.legacy_removed = [v for v in cast("list[object]", removed) if isinstance(v, str)] if isinstance(removed, list) else []
    return lock


def render_lock(lock: Lock, commit: str) -> bytes:
    data = {
        "schema": 1,
        "source": {"repo": SOURCE_REPO, "commit": commit},
        "entries": {k: {"files": sorted(v)} for k, v in sorted(lock.entries.items())},
        "files": {k: {"source_sha256": s, "installed_sha256": i} for k, (s, i) in sorted(lock.files.items())},
        "managed_lines": {PRETTIER_IGNORE: lock.managed_lines} if lock.managed_lines else {},
        "legacy_removed": sorted(set(lock.legacy_removed)),
    }
    return (json.dumps(data, indent=2) + "\n").encode()


# --- plan ---

@dataclass
class Plan:
    actions: dict[str, str] = field(default_factory=dict)  # path -> add|update|remove|adopt|unchanged
    reasons: dict[str, list[str]] = field(default_factory=dict)  # conflicted entry -> reasons
    unmanaged: list[str] = field(default_factory=list)
    legacy_remove: dict[str, str] = field(default_factory=dict)  # legacy path -> entry
    legacy_report: list[str] = field(default_factory=list)
    members: dict[str, set[str]] = field(default_factory=dict)  # entry -> every path it owns or wants
    desired: dict[str, bytes] = field(default_factory=dict)
    sets: dict[str, dict[str, bytes]] = field(default_factory=dict)

    @property
    def conflicted(self) -> set[str]:
        return set(self.reasons)

    def blocked(self, path: str) -> bool:
        return any(path in paths for entry, paths in self.members.items() if entry in self.reasons)

    def changes(self) -> dict[str, str]:
        return {p: a for p, a in self.actions.items() if a != "unchanged" and not self.blocked(p)}


def legacy_table() -> dict[str, tuple[list[str], str | None]]:
    path = ROOT / "scripts" / "legacy-rules.json"
    if not path.is_file():
        return {}
    raw = load_json(path).get("rules")
    table: dict[str, tuple[list[str], str | None]] = {}
    for name, value in (cast("dict[str, object]", raw) if isinstance(raw, dict) else {}).items():
        entry = cast("dict[str, object]", value) if isinstance(value, dict) else {}
        hashes = entry.get("sha256")
        replaced = entry.get("replaced_by")
        table[name] = ([h for h in cast("list[object]", hashes) if isinstance(h, str)] if isinstance(hashes, list) else [],
                       replaced if isinstance(replaced, str) else None)
    return table


def compute_plan(worktree: Path, target: Target, lock: Lock) -> Plan:
    plan = Plan(sets=desired_sets(target))
    for files in plan.sets.values():
        plan.desired.update(files)
    for entry in set(plan.sets) | set(lock.entries):
        plan.members[entry] = set(plan.sets.get(entry, {})) | set(lock.entries.get(entry, []))

    def conflict(entry: str, reason: str) -> None:
        plan.reasons.setdefault(entry, []).append(reason)

    for rel in sorted(set(plan.desired) | (set(lock.files) - {INDEX})):
        current = current_hash(worktree, rel)
        locked = lock.files.get(rel)
        wanted = plan.desired.get(rel)
        if locked is not None:
            if current != locked[1]:
                action = "conflict"
            elif wanted is None:
                action = "remove"
            else:
                action = "update" if sha(wanted) != locked[0] else "unchanged"
        elif wanted is not None and current is None:
            action = "add"
        elif wanted is not None and current == sha(wanted):
            action = "adopt"
        else:
            action = "conflict"
        plan.actions[rel] = action
        if action == "conflict":
            what = "edited or removed locally" if locked is not None else "already exists and is not managed by sync"
            for entry, paths in plan.members.items():
                if rel in paths:
                    conflict(entry, f"{rel} {what}")

    index_hash = current_hash(worktree, INDEX)
    locked_index = lock.files.get(INDEX)
    if index_hash is not None and (locked_index is None or index_hash != locked_index[1]):
        for entry in plan.members:
            conflict(entry, f"{INDEX} was edited locally or is not managed by sync")

    for name, (hashes, replaced_by) in sorted(legacy_table().items()):
        rel = f"{RULES}/{name}"
        current = current_hash(worktree, rel)
        if current is None:
            continue
        if replaced_by is None or replaced_by not in plan.sets:
            plan.legacy_report.append(f"{rel} is a legacy rule with no replacement delivered yet; left in place")
        elif current in hashes:
            plan.legacy_remove[rel] = replaced_by
        else:
            conflict(replaced_by, f"{rel} is a modified legacy rule; reconcile it by hand")

    managed = {p for paths in plan.members.values() for p in paths} | {INDEX, LOCK}
    for base in (worktree / GUIDELINES / "components", worktree / GUIDELINES / "stacks"):
        for path in sorted(base.rglob("*")) if base.is_dir() and not base.is_symlink() else []:
            rel = path.relative_to(worktree).as_posix()
            if path.is_file() and rel not in managed:
                plan.unmanaged.append(rel)

    # A component pack that would change is frozen when any set containing it is conflicted, and
    # then every set containing that pack is held back too, until nothing new is blocked.
    while True:
        frozen = {pack for path, action in plan.actions.items() if action != "unchanged"
                  and (pack := pack_of(path)) and plan.blocked(path)}
        spread = [entry for entry, paths in plan.members.items()
                  if entry not in plan.reasons and any(pack_of(p) in frozen for p in paths)]
        if not spread:
            break
        for entry in spread:
            conflict(entry, "shares a component pack with a held-back set")
    return plan


def describe(plan: Plan) -> list[str]:
    lines: list[str] = []
    for entry in sorted(plan.members):
        if entry in plan.reasons:
            lines.append(f"  CONFLICT {entry}")
            lines.extend(f"    - {reason}" for reason in plan.reasons[entry])
            continue
        counts: dict[str, int] = {}
        for path in plan.members[entry]:
            action = plan.actions.get(path, "unchanged")
            counts[action] = counts.get(action, 0) + 1
        summary = ", ".join(f"{n} {a}" for a, n in sorted(counts.items()) if a != "unchanged") or "unchanged"
        state = "retire" if entry not in plan.sets else "deliver"
        lines.append(f"  {state} {entry}: {summary}")
    lines.extend(f"  legacy: remove {rel} (replaced by {entry})" for rel, entry in sorted(plan.legacy_remove.items())
                 if entry not in plan.reasons)
    lines.extend(f"  legacy: {note}" for note in plan.legacy_report)
    lines.extend(f"  unmanaged (kept): {rel}" for rel in plan.unmanaged)
    return lines


# --- repositories ---

def default_checkout(slug: str, checkouts: Path | None) -> Path:
    return (checkouts or Path.home() / "github") / slug


def verify_identity(checkout: Path, slug: str) -> None:
    pattern = re.compile(rf"[:/]{re.escape(slug)}(?:\.git)?/?$", re.I)
    for flag in ([], ["--push"]):
        url = git(checkout, "remote", "get-url", *flag, "origin", check=False)
        if not pattern.search(url):
            raise SyncError(f"{checkout} origin{' push' if flag else ''} URL {url!r} is not {slug}")


def check_local_state(checkout: Path) -> None:
    common = Path(git(checkout, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    hooks_path = git(checkout, "config", "--get", "core.hooksPath", check=False)
    hooks = Path(hooks_path) if hooks_path else common / "hooks"
    hooks = hooks if hooks.is_absolute() else checkout / hooks
    for hook in sorted(hooks.iterdir()) if hooks.is_dir() else []:
        if hook.is_file() and LEAK_GUARD in hook.read_text(encoding="utf-8", errors="replace"):
            raise SyncError(f"{hook} is the retired agent-rules leak guard; it rejects delivered rules. Remove it "
                            + f"(restore {hooks / 'pre-commit.chained'} as pre-commit if present) and rerun")
    exclude = common / "info" / "exclude"
    if exclude.is_file():
        stale = [line for line in exclude.read_text(encoding="utf-8").splitlines() if line.strip().startswith(".agents/")]
        if stale:
            raise SyncError(f"{exclude} still excludes {', '.join(stale)} from the retired synchronizer; remove those lines and rerun")


def preflight(checkout: Path, slug: str) -> tuple[str, str]:
    """Verify the checkout, fetch it and return (default branch, pinned commit)."""
    if not (checkout / ".git").exists():
        raise SyncError(f"no git checkout at {checkout}; clone {slug} there or pass --checkout")
    verify_identity(checkout, slug)
    check_local_state(checkout)
    _ = git(checkout, "fetch", "--quiet", "origin")
    head = git(checkout, "symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
    branch = head.removeprefix("origin/") if head else run(
        "gh", "repo", "view", "--repo", slug, "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name", cwd=checkout).stdout.strip()
    return branch, git(checkout, "rev-parse", f"origin/{branch}")


def source_commit(require_published: bool) -> str:
    commit = git(ROOT, "rev-parse", "HEAD")
    if require_published:
        if git(ROOT, "status", "--porcelain"):
            raise SyncError("agent-rules has uncommitted changes; commit or stash them first")
        _ = git(ROOT, "fetch", "--quiet", "origin")
        if run("git", "merge-base", "--is-ancestor", "HEAD", "origin/main", cwd=ROOT, check=False).returncode != 0:
            raise SyncError("agent-rules HEAD is not on origin/main; sync only delivers merged, validated content")
    return commit


@dataclass
class Worktree:
    checkout: Path
    path: Path

    def close(self) -> None:
        _ = run("git", "worktree", "remove", "--force", self.path, cwd=self.checkout, check=False)
        shutil.rmtree(self.path, ignore_errors=True)


def open_worktree(checkout: Path, commit: str) -> Worktree:
    path = Path(tempfile.mkdtemp(prefix="agent-rules-sync-"))
    path.rmdir()
    _ = git(checkout, "worktree", "add", "--detach", "--quiet", path, commit)
    return Worktree(checkout, path)


# --- apply ---

def has_prettier(worktree: Path) -> bool:
    if any((worktree / name).is_file() for name in PRETTIER_CONFIGS):
        return True
    package = worktree / "package.json"
    if not package.is_file():
        return False
    try:
        manifest = load_json(package)
    except (ValueError, SyncError):
        return False
    if "prettier" in manifest:  # inline configuration
        return True
    groups = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
    return any(isinstance(deps := manifest.get(group), dict) and "prettier" in cast("dict[str, object]", deps)
               for group in groups)  # installed with the default configuration


def write_changes(worktree: Path, plan: Plan, lock: Lock, commit: str) -> list[str]:
    """Apply the unblocked part of the plan; return the paths to stage."""
    touched: list[str] = []
    changes = plan.changes()
    for rel, action in sorted(changes.items()):
        path = safe(worktree, rel)
        if action == "remove":
            path.unlink(missing_ok=True)
            _ = lock.files.pop(rel, None)
        elif action in ("add", "update", "adopt"):
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_bytes(plan.desired[rel])
        touched.append(rel)
    for rel, entry in plan.legacy_remove.items():
        if entry not in plan.reasons:
            safe(worktree, rel).unlink()
            lock.legacy_removed.append(rel)
            touched.append(rel)
    for entry in plan.members:
        if entry in plan.reasons:
            continue
        if entry in plan.sets:
            lock.entries[entry] = sorted(plan.sets[entry])
        else:
            _ = lock.entries.pop(entry, None)
    for path in sorted((worktree / GUIDELINES).rglob("*"), reverse=True) if (worktree / GUIDELINES).is_dir() else []:
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    delivered = bool(lock.entries) and any(k.startswith(("components/", "stacks/")) for k in lock.entries)
    ignore = worktree / PRETTIER_IGNORE
    if ignore.is_symlink():
        raise SyncError(f"refusing to edit {PRETTIER_IGNORE}: it is a symlink")
    lines = ignore.read_text(encoding="utf-8").splitlines() if ignore.is_file() else []
    if delivered and has_prettier(worktree) and PRETTIER_LINE not in lines:
        _ = ignore.write_text("\n".join([*lines, PRETTIER_LINE]) + "\n", encoding="utf-8")
        lock.managed_lines = [PRETTIER_LINE]
        touched.append(PRETTIER_IGNORE)
    elif not delivered and PRETTIER_LINE in lock.managed_lines and PRETTIER_LINE in lines:
        kept = [line for line in lines if line != PRETTIER_LINE]
        if kept:
            _ = ignore.write_text("\n".join(kept) + "\n", encoding="utf-8")
        else:
            ignore.unlink()
        lock.managed_lines = []
        touched.append(PRETTIER_IGNORE)
    if delivered:
        result = run(sys.executable, "-I", "-B", BUILDER / "packs.py", "index", worktree / GUIDELINES, cwd=worktree, check=False)
        if result.returncode != 0:
            raise SyncError(f"could not generate {INDEX}: {(result.stdout + result.stderr).strip()}")
        touched.append(INDEX)
    elif (worktree / INDEX).is_file():
        (worktree / INDEX).unlink()
        _ = lock.files.pop(INDEX, None)
        touched.append(INDEX)
    run_hooks(worktree, sorted(set(touched)))
    for rel, action in changes.items():
        if action in ("add", "update", "adopt"):
            lock.files[rel] = (sha(plan.desired[rel]), current_hash(worktree, rel) or "")
    if delivered:
        index_bytes = (worktree / INDEX).read_bytes()
        lock.files[INDEX] = (sha(index_bytes), sha(index_bytes))
    referenced: set[str] = {p for files in lock.entries.values() for p in files}
    if delivered:
        referenced.add(INDEX)
    lock.files = {k: v for k, v in lock.files.items() if k in referenced}
    lock_path = safe(worktree, LOCK)
    if lock.entries:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        _ = lock_path.write_bytes(render_lock(lock, commit))
    else:
        lock_path.unlink(missing_ok=True)
    touched.append(LOCK)
    return sorted(set(touched))


def run_hooks(worktree: Path, paths: list[str]) -> None:
    if not (worktree / ".pre-commit-config.yaml").is_file():
        return
    tool = shutil.which("prek") or shutil.which("pre-commit")
    existing = [p for p in paths if (worktree / p).is_file()]
    if tool is None or not existing:
        return
    # A fixer that rewrites files exits non-zero once; a second run shows whether hooks really fail.
    output = ""
    for _attempt in range(2):
        result = run(tool, "run", "--files", *existing, cwd=worktree, check=False)
        if result.returncode == 0:
            return
        output = (result.stdout + result.stderr).strip()
    raise SyncError(f"the consumer's hooks fail on the delivered files:\n{output}")


def branch_tree(checkout: Path, branch: str) -> tuple[str | None, bool]:
    """(tree of the branch if it exists locally or on origin, whether origin has it)."""
    remote = bool(git(checkout, "ls-remote", "--heads", "origin", branch, check=False))
    if run("git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", cwd=checkout, check=False).returncode == 0:
        return git(checkout, "rev-parse", f"refs/heads/{branch}^{{tree}}"), remote
    if remote:
        _ = git(checkout, "fetch", "--quiet", "origin", f"refs/heads/{branch}:refs/remotes/origin/{branch}")
        return git(checkout, "rev-parse", f"refs/remotes/origin/{branch}^{{tree}}"), remote
    return None, remote


def apply(checkout: Path, target: Target, publish: bool) -> int:
    commit = source_commit(require_published=True)
    default, base = preflight(checkout, target.slug)
    worktree = open_worktree(checkout, base)
    try:
        lock = read_lock(worktree.path)
        plan = compute_plan(worktree.path, target, lock)
        print(f"{target.slug} @ {default} ({base[:7]}) from agent-rules@{commit[:7]}")
        print("\n".join(describe(plan)))
        status = 1 if plan.reasons else 0
        if not plan.changes() and not any(e not in plan.reasons for e in plan.legacy_remove.values()):
            print("  nothing to apply" if plan.reasons else "  up to date")
            return status
        touched = write_changes(worktree.path, plan, lock, commit)
        _ = git(worktree.path, "add", "-A", "--", *touched)
        if not git(worktree.path, "status", "--porcelain"):
            print("  up to date")
            return status
        body = "\n".join(["Delivered by agent-rules scripts/sync.py.", "", *describe(plan)])
        _ = git(worktree.path, "commit", "--quiet", "-s", "-m",
                f"chore(agents): sync coding guidelines from agent-rules@{commit[:7]}", "-m", body)
        tree = git(worktree.path, "rev-parse", "HEAD^{tree}")
        prepared = git(worktree.path, "rev-parse", "HEAD")
        branch = f"chore/sync-agent-guidelines-{commit[:7]}-{base[:7]}"
        existing, on_remote = branch_tree(checkout, branch)
        if existing is None:
            _ = git(checkout, "branch", branch, prepared)
            print(f"  prepared branch {branch}")
        elif existing != tree:
            print(f"  branch {branch} already exists with different content; delete it or move agent-rules on", file=sys.stderr)
            return 1
        else:
            print(f"  branch {branch} is already prepared")
            if run("git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", cwd=checkout, check=False).returncode != 0:
                _ = git(checkout, "branch", branch, f"refs/remotes/origin/{branch}")
        if publish:
            if not on_remote:
                _ = git(checkout, "push", "--quiet", "origin", f"refs/heads/{branch}:refs/heads/{branch}")
                print(f"  pushed {branch}")
            open_prs = run("gh", "pr", "list", "--repo", target.slug, "--head", branch, "--state", "open",
                           "--json", "url", "--jq", ".[].url", cwd=checkout).stdout.strip()
            if open_prs:
                print(f"  pull request already open: {open_prs}")
            else:
                url = run("gh", "pr", "create", "--repo", target.slug, "--base", default, "--head", branch,
                          "--title", f"chore(agents): sync coding guidelines from agent-rules@{commit[:7]}",
                          "--body", body, cwd=checkout).stdout.strip()
                print(f"  opened {url}")
        return status
    finally:
        worktree.close()


def show_plan(checkout: Path, target: Target) -> int:
    commit = source_commit(require_published=False)
    default, base = preflight(checkout, target.slug)
    worktree = open_worktree(checkout, base)
    try:
        plan = compute_plan(worktree.path, target, read_lock(worktree.path))
        print(f"{target.slug} @ {default} ({base[:7]}) from agent-rules@{commit[:7]}")
        print("\n".join(describe(plan)))
        if not plan.changes() and not plan.reasons and not plan.legacy_remove:
            print("  up to date")
        return 1 if plan.reasons else 0
    finally:
        worktree.close()


class Arguments(argparse.Namespace):
    command: str = ""
    repo: str | None = None
    checkout: Path | None = None
    all: bool = False
    checkouts: Path | None = None
    pr: bool = False


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    _ = parser.add_argument("command", choices=("plan", "apply"))
    _ = parser.add_argument("--repo")
    _ = parser.add_argument("--checkout", type=Path)
    _ = parser.add_argument("--all", action="store_true")
    _ = parser.add_argument("--checkouts", type=Path)
    _ = parser.add_argument("--pr", action="store_true")
    args = parser.parse_args(argv[1:], namespace=Arguments())
    if bool(args.repo) == args.all or (args.all and args.checkout) or (args.pr and args.command != "apply"):
        parser.print_usage(sys.stderr)
        return 2
    try:
        targets = load_targets()
        if args.repo:
            target = targets.get(args.repo.lower())
            if target is None:
                raise SyncError(f"{args.repo} is not an opted-in target in manifest.toml")
            selected = [(target, args.checkout or default_checkout(target.slug, args.checkouts))]
        else:
            selected = [(t, default_checkout(t.slug, args.checkouts)) for t in targets.values()]
        status = 0
        for target, checkout in selected:
            code = apply(checkout.resolve(), target, args.pr) if args.command == "apply" else show_plan(checkout.resolve(), target)
            status = max(status, code)
        return status
    except SyncError as error:
        print(f"sync: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
