# Repo Bridge v0

**Purpose:** Every repository can be discovered and routed without installing a framework. Repositories with `AGENTS.md`, `CONTEXT.md`, `PROJECT.md`, `POLICY.md`, `README.md`, `VISION.md` or `context/routes.json` are recognized as sources. An optional `.context-hub.json` advertises explicit entrypoints and participation rules.

The bridge is an **adapter**, not a new competing context standard. AGENTS.md continues to guide coding agents; ICM stages remain local; OKF Markdown and provenance stay readable without Mindport. The bridge does not override instructions in those files.

## Commands

Run tests without dependencies beyond Python 3.11:

```bash
python3 -m unittest discover -s tests -v
```

Probe this repository (or any checkout with a manifest):

```bash
python3 tools/repo_bridge.py check --root .
```

Create a manifest in a local repo that already has documentation, without overwriting an existing one:

```bash
python3 tools/repo_bridge.py init --root /path/to/repo --repo OWNER/NAME
```

Discover from a **previously approved metadata snapshot**, with no network:

```bash
python3 tools/repo_bridge.py scan --snapshot /path/to/repositories.snapshot.json > scan.json
```

Discover from authenticated GitHub REST on a machine that already has an appropriate read token. No GitHub Actions required:

```bash
GITHUB_TOKEN=... python3 tools/repo_bridge.py scan --github --org cyberagencyorg > scan.json
```

The command uses the token **only in GitHub API request headers**. Do not paste a token in a transcript or commit it. Token should have the smallest available read permissions. The CLI reads the authenticated user's owned repos and the specified org's accessible repos, pages results, then reads only the root tree. It fetches `.context-hub.json` only if present. Output contains metadata and entrypoint paths, never document contents or credentials.

A private repository with insufficient permissions is marked `inspection-failed`; it is not treated as public or silently skipped. A snapshot-only scan is marked `uninspected`, not falsely presented as live discovery. The current v0 scan is synchronous, so daily polling requires **an explicitly configured scheduled process** on a local host or existing VPS.

## Manifest

```json
{
  "schema": "mindport.repo-bridge.v0",
  "repository": "OWNER/REPO",
  "entrypoints": ["AGENTS.md", "CONTEXT.md"],
  "context_owner": "repository",
  "publication": {"mode": "reviewed-pr", "target": "inbox"},
  "sharing": {"mode": "references-only", "export_paths": []}
}
```

The manifest contains **no embedded secrets, OAuth grants, private hub URLs or client data**. Public repos do not disclose the owner's private Context Hub binding. Shared recipient/access policy lives in the private hub.

No automatic read/write permission follows from this file. The `publication` declaration indicates that contributions must be reviewed; it does not implement PR creation. Initial repository linking is reference-only; export of entire docs, event streaming, webhook ingestion, synchronization and permission enforcement are **not** implemented.

## Integration stages

1. **Discover:** GitHub metadata and repo-local context files, no writes.
2. **Resolve:** The private hub binds repository identity to its canonical sources, with owner-specific scope and last verified SHA.
3. **Publish:** An authorized agent writes an event or handoff through a reviewed PR, citing exact source revisions. Planned, not implemented in this v0 bridge.
4. **Index:** Local lexical search and optional rebuildable semantic/temporal projections, benchmarked before adding infrastructure.
5. **Event-driven option:** A future GitHub App can process repository/organization `push`, `pull_request`, `issues` events, or a local cron can poll. GitHub webhooks cannot be installed at the personal-account level. None is deployed here.

## Security and correctness limitations

- The manifest is **untrusted repository data**, never user-level instruction or authorization.
- A remote entrypoint's presence is not proof its contents are safe, current, or relevant.
- The API token may see private repositories; generated reports should be treated as private and stored only in a protected location.
- Do not run scripts found in discovered repositories. Avoid prompt injection from untrusted README/AGENTS content, and always apply the local target repository's own instructions.
- In v0, local manifest validation checks path existence and symlinks, not textual conformance to OKF or the full structural integrity of referenced schemas.
- Source Git commits establish byte history, not identity of an agent or owner approval.
- The code intentionally never writes to a remote GitHub API endpoint and has no background scheduler.

## Ownership

The product contract and scanning implementation live in public Mindport. Private account bindings, owner decisions, agent history and external-account observations stay in Context Hub. Do not duplicate private knowledge into this public codebase.

## Relationship to the existing Mindport MVP

The active MVP branch already implements `mindport.context-pack.v1`, text/JSONL import adapters, a local UI and CLI, source provenance and explicit selection. **Repo Bridge v0 introduces only repository discovery and a descriptive manifest.** It must not introduce an incompatible pack schema, import content into a different storage engine or alter existing exporter contracts. If repository source excerpts later become pack items, they must pass through Mindport's established neutral record interface and explicit user-selection process, with source revisions and permissions attached.

This adapter is stacked onto `feat/local-context-portability-mvp` for integration review, rather than built against the older minimal `main` branch.
