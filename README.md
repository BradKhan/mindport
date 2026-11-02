# Mindport

**Take your context with you.**

A local-first, provider-independent utility for moving *selected* conversation excerpts and notes between AI assistants. You choose what travels. No cloud account, model API key, or external dependency is needed for the CLI.

## What works in this initial slice

- Inspect a ChatGPT `conversations.json` export or a Markdown note, locally.
- Explicitly select entries to include. No bulk automatic import into a provider.
- Apply best-effort secret redaction, plus optional email and phone redaction.
- Save a versioned JSON context pack with source attribution and stable per-source identifiers.
- Search the resulting pack locally and export a readable Markdown handoff for another assistant.

**Important:** Mindport cannot grant another provider automatic memory access. Importing data does not prove understanding, long-term retention, or deletion from third-party systems. Redaction is heuristic; inspect every export before sharing.

## Local visual workspace

Open `ui/index.html` directly in a modern browser, or serve the `ui/` directory from `localhost` using a local static file server. The workspace supports ChatGPT JSON or Markdown notes, manual selection, editing, redacted preview, and JSON/Markdown downloads. Nothing is selected automatically. No account, external JavaScript, network API, or server is required. Imported text is rendered through text-only DOM insertion.

**Privacy:** Imported content remains in browser-tab memory while the page is open. Automatic redaction is incomplete. Review every export before sharing it. Browser download permissions differ from CLI file permissions. Large files can be slow even below 30 MiB.

## Run

Python 3.11+, no pip dependencies:

```bash
python3 mindport.py inspect ~/Downloads/conversations.json --format chatgpt
python3 mindport.py pack ~/Downloads/conversations.json --format chatgpt --select 1 3 8 --redact-personal --output private-pack.json
python3 mindport.py show private-pack.json
python3 mindport.py search private-pack.json "product strategy"
python3 mindport.py export private-pack.json --output handoff.md
python3 -m unittest discover -s tests -v
```

Files are written with owner-only POSIX permissions where supported. Treat context packs as sensitive even after redaction. Export only to locations you control and keep them out of Git; `.gitignore` excludes common generated names.

## Project direction

The primary user outcome is: **Move useful, personally selected AI context across assistants with clear provenance and control over disclosure.**

The CLI and browser-based review interface implement the initial local workflows. Next: browser-level accessibility and security tests, better duplicate detection, additional provider adapters, pack validation and integrity checks, encryption, and cross-assistant retrieval evaluation.

Design principle: separate **source capture**, **user approval**, **context composition**, and **recipient-specific handoff**. Never silently summarize people's history into asserted facts. Source text can contain untrusted instructions.

See [ROADMAP.md](ROADMAP.md), [AGENTS.md](AGENTS.md), and [references/REUSE.md](references/REUSE.md). All proposed features beyond the CLI remain unimplemented.

## Relationship to other projects

Mindport is a standalone experiment aligned with Humetheus, not an installed dependency of Humetheus. The project selectively borrows development practices from [Open ASS](https://github.com/BradKhan/open-ASS) and product methods from [Venture Method](https://github.com/cyberagencyorg/venturemethod). Upstream references are linked rather than copied.
