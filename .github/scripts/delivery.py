"""Plan exact rule updates; publish only a reviewed, unchanged plan from CI."""
import argparse
import base64
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "edbfi/agent-rules"
IDENTITY = {"name": "edbfi", "email": "326875205+edbfi@users.noreply.github.com"}
EXCLUDED = {"cccp-ps", "afisharr", "cdiag.link", "claude-atoll-web", "claude-diag", "tgraph-bot-source", "autoscan"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def api(endpoint, payload=None, source=False):
    env = os.environ.copy()
    env["GH_TOKEN"] = env.get("SOURCE_TOKEN" if source else "GH_TOKEN", "")
    command = ["gh", "api", endpoint]
    if payload is not None:
        command += ["--method", "POST", "--input", "-"]
    result = subprocess.run(command, input=None if payload is None else encoded(payload),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    require(result.returncode == 0, f"GitHub request failed: {endpoint.split('?')[0]}")
    return json.loads(result.stdout)


def manifest(root=ROOT):
    data = tomllib.loads((root / "manifest.toml").read_text())
    require(data["defaults"] == {"publish": False}, "Publishing must be explicit")
    seen = set()
    for entry in data["repo"]:
        slug = entry["slug"]
        require(re.fullmatch(r"edbfi/[A-Za-z0-9_.-]+", slug) and slug.split("/")[1].lower() not in EXCLUDED,
                "Invalid or excluded target")
        require(slug.lower() not in seen, "Duplicate target")
        seen.add(slug.lower())
        require(entry.get("publish") is True, "Target must opt in")
        rules = entry["rules"]
        require(rules and len(set(rules)) == len(rules), "Invalid rule list")
        for rule in rules:
            require(re.fullmatch(r"[a-z0-9_-]+", rule), "Invalid rule identifier")
            path = root / "rules" / (rule + ".md")
            require(path.is_file() and not path.is_symlink(), "Missing or unsafe rule")
            hashes = data["accepted"].get(rule, [])
            require(hashes and all(re.fullmatch(r"[0-9a-f]{64}", h) for h in hashes), "Missing accepted hashes")
        for name, sha in entry.get("remove", {}).items():
            require(re.fullmatch(r"[a-z0-9_-]+\.md", name) and name[:-3] not in rules,
                    "Invalid obsolete filename")
            require(re.fullmatch(r"[0-9a-f]{64}", sha), "Invalid obsolete hash")
    return data


def canonical_sha(root=ROOT):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
    require(not git("status", "--porcelain", "--untracked-files=normal"), "Canonical checkout is dirty")
    return git("rev-parse", "HEAD")


def build_plan(target, source_sha, root=ROOT, request=api):
    require(re.fullmatch(r"[0-9a-f]{40}", source_sha), "Invalid source revision")
    data = manifest(root)
    entries = [e for e in data["repo"] if e["slug"] == target]
    require(len(entries) == 1, "Target is not opted in")
    entry = entries[0]
    prefix = "repos/" + target
    repo = request(prefix)
    require(repo["full_name"] == target and not repo["archived"] and not repo["private"], "Unexpected target repository")
    branch = repo["default_branch"]
    base = request(prefix + "/branches/" + quote(branch, safe=""))["commit"]["sha"]
    commit = request(prefix + "/git/commits/" + base)
    tree = request(prefix + "/git/trees/" + commit["tree"]["sha"] + "?recursive=1")
    require(not tree.get("truncated"), "Incomplete consumer tree")
    paths = {e["path"]: e for e in tree["tree"]}
    for name in [".agents", ".agents/rules"]:
        require(name not in paths or paths[name]["type"] == "tree", "Unsafe consumer directory")
    changes, diff = [], []
    desired = {r + ".md": (root / "rules" / (r + ".md")).read_bytes() for r in entry["rules"]}
    desired.update({name: None for name in entry.get("remove", {})})
    for name, new in sorted(desired.items()):
        path = ".agents/rules/" + name
        item = paths.get(path)
        old = None
        if item:
            require(item["type"] == "blob" and item["mode"] == "100644", "Unsafe managed file")
            blob = request(prefix + "/git/blobs/" + item["sha"])
            require(blob["encoding"] == "base64", "Unexpected blob encoding")
            old = base64.b64decode(blob["content"], validate=False)
        if old == new:
            continue
        if old is not None:
            allowed = [entry["remove"][name]] if new is None else data["accepted"][name[:-3]]
            require(digest(old) in allowed, "Consumer has unreviewed edits: " + path)
        changes.append({"path": path, "old_blob": item["sha"] if item else None,
                        "old_sha256": digest(old) if old is not None else None,
                        "new_sha256": digest(new) if new is not None else None,
                        "content": base64.b64encode(new).decode() if new is not None else None})
        diff.extend(difflib.unified_diff((old or b"").decode().splitlines(True),
                                        (new or b"").decode().splitlines(True),
                                        fromfile="a/" + path, tofile="b/" + path))
    return {"schema": 1, "source": SOURCE, "source_sha": source_sha, "target": target,
            "target_id": repo["id"], "base_branch": branch, "base_sha": base,
            "base_tree": commit["tree"]["sha"], "changes": changes}, "".join(diff)


def source_ready(sha, request=api):
    repo = request("repos/" + SOURCE, source=True)
    require(repo["id"] == 1343246959, "Wrong canonical repository")
    branch = request("repos/" + SOURCE + "/branches/" + quote(repo["default_branch"], safe=""), source=True)
    require(branch["commit"]["sha"] == sha, "Canonical default branch moved")
    runs = request("repos/" + SOURCE + "/actions/workflows/ci.yml/runs?event=push&head_sha=" + sha, source=True)
    require(runs["workflow_runs"] and runs["workflow_runs"][0]["head_sha"] == sha
            and runs["workflow_runs"][0]["conclusion"] == "success", "Exact final CI has not passed")


def publish(plan, root=ROOT, request=api):
    require(canonical_sha(root) == plan["source_sha"], "Wrong canonical checkout")
    source_ready(plan["source_sha"], request)
    fresh, _ = build_plan(plan["target"], plan["source_sha"], root, request)
    require(fresh == plan, "Reviewed plan is stale or modified")
    if not plan["changes"]:
        return {"result": "no-op", "target": plan["target"]}
    require(request("user")["id"] == 326875205, "Writer token must belong to edbfi")
    prefix = "repos/" + plan["target"]
    branch = "chore/agent-rules-" + plan["source_sha"][:12]
    existing = request(prefix + "/git/matching-refs/heads/" + branch)
    existing = [r for r in existing if r["ref"] == "refs/heads/" + branch]
    tree_entries = []
    for change in plan["changes"]:
        blob_sha = None
        if change["content"] is not None:
            blob_sha = request(prefix + "/git/blobs", {"encoding": "base64", "content": change["content"]})["sha"]
        tree_entries.append({"path": change["path"], "mode": "100644", "type": "blob", "sha": blob_sha})
    tree = request(prefix + "/git/trees", {"base_tree": plan["base_tree"], "tree": tree_entries})["sha"]
    message = ("chore(rules): sync canonical agent guidance\n\nCanonical: " + plan["source_sha"]
               + "\nPlan-SHA256: " + digest(encoded(plan))
               + "\n\nSigned-off-by: edbfi <326875205+edbfi@users.noreply.github.com>\n")
    if existing:
        head = existing[0]["object"]["sha"]
        commit = request(prefix + "/git/commits/" + head)
        require(commit["tree"]["sha"] == tree and [p["sha"] for p in commit["parents"]] == [plan["base_sha"]]
                and commit["message"].rstrip("\n") == message.rstrip("\n")
                and all(commit["author"][k] == v for k, v in IDENTITY.items()), "Existing branch differs; preserved")
    else:
        head = request(prefix + "/git/commits", {"message": message, "tree": tree,
                       "parents": [plan["base_sha"]], "author": IDENTITY, "committer": IDENTITY})["sha"]
        source_ready(plan["source_sha"], request)
        fresh, _ = build_plan(plan["target"], plan["source_sha"], root, request)
        require(fresh == plan, "Consumer moved before branch creation")
        request(prefix + "/git/refs", {"ref": "refs/heads/" + branch, "sha": head})
    prs = request(prefix + "/pulls?state=all&head=" + quote("edbfi:" + branch, safe="") + "&per_page=100")
    if prs:
        require(len(prs) == 1 and prs[0]["state"] == "open" and prs[0]["head"]["sha"] == head
                and prs[0]["base"]["ref"] == plan["base_branch"], "Existing PR differs or is closed; preserved")
        return {"result": "existing", "url": prs[0]["html_url"], "head": head}
    pr = request(prefix + "/pulls", {"title": "chore(rules): sync canonical agent guidance",
                 "head": branch, "base": plan["base_branch"],
                 "body": "Update canonical guidance from edbfi/agent-rules at `" + plan["source_sha"]
                 + "`.\n\nReviewed plan SHA256: `" + digest(encoded(plan))
                 + "`. Consumer base: `" + plan["base_sha"]
                 + "`.\n\nReview the full diff and project toolchain requirements, all expected CI jobs and artifacts, "
                 + "and exact head/base before merging manually. No toolchain files or prek settings are changed."})
    return {"result": "created", "url": pr["html_url"], "head": head}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["preview", "publish"])
    parser.add_argument("--target", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan-sha256")
    parser.add_argument("--preview-run")
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == SOURCE,
            "Delivery runs only in canonical repository CI")
    require(os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch", "Manual dispatch required")
    require(canonical_sha() == args.source_sha, "Unexpected checkout")
    source_ready(args.source_sha)
    if args.mode == "preview":
        plan, diff = build_plan(args.target, args.source_sha)
        args.output.mkdir(parents=True, exist_ok=False)
        raw = encoded(plan)
        (args.output / "plan.json").write_bytes(raw)
        (args.output / "changes.diff").write_text(diff)
        (args.output / "SHA256").write_text(digest(raw) + "  plan.json\n")
        print("Plan SHA256:", digest(raw), "changed files:", len(plan["changes"]))
    else:
        require(args.preview_run and re.fullmatch(r"[0-9]+", args.preview_run), "Preview run required")
        run = api("repos/" + SOURCE + "/actions/runs/" + args.preview_run, source=True)
        require(run["path"] == ".github/workflows/preview.yml" and run["event"] == "workflow_dispatch"
                and run["head_sha"] == args.source_sha and run["conclusion"] == "success", "Invalid preview provenance")
        raw = (args.output / "plan.json").read_bytes()
        require(digest(raw) == args.plan_sha256, "Reviewed artifact hash does not match")
        plan = json.loads(raw)
        require(plan["target"] == args.target and plan["source_sha"] == args.source_sha, "Wrong plan identity")
        print(json.dumps(publish(plan), indent=2))


if __name__ == "__main__":
    main()
