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
            ? 'bg-gradient-to-r from-emerald-500 to-teal-500'
            : passRate >= 50
            ? 'bg-gradient-to-r from-yellow-500 to-orange-500'
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
              <div className="text-3xl font-bold text-white">{passRate}%</div>
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
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
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
                <div className="flex items-center gap-2 py-2 px-3 bg-gray-50 rounded-lg text-sm text-gray-600">
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
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Execution time: {feedback.executionTimeMs}ms</span>
            </div>
          )}

          {/* AI Analysis (Practice Mode) */}
          {isPractice && feedback.analysis && (
            <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
              <h3 className="text-sm font-semibold text-purple-800 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                AI Analysis
              </h3>
              <p className="text-sm text-purple-700">{feedback.analysis}</p>
            </div>
          )}

          {/* Strengths & Concerns (Practice Mode) */}
          {isPractice && (feedback.strengths.length > 0 || feedback.concerns.length > 0) && (
            <div className="grid grid-cols-2 gap-4">
              {feedback.strengths.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Strengths</h4>
                  <ul className="space-y-1">
                    {feedback.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <svg className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {feedback.concerns.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Areas to Improve</h4>
                  <ul className="space-y-1">
                    {feedback.concerns.map((c, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <svg className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Tips (Practice Mode) */}
          {isPractice && feedback.tips && feedback.tips.length > 0 && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
              <h3 className="text-sm font-semibold text-blue-800 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Tips for Improvement
              </h3>
              <ul className="space-y-2">
                {feedback.tips.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-blue-700">
                    <span className="text-blue-400">{i + 1}.</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Complexity Info (Practice Mode) */}
          {isPractice && (feedback.timeComplexity || feedback.optimalComplexity) && (
            <div className="flex items-center gap-4 text-sm">
              {feedback.timeComplexity && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">Your complexity:</span>
                  <code className="bg-gray-100 px-2 py-0.5 rounded text-gray-700 font-mono">
                    {feedback.timeComplexity}
                  </code>
                </div>
              )}
              {feedback.optimalComplexity && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">Optimal:</span>
                  <code className="bg-emerald-100 px-2 py-0.5 rounded text-emerald-700 font-mono">
                    {feedback.optimalComplexity}
                  </code>
                </div>
              )}
            </div>
          )}

          {/* AI Score */}
          {feedback.aiScore !== undefined && feedback.aiScore !== null && (
            <div className="flex items-center justify-center pt-4 border-t">
              <div className="text-center">
                <div className="text-4xl font-bold text-emerald-600">
                  {feedback.aiScore.toFixed(1)}
                  <span className="text-lg text-gray-400">/10</span>
                </div>
                <div className="text-sm text-gray-500">Overall Score</div>
              </div>
            </div>
          )}

          {/* Continue Button */}
          <div className="pt-4">
            <Button
              onClick={onContinue}
              className={`w-full py-3 font-semibold ${
                isPractice
                  ? 'bg-purple-600 hover:bg-purple-700'
                  : 'bg-emerald-600 hover:bg-emerald-700'
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
      result.passed ? 'bg-green-50' : 'bg-red-50'
    }`}>
      {result.passed ? (
        <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      )}
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm text-gray-800 truncate">{result.name}</div>
        {!result.passed && result.error && (
          <div className="text-xs text-red-600 mt-0.5">{result.error}</div>
        )}
        {!result.passed && !result.error && (
          <div className="text-xs text-gray-500 mt-0.5">
            Expected: <code className="text-blue-600">{result.expected}</code>{' '}
            Got: <code className="text-red-600">{result.actual}</code>
          </div>
        )}
      </div>
    </div>
  )
}
