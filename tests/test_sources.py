import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mindport
import mindport_sources as sources


class SourceAdapterTests(unittest.TestCase):
    def test_chatgpt_retains_time_identity_and_roles(self):
        chats = [{"id": "c-77", "title": "Design research", "mapping": {
            "later": {"message": {"id": "m-2", "author": {"role": "assistant"},
                                  "create_time": 20, "content": {"parts": ["Second"]}}},
            "earlier": {"message": {"id": "m-1", "author": {"role": "user"},
                                    "create_time": 10, "content": {"parts": ["First"]}}},
            "tool": {"message": {"author": {"role": "tool"},
                                 "create_time": 15, "content": {"parts": ["Do not import"]}}},
        }}]
        records = sources.chatgpt(chats)
        self.assertEqual([r["text"] for r in records], ["First", "Second"])
        self.assertEqual([r["message_id"] for r in records], ["m-1", "m-2"])
        self.assertEqual(records[0]["source_id"], "c-77")
        self.assertEqual(records[0]["timestamp"], 10)
        self.assertEqual(records[0]["provider"], "chatgpt")

    def test_claude_uses_typed_text_blocks_avoids_tool_placeholder(self):
        conversations = [{"uuid": "cl-1", "name": "New idea", "chat_messages": [
            {"uuid": "a", "sender": "human", "created_at": "2026-01-01T00:00:00Z",
             "text": "Build this", "content": [{"type": "text", "text": "Build this"}]},
            {"uuid": "b", "sender": "assistant",
             "text": "This block is not supported on your current device yet",
             "content": [{"type": "tool_use", "name": "search"},
                         {"type": "text", "text": "Found three papers"}]},
            {"uuid": "c", "sender": "assistant", "text": "This block is not supported on your current device yet"},
        ]}]
        records = sources.claude(conversations)
        self.assertEqual([r["text"] for r in records], ["Build this", "Found three papers"])
        self.assertEqual(records[0]["timestamp"], "2026-01-01T00:00:00Z")
        self.assertEqual(records[1]["provider"], "claude")

    def test_jsonl_is_an_explicit_contract(self):
        raw = ('{"source":"study","role":"note","text":"Observation",'
               '"source_id":"doc1","message_id":"para2"}\n')
        records = sources.jsonl(raw)
        self.assertEqual(records[0]["message_id"], "para2")
        with self.assertRaisesRegex(ValueError, "line 1"):
            sources.jsonl('{"hello":"world"}\n')
        with self.assertRaisesRegex(ValueError, "line 2"):
            sources.jsonl(raw + "{broken")

    def test_directory_is_explicit_and_symlinks_rejected(self):
        with TemporaryDirectory() as root:
            base = Path(root)
            (base / "sub").mkdir()
            (base / "sub" / "paper.md").write_text("A finding", encoding="utf-8")
            (base / "private.txt").write_text("not included", encoding="utf-8")
            records = sources.load(base, "markdown-dir")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["source"], "sub/paper.md")
            try:
                (base / "leak.md").symlink_to(base / "private.txt")
            except (OSError, NotImplementedError):
                return
            with self.assertRaisesRegex(ValueError, "symlink"):
                sources.load(base, "markdown-dir")

    def test_unknown_json_does_not_get_mislabeled(self):
        with TemporaryDirectory() as root:
            path = Path(root) / "MyActivity.json"
            path.write_text('[{"title":"Gemini activity but not full chat"}]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unknown"):
                sources.load(path, "auto")
            with self.assertRaises(ValueError):
                sources.load(path, "claude")

    def test_pack_roundtrip_with_source_attribution(self):
        with TemporaryDirectory() as root:
            source = Path(root) / "conversations.json"
            source.write_text(json.dumps([{"uuid": "chat-a", "name": "Notes", "chat_messages": [
                {"uuid": "message-a", "sender": "human", "text": "My research"}
            ]}]), encoding="utf-8")
            selected = mindport.build_pack(source, "claude", [1], False)
            self.assertEqual(len(mindport.validate(selected)), 1)
            self.assertEqual(selected["items"][0]["provider"], "claude")
            self.assertEqual(selected["items"][0]["source_id"], "chat-a")
            self.assertEqual(selected["items"][0]["message_id"], "message-a")
            self.assertEqual(
                selected["items"][0]["id"],
                mindport.build_pack(source, "auto", [1], False)["items"][0]["id"]
            )
            dest = Path(root) / "pack.json"
            mindport.save(dest, selected)
            self.assertEqual(mindport.validate(json.loads(dest.read_text())), selected["items"])

    def test_duplicate_ids_cannot_form_a_valid_pack(self):
        item = {"id": "same", "source": "A", "role": "note", "text": "X"}
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            mindport.validate({"schema": "mindport.context-pack.v1", "items": [item, dict(item)]})


if __name__ == "__main__":
    unittest.main()
