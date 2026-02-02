/**
 * API client for Pathway backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
export interface GitHubData {
  username: string
  avatarUrl?: string
  profileUrl: string
  publicRepos: number
  followers: number
  following: number
  repos: Array<{
    name: string
    fullName?: string
    description?: string
    language?: string
    stars: number
    forks: number
    url: string
    updatedAt: string
    isFork?: boolean
    owner?: string
    isOwner?: boolean  // true if user owns it, false if collaborator
  }>
  languages: Record<string, number>
  totalContributions?: number
}

export interface GitHubAnalysis {
  overallScore: number
  originalityScore: number
  activityScore: number
  depthScore: number
  collaborationScore: number
  totalReposAnalyzed: number
  totalCommits: number
  totalLinesAdded: number
  personalProjects: number
  classProjects: number
  aiAssistedRepos: number
  organicCodeRatio: number
  hasTests: boolean
  hasCiCd: boolean
  primaryLanguages: Array<{
    language: string
    bytes: number
    percentage: number
    proficiency: string
  }>
  flags: Array<{
    type: string
    repo?: string
    detail: string
  }>
  requiresReview: boolean
  analyzedAt?: string
}

export interface SharingPreferences {
  companyStages: string[]  // ["seed", "series_a", "series_b", "series_c_plus"]
  locations: string[]  // ["remote", "sf", "nyc", "seattle", "austin", etc.]
  industries: string[]  // ["fintech", "climate", "ai", "healthcare", etc.]
  emailDigest: boolean
}

export interface SharingPreferencesResponse {
  optedInToSharing: boolean
  preferences?: SharingPreferences
}

export interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  targetRoles: string[]
  // Education fields
  university?: string
  major?: string
  graduationYear?: number
  gpa?: number
  courses?: string[]
  // GitHub integration
  githubUsername?: string
  githubData?: GitHubData
  githubConnectedAt?: string
  // Resume
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
    gpa?: string
  }>
  projects: Array<{
    name: string
    description?: string
    technologies?: string[]
    highlights?: string[]
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

// Career verticals based on 2026 new grad job market
export type Vertical = 'software_engineering' | 'data' | 'product' | 'design' | 'finance'

// Entry-level role types
export type RoleType =
  // Software Engineering (most common new grad roles)
  | 'software_engineer'
  | 'embedded_engineer'
  | 'qa_engineer'
  // Data
  | 'data_analyst'
  | 'data_scientist'
  | 'ml_engineer'
  | 'data_engineer'
  // Product
  | 'product_manager'
  | 'associate_pm'
  // Design
  | 'ux_designer'
  | 'ui_designer'
  | 'product_designer'
  // Finance
  | 'ib_analyst'
  | 'finance_analyst'
  | 'equity_research'

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
  communication: number     // Clarity, articulation, confidence
  problemSolving: number    // Analytical thinking, approach to challenges
  domainKnowledge: number   // Relevant skills, depth of understanding
  growthMindset: number     // Learning from failures, curiosity, adaptability
  cultureFit: number        // Teamwork, values alignment, enthusiasm
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

// Helper to transform snake_case to camelCase for parsed resume data
function transformParsedResume(data: unknown): ParsedResumeData | undefined {
  if (!data || typeof data !== 'object') return undefined
  const d = data as Record<string, unknown>

  return {
    name: d.name as string | undefined,
    email: d.email as string | undefined,
    phone: d.phone as string | undefined,
    location: d.location as string | undefined,
    summary: d.summary as string | undefined,
    skills: (d.skills as string[]) || [],
    experience: ((d.experience as Array<Record<string, unknown>>) || []).map(exp => ({
      company: exp.company as string,
      title: exp.title as string,
      startDate: (exp.start_date || exp.startDate) as string | undefined,
      endDate: (exp.end_date || exp.endDate) as string | undefined,
      description: exp.description as string | undefined,
      highlights: (exp.highlights as string[]) || [],
    })),
    education: ((d.education as Array<Record<string, unknown>>) || []).map(edu => ({
      institution: edu.institution as string,
      degree: edu.degree as string | undefined,
      fieldOfStudy: (edu.field_of_study || edu.fieldOfStudy) as string | undefined,
      startDate: (edu.start_date || edu.startDate) as string | undefined,
      endDate: (edu.end_date || edu.endDate) as string | undefined,
      gpa: edu.gpa as string | undefined,
    })),
    projects: ((d.projects as Array<Record<string, unknown>>) || []).map(proj => ({
      name: proj.name as string,
      description: proj.description as string | undefined,
      technologies: (proj.technologies as string[]) || [],
      highlights: (proj.highlights as string[]) || [],
    })),
    languages: (d.languages as string[]) || [],
    certifications: (d.certifications as string[]) || [],
  }
}

// Helper to transform talent profile response from snake_case to camelCase
function transformTalentProfileResponse(data: Record<string, unknown>): TalentProfileDetail {
  const profile = data.profile as Record<string, unknown> | undefined
  const candidate = data.candidate as Record<string, unknown>
  const interview = data.interview as Record<string, unknown> | undefined
  const employerStatus = data.employer_status as Record<string, unknown> | undefined
  const completionStatus = data.completion_status as Record<string, unknown> | undefined
  const profileScoreData = data.profile_score as Record<string, unknown> | undefined

  return {
    profile: profile ? {
      id: profile.id as string | undefined,
      vertical: profile.vertical as string | undefined,
      roleType: (profile.role_type || profile.roleType) as string | undefined,
      interviewScore: profile.interview_score as number | undefined,
      bestScore: (profile.best_score || profile.bestScore) as number | undefined,
      totalInterviews: (profile.total_interviews || profile.totalInterviews || profile.attempt_count || 0) as number,
      completedAt: (profile.completed_at || profile.completedAt) as string | undefined,
      status: profile.status as string | undefined,
    } : {
      status: 'no_profile',
    },
    candidate: {
      id: candidate.id as string,
      name: candidate.name as string,
      email: candidate.email as string,
      phone: candidate.phone as string | undefined,
      university: candidate.university as string | undefined,
      major: candidate.major as string | undefined,
      graduationYear: (candidate.graduation_year || candidate.graduationYear) as number | undefined,
      gpa: candidate.gpa as number | undefined,
      resumeUrl: (candidate.resume_url || candidate.resumeUrl) as string | undefined,
      resumeData: transformParsedResume(candidate.resume_data || candidate.resumeData),
      githubUsername: (candidate.github_username || candidate.githubUsername) as string | undefined,
      githubData: (candidate.github_data || candidate.githubData) as GitHubData | undefined,
    },
    completionStatus: completionStatus ? {
      resumeUploaded: (completionStatus.resume_uploaded || completionStatus.resumeUploaded || false) as boolean,
      githubConnected: (completionStatus.github_connected || completionStatus.githubConnected || false) as boolean,
      interviewCompleted: (completionStatus.interview_completed || completionStatus.interviewCompleted || false) as boolean,
      educationFilled: (completionStatus.education_filled || completionStatus.educationFilled || false) as boolean,
    } : undefined,
    profileScore: profileScoreData ? {
      score: profileScoreData.score as number,
      breakdown: {
        technicalSkills: (profileScoreData.breakdown as Record<string, number> | undefined)?.technical_skills,
        experienceQuality: (profileScoreData.breakdown as Record<string, number> | undefined)?.experience_quality,
        education: (profileScoreData.breakdown as Record<string, number> | undefined)?.education,
        githubActivity: (profileScoreData.breakdown as Record<string, number> | undefined)?.github_activity,
      },
    } : undefined,
    interview: interview ? {
      sessionId: (interview.session_id || interview.sessionId) as string,
      totalScore: (interview.total_score || interview.totalScore) as number | undefined,
      aiSummary: (interview.ai_summary || interview.aiSummary) as string | undefined,
      completedAt: (interview.completed_at || interview.completedAt) as string | undefined,
      responses: ((interview.responses as Array<Record<string, unknown>>) || []).map(resp => ({
        id: resp.id as string,
        questionIndex: (resp.question_index || resp.questionIndex) as number,
        questionText: (resp.question_text || resp.questionText) as string,
        videoUrl: (resp.video_url || resp.videoUrl) as string | undefined,
        transcription: resp.transcription as string | undefined,
        durationSeconds: (resp.duration_seconds || resp.durationSeconds) as number | undefined,
        aiScore: (resp.ai_score || resp.aiScore) as number | undefined,
        aiAnalysis: (resp.ai_analysis || resp.aiAnalysis) as string | undefined,
        scoringDimensions: resp.scoring_dimensions as Record<string, number> | undefined,
        isFollowup: (resp.is_followup || resp.isFollowup || false) as boolean,
        questionType: (resp.question_type || resp.questionType || 'behavioral') as string,
        createdAt: (resp.created_at || resp.createdAt || new Date().toISOString()) as string,
      })),
    } : undefined,
    employerStatus: employerStatus ? {
      status: employerStatus.status as MatchStatus,
      matchId: (employerStatus.match_id || employerStatus.matchId) as string | undefined,
      jobId: (employerStatus.job_id || employerStatus.jobId) as string | undefined,
      jobTitle: (employerStatus.job_title || employerStatus.jobTitle) as string | undefined,
      notes: employerStatus.notes as string | undefined,
    } : undefined,
  }
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
      parsedData: transformParsedResume(data.parsed_data),
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
      parsedData: transformParsedResume(data.parsed_data),
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

  // Transcript upload
  uploadTranscript: async (
    candidateId: string,
    file: File,
    token?: string
  ): Promise<{
    success: boolean
    message: string
    parsedData: ParsedResumeData | null
  }> => {
    const formData = new FormData()
    formData.append('file', file)

    const url = `${API_BASE_URL}/api/candidates/${candidateId}/transcript`
    const headers: Record<string, string> = {}

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
      throw new ApiError(response.status, error.detail || 'Failed to upload transcript')
    }

    const data = await response.json()
    return {
      success: data.success,
      message: data.message,
      parsedData: data.parsed_data,
    }
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

  // GitHub OAuth
  getGitHubAuthUrl: async (state?: string): Promise<{ authUrl: string; state: string }> => {
    const params = state ? `?state=${encodeURIComponent(state)}` : ''
    const response = await apiRequest<{ auth_url: string; state: string }>(`/api/candidates/auth/github/url${params}`)
    return {
      authUrl: response.auth_url,
      state: response.state,
    }
  },

  connectGitHub: async (code: string, state?: string): Promise<{
    success: boolean
    message: string
    githubUsername: string
    githubData: GitHubData
  }> => {
    // IMPORTANT: Explicitly use candidate token for this endpoint
    const candidateToken = typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null
    if (!candidateToken) {
      throw new ApiError(401, 'You must be logged in as a student to connect GitHub')
    }

    const url = `${API_BASE_URL}/api/candidates/auth/github/callback`
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${candidateToken}`,
      },
      body: JSON.stringify({ code, state }),
    })

    if (!res.ok) {
      let message = 'Failed to connect GitHub'
      try {
        const error = await res.json()
        message = error.detail || error.message || message
      } catch {
        // ignore JSON parse errors
      }
      throw new ApiError(res.status, message)
    }

    const response = await res.json() as {
      success: boolean
      message: string
      github_username: string
      github_data: {
        username: string
        connected_at?: string
        top_repos?: Array<{
          name: string
          full_name?: string
          description?: string
          language?: string
          stars: number
          forks?: number
          url: string
          updated_at?: string
          is_fork?: boolean
          owner?: string
          is_owner?: boolean
        }>
        total_repos?: number
        total_contributions?: number
        languages?: Record<string, number>
      }
    }

    // Map backend response (top_repos) to frontend format (repos)
    const topRepos = response.github_data?.top_repos || []

    return {
      success: response.success,
      message: response.message,
      githubUsername: response.github_username,
      githubData: {
        username: response.github_data.username,
        avatarUrl: undefined,
        profileUrl: `https://github.com/${response.github_data.username}`,
        publicRepos: response.github_data.total_repos || 0,
        followers: 0,
        following: 0,
        repos: topRepos.map(r => ({
          name: r.name,
          fullName: r.full_name,
          description: r.description,
          language: r.language,
          stars: r.stars || 0,
          forks: r.forks || 0,
          url: r.url,
          updatedAt: r.updated_at || '',
          isFork: r.is_fork,
          owner: r.owner,
          isOwner: r.is_owner,
        })),
        languages: response.github_data.languages || {},
        totalContributions: response.github_data.total_contributions,
      },
    }
  },

  disconnectGitHub: (): Promise<{ success: boolean; message: string }> =>
    apiRequest('/api/candidates/me/github', { method: 'DELETE' }),

  getGitHubInfo: async (token?: string): Promise<GitHubData | null> => {
    try {
      const url = `${API_BASE_URL}/api/candidates/me/github`
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }

      const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`
      }

      const res = await fetch(url, { headers })

      // GitHub not connected returns 404, which is expected
      if (res.status === 404) {
        return null
      }

      if (!res.ok) {
        return null
      }

      const response = await res.json()

      if (!response.username) {
        return null
      }

      return {
        username: response.username,
        avatarUrl: response.avatar_url,
        profileUrl: response.profile_url || `https://github.com/${response.username}`,
        publicRepos: response.public_repos || response.total_repos || 0,
        followers: response.followers || 0,
        following: response.following || 0,
        repos: (response.repos || response.top_repos || []).map((r: { name: string; full_name?: string; description?: string; language?: string; stars?: number; forks?: number; url?: string; updated_at?: string; is_fork?: boolean; owner?: string; is_owner?: boolean }) => ({
          name: r.name,
          fullName: r.full_name,
          description: r.description,
          language: r.language,
          stars: r.stars || 0,
          forks: r.forks || 0,
          url: r.url || '',
          updatedAt: r.updated_at || '',
          isFork: r.is_fork || false,
          owner: r.owner,
          isOwner: r.is_owner !== false,  // default to true if not specified
        })),
        languages: response.languages || {},
        totalContributions: response.total_contributions,
      }
    } catch {
      return null
    }
  },

  refreshGitHubData: async (): Promise<GitHubData> => {
    const response = await apiRequest<{
      success: boolean
      message: string
      github_data: {
        username: string
        connected_at?: string
        top_repos?: Array<{
          name: string
          full_name?: string
          description?: string
          language?: string
          stars?: number
          forks?: number
          url: string
          updated_at?: string
          is_fork?: boolean
          owner?: string
          is_owner?: boolean
        }>
        total_repos?: number
        total_contributions?: number
        languages?: Record<string, number>
      }
    }>('/api/candidates/me/github/refresh', { method: 'POST' })

    // Map backend response (top_repos) to frontend format (repos)
    const topRepos = response.github_data?.top_repos || []

    return {
      username: response.github_data.username,
      avatarUrl: undefined,
      profileUrl: `https://github.com/${response.github_data.username}`,
      publicRepos: response.github_data.total_repos || 0,
      followers: 0,
      following: 0,
      repos: topRepos.map(r => ({
        name: r.name,
        fullName: r.full_name,
        description: r.description,
        language: r.language,
        stars: r.stars || 0,
        forks: r.forks || 0,
        url: r.url,
        updatedAt: r.updated_at || '',
        isFork: r.is_fork || false,
        owner: r.owner,
        isOwner: r.is_owner !== false,
      })),
      languages: response.github_data.languages || {},
      totalContributions: response.github_data.total_contributions,
    }
  },

  // Update education info
  updateEducation: (data: {
    university?: string
    major?: string
    graduationYear?: number
    gpa?: number
    courses?: string[]
  }): Promise<Candidate> =>
    apiRequest('/api/candidates/me', {
      method: 'PATCH',
      body: JSON.stringify({
        university: data.university,
        major: data.major,
        graduation_year: data.graduationYear,
        gpa: data.gpa,
        courses: data.courses,
      }),
    }),

  // GitHub Analysis
  analyzeGitHub: async (): Promise<GitHubAnalysis> => {
    const response = await apiRequest<{
      overall_score: number
      originality_score: number
      activity_score: number
      depth_score: number
      collaboration_score: number
      total_repos_analyzed: number
      total_commits: number
      total_lines_added: number
      personal_projects: number
      class_projects: number
      ai_assisted_repos: number
      organic_code_ratio: number
      has_tests: boolean
      has_ci_cd: boolean
      primary_languages: Array<{
        language: string
        bytes: number
        percentage: number
        proficiency: string
      }>
      flags: Array<{
        type: string
        repo?: string
        detail: string
      }>
      requires_review: boolean
      analyzed_at?: string
    }>('/api/candidates/me/github/analyze', { method: 'POST' })

    return {
      overallScore: response.overall_score,
      originalityScore: response.originality_score,
      activityScore: response.activity_score,
      depthScore: response.depth_score,
      collaborationScore: response.collaboration_score,
      totalReposAnalyzed: response.total_repos_analyzed,
      totalCommits: response.total_commits,
      totalLinesAdded: response.total_lines_added,
      personalProjects: response.personal_projects,
      classProjects: response.class_projects,
      aiAssistedRepos: response.ai_assisted_repos,
      organicCodeRatio: response.organic_code_ratio,
      hasTests: response.has_tests,
      hasCiCd: response.has_ci_cd,
      primaryLanguages: response.primary_languages,
      flags: response.flags,
      requiresReview: response.requires_review,
      analyzedAt: response.analyzed_at,
    }
  },

  getGitHubAnalysis: async (token?: string): Promise<GitHubAnalysis | null> => {
    try {
      const url = `${API_BASE_URL}/api/candidates/me/github/analysis`
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }

      const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`
      }

      const res = await fetch(url, { headers })

      // No analysis yet returns 404 or null, which is expected
      if (!res.ok) {
        return null
      }

      const response = await res.json()

      if (!response) return null

      return {
        overallScore: response.overall_score,
        originalityScore: response.originality_score,
        activityScore: response.activity_score,
        depthScore: response.depth_score,
        collaborationScore: response.collaboration_score,
        totalReposAnalyzed: response.total_repos_analyzed,
        totalCommits: response.total_commits,
        totalLinesAdded: response.total_lines_added,
        personalProjects: response.personal_projects,
        classProjects: response.class_projects,
        aiAssistedRepos: response.ai_assisted_repos,
        organicCodeRatio: response.organic_code_ratio,
        hasTests: response.has_tests,
        hasCiCd: response.has_ci_cd,
        primaryLanguages: response.primary_languages,
        flags: response.flags,
        requiresReview: response.requires_review,
        analyzedAt: response.analyzed_at,
      }
    } catch {
      return null
    }
  },

  // Sharing preferences (GTM)
  getSharingPreferences: async (token?: string): Promise<SharingPreferencesResponse> => {
    const url = `${API_BASE_URL}/api/candidates/me/sharing-preferences`
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
      throw new ApiError(response.status, error.detail || 'Failed to get sharing preferences')
    }

    const data = await response.json()
    return {
      optedInToSharing: data.opted_in_to_sharing,
      preferences: data.preferences ? {
        companyStages: data.preferences.company_stages || [],
        locations: data.preferences.locations || [],
        industries: data.preferences.industries || [],
        emailDigest: data.preferences.email_digest ?? true,
      } : undefined,
    }
  },

  updateSharingPreferences: async (
    preferences: {
      optedInToSharing?: boolean
      companyStages?: string[]
      locations?: string[]
      industries?: string[]
      emailDigest?: boolean
    },
    token?: string
  ): Promise<SharingPreferencesResponse> => {
    const url = `${API_BASE_URL}/api/candidates/me/sharing-preferences`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const body: Record<string, any> = {}
    if (preferences.optedInToSharing !== undefined) {
      body.opted_in_to_sharing = preferences.optedInToSharing
    }
    if (preferences.companyStages !== undefined) {
      body.company_stages = preferences.companyStages
    }
    if (preferences.locations !== undefined) {
      body.locations = preferences.locations
    }
    if (preferences.industries !== undefined) {
      body.industries = preferences.industries
    }
    if (preferences.emailDigest !== undefined) {
      body.email_digest = preferences.emailDigest
    }

    const response = await fetch(url, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to update sharing preferences')
    }

    const data = await response.json()
    return {
      optedInToSharing: data.opted_in_to_sharing,
      preferences: data.preferences ? {
        companyStages: data.preferences.company_stages || [],
        locations: data.preferences.locations || [],
        industries: data.preferences.industries || [],
        emailDigest: data.preferences.email_digest ?? true,
      } : undefined,
    }
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

    // Get auth token from localStorage
    const headers: Record<string, string> = {}
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('candidate_token')
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
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

    // Get auth token from localStorage
    const headers: Record<string, string> = {}
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('candidate_token')
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
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

  // Profile sharing (GTM)
  generateProfileLink: async (candidateId: string): Promise<{
    success: boolean
    token: string
    candidateId: string
    expiresAt: string
    shareUrl: string
  }> => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('employer_token') : null
    const url = `${API_BASE_URL}/api/employers/talent-pool/${candidateId}/generate-link`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to generate profile link')
    }

    const data = await response.json()
    return {
      success: data.success,
      token: data.token,
      candidateId: data.candidate_id,
      expiresAt: data.expires_at,
      shareUrl: data.share_url,
    }
  },

  getProfileLinks: async (candidateId: string): Promise<{
    candidateId: string
    candidateName: string
    links: Array<{
      id: string
      token: string
      shareUrl: string
      expiresAt: string
      isExpired: boolean
      viewCount: number
      lastViewedAt: string | null
      createdAt: string
    }>
  }> => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('employer_token') : null
    const url = `${API_BASE_URL}/api/employers/talent-pool/${candidateId}/profile-links`

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to get profile links')
    }

    const data = await response.json()
    return {
      candidateId: data.candidate_id,
      candidateName: data.candidate_name,
      links: data.links,
    }
  },
}

// Public API (no auth required)
export const publicApi = {
  getCandidateProfile: async (candidateId: string, token: string): Promise<{
    id: string
    name: string
    university?: string
    major?: string
    majors?: string[]
    minors?: string[]
    graduationYear?: number
    gpa?: number
    githubUsername?: string
    githubData?: any
    bio?: string
    linkedinUrl?: string
    portfolioUrl?: string
    targetRoles: string[]
    bestScores?: Record<string, number>
    interviewHistory?: Array<{
      month: number
      year: number
      vertical: string
      roleType?: string
      overallScore: number
      communicationScore?: number
      problemSolvingScore?: number
      technicalScore?: number
      growthMindsetScore?: number
      cultureFitScore?: number
      completedAt?: string
    }>
    resumeUrl?: string
  }> => {
    const url = `${API_BASE_URL}/api/public/talent/${candidateId}?token=${token}`

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to load candidate profile')
    }

    const data = await response.json()
    return {
      id: data.id,
      name: data.name,
      university: data.university,
      major: data.major,
      majors: data.majors,
      minors: data.minors,
      graduationYear: data.graduation_year,
      gpa: data.gpa,
      githubUsername: data.github_username,
      githubData: data.github_data,
      bio: data.bio,
      linkedinUrl: data.linkedin_url,
      portfolioUrl: data.portfolio_url,
      targetRoles: data.target_roles || [],
      bestScores: data.best_scores,
      interviewHistory: data.interview_history,
      resumeUrl: data.resume_url,
    }
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
  interviewSessionId?: string  // Current/last interview session ID
  interviewScore?: number
  bestScore?: number
  totalInterviews: number
  lastInterviewAt?: string
  nextEligibleAt?: string
  completedAt?: string
  canInterview: boolean  // True if 30+ days since last interview
}

export type MatchStatus = 'PENDING' | 'CONTACTED' | 'IN_REVIEW' | 'SHORTLISTED' | 'REJECTED' | 'HIRED'

export interface CompletionStatus {
  resumeUploaded: boolean
  githubConnected: boolean
  interviewCompleted: boolean
  educationFilled: boolean
}

export interface ScoreBreakdown {
  // Interview-based scores
  communication?: number
  problemSolving?: number
  domainKnowledge?: number
  motivation?: number
  cultureFit?: number
  // Profile-based scores (when no interview)
  technicalSkills?: number
  experienceQuality?: number
  education?: number
  githubActivity?: number
}

export interface TalentPoolCandidate {
  profileId?: string  // May be null for candidates without vertical profile
  candidateId: string
  candidateName: string
  candidateEmail: string
  vertical?: string  // May be null for candidates without vertical profile
  roleType?: string
  interviewScore?: number
  bestScore?: number
  profileScore?: number  // Score based on resume/GitHub (pre-interview)
  status: string  // completed, in_progress, pending, or profile_only
  completedAt?: string
  skills: string[]
  experienceSummary?: string
  location?: string
  university?: string
  major?: string
  graduationYear?: number
  // Completion indicators
  completionStatus?: CompletionStatus
  // Score breakdown
  scoreBreakdown?: ScoreBreakdown
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
    growthMindset?: number
    cultureFit?: number
  }
}

export interface TalentProfileDetail {
  profile: {
    id?: string
    vertical?: string
    roleType?: string
    interviewScore?: number
    bestScore?: number
    totalInterviews?: number
    completedAt?: string
    status?: string  // completed, in_progress, pending, no_profile
  }
  candidate: {
    id: string
    name: string
    email: string
    phone?: string
    university?: string
    major?: string
    graduationYear?: number
    gpa?: number
    resumeUrl?: string
    resumeData?: ParsedResumeData
    githubUsername?: string
    githubData?: GitHubData
  }
  completionStatus?: CompletionStatus
  profileScore?: {
    score: number
    breakdown: {
      technicalSkills?: number
      experienceQuality?: number
      education?: number
      githubActivity?: number
    }
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
    jobId?: string
    jobTitle?: string
    status: MatchStatus
    updatedAt?: string
    notes?: string
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
        interviewSessionId: p.interview_session_id,
        interviewScore: p.interview_score,
        bestScore: p.best_score,
        totalInterviews: p.total_interviews || 0,
        lastInterviewAt: p.last_interview_at,
        nextEligibleAt: p.next_eligible_at,
        completedAt: p.completed_at,
        canInterview: p.can_interview ?? true,
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

// Helper to transform talent pool candidate from snake_case to camelCase
function transformTalentPoolCandidate(c: Record<string, unknown>): TalentPoolCandidate {
  const completionStatus = c.completion_status as Record<string, unknown> | undefined
  const scoreBreakdown = c.score_breakdown as Record<string, unknown> | undefined

  return {
    profileId: (c.profile_id || c.profileId) as string | undefined,
    candidateId: (c.candidate_id || c.candidateId) as string,
    candidateName: (c.candidate_name || c.candidateName) as string,
    candidateEmail: (c.candidate_email || c.candidateEmail) as string,
    vertical: c.vertical as string | undefined,
    roleType: (c.role_type || c.roleType) as string | undefined,
    interviewScore: (c.interview_score || c.interviewScore) as number | undefined,
    bestScore: (c.best_score || c.bestScore) as number | undefined,
    profileScore: (c.profile_score || c.profileScore) as number | undefined,
    status: c.status as string,
    completedAt: (c.completed_at || c.completedAt) as string | undefined,
    skills: (c.skills || []) as string[],
    experienceSummary: (c.experience_summary || c.experienceSummary) as string | undefined,
    location: c.location as string | undefined,
    university: c.university as string | undefined,
    major: c.major as string | undefined,
    graduationYear: (c.graduation_year || c.graduationYear) as number | undefined,
    completionStatus: completionStatus ? {
      resumeUploaded: (completionStatus.resume_uploaded || completionStatus.resumeUploaded || false) as boolean,
      githubConnected: (completionStatus.github_connected || completionStatus.githubConnected || false) as boolean,
      interviewCompleted: (completionStatus.interview_completed || completionStatus.interviewCompleted || false) as boolean,
      educationFilled: (completionStatus.education_filled || completionStatus.educationFilled || false) as boolean,
    } : undefined,
    scoreBreakdown: scoreBreakdown ? {
      communication: scoreBreakdown.communication as number | undefined,
      problemSolving: (scoreBreakdown.problem_solving || scoreBreakdown.problemSolving) as number | undefined,
      domainKnowledge: (scoreBreakdown.domain_knowledge || scoreBreakdown.domainKnowledge) as number | undefined,
      motivation: scoreBreakdown.motivation as number | undefined,
      cultureFit: (scoreBreakdown.culture_fit || scoreBreakdown.cultureFit) as number | undefined,
      technicalSkills: (scoreBreakdown.technical_skills || scoreBreakdown.technicalSkills) as number | undefined,
      experienceQuality: (scoreBreakdown.experience_quality || scoreBreakdown.experienceQuality) as number | undefined,
      education: scoreBreakdown.education as number | undefined,
      githubActivity: (scoreBreakdown.github_activity || scoreBreakdown.githubActivity) as number | undefined,
    } : undefined,
  }
}

// Add employer API methods for talent pool
export const talentPoolApi = {
  // Browse talent pool with search
  // Now includes candidates with profile data even before completing interviews
  browse: async (params?: {
    vertical?: Vertical
    roleType?: RoleType
    minScore?: number
    search?: string  // Full-text search on name, skills, resume
    includeIncomplete?: boolean  // Include candidates with profile data but no completed interview (default: true)
    limit?: number
    offset?: number
  }): Promise<{ candidates: TalentPoolCandidate[]; total: number }> => {
    const searchParams = new URLSearchParams()
    if (params?.vertical) searchParams.set('vertical', params.vertical)
    if (params?.roleType) searchParams.set('role_type', params.roleType)
    if (params?.minScore) searchParams.set('min_score', params.minScore.toString())
    if (params?.search) searchParams.set('search', params.search)
    if (params?.includeIncomplete !== undefined) searchParams.set('include_incomplete', params.includeIncomplete.toString())
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.offset) searchParams.set('offset', params.offset.toString())

    const query = searchParams.toString()
    const data = await apiRequest<{ candidates: Record<string, unknown>[]; total: number }>(`/api/employers/talent-pool${query ? `?${query}` : ''}`)

    return {
      candidates: data.candidates.map(transformTalentPoolCandidate),
      total: data.total,
    }
  },

  // Get detailed talent profile with video URLs and scoring dimensions
  // Works for both profile_id and candidate_id
  getProfile: async (profileOrCandidateId: string): Promise<TalentProfileDetail> => {
    const data = await apiRequest<Record<string, unknown>>(`/api/employers/talent-pool/${profileOrCandidateId}`)
    return transformTalentProfileResponse(data)
  },

  // Get candidate details by candidate ID (works for all candidates)
  getCandidateDetail: async (candidateId: string): Promise<TalentProfileDetail> => {
    const data = await apiRequest<Record<string, unknown>>(`/api/employers/talent-pool/candidate/${candidateId}`)
    return transformTalentProfileResponse(data)
  },

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
