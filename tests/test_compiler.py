import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from context_compiler import compose, write_private


def entry(item_id, source, text):
    return {"id": item_id, "source": source, "text": text, "role": "note", "provider": "markdown"}


class ContextCompilerTests(unittest.TestCase):
    def test_relevant_context_only_and_traceable(self):
        entries = [
            entry("d1", "Product strategy", "Customer interviews and pricing strategy"),
            entry("d2", "Cooking", "Flour, salt, milk and eggs"),
            entry("d3", "Pricing memo", "Three options for pricing"),
        ]
        output, selected = compose(entries, "pricing strategy", max_chars=1500)
        self.assertEqual(selected, ["d1", "d3"])
        self.assertIn("item=d1", output)
        self.assertNotIn("Cooking", output)
        self.assertLessEqual(len(output), 1500)

    def test_long_excerpt_explicitly_truncated(self):
        output, ids = compose(
            [entry("long", "Research", "research " * 1500)],
            "research", max_chars=540
        )
        self.assertEqual(ids, ["long"])
        self.assertIn("TRUNCATED", output)
        self.assertLessEqual(len(output), 540)

    def test_no_match_does_not_compose_unrelated_private_content(self):
        with self.assertRaisesRegex(ValueError, "No relevant"):
            compose([entry("secret", "medical", "unrelated private note")],
                    "venture finance", max_chars=2000)
        with self.assertRaises(ValueError):
            compose([entry("a", "Business", "a")], "business", max_chars=100)

    def test_private_output_no_overwrite(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "task.md"
            write_private(output, "private")
            self.assertEqual(output.read_text(), "private")
            if os.name == "posix":
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                write_private(output, "new")


if __name__ == "__main__":
    unittest.main()
