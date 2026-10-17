"""Check the guidelines library, hand-written rules and manifest.toml (read-only, stdlib, Python 3.11+).

Usage: check-library.py [--stale]

Manifest: `schema = 2`, `[defaults] publish = false`, and explicit opt-in `[[repo]]` targets whose
`guidelines` entries name packs under guidelines/ and whose `rules` name files under rules/.
Rules: flat `rules/<name>.md` files, UTF-8 with LF endings, frontmatter with exactly
`type: "agent_requested"` and a quoted `description`, then one `# ` title. Names starting with
`guidelines-` are reserved for generated pointer rules.
Library: every pack passes the installed coding-guidelines-builder's `packs.py check`,
`packs.py sources` and `verify_examples.py`, and guidelines/INDEX.md is current.
--stale lists packs past their refresh_after date and fails when there are any.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import cast

ROOT = Path(os.environ.get("AGENT_RULES_ROOT") or Path(__file__).resolve().parents[1])
BUILDER = ROOT / ".agents" / "skills" / "coding-guidelines-builder" / "scripts"
LIBRARY = ROOT / "guidelines"
RULES = ROOT / "rules"
INSTALL = ("bunx skills add https://github.com/edbfi/skills/blob/main/coding-guidelines/coding-guidelines-builder/SKILL.md"
           " --skill coding-guidelines-builder --agent codex --yes")
RULE_NAME = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
ENTRY = re.compile(r"(components|stacks)/[a-z0-9]+(?:[-_][a-z0-9]+)*")
SLUG = re.compile(r"edbfi/[A-Za-z0-9_.-]+")
FRONTMATTER_LINE = re.compile(r'([a-z_]+): "([^"\\]+)"')
RULE_TYPES = {"agent_requested"}
RESERVED_PREFIX = "guidelines-"
# CommonMark fences: up to 3 spaces, then 3+ backticks or tildes; a backtick fence's info string
# has no backtick. A fence closes on the same character, at least as long, with nothing after it.
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")

errors: list[str] = []


def fail(where: str, message: str) -> None:
    errors.append(f"{where}: {message}")


def check_rule(path: Path) -> None:
    where = path.relative_to(ROOT).as_posix()
    if path.is_symlink() or not path.is_file():
        return fail(where, "must be a regular file")
    if path.suffix != ".md" or not RULE_NAME.fullmatch(path.stem):
        return fail(where, "filename must be lowercase <name>.md (letters, digits, '-', '_')")
    if path.stem.startswith(RESERVED_PREFIX):
        return fail(where, f"names starting with {RESERVED_PREFIX!r} are reserved for generated pointer rules")
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return fail(where, "must be UTF-8")
    if text.startswith("\ufeff") or "\r" in text or not text.endswith("\n"):
        return fail(where, "must be UTF-8 without BOM, LF line endings, ending in a newline")
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        return fail(where, "must start with a '---' frontmatter block")
    end = lines.index("---", 1)
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        match = FRONTMATTER_LINE.fullmatch(line)
        if not match:
            fail(where, f"frontmatter line must be key: \"value\": {line!r}")
        elif match[1] in fields:
            fail(where, f"duplicate frontmatter key {match[1]!r}")
        else:
            fields[match[1]] = match[2]
    if set(fields) != {"type", "description"}:
        fail(where, f"frontmatter keys must be type and description, found {sorted(fields)}")
    if "type" in fields and fields["type"] not in RULE_TYPES:
        fail(where, f"type must be one of {sorted(RULE_TYPES)}")
    body = lines[end + 1:]
    first = 1 if body[:1] == [""] else 0
    if len(body) <= first or not re.fullmatch(r"# \S.*", body[first]):
        fail(where, "the '# ' title must follow the frontmatter (one blank line allowed)")
    fence: str | None = None
    titles = 0
    for line in body:
        marker = FENCE.match(line)
        if fence is None:
            if marker and not (marker[1][0] == "`" and "`" in marker[2]):
                fence = marker[1]
            elif line.startswith("# "):
                titles += 1
        elif marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
            fence = None
    if fence is not None:
        fail(where, "unclosed code fence")
    if titles != 1:
        fail(where, f"must have exactly one '# ' title outside code fences, found {titles}")


def string_list(value: object, at: str, key: str) -> list[str]:
    if not isinstance(value, list):
        fail(at, f"{key} must be a list")
        return []
    items = cast("list[object]", value)
    names = [item for item in items if isinstance(item, str)]
    if len(names) != len(items) or len(set(names)) != len(names):
        fail(at, f"{key} must be a list of distinct strings")
    return names


def check_manifest(rules: set[str], packs: set[str]) -> list[str]:
    """Validate manifest.toml and return every guidelines entry it lists."""
    where = "manifest.toml"
    try:
        data = tomllib.loads((ROOT / where).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        fail(where, f"unreadable: {error}")
        return []
    if set(data) != {"schema", "defaults", "repo"}:
        fail(where, f"top-level keys must be schema, defaults and repo, found {sorted(data)}")
    if data.get("schema") != 2:
        fail(where, "schema must be 2")
    if data.get("defaults") != {"publish": False}:
        fail(where, "[defaults] must be exactly publish = false")
    raw_repos = cast("object", data.get("repo", []))
    repos = cast("list[object]", raw_repos) if isinstance(raw_repos, list) else []
    if not isinstance(raw_repos, list):
        fail(where, "repo must be an array of tables (for none, put `repo = []` above [defaults])")
    listed: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(repos):
        if not isinstance(raw, dict):
            fail(f"{where} [[repo]] #{index + 1}", "must be a table")
            continue
        entry = cast("dict[str, object]", raw)
        slug = entry.get("slug")
        at = f"{where} [[repo]] #{index + 1} ({slug})"
        if set(entry) != {"slug", "publish", "guidelines", "rules"}:
            fail(at, "keys must be exactly slug, publish, guidelines and rules")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            fail(at, "slug must be edbfi/<repo>")
        elif slug.lower() in seen:
            fail(at, "duplicate slug")
        else:
            seen.add(slug.lower())
        if entry.get("publish") is not True:
            fail(at, "publish must be true (targets opt in explicitly)")
        destinations: dict[str, str] = {}
        for item in string_list(entry.get("guidelines"), at, "guidelines"):
            if not ENTRY.fullmatch(item) or item not in packs:
                fail(at, f"unknown guidelines entry {item!r} (no guidelines/{item}/pack.json)")
            listed.append(item)
            _ = destinations.setdefault(f".agents/rules/{RESERVED_PREFIX}{item.replace('/', '-')}.md", item)
        for rule in string_list(entry.get("rules"), at, "rules"):
            if rule not in rules:
                fail(at, f"unknown rule {rule!r} (no rules/{rule}.md)")
            path = f".agents/rules/{rule}.md"
            if path in destinations:
                fail(at, f"rule {rule!r} and {destinations[path]!r} both deliver {path}")
            destinations[path] = rule
    return sorted(set(listed))


def builder(script: str, *args: str | Path) -> int:
    result = subprocess.run([sys.executable, "-I", "-B", str(BUILDER / script), *(str(a) for a in args)],
                            capture_output=True, text=True, check=False)
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        print(output)
        errors.append(f"{script} {' '.join(str(a) for a in args)}: exit {result.returncode}")
    elif "warning:" in output:
        print(output)
    return result.returncode


def check_library(listed: list[str]) -> None:
    if not (BUILDER / "packs.py").is_file():
        fail("guidelines", f"coding-guidelines-builder is not installed; run: {INSTALL}")
        return
    packs = sorted(p.parent for group in ("components", "stacks") for p in (LIBRARY / group).glob("*/pack.json"))
    if packs:
        _ = builder("packs.py", "check", "--library", LIBRARY)
        _ = builder("packs.py", "sources", *packs)
        for pack in packs:
            _ = builder("verify_examples.py", pack)
    _ = builder("packs.py", "index", LIBRARY, "--check", "--warn-unreferenced", "--referenced", ",".join(listed))
    for base in (LIBRARY, RULES):
        for path in sorted(base.rglob("*")) if base.is_dir() else []:
            if path.name.lower() == "skill.md":
                fail(path.relative_to(ROOT).as_posix(), "a SKILL.md does not belong in the library or rules")


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args == ["--stale"]:
        if not (BUILDER / "packs.py").is_file():
            print(f"coding-guidelines-builder is not installed; run: {INSTALL}", file=sys.stderr)
            return 2
        return subprocess.run([sys.executable, "-I", "-B", str(BUILDER / "packs.py"), "index", str(LIBRARY), "--stale"],
                              check=False).returncode
    if args:
        print(__doc__, file=sys.stderr)
        return 2
    entries = sorted(RULES.iterdir()) if RULES.is_dir() else []
    for path in entries:
        check_rule(path)
    rules = {path.stem for path in entries if path.suffix == ".md"}
    packs = {f"{group}/{p.parent.name}" for group in ("components", "stacks") for p in (LIBRARY / group).glob("*/pack.json")}
    listed = check_manifest(rules, packs)
    check_library(listed)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(entries)} rules, {len(packs)} packs and the manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
