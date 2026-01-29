'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
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
      <main className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4" />
          <p className="text-gray-300">Loading interview questions...</p>
        </div>
      </main>
    )
  }

  if (roomState === 'error') {
    return (
      <main className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg p-8 max-w-md w-full text-center">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => setRoomState('question')}>Try Again</Button>
        </div>
      </main>
    )
  }

  if (roomState === 'uploading') {
    return (
      <main className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg p-8 max-w-md w-full text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">{uploadProgress}</p>
        </div>
      </main>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === questions.length - 1
  const allQuestionsAnswered = completedQuestions.length === questions.length

  return (
    <main className="min-h-screen bg-gray-900 p-2 sm:p-4 safe-area-inset">
      <div className="max-w-4xl mx-auto space-y-3 sm:space-y-6">
        {/* Header - responsive */}
        <div className="flex items-center justify-between text-white px-2 sm:px-0">
          <h1 className="text-lg sm:text-xl font-semibold">Video Interview</h1>
          <div className="text-xs sm:text-sm text-gray-400">
            Q{currentQuestionIndex + 1}/{questions.length}
          </div>
        </div>

        {/* Progress - mobile optimized */}
        <div className="bg-white rounded-lg p-3 sm:p-4">
          <InterviewProgress
            currentQuestion={currentQuestionIndex}
            totalQuestions={questions.length}
            completedQuestions={completedQuestions}
          />
        </div>

        {/* Question - responsive padding */}
        {currentQuestion && (
          <QuestionCard
            questionNumber={currentQuestionIndex + 1}
            totalQuestions={questions.length}
            text={currentQuestion.text}
            textZh={currentQuestion.textZh}
          />
        )}

        {/* Video Recorder - responsive padding */}
        <div className="bg-white rounded-lg p-3 sm:p-4">
          <VideoRecorder
            key={currentQuestionIndex} // Reset recorder for each question
            onRecordingComplete={handleRecordingComplete}
            onError={handleRecordingError}
            maxDuration={120}
          />
        </div>

        {/* Navigation - stack on mobile */}
        <div className="flex flex-col-reverse sm:flex-row gap-3 sm:justify-between">
          <Button
            variant="outline"
            onClick={skipQuestion}
            disabled={isLastQuestion}
            className="bg-white min-h-[44px] text-sm sm:text-base"
          >
            Skip Question
          </Button>

          {allQuestionsAnswered && (
            <Button
              onClick={finishInterview}
              className="min-h-[44px] text-sm sm:text-base"
            >
              Finish Interview
            </Button>
          )}
        </div>

        {/* Error display - touch friendly */}
        {error && (
          <div className="bg-red-100 border border-red-300 rounded-lg p-3 sm:p-4">
            <p className="text-red-700 text-sm sm:text-base">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setError(null)}
              className="mt-2 min-h-[40px]"
            >
              Dismiss
            </Button>
          </div>
        )}
      </div>
    </main>
  )
}
