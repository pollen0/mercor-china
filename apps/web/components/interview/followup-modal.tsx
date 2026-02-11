'use client'

import { useState } from 'react'

interface FollowupModalProps {
  isOpen: boolean
  questionIndex: number
  followupQuestions: string[]
  queueId: string
  onAskFollowup: (followupIndex: number) => void
  onSkip: () => void
  isLoading?: boolean
}

export function FollowupModal({
  isOpen,
  questionIndex,
  followupQuestions,
  queueId,
  onAskFollowup,
  onSkip,
  isLoading = false,
}: FollowupModalProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)

  if (!isOpen) return null

  const handleAsk = () => {
    if (selectedIndex !== null) {
      onAskFollowup(selectedIndex)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-600 to-teal-500 px-6 py-4">
          <h3 className="text-lg font-semibold text-white">
            Follow-up Question
          </h3>
          <p className="text-sm text-teal-100 mt-1">
            Based on your response, here are some follow-up questions
          </p>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-sm text-stone-600 mb-4">
            You can choose to answer a follow-up question to expand on your answer, or skip to continue to the next question.
          </p>

          {/* Follow-up questions */}
          <div className="space-y-3">
            {followupQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setSelectedIndex(index)}
                disabled={isLoading}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedIndex === index
                    ? 'border-teal-500 bg-teal-50'
                    : 'border-stone-200 hover:border-teal-300 hover:bg-stone-50'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                    selectedIndex === index
                      ? 'bg-teal-500 text-white'
                      : 'bg-stone-200 text-stone-600'
                  }`}>
                    {index + 1}
                  </div>
                  <p className="text-stone-800">{question}</p>
                </div>
              </button>
            ))}
          </div>

          {/* Info note */}
          <div className="mt-4 p-3 bg-stone-50 rounded-lg">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-stone-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-stone-700">
                Follow-ups are optional. If you feel you&apos;ve fully answered the question, you can skip.
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-stone-50 flex justify-end gap-3">
          <button
            onClick={onSkip}
            disabled={isLoading}
            className="px-4 py-2 text-stone-700 hover:text-stone-900 hover:bg-stone-100 rounded-lg transition-colors disabled:opacity-50"
          >
            Skip Follow-up
          </button>
          <button
            onClick={handleAsk}
            disabled={selectedIndex === null || isLoading}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              <>
                Answer Follow-up
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
