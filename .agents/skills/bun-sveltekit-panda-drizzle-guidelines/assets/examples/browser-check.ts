import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const origin = 'http://127.0.0.1:3000';
const secret = 'guide-private-sentinel-7e2c';
const server = Bun.spawn(['bun', './build'], {
  stdout: 'ignore',
  stderr: 'inherit',
  env: { ...process.env, HOST: '127.0.0.1', PORT: '3000', API_KEY: secret },
});
try {
  let ready = false;
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch(origin);
      if (response.ok) {
        ready = true;
        break;
      }
    } catch {
      /* Wait for the generated server to listen. */
    }
    await Bun.sleep(100);
  }
  assert.ok(ready, 'production server must start');
  const html = await (await fetch(origin)).text();
  assert.ok(html.includes('Private service configured: yes'));
  assert.ok(!html.includes(secret));
  assert.equal((await fetch(`${origin}/api/notes/invalid`)).status, 400);
  assert.equal((await fetch(`${origin}/api/notes/999`)).status, 404);
  assert.deepEqual(await (await fetch(`${origin}/api/health`)).json(), {
    status: 'ok',
  });
  const browser = await chromium.launch({
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  try {
    const page = await browser.newPage();
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await page.goto(origin);
    await page.getByRole('button', { name: 'Count 0; scaled 0' }).click();
    await page.getByRole('button', { name: 'Count 1; scaled 2' }).waitFor();
    const trigger = page.getByRole('button', { name: 'Add local note' });
    await trigger.click();
    await page.getByRole('dialog', { name: 'Add a note' }).waitFor();
    await page.getByRole('button', { name: 'Create', exact: true }).click();
    await page
      .getByRole('status')
      .filter({ hasText: 'Enter a title.' })
      .waitFor();
    await page.getByLabel('Title', { exact: true }).fill('Browser note');
    await page.getByRole('button', { name: 'Create', exact: true }).click();
    await page.getByText('Browser note', { exact: true }).waitFor();
    await trigger.click();
    await page.keyboard.press('Escape');
    await page.getByRole('dialog').waitFor({ state: 'hidden' });
    assert.equal(
      await trigger.evaluate((element) => element === document.activeElement),
      true,
    );
    await page.getByRole('button', { name: 'Validate on server' }).click();
    await page
      .getByRole('alert')
      .filter({ hasText: 'Enter a title' })
      .waitFor();
    await page.getByLabel('Server title').fill('Valid server title');
    await page.getByRole('button', { name: 'Validate on server' }).click();
    await page.getByText('Validated: Valid server title').waitFor();
    assert.equal(
      await page
        .locator('main')
        .evaluate((element) => getComputedStyle(element).padding),
      '16px',
    );
    assert.ok(!(await page.content()).includes(secret));
    assert.deepEqual(errors, []);
    console.log(
      'PASS production hydration, Ark validation/Escape/focus, Panda styles, server actions, API status, private SSR boundary',
    );
  } finally {
    await browser.close();
  }
} finally {
  server.kill();
  await server.exited;
}
