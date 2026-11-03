"""Strict, local-only source adapters for Mindport. No optional dependencies.

The supported JSON formats are explicitly recognized. Unknown shapes fail rather
than turning arbitrary fields into a fabricated conversation.
"""
from __future__ import annotations

import json
from pathlib import Path

MAX_BYTES = 30 * 1024 * 1024
MAX_NOTES = 500


def _text_parts(parts):
    if not isinstance(parts, list):
        return ""
    return "\n".join(part for part in parts if isinstance(part, str)).strip()


def _record(source, role, text, provider, source_id, message_id, timestamp=None):
    entry = {"source": str(source), "role": role, "text": text,
             "provider": provider, "source_id": str(source_id),
             "message_id": str(message_id)}
    if timestamp is not None and isinstance(timestamp, (str, int, float)):
        entry["timestamp"] = timestamp
    return entry


def chatgpt(data):
    if not isinstance(data, list) or not any(
        isinstance(c, dict) and isinstance(c.get("mapping"), dict) for c in data
    ):
        raise ValueError("Expected ChatGPT conversations.json with mapping objects")
    result = []
    for index, conversation in enumerate(data):
        if not isinstance(conversation, dict) or not isinstance(conversation.get("mapping"), dict):
            continue
        mapping = conversation["mapping"]
        title = conversation.get("title") or "Untitled"
        conversation_id = conversation.get("id") or f"conversation-{index + 1}"
        nodes = list(mapping.items())
        # The mapping is a graph, not a guaranteed chronological sequence.
        nodes.sort(key=lambda pair: (
            float((pair[1] or {}).get("message", {}).get("create_time") or 0)
            if isinstance(pair[1], dict) and isinstance(pair[1].get("message"), dict)
            else 0
        ))
        for node_id, node in nodes:
            if not isinstance(node, dict):
                continue
            msg = node.get("message")
            if not isinstance(msg, dict):
                continue
            author = msg.get("author")
            role = author.get("role") if isinstance(author, dict) else None
            if role not in ("user", "assistant"):
                continue
            body = msg.get("content")
            if not isinstance(body, dict):
                continue
            text = _text_parts(body.get("parts"))
            if not text:
                continue
            result.append(_record(title, role, text, "chatgpt",
                                  conversation_id, msg.get("id") or node_id,
                                  msg.get("create_time")))
    return result


def claude(data):
    if not isinstance(data, list) or not any(
        isinstance(c, dict) and isinstance(c.get("chat_messages"), list) for c in data
    ):
        raise ValueError("Expected Claude conversations.json with chat_messages arrays")
    result = []
    for index, conversation in enumerate(data):
        if not isinstance(conversation, dict) or not isinstance(conversation.get("chat_messages"), list):
            continue
        source_id = conversation.get("uuid") or conversation.get("id") or f"conversation-{index + 1}"
        title = conversation.get("name") or "Untitled"
        for n, msg in enumerate(conversation["chat_messages"]):
            if not isinstance(msg, dict):
                continue
            sender = msg.get("sender") or msg.get("role")
            role = {"human": "user", "user": "user", "assistant": "assistant"}.get(sender)
            if not role:
                continue
            blocks = msg.get("content")
            # Prefer typed text blocks: the plain 'text' field can contain
            # placeholder strings for unsupported tool or thinking blocks.
            typed = [block.get("text") for block in blocks
                     if isinstance(block, dict) and block.get("type") == "text"
                     and isinstance(block.get("text"), str)] if isinstance(blocks, list) else []
            text = "\n".join(typed).strip()
            if not text:
                plain = msg.get("text")
                text = plain.strip() if isinstance(plain, str) else ""
                if "This block is not supported on your current device yet" in text:
                    text = ""
            if text:
                result.append(_record(title, role, text, "claude",
                                      source_id, msg.get("uuid") or msg.get("id") or f"message-{n + 1}",
                                      msg.get("created_at")))
    return result


def jsonl(raw):
    result = []
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_no}: {exc.msg}") from exc
        if (not isinstance(row, dict)
            or row.get("role") not in ("user", "assistant", "note")
            or not isinstance(row.get("text"), str)
            or not isinstance(row.get("source"), str)):
            raise ValueError(f"JSONL line {line_no} requires source, role, text")
        if row["text"].strip():
            result.append(_record(row["source"], row["role"], row["text"].strip(),
                                  "jsonl", row.get("source_id") or row["source"],
                                  row.get("message_id") or f"line-{line_no}",
                                  row.get("timestamp")))
    return result


def _read(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Source must be a regular, non-symlink file")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Source file exceeds 30 MiB")
    return path.read_text(encoding="utf-8")


def markdown_directory(directory):
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError("Expected an existing, non-symlink Markdown directory")
    files = sorted(p for p in directory.rglob("*") if p.suffix.lower() in (".md", ".markdown"))
    if len(files) > MAX_NOTES:
        raise ValueError(f"Directory has more than {MAX_NOTES} Markdown files")
    total = 0
    items = []
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Refusing symlink or non-file: {path.name}")
        total += path.stat().st_size
        if total > MAX_BYTES:
            raise ValueError("Markdown directory exceeds 30 MiB total")
        text = _read(path).strip()
        if text:
            rel = path.relative_to(directory).as_posix()
            items.append(_record(rel, "note", text, "markdown",
                                 rel, rel))
    return items


def load(path: Path, kind: str):
    path = Path(path)
    if kind == "markdown-dir":
        return markdown_directory(path)
    raw = _read(path)
    if kind == "auto":
        if path.suffix.lower() in (".md", ".markdown"):
            kind = "markdown"
        elif path.suffix.lower() == ".jsonl":
            kind = "jsonl"
        else:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("Unknown JSON export format; specify a supported adapter")
            if any(isinstance(c, dict) and isinstance(c.get("mapping"), dict) for c in data):
                kind = "chatgpt"
            elif any(isinstance(c, dict) and isinstance(c.get("chat_messages"), list) for c in data):
                kind = "claude"
            else:
                raise ValueError("Unknown export format; only ChatGPT or Claude conversation JSON is detected")
            return chatgpt(data) if kind == "chatgpt" else claude(data)
    if kind == "markdown":
        return [_record(path.name, "note", raw, "markdown", path.name, path.name)] if raw.strip() else []
    if kind == "jsonl":
        return jsonl(raw)
    data = json.loads(raw)
    if kind == "chatgpt":
        return chatgpt(data)
    if kind == "claude":
        return claude(data)
    raise ValueError("Unsupported input format")
