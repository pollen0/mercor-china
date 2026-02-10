'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AdminNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { CustomSelect } from '@/components/ui/custom-select'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AdminStats {
  total_candidates: number
  verified_candidates: number
  total_employers: number
  verified_employers: number
  total_jobs: number
  active_jobs: number
  total_interviews: number
  completed_interviews: number
  total_matches: number
  hired_count: number
  new_candidates_7d: number
  new_employers_7d: number
  new_interviews_7d: number
  avg_interviews_per_candidate?: number
  by_vertical?: Record<string, number>
  candidates_with_github?: number
  candidates_with_resume?: number
}

interface CandidateAdmin {
  id: string
  name: string
  email: string
  phone: string
  email_verified: boolean
  interview_count: number
  vertical_profile_count: number
  has_resume: boolean
  has_github: boolean
  has_transcript: boolean
  created_at: string
}

interface EmployerAdmin {
  id: string
  company_name: string
  email: string
  is_verified: boolean
  job_count: number
  created_at: string
}

interface University {
  id: string
  name: string
  short_name: string
  tier: number
  cs_ranking?: number
}

interface Course {
  id: string
  university_id: string
  department: string
  number: string
  name: string
  difficulty_tier: number
  difficulty_score: number
  typical_gpa?: number
  is_curved: boolean
  course_type: string
  is_technical: boolean
  is_weeder: boolean
  is_proof_based: boolean
  has_coding: boolean
  units: number
  description?: string
  confidence: number
  source?: string
}

interface CourseStats {
  total_courses: number
  total_universities: number
  by_difficulty_tier: Record<string, number>
}

interface ClubAdmin {
  id: string
  university_id: string
  name: string
  short_name?: string
  category: string
  prestige_tier: number
  prestige_score: number
  is_selective: boolean
  acceptance_rate?: number
  is_technical: boolean
  is_professional: boolean
  has_projects: boolean
  has_competitions: boolean
  is_honor_society: boolean
  description?: string
}

interface UniversityDetail {
  id: string
  name: string
  short_name: string
  gpa_scale: number
  uses_plus_minus: boolean
  tier: number
  cs_ranking?: number
  course_count: number
  club_count: number
}

type Tab = 'overview' | 'candidates' | 'employers' | 'universities' | 'courses' | 'clubs' | 'referrals'

export default function AdminPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('overview')

  // Data
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [candidates, setCandidates] = useState<CandidateAdmin[]>([])
  const [employers, setEmployers] = useState<EmployerAdmin[]>([])
  const [candidateTotal, setCandidateTotal] = useState(0)
  const [employerTotal, setEmployerTotal] = useState(0)

  // Search and sorting
  const [searchQuery, setSearchQuery] = useState('')
  const [candidateSort, setCandidateSort] = useState<{ field: string; dir: 'asc' | 'desc' }>({ field: 'created_at', dir: 'desc' })
  const [employerSort, setEmployerSort] = useState<{ field: string; dir: 'asc' | 'desc' }>({ field: 'created_at', dir: 'desc' })
  const [candidateFilter, setCandidateFilter] = useState<'all' | 'verified' | 'unverified'>('all')
  const [employerFilter, setEmployerFilter] = useState<'all' | 'verified' | 'unverified'>('all')

  // Admin password
  const [adminPassword, setAdminPassword] = useState<string | null>(null)
  const [passwordInput, setPasswordInput] = useState('')
  const [showPasswordPrompt, setShowPasswordPrompt] = useState(false)

  // Course management state
  const [universities, setUniversities] = useState<University[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [courseStats, setCourseStats] = useState<CourseStats | null>(null)
  const [selectedUniversity, setSelectedUniversity] = useState<string>('')
  const [selectedDepartment, setSelectedDepartment] = useState<string>('')
  const [editingCourse, setEditingCourse] = useState<Course | null>(null)
  const [showAddCourse, setShowAddCourse] = useState(false)

  // University details state
  const [universityDetails, setUniversityDetails] = useState<UniversityDetail[]>([])

  // Club management state
  const [clubs, setClubs] = useState<ClubAdmin[]>([])
  const [clubTotal, setClubTotal] = useState(0)
  const [selectedClubCategory, setSelectedClubCategory] = useState<string>('')
  const [clubPrestigeFilter, setClubPrestigeFilter] = useState<number | ''>('')
  const [selectedClubUniversity, setSelectedClubUniversity] = useState<string>('')

  // Referral state
  const [referralData, setReferralData] = useState<{ referrals: any[]; total: number }>({ referrals: [], total: 0 })
  const [referralLeaderboard, setReferralLeaderboard] = useState<any[]>([])
  const [referralStats, setReferralStats] = useState<any>(null)
  const [referralStatusFilter, setReferralStatusFilter] = useState<string>('')

  // Nudge dropdown state
  const [openNudgeDropdown, setOpenNudgeDropdown] = useState<string | null>(null)
  const [sendingNudge, setSendingNudge] = useState<string | null>(null)

  useEffect(() => {
    // Admin only requires password - no employer login needed
    const storedPassword = localStorage.getItem('admin_password')
    if (storedPassword) {
      setAdminPassword(storedPassword)
    } else {
      setShowPasswordPrompt(true)
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (adminPassword) {
      fetchStats()
    }
  }, [adminPassword])

  useEffect(() => {
    if (!adminPassword) return

    if (activeTab === 'candidates') {
      fetchCandidates()
    } else if (activeTab === 'employers') {
      fetchEmployers()
    } else if (activeTab === 'universities') {
      fetchUniversityDetails()
    } else if (activeTab === 'courses') {
      fetchUniversities()
      fetchCourses()
      fetchCourseStats()
    } else if (activeTab === 'clubs') {
      fetchClubs()
    } else if (activeTab === 'referrals') {
      fetchReferrals()
      fetchReferralLeaderboard()
      fetchReferralStats()
    }
  }, [activeTab, searchQuery, selectedUniversity, selectedDepartment, adminPassword, candidateSort, employerSort, candidateFilter, employerFilter, selectedClubCategory, clubPrestigeFilter, selectedClubUniversity, referralStatusFilter])

  const getAuthHeaders = () => {
    const password = adminPassword || localStorage.getItem('admin_password')
    return {
      'Content-Type': 'application/json',
      'X-Admin-Password': password || '',
    }
  }

  const handlePasswordSubmit = () => {
    if (passwordInput) {
      localStorage.setItem('admin_password', passwordInput)
      setAdminPassword(passwordInput)
      setShowPasswordPrompt(false)
      setError(null)
    }
  }

  const clearAdminPassword = () => {
    localStorage.removeItem('admin_password')
    setAdminPassword(null)
    setShowPasswordPrompt(true)
  }

  const fetchStats = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
        headers: getAuthHeaders(),
      })

      if (response.status === 403) {
        localStorage.removeItem('admin_password')
        setAdminPassword(null)
        setShowPasswordPrompt(true)
        setError('Invalid admin password. Please try again.')
        setIsLoading(false)
        return
      }

      if (!response.ok) {
        throw new Error('Failed to fetch stats')
      }

      const data = await response.json()
      setStats(data)
      setError(null)
    } catch (err) {
      setError('Failed to load admin data')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchCandidates = async () => {
    try {
      const params = new URLSearchParams()
      if (searchQuery) params.set('search', searchQuery)
      params.set('limit', '50')

      const response = await fetch(`${API_BASE_URL}/api/admin/candidates?${params}`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) throw new Error('Failed to fetch candidates')

      const data = await response.json()
      setCandidates(data.users)
      setCandidateTotal(data.total)
    } catch (err) {
      console.error('Failed to fetch candidates:', err)
    }
  }

  const fetchEmployers = async () => {
    try {
      const params = new URLSearchParams()
      if (searchQuery) params.set('search', searchQuery)
      params.set('limit', '50')

      const response = await fetch(`${API_BASE_URL}/api/admin/employers?${params}`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) throw new Error('Failed to fetch employers')

      const data = await response.json()
      setEmployers(data.users)
      setEmployerTotal(data.total)
    } catch (err) {
      console.error('Failed to fetch employers:', err)
    }
  }

  const fetchUniversities = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/courses/universities`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setUniversities(data)
      }
    } catch (err) {
      console.error('Failed to fetch universities:', err)
    }
  }

  const fetchCourses = async () => {
    try {
      const params = new URLSearchParams()
      if (selectedUniversity) params.set('university_id', selectedUniversity)
      if (selectedDepartment) params.set('department', selectedDepartment)
      params.set('limit', '100')

      const response = await fetch(`${API_BASE_URL}/api/courses/courses?${params}`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setCourses(data)
      }
    } catch (err) {
      console.error('Failed to fetch courses:', err)
    }
  }

  const fetchCourseStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/courses/admin/courses/stats`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setCourseStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch course stats:', err)
    }
  }

  const fetchUniversityDetails = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/courses/universities/detailed`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setUniversityDetails(data)
      }
    } catch (err) {
      console.error('Failed to fetch university details:', err)
    }
  }

  const fetchClubs = async () => {
    try {
      const params = new URLSearchParams()
      if (selectedClubCategory) params.set('category', selectedClubCategory)
      if (clubPrestigeFilter) params.set('min_prestige', String(clubPrestigeFilter))
      if (selectedClubUniversity) params.set('university_id', selectedClubUniversity)
      params.set('limit', '500')

      const response = await fetch(`${API_BASE_URL}/api/activities/clubs?${params}`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setClubs(data)
        setClubTotal(data.length)
      }
    } catch (err) {
      console.error('Failed to fetch clubs:', err)
    }
  }


  const fetchReferrals = async () => {
    try {
      const params = new URLSearchParams()
      if (referralStatusFilter) params.set('status_filter', referralStatusFilter)
      params.set('limit', '200')
      const response = await fetch(`${API_BASE_URL}/api/admin/referrals?${params}`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setReferralData(data)
      }
    } catch (err) {
      console.error('Failed to fetch referrals:', err)
    }
  }

  const fetchReferralLeaderboard = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/referrals/leaderboard`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setReferralLeaderboard(data.leaderboard)
      }
    } catch (err) {
      console.error('Failed to fetch referral leaderboard:', err)
    }
  }

  const fetchReferralStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/referrals/stats`, {
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        setReferralStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch referral stats:', err)
    }
  }

  const updateCourse = async (courseId: string, updates: Partial<Course>) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/courses/admin/courses/${courseId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(updates),
      })
      if (response.ok) {
        const updated = await response.json()
        setCourses(prev => prev.map(c => c.id === courseId ? updated : c))
        setEditingCourse(null)
      }
    } catch (err) {
      console.error('Failed to update course:', err)
    }
  }

  const deleteCourse = async (courseId: string) => {
    if (!confirm('Are you sure you want to delete this course?')) return
    try {
      const response = await fetch(`${API_BASE_URL}/api/courses/admin/courses/${courseId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        setCourses(prev => prev.filter(c => c.id !== courseId))
        fetchCourseStats()
      }
    } catch (err) {
      console.error('Failed to delete course:', err)
    }
  }

  const getDifficultyColor = (tier: number) => {
    switch (tier) {
      case 1: return 'bg-emerald-50 text-emerald-700'
      case 2: return 'bg-teal-50 text-teal-700'
      case 3: return 'bg-amber-50 text-amber-700'
      case 4: return 'bg-orange-50 text-orange-700'
      case 5: return 'bg-rose-50 text-rose-600'
      default: return 'bg-stone-100 text-stone-600'
    }
  }

  const getDifficultyLabel = (tier: number) => {
    switch (tier) {
      case 1: return 'Intro'
      case 2: return 'Foundation'
      case 3: return 'Challenging'
      case 4: return 'Very Hard'
      case 5: return 'Elite'
      default: return 'Unknown'
    }
  }

  const getPrestigeColor = (tier: number) => {
    switch (tier) {
      case 1: return 'bg-stone-100 text-stone-600'
      case 2: return 'bg-sky-50 text-sky-700'
      case 3: return 'bg-teal-50 text-teal-700'
      case 4: return 'bg-violet-50 text-violet-700'
      case 5: return 'bg-amber-50 text-amber-700'
      default: return 'bg-stone-100 text-stone-600'
    }
  }

  const getPrestigeLabel = (tier: number) => {
    switch (tier) {
      case 1: return 'Casual'
      case 2: return 'Active'
      case 3: return 'Competitive'
      case 4: return 'Selective'
      case 5: return 'Elite'
      default: return 'Unknown'
    }
  }

  const toggleCandidateVerification = async (id: string, verified: boolean) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/candidates/${id}/verify?verified=${verified}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
      })

      if (response.ok) {
        setCandidates(prev => prev.map(c =>
          c.id === id ? { ...c, email_verified: verified } : c
        ))
      }
    } catch (err) {
      console.error('Failed to update verification:', err)
    }
  }

  const toggleEmployerVerification = async (id: string, verified: boolean) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/employers/${id}/verify?verified=${verified}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
      })

      if (response.ok) {
        setEmployers(prev => prev.map(e =>
          e.id === id ? { ...e, is_verified: verified } : e
        ))
      }
    } catch (err) {
      console.error('Failed to update verification:', err)
    }
  }

  const sendNudge = async (candidateId: string, nudgeType: 'resume' | 'github' | 'transcript') => {
    setSendingNudge(`${candidateId}-${nudgeType}`)
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/candidates/${candidateId}/nudge`, {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nudge_type: nudgeType }),
      })

      if (response.ok) {
        alert(`Nudge email sent successfully!`)
      } else {
        const data = await response.json()
        alert(`Failed to send nudge: ${data.detail || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Failed to send nudge:', err)
      alert('Failed to send nudge email')
    } finally {
      setSendingNudge(null)
      setOpenNudgeDropdown(null)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    localStorage.removeItem('admin_password')
    router.push('/')
  }

  if (isLoading) {
    return (
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-stone-200 border-t-teal-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-stone-400 text-sm">Loading admin panel...</p>
        </div>
      </PageWrapper>
    )
  }

  // Password prompt
  if (showPasswordPrompt) {
    return (
      <PageWrapper className="bg-stone-50">
        <AdminNavbar onLogout={handleLogout} />
        <Container className="py-12 pt-28">
          <Card className="max-w-sm mx-auto shadow-sm border-stone-100">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl font-medium text-stone-800">Admin Access</CardTitle>
              <CardDescription className="text-stone-400">Enter the admin password to continue</CardDescription>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="mb-4 p-3 bg-rose-50 text-rose-600 rounded-lg text-sm">
                  {error}
                </div>
              )}
              <div className="space-y-4">
                <input
                  type="password"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handlePasswordSubmit()}
                  placeholder="Admin password"
                  className="w-full px-4 py-3 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-700"
                  autoFocus
                />
                <div className="flex gap-2">
                  <Button
                    onClick={handlePasswordSubmit}
                    className="flex-1 bg-teal-600 hover:bg-teal-700 text-white rounded-xl py-2.5"
                  >
                    Continue
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => router.push('/')}
                    className="border-stone-200 text-stone-600 rounded-xl"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </Container>
      </PageWrapper>
    )
  }

  if (error && !showPasswordPrompt) {
    return (
      <PageWrapper className="bg-stone-50">
        <AdminNavbar onLogout={handleLogout} />
        <Container className="py-12 pt-28">
          <Card className="shadow-sm border-stone-100">
            <CardContent className="py-16 text-center">
              <div className="w-16 h-16 bg-rose-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-stone-800 mb-2">Access Denied</h3>
              <p className="text-stone-400 mb-6">{error}</p>
              <Button
                onClick={() => router.push('/')}
                className="bg-stone-900 hover:bg-stone-800 text-white rounded-xl px-6"
              >
                Back to Home
              </Button>
            </CardContent>
          </Card>
        </Container>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper className="bg-stone-50 min-h-screen">
      <AdminNavbar onLogout={handleLogout} />

      <Container className="py-10 pt-24">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-medium text-stone-800">Admin Dashboard</h1>
          <p className="text-stone-400 text-sm mt-1">System management and statistics</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-8 border-b border-stone-200">
          {(['overview', 'candidates', 'employers', 'universities', 'courses', 'clubs', 'referrals'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-3 text-sm font-medium border-b-2 -mb-px transition-all duration-200 ${
                activeTab === tab
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-stone-400 hover:text-stone-600'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="space-y-8">
            {/* Quick Stats - All using consistent teal/stone palette */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-3xl font-semibold text-stone-800">{stats.total_candidates}</div>
                  <p className="text-sm text-stone-400 mt-1">Total Candidates</p>
                  <p className="text-xs text-teal-600 mt-2">+{stats.new_candidates_7d} this week</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-3xl font-semibold text-stone-800">{stats.total_employers}</div>
                  <p className="text-sm text-stone-400 mt-1">Total Employers</p>
                  <p className="text-xs text-teal-600 mt-2">+{stats.new_employers_7d} this week</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-3xl font-semibold text-stone-800">{stats.total_interviews}</div>
                  <p className="text-sm text-stone-400 mt-1">Total Interviews</p>
                  <p className="text-xs text-teal-600 mt-2">+{stats.new_interviews_7d} this week</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-3xl font-semibold text-stone-800">{stats.hired_count}</div>
                  <p className="text-sm text-stone-400 mt-1">Hired</p>
                  <p className="text-xs text-stone-400 mt-2">{stats.total_matches} total matches</p>
                </CardContent>
              </Card>
            </div>

            {/* Key Metrics Row - All using teal accent */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-teal-50/50 border-teal-100/50 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-700">
                    {stats.total_candidates > 0
                      ? (stats.total_interviews / stats.total_candidates).toFixed(1)
                      : '0'}
                  </div>
                  <p className="text-sm text-teal-600/70 mt-1">Avg Interviews / Candidate</p>
                </CardContent>
              </Card>
              <Card className="bg-teal-50/50 border-teal-100/50 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-700">
                    {stats.total_candidates > 0
                      ? Math.round((stats.verified_candidates / stats.total_candidates) * 100)
                      : 0}%
                  </div>
                  <p className="text-sm text-teal-600/70 mt-1">Verification Rate</p>
                </CardContent>
              </Card>
              <Card className="bg-teal-50/50 border-teal-100/50 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-700">
                    {stats.total_interviews > 0
                      ? Math.round((stats.completed_interviews / stats.total_interviews) * 100)
                      : 0}%
                  </div>
                  <p className="text-sm text-teal-600/70 mt-1">Completion Rate</p>
                </CardContent>
              </Card>
              <Card className="bg-teal-50/50 border-teal-100/50 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-700">
                    {stats.total_employers > 0
                      ? (stats.total_jobs / stats.total_employers).toFixed(1)
                      : '0'}
                  </div>
                  <p className="text-sm text-teal-600/70 mt-1">Avg Jobs / Employer</p>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Stats */}
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="border-stone-100 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base font-medium text-stone-700">Candidates</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Total</span>
                      <span className="font-medium text-stone-700">{stats.total_candidates}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Verified</span>
                      <div className="flex items-center gap-3">
                        <div className="w-24 h-1.5 bg-stone-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: `${stats.total_candidates > 0 ? (stats.verified_candidates / stats.total_candidates) * 100 : 0}%` }}
                          />
                        </div>
                        <span className="font-medium text-emerald-600 w-8 text-right">{stats.verified_candidates}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Unverified</span>
                      <span className="font-medium text-amber-600">
                        {stats.total_candidates - stats.verified_candidates}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-stone-100 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base font-medium text-stone-700">Employers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Total</span>
                      <span className="font-medium text-stone-700">{stats.total_employers}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Verified</span>
                      <div className="flex items-center gap-3">
                        <div className="w-24 h-1.5 bg-stone-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: `${stats.total_employers > 0 ? (stats.verified_employers / stats.total_employers) * 100 : 0}%` }}
                          />
                        </div>
                        <span className="font-medium text-emerald-600 w-8 text-right">{stats.verified_employers}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Active Jobs</span>
                      <span className="font-medium text-stone-700">{stats.active_jobs} / {stats.total_jobs}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-stone-100 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base font-medium text-stone-700">Interviews</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Total</span>
                      <span className="font-medium text-stone-700">{stats.total_interviews}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Completed</span>
                      <div className="flex items-center gap-3">
                        <div className="w-24 h-1.5 bg-stone-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: `${stats.total_interviews > 0 ? (stats.completed_interviews / stats.total_interviews) * 100 : 0}%` }}
                          />
                        </div>
                        <span className="font-medium text-emerald-600 w-8 text-right">{stats.completed_interviews}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">In Progress</span>
                      <span className="font-medium text-amber-600">
                        {stats.total_interviews - stats.completed_interviews}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-stone-100 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base font-medium text-stone-700">Matches & Hiring</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Total Matches</span>
                      <span className="font-medium text-stone-700">{stats.total_matches}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Hired</span>
                      <div className="flex items-center gap-3">
                        <div className="w-24 h-1.5 bg-stone-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: `${stats.total_matches > 0 ? (stats.hired_count / stats.total_matches) * 100 : 0}%` }}
                          />
                        </div>
                        <span className="font-medium text-emerald-600 w-8 text-right">{stats.hired_count}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-stone-500">Hire Rate</span>
                      <span className="font-medium text-stone-700">
                        {stats.total_matches > 0
                          ? Math.round((stats.hired_count / stats.total_matches) * 100)
                          : 0}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Weekly Growth Summary */}
            <Card className="border-stone-100 shadow-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-medium text-stone-700">This Week's Growth</CardTitle>
                <CardDescription className="text-stone-400">Activity in the last 7 days</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-8 text-center py-4">
                  <div>
                    <div className="text-3xl font-semibold text-teal-600">+{stats.new_candidates_7d}</div>
                    <p className="text-sm text-stone-500 mt-1">New Candidates</p>
                  </div>
                  <div>
                    <div className="text-3xl font-semibold text-teal-600">+{stats.new_employers_7d}</div>
                    <p className="text-sm text-stone-500 mt-1">New Employers</p>
                  </div>
                  <div>
                    <div className="text-3xl font-semibold text-teal-600">+{stats.new_interviews_7d}</div>
                    <p className="text-sm text-stone-500 mt-1">New Interviews</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Candidates Tab */}
        {activeTab === 'candidates' && (
          <div className="space-y-6">
            {/* Search and Filters */}
            <div className="flex flex-wrap gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name, email, phone..."
                className="flex-1 min-w-[200px] px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-700 placeholder:text-stone-400"
              />
              <CustomSelect
                value={candidateFilter}
                onChange={(v) => setCandidateFilter(v as 'all' | 'verified' | 'unverified')}
                options={[
                  { value: 'all', label: 'All Status' },
                  { value: 'verified', label: 'Verified Only' },
                  { value: 'unverified', label: 'Unverified Only' },
                ]}
                placeholder="All Status"
              />
            </div>

            <p className="text-sm text-stone-400">
              {candidateTotal} candidates found
              {candidateFilter !== 'all' && ` (filtered: ${candidateFilter})`}
            </p>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-stone-200">
                    <th
                      className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider cursor-pointer hover:text-stone-700 transition-colors"
                      onClick={() => setCandidateSort(s => ({ field: 'name', dir: s.field === 'name' && s.dir === 'asc' ? 'desc' : 'asc' }))}
                    >
                      Name {candidateSort.field === 'name' && (candidateSort.dir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Email</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Phone</th>
                    <th
                      className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider cursor-pointer hover:text-stone-700 transition-colors"
                      onClick={() => setCandidateSort(s => ({ field: 'interview_count', dir: s.field === 'interview_count' && s.dir === 'asc' ? 'desc' : 'asc' }))}
                    >
                      Interviews {candidateSort.field === 'interview_count' && (candidateSort.dir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Profile</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Status</th>
                    <th
                      className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider cursor-pointer hover:text-stone-700 transition-colors"
                      onClick={() => setCandidateSort(s => ({ field: 'created_at', dir: s.field === 'created_at' && s.dir === 'asc' ? 'desc' : 'asc' }))}
                    >
                      Joined {candidateSort.field === 'created_at' && (candidateSort.dir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {candidates
                    .filter(c => {
                      if (candidateFilter === 'verified') return c.email_verified
                      if (candidateFilter === 'unverified') return !c.email_verified
                      return true
                    })
                    .sort((a, b) => {
                      const field = candidateSort.field as keyof CandidateAdmin
                      const dir = candidateSort.dir === 'asc' ? 1 : -1
                      if (a[field] < b[field]) return -1 * dir
                      if (a[field] > b[field]) return 1 * dir
                      return 0
                    })
                    .map((c) => (
                    <tr key={c.id} className="hover:bg-stone-50/50 transition-colors">
                      <td className="px-4 py-4 text-sm font-medium text-stone-800">{c.name}</td>
                      <td className="px-4 py-4 text-sm text-stone-500">{c.email}</td>
                      <td className="px-4 py-4 text-sm text-stone-500">{c.phone || '—'}</td>
                      <td className="px-4 py-4 text-sm text-stone-600">{c.interview_count}</td>
                      <td className="px-4 py-4">
                        <div className="flex gap-1.5">
                          <span className={`p-1 rounded ${c.has_resume ? 'bg-teal-100 text-teal-700' : 'bg-stone-100 text-stone-400'}`} title="Resume">
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </span>
                          <span className={`p-1 rounded ${c.has_github ? 'bg-teal-100 text-teal-700' : 'bg-stone-100 text-stone-400'}`} title="GitHub">
                            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                            </svg>
                          </span>
                          <span className={`p-1 rounded ${c.has_transcript ? 'bg-teal-100 text-teal-700' : 'bg-stone-100 text-stone-400'}`} title="Transcript">
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                          c.email_verified
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-amber-50 text-amber-700'
                        }`}>
                          {c.email_verified ? 'Verified' : 'Unverified'}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-400">
                        {new Date(c.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => toggleCandidateVerification(c.id, !c.email_verified)}
                            className="text-xs border-stone-200 text-stone-600 hover:bg-stone-50 rounded-lg"
                          >
                            {c.email_verified ? 'Unverify' : 'Verify'}
                          </Button>
                          {/* Nudge Dropdown */}
                          <div className="relative">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setOpenNudgeDropdown(openNudgeDropdown === c.id ? null : c.id)}
                              className="text-xs border-stone-200 text-teal-600 hover:bg-teal-50 rounded-lg"
                              disabled={c.has_resume && c.has_github && c.has_transcript}
                            >
                              Nudge ▾
                            </Button>
                            {openNudgeDropdown === c.id && (
                              <div className="absolute right-0 mt-1 w-44 bg-white border border-stone-200 rounded-lg shadow-lg z-10">
                                {!c.has_resume && (
                                  <button
                                    onClick={() => sendNudge(c.id, 'resume')}
                                    disabled={sendingNudge === `${c.id}-resume`}
                                    className="w-full px-3 py-2 text-left text-sm text-stone-700 hover:bg-stone-50 flex items-center gap-2 disabled:opacity-50 first:rounded-t-lg"
                                  >
                                    <svg className="w-4 h-4 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    {sendingNudge === `${c.id}-resume` ? 'Sending...' : 'Add Resume'}
                                  </button>
                                )}
                                {!c.has_github && (
                                  <button
                                    onClick={() => sendNudge(c.id, 'github')}
                                    disabled={sendingNudge === `${c.id}-github`}
                                    className="w-full px-3 py-2 text-left text-sm text-stone-700 hover:bg-stone-50 flex items-center gap-2 disabled:opacity-50"
                                  >
                                    <svg className="w-4 h-4 text-stone-500" fill="currentColor" viewBox="0 0 24 24">
                                      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                                    </svg>
                                    {sendingNudge === `${c.id}-github` ? 'Sending...' : 'Connect GitHub'}
                                  </button>
                                )}
                                {!c.has_transcript && (
                                  <button
                                    onClick={() => sendNudge(c.id, 'transcript')}
                                    disabled={sendingNudge === `${c.id}-transcript`}
                                    className="w-full px-3 py-2 text-left text-sm text-stone-700 hover:bg-stone-50 flex items-center gap-2 disabled:opacity-50 last:rounded-b-lg"
                                  >
                                    <svg className="w-4 h-4 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                    {sendingNudge === `${c.id}-transcript` ? 'Sending...' : 'Add Transcript'}
                                  </button>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Employers Tab */}
        {activeTab === 'employers' && (
          <div className="space-y-6">
            {/* Search and Filters */}
            <div className="flex flex-wrap gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by company name, email..."
                className="flex-1 min-w-[200px] px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-700 placeholder:text-stone-400"
              />
              <CustomSelect
                value={employerFilter}
                onChange={(v) => setEmployerFilter(v as 'all' | 'verified' | 'unverified')}
                options={[
                  { value: 'all', label: 'All Status' },
                  { value: 'verified', label: 'Verified Only' },
                  { value: 'unverified', label: 'Unverified Only' },
                ]}
                placeholder="All Status"
              />
            </div>

            <p className="text-sm text-stone-400">
              {employerTotal} employers found
              {employerFilter !== 'all' && ` (filtered: ${employerFilter})`}
            </p>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-stone-200">
                    <th
                      className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider cursor-pointer hover:text-stone-700 transition-colors"
                      onClick={() => setEmployerSort(s => ({ field: 'company_name', dir: s.field === 'company_name' && s.dir === 'asc' ? 'desc' : 'asc' }))}
                    >
                      Company {employerSort.field === 'company_name' && (employerSort.dir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Email</th>
                    <th
                      className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider cursor-pointer hover:text-stone-700 transition-colors"
                      onClick={() => setEmployerSort(s => ({ field: 'job_count', dir: s.field === 'job_count' && s.dir === 'asc' ? 'desc' : 'asc' }))}
                    >
                      Jobs {employerSort.field === 'job_count' && (employerSort.dir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Status</th>
                    <th
                      className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider cursor-pointer hover:text-stone-700 transition-colors"
                      onClick={() => setEmployerSort(s => ({ field: 'created_at', dir: s.field === 'created_at' && s.dir === 'asc' ? 'desc' : 'asc' }))}
                    >
                      Joined {employerSort.field === 'created_at' && (employerSort.dir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {employers
                    .filter(e => {
                      if (employerFilter === 'verified') return e.is_verified
                      if (employerFilter === 'unverified') return !e.is_verified
                      return true
                    })
                    .sort((a, b) => {
                      const field = employerSort.field as keyof EmployerAdmin
                      const dir = employerSort.dir === 'asc' ? 1 : -1
                      if (a[field] < b[field]) return -1 * dir
                      if (a[field] > b[field]) return 1 * dir
                      return 0
                    })
                    .map((e) => (
                    <tr key={e.id} className="hover:bg-stone-50/50 transition-colors">
                      <td className="px-4 py-4 text-sm font-medium text-stone-800">{e.company_name}</td>
                      <td className="px-4 py-4 text-sm text-stone-500">{e.email}</td>
                      <td className="px-4 py-4 text-sm text-stone-600">{e.job_count}</td>
                      <td className="px-4 py-4">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                          e.is_verified
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-amber-50 text-amber-700'
                        }`}>
                          {e.is_verified ? 'Verified' : 'Unverified'}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-400">
                        {new Date(e.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleEmployerVerification(e.id, !e.is_verified)}
                          className="text-xs border-stone-200 text-stone-600 hover:bg-stone-50 rounded-lg"
                        >
                          {e.is_verified ? 'Unverify' : 'Verify'}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Universities Tab */}
        {activeTab === 'universities' && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-600">{universityDetails.length}</div>
                  <p className="text-sm text-stone-400 mt-1">Total Universities</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-stone-700">
                    {universityDetails.reduce((sum, u) => sum + u.course_count, 0)}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Total Courses</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-stone-700">
                    {universityDetails.reduce((sum, u) => sum + u.club_count, 0)}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Total Clubs</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-stone-700">
                    {universityDetails.filter(u => u.tier === 1).length}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Tier 1 Schools</p>
                </CardContent>
              </Card>
            </div>

            {/* Universities Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-stone-200">
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">CS Rank</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">University</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Tier</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">GPA Scale</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">+/- Grading</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Courses</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Clubs</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {universityDetails.map((uni) => (
                    <tr key={uni.id} className="hover:bg-stone-50/50 transition-colors">
                      <td className="px-4 py-4">
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-stone-100 text-sm font-semibold text-stone-700">
                          {uni.cs_ranking || '—'}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <div className="text-sm font-medium text-stone-800">{uni.name}</div>
                        <div className="text-xs text-stone-400">{uni.short_name} · {uni.id}</div>
                      </td>
                      <td className="px-4 py-4">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                          uni.tier === 1 ? 'bg-amber-50 text-amber-700' :
                          uni.tier === 2 ? 'bg-teal-50 text-teal-700' :
                          'bg-stone-100 text-stone-600'
                        }`}>
                          Tier {uni.tier}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-600">{uni.gpa_scale.toFixed(1)}</td>
                      <td className="px-4 py-4">
                        <span className={`px-2 py-0.5 text-xs rounded ${
                          uni.uses_plus_minus ? 'bg-teal-50 text-teal-700' : 'bg-stone-100 text-stone-500'
                        }`}>
                          {uni.uses_plus_minus ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <span className={`text-sm font-medium ${uni.course_count > 0 ? 'text-stone-700' : 'text-stone-300'}`}>
                          {uni.course_count}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <span className={`text-sm font-medium ${uni.club_count > 0 ? 'text-stone-700' : 'text-stone-300'}`}>
                          {uni.club_count}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {universityDetails.length === 0 && (
              <div className="text-center py-12">
                <h3 className="text-lg font-medium text-stone-700 mb-2">No universities found</h3>
                <p className="text-stone-400 mb-4">University data will be auto-seeded on next API restart</p>
              </div>
            )}
          </div>
        )}

        {/* Courses Tab */}
        {activeTab === 'courses' && (
          <div className="space-y-6">
            {/* Stats */}
            {courseStats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-teal-600">{courseStats.total_courses}</div>
                    <p className="text-sm text-stone-400 mt-1">Total Courses</p>
                  </CardContent>
                </Card>
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-stone-700">{courseStats.total_universities}</div>
                    <p className="text-sm text-stone-400 mt-1">Universities</p>
                  </CardContent>
                </Card>
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-rose-600">{courseStats.by_difficulty_tier?.tier_5 || 0}</div>
                    <p className="text-sm text-stone-400 mt-1">Elite Courses</p>
                  </CardContent>
                </Card>
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-emerald-600">{courseStats.by_difficulty_tier?.tier_1 || 0}</div>
                    <p className="text-sm text-stone-400 mt-1">Intro Courses</p>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Filters */}
            <div className="flex flex-wrap gap-3">
              <CustomSelect
                value={selectedUniversity}
                onChange={(v) => setSelectedUniversity(v)}
                options={[
                  { value: '', label: 'All Universities' },
                  ...universities.map(u => ({ value: u.id, label: u.short_name })),
                ]}
                placeholder="All Universities"
                searchable
                searchPlaceholder="Search universities..."
              />
              <CustomSelect
                value={selectedDepartment}
                onChange={(v) => setSelectedDepartment(v)}
                options={[
                  { value: '', label: 'All Departments' },
                  { value: 'CS', label: 'CS' },
                  { value: 'EECS', label: 'EECS' },
                  { value: 'DATA', label: 'DATA' },
                  { value: 'MATH', label: 'MATH' },
                  { value: 'ECE', label: 'ECE' },
                ]}
                placeholder="All Departments"
              />
              <Button
                variant="outline"
                onClick={() => setShowAddCourse(true)}
                className="border-stone-200 text-stone-600 hover:bg-stone-50 rounded-xl"
              >
                + Add Course
              </Button>
            </div>

            <p className="text-sm text-stone-400">{courses.length} courses found</p>

            {/* Difficulty Legend */}
            <div className="flex flex-wrap gap-2 text-xs">
              {[1, 2, 3, 4, 5].map(tier => (
                <span key={tier} className={`px-2.5 py-1 rounded-full ${getDifficultyColor(tier)}`}>
                  Tier {tier}: {getDifficultyLabel(tier)}
                </span>
              ))}
            </div>

            {/* Courses Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-stone-200">
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Course</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Difficulty</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Score</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">GPA</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Flags</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {courses.map((c) => (
                    <tr key={c.id} className="hover:bg-stone-50/50 transition-colors">
                      <td className="px-4 py-4">
                        <div className="text-sm font-medium text-stone-800">{c.department} {c.number}</div>
                        <div className="text-xs text-stone-400">{c.university_id}</div>
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-600 max-w-xs truncate" title={c.name}>
                        {c.name}
                      </td>
                      <td className="px-4 py-4">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${getDifficultyColor(c.difficulty_tier)}`}>
                          Tier {c.difficulty_tier}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm font-medium text-stone-700">
                        {c.difficulty_score.toFixed(1)}
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-500">
                        {c.typical_gpa?.toFixed(1) || '—'}
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex gap-1 flex-wrap">
                          {c.is_weeder && (
                            <span className="px-1.5 py-0.5 text-xs bg-rose-50 text-rose-600 rounded">Weeder</span>
                          )}
                          {c.is_proof_based && (
                            <span className="px-1.5 py-0.5 text-xs bg-violet-50 text-violet-600 rounded">Proofs</span>
                          )}
                          {c.is_curved && (
                            <span className="px-1.5 py-0.5 text-xs bg-sky-50 text-sky-600 rounded">Curved</span>
                          )}
                          {c.has_coding && (
                            <span className="px-1.5 py-0.5 text-xs bg-emerald-50 text-emerald-600 rounded">Code</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setEditingCourse(c)}
                            className="text-xs border-stone-200 text-stone-600 hover:bg-stone-50 rounded-lg"
                          >
                            Edit
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-xs border-stone-200 text-rose-600 hover:bg-rose-50 rounded-lg"
                            onClick={() => deleteCourse(c.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Edit Course Modal */}
            {editingCourse && (
              <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="bg-white rounded-2xl p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto shadow-xl">
                  <h3 className="text-lg font-medium text-stone-800 mb-1">
                    Edit {editingCourse.department} {editingCourse.number}
                  </h3>
                  <p className="text-sm text-stone-400 mb-6">{editingCourse.name}</p>

                  <div className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium text-stone-600 mb-2">
                        Difficulty Tier (1-5)
                      </label>
                      <CustomSelect
                        value={String(editingCourse.difficulty_tier)}
                        onChange={(v) => setEditingCourse({...editingCourse, difficulty_tier: parseInt(v)})}
                        options={[
                          { value: '1', label: '1 - Introductory' },
                          { value: '2', label: '2 - Foundational' },
                          { value: '3', label: '3 - Challenging' },
                          { value: '4', label: '4 - Very Challenging' },
                          { value: '5', label: '5 - Elite' },
                        ]}
                        placeholder="Select tier"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-stone-600 mb-2">
                        Difficulty Score (0-10)
                      </label>
                      <input
                        type="number"
                        step="0.5"
                        min="0"
                        max="10"
                        value={editingCourse.difficulty_score}
                        onChange={(e) => setEditingCourse({
                          ...editingCourse,
                          difficulty_score: parseFloat(e.target.value)
                        })}
                        className="w-full px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-stone-600 mb-2">
                        Typical GPA
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="4"
                        value={editingCourse.typical_gpa || ''}
                        onChange={(e) => setEditingCourse({
                          ...editingCourse,
                          typical_gpa: e.target.value ? parseFloat(e.target.value) : undefined
                        })}
                        className="w-full px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                        placeholder="e.g., 3.0"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <label className="flex items-center gap-3 p-3 bg-stone-50 rounded-xl cursor-pointer hover:bg-stone-100 transition-colors">
                        <input
                          type="checkbox"
                          checked={editingCourse.is_weeder}
                          onChange={(e) => setEditingCourse({
                            ...editingCourse,
                            is_weeder: e.target.checked
                          })}
                          className="w-4 h-4 text-teal-600 rounded"
                        />
                        <span className="text-sm text-stone-600">Weeder Course</span>
                      </label>
                      <label className="flex items-center gap-3 p-3 bg-stone-50 rounded-xl cursor-pointer hover:bg-stone-100 transition-colors">
                        <input
                          type="checkbox"
                          checked={editingCourse.is_proof_based}
                          onChange={(e) => setEditingCourse({
                            ...editingCourse,
                            is_proof_based: e.target.checked
                          })}
                          className="w-4 h-4 text-teal-600 rounded"
                        />
                        <span className="text-sm text-stone-600">Proof-Based</span>
                      </label>
                      <label className="flex items-center gap-3 p-3 bg-stone-50 rounded-xl cursor-pointer hover:bg-stone-100 transition-colors">
                        <input
                          type="checkbox"
                          checked={editingCourse.is_curved}
                          onChange={(e) => setEditingCourse({
                            ...editingCourse,
                            is_curved: e.target.checked
                          })}
                          className="w-4 h-4 text-teal-600 rounded"
                        />
                        <span className="text-sm text-stone-600">Curved</span>
                      </label>
                      <label className="flex items-center gap-3 p-3 bg-stone-50 rounded-xl cursor-pointer hover:bg-stone-100 transition-colors">
                        <input
                          type="checkbox"
                          checked={editingCourse.has_coding}
                          onChange={(e) => setEditingCourse({
                            ...editingCourse,
                            has_coding: e.target.checked
                          })}
                          className="w-4 h-4 text-teal-600 rounded"
                        />
                        <span className="text-sm text-stone-600">Has Coding</span>
                      </label>
                    </div>
                  </div>

                  <div className="flex gap-3 mt-8">
                    <Button
                      onClick={() => updateCourse(editingCourse.id, {
                        difficulty_tier: editingCourse.difficulty_tier,
                        difficulty_score: editingCourse.difficulty_score,
                        typical_gpa: editingCourse.typical_gpa,
                        is_weeder: editingCourse.is_weeder,
                        is_proof_based: editingCourse.is_proof_based,
                        is_curved: editingCourse.is_curved,
                        has_coding: editingCourse.has_coding,
                      })}
                      className="flex-1 bg-teal-600 hover:bg-teal-700 text-white rounded-xl py-2.5"
                    >
                      Save Changes
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setEditingCourse(null)}
                      className="border-stone-200 text-stone-600 rounded-xl"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Clubs Tab */}
        {activeTab === 'clubs' && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-600">{clubTotal}</div>
                  <p className="text-sm text-stone-400 mt-1">Total Clubs</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-600">
                    {new Set(clubs.map(c => c.university_id)).size}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Universities</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-amber-600">
                    {clubs.filter(c => c.prestige_tier === 5).length}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Elite Clubs</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-violet-600">
                    {clubs.filter(c => c.prestige_tier === 4).length}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Selective Clubs</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-stone-700">
                    {clubs.filter(c => c.is_technical).length}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Technical</p>
                </CardContent>
              </Card>
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-stone-700">
                    {clubs.filter(c => c.is_selective).length}
                  </div>
                  <p className="text-sm text-stone-400 mt-1">Application Required</p>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-3">
              <CustomSelect
                value={selectedClubUniversity}
                onChange={(v) => setSelectedClubUniversity(v)}
                options={[
                  { value: '', label: 'All Universities' },
                  { value: 'berkeley', label: 'UC Berkeley' },
                  { value: 'uiuc', label: 'UIUC' },
                  { value: 'stanford', label: 'Stanford' },
                  { value: 'mit', label: 'MIT' },
                  { value: 'cmu', label: 'CMU' },
                  { value: 'purdue', label: 'Purdue' },
                  { value: 'cornell', label: 'Cornell' },
                  { value: 'uw', label: 'UW' },
                  { value: 'georgia_tech', label: 'Georgia Tech' },
                  { value: 'princeton', label: 'Princeton' },
                  { value: 'caltech', label: 'Caltech' },
                  { value: 'umich', label: 'UMich' },
                  { value: 'columbia', label: 'Columbia' },
                  { value: 'ucla', label: 'UCLA' },
                  { value: 'ut_austin', label: 'UT Austin' },
                  { value: 'uw_madison', label: 'UW-Madison' },
                  { value: 'ucsd', label: 'UC San Diego' },
                  { value: 'umd', label: 'UMD' },
                  { value: 'upenn', label: 'UPenn' },
                  { value: 'harvard', label: 'Harvard' },
                  { value: 'ucsb', label: 'UCSB' },
                ]}
                placeholder="All Universities"
              />
              <CustomSelect
                value={selectedClubCategory}
                onChange={(v) => setSelectedClubCategory(v)}
                options={[
                  { value: '', label: 'All Categories' },
                  { value: 'engineering', label: 'Engineering/Tech' },
                  { value: 'business', label: 'Business/Professional' },
                  { value: 'professional', label: 'Professional' },
                  { value: 'competition', label: 'Competition' },
                  { value: 'social_impact', label: 'Social Impact' },
                  { value: 'cultural', label: 'Cultural' },
                  { value: 'greek', label: 'Greek Life' },
                  { value: 'sports', label: 'Sports/Recreation' },
                  { value: 'arts', label: 'Performing Arts' },
                  { value: 'research', label: 'Research/Academic' },
                  { value: 'other', label: 'Other' },
                ]}
                placeholder="All Categories"
              />
              <CustomSelect
                value={String(clubPrestigeFilter)}
                onChange={(v) => setClubPrestigeFilter(v === '' ? '' : parseInt(v))}
                options={[
                  { value: '', label: 'All Prestige Tiers' },
                  { value: '5', label: 'Tier 5 - Elite' },
                  { value: '4', label: 'Tier 4 - Selective' },
                  { value: '3', label: 'Tier 3 - Competitive' },
                  { value: '2', label: 'Tier 2 - Active' },
                  { value: '1', label: 'Tier 1 - Casual' },
                ]}
                placeholder="All Prestige Tiers"
              />
            </div>

            <p className="text-sm text-stone-400">{clubs.length} clubs found</p>

            {/* Prestige Legend */}
            <div className="flex flex-wrap gap-2 text-xs">
              {[1, 2, 3, 4, 5].map(tier => (
                <span key={tier} className={`px-2.5 py-1 rounded-full ${getPrestigeColor(tier)}`}>
                  Tier {tier}: {getPrestigeLabel(tier)}
                </span>
              ))}
            </div>

            {/* Clubs Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-stone-200">
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Club Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">University</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Category</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Prestige</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Score</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Acceptance</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Attributes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {clubs.map((club) => (
                    <tr key={club.id} className="hover:bg-stone-50/50 transition-colors">
                      <td className="px-4 py-4">
                        <div className="text-sm font-medium text-stone-800">{club.name}</div>
                        {club.short_name && (
                          <div className="text-xs text-stone-400">{club.short_name}</div>
                        )}
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-500">
                        {club.university_id.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-600 capitalize">
                        {club.category.replace('_', ' ')}
                      </td>
                      <td className="px-4 py-4">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${getPrestigeColor(club.prestige_tier)}`}>
                          Tier {club.prestige_tier}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm font-medium text-stone-700">
                        {club.prestige_score.toFixed(1)}
                      </td>
                      <td className="px-4 py-4 text-sm text-stone-500">
                        {club.is_selective ? (
                          club.acceptance_rate
                            ? `${(club.acceptance_rate * 100).toFixed(0)}%`
                            : 'Selective'
                        ) : (
                          'Open'
                        )}
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex gap-1 flex-wrap">
                          {club.is_technical && (
                            <span className="px-1.5 py-0.5 text-xs bg-sky-50 text-sky-600 rounded">Tech</span>
                          )}
                          {club.is_professional && (
                            <span className="px-1.5 py-0.5 text-xs bg-indigo-50 text-indigo-600 rounded">Pro</span>
                          )}
                          {club.has_projects && (
                            <span className="px-1.5 py-0.5 text-xs bg-emerald-50 text-emerald-600 rounded">Projects</span>
                          )}
                          {club.has_competitions && (
                            <span className="px-1.5 py-0.5 text-xs bg-rose-50 text-rose-600 rounded">Compete</span>
                          )}
                          {club.is_honor_society && (
                            <span className="px-1.5 py-0.5 text-xs bg-amber-50 text-amber-600 rounded">Honor</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {clubs.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-stone-700 mb-2">No clubs found</h3>
                <p className="text-stone-400 mb-4">Club data will be auto-seeded on next API restart</p>
              </div>
            )}
          </div>
        )}

        {/* Referrals Tab */}
        {activeTab === 'referrals' && (
          <div className="space-y-6">
            {/* Stats */}
            {referralStats && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-teal-600">{referralStats.total_referrals}</div>
                    <p className="text-sm text-stone-400 mt-1">Total Referrals</p>
                  </CardContent>
                </Card>
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-stone-700">{referralStats.by_status?.registered || 0}</div>
                    <p className="text-sm text-stone-400 mt-1">Registered</p>
                  </CardContent>
                </Card>
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-stone-700">{referralStats.by_status?.onboarded || 0}</div>
                    <p className="text-sm text-stone-400 mt-1">Onboarded</p>
                  </CardContent>
                </Card>
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-emerald-600">{referralStats.by_status?.interviewed || 0}</div>
                    <p className="text-sm text-stone-400 mt-1">Interviewed</p>
                  </CardContent>
                </Card>
                <Card className="border-stone-100 shadow-sm">
                  <CardContent className="pt-6 pb-5">
                    <div className="text-2xl font-semibold text-teal-600">
                      {referralStats.conversion_rate ? `${(referralStats.conversion_rate * 100).toFixed(1)}%` : '0%'}
                    </div>
                    <p className="text-sm text-stone-400 mt-1">Conversion Rate</p>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Leaderboard */}
            {referralLeaderboard.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-stone-800 mb-4">Referral Leaderboard</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-stone-200">
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">#</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Referrer</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Email</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Code</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Total</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Registered</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Onboarded</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Interviewed</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-100">
                      {referralLeaderboard.map((entry: any, idx: number) => (
                        <tr key={entry.referrer_id} className="hover:bg-stone-50/50 transition-colors">
                          <td className="px-4 py-4">
                            <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold ${
                              idx === 0 ? 'bg-amber-100 text-amber-700' :
                              idx === 1 ? 'bg-stone-200 text-stone-700' :
                              idx === 2 ? 'bg-orange-100 text-orange-700' :
                              'bg-stone-100 text-stone-500'
                            }`}>
                              {idx + 1}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-sm font-medium text-stone-800">{entry.referrer_name}</td>
                          <td className="px-4 py-4 text-sm text-stone-500">{entry.referrer_email}</td>
                          <td className="px-4 py-4">
                            <span className="px-2 py-1 text-xs font-mono bg-stone-100 text-stone-600 rounded">
                              {entry.referral_code || '—'}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-sm font-semibold text-stone-800">{entry.total}</td>
                          <td className="px-4 py-4 text-sm text-stone-600">{entry.registered}</td>
                          <td className="px-4 py-4 text-sm text-stone-600">{entry.onboarded}</td>
                          <td className="px-4 py-4 text-sm text-emerald-600 font-medium">{entry.interviewed}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* All Referrals */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-stone-800">All Referrals</h3>
                <CustomSelect
                  value={referralStatusFilter}
                  onChange={(v) => setReferralStatusFilter(v)}
                  options={[
                    { value: '', label: 'All Status' },
                    { value: 'pending', label: 'Pending' },
                    { value: 'registered', label: 'Registered' },
                    { value: 'onboarded', label: 'Onboarded' },
                    { value: 'interviewed', label: 'Interviewed' },
                  ]}
                  placeholder="All Status"
                />
              </div>

              <p className="text-sm text-stone-400 mb-4">{referralData.total} referrals found</p>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-stone-200">
                      <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Referrer</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Referee Email</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Referee Name</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Referred On</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Converted On</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100">
                    {referralData.referrals.map((ref: any) => (
                      <tr key={ref.id} className="hover:bg-stone-50/50 transition-colors">
                        <td className="px-4 py-4">
                          <div className="text-sm font-medium text-stone-800">{ref.referrer_name}</div>
                          <div className="text-xs text-stone-400">{ref.referrer_email}</div>
                        </td>
                        <td className="px-4 py-4 text-sm text-stone-600">{ref.referee_email}</td>
                        <td className="px-4 py-4 text-sm text-stone-600">{ref.referee_name || '—'}</td>
                        <td className="px-4 py-4">
                          <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                            ref.status === 'interviewed' ? 'bg-emerald-50 text-emerald-700' :
                            ref.status === 'onboarded' ? 'bg-teal-50 text-teal-700' :
                            ref.status === 'registered' ? 'bg-sky-50 text-sky-700' :
                            'bg-stone-100 text-stone-500'
                          }`}>
                            {ref.status.charAt(0).toUpperCase() + ref.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm text-stone-400">
                          {new Date(ref.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-4 text-sm text-stone-400">
                          {ref.converted_at ? new Date(ref.converted_at).toLocaleDateString() : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {referralData.referrals.length === 0 && (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-stone-700 mb-2">No referrals yet</h3>
                  <p className="text-stone-400">Referrals will appear here when users share their referral codes</p>
                </div>
              )}
            </div>
          </div>
        )}
      </Container>
    </PageWrapper>
  )
}
