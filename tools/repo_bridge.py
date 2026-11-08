#!/usr/bin/env python3
"""Mindport repository bridge v0: discover, describe and validate repo context.

Read-only discovery. No account writes, memory extraction or background tasks.
Requires Python 3.11+ and the standard library.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

SCHEMA = "mindport.repo-bridge.v0"
SCAN_SCHEMA = "mindport.repo-scan.v0"
ENTRYPOINTS = (
    "AGENTS.md", "CONTEXT.md", "PROJECT.md", "POLICY.md", "README.md",
    "VISION.md", "context/routes.json",
)
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
API = "https://api.github.com"


class BridgeError(ValueError):
    pass


def valid_repo(value: str) -> str:
    if not isinstance(value, str) or not REPO_RE.fullmatch(value):
        raise BridgeError("repository must be owner/name")
    return value


def valid_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise BridgeError("invalid relative path")
    parts = value.split("/")
    if value.startswith("/") or any(p in ("", ".", "..") for p in parts):
        raise BridgeError("unsafe or ambiguous relative path")
    if parts[0] in (".git", ".env", "secrets", "private"):
        raise BridgeError("restricted path")
    return value


def default_manifest(repository: str, entrypoints: list[str]) -> dict:
    return {
        "schema": SCHEMA,
        "repository": valid_repo(repository),
        "entrypoints": entrypoints,
        "context_owner": "repository",
        "publication": {"mode": "reviewed-pr", "target": "inbox"},
        "sharing": {"mode": "references-only", "export_paths": []},
        "note": "This file describes capabilities; it grants no credentials or cross-repository access.",
    }


def validate_manifest(manifest: object, root: Path | None = None) -> dict:
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise BridgeError("unsupported manifest schema")
    valid_repo(manifest.get("repository"))
    entries = manifest.get("entrypoints")
    if not isinstance(entries, list) or not entries or any(not isinstance(x, str) for x in entries):
        raise BridgeError("entrypoints must be a nonempty list")
    if len(entries) != len(set(entries)):
        raise BridgeError("duplicate entrypoint")
    for path in entries:
        valid_path(path)
    if manifest.get("context_owner") != "repository":
        raise BridgeError("repository must retain ownership of its local context")
    publication = manifest.get("publication")
    if not isinstance(publication, dict) or publication.get("mode") != "reviewed-pr":
        raise BridgeError("only reviewed-pr publication is supported")
    valid_path(publication.get("target", ""))
    sharing = manifest.get("sharing")
    if not isinstance(sharing, dict) or sharing.get("mode") != "references-only" or sharing.get("export_paths") != []:
        raise BridgeError("v0 allows references-only sharing; no automatic content export")
    if root is not None:
        root = root.resolve(strict=True)
        for path in entries:
            current = root
            for part in PurePosixPath(path).parts:
                current = current / part
                if current.is_symlink():
                    raise BridgeError(f"symlinked entrypoint: {path}")
            if not current.is_file() or not current.resolve().is_relative_to(root):
                raise BridgeError(f"entrypoint missing or outside root: {path}")
    return manifest


class GitHubReadOnly:
    def __init__(self, token: str):
        if not token:
            raise BridgeError("GITHUB_TOKEN or GH_TOKEN required for private repository discovery")
        self.token = token

    def get(self, endpoint: str) -> object:
        # No user-supplied URLs. Every request stays on the GitHub REST API origin.
        if not endpoint.startswith("/") or "://" in endpoint:
            raise BridgeError("invalid API path")
        req = urllib.request.Request(
            API + endpoint,
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "User-Agent": "mindport-repo-bridge/0.1",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            # Never report request headers or the credential.
            raise BridgeError(f"GitHub REST returned HTTP {exc.code} for {endpoint.split('?')[0]}") from None
        except urllib.error.URLError:
            raise BridgeError("GitHub REST unavailable") from None

    def pages(self, path: str, maximum: int = 20) -> list[dict]:
        # Predictable page navigation rather than following arbitrary Link URLs.
        output = []
        for page in range(1, maximum + 1):
            sep = "&" if "?" in path else "?"
            batch = self.get(f"{path}{sep}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise BridgeError("expected a GitHub repository collection")
            output.extend(batch)
            if len(batch) < 100:
                return output
        raise BridgeError("pagination limit exceeded; collection incomplete")

    def root(self, full_name: str, branch: str) -> list[str]:
        valid_repo(full_name)
        if not isinstance(branch, str) or not branch:
            raise BridgeError("repository default branch missing")
        route = urllib.parse.quote(branch, safe="")
        data = self.get(f"/repos/{full_name}/git/trees/{route}")
        if not isinstance(data, dict) or not isinstance(data.get("tree"), list):
            raise BridgeError("invalid Git tree")
        return sorted({t["path"] for t in data["tree"] if t.get("type") == "blob"})

    def manifest(self, full_name: str, branch: str) -> dict:
        route = urllib.parse.quote(branch, safe="")
        data = self.get(f"/repos/{full_name}/contents/.context-hub.json?ref={route}")
        if not isinstance(data, dict) or data.get("encoding") != "base64":
            raise BridgeError("invalid remote manifest")
        try:
            content = base64.b64decode(data["content"], validate=False)
            manifest = json.loads(content.decode("utf-8"))
        except (ValueError, TypeError, UnicodeDecodeError, KeyError) as exc:
            raise BridgeError("invalid remote manifest content") from exc
        return validate_manifest(manifest)


def summarize(repo: dict, root: list[str] | None = None, manifest: dict | None = None) -> dict:
    full_name = valid_repo(repo["full_name"])
    docs = sorted(set(root or []).intersection(ENTRYPOINTS))
    status = (
        "manifest-linked" if manifest else
        "route-detected" if root is not None and ("AGENTS.md" in docs or "CONTEXT.md" in docs) else
        "readme-only" if root is not None and docs else
        "no-context-docs" if root is not None else "uninspected"
    )
    visibility = ("private" if repo.get("private") is True or repo.get("visibility") == "private"
                  else "public" if repo.get("private") is False or repo.get("visibility") == "public"
                  else "unknown")
    return {
        "repository": full_name,
        "url": f"https://github.com/{full_name}",
        "default_branch": repo.get("default_branch"),
        "visibility": visibility,
        "fork": repo.get("fork"),
        "archived": repo.get("archived"),
        "entrypoints": docs,
        "bridge_status": status,
        "manifest": manifest,
        "authority": "source-repository",
        "inspection_error": None,
    }


def scan_online(client: GitHubReadOnly, orgs: list[str], inspect_roots: bool = True) -> list[dict]:
    repos = client.pages("/user/repos?affiliation=owner")
    for org in sorted(set(orgs)):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", org):
            raise BridgeError("invalid organization")
        repos += client.pages(f"/orgs/{org}/repos?type=all")
    seen = {}
    for repo in repos:
        if not isinstance(repo, dict):
            continue
        name = repo.get("full_name")
        if not isinstance(name, str) or not REPO_RE.fullmatch(name):
            continue
        seen[name.casefold()] = repo
    result = []
    for repo in sorted(seen.values(), key=lambda r: r["full_name"].casefold()):
        root = None
        manifest = None
        error = None
        if inspect_roots:
            try:
                root = client.root(repo["full_name"], repo.get("default_branch"))
                if ".context-hub.json" in root:
                    manifest = client.manifest(repo["full_name"], repo["default_branch"])
                    if manifest["repository"].casefold() != repo["full_name"].casefold():
                        raise BridgeError("manifest repository mismatch")
            except BridgeError as exc:
                error = str(exc)
        item = summarize(repo, root, manifest)
        item["inspection_error"] = error
        if error:
            item["bridge_status"] = "inspection-failed"
        result.append(item)
    return result


def scan_snapshot(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("repositories"), list):
        raise BridgeError("expected a repositories array in snapshot")
    result = []
    for r in data["repositories"]:
        name = valid_repo(r["full_name"])
        result.append(summarize({"full_name": name, "visibility": r.get("visibility"),
                                 "fork": r.get("fork"), "archived": r.get("archived"),
                                 "default_branch": r.get("default_branch")}))
    return sorted(result, key=lambda x: x["repository"].casefold())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init", help="Create an opt-in manifest in a local repo")
    init.add_argument("--root", type=Path, default=Path("."))
    init.add_argument("--repo", required=True)
    check = sub.add_parser("check", help="Validate repo manifest and local entrypoints")
    check.add_argument("--root", type=Path, default=Path("."))
    scan = sub.add_parser("scan", help="Discover repository metadata, read-only")
    group = scan.add_mutually_exclusive_group(required=True)
    group.add_argument("--snapshot", type=Path)
    group.add_argument("--github", action="store_true")
    scan.add_argument("--org", action="append", default=[])
    scan.add_argument("--no-root-inspection", action="store_true")
    args = parser.parse_args()
    try:
        if args.cmd == "init":
            root = args.root.resolve(strict=True)
            if not root.is_dir() or root.is_symlink():
                raise BridgeError("root must be a real directory")
            target = root / ".context-hub.json"
            if target.exists() or target.is_symlink():
                raise BridgeError("manifest already exists; refusing to overwrite")
            entrypoints = [p for p in ENTRYPOINTS if (root / p).is_file() and not (root / p).is_symlink()]
            if not entrypoints:
                raise BridgeError("no valid local entrypoint exists")
            manifest = validate_manifest(default_manifest(args.repo, entrypoints), root)
            target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"created": str(target), "entrypoints": entrypoints}))
        elif args.cmd == "check":
            root = args.root.resolve(strict=True)
            data = json.loads((root / ".context-hub.json").read_text(encoding="utf-8"))
            result = validate_manifest(data, root)
            print(json.dumps({"valid": True, "repository": result["repository"],
                              "entrypoints": result["entrypoints"]}))
        else:
            if args.github:
                token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
                result = scan_online(GitHubReadOnly(token or ""), args.org,
                                     not args.no_root_inspection)
                source = "github-authenticated-read"
            else:
                result = scan_snapshot(args.snapshot)
                source = "existing-snapshot-no-live-check"
            print(json.dumps({
                "schema": SCAN_SCHEMA, "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "source": source, "count": len(result), "repositories": result,
                "note": "This discovery output is not approval to publish private data or execute code.",
            }, indent=2))
    except (BridgeError, OSError, ValueError, TypeError) as exc:
        print(f"repo-bridge: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
