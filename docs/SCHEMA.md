# Context pack v1

Mindport's smallest interoperable object is a file containing **explicitly selected** excerpts. The format is JSON, UTF-8, versioned as `mindport.context-pack.v1`. It is not a claim that the receiving model has installed or retained memory.

```json
{
  "schema": "mindport.context-pack.v1",
  "privacy": {
    "local_only": true,
    "personal_redaction": true,
    "secret_redaction": "best_effort",
    "explicit_selection": true
  },
  "items": [
    {
      "id": "local-entry-id",
      "source": "Research conversation",
      "role": "user",
      "text": "An approved excerpt",
      "provider": "claude",
      "source_id": "conversation-id",
      "message_id": "message-id",
      "timestamp": "2026-10-01T00:00:00Z",
      "origin_index": 1
    }
  ]
}
```

## Required fields

`schema` and `items` are required at the root. Each item requires string fields `id`, `source`, `role`, `text`. Supported roles are `user`, `assistant`, and `note`. IDs must be unique within a pack. Other properties are optional for backwards compatibility with first-generation packs.

## Provenance

`provider` identifies the adapter used to parse the input, not proof of authenticity. `source_id` and `message_id` preserve identifiers from the source where available; generated fallback identifiers are not authoritative. `timestamp` is carried as published, string or number, without inventing missing dates. `origin_index` is the one-based position in the inspected source list, not a universal conversation order.

Imported conversations may contain branches or missing parts. File formats change. Unsupported attachments, thinking blocks, tool traffic, and multimedia are not silently synthesized into conversation text.

## Export behavior

A context pack is local and unencrypted. Filename and item metadata can contain personal information. Best-effort redaction applies to selected text and selected provenance fields, but cannot guarantee detection of secrets or indirect identifiers. The browser requires an explicit full-selection review before download. The CLI requires explicit indexes. Recipients may still process source text as instructions despite the handoff disclaimer.

Python CLI `id` values are deterministic UUIDv5 identifiers derived from source identity. The browser uses a lightweight deterministic fingerprint for display, **not** a cryptographic integrity check. Neither certifies authenticity. Cryptographic receipts, encryption, corrections, and audited migrations are future work.

The browser and Python parsers can read the versioned file where supported. The CLI currently reads packs with `show`, `search`, `export`, and `compose`; the browser can re-import a pack for further curation. Both preserve the v1 schema.
