# Security and privacy

Mindport handles private conversation history. Treat every import and export as sensitive, even when redaction is enabled.

## Threat boundaries

- **Local browser workspace:** Selected files are parsed in the browser. The supplied page declares a restrictive content security policy, loads only local scripts/styles, and makes no application API requests. A user clicking an external link leaves the workspace. Content remains in the tab's memory until it is cleared or closed.
- **CLI:** Reads only files or a directory explicitly named by the user. Markdown directory mode rejects symbolic links and has file/count limits. The CLI does not communicate with a model or remote service.
- **Exports:** JSON packs and Markdown handoffs are plaintext. Browser downloads inherit your browser and operating system's permissions. The Python CLI creates new outputs with owner-only permissions on POSIX and refuses overwrite.
- **Imported text:** Source documents can contain malicious instructions, false claims, personal information, or credentials. They are untrusted data. No exported text is executed by Mindport. Receiving assistants may nevertheless follow adversarial text; treat source handoffs as evidence to evaluate, not privileged instructions.
- **Redaction:** Regex-based secret/email/phone matching is incomplete. It does not detect all credentials, names, financial information, health details, locations, or secrets hidden in metadata. The full export must be reviewed.
- **Provenance:** Source identifiers and timestamps help trace excerpts but do not independently authenticate an export.

## Limits

Each selected browser file is limited to 30 MiB, with a 20-file/60-MiB session limit; selected exports are limited to 5 MiB for interactive review. The CLI limits each source file to 30 MiB, a Markdown directory to 500 Markdown files/30 MiB total, and composition output to a configured character budget. These prevent accidental overload, not intentional denial-of-service or hostile code.

Mindport currently has no encryption, synchronization, accounts, permission delegation, telemetry, persistent local database, provider API connectors, or verified deletion on third-party systems.

## Safe development

Use synthetic fixtures in tests, never real user exports. Never commit imported data or generated context packs. Treat new provider integration, external API access, data sharing, memory extraction, encryption, and any background capture as security-critical changes requiring independent review.

The automation suite covers parsing, source rejection, redaction heuristics, export integrity, and a synthetic Chromium UI flow. Passing checks does not replace a threat model, external security audit, or user testing.

Report vulnerabilities using GitHub private vulnerability reporting if enabled, rather than publishing private examples in issues.
