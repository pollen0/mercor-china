'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { candidateApi, candidateVerticalApi, type VerticalProfile, type MatchingJob } from '@/lib/api'

interface Candidate {
  id: string
  name: string
  email: string
}

// Vertical display config
const VERTICAL_CONFIG = {
  new_energy: {
    name: 'New Energy / EV',
    nameZh: '新能源 / 电动汽车',
    icon: '🔋',
    color: 'emerald',
  },
  sales: {
    name: 'Sales / BD',
    nameZh: '销售 / 商务拓展',
    icon: '💼',
    color: 'blue',
  },
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

export default function CandidateDashboard() {
  const router = useRouter()
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasResume, setHasResume] = useState(false)
  const [verticalProfiles, setVerticalProfiles] = useState<VerticalProfile[]>([])
  const [matchingJobs, setMatchingJobs] = useState<MatchingJob[]>([])

  useEffect(() => {
    // Check if candidate is logged in
    const stored = localStorage.getItem('candidate')
    const token = localStorage.getItem('candidate_token')
    if (!stored) {
      router.push('/candidate/login')
      return
    }

    setCandidate(JSON.parse(stored))

    // Fetch all data in parallel for faster loading
    const fetchData = async () => {
      try {
        const [resumeResult, profileResult, jobResult] = await Promise.allSettled([
          candidateApi.getMyResume(token || undefined),
          candidateVerticalApi.getMyVerticals(token || undefined),
          candidateVerticalApi.getMatchingJobs(token || undefined)
        ])

        // Handle resume
        if (resumeResult.status === 'fulfilled') {
          setHasResume(resumeResult.value?.parsedData != null)
        }

        // Handle profiles
        if (profileResult.status === 'fulfilled') {
          setVerticalProfiles(profileResult.value.profiles)
        }

        // Handle jobs
        if (jobResult.status === 'fulfilled') {
          setMatchingJobs(jobResult.value.jobs)
        }
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('candidate')
    localStorage.removeItem('candidate_token')
    router.push('/')
  }

  const getProfileForVertical = (vertical: string): VerticalProfile | undefined => {
    return verticalProfiles.find(p => p.vertical === vertical)
  }

  const hasCompletedProfiles = verticalProfiles.some(p => p.status === 'completed')

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
              <Link href="/candidate/resume">
                <Button variant="outline" size="sm">
                  My Resume
                </Button>
              </Link>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Resume Upload Prompt */}
      {!hasResume && !isLoading && (
        <div className="bg-amber-50 border-b border-amber-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-amber-800">Upload your resume first</p>
                  <p className="text-sm text-amber-600">We&apos;ll use it to better match you with employers.</p>
                </div>
              </div>
              <Link href="/candidate/resume?onboarding=true">
                <Button className="bg-amber-600 hover:bg-amber-700 text-white whitespace-nowrap">
                  Upload Resume
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Your Talent Profile</h1>
          <p className="text-gray-600">Complete interviews to enter the talent pool and get matched with employers</p>
        </div>

        {/* Vertical Interview Profiles */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">My Interview Profiles</h2>
            <Link href="/interview/select">
              <Button className="bg-gradient-to-r from-emerald-600 to-teal-600">
                Start New Interview
              </Button>
            </Link>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {Object.entries(VERTICAL_CONFIG).map(([key, config]) => {
              const profile = getProfileForVertical(key)
              const isCompleted = profile?.status === 'completed'
              const isInProgress = profile?.status === 'in_progress'

              return (
                <Card key={key} className="relative overflow-hidden">
                  {isCompleted && (
                    <div className="absolute top-0 right-0 w-20 h-20 overflow-hidden">
                      <div className={`absolute transform rotate-45 bg-${config.color}-500 text-white text-xs font-semibold py-1 right-[-35px] top-[20px] w-[120px] text-center`}>
                        Completed
                      </div>
                    </div>
                  )}
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">{config.icon}</span>
                      <div>
                        <CardTitle className="text-lg">{config.nameZh}</CardTitle>
                        <CardDescription>{config.name}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {isCompleted ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Role:</span>
                          <span className="font-medium">{ROLE_NAMES[profile.roleType] || profile.roleType}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Best Score:</span>
                          <span className="font-medium text-emerald-600">{profile.bestScore?.toFixed(1)}/10</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Attempts:</span>
                          <span className="font-medium">{profile.attemptCount}/3</span>
                        </div>
                        {profile.canRetake && (
                          <Link href="/interview/select">
                            <Button variant="outline" size="sm" className="w-full mt-2">
                              Retake Interview
                            </Button>
                          </Link>
                        )}
                        {!profile.canRetake && profile.attemptCount >= 3 && (
                          <p className="text-xs text-gray-500 text-center">Maximum attempts reached</p>
                        )}
                        {!profile.canRetake && profile.attemptCount < 3 && profile.nextRetakeAvailableAt && (
                          <p className="text-xs text-gray-500 text-center">
                            Retake available: {new Date(profile.nextRetakeAvailableAt).toLocaleString()}
                          </p>
                        )}
                      </div>
                    ) : isInProgress ? (
                      <div className="text-center py-4">
                        <p className="text-amber-600 font-medium mb-3">Interview in progress</p>
                        <Link href="/interview/select">
                          <Button className="bg-amber-600 hover:bg-amber-700">
                            Continue Interview
                          </Button>
                        </Link>
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-gray-500 mb-3">Not started</p>
                        <Link href="/interview/select">
                          <Button variant="outline">
                            Start Interview
                          </Button>
                        </Link>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Matching Jobs */}
        {hasCompletedProfiles && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Jobs Matching Your Profile ({matchingJobs.length})
            </h2>

            {matchingJobs.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No matching jobs yet</h3>
                  <p className="text-gray-500">
                    Employers will contact you when they find a good match. Check back later for new opportunities.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {matchingJobs.map((job) => (
                  <Card key={job.jobId} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{job.jobTitle}</CardTitle>
                      <CardDescription>{job.companyName}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            job.vertical === 'new_energy'
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {VERTICAL_CONFIG[job.vertical as keyof typeof VERTICAL_CONFIG]?.nameZh || job.vertical}
                          </span>
                          {job.roleType && (
                            <span className="text-xs text-gray-500">
                              {ROLE_NAMES[job.roleType] || job.roleType}
                            </span>
                          )}
                        </div>
                        {job.location && (
                          <p className="text-sm text-gray-600">📍 {job.location}</p>
                        )}
                        {(job.salaryMin || job.salaryMax) && (
                          <p className="text-sm text-gray-600">
                            💰 {job.salaryMin && `${job.salaryMin}K`}
                            {job.salaryMin && job.salaryMax && ' - '}
                            {job.salaryMax && `${job.salaryMax}K`}
                          </p>
                        )}
                        {job.matchScore && (
                          <div className="pt-2 border-t border-gray-100">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Match Score</span>
                              <span className="font-medium text-emerald-600">{job.matchScore.toFixed(0)}%</span>
                            </div>
                          </div>
                        )}
                        {job.matchStatus && (
                          <div className="pt-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              job.matchStatus === 'SHORTLISTED'
                                ? 'bg-green-100 text-green-700'
                                : job.matchStatus === 'REJECTED'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}>
                              {job.matchStatus === 'SHORTLISTED' ? 'Shortlisted' :
                               job.matchStatus === 'REJECTED' ? 'Not selected' : 'Pending review'}
                            </span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* How it works */}
        <Card className="bg-emerald-50 border-emerald-100">
          <CardContent className="py-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">How the Talent Pool Works</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>1. Complete ONE interview per industry vertical (New Energy or Sales)</li>
                  <li>2. Your profile and score are shown to ALL employers in that vertical</li>
                  <li>3. Employers can browse the talent pool and contact qualified candidates</li>
                  <li>4. You can retake up to 3 times - your BEST score is shown to employers</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
