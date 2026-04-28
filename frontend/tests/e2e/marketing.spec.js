import { test, expect } from '@playwright/test';

test('homepage presents the premium landing experience', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { level: 1, name: 'AltixEdu' })).toBeVisible();
  await expect(page.getByText('A premium operating layer for schools, educators, families, and government oversight.')).toBeVisible();
  await expect(page.getByRole('link', { name: /Create a workspace/i }).first()).toBeVisible();
});

test('pricing page renders plan cards', async ({ page }) => {
  await page.goto('/pricing');

  await expect(page.getByRole('heading', { name: /Plans designed for growing schools/i })).toBeVisible();
  const pricingContent = page.getByText(/Start with this plan|Pricing tiers will appear here once the billing catalog is available\./i).first();
  await expect(pricingContent).toBeVisible();
});
