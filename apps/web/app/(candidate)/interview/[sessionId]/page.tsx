'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PermissionCheck } from '@/components/interview/permission-check'
import { interviewApi, type InterviewSession } from '@/lib/api'

type PageState = 'loading' | 'permission' | 'ready' | 'error'

export default function InterviewStartPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.sessionId as string

  const [pageState, setPageState] = useState<PageState>('loading')
  const [session, setSession] = useState<InterviewSession | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [permissionGranted, setPermissionGranted] = useState(false)

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = await interviewApi.get(sessionId)
        setSession(data)

        if (data.status === 'COMPLETED') {
          router.push(`/interview/${sessionId}/complete`)
          return
        }

        setPageState('permission')
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load interview')
        setPageState('error')
      }
    }

    fetchSession()
  }, [sessionId, router])

  const handlePermissionGranted = () => {
    setPermissionGranted(true)
    setPageState('ready')
  }

  const startInterview = () => {
    router.push(`/interview/${sessionId}/room`)
  }

  if (pageState === 'loading') {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading interview...</p>
        </div>
      </main>
    )
  }

  if (pageState === 'error') {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <CardTitle className="text-red-600">Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Link href="/">
              <Button variant="outline">Back to Home</Button>
            </Link>
          </CardContent>
        </Card>
      </main>
    )
  }

  if (pageState === 'permission') {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <PermissionCheck onPermissionGranted={handlePermissionGranted} />
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <Link href="/" className="text-2xl font-bold text-blue-600 mb-2">
            ZhiPin AI
          </Link>
          <CardTitle className="text-2xl">Video Interview</CardTitle>
          <CardDescription>
            {session?.jobTitle} at {session?.companyName}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Instructions */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-3">Interview Instructions</h3>
            <ul className="space-y-2 text-blue-800">
              <li className="flex items-start gap-2">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>You will be asked {session?.responses.length || 5} questions</span>
              </li>
              <li className="flex items-start gap-2">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>You have up to 2 minutes to answer each question</span>
              </li>
              <li className="flex items-start gap-2">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>You can re-record your answer before submitting</span>
              </li>
              <li className="flex items-start gap-2">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Find a quiet, well-lit space</span>
              </li>
              <li className="flex items-start gap-2">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Speak clearly and look at the camera</span>
              </li>
            </ul>
          </div>

          {/* Status indicators */}
          <div className="flex items-center justify-center gap-8">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${permissionGranted ? 'bg-green-500' : 'bg-gray-300'}`} />
              <span className="text-sm text-gray-600">Camera Ready</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${permissionGranted ? 'bg-green-500' : 'bg-gray-300'}`} />
              <span className="text-sm text-gray-600">Microphone Ready</span>
            </div>
          </div>

          {/* Start button */}
          <Button
            size="lg"
            className="w-full"
            onClick={startInterview}
            disabled={!permissionGranted}
          >
            Start Interview
          </Button>

          <p className="text-center text-xs text-gray-500">
            By starting this interview, you agree to have your video and audio recorded
            for evaluation purposes.
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
