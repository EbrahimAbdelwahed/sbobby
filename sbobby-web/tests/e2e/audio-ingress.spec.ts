import { test, expect } from '@playwright/test';

test.skip(!process.env.PREVIEW_URL && process.env.RUN_AUDIO_E2E !== 'true', 'Set PREVIEW_URL for a preview smoke or RUN_AUDIO_E2E=true for the local browser gate.');

test('audio ingress workbench is reachable', async ({ page }) => {
  await page.goto('/dev/workbench/audio-ingress');
  await expect(page.getByRole('heading', { name: 'Audio ingress lab' })).toBeVisible();
  await expect(page.getByText('Storage audit')).toBeVisible();
  if (process.env.AUDIO_FIXTURE) {
    await page.locator('#audio-file').setInputFiles(process.env.AUDIO_FIXTURE);
    await expect(page.getByText('READY')).toBeVisible({ timeout: 120_000 });
    await page.getByRole('button', { name: 'Prepara chunk' }).click();
    await expect(page.getByText('#01')).toBeVisible({ timeout: 120_000 });
  }
});
