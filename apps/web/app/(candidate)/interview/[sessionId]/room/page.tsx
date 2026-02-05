'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { VideoRecorder } from '@/components/interview/video-recorder'
import { InterviewProgress } from '@/components/interview/interview-progress'
import { PracticeFeedbackCard } from '@/components/interview/practice-feedback-card'
import { FollowupModal } from '@/components/interview/followup-modal'
import { CodeEditor } from '@/components/interview/code-editor'
import { CodeResultsCard } from '@/components/interview/code-results-card'
import {
  interviewApi,
  questionsApi,
  type QuestionInfo,
  type PracticeFeedback,
  type FollowupResponse,
  type FollowupQuestionInfo,
  type CodingQuestionInfo,
  type CodingFeedback,
  type ResponseDetail,
} from '@/lib/api'

type RoomState =
  | 'loading'
  | 'question'
  | 'uploading'
  | 'scoring'
  | 'feedback'
  | 'checking_followup'
  | 'followup_prompt'
  | 'followup_question'
  | 'code_editor'
  | 'code_executing'
  | 'code_results'
  | 'error'

// Extended question info that includes question type
interface ExtendedQuestionInfo extends QuestionInfo {
  questionType?: string
}

export default function InterviewRoomPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.sessionId as string

  const [roomState, setRoomState] = useState<RoomState>('loading')
  const [questions, setQuestions] = useState<ExtendedQuestionInfo[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [completedQuestions, setCompletedQuestions] = useState<number[]>([])
  const [error, setError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState<string>('')
  const [isPractice, setIsPractice] = useState(false)
  const [practiceFeedback, setPracticeFeedback] = useState<PracticeFeedback | null>(null)
  const [lastResponseId, setLastResponseId] = useState<string | null>(null)

  // Follow-up question state
  const [followupData, setFollowupData] = useState<FollowupResponse | null>(null)
  const [activeFollowup, setActiveFollowup] = useState<FollowupQuestionInfo | null>(null)
  const [isFollowupLoading, setIsFollowupLoading] = useState(false)

  // Coding challenge state
  const [codingChallenge, setCodingChallenge] = useState<CodingQuestionInfo | null>(null)
  const [codingFeedback, setCodingFeedback] = useState<CodingFeedback | null>(null)
  const [isCodeSubmitting, setIsCodeSubmitting] = useState(false)

  useEffect(() => {
    const loadData = async () => {
      try {
        // Get session to check status and job ID
        const session = await interviewApi.get(sessionId)

        if (session.status === 'COMPLETED') {
          router.push(`/interview/${sessionId}/complete`)
          return
        }

        // Handle both camelCase and snake_case from API response
        const rawSession = session as unknown as Record<string, unknown>
        setIsPractice(session.isPractice || rawSession.is_practice as boolean || false)

        // Use AI-generated questions stored on the session (preferred)
        // Fall back to static question templates only for legacy sessions
        const sessionQuestions = session.questions || (rawSession.questions as QuestionInfo[]) || []
        let loadedQuestions: ExtendedQuestionInfo[] = []

        if (sessionQuestions.length > 0) {
          // Use personalized AI-generated questions from the session
          // API may return snake_case or camelCase keys depending on endpoint
          loadedQuestions = (sessionQuestions as unknown as Record<string, unknown>[]).map((q, i) => ({
            index: (q.index as number) ?? i,
            text: (q.text as string) || '',
            category: (q.category as string) || undefined,
            questionType: (q.question_type as string) || (q.questionType as string) || 'video',
            codingChallengeId: (q.coding_challenge_id as string) || (q.codingChallengeId as string) || undefined,
          }))
        } else {
          // Legacy fallback: fetch from static questions table
          const jobId = session.jobId || rawSession.job_id as string || undefined
          const questionsData = await questionsApi.list(jobId)
          if (questionsData.questions.length === 0) {
            const seeded = await questionsApi.seedDefaults()
            loadedQuestions = seeded.questions.map((q, i) => ({ ...q, index: i }))
          } else {
            loadedQuestions = questionsData.questions.map((q, i) => ({ ...q, index: i }))
          }
        }

        setQuestions(loadedQuestions)

        // Mark already completed questions (video responses have videoUrl, coding responses have codeSolution)
        const responses = session.responses || (rawSession.responses as ResponseDetail[]) || []
        const completed = (responses as unknown as Record<string, unknown>[])
          .filter((r) =>
            r.videoUrl || r.video_url || r.codeSolution || r.code_solution
          )
          .map((r) => (r.questionIndex ?? r.question_index) as number)
        setCompletedQuestions(completed)

        // Find first unanswered question
        const firstUnanswered = loadedQuestions.findIndex(
          (_, i) => !completed.includes(i)
        )
        const startIndex = firstUnanswered >= 0 ? firstUnanswered : 0
        setCurrentQuestionIndex(startIndex)

        // Check if the first question is a coding question
        const firstQuestion = loadedQuestions[startIndex]
        if (firstQuestion?.questionType === 'coding') {
          // Load the coding challenge
          try {
            const challenge = await interviewApi.getCodingChallenge(sessionId, startIndex)
            setCodingChallenge(challenge)
            setRoomState('code_editor')
          } catch {
            // Fall back to regular question view if challenge loading fails
            setRoomState('question')
          }
        } else {
          setRoomState('question')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load interview')
        setRoomState('error')
      }
    }

    loadData()
  }, [sessionId, router])

  const handleRecordingComplete = useCallback(async (blob: Blob) => {
    // Check if we're recording a follow-up response
    if (activeFollowup) {
      setRoomState('uploading')
      setUploadProgress('Uploading follow-up response...')

      try {
        await interviewApi.submitFollowupResponse(sessionId, activeFollowup.queueId, blob)
        setActiveFollowup(null)
        setFollowupData(null)

        // Move to next question or complete
        if (currentQuestionIndex < questions.length - 1) {
          setCurrentQuestionIndex(prev => prev + 1)
          setRoomState('question')
        } else {
          setUploadProgress('Completing interview...')
          await interviewApi.complete(sessionId)
          router.push(`/interview/${sessionId}/complete`)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to upload follow-up')
        setRoomState('error')
      }
      return
    }

    // Normal response submission
    setRoomState('uploading')
    setUploadProgress('Uploading video...')

    try {
      const result = await interviewApi.submitResponse(sessionId, currentQuestionIndex, blob)
      setLastResponseId(result.responseId)

      setUploadProgress('Video uploaded successfully!')

      // Mark question as completed
      setCompletedQuestions(prev => [...prev, currentQuestionIndex])

      // If practice mode, get immediate feedback
      if (isPractice) {
        setRoomState('scoring')
        setUploadProgress('Analyzing your response...')

        try {
          const feedback = await interviewApi.getPracticeFeedback(sessionId, result.responseId)
          setPracticeFeedback(feedback)
          setRoomState('feedback')
        } catch (feedbackErr) {
          console.error('Failed to get feedback:', feedbackErr)
          // If feedback fails, still allow to continue
          handleContinueAfterFeedback()
        }
      } else {
        // Non-practice mode: move to next question IMMEDIATELY
        // No waiting for follow-ups - this makes transitions instant
        const questionJustAnswered = currentQuestionIndex

        if (currentQuestionIndex < questions.length - 1) {
          // Move to next question immediately - no blocking
          setCurrentQuestionIndex(prev => prev + 1)
          setRoomState('question')
        } else {
          // Last question - complete the interview
          setUploadProgress('Completing interview...')
          await interviewApi.complete(sessionId)
          router.push(`/interview/${sessionId}/complete`)
        }

        // Check for follow-ups in TRUE background (fire and forget, don't await)
        // This allows the UI to transition immediately while follow-ups are checked
        interviewApi.getFollowups(sessionId, questionJustAnswered)
          .then(followups => {
            if (followups.hasFollowups && followups.followupQuestions.length > 0) {
              // Show follow-up prompt if we're still on the question state
              setFollowupData(followups)
              setRoomState('followup_prompt')
            }
          })
          .catch(err => {
            console.error('Failed to check follow-ups (background):', err)
            // Silent failure - user continues normally
          })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload video')
      setRoomState('error')
    }
  }, [sessionId, currentQuestionIndex, questions.length, router, isPractice, activeFollowup])

  const handleContinueAfterFeedback = useCallback(async () => {
    setPracticeFeedback(null)

    // Move to next question or complete
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
      setRoomState('question')
    } else {
      // All questions completed, finish practice
      setRoomState('uploading')
      setUploadProgress('Completing practice session...')
      try {
        await interviewApi.complete(sessionId)
        router.push(`/interview/${sessionId}/complete`)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to complete interview')
        setRoomState('error')
      }
    }
  }, [currentQuestionIndex, questions.length, sessionId, router])

  const handleRecordingError = useCallback((errorMessage: string) => {
    setError(errorMessage)
  }, [])

  // Follow-up handlers
  const handleAskFollowup = useCallback(async (followupIndex: number) => {
    if (!followupData?.queueId) return

    setIsFollowupLoading(true)
    try {
      const followupInfo = await interviewApi.askFollowup(
        sessionId,
        currentQuestionIndex,
        followupIndex
      )
      setActiveFollowup(followupInfo)
      setRoomState('followup_question')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load follow-up question')
      setRoomState('error')
    } finally {
      setIsFollowupLoading(false)
    }
  }, [followupData, sessionId, currentQuestionIndex])

  const handleSkipFollowup = useCallback(async () => {
    setIsFollowupLoading(true)
    try {
      await interviewApi.skipFollowup(sessionId, currentQuestionIndex)
      setFollowupData(null)

      // Move to next question or complete
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1)
        setRoomState('question')
      } else {
        setRoomState('uploading')
        setUploadProgress('Completing interview...')
        await interviewApi.complete(sessionId)
        router.push(`/interview/${sessionId}/complete`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to skip follow-up')
      setRoomState('error')
    } finally {
      setIsFollowupLoading(false)
    }
  }, [sessionId, currentQuestionIndex, questions.length, router])

  // Coding challenge handlers
  const handleCodeSubmit = useCallback(async (code: string) => {
    setIsCodeSubmitting(true)
    setRoomState('code_executing')

    try {
      const result = await interviewApi.submitCode(sessionId, currentQuestionIndex, code)
      setLastResponseId(result.responseId)

      // Poll for results
      const feedback = await interviewApi.pollCodingResults(sessionId, result.responseId)
      setCodingFeedback(feedback)

      // Mark question as completed
      setCompletedQuestions(prev => [...prev, currentQuestionIndex])

      setRoomState('code_results')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit code')
      setRoomState('code_editor')
    } finally {
      setIsCodeSubmitting(false)
    }
  }, [sessionId, currentQuestionIndex])

  const handleCodeResultsContinue = useCallback(async () => {
    setCodingFeedback(null)
    setCodingChallenge(null)

    // Move to next question or complete
    if (currentQuestionIndex < questions.length - 1) {
      const nextIndex = currentQuestionIndex + 1
      setCurrentQuestionIndex(nextIndex)

      // Check if next question is also a coding question
      const nextQuestion = questions[nextIndex] as ExtendedQuestionInfo
      if (nextQuestion?.questionType === 'coding') {
        try {
          const challenge = await interviewApi.getCodingChallenge(sessionId, nextIndex)
          setCodingChallenge(challenge)
          setRoomState('code_editor')
        } catch {
          setRoomState('question')
        }
      } else {
        setRoomState('question')
      }
    } else {
      // All questions completed, finish interview
      setRoomState('uploading')
      setUploadProgress(isPractice ? 'Completing practice session...' : 'Completing interview...')
      try {
        await interviewApi.complete(sessionId)
        router.push(`/interview/${sessionId}/complete`)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to complete interview')
        setRoomState('error')
      }
    }
  }, [currentQuestionIndex, questions, sessionId, router, isPractice])

  const skipQuestion = useCallback(async () => {
    if (currentQuestionIndex < questions.length - 1) {
      const nextIndex = currentQuestionIndex + 1
      setCurrentQuestionIndex(nextIndex)

      // Reset coding state
      setCodingChallenge(null)
      setCodingFeedback(null)

      // Check if next question is a coding question
      const nextQuestion = questions[nextIndex] as ExtendedQuestionInfo
      if (nextQuestion?.questionType === 'coding') {
        try {
          const challenge = await interviewApi.getCodingChallenge(sessionId, nextIndex)
          setCodingChallenge(challenge)
          setRoomState('code_editor')
        } catch {
          setRoomState('question')
        }
      } else {
        setRoomState('question')
      }
    }
  }, [currentQuestionIndex, questions, sessionId])

  // Navigate to a specific question (for retaking)
  const goToQuestion = useCallback(async (questionIndex: number) => {
    // Don't allow navigation during follow-up or other special states
    if (roomState !== 'question') return
    if (questionIndex < 0 || questionIndex >= questions.length) return

    setCurrentQuestionIndex(questionIndex)

    // Reset states
    setCodingChallenge(null)
    setCodingFeedback(null)
    setFollowupData(null)
    setActiveFollowup(null)

    // Check if the question is a coding question
    const targetQuestion = questions[questionIndex] as ExtendedQuestionInfo
    if (targetQuestion?.questionType === 'coding') {
      try {
        const challenge = await interviewApi.getCodingChallenge(sessionId, questionIndex)
        setCodingChallenge(challenge)
        setRoomState('code_editor')
      } catch {
        setRoomState('question')
      }
    } else {
      setRoomState('question')
    }
  }, [questions, sessionId, roomState])

  // Go to previous question
  const goToPreviousQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      goToQuestion(currentQuestionIndex - 1)
    }
  }, [currentQuestionIndex, goToQuestion])

  const finishInterview = async () => {
    try {
      setRoomState('uploading')
      setUploadProgress(isPractice ? 'Completing practice session...' : 'Completing interview...')
      await interviewApi.complete(sessionId)
      router.push(`/interview/${sessionId}/complete`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete interview')
      setRoomState('error')
    }
  }

  if (roomState === 'loading') {
    return (
      <main className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-slate-700 border-t-teal-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading interview questions...</p>
        </div>
      </main>
    )
  }

  if (roomState === 'error') {
    return (
      <main className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
          <div className="mx-auto w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-6">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-stone-900 mb-2">Something went wrong</h2>
          <p className="text-stone-500 mb-6">{error}</p>
          <Button
            onClick={() => setRoomState('question')}
            className="bg-teal-600 hover:bg-teal-700"
          >
            Try Again
          </Button>
        </div>
      </main>
    )
  }

  if (roomState === 'uploading' || roomState === 'scoring' || roomState === 'checking_followup' || roomState === 'code_executing') {
    return (
      <main className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
          <div className="w-12 h-12 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-stone-600">
            {roomState === 'code_executing' ? 'Running your code...' : uploadProgress}
          </p>
          {(roomState === 'scoring' || roomState === 'checking_followup' || roomState === 'code_executing') && (
            <p className="text-sm text-stone-400 mt-2">This may take a moment...</p>
          )}
        </div>
      </main>
    )
  }

  // Show coding results
  if (roomState === 'code_results' && codingFeedback) {
    return (
      <main className="min-h-screen bg-slate-900">
        <CodeResultsCard
          feedback={codingFeedback}
          onContinue={handleCodeResultsContinue}
          questionNumber={currentQuestionIndex + 1}
          totalQuestions={questions.length}
          isPractice={isPractice}
        />
      </main>
    )
  }

  // Show code editor for coding questions
  if (roomState === 'code_editor' && codingChallenge?.codingChallenge) {
    return (
      <main className="min-h-screen bg-slate-900 safe-area-inset">
        {/* Header */}
        <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-7 h-7 bg-gradient-to-br from-teal-500 to-teal-500 rounded-lg flex items-center justify-center">
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
              </div>
              <span className="font-medium text-white text-sm">Pathway</span>
            </Link>
            <div className="flex items-center gap-3">
              {isPractice && (
                <span className="px-2 py-1 bg-teal-500/20 text-teal-300 text-xs rounded-full border border-teal-500/30">
                  Practice Mode
                </span>
              )}
              <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30">
                Coding Challenge
              </span>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-slate-400">Question</span>
                <span className="text-white font-semibold">{currentQuestionIndex + 1}</span>
                <span className="text-slate-400">of</span>
                <span className="text-white font-semibold">{questions.length}</span>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto p-4 sm:p-6">
          {/* Progress */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50 mb-4">
            <InterviewProgress
              currentQuestion={currentQuestionIndex}
              totalQuestions={questions.length}
              completedQuestions={completedQuestions}
              onQuestionClick={goToQuestion}
            />
          </div>

          {/* Code Editor */}
          <CodeEditor
            challenge={codingChallenge.codingChallenge}
            onSubmit={handleCodeSubmit}
            isSubmitting={isCodeSubmitting}
            isPractice={isPractice}
          />

          {/* Navigation */}
          <div className="flex justify-between mt-4">
            <Button
              variant="outline"
              onClick={skipQuestion}
              disabled={currentQuestionIndex >= questions.length - 1}
              className="bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white"
            >
              Skip Question
            </Button>
            {completedQuestions.length === questions.length && (
              <Button
                onClick={finishInterview}
                className={isPractice ? 'bg-teal-500 hover:bg-teal-600' : 'bg-teal-600 hover:bg-teal-700'}
              >
                {isPractice ? 'Finish Practice' : 'Finish Interview'}
              </Button>
            )}
          </div>
        </div>
      </main>
    )
  }

  // Show follow-up prompt modal
  if (roomState === 'followup_prompt' && followupData) {
    return (
      <main className="min-h-screen bg-slate-900">
        <FollowupModal
          isOpen={true}
          questionIndex={currentQuestionIndex}
          followupQuestions={followupData.followupQuestions}
          queueId={followupData.queueId || ''}
          onAskFollowup={handleAskFollowup}
          onSkip={handleSkipFollowup}
          isLoading={isFollowupLoading}
        />
      </main>
    )
  }

  // Show practice feedback modal
  if (roomState === 'feedback' && practiceFeedback) {
    return (
      <main className="min-h-screen bg-slate-900">
        <PracticeFeedbackCard
          feedback={practiceFeedback}
          onContinue={handleContinueAfterFeedback}
          questionNumber={currentQuestionIndex + 1}
          totalQuestions={questions.length}
        />
      </main>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === questions.length - 1
  const allQuestionsAnswered = completedQuestions.length === questions.length
  const isFollowupMode = roomState === 'followup_question' && activeFollowup

  return (
    <main className="min-h-screen bg-slate-900 safe-area-inset">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 bg-gradient-to-br from-teal-500 to-teal-500 rounded-lg flex items-center justify-center">
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            </div>
            <span className="font-medium text-white text-sm">Pathway</span>
          </Link>
          <div className="flex items-center gap-3">
            {isPractice && (
              <span className="px-2 py-1 bg-teal-500/20 text-teal-300 text-xs rounded-full border border-teal-500/30">
                Practice Mode
              </span>
            )}
            <div className="flex items-center gap-2 text-sm">
              <span className="text-slate-400">Question</span>
              <span className="text-white font-semibold">{currentQuestionIndex + 1}</span>
              <span className="text-slate-400">of</span>
              <span className="text-white font-semibold">{questions.length}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-3 sm:p-6 space-y-4 sm:space-y-6">
        {/* Practice mode info banner */}
        {isPractice && (
          <div className="bg-teal-500/10 border border-teal-500/30 rounded-xl p-4 flex items-start gap-3">
            <svg className="w-5 h-5 text-teal-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-teal-300 text-sm font-medium">Practice Mode Active</p>
              <p className="text-teal-300/70 text-xs mt-1">
                You&apos;ll receive instant feedback after each answer. This session is private and won&apos;t be visible to employers.
              </p>
            </div>
          </div>
        )}

        {/* Progress */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
          <InterviewProgress
            currentQuestion={currentQuestionIndex}
            totalQuestions={questions.length}
            completedQuestions={completedQuestions}
            onQuestionClick={!isFollowupMode ? goToQuestion : undefined}
          />
        </div>

        {/* Question Card */}
        {isFollowupMode ? (
          /* Follow-up Question Card */
          <div className="rounded-xl p-5 sm:p-6 text-white shadow-lg bg-gradient-to-br from-amber-500 to-orange-600">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-sm text-amber-100">
                Follow-up Question
              </span>
              <span className="ml-auto px-2 py-0.5 bg-white/20 rounded text-xs">
                Question {currentQuestionIndex + 1}
              </span>
            </div>
            <h2 className="text-lg sm:text-xl font-medium leading-relaxed">{activeFollowup.questionText}</h2>
            <p className="mt-3 text-sm text-amber-100">
              Please elaborate on your previous answer.
            </p>
          </div>
        ) : currentQuestion && (
          /* Regular Question Card */
          <div className={`rounded-xl p-5 sm:p-6 text-white shadow-lg ${
            isPractice
              ? 'bg-gradient-to-br from-teal-500 to-teal-700'
              : 'bg-gradient-to-br from-teal-600 to-teal-600'
          }`}>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold">{currentQuestionIndex + 1}</span>
              </div>
              <span className={`text-sm ${isPractice ? 'text-teal-100' : 'text-teal-100'}`}>
                Question {currentQuestionIndex + 1} of {questions.length}
              </span>
            </div>
            <h2 className="text-lg sm:text-xl font-medium leading-relaxed">{currentQuestion.text}</h2>
            {currentQuestion.textZh && (
              <p className={`mt-2 text-sm sm:text-base ${isPractice ? 'text-teal-100' : 'text-teal-100'}`}>
                {currentQuestion.textZh}
              </p>
            )}
          </div>
        )}

        {/* Video Recorder */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 sm:p-6 border border-slate-700/50">
          <VideoRecorder
            key={currentQuestionIndex}
            onRecordingComplete={handleRecordingComplete}
            onError={handleRecordingError}
            maxDuration={120}
          />
        </div>

        {/* Navigation */}
        <div className="flex flex-col-reverse sm:flex-row gap-3 sm:justify-between">
          {!isFollowupMode ? (
            <div className="flex gap-2">
              {/* Previous Question Button - for retaking */}
              {currentQuestionIndex > 0 && (
                <Button
                  variant="outline"
                  onClick={goToPreviousQuestion}
                  className="bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white min-h-[48px]"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Previous
                </Button>
              )}
              <Button
                variant="outline"
                onClick={skipQuestion}
                disabled={isLastQuestion}
                className="bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white min-h-[48px]"
              >
                Skip Question
              </Button>
            </div>
          ) : (
            <div /> /* Spacer for follow-up mode */
          )}

          {allQuestionsAnswered && !isFollowupMode && (
            <Button
              onClick={finishInterview}
              className={`min-h-[48px] ${
                isPractice
                  ? 'bg-teal-500 hover:bg-teal-600'
                  : 'bg-teal-600 hover:bg-teal-700'
              }`}
            >
              <span className="flex items-center gap-2">
                {isPractice ? 'Finish Practice' : 'Finish Interview'}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
            </Button>
          )}
        </div>

        {/* Retake Hint - shows when there are completed questions */}
        {completedQuestions.length > 0 && !isFollowupMode && (
          <div className="text-center">
            <p className="text-xs text-slate-500">
              Use &quot;Previous&quot; to go back and re-record any answer before finishing
            </p>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <p className="text-red-300 text-sm">{error}</p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setError(null)}
                  className="mt-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 p-0 h-auto"
                >
                  Dismiss
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
