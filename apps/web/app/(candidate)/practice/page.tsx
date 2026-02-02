'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { interviewApi, type InterviewStartResponse } from '@/lib/api'

export default function PracticeModePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [candidateId, setCandidateId] = useState<string | null>(null)

  useEffect(() => {
    // Check if user is logged in
    const stored = localStorage.getItem('candidate')
    if (stored) {
      try {
        const candidate = JSON.parse(stored)
        setCandidateId(candidate.id)
      } catch {
        // Invalid stored data
      }
    }
  }, [])

  const startPractice = async () => {
    if (!candidateId) {
      router.push('/candidate/register?practice=true')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response: InterviewStartResponse = await interviewApi.startPractice(candidateId)
      router.push(`/interview/${response.sessionId}/room`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start practice session')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg bg-slate-800 border-slate-700">
        <CardHeader className="text-center">
          <Link href="/" className="inline-flex items-center justify-center gap-2 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-teal-500 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </Link>
          <CardTitle className="text-2xl text-white">Practice Mode</CardTitle>
          <CardDescription className="text-slate-400">
            Sharpen your interview skills with instant AI feedback
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Features list */}
          <div className="bg-slate-700/50 rounded-lg p-4 space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-teal-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-medium">Instant Feedback</h3>
                <p className="text-sm text-slate-400">Get immediate AI analysis after each answer</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-teal-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-medium">Improvement Tips</h3>
                <p className="text-sm text-slate-400">Receive specific suggestions to enhance your responses</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-teal-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-medium">Private & Safe</h3>
                <p className="text-sm text-slate-400">Practice sessions are not visible to employers</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-teal-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
              <div>
                <h3 className="text-white font-medium">Unlimited Practice</h3>
                <p className="text-sm text-slate-400">Practice as many times as you need</p>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <Button
            onClick={startPractice}
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-teal-500 to-teal-500 hover:from-teal-600 hover:to-teal-500 text-white py-6 text-lg"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Starting Practice...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Start Practice Session
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            )}
          </Button>

          {!candidateId && (
            <p className="text-center text-sm text-slate-500">
              You&apos;ll need to create an account first to start practicing
            </p>
          )}

          <div className="flex items-center justify-center gap-4 pt-4 border-t border-slate-700">
            <Link
              href="/candidate/dashboard"
              className="text-sm text-slate-400 hover:text-teal-400 transition-colors"
            >
              Back to Dashboard
            </Link>
            <span className="text-slate-600">|</span>
            <Link
              href="/"
              className="text-sm text-slate-400 hover:text-teal-400 transition-colors"
            >
              Home
            </Link>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}
