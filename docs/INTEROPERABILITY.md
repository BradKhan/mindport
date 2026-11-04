# Interoperability is the product requirement

Mindport must never depend on one AI provider, chat UI, model API, storage engine, programming language, or agent framework. A native provider export is just one way to create records. The useful unit is a **person-approved, versioned context record with provenance**, not a vendor conversation object.

## Import compatibility

| Source shape | CLI | Browser | Important distinction |
| --- | --- | --- | --- |
| ChatGPT `conversations.json` with mapping | Yes | Yes | Source export, text messages only |
| Claude `conversations.json` with chat_messages | Yes | Yes | Source export, text messages only |
| `{messages: [{role, content}]}` or message array | Yes | Yes | OpenAI-compatible chat request or app log structure; includes Ollama-style message arrays |
| Anthropic Messages API-shaped text blocks | Yes | Yes | Text content within the neutral message adapter, **not** Claude account export |
| OpenAI Responses API-shaped `{input: [...]}` | Yes | Yes | Recognizes text message input, **not** full Responses activity, tool execution, or provider history |
| Gemini API `{contents: [{role, parts}]}` | Yes | Yes | API request shape, **not** Google Takeout/Gemini account history |
| `{conversations:[{id, title, messages}]}` | Yes | Yes | Portable structured conversation collection |
| Mindport v1 context pack JSON | Yes | Yes | Previously selected entries may be reselected and curated |
| Mindport JSONL records | Yes | Yes | Neutral line-delimited text records with optional provenance |
| Markdown notes | Yes | Yes | Single files |
| Plain UTF-8 text (`.txt`) | Yes | Yes | A text file becomes a user-curated note, not a fabricated conversation |
| Newline-delimited JSON (`.ndjson`) | Yes | Yes | Alias of the documented JSONL contract |
| Markdown/Obsidian folder | Yes | Files individually | CLI requires an explicitly chosen folder, rejects symlinks |

**Any application, model, or agent capable of writing the documented JSONL contract or a recognized message object can participate.** That is format interoperability, not a promise of a vendor connection or lossless import.

Grok, Perplexity, DeepSeek, Gemini web, Copilot, Cursor, LM Studio, vLLM, Open WebUI, Ollama, OpenRouter and other systems may produce different exports or logs. Until their real export variants are tested, do not claim native compatibility. Use the neutral record contract or an explicitly implemented adapter.

## Canonical ingestion

Adapters produce the same internal text-record contract:

```json
{
  "provider": "messages",
  "source": "Research session",
  "source_id": "session-id",
  "message_id": "message-id",
  "role": "user",
  "text": "Source text",
  "timestamp": "2026-11-01T10:00:00Z"
}
```

The output pack remains `mindport.context-pack.v1`. Its machine-readable contract is [schemas/context-pack.v1.schema.json](../schemas/context-pack.v1.schema.json) and its human-readable contract is [SCHEMA.md](SCHEMA.md). The `provider` field describes which import adapter was used or what upstream provenance was supplied, not proof of authenticity.

A record can originate from a model, local note, repository, API call, agent, browser session, or application. No downstream memory index should require an upstream vendor identity.

## Interchange

The least specialized exchange format is UTF-8 **JSONL**, one record per line containing `source`, `role`, `text`, plus optional `provider`, `source_id`, `message_id`, and `timestamp`.

```json
{"source":"Research","role":"note","text":"An approved observation","provider":"markdown","source_id":"research.md","message_id":"p1"}
```

Browser downloads include versioned pack JSON, provenance-aware Markdown, and JSONL. CLI can convert an already approved pack with:

```bash
python3 mindport.py convert private-pack.json --to jsonl --output portable-records.jsonl
python3 mindport.py pack portable-records.jsonl --format auto --select 1 --output curated-again.json
```

The CLI also accepts `--format messages`, `--format gemini-api`, `--format pack`, or `--format auto`. **No model is called. No memory is automatically installed into another provider.**

## Adapter contract for future integrations

1. Accept an explicitly approved file, folder, or authenticated source scope; no implicit account-wide capture.
2. Validate a documented input shape. Unknown JSON must fail visibly rather than be guessed.
3. Emit text records with source, role, provider, stable origin references where available, and authentic timestamps only.
4. Preserve the distinction between the original record and any derived summary. Never invent missing text or chronology.
5. Treat developer/system/tool instructions and hidden reasoning as **excluded** from personal knowledge imports unless a separate, explicitly reviewed record type is defined.
6. Skip unsupported media and binary blocks rather than representing them as imaginary text. Record coverage limitations publicly.
7. Do not upload, embed, summarize, or transmit imported content without a separate user authorization.
8. Keep all adapters replaceable and test at least one interoperable round-trip through JSONL and context-pack JSON.

Provider-specific packages belong at the edge, not in the canonical format, storage layer, context compiler, or user identity.

## Known boundaries

These adapters are **text-only**. Tool calls, media, system/developer content, private thinking blocks, files, and attachments are not yet preserved. A recognized message object may contain unsupported fields, which are not represented in the resulting text records. A fully lossless conversation archive is not currently supported.

API-shaped message objects are not standardized account exports. There is currently no official Gemini web conversation export adapter, no connected accounts, no automated synchronization, no proven provider-native memory injection, and no cross-provider semantic fidelity certification.

Sources for implementation patterns: [OpenAI chat format](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), [Anthropic Messages](https://platform.claude.com/docs/en/api/go/messages/create), [Ollama OpenAPI](https://github.com/ollama/ollama/blob/main/docs/openapi.yaml). Each provider can change its specifications.

## Acceptance criteria for every new adapter

Document the exact source version and format, include synthetic privacy-safe fixtures, test malformed/unsupported inputs, prove text and provenance output, prove JSONL/pack reimport, and state what was omitted. Keep existing supported formats functioning.
