<p align="center">
  <img src="assets/mindport-hero.svg" width="100%" alt="Mindport. Your intelligence should travel with you. Ivory typography and seven interlocking gold circles on charcoal." />
</p>

**Your intelligence should travel with you.**

Memory is too valuable to leave inside a chat window. Mindport is a local-first effort to make the knowledge, research, decisions, and context you've accumulated usable across AI models, agents, applications, and devices.

The ChatGPT importer is the first adapter. It isn't the product's boundary.

## What we're building

A portable intelligence layer that answers to the person using it.

- **Bring your sources.** Conversations from ChatGPT, Claude, Gemini and other assistants; notes, documents, browser research, project files, saved material, and agent histories.
- **Keep what matters.** Normalize different formats while retaining origins, dates, decisions, references, and corrections. Never confuse generated summaries with verified facts.
- **Make context useful.** Find relevant material and assemble task-specific context for whichever model, agent, or application you choose. Give each recipient only what it needs.
- **Own the infrastructure.** Store locally by default, control disclosure and retention, support portable exports, and eventually offer optional encrypted synchronization without tying memory to a provider.

Those are the design goals, not a claim that every integration exists today. See the [architecture and product direction](VISION.md).

## What works today

The [first implementation](https://github.com/BradKhan/mindport/pull/7) provides a small, testable slice:

- Inspect ChatGPT `conversations.json` exports and Markdown notes on your computer.
- Browse, search, edit, and explicitly select which excerpts travel.
- Apply best-effort credential redaction and optional personal-data redaction.
- Export a versioned JSON context pack or a Markdown handoff.
- Use the local browser interface or a dependency-free Python CLI.

**No automated memory import into other assistants yet.** No encrypted vault, persistent graph, multi-provider ingestion, or automatic context routing. Redaction is heuristic and requires review before sharing. Imported material is untrusted data, not instructions.

## Run the prototype

The application is on the implementation branch while [PR #7](https://github.com/BradKhan/mindport/pull/7) is reviewed.

```bash
git clone https://github.com/BradKhan/mindport.git
cd mindport
git switch feat/local-context-portability-mvp
python3 -m http.server 8765 --directory ui
```

Open [http://localhost:8765](http://localhost:8765) and select a ChatGPT export or Markdown note. The page processes the selected file in your browser, without uploading it to a service.

The CLI needs Python 3.11+ and no third-party packages:

```bash
python3 mindport.py inspect conversations.json --format chatgpt
python3 mindport.py pack conversations.json --format chatgpt --select 1 3 8 --redact-personal --output private-pack.json
python3 mindport.py export private-pack.json --output handoff.md
python3 -m unittest discover -s tests -v
```

## What comes next

The immediate priorities are verified import adapters, editable source attribution, privacy review, stronger pack integrity, local retrieval, and measured cross-assistant handoffs. The larger architecture includes user-controlled memory, replaceable retrieval engines, and context delivery to agents and software through open interfaces.

The test is straightforward: **Can someone change their models, tools, or devices without abandoning what they've learned?**

[Product direction](VISION.md) · [Development roadmap](https://github.com/BradKhan/mindport/blob/feat/local-context-portability-mvp/ROADMAP.md) · [GitHub issues](https://github.com/BradKhan/mindport/issues) · [MVP pull request](https://github.com/BradKhan/mindport/pull/7)

Built by [Brad Khan](https://bradkhan.com). Mindport is a focused component of a broader vision for human-owned intelligence, alongside Humetheus, [Open ASS](https://github.com/BradKhan/open-ASS), and [Venture Method](https://github.com/cyberagencyorg/venturemethod).
