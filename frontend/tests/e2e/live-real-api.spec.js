import { expect, test } from '@playwright/test';

const loginAs = async (page, email) => {
  await page.goto('/login');
  await page.locator('#login-email').fill(email);
  await page.locator('#login-password').fill('Password123!');
  await page.getByRole('button', { name: /Sign in/i }).click();
};

test('admin can log in and reach settings and user operations with live APIs', async ({ page }) => {
  await loginAs(page, 'admin@atlascollege.test');
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText('School leadership overview')).toBeVisible();

  await page.goto('/app/admin/settings');
  await expect(page.getByText('Brand preview')).toBeVisible();
  await expect(page.locator('#school-name')).toHaveValue('Atlas College');

  await page.goto('/app/admin/users');
  await expect(page.getByText('Students directory')).toBeVisible();
  await expect(page.getByText('Ada Okafor')).toBeVisible();
});

test('teacher, student, parent, and bursar dashboards load from live APIs', async ({ page }) => {
  await loginAs(page, 'teacher@atlascollege.test');
  await expect(page).toHaveURL(/\/app\/teacher$/);
  await expect(page.getByText('Instruction, interventions, and classroom rhythm')).toBeVisible();

  await loginAs(page, 'student@atlascollege.test');
  await expect(page).toHaveURL(/\/app\/student$/);
  await expect(page.getByText(/Progress overview for Ada/i)).toBeVisible();

  await loginAs(page, 'parent@atlascollege.test');
  await expect(page).toHaveURL(/\/app\/parent$/);
  await expect(page.getByText('Children overview')).toBeVisible();

  await loginAs(page, 'bursar@atlascollege.test');
  await expect(page).toHaveURL(/\/app\/bursar$/);
  await expect(page.getByText('Collection status mix')).toBeVisible();
});

test('superadmin and ministry admin dashboards load from live APIs', async ({ page }) => {
  await loginAs(page, 'superadmin@altixedu.test');
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText('Portfolio and growth command')).toBeVisible();
  await expect(page.getByText('Tier mix')).toBeVisible();

  await loginAs(page, 'ministry@oyo-edu.test');
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText('Education system oversight')).toBeVisible();
  await expect(page.getByText('State performance')).toBeVisible();
});
