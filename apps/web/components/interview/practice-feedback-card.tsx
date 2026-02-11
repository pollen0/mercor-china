'use client'

import { Button } from '@/components/ui/button'
import type { PracticeFeedback } from '@/lib/api'

interface PracticeFeedbackCardProps {
  feedback: PracticeFeedback
  onContinue: () => void
  questionNumber: number
  totalQuestions: number
}

function ScoreBar({ label, score, maxScore = 10 }: { label: string; score: number; maxScore?: number }) {
  const percentage = (score / maxScore) * 100
  const getColor = () => {
    if (percentage >= 80) return 'bg-teal-500'
    if (percentage >= 60) return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-sm text-slate-300">{label}</span>
        <span className="text-sm font-medium text-white">{score.toFixed(1)}/{maxScore}</span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${getColor()}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

export function PracticeFeedbackCard({
  feedback,
  onContinue,
  questionNumber,
  totalQuestions
}: PracticeFeedbackCardProps) {
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-600 to-teal-500 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-teal-100 text-sm">Response Recorded</p>
              <h2 className="text-xl font-semibold text-white">
                Question {questionNumber} of {totalQuestions}
              </h2>
            </div>
            <div className="text-right">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Status message - no scores or feedback shown to students */}
          <div className="text-center py-4">
            <p className="text-slate-300 text-sm">
              Your response has been recorded and will be reviewed by employers.
            </p>
          </div>

          {/* Continue Button */}
          <Button
            onClick={onContinue}
            className="w-full bg-gradient-to-r from-teal-500 to-teal-400 hover:from-teal-600 hover:to-teal-500 py-6 text-lg"
          >
            {questionNumber < totalQuestions ? (
              <span className="flex items-center gap-2">
                Continue to Next Question
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Complete Practice Session
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
