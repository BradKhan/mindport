"""Contract tests for vendor-neutral API-like formats and JSONL exchange.

Synthetic fixtures only, no provider credentials or private user histories.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mindport
import mindport_sources
from mindport_interop import import_messages, import_pack, to_jsonl


class InteropTests(unittest.TestCase):
    def test_openai_compatible_messages(self):
        payload = {"id": "session-42", "messages": [
            {"role": "system", "content": "INTERNAL SYSTEM PROMPT"},
            {"role": "user", "id": "u-1", "content": [
                {"type": "text", "text": "My public question"},
                {"type": "image_url", "image_url": {"url": "https://example.invalid/picture"}}]},
            {"role": "tool", "content": "PRIVATE TOOL TRACE"},
            {"role": "assistant", "id": "a-1", "content": "Plain answer"},
        ]}
        entries = import_messages(payload)
        self.assertEqual([e["role"] for e in entries], ["user", "assistant"])
        self.assertEqual([e["text"] for e in entries], ["My public question", "Plain answer"])
        self.assertEqual(entries[0]["message_id"], "u-1")
        self.assertEqual(entries[0]["source_id"], "session-42")

    def test_ollama_style_and_anthropic_style_text(self):
        ollama = [{"role": "user", "content": "Local query"},
                  {"role": "assistant", "content": "Local response", "tool_calls": [{"name": "ignore"}]}]
        self.assertEqual([e["text"] for e in import_messages(ollama)],
                         ["Local query", "Local response"])
        anthropic = {"messages": [{"role": "assistant", "content": [
            {"type": "thinking", "thinking": "ignore"},
            {"type": "text", "text": "Visible response"}]}]}
        self.assertEqual(import_messages(anthropic)[0]["text"], "Visible response")

    def test_gemini_api_content_parts(self):
        contents = {"contents": [
            {"role": "user", "parts": [{"text": "First question"}, {"inline_data": {"mime_type": "image/png"}}]},
            {"role": "model", "parts": [{"text": "First answer"}]}]}
        entries = import_messages(contents, "gemini-api")
        self.assertEqual([e["role"] for e in entries], ["user", "assistant"])
        self.assertEqual(entries[0]["provider"], "gemini-api")
        self.assertEqual(entries[0]["text"], "First question")

    def test_multi_conversation_and_responses_input(self):
        data = {"conversations": [
            {"id": "c1", "title": "A", "messages": [{"role": "user", "content": "Alpha"}]},
            {"id": "c2", "title": "B", "messages": [{"role": "user", "content": "Beta"}]}]}
        self.assertEqual([x["source_id"] for x in import_messages(data)], ["c1", "c2"])
        self.assertEqual(import_messages({"input": [
            {"role": "user", "content": [{"type": "input_text", "text": "Question"}]}]})[0]["text"],
            "Question")

    def test_auto_detect_generic_messages_and_reject_unknown(self):
        with TemporaryDirectory() as d:
            path = Path(d) / "chat.json"
            path.write_text(json.dumps({"messages": [{"role": "user", "content": "Portable"}]}))
            records = mindport_sources.load(path, "auto")
            self.assertEqual(records[0]["provider"], "messages")
            selected = mindport.build_pack(path, "messages", [1], False)
            self.assertEqual(selected["items"][0]["text"], "Portable")
            path.write_text(json.dumps({"events": [{"type": "page-view"}]}))
            with self.assertRaisesRegex(ValueError, "Unknown"):
                mindport_sources.load(path, "auto")

    def test_pack_jsonl_round_trip_preserves_provider(self):
        with TemporaryDirectory() as d:
            source = Path(d) / "source.json"
            source.write_text(json.dumps({"contents": [
                {"role": "user", "parts": [{"text": "Portable user context"}]}]}))
            pack = mindport.build_pack(source, "gemini-api", [1], True)
            stream = to_jsonl(pack)
            out = Path(d) / "records.jsonl"
            out.write_text(stream)
            restored = mindport_sources.load(out, "jsonl")
            self.assertEqual(restored[0]["provider"], "gemini-api")
            self.assertEqual(restored[0]["text"], "Portable user context")
            pack_file = Path(d) / "pack.json"
            pack_file.write_text(json.dumps(pack))
            reread = mindport_sources.load(pack_file, "pack")
            self.assertEqual(reread[0]["provider"], "gemini-api")
            self.assertEqual(reread[0]["message_id"], pack["items"][0]["message_id"])
            self.assertEqual(len(import_pack(pack)), 1)

    def test_tools_and_system_never_become_user_records(self):
        with self.assertRaisesRegex(ValueError, "No supported"):
            import_messages({"messages": [
                {"role": "system", "content": "high priority"},
                {"role": "tool", "content": "secret"}]})
        with self.assertRaises(ValueError):
            import_messages({"messages": [{"role": "user", "content": [{"type": "image_url"}]}]})

    def test_text_and_ndjson_without_provider_accounts(self):
        with TemporaryDirectory() as folder:
            note = Path(folder) / "my-notes.txt"
            note.write_text("Locally owned knowledge", encoding="utf-8")
            self.assertEqual(mindport_sources.load(note, "auto")[0]["text"],
                             "Locally owned knowledge")
            nd = Path(folder) / "portable.ndjson"
            nd.write_text('{"source":"note","role":"note","text":"Reimported",'
                          '"provider":"personal-agent"}\n', encoding="utf-8")
            records = mindport_sources.load(nd, "auto")
            self.assertEqual(records[0]["provider"], "personal-agent")

    def test_cli_convert_only_selected_pack(self):
        with TemporaryDirectory() as d:
            source = Path(d) / "chat.json"
            source.write_text(json.dumps({"messages": [
                {"role": "user", "content": "Selected"},
                {"role": "assistant", "content": "Not selected"}]}))
            pack = mindport.build_pack(source, "messages", [1], False)
            pack_file = Path(d) / "pack.json"
            mindport.save(pack_file, pack)
            output = Path(d) / "records.jsonl"
            result = mindport.main(["convert", str(pack_file), "--to", "jsonl", "--output", str(output)])
            self.assertEqual(result, 0)
            rows = [json.loads(line) for line in output.read_text().splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["text"], "Selected")
            self.assertEqual(rows[0]["provider"], "messages")


if __name__ == "__main__":
    unittest.main()
