/**
 * API client for ZhiMian (智面) backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
export interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  targetRoles: string[]
  resumeUrl?: string
  createdAt: string
}

export type Vertical = 'new_energy' | 'sales'
export type RoleType =
  | 'battery_engineer'
  | 'embedded_software'
  | 'autonomous_driving'
  | 'supply_chain'
  | 'ev_sales'
  | 'sales_rep'
  | 'bd_manager'
  | 'account_manager'

export interface Job {
  id: string
  title: string
  description: string
  vertical?: Vertical
  roleType?: RoleType
  requirements: string[]
  location?: string
  salaryMin?: number
  salaryMax?: number
  isActive: boolean
  employerId: string
  createdAt: string
}

export interface Employer {
  id: string
  companyName: string
  email: string
  logo?: string
  isVerified: boolean
  createdAt: string
}

export interface QuestionInfo {
  index: number
  text: string
  textZh?: string
  category?: string
}

export interface InterviewStartResponse {
  sessionId: string
  questions: QuestionInfo[]
  jobTitle: string
  companyName: string
}

export interface ResponseSubmitResult {
  responseId: string
  questionIndex: number
  status: string
  videoUrl?: string
}

export interface ScoreDetails {
  communication: number  // 沟通能力
  problemSolving: number  // 解决问题能力
  domainKnowledge: number  // 专业知识
  motivation: number  // 动机
  cultureFit: number  // 文化契合度
  overall: number
  analysis: string
  strengths: string[]
  concerns: string[]
  highlightQuotes?: string[]
}

export interface ResponseDetail {
  id: string
  questionIndex: number
  questionText: string
  videoUrl?: string
  transcription?: string
  aiScore?: number
  aiAnalysis?: string
  scoreDetails?: ScoreDetails
  durationSeconds?: number
  createdAt: string
}

export interface InterviewSession {
  id: string
  status: 'PENDING' | 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  totalScore?: number
  aiSummary?: string
  startedAt?: string
  completedAt?: string
  createdAt: string
  candidateId: string
  candidateName?: string
  jobId: string
  jobTitle?: string
  companyName?: string
  responses: ResponseDetail[]
}

export interface InterviewResults {
  sessionId: string
  status: string
  totalScore?: number
  aiSummary?: string
  recommendation?: string
  overallStrengths: string[]
  overallImprovements: string[]
  responses: ResponseDetail[]
}

export interface UploadUrlResponse {
  uploadUrl: string
  storageKey: string
  expiresIn: number
}

export interface DashboardStats {
  totalInterviews: number
  pendingReview: number
  shortlisted: number
  rejected: number
  averageScore?: number
}

export interface EmployerWithToken {
  employer: Employer
  token: string
  tokenType: string
}

// API Error class
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Helper to make API requests
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  }

  // Add auth token if available
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('employer_token')
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let message = 'Request failed'
    try {
      const error = await response.json()
      message = error.detail || error.message || message
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(response.status, message)
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

// Candidate API
export const candidateApi = {
  register: (data: {
    name: string
    email: string
    phone: string
    targetRoles: string[]
  }): Promise<Candidate> =>
    apiRequest('/api/candidates/', {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        email: data.email,
        phone: data.phone,
        target_roles: data.targetRoles,
      }),
    }),

  get: (id: string): Promise<Candidate> =>
    apiRequest(`/api/candidates/${id}`),
}

// Interview API
export const interviewApi = {
  start: (candidateId: string, jobId: string): Promise<InterviewStartResponse> =>
    apiRequest('/api/interviews/start', {
      method: 'POST',
      body: JSON.stringify({
        candidate_id: candidateId,
        job_id: jobId,
      }),
    }),

  get: (sessionId: string): Promise<InterviewSession> =>
    apiRequest(`/api/interviews/${sessionId}`),

  getUploadUrl: (sessionId: string, questionIndex: number): Promise<UploadUrlResponse> =>
    apiRequest(`/api/interviews/${sessionId}/upload-url?question_index=${questionIndex}`),

  submitResponse: async (
    sessionId: string,
    questionIndex: number,
    videoBlob: Blob
  ): Promise<ResponseSubmitResult> => {
    const formData = new FormData()
    formData.append('video', videoBlob, 'video.webm')

    const url = `${API_BASE_URL}/api/interviews/${sessionId}/response?question_index=${questionIndex}`
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to submit response')
    }

    return response.json()
  },

  complete: (sessionId: string): Promise<InterviewResults> =>
    apiRequest(`/api/interviews/${sessionId}/complete`, {
      method: 'POST',
    }),

  getResults: (sessionId: string): Promise<InterviewResults> =>
    apiRequest(`/api/interviews/${sessionId}/results`),
}

// Employer API
export const employerApi = {
  register: (data: {
    companyName: string
    email: string
    password: string
  }): Promise<EmployerWithToken> =>
    apiRequest('/api/employers/register', {
      method: 'POST',
      body: JSON.stringify({
        company_name: data.companyName,
        email: data.email,
        password: data.password,
      }),
    }),

  login: (email: string, password: string): Promise<EmployerWithToken> =>
    apiRequest('/api/employers/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  getMe: (): Promise<Employer> =>
    apiRequest('/api/employers/me'),

  getDashboard: (): Promise<DashboardStats> =>
    apiRequest('/api/employers/dashboard'),

  listJobs: (isActive?: boolean): Promise<{ jobs: Job[]; total: number }> =>
    apiRequest(`/api/employers/jobs${isActive !== undefined ? `?is_active=${isActive}` : ''}`),

  createJob: (data: {
    title: string
    description: string
    requirements: string[]
    location?: string
    salaryMin?: number
    salaryMax?: number
    vertical?: string
    roleType?: string
  }): Promise<Job> =>
    apiRequest('/api/employers/jobs', {
      method: 'POST',
      body: JSON.stringify({
        title: data.title,
        description: data.description,
        requirements: data.requirements,
        location: data.location,
        salary_min: data.salaryMin,
        salary_max: data.salaryMax,
        vertical: data.vertical,
        role_type: data.roleType,
      }),
    }),

  listInterviews: (params?: {
    skip?: number
    limit?: number
    jobId?: string
    status?: string
    minScore?: number
  }): Promise<{ interviews: InterviewSession[]; total: number }> => {
    const searchParams = new URLSearchParams()
    if (params?.skip) searchParams.set('skip', params.skip.toString())
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.jobId) searchParams.set('job_id', params.jobId)
    if (params?.status) searchParams.set('status_filter', params.status)
    if (params?.minScore) searchParams.set('min_score', params.minScore.toString())

    const query = searchParams.toString()
    return apiRequest(`/api/employers/interviews${query ? `?${query}` : ''}`)
  },

  getInterview: (id: string): Promise<InterviewSession> =>
    apiRequest(`/api/employers/interviews/${id}`),

  updateInterviewStatus: (id: string, status: 'SHORTLISTED' | 'REJECTED'): Promise<InterviewSession> =>
    apiRequest(`/api/employers/interviews/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
}

// Questions API
export const questionsApi = {
  list: (jobId?: string): Promise<{ questions: QuestionInfo[]; total: number }> =>
    apiRequest(`/api/questions/${jobId ? `job/${jobId}` : 'defaults'}`),

  seedDefaults: (): Promise<{ questions: QuestionInfo[]; total: number }> =>
    apiRequest('/api/questions/seed-defaults', { method: 'POST' }),
}

// Invite Token types and API
export interface InviteValidation {
  valid: boolean
  jobId?: string
  jobTitle?: string
  companyName?: string
  error?: string
}

export interface InviteTokenResponse {
  id: string
  token: string
  jobId: string
  jobTitle?: string
  maxUses: number
  usedCount: number
  expiresAt?: string
  isActive: boolean
  inviteUrl: string
  createdAt: string
}

export const inviteApi = {
  validate: (token: string): Promise<InviteValidation> =>
    apiRequest(`/api/interviews/invite/validate/${token}`),

  registerAndStart: (data: {
    name: string
    email: string
    phone: string
    inviteToken: string
  }): Promise<InterviewStartResponse> =>
    apiRequest('/api/interviews/invite/register-and-start', {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        email: data.email,
        phone: data.phone,
        invite_token: data.inviteToken,
      }),
    }),

  createToken: (jobId: string, maxUses: number = 0, expiresInDays?: number): Promise<InviteTokenResponse> =>
    apiRequest(`/api/employers/jobs/${jobId}/invites`, {
      method: 'POST',
      body: JSON.stringify({
        job_id: jobId,
        max_uses: maxUses,
        expires_in_days: expiresInDays,
      }),
    }),

  listTokens: (jobId: string): Promise<{ tokens: InviteTokenResponse[]; total: number }> =>
    apiRequest(`/api/employers/jobs/${jobId}/invites`),

  deleteToken: (inviteId: string): Promise<void> =>
    apiRequest(`/api/employers/invites/${inviteId}`, { method: 'DELETE' }),
}
