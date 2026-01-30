'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Container, PageWrapper } from '@/components/layout/container'
import { Logo } from '@/components/layout/navbar'
import { verticalApi, candidateVerticalApi, type Vertical, type RoleType, type VerticalProfile } from '@/lib/api'

// Clean vertical config - no emojis
const VERTICALS = {
  new_energy: {
    name: 'New Energy / EV',
    nameZh: '新能源',
    description: 'Battery, embedded systems, autonomous driving, EV sales',
    descriptionZh: '电池、嵌入式系统、自动驾驶、新能源销售',
    roles: [
      { value: 'battery_engineer', name: 'Battery Engineer', nameZh: '电池工程师', technical: true },
      { value: 'embedded_software', name: 'Embedded Software', nameZh: '嵌入式软件', technical: true },
      { value: 'autonomous_driving', name: 'Autonomous Driving', nameZh: '自动驾驶', technical: true },
      { value: 'supply_chain', name: 'Supply Chain', nameZh: '供应链', technical: true },
      { value: 'ev_sales', name: 'EV Sales', nameZh: '新能源销售', technical: false },
    ],
  },
  sales: {
    name: 'Sales / BD',
    nameZh: '销售',
    description: 'Sales representatives, business development, account management',
    descriptionZh: '销售代表、商务拓展、客户管理',
    roles: [
      { value: 'sales_rep', name: 'Sales Representative', nameZh: '销售代表', technical: false },
      { value: 'bd_manager', name: 'BD Manager', nameZh: '商务拓展', technical: false },
      { value: 'account_manager', name: 'Account Manager', nameZh: '客户经理', technical: false },
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
  const [isLoading, setIsLoading] = useState(true)
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [existingProfiles, setExistingProfiles] = useState<VerticalProfile[]>([])

  useEffect(() => {
    const stored = localStorage.getItem('candidate')
    const token = localStorage.getItem('candidate_token')
    if (!stored) {
      router.push('/candidate/login')
      return
    }

    const candidateData = JSON.parse(stored)
    setCandidate(candidateData)

    const loadProfiles = async () => {
      try {
        const data = await candidateVerticalApi.getMyVerticals(token || undefined)
        setExistingProfiles(data.profiles)
      } catch (err) {
        console.error('Failed to load profiles:', err)
      } finally {
        setIsLoading(false)
      }
    }

    loadProfiles()
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
        selectedRole
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
      {/* Clean header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md border-b border-warm-100 z-50">
        <Container size="md" className="h-full flex items-center justify-between">
          <Logo />
          <Link href="/candidate/dashboard">
            <Button variant="ghost" size="sm">Back</Button>
          </Link>
        </Container>
      </header>

      <Container size="md" className="pt-24 pb-12">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-2xl font-semibold text-warm-900 mb-2">Start Interview</h1>
          <p className="text-warm-500">
            One interview per vertical, matched with all relevant jobs
          </p>
        </div>

        {/* Step 1: Select Vertical */}
        <div className="mb-8">
          <h2 className="text-sm font-medium text-warm-500 uppercase tracking-wide mb-4">1. Select Industry</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {Object.entries(VERTICALS).map(([key, vertical]) => {
              const profile = getProfileForVertical(key as Vertical)
              const isCompleted = profile?.status === 'completed'
              const canRetake = profile?.canRetake
              const isSelected = selectedVertical === key

              return (
                <Card
                  key={key}
                  className={`cursor-pointer transition-all ${
                    isSelected
                      ? 'ring-2 ring-brand-500 border-brand-500'
                      : 'hover:border-warm-300'
                  } ${isCompleted && !canRetake ? 'opacity-50 cursor-not-allowed' : ''}`}
                  onClick={() => {
                    if (!isCompleted || canRetake) {
                      setSelectedVertical(key as Vertical)
                      setSelectedRole(null)
                    }
                  }}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{vertical.nameZh}</CardTitle>
                        <CardDescription>{vertical.name}</CardDescription>
                      </div>
                      {isCompleted && (
                        <div className="text-right">
                          <div className="text-sm font-medium text-brand-600">
                            {profile.bestScore?.toFixed(1)}/10
                          </div>
                          {canRetake && (
                            <div className="text-xs text-warm-500">Can retake</div>
                          )}
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-warm-500">{vertical.descriptionZh}</p>
                    {isCompleted && !canRetake && (
                      <p className="text-xs text-warm-400 mt-2">
                        Completed ({profile.attemptCount}/3 attempts)
                      </p>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Step 2: Select Role */}
        {selectedVertical && (
          <div className="mb-8">
            <h2 className="text-sm font-medium text-warm-500 uppercase tracking-wide mb-4">2. Select Role</h2>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
              {VERTICALS[selectedVertical].roles.map((role) => (
                <Card
                  key={role.value}
                  className={`cursor-pointer transition-all ${
                    selectedRole === role.value
                      ? 'ring-2 ring-brand-500 border-brand-500'
                      : 'hover:border-warm-300'
                  }`}
                  onClick={() => setSelectedRole(role.value as RoleType)}
                >
                  <CardContent className="py-4">
                    <div className="font-medium text-warm-900">{role.nameZh}</div>
                    <div className="text-sm text-warm-500">{role.name}</div>
                    {role.technical && (
                      <span className="inline-flex items-center mt-2 px-2 py-0.5 rounded text-xs font-medium bg-warm-100 text-warm-600">
                        Includes Coding
                      </span>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Interview Info */}
        {selectedRole && (
          <div className="mb-8">
            <Card className="bg-warm-50 border-warm-100">
              <CardContent className="py-5">
                <h3 className="font-medium text-warm-900 mb-3 text-sm">Interview Overview</h3>
                <ul className="space-y-2 text-sm text-warm-600">
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    5 video questions for your role
                  </li>
                  {VERTICALS[selectedVertical!].roles.find(r => r.value === selectedRole)?.technical && (
                    <li className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      1 coding challenge (Python)
                    </li>
                  )}
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Visible to all employers in this vertical
                  </li>
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Up to 3 attempts, best score shown
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-warm-50 border border-warm-200 rounded-xl">
            <p className="text-warm-700 text-sm">{error}</p>
          </div>
        )}

        {/* Start Button */}
        <div className="flex justify-center">
          <Button
            variant="brand"
            size="lg"
            className="px-10"
            disabled={!selectedVertical || !selectedRole || isStarting}
            onClick={startInterview}
            loading={isStarting}
          >
            {isStarting ? 'Starting...' : 'Start Interview'}
          </Button>
        </div>
      </Container>
    </PageWrapper>
  )
}
