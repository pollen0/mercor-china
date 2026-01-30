'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { VideoPlayer } from '@/components/dashboard/video-player'
import { ScoreCard } from '@/components/dashboard/score-card'
import { TranscriptViewer } from '@/components/dashboard/transcript-viewer'
import { ContactCandidateModal } from '@/components/dashboard/contact-candidate-modal'
import { employerApi, type InterviewSession, type ScoreDetails } from '@/lib/api'

export default function InterviewDetailPage() {
  const router = useRouter()
  const params = useParams()
  const interviewId = params.id as string

  const [interview, setInterview] = useState<InterviewSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUpdating, setIsUpdating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showContactModal, setShowContactModal] = useState(false)

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

  const handleContactCandidate = async (data: { subject: string; body: string; messageType: string; jobId?: string }) => {
    if (!interview?.candidateId) throw new Error('No candidate ID')
    await employerApi.contactCandidate(interview.candidateId, data)
  }

  const parseScoreDetails = (aiAnalysis: string | undefined): ScoreDetails | null => {
    if (!aiAnalysis) return null
    try {
      const data = JSON.parse(aiAnalysis)
      if (data.scores) {
        return {
          communication: data.scores.communication,
          problemSolving: data.scores.problem_solving,
          domainKnowledge: data.scores.domain_knowledge,
          motivation: data.scores.motivation,
          cultureFit: data.scores.culture_fit,
          overall: 0,
          analysis: data.analysis || '',
          strengths: data.strengths || [],
          concerns: data.concerns || [],
          highlightQuotes: data.highlight_quotes || [],
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
          <div className="w-12 h-12 border-2 border-gray-200 border-t-emerald-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading interview...</p>
        </div>
      </main>
    )
  }

  if (error || !interview) {
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
            <p className="text-gray-500 mb-6">{error || 'Interview not found'}</p>
            <Link href="/dashboard/interviews">
              <Button variant="outline" className="w-full">Back to Interviews</Button>
            </Link>
          </div>
        </div>
      </main>
    )
  }

  const summaryData = parseSummary(interview.aiSummary)

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">智</span>
              </div>
              <span className="font-semibold text-gray-900">ZhiMian</span>
            </Link>
            <span className="text-gray-300">/</span>
            <Link href="/dashboard/interviews" className="text-gray-500 hover:text-gray-900">
              Interviews
            </Link>
            <span className="text-gray-300">/</span>
            <span className="text-gray-600 font-medium">{interview.candidateName || 'Detail'}</span>
          </div>
          <Link href="/dashboard/interviews">
            <Button variant="outline" size="sm">Back to List</Button>
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Candidate Info & Actions */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center">
                <span className="text-emerald-700 font-bold text-3xl">
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
                <p className="text-sm text-gray-400 mt-1">
                  Submitted {new Date(interview.createdAt).toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              {interview.totalScore && (
                <ScoreCard score={interview.totalScore} size="lg" label="Overall Score" />
              )}

              <div className="flex flex-col gap-2">
                <Button
                  onClick={() => handleStatusUpdate('SHORTLISTED')}
                  disabled={isUpdating}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Shortlist
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowContactModal(true)}
                  className="text-emerald-600 border-emerald-200 hover:bg-emerald-50"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Contact
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleStatusUpdate('REJECTED')}
                  disabled={isUpdating}
                  className="text-red-600 border-red-200 hover:bg-red-50"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Reject
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* AI Summary */}
        {summaryData && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              AI Summary
            </h2>

            <div className="space-y-4">
              {summaryData.summary && (
                <p className="text-gray-700 leading-relaxed">{summaryData.summary}</p>
              )}

              {summaryData.recommendation && (
                <div className="flex items-center gap-3">
                  <span className="font-medium text-gray-700">Recommendation:</span>
                  <span
                    className={`px-4 py-1.5 rounded-full text-sm font-semibold ${
                      summaryData.recommendation === 'strong_yes'
                        ? 'bg-emerald-100 text-emerald-700'
                        : summaryData.recommendation === 'yes'
                        ? 'bg-emerald-50 text-emerald-600'
                        : summaryData.recommendation === 'maybe'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {summaryData.recommendation.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4">
                {summaryData.overall_strengths?.length > 0 && (
                  <div className="bg-emerald-50 rounded-xl p-5">
                    <h4 className="font-semibold text-emerald-900 mb-3 flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Strengths
                    </h4>
                    <ul className="space-y-2">
                      {summaryData.overall_strengths.map((s: string, i: number) => (
                        <li key={i} className="text-emerald-800 text-sm flex items-start gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 flex-shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {(summaryData.overall_concerns?.length > 0 || summaryData.overall_improvements?.length > 0) && (
                  <div className="bg-amber-50 rounded-xl p-5">
                    <h4 className="font-semibold text-amber-900 mb-3 flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Areas for Growth
                    </h4>
                    <ul className="space-y-2">
                      {(summaryData.overall_concerns || summaryData.overall_improvements || []).map((s: string, i: number) => (
                        <li key={i} className="text-amber-800 text-sm flex items-start gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Responses */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-gray-900">Interview Responses</h2>

          {interview.responses.map((response, index) => {
            const scoreDetails = parseScoreDetails(response.aiAnalysis)

            return (
              <div key={response.id} className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-4">
                  <h3 className="text-white font-semibold">
                    Question {index + 1}: {response.questionText}
                  </h3>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid lg:grid-cols-2 gap-6">
                    {/* Video */}
                    <div>
                      {response.videoUrl ? (
                        <VideoPlayer src={response.videoUrl} />
                      ) : (
                        <div className="aspect-video bg-gray-100 rounded-xl flex items-center justify-center">
                          <span className="text-gray-400">No video available</span>
                        </div>
                      )}
                    </div>

                    {/* Score & Analysis */}
                    <div className="space-y-4">
                      {response.aiScore && (
                        <div className="flex items-start gap-4">
                          <ScoreCard score={response.aiScore} size="md" />

                          {scoreDetails && (
                            <div className="flex-1 grid grid-cols-2 gap-3 text-sm">
                              <div className="bg-gray-50 rounded-lg p-2">
                                <span className="text-gray-500">Communication</span>
                                <div className="font-semibold text-gray-900">{scoreDetails.communication}/10</div>
                              </div>
                              <div className="bg-gray-50 rounded-lg p-2">
                                <span className="text-gray-500">Problem Solving</span>
                                <div className="font-semibold text-gray-900">{scoreDetails.problemSolving}/10</div>
                              </div>
                              <div className="bg-gray-50 rounded-lg p-2">
                                <span className="text-gray-500">Domain Knowledge</span>
                                <div className="font-semibold text-gray-900">{scoreDetails.domainKnowledge}/10</div>
                              </div>
                              <div className="bg-gray-50 rounded-lg p-2">
                                <span className="text-gray-500">Motivation</span>
                                <div className="font-semibold text-gray-900">{scoreDetails.motivation}/10</div>
                              </div>
                              <div className="bg-gray-50 rounded-lg p-2 col-span-2">
                                <span className="text-gray-500">Culture Fit</span>
                                <div className="font-semibold text-gray-900">{scoreDetails.cultureFit}/10</div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {scoreDetails?.analysis && (
                        <div className="bg-emerald-50 rounded-xl p-4">
                          <p className="text-emerald-800 text-sm leading-relaxed">{scoreDetails.analysis}</p>
                        </div>
                      )}

                      {scoreDetails?.highlightQuotes && scoreDetails.highlightQuotes.length > 0 && (
                        <div className="bg-gray-50 rounded-xl p-4">
                          <h5 className="text-sm font-medium text-gray-700 mb-2">Key Quotes</h5>
                          <ul className="space-y-2">
                            {scoreDetails.highlightQuotes.map((quote, i) => (
                              <li key={i} className="text-sm text-gray-600 italic">
                                &ldquo;{quote}&rdquo;
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Transcript */}
                  {response.transcription && (
                    <TranscriptViewer transcript={response.transcription} />
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Contact Candidate Modal */}
      {interview && (
        <ContactCandidateModal
          isOpen={showContactModal}
          onClose={() => setShowContactModal(false)}
          candidateId={interview.candidateId}
          candidateName={interview.candidateName || 'Candidate'}
          candidateEmail="" // Email not available in InterviewSession, would need to fetch from candidate
          jobId={interview.jobId}
          jobTitle={interview.jobTitle}
          onSend={handleContactCandidate}
        />
      )}
    </main>
  )
}
