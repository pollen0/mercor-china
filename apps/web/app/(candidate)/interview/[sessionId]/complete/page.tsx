'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { interviewApi, type InterviewResults } from '@/lib/api'

type PageState = 'loading' | 'processing' | 'complete' | 'error'

export default function InterviewCompletePage() {
  const params = useParams()
  const sessionId = params.sessionId as string

  const [pageState, setPageState] = useState<PageState>('loading')
  const [results, setResults] = useState<InterviewResults | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await interviewApi.getResults(sessionId)
        setResults(data)

        // Check if all responses have been processed
        const allProcessed = data.responses.every(r => r.transcription || r.aiScore)

        if (allProcessed) {
          setPageState('complete')
        } else {
          setPageState('processing')
          // Poll for updates
          const pollInterval = setInterval(async () => {
            try {
              const updated = await interviewApi.getResults(sessionId)
              setResults(updated)

              const nowComplete = updated.responses.every(r => r.transcription || r.aiScore)
              if (nowComplete) {
                setPageState('complete')
                clearInterval(pollInterval)
              }
            } catch {
              // Ignore polling errors
            }
          }, 5000)

          // Cleanup
          return () => clearInterval(pollInterval)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results')
        setPageState('error')
      }
    }

    fetchResults()
  }, [sessionId])

  if (pageState === 'loading') {
    return (
      <main className="min-h-screen bg-stone-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-stone-500">Loading results...</p>
        </div>
      </main>
    )
  }

  if (pageState === 'error') {
    return (
      <main className="min-h-screen bg-stone-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-soft-lg border border-stone-100 p-8">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-xl font-semibold text-stone-900 mb-2">Error</h1>
            <p className="text-stone-500 mb-6">{error}</p>
            <Link href="/">
              <Button variant="outline" className="w-full">Back to Home</Button>
            </Link>
          </div>
        </div>
      </main>
    )
  }

  if (pageState === 'processing') {
    return (
      <main className="min-h-screen bg-stone-50">
        {/* Header */}
        <header className="bg-white border-b border-stone-100">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-teal-600 to-teal-500 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
              </div>
              <span className="font-semibold text-stone-900">Pathway</span>
            </Link>
          </div>
        </header>

        <div className="flex items-center justify-center p-4 min-h-[calc(100vh-65px)]">
          <div className="w-full max-w-md bg-white rounded-2xl shadow-soft-lg border border-stone-100 p-8">
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center mb-6">
                <div className="w-8 h-8 border-2 border-teal-200 border-t-teal-600 rounded-full animate-spin" />
              </div>
              <h1 className="text-xl font-semibold text-stone-900 mb-2">Processing Your Interview</h1>
              <p className="text-stone-500">
                We are analyzing your responses. This may take a few minutes.
              </p>
            </div>

            <div className="space-y-3 mb-6">
              {results?.responses.map((response, index) => (
                <div
                  key={response.id}
                  className="flex items-center justify-between p-4 bg-stone-50 rounded-xl"
                >
                  <span className="text-sm font-medium text-stone-700">Question {index + 1}</span>
                  {response.transcription ? (
                    <div className="flex items-center gap-2 text-teal-600">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-xs font-medium">Processed</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-stone-400">
                      <div className="w-4 h-4 border-2 border-stone-300 border-t-stone-500 rounded-full animate-spin" />
                      <span className="text-xs">Processing</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="bg-stone-50 rounded-xl p-4 text-center">
              <p className="text-sm text-stone-500">
                You can safely close this page. We will notify you when the analysis is complete.
              </p>
            </div>
          </div>
        </div>
      </main>
    )
  }

  // Complete state
  return (
    <main className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-100">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-teal-600 to-teal-500 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            </div>
            <span className="font-semibold text-stone-900">Pathway</span>
          </Link>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-soft-lg border border-stone-100 overflow-hidden">
          {/* Success Header */}
          <div className="bg-gradient-to-br from-teal-600 to-teal-600 p-5 sm:p-8 text-center text-white">
            <div className="mx-auto w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold mb-2">Interview Complete!</h1>
            <p className="text-teal-100">
              Thank you for completing your interview. Your responses have been analyzed.
            </p>
          </div>

          <div className="p-4 sm:p-8 space-y-6">
            {/* Scores, AI summary, strengths, and concerns are employer-only */}

            {/* Next steps */}
            <div className="bg-stone-50 rounded-xl p-5 text-center">
              <h4 className="font-semibold text-stone-900 mb-2">What&apos;s Next?</h4>
              <p className="text-stone-600 text-sm">
                The hiring team will review your interview and contact you if they would like to proceed.
                Thank you for your interest!
              </p>
            </div>

            <div className="text-center pt-2">
              <Link href="/candidate/dashboard">
                <Button variant="outline" className="min-w-[140px]">
                  Back to Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
