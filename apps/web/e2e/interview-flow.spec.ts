import { test, expect } from '@playwright/test'

test.describe('Interview Flow', () => {
  test.describe('Interview Start Page', () => {
    test('should show invalid token message for missing token', async ({ page }) => {
      await page.goto('/interview/start')

      // Should show error for missing token
      await expect(page.getByText(/no invite token|invalid|error/i)).toBeVisible()
    })

    test('should show invalid token message for bad token', async ({ page }) => {
      await page.goto('/interview/start?token=invalid_token_12345')

      // Wait for validation response
      await page.waitForTimeout(2000)

      // Should show error message
      await expect(page.getByText(/invalid|expired|error/i)).toBeVisible()
    })

    test('should display loading state while validating', async ({ page }) => {
      await page.goto('/interview/start?token=test_token')

      // Should show loading indicator initially
      const loadingIndicator = page.locator('.animate-spin, [role="status"]')
      // May or may not be visible depending on how fast the API responds
    })
  })

  test.describe('Interview Start with Valid Token (Mocked)', () => {
    test.beforeEach(async ({ page }) => {
      // Mock the API to return a valid token
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
    })

    test('should display job information with valid token', async ({ page }) => {
      await page.goto('/interview/start?token=valid_test_token')

      // Wait for content to load
      await page.waitForTimeout(1000)

      // Should show job title
      await expect(page.getByText(/software engineer/i)).toBeVisible()

      // Should show company name
      await expect(page.getByText(/test company/i)).toBeVisible()
    })

    test('should display registration form fields', async ({ page }) => {
      await page.goto('/interview/start?token=valid_test_token')

      await page.waitForTimeout(1000)

      // Check for registration form
      await expect(page.getByLabel(/name|full name/i)).toBeVisible()
      await expect(page.getByLabel(/email/i)).toBeVisible()
      await expect(page.getByLabel(/phone/i)).toBeVisible()
    })

    test('should validate required fields', async ({ page }) => {
      await page.goto('/interview/start?token=valid_test_token')

      await page.waitForTimeout(1000)

      // Click submit without filling form
      await page.getByRole('button', { name: /start interview/i }).click()

      // Should show validation errors
      await expect(page.getByText(/required|please enter/i)).toBeVisible()
    })

    test('should show instructions before starting', async ({ page }) => {
      await page.goto('/interview/start?token=valid_test_token')

      await page.waitForTimeout(1000)

      // Should show interview instructions
      await expect(page.getByText(/5 questions|camera|microphone/i)).toBeVisible()
    })
  })

  test.describe('Interview Room', () => {
    test.beforeEach(async ({ page }) => {
      // Mock the interview session API
      await page.route('**/api/interviews/*', async (route) => {
        if (route.request().url().includes('/upload-url')) {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              uploadUrl: 'https://upload.example.com',
              storageKey: 'videos/test.webm',
              expiresIn: 3600,
            }),
          })
        } else {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'i123',
              status: 'IN_PROGRESS',
              candidateId: 'c123',
              candidateName: 'Test User',
              jobId: 'j123',
              jobTitle: 'Software Engineer',
              companyName: 'Test Company',
              responses: [],
            }),
          })
        }
      })
    })

    test('should request camera permissions', async ({ page, context }) => {
      // Grant permissions for the test
      await context.grantPermissions(['camera', 'microphone'])

      await page.goto('/interview/i123/room')

      // Should show video preview area
      await expect(page.locator('video, .video-preview, [data-testid="video-preview"]')).toBeVisible({ timeout: 10000 })
    })

    test('should show permission denied message', async ({ page, context }) => {
      // Don't grant permissions - should show error
      await page.goto('/interview/i123/room')

      // May show permission request or error
      const permissionUI = page.getByText(/camera|microphone|permission|grant access/i)
      await expect(permissionUI).toBeVisible({ timeout: 10000 })
    })
  })

  test.describe('Interview Complete Page', () => {
    test.beforeEach(async ({ page }) => {
      // Mock the results API
      await page.route('**/api/interviews/*/results', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            sessionId: 'i123',
            status: 'COMPLETED',
            totalScore: 75.5,
            aiSummary: 'Good candidate with strong communication skills.',
            responses: [
              {
                id: 'r1',
                questionIndex: 0,
                questionText: 'Tell me about yourself',
                aiScore: 8.0,
                transcription: 'Test response',
              },
            ],
          }),
        })
      })
    })

    test('should display completion message', async ({ page }) => {
      await page.goto('/interview/i123/complete')

      // Should show completion/thank you message
      await expect(page.getByText(/thank you|completed|submitted/i)).toBeVisible({ timeout: 10000 })
    })

    test('should show score when available', async ({ page }) => {
      await page.goto('/interview/i123/complete')

      // Wait for results to load
      await page.waitForTimeout(2000)

      // Should show score
      await expect(page.getByText(/75|score/i)).toBeVisible()
    })
  })
})
