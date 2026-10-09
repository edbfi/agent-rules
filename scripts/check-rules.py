"""Check the shape of the canonical rules and manifest.toml (read-only, stdlib, Python 3.11+).

Rules: flat `rules/<name>.md` files, UTF-8 with LF endings, frontmatter with exactly
`type: "agent_requested"` and a quoted `description`, then one `# ` title.
Manifest: `[defaults] publish = false`, explicit opt-in targets naming existing rules,
and `[accepted]` SHA256 lists keyed by existing rules.
"""
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
RULE_NAME = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
SLUG = re.compile(r"edbfi/[A-Za-z0-9_.-]+")
SHA256 = re.compile(r"[0-9a-f]{64}")
FRONTMATTER_LINE = re.compile(r'([a-z_]+): "([^"\\]+)"')
RULE_TYPES = {"agent_requested"}
FENCE = re.compile(r"(```|~~~)")

errors = []


def fail(where, message):
    errors.append(f"{where}: {message}")


def check_rule(path):
    where = path.relative_to(ROOT).as_posix()
    if path.is_symlink() or not path.is_file():
        return fail(where, "must be a regular file")
    if path.suffix != ".md" or not RULE_NAME.fullmatch(path.stem):
        return fail(where, "filename must be lowercase <name>.md (letters, digits, '-', '_')")
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return fail(where, "must be UTF-8")
    if text.startswith("﻿") or "\r" in text or not text.endswith("\n"):
        return fail(where, "must be UTF-8 without BOM, LF line endings, ending in a newline")
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        return fail(where, "must start with a '---' frontmatter block")
    end = lines.index("---", 1)
    fields = {}
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
    fence, titles = None, 0
    for line in body:
        marker = FENCE.match(line)
        if marker and (fence is None or marker[1] == fence):
            fence = marker[1] if fence is None else None
        elif fence is None and line.startswith("# "):
            titles += 1
    if fence is not None:
        fail(where, "unclosed code fence")
    if titles != 1:
        fail(where, f"must have exactly one '# ' title outside code fences, found {titles}")


def check_manifest(rules):
    where = "manifest.toml"
    try:
        data = tomllib.loads((ROOT / where).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        return fail(where, f"unreadable: {error}")
    if set(data) != {"defaults", "repo", "accepted"}:
        fail(where, f"top-level keys must be defaults, repo and accepted, found {sorted(data)}")
    if data.get("defaults") != {"publish": False}:
        fail(where, "[defaults] must be exactly publish = false")
    repos = data.get("repo", [])
    if not isinstance(repos, list) or not all(isinstance(entry, dict) for entry in repos):
        repos = []
        fail(where, "[[repo]] must be an array of tables")
    seen = set()
    for index, entry in enumerate(repos):
        slug = entry.get("slug")
        at = f"{where} [[repo]] #{index + 1} ({slug})"
        if set(entry) - {"slug", "publish", "rules", "remove"}:
            fail(at, f"unexpected keys {sorted(set(entry) - {'slug', 'publish', 'rules', 'remove'})}")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            fail(at, "slug must be edbfi/<repo>")
        elif slug.lower() in seen:
            fail(at, "duplicate slug")
        else:
            seen.add(slug.lower())
        if entry.get("publish") is not True:
            fail(at, "publish must be true (targets opt in explicitly)")
        listed = entry.get("rules")
        if not isinstance(listed, list) or not listed or len(set(map(str, listed))) != len(listed):
            fail(at, "rules must be a non-empty list without duplicates")
            listed = []
        for rule in listed:
            if rule not in rules:
                fail(at, f"unknown rule {rule!r} (no rules/{rule}.md)")
        remove = entry.get("remove", {})
        if not isinstance(remove, dict):
            fail(at, "remove must be a table of filename = sha256")
            remove = {}
        for name, sha in remove.items():
            if not (name.endswith(".md") and RULE_NAME.fullmatch(name[:-3])) or name[:-3] in listed:
                fail(at, f"invalid remove filename {name!r}")
            if not isinstance(sha, str) or not SHA256.fullmatch(sha):
                fail(at, f"remove {name!r} needs a lowercase SHA256")
    accepted = data.get("accepted", {})
    if not isinstance(accepted, dict):
        return fail(where, "[accepted] must be a table")
    for rule, hashes in accepted.items():
        at = f"{where} [accepted] {rule!r}"
        if rule not in rules:
            fail(at, f"unknown rule (no rules/{rule}.md)")
        if (not isinstance(hashes, list) or not hashes or len(set(map(str, hashes))) != len(hashes)
                or not all(isinstance(h, str) and SHA256.fullmatch(h) for h in hashes)):
            fail(at, "must be a non-empty list of distinct lowercase SHA256 hashes")
    return len(repos)


def main():
    rules_dir = ROOT / "rules"
    entries = sorted(rules_dir.iterdir()) if rules_dir.is_dir() else []
    if not entries:
        fail("rules/", "no canonical rules found")
    for path in entries:
        check_rule(path)
    rules = {path.stem for path in entries if path.suffix == ".md"}
    targets = check_manifest(rules)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(entries)} rules and {targets} manifest targets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
