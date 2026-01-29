import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('should display the home page', async ({ page }) => {
    await page.goto('/')

    // Check that the page loads
    await expect(page).toHaveTitle(/ZhiPin/i)
  })

  test('should have navigation elements', async ({ page }) => {
    await page.goto('/')

    // Check for main navigation or content
    const mainContent = page.locator('main')
    await expect(mainContent).toBeVisible()
  })

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    // Page should still be functional on mobile
    await expect(page.locator('body')).toBeVisible()
  })
})
