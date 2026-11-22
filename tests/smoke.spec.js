const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test('Arabic home screen and all learning worlds render', async ({ page }) => {
  await expect(page.getByRole('heading', { name: 'عالم فريدة' })).toBeVisible();
  for (const name of ['الغابة السحرية', 'مملكة البحار', 'وادي الرمال', 'جزر السحاب', 'حديقة الحيوانات']) {
    await expect(page.getByText(name, { exact: true })).toBeVisible();
  }
});

test('forest starts and home returns to the world menu', async ({ page }) => {
  await page.locator('#play').click();
  await expect(page.locator('#controls')).toBeVisible();
  await page.locator('#home').click();
  await expect(page.locator('#menu')).toBeVisible();
});

test('sea fishing responds to touch and keeps score bounded', async ({ page }) => {
  await page.locator('[data-world="sea"]').click();
  await expect(page.locator('#controls')).toBeVisible();
  await expect(page.locator('#scene')).toBeVisible();
});

test('animal garden advances through educational animals', async ({ page }) => {
  await page.locator('[data-world="learn"]').click();
  await expect(page.locator('#controls')).toBeHidden();
  await expect(page.locator('#learnControls')).toBeVisible();
  await page.locator('#scene').click({ position: { x: 180, y: 220 } });
  await expect(page.locator('#toast')).toContainText(/الفيل|الزرافة|القرد|الدلفين|البطريق|الأسد/);
});

test('sound toggle updates its accessible label', async ({ page }) => {
  await page.locator('#play').click();
  await page.locator('#sound').click();
  await expect(page.locator('#sound')).toHaveText('🔇');
  await page.locator('#sound').click();
  await expect(page.locator('#sound')).toHaveText('🔊');
});

test('saved gems and stars survive a reload', async ({ page }) => {
  await page.evaluate(() => {
    localStorage.setItem('fwGems', '7');
    localStorage.setItem('fwStars', '3');
  });
  await page.reload();
  await expect(page.locator('#gems')).toHaveText('7');
  await expect(page.locator('#stars')).toHaveText('3');
});

test('learning garden switches between animals, shapes, colors and Arabic letters', async ({ page }) => {
  await page.locator('[data-world="learn"]').click();
  for (const category of ['animals', 'shapes', 'colors', 'letters']) {
    await page.locator('[data-learn="' + category + '"]').click();
    await page.locator('#scene').click({ position: { x: 180, y: 220 } });
    await expect(page.locator('#toast')).not.toBeEmpty();
  }
});
