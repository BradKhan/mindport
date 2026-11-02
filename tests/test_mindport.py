import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mindport


class MindportTests(unittest.TestCase):
    def test_selected_only_and_redaction(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "notes.md"
            src.write_text("Contact person@example.com and token sk-abcdefghijklmnopqrstuvwxyz1234", encoding="utf-8")
            pack = mindport.build_pack(src, "markdown", [1], True)
            self.assertEqual(len(pack["items"]), 1)
            text = pack["items"][0]["text"]
            self.assertNotIn("person@example.com", text)
            self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz1234", text)
            self.assertIn("[REDACTED_EMAIL]", text)
            self.assertIn("[REDACTED_SECRET]", text)

    def test_reject_unselected_or_duplicate(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "notes.md"
            src.write_text("my data", encoding="utf-8")
            for select in ([], [1, 1], [2]):
                with self.assertRaises(ValueError):
                    mindport.build_pack(src, "markdown", select, False)

    def test_chatgpt_extract_and_validate(self):
        data = [{"title": "Research", "mapping": {
            "one": {"message": {"author": {"role": "user"}, "content": {"parts": ["hello"]}}},
            "two": {"message": {"author": {"role": "tool"}, "content": {"parts": ["hidden"]}}},
        }}]
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "conversations.json"
            src.write_text(json.dumps(data), encoding="utf-8")
            pack = mindport.build_pack(src, "chatgpt", [1], False)
            self.assertEqual(mindport.validate(pack)[0]["text"], "hello")
            self.assertEqual(len(mindport.load_source(src, "chatgpt")), 1)

    def test_no_overwrite(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "pack.json"
            mindport.save(path, {"schema": "mindport.context-pack.v1", "items": []})
            with self.assertRaises(FileExistsError):
                mindport.save(path, {"schema": "mindport.context-pack.v1", "items": []})

    def test_invalid_pack(self):
        with self.assertRaises(ValueError):
            mindport.validate({"schema": "wrong", "items": []})


if __name__ == "__main__":
    unittest.main()
