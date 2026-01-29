import { test, expect } from '@playwright/test'

test.describe('Employer Authentication', () => {
  test.describe('Login Page', () => {
    test('should display login form', async ({ page }) => {
      await page.goto('/login')

      // Check for login form elements
      await expect(page.getByLabel(/email/i)).toBeVisible()
      await expect(page.getByLabel(/password/i)).toBeVisible()
      await expect(page.getByRole('button', { name: /sign in|login/i })).toBeVisible()
    })

    test('should show validation errors for empty form', async ({ page }) => {
      await page.goto('/login')

      // Try to submit empty form
      await page.getByRole('button', { name: /sign in|login/i }).click()

      // Should show validation messages
      await expect(page.getByText(/required|invalid/i)).toBeVisible()
    })

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/login')

      // Fill in invalid credentials
      await page.getByLabel(/email/i).fill('invalid@test.com')
      await page.getByLabel(/password/i).fill('wrongpassword')
      await page.getByRole('button', { name: /sign in|login/i }).click()

      // Should show error message
      await expect(page.getByText(/error|incorrect|invalid/i)).toBeVisible({ timeout: 10000 })
    })

    test('should have link to registration', async ({ page }) => {
      await page.goto('/login')

      // Check for registration link
      const registerLink = page.getByRole('link', { name: /sign up|register|create account/i })
      await expect(registerLink).toBeVisible()
    })

    test('should toggle between login and register modes', async ({ page }) => {
      await page.goto('/login')

      // Click on register tab/link
      const registerTab = page.getByRole('tab', { name: /register|sign up/i }).or(
        page.getByRole('link', { name: /register|sign up/i })
      )

      if (await registerTab.isVisible()) {
        await registerTab.click()

        // Should show company name field (registration specific)
        await expect(page.getByLabel(/company name/i)).toBeVisible()
      }
    })
  })

  test.describe('Registration Flow', () => {
    test('should display registration form fields', async ({ page }) => {
      await page.goto('/login')

      // Navigate to registration if there are tabs
      const registerTab = page.getByRole('tab', { name: /register|sign up/i })
      if (await registerTab.isVisible()) {
        await registerTab.click()
      }

      // Check for registration fields
      await expect(page.getByLabel(/company name/i)).toBeVisible()
      await expect(page.getByLabel(/email/i)).toBeVisible()
      await expect(page.getByLabel(/password/i)).toBeVisible()
    })

    test('should validate email format', async ({ page }) => {
      await page.goto('/login')

      const registerTab = page.getByRole('tab', { name: /register|sign up/i })
      if (await registerTab.isVisible()) {
        await registerTab.click()
      }

      // Enter invalid email
      await page.getByLabel(/email/i).fill('invalid-email')
      await page.getByLabel(/email/i).blur()

      // Should show validation error
      await expect(page.getByText(/valid email|invalid email/i)).toBeVisible()
    })
  })
})
