"""Mindport repository bridge behavior, offline, no GitHub credits or network."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.repo_bridge import (BridgeError, default_manifest, validate_manifest,
                               valid_path, scan_snapshot, scan_online, summarize)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "AGENTS.md").write_text("# agent contract\n")
        (self.root / "CONTEXT.md").write_text("# scoped context\n")
        self.m = default_manifest("BradKhan/mindport", ["AGENTS.md", "CONTEXT.md"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_manifest_passes_with_real_files(self):
        self.assertEqual(validate_manifest(self.m, self.root)["schema"], "mindport.repo-bridge.v0")

    def test_no_implicit_export_or_pub_without_review(self):
        for key, value in [
            ("sharing", {"mode": "automatic", "export_paths": ["private/docs.md"]}),
            ("sharing", {"mode": "references-only", "export_paths": ["AGENTS.md"]}),
            ("publication", {"mode": "auto-push", "target": "inbox/"})]:
            m = json.loads(json.dumps(self.m))
            m[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(BridgeError):
                validate_manifest(m)

    def test_traversal_duplicates_symlink_missing_denied(self):
        for path in ["../secrets.md", "/etc/passwd", "AGENTS.md/../other", "private/data.md", "./AGENTS.md", "A\\B"]:
            with self.assertRaises(BridgeError):
                valid_path(path)
        m = dict(self.m, entrypoints=["AGENTS.md", "AGENTS.md"])
        with self.assertRaises(BridgeError):
            validate_manifest(m, self.root)
        (self.root / "CONTEXT.md").unlink()
        (self.root / "CONTEXT.md").symlink_to(self.root / "AGENTS.md")
        with self.assertRaises(BridgeError):
            validate_manifest(self.m, self.root)

    def test_reject_nonexistent_and_repo_mismatch(self):
        m = dict(self.m, entrypoints=["AGENTS.md", "MISSING.md"])
        with self.assertRaises(BridgeError):
            validate_manifest(m, self.root)
        m = dict(self.m, repository="not-a-repo")
        with self.assertRaises(BridgeError):
            validate_manifest(m, self.root)


class DiscoveryTests(unittest.TestCase):
    def test_snapshot_is_explicitly_uninspected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "repos.json"
            p.write_text(json.dumps({"repositories":[
                {"full_name": "BradKhan/mindport", "visibility": "public"},
                {"full_name": "BradKhan/sovereign-spine", "visibility": "private"},
                {"full_name": "cyberagencyorg/ca-brand"},
            ]}))
            records = scan_snapshot(p)
            self.assertEqual(len(records), 3)
            self.assertEqual(records[1]["bridge_status"], "uninspected")
            self.assertEqual(records[1]["visibility"], "private")
            self.assertEqual(records[2]["visibility"], "unknown")
            self.assertIsNone(records[2]["fork"])

    def test_existing_repo_with_agents_is_compatible_without_manifest(self):
        repo = {"full_name": "BradKhan/humanscaled", "private": True}
        item = summarize(repo, ["AGENTS.md", "CONTEXT.md", "README.md"])
        self.assertEqual(item["bridge_status"], "route-detected")
        self.assertEqual(item["authority"], "source-repository")
        self.assertIsNone(item["manifest"])

    def test_online_discovery_deduplicates_and_preserves_error(self):
        class Fake:
            def pages(self, path):
                if path.startswith("/user/"):
                    return [{"full_name": "BradKhan/mindport", "default_branch": "main", "private": False}]
                return [{"full_name": "BradKhan/mindport", "default_branch": "main", "private": False},
                        {"full_name": "cyberagencyorg/ca-os", "default_branch": "main", "private": True}]
            def root(self, name, branch):
                if name.startswith("cyberagencyorg"):
                    raise BridgeError("GitHub REST returned HTTP 403 for root")
                return ["AGENTS.md", ".context-hub.json"]
            def manifest(self, name, branch):
                return default_manifest(name, ["AGENTS.md"])
        records = scan_online(Fake(), ["cyberagencyorg"])
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["bridge_status"], "manifest-linked")
        self.assertEqual(records[1]["bridge_status"], "inspection-failed")
        self.assertIn("403", records[1]["inspection_error"])


if __name__ == "__main__":
    unittest.main()
