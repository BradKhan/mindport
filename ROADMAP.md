# Roadmap and delivery gates

## Stage 0: Local context portability (this PR)

User can inspect selected source records, select entries, optionally redact personal fields, export JSON and Markdown, and run deterministic tests. No inference or network dependency.

Gate: passing unit tests, no invented provider support, documented limitations, review of exported content, permissions and copy controls.

## Stage 1: Safer import and curation

- [ ] Provider adapters: Claude, Gemini, Markdown directories, JSONL with explicit format mapping.
- [ ] Preserve message timestamp, original conversation identity, and order.
- [ ] Interactive local selection and correction, deletion preview, and provenance view.
- [ ] Redaction review, sensitive-content warnings, encrypted output with audited library.
- [ ] Pack migration and round-trip tests across versions.

## Stage 2: Useful cross-provider retrieval

- [ ] Task-based context pack selection within explicit token budgets.
- [ ] Local full-text retrieval first; optional graph and semantic components only when measured to improve tasks.
- [ ] Recipient-specific export adapters and transparent import instructions.
- [ ] Repeatable evaluations: recall, attribution, leakage, usefulness and context cost.
- [ ] User can edit or delete locally stored memory and independently verify deletion.

## Stage 3: Humetheus interoperability

- [ ] Standard ingestion and export API, replaceable retrieval backend, provider-agnostic context compiler.
- [ ] Runtime policies, consent scopes, and portable memory bundles.
- [ ] Local-first UI and optional encrypted backup selected by the owner.

## Scope discipline

Do not claim provider memory import APIs or automatic revocation. Do not train on user data. No analytics, telemetry, remote storage, or execution of imported text. Capture only approved inputs. Keep original data out of public repositories.
