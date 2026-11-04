const test = require("node:test");
const assert = require("node:assert/strict");
const Core = require("../ui/core.js");

test("ChatGPT conversation graph retains chronology and message identity", () => {
  const entries = Core.parseFile("conversations.json", JSON.stringify([{
    id: "abc", title: "Strategy", mapping: {
      second: { message: { id: "b", create_time: 2, author: { role: "assistant" },
                           content: { parts: ["second"] } } },
      first: { message: { id: "a", create_time: 1, author: { role: "user" },
                          content: { parts: ["first"] } } },
      hidden: { message: { author: { role: "tool" }, content: { parts: ["tool"] } } }
    }
  }]));
  assert.deepEqual(entries.map(e => e.text), ["first", "second"]);
  assert.equal(entries[0].source_id, "abc");
  assert.equal(entries[0].message_id, "a");
  assert.equal(entries[0].selected, false);
});

test("Claude avoids tool block placeholders and preserves timestamps", () => {
  const entries = Core.parseFile("conversations.json", JSON.stringify([{
    uuid: "thread", name: "Study", chat_messages: [
      { uuid: "a", sender: "human", text: "hello",
        created_at: "2026-11-01T00:00:00Z" },
      { uuid: "b", sender: "assistant",
        text: "This block is not supported on your current device yet",
        content: [{ type: "tool_use", name: "search" },
                  { type: "text", text: "Relevant findings" }] }
    ]
  }]));
  assert.deepEqual(entries.map(e => e.text), ["hello", "Relevant findings"]);
  assert.equal(entries[0].timestamp, "2026-11-01T00:00:00Z");
  assert.equal(entries[0].provider, "claude");
});

test("Markdown and JSONL are distinct, explicit formats", () => {
  assert.equal(Core.parseFile("ideas.md", "# Idea")[0].role, "note");
  assert.equal(Core.parseFile("records.jsonl",
    '{"source":"journal","role":"note","text":"a thought"}\n')[0].source, "journal");
  assert.throws(() => Core.parseFile("records.jsonl", '{"unknown":true}'), /requires source/);
});

test("Mindport packs can be reimported without selecting everything", () => {
  const original = [{provider:"claude",source:"A",role:"assistant",edited:"private",
    source_id:"source-a",message_id:"message-a",selected:true}];
  const exported = Core.pack(original, false);
  assert.equal(exported.items.length, 1);
  assert.equal(exported.items[0].source_id, "source-a");
  const reimported = Core.parseFile("context.json", JSON.stringify(exported));
  assert.equal(reimported[0].provider, "claude");
  assert.equal(reimported[0].selected, false);
});

test("Unrecognized and Gemini activity JSON are not guessed", () => {
  assert.throws(() => Core.parseFile("MyActivity.json",
    '[{"title":"activity only"}]'), /Unrecognized export/);
  assert.throws(() => Core.parseFile("bad.json", '{"unknown":true}'), /Unrecognized export/);
  assert.throws(() => Core.parseFile("script.html", "<script/>"), /Choose a/);
});

test("Only selected entries appear, with best-effort secret and personal redaction", () => {
  const entries = [
    {provider:"markdown",source:"a.md",source_id:"a.md",message_id:"a.md",
     role:"note",edited:"email me at person@example.com token sk-abcdefghijklmnopqrstuvwxyz",
     selected:true},
    {provider:"markdown",source:"b.md",source_id:"b.md",message_id:"b.md",
     role:"note",edited:"UNSELECTED",selected:false}
  ];
  const result = Core.pack(entries, true);
  assert.equal(result.items.length, 1);
  assert.doesNotMatch(JSON.stringify(result), /person@example.com|UNSELECTED|sk-abcdef/);
  assert.match(result.items[0].text, /REDACTED_EMAIL/);
  assert.match(result.items[0].text, /REDACTED_SECRET/);
});

test("Malformed or oversized files fail before import", () => {
  assert.throws(() => Core.parseFile("data.json", "{not json}"), /Invalid JSON/);
  assert.throws(() => Core.parseFile("notes.md", "x".repeat(Core.MAX_BYTES + 1)), /exceeds/);
});
