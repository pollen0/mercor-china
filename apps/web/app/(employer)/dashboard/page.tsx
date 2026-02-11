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
import { MatchAlerts } from '@/components/employer/match-alerts'
import { CandidateNotes } from '@/components/employer/candidate-notes'
import { EmployerVerificationBanner } from '@/components/verification/employer-verification-banner'
import { employerApi, inviteApi, talentPoolApi, organizationApi, schedulingLinkApi, teamMemberApi, vibeCodeApi, type Employer, type DashboardStats, type InterviewSession, type Job, type InviteTokenResponse, type TalentPoolCandidate, type TalentProfileDetail, type Vertical, type RoleType, type Organization, type OrganizationMember, type OrganizationInvite, type SchedulingLink, type TeamMember, type MatchStatus, type VibeCodeProfileSummary } from '@/lib/api'
import { CustomSelect, StatusSelect, type SelectOption } from '@/components/ui/custom-select'
import { logout, clearAuthTokens } from '@/lib/auth'

type TabType = 'overview' | 'interviews' | 'jobs' | 'talent' | 'team' | 'scheduling'

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

// Candidate status options for employers
const MATCH_STATUS_OPTIONS: { value: MatchStatus; label: string; color: string; bgColor: string }[] = [
  { value: 'PENDING', label: 'New', color: 'text-stone-600', bgColor: 'bg-stone-100' },
  { value: 'CONTACTED', label: 'Contacted', color: 'text-stone-700', bgColor: 'bg-stone-100' },
  { value: 'IN_REVIEW', label: 'In Review', color: 'text-amber-700', bgColor: 'bg-amber-100' },
  { value: 'SHORTLISTED', label: 'Shortlisted', color: 'text-teal-700', bgColor: 'bg-teal-100' },
  { value: 'REJECTED', label: 'Rejected', color: 'text-red-700', bgColor: 'bg-red-100' },
  { value: 'HIRED', label: 'Hired', color: 'text-teal-700', bgColor: 'bg-teal-50' },
]

const SCHEDULING_DURATION_OPTIONS = [
  { value: 15, label: '15 minutes' },
  { value: 30, label: '30 minutes' },
  { value: 45, label: '45 minutes' },
  { value: 60, label: '1 hour' },
  { value: 90, label: '1.5 hours' },
]

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
  const [talentGraduationYear, setTalentGraduationYear] = useState<number | ''>('')
  const [talentSearch, setTalentSearch] = useState('')
  const [talentSearchInput, setTalentSearchInput] = useState('')

  // Expandable rows state
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [vibeCodeProfiles, setVibeCodeProfiles] = useState<Record<string, VibeCodeProfileSummary>>({})
  const [loadingVibeProfile, setLoadingVibeProfile] = useState<string | null>(null)
  const [expandedData, setExpandedData] = useState<Record<string, TalentProfileDetail>>({})
  const [loadingDetail, setLoadingDetail] = useState<string | null>(null)

  // Candidate status management state
  const [candidateStatuses, setCandidateStatuses] = useState<Record<string, MatchStatus>>({})
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null)

  // Contact modal state
  const [showContactModal, setShowContactModal] = useState(false)
  const [contactCandidate, setContactCandidate] = useState<TalentPoolCandidate | null>(null)
  const [contactSubject, setContactSubject] = useState('')
  const [contactMessage, setContactMessage] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [schedulingLinks, setSchedulingLinks] = useState<SchedulingLink[]>([])
  const [selectedSchedulingLink, setSelectedSchedulingLink] = useState<string>('')
  const [loadingSchedulingLinks, setLoadingSchedulingLinks] = useState(false)

  // Resume preview modal state
  const [showResumeModal, setShowResumeModal] = useState(false)
  const [resumePreviewUrl, setResumePreviewUrl] = useState<string | null>(null)
  const [resumePreviewName, setResumePreviewName] = useState<string>('')

  // Transcript preview modal state
  const [showTranscriptModal, setShowTranscriptModal] = useState(false)
  const [transcriptData, setTranscriptData] = useState<TalentProfileDetail | null>(null)
  const [transcriptCandidateName, setTranscriptCandidateName] = useState<string>('')

  // Profile dropdown state
  const [showProfileDropdown, setShowProfileDropdown] = useState(false)

  // Team state
  const [organization, setOrganization] = useState<Organization | null>(null)
  const [teamMembers, setTeamMembers] = useState<OrganizationMember[]>([])
  const [teamInvites, setTeamInvites] = useState<OrganizationInvite[]>([])
  const [teamLoading, setTeamLoading] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('recruiter')
  const [isInviting, setIsInviting] = useState(false)
  const [showCreateOrgModal, setShowCreateOrgModal] = useState(false)
  const [newOrgName, setNewOrgName] = useState('')
  const [isCreatingOrg, setIsCreatingOrg] = useState(false)

  // Scheduling state
  const [schedulingTeamMembers, setSchedulingTeamMembers] = useState<TeamMember[]>([])
  const [schedulingLoading, setSchedulingLoading] = useState(false)
  const [showCreateSchedulingLinkModal, setShowCreateSchedulingLinkModal] = useState(false)
  const [editingSchedulingLink, setEditingSchedulingLink] = useState<SchedulingLink | null>(null)
  const [schedulingCopiedSlug, setSchedulingCopiedSlug] = useState<string | null>(null)
  const [schedulingFormData, setSchedulingFormData] = useState({
    name: '',
    description: '',
    durationMinutes: 30,
    interviewerIds: [] as string[],
    bufferBeforeMinutes: 5,
    bufferAfterMinutes: 5,
    minNoticeHours: 24,
    maxDaysAhead: 14,
  })
  const [isSavingSchedulingLink, setIsSavingSchedulingLink] = useState(false)
  const [schedulingError, setSchedulingError] = useState<string | null>(null)
  const [schedulingWizardStep, setSchedulingWizardStep] = useState(1)

  // Initial data load
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/employer/login')
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
          clearAuthTokens('employer')
          router.push('/employer/login')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadInitialData()
  }, [router])

  // Re-fetch employer data when tab becomes visible (e.g. after email verification in another tab)
  useEffect(() => {
    if (employer?.isVerified) return
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible') {
        try {
          const employerData = await employerApi.getMe()
          setEmployer(employerData)
        } catch {
          // Silently ignore - not critical
        }
      }
    }
    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
  }, [employer?.isVerified])

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
        graduationYear: talentGraduationYear || undefined,
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
  }, [talentVertical, talentRole, talentMinScore, talentGraduationYear, talentSearch])

  useEffect(() => {
    if (activeTab === 'talent') {
      loadTalentPool()
    }
  }, [activeTab, loadTalentPool])

  // Load team when tab changes
  const loadTeam = useCallback(async () => {
    setTeamLoading(true)
    try {
      const [org, members, invites] = await Promise.all([
        organizationApi.getMe().catch(() => null),
        organizationApi.listMembers().catch(() => []),
        organizationApi.listInvites().catch(() => []),
      ])
      setOrganization(org)
      setTeamMembers(members)
      setTeamInvites(invites)
    } catch (err) {
      console.error('Failed to load team:', err)
    } finally {
      setTeamLoading(false)
    }
  }, [])

  useEffect(() => {
    if (activeTab === 'team') {
      loadTeam()
    }
  }, [activeTab, loadTeam])

  // Team handlers
  const handleCreateOrganization = async () => {
    if (!newOrgName.trim()) return
    setIsCreatingOrg(true)
    try {
      const org = await organizationApi.create({ name: newOrgName.trim() })
      setOrganization(org)
      setShowCreateOrgModal(false)
      setNewOrgName('')
      loadTeam()
    } catch (err) {
      console.error('Failed to create organization:', err)
      alert('Failed to create organization')
    } finally {
      setIsCreatingOrg(false)
    }
  }

  const handleInviteMember = async () => {
    if (!inviteEmail.trim()) return
    setIsInviting(true)
    try {
      await organizationApi.createInvite({ email: inviteEmail.trim(), role: inviteRole })
      setShowInviteModal(false)
      setInviteEmail('')
      setInviteRole('recruiter')
      loadTeam()
    } catch (err) {
      console.error('Failed to send invite:', err)
      alert('Failed to send invite')
    } finally {
      setIsInviting(false)
    }
  }

  const handleRemoveMember = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this team member?')) return
    try {
      await organizationApi.removeMember(memberId)
      loadTeam()
    } catch (err) {
      console.error('Failed to remove member:', err)
      alert('Failed to remove member')
    }
  }

  const handleCancelInvite = async (inviteId: string) => {
    try {
      await organizationApi.cancelInvite(inviteId)
      loadTeam()
    } catch (err) {
      console.error('Failed to cancel invite:', err)
    }
  }

  // Scheduling handlers
  const loadSchedulingData = useCallback(async () => {
    setSchedulingLoading(true)
    try {
      const [linksData, teamData] = await Promise.all([
        schedulingLinkApi.list(true),
        teamMemberApi.list(true).catch(() => ({ teamMembers: [] })),
      ])
      setSchedulingLinks(linksData.links)
      setSchedulingTeamMembers(teamData.teamMembers)
    } catch (err) {
      console.error('Failed to load scheduling data:', err)
    } finally {
      setSchedulingLoading(false)
    }
  }, [])

  useEffect(() => {
    if (activeTab === 'scheduling') {
      loadSchedulingData()
    }
  }, [activeTab, loadSchedulingData])

  const resetSchedulingForm = () => {
    setSchedulingFormData({
      name: '',
      description: '',
      durationMinutes: 30,
      interviewerIds: [],
      bufferBeforeMinutes: 5,
      bufferAfterMinutes: 5,
      minNoticeHours: 24,
      maxDaysAhead: 14,
    })
    setSchedulingWizardStep(1)
    setSchedulingError(null)
  }

  const handleCreateSchedulingLink = async () => {
    if (schedulingFormData.interviewerIds.length === 0) {
      setSchedulingError('Please select at least one interviewer')
      return
    }

    setSchedulingError(null)
    setIsSavingSchedulingLink(true)

    try {
      const newLink = await schedulingLinkApi.create({
        name: schedulingFormData.name,
        description: schedulingFormData.description || undefined,
        durationMinutes: schedulingFormData.durationMinutes,
        interviewerIds: schedulingFormData.interviewerIds,
        bufferBeforeMinutes: schedulingFormData.bufferBeforeMinutes,
        bufferAfterMinutes: schedulingFormData.bufferAfterMinutes,
        minNoticeHours: schedulingFormData.minNoticeHours,
        maxDaysAhead: schedulingFormData.maxDaysAhead,
      })

      setSchedulingLinks([newLink, ...schedulingLinks])
      setShowCreateSchedulingLinkModal(false)
      resetSchedulingForm()
    } catch (err) {
      console.error('Failed to create link:', err)
      setSchedulingError(err instanceof Error ? err.message : 'Failed to create scheduling link')
    } finally {
      setIsSavingSchedulingLink(false)
    }
  }

  const handleUpdateSchedulingLink = async () => {
    if (!editingSchedulingLink) return
    if (schedulingFormData.interviewerIds.length === 0) {
      setSchedulingError('Please select at least one interviewer')
      return
    }

    setSchedulingError(null)
    setIsSavingSchedulingLink(true)

    try {
      const updated = await schedulingLinkApi.update(editingSchedulingLink.id, {
        name: schedulingFormData.name,
        description: schedulingFormData.description || undefined,
        durationMinutes: schedulingFormData.durationMinutes,
        interviewerIds: schedulingFormData.interviewerIds,
        bufferBeforeMinutes: schedulingFormData.bufferBeforeMinutes,
        bufferAfterMinutes: schedulingFormData.bufferAfterMinutes,
        minNoticeHours: schedulingFormData.minNoticeHours,
        maxDaysAhead: schedulingFormData.maxDaysAhead,
      })

      setSchedulingLinks(schedulingLinks.map(l => l.id === updated.id ? updated : l))
      setEditingSchedulingLink(null)
      resetSchedulingForm()
    } catch (err) {
      console.error('Failed to update link:', err)
      setSchedulingError(err instanceof Error ? err.message : 'Failed to update scheduling link')
    } finally {
      setIsSavingSchedulingLink(false)
    }
  }

  const handleToggleSchedulingLinkActive = async (link: SchedulingLink) => {
    try {
      const updated = await schedulingLinkApi.update(link.id, {
        isActive: !link.isActive,
      })
      setSchedulingLinks(schedulingLinks.map(l => l.id === updated.id ? updated : l))
    } catch (err) {
      console.error('Failed to toggle link status:', err)
    }
  }

  const handleDeleteSchedulingLink = async (linkId: string) => {
    if (!confirm('Are you sure you want to delete this scheduling link?')) return

    try {
      await schedulingLinkApi.delete(linkId)
      setSchedulingLinks(schedulingLinks.filter(l => l.id !== linkId))
    } catch (err) {
      console.error('Failed to delete link:', err)
    }
  }

  const startEditSchedulingLink = (link: SchedulingLink) => {
    setSchedulingFormData({
      name: link.name,
      description: link.description || '',
      durationMinutes: link.durationMinutes,
      interviewerIds: link.interviewerIds,
      bufferBeforeMinutes: link.bufferBeforeMinutes,
      bufferAfterMinutes: link.bufferAfterMinutes,
      minNoticeHours: link.minNoticeHours,
      maxDaysAhead: link.maxDaysAhead,
    })
    setEditingSchedulingLink(link)
    setSchedulingWizardStep(1)
  }

  const copySchedulingLinkToClipboard = async (link: SchedulingLink) => {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin : ''
    const url = `${baseUrl}/schedule/${link.slug}`

    try {
      await navigator.clipboard.writeText(url)
      setSchedulingCopiedSlug(link.slug)
      setTimeout(() => setSchedulingCopiedSlug(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // Get all interviewers (self + team members) for scheduling
  const allSchedulingInterviewers: TeamMember[] = employer ? [
    {
      id: employer.id,
      employerId: employer.id,
      email: employer.email,
      name: employer.name || employer.companyName || 'Me',
      role: 'admin' as const,
      isActive: true,
      googleCalendarConnected: !!employer.googleCalendarConnectedAt,
      maxInterviewsPerDay: 8,
      maxInterviewsPerWeek: 30,
      interviewsThisWeek: 0,
      createdAt: new Date().toISOString(),
    },
    ...schedulingTeamMembers.filter(m => m.isActive),
  ] : []

  const handleLogout = async () => {
    // Call server to invalidate token, then clear local storage and cookies
    await logout('employer', true)
    localStorage.removeItem('employer')
    router.push('/employer/login')
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
    const candidateId = candidate.candidateId

    if (expandedId === id) {
      setExpandedId(null)
      return
    }

    setExpandedId(id)

    // Fetch profile detail if not already loaded
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

    // Fetch vibe code profile if not already loaded
    if (!vibeCodeProfiles[candidateId]) {
      setLoadingVibeProfile(candidateId)
      try {
        const vibeProfile = await vibeCodeApi.getProfile(candidateId)
        if (vibeProfile.totalSessions > 0) {
          setVibeCodeProfiles(prev => ({ ...prev, [candidateId]: vibeProfile }))
        }
      } catch {
        // No vibe code sessions - that's OK
      } finally {
        setLoadingVibeProfile(null)
      }
    }
  }

  // Update candidate status handler
  const handleStatusChange = async (candidateId: string, profileId: string | undefined, newStatus: MatchStatus) => {
    const id = profileId || candidateId
    setUpdatingStatus(id)
    try {
      await talentPoolApi.updateStatus(id, newStatus)
      setCandidateStatuses(prev => ({ ...prev, [id]: newStatus }))
      // Also update the expanded data if it exists
      if (expandedData[id]?.employerStatus) {
        setExpandedData(prev => ({
          ...prev,
          [id]: {
            ...prev[id],
            employerStatus: {
              ...prev[id].employerStatus,
              status: newStatus,
            }
          }
        }))
      }
    } catch (error) {
      console.error('Failed to update status:', error)
    } finally {
      setUpdatingStatus(null)
    }
  }

  // Get the current status for a candidate (from local state, expanded data, or default)
  const getCandidateStatus = (candidate: TalentPoolCandidate): MatchStatus => {
    const id = candidate.profileId || candidate.candidateId
    // Check local state first (most recent updates)
    if (candidateStatuses[id]) return candidateStatuses[id]
    // Check expanded data
    if (expandedData[id]?.employerStatus?.status) return expandedData[id].employerStatus!.status
    // Default to PENDING
    return 'PENDING'
  }

  const openContactModal = async (candidate: TalentPoolCandidate) => {
    setContactCandidate(candidate)
    setContactSubject(`Interview Opportunity at ${employer?.companyName || 'Our Company'}`)
    setSelectedSchedulingLink('')
    setShowContactModal(true)

    // Fetch scheduling links
    setLoadingSchedulingLinks(true)
    try {
      const { links } = await schedulingLinkApi.list()
      setSchedulingLinks(links.filter((link: SchedulingLink) => link.isActive))
    } catch (error) {
      console.error('Failed to load scheduling links:', error)
      setSchedulingLinks([])
    } finally {
      setLoadingSchedulingLinks(false)
    }

    // Set default message
    const roleDisplay = candidate.roleType ? (ROLE_NAMES[candidate.roleType] || candidate.roleType) : 'open'
    setContactMessage(`Dear ${candidate.candidateName},

We reviewed your profile on Pathway and were impressed by your qualifications for ${roleDisplay} positions.

We would like to discuss a potential opportunity with you. Would you be available for a conversation?

Best regards,
${employer?.companyName || 'Our Company'}`)
  }

  // Update message when scheduling link is selected
  const handleSchedulingLinkChange = (linkId: string) => {
    setSelectedSchedulingLink(linkId)
    if (!contactCandidate) return

    const roleDisplay = contactCandidate.roleType ? (ROLE_NAMES[contactCandidate.roleType] || contactCandidate.roleType) : 'open'
    const selectedLink = schedulingLinks.find(l => l.id === linkId)

    if (selectedLink) {
      const scheduleUrl = `${window.location.origin}/schedule/${selectedLink.slug}`
      setContactMessage(`Dear ${contactCandidate.candidateName},

We reviewed your profile on Pathway and were impressed by your qualifications for ${roleDisplay} positions.

We would like to schedule an interview with you. Please use the link below to select a time that works best for you:

Schedule your interview: ${scheduleUrl}

This ${selectedLink.durationMinutes}-minute interview will be conducted via Google Meet. You'll receive a calendar invite with the meeting link once you book a time.

Best regards,
${employer?.companyName || 'Our Company'}`)
    } else {
      setContactMessage(`Dear ${contactCandidate.candidateName},

We reviewed your profile on Pathway and were impressed by your qualifications for ${roleDisplay} positions.

We would like to discuss a potential opportunity with you. Would you be available for a conversation?

Best regards,
${employer?.companyName || 'Our Company'}`)
    }
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

  // Transcript download handler
  const downloadTranscript = (detail: TalentProfileDetail, candidateName: string) => {
    if (!detail.interview?.responses?.length) return

    // Build transcript text
    let content = `Interview - ${candidateName}\n`
    content += `${'='.repeat(50)}\n\n`

    if (detail.profile?.vertical) {
      content += `Vertical: ${detail.profile.vertical}\n`
    }
    if (detail.profile?.roleType) {
      content += `Role: ${detail.profile.roleType}\n`
    }
    if (detail.interview.completedAt) {
      content += `Date: ${new Date(detail.interview.completedAt).toLocaleDateString()}\n`
    }
    content += `\n${'='.repeat(50)}\n\n`

    detail.interview.responses.forEach((response, index) => {
      content += `Question ${index + 1}:\n`
      content += `${response.questionText || 'N/A'}\n\n`
      content += `Answer:\n`
      content += `${response.transcription || '(No transcript available)'}\n\n`
      content += `${'-'.repeat(40)}\n\n`
    })

    // Create and download file
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${candidateName.replace(/\s+/g, '_')}_interview.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
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
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <Link href="/" className="text-lg font-semibold text-stone-900">
            Pathway
          </Link>
          <div className="flex items-center gap-4">
            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                className="flex items-center gap-2 px-3 py-1.5 bg-stone-100 hover:bg-stone-200 rounded-full transition-colors cursor-pointer"
              >
                <div className="w-6 h-6 bg-teal-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium text-xs">
                    {(employer?.name?.charAt(0) || employer?.companyName?.charAt(0) || employer?.email?.split('@')[0]?.charAt(0) || 'U').toUpperCase()}
                  </span>
                </div>
                <span className="text-sm text-stone-700 font-medium">{employer?.name || employer?.companyName || employer?.email?.split('@')[0]}</span>
                <svg className={`w-4 h-4 text-stone-400 transition-transform ${showProfileDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {showProfileDropdown && (
                <>
                  {/* Backdrop to close dropdown */}
                  <div className="fixed inset-0 z-10" onClick={() => setShowProfileDropdown(false)} />

                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-stone-200 py-2 z-20">
                    {/* User Info */}
                    <div className="px-4 py-3 border-b border-stone-100">
                      <p className="font-medium text-stone-900">{employer?.name || employer?.email?.split('@')[0]}</p>
                      {employer?.companyName && (
                        <p className="text-xs text-stone-600">{employer.companyName}</p>
                      )}
                      <p className="text-xs text-stone-500">{employer?.email}</p>
                    </div>

                    {/* Menu Items */}
                    <div className="py-1">
                      <button
                        onClick={() => {
                          setShowProfileDropdown(false)
                          router.push('/dashboard/settings')
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-stone-700 hover:bg-stone-50 flex items-center gap-3"
                      >
                        <svg className="w-4 h-4 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        Account Settings
                      </button>
                      <button
                        onClick={() => {
                          setShowProfileDropdown(false)
                          // TODO: Navigate to billing page
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-stone-700 hover:bg-stone-50 flex items-center gap-3"
                      >
                        <svg className="w-4 h-4 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                        Billing
                      </button>
                    </div>

                    {/* Logout */}
                    <div className="border-t border-stone-100 pt-1">
                      <button
                        onClick={() => {
                          setShowProfileDropdown(false)
                          handleLogout()
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-3"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        Logout
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-stone-100">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="flex gap-1 overflow-x-auto">
            {[
              { key: 'overview', label: 'Overview' },
              { key: 'interviews', label: 'Interviews' },
              { key: 'jobs', label: 'Jobs' },
              { key: 'talent', label: 'Talent Pool' },
              { key: 'team', label: 'Team' },
              { key: 'scheduling', label: 'Scheduling' },
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

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Email Verification Banner */}
        {employer && !employer.isVerified && (
          <EmployerVerificationBanner email={employer.email} />
        )}

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

            {/* Match Alerts and Recent Interviews */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Match Alerts */}
              <MatchAlerts limit={5} showViewAll={true} />

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
                      View all <svg className="inline w-3.5 h-3.5 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
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
            </div>

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
                <div className="flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4 items-stretch sm:items-end">
                  <div className="w-full sm:w-40">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Job</Label>
                    <CustomSelect
                      value={selectedJob}
                      onChange={setSelectedJob}
                      options={[
                        { value: '', label: 'All Jobs' },
                        ...jobs.map(job => ({ value: job.id, label: job.title }))
                      ]}
                      size="sm"
                    />
                  </div>
                  <div className="w-full sm:w-40">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Status</Label>
                    <CustomSelect
                      value={statusFilter}
                      onChange={setStatusFilter}
                      options={[
                        { value: '', label: 'All Statuses' },
                        { value: 'PENDING', label: 'Pending' },
                        { value: 'IN_PROGRESS', label: 'In Progress' },
                        { value: 'COMPLETED', label: 'Completed' },
                      ]}
                      size="sm"
                    />
                  </div>
                  <div className="w-full sm:w-24">
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
                    <svg className="inline w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg> Back
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
                              {copiedId === invite.id ? 'Copied' : 'Copy'}
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

        {/* Team Tab */}
        {activeTab === 'team' && (
          <div className="space-y-6">
            {teamLoading ? (
              <div className="text-center py-12">
                <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto" />
              </div>
            ) : !organization ? (
              /* No Organization - Show Create Flow */
              <div className="max-w-lg mx-auto text-center py-12">
                <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-stone-900 mb-2">Set Up Your Team</h2>
                <p className="text-stone-500 mb-6">
                  Create an organization to collaborate with your team on hiring. Invite recruiters, hiring managers, and interviewers to work together.
                </p>
                <Button onClick={() => setShowCreateOrgModal(true)} className="bg-teal-600 hover:bg-teal-700">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Organization
                </Button>
              </div>
            ) : (
              /* Has Organization - Show Team Management */
              <>
                {/* Organization Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {organization.logoUrl ? (
                      <img src={organization.logoUrl} alt={organization.name} className="w-12 h-12 rounded-lg object-cover" />
                    ) : (
                      <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center">
                        <span className="text-xl font-semibold text-teal-700">{organization.name.charAt(0).toUpperCase()}</span>
                      </div>
                    )}
                    <div>
                      <h2 className="text-lg font-semibold text-stone-900">{organization.name}</h2>
                      <p className="text-sm text-stone-500">{teamMembers.length} team member{teamMembers.length !== 1 ? 's' : ''}</p>
                    </div>
                  </div>
                  <Button onClick={() => setShowInviteModal(true)} className="bg-teal-600 hover:bg-teal-700">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                    Invite Member
                  </Button>
                </div>

                {/* Team Members */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Team Members</CardTitle>
                    <CardDescription>People who can access your organization&apos;s hiring pipeline</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="divide-y divide-stone-100">
                      {teamMembers.map((member) => (
                        <div key={member.id} className="flex items-center justify-between py-3">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center">
                              <span className="text-sm font-semibold text-white">
                                {(member.name || member.email || 'U').charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <p className="font-medium text-stone-900">{member.name || member.email}</p>
                              <p className="text-sm text-stone-500">{member.email}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              member.role === 'owner' ? 'bg-stone-200 text-stone-700' :
                              member.role === 'admin' ? 'bg-stone-100 text-stone-700' :
                              member.role === 'recruiter' ? 'bg-teal-100 text-teal-700' :
                              member.role === 'hiring_manager' ? 'bg-amber-100 text-amber-700' :
                              'bg-stone-100 text-stone-600'
                            }`}>
                              {member.role === 'hiring_manager' ? 'Hiring Manager' :
                               member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                            </span>
                            {member.role !== 'owner' && member.employerId !== employer?.id && (
                              <button
                                onClick={() => handleRemoveMember(member.id)}
                                className="p-1 text-stone-400 hover:text-red-500 transition-colors"
                                title="Remove member"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Pending Invites */}
                {teamInvites.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Pending Invites</CardTitle>
                      <CardDescription>Invitations that haven&apos;t been accepted yet</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="divide-y divide-stone-100">
                        {teamInvites.map((invite) => (
                          <div key={invite.id} className="flex items-center justify-between py-3">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-stone-100 flex items-center justify-center">
                                <svg className="w-5 h-5 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                </svg>
                              </div>
                              <div>
                                <p className="font-medium text-stone-900">{invite.email}</p>
                                <p className="text-xs text-stone-400">
                                  Invited as {invite.role === 'hiring_manager' ? 'Hiring Manager' :
                                   invite.role.charAt(0).toUpperCase() + invite.role.slice(1)}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="px-2 py-1 text-xs font-medium rounded-full bg-amber-100 text-amber-700">
                                Pending
                              </span>
                              <button
                                onClick={() => handleCancelInvite(invite.id)}
                                className="p-1 text-stone-400 hover:text-red-500 transition-colors"
                                title="Cancel invite"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Role Permissions Info */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Role Permissions</CardTitle>
                    <CardDescription>What each role can do in your organization</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div className="p-4 bg-stone-100 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-stone-200 text-stone-700">Owner</span>
                        </div>
                        <p className="text-sm text-stone-600">Full access: manage team, billing, and all hiring activities</p>
                      </div>
                      <div className="p-4 bg-stone-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-stone-100 text-stone-700">Admin</span>
                        </div>
                        <p className="text-sm text-stone-600">Manage team members, jobs, and all candidates</p>
                      </div>
                      <div className="p-4 bg-teal-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-teal-100 text-teal-700">Recruiter</span>
                        </div>
                        <p className="text-sm text-stone-600">Create jobs, review candidates, send invites</p>
                      </div>
                      <div className="p-4 bg-amber-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-700">Hiring Manager</span>
                        </div>
                        <p className="text-sm text-stone-600">Review candidates for assigned jobs, leave feedback</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
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

                <div className="flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4 items-stretch sm:items-end">
                  <div className="w-full sm:w-44">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Industry Vertical</Label>
                    <CustomSelect
                      value={talentVertical}
                      onChange={handleTalentVerticalChange}
                      options={[
                        { value: '', label: 'All Verticals' },
                        ...VERTICALS.map(v => ({ value: v.value, label: v.label }))
                      ]}
                      size="sm"
                    />
                  </div>
                  <div className="w-full sm:w-40">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Role Type</Label>
                    <CustomSelect
                      value={talentRole}
                      onChange={(val) => setTalentRole(val as RoleType | '')}
                      options={[
                        { value: '', label: 'All Roles' },
                        ...availableTalentRoles.map(r => ({ value: r.value, label: r.label }))
                      ]}
                      disabled={!talentVertical}
                      size="sm"
                    />
                  </div>
                  <div className="w-full sm:w-32">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Min Score</Label>
                    <CustomSelect
                      value={String(talentMinScore)}
                      onChange={(val) => setTalentMinScore(Number(val))}
                      options={[
                        { value: '0', label: 'Any Score' },
                        { value: '5', label: '5+ / 10' },
                        { value: '6', label: '6+ / 10' },
                        { value: '7', label: '7+ / 10' },
                        { value: '8', label: '8+ / 10' },
                      ]}
                      size="sm"
                    />
                  </div>
                  <div className="w-full sm:w-36">
                    <Label className="text-xs text-stone-500 mb-1.5 block">Graduation Year</Label>
                    <CustomSelect
                      value={String(talentGraduationYear)}
                      onChange={(val) => setTalentGraduationYear(val ? Number(val) : '')}
                      options={[
                        { value: '', label: 'All Years' },
                        { value: '2025', label: 'Class of 2025' },
                        { value: '2026', label: 'Class of 2026' },
                        { value: '2027', label: 'Class of 2027' },
                        { value: '2028', label: 'Class of 2028' },
                        { value: '2029', label: 'Class of 2029' },
                      ]}
                      size="sm"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setTalentVertical('')
                      setTalentRole('')
                      setTalentMinScore(0)
                      setTalentGraduationYear('')
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
                    // Try bestScore first, then interviewScore (for completed interviews), then profileScore (pre-interview)
                    const displayScore = candidate.bestScore ?? candidate.interviewScore ?? candidate.profileScore
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
                          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 sm:gap-4">
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
                              <div className="flex items-center gap-2 flex-wrap">
                                <h3 className="font-medium text-stone-900 truncate">{candidate.candidateName}</h3>
                                {candidate.graduationYear && (
                                  <span className="px-1.5 py-0.5 text-xs bg-stone-200 text-stone-700 rounded-full font-medium">
                                    '{String(candidate.graduationYear).slice(-2)}
                                  </span>
                                )}
                                {candidate.cohortBadge && (
                                  <span className="px-2 py-0.5 text-xs bg-teal-100 text-teal-700 rounded-full font-medium">
                                    Top {candidate.cohortBadge.topPercent}%
                                  </span>
                                )}
                                {candidate.completionStatus?.resumeUploaded && (
                                  <span className="px-1.5 py-0.5 text-xs bg-stone-100 text-stone-700 rounded-full">Resume</span>
                                )}
                                {candidate.completionStatus?.transcriptUploaded && (
                                  <span className="px-1.5 py-0.5 text-xs bg-amber-50 text-amber-700 rounded-full">Transcript</span>
                                )}
                                {candidate.completionStatus?.githubConnected && (
                                  <span className="px-1.5 py-0.5 text-xs bg-stone-100 text-stone-700 rounded-full">GitHub</span>
                                )}
                                {candidate.completionStatus?.interviewCompleted ? (
                                  <span className="px-2 py-0.5 text-xs bg-teal-50 text-teal-700 rounded-full flex items-center gap-1">
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
                                {candidate.cohortBadge && (
                                  <span className="text-xs text-teal-600 font-medium hidden lg:inline" title={`Out of ${candidate.cohortBadge.cohortSize} candidates`}>
                                    {candidate.cohortBadge.cohortLabel}
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
                            <div
                              className="hidden sm:block text-center w-20 flex-shrink-0"
                              title={candidate.cohortBadge ? `${candidate.cohortBadge.badgeText} (${candidate.cohortBadge.cohortSize} candidates)` : undefined}
                            >
                              {displayScore ? (
                                <>
                                  <div className={`text-lg font-semibold ${isProfileOnly ? 'text-stone-600' : 'text-teal-600'}`}>
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

                            {/* Status Dropdown */}
                            <div className="hidden sm:block flex-shrink-0 w-28" onClick={(e) => e.stopPropagation()}>
                              {(() => {
                                const currentStatus = getCandidateStatus(candidate)
                                const isUpdating = updatingStatus === rowId
                                return (
                                  <StatusSelect
                                    value={currentStatus}
                                    onChange={(val) => handleStatusChange(candidate.candidateId, candidate.profileId, val as MatchStatus)}
                                    options={MATCH_STATUS_OPTIONS}
                                    disabled={isUpdating}
                                  />
                                )
                              })()}
                            </div>

                            {/* Interview Button */}
                            <div className="hidden sm:block flex-shrink-0">
                              <Button
                                size="sm"
                                className="bg-teal-600 hover:bg-teal-700"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  openContactModal(candidate)
                                }}
                              >
                                Interview
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
                              <div className="space-y-4">
                                {/* View Full Profile Link */}
                                <div className="flex items-center justify-end">
                                  <Link
                                    href={`/dashboard/talent-pool/${rowId}`}
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-teal-700 hover:text-teal-800 hover:bg-teal-100 rounded-md transition-colors"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    View Full Profile
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                    </svg>
                                  </Link>
                                </div>
                                <div className="grid grid-cols-1 gap-4 lg:gap-6 lg:grid-cols-3">
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
                                          if (value == null) return null
                                          const numValue = Number(value) || 0
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
                                                  style={{ width: `${(numValue / 10) * 100}%` }}
                                                />
                                              </div>
                                              <span className="text-xs font-medium w-8">{numValue.toFixed(1)}</span>
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
                                    const isFromInterview = !!(detail.interview?.overallStrengths?.length || detail.interview?.overallConcerns?.length)

                                    return hasAssessment ? (
                                      <div>
                                        <h4 className="text-sm font-semibold text-stone-700 mb-2">
                                          Assessment
                                          {isFromInterview && <span className="text-xs font-normal text-stone-400 ml-1">(Interview)</span>}
                                        </h4>
                                        <div className="space-y-2">
                                          {strengths.length > 0 && (
                                            <div>
                                              <p className="text-xs font-medium text-teal-700 mb-1">Strengths</p>
                                              <ul className="space-y-0.5">
                                                {strengths.slice(0, 3).map((s, i) => (
                                                  <li key={i} className="text-xs text-stone-600 flex items-start gap-1">
                                                    <span className="text-teal-600 mt-0.5">+</span>
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

                                  {/* AI Builder Profile (Vibe Code) */}
                                  {(() => {
                                    const vibeProfile = vibeCodeProfiles[detail.candidate.id]
                                    const isLoading = loadingVibeProfile === detail.candidate.id

                                    if (isLoading) {
                                      return (
                                        <div>
                                          <h4 className="text-sm font-semibold text-stone-700 mb-2">AI Builder Profile</h4>
                                          <div className="flex items-center gap-2 text-xs text-stone-400">
                                            <div className="animate-spin h-3 w-3 border border-stone-300 border-t-stone-600 rounded-full" />
                                            Loading...
                                          </div>
                                        </div>
                                      )
                                    }

                                    if (vibeProfile && vibeProfile.totalSessions > 0) {
                                      return (
                                        <div>
                                          <h4 className="text-sm font-semibold text-stone-700 mb-2">AI Builder Profile</h4>
                                          <div className="space-y-2">
                                            {vibeProfile.bestBuilderScore && (
                                              <div className="flex items-center justify-between">
                                                <span className="text-xs text-stone-500">Builder Score</span>
                                                <span className="text-sm font-semibold text-teal-600">{vibeProfile.bestBuilderScore.toFixed(1)}</span>
                                              </div>
                                            )}
                                            {vibeProfile.primaryArchetype && (
                                              <div className="flex items-center justify-between">
                                                <span className="text-xs text-stone-500">Archetype</span>
                                                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                                                  vibeProfile.primaryArchetype === 'architect'
                                                    ? 'bg-stone-900 text-white'
                                                    : vibeProfile.primaryArchetype === 'iterative_builder'
                                                    ? 'bg-teal-50 text-teal-700'
                                                    : vibeProfile.primaryArchetype === 'experimenter'
                                                    ? 'bg-stone-100 text-stone-700'
                                                    : vibeProfile.primaryArchetype === 'ai_dependent'
                                                    ? 'bg-amber-50 text-amber-700'
                                                    : vibeProfile.primaryArchetype === 'copy_paster'
                                                    ? 'bg-red-50 text-red-700'
                                                    : 'bg-stone-100 text-stone-700'
                                                }`}>
                                                  {vibeProfile.primaryArchetype.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                                </span>
                                              </div>
                                            )}
                                            {vibeProfile.topStrengths && vibeProfile.topStrengths.length > 0 && (
                                              <div>
                                                <p className="text-xs text-stone-500 mb-1">Strengths</p>
                                                <ul className="space-y-0.5">
                                                  {vibeProfile.topStrengths.slice(0, 2).map((s, i) => (
                                                    <li key={i} className="text-xs text-stone-600 flex items-start gap-1">
                                                      <span className="text-teal-500 mt-0.5">+</span>
                                                      <span className="line-clamp-1">{s}</span>
                                                    </li>
                                                  ))}
                                                </ul>
                                              </div>
                                            )}
                                            <p className="text-xs text-stone-400">
                                              {vibeProfile.totalSessions} session{vibeProfile.totalSessions !== 1 ? 's' : ''} analyzed
                                            </p>
                                          </div>
                                        </div>
                                      )
                                    }

                                    return null
                                  })()}

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
                                            <svg className="w-5 h-5 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                            <span className="text-sm text-stone-700">Interview</span>
                                            <span className="text-xs text-stone-400">({detail.interview.responses.length} response{detail.interview.responses.length > 1 ? 's' : ''})</span>
                                          </div>
                                          <div className="flex items-center gap-1">
                                            <button
                                              onClick={(e) => {
                                                e.stopPropagation()
                                                openTranscriptPreview(detail, candidate.candidateName || 'Candidate')
                                              }}
                                              className="px-2 py-1 text-xs font-medium text-teal-600 hover:bg-teal-50 rounded transition-colors"
                                            >
                                              Preview
                                            </button>
                                            <button
                                              onClick={(e) => {
                                                e.stopPropagation()
                                                downloadTranscript(detail, candidate.candidateName || 'Candidate')
                                              }}
                                              className="px-2 py-1 text-xs font-medium text-stone-600 hover:bg-stone-100 rounded transition-colors"
                                            >
                                              Download
                                            </button>
                                          </div>
                                        </div>
                                      )}

                                      {!detail.candidate.resumeUrl && (!detail.interview || !detail.interview.responses || detail.interview.responses.length === 0) && (
                                        <p className="text-xs text-stone-400 italic">No documents available</p>
                                      )}
                                    </div>

                                    {/* Notes Section */}
                                    <CandidateNotes
                                      candidateId={detail.candidate.id}
                                      candidateName={candidate.candidateName}
                                    />
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

        {/* Scheduling Tab */}
        {activeTab === 'scheduling' && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-stone-900">Scheduling Links</h2>
                <p className="text-sm text-stone-500">Create shareable links for candidates to book interviews</p>
              </div>
              <Button onClick={() => { resetSchedulingForm(); setShowCreateSchedulingLinkModal(true) }}>
                Create Link
              </Button>
            </div>

            {/* Links List */}
            {schedulingLoading ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-500 rounded-full animate-spin mx-auto mb-3" />
                  <p className="text-stone-500 text-sm">Loading scheduling links...</p>
                </CardContent>
              </Card>
            ) : schedulingLinks.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <div className="w-12 h-12 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                  </div>
                  <h3 className="text-base font-medium text-stone-900 mb-1">No scheduling links yet</h3>
                  <p className="text-stone-500 text-sm mb-4">
                    Create a scheduling link to let candidates book interviews with your team
                  </p>
                  <Button onClick={() => { resetSchedulingForm(); setShowCreateSchedulingLinkModal(true) }}>
                    Create Your First Link
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {schedulingLinks.map(link => (
                  <Card key={link.id} className={!link.isActive ? 'opacity-60' : ''}>
                    <CardContent className="py-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium text-stone-900">{link.name}</h3>
                            <span className={`px-2 py-0.5 text-xs rounded-full ${
                              link.isActive ? 'bg-teal-50 text-teal-700' : 'bg-stone-100 text-stone-500'
                            }`}>
                              {link.isActive ? 'Active' : 'Inactive'}
                            </span>
                          </div>

                          {link.description && (
                            <p className="text-sm text-stone-500 mb-2">{link.description}</p>
                          )}

                          <div className="flex items-center gap-4 text-sm text-stone-500">
                            <span>{link.durationMinutes} min</span>
                            <span>{link.interviewerIds.length} interviewer{link.interviewerIds.length !== 1 ? 's' : ''}</span>
                            <span>Up to {link.maxDaysAhead} days ahead</span>
                          </div>

                          {/* Interviewers */}
                          {link.interviewers && link.interviewers.length > 0 && (
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-stone-400">Assigned:</span>
                              <div className="flex -space-x-1.5">
                                {link.interviewers.slice(0, 3).map(interviewer => (
                                  <div
                                    key={interviewer.id}
                                    className="w-6 h-6 rounded-full bg-stone-100 text-stone-600 flex items-center justify-center text-xs font-medium border-2 border-white"
                                    title={interviewer.name}
                                  >
                                    {interviewer.name.charAt(0).toUpperCase()}
                                  </div>
                                ))}
                                {link.interviewers.length > 3 && (
                                  <div className="w-6 h-6 rounded-full bg-stone-100 text-stone-500 flex items-center justify-center text-xs font-medium border-2 border-white">
                                    +{link.interviewers.length - 3}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Stats */}
                          <div className="flex items-center gap-4 mt-3 text-xs text-stone-400">
                            <span>{link.viewCount} views</span>
                            <span>{link.bookingCount} bookings</span>
                            <span>Created {new Date(link.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 ml-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => copySchedulingLinkToClipboard(link)}
                            className={schedulingCopiedSlug === link.slug ? 'bg-teal-50 text-teal-700 border-teal-200' : ''}
                          >
                            {schedulingCopiedSlug === link.slug ? (
                              <>
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                                Copied
                              </>
                            ) : (
                              <>
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                                </svg>
                                Copy Link
                              </>
                            )}
                          </Button>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => startEditSchedulingLink(link)}
                          >
                            Edit
                          </Button>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleToggleSchedulingLinkActive(link)}
                          >
                            {link.isActive ? 'Deactivate' : 'Activate'}
                          </Button>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteSchedulingLink(link.id)}
                            className="text-red-600 hover:bg-red-50"
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create/Edit Scheduling Link Modal */}
      {(showCreateSchedulingLinkModal || editingSchedulingLink) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">
                {editingSchedulingLink ? 'Edit Scheduling Link' : 'Create Scheduling Link'}
              </h2>
              {!editingSchedulingLink && (
                <div className="flex items-center gap-2 mt-4">
                  {[1, 2, 3].map(step => (
                    <div
                      key={step}
                      className={`flex items-center ${step < 3 ? 'flex-1' : ''}`}
                    >
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-medium ${
                          step <= schedulingWizardStep
                            ? 'bg-stone-900 text-white'
                            : 'bg-stone-100 text-stone-400'
                        }`}
                      >
                        {step}
                      </div>
                      {step < 3 && (
                        <div
                          className={`flex-1 h-0.5 mx-2 ${
                            step < schedulingWizardStep ? 'bg-stone-900' : 'bg-stone-100'
                          }`}
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6">
              {schedulingError && (
                <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm mb-4">
                  {schedulingError}
                </div>
              )}

              {/* Step 1: Basic Info */}
              {(schedulingWizardStep === 1 || editingSchedulingLink) && (
                <div className="space-y-4">
                  {!editingSchedulingLink && (
                    <h3 className="font-medium text-stone-900">Basic Information</h3>
                  )}

                  <div>
                    <Label htmlFor="scheduling-name">Name *</Label>
                    <Input
                      id="scheduling-name"
                      value={schedulingFormData.name}
                      onChange={e => setSchedulingFormData({ ...schedulingFormData, name: e.target.value })}
                      placeholder="e.g., Engineering Phone Screen"
                      required
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="scheduling-description">Description</Label>
                    <textarea
                      id="scheduling-description"
                      value={schedulingFormData.description}
                      onChange={e => setSchedulingFormData({ ...schedulingFormData, description: e.target.value })}
                      placeholder="Brief description shown to candidates..."
                      rows={2}
                      className="mt-1 w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-stone-900/10 focus:border-stone-300"
                    />
                  </div>

                  <div>
                    <Label>Duration *</Label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 mt-2">
                      {SCHEDULING_DURATION_OPTIONS.map(option => (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => setSchedulingFormData({ ...schedulingFormData, durationMinutes: option.value })}
                          className={`py-2 px-3 rounded-lg border text-sm transition-colors ${
                            schedulingFormData.durationMinutes === option.value
                              ? 'border-stone-900 bg-stone-50 text-stone-900'
                              : 'border-stone-200 text-stone-600 hover:border-stone-300'
                          }`}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {editingSchedulingLink && (
                    <>
                      {/* Show all sections for edit mode */}
                      <div className="border-t border-stone-100 pt-4 mt-4">
                        <h3 className="font-medium text-stone-900 mb-4">Interviewers</h3>
                        <div className="space-y-2">
                          {allSchedulingInterviewers.map(member => (
                            <label
                              key={member.id}
                              className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                                schedulingFormData.interviewerIds.includes(member.id)
                                  ? 'border-stone-900 bg-stone-50'
                                  : 'border-stone-200 hover:border-stone-300'
                              }`}
                            >
                              <input
                                type="checkbox"
                                checked={schedulingFormData.interviewerIds.includes(member.id)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSchedulingFormData({
                                      ...schedulingFormData,
                                      interviewerIds: [...schedulingFormData.interviewerIds, member.id]
                                    })
                                  } else {
                                    setSchedulingFormData({
                                      ...schedulingFormData,
                                      interviewerIds: schedulingFormData.interviewerIds.filter(id => id !== member.id)
                                    })
                                  }
                                }}
                                className="w-4 h-4 text-stone-900 rounded border-stone-300"
                              />
                              <div className="w-8 h-8 rounded-full bg-stone-100 flex items-center justify-center text-sm font-medium">
                                {member.name.charAt(0).toUpperCase()}
                              </div>
                              <div className="flex-1">
                                <p className="text-sm font-medium text-stone-900">{member.name}</p>
                                <p className="text-xs text-stone-500">{member.email}</p>
                              </div>
                              {member.googleCalendarConnected && (
                                <span className="text-xs text-teal-600">Calendar connected</span>
                              )}
                            </label>
                          ))}
                        </div>
                      </div>

                      <div className="border-t border-stone-100 pt-4 mt-4">
                        <h3 className="font-medium text-stone-900 mb-4">Booking Settings</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="edit-bufferBefore">Buffer Before (minutes)</Label>
                            <Input
                              id="edit-bufferBefore"
                              type="number"
                              min={0}
                              max={60}
                              value={schedulingFormData.bufferBeforeMinutes}
                              onChange={e => setSchedulingFormData({ ...schedulingFormData, bufferBeforeMinutes: parseInt(e.target.value) || 0 })}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="edit-bufferAfter">Buffer After (minutes)</Label>
                            <Input
                              id="edit-bufferAfter"
                              type="number"
                              min={0}
                              max={60}
                              value={schedulingFormData.bufferAfterMinutes}
                              onChange={e => setSchedulingFormData({ ...schedulingFormData, bufferAfterMinutes: parseInt(e.target.value) || 0 })}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="edit-minNotice">Min Notice (hours)</Label>
                            <Input
                              id="edit-minNotice"
                              type="number"
                              min={1}
                              max={168}
                              value={schedulingFormData.minNoticeHours}
                              onChange={e => setSchedulingFormData({ ...schedulingFormData, minNoticeHours: parseInt(e.target.value) || 24 })}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="edit-maxDays">Max Days Ahead</Label>
                            <Input
                              id="edit-maxDays"
                              type="number"
                              min={1}
                              max={90}
                              value={schedulingFormData.maxDaysAhead}
                              onChange={e => setSchedulingFormData({ ...schedulingFormData, maxDaysAhead: parseInt(e.target.value) || 14 })}
                              className="mt-1"
                            />
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Step 2: Select Interviewers (create mode only) */}
              {schedulingWizardStep === 2 && !editingSchedulingLink && (
                <div className="space-y-4">
                  <h3 className="font-medium text-stone-900">Select Interviewers</h3>
                  <p className="text-sm text-stone-500">
                    Choose who will be available to conduct interviews. You can select yourself and/or team members.
                  </p>

                  <div className="space-y-2">
                    {allSchedulingInterviewers.map(member => (
                      <label
                        key={member.id}
                        className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                          schedulingFormData.interviewerIds.includes(member.id)
                            ? 'border-stone-900 bg-stone-50'
                            : 'border-stone-200 hover:border-stone-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={schedulingFormData.interviewerIds.includes(member.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSchedulingFormData({
                                ...schedulingFormData,
                                interviewerIds: [...schedulingFormData.interviewerIds, member.id]
                              })
                            } else {
                              setSchedulingFormData({
                                ...schedulingFormData,
                                interviewerIds: schedulingFormData.interviewerIds.filter(id => id !== member.id)
                              })
                            }
                          }}
                          className="w-4 h-4 text-stone-900 rounded border-stone-300"
                        />
                        <div className="w-8 h-8 rounded-full bg-stone-100 flex items-center justify-center text-sm font-medium">
                          {member.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-stone-900">{member.name}</p>
                          <p className="text-xs text-stone-500">{member.email}</p>
                        </div>
                        {member.googleCalendarConnected && (
                          <span className="text-xs text-teal-600">Calendar connected</span>
                        )}
                      </label>
                    ))}
                  </div>

                  {schedulingTeamMembers.length === 0 && (
                    <p className="text-xs text-stone-400">
                      Tip: Add team members in Team tab to enable load balancing across multiple interviewers.
                    </p>
                  )}
                </div>
              )}

              {/* Step 3: Booking Settings (create mode only) */}
              {schedulingWizardStep === 3 && !editingSchedulingLink && (
                <div className="space-y-4">
                  <h3 className="font-medium text-stone-900">Booking Settings</h3>
                  <p className="text-sm text-stone-500">
                    Configure how far in advance candidates can book and buffer times between interviews.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="create-bufferBefore">Buffer Before (minutes)</Label>
                      <Input
                        id="create-bufferBefore"
                        type="number"
                        min={0}
                        max={60}
                        value={schedulingFormData.bufferBeforeMinutes}
                        onChange={e => setSchedulingFormData({ ...schedulingFormData, bufferBeforeMinutes: parseInt(e.target.value) || 0 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">Time before interview starts</p>
                    </div>
                    <div>
                      <Label htmlFor="create-bufferAfter">Buffer After (minutes)</Label>
                      <Input
                        id="create-bufferAfter"
                        type="number"
                        min={0}
                        max={60}
                        value={schedulingFormData.bufferAfterMinutes}
                        onChange={e => setSchedulingFormData({ ...schedulingFormData, bufferAfterMinutes: parseInt(e.target.value) || 0 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">Time after interview ends</p>
                    </div>
                    <div>
                      <Label htmlFor="create-minNotice">Minimum Notice (hours)</Label>
                      <Input
                        id="create-minNotice"
                        type="number"
                        min={1}
                        max={168}
                        value={schedulingFormData.minNoticeHours}
                        onChange={e => setSchedulingFormData({ ...schedulingFormData, minNoticeHours: parseInt(e.target.value) || 24 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">How far in advance to book</p>
                    </div>
                    <div>
                      <Label htmlFor="create-maxDays">Maximum Days Ahead</Label>
                      <Input
                        id="create-maxDays"
                        type="number"
                        min={1}
                        max={90}
                        value={schedulingFormData.maxDaysAhead}
                        onChange={e => setSchedulingFormData({ ...schedulingFormData, maxDaysAhead: parseInt(e.target.value) || 14 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">How far out candidates can book</p>
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="mt-6 p-4 bg-stone-50 rounded-lg border border-stone-100">
                    <h4 className="font-medium text-stone-900 mb-2">Summary</h4>
                    <ul className="text-sm text-stone-600 space-y-1">
                      <li><span className="text-stone-400">Name:</span> {schedulingFormData.name}</li>
                      <li><span className="text-stone-400">Duration:</span> {schedulingFormData.durationMinutes} minutes</li>
                      <li><span className="text-stone-400">Interviewers:</span> {schedulingFormData.interviewerIds.length} selected</li>
                      <li><span className="text-stone-400">Booking window:</span> {schedulingFormData.minNoticeHours}h notice, up to {schedulingFormData.maxDaysAhead} days ahead</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t flex justify-between">
              <div>
                {!editingSchedulingLink && schedulingWizardStep > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setSchedulingWizardStep(schedulingWizardStep - 1)}
                  >
                    Back
                  </Button>
                )}
              </div>

              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateSchedulingLinkModal(false)
                    setEditingSchedulingLink(null)
                    resetSchedulingForm()
                  }}
                >
                  Cancel
                </Button>

                {editingSchedulingLink ? (
                  <Button onClick={handleUpdateSchedulingLink} disabled={isSavingSchedulingLink || !schedulingFormData.name}>
                    {isSavingSchedulingLink ? 'Saving...' : 'Save Changes'}
                  </Button>
                ) : schedulingWizardStep < 3 ? (
                  <Button
                    onClick={() => setSchedulingWizardStep(schedulingWizardStep + 1)}
                    disabled={
                      (schedulingWizardStep === 1 && !schedulingFormData.name) ||
                      (schedulingWizardStep === 2 && schedulingFormData.interviewerIds.length === 0)
                    }
                  >
                    Next
                  </Button>
                ) : (
                  <Button onClick={handleCreateSchedulingLink} disabled={isSavingSchedulingLink}>
                    {isSavingSchedulingLink ? 'Creating...' : 'Create Link'}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Contact Modal */}
      {showContactModal && contactCandidate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Interview {contactCandidate.candidateName}</span>
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
                Send an interview invitation to {contactCandidate.candidateEmail}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Scheduling Link Selection */}
              <div className="bg-stone-50 border border-stone-200 rounded-lg p-4">
                <Label className="text-sm font-medium text-stone-700 mb-2 block flex items-center gap-2">
                  <svg className="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Include Scheduling Link
                </Label>
                {loadingSchedulingLinks ? (
                  <div className="flex items-center gap-2 text-sm text-stone-500">
                    <div className="w-4 h-4 border-2 border-stone-200 border-t-teal-500 rounded-full animate-spin" />
                    Loading scheduling links...
                  </div>
                ) : schedulingLinks.length > 0 ? (
                  <CustomSelect
                    value={selectedSchedulingLink}
                    onChange={handleSchedulingLinkChange}
                    options={[
                      { value: '', label: 'No scheduling link (just send message)' },
                      ...schedulingLinks.map(link => ({
                        value: link.id,
                        label: `${link.name} (${link.durationMinutes} min)`
                      }))
                    ]}
                  />
                ) : (
                  <div className="text-sm text-stone-500">
                    <p>No scheduling links available.</p>
                    <button
                      type="button"
                      onClick={() => {
                        setShowContactModal(false)
                        setActiveTab('scheduling')
                      }}
                      className="text-teal-600 hover:underline"
                    >
                      Create a scheduling link <svg className="inline w-3.5 h-3.5 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
                    </button>
                  </div>
                )}
                {selectedSchedulingLink && (
                  <p className="text-xs text-teal-600 mt-2 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Candidate will be able to pick a time from your availability and receive a Google Meet link
                  </p>
                )}
              </div>

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
                  rows={10}
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
                  {isSending ? 'Sending...' : selectedSchedulingLink ? 'Send with Scheduling Link' : 'Send Email'}
                </Button>
              </div>
              <p className="text-xs text-stone-500 text-center">
                {selectedSchedulingLink
                  ? 'The candidate will receive this email with a link to schedule an interview'
                  : 'The candidate will receive this email and their status will be updated to "Contacted"'}
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

      {/* Create Organization Modal */}
      {showCreateOrgModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Create Organization</span>
                <button
                  onClick={() => setShowCreateOrgModal(false)}
                  className="text-stone-400 hover:text-stone-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </CardTitle>
              <CardDescription>
                Create an organization for your company to enable team collaboration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium text-stone-700 mb-1 block">Organization Name</Label>
                <Input
                  type="text"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  placeholder="e.g. Acme Corp"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowCreateOrgModal(false)}
                  disabled={isCreatingOrg}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-teal-600 hover:bg-teal-700"
                  onClick={handleCreateOrganization}
                  disabled={isCreatingOrg || !newOrgName.trim()}
                >
                  {isCreatingOrg ? 'Creating...' : 'Create'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Invite Member Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Invite Team Member</span>
                <button
                  onClick={() => setShowInviteModal(false)}
                  className="text-stone-400 hover:text-stone-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </CardTitle>
              <CardDescription>
                Send an invitation to join your organization
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium text-stone-700 mb-1 block">Email Address</Label>
                <Input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@company.com"
                />
              </div>
              <div>
                <Label className="text-sm font-medium text-stone-700 mb-1 block">Role</Label>
                <CustomSelect
                  value={inviteRole}
                  onChange={setInviteRole}
                  options={[
                    { value: 'admin', label: 'Admin' },
                    { value: 'recruiter', label: 'Recruiter' },
                    { value: 'hiring_manager', label: 'Hiring Manager' },
                    { value: 'interviewer', label: 'Interviewer' },
                  ]}
                />
                <p className="text-xs text-stone-500 mt-1">
                  {inviteRole === 'admin' && 'Can manage team members, jobs, and all candidates'}
                  {inviteRole === 'recruiter' && 'Can create jobs, review candidates, and send invites'}
                  {inviteRole === 'hiring_manager' && 'Can review candidates for assigned jobs'}
                  {inviteRole === 'interviewer' && 'Can view assigned candidates and leave feedback'}
                </p>
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowInviteModal(false)}
                  disabled={isInviting}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-teal-600 hover:bg-teal-700"
                  onClick={handleInviteMember}
                  disabled={isInviting || !inviteEmail.trim()}
                >
                  {isInviting ? 'Sending...' : 'Send Invite'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Transcript Preview Modal */}
      {showTranscriptModal && transcriptData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-4xl max-h-[90vh] bg-white rounded-xl shadow-2xl flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200">
              <div className="flex items-center gap-3">
                <svg className="w-6 h-6 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-semibold text-stone-900">{transcriptCandidateName}&apos;s Interview</h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => downloadTranscript(transcriptData, transcriptCandidateName)}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-stone-700 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download
                </button>
                <button
                  onClick={() => setShowTranscriptModal(false)}
                  className="p-2 text-stone-400 hover:text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
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
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-teal-50 text-teal-700">
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
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {transcriptData.interview.overallStrengths && transcriptData.interview.overallStrengths.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-teal-700 mb-1">Strengths</p>
                              <ul className="space-y-1">
                                {transcriptData.interview.overallStrengths.map((s, i) => (
                                  <li key={i} className="text-xs text-stone-600 flex items-start gap-1">
                                    <span className="text-teal-600 mt-0.5">+</span>
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
