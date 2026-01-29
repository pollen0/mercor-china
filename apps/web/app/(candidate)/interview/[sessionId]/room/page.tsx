'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { VideoRecorder } from '@/components/interview/video-recorder'
import { QuestionCard } from '@/components/interview/question-card'
import { InterviewProgress } from '@/components/interview/interview-progress'
import { interviewApi, questionsApi, type QuestionInfo } from '@/lib/api'

type RoomState = 'loading' | 'question' | 'uploading' | 'error'

export default function InterviewRoomPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.sessionId as string

  const [roomState, setRoomState] = useState<RoomState>('loading')
  const [questions, setQuestions] = useState<QuestionInfo[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [completedQuestions, setCompletedQuestions] = useState<number[]>([])
  const [error, setError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState<string>('')

  useEffect(() => {
    const loadData = async () => {
      try {
        // Get session to check status and job ID
        const session = await interviewApi.get(sessionId)

        if (session.status === 'COMPLETED') {
          router.push(`/interview/${sessionId}/complete`)
          return
        }

        // Get questions for this job
        const questionsData = await questionsApi.list(session.jobId)

        if (questionsData.questions.length === 0) {
          // Seed default questions if none exist
          const seeded = await questionsApi.seedDefaults()
          setQuestions(seeded.questions.map((q, i) => ({ ...q, index: i })))
        } else {
          setQuestions(questionsData.questions.map((q, i) => ({ ...q, index: i })))
        }

        // Mark already completed questions
        const completed = session.responses
          .filter(r => r.videoUrl)
          .map(r => r.questionIndex)
        setCompletedQuestions(completed)

        // Find first unanswered question
        const firstUnanswered = questionsData.questions.findIndex(
          (_, i) => !completed.includes(i)
        )
        setCurrentQuestionIndex(firstUnanswered >= 0 ? firstUnanswered : 0)

        setRoomState('question')
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load interview')
        setRoomState('error')
      }
    }

    loadData()
  }, [sessionId, router])

  const handleRecordingComplete = useCallback(async (blob: Blob) => {
    setRoomState('uploading')
    setUploadProgress('Uploading video...')

    try {
      await interviewApi.submitResponse(sessionId, currentQuestionIndex, blob)

      setUploadProgress('Video uploaded successfully!')

      // Mark question as completed
      setCompletedQuestions(prev => [...prev, currentQuestionIndex])

      // Move to next question or complete
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1)
        setRoomState('question')
      } else {
        // All questions completed, finish interview
        setUploadProgress('Completing interview...')
        await interviewApi.complete(sessionId)
        router.push(`/interview/${sessionId}/complete`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload video')
      setRoomState('error')
    }
  }, [sessionId, currentQuestionIndex, questions.length, router])

  const handleRecordingError = useCallback((errorMessage: string) => {
    setError(errorMessage)
  }, [])

  const skipQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    }
  }

  const finishInterview = async () => {
    try {
      setRoomState('uploading')
      setUploadProgress('Completing interview...')
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
          <div className="w-12 h-12 border-2 border-slate-700 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4" />
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
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-500 mb-6">{error}</p>
          <Button
            onClick={() => setRoomState('question')}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            Try Again
          </Button>
        </div>
      </main>
    )
  }

  if (roomState === 'uploading') {
    return (
      <main className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
          <div className="w-12 h-12 border-2 border-gray-200 border-t-emerald-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">{uploadProgress}</p>
        </div>
      </main>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === questions.length - 1
  const allQuestionsAnswered = completedQuestions.length === questions.length

  return (
    <main className="min-h-screen bg-slate-900 safe-area-inset">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xs">智</span>
            </div>
            <span className="font-medium text-white text-sm">ZhiMian</span>
          </Link>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Question</span>
            <span className="text-white font-semibold">{currentQuestionIndex + 1}</span>
            <span className="text-slate-400">of</span>
            <span className="text-white font-semibold">{questions.length}</span>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-3 sm:p-6 space-y-4 sm:space-y-6">
        {/* Progress */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
          <InterviewProgress
            currentQuestion={currentQuestionIndex}
            totalQuestions={questions.length}
            completedQuestions={completedQuestions}
          />
        </div>

        {/* Question Card */}
        {currentQuestion && (
          <div className="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-xl p-5 sm:p-6 text-white shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-semibold">{currentQuestionIndex + 1}</span>
              </div>
              <span className="text-emerald-100 text-sm">Question {currentQuestionIndex + 1} of {questions.length}</span>
            </div>
            <h2 className="text-lg sm:text-xl font-medium leading-relaxed">{currentQuestion.text}</h2>
            {currentQuestion.textZh && (
              <p className="mt-2 text-emerald-100 text-sm sm:text-base">{currentQuestion.textZh}</p>
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
          <Button
            variant="outline"
            onClick={skipQuestion}
            disabled={isLastQuestion}
            className="bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white min-h-[48px]"
          >
            Skip Question
          </Button>

          {allQuestionsAnswered && (
            <Button
              onClick={finishInterview}
              className="bg-emerald-600 hover:bg-emerald-700 min-h-[48px]"
            >
              <span className="flex items-center gap-2">
                Finish Interview
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
            </Button>
          )}
        </div>

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
