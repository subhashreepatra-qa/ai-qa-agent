import { test, expect } from '@playwright/test';

const BASE_URL = 'https://demo.playwright.dev/todomvc';

test.describe('Todo App', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('TC-001 | can create a new todo item', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Buy milk');
    await input.press('Enter');
    await expect(page.getByText('Buy milk')).toBeVisible();
  });

  test('TC-002 | can mark a todo as complete', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Write tests');
    await input.press('Enter');
    await page.locator('input.toggle').click();
    await expect(page.locator('li.completed')).toBeVisible();
  });

  test('TC-003 | empty input does not create a todo', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(0);
  });

  test('TC-004 | can filter to show only active todos', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Active item');
    await input.press('Enter');
    await input.fill('Completed item');
    await input.press('Enter');
    await page.locator('input.toggle').nth(1).click();
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByText('Active item')).toBeVisible();
    await expect(page.getByText('Completed item')).not.toBeVisible();
  });

  test('TC-005 | can delete a todo item', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Item to delete');
    await input.press('Enter');
    await page.locator('li').filter({ hasText: 'Item to delete' }).hover();
    await page.locator('button.destroy').click();
    await expect(page.getByText('Item to delete')).not.toBeVisible();
  });

});
