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
      <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-gray-200 border-t-emerald-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading results...</p>
        </div>
      </main>
    )
  }

  if (pageState === 'error') {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Error</h1>
            <p className="text-gray-500 mb-6">{error}</p>
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
      <main className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-100">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">智</span>
              </div>
              <span className="font-semibold text-gray-900">ZhiMian 智面</span>
            </Link>
          </div>
        </header>

        <div className="flex items-center justify-center p-4 min-h-[calc(100vh-65px)]">
          <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                <div className="w-8 h-8 border-2 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900 mb-2">Processing Your Interview</h1>
              <p className="text-gray-500">
                We are analyzing your responses. This may take a few minutes.
              </p>
            </div>

            <div className="space-y-3 mb-6">
              {results?.responses.map((response, index) => (
                <div
                  key={response.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
                >
                  <span className="text-sm font-medium text-gray-700">Question {index + 1}</span>
                  {response.transcription ? (
                    <div className="flex items-center gap-2 text-emerald-600">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-xs font-medium">Processed</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-gray-400">
                      <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-500 rounded-full animate-spin" />
                      <span className="text-xs">Processing</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="bg-gray-50 rounded-xl p-4 text-center">
              <p className="text-sm text-gray-500">
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
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">智</span>
            </div>
            <span className="font-semibold text-gray-900">ZhiMian 智面</span>
          </Link>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
          {/* Success Header */}
          <div className="bg-gradient-to-br from-emerald-600 to-teal-700 p-8 text-center text-white">
            <div className="mx-auto w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold mb-2">Interview Complete!</h1>
            <p className="text-emerald-100">
              Thank you for completing your interview. Your responses have been analyzed.
            </p>
          </div>

          <div className="p-8 space-y-6">
            {/* Score */}
            {results?.totalScore && (
              <div className="flex justify-center">
                <div className="text-center">
                  <div className="relative">
                    <div className="w-28 h-28 rounded-full bg-gradient-to-br from-emerald-50 to-teal-50 border-4 border-emerald-200 flex items-center justify-center">
                      <span className="text-4xl font-bold text-emerald-600">
                        {results.totalScore.toFixed(1)}
                      </span>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500 mt-2">Overall Score</div>
                </div>
              </div>
            )}

            {/* AI Summary */}
            {results?.aiSummary && (
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-5">
                <h3 className="font-semibold text-emerald-900 mb-2 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  AI Summary
                </h3>
                <p className="text-emerald-800 text-sm leading-relaxed">{results.aiSummary}</p>
              </div>
            )}

            {/* Strengths & Concerns */}
            <div className="grid md:grid-cols-2 gap-4">
              {results?.overallStrengths && results.overallStrengths.length > 0 && (
                <div className="bg-emerald-50 rounded-xl p-5">
                  <h4 className="font-semibold text-emerald-900 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Strengths
                  </h4>
                  <ul className="space-y-2">
                    {results.overallStrengths.map((strength, i) => (
                      <li key={i} className="flex items-start gap-2 text-emerald-800">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 flex-shrink-0" />
                        <span className="text-sm">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {results?.overallConcerns && results.overallConcerns.length > 0 && (
                <div className="bg-amber-50 rounded-xl p-5">
                  <h4 className="font-semibold text-amber-900 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Areas for Growth
                  </h4>
                  <ul className="space-y-2">
                    {results.overallConcerns.map((concern, i) => (
                      <li key={i} className="flex items-start gap-2 text-amber-800">
                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0" />
                        <span className="text-sm">{concern}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Next steps */}
            <div className="bg-gray-50 rounded-xl p-5 text-center">
              <h4 className="font-semibold text-gray-900 mb-2">What&apos;s Next?</h4>
              <p className="text-gray-600 text-sm">
                The hiring team will review your interview and contact you if they would like to proceed.
                Thank you for your interest!
              </p>
            </div>

            <div className="text-center pt-2">
              <Link href="/">
                <Button variant="outline" className="min-w-[140px]">
                  Back to Home
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
