'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CandidateCard } from '@/components/dashboard/candidate-card'
import { employerApi, type InterviewSession, type Job } from '@/lib/api'

export default function InterviewsListPage() {
  const router = useRouter()
  const [interviews, setInterviews] = useState<InterviewSession[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [total, setTotal] = useState(0)

  // Filters
  const [selectedJob, setSelectedJob] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [minScore, setMinScore] = useState<string>('')

  useEffect(() => {
    const loadData = async () => {
      try {
        // Check for token
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/login')
          return
        }

        // Load jobs for filter
        const jobsData = await employerApi.listJobs()
        setJobs(jobsData.jobs)

        // Load interviews
        await loadInterviews()
      } catch (err) {
        console.error('Failed to load data:', err)
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

  const loadInterviews = async () => {
    try {
      const data = await employerApi.listInterviews({
        jobId: selectedJob || undefined,
        status: statusFilter || undefined,
        minScore: minScore ? parseFloat(minScore) : undefined,
        limit: 50,
      })
      setInterviews(data.interviews)
      setTotal(data.total)
    } catch (err) {
      console.error('Failed to load interviews:', err)
    }
  }

  const handleFilter = () => {
    loadInterviews()
  }

  const handleClearFilters = () => {
    setSelectedJob('')
    setStatusFilter('')
    setMinScore('')
    loadInterviews()
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading interviews...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-xl font-bold text-blue-600">
              ZhiPin AI
            </Link>
            <span className="text-gray-400">/</span>
            <span className="text-gray-600">Interviews</span>
          </div>
          <Link href="/dashboard">
            <Button variant="outline" size="sm">Back to Dashboard</Button>
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">All Interviews</h1>
          <p className="text-gray-600">{total} total interviews</p>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <div className="w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job
                </label>
                <select
                  value={selectedJob}
                  onChange={(e) => setSelectedJob(e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="">All Jobs</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="COMPLETED">Completed</option>
                </select>
              </div>

              <div className="w-32">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Score
                </label>
                <Input
                  type="number"
                  min="0"
                  max="10"
                  step="0.5"
                  value={minScore}
                  onChange={(e) => setMinScore(e.target.value)}
                  placeholder="0-10"
                />
              </div>

              <div className="flex items-end gap-2">
                <Button onClick={handleFilter}>Apply</Button>
                <Button variant="outline" onClick={handleClearFilters}>
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Interview List */}
        {interviews.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-gray-500">
                <p className="text-lg">No interviews found</p>
                <p className="text-sm mt-1">
                  Try adjusting your filters or wait for candidates to complete interviews
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {interviews.map((interview) => (
              <Card
                key={interview.id}
                className="cursor-pointer hover:border-blue-300 transition-colors"
                onClick={() => router.push(`/dashboard/interviews/${interview.id}`)}
              >
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-blue-700 font-semibold">
                          {(interview.candidateName || 'U').charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">
                          {interview.candidateName || 'Unknown Candidate'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {interview.jobTitle} • {new Date(interview.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      {/* Status badge */}
                      <span
                        className={`px-3 py-1 text-xs font-medium rounded-full ${
                          interview.status === 'COMPLETED'
                            ? 'bg-green-100 text-green-700'
                            : interview.status === 'IN_PROGRESS'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {interview.status}
                      </span>

                      {/* Score */}
                      {interview.totalScore && (
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {interview.totalScore.toFixed(1)}
                          </div>
                          <div className="text-xs text-gray-500">Score</div>
                        </div>
                      )}

                      <svg
                        className="w-5 h-5 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
