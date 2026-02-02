'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AdminNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'

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

type Tab = 'overview' | 'candidates' | 'employers' | 'courses' | 'clubs'

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

  // Club management state
  const [clubs, setClubs] = useState<ClubAdmin[]>([])
  const [clubTotal, setClubTotal] = useState(0)
  const [selectedClubCategory, setSelectedClubCategory] = useState<string>('')
  const [clubPrestigeFilter, setClubPrestigeFilter] = useState<number | ''>('')

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
    } else if (activeTab === 'courses') {
      fetchUniversities()
      fetchCourses()
      fetchCourseStats()
    } else if (activeTab === 'clubs') {
      fetchClubs()
    }
  }, [activeTab, searchQuery, selectedUniversity, selectedDepartment, adminPassword, candidateSort, employerSort, candidateFilter, employerFilter, selectedClubCategory, clubPrestigeFilter])

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

  const fetchClubs = async () => {
    try {
      const params = new URLSearchParams()
      if (selectedClubCategory) params.set('category', selectedClubCategory)
      if (clubPrestigeFilter) params.set('min_prestige', String(clubPrestigeFilter))
      params.set('limit', '200')

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

  const seedClubs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/activities/admin/clubs/seed`, {
        method: 'POST',
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        const data = await response.json()
        alert(`Seeded ${data.clubs_added} clubs. Total: ${data.total_clubs}`)
        fetchClubs()
      }
    } catch (err) {
      console.error('Failed to seed clubs:', err)
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
          {(['overview', 'candidates', 'employers', 'courses', 'clubs'] as Tab[]).map((tab) => (
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
              <select
                value={candidateFilter}
                onChange={(e) => setCandidateFilter(e.target.value as 'all' | 'verified' | 'unverified')}
                className="px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-600"
              >
                <option value="all">All Status</option>
                <option value="verified">Verified Only</option>
                <option value="unverified">Unverified Only</option>
              </select>
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
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleCandidateVerification(c.id, !c.email_verified)}
                          className="text-xs border-stone-200 text-stone-600 hover:bg-stone-50 rounded-lg"
                        >
                          {c.email_verified ? 'Unverify' : 'Verify'}
                        </Button>
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
              <select
                value={employerFilter}
                onChange={(e) => setEmployerFilter(e.target.value as 'all' | 'verified' | 'unverified')}
                className="px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-600"
              >
                <option value="all">All Status</option>
                <option value="verified">Verified Only</option>
                <option value="unverified">Unverified Only</option>
              </select>
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
              <select
                value={selectedUniversity}
                onChange={(e) => setSelectedUniversity(e.target.value)}
                className="px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-600"
              >
                <option value="">All Universities</option>
                {universities.map(u => (
                  <option key={u.id} value={u.id}>{u.short_name}</option>
                ))}
              </select>
              <select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-600"
              >
                <option value="">All Departments</option>
                <option value="CS">CS</option>
                <option value="EECS">EECS</option>
                <option value="DATA">DATA</option>
                <option value="MATH">MATH</option>
                <option value="ECE">ECE</option>
              </select>
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
                      <select
                        value={editingCourse.difficulty_tier}
                        onChange={(e) => setEditingCourse({
                          ...editingCourse,
                          difficulty_tier: parseInt(e.target.value)
                        })}
                        className="w-full px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                      >
                        <option value="1">1 - Introductory</option>
                        <option value="2">2 - Foundational</option>
                        <option value="3">3 - Challenging</option>
                        <option value="4">4 - Very Challenging</option>
                        <option value="5">5 - Elite</option>
                      </select>
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
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <Card className="border-stone-100 shadow-sm">
                <CardContent className="pt-6 pb-5">
                  <div className="text-2xl font-semibold text-teal-600">{clubTotal}</div>
                  <p className="text-sm text-stone-400 mt-1">Total Clubs</p>
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
              <select
                value={selectedClubCategory}
                onChange={(e) => setSelectedClubCategory(e.target.value)}
                className="px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-600"
              >
                <option value="">All Categories</option>
                <option value="engineering">Engineering/Tech</option>
                <option value="business">Business/Professional</option>
                <option value="cultural">Cultural</option>
                <option value="greek">Greek Life</option>
                <option value="sports">Sports/Recreation</option>
                <option value="arts">Performing Arts</option>
                <option value="research">Research/Academic</option>
                <option value="service">Service/Social Good</option>
                <option value="honor">Honor Society</option>
                <option value="other">Other</option>
              </select>
              <select
                value={clubPrestigeFilter}
                onChange={(e) => setClubPrestigeFilter(e.target.value === '' ? '' : parseInt(e.target.value))}
                className="px-4 py-2.5 border border-stone-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-stone-600"
              >
                <option value="">All Prestige Tiers</option>
                <option value="5">Tier 5 - Elite</option>
                <option value="4">Tier 4 - Selective</option>
                <option value="3">Tier 3 - Competitive</option>
                <option value="2">Tier 2 - Active</option>
                <option value="1">Tier 1 - Casual</option>
              </select>
              <Button
                variant="outline"
                onClick={seedClubs}
                className="border-stone-200 text-stone-600 hover:bg-stone-50 rounded-xl"
              >
                Seed/Refresh Clubs
              </Button>
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
                <p className="text-stone-400 mb-4">Click "Seed/Refresh Clubs" to populate the club database</p>
              </div>
            )}
          </div>
        )}
      </Container>
    </PageWrapper>
  )
}
