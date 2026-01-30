'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { CandidateCard } from '@/components/dashboard/candidate-card'
import { employerApi, type Employer, type DashboardStats, type InterviewSession } from '@/lib/api'

export default function DashboardPage() {
  const router = useRouter()
  const [employer, setEmployer] = useState<Employer | null>(null)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentInterviews, setRecentInterviews] = useState<InterviewSession[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/login')
          return
        }

        // Fetch all data in parallel for faster loading
        const [employerData, statsData, interviewsData] = await Promise.all([
          employerApi.getMe(),
          employerApi.getDashboard(),
          employerApi.listInterviews({ limit: 5 })
        ])

        setEmployer(employerData)
        setStats(statsData)
        setRecentInterviews(interviewsData.interviews)
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

    loadData()
  }, [router])

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
          <p className="text-warm-500 text-sm">Loading dashboard...</p>
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <DashboardNavbar companyName={employer?.companyName} onLogout={handleLogout} />

      <Container className="py-8 pt-24">
        {/* Welcome Section */}
        <div className="mb-10">
          <h1 className="text-2xl sm:text-3xl font-bold text-warm-900 mb-2">
            Welcome back, {employer?.companyName}
          </h1>
          <p className="text-warm-500">Here&apos;s an overview of your hiring activity</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
          <div className="bg-white rounded-2xl shadow-soft p-5 hover:shadow-soft-md transition-shadow">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-brand-50 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-warm-500">Total Interviews</span>
            </div>
            <div className="text-3xl font-bold text-warm-900">{stats?.totalInterviews || 0}</div>
          </div>

          <div className="bg-white rounded-2xl shadow-soft p-5 hover:shadow-soft-md transition-shadow">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-warning-light rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-warm-500">Pending Review</span>
            </div>
            <div className="text-3xl font-bold text-warm-900">{stats?.pendingReview || 0}</div>
          </div>

          <div className="bg-white rounded-2xl shadow-soft p-5 hover:shadow-soft-md transition-shadow">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-success-light rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-warm-500">Shortlisted</span>
            </div>
            <div className="text-3xl font-bold text-warm-900">{stats?.shortlisted || 0}</div>
          </div>

          <div className="bg-white rounded-2xl shadow-soft p-5 hover:shadow-soft-md transition-shadow">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-info-light rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-warm-500">Avg. Score</span>
            </div>
            <div className="text-3xl font-bold text-warm-900">
              {stats?.averageScore ? stats.averageScore.toFixed(1) : '-'}
              {stats?.averageScore && <span className="text-lg font-normal text-warm-400">/10</span>}
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Recent Interviews */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-soft overflow-hidden">
            <div className="px-6 py-5 border-b border-warm-100 flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-warm-900">Recent Interviews</h2>
                <p className="text-sm text-warm-500">Latest candidate submissions</p>
              </div>
              <Link href="/dashboard/interviews">
                <Button variant="ghost" size="sm" className="text-brand-600 hover:text-brand-700 hover:bg-brand-50">
                  View all
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              </Link>
            </div>
            <div className="p-6">
              {recentInterviews.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p className="text-warm-900 font-medium mb-1">No interviews yet</p>
                  <p className="text-sm text-warm-500 mb-4">
                    Create a job posting and share interview links with candidates
                  </p>
                  <Link href="/dashboard/jobs">
                    <Button variant="brand" size="sm">Create Job Posting</Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
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
            </div>
          </div>

          {/* Quick Actions Sidebar */}
          <div className="space-y-6">
            {/* Create Interview */}
            <div className="bg-gradient-to-br from-brand-500 to-brand-600 rounded-2xl p-6 text-white shadow-brand">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <h3 className="font-semibold text-lg mb-2">Create Interview Link</h3>
              <p className="text-brand-100 text-sm mb-4 leading-relaxed">
                Generate unique links to share with candidates for async video interviews
              </p>
              <Link href="/dashboard/jobs">
                <Button className="w-full bg-white text-brand-600 hover:bg-brand-50">
                  Manage Jobs
                </Button>
              </Link>
            </div>

            {/* Quick Links */}
            <div className="bg-white rounded-2xl shadow-soft p-6">
              <h3 className="font-semibold text-warm-900 mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <Link
                  href="/dashboard/interviews"
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-warm-50 transition-colors group"
                >
                  <div className="w-10 h-10 bg-warm-100 rounded-lg flex items-center justify-center group-hover:bg-brand-100 transition-colors">
                    <svg className="w-5 h-5 text-warm-600 group-hover:text-brand-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-warm-900 text-sm">All Interviews</div>
                    <div className="text-xs text-warm-500">View and manage submissions</div>
                  </div>
                  <svg className="w-4 h-4 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>

                <Link
                  href="/dashboard/jobs"
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-warm-50 transition-colors group"
                >
                  <div className="w-10 h-10 bg-warm-100 rounded-lg flex items-center justify-center group-hover:bg-brand-100 transition-colors">
                    <svg className="w-5 h-5 text-warm-600 group-hover:text-brand-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-warm-900 text-sm">Job Postings</div>
                    <div className="text-xs text-warm-500">Create and manage jobs</div>
                  </div>
                  <svg className="w-4 h-4 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>

                <Link
                  href="/dashboard/talent-pool"
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-warm-50 transition-colors group"
                >
                  <div className="w-10 h-10 bg-warm-100 rounded-lg flex items-center justify-center group-hover:bg-brand-100 transition-colors">
                    <svg className="w-5 h-5 text-warm-600 group-hover:text-brand-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-warm-900 text-sm">Talent Pool</div>
                    <div className="text-xs text-warm-500">Browse pre-interviewed candidates</div>
                  </div>
                  <svg className="w-4 h-4 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Pro Tips */}
            <div className="bg-warning-light border border-warning/20 rounded-2xl p-6">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-warning/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-warning-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-warning-dark text-sm mb-1">Pro Tip</h4>
                  <p className="text-warning-dark/80 text-xs leading-relaxed">
                    Review interviews within 48 hours to keep candidates engaged. Fast response times improve your hiring success rate.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </PageWrapper>
  )
}
