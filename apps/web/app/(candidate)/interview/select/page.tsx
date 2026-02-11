'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { verticalApi, candidateVerticalApi, candidateApi, type Vertical, type RoleType, type VerticalProfile } from '@/lib/api'

// SVG icons for verticals (stroke style per design system)
const VERTICAL_ICONS: Record<string, React.ReactNode> = {
  software_engineering: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" /></svg>
  ),
  data: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>
  ),
  product: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" /></svg>
  ),
  design: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" /></svg>
  ),
  finance: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
  ),
}

// Simplified verticals based on 2026 new grad job market
const VERTICALS: Record<Vertical, {
  name: string
  description: string
  roles: { value: RoleType; name: string; technical: boolean }[]
}> = {
  software_engineering: {
    name: 'Software Engineering',
    description: 'SWE, Embedded, QA - Most common new grad role',
    roles: [
      { value: 'software_engineer', name: 'Software Engineer', technical: true },
      { value: 'embedded_engineer', name: 'Embedded Engineer', technical: true },
      { value: 'qa_engineer', name: 'QA Engineer', technical: true },
    ],
  },
  data: {
    name: 'Data',
    description: 'Data Science, ML, Analytics, Data Engineering',
    roles: [
      { value: 'data_analyst', name: 'Data Analyst', technical: true },
      { value: 'data_scientist', name: 'Data Scientist', technical: true },
      { value: 'ml_engineer', name: 'ML Engineer', technical: true },
      { value: 'data_engineer', name: 'Data Engineer', technical: true },
    ],
  },
  product: {
    name: 'Product Management',
    description: 'Product Manager, APM',
    roles: [
      { value: 'product_manager', name: 'Product Manager', technical: false },
      { value: 'associate_pm', name: 'Associate PM', technical: false },
    ],
  },
  design: {
    name: 'Design',
    description: 'UX/UI, Product Design',
    roles: [
      { value: 'ux_designer', name: 'UX Designer', technical: false },
      { value: 'ui_designer', name: 'UI Designer', technical: false },
      { value: 'product_designer', name: 'Product Designer', technical: false },
    ],
  },
  finance: {
    name: 'Finance',
    description: 'Investment Banking, Finance Analyst',
    roles: [
      { value: 'ib_analyst', name: 'IB Analyst', technical: false },
      { value: 'finance_analyst', name: 'Finance Analyst', technical: false },
      { value: 'equity_research', name: 'Equity Research', technical: false },
    ],
  },
}

interface Candidate {
  id: string
  name: string
  email: string
}

export default function InterviewSelectPage() {
  const router = useRouter()
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [selectedVertical, setSelectedVertical] = useState<Vertical | null>(null)
  const [selectedRole, setSelectedRole] = useState<RoleType | null>(null)
  const [isPractice, setIsPractice] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [existingProfiles, setExistingProfiles] = useState<VerticalProfile[]>([])

  // Profile completion check
  const [hasResume, setHasResume] = useState(false)
  const [profileCheckComplete, setProfileCheckComplete] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('candidate')
    const token = localStorage.getItem('candidate_token')
    if (!stored || !token) {
      router.push('/candidate/login')
      return
    }

    const candidateData = JSON.parse(stored)
    setCandidate(candidateData)

    const loadData = async () => {
      try {
        // Check profile completion and existing interview profiles in parallel
        const [resumeResult, profilesResult] = await Promise.allSettled([
          candidateApi.getMyResume(token),
          candidateVerticalApi.getMyVerticals(token)
        ])

        // Check if resume exists
        if (resumeResult.status === 'fulfilled' && resumeResult.value?.parsedData) {
          setHasResume(true)
        }

        // Load existing vertical profiles
        if (profilesResult.status === 'fulfilled') {
          setExistingProfiles(profilesResult.value.profiles)
        }
      } catch (err) {
        console.error('Failed to load data:', err)
      } finally {
        setProfileCheckComplete(true)
        setIsLoading(false)
      }
    }

    loadData()
  }, [router])

  const getProfileForVertical = (vertical: Vertical): VerticalProfile | undefined => {
    return existingProfiles.find(p => p.vertical === vertical)
  }

  const startInterview = async () => {
    if (!candidate || !selectedVertical || !selectedRole) return

    setIsStarting(true)
    setError(null)

    try {
      const response = await verticalApi.startVerticalInterview(
        candidate.id,
        selectedVertical,
        selectedRole,
        isPractice
      )
      router.push(`/interview/${response.sessionId}`)
    } catch (err) {
      console.error('Failed to start interview:', err)
      setError(err instanceof Error ? err.message : 'Failed to start interview')
      setIsStarting(false)
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-900 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-400 text-sm">Loading...</p>
        </div>
      </main>
    )
  }

  // Show profile completion requirement if resume not uploaded
  if (profileCheckComplete && !hasResume) {
    return (
      <main className="min-h-screen bg-white">
        {/* Header */}
        <header className="border-b border-stone-100">
          <div className="max-w-2xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
            <Link href="/" className="text-lg font-semibold text-stone-900">
              Pathway
            </Link>
            <Link href="/candidate/dashboard">
              <Button variant="ghost" size="sm" className="text-stone-500 hover:text-stone-900">Back</Button>
            </Link>
          </div>
        </header>

        <div className="max-w-md mx-auto px-6 py-16">
          <Card className="shadow-soft-sm">
            <CardContent className="pt-8 pb-6 text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-amber-50 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-stone-900 mb-2">Complete Your Profile First</h2>
              <p className="text-stone-500 text-sm mb-6">
                Please upload your resume before starting an interview. This helps us personalize your questions and match you with the right opportunities.
              </p>

              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-stone-50 rounded-xl text-left">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${hasResume ? 'bg-teal-100' : 'bg-stone-200'}`}>
                    {hasResume ? (
                      <svg className="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <span className="text-xs text-stone-500">1</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-stone-900">Upload Resume</p>
                    <p className="text-xs text-stone-500">Required for personalized interviews</p>
                  </div>
                  {!hasResume && (
                    <span className="text-xs text-amber-600 font-medium">Required</span>
                  )}
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-stone-100">
                <Link href="/candidate/dashboard?tab=profile">
                  <Button className="w-full bg-stone-900 hover:bg-stone-800 text-white">
                    Go to Profile
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-stone-100">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <Link href="/" className="text-lg font-semibold text-stone-900">
            Pathway
          </Link>
          <Link href="/candidate/dashboard">
            <Button variant="ghost" size="sm" className="text-stone-500 hover:text-stone-900">Back</Button>
          </Link>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-2xl font-semibold text-stone-900 mb-2">Start Interview</h1>
          <p className="text-stone-400 text-sm">
            One interview per vertical, visible to all employers
          </p>
        </div>

        {/* Step 1: Select Vertical */}
        <div className="mb-10">
          <p className="text-xs text-stone-400 uppercase tracking-wide mb-4">1. Industry</p>
          <div className="grid sm:grid-cols-2 gap-3">
            {Object.entries(VERTICALS).map(([key, vertical]) => {
              const profile = getProfileForVertical(key as Vertical)
              const isCompleted = profile?.status === 'completed'
              const canInterview = profile?.canInterview
              const isSelected = selectedVertical === key
              const isDisabled = isCompleted && !canInterview

              return (
                <button
                  key={key}
                  className={`text-left p-4 border rounded-xl transition-all duration-200 ${
                    isSelected
                      ? 'border-stone-900 bg-stone-50'
                      : isDisabled
                      ? 'border-stone-100 opacity-50 cursor-not-allowed'
                      : 'border-stone-100 hover:border-stone-300'
                  }`}
                  onClick={() => {
                    if (!isDisabled) {
                      setSelectedVertical(key as Vertical)
                      setSelectedRole(null)
                    }
                  }}
                  disabled={isDisabled}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-stone-900">{vertical.name}</h3>
                      <p className="text-xs text-stone-400 mt-0.5">{vertical.description}</p>
                    </div>
                    {isCompleted && (
                      <span className="text-xs text-stone-500 bg-stone-100 px-2 py-0.5 rounded-full">
                        Done
                      </span>
                    )}
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Step 2: Select Role */}
        {selectedVertical && (
          <div className="mb-10">
            <p className="text-xs text-stone-400 uppercase tracking-wide mb-4">2. Role</p>
            <div className="flex flex-wrap gap-2">
              {VERTICALS[selectedVertical].roles.map((role) => (
                <button
                  key={role.value}
                  className={`px-4 py-2 text-sm rounded-full border transition-all duration-200 ${
                    selectedRole === role.value
                      ? 'bg-stone-900 text-white border-stone-900'
                      : 'bg-white text-stone-600 border-stone-200 hover:border-stone-400'
                  }`}
                  onClick={() => setSelectedRole(role.value as RoleType)}
                >
                  {role.name}
                  {role.technical && <span className="ml-1 text-stone-400">*</span>}
                </button>
              ))}
            </div>
            <p className="text-xs text-stone-300 mt-3">* Includes coding</p>
          </div>
        )}

        {/* Practice Mode Toggle */}
        {selectedRole && (
          <div className="mb-6">
            <button
              type="button"
              onClick={() => setIsPractice(!isPractice)}
              className={`w-full p-4 border rounded-xl transition-all duration-200 text-left ${
                isPractice
                  ? 'border-teal-500 bg-teal-50'
                  : 'border-stone-200 hover:border-stone-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 21a9 9 0 100-18 9 9 0 000 18zm0-4.5a4.5 4.5 0 100-9 4.5 4.5 0 000 9zm0-3a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" /></svg>
                    <h3 className="font-medium text-stone-900">Practice Mode</h3>
                  </div>
                  <p className="text-xs text-stone-400 mt-1">
                    Get the same questions and feedback without affecting your profile score
                  </p>
                </div>
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                  isPractice ? 'border-teal-500 bg-teal-500' : 'border-stone-300'
                }`}>
                  {isPractice && (
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
              </div>
            </button>
          </div>
        )}

        {/* Interview Info */}
        {selectedRole && (
          <div className="mb-10 py-5 border-t border-stone-100">
            <p className="text-xs text-stone-400 uppercase tracking-wide mb-3">Overview</p>
            <ul className="text-sm text-stone-500 space-y-1.5">
              <li>5 video questions for your role</li>
              {VERTICALS[selectedVertical!].roles.find(r => r.value === selectedRole)?.technical && (
                <li>1 coding challenge</li>
              )}
              {isPractice ? (
                <>
                  <li className="text-teal-600">Practice only - won&apos;t count toward your profile</li>
                  <li className="text-teal-600">Get immediate AI feedback on your answers</li>
                </>
              ) : (
                <>
                  <li>Visible to all employers in this vertical</li>
                  <li>Interview monthly to show your growth</li>
                </>
              )}
            </ul>
          </div>
        )}

        {/* Error */}
        {error && (
          <p className="text-sm text-red-500 mb-6">{error}</p>
        )}

        {/* Start Button */}
        <div className="flex justify-center">
          <Button
            size="lg"
            className={`${isPractice ? 'bg-teal-600 hover:bg-teal-700' : 'bg-stone-900 hover:bg-stone-800'} text-white rounded-full px-10`}
            disabled={!selectedVertical || !selectedRole || isStarting}
            onClick={startInterview}
          >
            {isStarting ? 'Starting...' : isPractice ? 'Start Practice' : 'Start Interview'}
          </Button>
        </div>
      </div>
    </main>
  )
}
