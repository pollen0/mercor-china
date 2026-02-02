'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { talentPoolApi, employerApi, type TalentPoolCandidate, type TalentProfileDetail, type Vertical, type RoleType } from '@/lib/api'

// 2026 simplified verticals based on job market
const VERTICALS = [
  { value: 'software_engineering', label: 'Software Engineering' },
  { value: 'data', label: 'Data & Analytics' },
  { value: 'product', label: 'Product Management' },
  { value: 'design', label: 'Design' },
  { value: 'finance', label: 'Finance & IB' },
]

const ROLES_BY_VERTICAL: Record<string, Array<{ value: string; label: string }>> = {
  software_engineering: [
    { value: 'software_engineer', label: 'Software Engineer' },
    { value: 'embedded_engineer', label: 'Embedded Engineer' },
    { value: 'qa_engineer', label: 'QA Engineer' },
  ],
  data: [
    { value: 'data_analyst', label: 'Data Analyst' },
    { value: 'data_scientist', label: 'Data Scientist' },
    { value: 'ml_engineer', label: 'ML Engineer' },
    { value: 'data_engineer', label: 'Data Engineer' },
  ],
  product: [
    { value: 'product_manager', label: 'Product Manager' },
    { value: 'associate_pm', label: 'Associate PM' },
  ],
  design: [
    { value: 'ux_designer', label: 'UX Designer' },
    { value: 'ui_designer', label: 'UI Designer' },
    { value: 'product_designer', label: 'Product Designer' },
  ],
  finance: [
    { value: 'ib_analyst', label: 'IB Analyst' },
    { value: 'finance_analyst', label: 'Finance Analyst' },
    { value: 'equity_research', label: 'Equity Research' },
  ],
}

const ROLE_NAMES: Record<string, string> = {
  // Software Engineering
  software_engineer: 'Software Engineer',
  embedded_engineer: 'Embedded Engineer',
  qa_engineer: 'QA Engineer',
  // Legacy engineering roles
  frontend_engineer: 'Frontend Engineer',
  backend_engineer: 'Backend Engineer',
  fullstack_engineer: 'Full Stack Engineer',
  mobile_engineer: 'Mobile Engineer',
  devops_engineer: 'DevOps Engineer',
  // Data
  data_analyst: 'Data Analyst',
  data_scientist: 'Data Scientist',
  ml_engineer: 'ML Engineer',
  data_engineer: 'Data Engineer',
  // Product
  product_manager: 'Product Manager',
  associate_pm: 'Associate PM',
  business_analyst: 'Business Analyst',
  // Design
  ux_designer: 'UX Designer',
  ui_designer: 'UI Designer',
  product_designer: 'Product Designer',
  // Finance
  ib_analyst: 'IB Analyst',
  finance_analyst: 'Finance Analyst',
  equity_research: 'Equity Research',
}

export default function TalentPoolPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [candidates, setCandidates] = useState<TalentPoolCandidate[]>([])
  const [total, setTotal] = useState(0)
  const [companyName, setCompanyName] = useState<string>('')

  // Filters
  const [selectedVertical, setSelectedVertical] = useState<Vertical | ''>('')
  const [selectedRole, setSelectedRole] = useState<RoleType | ''>('')
  const [minScore, setMinScore] = useState<number>(0)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [searchInput, setSearchInput] = useState<string>('')

  // Expandable rows
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [expandedData, setExpandedData] = useState<Record<string, TalentProfileDetail>>({})
  const [loadingDetail, setLoadingDetail] = useState<string | null>(null)

  // Contact modal
  const [showContactModal, setShowContactModal] = useState(false)
  const [contactCandidate, setContactCandidate] = useState<TalentPoolCandidate | null>(null)
  const [contactSubject, setContactSubject] = useState('')
  const [contactMessage, setContactMessage] = useState('')
  const [isSending, setIsSending] = useState(false)

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 12

  useEffect(() => {
    // Check if employer is logged in
    const token = localStorage.getItem('employer_token')
    if (!token) {
      router.push('/login')
      return
    }

    // Get company name
    employerApi.getMe().then(employer => {
      setCompanyName(employer.companyName || '')
    }).catch(() => {})

    fetchCandidates()
  }, [selectedVertical, selectedRole, minScore, searchQuery, currentPage])

  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    router.push('/login')
  }

  const fetchCandidates = async () => {
    setIsLoading(true)
    try {
      const data = await talentPoolApi.browse({
        vertical: selectedVertical || undefined,
        roleType: selectedRole || undefined,
        minScore: minScore || undefined,
        search: searchQuery || undefined,
        limit: pageSize,
        offset: (currentPage - 1) * pageSize,
      })
      setCandidates(data.candidates)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch talent pool:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearchQuery(searchInput)
    setCurrentPage(1)
  }

  const toggleExpand = async (candidate: TalentPoolCandidate) => {
    const id = candidate.profileId || candidate.candidateId

    if (expandedId === id) {
      // Collapse
      setExpandedId(null)
      return
    }

    // Expand and load details if not cached
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
    setContactSubject(`Interview Opportunity at ${companyName}`)
    const roleDisplay = candidate.roleType ? (ROLE_NAMES[candidate.roleType] || candidate.roleType) : 'open'
    setContactMessage(`Dear ${candidate.candidateName},

We reviewed your profile on Pathway and were impressed by your qualifications for ${roleDisplay} positions.

We would like to discuss a potential opportunity with you. Would you be available for a conversation?

Best regards,
${companyName}`)
    setShowContactModal(true)
  }

  const sendContactEmail = async () => {
    if (!contactCandidate || !contactSubject.trim() || !contactMessage.trim()) return

    setIsSending(true)
    try {
      // Use profileId if available, otherwise use candidateId
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

  const handleVerticalChange = (value: string) => {
    setSelectedVertical(value as Vertical | '')
    setSelectedRole('')  // Reset role when vertical changes
    setCurrentPage(1)
  }

  const handleRoleChange = (value: string) => {
    setSelectedRole(value as RoleType | '')
    setCurrentPage(1)
  }

  const handleMinScoreChange = (value: number) => {
    setMinScore(value)
    setCurrentPage(1)
  }

  const availableRoles = selectedVertical ? ROLES_BY_VERTICAL[selectedVertical] || [] : []
  const totalPages = Math.ceil(total / pageSize)

  return (
    <PageWrapper>
      <DashboardNavbar companyName={companyName} onLogout={handleLogout} />

      <Container className="py-8 pt-24">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Talent Pool</h1>
          <p className="text-gray-500">Browse candidates with their resumes, GitHub profiles, and interview scores</p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-6">
          <CardContent className="py-4">
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="mb-4">
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Search by name, skills, company, keywords..."
                    className="w-full px-4 py-2 pl-10 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  />
                  <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <Button type="submit" variant="brand">
                  Search
                </Button>
              </div>
            </form>

            <div className="flex flex-wrap gap-4 items-end">
              {/* Vertical Filter */}
              <div className="w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry Vertical
                </label>
                <select
                  value={selectedVertical}
                  onChange={(e) => handleVerticalChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="">All Verticals</option>
                  {VERTICALS.map((v) => (
                    <option key={v.value} value={v.value}>
                      {v.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Role Filter */}
              <div className="w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role Type
                </label>
                <select
                  value={selectedRole}
                  onChange={(e) => handleRoleChange(e.target.value)}
                  disabled={!selectedVertical}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 disabled:bg-gray-50"
                >
                  <option value="">All Roles</option>
                  {availableRoles.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Min Score Filter */}
              <div className="w-40">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Score
                </label>
                <select
                  value={minScore}
                  onChange={(e) => handleMinScoreChange(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value={0}>Any Score</option>
                  <option value={5}>5+ / 10</option>
                  <option value={6}>6+ / 10</option>
                  <option value={7}>7+ / 10</option>
                  <option value={8}>8+ / 10</option>
                </select>
              </div>

              {/* Clear Filters */}
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedVertical('')
                  setSelectedRole('')
                  setMinScore(0)
                  setSearchInput('')
                  setSearchQuery('')
                  setCurrentPage(1)
                }}
              >
                Clear All
              </Button>
            </div>

            {/* Active Search Tag */}
            {searchQuery && (
              <div className="mt-3 flex items-center gap-2">
                <span className="text-sm text-gray-600">Searching:</span>
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-teal-100 text-teal-700 rounded-full text-sm">
                  "{searchQuery}"
                  <button
                    onClick={() => {
                      setSearchInput('')
                      setSearchQuery('')
                      setCurrentPage(1)
                    }}
                    className="ml-1 hover:text-teal-900"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-600">
            {total} candidate{total !== 1 ? 's' : ''} found
          </p>
        </div>

        {/* Candidates List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-12 h-12 border-2 border-gray-200 border-t-teal-500 rounded-full animate-spin"></div>
          </div>
        ) : candidates.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No candidates found</h3>
              <p className="text-gray-500">
                Try adjusting your filters or check back later for new candidates.
              </p>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Expandable row-based candidate list */}
            <Card className="mb-6">
              <div className="divide-y divide-gray-100">
                {candidates.map((candidate) => {
                  // Determine the score to display (interview > profile)
                  const displayScore = candidate.bestScore ?? candidate.profileScore
                  const isProfileOnly = candidate.status === 'profile_only' || candidate.status === 'pending' || candidate.status === 'in_progress'
                  const rowId = candidate.profileId || candidate.candidateId
                  const isExpanded = expandedId === rowId
                  const detail = expandedData[rowId]

                  return (
                    <div key={rowId}>
                      {/* Main Row */}
                      <div
                        className={`p-4 cursor-pointer transition-colors ${isExpanded ? 'bg-teal-50' : 'hover:bg-gray-50'}`}
                        onClick={() => toggleExpand(candidate)}
                      >
                        <div className="flex items-center gap-4">
                          {/* Expand/Collapse Icon */}
                          <div className="flex-shrink-0 w-6">
                            <svg
                              className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
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
                              <h3 className="font-medium text-gray-900 truncate">{candidate.candidateName}</h3>
                              {/* Completion Status Badges */}
                              {candidate.completionStatus?.interviewCompleted && (
                                <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                  Interview
                                </span>
                              )}
                              {candidate.completionStatus?.resumeUploaded && (
                                <span className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">Resume</span>
                              )}
                              {candidate.completionStatus?.githubConnected && (
                                <span className="px-1.5 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">GitHub</span>
                              )}
                              {!candidate.completionStatus?.interviewCompleted && (
                                <span className="px-1.5 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded-full">No Interview</span>
                              )}
                            </div>
                            <div className="flex items-center gap-3 mt-0.5">
                              {candidate.vertical && (
                                <span className="text-xs text-gray-600">
                                  {VERTICALS.find(v => v.value === candidate.vertical)?.label || candidate.vertical}
                                </span>
                              )}
                              {candidate.roleType && (
                                <span className="text-xs text-gray-500">
                                  {ROLE_NAMES[candidate.roleType] || candidate.roleType}
                                </span>
                              )}
                              {candidate.location && (
                                <span className="text-xs text-gray-400">{candidate.location}</span>
                              )}
                            </div>
                          </div>

                          {/* Skills */}
                          <div className="hidden md:flex flex-wrap gap-1 max-w-xs">
                            {candidate.skills.slice(0, 3).map((skill, i) => (
                              <span
                                key={i}
                                className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                              >
                                {skill}
                              </span>
                            ))}
                            {candidate.skills.length > 3 && (
                              <span className="text-xs text-gray-400">+{candidate.skills.length - 3}</span>
                            )}
                          </div>

                          {/* Score */}
                          <div className="text-center w-16 flex-shrink-0">
                            {displayScore ? (
                              <>
                                <div className={`text-lg font-bold ${isProfileOnly ? 'text-blue-600' : 'text-teal-600'}`}>
                                  {displayScore.toFixed(1)}
                                </div>
                                <div className="text-xs text-gray-400">
                                  {isProfileOnly ? 'profile' : 'score'}
                                </div>
                              </>
                            ) : (
                              <div className="text-xs text-gray-400">-</div>
                            )}
                          </div>

                          {/* Contact Button */}
                          <div className="flex-shrink-0">
                            <Button
                              size="sm"
                              variant="brand"
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
                        <div className="bg-gray-50 border-t border-gray-100 px-4 py-4">
                          {loadingDetail === rowId ? (
                            <div className="flex items-center justify-center py-8">
                              <div className="w-8 h-8 border-2 border-gray-200 border-t-teal-500 rounded-full animate-spin"></div>
                            </div>
                          ) : detail ? (
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                              {/* Left: Contact & Basic Info */}
                              <div className="space-y-4">
                                <div>
                                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Contact Info</h4>
                                  <div className="space-y-1 text-sm">
                                    <p><span className="text-gray-500">Email:</span> {detail.candidate.email}</p>
                                    {detail.candidate.phone && (
                                      <p><span className="text-gray-500">Phone:</span> {detail.candidate.phone}</p>
                                    )}
                                    {detail.candidate.university && (
                                      <p><span className="text-gray-500">University:</span> {detail.candidate.university}</p>
                                    )}
                                    {detail.candidate.major && (
                                      <p><span className="text-gray-500">Major:</span> {detail.candidate.major}</p>
                                    )}
                                    {detail.candidate.graduationYear && (
                                      <p><span className="text-gray-500">Graduation:</span> {detail.candidate.graduationYear}</p>
                                    )}
                                    {detail.candidate.gpa && (
                                      <p><span className="text-gray-500">GPA:</span> {detail.candidate.gpa.toFixed(2)}</p>
                                    )}
                                  </div>
                                </div>

                                {/* Score Breakdown */}
                                {(detail.profileScore || detail.profile?.bestScore) && (
                                  <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Score Breakdown</h4>
                                    <div className="space-y-1">
                                      {detail.profileScore?.breakdown && Object.entries(detail.profileScore.breakdown).map(([key, value]) => {
                                        // Convert camelCase to Title Case with spaces
                                        const label = key
                                          .replace(/([A-Z])/g, ' $1')
                                          .replace(/^./, str => str.toUpperCase())
                                          .trim()
                                        return (
                                          <div key={key} className="flex items-center gap-2">
                                            <span className="text-xs text-gray-500 w-28">{label}</span>
                                            <div className="flex-1 h-2 bg-gray-200 rounded-full">
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

                                {/* Pros & Cons */}
                                {(detail.profileScore?.strengths?.length > 0 || detail.profileScore?.concerns?.length > 0) && (
                                  <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Assessment</h4>
                                    <div className="space-y-2">
                                      {detail.profileScore?.strengths?.length > 0 && (
                                        <div>
                                          <p className="text-xs font-medium text-green-700 mb-1">Strengths</p>
                                          <ul className="space-y-0.5">
                                            {detail.profileScore.strengths.slice(0, 3).map((s: string, i: number) => (
                                              <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                                                <span className="text-green-500 mt-0.5">+</span>
                                                <span>{s}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                      {detail.profileScore?.concerns?.length > 0 && (
                                        <div>
                                          <p className="text-xs font-medium text-amber-700 mb-1">Areas to Explore</p>
                                          <ul className="space-y-0.5">
                                            {detail.profileScore.concerns.slice(0, 3).map((c: string, i: number) => (
                                              <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                                                <span className="text-amber-500 mt-0.5">•</span>
                                                <span>{c}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Middle: Skills & Experience */}
                              <div className="space-y-4">
                                {detail.candidate.resumeData?.skills && detail.candidate.resumeData.skills.length > 0 && (
                                  <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Skills</h4>
                                    <div className="flex flex-wrap gap-1">
                                      {detail.candidate.resumeData.skills.slice(0, 15).map((skill, i) => (
                                        <span key={i} className="px-2 py-1 text-xs bg-white border border-gray-200 text-gray-700 rounded">
                                          {skill}
                                        </span>
                                      ))}
                                      {detail.candidate.resumeData.skills.length > 15 && (
                                        <span className="text-xs text-gray-400">+{detail.candidate.resumeData.skills.length - 15} more</span>
                                      )}
                                    </div>
                                  </div>
                                )}

                                {detail.candidate.resumeData?.experience && detail.candidate.resumeData.experience.length > 0 && (
                                  <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Experience</h4>
                                    <div className="space-y-2">
                                      {detail.candidate.resumeData.experience.slice(0, 2).map((exp, i) => (
                                        <div key={i} className="text-sm">
                                          <p className="font-medium text-gray-900">{exp.title}</p>
                                          <p className="text-gray-500">{exp.company}</p>
                                          {exp.startDate && (
                                            <p className="text-xs text-gray-400">
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
                                    <h4 className="text-sm font-semibold text-gray-700 mb-2">GitHub</h4>
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
                                      <div className="mt-2 text-xs text-gray-500">
                                        <p>{detail.candidate.githubData.publicRepos} repos • {detail.candidate.githubData.followers} followers</p>
                                      </div>
                                    )}
                                  </div>
                                )}

                                {detail.candidate.resumeData?.projects && detail.candidate.resumeData.projects.length > 0 && (
                                  <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Projects</h4>
                                    <div className="space-y-2">
                                      {detail.candidate.resumeData.projects.slice(0, 2).map((project, i) => (
                                        <div key={i} className="text-sm">
                                          <p className="font-medium text-gray-900">{project.name}</p>
                                          {project.description && (
                                            <p className="text-gray-500 text-xs line-clamp-2">{project.description}</p>
                                          )}
                                          {project.technologies && project.technologies.length > 0 && (
                                            <div className="flex flex-wrap gap-1 mt-1">
                                              {project.technologies.slice(0, 4).map((tech, j) => (
                                                <span key={j} className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
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

                                {detail.candidate.resumeUrl && (
                                  <div>
                                    <a
                                      href={detail.candidate.resumeUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center gap-2 text-sm text-teal-600 hover:text-teal-700"
                                      onClick={(e) => e.stopPropagation()}
                                    >
                                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                      </svg>
                                      Download Resume
                                    </a>
                                  </div>
                                )}
                              </div>
                            </div>
                          ) : (
                            <p className="text-sm text-gray-500 text-center py-4">Failed to load details</p>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </Card>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(p => p - 1)}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-600">
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(p => p + 1)}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </Container>

      {/* Contact Modal */}
      {showContactModal && contactCandidate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Contact {contactCandidate.candidateName}</span>
                <button
                  onClick={() => setShowContactModal(false)}
                  className="text-gray-400 hover:text-gray-600"
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
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject
                </label>
                <input
                  type="text"
                  value={contactSubject}
                  onChange={(e) => setContactSubject(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  placeholder="Email subject..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Message
                </label>
                <textarea
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
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
                  variant="brand"
                  className="flex-1"
                  onClick={sendContactEmail}
                  disabled={isSending || !contactSubject.trim() || !contactMessage.trim()}
                >
                  {isSending ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Sending...
                    </>
                  ) : (
                    'Send Email'
                  )}
                </Button>
              </div>
              <p className="text-xs text-gray-500 text-center">
                The candidate will receive this email and their status will be updated to "Contacted"
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </PageWrapper>
  )
}
