'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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

  // Bulk selection
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [isBulkActionLoading, setIsBulkActionLoading] = useState(false)
  const [bulkActionResult, setBulkActionResult] = useState<{ success: boolean; message: string } | null>(null)
  const [isExporting, setIsExporting] = useState(false)

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

  // Bulk selection handlers
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

  const handleBulkAction = async (action: 'shortlist' | 'reject') => {
    if (selectedIds.size === 0) return

    setIsBulkActionLoading(true)
    setBulkActionResult(null)

    try {
      const result = await employerApi.bulkAction(Array.from(selectedIds), action)
      setBulkActionResult({
        success: result.success,
        message: `Successfully ${action === 'shortlist' ? 'shortlisted' : 'rejected'} ${result.processed} interview(s)${result.failed > 0 ? `. ${result.failed} failed.` : ''}`,
      })
      setSelectedIds(new Set())
      // Reload interviews to show updated statuses
      loadInterviews()
    } catch (err) {
      setBulkActionResult({
        success: false,
        message: err instanceof Error ? err.message : 'Bulk action failed',
      })
    } finally {
      setIsBulkActionLoading(false)
    }
  }

  const clearBulkResult = () => setBulkActionResult(null)

  const handleExportCSV = async () => {
    setIsExporting(true)
    try {
      const blob = await employerApi.exportInterviewsCsv(selectedJob || undefined)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `interviews-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Export failed:', err)
      setBulkActionResult({
        success: false,
        message: err instanceof Error ? err.message : 'Export failed',
      })
    } finally {
      setIsExporting(false)
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-gray-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading interviews...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-teal-600 to-teal-500 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <span className="font-semibold text-gray-900">Pathway</span>
            </Link>
            <span className="text-gray-300">/</span>
            <span className="text-gray-600">Interviews</span>
          </div>
          <Link href="/dashboard">
            <Button variant="outline" size="sm">Back to Dashboard</Button>
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">All Interviews</h1>
            <p className="text-gray-500 mt-1">{total} total interviews</p>
          </div>
          <Button
            onClick={handleExportCSV}
            disabled={isExporting || interviews.length === 0}
            variant="outline"
          >
            {isExporting ? (
              <>
                <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin mr-2" />
                Exporting...
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export CSV
              </>
            )}
          </Button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Filters</h3>
          <div className="flex flex-wrap gap-4 items-end">
            <div className="w-48">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Job
              </label>
              <select
                value={selectedJob}
                onChange={(e) => setSelectedJob(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
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
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              >
                <option value="">All Statuses</option>
                <option value="PENDING">Pending</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="COMPLETED">Completed</option>
              </select>
            </div>

            <div className="w-32">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
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
                className="focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div className="flex items-end gap-2">
              <Button
                onClick={handleFilter}
                className="bg-teal-600 hover:bg-teal-700"
              >
                Apply Filters
              </Button>
              <Button variant="outline" onClick={handleClearFilters}>
                Clear
              </Button>
            </div>
          </div>
        </div>

        {/* Bulk Action Toolbar */}
        {selectedIds.size > 0 && (
          <div className="bg-teal-50 border border-teal-200 rounded-xl p-4 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="font-medium text-teal-800">
                {selectedIds.size} interview{selectedIds.size > 1 ? 's' : ''} selected
              </span>
              <Button
                onClick={() => handleBulkAction('shortlist')}
                disabled={isBulkActionLoading}
                className="bg-teal-600 hover:bg-teal-700"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Shortlist All
              </Button>
              <Button
                onClick={() => handleBulkAction('reject')}
                disabled={isBulkActionLoading}
                variant="outline"
                className="text-red-600 border-red-200 hover:bg-red-50"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Reject All
              </Button>
            </div>
            <Button
              onClick={() => setSelectedIds(new Set())}
              variant="ghost"
              size="sm"
              className="text-teal-700"
            >
              Clear Selection
            </Button>
          </div>
        )}

        {/* Bulk Action Result */}
        {bulkActionResult && (
          <div className={`rounded-xl p-4 mb-6 flex items-center justify-between ${
            bulkActionResult.success ? 'bg-teal-50 border border-teal-200' : 'bg-red-50 border border-red-200'
          }`}>
            <span className={bulkActionResult.success ? 'text-teal-800' : 'text-red-800'}>
              {bulkActionResult.message}
            </span>
            <Button onClick={clearBulkResult} variant="ghost" size="sm">
              Dismiss
            </Button>
          </div>
        )}

        {/* Interview List */}
        {interviews.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-lg font-medium text-gray-900">No interviews found</p>
              <p className="text-sm text-gray-500 mt-1">
                Try adjusting your filters or wait for candidates to complete interviews
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Select All Header */}
            <div className="flex items-center gap-3 mb-3 px-2">
              <input
                type="checkbox"
                checked={selectedIds.size === interviews.length && interviews.length > 0}
                onChange={toggleSelectAll}
                className="w-5 h-5 rounded border-gray-300 text-teal-600 focus:ring-teal-500 cursor-pointer"
              />
              <span className="text-sm text-gray-600">Select all</span>
            </div>

          <div className="space-y-3">
            {interviews.map((interview) => (
              <div
                key={interview.id}
                className={`bg-white rounded-xl border p-5 transition-all ${
                  selectedIds.has(interview.id)
                    ? 'border-teal-400 bg-teal-50/30 shadow-sm'
                    : 'border-gray-200 hover:border-teal-300 hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(interview.id)}
                      onChange={(e) => {
                        e.stopPropagation()
                        toggleSelect(interview.id)
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="w-5 h-5 rounded border-gray-300 text-teal-600 focus:ring-teal-500 cursor-pointer"
                    />
                    <div
                      className="flex items-center gap-4 cursor-pointer"
                      onClick={() => router.push(`/dashboard/interviews/${interview.id}`)}
                    >
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-teal-100 to-teal-50 flex items-center justify-center">
                        <span className="text-teal-700 font-semibold text-lg">
                          {(interview.candidateName || 'U').charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {interview.candidateName || 'Unknown Candidate'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {interview.jobTitle} • {new Date(interview.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div
                    className="flex items-center gap-6 cursor-pointer"
                    onClick={() => router.push(`/dashboard/interviews/${interview.id}`)}
                  >
                    {/* Status badge */}
                    <span
                      className={`px-3 py-1.5 text-xs font-semibold rounded-full ${
                        interview.status === 'COMPLETED'
                          ? 'bg-teal-100 text-teal-700'
                          : interview.status === 'IN_PROGRESS'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {interview.status === 'COMPLETED' ? 'Completed' :
                       interview.status === 'IN_PROGRESS' ? 'In Progress' : 'Pending'}
                    </span>

                    {/* Score */}
                    {interview.totalScore && (
                      <div className="text-center">
                        <div className="text-2xl font-bold text-teal-600">
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
              </div>
            ))}
          </div>
          </>
        )}
      </div>
    </main>
  )
}
