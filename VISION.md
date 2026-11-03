# Mindport: product direction

## The proposition

**Intelligence should be portable, persistent, inspectable, and owned by the person who accumulated it.**

An AI conversation export solves one small part of this problem. The larger problem is continuity across models, agents, software, devices, and time.

Mindport aims to become a user-controlled **memory and context substrate**, accessible through open formats and replaceable adapters. It should remain useful even when a model provider disappears, an application changes its API, or a person decides to move everything elsewhere.

## What belongs in a portable intelligence system

| Source | Examples | Why it matters |
| --- | --- | --- |
| Conversations | ChatGPT, Claude, Gemini, Grok, Perplexity, Copilot, local assistants | Reasoning history, corrections, preferences, decisions |
| Knowledge | Markdown/Obsidian, documents, papers, annotations, PDFs | Research and authored material |
| Activity | Browser research, bookmarks, saved links, authorized social saves | Source trails and developing interests |
| Work | Repositories, issues, product specifications, tasks, meeting notes | Projects, decisions, dependencies and commitments |
| Agent activity | Runs, tool calls, results, reviews, memory updates | What an assistant did, with evidence |
| Media | Images, audio, video, transcripts | Knowledge beyond text |

These are **targets**, not implemented adapters. Permissions and source availability differ. Collection must be explicit and lawful.

## Intended architecture

```text
User-approved sources
        |
        v
Import adapters -> source snapshots and provenance
        |
        v
Normalized records -> edits, corrections, version history
        |
        +-> searchable local index (start with lexical search)
        +-> optional structured/temporal graph
        +-> optional embeddings and other retrieval engines
        |
        v
Context compiler: purpose, permissions, relevance, token budget
        |
        v
Recipient adapters: model / agent / application / device
        |
        v
Visible handoff and audit receipt
```

Key rules:

1. **Sources remain distinguishable from interpretations.** A statement made in a conversation is not automatically a verified fact. Retain source IDs, timestamps when available, and exact excerpts.
2. **The owner can inspect and correct memory.** Support revisions, deletion, and provenance. Never make an invisible, irreversible summary the canonical record.
3. **Context is selected per task.** A provider or agent receives only authorized relevant material. Do not send a lifetime of history to answer a simple question.
4. **Models and stores are replaceable.** Begin with plain files and SQLite full-text retrieval. Graphiti, Mem0, pgvector and similar components are optional only after comparison against a simpler baseline.
5. **Privacy is architectural.** Local-first by default; consent for source access and recipient disclosure; protection of secrets; encrypted sync only after review. Imported prompts are data, not authority.
6. **Export must remain viable.** Formats, schemas, and recipient adapters should be documented and independently implementable.

## Delivery sequence

**Current prototype:** manual ChatGPT/Markdown import, explicit selection and editing, basic redaction, local JSON and Markdown export, CLI search. No background capture, persistent memory engine, or external provider access.

**Next:** additional format adapters with synthetic fixtures, source metadata and identity, schema validation, redaction review and recipient-scoped packs.

**Then:** persistent local index and task-aware retrieval, provenance-aware correction, duplicate reconciliation, token-budget context compilation, cross-assistant evaluation.

**Later:** optional temporal graphs, private synchronization between devices, agent protocol adapters, source-specific permissions, shared organizational contexts with strict access boundaries.

## Proof, not promises

Evaluate with consented or synthetic histories. Measure whether a new assistant can accurately use relevant prior knowledge, cite its source, obey disclosure boundaries, avoid unrelated private data, and reduce repeated setup. Compare each new technique with plain text, local search and explicit human selection.

The unit of progress is an independently reproducible user outcome, not the number of supported providers or indexed records.

## Related projects

Mindport is the portability, curation and context interface. [Humetheus](https://github.com/BradKhan) is the broader ambition for private, user-owned intelligence, model routing and agent workflows. [Open ASS](https://github.com/BradKhan/open-ASS) supplies engineering practices and context routing; [Venture Method](https://github.com/cyberagencyorg/venturemethod) supports product discovery and evaluation.

The projects can interoperate without becoming mandatory dependencies of one another.
