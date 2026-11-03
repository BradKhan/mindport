# Mindport roadmap

Mindport's destination is a **portable, person-owned intelligence layer**. ChatGPT export is the first tested source format, not the scope of the project. See [VISION.md](VISION.md).

## 0. Prove the handoff (current implementation branch)

- Local import of ChatGPT text conversations and Markdown notes
- Inspect, edit, select, best-effort redact, and export versioned context packs
- Local browser review and Python CLI
- Source attribution and deterministic tests

Gate: end-to-end verification with synthetic files, browser QA, independently reviewed privacy limitations. No external provider or model calls.

## 1. Broaden sources and strengthen consent

- Import adapters for Claude, Gemini, and other documented provider exports
- Markdown folders, Obsidian vaults, JSONL, research/document sources with explicit scope
- Preserve original source identifiers, timestamps, message ordering, permissions and links
- Sensitive-data review and validated context pack schema
- Clear difference between primary source material and machine-generated interpretation

Gate: tested source fixtures, lossless where feasible, explicit unsupported cases, reviewable disclosure.

## 2. Persistent, inspectable memory

- Local durable store with searchable history and user edits
- Corrections, provenance, deletion and bounded retention
- Deduplication and linked references without automatic claims of truth
- Evaluate SQLite FTS first; optional embeddings and temporal graph adapters after benchmarks

Gate: measurable recall, attribution, correction fidelity, deletion verification and no unauthorized disclosure.

## 3. Context portability across systems

- Task-scoped context compiler respecting recipient, purpose, time and token budget
- Model and agent handoff adapters with replaceable providers
- Open file and API contracts for applications and devices
- End-to-end evaluation across at least two distinct assistant runtimes

Gate: an independently reproducible task where relevant context transfers accurately without leaking unrelated personal material.

## 4. Private synchronization and deeper interoperability

- Optional encrypted sync between owner-controlled devices
- Local-first backup and recovery, vault portability
- Humetheus integration with replaceable models and independently governed context
- Organizational and multi-agent scopes only after an explicit permission model

Gate: threat model, cryptographic review, recovery drills, multi-device and permission-boundary testing.

## Constraints

No mandatory provider account, no silent ingestion, no external upload without explicit authorization, and no executing imported prompts. Keep raw personal exports out of public Git. Future capabilities must be labeled planned until independently demonstrated.
