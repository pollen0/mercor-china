// Shared types for ZhiPin AI

export enum InterviewStatus {
  PENDING = 'PENDING',
  SCHEDULED = 'SCHEDULED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

export enum MatchStatus {
  PENDING = 'PENDING',
  SHORTLISTED = 'SHORTLISTED',
  REJECTED = 'REJECTED',
  HIRED = 'HIRED',
}

export interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  targetRoles: string[]
  resumeUrl?: string
  createdAt: Date
  updatedAt: Date
}

export interface Employer {
  id: string
  companyName: string
  email: string
  logo?: string
  createdAt: Date
  updatedAt: Date
}

export interface Job {
  id: string
  title: string
  description: string
  requirements: string[]
  location?: string
  salaryMin?: number
  salaryMax?: number
  isActive: boolean
  employerId: string
  createdAt: Date
  updatedAt: Date
}

export interface InterviewSession {
  id: string
  status: InterviewStatus
  scheduledAt?: Date
  startedAt?: Date
  completedAt?: Date
  totalScore?: number
  aiSummary?: string
  candidateId: string
  jobId: string
  createdAt: Date
  updatedAt: Date
}

export interface InterviewResponse {
  id: string
  questionIndex: number
  questionText: string
  videoUrl?: string
  audioUrl?: string
  transcription?: string
  aiScore?: number
  aiAnalysis?: string
  durationSeconds?: number
  sessionId: string
  createdAt: Date
}

export interface Match {
  id: string
  score: number
  status: MatchStatus
  aiReasoning?: string
  candidateId: string
  jobId: string
  createdAt: Date
  updatedAt: Date
}

export const TARGET_ROLE_OPTIONS = [
  { value: 'frontend', label: '前端开发' },
  { value: 'backend', label: '后端开发' },
  { value: 'fullstack', label: '全栈开发' },
  { value: 'mobile', label: '移动端开发' },
  { value: 'data', label: '数据工程师' },
  { value: 'ai', label: 'AI/机器学习' },
  { value: 'devops', label: 'DevOps' },
  { value: 'product', label: '产品经理' },
  { value: 'design', label: 'UI/UX设计' },
  { value: 'qa', label: '测试工程师' },
] as const
