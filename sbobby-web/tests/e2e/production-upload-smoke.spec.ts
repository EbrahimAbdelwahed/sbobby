import { expect, test } from '@playwright/test';

test('production stores an MP3 before handing it to the worker', async ({ page }) => {
  const accessCode = process.env.TEST_ACCESS_CODE;
  test.skip(!accessCode, 'TEST_ACCESS_CODE is required');

  await page.goto('/sign-in');
  await page.getByLabel('Codice di accesso').fill(accessCode!);
  await page.getByRole('button', { name: 'Continua' }).click();
  await expect(page).toHaveURL(/\/app$/);

  await page.getByLabel(/Scegli MP3 o M4A/).setInputFiles({
    name: 'smoke.mp3',
    mimeType: 'audio/mpeg',
    buffer: Buffer.from('ID3-smoke'),
  });
  const uploadResponsePromise = page.waitForResponse(
    (response) => response.url().endsWith('/api/upload') && response.request().method() === 'POST',
  );
  const jobResponsePromise = page.waitForResponse(
    (response) => response.url().endsWith('/api/jobs/start') && response.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Genera sbobina' }).click();

  const uploadResponse = await uploadResponsePromise;
  expect(uploadResponse.ok()).toBeTruthy();
  const jobResponse = await jobResponsePromise;
  expect(jobResponse.status()).not.toBe(400);
});
