'use client'

import { Button } from '@/components/ui/button'
import type { CodingFeedback, TestCaseResult } from '@/lib/api'

interface CodeResultsCardProps {
  feedback: CodingFeedback
  onContinue: () => void
  questionNumber: number
  totalQuestions: number
  isPractice?: boolean
}

export function CodeResultsCard({
  feedback,
  onContinue,
  questionNumber,
  totalQuestions,
  isPractice = false,
}: CodeResultsCardProps) {
  const isComplete = feedback.executionStatus !== 'processing'
  const allPassed = feedback.passedCount === feedback.totalCount
  const passRate = feedback.totalCount > 0
    ? Math.round((feedback.passedCount / feedback.totalCount) * 100)
    : 0

  // Get visible test results (non-hidden)
  const visibleResults = feedback.testResults.filter(t => !t.hidden)
  const hiddenResults = feedback.testResults.filter(t => t.hidden)
  const hiddenPassed = hiddenResults.filter(t => t.passed).length

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden">
        {/* Header */}
        <div className={`px-6 py-4 ${
          allPassed
            ? 'bg-gradient-to-r from-teal-500 to-cyan-500'
            : passRate >= 50
            ? 'bg-gradient-to-r from-amber-500 to-amber-400'
            : 'bg-gradient-to-r from-red-500 to-pink-500'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {allPassed ? (
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              ) : (
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              )}
              <div>
                <h2 className="text-white font-semibold text-lg">
                  {allPassed ? 'All Tests Passed!' : 'Some Tests Failed'}
                </h2>
                <p className="text-white/80 text-sm">
                  Question {questionNumber} of {totalQuestions}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-semibold text-white">{passRate}%</div>
              <div className="text-white/80 text-sm">
                {feedback.passedCount}/{feedback.totalCount} tests
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Test Results */}
          <div>
            <h3 className="text-sm font-semibold text-stone-700 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              Test Results
            </h3>
            <div className="space-y-2">
              {visibleResults.map((result, i) => (
                <TestResultRow key={i} result={result} />
              ))}
              {hiddenResults.length > 0 && (
                <div className="flex items-center gap-2 py-2 px-3 bg-stone-50 rounded-lg text-sm text-stone-600">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  <span>
                    {hiddenPassed}/{hiddenResults.length} hidden tests passed
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Execution Time */}
          {feedback.executionTimeMs > 0 && (
            <div className="flex items-center gap-2 text-sm text-stone-500">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Execution time: {feedback.executionTimeMs}ms</span>
            </div>
          )}

          {/* AI analysis, strengths, concerns, tips, complexity, and scores are employer-only */}

          {/* Continue Button */}
          <div className="pt-4">
            <Button
              onClick={onContinue}
              className={`w-full py-3 font-semibold ${
                isPractice
                  ? 'bg-teal-500 hover:bg-teal-600'
                  : 'bg-teal-600 hover:bg-teal-700'
              }`}
            >
              {questionNumber < totalQuestions ? 'Next Question' : 'Finish Interview'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Individual test result row
function TestResultRow({ result }: { result: TestCaseResult }) {
  return (
    <div className={`flex items-center gap-3 py-2 px-3 rounded-lg ${
      result.passed ? 'bg-teal-50' : 'bg-red-50'
    }`}>
      {result.passed ? (
        <svg className="w-5 h-5 text-teal-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      )}
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm text-stone-800 truncate">{result.name}</div>
        {!result.passed && result.error && (
          <div className="text-xs text-red-600 mt-0.5">{result.error}</div>
        )}
        {!result.passed && !result.error && (
          <div className="text-xs text-stone-500 mt-0.5">
            Expected: <code className="text-stone-700">{result.expected}</code>{' '}
            Got: <code className="text-red-600">{result.actual}</code>
          </div>
        )}
      </div>
    </div>
  )
}
