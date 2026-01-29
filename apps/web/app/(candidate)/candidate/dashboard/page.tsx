'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface Candidate {
  id: string
  name: string
  email: string
}

interface Job {
  id: string
  title: string
  company_name: string
  vertical: string
}

export default function CandidateDashboard() {
  const router = useRouter()
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if candidate is logged in
    const stored = localStorage.getItem('candidate')
    if (!stored) {
      router.push('/candidate/login')
      return
    }

    setCandidate(JSON.parse(stored))

    // Fetch available jobs via local API route
    const fetchJobs = async () => {
      try {
        const response = await fetch('/api/jobs?is_active=true')
        if (response.ok) {
          const data = await response.json()
          setJobs(data.jobs || [])
        }
      } catch (error) {
        console.error('Failed to fetch jobs:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchJobs()
  }, [router])

  const startInterview = async (jobId: string) => {
    if (!candidate) return

    try {
      const response = await fetch('/api/interviews/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidate.id,
          job_id: jobId || undefined,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to start interview')
      }

      const data = await response.json()
      router.push(`/interview/${data.session_id}`)

    } catch (error) {
      console.error('Failed to start interview:', error)
      alert(error instanceof Error ? error.message : 'Failed to start interview. Please try again.')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('candidate')
    router.push('/')
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">智</span>
              </div>
              <span className="font-semibold text-gray-900">ZhiMian</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">Hi, {candidate?.name}</span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Your Dashboard</h1>
          <p className="text-gray-600">Find jobs and complete AI interviews</p>
        </div>

        {/* Available Jobs */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Opportunities</h2>

          {jobs.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs available yet</h3>
                <p className="text-gray-500 mb-4">
                  Check back later for new opportunities, or complete a general interview to be matched with employers.
                </p>
                <Button
                  onClick={() => startInterview('')}
                  className="bg-gradient-to-r from-emerald-600 to-teal-600"
                >
                  Take General Interview
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {jobs.map((job) => (
                <Card key={job.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{job.title}</CardTitle>
                    <CardDescription>{job.company_name}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2 mb-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        job.vertical === 'NEW_ENERGY'
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {job.vertical === 'NEW_ENERGY' ? 'New Energy' : 'Sales'}
                      </span>
                    </div>
                    <Button
                      onClick={() => startInterview(job.id)}
                      className="w-full bg-gradient-to-r from-emerald-600 to-teal-600"
                    >
                      Start Interview
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Info Section */}
        <Card className="bg-emerald-50 border-emerald-100">
          <CardContent className="py-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-1">How it works</h3>
                <p className="text-sm text-gray-600">
                  Select a job and complete a 15-minute AI video interview. Your responses are analyzed by AI and shared with employers.
                  You&apos;ll be contacted if there&apos;s a match.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
