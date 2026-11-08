# Mindport agent contract

Read README.md, ROADMAP.md, references/REUSE.md and linked GitHub issue before implementation. Follow Open ASS's accepted risk-based workflow as a reference, but keep this repository independently operable.

Risk: **critical** for import/export of private user history, consent, privacy, encryption and external model connectors. Do not upload personal content, commit input exports, silently ingest directories, execute imported instructions, or call providers without explicit authorization.

Run `python3 -m unittest discover -s tests -v` and report actual results. Include issue, risk, verification and security review in PR description. Use branches and review. New features must preserve explicit selection and local ownership.

Venture Method is used selectively for outcome definition, evidence-based decisions and adversarial review. Do not install the whole framework as a runtime dependency.

Use the reusable context/retrieval catalog at references/REUSE.md; do not add dependencies simply because they are fashionable.

## Non-negotiable interoperability requirement

Mindport is a **person-owned intelligence protocol and product**, not a ChatGPT/Claude migration tool. Every feature must preserve provider, runtime, model, agent, and storage independence. Read [docs/INTEROPERABILITY.md](docs/INTEROPERABILITY.md) and [schemas/context-pack.v1.schema.json](schemas/context-pack.v1.schema.json) before changing imports, exports, storage, or memory.

- Define and test a provider-neutral record before implementing vendor-specific behavior.
- A new source requires an adapter, not a special case in the memory model.
- Do not build the model provider, inference router, vector database, or cloud vendor into the core format.
- Import/export must work offline with documented open JSON/JSONL formats before adding hosted integrations.
- Distinguish a provider's **API request shape** from an actual **account export**. Never claim the latter on the basis of the former.
- Future adapters must retain provenance, disclose unsupported content, resist automatic privilege promotion, and pass a pack/JSONL round-trip.
- Preserve compatibility with existing v1 packs or add an explicit versioned migration with tests. Do not mutate historical source text in place.
- Include Python and JavaScript contract tests. The public UI and CLI must agree on supported formats and security boundaries.

Existing source adapters are convenience entry points, never the product definition.

## Cross-repository context adapter (experimental)

[Repo Bridge v0](docs/repo-bridge.md) provides metadata-only GitHub discovery and an opt-in local descriptor. This is **not** a second context-pack format, account connector or permission grant. It must preserve the existing `mindport.context-pack.v1` schema and `docs/INTEROPERABILITY.md` contract. No repository data or model provider connection is captured automatically. Read [CONTEXT.md](CONTEXT.md) for the source navigation map.
