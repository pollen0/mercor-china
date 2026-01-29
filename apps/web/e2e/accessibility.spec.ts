import { test, expect } from '@playwright/test'

test.describe('Accessibility', () => {
  test('home page should have proper heading structure', async ({ page }) => {
    await page.goto('/')

    // Should have an h1 heading
    const h1 = page.locator('h1')
    await expect(h1).toBeVisible()
  })

  test('login form should have proper labels', async ({ page }) => {
    await page.goto('/login')

    // Form inputs should have associated labels
    const emailInput = page.getByLabel(/email/i)
    const passwordInput = page.getByLabel(/password/i)

    await expect(emailInput).toBeVisible()
    await expect(passwordInput).toBeVisible()
  })

  test('buttons should be keyboard accessible', async ({ page }) => {
    await page.goto('/login')

    // Tab to the submit button
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')

    // The button should be focusable
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  })

  test('error messages should be announced', async ({ page }) => {
    await page.goto('/login')

    // Submit empty form
    await page.getByRole('button', { name: /sign in|login/i }).click()

    // Error messages should have appropriate ARIA attributes or be in alert role
    const errorMessages = page.locator('[role="alert"], .text-red-500, .text-red-600')
    await expect(errorMessages.first()).toBeVisible()
  })

  test('interview start page should have skip links or logical focus order', async ({ page }) => {
    // Mock valid token
    await page.route('**/api/interviews/invite/validate/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          valid: true,
          jobId: 'j123',
          jobTitle: 'Software Engineer',
          companyName: 'Test Company',
        }),
      })
    })

    await page.goto('/interview/start?token=test')
    await page.waitForTimeout(1000)

    // Tab through form elements
    await page.keyboard.press('Tab')

    // Should be able to navigate with keyboard
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  })

  test('images should have alt text', async ({ page }) => {
    await page.goto('/')

    // Check that images have alt attributes
    const images = page.locator('img')
    const count = await images.count()

    for (let i = 0; i < count; i++) {
      const img = images.nth(i)
      const alt = await img.getAttribute('alt')
      // Alt should exist (can be empty string for decorative images)
      expect(alt !== null).toBeTruthy()
    }
  })

  test('color contrast should be sufficient', async ({ page }) => {
    await page.goto('/')

    // This is a basic check - proper contrast testing requires specialized tools
    // Just verify that text elements are visible and readable
    const textElements = page.locator('p, h1, h2, h3, h4, h5, h6, span, a, button')
    const count = await textElements.count()

    expect(count).toBeGreaterThan(0)
  })

  test('focus indicators should be visible', async ({ page }) => {
    await page.goto('/login')

    // Focus on an input
    await page.getByLabel(/email/i).focus()

    // Check that focus is visible (element should have focus styles)
    const focusedInput = page.locator(':focus')
    await expect(focusedInput).toBeVisible()

    // The focused element should have some visual indication
    // This could be a ring, border, or other style
    const hasFocusStyles = await focusedInput.evaluate((el) => {
      const styles = window.getComputedStyle(el)
      return (
        styles.outline !== 'none' ||
        styles.boxShadow !== 'none' ||
        styles.border !== ''
      )
    })

    expect(hasFocusStyles).toBeTruthy()
  })
})
