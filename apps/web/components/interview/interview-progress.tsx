'use client'

interface InterviewProgressProps {
  currentQuestion: number
  totalQuestions: number
  completedQuestions: number[]
}

export function InterviewProgress({
  currentQuestion,
  totalQuestions,
  completedQuestions,
}: InterviewProgressProps) {
  const progress = (completedQuestions.length / totalQuestions) * 100

  return (
    <div className="space-y-2 sm:space-y-3">
      {/* Progress label - responsive */}
      <div className="flex justify-between items-center">
        <span className="text-xs sm:text-sm font-medium text-gray-700">Progress</span>
        <span className="text-xs sm:text-sm text-gray-500">
          {completedQuestions.length}/{totalQuestions} completed
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Question indicators - mobile optimized */}
      <div className="flex justify-between gap-1 sm:gap-2">
        {Array.from({ length: totalQuestions }, (_, i) => {
          const isCompleted = completedQuestions.includes(i)
          const isCurrent = currentQuestion === i

          return (
            <div
              key={i}
              className={`
                flex-1 h-1.5 sm:h-2 rounded-full transition-colors
                ${isCompleted ? 'bg-green-500' : isCurrent ? 'bg-blue-600' : 'bg-gray-200'}
              `}
              title={`Question ${i + 1}`}
            />
          )
        })}
      </div>

      {/* Step indicators with numbers - smaller on mobile */}
      <div className="flex justify-between px-1">
        {Array.from({ length: totalQuestions }, (_, i) => {
          const questionNum = i + 1
          const isCompleted = completedQuestions.includes(i)
          const isCurrent = currentQuestion === i

          return (
            <div
              key={i}
              className={`
                w-6 h-6 sm:w-8 sm:h-8 rounded-full flex items-center justify-center
                text-xs sm:text-sm font-medium transition-all
                ${isCurrent ? 'ring-2 ring-blue-300 ring-offset-1' : ''}
                ${isCompleted
                  ? 'bg-green-100 text-green-700'
                  : isCurrent
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-400'
                }
              `}
            >
              {isCompleted ? (
                <svg className="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                questionNum
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
