'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { PracticeFeedback, ScoreDetails } from '@/lib/api'

interface PracticeFeedbackCardProps {
  feedback: PracticeFeedback
  onContinue: () => void
  questionNumber: number
  totalQuestions: number
}

function ScoreBar({ label, score, maxScore = 10 }: { label: string; score: number; maxScore?: number }) {
  const percentage = (score / maxScore) * 100
  const getColor = () => {
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-yellow-500'
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
  const [showSampleAnswer, setShowSampleAnswer] = useState(false)
  const { scoreDetails, tips, sampleAnswer } = feedback

  const overallPercentage = (scoreDetails.overall / 10) * 100
  const getOverallRating = () => {
    if (overallPercentage >= 80) return { label: 'Excellent', color: 'text-green-400' }
    if (overallPercentage >= 60) return { label: 'Good', color: 'text-yellow-400' }
    return { label: 'Needs Improvement', color: 'text-red-400' }
  }

  const rating = getOverallRating()

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-600 to-teal-500 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-teal-100 text-sm">Practice Feedback</p>
              <h2 className="text-xl font-semibold text-white">
                Question {questionNumber} of {totalQuestions}
              </h2>
            </div>
            <div className="text-right">
              <p className="text-teal-100 text-sm">Overall Score</p>
              <p className="text-3xl font-bold text-white">{scoreDetails.overall.toFixed(1)}</p>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Overall Rating */}
          <div className="text-center py-4 border-b border-slate-700">
            <p className={`text-xl font-semibold ${rating.color}`}>{rating.label}</p>
            <p className="text-slate-400 text-sm mt-1">{scoreDetails.analysis}</p>
          </div>

          {/* Score Breakdown */}
          <div className="space-y-4">
            <h3 className="font-medium text-white flex items-center gap-2">
              <svg className="w-5 h-5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Score Breakdown
            </h3>
            <div className="space-y-3 bg-slate-700/30 rounded-lg p-4">
              <ScoreBar label="Communication" score={scoreDetails.communication} />
              <ScoreBar label="Problem Solving" score={scoreDetails.problemSolving} />
              <ScoreBar label="Domain Knowledge" score={scoreDetails.domainKnowledge} />
              <ScoreBar label="Growth Mindset" score={scoreDetails.growthMindset} />
              <ScoreBar label="Culture Fit" score={scoreDetails.cultureFit} />
            </div>
          </div>

          {/* Strengths & Concerns */}
          <div className="grid grid-cols-2 gap-4">
            {scoreDetails.strengths.length > 0 && (
              <div className="bg-green-500/10 rounded-lg p-4">
                <h4 className="font-medium text-green-400 flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Strengths
                </h4>
                <ul className="space-y-1">
                  {scoreDetails.strengths.map((strength, i) => (
                    <li key={i} className="text-sm text-slate-300">{strength}</li>
                  ))}
                </ul>
              </div>
            )}
            {scoreDetails.concerns.length > 0 && (
              <div className="bg-amber-500/10 rounded-lg p-4">
                <h4 className="font-medium text-amber-400 flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Areas to Improve
                </h4>
                <ul className="space-y-1">
                  {scoreDetails.concerns.map((concern, i) => (
                    <li key={i} className="text-sm text-slate-300">{concern}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Improvement Tips */}
          {tips.length > 0 && (
            <div className="bg-blue-500/10 rounded-lg p-4">
              <h4 className="font-medium text-blue-400 flex items-center gap-2 mb-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Tips for Improvement
              </h4>
              <ul className="space-y-2">
                {tips.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                    <span className="text-blue-400 mt-0.5">{i + 1}.</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Sample Answer */}
          {sampleAnswer && (
            <div className="border border-slate-600 rounded-lg overflow-hidden">
              <button
                onClick={() => setShowSampleAnswer(!showSampleAnswer)}
                className="w-full p-3 bg-slate-700/50 text-left flex items-center justify-between hover:bg-slate-700/70 transition-colors"
              >
                <span className="font-medium text-slate-200 flex items-center gap-2">
                  <svg className="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  View Sample Answer
                </span>
                <svg
                  className={`w-5 h-5 text-slate-400 transition-transform ${showSampleAnswer ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {showSampleAnswer && (
                <div className="p-4 bg-slate-700/30">
                  <p className="text-sm text-slate-300 italic">&ldquo;{sampleAnswer}&rdquo;</p>
                </div>
              )}
            </div>
          )}

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
