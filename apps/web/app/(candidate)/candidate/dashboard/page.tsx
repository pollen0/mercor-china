'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Container, PageWrapper } from '@/components/layout/container'
import { Logo } from '@/components/layout/navbar'
import { candidateApi, candidateVerticalApi, type VerticalProfile, type MatchingJob } from '@/lib/api'

interface Candidate {
  id: string
  name: string
  email: string
}

// Clean vertical config - no emojis, unified colors
const VERTICAL_CONFIG = {
  new_energy: {
    name: 'New Energy / EV',
    nameZh: '新能源',
  },
  sales: {
    name: 'Sales / BD',
    nameZh: '销售',
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
    const stored = localStorage.getItem('candidate')
    const token = localStorage.getItem('candidate_token')
    if (!stored) {
      router.push('/candidate/login')
      return
    }

    setCandidate(JSON.parse(stored))

    const fetchData = async () => {
      try {
        const [resumeResult, profileResult, jobResult] = await Promise.allSettled([
          candidateApi.getMyResume(token || undefined),
          candidateVerticalApi.getMyVerticals(token || undefined),
          candidateVerticalApi.getMatchingJobs(token || undefined)
        ])

        if (resumeResult.status === 'fulfilled') {
          setHasResume(resumeResult.value?.parsedData != null)
        }
        if (profileResult.status === 'fulfilled') {
          setVerticalProfiles(profileResult.value.profiles)
        }
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
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-warm-200 border-t-brand-500 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-warm-500 text-sm">Loading...</p>
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      {/* Clean minimal header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md border-b border-warm-100 z-50">
        <Container className="h-full flex items-center justify-between">
          <Logo />
          <div className="flex items-center gap-3">
            <span className="text-sm text-warm-500">{candidate?.name}</span>
            <Link href="/candidate/resume">
              <Button variant="ghost" size="sm">Resume</Button>
            </Link>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </Container>
      </header>

      <Container className="pt-24 pb-12">
        {/* Resume prompt - subtle warning */}
        {!hasResume && (
          <div className="mb-8 p-4 bg-warm-50 border border-warm-200 rounded-2xl">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-warm-100 rounded-xl flex items-center justify-center">
                  <svg className="w-5 h-5 text-warm-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-warm-900">Upload your resume</p>
                  <p className="text-sm text-warm-500">Better matching with employers</p>
                </div>
              </div>
              <Link href="/candidate/resume?onboarding=true">
                <Button variant="brand" size="sm">Upload</Button>
              </Link>
            </div>
          </div>
        )}

        {/* Welcome */}
        <div className="mb-10">
          <h1 className="text-2xl font-semibold text-warm-900 mb-1">Your Profile</h1>
          <p className="text-warm-500">Complete interviews to join the talent pool</p>
        </div>

        {/* Interview Profiles */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-medium text-warm-900">Interview Profiles</h2>
            <Link href="/interview/select">
              <Button variant="brand">Start Interview</Button>
            </Link>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {Object.entries(VERTICAL_CONFIG).map(([key, config]) => {
              const profile = getProfileForVertical(key)
              const isCompleted = profile?.status === 'completed'
              const isInProgress = profile?.status === 'in_progress'

              return (
                <Card key={key} className="relative">
                  {isCompleted && (
                    <div className="absolute top-4 right-4">
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-brand-50 text-brand-700">
                        Completed
                      </span>
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle className="text-lg">{config.nameZh}</CardTitle>
                    <CardDescription>{config.name}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {isCompleted ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-warm-500">Role</span>
                          <span className="font-medium text-warm-900">{ROLE_NAMES[profile.roleType] || profile.roleType}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-warm-500">Best Score</span>
                          <span className="font-medium text-brand-600">{profile.bestScore?.toFixed(1)}/10</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-warm-500">Attempts</span>
                          <span className="font-medium text-warm-900">{profile.attemptCount}/3</span>
                        </div>
                        {profile.canRetake && (
                          <Link href="/interview/select" className="block mt-3">
                            <Button variant="outline" size="sm" className="w-full">Retake</Button>
                          </Link>
                        )}
                      </div>
                    ) : isInProgress ? (
                      <div className="text-center py-4">
                        <p className="text-warm-500 text-sm mb-3">In progress</p>
                        <Link href="/interview/select">
                          <Button variant="brand" size="sm">Continue</Button>
                        </Link>
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-warm-400 text-sm mb-3">Not started</p>
                        <Link href="/interview/select">
                          <Button variant="outline" size="sm">Start</Button>
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
          <div className="mb-10">
            <h2 className="text-lg font-medium text-warm-900 mb-5">
              Matching Jobs <span className="text-warm-400 font-normal">({matchingJobs.length})</span>
            </h2>

            {matchingJobs.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <div className="w-14 h-14 bg-warm-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-7 h-7 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="font-medium text-warm-900 mb-1">No matches yet</h3>
                  <p className="text-sm text-warm-500">Employers will contact you when they find a match</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {matchingJobs.map((job) => (
                  <Card key={job.jobId}>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base">{job.jobTitle}</CardTitle>
                      <CardDescription>{job.companyName}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-warm-100 text-warm-700">
                          {VERTICAL_CONFIG[job.vertical as keyof typeof VERTICAL_CONFIG]?.nameZh || job.vertical}
                        </span>
                        {job.location && (
                          <p className="text-warm-500">{job.location}</p>
                        )}
                        {(job.salaryMin || job.salaryMax) && (
                          <p className="text-warm-500">
                            {job.salaryMin && `${job.salaryMin}K`}
                            {job.salaryMin && job.salaryMax && ' - '}
                            {job.salaryMax && `${job.salaryMax}K`}
                          </p>
                        )}
                        {job.matchScore && (
                          <div className="pt-2 border-t border-warm-100 flex items-center justify-between">
                            <span className="text-warm-500">Match</span>
                            <span className="font-medium text-brand-600">{job.matchScore.toFixed(0)}%</span>
                          </div>
                        )}
                        {job.matchStatus && (
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${
                            job.matchStatus === 'SHORTLISTED'
                              ? 'bg-brand-50 text-brand-700'
                              : job.matchStatus === 'REJECTED'
                              ? 'bg-warm-100 text-warm-500'
                              : 'bg-warm-50 text-warm-600'
                          }`}>
                            {job.matchStatus === 'SHORTLISTED' ? 'Shortlisted' :
                             job.matchStatus === 'REJECTED' ? 'Not selected' : 'Pending'}
                          </span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* How it works - minimal info card */}
        <Card className="bg-warm-50 border-warm-100">
          <CardContent className="py-5">
            <div className="flex items-start gap-4">
              <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center flex-shrink-0 shadow-soft-sm">
                <svg className="w-4 h-4 text-warm-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-warm-900 mb-2 text-sm">How it works</h3>
                <ul className="text-sm text-warm-600 space-y-1">
                  <li>Complete one interview per vertical</li>
                  <li>Your profile is shown to all employers</li>
                  <li>Retake up to 3 times - best score shown</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </Container>
    </PageWrapper>
  )
}
