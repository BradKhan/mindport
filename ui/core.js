/* Mindport source parsing shared by browser and Node tests. No network calls. */
(function (root, make) {
  const api = make();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.MindportCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const MAX_BYTES = 30 * 1024 * 1024;
  const secretPatterns = [
    /\b(?:sk-[a-z0-9_-]{16,}|gh[pousr]_[a-z0-9]{20,}|github_pat_[a-z0-9_]{20,})\b/gi,
    /\b(?:api[_ -]?key|access[_ -]?token|password)\s*[:=]\s*[^\s,;]{6,}/gi
  ];
  const emailPattern = /[\w.+-]+@[\w.-]+\.[a-z]{2,}/gi;
  const phonePattern = /\+?\d[\d ()-]{8,}\d/g;

  function redact(text, personal = false) {
    let result = String(text);
    for (const pattern of secretPatterns) result = result.replace(pattern, "[REDACTED_SECRET]");
    if (personal) result = result.replace(emailPattern, "[REDACTED_EMAIL]").replace(phonePattern, "[REDACTED_PHONE]");
    return result;
  }
  function normalized(provider, source, role, text, sourceId, messageId, timestamp) {
    const e = {
      provider, source: String(source), role, text: String(text),
      edited: String(text), source_id: String(sourceId),
      message_id: String(messageId), selected: false
    };
    if (timestamp !== undefined && timestamp !== null &&
        ["string", "number"].includes(typeof timestamp)) e.timestamp = timestamp;
    return e;
  }
  function chatgpt(data) {
    if (!Array.isArray(data) || !data.some(c => c && c.mapping && typeof c.mapping === "object"))
      throw new Error("Not a recognized ChatGPT export.");
    const out = [];
    data.forEach((chat, index) => {
      if (!chat || !chat.mapping || typeof chat.mapping !== "object") return;
      const name = chat.title || "Untitled", cid = chat.id || "conversation-" + (index + 1);
      const nodes = Object.entries(chat.mapping).map(([id, n], i) => ({ id, n, i }));
      nodes.sort((a, b) => {
        const t = n => Number(n?.message?.create_time) || 0;
        return t(a.n) - t(b.n) || a.i - b.i;
      });
      for (const { id, n } of nodes) {
        const m = n?.message, role = m?.author?.role;
        if (!["user", "assistant"].includes(role) || !Array.isArray(m?.content?.parts)) continue;
        const text = m.content.parts.filter(v => typeof v === "string").join("\n").trim();
        if (text) out.push(normalized("chatgpt", name, role, text, cid,
                                     m.id || id, m.create_time));
      }
    });
    return out;
  }
  function claude(data) {
    if (!Array.isArray(data) || !data.some(c => c && Array.isArray(c.chat_messages)))
      throw new Error("Not a recognized Claude conversations export.");
    const out = [];
    data.forEach((chat, index) => {
      if (!chat || !Array.isArray(chat.chat_messages)) return;
      const name = chat.name || "Untitled";
      const cid = chat.uuid || chat.id || "conversation-" + (index + 1);
      chat.chat_messages.forEach((m, n) => {
        const role = ({ human: "user", user: "user", assistant: "assistant" })[m?.sender || m?.role];
        if (!role) return;
        const blocks = Array.isArray(m.content) ? m.content
          .filter(b => b && b.type === "text" && typeof b.text === "string").map(b => b.text) : [];
        let text = blocks.join("\n").trim();
        if (!text) text = typeof m.text === "string" ? m.text.trim() : "";
        if (text.includes("This block is not supported on your current device yet"))
          text = blocks.join("\n").trim();
        if (text) out.push(normalized("claude", name, role, text, cid,
                                     m.uuid || m.id || "message-" + (n + 1), m.created_at));
      });
    });
    return out;
  }
  function jsonl(raw) {
    return raw.split(/\r?\n/).flatMap((line, index) => {
      if (!line.trim()) return [];
      let e;
      try { e = JSON.parse(line); } catch (_) {
        throw new Error("Invalid JSONL on line " + (index + 1));
      }
      if (!e || !["user", "assistant", "note"].includes(e.role) ||
          typeof e.text !== "string" || typeof e.source !== "string")
        throw new Error("JSONL line " + (index + 1) + " requires source, role and text.");
      return e.text.trim()
        ? [normalized("jsonl", e.source, e.role, e.text.trim(),
                      e.source_id || e.source, e.message_id || "line-" + (index + 1), e.timestamp)]
        : [];
    });
  }
  function mindportPack(data) {
    if (data?.schema !== "mindport.context-pack.v1" || !Array.isArray(data.items))
      throw new Error("Invalid Mindport context pack.");
    return data.items.map((item, index) => {
      if (!item || ["source", "role", "text", "id"].some(k => typeof item[k] !== "string"))
        throw new Error("Invalid context pack entry " + (index + 1));
      if (!["user", "assistant", "note"].includes(item.role))
        throw new Error("Unsupported context pack role");
      return normalized(item.provider || "mindport", item.source, item.role, item.text,
        item.source_id || item.source, item.message_id || item.id, item.timestamp);
    });
  }
  function parseFile(filename, raw) {
    if (typeof raw !== "string" || new TextEncoder().encode(raw).length > MAX_BYTES)
      throw new Error("File exceeds 30 MiB.");
    if (/\.(md|markdown)$/i.test(filename))
      return [normalized("markdown", filename, "note", raw, filename, filename)];
    if (/\.jsonl$/i.test(filename)) return jsonl(raw);
    if (!/\.json$/i.test(filename)) throw new Error("Choose a .json, .jsonl or Markdown file.");
    let data;
    try { data = JSON.parse(raw); } catch (_) { throw new Error("Invalid JSON file."); }
    if (data?.schema === "mindport.context-pack.v1") return mindportPack(data);
    if (!Array.isArray(data)) throw new Error("Unknown JSON format. Select a documented export.");
    if (data.some(c => c && typeof c.mapping === "object" && c.mapping))
      return chatgpt(data);
    if (data.some(c => c && Array.isArray(c.chat_messages))) return claude(data);
    throw new Error("Unrecognized export. Gemini Takeout activity is not a full conversation export.");
  }
  function pack(entries, personal) {
    const chosen = entries.filter(e => e.selected);
    return {
      schema: "mindport.context-pack.v1",
      privacy: { local_only: true, personal_redaction: personal,
                 secret_redaction: "best_effort", explicit_selection: true },
      items: chosen.map((e, index) => ({
        id: "local-" + (index + 1) + "-" + (e.message_id || "item"),
        source: e.source, role: e.role, text: redact(e.edited, personal),
        origin_index: e.origin_index || index + 1,
        provider: e.provider, source_id: e.source_id, message_id: e.message_id,
        ...(e.timestamp === undefined ? {} : { timestamp: e.timestamp })
      }))
    };
  }
  return { parseFile, chatgpt, claude, jsonl, mindportPack, redact, pack, MAX_BYTES };
});
