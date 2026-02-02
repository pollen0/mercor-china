/**
 * Tests for API client.
 */
import { ApiError, candidateApi, employerApi, interviewApi, inviteApi } from '@/lib/api'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('ApiError', () => {
  it('creates error with status and message', () => {
    const error = new ApiError(404, 'Not found')
    expect(error.status).toBe(404)
    expect(error.message).toBe('Not found')
    expect(error.name).toBe('ApiError')
  })

  it('creates error with details', () => {
    const error = new ApiError(400, 'Bad request', { field: 'email' })
    expect(error.details).toEqual({ field: 'email' })
  })
})

describe('candidateApi', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    ;(localStorage.getItem as jest.Mock).mockClear()
  })

  describe('register', () => {
    it('sends correct request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve({ id: 'c123', name: 'Test' }),
      })

      await candidateApi.register({
        name: 'Test User',
        email: 'test@example.com',
        phone: '13800138000',
        targetRoles: ['Engineer'],
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/candidates/'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('transforms request data to snake_case', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve({ id: 'c123' }),
      })

      await candidateApi.register({
        name: 'Test',
        email: 'test@example.com',
        phone: '13800138000',
        targetRoles: ['Engineer'],
      })

      const callArgs = mockFetch.mock.calls[0]
      const body = JSON.parse(callArgs[1].body)
      expect(body).toHaveProperty('target_roles')
    })
  })

  describe('get', () => {
    it('fetches candidate by id', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'c123', name: 'Test' }),
      })

      const result = await candidateApi.get('c123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/candidates/c123'),
        expect.any(Object)
      )
      expect(result).toEqual({ id: 'c123', name: 'Test' })
    })
  })
})

describe('employerApi', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    ;(localStorage.getItem as jest.Mock).mockClear()
  })

  describe('register', () => {
    it('sends registration request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve({
          employer: { id: 'e123', companyName: 'Test Corp' },
          token: 'jwt-token',
        }),
      })

      await employerApi.register({
        companyName: 'Test Corp',
        email: 'employer@test.com',
        password: 'password123',
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/employers/register'),
        expect.objectContaining({ method: 'POST' })
      )
    })
  })

  describe('login', () => {
    it('sends login request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          employer: { id: 'e123' },
          token: 'jwt-token',
        }),
      })

      await employerApi.login('test@example.com', 'password123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/employers/login'),
        expect.objectContaining({ method: 'POST' })
      )
    })
  })

  describe('getMe', () => {
    it('includes auth token in request', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'e123' }),
      })

      await employerApi.getMe()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      )
    })
  })

  describe('listJobs', () => {
    it('fetches jobs without filter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ jobs: [], total: 0 }),
      })

      await employerApi.listJobs()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/employers/jobs'),
        expect.any(Object)
      )
    })

    it('fetches jobs with active filter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ jobs: [], total: 0 }),
      })

      await employerApi.listJobs(true)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('is_active=true'),
        expect.any(Object)
      )
    })
  })
})

describe('interviewApi', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    ;(localStorage.getItem as jest.Mock).mockClear()
  })

  describe('start', () => {
    it('starts interview session', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          sessionId: 'i123',
          questions: [],
          jobTitle: 'Engineer',
          companyName: 'Test Corp',
        }),
      })

      await interviewApi.start('c123', 'j123')

      const callArgs = mockFetch.mock.calls[0]
      const body = JSON.parse(callArgs[1].body)
      expect(body).toEqual({
        candidate_id: 'c123',
        job_id: 'j123',
        is_practice: false,
      })
    })
  })

  describe('get', () => {
    it('fetches interview session', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'i123', status: 'IN_PROGRESS' }),
      })

      await interviewApi.get('i123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/interviews/i123'),
        expect.any(Object)
      )
    })
  })

  describe('getUploadUrl', () => {
    it('gets presigned upload URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          uploadUrl: 'https://upload.example.com',
          storageKey: 'videos/test.webm',
          expiresIn: 3600,
        }),
      })

      const result = await interviewApi.getUploadUrl('i123', 0)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/interviews/i123/upload-url'),
        expect.any(Object)
      )
      expect(result.uploadUrl).toBe('https://upload.example.com')
    })
  })

  describe('complete', () => {
    it('completes interview', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          sessionId: 'i123',
          status: 'COMPLETED',
        }),
      })

      await interviewApi.complete('i123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/interviews/i123/complete'),
        expect.objectContaining({ method: 'POST' })
      )
    })
  })
})

describe('inviteApi', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    ;(localStorage.getItem as jest.Mock).mockClear()
  })

  describe('validate', () => {
    it('validates invite token', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          valid: true,
          jobId: 'j123',
          jobTitle: 'Engineer',
          companyName: 'Test Corp',
        }),
      })

      const result = await inviteApi.validate('test-token')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/interviews/invite/validate/test-token'),
        expect.any(Object)
      )
      expect(result.valid).toBe(true)
    })
  })

  describe('registerAndStart', () => {
    it('registers candidate and starts interview', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          sessionId: 'i123',
          questions: [],
        }),
      })

      await inviteApi.registerAndStart({
        name: 'Test User',
        email: 'test@example.com',
        phone: '13800138000',
        inviteToken: 'test-token',
      })

      const callArgs = mockFetch.mock.calls[0]
      const body = JSON.parse(callArgs[1].body)
      expect(body).toHaveProperty('invite_token', 'test-token')
    })
  })

  describe('createToken', () => {
    it('creates invite token', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve({
          id: 'inv123',
          token: 'new-token',
          inviteUrl: 'https://example.com/invite',
        }),
      })

      await inviteApi.createToken('j123', 10, 7)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/employers/jobs/j123/invites'),
        expect.objectContaining({ method: 'POST' })
      )
    })
  })
})

describe('GitHub OAuth (candidateApi)', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    ;(localStorage.getItem as jest.Mock).mockClear()
  })

  describe('getGitHubAuthUrl', () => {
    it('fetches GitHub OAuth URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          authUrl: 'https://github.com/login/oauth/authorize?client_id=xxx',
          state: 'abc123',
        }),
      })

      const result = await candidateApi.getGitHubAuthUrl()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/candidates/auth/github/url'),
        expect.any(Object)
      )
      expect(result.authUrl).toContain('github.com')
      expect(result.state).toBe('abc123')
    })

    it('includes state parameter when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ authUrl: 'https://github.com/...', state: 'custom-state' }),
      })

      await candidateApi.getGitHubAuthUrl('custom-state')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('state=custom-state'),
        expect.any(Object)
      )
    })
  })

  describe('connectGitHub', () => {
    it('exchanges code for GitHub connection', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: 'GitHub connected',
          github_username: 'testuser',
          github_data: {
            username: 'testuser',
            avatar_url: 'https://github.com/avatar.jpg',
            profile_url: 'https://github.com/testuser',
            public_repos: 10,
            followers: 5,
            following: 3,
            repos: [{ name: 'repo1', description: 'Test', language: 'TypeScript', stars: 5, forks: 1, url: 'https://github.com/testuser/repo1', updated_at: '2024-01-01' }],
            languages: { TypeScript: 1000, Python: 500 },
            total_contributions: 100,
          },
        }),
      })

      const result = await candidateApi.connectGitHub('auth-code', 'state')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/candidates/auth/github/callback'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('auth-code'),
        })
      )
      expect(result.success).toBe(true)
      expect(result.githubUsername).toBe('testuser')
      expect(result.githubData.repos).toHaveLength(1)
      expect(result.githubData.languages).toHaveProperty('TypeScript', 1000)
    })
  })

  describe('disconnectGitHub', () => {
    it('disconnects GitHub account', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, message: 'GitHub disconnected' }),
      })

      const result = await candidateApi.disconnectGitHub()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/candidates/me/github'),
        expect.objectContaining({ method: 'DELETE' })
      )
      expect(result.success).toBe(true)
    })
  })

  describe('getGitHubInfo', () => {
    it('returns GitHub data when connected', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          connected: true,
          username: 'testuser',
          avatar_url: 'https://github.com/avatar.jpg',
          profile_url: 'https://github.com/testuser',
          public_repos: 10,
          followers: 5,
          following: 3,
          repos: [],
          languages: {},
          total_contributions: 50,
          connected_at: '2024-01-01T00:00:00Z',
        }),
      })

      const result = await candidateApi.getGitHubInfo()

      expect(result).not.toBeNull()
      expect(result?.username).toBe('testuser')
      expect(result?.publicRepos).toBe(10)
    })

    it('returns null when not connected', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ connected: false }),
      })

      const result = await candidateApi.getGitHubInfo()

      expect(result).toBeNull()
    })

    it('returns null on error', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Unauthorized' }),
      })

      const result = await candidateApi.getGitHubInfo()

      expect(result).toBeNull()
    })
  })

  describe('refreshGitHubData', () => {
    it('refreshes GitHub profile data', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: 'GitHub data refreshed',
          github_data: {
            username: 'testuser',
            profile_url: 'https://github.com/testuser',
            public_repos: 15,
            followers: 10,
            following: 5,
            repos: [],
            languages: { JavaScript: 2000 },
            total_contributions: 200,
          },
        }),
      })

      const result = await candidateApi.refreshGitHubData()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/candidates/me/github/refresh'),
        expect.objectContaining({ method: 'POST' })
      )
      expect(result.publicRepos).toBe(15)
      expect(result.totalContributions).toBe(200)
    })
  })
})

describe('Education (candidateApi)', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    ;(localStorage.getItem as jest.Mock).mockClear()
  })

  describe('updateEducation', () => {
    it('updates education info', async () => {
      ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          id: 'c123',
          name: 'Test User',
          university: 'Stanford',
          major: 'Computer Science',
          graduationYear: 2025,
          gpa: 3.8,
          courses: ['CS101', 'CS201'],
        }),
      })

      const result = await candidateApi.updateEducation({
        university: 'Stanford',
        major: 'Computer Science',
        graduationYear: 2025,
        gpa: 3.8,
        courses: ['CS101', 'CS201'],
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/candidates/me'),
        expect.objectContaining({
          method: 'PATCH',
          body: expect.stringContaining('graduation_year'),
        })
      )
    })
  })
})

describe('API Error Handling', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    ;(localStorage.getItem as jest.Mock).mockClear()
  })

  it('throws ApiError on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: 'Not found' }),
    })

    await expect(candidateApi.get('nonexistent')).rejects.toThrow(ApiError)
  })

  it('handles 204 No Content', async () => {
    ;(localStorage.getItem as jest.Mock).mockReturnValue('test-token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
    })

    const result = await inviteApi.deleteToken('inv123')
    expect(result).toBeUndefined()
  })
})
