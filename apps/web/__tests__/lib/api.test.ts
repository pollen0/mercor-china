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
    localStorage.getItem = jest.fn()
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
    localStorage.getItem = jest.fn()
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
    localStorage.getItem = jest.fn()
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
    localStorage.getItem = jest.fn()
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

describe('API Error Handling', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    localStorage.getItem = jest.fn()
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
