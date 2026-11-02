# Reusable components and decision record

This is a source-linked shortlist, not an assertion that dependencies were installed or evaluated in this application.

## Applied during this first slice

- [Open ASS](https://github.com/BradKhan/open-ASS): scoped context routing, risk classification, agent handoff, verification-before-completion and provenance-oriented conventions. Adapted as project guidance; framework code was not copied.
- [Venture Method ADOPT](https://github.com/cyberagencyorg/venturemethod/blob/main/ADOPT.md): selective adoption instead of importing an entire methodology; product question and staged proof criteria.
- [Stack Mutiny](https://github.com/BradKhan/bradkhan/tree/main/composable-internet/stack-mutiny): find skills only when needed. No bulk installation.
- Python standard library: JSON ingestion, explicit selection, basic redaction, filesystem safety and unit tests.

## Candidates for later evaluation

| Source | Purpose | Integration decision |
| --- | --- | --- |
| [Context7](https://github.com/upstash/context7) | Current programming-library documentation for coding agents | Development-time only, not user-memory retrieval |
| [Graphify](https://github.com/)** | Ambiguous repository name; choose a specific canonical project after verification | No dependency until ownership, license and accuracy are checked |
| [Graphiti](https://github.com/getzep/graphiti) | Temporal knowledge graph and graph memory | Experiment behind optional adapter, never mandatory |
| [Mem0](https://github.com/mem0ai/mem0) | Memory extraction and retrieval | Benchmark for extraction quality and data portability |
| [Letta](https://github.com/letta-ai/letta) | Stateful agent memory design | Architecture reference and comparative tests |
| [pgvector](https://github.com/pgvector/pgvector) | Vector search on PostgreSQL | Optional later storage adapter |
| [Obsidian](https://obsidian.md/) | Locally owned Markdown knowledge | Import/export interoperability target |
| [LiteLLM](https://github.com/BerriAI/litellm) | Model routing | Only when actual provider connector tests exist |

**Graphify is unresolved** because the short name matches different tools. Do not guess at a canonical source or install an unrelated package.

## Context efficiency contract

Select data at three separate levels: relevant source, relevant excerpt, and recipient-specific budget. Keep provenance on every selected item. Begin with deterministic local keyword search before adding embeddings or graph extraction. Evaluate whether each additional component improves source attribution, recall, and privacy relative to complexity. Never load the entire user's history into agent context by default.
