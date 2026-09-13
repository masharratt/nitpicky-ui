/* Browser regressions use a temporary review and never write to a real review. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const {spawn, execFileSync} = require('node:child_process');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
let browser, server, run, base;
async function start() {
  server = spawn('python3', [path.join(root, 'lib/server.py'), '--run-dir', run, '--port', '0']);
  base = await new Promise((resolve, reject) => {
    let output = '';
    server.stdout.on('data', chunk => {
      output += chunk;
      if (output.includes('\n')) {
        try { resolve(JSON.parse(output.split('\n')[0]).url); } catch (error) { reject(error); }
      }
    });
    server.stderr.on('data', chunk => process.stderr.write(chunk));
    server.once('error', reject);
    server.once('exit', code => reject(new Error('Preview exited before ready: ' + code)));
  });
}
async function stop() {
  if (server && server.exitCode === null) await new Promise(resolve => {server.once('exit', resolve); server.kill();});
}
async function saved(page) {
  await page.waitForFunction(() => document.querySelector('#save-status').textContent === 'All changes saved');
}
(async () => {
  run = await fs.mkdtemp(path.join(os.tmpdir(), 'nitpicky-ui-'));
  try {
    await fs.cp(path.join(root, 'examples/demo-run'), run, {recursive: true});
    await fs.rm(path.join(run, 'decisions.json'), {force: true});
    execFileSync('python3', [path.join(root, 'lib/merge-findings.py'), '--run-dir', run]);
    await start();
    browser = await chromium.launch({headless: true, chromiumSandbox: true,
      ...(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {})});
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
    // Replace the demo's 1px placeholders only inside this disposable fixture.
    await page.setContent('<body style="background:#302842;color:white;font:32px sans-serif;padding:50px">Screenshot evidence fixture</body>');
    const proof = await page.screenshot();
    for (const name of await fs.readdir(path.join(run, 'screenshots'))) {
      if (name.endsWith('.png')) await fs.writeFile(path.join(run, 'screenshots', name), proof);
    }
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base);
    await page.waitForFunction(() => document.querySelector('#save-status').textContent === 'Autosave is on');
    const ids = await page.locator('.card').evaluateAll(cards => cards.map(card => card.dataset.id));
    assert.ok(ids.length > 1, 'Fixture must have multiple findings');
    assert.equal(await page.locator('#count-total').textContent(), String(ids.length), 'Total count');
    const first = page.locator('.card').first();
    const firstId = ids[0], lastId = ids[ids.length - 1];
    await page.locator('#f-search').fill(firstId);
    await page.waitForFunction(() => document.querySelectorAll('.card:not([hidden])').length === 1);
    assert.equal(await page.locator('#results-count').textContent(), `Showing 1 of ${ids.length} findings`, 'Search result count');
    await page.locator('#btn-reset').click();
    await page.locator('.lens-toggle').first().click();
    assert.equal(await page.locator('.lens-toggle').first().getAttribute('aria-pressed'), 'false', 'Lens exposes toggle state');
    assert.ok(await page.locator('.card:visible').count() < ids.length, 'Lens filters results');
    await page.locator('#btn-reset').click();
    await page.locator('#btn-next').click();
    assert.equal(new URL(page.url()).hash, '#' + firstId, 'Next links first undecided');
    await page.locator('#btn-next').click();
    assert.equal(new URL(page.url()).hash, '#' + ids[1], 'Next advances to another undecided');
    await first.locator('[data-d="fix"]').click();
    await saved(page);
    assert.equal(await first.locator('[data-d="fix"]').getAttribute('aria-pressed'), 'true', 'Decision exposes selected state');
    await first.locator('textarea').fill('Context <script>literal</script>');
    await first.locator('textarea').blur();
    await saved(page);
    await page.reload();
    await page.waitForFunction(id => document.getElementById('note-' + id).value.includes('<script>'), firstId);
    await first.locator('textarea').fill('');
    await first.locator('textarea').blur();
    await saved(page);
    await page.reload();
    await page.waitForFunction(id => document.getElementById(id).dataset.decided === 'fix', firstId);
    assert.equal(await first.locator('textarea').inputValue(), '', 'Cleared note remains cleared on reload');
    const evidence = first.locator('.evidence-button');
    await evidence.click();
    assert.equal(await page.locator('#lightbox').isVisible(), true, 'Evidence dialog opens');
    assert.equal(await page.locator('#btn-close-lightbox').evaluate(el => el === document.activeElement), true, 'Dialog receives focus');
    await page.keyboard.press('Tab');
    assert.equal(await page.locator('#btn-close-lightbox').evaluate(el => el === document.activeElement), true, 'Lightbox traps keyboard focus');
    await page.keyboard.press('Escape');
    assert.equal(await evidence.evaluate(el => el === document.activeElement), true, 'Closing evidence returns focus');
    await page.locator('#btn-bulk').click();
    await page.locator('[data-bulk="defer"]').click();
    assert.equal(await page.locator('#bulk-modal').isVisible(), true, 'Bulk confirmation is visible');
    await page.locator('#btn-bulk-cancel').click();
    assert.equal(await page.locator('#count-defer').textContent(), '0', 'Cancel does not change decisions');
    await page.locator('#btn-bulk').click();
    await page.locator('[data-bulk="defer"]').click();
    await page.locator('#bulk-note').fill('Review after launch');
    await page.locator('#btn-bulk-apply').click();
    await saved(page);
    assert.equal(await page.locator('#count-defer').textContent(), String(ids.length), 'Bulk applies to full filtered scope');
    await page.locator('#f-search').fill(lastId);
    await page.waitForFunction(() => document.querySelectorAll('.card:not([hidden])').length === 1);
    const last = page.locator('#' + lastId);
    await last.locator('[data-d="defer"]').click();
    await saved(page);
    assert.equal(await page.locator('#btn-next').isEnabled(), true, 'Clearing a decision restores undecided navigation');
    await last.locator('textarea').fill('Final item <b>exact note</b>');
    await last.locator('[data-d="fix"]').click();
    await saved(page);
    assert.equal(await page.locator('#btn-next').isDisabled(), true, 'Final decision disables Next independently of saving');
    let state = JSON.parse(await fs.readFile(path.join(run, 'decisions.json'), 'utf8'));
    assert.equal(state.decisions[lastId].explanation, 'Final item <b>exact note</b>', 'Final note persisted exactly');
    await page.route('**/api/decision', route => route.abort('failed'));
    await last.locator('[data-d="deny"]').click();
    await page.waitForFunction(() => document.querySelector('#save-status').textContent.startsWith('Not saved'));
    assert.equal(await page.locator('#btn-retry').isVisible(), true, 'Save failures expose Retry');
    await page.unroute('**/api/decision');
    await page.locator('#btn-retry').click();
    await saved(page);
    state = JSON.parse(await fs.readFile(path.join(run, 'decisions.json'), 'utf8'));
    assert.equal(state.decisions[lastId].decision, 'deny', 'Retry persists queued decision');
    await page.locator('#btn-export').click();
    await page.waitForFunction(() => document.querySelector('#export-path').textContent.startsWith('Written to disk:'));
    assert.ok((await fs.readFile(path.join(run, 'CHECKLIST.md'), 'utf8')).includes('Final item <b>exact note</b>'), 'Export preserves exact note');
    await page.keyboard.press('Escape');
    await page.locator('#btn-reset').click();
    await page.locator('[data-status="deny"]').click();
    assert.equal(await page.locator('.card:visible').count(), 1, 'Summary cards filter by decision');
    await page.evaluate(id => {location.hash = id;}, firstId);
    await page.waitForFunction(id => !document.getElementById(id).hidden, firstId);
    assert.equal(await page.locator('#f-status').inputValue(), 'any', 'Deep link reveals a filtered finding');
    await page.locator('#btn-theme').click();
    await page.reload();
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light', 'Theme persists across reload');
    await page.setViewportSize({width: 375, height: 812});
    await page.evaluate(() => scrollTo(0, 0));
    assert.equal(await page.locator('#filter-controls').isVisible(), false, 'Mobile filters start collapsed');
    await page.locator('#btn-filters').click();
    assert.equal(await page.locator('#filter-controls').isVisible(), true, 'Mobile filters expand');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'Mobile has no horizontal overflow');
    await page.locator('#btn-filters').click();
    await page.locator('#f-search').fill('a query that matches nothing');
    await page.waitForFunction(() => !document.querySelector('#empty-note').hidden);
    assert.equal(await page.locator('#btn-bulk').isDisabled(), true, 'Empty results disable bulk actions');
    await page.locator('#empty-note button').click();
    assert.equal(await page.locator('.card:visible').count(), ids.length, 'Empty-state reset restores results');
    await stop(); await start();
    await page.goto(base);
    await page.waitForFunction(id => document.getElementById(id).dataset.decided === 'deny', lastId);
    assert.equal(await page.locator('#note-' + lastId).inputValue(), 'Final item <b>exact note</b>', 'Server restart retains final note');
    assert.deepEqual(errors, [], 'No browser JavaScript errors');
    console.log('PASS: search, lens/status filters, advancing navigation, saves, note clearing, final item, Retry, bulk/cancel, export, screenshot focus, deep links, mobile, theme, restart.');
  } finally {
    await browser?.close(); await stop();
    if (run) await fs.rm(run, {recursive: true, force: true});
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
