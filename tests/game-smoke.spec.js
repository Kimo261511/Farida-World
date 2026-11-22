const { test, expect } = require('@playwright/test');

test('Arabic game menu loads with all five worlds', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/عالم فريدة/);
  await expect(page.getByRole('heading', { name: 'عالم فريدة' })).toBeVisible();
  await expect(page.locator('[data-world]')).toHaveCount(5);
  await expect(page.locator('#gems')).toHaveText('0');
  await expect(page.locator('#stars')).toHaveText('0');
});

test('forest world starts and touch controls appear', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /الغابة السحرية/ }).click();
  await expect(page.locator('#menu')).toHaveClass(/hidden/);
  await expect(page.locator('#controls')).not.toHaveClass(/hidden/);
  await expect(page.locator('#scene')).toBeVisible();
});

test('fishing world starts with its own scene', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /مملكة البحار/ }).click();
  await expect(page.locator('#menu')).toHaveClass(/hidden/);
  await expect(page.locator('#controls')).not.toHaveClass(/hidden/);
  await expect(page.locator('#scene')).toBeVisible();
});

test('sound toggle and return-to-menu controls work', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /الغابة السحرية/ }).click();
  await page.locator('#sound').click();
  await expect(page.locator('#sound')).toHaveText('🔇');
  await page.locator('#home').click();
  await expect(page.locator('#menu')).not.toHaveClass(/hidden/);
  await expect(page.locator('#controls')).toHaveClass(/hidden/);
});

test('PWA manifest and service worker are served', async ({ page, request }) => {
  await page.goto('/');
  const manifest = await request.get('/manifest.webmanifest');
  const worker = await request.get('/sw.js');
  expect(manifest.ok()).toBeTruthy();
  expect(worker.ok()).toBeTruthy();
  expect((await manifest.json()).name).toContain('عالم فريدة');
});
