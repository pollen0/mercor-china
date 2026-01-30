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
  resumeParsedData?: ParsedResumeData
  resumeUploadedAt?: string
  createdAt: string
}

export interface ParsedResumeData {
  name?: string
  email?: string
  phone?: string
  location?: string
  summary?: string
  skills: string[]
  experience: Array<{
    company: string
    title: string
    startDate?: string
    endDate?: string
    description?: string
    highlights?: string[]
  }>
  education: Array<{
    institution: string
    degree?: string
    fieldOfStudy?: string
    startDate?: string
    endDate?: string
  }>
  projects: Array<{
    name: string
    description?: string
    technologies?: string[]
  }>
  languages?: string[]
  certifications?: string[]
}

export interface ResumeParseResult {
  success: boolean
  message: string
  resumeUrl?: string
  parsedData?: ParsedResumeData
  rawTextPreview?: string
}

export interface ResumeResponse {
  candidateId: string
  resumeUrl?: string
  rawText?: string
  parsedData?: ParsedResumeData
  uploadedAt?: string
}

export interface PersonalizedQuestion {
  text: string
  textZh: string
  category: string
  basedOn: string
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
  questionType?: string
  codingChallengeId?: string | null
}

export interface InterviewStartResponse {
  sessionId: string
  questions: QuestionInfo[]
  jobTitle: string
  companyName: string
  isPractice: boolean
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
  isPractice: boolean
  totalScore?: number
  aiSummary?: string
  startedAt?: string
  completedAt?: string
  createdAt: string
  candidateId: string
  candidateName?: string
  jobId?: string
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
  overallConcerns: string[]
  responses: ResponseDetail[]
}

export interface PracticeFeedback {
  responseId: string
  questionIndex: number
  scoreDetails: ScoreDetails
  tips: string[]
  sampleAnswer?: string
}

// Follow-up question types
export interface FollowupResponse {
  hasFollowups: boolean
  questionIndex: number
  followupQuestions: string[]
  queueId?: string
}

export interface FollowupQuestionInfo {
  queueId: string
  questionIndex: number
  followupIndex: number
  questionText: string
  isFollowup: boolean
}

// Coding challenge types
export interface TestCase {
  input: string
  expected: string
  hidden: boolean
  name?: string
}

export interface TestCaseResult {
  name: string
  passed: boolean
  actual: string
  expected: string
  hidden: boolean
  error?: string
}

export interface CodingChallenge {
  id: string
  title: string
  titleZh?: string
  description: string
  descriptionZh?: string
  starterCode?: string
  testCases: TestCase[]
  timeLimitSeconds: number
  difficulty: string
  createdAt: string
}

export interface CodingQuestionInfo {
  index: number
  text: string
  textZh?: string
  category?: string
  questionType: string
  codingChallenge?: CodingChallenge
}

export interface CodeExecutionResponse {
  responseId: string
  questionIndex: number
  status: string
  executionTimeMs?: number
  testResults?: TestCaseResult[]
  passedCount?: number
  totalCount?: number
}

export interface CodingFeedback {
  responseId: string
  questionIndex: number
  executionStatus: string
  testResults: TestCaseResult[]
  passedCount: number
  totalCount: number
  executionTimeMs: number
  aiScore?: number
  analysis?: string
  strengths: string[]
  concerns: string[]
  tips: string[]
  suggestedApproach?: string
  timeComplexity?: string
  optimalComplexity?: string
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

export interface BulkActionResult {
  success: boolean
  processed: number
  failed: number
  errors: string[]
}

export interface MessageResponse {
  id: string
  subject: string
  body: string
  messageType: string
  employerId: string
  candidateId: string
  jobId?: string
  sentAt: string
  readAt?: string
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

  // Add auth token if available (check both employer and candidate tokens)
  if (typeof window !== 'undefined') {
    const employerToken = localStorage.getItem('employer_token')
    const candidateToken = localStorage.getItem('candidate_token')
    const token = employerToken || candidateToken
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

  uploadResume: async (candidateId: string, file: File, token?: string): Promise<ResumeParseResult> => {
    const formData = new FormData()
    formData.append('file', file)

    const url = `${API_BASE_URL}/api/candidates/${candidateId}/resume`
    const headers: Record<string, string> = {}

    // Get auth token
    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to upload resume')
    }

    // Transform snake_case to camelCase
    const data = await response.json()
    return {
      success: data.success,
      message: data.message,
      resumeUrl: data.resume_url,
      parsedData: data.parsed_data,
      rawTextPreview: data.raw_text_preview,
    }
  },

  getMyResume: async (token?: string): Promise<ResumeResponse> => {
    const url = `${API_BASE_URL}/api/candidates/me/resume`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(url, { headers })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to get resume')
    }

    // Transform snake_case to camelCase
    const data = await response.json()
    return {
      candidateId: data.candidate_id,
      resumeUrl: data.resume_url,
      rawText: data.raw_text,
      parsedData: data.parsed_data,
      uploadedAt: data.uploaded_at,
    }
  },

  getResume: (candidateId: string): Promise<ResumeResponse> =>
    apiRequest(`/api/candidates/${candidateId}/resume`),

  deleteResume: async (token?: string): Promise<{ success: boolean; message: string }> => {
    const url = `${API_BASE_URL}/api/candidates/me/resume`
    const headers: Record<string, string> = {}

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(url, {
      method: 'DELETE',
      headers,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to delete resume')
    }

    return response.json()
  },

  getPersonalizedQuestions: (
    candidateId: string,
    jobId?: string,
    numQuestions: number = 3
  ): Promise<PersonalizedQuestion[]> => {
    const params = new URLSearchParams()
    if (jobId) params.set('job_id', jobId)
    params.set('num_questions', numQuestions.toString())
    return apiRequest(`/api/candidates/${candidateId}/resume/personalized-questions?${params}`)
  },
}

// Interview API
export const interviewApi = {
  start: (candidateId: string, jobId?: string, isPractice: boolean = false): Promise<InterviewStartResponse> =>
    apiRequest('/api/interviews/start', {
      method: 'POST',
      body: JSON.stringify({
        candidate_id: candidateId,
        job_id: jobId || null,
        is_practice: isPractice,
      }),
    }),

  startPractice: (candidateId: string, jobId?: string): Promise<InterviewStartResponse> =>
    apiRequest('/api/interviews/start', {
      method: 'POST',
      body: JSON.stringify({
        candidate_id: candidateId,
        job_id: jobId || null,
        is_practice: true,
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

  getPracticeFeedback: (sessionId: string, responseId: string): Promise<PracticeFeedback> =>
    apiRequest(`/api/interviews/${sessionId}/practice-feedback/${responseId}`),

  // Follow-up question endpoints
  getFollowups: (sessionId: string, questionIndex: number): Promise<FollowupResponse> =>
    apiRequest(`/api/interviews/${sessionId}/followup?question_index=${questionIndex}`),

  askFollowup: (sessionId: string, questionIndex: number, followupIndex: number): Promise<FollowupQuestionInfo> =>
    apiRequest(`/api/interviews/${sessionId}/followup/ask?question_index=${questionIndex}`, {
      method: 'POST',
      body: JSON.stringify({ followup_index: followupIndex }),
    }),

  skipFollowup: (sessionId: string, questionIndex: number): Promise<{ status: string; questionIndex: number }> =>
    apiRequest(`/api/interviews/${sessionId}/followup/skip?question_index=${questionIndex}`, {
      method: 'POST',
    }),

  submitFollowupResponse: async (
    sessionId: string,
    queueId: string,
    videoBlob: Blob
  ): Promise<ResponseSubmitResult> => {
    const formData = new FormData()
    formData.append('video', videoBlob, 'video.webm')

    const url = `${API_BASE_URL}/api/interviews/${sessionId}/followup/response?queue_id=${queueId}`
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to submit follow-up response')
    }

    return response.json()
  },

  // Coding challenge endpoints
  getCodingChallenge: (sessionId: string, questionIndex: number): Promise<CodingQuestionInfo> =>
    apiRequest(`/api/interviews/${sessionId}/coding-challenge/${questionIndex}`),

  submitCode: (sessionId: string, questionIndex: number, code: string): Promise<CodeExecutionResponse> =>
    apiRequest(`/api/interviews/${sessionId}/code-response?question_index=${questionIndex}`, {
      method: 'POST',
      body: JSON.stringify({ code }),
    }),

  getCodingFeedback: (sessionId: string, responseId: string): Promise<CodingFeedback> =>
    apiRequest(`/api/interviews/${sessionId}/code-response/${responseId}`),

  // Poll for coding results (helper that polls until complete)
  pollCodingResults: async (
    sessionId: string,
    responseId: string,
    maxAttempts: number = 30,
    intervalMs: number = 2000
  ): Promise<CodingFeedback> => {
    for (let i = 0; i < maxAttempts; i++) {
      const feedback = await interviewApi.getCodingFeedback(sessionId, responseId)

      // Check if processing is complete
      if (feedback.executionStatus !== 'processing') {
        return feedback
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, intervalMs))
    }

    throw new ApiError(408, 'Timeout waiting for code execution results')
  },
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

  updateJob: (jobId: string, data: {
    title?: string
    description?: string
    requirements?: string[]
    location?: string
    salaryMin?: number
    salaryMax?: number
    vertical?: string
    roleType?: string
    isActive?: boolean
  }): Promise<Job> =>
    apiRequest(`/api/employers/jobs/${jobId}`, {
      method: 'PUT',
      body: JSON.stringify({
        title: data.title,
        description: data.description,
        requirements: data.requirements,
        location: data.location,
        salary_min: data.salaryMin,
        salary_max: data.salaryMax,
        vertical: data.vertical,
        role_type: data.roleType,
        is_active: data.isActive,
      }),
    }),

  deleteJob: (jobId: string): Promise<void> =>
    apiRequest(`/api/employers/jobs/${jobId}`, {
      method: 'DELETE',
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

  bulkAction: (interviewIds: string[], action: 'shortlist' | 'reject'): Promise<BulkActionResult> =>
    apiRequest('/api/employers/interviews/bulk-action', {
      method: 'POST',
      body: JSON.stringify({
        interview_ids: interviewIds,
        action,
      }),
    }),

  contactCandidate: (
    candidateId: string,
    data: { subject: string; body: string; messageType: string; jobId?: string }
  ): Promise<MessageResponse> =>
    apiRequest(`/api/employers/candidates/${candidateId}/contact`, {
      method: 'POST',
      body: JSON.stringify({
        subject: data.subject,
        body: data.body,
        message_type: data.messageType,
        job_id: data.jobId,
      }),
    }),

  exportInterviewsCsv: async (jobId?: string): Promise<Blob> => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('employer_token') : null
    const url = `${API_BASE_URL}/api/employers/interviews/export${jobId ? `?job_id=${jobId}` : ''}`

    const response = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })

    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to export interviews')
    }

    return response.blob()
  },
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


// ==================== VERTICAL / TALENT POOL TYPES ====================

export interface VerticalProfile {
  id: string
  vertical: Vertical
  roleType: RoleType
  status: 'pending' | 'in_progress' | 'completed'
  interviewScore?: number
  bestScore?: number
  attemptCount: number
  lastAttemptAt?: string
  completedAt?: string
  canRetake: boolean
  nextRetakeAvailableAt?: string
}

export type MatchStatus = 'PENDING' | 'CONTACTED' | 'IN_REVIEW' | 'SHORTLISTED' | 'REJECTED' | 'HIRED'

export interface TalentPoolCandidate {
  profileId: string
  candidateId: string
  candidateName: string
  candidateEmail: string
  vertical: string
  roleType: string
  interviewScore?: number
  bestScore?: number
  status: string
  completedAt?: string
  skills: string[]
  experienceSummary?: string
  location?: string
}

// Enhanced profile response with video and scoring details
export interface InterviewResponseDetail {
  id: string
  questionIndex: number
  questionText: string
  videoUrl?: string
  audioUrl?: string
  transcription?: string
  aiScore?: number
  aiAnalysis?: string
  durationSeconds?: number
  isFollowup: boolean
  questionType: string
  createdAt: string
  // Scoring dimensions breakdown
  scoringDimensions?: {
    communication?: number
    problemSolving?: number
    domainKnowledge?: number
    motivation?: number
    cultureFit?: number
  }
}

export interface TalentProfileDetail {
  profile: {
    id: string
    vertical: string
    roleType: string
    interviewScore?: number
    bestScore?: number
    attemptCount: number
    completedAt?: string
  }
  candidate: {
    id: string
    name: string
    email: string
    phone: string
    resumeUrl?: string
    resumeData?: Record<string, unknown>
  }
  interview?: {
    sessionId: string
    totalScore?: number
    aiSummary?: string
    completedAt?: string
    responses?: InterviewResponseDetail[]
  }
  // Employer's status for this candidate
  employerStatus?: {
    matchId?: string
    status: MatchStatus
    updatedAt?: string
  }
}

export interface MatchingJob {
  jobId: string
  jobTitle: string
  companyName: string
  vertical: string
  roleType?: string
  location?: string
  salaryMin?: number
  salaryMax?: number
  matchScore?: number
  matchStatus?: string
}

// ==================== VERTICAL / TALENT POOL API ====================

export const verticalApi = {
  // Start a vertical interview for talent pool
  startVerticalInterview: async (
    candidateId: string,
    vertical: Vertical,
    roleType: RoleType
  ): Promise<InterviewStartResponse> => {
    const response = await apiRequest<{
      session_id: string
      questions: Array<{
        index: number
        text: string
        text_zh?: string
        category?: string
        question_type?: string
        coding_challenge_id?: string | null
      }>
      job_title: string
      company_name: string
      is_practice: boolean
    }>('/api/interviews/start-vertical', {
      method: 'POST',
      body: JSON.stringify({
        candidate_id: candidateId,
        vertical,
        role_type: roleType,
      }),
    })

    // Transform snake_case to camelCase
    return {
      sessionId: response.session_id,
      questions: response.questions.map(q => ({
        index: q.index,
        text: q.text,
        textZh: q.text_zh,
        category: q.category,
        questionType: q.question_type,
        codingChallengeId: q.coding_challenge_id,
      })),
      jobTitle: response.job_title,
      companyName: response.company_name,
      isPractice: response.is_practice,
    }
  },
}

// Add candidate API methods for vertical profiles
export const candidateVerticalApi = {
  // Get candidate's vertical profiles
  getMyVerticals: async (token?: string): Promise<{ profiles: VerticalProfile[]; total: number }> => {
    const url = `${API_BASE_URL}/api/candidates/me/verticals`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(url, { headers })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to get vertical profiles')
    }

    // Transform snake_case to camelCase
    const data = await response.json()
    return {
      profiles: data.profiles.map((p: Record<string, unknown>) => ({
        id: p.id,
        vertical: p.vertical,
        roleType: p.role_type,
        status: p.status,
        interviewScore: p.interview_score,
        bestScore: p.best_score,
        attemptCount: p.attempt_count,
        lastAttemptAt: p.last_attempt_at,
        completedAt: p.completed_at,
        canRetake: p.can_retake,
        nextRetakeAvailableAt: p.next_retake_available_at,
      })),
      total: data.total,
    }
  },

  // Get jobs matching candidate's completed verticals
  getMatchingJobs: async (token?: string): Promise<{ jobs: MatchingJob[]; total: number }> => {
    const url = `${API_BASE_URL}/api/candidates/me/matching-jobs`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(url, { headers })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to get matching jobs')
    }

    const data = await response.json()
    return {
      jobs: data.jobs.map((j: Record<string, unknown>) => ({
        jobId: j.job_id,
        jobTitle: j.job_title,
        companyName: j.company_name,
        vertical: j.vertical,
        roleType: j.role_type,
        location: j.location,
        salaryMin: j.salary_min,
        salaryMax: j.salary_max,
        matchScore: j.match_score,
        matchStatus: j.match_status,
      })),
      total: data.total,
    }
  },
}

// Add employer API methods for talent pool
export const talentPoolApi = {
  // Browse talent pool with search
  browse: (params?: {
    vertical?: Vertical
    roleType?: RoleType
    minScore?: number
    search?: string  // Full-text search on name, skills, resume
    limit?: number
    offset?: number
  }): Promise<{ candidates: TalentPoolCandidate[]; total: number }> => {
    const searchParams = new URLSearchParams()
    if (params?.vertical) searchParams.set('vertical', params.vertical)
    if (params?.roleType) searchParams.set('role_type', params.roleType)
    if (params?.minScore) searchParams.set('min_score', params.minScore.toString())
    if (params?.search) searchParams.set('search', params.search)
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.offset) searchParams.set('offset', params.offset.toString())

    const query = searchParams.toString()
    return apiRequest(`/api/employers/talent-pool${query ? `?${query}` : ''}`)
  },

  // Get detailed talent profile with video URLs and scoring dimensions
  getProfile: (profileId: string): Promise<TalentProfileDetail> =>
    apiRequest(`/api/employers/talent-pool/${profileId}`),

  // Update candidate status (pipeline tracking)
  updateStatus: (
    profileId: string,
    status: MatchStatus,
    jobId?: string
  ): Promise<{ success: boolean; matchId: string; status: MatchStatus }> =>
    apiRequest(`/api/employers/talent-pool/${profileId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({
        status,
        job_id: jobId,
      }),
    }),

  // Contact candidate from talent pool (sends email notification)
  contactCandidate: (
    profileId: string,
    data: {
      subject: string
      body: string
      messageType?: 'interview_invite' | 'general' | 'job_offer'
      jobId?: string
    }
  ): Promise<{
    success: boolean
    messageId: string
    candidateEmail: string
    statusUpdated: boolean
  }> =>
    apiRequest(`/api/employers/talent-pool/${profileId}/contact`, {
      method: 'POST',
      body: JSON.stringify({
        subject: data.subject,
        body: data.body,
        message_type: data.messageType || 'general',
        job_id: data.jobId,
      }),
    }),
}

// ==================== AUTH / VERIFICATION API ====================

export const authApi = {
  // Verify email with token
  verifyEmail: (token: string, userType: 'candidate' | 'employer'): Promise<{
    success: boolean
    message: string
    user_type: string
    email: string
  }> =>
    apiRequest('/api/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({
        token,
        user_type: userType,
      }),
    }),

  // Resend verification email
  resendVerification: (email: string, userType: 'candidate' | 'employer'): Promise<{
    success: boolean
    message: string
  }> =>
    apiRequest('/api/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({
        email,
        user_type: userType,
      }),
    }),

  // Check verification status
  checkVerificationStatus: (email: string, userType: 'candidate' | 'employer'): Promise<{
    verified: boolean
  }> =>
    apiRequest(`/api/auth/verification-status?email=${encodeURIComponent(email)}&user_type=${userType}`),
}
