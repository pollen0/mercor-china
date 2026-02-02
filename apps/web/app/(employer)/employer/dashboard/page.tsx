'use client'

import { Suspense, useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { CandidateCard } from '@/components/dashboard/candidate-card'
import {
  employerApi,
  inviteApi,
  talentPoolApi,
  type Employer,
  type DashboardStats,
  type InterviewSession,
  type Job,
  type InviteTokenResponse,
  type TalentPoolCandidate,
  type Vertical,
  type RoleType,
} from '@/lib/api'

type TabType = 'overview' | 'jobs' | 'interviews' | 'talent'

// Vertical and Role definitions
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
  fullstack_engineer: 'Full-stack Engineer',
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

function EmployerDashboardContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const initialTab = (searchParams.get('tab') as TabType) || 'overview'

  const [activeTab, setActiveTab] = useState<TabType>(initialTab)
  const [employer, setEmployer] = useState<Employer | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Overview state
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentInterviews, setRecentInterviews] = useState<InterviewSession[]>([])

  // Jobs state
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [invites, setInvites] = useState<InviteTokenResponse[]>([])
  const [jobViewMode, setJobViewMode] = useState<'list' | 'create' | 'detail' | 'edit'>('list')
  const [jobFormData, setJobFormData] = useState({
    title: '', description: '', requirements: '', location: '',
    salaryMin: '', salaryMax: '', vertical: '', roleType: '',
  })
  const [isSaving, setIsSaving] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  // Interviews state
  const [interviews, setInterviews] = useState<InterviewSession[]>([])
  const [interviewsTotal, setInterviewsTotal] = useState(0)
  const [interviewJobFilter, setInterviewJobFilter] = useState('')
  const [interviewStatusFilter, setInterviewStatusFilter] = useState('')
  const [interviewMinScore, setInterviewMinScore] = useState('')

  // Talent pool state
  const [candidates, setCandidates] = useState<TalentPoolCandidate[]>([])
  const [talentTotal, setTalentTotal] = useState(0)
  const [talentVertical, setTalentVertical] = useState<Vertical | ''>('')
  const [talentRole, setTalentRole] = useState<RoleType | ''>('')
  const [talentMinScore, setTalentMinScore] = useState(0)
  const [talentSearch, setTalentSearch] = useState('')
  const [talentSearchInput, setTalentSearchInput] = useState('')
  const [talentPage, setTalentPage] = useState(1)
  const talentPageSize = 12

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/employer/login')
          return
        }

        const employerData = await employerApi.getMe()
        setEmployer(employerData)
        setIsLoading(false)
      } catch (err) {
        console.error('Failed to load employer:', err)
        if (err instanceof Error && err.message.includes('401')) {
          localStorage.removeItem('employer_token')
          router.push('/employer/login')
        }
        setIsLoading(false)
      }
    }

    loadInitialData()
  }, [router])

  // Load tab-specific data when tab changes
  useEffect(() => {
    if (!employer) return

    const loadTabData = async () => {
      switch (activeTab) {
        case 'overview':
          await loadOverviewData()
          break
        case 'jobs':
          await loadJobs()
          break
        case 'interviews':
          await loadInterviews()
          break
        case 'talent':
          await loadTalentPool()
          break
      }
    }

    loadTabData()
  }, [activeTab, employer])

  // Data loading functions
  const loadOverviewData = async () => {
    try {
      const [statsData, interviewsData] = await Promise.all([
        employerApi.getDashboard(),
        employerApi.listInterviews({ limit: 5 })
      ])
      setStats(statsData)
      setRecentInterviews(interviewsData.interviews)
    } catch (err) {
      console.error('Failed to load overview:', err)
    }
  }

  const loadJobs = async () => {
    try {
      const data = await employerApi.listJobs()
      setJobs(data.jobs)
    } catch (err) {
      console.error('Failed to load jobs:', err)
    }
  }

  const loadInvites = async (jobId: string) => {
    try {
      const data = await inviteApi.listTokens(jobId)
      setInvites(data.tokens)
    } catch (err) {
      console.error('Failed to load invites:', err)
    }
  }

  const loadInterviews = async () => {
    try {
      const [jobsData, interviewsData] = await Promise.all([
        employerApi.listJobs(),
        employerApi.listInterviews({
          jobId: interviewJobFilter || undefined,
          status: interviewStatusFilter || undefined,
          minScore: interviewMinScore ? parseFloat(interviewMinScore) : undefined,
          limit: 50,
        })
      ])
      setJobs(jobsData.jobs)
      setInterviews(interviewsData.interviews)
      setInterviewsTotal(interviewsData.total)
    } catch (err) {
      console.error('Failed to load interviews:', err)
    }
  }

  const loadTalentPool = async () => {
    try {
      const data = await talentPoolApi.browse({
        vertical: talentVertical || undefined,
        roleType: talentRole || undefined,
        minScore: talentMinScore || undefined,
        search: talentSearch || undefined,
        limit: talentPageSize,
        offset: (talentPage - 1) * talentPageSize,
      })
      setCandidates(data.candidates)
      setTalentTotal(data.total)
    } catch (err) {
      console.error('Failed to load talent pool:', err)
    }
  }

  // Handlers
  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    router.push('/employer/login')
  }

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    router.push(`/employer/dashboard?tab=${tab}`, { scroll: false })
  }

  // Job handlers
  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    try {
      await employerApi.createJob({
        title: jobFormData.title,
        description: jobFormData.description,
        requirements: jobFormData.requirements.split('\n').filter(r => r.trim()),
        location: jobFormData.location || undefined,
        salaryMin: jobFormData.salaryMin ? parseInt(jobFormData.salaryMin) : undefined,
        salaryMax: jobFormData.salaryMax ? parseInt(jobFormData.salaryMax) : undefined,
        vertical: jobFormData.vertical || undefined,
        roleType: jobFormData.roleType || undefined,
      })
      setJobFormData({ title: '', description: '', requirements: '', location: '', salaryMin: '', salaryMax: '', vertical: '', roleType: '' })
      setJobViewMode('list')
      loadJobs()
    } catch (err) {
      console.error('Failed to create job:', err)
    } finally {
      setIsSaving(false)
    }
  }

  const handleSelectJob = async (job: Job) => {
    setSelectedJob(job)
    await loadInvites(job.id)
    setJobViewMode('detail')
  }

  const handleCreateInvite = async () => {
    if (!selectedJob) return
    try {
      await inviteApi.createToken(selectedJob.id, 0, 30)
      await loadInvites(selectedJob.id)
    } catch (err) {
      console.error('Failed to create invite:', err)
    }
  }

  const handleCopyLink = async (url: string, id: string) => {
    await navigator.clipboard.writeText(url)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleDeleteInvite = async (inviteId: string) => {
    try {
      await inviteApi.deleteToken(inviteId)
      if (selectedJob) await loadInvites(selectedJob.id)
    } catch (err) {
      console.error('Failed to delete invite:', err)
    }
  }

  const getVerticalLabel = (v: string) => VERTICALS.find(x => x.value === v)?.label || v
  const getRoleLabel = (v: string, r: string) => ROLE_TYPES[v]?.find(x => x.value === r)?.label || r

  if (isLoading) {
    return (
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-gray-200 border-t-teal-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500 text-sm">Loading dashboard...</p>
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <DashboardNavbar companyName={employer?.companyName} onLogout={handleLogout} />

      <Container className="py-8 pt-24">
        {/* Tab Navigation */}
        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl mb-8 w-fit">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'jobs', label: 'Jobs', icon: '💼' },
            { id: 'interviews', label: 'Interviews', icon: '🎬' },
            { id: 'talent', label: 'Talent Pool', icon: '👥' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id as TabType)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-white shadow-sm text-gray-900'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span className="mr-1.5">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            <div className="mb-10">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                Welcome back, {employer?.companyName}
              </h1>
              <p className="text-gray-500">Here&apos;s an overview of your hiring activity</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
              <div className="bg-white rounded-2xl shadow-soft p-5">
                <p className="text-sm text-gray-500 mb-1">Total Interviews</p>
                <div className="text-3xl font-semibold text-gray-900">{stats?.totalInterviews || 0}</div>
              </div>
              <div className="bg-white rounded-2xl shadow-soft p-5">
                <p className="text-sm text-gray-500 mb-1">Pending Review</p>
                <div className="text-3xl font-semibold text-gray-900">{stats?.pendingReview || 0}</div>
              </div>
              <div className="bg-white rounded-2xl shadow-soft p-5">
                <p className="text-sm text-gray-500 mb-1">Shortlisted</p>
                <div className="text-3xl font-semibold text-gray-900">{stats?.shortlisted || 0}</div>
              </div>
              <div className="bg-white rounded-2xl shadow-soft p-5">
                <p className="text-sm text-gray-500 mb-1">Avg. Score</p>
                <div className="text-3xl font-semibold text-gray-900">
                  {stats?.averageScore ? stats.averageScore.toFixed(1) : '-'}
                  {stats?.averageScore && <span className="text-lg font-normal text-gray-400">/10</span>}
                </div>
              </div>
            </div>

            {/* Recent Interviews */}
            <div className="bg-white rounded-2xl shadow-soft overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-gray-900">Recent Interviews</h2>
                  <p className="text-sm text-gray-500">Latest candidate submissions</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => handleTabChange('interviews')}>
                  View all
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              </div>
              <div className="p-6">
                {recentInterviews.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500 mb-4">No interviews yet</p>
                    <Button variant="brand" size="sm" onClick={() => handleTabChange('jobs')}>
                      Create Job Posting
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {recentInterviews.map((interview) => (
                      <CandidateCard
                        key={interview.id}
                        name={interview.candidateName || 'Unknown'}
                        email={interview.candidateId}
                        score={interview.totalScore}
                        onClick={() => router.push(`/employer/dashboard/interviews/${interview.id}`)}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Jobs Tab */}
        {activeTab === 'jobs' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {jobViewMode === 'list' && 'Jobs'}
                  {jobViewMode === 'create' && 'Create New Job'}
                  {jobViewMode === 'detail' && selectedJob?.title}
                </h1>
                <p className="text-gray-500">
                  {jobViewMode === 'list' && `${jobs.length} job${jobs.length !== 1 ? 's' : ''} posted`}
                </p>
              </div>
              <div className="flex gap-3">
                {jobViewMode !== 'list' && (
                  <Button variant="outline" onClick={() => { setJobViewMode('list'); setSelectedJob(null) }}>
                    Back to Jobs
                  </Button>
                )}
                {jobViewMode === 'list' && (
                  <Button onClick={() => setJobViewMode('create')}>New Job</Button>
                )}
              </div>
            </div>

            {/* Job List */}
            {jobViewMode === 'list' && (
              <div className="space-y-4">
                {jobs.length === 0 ? (
                  <div className="text-center py-16 bg-gray-50 rounded-2xl border-2 border-dashed">
                    <p className="text-gray-500 mb-4">No jobs yet</p>
                    <Button onClick={() => setJobViewMode('create')}>Create Job</Button>
                  </div>
                ) : (
                  jobs.map((job) => (
                    <div
                      key={job.id}
                      onClick={() => handleSelectJob(job)}
                      className="bg-white border rounded-xl p-5 hover:shadow-md transition-all cursor-pointer"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold">{job.title}</h3>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${job.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                          {job.isActive ? 'Active' : 'Inactive'}
                        </span>
                        {job.vertical && (
                          <span className="px-2 py-0.5 text-xs bg-teal-100 text-teal-700 rounded-full">
                            {getVerticalLabel(job.vertical)}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600 text-sm line-clamp-2">{job.description}</p>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Create Job Form */}
            {jobViewMode === 'create' && (
              <form onSubmit={handleCreateJob} className="bg-white border rounded-xl p-6 space-y-6">
                <div>
                  <Label>Industry Vertical *</Label>
                  <div className="grid sm:grid-cols-2 gap-3 mt-2">
                    {VERTICALS.map((v) => (
                      <button
                        key={v.value}
                        type="button"
                        onClick={() => setJobFormData({ ...jobFormData, vertical: v.value, roleType: '' })}
                        className={`p-4 rounded-xl border-2 text-left ${jobFormData.vertical === v.value ? 'border-teal-500 bg-teal-50' : 'border-gray-200'}`}
                      >
                        <div className="font-medium">{v.label}</div>
                        <div className="text-sm text-gray-500">{v.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {jobFormData.vertical && ROLE_TYPES[jobFormData.vertical] && (
                  <div>
                    <Label>Role Type *</Label>
                    <div className="grid sm:grid-cols-3 gap-3 mt-2">
                      {ROLE_TYPES[jobFormData.vertical].map((r) => (
                        <button
                          key={r.value}
                          type="button"
                          onClick={() => setJobFormData({ ...jobFormData, roleType: r.value })}
                          className={`p-3 rounded-lg border-2 text-sm ${jobFormData.roleType === r.value ? 'border-teal-500 bg-teal-50' : 'border-gray-200'}`}
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
                    className="mt-2"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="description">Description *</Label>
                  <textarea
                    id="description"
                    value={jobFormData.description}
                    onChange={(e) => setJobFormData({ ...jobFormData, description: e.target.value })}
                    className="mt-2 w-full px-3 py-2 border rounded-lg min-h-[120px]"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="requirements">Requirements (one per line)</Label>
                  <textarea
                    id="requirements"
                    value={jobFormData.requirements}
                    onChange={(e) => setJobFormData({ ...jobFormData, requirements: e.target.value })}
                    className="mt-2 w-full px-3 py-2 border rounded-lg min-h-[100px] font-mono text-sm"
                  />
                </div>

                <div className="grid sm:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input id="location" value={jobFormData.location} onChange={(e) => setJobFormData({ ...jobFormData, location: e.target.value })} className="mt-2" />
                  </div>
                  <div>
                    <Label htmlFor="salaryMin">Min Salary ($/year)</Label>
                    <Input id="salaryMin" type="number" value={jobFormData.salaryMin} onChange={(e) => setJobFormData({ ...jobFormData, salaryMin: e.target.value })} className="mt-2" />
                  </div>
                  <div>
                    <Label htmlFor="salaryMax">Max Salary ($/year)</Label>
                    <Input id="salaryMax" type="number" value={jobFormData.salaryMax} onChange={(e) => setJobFormData({ ...jobFormData, salaryMax: e.target.value })} className="mt-2" />
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button type="button" variant="outline" onClick={() => setJobViewMode('list')}>Cancel</Button>
                  <Button type="submit" disabled={isSaving || !jobFormData.vertical || !jobFormData.roleType}>
                    {isSaving ? 'Creating...' : 'Create Job'}
                  </Button>
                </div>
              </form>
            )}

            {/* Job Detail */}
            {jobViewMode === 'detail' && selectedJob && (
              <div className="space-y-6">
                <div className="bg-white border rounded-xl p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-semibold">{selectedJob.title}</h2>
                      <div className="flex gap-2 mt-2">
                        {selectedJob.vertical && (
                          <span className="px-2 py-0.5 text-xs bg-teal-100 text-teal-700 rounded-full">
                            {getVerticalLabel(selectedJob.vertical)}
                          </span>
                        )}
                        {selectedJob.roleType && (
                          <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
                            {getRoleLabel(selectedJob.vertical || '', selectedJob.roleType)}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className={`px-3 py-1 text-sm rounded-full ${selectedJob.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {selectedJob.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <p className="text-gray-600">{selectedJob.description}</p>
                </div>

                <div className="bg-white border rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold">Interview Invite Links</h3>
                      <p className="text-sm text-gray-500">Share these links with candidates</p>
                    </div>
                    <Button onClick={handleCreateInvite}>New Link</Button>
                  </div>

                  {invites.length === 0 ? (
                    <p className="text-center py-8 text-gray-500">No invite links yet</p>
                  ) : (
                    <div className="space-y-3">
                      {invites.map((invite) => (
                        <div key={invite.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-mono truncate">{invite.inviteUrl}</div>
                            <div className="text-xs text-gray-500">Used: {invite.usedCount}/{invite.maxUses || '∞'}</div>
                          </div>
                          <Button variant="outline" size="sm" onClick={() => handleCopyLink(invite.inviteUrl, invite.id)}>
                            {copiedId === invite.id ? 'Copied!' : 'Copy'}
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => handleDeleteInvite(invite.id)} className="text-red-600">
                            Delete
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Interviews Tab */}
        {activeTab === 'interviews' && (
          <div>
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Interviews</h1>
              <p className="text-gray-500">{interviewsTotal} interview{interviewsTotal !== 1 ? 's' : ''}</p>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="py-4">
                <div className="flex flex-wrap gap-4 items-end">
                  <div className="w-48">
                    <Label className="text-sm">Job</Label>
                    <select
                      value={interviewJobFilter}
                      onChange={(e) => setInterviewJobFilter(e.target.value)}
                      className="w-full mt-1 px-3 py-2 border rounded-lg"
                    >
                      <option value="">All Jobs</option>
                      {jobs.map((job) => (
                        <option key={job.id} value={job.id}>{job.title}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-40">
                    <Label className="text-sm">Status</Label>
                    <select
                      value={interviewStatusFilter}
                      onChange={(e) => setInterviewStatusFilter(e.target.value)}
                      className="w-full mt-1 px-3 py-2 border rounded-lg"
                    >
                      <option value="">All</option>
                      <option value="completed">Completed</option>
                      <option value="in_progress">In Progress</option>
                    </select>
                  </div>
                  <div className="w-32">
                    <Label className="text-sm">Min Score</Label>
                    <Input
                      type="number"
                      value={interviewMinScore}
                      onChange={(e) => setInterviewMinScore(e.target.value)}
                      placeholder="0"
                      className="mt-1"
                    />
                  </div>
                  <Button onClick={loadInterviews}>Filter</Button>
                  <Button variant="outline" onClick={() => { setInterviewJobFilter(''); setInterviewStatusFilter(''); setInterviewMinScore(''); loadInterviews() }}>
                    Clear
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Interviews List */}
            {interviews.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-gray-500">No interviews found</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {interviews.map((interview) => (
                  <div
                    key={interview.id}
                    onClick={() => router.push(`/employer/dashboard/interviews/${interview.id}`)}
                    className="bg-white border rounded-xl p-4 hover:shadow-md transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium">{interview.candidateName || 'Unknown'}</h3>
                        <p className="text-sm text-gray-500">{interview.candidateId}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-teal-600">
                          {interview.totalScore?.toFixed(1) || '-'}
                        </div>
                        <div className="text-xs text-gray-500">/ 10</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Talent Pool Tab */}
        {activeTab === 'talent' && (
          <div>
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Talent Pool</h1>
              <p className="text-gray-500">Browse pre-interviewed candidates</p>
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="py-4">
                <form onSubmit={(e) => { e.preventDefault(); setTalentSearch(talentSearchInput); setTalentPage(1); loadTalentPool() }} className="mb-4">
                  <div className="flex gap-2">
                    <Input
                      value={talentSearchInput}
                      onChange={(e) => setTalentSearchInput(e.target.value)}
                      placeholder="Search by name, skills..."
                      className="flex-1"
                    />
                    <Button type="submit">Search</Button>
                  </div>
                </form>

                <div className="flex flex-wrap gap-4 items-end">
                  <div className="w-48">
                    <Label className="text-sm">Vertical</Label>
                    <select
                      value={talentVertical}
                      onChange={(e) => { setTalentVertical(e.target.value as Vertical | ''); setTalentRole(''); setTalentPage(1) }}
                      className="w-full mt-1 px-3 py-2 border rounded-lg"
                    >
                      <option value="">All Verticals</option>
                      {VERTICALS.map((v) => (
                        <option key={v.value} value={v.value}>{v.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-48">
                    <Label className="text-sm">Role</Label>
                    <select
                      value={talentRole}
                      onChange={(e) => { setTalentRole(e.target.value as RoleType | ''); setTalentPage(1) }}
                      disabled={!talentVertical}
                      className="w-full mt-1 px-3 py-2 border rounded-lg disabled:bg-gray-50"
                    >
                      <option value="">All Roles</option>
                      {talentVertical && ROLE_TYPES[talentVertical]?.map((r) => (
                        <option key={r.value} value={r.value}>{r.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-40">
                    <Label className="text-sm">Min Score</Label>
                    <select
                      value={talentMinScore}
                      onChange={(e) => { setTalentMinScore(Number(e.target.value)); setTalentPage(1) }}
                      className="w-full mt-1 px-3 py-2 border rounded-lg"
                    >
                      <option value={0}>Any Score</option>
                      <option value={5}>5+ / 10</option>
                      <option value={6}>6+ / 10</option>
                      <option value={7}>7+ / 10</option>
                      <option value={8}>8+ / 10</option>
                    </select>
                  </div>
                  <Button variant="outline" onClick={() => { setTalentVertical(''); setTalentRole(''); setTalentMinScore(0); setTalentSearchInput(''); setTalentSearch(''); setTalentPage(1) }}>
                    Clear All
                  </Button>
                </div>
              </CardContent>
            </Card>

            <p className="text-sm text-gray-600 mb-4">{talentTotal} candidate{talentTotal !== 1 ? 's' : ''} found</p>

            {/* Candidates Grid */}
            {candidates.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-gray-500">No candidates found</p>
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                  {candidates.map((candidate) => (
                    <Card key={candidate.profileId} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg">{candidate.candidateName}</CardTitle>
                            <CardDescription>{candidate.candidateEmail}</CardDescription>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-teal-600">{candidate.bestScore?.toFixed(1)}</div>
                            <div className="text-xs text-gray-500">/ 10</div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center gap-2 mb-3">
                          {candidate.vertical && (
                            <span className="px-2 py-1 text-xs bg-gray-100 rounded-md">
                              {VERTICALS.find(v => v.value === candidate.vertical)?.label || candidate.vertical}
                            </span>
                          )}
                          <span className="text-xs text-gray-500">
                            {candidate.roleType ? (ROLE_NAMES[candidate.roleType] || candidate.roleType) : 'No role'}
                          </span>
                        </div>
                        {candidate.skills.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            {candidate.skills.slice(0, 4).map((skill, i) => (
                              <span key={i} className="px-2 py-0.5 text-xs bg-gray-100 rounded">{skill}</span>
                            ))}
                            {candidate.skills.length > 4 && (
                              <span className="text-xs text-gray-400">+{candidate.skills.length - 4}</span>
                            )}
                          </div>
                        )}
                        <Link href={`/employer/dashboard/talent-pool/${candidate.profileId}`}>
                          <Button variant="outline" size="sm" className="w-full">View Profile</Button>
                        </Link>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Pagination */}
                {Math.ceil(talentTotal / talentPageSize) > 1 && (
                  <div className="flex items-center justify-center gap-2">
                    <Button variant="outline" size="sm" disabled={talentPage === 1} onClick={() => setTalentPage(p => p - 1)}>
                      Previous
                    </Button>
                    <span className="text-sm text-gray-600">
                      Page {talentPage} of {Math.ceil(talentTotal / talentPageSize)}
                    </span>
                    <Button variant="outline" size="sm" disabled={talentPage >= Math.ceil(talentTotal / talentPageSize)} onClick={() => setTalentPage(p => p + 1)}>
                      Next
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </Container>
    </PageWrapper>
  )
}

export default function EmployerDashboardPage() {
  return (
    <Suspense fallback={
      <PageWrapper className="flex items-center justify-center">
        <div className="w-12 h-12 border-2 border-gray-200 border-t-teal-500 rounded-full animate-spin" />
      </PageWrapper>
    }>
      <EmployerDashboardContent />
    </Suspense>
  )
}
