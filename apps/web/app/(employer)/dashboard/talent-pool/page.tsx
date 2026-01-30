'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { talentPoolApi, employerApi, type TalentPoolCandidate, type Vertical, type RoleType } from '@/lib/api'

// Vertical and role configurations
const VERTICALS = [
  { value: 'new_energy', label: 'New Energy / EV', labelZh: '新能源 / 电动汽车' },
  { value: 'sales', label: 'Sales / BD', labelZh: '销售 / 商务拓展' },
]

const ROLES_BY_VERTICAL: Record<string, Array<{ value: string; label: string; labelZh: string }>> = {
  new_energy: [
    { value: 'battery_engineer', label: 'Battery Engineer', labelZh: '电池工程师' },
    { value: 'embedded_software', label: 'Embedded Software', labelZh: '嵌入式软件' },
    { value: 'autonomous_driving', label: 'Autonomous Driving', labelZh: '自动驾驶' },
    { value: 'supply_chain', label: 'Supply Chain', labelZh: '供应链' },
    { value: 'ev_sales', label: 'EV Sales', labelZh: '新能源销售' },
  ],
  sales: [
    { value: 'sales_rep', label: 'Sales Rep', labelZh: '销售代表' },
    { value: 'bd_manager', label: 'BD Manager', labelZh: '商务拓展' },
    { value: 'account_manager', label: 'Account Manager', labelZh: '客户经理' },
  ],
}

const ROLE_NAMES: Record<string, string> = {
  battery_engineer: '电池工程师',
  embedded_software: '嵌入式软件',
  autonomous_driving: '自动驾驶',
  supply_chain: '供应链',
  ev_sales: '新能源销售',
  sales_rep: '销售代表',
  bd_manager: '商务拓展',
  account_manager: '客户经理',
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

  const openContactModal = (candidate: TalentPoolCandidate) => {
    setContactCandidate(candidate)
    setContactSubject(`Interview Opportunity at ${companyName}`)
    setContactMessage(`Dear ${candidate.candidateName},

We reviewed your profile on ZhiMian and were impressed by your qualifications for ${ROLE_NAMES[candidate.roleType] || candidate.roleType} positions.

We would like to discuss a potential opportunity with you. Would you be available for a conversation?

Best regards,
${companyName}`)
    setShowContactModal(true)
  }

  const sendContactEmail = async () => {
    if (!contactCandidate || !contactSubject.trim() || !contactMessage.trim()) return

    setIsSending(true)
    try {
      await talentPoolApi.contactCandidate(contactCandidate.profileId, {
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
          <h1 className="text-2xl sm:text-3xl font-bold text-warm-900">Talent Pool</h1>
          <p className="text-warm-500">Browse candidates who have completed vertical interviews</p>
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
                    className="w-full px-4 py-2 pl-10 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                  />
                  <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Industry Vertical
                </label>
                <select
                  value={selectedVertical}
                  onChange={(e) => handleVerticalChange(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                >
                  <option value="">All Verticals</option>
                  {VERTICALS.map((v) => (
                    <option key={v.value} value={v.value}>
                      {v.labelZh}
                    </option>
                  ))}
                </select>
              </div>

              {/* Role Filter */}
              <div className="w-48">
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Role Type
                </label>
                <select
                  value={selectedRole}
                  onChange={(e) => handleRoleChange(e.target.value)}
                  disabled={!selectedVertical}
                  className="w-full px-3 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 disabled:bg-warm-50"
                >
                  <option value="">All Roles</option>
                  {availableRoles.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.labelZh}
                    </option>
                  ))}
                </select>
              </div>

              {/* Min Score Filter */}
              <div className="w-40">
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Min Score
                </label>
                <select
                  value={minScore}
                  onChange={(e) => handleMinScoreChange(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
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
                <span className="text-sm text-warm-600">Searching:</span>
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-brand-100 text-brand-700 rounded-full text-sm">
                  "{searchQuery}"
                  <button
                    onClick={() => {
                      setSearchInput('')
                      setSearchQuery('')
                      setCurrentPage(1)
                    }}
                    className="ml-1 hover:text-brand-900"
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
          <p className="text-sm text-warm-600">
            {total} candidate{total !== 1 ? 's' : ''} found
          </p>
        </div>

        {/* Candidates Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-12 h-12 border-2 border-warm-200 border-t-brand-500 rounded-full animate-spin"></div>
          </div>
        ) : candidates.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-warm-900 mb-2">No candidates found</h3>
              <p className="text-warm-500">
                Try adjusting your filters or check back later for new candidates.
              </p>
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
                        <div className="text-2xl font-bold text-brand-600">
                          {candidate.bestScore?.toFixed(1)}
                        </div>
                        <div className="text-xs text-warm-500">/ 10</div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {/* Vertical & Role */}
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          candidate.vertical === 'new_energy'
                            ? 'bg-brand-100 text-brand-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {VERTICALS.find(v => v.value === candidate.vertical)?.labelZh || candidate.vertical}
                        </span>
                        <span className="text-xs text-warm-500">
                          {ROLE_NAMES[candidate.roleType] || candidate.roleType}
                        </span>
                      </div>

                      {/* Location */}
                      {candidate.location && (
                        <p className="text-sm text-warm-600 flex items-center gap-1">
                          <span>📍</span> {candidate.location}
                        </p>
                      )}

                      {/* Experience */}
                      {candidate.experienceSummary && (
                        <p className="text-sm text-warm-600 truncate">
                          💼 {candidate.experienceSummary}
                        </p>
                      )}

                      {/* Skills */}
                      {candidate.skills.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {candidate.skills.slice(0, 4).map((skill, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 text-xs bg-warm-100 text-warm-600 rounded"
                            >
                              {skill}
                            </span>
                          ))}
                          {candidate.skills.length > 4 && (
                            <span className="px-2 py-0.5 text-xs text-warm-400">
                              +{candidate.skills.length - 4}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-2 pt-2 border-t border-warm-100">
                        <Link href={`/dashboard/talent-pool/${candidate.profileId}`} className="flex-1">
                          <Button variant="outline" size="sm" className="w-full">
                            View Profile
                          </Button>
                        </Link>
                        <Button
                          size="sm"
                          variant="brand"
                          className="flex-1"
                          onClick={() => openContactModal(candidate)}
                        >
                          Contact
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

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
                <span className="text-sm text-warm-600">
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
                  className="text-warm-400 hover:text-warm-600"
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
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Subject
                </label>
                <input
                  type="text"
                  value={contactSubject}
                  onChange={(e) => setContactSubject(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                  placeholder="Email subject..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Message
                </label>
                <textarea
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-none"
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
              <p className="text-xs text-warm-500 text-center">
                The candidate will receive this email and their status will be updated to "Contacted"
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </PageWrapper>
  )
}
