"""Check public rule references without reading local-only manifests or consumers."""
import json
from pathlib import Path
import re
import sys
import tomllib

root = Path(__file__).resolve().parents[2]
manifest = tomllib.loads((root / "manifest.toml").read_text())
assert manifest["defaults"]["publish"] is False, "Publishing must be opt-in"
assert manifest["defaults"]["exclude_via"] == "info"
slugs = set()
publishing = []
for entry in manifest["repo"]:
    slug = entry["slug"]
    assert re.fullmatch(r"engels74/[A-Za-z0-9_.-]+", slug), "Unexpected public owner or slug"
    assert slug not in slugs, f"Duplicate public target: {slug}"
    slugs.add(slug)
    rules = entry["rules"]
    assert rules and len(rules) == len(set(rules)), f"Invalid rule list: {slug}"
    for rule in rules:
        assert re.fullmatch(r"[a-z0-9_-]+", rule), f"Invalid rule identifier: {rule}"
        assert (root / "rules" / f"{rule}.md").is_file(), f"Missing canonical rule: {rule}"
    if entry.get("publish", False) and not entry.get("archived", False):
        publishing.append(slug)
files = list((root / "rules").glob("*.md"))
assert files, "No canonical rules found"
for path in files:
    content = path.read_text()
    assert content.endswith("\n") and "\r" not in content, f"Invalid line endings: {path.name}"
    assert content.startswith("---\n") and "\n# " in content, f"Missing metadata/title: {path.name}"
    assert "type:" in content.split("---", 2)[1], f"Missing rule type: {path.name}"
if sys.argv[1:] == ["--targets"]:
    print("repositories=" + json.dumps(publishing, separators=(",", ":")))
else:
    assert not sys.argv[1:], "Usage: check-content.py [--targets]"
    print(f"Validated {len(files)} canonical rules and {len(slugs)} public targets")
