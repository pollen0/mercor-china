'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Suspense } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CandidateCard } from '@/components/dashboard/candidate-card'
import { employerApi, inviteApi, talentPoolApi, type Employer, type DashboardStats, type InterviewSession, type Job, type InviteTokenResponse, type TalentPoolCandidate, type TalentProfileDetail, type Vertical, type RoleType } from '@/lib/api'

type TabType = 'overview' | 'interviews' | 'jobs' | 'talent'

// Vertical and Role Type definitions
const VERTICALS = [
  { value: 'engineering', label: 'Engineering', description: 'Software, DevOps, Full-stack' },
  { value: 'data', label: 'Data', description: 'Data Science, ML, Analytics' },
  { value: 'business', label: 'Business', description: 'Product, Marketing, Finance' },
  { value: 'design', label: 'Design', description: 'UX/UI, Product Design' },
]

const ROLE_TYPES: Record<string, { value: string; label: string }[]> = {
  engineering: [
    { value: 'software_engineer', label: 'Software Engineer' },
    { value: 'frontend_engineer', label: 'Frontend Engineer' },
    { value: 'backend_engineer', label: 'Backend Engineer' },
    { value: 'fullstack_engineer', label: 'Full-stack Engineer' },
    { value: 'mobile_engineer', label: 'Mobile Engineer' },
    { value: 'devops_engineer', label: 'DevOps Engineer' },
  ],
  data: [
    { value: 'data_analyst', label: 'Data Analyst' },
    { value: 'data_scientist', label: 'Data Scientist' },
    { value: 'ml_engineer', label: 'ML Engineer' },
    { value: 'data_engineer', label: 'Data Engineer' },
  ],
  business: [
    { value: 'product_manager', label: 'Product Manager' },
    { value: 'business_analyst', label: 'Business Analyst' },
    { value: 'marketing_associate', label: 'Marketing Associate' },
    { value: 'finance_analyst', label: 'Finance Analyst' },
    { value: 'consultant', label: 'Consultant' },
  ],
  design: [
    { value: 'ux_designer', label: 'UX Designer' },
    { value: 'ui_designer', label: 'UI Designer' },
    { value: 'product_designer', label: 'Product Designer' },
  ],
}

const ROLE_NAMES: Record<string, string> = {
  software_engineer: 'Software Engineer',
  frontend_engineer: 'Frontend Engineer',
  backend_engineer: 'Backend Engineer',
  fullstack_engineer: 'Full Stack Engineer',
  mobile_engineer: 'Mobile Engineer',
  devops_engineer: 'DevOps Engineer',
  data_analyst: 'Data Analyst',
  data_scientist: 'Data Scientist',
  ml_engineer: 'ML Engineer',
  data_engineer: 'Data Engineer',
  product_manager: 'Product Manager',
  business_analyst: 'Business Analyst',
  marketing_associate: 'Marketing Associate',
  finance_analyst: 'Finance Analyst',
  consultant: 'Consultant',
  ux_designer: 'UX Designer',
  ui_designer: 'UI Designer',
  product_designer: 'Product Designer',
}

function DashboardContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const initialTab = (searchParams.get('tab') as TabType) || 'overview'

  const [activeTab, setActiveTab] = useState<TabType>(initialTab)
  const [employer, setEmployer] = useState<Employer | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Overview state
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentInterviews, setRecentInterviews] = useState<InterviewSession[]>([])

  // Interviews state
  const [interviews, setInterviews] = useState<InterviewSession[]>([])
  const [interviewsTotal, setInterviewsTotal] = useState(0)
  const [interviewsLoading, setInterviewsLoading] = useState(false)
  const [selectedJob, setSelectedJob] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [minScoreFilter, setMinScoreFilter] = useState<string>('')
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // Jobs state
  const [jobs, setJobs] = useState<Job[]>([])
  const [jobsLoading, setJobsLoading] = useState(false)
  const [jobViewMode, setJobViewMode] = useState<'list' | 'create' | 'detail' | 'edit'>('list')
  const [selectedJobDetail, setSelectedJobDetail] = useState<Job | null>(null)
  const [invites, setInvites] = useState<InviteTokenResponse[]>([])
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [jobFormData, setJobFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    salaryMin: '',
    salaryMax: '',
    vertical: '',
    roleType: '',
  })
  const [isSavingJob, setIsSavingJob] = useState(false)
  const [jobError, setJobError] = useState<string | null>(null)

  // Talent Pool state
  const [candidates, setCandidates] = useState<TalentPoolCandidate[]>([])
  const [talentTotal, setTalentTotal] = useState(0)
  const [talentLoading, setTalentLoading] = useState(false)
  const [talentVertical, setTalentVertical] = useState<Vertical | ''>('')
  const [talentRole, setTalentRole] = useState<RoleType | ''>('')
  const [talentMinScore, setTalentMinScore] = useState<number>(0)
  const [talentSearch, setTalentSearch] = useState('')
  const [talentSearchInput, setTalentSearchInput] = useState('')

  // Expandable rows state
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [expandedData, setExpandedData] = useState<Record<string, TalentProfileDetail>>({})
  const [loadingDetail, setLoadingDetail] = useState<string | null>(null)

  // Contact modal state
  const [showContactModal, setShowContactModal] = useState(false)
  const [contactCandidate, setContactCandidate] = useState<TalentPoolCandidate | null>(null)
  const [contactSubject, setContactSubject] = useState('')
  const [contactMessage, setContactMessage] = useState('')
  const [isSending, setIsSending] = useState(false)

  // Resume preview modal state
  const [showResumeModal, setShowResumeModal] = useState(false)
  const [resumePreviewUrl, setResumePreviewUrl] = useState<string | null>(null)
  const [resumePreviewName, setResumePreviewName] = useState<string>('')

  // Transcript preview modal state
  const [showTranscriptModal, setShowTranscriptModal] = useState(false)
  const [transcriptData, setTranscriptData] = useState<TalentProfileDetail | null>(null)
  const [transcriptCandidateName, setTranscriptCandidateName] = useState<string>('')

  // Initial data load
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/login')
          return
        }

        // Load employer info and overview data
        const [employerData, statsData, interviewsData, jobsData] = await Promise.all([
          employerApi.getMe(),
          employerApi.getDashboard(),
          employerApi.listInterviews({ limit: 5 }),
          employerApi.listJobs(),
        ])

        setEmployer(employerData)
        setStats(statsData)
        setRecentInterviews(interviewsData.interviews)
        setJobs(jobsData.jobs)
      } catch (err) {
        console.error('Failed to load dashboard:', err)
        if (err instanceof Error && err.message.includes('401')) {
          localStorage.removeItem('employer_token')
          router.push('/login')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadInitialData()
  }, [router])

  // Load interviews when tab changes to interviews
  const loadInterviews = useCallback(async () => {
    setInterviewsLoading(true)
    try {
      const data = await employerApi.listInterviews({
        jobId: selectedJob || undefined,
        status: statusFilter || undefined,
        minScore: minScoreFilter ? parseFloat(minScoreFilter) : undefined,
        limit: 50,
      })
      setInterviews(data.interviews)
      setInterviewsTotal(data.total)
    } catch (err) {
      console.error('Failed to load interviews:', err)
    } finally {
      setInterviewsLoading(false)
    }
  }, [selectedJob, statusFilter, minScoreFilter])

  useEffect(() => {
    if (activeTab === 'interviews') {
      loadInterviews()
    }
  }, [activeTab, loadInterviews])

  // Load talent pool when tab changes
  const loadTalentPool = useCallback(async () => {
    setTalentLoading(true)
    try {
      const data = await talentPoolApi.browse({
        vertical: talentVertical || undefined,
        roleType: talentRole || undefined,
        minScore: talentMinScore || undefined,
        search: talentSearch || undefined,
        limit: 12,
      })
      setCandidates(data.candidates)
      setTalentTotal(data.total)
    } catch (err) {
      console.error('Failed to load talent pool:', err)
    } finally {
      setTalentLoading(false)
    }
  }, [talentVertical, talentRole, talentMinScore, talentSearch])

  useEffect(() => {
    if (activeTab === 'talent') {
      loadTalentPool()
    }
  }, [activeTab, loadTalentPool])

  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    router.push('/login')
  }

  // Jobs handlers
  const loadInvites = async (jobId: string) => {
    try {
      const data = await inviteApi.listTokens(jobId)
      setInvites(data.tokens)
    } catch (err) {
      console.error('Failed to load invites', err)
    }
  }

  const handleSelectJob = async (job: Job) => {
    setSelectedJobDetail(job)
    await loadInvites(job.id)
    setJobViewMode('detail')
  }

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSavingJob(true)
    setJobError(null)

    try {
      const requirements = jobFormData.requirements
        .split('\n')
        .map(r => r.trim())
        .filter(r => r.length > 0)

      await employerApi.createJob({
        title: jobFormData.title,
        description: jobFormData.description,
        requirements,
        location: jobFormData.location || undefined,
        salaryMin: jobFormData.salaryMin ? parseInt(jobFormData.salaryMin) : undefined,
        salaryMax: jobFormData.salaryMax ? parseInt(jobFormData.salaryMax) : undefined,
        vertical: jobFormData.vertical || undefined,
        roleType: jobFormData.roleType || undefined,
      })

      setJobFormData({
        title: '',
        description: '',
        requirements: '',
        location: '',
        salaryMin: '',
        salaryMax: '',
        vertical: '',
        roleType: '',
      })
      setJobViewMode('list')

      // Reload jobs
      const jobsData = await employerApi.listJobs()
      setJobs(jobsData.jobs)
    } catch (err) {
      setJobError(err instanceof Error ? err.message : 'Failed to create job')
    } finally {
      setIsSavingJob(false)
    }
  }

  const handleCreateInvite = async () => {
    if (!selectedJobDetail) return
    try {
      await inviteApi.createToken(selectedJobDetail.id, 0, 30)
      await loadInvites(selectedJobDetail.id)
    } catch (err) {
      setJobError(err instanceof Error ? err.message : 'Failed to create invite')
    }
  }

  const handleCopyLink = async (url: string, id: string) => {
    try {
      await navigator.clipboard.writeText(url)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch {
      // Fallback
    }
  }

  const handleVerticalChange = (vertical: string) => {
    setJobFormData({ ...jobFormData, vertical, roleType: '' })
  }

  const getVerticalLabel = (value: string) => {
    return VERTICALS.find(v => v.value === value)?.label || value
  }

  const getRoleTypeLabel = (vertical: string, roleType: string) => {
    return ROLE_TYPES[vertical]?.find(r => r.value === roleType)?.label || roleType
  }

  // Interview selection handlers
  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const toggleSelectAll = () => {
    if (selectedIds.size === interviews.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(interviews.map(i => i.id)))
    }
  }

  // Talent pool handlers
  const handleTalentSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setTalentSearch(talentSearchInput)
  }

  const handleTalentVerticalChange = (value: string) => {
    setTalentVertical(value as Vertical | '')
    setTalentRole('')
  }

  const availableTalentRoles = talentVertical ? ROLE_TYPES[talentVertical] || [] : []

  // Expandable row handlers
  const toggleExpand = async (candidate: TalentPoolCandidate) => {
    const id = candidate.profileId || candidate.candidateId

    if (expandedId === id) {
      setExpandedId(null)
      return
    }

    setExpandedId(id)

    if (!expandedData[id]) {
      setLoadingDetail(id)
      try {
        const detail = await talentPoolApi.getProfile(id)
        setExpandedData(prev => ({ ...prev, [id]: detail }))
      } catch (error) {
        console.error('Failed to load candidate details:', error)
      } finally {
        setLoadingDetail(null)
      }
    }
  }

  const openContactModal = (candidate: TalentPoolCandidate) => {
    setContactCandidate(candidate)
    setContactSubject(`Interview Opportunity at ${employer?.companyName || 'Our Company'}`)
    const roleDisplay = candidate.roleType ? (ROLE_NAMES[candidate.roleType] || candidate.roleType) : 'open'
    setContactMessage(`Dear ${candidate.candidateName},

We reviewed your profile on Pathway and were impressed by your qualifications for ${roleDisplay} positions.

We would like to discuss a potential opportunity with you. Would you be available for a conversation?

Best regards,
${employer?.companyName || 'Our Company'}`)
    setShowContactModal(true)
  }

  const sendContactEmail = async () => {
    if (!contactCandidate || !contactSubject.trim() || !contactMessage.trim()) return

    setIsSending(true)
    try {
      const contactId = contactCandidate.profileId || contactCandidate.candidateId
      await talentPoolApi.contactCandidate(contactId, {
        subject: contactSubject,
        body: contactMessage,
        messageType: 'interview_invite',
      })
      alert(`Message sent to ${contactCandidate.candidateName}!`)
      setShowContactModal(false)
      setContactCandidate(null)
      setContactSubject('')
      setContactMessage('')
    } catch (error) {
      console.error('Failed to send message:', error)
      alert('Failed to send message. Please try again.')
    } finally {
      setIsSending(false)
    }
  }

  // Resume preview handler
  const openResumePreview = (resumeUrl: string, candidateName: string) => {
    setResumePreviewUrl(resumeUrl)
    setResumePreviewName(candidateName)
    setShowResumeModal(true)
  }

  // Transcript preview handler
  const openTranscriptPreview = (detail: TalentProfileDetail, candidateName: string) => {
    setTranscriptData(detail)
    setTranscriptCandidateName(candidateName)
    setShowTranscriptModal(true)
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-400 text-sm">Loading...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-100 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="text-lg font-semibold text-stone-900">
            Pathway
          </Link>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-stone-100 rounded-full">
              <div className="w-5 h-5 bg-teal-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-xs">
                  {employer?.companyName?.charAt(0) || 'E'}
                </span>
              </div>
              <span className="text-sm text-stone-600">{employer?.companyName}</span>
            </div>
            <Button variant="ghost" size="sm" className="text-stone-500 hover:text-stone-900" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-stone-100">
        <div className="max-w-5xl mx-auto px-6">
          <div className="flex gap-1">
            {[
              { key: 'overview', label: 'Overview' },
              { key: 'interviews', label: 'Interviews' },
              { key: 'jobs', label: 'Jobs' },
              { key: 'talent', label: 'Talent Pool' },
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as TabType)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors duration-200 ${
                  activeTab === tab.key
                    ? 'border-stone-900 text-stone-900'
                    : 'border-transparent text-stone-500 hover:text-stone-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-5">
                  <p className="text-sm text-stone-500 mb-1">Total Interviews</p>
                  <div className="text-3xl font-semibold text-stone-800">{stats?.totalInterviews || 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-5">
                  <p className="text-sm text-stone-500 mb-1">Pending Review</p>
                  <div className="text-3xl font-semibold text-stone-800">{stats?.pendingReview || 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-5">
                  <p className="text-sm text-stone-500 mb-1">Shortlisted</p>
                  <div className="text-3xl font-semibold text-stone-800">{stats?.shortlisted || 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-5">
                  <p className="text-sm text-stone-500 mb-1">Avg. Score</p>
                  <div className="text-3xl font-semibold text-stone-800">
                    {stats?.averageScore ? stats.averageScore.toFixed(1) : '-'}
                    {stats?.averageScore && <span className="text-lg font-normal text-stone-400">/10</span>}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Interviews */}
            <Card>
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">Recent Interviews</CardTitle>
                    <CardDescription>Latest candidate submissions</CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setActiveTab('interviews')}
                    className="text-teal-600 hover:text-teal-700"
                  >
                    View all →
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {recentInterviews.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="w-12 h-12 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <p className="text-stone-500 text-sm">No interviews yet</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setActiveTab('jobs')}
                      className="mt-3"
                    >
                      Create a Job
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {recentInterviews.map((interview) => (
                      <CandidateCard
                        key={interview.id}
                        name={interview.candidateName || 'Unknown'}
                        email={interview.candidateId}
                        score={interview.totalScore}
                        onClick={() => router.push(`/dashboard/interviews/${interview.id}`)}
                      />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid sm:grid-cols-3 gap-4">
              <button
                onClick={() => setActiveTab('interviews')}
                className="p-5 bg-white rounded-xl border border-stone-200 hover:border-stone-300 text-left transition-all hover:shadow-sm"
              >
                <div className="w-10 h-10 bg-stone-100 rounded-lg flex items-center justify-center mb-3">
                  <svg className="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="font-medium text-stone-900 text-sm">All Interviews</p>
                <p className="text-xs text-stone-500 mt-0.5">View and manage submissions</p>
              </button>
              <button
                onClick={() => setActiveTab('jobs')}
                className="p-5 bg-white rounded-xl border border-stone-200 hover:border-stone-300 text-left transition-all hover:shadow-sm"
              >
                <div className="w-10 h-10 bg-stone-100 rounded-lg flex items-center justify-center mb-3">
                  <svg className="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <p className="font-medium text-stone-900 text-sm">Job Postings</p>
                <p className="text-xs text-stone-500 mt-0.5">Create and manage jobs</p>
              </button>
              <button
                onClick={() => setActiveTab('talent')}
                className="p-5 bg-white rounded-xl border border-stone-200 hover:border-stone-300 text-left transition-all hover:shadow-sm"
              >
                <div className="w-10 h-10 bg-stone-100 rounded-lg flex items-center justify-center mb-3">
                  <svg className="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <p className="font-medium text-stone-900 text-sm">Talent Pool</p>
                <p className="text-xs text-stone-500 mt-0.5">Browse pre-interviewed candidates</p>
              </button>
            </div>
          </div>
        )}

        {/* Interviews Tab */}
        {activeTab === 'interviews' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-stone-900">All Interviews</h2>
                <p className="text-sm text-stone-500">{interviewsTotal} total interviews</p>
              </div>
            </div>

            {/* Filters */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-4 items-end">
                  <div className="w-40">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Job</Label>
                    <select
                      value={selectedJob}
                      onChange={(e) => setSelectedJob(e.target.value)}
                      className="w-full h-9 px-3 rounded-lg border border-stone-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="">All Jobs</option>
                      {jobs.map((job) => (
                        <option key={job.id} value={job.id}>{job.title}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-40">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Status</Label>
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                      className="w-full h-9 px-3 rounded-lg border border-stone-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="">All Statuses</option>
                      <option value="PENDING">Pending</option>
                      <option value="IN_PROGRESS">In Progress</option>
                      <option value="COMPLETED">Completed</option>
                    </select>
                  </div>
                  <div className="w-24">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Min Score</Label>
                    <Input
                      type="number"
                      min="0"
                      max="10"
                      step="0.5"
                      value={minScoreFilter}
                      onChange={(e) => setMinScoreFilter(e.target.value)}
                      placeholder="0-10"
                      className="h-9"
                    />
                  </div>
                  <Button onClick={loadInterviews} size="sm" className="bg-teal-600 hover:bg-teal-700">
                    Apply
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Interview List */}
            {interviewsLoading ? (
              <div className="text-center py-12">
                <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto" />
              </div>
            ) : interviews.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-stone-500">No interviews found</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {/* Select All */}
                <div className="flex items-center gap-3 px-2">
                  <input
                    type="checkbox"
                    checked={selectedIds.size === interviews.length && interviews.length > 0}
                    onChange={toggleSelectAll}
                    className="w-4 h-4 rounded border-stone-300 text-teal-600 focus:ring-teal-500"
                  />
                  <span className="text-sm text-stone-500">Select all</span>
                </div>

                {interviews.map((interview) => (
                  <div
                    key={interview.id}
                    className={`bg-white rounded-xl border p-4 transition-all cursor-pointer ${
                      selectedIds.has(interview.id)
                        ? 'border-teal-400 bg-teal-50/30'
                        : 'border-stone-200 hover:border-stone-300 hover:shadow-sm'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(interview.id)}
                        onChange={() => toggleSelect(interview.id)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-4 h-4 rounded border-stone-300 text-teal-600 focus:ring-teal-500"
                      />
                      <div
                        className="flex-1 flex items-center justify-between"
                        onClick={() => router.push(`/dashboard/interviews/${interview.id}`)}
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center">
                            <span className="text-teal-700 font-semibold">
                              {(interview.candidateName || 'U').charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-stone-900">{interview.candidateName || 'Unknown'}</p>
                            <p className="text-xs text-stone-500">
                              {interview.jobTitle} • {new Date(interview.createdAt).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            interview.status === 'COMPLETED' ? 'bg-teal-100 text-teal-700' :
                            interview.status === 'IN_PROGRESS' ? 'bg-amber-100 text-amber-700' :
                            'bg-stone-100 text-stone-600'
                          }`}>
                            {interview.status === 'COMPLETED' ? 'Done' :
                             interview.status === 'IN_PROGRESS' ? 'In Progress' : 'Pending'}
                          </span>
                          {interview.totalScore && (
                            <div className="text-right">
                              <span className="text-xl font-semibold text-teal-600">{interview.totalScore.toFixed(1)}</span>
                              <span className="text-xs text-stone-400">/10</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Jobs Tab */}
        {activeTab === 'jobs' && (
          <div className="space-y-6">
            {jobViewMode === 'list' && (
              <>
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-stone-900">Job Postings</h2>
                    <p className="text-sm text-stone-500">{jobs.length} job{jobs.length !== 1 ? 's' : ''} posted</p>
                  </div>
                  <Button onClick={() => setJobViewMode('create')} className="bg-teal-600 hover:bg-teal-700">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Job
                  </Button>
                </div>

                {jobs.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <div className="w-12 h-12 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <svg className="w-6 h-6 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <p className="text-stone-500">No jobs yet</p>
                      <Button onClick={() => setJobViewMode('create')} className="mt-3">Create Job</Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-3">
                    {jobs.map((job) => (
                      <div
                        key={job.id}
                        onClick={() => handleSelectJob(job)}
                        className="bg-white border border-stone-200 rounded-xl p-5 hover:border-stone-300 hover:shadow-sm transition-all cursor-pointer"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold text-stone-900">{job.title}</h3>
                              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                                job.isActive ? 'bg-teal-100 text-teal-700' : 'bg-stone-100 text-stone-600'
                              }`}>
                                {job.isActive ? 'Active' : 'Inactive'}
                              </span>
                            </div>
                            <p className="text-sm text-stone-500 line-clamp-1">{job.description}</p>
                            <div className="flex items-center gap-3 mt-2 text-xs text-stone-400">
                              {job.vertical && <span className="px-2 py-0.5 bg-stone-100 rounded">{getVerticalLabel(job.vertical)}</span>}
                              {job.location && <span>{job.location}</span>}
                            </div>
                          </div>
                          <svg className="w-5 h-5 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            {jobViewMode === 'create' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-stone-900">Create New Job</h2>
                  <Button variant="outline" onClick={() => setJobViewMode('list')}>Cancel</Button>
                </div>

                <form onSubmit={handleCreateJob} className="space-y-6">
                  {/* Vertical Selection */}
                  <div>
                    <Label className="text-sm font-medium">Industry Vertical *</Label>
                    <div className="grid sm:grid-cols-2 gap-3 mt-2">
                      {VERTICALS.map((v) => (
                        <button
                          key={v.value}
                          type="button"
                          onClick={() => handleVerticalChange(v.value)}
                          className={`p-4 rounded-xl border-2 text-left transition-all ${
                            jobFormData.vertical === v.value
                              ? 'border-teal-500 bg-teal-50'
                              : 'border-stone-200 hover:border-stone-300'
                          }`}
                        >
                          <div className="font-medium text-stone-900">{v.label}</div>
                          <div className="text-sm text-stone-500">{v.description}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Role Type */}
                  {jobFormData.vertical && ROLE_TYPES[jobFormData.vertical] && (
                    <div>
                      <Label className="text-sm font-medium">Role Type *</Label>
                      <div className="grid sm:grid-cols-3 gap-2 mt-2">
                        {ROLE_TYPES[jobFormData.vertical].map((r) => (
                          <button
                            key={r.value}
                            type="button"
                            onClick={() => setJobFormData({ ...jobFormData, roleType: r.value })}
                            className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                              jobFormData.roleType === r.value
                                ? 'border-teal-500 bg-teal-50 text-teal-700'
                                : 'border-stone-200 text-stone-700 hover:border-stone-300'
                            }`}
                          >
                            {r.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <div>
                    <Label htmlFor="title">Job Title *</Label>
                    <Input
                      id="title"
                      value={jobFormData.title}
                      onChange={(e) => setJobFormData({ ...jobFormData, title: e.target.value })}
                      placeholder="e.g. Software Engineer Intern"
                      className="mt-1.5"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="description">Description *</Label>
                    <textarea
                      id="description"
                      value={jobFormData.description}
                      onChange={(e) => setJobFormData({ ...jobFormData, description: e.target.value })}
                      placeholder="Describe the role..."
                      className="mt-1.5 w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[100px] resize-y"
                      required
                    />
                  </div>

                  <div className="grid sm:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="location">Location</Label>
                      <Input
                        id="location"
                        value={jobFormData.location}
                        onChange={(e) => setJobFormData({ ...jobFormData, location: e.target.value })}
                        placeholder="e.g. San Francisco"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="salaryMin">Min Salary ($/year)</Label>
                      <Input
                        id="salaryMin"
                        type="number"
                        value={jobFormData.salaryMin}
                        onChange={(e) => setJobFormData({ ...jobFormData, salaryMin: e.target.value })}
                        placeholder="60000"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="salaryMax">Max Salary ($/year)</Label>
                      <Input
                        id="salaryMax"
                        type="number"
                        value={jobFormData.salaryMax}
                        onChange={(e) => setJobFormData({ ...jobFormData, salaryMax: e.target.value })}
                        placeholder="120000"
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  {jobError && <p className="text-sm text-red-500">{jobError}</p>}

                  <div className="flex justify-end gap-3 pt-4 border-t">
                    <Button type="button" variant="outline" onClick={() => setJobViewMode('list')}>Cancel</Button>
                    <Button
                      type="submit"
                      disabled={isSavingJob || !jobFormData.vertical || !jobFormData.roleType || !jobFormData.title}
                      className="bg-teal-600 hover:bg-teal-700"
                    >
                      {isSavingJob ? 'Creating...' : 'Create Job'}
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {jobViewMode === 'detail' && selectedJobDetail && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-stone-900">{selectedJobDetail.title}</h2>
                  <Button variant="outline" onClick={() => { setJobViewMode('list'); setSelectedJobDetail(null); }}>
                    ← Back
                  </Button>
                </div>

                <Card>
                  <CardContent className="p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        selectedJobDetail.isActive ? 'bg-teal-100 text-teal-700' : 'bg-stone-100 text-stone-600'
                      }`}>
                        {selectedJobDetail.isActive ? 'Active' : 'Inactive'}
                      </span>
                      {selectedJobDetail.vertical && (
                        <span className="px-2 py-0.5 text-xs bg-stone-100 text-stone-600 rounded-full">
                          {getVerticalLabel(selectedJobDetail.vertical)}
                        </span>
                      )}
                    </div>
                    <p className="text-stone-600">{selectedJobDetail.description}</p>
                  </CardContent>
                </Card>

                {/* Invite Links */}
                <Card>
                  <CardHeader>
                    <div className="flex justify-between items-center">
                      <div>
                        <CardTitle className="text-base">Interview Links</CardTitle>
                        <CardDescription>Share with candidates</CardDescription>
                      </div>
                      <Button onClick={handleCreateInvite} size="sm" className="bg-teal-600 hover:bg-teal-700">
                        New Link
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {invites.length === 0 ? (
                      <p className="text-sm text-stone-400 text-center py-4">No invite links yet</p>
                    ) : (
                      <div className="space-y-2">
                        {invites.map((invite) => (
                          <div key={invite.id} className="flex items-center gap-3 p-3 bg-stone-50 rounded-lg">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-mono text-stone-600 truncate">{invite.inviteUrl}</p>
                              <p className="text-xs text-stone-400 mt-0.5">
                                Used: {invite.usedCount}/{invite.maxUses || '∞'}
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCopyLink(invite.inviteUrl, invite.id)}
                            >
                              {copiedId === invite.id ? '✓ Copied' : 'Copy'}
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}

        {/* Talent Pool Tab */}
        {activeTab === 'talent' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-stone-900">Talent Pool</h2>
                <p className="text-sm text-stone-500">Browse candidates with resumes, GitHub profiles, and interview scores</p>
              </div>
            </div>

            {/* Search and Filters */}
            <Card>
              <CardContent className="p-4">
                {/* Search Bar */}
                <form onSubmit={handleTalentSearch} className="mb-4">
                  <div className="flex gap-2">
                    <div className="flex-1 relative">
                      <Input
                        type="text"
                        value={talentSearchInput}
                        onChange={(e) => setTalentSearchInput(e.target.value)}
                        placeholder="Search by name, skills, company, keywords..."
                        className="pl-10"
                      />
                      <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <Button type="submit" className="bg-teal-600 hover:bg-teal-700">Search</Button>
                  </div>
                </form>

                <div className="flex flex-wrap gap-4 items-end">
                  <div className="w-44">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Industry Vertical</Label>
                    <select
                      value={talentVertical}
                      onChange={(e) => handleTalentVerticalChange(e.target.value)}
                      className="w-full h-9 px-3 rounded-lg border border-stone-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="">All Verticals</option>
                      {VERTICALS.map((v) => (
                        <option key={v.value} value={v.value}>{v.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-40">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Role Type</Label>
                    <select
                      value={talentRole}
                      onChange={(e) => setTalentRole(e.target.value as RoleType | '')}
                      disabled={!talentVertical}
                      className="w-full h-9 px-3 rounded-lg border border-stone-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 disabled:bg-stone-50"
                    >
                      <option value="">All Roles</option>
                      {availableTalentRoles.map((r) => (
                        <option key={r.value} value={r.value}>{r.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-32">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Min Score</Label>
                    <select
                      value={talentMinScore}
                      onChange={(e) => setTalentMinScore(Number(e.target.value))}
                      className="w-full h-9 px-3 rounded-lg border border-stone-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value={0}>Any Score</option>
                      <option value={5}>5+ / 10</option>
                      <option value={6}>6+ / 10</option>
                      <option value={7}>7+ / 10</option>
                      <option value={8}>8+ / 10</option>
                    </select>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setTalentVertical('')
                      setTalentRole('')
                      setTalentMinScore(0)
                      setTalentSearchInput('')
                      setTalentSearch('')
                    }}
                  >
                    Clear All
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Results Count */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-stone-500">{talentTotal} candidate{talentTotal !== 1 ? 's' : ''} found</p>
            </div>

            {/* Candidates List - Expandable Rows */}
            {talentLoading ? (
              <div className="text-center py-12">
                <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto" />
              </div>
            ) : candidates.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <div className="w-12 h-12 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <h3 className="font-medium text-stone-900 mb-1">No candidates found</h3>
                  <p className="text-sm text-stone-500">Try adjusting your filters or check back later</p>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <div className="divide-y divide-stone-100">
                  {candidates.map((candidate) => {
                    const displayScore = candidate.bestScore ?? candidate.profileScore
                    const isProfileOnly = candidate.status === 'profile_only' || candidate.status === 'pending' || candidate.status === 'in_progress'
                    const rowId = candidate.profileId || candidate.candidateId
                    const isExpanded = expandedId === rowId
                    const detail = expandedData[rowId]

                    return (
                      <div key={rowId}>
                        {/* Main Row */}
                        <div
                          className={`p-4 cursor-pointer transition-colors ${isExpanded ? 'bg-teal-50' : 'hover:bg-stone-50'}`}
                          onClick={() => toggleExpand(candidate)}
                        >
                          <div className="flex items-center gap-4">
                            {/* Expand/Collapse Icon */}
                            <div className="flex-shrink-0 w-6">
                              <svg
                                className={`w-5 h-5 text-stone-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                              </svg>
                            </div>

                            {/* Avatar */}
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center flex-shrink-0">
                              <span className="text-sm font-semibold text-white">
                                {(candidate.candidateName || 'U').charAt(0).toUpperCase()}
                              </span>
                            </div>

                            {/* Main Info */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <h3 className="font-medium text-stone-900 truncate">{candidate.candidateName}</h3>
                                {candidate.completionStatus?.resumeUploaded && (
                                  <span className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">Resume</span>
                                )}
                                {candidate.completionStatus?.githubConnected && (
                                  <span className="px-1.5 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">GitHub</span>
                                )}
                                {candidate.completionStatus?.interviewCompleted ? (
                                  <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                    Interview
                                  </span>
                                ) : (
                                  <span className="px-1.5 py-0.5 text-xs bg-amber-100 text-amber-700 rounded-full">No Interview</span>
                                )}
                              </div>
                              <div className="flex items-center gap-3 mt-0.5">
                                {candidate.vertical && (
                                  <span className="text-xs text-stone-600">
                                    {VERTICALS.find(v => v.value === candidate.vertical)?.label || candidate.vertical}
                                  </span>
                                )}
                                {candidate.roleType && (
                                  <span className="text-xs text-stone-500">
                                    {ROLE_NAMES[candidate.roleType] || candidate.roleType}
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Skills */}
                            <div className="hidden md:flex flex-wrap gap-1 max-w-xs">
                              {candidate.skills.slice(0, 3).map((skill, i) => (
                                <span key={i} className="px-2 py-0.5 text-xs bg-stone-100 text-stone-600 rounded">
                                  {skill}
                                </span>
                              ))}
                              {candidate.skills.length > 3 && (
                                <span className="text-xs text-stone-400">+{candidate.skills.length - 3}</span>
                              )}
                            </div>

                            {/* Score */}
                            <div className="text-center w-16 flex-shrink-0">
                              {displayScore ? (
                                <>
                                  <div className={`text-lg font-bold ${isProfileOnly ? 'text-blue-600' : 'text-teal-600'}`}>
                                    {displayScore.toFixed(1)}
                                  </div>
                                  <div className="text-xs text-stone-400">
                                    {isProfileOnly ? 'profile' : 'score'}
                                  </div>
                                </>
                              ) : (
                                <div className="text-xs text-stone-400">-</div>
                              )}
                            </div>

                            {/* Contact Button */}
                            <div className="flex-shrink-0">
                              <Button
                                size="sm"
                                className="bg-teal-600 hover:bg-teal-700"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  openContactModal(candidate)
                                }}
                              >
                                Contact
                              </Button>
                            </div>
                          </div>
                        </div>

                        {/* Expanded Details Panel */}
                        {isExpanded && (
                          <div className="bg-stone-50 border-t border-stone-100 px-4 py-4">
                            {loadingDetail === rowId ? (
                              <div className="flex items-center justify-center py-8">
                                <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-500 rounded-full animate-spin"></div>
                              </div>
                            ) : detail ? (
                              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                {/* Left: Contact & Basic Info */}
                                <div className="space-y-4">
                                  <div>
                                    <h4 className="text-sm font-semibold text-stone-700 mb-2">Contact Info</h4>
                                    <div className="space-y-1 text-sm">
                                      <p><span className="text-stone-500">Email:</span> {detail.candidate.email}</p>
                                      {detail.candidate.phone && (
                                        <p><span className="text-stone-500">Phone:</span> {detail.candidate.phone}</p>
                                      )}
                                      {detail.candidate.university && (
                                        <p><span className="text-stone-500">University:</span> {detail.candidate.university}</p>
                                      )}
                                      {detail.candidate.major && (
                                        <p><span className="text-stone-500">Major:</span> {detail.candidate.major}</p>
                                      )}
                                      {detail.candidate.graduationYear && (
                                        <p><span className="text-stone-500">Graduation:</span> {detail.candidate.graduationYear}</p>
                                      )}
                                      {detail.candidate.gpa && (
                                        <p><span className="text-stone-500">GPA:</span> {detail.candidate.gpa.toFixed(2)}</p>
                                      )}
                                    </div>
                                  </div>

                                  {/* Score Breakdown */}
                                  {detail.profileScore?.breakdown && (
                                    <div>
                                      <h4 className="text-sm font-semibold text-stone-700 mb-2">Score Breakdown</h4>
                                      <div className="space-y-1">
                                        {Object.entries(detail.profileScore.breakdown).map(([key, value]) => {
                                          const label = key
                                            .replace(/([A-Z])/g, ' $1')
                                            .replace(/^./, str => str.toUpperCase())
                                            .trim()
                                          return (
                                            <div key={key} className="flex items-center gap-2">
                                              <span className="text-xs text-stone-500 w-28">{label}</span>
                                              <div className="flex-1 h-2 bg-stone-200 rounded-full">
                                                <div
                                                  className="h-2 bg-teal-500 rounded-full"
                                                  style={{ width: `${((value as number) / 10) * 100}%` }}
                                                />
                                              </div>
                                              <span className="text-xs font-medium w-8">{(value as number).toFixed(1)}</span>
                                            </div>
                                          )
                                        })}
                                      </div>
                                    </div>
                                  )}

                                  {/* Strengths & Areas to Explore - check interview first, then profileScore */}
                                  {(() => {
                                    // Prefer interview assessment over profile assessment
                                    const strengths = detail.interview?.overallStrengths?.length
                                      ? detail.interview.overallStrengths
                                      : detail.profileScore?.strengths || []
                                    const concerns = detail.interview?.overallConcerns?.length
                                      ? detail.interview.overallConcerns
                                      : detail.profileScore?.concerns || []
                                    const hasAssessment = strengths.length > 0 || concerns.length > 0
                                    const isFromInterview = detail.interview?.overallStrengths?.length || detail.interview?.overallConcerns?.length

                                    return hasAssessment ? (
                                      <div>
                                        <h4 className="text-sm font-semibold text-stone-700 mb-2">
                                          Assessment
                                          {isFromInterview && <span className="text-xs font-normal text-stone-400 ml-1">(Interview)</span>}
                                        </h4>
                                        <div className="space-y-2">
                                          {strengths.length > 0 && (
                                            <div>
                                              <p className="text-xs font-medium text-green-700 mb-1">Strengths</p>
                                              <ul className="space-y-0.5">
                                                {strengths.slice(0, 3).map((s, i) => (
                                                  <li key={i} className="text-xs text-stone-600 flex items-start gap-1">
                                                    <span className="text-green-500 mt-0.5">+</span>
                                                    <span>{s}</span>
                                                  </li>
                                                ))}
                                              </ul>
                                            </div>
                                          )}
                                          {concerns.length > 0 && (
                                            <div>
                                              <p className="text-xs font-medium text-amber-700 mb-1">Areas to Explore</p>
                                              <ul className="space-y-0.5">
                                                {concerns.slice(0, 3).map((c, i) => (
                                                  <li key={i} className="text-xs text-stone-600 flex items-start gap-1">
                                                    <span className="text-amber-500 mt-0.5">•</span>
                                                    <span>{c}</span>
                                                  </li>
                                                ))}
                                              </ul>
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    ) : null
                                  })()}
                                </div>

                                {/* Middle: Skills & Experience */}
                                <div className="space-y-4">
                                  {detail.candidate.resumeData?.skills && detail.candidate.resumeData.skills.length > 0 && (
                                    <div>
                                      <h4 className="text-sm font-semibold text-stone-700 mb-2">Skills</h4>
                                      <div className="flex flex-wrap gap-1">
                                        {detail.candidate.resumeData.skills.slice(0, 15).map((skill, i) => (
                                          <span key={i} className="px-2 py-1 text-xs bg-white border border-stone-200 text-stone-700 rounded">
                                            {skill}
                                          </span>
                                        ))}
                                        {detail.candidate.resumeData.skills.length > 15 && (
                                          <span className="text-xs text-stone-400">+{detail.candidate.resumeData.skills.length - 15} more</span>
                                        )}
                                      </div>
                                    </div>
                                  )}

                                  {detail.candidate.resumeData?.experience && detail.candidate.resumeData.experience.length > 0 && (
                                    <div>
                                      <h4 className="text-sm font-semibold text-stone-700 mb-2">Experience</h4>
                                      <div className="space-y-2">
                                        {detail.candidate.resumeData.experience.slice(0, 2).map((exp, i) => (
                                          <div key={i} className="text-sm">
                                            <p className="font-medium text-stone-900">{exp.title}</p>
                                            <p className="text-stone-500">{exp.company}</p>
                                            {exp.startDate && (
                                              <p className="text-xs text-stone-400">
                                                {exp.startDate} - {exp.endDate || 'Present'}
                                              </p>
                                            )}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>

                                {/* Right: GitHub & Projects */}
                                <div className="space-y-4">
                                  {detail.candidate.githubUsername && (
                                    <div>
                                      <h4 className="text-sm font-semibold text-stone-700 mb-2">GitHub</h4>
                                      <a
                                        href={`https://github.com/${detail.candidate.githubUsername}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-2 text-sm text-teal-600 hover:text-teal-700"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                        </svg>
                                        @{detail.candidate.githubUsername}
                                      </a>
                                      {detail.candidate.githubData && (
                                        <div className="mt-2 text-xs text-stone-500">
                                          <p>{detail.candidate.githubData.publicRepos} repos • {detail.candidate.githubData.followers} followers</p>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  {detail.candidate.resumeData?.projects && detail.candidate.resumeData.projects.length > 0 && (
                                    <div>
                                      <h4 className="text-sm font-semibold text-stone-700 mb-2">Projects</h4>
                                      <div className="space-y-2">
                                        {detail.candidate.resumeData.projects.slice(0, 2).map((project, i) => (
                                          <div key={i} className="text-sm">
                                            <p className="font-medium text-stone-900">{project.name}</p>
                                            {project.description && (
                                              <p className="text-stone-500 text-xs line-clamp-2">{project.description}</p>
                                            )}
                                            {project.technologies && project.technologies.length > 0 && (
                                              <div className="flex flex-wrap gap-1 mt-1">
                                                {project.technologies.slice(0, 4).map((tech, j) => (
                                                  <span key={j} className="px-1.5 py-0.5 text-xs bg-stone-100 text-stone-600 rounded">
                                                    {tech}
                                                  </span>
                                                ))}
                                              </div>
                                            )}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                  {/* Documents Section */}
                                  <div className="pt-3 border-t border-stone-200">
                                    <h4 className="text-sm font-semibold text-stone-700 mb-3">Documents</h4>
                                    <div className="space-y-2">
                                      {/* Resume */}
                                      {detail.candidate.resumeUrl && (
                                        <div className="flex items-center justify-between p-2 bg-white border border-stone-200 rounded-lg">
                                          <div className="flex items-center gap-2">
                                            <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                                              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h6v6h6v10H6z"/>
                                            </svg>
                                            <span className="text-sm text-stone-700">Resume</span>
                                          </div>
                                          <div className="flex items-center gap-1">
                                            <button
                                              onClick={(e) => {
                                                e.stopPropagation()
                                                openResumePreview(detail.candidate.resumeUrl!, candidate.candidateName || 'Candidate')
                                              }}
                                              className="px-2 py-1 text-xs font-medium text-teal-600 hover:bg-teal-50 rounded transition-colors"
                                            >
                                              Preview
                                            </button>
                                            <a
                                              href={detail.candidate.resumeUrl}
                                              target="_blank"
                                              rel="noopener noreferrer"
                                              onClick={(e) => e.stopPropagation()}
                                              className="px-2 py-1 text-xs font-medium text-stone-600 hover:bg-stone-100 rounded transition-colors"
                                            >
                                              Download
                                            </a>
                                          </div>
                                        </div>
                                      )}

                                      {/* Transcript */}
                                      {detail.interview && detail.interview.responses && detail.interview.responses.length > 0 && (
                                        <div className="flex items-center justify-between p-2 bg-white border border-stone-200 rounded-lg">
                                          <div className="flex items-center gap-2">
                                            <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                            <span className="text-sm text-stone-700">Interview Transcript</span>
                                            <span className="text-xs text-stone-400">({detail.interview.responses.length} response{detail.interview.responses.length > 1 ? 's' : ''})</span>
                                          </div>
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation()
                                              openTranscriptPreview(detail, candidate.candidateName || 'Candidate')
                                            }}
                                            className="px-2 py-1 text-xs font-medium text-teal-600 hover:bg-teal-50 rounded transition-colors"
                                          >
                                            Preview
                                          </button>
                                        </div>
                                      )}

                                      {!detail.candidate.resumeUrl && (!detail.interview || !detail.interview.responses || detail.interview.responses.length === 0) && (
                                        <p className="text-xs text-stone-400 italic">No documents available</p>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ) : (
                              <p className="text-sm text-stone-500 text-center py-4">Failed to load details</p>
                            )}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </Card>
            )}
          </div>
        )}
      </div>

      {/* Contact Modal */}
      {showContactModal && contactCandidate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Contact {contactCandidate.candidateName}</span>
                <button
                  onClick={() => setShowContactModal(false)}
                  className="text-stone-400 hover:text-stone-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </CardTitle>
              <CardDescription>
                Send an email to {contactCandidate.candidateEmail}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium text-stone-700 mb-1 block">Subject</Label>
                <Input
                  type="text"
                  value={contactSubject}
                  onChange={(e) => setContactSubject(e.target.value)}
                  placeholder="Email subject..."
                />
              </div>
              <div>
                <Label className="text-sm font-medium text-stone-700 mb-1 block">Message</Label>
                <textarea
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none text-sm"
                  placeholder="Write your message..."
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowContactModal(false)}
                  disabled={isSending}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-teal-600 hover:bg-teal-700"
                  onClick={sendContactEmail}
                  disabled={isSending || !contactSubject.trim() || !contactMessage.trim()}
                >
                  {isSending ? 'Sending...' : 'Send Email'}
                </Button>
              </div>
              <p className="text-xs text-stone-500 text-center">
                The candidate will receive this email and their status will be updated to "Contacted"
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Resume Preview Modal */}
      {showResumeModal && resumePreviewUrl && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-4xl h-[90vh] bg-white rounded-xl shadow-2xl flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200">
              <div className="flex items-center gap-3">
                <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h6v6h6v10H6z"/>
                </svg>
                <h3 className="text-lg font-semibold text-stone-900">{resumePreviewName}&apos;s Resume</h3>
              </div>
              <div className="flex items-center gap-2">
                <a
                  href={resumePreviewUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-stone-700 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download
                </a>
                <button
                  onClick={() => setShowResumeModal(false)}
                  className="p-2 text-stone-400 hover:text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            {/* PDF Viewer - Use Google Docs Viewer for cross-origin PDFs */}
            <div className="flex-1 overflow-hidden bg-stone-100">
              <iframe
                src={`https://docs.google.com/viewer?url=${encodeURIComponent(resumePreviewUrl)}&embedded=true`}
                className="w-full h-full border-0"
                title="Resume Preview"
              />
            </div>
            {/* Fallback message */}
            <div className="px-6 py-3 bg-stone-50 border-t border-stone-200 text-center">
              <p className="text-xs text-stone-500">
                If the preview doesn&apos;t load, <a href={resumePreviewUrl} target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:underline">click here to open in a new tab</a>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Transcript Preview Modal */}
      {showTranscriptModal && transcriptData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-4xl max-h-[90vh] bg-white rounded-xl shadow-2xl flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200">
              <div className="flex items-center gap-3">
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-semibold text-stone-900">{transcriptCandidateName}&apos;s Interview Transcript</h3>
              </div>
              <button
                onClick={() => setShowTranscriptModal(false)}
                className="p-2 text-stone-400 hover:text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {/* Transcript Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {transcriptData.interview && transcriptData.interview.responses && transcriptData.interview.responses.length > 0 ? (
                <div className="space-y-6">
                  <div className="border border-stone-200 rounded-xl overflow-hidden">
                    {/* Interview Header */}
                    <div className="bg-stone-50 px-4 py-3 border-b border-stone-200">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-stone-900">Interview Session</h4>
                          <p className="text-sm text-stone-500">
                            {transcriptData.interview.completedAt ? new Date(transcriptData.interview.completedAt).toLocaleDateString() : 'Date unknown'} • Score: {transcriptData.interview.totalScore?.toFixed(1) || '-'}/10
                          </p>
                        </div>
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                          Completed
                        </span>
                      </div>
                    </div>

                    {/* AI Summary */}
                    {transcriptData.interview.aiSummary && (
                      <div className="px-4 py-3 bg-teal-50 border-b border-stone-200">
                        <h5 className="text-sm font-medium text-teal-800 mb-1">AI Summary</h5>
                        <p className="text-sm text-teal-700">{transcriptData.interview.aiSummary}</p>
                      </div>
                    )}

                    {/* Interview Assessment - Strengths & Concerns */}
                    {(transcriptData.interview.overallStrengths?.length || transcriptData.interview.overallConcerns?.length) ? (
                      <div className="px-4 py-3 bg-stone-50 border-b border-stone-200">
                        <h5 className="text-sm font-medium text-stone-800 mb-2">Interview Assessment</h5>
                        <div className="grid grid-cols-2 gap-4">
                          {transcriptData.interview.overallStrengths && transcriptData.interview.overallStrengths.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-green-700 mb-1">Strengths</p>
                              <ul className="space-y-1">
                                {transcriptData.interview.overallStrengths.map((s, i) => (
                                  <li key={i} className="text-xs text-stone-600 flex items-start gap-1">
                                    <span className="text-green-500 mt-0.5">+</span>
                                    <span>{s}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {transcriptData.interview.overallConcerns && transcriptData.interview.overallConcerns.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-amber-700 mb-1">Areas to Explore</p>
                              <ul className="space-y-1">
                                {transcriptData.interview.overallConcerns.map((c, i) => (
                                  <li key={i} className="text-xs text-stone-600 flex items-start gap-1">
                                    <span className="text-amber-500 mt-0.5">•</span>
                                    <span>{c}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : null}

                    {/* Responses */}
                    <div className="p-4 space-y-4">
                      {transcriptData.interview.responses.map((response, rIdx) => (
                        <div key={rIdx} className="border-l-2 border-teal-500 pl-4">
                          <p className="text-sm font-medium text-stone-900 mb-2">
                            Q{rIdx + 1}: {response.questionText}
                          </p>
                          {response.transcription ? (
                            <div className="bg-stone-50 rounded-lg p-3">
                              <p className="text-sm text-stone-600 whitespace-pre-wrap">
                                {response.transcription}
                              </p>
                            </div>
                          ) : (
                            <p className="text-sm text-stone-400 italic">No transcription available</p>
                          )}
                          {response.aiScore && (
                            <p className="text-xs text-stone-500 mt-2">
                              Response Score: <span className="font-medium text-teal-600">{response.aiScore.toFixed(1)}/10</span>
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <svg className="w-12 h-12 text-stone-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-stone-500">No interview transcripts available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  )
}

export default function EmployerDashboard() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin" />
      </main>
    }>
      <DashboardContent />
    </Suspense>
  )
}
