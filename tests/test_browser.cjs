const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const { spawn } = require("node:child_process");
const path = require("node:path");
const { chromium } = require("playwright");

async function startServer() {
  const server = spawn("python3", ["-m", "http.server", "8765",
    "--bind", "127.0.0.1", "--directory", "ui"], { stdio: "ignore" });
  await new Promise(resolve => setTimeout(resolve, 600));
  return server;
}
test("local browser import, review, approval, download and mobile layout", { timeout: 90000 }, async () => {
  const server = await startServer();
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 850 }, acceptDownloads: true });
    const outgoing = [];
    const pageErrors = [];
    page.on("pageerror", error => pageErrors.push(error.message));
    page.on("console", message => { if (message.type() === "error") pageErrors.push(message.text()); });
    await page.route("**/*", route => {
      const url = new URL(route.request().url());
      if (url.hostname !== "127.0.0.1") {
        outgoing.push(url.toString());
        return route.abort();
      }
      return route.continue();
    });
    await page.goto("http://127.0.0.1:8765", { waitUntil: "load" });
    assert.match(await page.title(), /Mindport/);
    const conversations = [{
      uuid: "synthetic-chat", name: "Research",
      chat_messages: [{ uuid: "entry-1", sender: "human",
        text: "Contact person@example.com. Credential sk-abcdefghijklmnopqrstuvwxyz1234",
        created_at: "2026-10-01T10:00:00Z" }]
    }];
    await page.locator("#sourceFile").setInputFiles([
      { name: "claude-conversations.json", mimeType: "application/json",
        buffer: Buffer.from(JSON.stringify(conversations)) },
      { name: "notes.md", mimeType: "text/markdown",
        buffer: Buffer.from("This private note is not selected") }
    ]);
    try {
      await page.locator("#library").waitFor({ state: "visible", timeout: 5000 });
    } catch (error) {
      await fs.mkdir("test-artifacts", { recursive: true });
      await page.screenshot({ path: "test-artifacts/mindport-import-failure.png", fullPage: true });
      const detail = {
        status: await page.locator("#status").textContent(),
        core: await page.evaluate(() => typeof window.MindportCore),
        scriptErrors: pageErrors,
        inputMultiple: await page.locator("#sourceFile").getAttribute("multiple"),
        workspaceHidden: await page.locator("#library").getAttribute("hidden")
      };
      throw new Error("Import did not open workspace: " + JSON.stringify(detail));
    }
    assert.equal(await page.locator(".record").count(), 2);
    assert.equal(await page.locator("#count").textContent(), "0");
    assert.equal(await page.locator("#exportJson").isDisabled(), true);

    await page.locator("#personal").check();
    await page.locator(".record").first().locator('input[type="checkbox"]').check();
    assert.equal(await page.locator("#reviewSelection").isEnabled(), true);
    await page.locator("#reviewSelection").click();
    const preview = await page.locator("#reviewAll").textContent();
    assert.match(preview, /REDACTED_SECRET/);
    assert.match(preview, /REDACTED_EMAIL/);
    assert.doesNotMatch(preview, /not selected/);
    assert.equal(await page.locator("#exportJson").isDisabled(), true);
    await page.locator("#approved").check();
    assert.equal(await page.locator("#exportJson").isEnabled(), true);

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.locator("#exportJson").click()
    ]);
    const pack = JSON.parse(await fs.readFile(await download.path(), "utf8"));
    assert.equal(pack.schema, "mindport.context-pack.v1");
    assert.equal(pack.items.length, 1);
    assert.equal(pack.items[0].provider, "claude");
    assert.equal(pack.items[0].source_id, "synthetic-chat");
    assert.doesNotMatch(JSON.stringify(pack), /person@example.com|sk-abcdefghij|not selected/);

    assert.equal(await page.locator("#exportJsonl").isEnabled(), true);
    const [jsonlDownload] = await Promise.all([
      page.waitForEvent("download"),
      page.locator("#exportJsonl").click()
    ]);
    const jsonlText = await fs.readFile(await jsonlDownload.path(), "utf8");
    const jsonlEntries = jsonlText.trim().split("\\n").map(line => JSON.parse(line));
    assert.equal(jsonlEntries.length, 1);
    assert.equal(jsonlEntries[0].provider, "claude");
    assert.doesNotMatch(jsonlText, /person@example.com|sk-abcdefghij|not selected/);

    await page.locator(".record").last().locator('input[type="checkbox"]').check();
    assert.equal(await page.locator("#exportJson").isDisabled(), true);

    await page.locator("#sourceFile").setInputFiles({
      name: "openai-compatible-messages.json", mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify({messages:[
        {role:"user",content:"Portable message from another runtime"}
      ]}))
    });
    await page.waitForFunction(() => document.querySelector("#sourceInfo")?.textContent.includes("3 entries"), null, {timeout: 5000});
    assert.equal(await page.locator(".record").count(), 3);
    assert.match(await page.locator("#sourceInfo").textContent(), /3 entries/);
    assert.equal(await page.locator("#exportJsonl").isDisabled(), true);

    await fs.mkdir("test-artifacts", { recursive: true });
    await page.screenshot({ path: "test-artifacts/mindport-desktop.png", fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: "test-artifacts/mindport-mobile.png", fullPage: true });
    const viewport = await page.evaluate(() => ({
      content: document.documentElement.scrollWidth,
      visible: window.innerWidth
    }));
    assert.ok(viewport.content <= viewport.visible + 1,
      "Unexpected horizontal overflow on mobile: " + JSON.stringify(viewport));
    assert.deepEqual(outgoing, [], "Unexpected external requests");
    await browser.close();
  } finally {
    await browser.close().catch(() => {});
    server.kill();
  }
});
