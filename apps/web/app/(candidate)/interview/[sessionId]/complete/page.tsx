'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading results...</p>
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

  if (pageState === 'processing') {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
            <CardTitle>Processing Your Interview</CardTitle>
            <CardDescription>
              We are analyzing your responses. This may take a few minutes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              {results?.responses.map((response, index) => (
                <div
                  key={response.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-sm">Question {index + 1}</span>
                  {response.transcription ? (
                    <div className="flex items-center gap-1 text-green-600">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-xs">Processed</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-gray-400">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400" />
                      <span className="text-xs">Processing</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <p className="text-center text-sm text-gray-500">
              You can safely close this page. We will notify you when the analysis is complete.
            </p>
          </CardContent>
        </Card>
      </main>
    )
  }

  // Complete state
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <CardTitle className="text-green-600">Interview Complete!</CardTitle>
          <CardDescription>
            Thank you for completing your interview. Your responses have been analyzed.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Summary */}
          {results?.aiSummary && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">AI Summary</h3>
              <p className="text-blue-800">{results.aiSummary}</p>
            </div>
          )}

          {/* Score */}
          {results?.totalScore && (
            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="text-5xl font-bold text-blue-600 mb-2">
                  {results.totalScore.toFixed(1)}
                </div>
                <div className="text-gray-500">Overall Score</div>
              </div>
            </div>
          )}

          {/* Strengths & Improvements */}
          <div className="grid md:grid-cols-2 gap-4">
            {results?.overallStrengths && results.overallStrengths.length > 0 && (
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2">Strengths</h4>
                <ul className="space-y-1">
                  {results.overallStrengths.map((strength, i) => (
                    <li key={i} className="flex items-start gap-2 text-green-800">
                      <svg className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-sm">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {results?.overallImprovements && results.overallImprovements.length > 0 && (
              <div className="bg-amber-50 rounded-lg p-4">
                <h4 className="font-semibold text-amber-900 mb-2">Areas for Improvement</h4>
                <ul className="space-y-1">
                  {results.overallImprovements.map((improvement, i) => (
                    <li key={i} className="flex items-start gap-2 text-amber-800">
                      <svg className="w-4 h-4 mt-0.5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-sm">{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Next steps */}
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <h4 className="font-semibold text-gray-900 mb-2">What&apos;s Next?</h4>
            <p className="text-gray-600 text-sm">
              The hiring team will review your interview and contact you if they would like to proceed.
              Thank you for your interest!
            </p>
          </div>

          <div className="text-center">
            <Link href="/">
              <Button variant="outline">Back to Home</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}
