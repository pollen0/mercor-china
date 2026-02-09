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

export interface Activity {
  id: string
  activityName: string
  organization?: string
  role?: string
  description?: string
  startDate?: string
  endDate?: string
}

export interface Award {
  id: string
  name: string
  issuer?: string
  date?: string
  description?: string
}

export interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  targetRoles: string[]
  // Email verification
  emailVerified?: boolean
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
  activities?: Array<{
    name: string
    organization?: string
    role?: string
    description?: string
    startDate?: string
    endDate?: string
  }>
  awards?: Array<{
    name: string
    issuer?: string
    date?: string
    description?: string
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
  name?: string  // Employer's personal name
  companyName: string
  email: string
  logo?: string
  industry?: string
  companySize?: string
  isVerified: boolean
  createdAt: string
  googleCalendarConnectedAt?: string
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
  questions: QuestionInfo[]
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

export interface MatchAlertCandidate {
  id: string
  name: string
  email: string
  university?: string
  major?: string
  graduationYear?: number
}

export interface MatchAlert {
  id: string
  candidate: MatchAlertCandidate
  jobId?: string
  jobTitle?: string
  matchScore: number
  interviewScore?: number
  skillsMatchScore?: number
  status: string
  createdAt: string
  isNew: boolean
}

export interface MatchAlertList {
  alerts: MatchAlert[]
  total: number
  unreadCount: number
}

// Skill Gap Analysis Types
export interface SkillMatch {
  requirement: string
  requirementCategory: string
  matched: boolean
  candidateSkill?: string
  matchType: 'exact' | 'synonym' | 'related' | 'partial' | 'none'
  proficiencyLevel: 'expert' | 'advanced' | 'intermediate' | 'beginner' | 'none'
  proficiencyScore: number
  evidence: string[]
  yearsExperience?: number
}

export interface LearningPriority {
  skill: string
  priority: 'critical' | 'recommended' | 'optional'
  reason: string
  estimatedEffort: string
}

export interface SkillGapAnalysis {
  overallMatchScore: number
  totalRequirements: number
  matchedRequirements: number
  criticalGaps: string[]
  skillMatches: SkillMatch[]
  categoryCoverage: Record<string, {
    matched: number
    total: number
    coverageScore: number
    avgProficiency: number
    importance: string
    description: string
  }>
  proficiencyDistribution: Record<string, number>
  avgProficiencyScore: number
  learningPriorities: LearningPriority[]
  alternativeSkills: Array<{
    missingRequirement: string
    alternativeSkill: string
    transferability: string
    note: string
  }>
  transferableSkills: string[]
  bonusSkills: string[]
  strongestAreas: string[]
}

// Enhanced Matching Types
export interface EnhancedMatchResult {
  overallMatchScore: number
  interviewScore: number
  skillsMatchScore: number
  experienceMatchScore: number
  githubSignalScore: number
  educationScore: number
  growthTrajectoryScore: number
  locationMatch: boolean
  factors: Record<string, unknown>
  skillGapSummary: {
    matchPercentage: number
    matchedCount: number
    missingCount: number
    missingSkills: string[]
    semanticMatches: number
    hasCriticalGaps: boolean
  }
  topStrengths: string[]
  areasForGrowth: string[]
  hiringRecommendation: string
  confidenceScore: number
  aiReasoning: string
}

export interface RankedCandidate {
  candidateId: string
  name: string
  email: string
  university?: string
  graduationYear?: number
  overallMatchScore: number
  interviewScore?: number
  skillsMatchScore?: number
  githubSignalScore?: number
  topStrengths: string[]
  skillGaps: string[]
  hiringRecommendation: string
}

export interface CandidateRankingResponse {
  jobId: string
  jobTitle: string
  candidates: RankedCandidate[]
  total: number
  averageMatchScore: number
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
export function transformParsedResume(data: unknown): ParsedResumeData | undefined {
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
    activities: ((d.activities as Array<Record<string, unknown>>) || []).map(act => ({
      name: act.name as string,
      organization: act.organization as string | undefined,
      role: act.role as string | undefined,
      description: act.description as string | undefined,
      startDate: (act.start_date || act.startDate) as string | undefined,
      endDate: (act.end_date || act.endDate) as string | undefined,
    })),
    awards: ((d.awards as Array<Record<string, unknown>>) || []).map(awd => ({
      name: awd.name as string,
      issuer: awd.issuer as string | undefined,
      date: awd.date as string | undefined,
      description: awd.description as string | undefined,
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
      transcriptUploaded: (completionStatus.transcript_uploaded || completionStatus.transcriptUploaded || false) as boolean,
    } : undefined,
    profileScore: profileScoreData ? {
      score: profileScoreData.score as number,
      breakdown: {
        technicalSkills: (profileScoreData.breakdown as Record<string, number> | undefined)?.technical_skills,
        experienceQuality: (profileScoreData.breakdown as Record<string, number> | undefined)?.experience_quality,
        education: (profileScoreData.breakdown as Record<string, number> | undefined)?.education,
        githubActivity: (profileScoreData.breakdown as Record<string, number> | undefined)?.github_activity,
      },
      strengths: (profileScoreData.strengths as string[]) || [],
      concerns: (profileScoreData.concerns as string[]) || [],
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
      overallStrengths: (interview.overall_strengths || interview.overallStrengths || []) as string[],
      overallConcerns: (interview.overall_concerns || interview.overallConcerns || []) as string[],
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
  options: RequestInit = {},
  _retried = false,
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  }

  // Add auth token if available - choose the right token based on endpoint
  let tokenType: 'candidate' | 'employer' = 'candidate'
  if (typeof window !== 'undefined') {
    const employerToken = localStorage.getItem('employer_token')
    const candidateToken = localStorage.getItem('candidate_token')

    // Use employer token for employer endpoints, candidate token for everything else
    let token: string | null = null
    if (endpoint.startsWith('/api/employers')) {
      token = employerToken || candidateToken
      tokenType = 'employer'
    } else {
      token = candidateToken || employerToken
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  // Auto-refresh token on 401 (expired) — try once
  if (response.status === 401 && !_retried && typeof window !== 'undefined') {
    const { refreshAccessToken } = await import('./auth')
    const newToken = await refreshAccessToken(tokenType)
    if (newToken) {
      return apiRequest<T>(endpoint, options, true)
    }
  }

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

  getMe: async (token?: string): Promise<Candidate> => {
    const url = `${API_BASE_URL}/api/candidates/me`
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
      throw new ApiError(response.status, error.detail || 'Failed to fetch profile')
    }

    const data = await response.json()
    return {
      id: data.id,
      name: data.name,
      email: data.email,
      phone: data.phone || '',
      targetRoles: data.target_roles || [],
      emailVerified: data.email_verified,
      university: data.university,
      major: data.major,
      graduationYear: data.graduation_year,
      gpa: data.gpa,
      githubUsername: data.github_username,
      resumeUrl: data.resume_url,
      createdAt: data.created_at,
    }
  },

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

  getResume: async (candidateId: string): Promise<ResumeResponse> => {
    const data = await apiRequest<Record<string, unknown>>(`/api/candidates/${candidateId}/resume`)
    return {
      candidateId: data.candidate_id as string,
      resumeUrl: data.resume_url as string | undefined,
      rawText: data.raw_text as string | undefined,
      parsedData: transformParsedResume(data.parsed_data),
      uploadedAt: data.uploaded_at as string | undefined,
    }
  },

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
          isOwner: r.is_owner === true,  // default to true if not specified
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
        isOwner: r.is_owner === true,
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

  // Skill Gap Analysis for Candidates
  getMySkillGap: async (
    options: {
      jobId?: string
      jobRequirements?: string[]
    },
    token?: string
  ): Promise<{
    overallMatchScore: number
    totalRequirements: number
    matchedRequirements: number
    criticalGaps: string[]
    proficiencyDistribution: Record<string, number>
    avgProficiencyScore: number
    learningPriorities: LearningPriority[]
    bonusSkills: string[]
    strongestAreas: string[]
  }> => {
    const url = `${API_BASE_URL}/api/candidates/me/skill-gap`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const body: Record<string, unknown> = {}
    if (options.jobId) body.job_id = options.jobId
    if (options.jobRequirements) body.job_requirements = options.jobRequirements

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to analyze skill gap')
    }

    const data = await response.json()
    return {
      overallMatchScore: data.overall_match_score,
      totalRequirements: data.total_requirements,
      matchedRequirements: data.matched_requirements,
      criticalGaps: data.critical_gaps,
      proficiencyDistribution: data.proficiency_distribution,
      avgProficiencyScore: data.avg_proficiency_score,
      learningPriorities: data.learning_priorities,
      bonusSkills: data.bonus_skills,
      strongestAreas: data.strongest_areas,
    }
  },

  // Activities API
  getActivities: async (token?: string): Promise<Activity[]> => {
    const url = `${API_BASE_URL}/api/candidates/me/activities`
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
      throw new ApiError(response.status, error.detail || 'Failed to get activities')
    }

    const data = await response.json()
    return data.map((item: { id: string; activity_name: string; organization?: string; role?: string; description?: string; start_date?: string; end_date?: string }) => ({
      id: item.id,
      activityName: item.activity_name,
      organization: item.organization,
      role: item.role,
      description: item.description,
      startDate: item.start_date,
      endDate: item.end_date,
    }))
  },

  createActivity: async (activity: Omit<Activity, 'id'>, token?: string): Promise<Activity> => {
    const url = `${API_BASE_URL}/api/candidates/me/activities`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        activity_name: activity.activityName,
        organization: activity.organization,
        role: activity.role,
        description: activity.description,
        start_date: activity.startDate,
        end_date: activity.endDate,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to create activity')
    }

    const data = await response.json()
    return {
      id: data.id,
      activityName: data.activity_name,
      organization: data.organization,
      role: data.role,
      description: data.description,
      startDate: data.start_date,
      endDate: data.end_date,
    }
  },

  updateActivity: async (id: string, activity: Partial<Omit<Activity, 'id'>>, token?: string): Promise<Activity> => {
    const url = `${API_BASE_URL}/api/candidates/me/activities/${id}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const body: Record<string, unknown> = {}
    if (activity.activityName !== undefined) body.activity_name = activity.activityName
    if (activity.organization !== undefined) body.organization = activity.organization
    if (activity.role !== undefined) body.role = activity.role
    if (activity.description !== undefined) body.description = activity.description
    if (activity.startDate !== undefined) body.start_date = activity.startDate
    if (activity.endDate !== undefined) body.end_date = activity.endDate

    const response = await fetch(url, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to update activity')
    }

    const data = await response.json()
    return {
      id: data.id,
      activityName: data.activity_name,
      organization: data.organization,
      role: data.role,
      description: data.description,
      startDate: data.start_date,
      endDate: data.end_date,
    }
  },

  deleteActivity: async (id: string, token?: string): Promise<void> => {
    const url = `${API_BASE_URL}/api/candidates/me/activities/${id}`
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
      throw new ApiError(response.status, error.detail || 'Failed to delete activity')
    }
  },

  // Awards API
  getAwards: async (token?: string): Promise<Award[]> => {
    const url = `${API_BASE_URL}/api/candidates/me/awards`
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
      throw new ApiError(response.status, error.detail || 'Failed to get awards')
    }

    const data = await response.json()
    return data.map((item: { id: string; name: string; issuer?: string; date?: string; description?: string }) => ({
      id: item.id,
      name: item.name,
      issuer: item.issuer,
      date: item.date,
      description: item.description,
    }))
  },

  createAward: async (award: Omit<Award, 'id'>, token?: string): Promise<Award> => {
    const url = `${API_BASE_URL}/api/candidates/me/awards`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        name: award.name,
        issuer: award.issuer,
        date: award.date,
        description: award.description,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to create award')
    }

    const data = await response.json()
    return {
      id: data.id,
      name: data.name,
      issuer: data.issuer,
      date: data.date,
      description: data.description,
    }
  },

  updateAward: async (id: string, award: Partial<Omit<Award, 'id'>>, token?: string): Promise<Award> => {
    const url = `${API_BASE_URL}/api/candidates/me/awards/${id}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null)
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const body: Record<string, unknown> = {}
    if (award.name !== undefined) body.name = award.name
    if (award.issuer !== undefined) body.issuer = award.issuer
    if (award.date !== undefined) body.date = award.date
    if (award.description !== undefined) body.description = award.description

    const response = await fetch(url, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(response.status, error.detail || 'Failed to update award')
    }

    const data = await response.json()
    return {
      id: data.id,
      name: data.name,
      issuer: data.issuer,
      date: data.date,
      description: data.description,
    }
  },

  deleteAward: async (id: string, token?: string): Promise<void> => {
    const url = `${API_BASE_URL}/api/candidates/me/awards/${id}`
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
      throw new ApiError(response.status, error.detail || 'Failed to delete award')
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

// Helper to transform employer response from snake_case to camelCase
function transformEmployerResponse(response: Record<string, unknown>): Employer {
  return {
    id: response.id as string,
    name: response.name as string | undefined,
    companyName: (response.company_name || response.companyName) as string,
    email: response.email as string,
    logo: response.logo as string | undefined,
    industry: response.industry as string | undefined,
    companySize: (response.company_size || response.companySize) as string | undefined,
    isVerified: (response.is_verified ?? response.isVerified ?? false) as boolean,
    createdAt: (response.created_at || response.createdAt || new Date().toISOString()) as string,
    googleCalendarConnectedAt: (response.google_calendar_connected_at || response.googleCalendarConnectedAt) as string | undefined,
  }
}

// Employer API
export const employerApi = {
  register: async (data: {
    name?: string
    companyName: string
    email: string
    password: string
  }): Promise<EmployerWithToken> => {
    const response = await apiRequest<Record<string, unknown>>('/api/employers/register', {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        company_name: data.companyName,
        email: data.email,
        password: data.password,
      }),
    })
    return {
      employer: transformEmployerResponse(response.employer as Record<string, unknown>),
      token: response.token as string,
      tokenType: (response.token_type || response.tokenType || 'bearer') as string,
    }
  },

  login: async (email: string, password: string): Promise<EmployerWithToken> => {
    const response = await apiRequest<Record<string, unknown>>('/api/employers/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    return {
      employer: transformEmployerResponse(response.employer as Record<string, unknown>),
      token: response.token as string,
      tokenType: (response.token_type || response.tokenType || 'bearer') as string,
    }
  },

  getMe: async (): Promise<Employer> => {
    const response = await apiRequest<Record<string, unknown>>('/api/employers/me')
    return transformEmployerResponse(response)
  },

  updateProfile: async (data: {
    name?: string
    companyName?: string
    industry?: string
    companySize?: string
  }): Promise<Employer> => {
    const response = await apiRequest<Record<string, unknown>>('/api/employers/me', {
      method: 'PATCH',
      body: JSON.stringify({
        name: data.name,
        company_name: data.companyName,
        industry: data.industry,
        company_size: data.companySize,
      }),
    })
    return transformEmployerResponse(response)
  },

  getDashboard: async (): Promise<DashboardStats> => {
    const data = await apiRequest<Record<string, unknown>>('/api/employers/dashboard')
    return {
      totalInterviews: (data.total_interviews ?? data.totalInterviews ?? 0) as number,
      pendingReview: (data.pending_review ?? data.pendingReview ?? 0) as number,
      shortlisted: (data.shortlisted ?? 0) as number,
      rejected: (data.rejected ?? 0) as number,
      averageScore: (data.average_score ?? data.averageScore) as number | undefined,
    }
  },

  listJobs: async (isActive?: boolean): Promise<{ jobs: Job[]; total: number }> => {
    const data = await apiRequest<Record<string, unknown>>(`/api/employers/jobs${isActive !== undefined ? `?is_active=${isActive}` : ''}`)
    const jobs = ((data.jobs as Array<Record<string, unknown>>) || []).map(j => ({
      id: j.id as string,
      title: j.title as string,
      description: j.description as string,
      vertical: (j.vertical) as Vertical | undefined,
      roleType: (j.role_type ?? j.roleType) as RoleType | undefined,
      requirements: (j.requirements || []) as string[],
      location: j.location as string | undefined,
      salaryMin: (j.salary_min ?? j.salaryMin) as number | undefined,
      salaryMax: (j.salary_max ?? j.salaryMax) as number | undefined,
      isActive: (j.is_active ?? j.isActive ?? true) as boolean,
      employerId: (j.employer_id ?? j.employerId) as string,
      createdAt: (j.created_at ?? j.createdAt) as string,
    }))
    return { jobs, total: (data.total as number) || jobs.length }
  },

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

  // Match Alerts
  getMatchAlerts: async (options?: {
    limit?: number
    offset?: number
    unreadOnly?: boolean
  }): Promise<MatchAlertList> => {
    const params = new URLSearchParams()
    if (options?.limit !== undefined) params.append('limit', options.limit.toString())
    if (options?.offset !== undefined) params.append('offset', options.offset.toString())
    if (options?.unreadOnly !== undefined) params.append('unread_only', options.unreadOnly.toString())

    const queryString = params.toString()
    const url = `/api/employers/match-alerts${queryString ? `?${queryString}` : ''}`
    const data = await apiRequest<Record<string, unknown>>(url)

    // Transform snake_case to camelCase
    const alerts = ((data.alerts as Array<Record<string, unknown>>) || []).map(a => {
      const candidate = a.candidate as Record<string, unknown>
      return {
        id: a.id as string,
        candidate: {
          id: candidate.id as string,
          name: candidate.name as string,
          email: candidate.email as string,
          university: candidate.university as string | undefined,
          major: candidate.major as string | undefined,
          graduationYear: (candidate.graduation_year ?? candidate.graduationYear) as number | undefined,
        },
        jobId: (a.job_id ?? a.jobId) as string | undefined,
        jobTitle: (a.job_title ?? a.jobTitle) as string | undefined,
        matchScore: (a.match_score ?? a.matchScore) as number,
        interviewScore: (a.interview_score ?? a.interviewScore) as number | undefined,
        skillsMatchScore: (a.skills_match_score ?? a.skillsMatchScore) as number | undefined,
        status: a.status as string,
        createdAt: (a.created_at ?? a.createdAt) as string,
        isNew: (a.is_new ?? a.isNew ?? false) as boolean,
      }
    })

    return {
      alerts,
      total: (data.total as number) || 0,
      unreadCount: (data.unread_count ?? (data as Record<string, unknown>).unreadCount ?? 0) as number,
    }
  },

  markMatchViewed: (matchId: string): Promise<{ success: boolean; status: string }> =>
    apiRequest(`/api/employers/match-alerts/${matchId}/mark-viewed`, { method: 'POST' }),

  // Skill Gap Analysis & ML-Powered Matching
  analyzeSkillGap: async (
    candidateId: string,
    jobId?: string,
    jobRequirements?: string[]
  ): Promise<SkillGapAnalysis> => {
    const body: Record<string, unknown> = { candidate_id: candidateId }
    if (jobId) body.job_id = jobId
    if (jobRequirements) body.job_requirements = jobRequirements

    const response = await apiRequest('/api/employers/skill-gap/analyze', {
      method: 'POST',
      body: JSON.stringify(body),
    })
    const data = response as Record<string, unknown>

    return {
      overallMatchScore: data.overall_match_score as number,
      totalRequirements: data.total_requirements as number,
      matchedRequirements: data.matched_requirements as number,
      criticalGaps: data.critical_gaps as string[],
      skillMatches: data.skill_matches as SkillMatch[],
      categoryCoverage: data.category_coverage as Record<string, {
        matched: number
        total: number
        coverageScore: number
        avgProficiency: number
        importance: string
        description: string
      }>,
      proficiencyDistribution: data.proficiency_distribution as Record<string, number>,
      avgProficiencyScore: data.avg_proficiency_score as number,
      learningPriorities: data.learning_priorities as LearningPriority[],
      alternativeSkills: data.alternative_skills as Array<{
        missingRequirement: string
        alternativeSkill: string
        transferability: string
        note: string
      }>,
      transferableSkills: data.transferable_skills as string[],
      bonusSkills: data.bonus_skills as string[],
      strongestAreas: data.strongest_areas as string[],
    }
  },

  getEnhancedMatch: async (
    candidateId: string,
    options?: {
      jobId?: string
      jobTitle?: string
      jobRequirements?: string[]
      jobVertical?: string
      includeSkillGap?: boolean
    }
  ): Promise<EnhancedMatchResult> => {
    const body: Record<string, unknown> = {
      candidate_id: candidateId,
      include_skill_gap: options?.includeSkillGap ?? true,
    }
    if (options?.jobId) body.job_id = options.jobId
    if (options?.jobTitle) body.job_title = options.jobTitle
    if (options?.jobRequirements) body.job_requirements = options.jobRequirements
    if (options?.jobVertical) body.job_vertical = options.jobVertical

    const response = await apiRequest('/api/employers/enhanced-match', {
      method: 'POST',
      body: JSON.stringify(body),
    })
    const data = response as Record<string, unknown>
    const skillGapSummary = data.skill_gap_summary as Record<string, unknown> | undefined

    return {
      overallMatchScore: data.overall_match_score as number,
      interviewScore: data.interview_score as number,
      skillsMatchScore: data.skills_match_score as number,
      experienceMatchScore: data.experience_match_score as number,
      githubSignalScore: data.github_signal_score as number,
      educationScore: data.education_score as number,
      growthTrajectoryScore: data.growth_trajectory_score as number,
      locationMatch: data.location_match as boolean,
      factors: data.factors as Record<string, unknown>,
      skillGapSummary: {
        matchPercentage: (skillGapSummary?.match_percentage as number) || 0,
        matchedCount: (skillGapSummary?.matched_count as number) || 0,
        missingCount: (skillGapSummary?.missing_count as number) || 0,
        missingSkills: (skillGapSummary?.missing_skills as string[]) || [],
        semanticMatches: (skillGapSummary?.semantic_matches as number) || 0,
        hasCriticalGaps: (skillGapSummary?.has_critical_gaps as boolean) || false,
      },
      topStrengths: data.top_strengths as string[],
      areasForGrowth: data.areas_for_growth as string[],
      hiringRecommendation: data.hiring_recommendation as string,
      confidenceScore: data.confidence_score as number,
      aiReasoning: data.ai_reasoning as string,
    }
  },

  rankCandidates: async (
    jobId: string,
    options?: {
      limit?: number
      offset?: number
      minScore?: number
      includeSkillGap?: boolean
    }
  ): Promise<CandidateRankingResponse> => {
    const body: Record<string, unknown> = {
      job_id: jobId,
      limit: options?.limit ?? 20,
      offset: options?.offset ?? 0,
      min_score: options?.minScore ?? 0,
      include_skill_gap: options?.includeSkillGap ?? false,
    }

    const response = await apiRequest('/api/employers/candidates/rank', {
      method: 'POST',
      body: JSON.stringify(body),
    })
    const data = response as Record<string, unknown>

    return {
      jobId: data.job_id as string,
      jobTitle: data.job_title as string,
      candidates: (data.candidates as Array<Record<string, unknown>>).map((c) => ({
        candidateId: c.candidate_id as string,
        name: c.name as string,
        email: c.email as string,
        university: c.university as string | undefined,
        graduationYear: c.graduation_year as number | undefined,
        overallMatchScore: c.overall_match_score as number,
        interviewScore: c.interview_score as number | undefined,
        skillsMatchScore: c.skills_match_score as number | undefined,
        githubSignalScore: c.github_signal_score as number | undefined,
        topStrengths: (c.top_strengths as string[]) || [],
        skillGaps: (c.skill_gaps as string[]) || [],
        hiringRecommendation: c.hiring_recommendation as string,
      })),
      total: data.total as number,
      averageMatchScore: data.average_match_score as number,
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

  createToken: async (jobId: string, maxUses: number = 0, expiresInDays?: number): Promise<InviteTokenResponse> => {
    const res = await apiRequest<Record<string, unknown>>(`/api/employers/jobs/${jobId}/invites`, {
      method: 'POST',
      body: JSON.stringify({
        job_id: jobId,
        max_uses: maxUses,
        expires_in_days: expiresInDays,
      }),
    })
    return {
      id: res.id as string,
      token: res.token as string,
      jobId: res.job_id as string,
      jobTitle: res.job_title as string | undefined,
      maxUses: res.max_uses as number,
      usedCount: res.used_count as number,
      expiresAt: res.expires_at as string | undefined,
      isActive: res.is_active as boolean,
      inviteUrl: res.invite_url as string,
      createdAt: res.created_at as string,
    }
  },

  listTokens: async (jobId: string): Promise<{ tokens: InviteTokenResponse[]; total: number }> => {
    const res = await apiRequest<Record<string, unknown>>(`/api/employers/jobs/${jobId}/invites`)
    const tokens = (res.tokens as Array<Record<string, unknown>>).map(t => ({
      id: t.id as string,
      token: t.token as string,
      jobId: t.job_id as string,
      jobTitle: t.job_title as string | undefined,
      maxUses: t.max_uses as number,
      usedCount: t.used_count as number,
      expiresAt: t.expires_at as string | undefined,
      isActive: t.is_active as boolean,
      inviteUrl: t.invite_url as string,
      createdAt: t.created_at as string,
    }))
    return { tokens, total: res.total as number }
  },

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
  transcriptUploaded: boolean
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
    strengths?: string[]
    concerns?: string[]
  }
  interview?: {
    sessionId: string
    totalScore?: number
    aiSummary?: string
    completedAt?: string
    responses?: InterviewResponseDetail[]
    overallStrengths?: string[]
    overallConcerns?: string[]
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
    roleType: RoleType,
    isPractice: boolean = false
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
        is_practice: isPractice,
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
        nextEligibleAt: p.next_interview_available_at || p.next_eligible_at,
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
      transcriptUploaded: (completionStatus.transcript_uploaded || completionStatus.transcriptUploaded || false) as boolean,
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

  // Forgot password
  forgotPassword: (email: string, userType: 'candidate' | 'employer'): Promise<{
    success: boolean
    message: string
  }> =>
    apiRequest('/api/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({
        email,
        user_type: userType,
      }),
    }),

  // Reset password
  resetPassword: (token: string, userType: 'candidate' | 'employer', newPassword: string): Promise<{
    success: boolean
    message: string
  }> =>
    apiRequest('/api/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({
        token,
        user_type: userType,
        new_password: newPassword,
      }),
    }),
}

// ==================== CALENDAR API ====================

export interface CalendarStatus {
  connected: boolean
  connectedAt?: string
}

// Scheduled interview types
export type InterviewType = 'phone_screen' | 'technical' | 'behavioral' | 'culture_fit' | 'final' | 'other'
export type ScheduledInterviewStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no_show' | 'rescheduled'

export interface ScheduledInterview {
  id: string
  employerId: string
  candidateId: string
  candidateName?: string
  candidateEmail?: string
  jobId?: string
  jobTitle?: string
  title: string
  description?: string
  interviewType: InterviewType
  scheduledAt: string
  durationMinutes: number
  timezone: string
  googleEventId?: string
  googleMeetLink?: string
  calendarLink?: string
  additionalAttendees?: string[]
  status: ScheduledInterviewStatus
  employerNotes?: string
  rescheduledToId?: string
  createdAt: string
  updatedAt?: string
}

export interface MeetingDetails {
  eventId: string
  calendarLink: string
  meetLink?: string
}

export const calendarApi = {
  // Get Google OAuth URL
  getGoogleAuthUrl: async (): Promise<{ url: string; state: string }> => {
    const response = await apiRequest<{ url: string; state: string }>('/api/calendar/google/url')
    return response
  },

  // Connect Google Calendar (exchange code for tokens)
  connectGoogle: async (code: string, state?: string, candidateId?: string): Promise<{
    success: boolean
    message: string
  }> => {
    const candidateToken = typeof window !== 'undefined' ? localStorage.getItem('candidate_token') : null
    if (!candidateToken) {
      throw new ApiError(401, 'You must be logged in to connect Google Calendar')
    }

    const url = `${API_BASE_URL}/api/calendar/google/callback?candidate_id=${candidateId}`
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${candidateToken}`,
      },
      body: JSON.stringify({ code, state }),
    })

    if (!res.ok) {
      let message = 'Failed to connect Google Calendar'
      try {
        const error = await res.json()
        message = error.detail || error.message || message
      } catch {
        // ignore JSON parse errors
      }
      throw new ApiError(res.status, message)
    }

    return res.json()
  },

  // Get calendar connection status
  getStatus: async (candidateId: string): Promise<CalendarStatus> => {
    const response = await apiRequest<{ connected: boolean; connected_at?: string }>(
      `/api/calendar/google/status?candidate_id=${candidateId}`
    )
    return {
      connected: response.connected,
      connectedAt: response.connected_at,
    }
  },

  // Disconnect Google Calendar
  disconnect: async (candidateId: string): Promise<{ success: boolean; message: string }> => {
    return apiRequest(`/api/calendar/google/disconnect?candidate_id=${candidateId}`, {
      method: 'DELETE',
    })
  },

  // Create a meeting with Google Meet link
  createMeeting: async (
    candidateId: string,
    data: {
      title: string
      description: string
      startTime: Date
      durationMinutes?: number
      attendeeEmails: string[]
      timezone?: string
    }
  ): Promise<MeetingDetails> => {
    const response = await apiRequest<{
      success: boolean
      event_id: string
      calendar_link: string
      meet_link?: string
    }>(`/api/calendar/meetings/create?candidate_id=${candidateId}`, {
      method: 'POST',
      body: JSON.stringify({
        title: data.title,
        description: data.description,
        start_time: data.startTime.toISOString(),
        duration_minutes: data.durationMinutes || 30,
        attendee_emails: data.attendeeEmails,
        timezone: data.timezone || 'America/Los_Angeles',
      }),
    })

    return {
      eventId: response.event_id,
      calendarLink: response.calendar_link,
      meetLink: response.meet_link,
    }
  },

  // Cancel a meeting
  cancelMeeting: async (candidateId: string, eventId: string): Promise<{ success: boolean; message: string }> => {
    return apiRequest(`/api/calendar/meetings/${eventId}?candidate_id=${candidateId}`, {
      method: 'DELETE',
    })
  },
}

// ==================== EMPLOYER CALENDAR API ====================

export const employerCalendarApi = {
  // Get Google OAuth URL for employer
  getGoogleAuthUrl: async (): Promise<{ url: string; state: string }> => {
    return apiRequest('/api/employers/calendar/google/url')
  },

  // Connect Google Calendar (exchange code for tokens)
  connectGoogle: async (code: string, state?: string): Promise<{
    success: boolean
    message: string
  }> => {
    return apiRequest('/api/employers/calendar/google/callback', {
      method: 'POST',
      body: JSON.stringify({ code, state }),
    })
  },

  // Get calendar connection status
  getStatus: async (): Promise<CalendarStatus> => {
    const response = await apiRequest<{ connected: boolean; connected_at?: string }>(
      '/api/employers/calendar/google/status'
    )
    return {
      connected: response.connected,
      connectedAt: response.connected_at,
    }
  },

  // Disconnect Google Calendar
  disconnect: async (): Promise<{ success: boolean; message: string }> => {
    return apiRequest('/api/employers/calendar/google/disconnect', {
      method: 'DELETE',
    })
  },
}

// ==================== SCHEDULED INTERVIEW API ====================

// Helper to transform scheduled interview response
function transformScheduledInterview(data: Record<string, unknown>): ScheduledInterview {
  return {
    id: data.id as string,
    employerId: (data.employer_id || data.employerId) as string,
    candidateId: (data.candidate_id || data.candidateId) as string,
    candidateName: (data.candidate_name || data.candidateName) as string | undefined,
    candidateEmail: (data.candidate_email || data.candidateEmail) as string | undefined,
    jobId: (data.job_id || data.jobId) as string | undefined,
    jobTitle: (data.job_title || data.jobTitle) as string | undefined,
    title: data.title as string,
    description: data.description as string | undefined,
    interviewType: (data.interview_type || data.interviewType || 'other') as InterviewType,
    scheduledAt: (data.scheduled_at || data.scheduledAt) as string,
    durationMinutes: (data.duration_minutes || data.durationMinutes || 30) as number,
    timezone: data.timezone as string,
    googleEventId: (data.google_event_id || data.googleEventId) as string | undefined,
    googleMeetLink: (data.google_meet_link || data.googleMeetLink) as string | undefined,
    calendarLink: (data.calendar_link || data.calendarLink) as string | undefined,
    additionalAttendees: (data.additional_attendees || data.additionalAttendees) as string[] | undefined,
    status: (data.status || 'pending') as ScheduledInterviewStatus,
    employerNotes: (data.employer_notes || data.employerNotes) as string | undefined,
    rescheduledToId: (data.rescheduled_to_id || data.rescheduledToId) as string | undefined,
    createdAt: (data.created_at || data.createdAt) as string,
    updatedAt: (data.updated_at || data.updatedAt) as string | undefined,
  }
}

export const scheduledInterviewApi = {
  // Schedule an interview with a candidate
  schedule: async (
    profileId: string,
    data: {
      interviewType?: InterviewType
      title?: string
      description?: string
      scheduledAt: Date
      durationMinutes?: number
      timezone?: string
      jobId?: string
      additionalAttendees?: string[]
      employerNotes?: string
    }
  ): Promise<{
    success: boolean
    interview: ScheduledInterview
    googleMeetLink?: string
    calendarLink?: string
    message: string
  }> => {
    const response = await apiRequest<{
      success: boolean
      interview: Record<string, unknown>
      google_meet_link?: string
      calendar_link?: string
      message: string
    }>(`/api/employers/talent-pool/${profileId}/schedule-interview`, {
      method: 'POST',
      body: JSON.stringify({
        interview_type: data.interviewType || 'other',
        title: data.title,
        description: data.description,
        scheduled_at: data.scheduledAt.toISOString(),
        duration_minutes: data.durationMinutes || 30,
        timezone: data.timezone || 'America/Los_Angeles',
        job_id: data.jobId,
        additional_attendees: data.additionalAttendees,
        employer_notes: data.employerNotes,
      }),
    })

    return {
      success: response.success,
      interview: transformScheduledInterview(response.interview),
      googleMeetLink: response.google_meet_link,
      calendarLink: response.calendar_link,
      message: response.message,
    }
  },

  // List scheduled interviews
  list: async (params?: {
    status?: ScheduledInterviewStatus
    jobId?: string
    fromDate?: Date
    toDate?: Date
    limit?: number
    offset?: number
  }): Promise<{
    interviews: ScheduledInterview[]
    total: number
  }> => {
    const searchParams = new URLSearchParams()
    if (params?.status) searchParams.set('status_filter', params.status)
    if (params?.jobId) searchParams.set('job_id', params.jobId)
    if (params?.fromDate) searchParams.set('from_date', params.fromDate.toISOString())
    if (params?.toDate) searchParams.set('to_date', params.toDate.toISOString())
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.offset) searchParams.set('offset', params.offset.toString())

    const query = searchParams.toString()
    const response = await apiRequest<{
      interviews: Record<string, unknown>[]
      total: number
    }>(`/api/employers/scheduled-interviews${query ? `?${query}` : ''}`)

    return {
      interviews: response.interviews.map(transformScheduledInterview),
      total: response.total,
    }
  },

  // Get a specific scheduled interview
  get: async (interviewId: string): Promise<ScheduledInterview> => {
    const response = await apiRequest<Record<string, unknown>>(
      `/api/employers/scheduled-interviews/${interviewId}`
    )
    return transformScheduledInterview(response)
  },

  // Cancel a scheduled interview
  cancel: async (interviewId: string, notifyAttendees: boolean = true): Promise<{
    success: boolean
    message: string
    interviewId: string
  }> => {
    const response = await apiRequest<{
      success: boolean
      message: string
      interview_id: string
    }>(`/api/employers/scheduled-interviews/${interviewId}?notify_attendees=${notifyAttendees}`, {
      method: 'DELETE',
    })

    return {
      success: response.success,
      message: response.message,
      interviewId: response.interview_id,
    }
  },

  // Reschedule an interview
  reschedule: async (
    interviewId: string,
    data: {
      scheduledAt: Date
      durationMinutes?: number
      timezone?: string
      reason?: string
    }
  ): Promise<{
    success: boolean
    message: string
    oldInterview: ScheduledInterview
    newInterview: ScheduledInterview
  }> => {
    const response = await apiRequest<{
      success: boolean
      message: string
      old_interview: Record<string, unknown>
      new_interview: Record<string, unknown>
    }>(`/api/employers/scheduled-interviews/${interviewId}/reschedule`, {
      method: 'POST',
      body: JSON.stringify({
        scheduled_at: data.scheduledAt.toISOString(),
        duration_minutes: data.durationMinutes,
        timezone: data.timezone,
        reason: data.reason,
      }),
    })

    return {
      success: response.success,
      message: response.message,
      oldInterview: transformScheduledInterview(response.old_interview),
      newInterview: transformScheduledInterview(response.new_interview),
    }
  },
}

// ==================== CANDIDATE NOTES API ====================

export interface CandidateNote {
  id: string
  employerId: string
  candidateId: string
  content: string
  createdAt: string
  updatedAt?: string
}

export const candidateNotesApi = {
  // List notes for a candidate
  list: async (candidateId: string): Promise<{
    notes: CandidateNote[]
    total: number
  }> => {
    const response = await apiRequest<{
      notes: Array<{
        id: string
        employer_id: string
        candidate_id: string
        content: string
        created_at: string
        updated_at?: string
      }>
      total: number
    }>(`/api/employers/candidates/${candidateId}/notes`)

    return {
      notes: response.notes.map(n => ({
        id: n.id,
        employerId: n.employer_id,
        candidateId: n.candidate_id,
        content: n.content,
        createdAt: n.created_at,
        updatedAt: n.updated_at,
      })),
      total: response.total,
    }
  },

  // Create a note
  create: async (candidateId: string, content: string): Promise<CandidateNote> => {
    const response = await apiRequest<{
      id: string
      employer_id: string
      candidate_id: string
      content: string
      created_at: string
      updated_at?: string
    }>(`/api/employers/candidates/${candidateId}/notes`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    })

    return {
      id: response.id,
      employerId: response.employer_id,
      candidateId: response.candidate_id,
      content: response.content,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    }
  },

  // Update a note
  update: async (candidateId: string, noteId: string, content: string): Promise<CandidateNote> => {
    const response = await apiRequest<{
      id: string
      employer_id: string
      candidate_id: string
      content: string
      created_at: string
      updated_at?: string
    }>(`/api/employers/candidates/${candidateId}/notes/${noteId}`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    })

    return {
      id: response.id,
      employerId: response.employer_id,
      candidateId: response.candidate_id,
      content: response.content,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    }
  },

  // Delete a note
  delete: async (candidateId: string, noteId: string): Promise<{ success: boolean }> => {
    return apiRequest(`/api/employers/candidates/${candidateId}/notes/${noteId}`, {
      method: 'DELETE',
    })
  },
}

// ==================== TEAM MEMBER API ====================

export type TeamMemberRole = 'admin' | 'recruiter' | 'hiring_manager' | 'interviewer'

export interface TeamMember {
  id: string
  employerId: string
  email: string
  name: string
  role: TeamMemberRole
  isActive: boolean
  googleCalendarConnected: boolean
  googleCalendarConnectedAt?: string
  maxInterviewsPerDay: number
  maxInterviewsPerWeek: number
  createdAt: string
  updatedAt?: string
  // Load info (from getTeamMember)
  interviewsToday?: number
  interviewsThisWeek?: number
  availableToday?: boolean
  availableThisWeek?: boolean
}

export interface AvailabilitySlot {
  id: string
  teamMemberId: string
  dayOfWeek: number
  startTime: string
  endTime: string
  timezone: string
  isActive: boolean
  createdAt: string
}

export interface AvailabilityException {
  id: string
  teamMemberId: string
  date: string
  isUnavailable: boolean
  startTime?: string
  endTime?: string
  reason?: string
  createdAt: string
}

export interface TimeSlot {
  start: string
  end: string
  interviewerId: string
  interviewerName?: string
}

// Helper to transform team member from snake_case to camelCase
function transformTeamMember(data: Record<string, unknown>): TeamMember {
  return {
    id: data.id as string,
    employerId: (data.employer_id || data.employerId) as string,
    email: data.email as string,
    name: data.name as string,
    role: (data.role || 'interviewer') as TeamMemberRole,
    isActive: (data.is_active ?? data.isActive ?? true) as boolean,
    googleCalendarConnected: (data.google_calendar_connected ?? data.googleCalendarConnected ?? false) as boolean,
    googleCalendarConnectedAt: (data.google_calendar_connected_at || data.googleCalendarConnectedAt) as string | undefined,
    maxInterviewsPerDay: (data.max_interviews_per_day || data.maxInterviewsPerDay || 4) as number,
    maxInterviewsPerWeek: (data.max_interviews_per_week || data.maxInterviewsPerWeek || 15) as number,
    createdAt: (data.created_at || data.createdAt) as string,
    updatedAt: (data.updated_at || data.updatedAt) as string | undefined,
    interviewsToday: (data.interviews_today || data.interviewsToday) as number | undefined,
    interviewsThisWeek: (data.interviews_this_week || data.interviewsThisWeek) as number | undefined,
    availableToday: (data.available_today ?? data.availableToday) as boolean | undefined,
    availableThisWeek: (data.available_this_week ?? data.availableThisWeek) as boolean | undefined,
  }
}

export const teamMemberApi = {
  // Create a team member
  create: async (data: {
    email: string
    name: string
    role?: TeamMemberRole
    maxInterviewsPerDay?: number
    maxInterviewsPerWeek?: number
  }): Promise<TeamMember> => {
    const response = await apiRequest<Record<string, unknown>>('/api/employers/team-members', {
      method: 'POST',
      body: JSON.stringify({
        email: data.email,
        name: data.name,
        role: data.role || 'interviewer',
        max_interviews_per_day: data.maxInterviewsPerDay || 4,
        max_interviews_per_week: data.maxInterviewsPerWeek || 15,
      }),
    })
    return transformTeamMember(response)
  },

  // List team members
  list: async (includeInactive?: boolean): Promise<{
    teamMembers: TeamMember[]
    total: number
  }> => {
    const query = includeInactive ? '?include_inactive=true' : ''
    const response = await apiRequest<{
      team_members: Record<string, unknown>[]
      total: number
    }>(`/api/employers/team-members${query}`)
    return {
      teamMembers: response.team_members.map(transformTeamMember),
      total: response.total,
    }
  },

  // Get a team member
  get: async (teamMemberId: string): Promise<TeamMember> => {
    const response = await apiRequest<Record<string, unknown>>(
      `/api/employers/team-members/${teamMemberId}`
    )
    return transformTeamMember(response)
  },

  // Update a team member
  update: async (teamMemberId: string, data: {
    name?: string
    role?: TeamMemberRole
    isActive?: boolean
    maxInterviewsPerDay?: number
    maxInterviewsPerWeek?: number
  }): Promise<TeamMember> => {
    const response = await apiRequest<Record<string, unknown>>(
      `/api/employers/team-members/${teamMemberId}`,
      {
        method: 'PATCH',
        body: JSON.stringify({
          name: data.name,
          role: data.role,
          is_active: data.isActive,
          max_interviews_per_day: data.maxInterviewsPerDay,
          max_interviews_per_week: data.maxInterviewsPerWeek,
        }),
      }
    )
    return transformTeamMember(response)
  },

  // Delete a team member
  delete: async (teamMemberId: string): Promise<void> => {
    return apiRequest(`/api/employers/team-members/${teamMemberId}`, {
      method: 'DELETE',
    })
  },

  // Get calendar connect URL
  getCalendarConnectUrl: async (teamMemberId: string): Promise<{ url: string }> => {
    return apiRequest(`/api/employers/team-members/${teamMemberId}/calendar/connect-url`)
  },

  // Connect calendar
  connectCalendar: async (teamMemberId: string, code: string): Promise<{
    success: boolean
    message: string
    connectedAt?: string
  }> => {
    const response = await apiRequest<{
      success: boolean
      message: string
      connected_at?: string
    }>(`/api/employers/team-members/${teamMemberId}/calendar/connect`, {
      method: 'POST',
      body: JSON.stringify({ code }),
    })
    return {
      success: response.success,
      message: response.message,
      connectedAt: response.connected_at,
    }
  },

  // Disconnect calendar
  disconnectCalendar: async (teamMemberId: string): Promise<{
    success: boolean
    message: string
  }> => {
    return apiRequest(`/api/employers/team-members/${teamMemberId}/calendar`, {
      method: 'DELETE',
    })
  },

  // Get availability
  getAvailability: async (teamMemberId: string): Promise<{
    teamMemberId: string
    timezone: string
    slots: AvailabilitySlot[]
    exceptions: AvailabilityException[]
  }> => {
    const response = await apiRequest<{
      team_member_id: string
      timezone: string
      slots: Array<{
        id: string
        team_member_id: string
        day_of_week: number
        start_time: string
        end_time: string
        timezone: string
        is_active: boolean
        created_at: string
      }>
      exceptions: Array<{
        id: string
        team_member_id: string
        date: string
        is_unavailable: boolean
        start_time?: string
        end_time?: string
        reason?: string
        created_at: string
      }>
    }>(`/api/employers/team-members/${teamMemberId}/availability`)
    return {
      teamMemberId: response.team_member_id,
      timezone: response.timezone,
      slots: response.slots.map(s => ({
        id: s.id,
        teamMemberId: s.team_member_id,
        dayOfWeek: s.day_of_week,
        startTime: s.start_time,
        endTime: s.end_time,
        timezone: s.timezone,
        isActive: s.is_active,
        createdAt: s.created_at,
      })),
      exceptions: response.exceptions.map(e => ({
        id: e.id,
        teamMemberId: e.team_member_id,
        date: e.date,
        isUnavailable: e.is_unavailable,
        startTime: e.start_time,
        endTime: e.end_time,
        reason: e.reason,
        createdAt: e.created_at,
      })),
    }
  },

  // Set availability
  setAvailability: async (teamMemberId: string, data: {
    slots: Array<{
      dayOfWeek: number
      startTime: string
      endTime: string
    }>
    timezone: string
  }): Promise<{ success: boolean; message: string }> => {
    return apiRequest(`/api/employers/team-members/${teamMemberId}/availability`, {
      method: 'PUT',
      body: JSON.stringify({
        slots: data.slots.map(s => ({
          day_of_week: s.dayOfWeek,
          start_time: s.startTime,
          end_time: s.endTime,
        })),
        timezone: data.timezone,
      }),
    })
  },

  // Add availability exception
  addException: async (teamMemberId: string, data: {
    date: string
    isUnavailable: boolean
    startTime?: string
    endTime?: string
    reason?: string
  }): Promise<AvailabilityException> => {
    const response = await apiRequest<{
      id: string
      team_member_id: string
      date: string
      is_unavailable: boolean
      start_time?: string
      end_time?: string
      reason?: string
      created_at: string
    }>(`/api/employers/team-members/${teamMemberId}/availability/exceptions`, {
      method: 'POST',
      body: JSON.stringify({
        date: data.date,
        is_unavailable: data.isUnavailable,
        start_time: data.startTime,
        end_time: data.endTime,
        reason: data.reason,
      }),
    })
    return {
      id: response.id,
      teamMemberId: response.team_member_id,
      date: response.date,
      isUnavailable: response.is_unavailable,
      startTime: response.start_time,
      endTime: response.end_time,
      reason: response.reason,
      createdAt: response.created_at,
    }
  },

  // Delete availability exception
  deleteException: async (teamMemberId: string, exceptionId: string): Promise<void> => {
    return apiRequest(
      `/api/employers/team-members/${teamMemberId}/availability/exceptions/${exceptionId}`,
      { method: 'DELETE' }
    )
  },

  // Get available slots
  getAvailableSlots: async (teamMemberId: string, params: {
    startDate: string
    endDate: string
    durationMinutes?: number
  }): Promise<{
    slots: TimeSlot[]
    timezone: string
    total: number
  }> => {
    const searchParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
    })
    if (params.durationMinutes) {
      searchParams.set('duration_minutes', params.durationMinutes.toString())
    }
    const response = await apiRequest<{
      slots: Array<{
        start: string
        end: string
        interviewer_id: string
        interviewer_name?: string
      }>
      timezone: string
      total: number
    }>(`/api/employers/team-members/${teamMemberId}/slots?${searchParams}`)
    return {
      slots: response.slots.map(s => ({
        start: s.start,
        end: s.end,
        interviewerId: s.interviewer_id,
        interviewerName: s.interviewer_name,
      })),
      timezone: response.timezone,
      total: response.total,
    }
  },
}

// ==================== SCHEDULING LINK API ====================

export interface SchedulingLink {
  id: string
  employerId: string
  jobId?: string
  jobTitle?: string
  slug: string
  name: string
  description?: string
  durationMinutes: number
  interviewerIds: string[]
  interviewers?: Array<{ id: string; name: string; email: string }>
  bufferBeforeMinutes: number
  bufferAfterMinutes: number
  minNoticeHours: number
  maxDaysAhead: number
  isActive: boolean
  expiresAt?: string
  viewCount: number
  bookingCount: number
  createdAt: string
  updatedAt?: string
  publicUrl?: string
}

export interface PublicSchedulingLink {
  id: string
  name: string
  description?: string
  durationMinutes: number
  companyName: string
  companyLogo?: string
  jobTitle?: string
  minNoticeHours: number
  maxDaysAhead: number
}

// Helper to transform scheduling link from snake_case to camelCase
function transformSchedulingLink(data: Record<string, unknown>): SchedulingLink {
  const interviewers = data.interviewers as Array<Record<string, unknown>> | undefined
  return {
    id: data.id as string,
    employerId: (data.employer_id || data.employerId) as string,
    jobId: (data.job_id || data.jobId) as string | undefined,
    jobTitle: (data.job_title || data.jobTitle) as string | undefined,
    slug: data.slug as string,
    name: data.name as string,
    description: data.description as string | undefined,
    durationMinutes: (data.duration_minutes || data.durationMinutes || 30) as number,
    interviewerIds: (data.interviewer_ids || data.interviewerIds || []) as string[],
    interviewers: interviewers?.map(i => ({
      id: i.id as string,
      name: i.name as string,
      email: i.email as string,
    })),
    bufferBeforeMinutes: (data.buffer_before_minutes || data.bufferBeforeMinutes || 5) as number,
    bufferAfterMinutes: (data.buffer_after_minutes || data.bufferAfterMinutes || 5) as number,
    minNoticeHours: (data.min_notice_hours || data.minNoticeHours || 24) as number,
    maxDaysAhead: (data.max_days_ahead || data.maxDaysAhead || 14) as number,
    isActive: (data.is_active ?? data.isActive ?? true) as boolean,
    expiresAt: (data.expires_at || data.expiresAt) as string | undefined,
    viewCount: (data.view_count || data.viewCount || 0) as number,
    bookingCount: (data.booking_count || data.bookingCount || 0) as number,
    createdAt: (data.created_at || data.createdAt) as string,
    updatedAt: (data.updated_at || data.updatedAt) as string | undefined,
    publicUrl: (data.public_url || data.publicUrl) as string | undefined,
  }
}

export const schedulingLinkApi = {
  // Create a scheduling link
  create: async (data: {
    name: string
    interviewerIds: string[]
    durationMinutes?: number
    jobId?: string
    description?: string
    bufferBeforeMinutes?: number
    bufferAfterMinutes?: number
    minNoticeHours?: number
    maxDaysAhead?: number
    expiresAt?: string
  }): Promise<SchedulingLink> => {
    const response = await apiRequest<Record<string, unknown>>('/api/employers/scheduling-links', {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        interviewer_ids: data.interviewerIds,
        duration_minutes: data.durationMinutes || 30,
        job_id: data.jobId,
        description: data.description,
        buffer_before_minutes: data.bufferBeforeMinutes || 5,
        buffer_after_minutes: data.bufferAfterMinutes || 5,
        min_notice_hours: data.minNoticeHours || 24,
        max_days_ahead: data.maxDaysAhead || 14,
        expires_at: data.expiresAt,
      }),
    })
    return transformSchedulingLink(response)
  },

  // List scheduling links
  list: async (includeInactive?: boolean): Promise<{
    links: SchedulingLink[]
    total: number
  }> => {
    const query = includeInactive ? '?include_inactive=true' : ''
    const response = await apiRequest<{
      links: Record<string, unknown>[]
      total: number
    }>(`/api/employers/scheduling-links${query}`)
    return {
      links: response.links.map(transformSchedulingLink),
      total: response.total,
    }
  },

  // Get a scheduling link
  get: async (linkId: string): Promise<SchedulingLink> => {
    const response = await apiRequest<Record<string, unknown>>(
      `/api/employers/scheduling-links/${linkId}`
    )
    return transformSchedulingLink(response)
  },

  // Update a scheduling link
  update: async (linkId: string, data: {
    name?: string
    description?: string
    durationMinutes?: number
    interviewerIds?: string[]
    bufferBeforeMinutes?: number
    bufferAfterMinutes?: number
    minNoticeHours?: number
    maxDaysAhead?: number
    isActive?: boolean
    expiresAt?: string
  }): Promise<SchedulingLink> => {
    const response = await apiRequest<Record<string, unknown>>(
      `/api/employers/scheduling-links/${linkId}`,
      {
        method: 'PATCH',
        body: JSON.stringify({
          name: data.name,
          description: data.description,
          duration_minutes: data.durationMinutes,
          interviewer_ids: data.interviewerIds,
          buffer_before_minutes: data.bufferBeforeMinutes,
          buffer_after_minutes: data.bufferAfterMinutes,
          min_notice_hours: data.minNoticeHours,
          max_days_ahead: data.maxDaysAhead,
          is_active: data.isActive,
          expires_at: data.expiresAt,
        }),
      }
    )
    return transformSchedulingLink(response)
  },

  // Delete a scheduling link
  delete: async (linkId: string): Promise<void> => {
    return apiRequest(`/api/employers/scheduling-links/${linkId}`, {
      method: 'DELETE',
    })
  },

  // Get public scheduling link info and available slots (no auth required)
  getPublic: async (slug: string): Promise<{
    link: PublicSchedulingLink
    slots: Array<{ start: string; end: string }>
    timezone: string
  }> => {
    const response = await apiRequest<{
      link: {
        id: string
        name: string
        description?: string
        duration_minutes: number
        company_name: string
        company_logo?: string
        job_title?: string
        min_notice_hours: number
        max_days_ahead: number
      }
      slots: Array<{ start: string; end: string }>
      timezone: string
    }>(`/api/employers/scheduling-links/public/${slug}`)
    return {
      link: {
        id: response.link.id,
        name: response.link.name,
        description: response.link.description,
        durationMinutes: response.link.duration_minutes,
        companyName: response.link.company_name,
        companyLogo: response.link.company_logo,
        jobTitle: response.link.job_title,
        minNoticeHours: response.link.min_notice_hours,
        maxDaysAhead: response.link.max_days_ahead,
      },
      slots: response.slots,
      timezone: response.timezone,
    }
  },

  // Book a slot (no auth required)
  book: async (slug: string, data: {
    slotStart: string
    candidateName: string
    candidateEmail: string
    candidatePhone?: string
    candidateNotes?: string
    timezone?: string
  }): Promise<{
    success: boolean
    message: string
    interviewId?: string
    scheduledAt?: string
    durationMinutes?: number
    googleMeetLink?: string
    calendarLink?: string
    interviewerName?: string
    confirmationEmailSent?: boolean
    error?: string
    errorCode?: string
  }> => {
    const response = await apiRequest<{
      success: boolean
      message: string
      interview_id?: string
      scheduled_at?: string
      duration_minutes?: number
      google_meet_link?: string
      calendar_link?: string
      interviewer_name?: string
      confirmation_email_sent?: boolean
      error?: string
      error_code?: string
    }>(`/api/employers/scheduling-links/public/${slug}/book`, {
      method: 'POST',
      body: JSON.stringify({
        slot_start: data.slotStart,
        candidate_name: data.candidateName,
        candidate_email: data.candidateEmail,
        candidate_phone: data.candidatePhone,
        candidate_notes: data.candidateNotes,
        timezone: data.timezone || 'America/Los_Angeles',
      }),
    })
    return {
      success: response.success,
      message: response.message,
      interviewId: response.interview_id,
      scheduledAt: response.scheduled_at,
      durationMinutes: response.duration_minutes,
      googleMeetLink: response.google_meet_link,
      calendarLink: response.calendar_link,
      interviewerName: response.interviewer_name,
      confirmationEmailSent: response.confirmation_email_sent,
      error: response.error,
      errorCode: response.error_code,
    }
  },

  // Find panel slots (where all specified interviewers are available)
  findPanelSlots: async (data: {
    interviewerIds: string[]
    durationMinutes?: number
    daysAhead?: number
  }): Promise<{
    slots: TimeSlot[]
    total: number
  }> => {
    const response = await apiRequest<{
      slots: Array<{
        start: string
        end: string
        interviewer_id: string
        interviewer_name?: string
      }>
      total: number
    }>('/api/employers/scheduling-links/find-panel-slots', {
      method: 'POST',
      body: JSON.stringify({
        interviewer_ids: data.interviewerIds,
        duration_minutes: data.durationMinutes || 30,
        days_ahead: data.daysAhead || 14,
      }),
    })
    return {
      slots: response.slots.map(s => ({
        start: s.start,
        end: s.end,
        interviewerId: s.interviewer_id,
        interviewerName: s.interviewer_name,
      })),
      total: response.total,
    }
  },

  // Check for scheduling conflicts
  checkConflicts: async (data: {
    interviewerIds: string[]
    proposedStart: string
    durationMinutes?: number
  }): Promise<{
    hasConflicts: boolean
    conflicts: Array<{
      interviewerId: string
      interviewerName: string
      conflictType: string
      conflictStart: string
      conflictEnd: string
      description?: string
    }>
    suggestedAlternatives: TimeSlot[]
  }> => {
    const response = await apiRequest<{
      has_conflicts: boolean
      conflicts: Array<{
        interviewer_id: string
        interviewer_name: string
        conflict_type: string
        conflict_start: string
        conflict_end: string
        description?: string
      }>
      suggested_alternatives: Array<{
        start: string
        end: string
        interviewer_id: string
        interviewer_name?: string
      }>
    }>('/api/employers/scheduling-links/check-conflicts', {
      method: 'POST',
      body: JSON.stringify({
        interviewer_ids: data.interviewerIds,
        proposed_start: data.proposedStart,
        duration_minutes: data.durationMinutes || 30,
      }),
    })
    return {
      hasConflicts: response.has_conflicts,
      conflicts: response.conflicts.map(c => ({
        interviewerId: c.interviewer_id,
        interviewerName: c.interviewer_name,
        conflictType: c.conflict_type,
        conflictStart: c.conflict_start,
        conflictEnd: c.conflict_end,
        description: c.description,
      })),
      suggestedAlternatives: response.suggested_alternatives.map(s => ({
        start: s.start,
        end: s.end,
        interviewerId: s.interviewer_id,
        interviewerName: s.interviewer_name,
      })),
    }
  },
}

// ==================== ORGANIZATION / TEAM API ====================

export interface Organization {
  id: string
  name: string
  slug: string
  logoUrl?: string
  website?: string
  industry?: string
  companySize?: string
  description?: string
  plan: string
  memberCount: number
  createdAt: string
}

export interface OrganizationMember {
  id: string
  employerId: string
  name: string
  email: string
  role: 'owner' | 'admin' | 'recruiter' | 'hiring_manager' | 'interviewer'
  joinedAt: string
  invitedBy?: string
}

export interface OrganizationInvite {
  id: string
  email: string
  role: string
  status: 'pending' | 'accepted' | 'expired' | 'cancelled'
  inviteUrl: string
  expiresAt: string
  createdAt: string
  invitedBy?: string
}

export const organizationApi = {
  // Create organization
  create: async (data: {
    name: string
    website?: string
    industry?: string
    companySize?: string
    description?: string
  }): Promise<Organization> => {
    const response = await apiRequest<Record<string, unknown>>('/api/organizations', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return {
      id: response.id as string,
      name: response.name as string,
      slug: response.slug as string,
      logoUrl: response.logo_url as string | undefined,
      website: response.website as string | undefined,
      industry: response.industry as string | undefined,
      companySize: response.company_size as string | undefined,
      description: response.description as string | undefined,
      plan: response.plan as string,
      memberCount: response.member_count as number,
      createdAt: response.created_at as string,
    }
  },

  // Get current organization
  getMe: async (): Promise<Organization> => {
    const response = await apiRequest<Record<string, unknown>>('/api/organizations/me')
    return {
      id: response.id as string,
      name: response.name as string,
      slug: response.slug as string,
      logoUrl: response.logo_url as string | undefined,
      website: response.website as string | undefined,
      industry: response.industry as string | undefined,
      companySize: response.company_size as string | undefined,
      description: response.description as string | undefined,
      plan: response.plan as string,
      memberCount: response.member_count as number,
      createdAt: response.created_at as string,
    }
  },

  // Update organization
  update: async (data: {
    name?: string
    website?: string
    industry?: string
    companySize?: string
    description?: string
    logoUrl?: string
  }): Promise<Organization> => {
    const response = await apiRequest<Record<string, unknown>>('/api/organizations/me', {
      method: 'PATCH',
      body: JSON.stringify({
        name: data.name,
        website: data.website,
        industry: data.industry,
        company_size: data.companySize,
        description: data.description,
        logo_url: data.logoUrl,
      }),
    })
    return {
      id: response.id as string,
      name: response.name as string,
      slug: response.slug as string,
      logoUrl: response.logo_url as string | undefined,
      website: response.website as string | undefined,
      industry: response.industry as string | undefined,
      companySize: response.company_size as string | undefined,
      description: response.description as string | undefined,
      plan: response.plan as string,
      memberCount: response.member_count as number,
      createdAt: response.created_at as string,
    }
  },

  // List team members
  listMembers: async (): Promise<OrganizationMember[]> => {
    const response = await apiRequest<Array<Record<string, unknown>>>('/api/organizations/members')
    return response.map(m => ({
      id: m.id as string,
      employerId: m.employer_id as string,
      name: m.name as string,
      email: m.email as string,
      role: m.role as OrganizationMember['role'],
      joinedAt: m.joined_at as string,
      invitedBy: m.invited_by as string | undefined,
    }))
  },

  // Update member role
  updateMemberRole: (memberId: string, role: string): Promise<{ success: boolean; message: string }> =>
    apiRequest(`/api/organizations/members/${memberId}/role?role=${role}`, {
      method: 'PATCH',
    }),

  // Remove member
  removeMember: (memberId: string): Promise<{ success: boolean; message: string }> =>
    apiRequest(`/api/organizations/members/${memberId}`, {
      method: 'DELETE',
    }),

  // Create invite
  createInvite: async (data: { email: string; role: string }): Promise<OrganizationInvite> => {
    const response = await apiRequest<Record<string, unknown>>('/api/organizations/invites', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return {
      id: response.id as string,
      email: response.email as string,
      role: response.role as string,
      status: response.status as OrganizationInvite['status'],
      inviteUrl: response.invite_url as string,
      expiresAt: response.expires_at as string,
      createdAt: response.created_at as string,
      invitedBy: response.invited_by as string | undefined,
    }
  },

  // List invites
  listInvites: async (): Promise<OrganizationInvite[]> => {
    const response = await apiRequest<Array<Record<string, unknown>>>('/api/organizations/invites')
    return response.map(inv => ({
      id: inv.id as string,
      email: inv.email as string,
      role: inv.role as string,
      status: inv.status as OrganizationInvite['status'],
      inviteUrl: inv.invite_url as string,
      expiresAt: inv.expires_at as string,
      createdAt: inv.created_at as string,
      invitedBy: inv.invited_by as string | undefined,
    }))
  },

  // Cancel invite
  cancelInvite: (inviteId: string): Promise<{ success: boolean; message: string }> =>
    apiRequest(`/api/organizations/invites/${inviteId}`, {
      method: 'DELETE',
    }),

  // Join organization via invite token
  join: (token: string): Promise<{
    success: boolean
    message: string
    organizationId: string
    role: string
  }> =>
    apiRequest('/api/organizations/join', {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),

  // List team jobs (all jobs from organization members)
  listTeamJobs: async (): Promise<Array<{
    id: string
    title: string
    vertical?: string
    roleType?: string
    location?: string
    isActive: boolean
    createdAt: string
    createdBy: string
    createdById: string
  }>> => {
    const response = await apiRequest<{ jobs: Array<Record<string, unknown>> }>('/api/organizations/jobs')
    return response.jobs.map(j => ({
      id: j.id as string,
      title: j.title as string,
      vertical: j.vertical as string | undefined,
      roleType: j.role_type as string | undefined,
      location: j.location as string | undefined,
      isActive: j.is_active as boolean,
      createdAt: j.created_at as string,
      createdBy: j.created_by as string,
      createdById: j.created_by_id as string,
    }))
  },
}


// ============================================================================
// Vibe Code Sessions - AI Coding Session Analysis
// ============================================================================

// Student-facing session (qualitative feedback only - NO numerical scores)
export interface VibeCodeSession {
  id: string
  candidateId: string
  title?: string
  description?: string
  source: string
  projectUrl?: string
  messageCount?: number
  wordCount?: number
  analysisStatus: string  // pending, analyzing, completed, failed
  builderArchetype?: string  // "architect", "iterative_builder", etc.
  strengths?: string[]  // What they did well
  notablePatterns?: string[]  // Interesting behaviors observed
  uploadedAt?: string
  analyzedAt?: string
}

export interface VibeCodeUploadResponse {
  success: boolean
  message: string
  session: VibeCodeSession
}

export interface VibeCodeSessionList {
  sessions: VibeCodeSession[]
  total: number
}

// Employer-facing types (with scores - used in talent pool)
export interface VibeCodeProfileSummary {
  totalSessions: number
  bestBuilderScore?: number
  avgBuilderScore?: number
  primaryArchetype?: string
  topStrengths: string[]
  sourcesUsed: string[]
}

function transformVibeCodeSession(data: Record<string, unknown>): VibeCodeSession {
  return {
    id: data.id as string,
    candidateId: data.candidate_id as string,
    title: data.title as string | undefined,
    description: data.description as string | undefined,
    source: data.source as string,
    projectUrl: data.project_url as string | undefined,
    messageCount: data.message_count as number | undefined,
    wordCount: data.word_count as number | undefined,
    analysisStatus: data.analysis_status as string,
    builderArchetype: data.builder_archetype as string | undefined,
    strengths: data.strengths as string[] | undefined,
    notablePatterns: data.notable_patterns as string[] | undefined,
    uploadedAt: data.uploaded_at as string | undefined,
    analyzedAt: data.analyzed_at as string | undefined,
  }
}

export const vibeCodeApi = {
  // Upload a new AI coding session
  upload: async (data: {
    sessionContent: string
    title?: string
    description?: string
    source?: string
    projectUrl?: string
  }): Promise<VibeCodeUploadResponse> => {
    const response = await apiRequest<Record<string, unknown>>('/api/vibe-code/sessions', {
      method: 'POST',
      body: JSON.stringify({
        session_content: data.sessionContent,
        title: data.title,
        description: data.description,
        source: data.source,
        project_url: data.projectUrl,
      }),
    })
    return {
      success: response.success as boolean,
      message: response.message as string,
      session: transformVibeCodeSession(response.session as Record<string, unknown>),
    }
  },

  // List all sessions for current student (no scores returned)
  listSessions: async (): Promise<VibeCodeSessionList> => {
    const response = await apiRequest<Record<string, unknown>>('/api/vibe-code/sessions')
    const sessions = (response.sessions as Array<Record<string, unknown>>).map(transformVibeCodeSession)
    return {
      sessions,
      total: response.total as number,
    }
  },

  // Get a single session (student view - no scores)
  getSession: async (sessionId: string): Promise<VibeCodeSession> => {
    const data = await apiRequest<Record<string, unknown>>(`/api/vibe-code/sessions/${sessionId}`)
    return transformVibeCodeSession(data)
  },

  // Delete a session
  deleteSession: (sessionId: string): Promise<void> =>
    apiRequest(`/api/vibe-code/sessions/${sessionId}`, { method: 'DELETE' }),

  // Re-trigger analysis
  reanalyze: async (sessionId: string): Promise<VibeCodeSession> => {
    const data = await apiRequest<Record<string, unknown>>(`/api/vibe-code/sessions/${sessionId}/reanalyze`, {
      method: 'POST',
    })
    return transformVibeCodeSession(data)
  },

  // Get candidate's vibe code profile summary (for talent pool - employer facing)
  getProfile: async (candidateId: string): Promise<VibeCodeProfileSummary> => {
    const data = await apiRequest<Record<string, unknown>>(`/api/vibe-code/profile/${candidateId}`)
    return {
      totalSessions: data.total_sessions as number,
      bestBuilderScore: data.best_builder_score as number | undefined,
      avgBuilderScore: data.avg_builder_score as number | undefined,
      primaryArchetype: data.primary_archetype as string | undefined,
      topStrengths: data.top_strengths as string[],
      sourcesUsed: data.sources_used as string[],
    }
  },
}
