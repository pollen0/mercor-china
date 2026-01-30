'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { verticalApi, candidateVerticalApi, type Vertical, type RoleType, type VerticalProfile } from '@/lib/api'

// Vertical and role configurations
const VERTICALS = {
  new_energy: {
    name: 'New Energy / EV',
    nameZh: '新能源 / 电动汽车',
    description: 'Battery technology, embedded systems, autonomous driving, and EV sales',
    descriptionZh: '电池技术、嵌入式系统、自动驾驶和新能源汽车销售',
    icon: '🔋',
    color: 'emerald',
    roles: [
      { value: 'battery_engineer', name: 'Battery Engineer', nameZh: '电池工程师', technical: true },
      { value: 'embedded_software', name: 'Embedded Software', nameZh: '嵌入式软件工程师', technical: true },
      { value: 'autonomous_driving', name: 'Autonomous Driving', nameZh: '自动驾驶工程师', technical: true },
      { value: 'supply_chain', name: 'Supply Chain', nameZh: '供应链管理', technical: true },
      { value: 'ev_sales', name: 'EV Sales', nameZh: '新能源汽车销售', technical: false },
    ],
  },
  sales: {
    name: 'Sales / BD',
    nameZh: '销售 / 商务拓展',
    description: 'Sales representatives, business development, and account management',
    descriptionZh: '销售代表、商务拓展和客户管理',
    icon: '💼',
    color: 'blue',
    roles: [
      { value: 'sales_rep', name: 'Sales Representative', nameZh: '销售代表', technical: false },
      { value: 'bd_manager', name: 'BD Manager', nameZh: '商务拓展经理', technical: false },
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
    // Check if candidate is logged in
    const stored = localStorage.getItem('candidate')
    const token = localStorage.getItem('candidate_token')
    if (!stored) {
      router.push('/candidate/login')
      return
    }

    const candidateData = JSON.parse(stored)
    setCandidate(candidateData)

    // Load existing vertical profiles
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
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">智</span>
              </div>
              <span className="font-semibold text-gray-900">ZhiMian</span>
            </div>
            <Link href="/candidate/dashboard">
              <Button variant="outline" size="sm">
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Start Your Talent Pool Interview</h1>
          <p className="text-gray-600">
            Complete ONE interview per vertical and get matched with ALL relevant jobs.
          </p>
        </div>

        {/* Step 1: Select Vertical */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">1. Select Industry Vertical</h2>
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
                      ? 'ring-2 ring-emerald-500 border-emerald-500'
                      : 'hover:border-gray-300'
                  } ${isCompleted && !canRetake ? 'opacity-60' : ''}`}
                  onClick={() => {
                    if (!isCompleted || canRetake) {
                      setSelectedVertical(key as Vertical)
                      setSelectedRole(null)
                    }
                  }}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">{vertical.icon}</span>
                        <div>
                          <CardTitle className="text-lg">{vertical.nameZh}</CardTitle>
                          <CardDescription>{vertical.name}</CardDescription>
                        </div>
                      </div>
                      {isCompleted && (
                        <div className="text-right">
                          <div className="text-sm font-medium text-emerald-600">
                            Score: {profile.bestScore?.toFixed(1)}/10
                          </div>
                          {canRetake && (
                            <div className="text-xs text-amber-600">Can retake</div>
                          )}
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{vertical.descriptionZh}</p>
                    {isCompleted && !canRetake && (
                      <p className="text-xs text-gray-500 mt-2">
                        Already completed ({profile.attemptCount}/3 attempts)
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
            <h2 className="text-lg font-semibold text-gray-900 mb-4">2. Select Role Type</h2>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
              {VERTICALS[selectedVertical].roles.map((role) => (
                <Card
                  key={role.value}
                  className={`cursor-pointer transition-all ${
                    selectedRole === role.value
                      ? 'ring-2 ring-emerald-500 border-emerald-500'
                      : 'hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedRole(role.value as RoleType)}
                >
                  <CardContent className="pt-4">
                    <div className="font-medium text-gray-900">{role.nameZh}</div>
                    <div className="text-sm text-gray-500">{role.name}</div>
                    {role.technical && (
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700">
                          Includes Coding
                        </span>
                      </div>
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
            <Card className="bg-emerald-50 border-emerald-100">
              <CardContent className="py-6">
                <h3 className="font-medium text-gray-900 mb-3">Interview Overview</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    5 video questions tailored to your selected role
                  </li>
                  {VERTICALS[selectedVertical!].roles.find(r => r.value === selectedRole)?.technical && (
                    <li className="flex items-center gap-2">
                      <span className="text-emerald-600">✓</span>
                      1 coding challenge (Python)
                    </li>
                  )}
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Your score will be shown to all employers in this vertical
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    You can retake up to 3 times (best score shown)
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Start Button */}
        <div className="flex justify-center">
          <Button
            size="lg"
            className="bg-gradient-to-r from-emerald-600 to-teal-600 px-8"
            disabled={!selectedVertical || !selectedRole || isStarting}
            onClick={startInterview}
          >
            {isStarting ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Starting...
              </>
            ) : (
              'Start Interview'
            )}
          </Button>
        </div>
      </div>
    </main>
  )
}
