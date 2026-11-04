const test = require("node:test");
const assert = require("node:assert/strict");
const Core = require("../ui/core.js");

test("provider-neutral message arrays and typed content", () => {
  const data = {messages: [
    {role:"system",content:"DO NOT EXPORT"},
    {role:"user",id:"u-1",content:[{type:"input_text",text:"Question"},{type:"image_url",image_url:{url:"x"}}]},
    {role:"tool",content:"PRIVATE TOOL DATA"},
    {role:"assistant",id:"a-1",content:"Answer"}
  ]};
  const records = Core.parseFile("messages.json", JSON.stringify(data));
  assert.deepEqual(records.map(x => x.text), ["Question", "Answer"]);
  assert.equal(records[0].message_id, "u-1");
  assert.equal(records[0].provider, "messages");
  assert.equal(records[0].selected, false);
});

test("Gemini API contents and role=model are normalized", () => {
  const data = {contents: [
    {role:"user",parts:[{text:"Question"},{inline_data:{data:"unimported"}}]},
    {role:"model",parts:[{text:"Answer"}]}
  ]};
  const records = Core.parseFile("gemini-api.json", JSON.stringify(data));
  assert.deepEqual(records.map(x=>x.role), ["user","assistant"]);
  assert.deepEqual(records.map(x=>x.text), ["Question","Answer"]);
  assert.equal(records[0].provider, "gemini-api");
});

test("multiple conversations and OpenAI responses input", () => {
  const many = {conversations:[
    {id:"c1",title:"One",messages:[{role:"user",content:"first"}]},
    {id:"c2",title:"Two",messages:[{role:"assistant",content:"second"}]}
  ]};
  assert.deepEqual(Core.parseFile("conversations.json",JSON.stringify(many)).map(x=>x.source_id),
    ["c1","c2"]);
  assert.equal(Core.parseFile("request.json",JSON.stringify({input:[
    {role:"user",content:[{type:"input_text",text:"New prompt"}]}
  ]}))[0].text, "New prompt");
});

test("selected JSONL records roundtrip without provider loss", () => {
  const records=Core.parseFile("gemini-api.json",JSON.stringify({contents:[
    {role:"model",parts:[{text:"An answer"}]}
  ]}));
  records[0].selected=true;
  const pack=Core.pack(records,false);
  const stream=Core.toJSONL(pack);
  const reread=Core.parseFile("transfer.jsonl",stream);
  assert.equal(reread.length,1);
  assert.equal(reread[0].provider,"gemini-api");
  assert.equal(reread[0].text,"An answer");
  assert.equal(reread[0].selected,false);
});

test("unknown provider files fail rather than pretending to be compatible", () => {
  assert.throws(()=>Core.parseFile("history.json",JSON.stringify({events:[
    {type:"page_view",title:"Gemini activity"}
  ]})),/Unrecognized/);
  assert.throws(()=>Core.parseFile("messages.json",JSON.stringify({messages:[
    {role:"tool",content:"private"}
  ]})),/No supported/);
});

test("plain TXT and NDJSON work without a provider export format", () => {
  const note = Core.parseFile("agent-transcript.txt", "Locally saved session");
  assert.equal(note[0].role, "note");
  assert.equal(note[0].provider, "text");
  const stream = '{"source":"note","role":"note","text":"Reimported","provider":"local-agent"}\\n';
  const records = Core.parseFile("context.ndjson", stream);
  assert.equal(records.length, 1);
  assert.equal(records[0].provider, "local-agent");
});
