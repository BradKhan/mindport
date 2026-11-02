<p align="center">
  <img src="assets/mindport-hero.svg" width="100%" alt="Mindport. Take your context with you. Ivory type and seven interlocking gold circles on charcoal." />
</p>

**Your AI history belongs to you.**

Conversations, decisions, research, and the context you've built shouldn't disappear when you change assistants. Mindport helps you choose what's worth carrying, inspect it on your own computer, and export it as a portable file.

No account. No mandatory cloud service. No wholesale transfer of your history.

## Try Mindport

The first working implementation is in [PR #7](https://github.com/BradKhan/mindport/pull/7), pending review. It includes a local browser workspace and a Python CLI.

```bash
git clone https://github.com/BradKhan/mindport.git
cd mindport
git switch feat/local-context-portability-mvp
python3 -m http.server 8765 --directory ui
```

Open **http://localhost:8765** in your browser. Choose a ChatGPT `conversations.json` export or a Markdown note. Browse and edit the entries, select only what you want to share, preview redaction, and export JSON or Markdown.

For the CLI:

```bash
python3 mindport.py inspect conversations.json --format chatgpt
python3 mindport.py pack conversations.json --format chatgpt --select 1 3 8 --redact-personal --output private-pack.json
python3 mindport.py export private-pack.json --output handoff.md
```

Requires Python 3.11+ for the CLI. No third-party packages required.

## The principle

**You decide what another AI gets to know.**

Mindport keeps the steps visible: source material, your selection, your edits, and the file you choose to provide to another assistant. It preserves source attribution in the exported context pack.

The current prototype supports:

- Local inspection of ChatGPT text conversations and Markdown notes
- Explicit, item-by-item selection and editing
- Best-effort credential redaction, with optional email and phone redaction
- Portable JSON context packs and readable Markdown handoffs
- Local search through selected context using the CLI

These exports do not automatically install memories in ChatGPT, Claude, Gemini, or other providers. They are files you can inspect and choose to share. Redaction cannot guarantee removal of sensitive information. Review every export.

## Where it goes

Mindport is an early experiment in **portable, person-owned intelligence**. The larger goal is to carry relevant memory, research, decisions, and context between tools without starting over or becoming captive to any one model.

The next steps are additional import formats, stronger disclosure controls, provenance and integrity checks, cross-assistant retrieval testing, and optional local memory backends. A capability joins the product when it improves a real user outcome, not merely because an AI framework exists.

**Development:** [MVP PR](https://github.com/BradKhan/mindport/pull/7) · [Roadmap](https://github.com/BradKhan/mindport/blob/feat/local-context-portability-mvp/ROADMAP.md) · [Issues](https://github.com/BradKhan/mindport/issues) · [Source reuse](https://github.com/BradKhan/mindport/blob/feat/local-context-portability-mvp/references/REUSE.md)

Built by [Brad Khan](https://bradkhan.com). Part of a wider exploration of human agency, independent software, and intelligence people can own. Development practices draw selectively from [Open ASS](https://github.com/BradKhan/open-ASS) and [Venture Method](https://github.com/cyberagencyorg/venturemethod).
