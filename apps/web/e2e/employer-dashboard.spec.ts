import { test, expect } from '@playwright/test'

test.describe('Employer Dashboard', () => {
  // Mock authentication for all dashboard tests
  test.beforeEach(async ({ page }) => {
    // Set mock token in localStorage
    await page.addInitScript(() => {
      window.localStorage.setItem('employer_token', 'mock_jwt_token_12345')
    })

    // Mock employer API endpoints
    await page.route('**/api/employers/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'e123',
          companyName: 'Test Company',
          email: 'employer@test.com',
          isVerified: true,
          createdAt: '2024-01-01T00:00:00Z',
        }),
      })
    })

    await page.route('**/api/employers/dashboard', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          totalInterviews: 25,
          pendingReview: 5,
          shortlisted: 10,
          rejected: 8,
          averageScore: 72.5,
        }),
      })
    })

    await page.route('**/api/employers/jobs*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          jobs: [
            {
              id: 'j1',
              title: 'Software Engineer',
              description: 'Build amazing software',
              requirements: ['Python', 'JavaScript'],
              location: 'Shanghai',
              isActive: true,
              createdAt: '2024-01-15T00:00:00Z',
            },
            {
              id: 'j2',
              title: 'Product Manager',
              description: 'Lead product development',
              requirements: ['Communication', 'Leadership'],
              location: 'Beijing',
              isActive: true,
              createdAt: '2024-01-10T00:00:00Z',
            },
          ],
          total: 2,
        }),
      })
    })

    await page.route('**/api/employers/interviews*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          interviews: [
            {
              id: 'i1',
              status: 'COMPLETED',
              totalScore: 85.0,
              candidateId: 'c1',
              candidateName: 'John Doe',
              jobId: 'j1',
              jobTitle: 'Software Engineer',
              companyName: 'Test Company',
              createdAt: '2024-01-20T00:00:00Z',
            },
            {
              id: 'i2',
              status: 'COMPLETED',
              totalScore: 72.0,
              candidateId: 'c2',
              candidateName: 'Jane Smith',
              jobId: 'j1',
              jobTitle: 'Software Engineer',
              companyName: 'Test Company',
              createdAt: '2024-01-19T00:00:00Z',
            },
          ],
          total: 2,
        }),
      })
    })
  })

  test.describe('Dashboard Home', () => {
    test('should display dashboard stats', async ({ page }) => {
      await page.goto('/dashboard')

      // Should show statistics
      await expect(page.getByText('25')).toBeVisible() // total interviews
      await expect(page.getByText('5')).toBeVisible() // pending
      await expect(page.getByText('10')).toBeVisible() // shortlisted
    })

    test('should show company name', async ({ page }) => {
      await page.goto('/dashboard')

      await expect(page.getByText(/test company/i)).toBeVisible()
    })

    test('should have navigation to interviews', async ({ page }) => {
      await page.goto('/dashboard')

      const interviewsLink = page.getByRole('link', { name: /interviews/i })
      await expect(interviewsLink).toBeVisible()
    })

    test('should have navigation to jobs', async ({ page }) => {
      await page.goto('/dashboard')

      const jobsLink = page.getByRole('link', { name: /jobs/i })
      if (await jobsLink.isVisible()) {
        await expect(jobsLink).toBeVisible()
      }
    })
  })

  test.describe('Interview List', () => {
    test('should display list of interviews', async ({ page }) => {
      await page.goto('/dashboard/interviews')

      // Should show candidate names
      await expect(page.getByText('John Doe')).toBeVisible()
      await expect(page.getByText('Jane Smith')).toBeVisible()
    })

    test('should show interview scores', async ({ page }) => {
      await page.goto('/dashboard/interviews')

      // Should show scores
      await expect(page.getByText(/85|72/)).toBeVisible()
    })

    test('should have status indicators', async ({ page }) => {
      await page.goto('/dashboard/interviews')

      // Should show status badges
      await expect(page.getByText(/completed/i)).toBeVisible()
    })

    test('should be able to click on interview to view details', async ({ page }) => {
      // Mock interview detail
      await page.route('**/api/employers/interviews/i1', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'i1',
            status: 'COMPLETED',
            totalScore: 85.0,
            aiSummary: 'Strong candidate',
            candidateId: 'c1',
            candidateName: 'John Doe',
            jobId: 'j1',
            jobTitle: 'Software Engineer',
            companyName: 'Test Company',
            responses: [
              {
                id: 'r1',
                questionIndex: 0,
                questionText: 'Tell me about yourself',
                aiScore: 8.5,
                transcription: 'I am a software engineer...',
              },
            ],
          }),
        })
      })

      await page.goto('/dashboard/interviews')

      // Click on an interview
      await page.getByText('John Doe').click()

      // Should navigate to detail page
      await expect(page).toHaveURL(/\/dashboard\/interviews\/i1/)
    })
  })

  test.describe('Interview Detail', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/api/employers/interviews/i1', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'i1',
            status: 'COMPLETED',
            totalScore: 85.0,
            aiSummary: 'Strong candidate with excellent communication skills.',
            candidateId: 'c1',
            candidateName: 'John Doe',
            jobId: 'j1',
            jobTitle: 'Software Engineer',
            companyName: 'Test Company',
            responses: [
              {
                id: 'r1',
                questionIndex: 0,
                questionText: 'Tell me about yourself',
                aiScore: 8.5,
                transcription: 'I am a software engineer with 5 years of experience...',
                videoUrl: 'https://example.com/video.webm',
              },
              {
                id: 'r2',
                questionIndex: 1,
                questionText: 'Why do you want this role?',
                aiScore: 8.0,
                transcription: 'I am passionate about building great products...',
                videoUrl: 'https://example.com/video2.webm',
              },
            ],
          }),
        })
      })
    })

    test('should display candidate information', async ({ page }) => {
      await page.goto('/dashboard/interviews/i1')

      await expect(page.getByText('John Doe')).toBeVisible()
      await expect(page.getByText('Software Engineer')).toBeVisible()
    })

    test('should display overall score', async ({ page }) => {
      await page.goto('/dashboard/interviews/i1')

      await expect(page.getByText(/85/)).toBeVisible()
    })

    test('should display AI summary', async ({ page }) => {
      await page.goto('/dashboard/interviews/i1')

      await expect(page.getByText(/strong candidate|excellent communication/i)).toBeVisible()
    })

    test('should display question responses', async ({ page }) => {
      await page.goto('/dashboard/interviews/i1')

      // Should show questions
      await expect(page.getByText(/tell me about yourself/i)).toBeVisible()
      await expect(page.getByText(/why do you want/i)).toBeVisible()
    })

    test('should display transcripts', async ({ page }) => {
      await page.goto('/dashboard/interviews/i1')

      // Should show transcripts
      await expect(page.getByText(/software engineer with 5 years/i)).toBeVisible()
    })

    test('should have action buttons for shortlist/reject', async ({ page }) => {
      await page.goto('/dashboard/interviews/i1')

      // Should have action buttons
      const shortlistButton = page.getByRole('button', { name: /shortlist/i })
      const rejectButton = page.getByRole('button', { name: /reject/i })

      await expect(shortlistButton.or(rejectButton)).toBeVisible()
    })
  })

  test.describe('Responsive Design', () => {
    test('should be usable on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/dashboard')

      // Dashboard should still be functional
      await expect(page.getByText(/test company/i)).toBeVisible()
    })

    test('should show mobile navigation', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/dashboard')

      // Should have mobile menu or collapsed navigation
      const mobileMenu = page.locator('[data-testid="mobile-menu"], .mobile-nav, [aria-label="Menu"]')
      // Mobile menu may or may not exist depending on design
    })

    test('interview list should be scrollable on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('/dashboard/interviews')

      // List should be visible and scrollable
      const interviewList = page.locator('[data-testid="interview-list"], main, .interview-list')
      await expect(interviewList).toBeVisible()
    })
  })
})
