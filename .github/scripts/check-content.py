"""Check public rule references without reading local-only manifests or consumers."""
import json
from pathlib import Path
import sys

from delivery import manifest

root = Path(__file__).resolve().parents[2]
manifest_data = manifest(root)
slugs = [entry["slug"] for entry in manifest_data["repo"]]
publishing = slugs
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
