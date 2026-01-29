'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { VideoPlayer } from '@/components/dashboard/video-player'
import { ScoreCard } from '@/components/dashboard/score-card'
import { TranscriptViewer } from '@/components/dashboard/transcript-viewer'
import { employerApi, type InterviewSession, type ScoreDetails } from '@/lib/api'

export default function InterviewDetailPage() {
  const router = useRouter()
  const params = useParams()
  const interviewId = params.id as string

  const [interview, setInterview] = useState<InterviewSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUpdating, setIsUpdating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadInterview = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/login')
          return
        }

        const data = await employerApi.getInterview(interviewId)
        setInterview(data)
      } catch (err) {
        console.error('Failed to load interview:', err)
        setError(err instanceof Error ? err.message : 'Failed to load interview')
      } finally {
        setIsLoading(false)
      }
    }

    loadInterview()
  }, [interviewId, router])

  const handleStatusUpdate = async (status: 'SHORTLISTED' | 'REJECTED') => {
    setIsUpdating(true)
    try {
      const updated = await employerApi.updateInterviewStatus(interviewId, status)
      setInterview(updated)
    } catch (err) {
      console.error('Failed to update status:', err)
      setError(err instanceof Error ? err.message : 'Failed to update status')
    } finally {
      setIsUpdating(false)
    }
  }

  const parseScoreDetails = (aiAnalysis: string | undefined): ScoreDetails | null => {
    if (!aiAnalysis) return null
    try {
      const data = JSON.parse(aiAnalysis)
      if (data.scores) {
        return {
          relevance: data.scores.relevance,
          clarity: data.scores.clarity,
          depth: data.scores.depth,
          communication: data.scores.communication,
          jobFit: data.scores.job_fit,
          overall: 0,
          analysis: data.analysis || '',
          strengths: data.strengths || [],
          improvements: data.improvements || [],
        }
      }
    } catch {
      // Ignore parse errors
    }
    return null
  }

  const parseSummary = (aiSummary: string | undefined) => {
    if (!aiSummary) return null
    try {
      return JSON.parse(aiSummary)
    } catch {
      return { summary: aiSummary }
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading interview...</p>
        </div>
      </main>
    )
  }

  if (error || !interview) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-red-600">Error</CardTitle>
            <CardDescription>{error || 'Interview not found'}</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Link href="/dashboard/interviews">
              <Button variant="outline">Back to Interviews</Button>
            </Link>
          </CardContent>
        </Card>
      </main>
    )
  }

  const summaryData = parseSummary(interview.aiSummary)

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-xl font-bold text-blue-600">
              ZhiPin AI
            </Link>
            <span className="text-gray-400">/</span>
            <Link href="/dashboard/interviews" className="text-gray-600 hover:text-gray-900">
              Interviews
            </Link>
            <span className="text-gray-400">/</span>
            <span className="text-gray-600">{interview.candidateName || 'Interview Detail'}</span>
          </div>
          <Link href="/dashboard/interviews">
            <Button variant="outline" size="sm">Back to List</Button>
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Candidate Info & Actions */}
        <Card className="mb-6">
          <CardContent className="py-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-blue-700 font-bold text-2xl">
                    {(interview.candidateName || 'U').charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {interview.candidateName || 'Unknown Candidate'}
                  </h1>
                  <p className="text-gray-500">
                    {interview.jobTitle} at {interview.companyName}
                  </p>
                  <p className="text-sm text-gray-400">
                    Submitted {new Date(interview.createdAt).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                {interview.totalScore && (
                  <ScoreCard score={interview.totalScore} size="lg" label="Overall Score" />
                )}

                <div className="flex flex-col gap-2">
                  <Button
                    onClick={() => handleStatusUpdate('SHORTLISTED')}
                    disabled={isUpdating}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Shortlist
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleStatusUpdate('REJECTED')}
                    disabled={isUpdating}
                    className="text-red-600 border-red-300 hover:bg-red-50"
                  >
                    Reject
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Summary */}
        {summaryData && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>AI Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {summaryData.summary && (
                <p className="text-gray-700">{summaryData.summary}</p>
              )}

              {summaryData.recommendation && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">Recommendation:</span>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      summaryData.recommendation === 'strong_yes'
                        ? 'bg-green-100 text-green-700'
                        : summaryData.recommendation === 'yes'
                        ? 'bg-green-50 text-green-600'
                        : summaryData.recommendation === 'maybe'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {summaryData.recommendation.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4">
                {summaryData.overall_strengths?.length > 0 && (
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-semibold text-green-900 mb-2">Strengths</h4>
                    <ul className="space-y-1">
                      {summaryData.overall_strengths.map((s: string, i: number) => (
                        <li key={i} className="text-green-800 text-sm flex items-start gap-2">
                          <svg className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {summaryData.overall_improvements?.length > 0 && (
                  <div className="bg-amber-50 rounded-lg p-4">
                    <h4 className="font-semibold text-amber-900 mb-2">Areas for Improvement</h4>
                    <ul className="space-y-1">
                      {summaryData.overall_improvements.map((s: string, i: number) => (
                        <li key={i} className="text-amber-800 text-sm flex items-start gap-2">
                          <svg className="w-4 h-4 mt-0.5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Responses */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-gray-900">Interview Responses</h2>

          {interview.responses.map((response, index) => {
            const scoreDetails = parseScoreDetails(response.aiAnalysis)

            return (
              <Card key={response.id}>
                <CardHeader>
                  <CardTitle className="text-lg">
                    Question {index + 1}: {response.questionText}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid lg:grid-cols-2 gap-6">
                    {/* Video */}
                    <div>
                      {response.videoUrl ? (
                        <VideoPlayer src={response.videoUrl} />
                      ) : (
                        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                          <span className="text-gray-400">No video available</span>
                        </div>
                      )}
                    </div>

                    {/* Score & Analysis */}
                    <div className="space-y-4">
                      {response.aiScore && (
                        <div className="flex items-center gap-4">
                          <ScoreCard score={response.aiScore} size="md" />

                          {scoreDetails && (
                            <div className="flex-1 grid grid-cols-2 gap-2 text-sm">
                              <div>Relevance: <span className="font-medium">{scoreDetails.relevance}/10</span></div>
                              <div>Clarity: <span className="font-medium">{scoreDetails.clarity}/10</span></div>
                              <div>Depth: <span className="font-medium">{scoreDetails.depth}/10</span></div>
                              <div>Communication: <span className="font-medium">{scoreDetails.communication}/10</span></div>
                              <div>Job Fit: <span className="font-medium">{scoreDetails.jobFit}/10</span></div>
                            </div>
                          )}
                        </div>
                      )}

                      {scoreDetails?.analysis && (
                        <div className="bg-blue-50 rounded-lg p-3">
                          <p className="text-blue-800 text-sm">{scoreDetails.analysis}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Transcript */}
                  {response.transcription && (
                    <TranscriptViewer transcript={response.transcription} />
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </main>
  )
}
