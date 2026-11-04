"""Provider-neutral message interchange adapters.

Consumes *text* from recognized API-shaped JSON records and Mindport packs.
API request/response formats are not the same thing as vendor account exports.
Unsupported tool calls, hidden reasoning and media are never converted to text.
"""
from __future__ import annotations


def _text(value):
    if isinstance(value, str):
        return value.strip()
    if not isinstance(value, list):
        return ""
    result = []
    for part in value:
        if not isinstance(part, dict):
            continue
        kind = part.get("type")
        # OpenAI-compatible, Anthropic, and Gemini typed text sections.
        if kind not in (None, "text", "input_text", "output_text"):
            continue
        text = part.get("text")
        if isinstance(text, str):
            result.append(text)
    return "\n".join(result).strip()


def _record(source, role, text, provider, source_id, message_id, timestamp=None):
    record = {
        "source": str(source), "role": role, "text": text,
        "provider": str(provider), "source_id": str(source_id),
        "message_id": str(message_id)
    }
    if timestamp is not None and isinstance(timestamp, (str, int, float)):
        record["timestamp"] = timestamp
    return record


def _messages(items, source, source_id, provider):
    if not isinstance(items, list) or not items:
        raise ValueError("A nonempty messages list is required")
    result = []
    for index, msg in enumerate(items, 1):
        if not isinstance(msg, dict):
            raise ValueError(f"Message {index} must be an object")
        role = {"human": "user", "model": "assistant"}.get(msg.get("role"), msg.get("role"))
        if role not in ("user", "assistant"):
            # System, developer and tool messages are deliberately outside the
            # owner-authored conversation record and are not silently promoted.
            continue
        content = msg.get("content")
        if content is None:
            content = msg.get("parts")
        text = _text(content)
        if not text:
            continue
        result.append(_record(
            source, role, text, provider, source_id,
            msg.get("id") or msg.get("uuid") or f"message-{index}",
            msg.get("timestamp", msg.get("created_at"))
        ))
    if not result:
        raise ValueError("No supported user or assistant text in messages")
    return result


def import_messages(data, fmt="messages"):
    """API-shaped JSON, never a claim of official account export compatibility.

    Supports: [{role, content}], {messages: [...]}, {input: [...]},
    {conversations: [{id, title, messages: [...]}]}.
    Google Gemini API: {contents: [{role: user|model, parts: [{text: ...}]}]}.
    """
    if fmt == "gemini-api":
        if not isinstance(data, dict) or not isinstance(data.get("contents"), list):
            raise ValueError("Gemini API requires a contents array")
        return _messages(data["contents"], data.get("title", "Gemini API conversation"),
                         data.get("id", "gemini-api"), "gemini-api")
    if isinstance(data, list):
        return _messages(data, "API message array", "api-message-array", "messages")
    if not isinstance(data, dict):
        raise ValueError("Expected a message array or a supported messages object")
    if isinstance(data.get("contents"), list):
        return import_messages(data, "gemini-api")
    if isinstance(data.get("conversations"), list):
        result = []
        if not data["conversations"]:
            raise ValueError("No conversations found")
        for index, conversation in enumerate(data["conversations"], 1):
            if not isinstance(conversation, dict) or not isinstance(conversation.get("messages"), list):
                raise ValueError(f"Conversation {index} must include messages")
            result.extend(_messages(
                conversation["messages"],
                conversation.get("title") or conversation.get("name") or f"Conversation {index}",
                conversation.get("id") or f"conversation-{index}",
                "messages"
            ))
        return result
    for key in ("messages", "input"):
        if isinstance(data.get(key), list):
            return _messages(data[key], data.get("title") or "API conversation",
                             data.get("id") or "api-messages", "messages")
    raise ValueError("No recognized messages, input, contents, or conversations array")


def import_pack(data):
    if not isinstance(data, dict) or data.get("schema") != "mindport.context-pack.v1":
        raise ValueError("Expected Mindport context-pack v1")
    items = data.get("items")
    if not isinstance(items, list):
        raise ValueError("Pack must contain items")
    result = []
    ids = set()
    for index, item in enumerate(items, 1):
        if (not isinstance(item, dict)
            or any(not isinstance(item.get(key), str) for key in ("id", "source", "role", "text"))
            or item["role"] not in ("user", "assistant", "note")):
            raise ValueError(f"Invalid pack item {index}")
        if item["id"] in ids:
            raise ValueError("Duplicate pack item IDs")
        ids.add(item["id"])
        row = _record(
            item["source"], item["role"], item["text"],
            item.get("provider") or "mindport",
            item.get("source_id") or item["source"],
            item.get("message_id") or item["id"],
            item.get("timestamp")
        )
        result.append(row)
    return result


def to_jsonl(pack):
    """An open, line-oriented interchange: one approved record per line.

    Carries provenance. It is not a provider-native memory-injection command.
    """
    import json
    if not isinstance(pack, dict) or pack.get("schema") != "mindport.context-pack.v1":
        raise ValueError("Not a Mindport v1 context pack")
    lines = []
    for index, item in enumerate(pack.get("items", []), 1):
        if (not isinstance(item, dict)
            or any(not isinstance(item.get(key), str) for key in ("source", "role", "text"))
            or item["role"] not in ("user", "assistant", "note")):
            raise ValueError(f"Invalid item {index}")
        row = {key: item[key] for key in
               ("source", "role", "text", "provider", "source_id", "message_id", "timestamp")
               if key in item}
        lines.append(json.dumps(row, ensure_ascii=False))
    return "\n".join(lines) + ("\n" if lines else "")
