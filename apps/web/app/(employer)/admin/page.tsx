'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DashboardNavbar } from '@/components/layout/navbar'
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

type Tab = 'overview' | 'candidates' | 'employers'

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

  // Search
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('employer_token')
    if (!token) {
      router.push('/login')
      return
    }
    fetchStats()
  }, [])

  useEffect(() => {
    if (activeTab === 'candidates') {
      fetchCandidates()
    } else if (activeTab === 'employers') {
      fetchEmployers()
    }
  }, [activeTab, searchQuery])

  const getAuthHeaders = () => {
    const token = localStorage.getItem('employer_token')
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    }
  }

  const fetchStats = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
        headers: getAuthHeaders(),
      })

      if (response.status === 403) {
        setError('Admin access required. Please login with an admin account.')
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
    router.push('/login')
  }

  if (isLoading) {
    return (
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-warm-200 border-t-brand-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-warm-500 text-sm">Loading admin panel...</p>
        </div>
      </PageWrapper>
    )
  }

  if (error) {
    return (
      <PageWrapper>
        <DashboardNavbar companyName="Admin" onLogout={handleLogout} />
        <Container className="py-8 pt-24">
          <Card>
            <CardContent className="py-12 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-warm-900 mb-2">Access Denied</h3>
              <p className="text-warm-500 mb-4">{error}</p>
              <Button onClick={() => router.push('/dashboard')}>
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>
        </Container>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <DashboardNavbar companyName="Admin Panel" onLogout={handleLogout} />

      <Container className="py-8 pt-24">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-warm-900">Admin Dashboard</h1>
          <p className="text-warm-500">System management and statistics</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-warm-200">
          {(['overview', 'candidates', 'employers'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activeTab === tab
                  ? 'border-brand-500 text-brand-600'
                  : 'border-transparent text-warm-500 hover:text-warm-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-brand-600">{stats.total_candidates}</div>
                  <p className="text-sm text-warm-500">Total Candidates</p>
                  <p className="text-xs text-green-600 mt-1">+{stats.new_candidates_7d} this week</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-blue-600">{stats.total_employers}</div>
                  <p className="text-sm text-warm-500">Total Employers</p>
                  <p className="text-xs text-green-600 mt-1">+{stats.new_employers_7d} this week</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-purple-600">{stats.total_interviews}</div>
                  <p className="text-sm text-warm-500">Total Interviews</p>
                  <p className="text-xs text-green-600 mt-1">+{stats.new_interviews_7d} this week</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-green-600">{stats.hired_count}</div>
                  <p className="text-sm text-warm-500">Hired</p>
                  <p className="text-xs text-warm-400 mt-1">{stats.total_matches} total matches</p>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Stats */}
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Candidates</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-warm-600">Total</span>
                      <span className="font-medium">{stats.total_candidates}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Verified</span>
                      <span className="font-medium text-green-600">{stats.verified_candidates}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Unverified</span>
                      <span className="font-medium text-yellow-600">
                        {stats.total_candidates - stats.verified_candidates}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Employers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-warm-600">Total</span>
                      <span className="font-medium">{stats.total_employers}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Verified</span>
                      <span className="font-medium text-green-600">{stats.verified_employers}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Active Jobs</span>
                      <span className="font-medium">{stats.active_jobs} / {stats.total_jobs}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Interviews</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-warm-600">Total</span>
                      <span className="font-medium">{stats.total_interviews}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Completed</span>
                      <span className="font-medium text-green-600">{stats.completed_interviews}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Completion Rate</span>
                      <span className="font-medium">
                        {stats.total_interviews > 0
                          ? Math.round((stats.completed_interviews / stats.total_interviews) * 100)
                          : 0}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Matches</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-warm-600">Total Matches</span>
                      <span className="font-medium">{stats.total_matches}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Hired</span>
                      <span className="font-medium text-green-600">{stats.hired_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-warm-600">Hire Rate</span>
                      <span className="font-medium">
                        {stats.total_matches > 0
                          ? Math.round((stats.hired_count / stats.total_matches) * 100)
                          : 0}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Candidates Tab */}
        {activeTab === 'candidates' && (
          <div className="space-y-4">
            {/* Search */}
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name, email, phone..."
                className="flex-1 px-4 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <p className="text-sm text-warm-500">{candidateTotal} candidates found</p>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full border border-warm-200 rounded-lg">
                <thead className="bg-warm-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Name</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Email</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Phone</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Interviews</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-warm-100">
                  {candidates.map((c) => (
                    <tr key={c.id} className="hover:bg-warm-50">
                      <td className="px-4 py-3 text-sm">{c.name}</td>
                      <td className="px-4 py-3 text-sm text-warm-600">{c.email}</td>
                      <td className="px-4 py-3 text-sm text-warm-600">{c.phone}</td>
                      <td className="px-4 py-3 text-sm">{c.interview_count}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          c.email_verified
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {c.email_verified ? 'Verified' : 'Unverified'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleCandidateVerification(c.id, !c.email_verified)}
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
          <div className="space-y-4">
            {/* Search */}
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by company name, email..."
                className="flex-1 px-4 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <p className="text-sm text-warm-500">{employerTotal} employers found</p>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full border border-warm-200 rounded-lg">
                <thead className="bg-warm-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Company</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Email</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Jobs</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-warm-600">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-warm-100">
                  {employers.map((e) => (
                    <tr key={e.id} className="hover:bg-warm-50">
                      <td className="px-4 py-3 text-sm font-medium">{e.company_name}</td>
                      <td className="px-4 py-3 text-sm text-warm-600">{e.email}</td>
                      <td className="px-4 py-3 text-sm">{e.job_count}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          e.is_verified
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {e.is_verified ? 'Verified' : 'Unverified'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleEmployerVerification(e.id, !e.is_verified)}
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
      </Container>
    </PageWrapper>
  )
}
